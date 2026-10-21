#!/usr/bin/env bash
# Checks that ffmpeg/ffprobe and Pillow are available (captions are PNG overlays: no libass needed).
#   bash setup.sh            check only; if missing, say how to install and exit 1
#   bash setup.sh --install  run `brew install ffmpeg` (only after the user agreed)
set -u

have() { command -v "$1" >/dev/null 2>&1; }

if have ffmpeg && have ffprobe; then
  if ! ffmpeg -hide_banner -filters 2>/dev/null | grep -q " overlay "; then
    echo "ffmpeg has no 'overlay' filter; reinstall with: brew reinstall ffmpeg"
    exit 1
  fi
  # `brew install ffmpeg` can put a newer Homebrew python3 first on PATH; use whichever interpreter has Pillow.
  for py in python3 /usr/bin/python3 /usr/local/bin/python3.12 /opt/homebrew/bin/python3; do
    if command -v "$py" >/dev/null 2>&1 && "$py" -c "import PIL" 2>/dev/null; then
      echo "OK ffmpeg $(ffmpeg -version | head -1 | awk '{print $3}'), Pillow in: $(command -v "$py")"
      echo "Run the reel scripts with that interpreter (PYTHON=$(command -v "$py"))."
      exit 0
    fi
  done
  echo "Pillow not found in any python3. Install it: python3 -m pip install --user Pillow"
  exit 1
fi

echo "ffmpeg/ffprobe not found."
if [ "${1:-}" = "--install" ]; then
  if ! have brew; then echo "Homebrew not found; install ffmpeg manually (https://ffmpeg.org/download.html)."; exit 1; fi
  brew install ffmpeg && exec bash "$0"
fi
echo "Ask the user, then run: bash $0 --install   (equivalent to: brew install ffmpeg)"
exit 1
