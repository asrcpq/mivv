#!/bin/bash
cd "$(dirname "$1")"
mkdir -p "$1.to_svg.d"
cd "$1.to_svg.d"
pdf2svg "../$1" "%d.svg" all
for file in *.svg; do
	geom="$(sed -n '2p' "$file" | grep -o 'width="[0-9]*pt" height="[0-9]*pt"')"
	sed -i "s/symbol/g/g;2a <rect $geom fill=\"white\"/>" "$file"
done
