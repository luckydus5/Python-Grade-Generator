#!/usr/bin/env bash
# organizer.sh
# Archives CSV files with timestamp and logs to organizer.log

ARCHIVE_DIR="archive"
LOG_FILE="organizer.log"

# Create archive dir if it doesn't exist
mkdir -p "$ARCHIVE_DIR"

# Find all CSV files in current directory
shopt -s nullglob
CSV_FILES=( *.csv )
shopt -u nullglob

if [ ${#CSV_FILES[@]} -eq 0 ]; then
  echo "No .csv files found in $(pwd). Nothing to do."
  exit 0
fi

# Process each CSV file
for f in "${CSV_FILES[@]}"; do
  # Generate timestamp (format: YYYYMMDD-HHMMSS)
  timestamp=$(date +"%Y%m%d-%H%M%S")
  
  # Build new filename with timestamp before extension
  base="$(basename "$f" .csv)"
  newname="${base}-${timestamp}.csv"
  
  # If file with same name exists (unlikely), append random suffix
  if [ -e "$ARCHIVE_DIR/$newname" ]; then
    rand=$(printf "%04d" $((RANDOM % 10000)))
    newname="${base}-${timestamp}-${rand}.csv"
  fi
  
  # Log the action with timestamp and file content
  echo "=== Archive Log Entry ===" >> "$LOG_FILE"
  echo "Date: $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG_FILE"
  echo "Original File: $f" >> "$LOG_FILE"
  echo "New Location: $ARCHIVE_DIR/$newname" >> "$LOG_FILE"
  echo "--- File Content ---" >> "$LOG_FILE"
  cat "$f" >> "$LOG_FILE"
  echo "" >> "$LOG_FILE"
  echo "--- End of Content ---" >> "$LOG_FILE"
  echo "" >> "$LOG_FILE"
  
  # Move file to archive with new name
  mv -- "$f" "$ARCHIVE_DIR/$newname"
  echo "Archived: $f -> $ARCHIVE_DIR/$newname"
done

echo "Done. Archived ${#CSV_FILES[@]} file(s). Check $LOG_FILE for details."

