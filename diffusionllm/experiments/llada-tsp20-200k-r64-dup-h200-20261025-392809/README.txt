Fresh TSP20 rank-64 LoRA test with a city uniqueness loss

200,000 newly generated training examples, one epoch, fresh adapter on the pinned
LLaDA-8B-Instruct base. No adapter from an earlier run is loaded. Rank 64, alpha
64, dropout 0.05; BF16 frozen base and FP32 adapters. AdamW learning rate 1e-4,
5% warmup (625 updates), cosine decay, effective batch 16 = microbatch 8 x 2.
One H200 NVL on galileo4; activation checkpointing disabled.

Loss = response-only masked diffusion cross-entropy + 0.1 * city collision loss.
Independent random token masking and inverse masking-probability SFT weighting
are unchanged. The collision term reads only visible city digits and model
logits for masked digits. At each annotated route field, candidates are city
IDs 0..19 with the same digit width and compatible visible digits. Summed masked
digit logits are normalized over those candidates. The twenty first city
occurrences are included; the legal closing zero is excluded.

For each active city field i, the auxiliary loss is:
-log sum_c P_i(c) product_(j != i)(1-P_j(c)).
Average over active fields per example, then over the effective batch. The
factorized product penalizes duplicates with visible cities and collisions
between two masked city fields. Numerically clamp probabilities entering the
log-complement at 1-1e-6. This is a surrogate conditional on the known reference
field widths, not an exact decoded-tour probability. Cross-width formatting
errors are covered by the SFT term, not guaranteed away by this auxiliary loss.
Weight 0.1 is an experimental fixed choice, not a quality-tuned optimum.

Data preparation uses eight workers on the user's Mac CPU. Generate exact MILP
labels, check each optimum certificate, exclude all 160,000 earlier training
geometries and the fixed 100 validation geometries. New seed 25102026. Validate
all city spans and never truncate. Validation is the same 100 cases as previous
runs, not an untouched final test.

Permanent full checkpoints at 6,250 updates (100k examples) and 12,500 updates
(200k). Checkpoints contain adapter, optimizer, scheduler, shuffled order, and
RNG states. Keep two rolling recovery checkpoints in addition to milestones.
Training can resume after public-partition preemption without changing the
loss or recipe. All source/config/data hashes are frozen before submission.

Run a twelve-update GPU gate before full training: first four updates on the
longest actual examples, last eight representative; exact adapter reload and
one validation answer. Then begin full training with a fresh adapter. Evaluate
100 cases before, at 100k, and at 200k with the unchanged official sampler:
512 output slots, 128 diffusion passes, temperature zero, no duplicate filter,
no repairs, one answer per instance. Report total loss, SFT loss, collision loss,
validity, optimality, and coordinate-recomputed distance gap separately.

This experiment changes data amount and loss relative to the prior 160k run;
it is not a matched same-data ablation proving the auxiliary loss's effect.
