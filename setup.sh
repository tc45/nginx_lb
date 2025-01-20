#!/bin/bash

# Get the current directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Update package list and install necessary packages
echo "Updating package list..."
sudo apt update

# Install Python3 and venv
echo "Installing Python3 and venv..."
sudo apt install -y python3 python3-venv python3-full

# Create a virtual environment in the root directory
echo "Creating a virtual environment..."
python3 -m venv "$SCRIPT_DIR/venv"

# Activate the virtual environment
echo "Activating the virtual environment..."
source "$SCRIPT_DIR/venv/bin/activate"

# Install required Python packages
echo "Installing required Python packages..."
pip install -r "$SCRIPT_DIR/requirements.txt"

# Install NGINX
echo "Installing NGINX..."
sudo apt install -y nginx

echo "Setup completed successfully."