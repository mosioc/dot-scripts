# Free Memory

**Features:**

* Shows detailed RAM and swap usage with color-coded progress bars
* Works on both Linux and macOS
* Displays total, used, available, free, cached memory
* Can clear page cache (safe operation)
* Can clear swap space
* Watch mode for real-time monitoring
* Human-readable sizes (KB, MB, GB)
* Color-coded warnings (green < 70%, yellow < 85%, red > 85%)

**Installation:**

```bash
# Save files
# bash/free-memory.sh 
# bin/free-memory 

# Make executable
chmod +x bash/free-memory.sh
chmod +x bin/free-memory
```

**Usage examples:**

```bash
# Show current memory usage
free-memory

# Clear page cache (requires sudo)
free-memory -c

# Clear swap space (requires sudo)
free-memory -s

# Clear everything (requires sudo)
free-memory -a

# Watch mode (live updates every 2 seconds)
free-memory -w

# Show help
free-memory --help
```
