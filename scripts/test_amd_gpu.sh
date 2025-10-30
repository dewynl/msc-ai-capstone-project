#!/bin/bash
# Quick AMD GPU Detection Test for WSL2

echo "================================"
echo "AMD GPU Detection Test (WSL2)"
echo "================================"
echo ""

echo "1. Checking WSL version..."
if grep -qi microsoft /proc/version; then
    echo "   ✅ Running in WSL"
else
    echo "   ❌ Not running in WSL"
    exit 1
fi

echo ""
echo "2. Checking for AMD GPU in lspci..."
if lspci | grep -i 'VGA.*AMD'; then
    echo "   ✅ AMD GPU detected by lspci"
else
    echo "   ⚠️  AMD GPU not visible in lspci (may need driver install)"
fi

echo ""
echo "3. Checking if rocminfo is installed..."
if command -v rocminfo &> /dev/null; then
    echo "   ✅ rocminfo found"
    echo ""
    echo "   ROCm GPU Info:"
    rocminfo | grep -A 5 "Agent.*GPU" || echo "   ⚠️  No GPU agents found"
else
    echo "   ❌ rocminfo not installed (ROCm not set up)"
    echo ""
    echo "   To install ROCm on WSL2:"
    echo "   1. Install AMD Adrenalin 24.12.1+ on Windows"
    echo "   2. In WSL2:"
    echo "      wget https://repo.radeon.com/amdgpu-install/latest/ubuntu/jammy/amdgpu-install_6.2.60202-1_all.deb"
    echo "      sudo apt install ./amdgpu-install_6.2.60202-1_all.deb"
    echo "      sudo amdgpu-install --usecase=rocm --no-dkms"
fi

echo ""
echo "4. Checking if PyTorch with ROCm is installed..."
if python3 -c "import torch; print(f'PyTorch {torch.__version__}'); print(f'ROCm available: {torch.version.hip}')" 2>/dev/null; then
    echo "   ✅ PyTorch with ROCm found"
else
    echo "   ❌ PyTorch with ROCm not installed"
    echo ""
    echo "   To install:"
    echo "   pip install torch torchvision --index-url https://repo.radeon.com/rocm/manylinux/rocm-rel-6.2/"
fi

echo ""
echo "================================"
echo "Test complete!"
echo "================================"
