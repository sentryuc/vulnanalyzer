#!/bin/bash

# Exit on any error
set -e

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check required dependencies
echo "Checking dependencies..."
if ! command_exists pip; then
    echo "Error: pip is not installed"
    exit 1
fi

if ! command_exists git; then
    echo "Error: git is not installed"
    exit 1
fi

if ! command_exists docker; then
    echo "Error: docker is not installed"
    exit 1
fi

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create folder tools
echo "Creating tools directory..."
mkdir -p tools
cd tools

# Clone the Caldera repository
echo "Cloning the Caldera repository..."
if [ -d "caldera" ]; then
    echo "Caldera directory already exists. Removing it..."
    rm -rf caldera
fi

git clone https://github.com/mitre/caldera.git --recursive --branch 5.3.0
cd caldera

# Build Docker image
echo "Building Caldera Docker image..."
docker build --build-arg WIN_BUILD=true . -t caldera:server

echo "Setup completed successfully!"
echo "You can now run Caldera using: docker run -p 8888:8888 caldera:server"
