# Native Windows Setup with AMD GPU (RX 7900 XTX)

**Goal**: Run CodeT5 training on native Windows with AMD GPU acceleration (10-20x faster than CPU)

---

## Prerequisites Check

**Hardware**:
- ✅ AMD Radeon RX 7900 XTX (24GB VRAM)
- ✅ Windows 10 (Build 16299+) or Windows 11

**Software**:
- Latest AMD Adrenalin drivers (24.12.1 or newer recommended)
- Python 3.8+ (preferably 3.10 or 3.11)
- Git for Windows

---

## Step 1: Install AMD Drivers (If Not Already Done)

1. Download latest AMD Adrenalin Edition:
   - https://www.amd.com/en/support
   - Select: Graphics → Radeon RX 7000 Series → Radeon RX 7900 XTX
   - Download "Adrenalin Edition" (should be 24.12.1 or newer)

2. Install with default options

3. **Reboot Windows**

---

## Step 2: Verify GPU is Detected

Open PowerShell and run:

```powershell
# Check if GPU is detected
Get-WmiObject Win32_VideoController | Select-Object Name, DriverVersion

# Should show something like:
# Name: AMD Radeon RX 7900 XTX
# DriverVersion: 31.0.24033.1003 (or similar)
```

---

## Step 3: Clone Repository to Native Windows

```powershell
# Navigate to your preferred location (e.g., C:\Users\YourName\Projects)
cd C:\Users\YourName\Projects

# Clone the repository
git clone https://github.com/dewynl/msc-ai-capstone-project.git
cd msc-ai-capstone-project
```

---

## Step 4: Create Python Virtual Environment

```powershell
# Create virtual environment
python -m venv venv

# Activate it
.\venv\Scripts\Activate.ps1

# If you get execution policy error:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Verify Python version
python --version
# Should be 3.8 or higher
```

---

## Step 5: Install PyTorch with ROCm (AMD GPU Support)

**Option A: ROCm on Windows (Recommended - Official AMD Support)**

```powershell
# Install PyTorch with ROCm 6.2
pip install torch torchvision --index-url https://download.pytorch.org/whl/rocm6.2

# This downloads ~2-3GB, may take 5-10 minutes
```

**Option B: DirectML (Alternative - Easier but less performance)**

```powershell
# Install PyTorch with DirectML
pip install torch-directml
pip install torch torchvision
```

---

## Step 6: Test GPU Detection

Create a test file `test_gpu.py`:

```python
import torch

print("=" * 60)
print("GPU Detection Test")
print("=" * 60)

# For ROCm:
if torch.cuda.is_available():
    print(f"✅ GPU Available: {torch.cuda.is_available()}")
    print(f"   GPU Name: {torch.cuda.get_device_name(0)}")
    print(f"   GPU Count: {torch.cuda.device_count()}")
    print(f"   CUDA Version: {torch.version.cuda}")
else:
    print("❌ GPU Not Available")
    print("   Will train on CPU (slower)")

# Test actual GPU computation
if torch.cuda.is_available():
    x = torch.randn(1000, 1000).cuda()
    y = torch.randn(1000, 1000).cuda()
    z = x @ y
    print(f"\n✅ GPU Computation Test: SUCCESS")
    print(f"   Matrix multiplication on GPU completed")
else:
    print("\n⚠️  Running on CPU")

print("=" * 60)
```

Run it:

```powershell
python test_gpu.py
```

**Expected Output (if working)**:
```
✅ GPU Available: True
   GPU Name: AMD Radeon RX 7900 XTX
   GPU Count: 1
   CUDA Version: (ROCm version)
✅ GPU Computation Test: SUCCESS
```

---

## Step 7: Install Project Dependencies

```powershell
# Install all required packages
pip install -r requirements.txt

# If you get errors, install individually:
pip install transformers accelerate datasets sentencepiece
pip install chromadb sentence-transformers
pip install streamlit supabase httpx
```

---

## Step 8: Run CodeT5 Training with GPU

```powershell
# Navigate to project root
cd C:\Users\YourName\Projects\msc-ai-capstone-project

# Activate virtual environment (if not already)
.\venv\Scripts\Activate.ps1

# Run training
python scripts/codet5_function_call_trainer.py
```

**Expected Timeline**:
- Model download: 2-3 minutes (first time only)
- Training (10 epochs): **10-20 minutes on GPU** (vs 2-3 hours on CPU!)
- Total: ~15-25 minutes

---

## Step 9: Monitor Training Progress

Training will output logs like:

```
🚀 Starting Optimized CodeT5 Function Call Training
📦 Loading Salesforce/codet5-small model...
✅ Fine-tuned model loaded
📂 Loading training data from: data/training/rag_enhanced_t5_training.json
✅ Loaded 260 function call training examples

📊 Dataset Split:
   Training examples: 234
   Validation examples: 26

🏋️  Starting Training...
Epoch 1/10: [███████████████] loss: 2.456
Epoch 2/10: [███████████████] loss: 1.234
...
```

**Watch for**:
- GPU utilization (should be 30-50% on 7900 XTX)
- Loss decreasing each epoch
- No CUDA/ROCm errors

---

## Step 10: Verify Trained Model Works

After training completes:

```powershell
python -c "
from transformers import RobertaTokenizer, T5ForConditionalGeneration
import torch

model_path = './models/codet5-function-call-finetuned'
tokenizer = RobertaTokenizer.from_pretrained(model_path)
model = T5ForConditionalGeneration.from_pretrained(model_path)

if torch.cuda.is_available():
    model = model.cuda()

test_input = 'Generate course syllabus: {\"title\": \"Test Course\"}'
input_ids = tokenizer(test_input, return_tensors='pt').input_ids

if torch.cuda.is_available():
    input_ids = input_ids.cuda()

with torch.no_grad():
    output = model.generate(input_ids, max_length=100)

result = tokenizer.decode(output[0], skip_special_tokens=True)
print('Generated:', result)

# Should see function calls like:
# b = SyllabusBuilder()
# b.set_info(...)
# NOT just echoing the input like T5 did!
"
```

---

## Troubleshooting

### GPU Not Detected

**Issue**: `torch.cuda.is_available()` returns `False`

**Solutions**:
1. Verify driver installation: Check Device Manager → Display Adapters
2. Try DirectML instead: `pip install torch-directml`
3. Reinstall PyTorch with ROCm: `pip uninstall torch && pip install torch --index-url https://download.pytorch.org/whl/rocm6.2`

### Out of Memory Error

**Issue**: `RuntimeError: CUDA out of memory`

**Solutions**:
1. Your 7900 XTX has 24GB - this shouldn't happen for CodeT5-small (needs ~2-4GB)
2. If it does, reduce batch size in `codet5_function_call_trainer.py`:
   ```python
   batch_size = 2  # was 4
   ```

### Slow Performance (Not Using GPU)

**Issue**: Training takes hours (like CPU)

**Check**:
```powershell
# Monitor GPU usage during training
# Open Task Manager → Performance → GPU

# Or use AMD Radeon Software overlay (Alt+R)
```

If GPU usage is 0%, training is on CPU. Reinstall PyTorch with ROCm.

### Import Errors

**Issue**: `ModuleNotFoundError: No module named 'transformers'`

**Solution**:
```powershell
# Make sure virtual environment is activated
.\venv\Scripts\Activate.ps1

# Reinstall requirements
pip install -r requirements.txt
```

---

## Performance Comparison

| Setup | Hardware | Time (10 epochs) |
|-------|----------|------------------|
| WSL2 CPU | AMD Ryzen (all cores) | 2-3 hours |
| Windows GPU | RX 7900 XTX (24GB) | **10-20 minutes** |

**Speedup: 10-20x faster!**

---

## Next Steps After Training

1. **Verify model quality**: Test generates valid function calls (not gibberish)
2. **Upload to Hugging Face**: `python scripts/upload_model_to_huggingface.py`
3. **Update Streamlit app**: Change model path to use CodeT5 instead of T5
4. **Deploy**: Push to GitHub, Streamlit Cloud will auto-deploy

---

## Quick Reference Commands

```powershell
# Activate environment
.\venv\Scripts\Activate.ps1

# Train model
python scripts/codet5_function_call_trainer.py

# Test GPU
python test_gpu.py

# Monitor logs (during training)
Get-Content codet5_training.log -Wait -Tail 50

# Check process
Get-Process python
```

---

## Summary

1. ✅ Install AMD drivers (Adrenalin 24.12.1+)
2. ✅ Clone repo to Windows (not WSL)
3. ✅ Create Python venv
4. ✅ Install PyTorch with ROCm: `pip install torch --index-url https://download.pytorch.org/whl/rocm6.2`
5. ✅ Test GPU: `python test_gpu.py`
6. ✅ Install deps: `pip install -r requirements.txt`
7. ✅ Train: `python scripts/codet5_function_call_trainer.py` (10-20 min!)
8. ✅ Celebrate 10-20x speedup! 🎉

**Good luck! Your 24GB GPU is perfect for this task.**
