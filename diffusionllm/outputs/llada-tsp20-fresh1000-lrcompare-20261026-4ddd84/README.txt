TSP20: fresh 1,000-case comparison of continued learning rates

Training job: 1463107. Comparison runs only after that job completes successfully.
Resources: four L40S on nlp-l40-1, cs/public, 16 CPU threads, 128 GiB host memory,
12-hour allocation cap. Expected inference duration is 6–8 hours, plus queueing.

Frozen fresh set: 1,000 exact-labeled TSP20 geometries, seed 2610202601.
Excluded: the original 200k training set, earlier 160k training set, reused 20k
continuation set, and all 100 old validation cases. Prompt format, coordinate
distribution, exact solver, decoding settings and score definitions match the
training experiments. References never enter model prompts.

Conditions: original 200k adapter; previous LR 1e-4 epoch 8; previous LR 1e-4
epoch 10; new LR 1e-5 epoch 10; and the new best epoch if different from epoch 10.
Choose that last checkpoint using only the old 100 cases: highest optimal-tour
count, then highest complete-tour count, then lowest mean complete-tour gap,
then earliest epoch. The fresh set does not participate in selection.

Inference: BF16 base, FP32 LoRA, one answer per instance, 512 output positions,
128 official diffusion steps, temperature zero, seed 42 + case index. The same
case has the same seed for every checkpoint. No retries, repair, or best-of-k.
Before fresh inference, four original-checkpoint answers must reproduce the
corresponding saved answers from the preceding matched four-GPU evaluation.

All raw outputs, prompts, token IDs, exact reference solutions and coordinate-
recomputed scores are saved. Gap is defined only for complete tours. Generated
numeric objectives are checked separately. Paired differences and descriptive,
approximate 95% intervals are recorded; intervals are not multiplicity adjusted.

Checkpoint weights remain on Newton and are hash-verified before loading.
Atomic per-case files allow resumption after preemption. The comparison is
bounded to four or five checkpoints (4,000–5,000 answers), not an open-ended sweep.
Completion requires every requested case for every resolved checkpoint and
successful Slurm accounting; a report alone does not prove job completion.
