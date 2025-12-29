#!/usr/bin/env python3

import os
import re
import sys
import argparse
from pathlib import Path


# colors
class Colors:
    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    YELLOW = "\033[1;33m"
    BLUE = "\033[0;34m"
    CYAN = "\033[0;36m"
    DIM = "\033[2m"
    BOLD = "\033[1m"
    RESET = "\033[0m"


def show_help():
    help_text = f"""
{Colors.BLUE}{Colors.BOLD}rename-files{Colors.RESET} - Batch rename files with patterns

{Colors.YELLOW}Usage:{Colors.RESET}
  rename-files [options] <pattern> <replacement>

{Colors.YELLOW}Options:{Colors.RESET}
  -d, --dir <path>        Directory to process (default: current)
  -r, --regex             Use regex patterns
  -e, --ext <ext>         Only rename files with extension
  -n, --dry-run           Show what would be renamed without doing it
  -i, --interactive       Ask for confirmation before each rename
  --recursive             Process subdirectories recursively
  --case-insensitive      Case-insensitive matching
  -h, --help              Show this help message

{Colors.YELLOW}Built-in patterns:{Colors.RESET}
  --lowercase             Convert to lowercase
  --uppercase             Convert to uppercase
  --spaces-to-dash        Replace spaces with dashes
  --spaces-to-underscore  Replace spaces with underscores
  --remove-spaces         Remove all spaces
  --add-prefix <text>     Add prefix to filename
  --add-suffix <text>     Add suffix before extension
  --number                Add sequential numbers (001, 002, etc.)

{Colors.YELLOW}Examples:{Colors.RESET}
  # Simple find and replace
  rename-files "photo" "image"
  
  # Regex pattern
  rename-files -r "IMG_(\d+)" "Photo_\\1"
  
  # Only .jpg files
  rename-files -e jpg "DSC" "Photo"
  
  # Convert to lowercase
  rename-files --lowercase
  
  # Replace spaces with dashes
  rename-files --spaces-to-dash
  
  # Add prefix
  rename-files --add-prefix "2024_"
  
  # Add sequential numbers
  rename-files --number
  
  # Dry run to preview
  rename-files -n "old" "new"
  
  # Interactive mode
  rename-files -i --lowercase

{Colors.YELLOW}Regex examples:{Colors.RESET}
  rename-files -r "^(\d+)" "file_\\1"         # Add prefix to numbers
  rename-files -r "(\w+)_(\w+)" "\\2_\\1"     # Swap parts
  rename-files -r "\s+" "_"                    # Replace spaces with underscore
"""
    print(help_text)


def get_files(directory, extension=None, recursive=False):
    """get list of files to process"""
    files = []
    path = Path(directory)

    if recursive:
        pattern = "**/*" if not extension else f"**/*.{extension}"
        files = [f for f in path.glob(pattern) if f.is_file()]
    else:
        pattern = "*" if not extension else f"*.{extension}"
        files = [f for f in path.glob(pattern) if f.is_file()]

    return sorted(files)


def apply_pattern(
    filename, pattern, replacement, use_regex=False, case_insensitive=False
):
    """apply renaming pattern to filename"""
    if use_regex:
        flags = re.IGNORECASE if case_insensitive else 0
        new_name = re.sub(pattern, replacement, filename, flags=flags)
    else:
        if case_insensitive:
            # case-insensitive simple replace
            pattern_re = re.compile(re.escape(pattern), re.IGNORECASE)
            new_name = pattern_re.sub(replacement, filename)
        else:
            new_name = filename.replace(pattern, replacement)

    return new_name


def rename_with_builtin(files, mode, prefix=None, suffix=None):
    """apply built-in renaming patterns"""
    renames = []

    for i, filepath in enumerate(files, 1):
        old_name = filepath.name
        stem = filepath.stem
        ext = filepath.suffix

        if mode == "lowercase":
            new_name = old_name.lower()
        elif mode == "uppercase":
            new_name = old_name.upper()
        elif mode == "spaces-to-dash":
            new_name = old_name.replace(" ", "-")
        elif mode == "spaces-to-underscore":
            new_name = old_name.replace(" ", "_")
        elif mode == "remove-spaces":
            new_name = old_name.replace(" ", "")
        elif mode == "add-prefix" and prefix:
            new_name = prefix + old_name
        elif mode == "add-suffix" and suffix:
            new_name = stem + suffix + ext
        elif mode == "number":
            new_name = f"{i:03d}_{old_name}"
        else:
            continue

        if new_name != old_name:
            renames.append((filepath, filepath.parent / new_name))

    return renames


def rename_with_pattern(
    files, pattern, replacement, use_regex=False, case_insensitive=False
):
    """rename files using pattern matching"""
    renames = []

    for filepath in files:
        old_name = filepath.name
        new_name = apply_pattern(
            old_name, pattern, replacement, use_regex, case_insensitive
        )

        if new_name != old_name:
            renames.append((filepath, filepath.parent / new_name))

    return renames


def preview_renames(renames):
    """show preview of what will be renamed"""
    if not renames:
        print(f"{Colors.YELLOW}No files to rename{Colors.RESET}")
        return

    print(f"\n{Colors.BOLD}{Colors.BLUE}Preview:{Colors.RESET}")
    print(f"{Colors.DIM}{'─' * 70}{Colors.RESET}\n")

    for old_path, new_path in renames:
        print(f"{Colors.DIM}→{Colors.RESET} {Colors.RED}{old_path.name}{Colors.RESET}")
        print(f"  {Colors.GREEN}{new_path.name}{Colors.RESET}\n")

    print(f"{Colors.DIM}{'─' * 70}{Colors.RESET}")
    print(f"{Colors.CYAN}Total: {len(renames)} file(s) to rename{Colors.RESET}\n")


def perform_renames(renames, interactive=False):
    """actually rename the files"""
    if not renames:
        print(f"{Colors.YELLOW}No files to rename{Colors.RESET}")
        return 0

    success_count = 0
    skip_count = 0
    error_count = 0

    for old_path, new_path in renames:
        # check if target exists
        if new_path.exists():
            print(f"{Colors.RED}✗ Skip: {old_path.name}{Colors.RESET}")
            print(f"  {Colors.DIM}Target already exists: {new_path.name}{Colors.RESET}")
            skip_count += 1
            continue

        # interactive confirmation
        if interactive:
            print(f"\n{Colors.CYAN}Rename:{Colors.RESET}")
            print(f"  {Colors.DIM}From:{Colors.RESET} {old_path.name}")
            print(f"  {Colors.DIM}To:{Colors.RESET}   {new_path.name}")
            response = input(
                f"{Colors.YELLOW}Continue? (y/n/q): {Colors.RESET}"
            ).lower()

            if response == "q":
                print(f"\n{Colors.YELLOW}Aborted by user{Colors.RESET}")
                break
            elif response != "y":
                skip_count += 1
                continue

        # perform rename
        try:
            old_path.rename(new_path)
            print(f"{Colors.GREEN}✓{Colors.RESET} {old_path.name} → {new_path.name}")
            success_count += 1
        except Exception as e:
            print(f"{Colors.RED}✗ Error renaming {old_path.name}: {e}{Colors.RESET}")
            error_count += 1

    # summary
    print(f"\n{Colors.DIM}{'─' * 70}{Colors.RESET}")
    print(f"{Colors.GREEN}Renamed: {success_count}{Colors.RESET}", end="")
    if skip_count > 0:
        print(f" | {Colors.YELLOW}Skipped: {skip_count}{Colors.RESET}", end="")
    if error_count > 0:
        print(f" | {Colors.RED}Errors: {error_count}{Colors.RESET}", end="")
    print()

    return success_count


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("-h", "--help", action="store_true")
    parser.add_argument("-d", "--dir", default=".")
    parser.add_argument("-r", "--regex", action="store_true")
    parser.add_argument("-e", "--ext")
    parser.add_argument("-n", "--dry-run", action="store_true")
    parser.add_argument("-i", "--interactive", action="store_true")
    parser.add_argument("--recursive", action="store_true")
    parser.add_argument("--case-insensitive", action="store_true")

    # built-in patterns
    parser.add_argument("--lowercase", action="store_true")
    parser.add_argument("--uppercase", action="store_true")
    parser.add_argument("--spaces-to-dash", action="store_true")
    parser.add_argument("--spaces-to-underscore", action="store_true")
    parser.add_argument("--remove-spaces", action="store_true")
    parser.add_argument("--add-prefix")
    parser.add_argument("--add-suffix")
    parser.add_argument("--number", action="store_true")

    parser.add_argument("pattern", nargs="?")
    parser.add_argument("replacement", nargs="?")

    args = parser.parse_args()

    if args.help:
        show_help()
        return 0

    # check if directory exists
    if not os.path.isdir(args.dir):
        print(f"{Colors.RED}Error: Directory does not exist: {args.dir}{Colors.RESET}")
        return 1

    # get files
    files = get_files(args.dir, args.ext, args.recursive)

    if not files:
        print(f"{Colors.YELLOW}No files found{Colors.RESET}")
        return 0

    print(f"{Colors.BLUE}Found {len(files)} file(s){Colors.RESET}")

    # determine renaming mode
    renames = []

    if args.lowercase:
        renames = rename_with_builtin(files, "lowercase")
    elif args.uppercase:
        renames = rename_with_builtin(files, "uppercase")
    elif args.spaces_to_dash:
        renames = rename_with_builtin(files, "spaces-to-dash")
    elif args.spaces_to_underscore:
        renames = rename_with_builtin(files, "spaces-to-underscore")
    elif args.remove_spaces:
        renames = rename_with_builtin(files, "remove-spaces")
    elif args.add_prefix:
        renames = rename_with_builtin(files, "add-prefix", prefix=args.add_prefix)
    elif args.add_suffix:
        renames = rename_with_builtin(files, "add-suffix", suffix=args.add_suffix)
    elif args.number:
        renames = rename_with_builtin(files, "number")
    elif args.pattern and args.replacement:
        renames = rename_with_pattern(
            files, args.pattern, args.replacement, args.regex, args.case_insensitive
        )
    else:
        print(f"{Colors.RED}Error: No pattern specified{Colors.RESET}")
        print(f"{Colors.DIM}Use --help for usage information{Colors.RESET}")
        return 1

    # preview or execute
    if args.dry_run:
        preview_renames(renames)
    else:
        if not args.interactive:
            preview_renames(renames)
            response = input(
                f"\n{Colors.YELLOW}Proceed with rename? (y/n): {Colors.RESET}"
            ).lower()
            if response != "y":
                print(f"{Colors.YELLOW}Aborted{Colors.RESET}")
                return 0

        perform_renames(renames, args.interactive)

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Aborted by user{Colors.RESET}")
        sys.exit(1)
