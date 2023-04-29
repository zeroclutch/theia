/**
 * Injectable script to render a cursor on all webpages
 */

// 1. Create a connection to our websocket
// 2. Receive the readablestream of information
// 3. Render the cursor accordingly

// Ensure extension script is not injected twice
var __CURSOR_JS_LOADED__

;(function() {
if(__CURSOR_JS_LOADED__) return
__CURSOR_JS_LOADED__ = true

const Options = {
    VERBOSE: false
}

// Create WebSocket connection.
const socket = new WebSocket('ws://localhost:8888');
const States = {
    AWAITING_CALIBRATION: Symbol(0),
    CALIBRATING: Symbol(1),
    NOT_READY: Symbol(2),
    READY: Symbol(3),
}

// A list of string messages that we can send to the server
// Note: this list does not include data messages (ArrayBuffers, Blobs, etc)
const WebSocketMessages = {
    AWAITING_CALIBRATION: 'awaiting_calibration',
    CALIBRATE: 'calibrate',
    READY: 'ready',
    GET: 'get',
    CLICK: 'click',
    CLOSE: 'close',
}

const POLLING_INTERVAL = 100

const FRAME_DURATION = 1000 / 60

let currentState = States.AWAITING_CALIBRATION

// Clicking
const CLICK_TIMEOUT = 0
let lastClick = performance.now()

// Draw cursor
const drawCanvas = document.createElement('canvas')
drawCanvas.height = window.innerHeight
drawCanvas.width = window.innerWidth

// Add styles to overlay
Object.assign(drawCanvas.style, {
    zIndex: '99999999',
    position: 'fixed',
    backgroundColor: 'rgba(255,255,255,1)',
    top: '0',
    left: '0',
    pointerEvents: 'none',// allows for click-through
    // cursor: 'none',
    transition: 'all 0.5s ease-out'
})

// Update canvas size on resize
window.addEventListener('resize', () => {
    drawCanvas.height = window.innerHeight
    drawCanvas.width = window.innerWidth
})

document.body.appendChild(drawCanvas)
const ctx = drawCanvas.getContext("2d");

// Calibration
const CALIBRATION_POINTS = [
    {x: 0.5, y: 0.5},
    {x: 0.1, y: 0.1},
    {x: 0.1, y: 0.9},
    {x: 0.9, y: 0.1},
    {x: 0.9, y: 0.9},
]

const CALIBRATION_DURATION = 1000
let calibrationStart

function clear() {
ctx.clearRect(0, 0, drawCanvas.width, drawCanvas.height)
}

function ellipse({x, y, width, height, color, rotation = 0}) {
    ctx.fillStyle = color
    ctx.beginPath();
    ctx.ellipse(
        x,
        y,
        width,
        height,
        rotation,
        0,
        2 * Math.PI
    );
    ctx.fill()
}

let prevLoc = CALIBRATION_POINTS[0]
const maxVelocity = 0.5

const dist = (x1, y1, x2, y2) => Math.sqrt((x2-x1) ** 2 + (y2-y1) ** 2);

function interpolate(from, to, velocity) {
    const x = from.x - (from.x - to.x) * velocity
    const y = from.y - (from.y - to.y) * velocity
    return {x, y}
}

function drawCalibration(calibrationState) {
    console.log('drawing...')
    if(!calibrationStart) {
        calibrationStart = performance.now()
    }
    const timestamp = performance.now()
    const elapsed = timestamp - calibrationStart
    const coefficient = 1 - elapsed/CALIBRATION_DURATION
    
    clear()

    const nextLoc = CALIBRATION_POINTS[calibrationState] // Pass x,y

    const { x, y } = interpolate(prevLoc, nextLoc, maxVelocity)

    // Interpolate between currentX/Y nextX and nextY

    const size = Math.ceil(5 * Math.sin(elapsed / 1000 * Math.PI)) + 10

    ellipse({
        x: x * window.innerWidth,
        y: y * window.innerHeight,
        width: size,
        height: size,
        color: `rgb(${255 * coefficient},13,255)`,
    })
    

    // Copy over positions
    prevLoc.x = x
    prevLoc.y = y
    if(elapsed < CALIBRATION_DURATION) {
        requestAnimationFrame(() => drawCalibration(calibrationState))
    } else {
        calibrationStart = null
    }
}

function avg(a, b) {
    return (a + b)/2
}

let prevSize = null


const CURSOR_COLORS = [
    '#ff0d72',
    '#e84d9a'
]

function drawCursor(x,y,state) {
   clear()

    let size = 20

    if(prevSize) {
        size = prevSize + (size- prevSize) * 0.1
    }

    prevSize = size
    
    let screenX = Math.round(window.innerWidth * x)
    let screenY = Math.round(window.innerHeight * y)

   ellipse({
        x: screenX,
        y: screenY,
        width: size,
        height: size,
        color: CURSOR_COLORS[state], // Pinkish red
    })
}
 
 function click(x,y) {
     if(performance.now() - lastClick > CLICK_TIMEOUT) {
         console.log('clicked!')
         let screenX = Math.round(window.innerWidth * x)
        let screenY = Math.round(window.innerHeight * y)

         let ev = new MouseEvent('click', {
             'view': window,
             'bubbles': true,
             'cancelable': true,
             'screenX': screenX,
             'screenY': screenY
         });
 
         let el = document.elementFromPoint(screenX, screenY)
 
         el.dispatchEvent(ev);
        lastClick = performance.now()
     }
 }

// Start sending ready messages
socket.addEventListener('open', (ev) => {
    currentState = States.AWAITING_CALIBRATION
    socket.send(WebSocketMessages.AWAITING_CALIBRATION)
});

/**
 * Example server communication:
 * Client: awaiting_calibration
 * Server: 
 * Client: awaiting_calibration
 * Server: calibrate!
 * Client: [0.5, 0.5]
 * Server: 1
 * Client: [0.1, 0.1]
 * Server: 2
 * Client: [0.1, 0.9]
 * Server: 3
 * Client: [0.9, 0.1]
 * Server: 4
 * Client: [0.9, 0.9]
 * Server: 5
 * Client: ready
 * Server: ready!
 * Client: get
 * Server: EyeData
 */

// State machine
const MESSAGE_HANDLERS = {
    [States.AWAITING_CALIBRATION]: (ev) => {
        console.log('Awaiting calibration...')
        if(ev.data === 'ready!') {
            currentState = States.READYING
            socket.send(WebSocketMessages.READY)
        } else if(ev.data === 'calibrate!') {
            currentState = States.CALIBRATING

            // Send a new message with the first calibration point
            setTimeout(() => socket.send(WebSocketMessages.CALIBRATE), CALIBRATION_DURATION)
        } else {
            // Ask again in a bit
            setTimeout(() => socket.send(WebSocketMessages.AWAITING_CALIBRATION), POLLING_INTERVAL)
        }
    },
    [States.CALIBRATING]: (ev) => {
        // Check if we've already calibrated
        if(ev.data === 'ready!') {
            currentState = States.READYING
            socket.send(WebSocketMessages.READY)
        } else {
        console.log('Calibrating...')
        const calibrationState = parseInt(ev.data)
        const remaining = CALIBRATION_POINTS.length - calibrationState

        console.log(`Calibrating ${calibrationState} of ${CALIBRATION_POINTS.length} (${remaining} remaining)`)

        if(remaining) {
            // Animate the calibration
            requestAnimationFrame(() => drawCalibration(calibrationState))
            
            // Send our calibration message after the calibration duration
            setTimeout(() => socket.send(JSON.stringify(CALIBRATION_POINTS[calibrationState])), CALIBRATION_DURATION)
        } else {
            currentState = States.READYING
            socket.send(WebSocketMessages.READY)
        }
        }
    },
    [States.READYING]: (ev) => {
        console.log('Readying...')
        // When we receive a ready message, start sending get messages
        if(ev.data === 'ready!') {
            currentState = States.READY
            socket.send(WebSocketMessages.GET)

            // Remove background
            drawCanvas.style.backgroundColor = 'rgba(255,255,255,0)'
        } else {
            console.log('Waiting...')
            setTimeout(() => socket.send(WebSocketMessages.READY), POLLING_INTERVAL)
        }
    },
    [States.READY]: (ev) => {
        // Parse the data and draw the cursor
        let data
        try {
            data = JSON.parse(ev.data.replace(/NaN/gm, 'null'))
        } catch(err) {
            throw err
        }

        console.log('data', data)
        
        // Draw cursor on webpage
        if(data) {
            const [pos, state] = data
            const [x, y] = pos
            
            requestAnimationFrame(() => {
                drawCursor(x,y)
                // else clear()
                // This will request the server at the current framerate
                // We may want to limit this to 60Hz on higher Hz displays
                socket.send(WebSocketMessages.GET)
            })
        }
    }
}


// Listen for messages
// TODO: clean this up and add proper initial calibration
socket.addEventListener('message', (ev) => {
    if(Options.VERBOSE === true) {
    console.log('message data', ev.data)
    console.log('Current state: ', currentState)
    }

    if(MESSAGE_HANDLERS[currentState]) {
        MESSAGE_HANDLERS[currentState](ev)
    } else {
        throw new ReferenceError('Unknown state ' + currentState)
    }
});


requestIdleCallback(() => {
    var links = document.links, i, length;

    for (i = 0, length = links.length; i < length; i++) {
        links[i].target == '_blank' && links[i].removeAttribute('target');
    }
})

document.addEventListener('keydown', event => {
    if(event.key === 'Control' || event.key === 'Enter') {
        console.log("clicking......")
        socket.send(WebSocketMessages.CLICK)
    }

    event.stopPropagation();
    event.stopImmediatePropagation();
    event.preventDefault();
    
})

document.addEventListener('beforeunload', event => {
    // Normal closure
    socket.send(WebSocketMessages.CLOSE)
})

})()