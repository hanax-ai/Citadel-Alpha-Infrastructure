#!/bin/bash

# Internal Link Audit Script
# This script checks all markdown files for broken internal links

echo "🔍 Internal Link Audit Report"
echo "=============================="
echo ""

# Base directory
BASE_DIR="/home/agent0/Citadel-Alpha-Infrastructure"
cd "$BASE_DIR"

# Initialize counters
TOTAL_LINKS=0
BROKEN_LINKS=0
FIXED_LINKS=0

echo "📊 Link Audit Summary:"
echo "----------------------"

# Function to check if a link target exists
check_link() {
    local link_path="$1"
    local source_file="$2"
    local source_dir=$(dirname "$source_file")
    
    # Handle relative links
    if [[ "$link_path" =~ ^\./ ]]; then
        # Remove the leading ./
        link_path="${link_path#./}"
        full_path="$source_dir/$link_path"
    elif [[ "$link_path" =~ ^\.\.\/ ]]; then
        # Handle ../
        full_path="$source_dir/$link_path"
    elif [[ "$link_path" =~ ^/ ]]; then
        # Absolute path from root
        full_path="$link_path"
    else
        # Relative path
        full_path="$source_dir/$link_path"
    fi
    
    # Normalize the path
    full_path=$(realpath -m "$full_path" 2>/dev/null)
    
    if [[ -f "$full_path" || -d "$full_path" ]]; then
        return 0  # Link is valid
    else
        return 1  # Link is broken
    fi
}

# Find all markdown files and check their links
while IFS= read -r -d '' file; do
    echo "📄 Checking: $file"
    
    # Extract markdown links using grep
    while IFS= read -r line; do
        if [[ -n "$line" ]]; then
            TOTAL_LINKS=$((TOTAL_LINKS + 1))
            link_text=$(echo "$line" | sed 's/.*\[\([^]]*\)\](\([^)]*\)).*/\1/')
            link_path=$(echo "$line" | sed 's/.*\[\([^]]*\)\](\([^)]*\)).*/\2/')
            
            # Skip external links (http, https, mailto, etc.)
            if [[ "$link_path" =~ ^https?:// ]] || [[ "$link_path" =~ ^mailto: ]] || [[ "$link_path" =~ ^ftp:// ]]; then
                continue
            fi
            
            # Check if link exists
            if ! check_link "$link_path" "$file"; then
                echo "  ❌ BROKEN: [$link_text]($link_path)"
                BROKEN_LINKS=$((BROKEN_LINKS + 1))
            else
                echo "  ✅ VALID: [$link_text]($link_path)"
            fi
        fi
    done < <(grep -oP '\[[^\]]*\]\([^)]*\)' "$file" 2>/dev/null || true)
    
done < <(find "$BASE_DIR" -name "*.md" -not -path "*/X-Archive/*" -not -path "*/.git/*" -print0)

echo ""
echo "📈 Final Report:"
echo "=================="
echo "Total links found: $TOTAL_LINKS"
echo "Broken links: $BROKEN_LINKS"
echo "Valid links: $((TOTAL_LINKS - BROKEN_LINKS))"
echo ""

if [ $BROKEN_LINKS -gt 0 ]; then
    echo "❌ $BROKEN_LINKS broken links found that need to be fixed."
    exit 1
else
    echo "✅ All internal links are valid!"
    exit 0
fi
