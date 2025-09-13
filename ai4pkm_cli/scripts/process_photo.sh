#!/bin/bash
# Photo Processing Script for PPP Workflow
# Extracts EXIF metadata and converts images to optimized JPEG format
# Skips work if outputs already exist
# Writes a full Markdown metadata report

set -euo pipefail

# Configuration
TARGET_SIZE_KB=100
OUTPUT_QUALITY=85
MIN_QUALITY=70
DEFAULT_WIDTH=1024
COLOR_PROFILE_PATH="/System/Library/ColorSync/Profiles/sRGB Profile.icc"

# Input validation
if [[ $# -ne 2 ]]; then
    echo "Usage: $0 <image_file> <output_dir>"
    exit 1
fi

input_file="$1"
DEST_DIR="$2"

input_basename=$(basename "$input_file")
input_name="${input_basename%.*}"
input_dir=$(dirname "$input_file")
input_ext="${input_basename##*.}"
input_ext_upper="$(printf '%s' "$input_ext" | tr '[:lower:]' '[:upper:]')"

if [[ ! -f "$input_file" ]]; then
    exit 1
fi

if ! command -v exiftool &> /dev/null; then
    exit 1
fi

if ! command -v sips &> /dev/null; then
    exit 1
fi

mkdir -p "$DEST_DIR"

# --- Quick pre-check: Skip if ANY processed version exists ---
# This avoids expensive exiftool call when files are already processed
quick_check=$(find "$DEST_DIR" -name "*${input_name}.*" -print -quit 2>/dev/null)
if [[ -n "$quick_check" ]]; then
    echo "Skipping: File already exists - $quick_check"
    exit 0
fi

# --- Extract EXIF ---
datetime_original=$(exiftool -DateTimeOriginal -d "%Y-%m-%d %H:%M:%S" -s3 "$input_file" 2>/dev/null || echo "")
date_created=$(exiftool -CreateDate -d "%Y-%m-%d %H:%M:%S" -s3 "$input_file" 2>/dev/null || echo "")
gps_lat=$(exiftool -GPSLatitude -s3 "$input_file" 2>/dev/null || echo "")
gps_lon=$(exiftool -GPSLongitude -s3 "$input_file" 2>/dev/null || echo "")
camera_make=$(exiftool -Make -s3 "$input_file" 2>/dev/null || echo "")
camera_model=$(exiftool -Model -s3 "$input_file" 2>/dev/null || echo "")
lens_model=$(exiftool -LensModel -s3 "$input_file" 2>/dev/null || echo "")
focal_length=$(exiftool -FocalLength -s3 "$input_file" 2>/dev/null || echo "")
iso=$(exiftool -ISO -s3 "$input_file" 2>/dev/null || echo "")
aperture=$(exiftool -FNumber -s3 "$input_file" 2>/dev/null || echo "")
shutter_speed=$(exiftool -ShutterSpeed -s3 "$input_file" 2>/dev/null || echo "")
image_size=$(exiftool -ImageSize -s3 "$input_file" 2>/dev/null || echo "")
file_size=$(exiftool -FileSize -s3 "$input_file" 2>/dev/null || echo "")

photo_datetime="$datetime_original"
if [[ -z "$photo_datetime" ]]; then
    photo_datetime="$date_created"
fi

if [[ -z "$photo_datetime" ]]; then
    photo_date="unknown"
    photo_time="unknown"
    photo_date_formatted="unknown"
else
    photo_date="${photo_datetime%% *}"
    photo_time="${photo_datetime##* }"
    photo_date_formatted="${photo_date}"  # Keep YYYY-MM-DD format
fi

# Skip check already done above - proceeding with processing

# Use YYYY-MM-DD format with space separator to match repo convention
final_md="${DEST_DIR}${photo_date_formatted} ${input_name}.md"
final_jpg="${DEST_DIR}${photo_date_formatted} ${input_name}.jpg"

# --- Metadata file (full markdown) ---
cat > "$final_md" << EOF
---
original_file: "$input_basename"
photo_date: "$photo_date"
photo_time: "$photo_time"
created: $(date -Iseconds)
---

# Photo Metadata: $input_basename

## Date & Time
- **Original DateTime**: $photo_datetime
- **Date**: $photo_date
- **Time**: $photo_time
- **Date (formatted)**: ${photo_date_formatted:-unknown}

## Location
EOF

if [[ -n "$gps_lat" && -n "$gps_lon" ]]; then
    cat >> "$final_md" << EOF
- **GPS Coordinates**: $gps_lat, $gps_lon
- **Map Link**: [View on Maps](https://maps.apple.com/?q=$gps_lat,$gps_lon)
EOF
else
    echo "- **GPS Coordinates**: Not available" >> "$final_md"
fi

cat >> "$final_md" << EOF

## Camera Info
- **Make**: ${camera_make:-N/A}
- **Model**: ${camera_model:-N/A}
- **Lens**: ${lens_model:-N/A}

## Settings
- **Focal Length**: ${focal_length:-N/A}
- **ISO**: ${iso:-N/A}
- **Aperture**: ${aperture:-N/A}
- **Shutter Speed**: ${shutter_speed:-N/A}

## File Info
- **Original Size**: $image_size
- **File Size**: $file_size

## Processing Notes
- Processed on: $(date)
- Target output size: <${TARGET_SIZE_KB}KB
- Conversion quality: ${OUTPUT_QUALITY}%

## Suggested Caption
_[Add descriptive caption here based on image content]_

## Photolog Integration
\`\`\`
Time: $photo_time
Caption: [Add caption]
File: ${photo_date_formatted:-YYYY-MM-DD} ${input_name}.jpg
\`\`\`
EOF

# --- Convert image ---
original_width=$(sips -g pixelWidth "$input_file" | awk '/pixelWidth:/ {print $2}')
original_height=$(sips -g pixelHeight "$input_file" | awk '/pixelHeight:/ {print $2}')

# Keep target_width = 1024 and set target_height same aspect ratio as original
target_width=$DEFAULT_WIDTH
target_height=$(( original_height * $DEFAULT_WIDTH / original_width ))

if [[ -f "$COLOR_PROFILE_PATH" ]]; then
  sips --matchTo "$COLOR_PROFILE_PATH" \
        -s format jpeg \
        -s formatOptions $OUTPUT_QUALITY \
        -Z $target_width \
        "$input_file" \
        --out "$final_jpg" >/dev/null
else
  sips -s format jpeg \
        -s formatOptions $OUTPUT_QUALITY \
        -Z $target_width \
        "$input_file" \
        --out "$final_jpg" >/dev/null
fi

exit 0
