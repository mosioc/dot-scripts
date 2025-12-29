#!/usr/bin/env node

const http = require('http');
const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');

const COLORS = {
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m',
  reset: '\x1b[0m',
  dim: '\x1b[2m',
  bold: '\x1b[1m'
};

const MIME_TYPES = {
  '.html': 'text/html',
  '.css': 'text/css',
  '.js': 'text/javascript',
  '.json': 'application/json',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.gif': 'image/gif',
  '.svg': 'image/svg+xml',
  '.ico': 'image/x-icon',
  '.webp': 'image/webp',
  '.mp4': 'video/mp4',
  '.webm': 'video/webm',
  '.mp3': 'audio/mpeg',
  '.wav': 'audio/wav',
  '.pdf': 'application/pdf',
  '.txt': 'text/plain',
  '.xml': 'application/xml',
  '.woff': 'font/woff',
  '.woff2': 'font/woff2',
  '.ttf': 'font/ttf',
  '.md': 'text/markdown'
};

function parseArgs() {
  const args = process.argv.slice(2);
  const options = {
    port: 3000,
    dir: process.cwd(),
    open: false,
    help: false
  };

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    
    if (arg === '-h' || arg === '--help') {
      options.help = true;
    } else if (arg === '-p' || arg === '--port') {
      options.port = parseInt(args[++i], 10) || 3000;
    } else if (arg === '-d' || arg === '--dir') {
      options.dir = path.resolve(args[++i]);
    } else if (arg === '-o' || arg === '--open') {
      options.open = true;
    } else if (!arg.startsWith('-')) {
      // First non-flag argument is the port
      const portNum = parseInt(arg, 10);
      if (!isNaN(portNum)) {
        options.port = portNum;
      }
    }
  }

  return options;
}

function showHelp() {
  console.log(`
${COLORS.blue}${COLORS.bold}serve-here${COLORS.reset} - Local static file server

${COLORS.yellow}Usage:${COLORS.reset}
  serve-here [port] [options]
  
${COLORS.yellow}Options:${COLORS.reset}
  -p, --port <port>   Port number (default: 3000)
  -d, --dir <path>    Directory to serve (default: current)
  -o, --open          Open browser automatically
  -h, --help          Show this help message
  
${COLORS.yellow}Examples:${COLORS.reset}
  serve-here                    # Serve current dir on port 3000
  serve-here 8080               # Serve on port 8080
  serve-here -p 5000 -o         # Port 5000 and open browser
  serve-here -d ./dist          # Serve ./dist directory
`);
}

function generateDirectoryListing(dirPath, urlPath) {
  const files = fs.readdirSync(dirPath);
  
  const items = files.map(file => {
    const filePath = path.join(dirPath, file);
    const stat = fs.statSync(filePath);
    const isDir = stat.isDirectory();
    const href = path.join(urlPath, file);
    const size = isDir ? '-' : formatBytes(stat.size);
    const icon = isDir ? '📁' : '📄';
    
    return { name: file, href, isDir, size, modified: stat.mtime };
  });

  // Sort: directories first, then alphabetically
  items.sort((a, b) => {
    if (a.isDir && !b.isDir) return -1;
    if (!a.isDir && b.isDir) return 1;
    return a.name.localeCompare(b.name);
  });

  const parent = urlPath !== '/' ? 
    `<tr><td><a href="${path.dirname(urlPath)}">📁 ..</a></td><td>-</td><td>-</td></tr>` : '';

  const rows = items.map(item => `
    <tr>
      <td><a href="${item.href}">${item.isDir ? '📁' : '📄'} ${item.name}${item.isDir ? '/' : ''}</a></td>
      <td>${item.size}</td>
      <td>${item.modified.toLocaleString()}</td>
    </tr>
  `).join('');

  return `
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Index of ${urlPath}</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      padding: 2rem;
      background: #f5f5f5;
    }
    .container {
      max-width: 1200px;
      margin: 0 auto;
      background: white;
      border-radius: 8px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.1);
      padding: 2rem;
    }
    h1 {
      color: #333;
      margin-bottom: 1.5rem;
      font-size: 1.5rem;
    }
    table {
      width: 100%;
      border-collapse: collapse;
    }
    th {
      text-align: left;
      padding: 0.75rem;
      background: #f8f9fa;
      font-weight: 600;
      border-bottom: 2px solid #dee2e6;
    }
    td {
      padding: 0.75rem;
      border-bottom: 1px solid #e9ecef;
    }
    tr:hover {
      background: #f8f9fa;
    }
    a {
      color: #0066cc;
      text-decoration: none;
    }
    a:hover {
      text-decoration: underline;
    }
    .path {
      color: #666;
      font-size: 0.9rem;
      font-family: monospace;
    }
  </style>
</head>
<body>
  <div class="container">
    <h1>Index of ${urlPath}</h1>
    <p class="path">${dirPath}</p>
    <table>
      <thead>
        <tr>
          <th>Name</th>
          <th>Size</th>
          <th>Modified</th>
        </tr>
      </thead>
      <tbody>
        ${parent}
        ${rows}
      </tbody>
    </table>
  </div>
</body>
</html>
  `;
}

function formatBytes(bytes) {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

function openBrowser(url) {
  const command = process.platform === 'darwin' ? 'open' :
                  process.platform === 'win32' ? 'start' : 'xdg-open';
  exec(`${command} ${url}`);
}

function getLocalIP() {
  const { networkInterfaces } = require('os');
  const nets = networkInterfaces();
  
  for (const name of Object.keys(nets)) {
    for (const net of nets[name]) {
      // Skip internal and non-IPv4 addresses
      if (net.family === 'IPv4' && !net.internal) {
        return net.address;
      }
    }
  }
  return 'localhost';
}

function createServer(rootDir, port) {
  const server = http.createServer((req, res) => {
    // Decode URL and remove query string
    let urlPath = decodeURIComponent(req.url.split('?')[0]);
    
    // Security: prevent directory traversal
    if (urlPath.includes('..')) {
      res.writeHead(403, { 'Content-Type': 'text/plain' });
      res.end('403 Forbidden');
      return;
    }

    const filePath = path.join(rootDir, urlPath);

    // Log request
    const timestamp = new Date().toLocaleTimeString();
    console.log(`${COLORS.dim}[${timestamp}]${COLORS.reset} ${COLORS.cyan}${req.method}${COLORS.reset} ${urlPath}`);

    fs.stat(filePath, (err, stats) => {
      if (err) {
        res.writeHead(404, { 'Content-Type': 'text/plain' });
        res.end('404 Not Found');
        return;
      }

      if (stats.isDirectory()) {
        // Try to serve index.html
        const indexPath = path.join(filePath, 'index.html');
        if (fs.existsSync(indexPath)) {
          fs.readFile(indexPath, (err, data) => {
            if (err) {
              res.writeHead(500, { 'Content-Type': 'text/plain' });
              res.end('500 Internal Server Error');
              return;
            }
            res.writeHead(200, { 'Content-Type': 'text/html' });
            res.end(data);
          });
        } else {
          // Generate directory listing
          const html = generateDirectoryListing(filePath, urlPath);
          res.writeHead(200, { 'Content-Type': 'text/html' });
          res.end(html);
        }
      } else {
        // Serve file
        const ext = path.extname(filePath).toLowerCase();
        const mimeType = MIME_TYPES[ext] || 'application/octet-stream';

        fs.readFile(filePath, (err, data) => {
          if (err) {
            res.writeHead(500, { 'Content-Type': 'text/plain' });
            res.end('500 Internal Server Error');
            return;
          }
          res.writeHead(200, { 'Content-Type': mimeType });
          res.end(data);
        });
      }
    });
  });

  return server;
}

function main() {
  const options = parseArgs();

  if (options.help) {
    showHelp();
    return;
  }

  if (!fs.existsSync(options.dir)) {
    console.error(`${COLORS.red}Error: Directory does not exist: ${options.dir}${COLORS.reset}`);
    process.exit(1);
  }

  const server = createServer(options.dir, options.port);

  server.listen(options.port, () => {
    const localIP = getLocalIP();
    console.log(`
${COLORS.green}${COLORS.bold}✓ Server running!${COLORS.reset}

  ${COLORS.dim}Local:${COLORS.reset}    ${COLORS.cyan}http://localhost:${options.port}${COLORS.reset}
  ${COLORS.dim}Network:${COLORS.reset}  ${COLORS.cyan}http://${localIP}:${options.port}${COLORS.reset}

  ${COLORS.dim}Serving:${COLORS.reset}  ${options.dir}

${COLORS.yellow}Press Ctrl+C to stop${COLORS.reset}
`);

    if (options.open) {
      openBrowser(`http://localhost:${options.port}`);
    }
  });

  server.on('error', (err) => {
    if (err.code === 'EADDRINUSE') {
      console.error(`${COLORS.red}Error: Port ${options.port} is already in use${COLORS.reset}`);
      console.log(`${COLORS.dim}Try a different port with: serve-here -p <port>${COLORS.reset}`);
    } else {
      console.error(`${COLORS.red}Server error: ${err.message}${COLORS.reset}`);
    }
    process.exit(1);
  });
}

main();