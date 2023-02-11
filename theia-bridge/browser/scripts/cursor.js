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

let currentState = STATES.NOT_READY
let checkIfReadyInterval


// Draw cursor
const drawCanvas = document.createElement('canvas')
drawCanvas.height = window.innerHeight
drawCanvas.width = window.innerWidth
drawCanvas.style.zIndex = '99999999'
drawCanvas.style.position = 'fixed'
drawCanvas.style.backgroundColor = 'rgba(0,0,0,0)'
drawCanvas.style.top = '0'
drawCanvas.style.left = '0'

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
  checkIfReadyInterval = setInterval(checkIfReady, 1000)
});

// Listen for messages
// TODO: clean this up and add proper initial calibration
socket.addEventListener('message', (event) => {
    if(currentState === STATES.NOT_READY && event.data === 'ready!') {
      currentState = STATES.READY;
      clearInterval(checkIfReadyInterval)
      setInterval(poll, Math.floor(1000 / 60))
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

const checkIfReady = () => socket.send('ready');
const poll = () => socket.send('get')