#!/bin/bash
cd "$(dirname "$1")"
mkdir -p "$1.to_svg.d"
cd "$1.to_svg.d"
pdf2svg "../$1" "%d.svg" all
for file in *.svg; do
	sed -i 's/symbol/g/g' "$file"
done
