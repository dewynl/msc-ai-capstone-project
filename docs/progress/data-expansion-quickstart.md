# Data Expansion Quick Start Guide
**If you decide to expand your dataset, follow this exact sequence**

---

## ⚡ Quick Decision: Should You Do This?

**❌ NO if:**
- It's before Week 2 (evaluation chapter and web app come first)
- You're behind schedule on dissertation writing
- You don't have API budget (~$15-25)

**✅ YES if:**
- You're ahead of schedule (finished Week 1 goals early)
- You want scalability data for evaluation chapter
- You have 6-8 hours available on a weekend

---

## 🎯 Recommended Minimal Expansion

**Target:** +30 training examples (90 → 120)
**Time:** 3-4 hours
**Cost:** ~$5-10

This is enough to show scalability without major time investment.

---

## 📋 Step-by-Step Process

### Pre-Check (5 minutes)

```bash
cd /home/dewyn/dev/msc-ai-capstone-project

# Check current counts
python3 -c "
import json
print('Current components:')
print(f'Modules: {len(json.load(open(\"data/components/modules.json\")))}')
print(f'Activities: {len(json.load(open(\"data/components/activities.json\")))}')
print(f'Assessments: {len(json.load(open(\"data/components/assessments.json\")))}')
print(f'\\nTraining examples: {len(json.load(open(\"data/training/t5_function_call_training.json\")))}')
"

# Check API key
echo $ANTHROPIC_API_KEY
```

If API key not set:
```bash
export ANTHROPIC_API_KEY='your-api-key-here'
```

---

### Option 1: Just Training Data (QUICKEST)

**Time:** 1 hour
**Goal:** 90 → 120 training examples
**Uses:** Existing components only

```bash
# Edit the training data generator
nano scripts/create_clean_training_data.py

# Find line 219, change:
# training_data = generator.generate_training_dataset(examples_per_domain=30)
# TO:
# training_data = generator.generate_training_dataset(examples_per_domain=40)

# Save and run
python3 scripts/create_clean_training_data.py

# Check output
python3 -c "
import json
data = json.load(open('data/training/t5_function_call_training.json'))
print(f'New training examples: {len(data)}')
"
```

**Result:** More training data WITHOUT generating new components.

---

### Option 2: Expand Everything (THOROUGH)

**Time:** 6-8 hours
**Goal:** New components + more training data
**Cost:** ~$15-25

#### Step 1: Backup Current Data (5 minutes)

```bash
# Create backup directory
mkdir -p data/backups/$(date +%Y%m%d)

# Backup components
cp data/components/*.json data/backups/$(date +%Y%m%d)/

# Backup training data
cp data/training/*.json data/backups/$(date +%Y%m%d)/

# Backup ChromaDB
cp -r chroma_db data/backups/$(date +%Y%m%d)/chroma_db_backup

echo "✅ Backup created in data/backups/$(date +%Y%m%d)/"
```

#### Step 2: Check Domain Alignment (10 minutes)

Your system uses 3 domains, but generator uses 4:

```bash
# Check generator domains
grep -n "self.stem_domains" src/data/stem_components_generator.py

# You'll see:
# Domain.CS, Domain.MATH, Domain.PHYSICS, Domain.ENGINEERING
```

**You need to remove Engineering or adjust your system.**

**Quick fix:** Edit the generator to match your system:

```bash
nano src/data/stem_components_generator.py

# Find lines 54-60, change from:
#     self.stem_domains = [
#         Domain.CS,
#         Domain.MATH,
#         Domain.PHYSICS,
#         Domain.ENGINEERING,  # ← Remove this line
#     ]

# TO:
#     self.stem_domains = [
#         Domain.CS,
#         Domain.MATH,
#         Domain.PHYSICS,
#     ]
```

#### Step 3: Generate New Components (3-4 hours)

```bash
# Check models.py exists
ls src/data/models.py

# If missing, you'll get import errors. Check what schema file exists:
ls src/data/

# Run generation (CONSERVATIVE targets)
python3 << 'EOF'
import sys
import os
sys.path.append('src')

from data.stem_components_generator import STEMComponentsGenerator

# Get API key
api_key = os.getenv('ANTHROPIC_API_KEY')
if not api_key:
    print("❌ ANTHROPIC_API_KEY not set!")
    sys.exit(1)

# Create generator with custom output directory
generator = STEMComponentsGenerator(
    api_key=api_key,
    output_dir='data/components/expanded'
)

print("🚀 Starting component generation...")
print("This will take 3-4 hours due to API rate limits")
print("Press Ctrl+C to stop (progress is saved incrementally)")

# Conservative expansion
results = generator.generate_all_stem_components(
    activities_per_domain=50,  # +10 per domain = +30 total
    assessments_per_domain=20, # +5 per domain = +15 total
    modules_per_domain=15      # +5 per domain = +15 total
)

if results:
    print("\n✅ Generation complete!")
    print(f"Total: {results['total_components']} components")
else:
    print("\n⚠️ Generation interrupted or failed")
EOF
```

**This runs in foreground. Leave it running.**

Components are saved incrementally in:
- `data/components/expanded/stem_learning_activities.json`
- `data/components/expanded/stem_assessments.json`
- `data/components/expanded/stem_modules.json`

#### Step 4: Merge Components (30 minutes)

Create merge script:

```bash
cat > scripts/merge_components.py << 'EOF'
#!/usr/bin/env python3
"""Merge expanded components with existing ones"""
import json
from pathlib import Path

def merge_components(original_file, expanded_file, output_file):
    """Merge two component JSON files, removing duplicates"""

    # Load files
    with open(original_file) as f:
        original = json.load(f)

    with open(expanded_file) as f:
        expanded = json.load(f)

    print(f"Original: {len(original)} items")
    print(f"Expanded: {len(expanded)} items")

    # Simple merge - expanded file already checks duplicates
    merged = original + expanded

    print(f"Merged: {len(merged)} items")

    # Save
    with open(output_file, 'w') as f:
        json.dump(merged, f, indent=2)

    print(f"✅ Saved to {output_file}")

# Merge all three types
print("\n📦 Merging Activities...")
merge_components(
    'data/components/activities.json',
    'data/components/expanded/stem_learning_activities.json',
    'data/components/activities_merged.json'
)

print("\n📦 Merging Assessments...")
merge_components(
    'data/components/assessments.json',
    'data/components/expanded/stem_assessments.json',
    'data/components/assessments_merged.json'
)

print("\n📦 Merging Modules...")
merge_components(
    'data/components/modules.json',
    'data/components/expanded/stem_modules.json',
    'data/components/modules_merged.json'
)

print("\n✅ Merge complete!")
print("\nTo use merged files:")
print("  mv data/components/activities_merged.json data/components/activities.json")
print("  mv data/components/assessments_merged.json data/components/assessments.json")
print("  mv data/components/modules_merged.json data/components/modules.json")
EOF

chmod +x scripts/merge_components.py
python3 scripts/merge_components.py

# Review counts before replacing
python3 -c "
import json
print('Merged files:')
print(f'Activities: {len(json.load(open(\"data/components/activities_merged.json\")))}')
print(f'Assessments: {len(json.load(open(\"data/components/assessments_merged.json\")))}')
print(f'Modules: {len(json.load(open(\"data/components/modules_merged.json\")))}')
"

# If happy with counts, replace original files
mv data/components/activities.json data/components/activities_old.json
mv data/components/activities_merged.json data/components/activities.json

mv data/components/assessments.json data/components/assessments_old.json
mv data/components/assessments_merged.json data/components/assessments.json

mv data/components/modules.json data/components/modules_old.json
mv data/components/modules_merged.json data/components/modules.json

echo "✅ Original files replaced (old files saved with _old suffix)"
```

#### Step 5: Rebuild Vector Store (20 minutes)

```bash
# Delete old ChromaDB
rm -rf chroma_db

# Rebuild with new components
python3 scripts/rebuild_vector_store.py

# Verify
python3 -c "
from src.rag.vector_store import SyllabusComponentStore
store = SyllabusComponentStore()
stats = store.get_collection_stats()
print(f'Vector store components: {stats[\"total_components\"]}')
"
```

#### Step 6: Generate More Training Data (30 minutes)

```bash
# Edit training data generator
nano scripts/create_clean_training_data.py

# Line 219, change to:
# training_data = generator.generate_training_dataset(examples_per_domain=50)

# Rename old training file
mv data/training/t5_function_call_training.json data/training/t5_function_call_training_old.json

# Generate new training data
python3 scripts/create_clean_training_data.py

# Verify
python3 -c "
import json
data = json.load(open('data/training/t5_function_call_training.json'))
print(f'New training examples: {len(data)}')

# Count by domain
from collections import Counter
domains = [json.loads(ex['input_json'])['domain'] for ex in data]
print('\\nBreakdown by domain:')
for domain, count in Counter(domains).items():
    print(f'  {domain}: {count}')
"
```

#### Step 7: Re-train T5 Model (2-4 hours)

```bash
# Backup old model
mv models/t5-function-call-finetuned models/t5-function-call-finetuned-old

# Re-train
python3 scripts/t5_function_call_trainer.py

# This takes 2-4 hours depending on hardware
# You can run in background:
# nohup python3 scripts/t5_function_call_trainer.py > training.log 2>&1 &
# tail -f training.log  # to monitor
```

#### Step 8: Test New Model (30 minutes)

```bash
# Test generation
python3 scripts/custom_input_demo.py

# Compare with old model by temporarily swapping:
# mv models/t5-function-call-finetuned models/t5-function-call-finetuned-new
# mv models/t5-function-call-finetuned-old models/t5-function-call-finetuned
# python3 scripts/custom_input_demo.py
# (swap back when done)
```

#### Step 9: Document Results (1 hour)

Create comparison document:

```bash
cat > docs/evaluation/dataset-expansion-results.md << 'EOF'
# Dataset Expansion Results

## Before Expansion
- Components: 3,346 (960 modules, 1,910 activities, 476 assessments)
- Training examples: 90 (30 per domain)
- Model: T5-small fine-tuned

## After Expansion
- Components: [NEW COUNT]
- Training examples: [NEW COUNT]
- Model: Re-trained T5-small

## Performance Comparison

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| JSON Validity | 100% | [%] | [%] |
| T5 Utilization | 85% | [%] | [%] |
| Avg Generation Time | 2.3s | [s] | [s] |
| Component Diversity | [score] | [score] | [score] |

## Observations
- [Add qualitative observations]
- [Generation quality]
- [Training insights]

## Conclusion
[Summary of whether expansion improved system]
EOF

# Edit with your actual results
nano docs/evaluation/dataset-expansion-results.md
```

---

## 🎯 Validation Checklist

After expansion, verify:

```bash
# 1. Component counts increased
python3 -c "
import json
print('Components:')
print(f'  Modules: {len(json.load(open(\"data/components/modules.json\")))}')
print(f'  Activities: {len(json.load(open(\"data/components/activities.json\")))}')
print(f'  Assessments: {len(json.load(open(\"data/components/assessments.json\")))}')
"

# 2. Training data increased
python3 -c "
import json
data = json.load(open('data/training/t5_function_call_training.json'))
print(f'Training examples: {len(data)}')
"

# 3. Vector store rebuilt
python3 -c "
from src.rag.vector_store import SyllabusComponentStore
store = SyllabusComponentStore()
stats = store.get_collection_stats()
print(f'Vector store: {stats[\"total_components\"]} components')
"

# 4. Model exists
ls -lh models/t5-function-call-finetuned/

# 5. System still works
python3 scripts/custom_input_demo.py
```

---

## 🚨 Troubleshooting

### Issue: Import errors from stem_components_generator.py

**Cause:** Missing `models.py` file in `src/data/`

**Fix:** Check what schema files exist:
```bash
ls src/data/
# Look for: models.py, schemas.py, or educational_models.py
```

If missing, you'll need to create it or adjust imports.

### Issue: API rate limit errors

**Fix:** Increase delay in generator:
```python
# In stem_components_generator.py line 38
self.rate_limit_delay = 3.0  # Increase from 2.0 to 3.0
```

### Issue: Training fails with CUDA/memory errors

**Fix:** Reduce batch size:
```bash
# Edit scripts/t5_function_call_trainer.py
# Change training batch size from 2 to 1
```

### Issue: Vector store doesn't reflect new components

**Fix:** Force rebuild:
```bash
rm -rf chroma_db
python3 scripts/rebuild_vector_store.py
```

---

## ⏱️ Time Estimates Summary

| Task | Time | Can Skip? |
|------|------|-----------|
| Pre-check & backup | 15 min | No |
| Generate components | 3-4 hours | Yes* |
| Merge components | 30 min | Yes* |
| Rebuild vector store | 20 min | Yes* |
| Generate training data | 30 min | No |
| Re-train T5 | 2-4 hours | No |
| Test & validate | 30 min | No |
| Document results | 1 hour | No |
| **TOTAL** | **8-11 hours** | |

*You can skip component generation and just generate more training data from existing components (Option 1)

---

## 💡 Pro Tips

1. **Start on weekend** when you have 8-hour blocks
2. **Run training overnight** (it's automated)
3. **Monitor API costs** via Anthropic console
4. **Save incrementally** (scripts already do this)
5. **Test old model first** for baseline comparison
6. **Document as you go** for evaluation chapter

---

**Remember:** Only do this if you're ahead of schedule. Evaluation chapter and web app are higher priority!
