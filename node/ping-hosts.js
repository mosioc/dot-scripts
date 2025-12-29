#!/usr/bin/env node

// checks multiple hosts in parallel for speed
// shows response time in ms with color coding (green < 50ms, yellow < 150ms, blue > 150ms)
// works on Linux, macOS, and Windows
// can read hosts from a file (-f hosts.txt)
// accepts hosts as arguments or uses defaults
// color-coded output with summary
// returns exit code 1 if any host is unreachable (useful for scripts)

const { exec } = require("child_process");
const { promisify } = require("util");
const execAsync = promisify(exec);

const COLORS = {
  green: "\x1b[32m",
  red: "\x1b[31m",
  yellow: "\x1b[33m",
  blue: "\x1b[34m",
  reset: "\x1b[0m",
  dim: "\x1b[2m",
};

// default hosts to check if none provided
const DEFAULT_HOSTS = ["google.com", "github.com", "cloudflare.com"];

async function pingHost(host) {
  const isWindows = process.platform === "win32";
  const pingCmd = isWindows
    ? `ping -n 1 -w 1000 ${host}`
    : `ping -c 1 -W 1 ${host}`;

  try {
    const { stdout } = await execAsync(pingCmd);

    // extract response time
    const timeMatch = stdout.match(/time[=<](\d+\.?\d*)\s*ms/i);
    const time = timeMatch ? parseFloat(timeMatch[1]) : null;

    return { host, success: true, time };
  } catch (error) {
    return { host, success: false, time: null };
  }
}

function formatResult(result) {
  const { host, success, time } = result;

  if (success) {
    const timeStr = time !== null ? `${time}ms` : "OK";
    const color =
      time < 50 ? COLORS.green : time < 150 ? COLORS.yellow : COLORS.blue;
    return `${COLORS.green}✓${COLORS.reset} ${host.padEnd(
      30
    )} ${color}${timeStr}${COLORS.reset}`;
  } else {
    return `${COLORS.red}✗${COLORS.reset} ${host.padEnd(30)} ${
      COLORS.red
    }UNREACHABLE${COLORS.reset}`;
  }
}

async function main() {
  const args = process.argv.slice(2);

  // show help
  if (args.includes("-h") || args.includes("--help")) {
    console.log(`
${COLORS.blue}ping-hosts${COLORS.reset} - Check availability of multiple hosts

${COLORS.yellow}Usage:${COLORS.reset}
  ping-hosts [hosts...]
  ping-hosts -f <file>
  
${COLORS.yellow}Options:${COLORS.reset}
  -h, --help          Show this help message
  -f, --file <file>   Read hosts from file (one per line)
  
${COLORS.yellow}Examples:${COLORS.reset}
  ping-hosts google.com github.com
  ping-hosts -f hosts.txt
  ping-hosts 8.8.8.8 1.1.1.1 cloudflare.com
`);
    return;
  }

  let hosts = [];

  // read from file
  if (args.includes("-f") || args.includes("--file")) {
    const fileIndex = args.findIndex((arg) => arg === "-f" || arg === "--file");
    const filePath = args[fileIndex + 1];

    if (!filePath) {
      console.error(`${COLORS.red}Error: No file specified${COLORS.reset}`);
      process.exit(1);
    }

    try {
      const fs = require("fs");
      const content = fs.readFileSync(filePath, "utf8");
      hosts = content
        .split("\n")
        .map((line) => line.trim())
        .filter((line) => line && !line.startsWith("#"));
    } catch (error) {
      console.error(
        `${COLORS.red}Error reading file: ${error.message}${COLORS.reset}`
      );
      process.exit(1);
    }
  } else if (args.length > 0) {
    // use provided hosts
    hosts = args;
  } else {
    // use defaults
    hosts = DEFAULT_HOSTS;
    console.log(
      `${COLORS.dim}No hosts specified, checking defaults...${COLORS.reset}\n`
    );
  }

  if (hosts.length === 0) {
    console.error(`${COLORS.red}Error: No hosts to check${COLORS.reset}`);
    process.exit(1);
  }

  console.log(
    `${COLORS.blue}Checking ${hosts.length} host(s)...${COLORS.reset}\n`
  );

  // ping all hosts in parallel
  const results = await Promise.all(hosts.map(pingHost));

  // display results
  results.forEach((result) => {
    console.log(formatResult(result));
  });

  // summary
  const available = results.filter((r) => r.success).length;
  const unavailable = results.length - available;

  console.log(`\n${COLORS.dim}${"─".repeat(50)}${COLORS.reset}`);
  console.log(
    `${COLORS.green}Available: ${available}${COLORS.reset} | ${COLORS.red}Unreachable: ${unavailable}${COLORS.reset}`
  );

  // exit with error code if any host is down
  process.exit(unavailable > 0 ? 1 : 0);
}

main().catch((error) => {
  console.error(`${COLORS.red}Error: ${error.message}${COLORS.reset}`);
  process.exit(1);
});
