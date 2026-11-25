#!/bin/sh
# Create today's diary entry from the template (or show it if it already exists).
set -e
dir="$(cd "$(dirname "$0")" && pwd)"
today="$(date +%Y-%m-%d)"
file="$dir/entries/$today.md"
mkdir -p "$dir/entries"
if [ -e "$file" ]; then
  echo "Already exists: $file"
else
  sed "s/{{DATE}}/$today/" "$dir/TEMPLATE.md" > "$file"
  echo "Created: $file"
fi
