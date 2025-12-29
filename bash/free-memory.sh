#!/bin/bash

# colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
DIM='\033[2m'
BOLD='\033[1m'
RESET='\033[0m'

show_help() {
    cat << EOF
${BLUE}${BOLD}free-memory${RESET} - enhanced memory monitor & optimizer

${YELLOW}Usage:${RESET}
  free-memory [options]

${YELLOW}Options:${RESET}
  -h, --help       Show this help message
  -c, --clear      Clear page cache (safe)
  -s, --swap       Clear swap space (moves swap to ram)
  -a, --all        Clear everything (cache + swap)
  -w, --watch      Watch mode (refresh every 2s)

${YELLOW}Note:${RESET}
  swap clearing will be aborted if your available ram is less than used swap
  to prevent system freezing (oom killer).
EOF
}

# optimized bytes formatting (reduces awk calls)
format_bytes() {
    local bytes=$1
    if (( bytes < 1024 )); then
        echo "${bytes}B"
    elif (( bytes < 1048576 )); then
        echo "$((bytes / 1024))KB"
    elif (( bytes < 1073741824 )); then
        echo "$((bytes / 1048576))MB"
    else
        awk "BEGIN {printf \"%.2fGB\", $bytes / 1073741824}"
    fi
}

get_memory_info() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # linux /proc/meminfo parsing
        mem_total=$(grep MemTotal /proc/meminfo | awk '{print $2 * 1024}')
        mem_free=$(grep MemFree /proc/meminfo | awk '{print $2 * 1024}')
        mem_cached=$(grep "^Cached:" /proc/meminfo | awk '{print $2 * 1024}')
        mem_buffers=$(grep Buffers /proc/meminfo | awk '{print $2 * 1024}')
        mem_available=$(grep MemAvailable /proc/meminfo | awk '{print $2 * 1024}')
        swap_total=$(grep SwapTotal /proc/meminfo | awk '{print $2 * 1024}')
        swap_free=$(grep SwapFree /proc/meminfo | awk '{print $2 * 1024}')
        
        mem_used=$((mem_total - mem_available))
        swap_used=$((swap_total - swap_free))
        
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macos vm_stat parsing
        page_size=$(sysctl -n hw.pagesize)
        vm_stats=$(vm_stat)
        pages_free=$(echo "$vm_stats" | awk '/Pages free/ {print $3}' | tr -d '.')
        pages_active=$(echo "$vm_stats" | awk '/Pages active/ {print $3}' | tr -d '.')
        pages_inactive=$(echo "$vm_stats" | awk '/Pages inactive/ {print $3}' | tr -d '.')
        pages_wired=$(echo "$vm_stats" | awk '/Pages wired down/ {print $4}' | tr -d '.')
        pages_compressed=$(echo "$vm_stats" | awk '/Pages occupied by compressor/ {print $5}' | tr -d '.')
        
        mem_total=$(sysctl -n hw.memsize)
        mem_used=$(( (pages_active + pages_wired + pages_compressed) * page_size ))
        mem_free=$((pages_free * page_size))
        mem_cached=$((pages_inactive * page_size))
        mem_available=$((mem_total - mem_used))
        mem_buffers=0
        
        # macos swap
        swap_info=$(sysctl -n vm.swapusage)
        swap_total=$(echo "$swap_info" | awk '{print $3}' | tr -d 'M' | awk '{print $1 * 1024 * 1024}')
        swap_used=$(echo "$swap_info" | awk '{print $6}' | tr -d 'M' | awk '{print $1 * 1024 * 1024}')
        swap_free=$((swap_total - swap_used))
    fi
    
    mem_used_percent=$(awk "BEGIN {printf \"%.1f\", $mem_used * 100 / $mem_total}")
    [ "$swap_total" -gt 0 ] && swap_used_percent=$(awk "BEGIN {printf \"%.1f\", $swap_used * 100 / $swap_total}") || swap_used_percent=0
}

draw_bar() {
    local percent=$1
    local width=40
    local filled=$(awk "BEGIN {printf \"%.0f\", $percent * $width / 100}")
    local empty=$((width - filled))
    
    local color=$GREEN
    (( $(awk "BEGIN {print ($percent > 70)}") )) && color=$YELLOW
    (( $(awk "BEGIN {print ($percent > 90)}") )) && color=$RED
    
    echo -ne "${color}"
    printf '%*s' "$filled" | tr ' ' '█'
    echo -ne "${DIM}"
    printf '%*s' "$empty" | tr ' ' '░'
    echo -ne "${RESET}"
}

display_memory() {
    get_memory_info
    echo -e "\n${BOLD}${BLUE}System Memory Status${RESET}"
    echo -e "${DIM}────────────────────────────────────────────────────────${RESET}"
    
    echo -e "${CYAN}RAM:${RESET}"
    echo -ne "  $(draw_bar "$mem_used_percent")"
    printf " ${BOLD}%s%%${RESET}\n" "$mem_used_percent"
    printf "  Used: %-12s Available: %-12s\n" "$(format_bytes $mem_used)" "$(format_bytes $mem_available)"
    printf "  Free: %-12s Cached:    %-12s\n" "$(format_bytes $mem_free)" "$(format_bytes $mem_cached)"

    if [ "$swap_total" -gt 0 ]; then
        echo -e "\n${CYAN}Swap:${RESET}"
        echo -ne "  $(draw_bar "$swap_used_percent")"
        printf " ${BOLD}%s%%${RESET}\n" "$swap_used_percent"
        printf "  Used: %-12s Total:     %-12s\n" "$(format_bytes $swap_used)" "$(format_bytes $swap_total)"
    fi
    echo -e "${DIM}────────────────────────────────────────────────────────${RESET}"
}

clear_cache() {
    echo -e "${YELLOW}Requesting sudo to clear cache...${RESET}"
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        sync && echo 3 | sudo tee /proc/sys/vm/drop_caches > /dev/null
    else
        sudo purge
    fi
    echo -e "${GREEN}✓ cache cleared successfully${RESET}"
}

clear_swap() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        get_memory_info
        if [ "$mem_available" -le "$swap_used" ]; then
            echo -e "${RED}⚠ ABORTED: not enough free RAM to dump swap (${swap_used} used).${RESET}"
            return 1
        fi
        echo -e "${YELLOW}flushing swap into RAM... (this may take a moment)${RESET}"
        sudo swapoff -a && sudo swapon -a
        echo -e "${GREEN}✓ swap cleared successfully${RESET}"
    else
        echo -e "${DIM}note: macos manages swap dynamically; manual clear not required.${RESET}"
    fi
}

main() {
    local do_cache=false do_swap=false do_watch=false

    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help) show_help; exit 0 ;;
            -c|--clear) do_cache=true; shift ;;
            -s|--swap) do_swap=true; shift ;;
            -a|--all) do_cache=true; do_swap=true; shift ;;
            -w|--watch) do_watch=true; shift ;;
            *) echo "Unknown option: $1"; exit 1 ;;
        esac
    done

    if [ "$do_watch" = true ]; then
        clear
        while true; do
            tput cup 0 0
            display_memory
            echo -e "${DIM}press ctrl+c to exit${RESET}"
            sleep 2
        done
    fi

    display_memory
    [ "$do_cache" = true ] && (echo ""; clear_cache)
    [ "$do_swap" = true ] && (echo ""; clear_swap)
    
    if [ "$do_cache" = true ] || [ "$do_swap" = true ]; then
        echo -e "\n${BOLD}Updated State:${RESET}"
        display_memory
    fi
}

main "$@"