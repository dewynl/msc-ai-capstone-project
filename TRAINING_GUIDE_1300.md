# Training Guide: 1,300-Example Dataset

## Quick Start

Once data generation completes, run:

```bash
source .venv/bin/activate && \
python scripts/train_1300_examples.py \
  --epochs 10 \
  --batch-size 20 \
  --grad-accum 4 \
  2>&1 | tee training_1300_examples.log &
```

**Note:** Only 10 epochs needed! More data = fewer epochs for equivalent training intensity.

Monitor progress:
```bash
tail -f training_1300_examples.log
```

## Optimizations vs 260-Example Baseline

| Parameter | 260 Examples | 1,300 Examples | Reason |
|-----------|--------------|----------------|--------|
| **Number of Epochs** | 41 | 10 | More data needs FEWER epochs for equivalent intensity |
| **Example Exposures** | 10,660 | 13,000 | Similar training intensity |
| **Effective Batch Size** | 64 (16×4) | 80 (20×4) | Larger dataset → better gradient estimates |
| **Steps per Epoch** | 3.65 | 14.6 | More data = more steps |
| **Total Steps** | ~150 | ~146 | Comparable gradient updates |
| **Evaluation Frequency** | Every epoch | Every 0.5 epoch | Better monitoring |
| **Checkpoint Frequency** | Every epoch | Every 2 epochs | Balance save overhead vs recovery |
| **Early Stopping Patience** | 5 epochs | 10 evals (5 epochs) | Scaled to eval frequency |
| **Expected Duration** | 4.3 hours (41 epochs) | **~4-5 hours (10 epochs)** | Similar time! |

## Key Features

### 1. Progress Tracking
- Real-time epoch duration tracking
- Average time per epoch
- Estimated time remaining
- Total elapsed time

### 2. Enhanced Checkpointing
- Saves every 2 epochs (vs every epoch before)
- Keeps 5 best checkpoints (vs 3 before)
- Automatic best model selection

### 3. Frequent Evaluation
- Evaluates every ~0.5 epoch (vs 1 epoch before)
- Better loss curve for debugging
- Earlier detection of convergence/divergence

### 4. Checkpoint Resume Support
- Script can use checkpoint file if final file not ready
- Enables starting training even if generation still running

## Expected Timeline

```
Start:     0 hours   (Launch training)
Eval 1:    0.7 hours (First half-epoch)
Epoch 1:   1.4 hours
Epoch 10:  14 hours  (Monitor: should see loss decreasing)
Epoch 20:  ~20 hours (Check if converging)
Epoch 50:  ~22 hours (Completion, or earlier with early stopping)
```

## Resource Usage

- **GPU Memory**: ~18-20GB (vs 16-18GB before)
- **Disk Space**: ~2.5GB for 5 checkpoints
- **Log Size**: ~50-100MB

## Commands

### Start Training
```bash
python scripts/train_1300_examples.py
```

### Start with Custom Config
```bash
python scripts/train_1300_examples.py \
  --epochs 40 \
  --batch-size 24 \
  --grad-accum 3
```

### Use Checkpoint File (if generation still running)
```bash
python scripts/train_1300_examples.py \
  --data data/training/rag_enhanced_t5_training_1300_checkpoint.json
```

### Monitor Training
```bash
# Live logs
tail -f training_1300_examples.log

# GPU usage
watch -n 1 nvidia-smi

# Latest evaluation results
grep "eval_loss" training_1300_examples.log | tail -20
```

### After Training Completes

Run evaluation:
```bash
python scripts/evaluate_codet5_model.py \
  --model ./models/codet5-1300examples
```

## Troubleshooting

### Out of Memory
```bash
# Reduce batch size
python scripts/train_1300_examples.py --batch-size 16 --grad-accum 5
```

### Training Too Slow
```bash
# Check GPU utilization
nvidia-smi

# Check dataloader workers
# If CPU bottleneck, reduce workers in script (line 172)
```

### Want to Resume from Checkpoint
```bash
# Training automatically resumes from last checkpoint in output_dir
python scripts/train_1300_examples.py
```

## What to Watch For

### Good Signs ✅
- Eval loss decreasing steadily
- Train loss lower than eval loss (some overfitting is OK)
- Avg time per epoch stabilizes after first few epochs
- GPU utilization >80%

### Bad Signs ❌
- Eval loss plateaus early (<10 epochs)
- Eval loss increases while train loss decreases (severe overfitting)
- Training crashes repeatedly (OOM or data issues)
- Time per epoch increasing (memory leak?)

## Next Steps After Training

1. **Evaluate Model** - Run comprehensive test suite
2. **Compare with Baseline** - 260 examples (0% pass) vs 1,300 examples
3. **Analyze Output Length** - Check if generating full 800-1000 char outputs
4. **Test Component Coverage** - Verify modules, activities, assessments included
5. **Deploy or Iterate** - If pass rate >60%, deploy; else investigate hybrid approach
