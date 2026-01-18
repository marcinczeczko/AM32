#!/usr/bin/env bash
set -euo pipefail

OUTPUT="${1:-/dev/stdout}"
ROOT="$(pwd)"

{
echo "################################################################################"
echo "# FILE: .vscode/settings.json"
echo "################################################################################"
echo
cat .vscode/settings.json
echo
echo
} >> "$OUTPUT"


{
echo "################################################################################"
echo "# FILE: CMakePresets.json"
echo "################################################################################"
echo
cat CMakePresets.json
echo
echo
} >> "$OUTPUT"

{
echo "################################################################################"
echo "# FILE: CMakeLists.txt"
echo "################################################################################"
echo
cat CMakeLists.txt
echo
echo
} >> "$OUTPUT"

find cmake/ \
  -type f \
  -name "*.cmake" \
  | while read -r file; do
      rel="${file#./}"
      {
        echo "################################################################################"
        echo "# FILE: $rel"
        echo "################################################################################"
        echo
        cat "$file"
        echo
        echo
      } >> "$OUTPUT"
    done
