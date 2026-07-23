// Simple watchdog for shift-scheduler server
// Monitors port 8082 and restarts if down
const http = require('http');
const { spawn } = require('child_process');
const path = require('path');

const PORT = 8082;
const SERVER_JS = path.join(__dirname, 'server.js');
const CHECK_INTERVAL = 30000; // 30 seconds

let serverProcess = null;

function startServer() {
  if (serverProcess) {
    serverProcess.kill();
    serverProcess = null;
  }
  
  serverProcess = spawn('D:\\123\\node.exe', [SERVER_JS], {
    stdio: ['ignore', 'pipe', 'pipe'],
    detached: false,
    windowsHide: true
  });
  
  serverProcess.stdout.on('data', d => process.stdout.write(`[server] ${d}`));
  serverProcess.stderr.on('data', d => process.stderr.write(`[server-err] ${d}`));
  
  serverProcess.on('exit', (code, signal) => {
    console.log(`[watchdog] Server exited (code=${code}, signal=${signal})`);
    serverProcess = null;
  });
  
  console.log(`[watchdog] Started server PID ${serverProcess.pid}`);
}

function checkServer() {
  const req = http.get(`http://127.0.0.1:${PORT}/`, res => {
    res.resume();
    // Server is up
  });
  
  req.on('error', () => {
    console.log(`[watchdog] Server down! Restarting...`);
    startServer();
  });
  
  req.setTimeout(5000, () => {
    req.destroy();
    console.log(`[watchdog] Server timeout! Restarting...`);
    startServer();
  });
}

// Start
startServer();
setInterval(checkServer, CHECK_INTERVAL);
console.log(`[watchdog] Watching port ${PORT} every ${CHECK_INTERVAL/1000}s`);
