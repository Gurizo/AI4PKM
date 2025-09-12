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
DEFAULT_WIDTH=1000
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

# --- Early skip check (by filename base) ---
final_base="${input_name}"
final_md="${DEST_DIR}/${final_base}.md"
final_jpg="${DEST_DIR}/${final_base}.jpg"

if [[ -f "$final_md" || -f "$final_jpg" ]]; then
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
    photo_date_compact="$input_name"
else
    photo_date="${photo_datetime%% *}"
    photo_time="${photo_datetime##* }"
    photo_date_compact="${photo_date//-/}"
fi

# Use EXIF-derived basename if possible
final_base="${photo_date_compact}"
final_md="${DEST_DIR}/${final_base}.md"
final_jpg="${DEST_DIR}/${final_base}.jpg"

# Skip if EXIF-based outputs already exist
if [[ -f "$final_md" || -f "$final_jpg" ]]; then
    exit 0
fi

# --- Metadata file (full markdown) ---
metadata_file="${input_dir}/${input_name}.md"
cat > "$metadata_file" << EOF
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
- **Date (compact)**: ${photo_date_compact:-unknown}

## Location
EOF

if [[ -n "$gps_lat" && -n "$gps_lon" ]]; then
    cat >> "$metadata_file" << EOF
- **GPS Coordinates**: $gps_lat, $gps_lon
- **Map Link**: [View on Maps](https://maps.apple.com/?q=$gps_lat,$gps_lon)
EOF
else
    echo "- **GPS Coordinates**: Not available" >> "$metadata_file"
fi

cat >> "$metadata_file" << EOF

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
File: ${photo_date_compact:-YYYYMMDD} [caption].jpg
\`\`\`
EOF

# --- Convert image ---
output_file="${input_dir}/${input_name}.jpg"
original_width=$(sips -g pixelWidth "$input_file" | awk '/pixelWidth:/ {print $2}')
original_height=$(sips -g pixelHeight "$input_file" | awk '/pixelHeight:/ {print $2}')

if [[ $original_width -gt $DEFAULT_WIDTH ]]; then
    target_width=$DEFAULT_WIDTH
    target_height=$(( original_height * target_width / original_width ))
else
    target_width=$original_width
    target_height=$original_height
fi

if [[ $target_height -gt 600 ]]; then
    target_height=600
    target_width=$(( original_width * target_height / original_height ))
fi

convert_with_sips() {
  if [[ -f "$COLOR_PROFILE_PATH" ]]; then
    sips --matchTo "$COLOR_PROFILE_PATH" \
         -s format jpeg \
         -s formatOptions $OUTPUT_QUALITY \
         -Z $target_width \
         "$input_file" \
         --out "$output_file" >/dev/null
  else
    sips -s format jpeg \
         -s formatOptions $OUTPUT_QUALITY \
         -Z $target_width \
         "$input_file" \
         --out "$output_file" >/dev/null
  fi
}

convert_with_ffmpeg() {
  local q=3
  ffmpeg -y -hide_banner -loglevel error \
    -i "$input_file" \
    -vf "scale='min(iw,${target_width})':-2:flags=lanczos,format=yuv420p" \
    -q:v $q "$output_file"
}

if command -v ffmpeg >/dev/null 2>&1 && [[ "$input_ext_upper" == "HEIC" ]]; then
  convert_with_ffmpeg
else
  convert_with_sips
fi

# --- Adjust size loop ---
current_size_kb=$(( $(wc -c < "$output_file") / 1024 ))
if command -v ffmpeg >/dev/null 2>&1 && [[ "$input_ext_upper" == "HEIC" ]]; then
  ff_q=3
  while [[ $current_size_kb -gt $TARGET_SIZE_KB && $ff_q -lt 9 ]]; do
      ff_q=$(( ff_q + 1 ))
      ffmpeg -y -hide_banner -loglevel error \
        -i "$input_file" \
        -vf "scale='min(iw,${target_width})':-2:flags=lanczos,format=yuv420p" \
        -q:v $ff_q "$output_file"
      current_size_kb=$(( $(wc -c < "$output_file") / 1024 ))
  done
else
  quality=$OUTPUT_QUALITY
  while [[ $current_size_kb -gt $TARGET_SIZE_KB && $quality -gt $MIN_QUALITY ]]; do
      quality=$(( quality - 5 ))
      sips -s formatOptions $quality "$output_file" >/dev/null
      current_size_kb=$(( $(wc -c < "$output_file") / 1024 ))
  done
fi

if [[ $current_size_kb -gt $TARGET_SIZE_KB ]]; then
    new_width=$(( target_width * 90 / 100 ))
    sips -Z $new_width "$output_file" >/dev/null
    current_size_kb=$(( $(wc -c < "$output_file") / 1024 ))
    if [[ $current_size_kb -gt $TARGET_SIZE_KB ]]; then
        new_width=$(( target_width * 80 / 100 ))
        sips -Z $new_width "$output_file" >/dev/null
    fi
fi

# --- Add EXIF back ---
if [[ -n "$photo_datetime" ]]; then
    exiftool -overwrite_original -DateTimeOriginal="$photo_datetime" "$output_file" >/dev/null 2>&1 || true
fi
if [[ -n "$gps_lat" && -n "$gps_lon" ]]; then
    exiftool -overwrite_original -GPSLatitude="$gps_lat" -GPSLongitude="$gps_lon" "$output_file" >/dev/null 2>&1 || true
fi

# --- Move results ---
rm -f "${DEST_DIR}/${final_base}".*
mv "$metadata_file" "$final_md"
mv "$output_file" "$final_jpg"

exit 0
