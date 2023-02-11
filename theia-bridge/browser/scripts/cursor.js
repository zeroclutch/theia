/**
 * Injectable script to render a cursor on all webpages
 */

// 1. Create a connection to our websocket
// 2. Receive the readablestream of information
// 3. Render the cursor accordingly

// Create WebSocket connection.
const socket = new WebSocket('ws://localhost:8888');
const STATES = {
  NOT_READY: Symbol(0),
  CALIBRATING: Symbol(1),
  READY: Symbol(2),
}

const WEBSOCKET_MESSAGES = {
    READY: 'ready',
    GET: 'get',
}

let currentState = STATES.NOT_READY
let sendGetInterval = null

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

function drawCalibration() {
  ctx.fillStyle = 'red'
  let points = [
    [0.5, 0.5],
    [0.1, 0.1],
    [0.1, 0.9],
    [0.9, 0.1],
    [0.9, 0.9],
  ]
  for(let point of points) {
    const [x, y] = point
    ctx.fillRect(Math.round(window.innerWidth * x), Math.round(window.innerHeight * y), 10, 10);
  }
}

function clear() {
  ctx.clearRect(0, 0, drawCanvas.width, drawCanvas.height)
}

function drawCursor(x, y) {
  ctx.fillStyle = "green";
  ctx.fillRect(Math.round(window.innerWidth * x), Math.round(window.innerHeight * y), 25, 25);
}

// Start sending ready messages
socket.addEventListener('open', (event) => {
  sendGetInterval = setInterval(sendReady, 1000)
});

// State machine
const STATE_HANDLERS = {
    [STATES.NOT_READY]: (event) => {
        // When we receive a ready message, start sending get messages
        if(event.data === 'ready!') {
            currentState = STATES.READY
            clearInterval(sendGetInterval)
        } else {
            console.log('Waiting...')
        }
    },
    [STATES.CALIBRATING]: (event) => {},
    [STATES.READY]: (event) => {
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
                sendGet()
            })
        }
    }
}


// Listen for messages
// TODO: clean this up and add proper initial calibration
socket.addEventListener('message', (event) => {
    if(STATE_HANDLERS[currentState]) {
        STATE_HANDLERS[currentState](event)
    } else {
        throw new ReferenceError('Unknown state ' + currentState)
    }
});

drawCalibration()

const sendReady = () => socket.send(WEBSOCKET_MESSAGES.READY);
const sendGet = () => socket.send(WEBSOCKET_MESSAGES.GET)