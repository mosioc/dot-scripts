# web-to-markdown

Extract webpage content and convert it to markdown format.

## Description

This script fetches webpages from a list of URLs and converts their HTML content to clean markdown format. It's useful for:

- Archiving web content in a readable format
- Creating offline documentation from web resources
- Converting blog posts or articles to markdown
- Batch processing multiple URLs at once

## Features

- Converts HTML to clean markdown format
- Preserves structure: headings, lists, links, images, code blocks
- Batch processing of multiple URLs
- Read URLs from a file
- Customizable output directory
- Colored terminal output
- Error handling and progress reporting
- Automatic filename generation from URLs

## Installation

1. Copy the script to the `node/` directory:

   ```bash
   cp web-to-markdown.js ~/dot-scripts/node/
   ```

2. Copy the launcher to the `bin/` directory:

   ```bash
   cp web-to-markdown ~/dot-scripts/bin/
   chmod +x ~/dot-scripts/bin/web-to-markdown
   ```

3. Make sure `~/dot-scripts/bin` is in your PATH:

   ```bash
   export PATH="$HOME/dot-scripts/bin:$PATH"
   ```

## Usage

### Basic Usage

Convert a single webpage:

```bash
web-to-markdown https://example.com
```

Convert multiple webpages:

```bash
web-to-markdown https://example.com https://example.org https://example.net
```

### Using a URL List File

Create a file with URLs (one per line):

```bash
# urls.txt
https://example.com
https://example.org
# This is a comment - lines starting with # are ignored
https://example.net
```

Then run:

```bash
web-to-markdown -f urls.txt
```

### Specify Output Directory

```bash
web-to-markdown -o ./my-docs https://example.com
```

### Combined Options

```bash
web-to-markdown -f urls.txt -o ./saved-pages
```

## Options

| Option | Description |
|--------|-------------|
| `-f, --file <path>` | Read URLs from file (one per line) |
| `-o, --output <dir>` | Output directory (default: `./markdown-output`) |
| `-h, --help` | Show help message |

## Output

- Files are saved as `.md` (markdown) files
- Filenames are automatically generated from the URL path
- Output directory is created automatically if it doesn't exist
- Existing files with the same name will be overwritten

## Examples

### Example 1: Save Documentation Pages

```bash
# Create a list of documentation URLs
cat > docs.txt << EOF
https://nodejs.org/api/fs.html
https://nodejs.org/api/http.html
https://nodejs.org/api/path.html
EOF

# Convert all pages to markdown
web-to-markdown -f docs.txt -o ./node-docs
```

### Example 2: Archive Blog Posts

```bash
web-to-markdown -o ./blog-archive \
  https://blog.example.com/post-1 \
  https://blog.example.com/post-2 \
  https://blog.example.com/post-3
```

### Example 3: Quick Single Page Conversion

```bash
web-to-markdown https://github.com/torvalds/linux
```

## Notes

- The script requires Node.js to be installed
- Handles HTTP and HTTPS URLs
- Follows redirects automatically
- Removes script and style tags from HTML
- Preserves most common markdown formatting elements
- Large pages may take a moment to process

## Supported HTML Elements

The converter handles:

- Headings (h1-h6)
- Paragraphs
- Links
- Images (with alt text)
- Bold and italic text
- Code blocks and inline code
- Ordered and unordered lists
- Blockquotes
- Horizontal rules
- Line breaks

## Troubleshooting

**URLs file not found:**

- Check the file path is correct
- Use absolute path if needed: `/full/path/to/urls.txt`

**Permission denied:**

- Ensure the launcher script is executable: `chmod +x ~/dot-scripts/bin/web-to-markdown`

**HTTP errors:**

- Some websites may block automated requests
- Check if the URL is accessible in a browser
- Some sites require authentication (not supported)

## File Format Example

The URLs file format is simple - one URL per line:

```
https://example.com
https://example.org/page1
https://example.net/docs/index.html

# Comments start with #
# Blank lines are ignored

https://example.com/another-page
```

## Integration with dot-scripts

This script follows the dot-scripts philosophy:

- Implementation in `node/` directory (JavaScript/Node.js)
- Launcher in `bin/` directory (shell wrapper)
- Documentation in `markdown/` directory
- Simple, single-purpose utility
- No extensions needed in command name
