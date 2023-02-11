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

// Connection opened
socket.addEventListener('open', (event) => {
  checkIfReadyInterval = setInterval(checkIfReady, 1000)
});

// Listen for messages
socket.addEventListener('message', (event) => {
    if(currentState === STATES.NOT_READY && event.data === 'ready!') {
      currentState = STATES.READY;
      clearInterval(checkIfReadyInterval)
      setInterval(poll, Math.floor(1000 / 60))
    } else if(currentState === STATES.READY) {
      console.log(JSON.parse(event.data))
      // Draw cursor on webpage
      // requestAnimationFrame(drawCursor)
    } else if(currentState === STATES.NOT_READY && event.data === 'not ready!') {
      console.log('Waiting...')
    }
});

const checkIfReady = () => socket.send('ready');
const poll = () => socket.send('get')