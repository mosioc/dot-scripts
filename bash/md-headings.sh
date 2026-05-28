#!/bin/bash
output_file="headings_$(date +%Y%m%d_%H%M%S).txt"

echo "=== Headings from all markdown files ===" > "$output_file"
echo >> "$output_file"

for file in *.md; do
    if [ -f "$file" ]; then
        echo "📄 $file" >> "$output_file"
        echo "-----------------------------------" >> "$output_file"
        grep '^#' "$file" >> "$output_file"
        echo >> "$output_file"
    fi
done

echo "Headings saved to: $output_file"
echo "View with: cat $output_file"
echo "Or: less $output_file"