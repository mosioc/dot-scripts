# Serve Here

**Features:**

* Static file server with zero configuration
* Beautiful directory listing with icons and file info
* Automatic index.html serving
* Proper MIME types for all common file formats
* Shows both local and network URLs
* Request logging with timestamps
* Security protection against directory traversal
* Open browser automatically with `-o` flag
* Custom port and directory options

**Installation:**

```bash
# Save files
# node/serve-here.js
# bin/serve-here 

# Make executable
chmod +x node/serve-here.js
chmod +x bin/serve-here
```

**Usage examples:**

```bash
# Serve current directory on port 3000
serve-here

# Serve on custom port
serve-here 8080

# Serve specific directory
serve-here -d ./dist

# Open browser automatically
serve-here -o

# Combine options
serve-here -p 5000 -d ./build -o

# Show help
serve-here --help
```
