# Windows GPU Training Setup (AMD 7900 XTX)

## Quick Overview

Your AMD 7900 XTX can give you **10-20× speedup** over CPU:
- CPU Training: ~6-7 hours
- GPU Training: ~2-3 hours

**Setup Time:** 30-60 minutes
**Risk:** Medium (DirectML is less mature than CUDA)
**Reward:** High (save 4-5 hours per training run)

---

## Step 1: Copy Project to Windows (5 minutes)

### Option A: Via File Explorer
1. Open File Explorer
2. Navigate to: `\\wsl.localhost\Ubuntu\home\dewyn\dev\msc-ai-capstone-project`
3. Copy entire folder to: `C:\Users\YourName\dev\msc-ai-capstone-project`

### Option B: Via WSL Command
```bash
# Run in WSL2:
cp -r /home/dewyn/dev/msc-ai-capstone-project /mnt/c/Users/YourName/dev/
```

---

## Step 2: Install Python on Windows (10 minutes)

Open **PowerShell as Administrator**:

```powershell
# Check if Python already installed
python --version

# If not installed, use winget (Windows 11):
winget install Python.Python.3.10

# Or download manually from: https://www.python.org/downloads/windows/
# During installation: CHECK "Add Python to PATH"
```

**Verify installation:**
```powershell
python --version  # Should show: Python 3.10.x
pip --version     # Should show pip version
```

---

## Step 3: Install PyTorch with DirectML (15-20 minutes)

In **PowerShell** (navigate to project folder):

```powershell
cd C:\Users\YourName\dev\msc-ai-capstone-project

# Create virtual environment
python -m venv .venv-windows

# Activate it
.\.venv-windows\Scripts\Activate.ps1

# If you get execution policy error:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Install DirectML (for AMD GPU)
pip install torch-directml

# Install dependencies
pip install transformers datasets accelerate sentencepiece protobuf
pip install numpy pandas scikit-learn
```

---

## Step 4: Test GPU Detection (5 minutes)

Create test file: `test_gpu.py`

```python
import torch
import torch_directml

print("=" * 60)
print("GPU Detection Test")
print("=" * 60)

try:
    device = torch_directml.device()
    print(f"✅ DirectML device found: {device}")

    # Test tensor creation
    x = torch.randn(1000, 1000).to(device)
    y = torch.randn(1000, 1000).to(device)
    z = x @ y  # Matrix multiplication on GPU

    print(f"✅ GPU computation successful!")
    print(f"   Result shape: {z.shape}")
    print(f"\n🎉 Your AMD 7900 XTX is ready for training!")

except Exception as e:
    print(f"❌ Error: {e}")
    print(f"\n⚠️  DirectML not working. Will fall back to CPU.")
```

**Run test:**
```powershell
python test_gpu.py
```

**If you see "GPU computation successful" → You're ready!**

---

## Step 5: Run Training (2-3 hours)

### Wait for Data Generation to Complete

In **WSL2**, check if data ready:
```bash
ls -lh data/training/rag_enhanced_t5_training_1300*.json
```

### Copy Data File to Windows

```bash
# In WSL2:
cp data/training/rag_enhanced_t5_training_1300.json /mnt/c/Users/YourName/dev/msc-ai-capstone-project/data/training/
```

### Start Training in Windows

In **PowerShell**:
```powershell
# Navigate to project
cd C:\Users\YourName\dev\msc-ai-capstone-project

# Activate environment
.\.venv-windows\Scripts\Activate.ps1

# Start training with GPU!
python scripts\train_1300_examples_windows.py --epochs 15 --batch-size 20 --grad-accum 4
```

**Monitor progress:**
- Look for: "✅ Using DirectML (AMD GPU on Windows)"
- Training should show progress bars
- First epoch: ~12-15 minutes
- Total: ~2-3 hours for 15 epochs

---

## Troubleshooting

### Issue 1: DirectML Import Error
```
ModuleNotFoundError: No module named 'torch_directml'
```

**Solution:**
```powershell
pip install torch-directml
```

### Issue 2: Execution Policy Error
```
cannot be loaded because running scripts is disabled
```

**Solution:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Issue 3: Python Not Found
```
'python' is not recognized as an internal or external command
```

**Solution:**
1. Reinstall Python
2. **CHECK** "Add Python to PATH" during installation
3. Restart PowerShell

### Issue 4: GPU Not Detected
```
⚠️  Using CPU (no GPU detected)
```

**Check AMD Driver:**
- Open Device Manager
- Check "Display adapters" → Should show "AMD Radeon RX 7900 XTX"
- Update driver if needed: [AMD Driver Download](https://www.amd.com/en/support)

**DirectML Fallback:**
If DirectML doesn't work, script automatically falls back to CPU (still works, just slower).

---

## Performance Comparison

| Environment | Device | Time | Notes |
|-------------|--------|------|-------|
| **WSL2** | CPU (Ryzen 7700X) | ~6-7 hours | What you're using now |
| **Windows** | GPU (7900 XTX) | **~2-3 hours** | 🚀 3× faster! |
| **Windows** | CPU (if GPU fails) | ~6-7 hours | Same as WSL2 |

---

## Decision Framework

### Try Windows GPU If:
- ✅ You have 30-60 min for setup
- ✅ Want to save 4-5 hours per training run
- ✅ Comfortable with Windows PowerShell
- ✅ Data generation still running (time to set up)

### Stick with WSL2 CPU If:
- ✅ Data generation almost done (no time for setup)
- ✅ Can't risk setup failures
- ✅ Prefer familiar WSL2 environment
- ✅ 6-7 hours overnight works for you

---

## What Script Does Differently

The Windows version (`train_1300_examples_windows.py`) automatically:
1. **Tries DirectML first** (AMD GPU)
2. **Falls back to CUDA** if available (NVIDIA GPU)
3. **Falls back to CPU** if no GPU works
4. **Disables dataloader workers** (Windows threading issues)
5. **Uses FP32** (DirectML FP16 unstable)

**It's a safe, automatic GPU-or-CPU approach.**

---

## Summary

**Path:**
1. Copy project to Windows (5 min)
2. Install Python + DirectML (25 min)
3. Test GPU (5 min)
4. Run training (2-3 hours)

**Total:** 35 min setup + 2-3 hours training = **~3.5 hours total**

vs

**WSL2 CPU:** 0 min setup + 6-7 hours training = **~7 hours total**

**Net savings: 3.5 hours!** ⚡

---

## Need Help?

If setup fails after 30 minutes:
1. Abort Windows attempt
2. Return to WSL2
3. Run CPU training (proven to work)
4. Save GPU setup for next project

**Zero risk of losing progress!**
