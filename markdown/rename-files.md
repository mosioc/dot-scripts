# Rename Files

**Installation:**

```bash
# Save files
# python/rename-files.py 
# bin/rename-files 

# Make executable
chmod +x python/rename-files.py
chmod +x bin/rename-files
```

**Usage examples:**

```bash
# Simple replacement
rename-files "photo" "image"

# Regex: add prefix to numbered files
rename-files -r "^(\d+)" "file_\1"

# Convert all to lowercase
rename-files --lowercase

# Replace spaces with dashes
rename-files --spaces-to-dash

# Add prefix to all files
rename-files --add-prefix "2024_"

# Number files sequentially (001_file.jpg, 002_file.jpg)
rename-files --number

# Only rename .jpg files
rename-files -e jpg "IMG" "Photo"

# Preview without changing (dry-run)
rename-files -n "old" "new"

# Interactive mode (confirm each)
rename-files -i --lowercase

# Recursive subdirectories
rename-files --recursive "old" "new"

# Show help
rename-files --help
```
