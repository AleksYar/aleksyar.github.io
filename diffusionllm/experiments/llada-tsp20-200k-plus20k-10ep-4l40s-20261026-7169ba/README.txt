TSP20 continuation: completed 200k adapter + 20k new examples, ten epochs

Continue the final 200k rank-64 checkpoint from experiment
llada-tsp20-200k-r64-dup-h200-20261025-392809, including its AdamW moment history.
Existing parent files are read-only. This run writes to its own experiment folder.

20,000 new exact MILP-labeled TSP20 examples; all 360,000 previous training
geometries and the fixed 100 validation geometries are excluded. Ten complete
shuffled passes; fresh random masks on every visit. 200,000 additional training
presentations, 1,250 optimizer updates per epoch, 12,500 additional updates total.

Four NVIDIA L40S on nlp-l40-1. Best measured execution settings: one example per
GPU per microbatch, four accumulation steps, global effective batch 16,
activation checkpointing disabled. BF16 frozen LLaDA-8B-Instruct base, FP32
rank-64/alpha-64 adapters, dropout 0.05, no quantization. The response-only masked
loss plus 0.1 city-collision loss is unchanged. Learning rate restarts with a
625-update warmup to 1e-4, then cosine decay to zero; AdamW weight decay 0.01,
gradient norm clipping 1.0. Throughput settings were measured; LR/loss weight are
retained experimental choices, not claimed quality optima.

Before full continuation, a 12-update gate uses this checkpoint and actual loss:
four updates on the longest new examples and eight on a representative sample.
Checks finite loss/gradients, frozen base samples, identical adapter replicas,
exact adapter reload, exact per-rank RNG/optimizer/scheduler restoration and tightly bounded
numerical next-update replay, one validation answer per GPU, and at least 6 GiB memory headroom.
Gate updates are discarded; full continuation reloads the parent checkpoint.

Evaluate the loaded 200k model before training and all 100 fixed validation cases
after each epoch, distributed across four GPUs. Same sampler: 512 answer slots,
128 denoising passes, temperature zero, seed 42 + instance index, one answer,
no repair or duplicate constraint. These reused validation cases are not a final
untouched test. Save every raw answer and coordinate-recomputed tour metrics.

Save a permanent full checkpoint every epoch and two rolling recovery checkpoints
at 125-update/15-minute intervals. Checkpoints include optimizer/scheduler state,
per-rank CPU/CUDA/Python RNG, step, recipe fingerprint and weight/state hashes.
Epoch order is reproducible from seed + epoch. Scheduler preemption signals
request a coordinated checkpoint and requeue. Hard wall limit: 12 hours.

Prior standard-loss four-GPU timing implies approximately 4.0 training hours,
plus model loading, validation, checkpoint I/O and queueing. The actual-loss gate
records an updated speed estimate. Check status with check.sh; download compact
results with fetch.sh. Large adapters and optimizer checkpoints stay on Newton.

Repair after initial gate job 1462555: a bitwise replay assertion rejected GPU
backward numerical variation. Diagnostic job 1462568 verified exact RNG and
optimizer restoration, identical losses and maximum weight difference 1.86e-8.
The revised gate requires exact checkpoint state, replica agreement, parameter
error <=1e-7, loss relative error <=1e-5 and gradient-norm relative error <=1e-3.
Original launch sources and failure evidence are preserved under attempts/.
