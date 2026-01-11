#!/bin/bash
#
# generate-icons.sh - Generate app icons from SVG
#
# Requires: ImageMagick (convert) or librsvg (rsvg-convert)
#

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SVG_FILE="${SCRIPT_DIR}/icon.svg"
OUTPUT_DIR="${SCRIPT_DIR}"

echo "Generating icons from ${SVG_FILE}..."

# Check for conversion tool
if command -v rsvg-convert &> /dev/null; then
    CONVERT="rsvg-convert"
elif command -v convert &> /dev/null; then
    CONVERT="imagemagick"
else
    echo "Error: Need rsvg-convert (librsvg) or ImageMagick (convert)"
    echo "Install with:"
    echo "  macOS:  brew install librsvg"
    echo "  Ubuntu: sudo apt install librsvg2-bin"
    exit 1
fi

# Generate PNG icons at various sizes
SIZES="16 32 48 64 128 256 512 1024"

for size in $SIZES; do
    echo "  Generating ${size}x${size}..."
    if [ "$CONVERT" = "rsvg-convert" ]; then
        rsvg-convert -w $size -h $size "$SVG_FILE" -o "${OUTPUT_DIR}/icon-${size}.png"
    else
        convert -background none -resize ${size}x${size} "$SVG_FILE" "${OUTPUT_DIR}/icon-${size}.png"
    fi
done

# Copy main icon
cp "${OUTPUT_DIR}/icon-512.png" "${OUTPUT_DIR}/icon.png"

# Generate tray icon (16x16)
cp "${OUTPUT_DIR}/icon-16.png" "${OUTPUT_DIR}/tray-icon.png"

# Generate macOS .icns (if iconutil available - macOS only)
if command -v iconutil &> /dev/null; then
    echo "  Generating macOS .icns..."
    ICONSET="${OUTPUT_DIR}/icon.iconset"
    mkdir -p "$ICONSET"
    
    cp "${OUTPUT_DIR}/icon-16.png" "${ICONSET}/icon_16x16.png"
    cp "${OUTPUT_DIR}/icon-32.png" "${ICONSET}/icon_16x16@2x.png"
    cp "${OUTPUT_DIR}/icon-32.png" "${ICONSET}/icon_32x32.png"
    cp "${OUTPUT_DIR}/icon-64.png" "${ICONSET}/icon_32x32@2x.png"
    cp "${OUTPUT_DIR}/icon-128.png" "${ICONSET}/icon_128x128.png"
    cp "${OUTPUT_DIR}/icon-256.png" "${ICONSET}/icon_128x128@2x.png"
    cp "${OUTPUT_DIR}/icon-256.png" "${ICONSET}/icon_256x256.png"
    cp "${OUTPUT_DIR}/icon-512.png" "${ICONSET}/icon_256x256@2x.png"
    cp "${OUTPUT_DIR}/icon-512.png" "${ICONSET}/icon_512x512.png"
    cp "${OUTPUT_DIR}/icon-1024.png" "${ICONSET}/icon_512x512@2x.png"
    
    iconutil -c icns "$ICONSET" -o "${OUTPUT_DIR}/icon.icns"
    rm -rf "$ICONSET"
fi

# Generate Windows .ico (if ImageMagick available)
if command -v convert &> /dev/null; then
    echo "  Generating Windows .ico..."
    convert "${OUTPUT_DIR}/icon-16.png" "${OUTPUT_DIR}/icon-32.png" "${OUTPUT_DIR}/icon-48.png" "${OUTPUT_DIR}/icon-64.png" "${OUTPUT_DIR}/icon-128.png" "${OUTPUT_DIR}/icon-256.png" "${OUTPUT_DIR}/icon.ico"
fi

echo "Done! Icons generated in ${OUTPUT_DIR}"
ls -la "${OUTPUT_DIR}"/*.png "${OUTPUT_DIR}"/*.ico "${OUTPUT_DIR}"/*.icns 2>/dev/null
