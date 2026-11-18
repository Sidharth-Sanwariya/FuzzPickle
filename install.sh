#!/bin/bash

echo "========================================="
echo "   FuzzPickle Installer"
echo "========================================="

# 1. Install Rust (for the fuzzer)
if ! command -v cargo &> /dev/null; then
    echo "[*] Installing Rust..."
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
    source "$HOME/.cargo/env"
else
    echo "[+] Rust is already installed."
fi

# 2. Setup Python Virtual Environment
echo "[*] Setting up Python virtual environment..."
python3 -m venv .venv
source .venv/bin/activate

# 3. Install Python Dependencies
echo "[*] Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# 4. Clone and Build the Rust Fuzzer
if [ ! -d "pickle-fuzzer" ]; then
    echo "[*] Cloning and compiling the pickle-fuzzer..."
    git clone https://github.com/cisco-ai-defense/pickle-fuzzer.git
    cd pickle-fuzzer
    cargo build --release
    cd ..
else
    echo "[+] Fuzzer is already built."
fi

echo "========================================="
echo "   INSTALLATION COMPLETE!"
echo "   Activate your environment with:"
echo "   source .venv/bin/activate"
echo "========================================="
