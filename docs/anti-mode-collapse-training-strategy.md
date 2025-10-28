# Anti-Mode-Collapse Training Strategy

## Problem Summary
- **Observed**: Model generates ~70 tokens (lines 1-3: set_info + objectives) then emits EOS
- **Expected**: Model should generate ~404 tokens (lines 1-12: full sequence through assessments)
- **Root Cause**: Mode collapse - model found local optimum (short outputs minimize loss)
- **Additional Issue**: Exposure bias - model never trained on its own errors, drifts during auto-regressive generation

## Why Original Approach (20 epochs, standard training) Failed
1. Model found shortcut: Generate easy prefix → EOS → low loss achieved
2. Never learned module/activity/assessment patterns (lines 5-12)
3. Exposure bias: Trained with teacher forcing, fails during auto-regressive inference
4. Insufficient epochs to escape local optimum (20 epochs not enough)

## Three-Phase Robust Approach

### Phase 1: Diagnostic Training (30-45 min) - VALIDATE APPROACH
**Goal**: Verify anti-mode-collapse techniques work before committing to long training

**Configuration**:
- Epochs: 5 (quick validation)
- EOS masking: First 150 tokens
- Position weighting: 1.0x → 2.0x (mild)
- Gradient accumulation: 4 (increased diversity)

**Success Criteria**:
- Output length increases from 70 → 100+ tokens
- At least some module calls appear in outputs
- No complete gibberish when forcing min_length=200

**Decision Point**:
- ✅ If success → Proceed to Phase 2 (Curriculum Learning)
- ❌ If failure → Switch to Phase 2B (Progressive Fine-Tuning)

---

### Phase 2A: Curriculum Learning (3-4 hours) - GRADUAL TEACHING
**Goal**: Gradually teach model to generate longer, more structured outputs

**Stage 1 (Epochs 1-10)**: Learn Objectives + Early Modules
- EOS masking: First 100 tokens
- Position weighting: 1.0x → 1.5x
- Target: Model learns to go beyond objectives, start generating modules

**Stage 2 (Epochs 11-25)**: Learn Full Module Sequence
- EOS masking: First 200 tokens
- Position weighting: 1.0x → 2.5x
- Target: Model generates all modules, starts activities

**Stage 3 (Epochs 26-40)**: Learn Complete Sequences
- EOS masking: First 250 tokens
- Position weighting: 1.0x → 3.0x
- Target: Model generates complete sequences (objectives → modules → activities → assessments)

**Stage 4 (Epochs 41-50)**: Refinement
- EOS masking: First 200 tokens (relaxed slightly)
- Position weighting: 1.5x → 3.0x
- Target: Clean, consistent complete outputs

---

### Phase 2B: Progressive Fine-Tuning (Backup if 2A fails)
**Goal**: Build up capability incrementally

**Step 1**: Filter training data to only objectives (no modules/activities/assessments)
- Train 10 epochs until perfect
- Model learns: set_info → objectives → EOS

**Step 2**: Add modules to training data
- Train 10 more epochs on objectives + modules
- Model learns: set_info → objectives → modules → EOS

**Step 3**: Add activities
- Train 10 more epochs on full data minus assessments
- Model learns: ... → modules → activities → EOS

**Step 4**: Add assessments (complete)
- Train 10 more epochs on full data
- Model learns complete sequences

---

## Implementation Details

### Custom Trainer with Anti-Mode-Collapse Loss

```python
class AntiModeCollapseTrainer(Trainer):
    def compute_loss(self, model, inputs, return_outputs=False):
        # Get labels and outputs
        labels = inputs.get("labels")
        outputs = model(**inputs)
        logits = outputs.get("logits")

        # Per-token cross-entropy loss
        loss_fct = torch.nn.CrossEntropyLoss(reduction="none")
        shift_logits = logits[..., :-1, :].contiguous()
        shift_labels = labels[..., 1:].contiguous()
        loss = loss_fct(shift_logits.view(-1, shift_logits.size(-1)),
                       shift_labels.view(-1))
        loss = loss.view(shift_labels.size())

        # FIX 1: Mask EOS tokens for first N positions
        batch_size, seq_len = shift_labels.size()
        for b in range(batch_size):
            for pos in range(min(self.min_length_tokens, seq_len)):
                if shift_labels[b, pos] == self.eos_token_id:
                    loss[b, pos] = 0.0  # Don't penalize/reward EOS here

        # FIX 2: Position-based weighting (encourage full sequences)
        position_weights = torch.linspace(
            self.position_weight_start,
            self.position_weight_end,
            seq_len,
            device=loss.device
        )
        position_weights = position_weights.unsqueeze(0).expand(batch_size, -1)
        weighted_loss = loss * position_weights

        # Mask padding
        mask = (shift_labels != -100).float()
        weighted_loss = weighted_loss * mask

        # Average over non-padding tokens
        final_loss = weighted_loss.sum() / mask.sum()
        return (final_loss, outputs) if return_outputs else final_loss
```

### Generation Parameters During Testing

```python
# After training, test with:
output = model.generate(
    input_ids,
    max_length=536,
    min_length=300,  # Enforce minimum (model should have learned patterns)
    num_beams=4,
    early_stopping=False,  # Don't stop until complete
    no_repeat_ngram_size=2,
    length_penalty=1.2,  # Slight bias toward longer outputs
)
```

---

## Timeline Estimates

| Phase | Duration | Cumulative | Risk |
|-------|----------|------------|------|
| Phase 1 (Diagnostic) | 30-45 min | 0.5-0.75 hr | LOW - Quick validation |
| Phase 2A (Curriculum) | 3-4 hours | 3.5-4.75 hr | MEDIUM - Standard approach |
| Phase 2B (Progressive) | 3-4 hours | 3.5-4.75 hr | LOW - Conservative fallback |

**Total Time**: 3.5-5 hours (with validation and potential fallback)

---

## Success Metrics

### After Phase 1 (Diagnostic):
- ✅ Output length: 100-150 tokens (up from 70)
- ✅ Some module calls present
- ✅ No gibberish when min_length=200

### After Phase 2 (Full Training):
- ✅ Output length: 350-450 tokens (target: 404)
- ✅ Evaluation tests: ≥80% pass rate (was 0%)
- ✅ All sections present: objectives → modules → activities → assessments
- ✅ Valid Python syntax: 100%
- ✅ Executable code: ≥80%

---

## Why This Approach is More Robust

1. **Early Validation** (Phase 1): We don't waste 5-10 hours on wrong approach
2. **Gradual Teaching** (Curriculum): Model learns progressively, not all-at-once
3. **Fallback Plan** (Progressive): If curriculum fails, we have Plan B
4. **Addresses Root Causes**:
   - Mode collapse: EOS masking + position weighting
   - Exposure bias: Longer training allows model to self-correct patterns
   - Data scarcity: Curriculum learning more efficient with small datasets

4. **Literature-Backed**:
   - Curriculum learning: Well-established for complex seq2seq tasks
   - Progressive fine-tuning: Used in multi-task learning
   - Position weighting: Common in hierarchical generation

---

## Alternative Considered: Scheduled Sampling

**Why Not Implemented** (but could be added if Phase 2 fails):
- Scheduled sampling: Gradually replace teacher forcing with model predictions
- Addresses exposure bias directly
- More complex implementation (requires custom training loop)
- Save as Phase 3 if needed

---

## Decision Matrix

```
Phase 1 Results → Next Action
─────────────────────────────────────────────────────────
Success (100→150 tokens) → Phase 2A (Curriculum)
Partial (70→90 tokens)   → Phase 2B (Progressive)
Failure (still 70 tokens) → Investigate data/tokenization issue
Gibberish (random output) → Check model loading/device issues
```

---

## Academic Value (For Dissertation)

This demonstrates:
1. **Problem diagnosis**: Identified mode collapse through systematic analysis
2. **Root cause analysis**: Traced to training optimization, not architecture
3. **Solution validation**: Multi-phase approach with checkpoints
4. **ML expertise**: Understanding of exposure bias, curriculum learning, loss engineering
5. **Engineering rigor**: Not just "try more epochs", but principled debugging

This is graduate-level ML engineering suitable for MSc dissertation.
