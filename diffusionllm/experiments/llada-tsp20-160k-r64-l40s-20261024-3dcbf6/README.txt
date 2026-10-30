TSP20 · 160,000 examples · rank-64 LoRA · 24 October 2026

One fresh LLaDA-8B-Instruct adapter, one epoch, one NVIDIA L40S.
Rank 64, alpha 64, dropout 0.05; frozen BF16 base and FP32 adapters.
Microbatch 2 × accumulation 8 = effective batch 16; 10,000 optimizer updates.
AdamW, learning rate 0.0001, weight decay 0.01, cosine schedule, 500 warmup updates.
Activation checkpointing is OFF, including after evaluation.

Permanent, resumable checkpoints after 80,000 examples (update 5,000) and
160,000 examples (update 10,000). Each includes adapter weights, optimizer,
scheduler, data order and RNG state. Stable pointers are in
tsp20/results/milestones/update-005000.json and update-010000.json.
Two recent recovery checkpoints are also retained, saved every 125 updates
or 15 minutes. The final adapter is additionally saved in tsp20/results/adapter.

The dataset reuses 100,000 verified TSP20 training examples and adds 60,000
new unique instances from seed 24102026, prepared using eight Mac CPU workers. A single seeded shuffle mixes all
160,000 examples; each is visited once. Exact MILP labels are checked, and
training geometries cannot overlap the fixed 100 validation cases.
Validation is run before training, at 80k examples and at 160k examples:
100 answers per stage, 512 output positions, 128 diffusion steps, seed 42,
temperature zero, one answer per instance, no repair. All raw answers and
token arrays are saved. Validation is not an untouched final test set.

Measured rank-64 throughput projects to 12.48 training GPU-hours, with the
midpoint at 6.24 training hours. Allow 15–18 GPU-hours for the full experiment
including validation, checkpoint I/O and throughput variation; queue time,
preemption and CPU data preparation are additional. Estimated peak allocated
GPU memory is about 33.5 GiB for these roughly 976-token training examples.

Run bash prepare_local.sh on the Mac to generate and validate the data.
Upload the verified dataset and frozen sources to the new experiment directory
on Newton, then run submit.py there. It verifies all dataset hashes before
submitting one GPU job. Rerunning submit.py does not submit a duplicate once
its job ID has been recorded. The allocated GPU job independently checks the
complete tokenized dataset, then performs a four-update save/reload check
before training starts fresh. The 24-hour allocation supports resumable stops.
Do not modify frozen source/config files after preparation or submission.

The experiment reuses the existing Newton GPU environment read-only. The
Mac uses the existing local CPU environment and the pinned original tokenizer.
Open experiment.html for the protocol, report.html for the latest collected
status, and tsp20/results/report.html for results after the first collection.
Local status is a snapshot, not a live monitor.
