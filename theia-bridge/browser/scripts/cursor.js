/**
 * Injectable script to render a cursor on all webpages
 */

// 1. Create a connection to our websocket
// 2. Receive the readablestream of information
// 3. Render the cursor accordingly

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
}

const POLLING_INTERVAL = 100

let currentState = States.AWAITING_CALIBRATION

// Draw cursor
const drawCanvas = document.createElement('canvas')
drawCanvas.height = window.innerHeight
drawCanvas.width = window.innerWidth

// Add styles to overlay
Object.assign(drawCanvas.style, {
    zIndex: '99999999',
    position: 'fixed',
    backgroundColor: 'rgba(0,0,0,0)',
    top: '0',
    left: '0',
    pointerEvents: 'none',
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

function clear() {
  ctx.clearRect(0, 0, drawCanvas.width, drawCanvas.height)
}

let calibrationStart
function drawCalibration(calibrationState) {
    if(!calibrationStart) {
        calibrationStart = performance.now()
    }
    const timestamp = performance.now()
    const elapsed = timestamp - calibrationStart
    const coefficient = 1 - elapsed/CALIBRATION_DURATION
    
    clear()

    ctx.fillStyle = 'red'
    const {x, y} = CALIBRATION_POINTS[calibrationState]
    ctx.fillRect(
        Math.round(window.innerWidth * x),
        Math.round(window.innerHeight * y),
        Math.ceil(Math.max(20 * coefficient, 0)),
        Math.ceil(Math.max(20 * coefficient, 0)));

    if(coefficient > 0) {
        requestAnimationFrame(() => drawCalibration(calibrationState))
    } else {
        calibrationStart = null
    }
  }

function drawCursor(x, y) {
  ctx.fillStyle = "green";
  ctx.fillRect(Math.round(window.innerWidth * x), Math.round(window.innerHeight * y), 25, 25);
}

// Start sending ready messages
socket.addEventListener('open', (event) => {
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
    [States.AWAITING_CALIBRATION]: (event) => {
        console.log('Awaiting calibration...')
        if(event.data === 'calibrate!') {
            currentState = States.CALIBRATING

            // Send a new message with the first calibration point
            setTimeout(() => socket.send(WebSocketMessages.CALIBRATE), CALIBRATION_DURATION)
        } else {
            // Ask again in a bit
            setTimeout(() => socket.send(WebSocketMessages.AWAITING_CALIBRATION), POLLING_INTERVAL)
        }
    },
    [States.CALIBRATING]: (event) => {
        console.log('Calibrating...')
        const calibrationState = parseInt(event.data)
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
    },
    [States.READYING]: (event) => {
        console.log('Readying...')
        // When we receive a ready message, start sending get messages
        if(event.data === 'ready!') {
            currentState = States.READY
        } else {
            console.log('Waiting...')
            setTimeout(() => socket.send(WebSocketMessages.READY), POLLING_INTERVAL)
        }
    },
    [States.READY]: (event) => {
        console.log('Ready!')
        // Parse the data and draw the cursor
        let data
        try {
            // Note, eval is dangerous, this should only be used with trusted data
            eval(`data = ${event.data}`)
        } catch(err) {
            throw err
        }

        // Draw cursor on webpage
        if(data) {
            const [x, y] = data.left_gaze_point_on_display_area
            requestAnimationFrame(() => {
                clear()
                drawCursor(x, y)
                // This will request the server at the current framerate
                // We may want to limit this to 60Hz on higher Hz displays
                socket.send(WebSocketMessages.GET)
            })
        }
    }
}


// Listen for messages
// TODO: clean this up and add proper initial calibration
socket.addEventListener('message', (event) => {
    if(MESSAGE_HANDLERS[currentState]) {
        MESSAGE_HANDLERS[currentState](event)
    } else {
        throw new ReferenceError('Unknown state ' + currentState)
    }
});