/**
 * Injectable script to render a cursor on all webpages
 */

// 1. Create a connection to our websocket
// 2. Receive the readablestream of information
// 3. Render the cursor accordingly

// Create WebSocket connection.
const socket = new WebSocket('ws://localhost:8888');
const STATES = {
  NOT_READY: 0,
  CALIBRATING: 1,
  READY: 2,
}

const WEBSOCKET_MESSAGES = {
    READY: 'ready',
    GET: 'get',
}

const POLL_INTERVAL = Math.floor(1000 / 60)

let currentState = STATES.NOT_READY
let sendGetInterval = null

// Draw cursor
const drawCanvas = document.createElement('canvas')
drawCanvas.height = window.innerHeight
drawCanvas.width = window.innerWidth

// Add styles to overlay
Object.apply(drawCanvas.style, {
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
  ctx.clearRect (0, 0, drawCanvas.width, drawCanvas.height)
}

function drawCursor(x, y) {
  ctx.fillStyle = "green";
  ctx.fillRect(Math.round(window.innerWidth * x), Math.round(window.innerHeight * y), 25, 25);
}

// Connection opened
socket.addEventListener('open', (event) => {
  sendGetInterval = setInterval(sendGet, 1000)
});

// Listen for messages
// TODO: clean this up and add proper initial calibration
socket.addEventListener('message', (event) => {
    if(currentState === STATES.NOT_READY && event.data === 'ready!') {
      currentState = STATES.READY;
      clearInterval(sendGetInterval)
      setInterval(sendGet, Math.floor(1000 / 60))
    } else if(currentState === STATES.READY) {
      let data
      try {
        data = JSON.parse(event.data)
      } catch(err) {
        // We received NaNs
      }

      // Draw cursor on webpage
      if(data) {
        const [x, y] = data.left_gaze_point_on_display_area
        requestAnimationFrame(() => {
          clear()
          drawCursor(x, y)
        })
      }

    } else if(currentState === STATES.NOT_READY && event.data === 'not ready!') {
      console.log('Waiting...')
    }
});

drawCalibration()

const sendReady = () => socket.send(WEBSOCKET_MESSAGES.READY);
const sendGet = () => socket.send(WEBSOCKET_MESSAGES.GET)