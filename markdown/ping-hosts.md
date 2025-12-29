# Ping Hosts

**Installation:**

```bash
# Save the script
# node/ping-hosts.js 

# Save the launcher
# bin/ping-hosts

# Make executable
chmod +x node/ping-hosts.js
chmod +x bin/ping-hosts
```

**Usage examples:**

```bash
# Check default hosts
ping-hosts

# Check specific hosts
ping-hosts google.com github.com 8.8.8.8

# Read from file
ping-hosts -f my-servers.txt

# Show help
ping-hosts --help
```

**Example hosts.txt:**

```txt
google.com
github.com
# DNS servers
8.8.8.8
1.1.1.1
```
