#!/usr/bin/env node

/**
 * web-to-markdown
 * Reads a list of webpages and extracts their content in markdown format
 */

const https = require('https');
const http = require('http');
const fs = require('fs');
const path = require('path');
const { URL } = require('url');

// ANSI color codes for terminal output
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  red: '\x1b[31m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m'
};

/**
 * Simple HTML to Markdown converter
 */
class HtmlToMarkdown {
  constructor(html) {
    this.html = html;
  }

  convert() {
    let markdown = this.html;

    // Remove script and style tags
    markdown = markdown.replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '');
    markdown = markdown.replace(/<style\b[^<]*(?:(?!<\/style>)<[^<]*)*<\/style>/gi, '');
    
    // Extract title
    const titleMatch = markdown.match(/<title[^>]*>(.*?)<\/title>/i);
    const title = titleMatch ? titleMatch[1].trim() : '';

    // Convert headings
    markdown = markdown.replace(/<h1[^>]*>(.*?)<\/h1>/gi, '\n# $1\n');
    markdown = markdown.replace(/<h2[^>]*>(.*?)<\/h2>/gi, '\n## $1\n');
    markdown = markdown.replace(/<h3[^>]*>(.*?)<\/h3>/gi, '\n### $1\n');
    markdown = markdown.replace(/<h4[^>]*>(.*?)<\/h4>/gi, '\n#### $1\n');
    markdown = markdown.replace(/<h5[^>]*>(.*?)<\/h5>/gi, '\n##### $1\n');
    markdown = markdown.replace(/<h6[^>]*>(.*?)<\/h6>/gi, '\n###### $1\n');

    // Convert paragraphs
    markdown = markdown.replace(/<p[^>]*>(.*?)<\/p>/gi, '\n$1\n');

    // Convert links
    markdown = markdown.replace(/<a[^>]*href=["']([^"']*)["'][^>]*>(.*?)<\/a>/gi, '[$2]($1)');

    // Convert images
    markdown = markdown.replace(/<img[^>]*alt=["']([^"']*)["'][^>]*src=["']([^"']*)["'][^>]*>/gi, '![$1]($2)');
    markdown = markdown.replace(/<img[^>]*src=["']([^"']*)["'][^>]*alt=["']([^"']*)["'][^>]*>/gi, '![$2]($1)');
    markdown = markdown.replace(/<img[^>]*src=["']([^"']*)["'][^>]*>/gi, '![]($1)');

    // Convert bold and italic
    markdown = markdown.replace(/<strong[^>]*>(.*?)<\/strong>/gi, '**$1**');
    markdown = markdown.replace(/<b[^>]*>(.*?)<\/b>/gi, '**$1**');
    markdown = markdown.replace(/<em[^>]*>(.*?)<\/em>/gi, '*$1*');
    markdown = markdown.replace(/<i[^>]*>(.*?)<\/i>/gi, '*$1*');

    // Convert code
    markdown = markdown.replace(/<code[^>]*>(.*?)<\/code>/gi, '`$1`');
    markdown = markdown.replace(/<pre[^>]*>(.*?)<\/pre>/gi, '\n```\n$1\n```\n');

    // Convert lists
    markdown = markdown.replace(/<ul[^>]*>(.*?)<\/ul>/gis, (match, content) => {
      return '\n' + content.replace(/<li[^>]*>(.*?)<\/li>/gi, '- $1\n') + '\n';
    });
    markdown = markdown.replace(/<ol[^>]*>(.*?)<\/ol>/gis, (match, content) => {
      let counter = 0;
      return '\n' + content.replace(/<li[^>]*>(.*?)<\/li>/gi, () => {
        counter++;
        return `${counter}. $1\n`;
      }) + '\n';
    });

    // Convert line breaks
    markdown = markdown.replace(/<br\s*\/?>/gi, '\n');
    markdown = markdown.replace(/<hr\s*\/?>/gi, '\n---\n');

    // Convert blockquotes
    markdown = markdown.replace(/<blockquote[^>]*>(.*?)<\/blockquote>/gis, (match, content) => {
      return '\n> ' + content.trim().replace(/\n/g, '\n> ') + '\n';
    });

    // Remove remaining HTML tags
    markdown = markdown.replace(/<[^>]+>/g, '');

    // Decode HTML entities
    markdown = markdown
      .replace(/&nbsp;/g, ' ')
      .replace(/&amp;/g, '&')
      .replace(/&lt;/g, '<')
      .replace(/&gt;/g, '>')
      .replace(/&quot;/g, '"')
      .replace(/&#39;/g, "'")
      .replace(/&apos;/g, "'");

    // Clean up whitespace
    markdown = markdown.replace(/\n{3,}/g, '\n\n');
    markdown = markdown.trim();

    // Add title if found
    if (title) {
      markdown = `# ${title}\n\n${markdown}`;
    }

    return markdown;
  }
}

/**
 * Fetch URL content
 */
function fetchUrl(url) {
  return new Promise((resolve, reject) => {
    const parsedUrl = new URL(url);
    const client = parsedUrl.protocol === 'https:' ? https : http;

    const options = {
      headers: {
        'User-Agent': 'Mozilla/5.0 (compatible; WebToMarkdown/1.0)'
      }
    };

    client.get(url, options, (res) => {
      if (res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {
        // Handle redirects
        const redirectUrl = new URL(res.headers.location, url).href;
        fetchUrl(redirectUrl).then(resolve).catch(reject);
        return;
      }

      if (res.statusCode !== 200) {
        reject(new Error(`HTTP ${res.statusCode}: ${res.statusMessage}`));
        return;
      }

      let data = '';
      res.setEncoding('utf8');
      res.on('data', (chunk) => { data += chunk; });
      res.on('end', () => resolve(data));
    }).on('error', reject);
  });
}

/**
 * Generate filename from URL
 */
function generateFilename(url) {
  const parsedUrl = new URL(url);
  let filename = parsedUrl.pathname
    .replace(/^\//, '')
    .replace(/\//g, '_')
    .replace(/[^a-zA-Z0-9_-]/g, '_');
  
  if (!filename || filename === '_') {
    filename = parsedUrl.hostname.replace(/\./g, '_');
  }
  
  filename = filename.replace(/_+/g, '_').replace(/^_|_$/g, '');
  
  return filename + '.md';
}

/**
 * Process a single URL
 */
async function processUrl(url, outputDir, options) {
  try {
    console.log(`${colors.blue}Fetching:${colors.reset} ${url}`);
    
    const html = await fetchUrl(url);
    const converter = new HtmlToMarkdown(html);
    const markdown = converter.convert();
    
    const filename = options.filename || generateFilename(url);
    const filepath = path.join(outputDir, filename);
    
    fs.writeFileSync(filepath, markdown, 'utf8');
    
    console.log(`${colors.green}✓ Saved:${colors.reset} ${filepath}`);
    return { success: true, url, filepath };
  } catch (error) {
    console.error(`${colors.red}✗ Failed:${colors.reset} ${url}`);
    console.error(`  ${colors.red}Error:${colors.reset} ${error.message}`);
    return { success: false, url, error: error.message };
  }
}

/**
 * Read URLs from file
 */
function readUrlsFromFile(filepath) {
  const content = fs.readFileSync(filepath, 'utf8');
  return content
    .split('\n')
    .map(line => line.trim())
    .filter(line => line && !line.startsWith('#'));
}

/**
 * Display help message
 */
function displayHelp() {
  console.log(`
${colors.bright}web-to-markdown${colors.reset} - Convert webpages to markdown files

${colors.bright}USAGE:${colors.reset}
  web-to-markdown [options] <url1> [url2] [url3] ...
  web-to-markdown [options] -f <file-with-urls>

${colors.bright}OPTIONS:${colors.reset}
  -f, --file <path>       Read URLs from file (one per line)
  -o, --output <dir>      Output directory (default: ./markdown-output)
  -h, --help              Show this help message

${colors.bright}EXAMPLES:${colors.reset}
  # Convert single URL
  web-to-markdown https://example.com

  # Convert multiple URLs
  web-to-markdown https://example.com https://example.org

  # Read URLs from file
  web-to-markdown -f urls.txt

  # Specify output directory
  web-to-markdown -o ./docs https://example.com

  # URLs file format (urls.txt):
  https://example.com
  https://example.org
  # This is a comment
  https://example.net
`);
}

/**
 * Main function
 */
async function main() {
  const args = process.argv.slice(2);

  if (args.length === 0 || args.includes('-h') || args.includes('--help')) {
    displayHelp();
    process.exit(0);
  }

  let urls = [];
  let outputDir = './markdown-output';
  let urlFile = null;

  // Parse arguments
  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    
    if (arg === '-f' || arg === '--file') {
      urlFile = args[++i];
    } else if (arg === '-o' || arg === '--output') {
      outputDir = args[++i];
    } else if (!arg.startsWith('-')) {
      urls.push(arg);
    }
  }

  // Read URLs from file if specified
  if (urlFile) {
    if (!fs.existsSync(urlFile)) {
      console.error(`${colors.red}Error:${colors.reset} File not found: ${urlFile}`);
      process.exit(1);
    }
    const fileUrls = readUrlsFromFile(urlFile);
    urls = urls.concat(fileUrls);
  }

  if (urls.length === 0) {
    console.error(`${colors.red}Error:${colors.reset} No URLs provided`);
    displayHelp();
    process.exit(1);
  }

  // Create output directory
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
    console.log(`${colors.cyan}Created output directory:${colors.reset} ${outputDir}\n`);
  }

  console.log(`${colors.bright}Processing ${urls.length} URL(s)...${colors.reset}\n`);

  // Process all URLs
  const results = [];
  for (const url of urls) {
    const result = await processUrl(url, outputDir, {});
    results.push(result);
  }

  // Summary
  console.log(`\n${colors.bright}SUMMARY:${colors.reset}`);
  const successful = results.filter(r => r.success).length;
  const failed = results.filter(r => !r.success).length;
  
  console.log(`${colors.green}✓ Successful:${colors.reset} ${successful}`);
  if (failed > 0) {
    console.log(`${colors.red}✗ Failed:${colors.reset} ${failed}`);
  }
  console.log(`${colors.cyan}Output directory:${colors.reset} ${path.resolve(outputDir)}`);

  process.exit(failed > 0 ? 1 : 0);
}

// Run the script
if (require.main === module) {
  main().catch(error => {
    console.error(`${colors.red}Fatal error:${colors.reset}`, error);
    process.exit(1);
  });
}