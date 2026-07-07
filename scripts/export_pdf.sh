#!/usr/bin/env bash
# Export tailored resume .docx files to PDF (house design preserved).
#
# Usage:
#   scripts/export_pdf.sh                          # export ALL applications/*/tailored_resume.docx
#   scripts/export_pdf.sh applications/belvo-applied-ai        # one application folder
#   scripts/export_pdf.sh applications/foo/tailored_resume.docx  # explicit file(s)
#
# Converter preference:
#   1. LibreOffice (soffice) if installed  - headless, no UI
#   2. Microsoft Word via AppleScript      - first run may ask for an Automation permission; click OK
#
# PDFs land next to their .docx with the same basename.
set -euo pipefail

cd "$(dirname "$0")/.."

# ---------- collect targets ----------
targets=()
if [[ $# -eq 0 ]]; then
  for f in applications/*/tailored_resume.docx; do
    [[ -e "$f" ]] && targets+=("$f")
  done
else
  for arg in "$@"; do
    if [[ -d "$arg" ]]; then
      for f in "$arg"/*.docx; do [[ -e "$f" ]] && targets+=("$f"); done
    elif [[ -f "$arg" ]]; then
      targets+=("$arg")
    else
      echo "skip (not found): $arg" >&2
    fi
  done
fi

if [[ ${#targets[@]} -eq 0 ]]; then
  echo "No .docx files to export." >&2
  exit 1
fi

# ---------- pick converter ----------
SOFFICE="$(command -v soffice || true)"
[[ -z "$SOFFICE" && -x "/Applications/LibreOffice.app/Contents/MacOS/soffice" ]] \
  && SOFFICE="/Applications/LibreOffice.app/Contents/MacOS/soffice"

word_export() { # $1 = absolute docx path, $2 = absolute pdf path
  osascript - "$1" "$2" <<'OSA'
on run argv
    set docxPath to item 1 of argv
    set pdfPath to item 2 of argv
    tell application "Microsoft Word"
        launch
        with timeout of 600 seconds
            open (POSIX file docxPath)
            delay 1
            set theDoc to active document
            save as theDoc file name pdfPath file format format PDF
            close theDoc saving no
        end timeout
    end tell
end run
OSA
}

# ---------- export ----------
ok=0 fail=0
for docx in "${targets[@]}"; do
  abs_docx="$(cd "$(dirname "$docx")" && pwd)/$(basename "$docx")"
  pdf="${abs_docx%.docx}.pdf"
  if [[ -n "$SOFFICE" ]]; then
    if "$SOFFICE" --headless --convert-to pdf --outdir "$(dirname "$abs_docx")" "$abs_docx" >/dev/null 2>&1; then
      echo "ok  (soffice): ${pdf}"
      ok=$((ok + 1))
    else
      echo "FAIL (soffice): ${docx}" >&2
      fail=$((fail + 1))
    fi
  elif [[ -d "/Applications/Microsoft Word.app" ]]; then
    if word_export "$abs_docx" "$pdf"; then
      echo "ok  (Word): ${pdf}"
      ok=$((ok + 1))
    else
      echo "FAIL (Word): ${docx}" >&2
      fail=$((fail + 1))
    fi
  else
    echo "No converter found: install LibreOffice (brew install --cask libreoffice) or Microsoft Word." >&2
    exit 1
  fi
done

echo "---"
echo "exported: ${ok}  failed: ${fail}"
[[ $fail -eq 0 ]]
