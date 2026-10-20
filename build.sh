#!/usr/bin/env bash
# Exit on any error
set -o errexit

echo "==> Starting OmniOCR Unified Build"

# 1. Build React Frontend SPA
if [ -d "frontend" ]; then
  echo "==> Building React frontend assets..."
  cd frontend
  npm install
  npm run build
  cd ..
  echo "==> Frontend build completed successfully."
fi

# 2. Upgrade pip
python -m pip install --upgrade pip

# 3. Install lightweight CPU PyTorch first (avoids multi-gigabyte CUDA bloat on Render)
echo "==> Installing CPU-optimized PyTorch..."
python -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# 4. Install remaining requirements
echo "==> Installing backend dependencies..."
python -m pip install -r requirements.txt

echo "==> OmniOCR build finished successfully!"
