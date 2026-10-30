TSP20 best-of-8: 50 validation cases across four L40S GPUs

This fresh run replaces cancelled job 1460442 at the user's request. The old
attempt and its partial answers remain preserved in their original directory.

Dataset: first 50 cases in the original frozen 100-case validation order.
The subset was chosen by order, not by model results. All historical greedy
and CPU baseline comparisons in this report use exactly the same 50 cases.
This is reused validation data, not an untouched held-out test set.

The final 100k-example SFT adapter, prompts, per-candidate seeds, BF16 base,
FP32 adapter weights, temperature 0.7, 512 output positions, 128 diffusion
passes, and original pinned sampler are preserved from the cancelled run.

One Slurm allocation reserves four L40S GPUs on nlp-l40-1, 16 CPU cores,
128 GiB host memory, and at most two hours. Four Slurm tasks are each bound
to one physical GPU. Worker 0 generates candidate indices 0 and 4 for each
case; worker 1 generates 1 and 5; worker 2 generates 2 and 6; worker 3 generates
3 and 7. This is exactly 100 sampled answers per GPU, 400 total. All samples
are generated fresh; none are imported from the cancelled attempt.

Each worker must load the adapter exactly, match all 50 saved prompt token
arrays, and reproduce one historical temperature-0 answer exactly. The driver
verifies four distinct physical GPU UUIDs before releasing the workers to
sample. These four replay checks are excluded from the 400 candidates.

Selection uses the shortest valid closed tour, with length recomputed from
coordinates. Every city must occur once before closing the cycle. No repairs
are made. The model's claimed objective and reference optimum do not guide
selection. All raw answers and generated token canvases are retained. Best-
of-1/2/4 prefix metrics are also reported from the same candidate samples.

Each worker writes independent status and event files. Candidate filenames
are disjoint by worker assignment and are written atomically. Only the driver
writes aggregate reports. A case enters best-of-8 scores only when all eight
candidates are saved. Complete means 400 candidates, 50 complete groups,
four successful workers, and subsequently verified Slurm COMPLETED/exit 0:0.

No downloads, RL, additional fine-tuning, automatic retry, or requeue.
Raw files: results/candidates/. Per-worker records: results/workers/.
Report: results/report.html. Config and source hashes are frozen pre-submission.

Parallel Slurm task and GPU binding reference:
https://slurm.schedmd.com/srun.html
Newton launch instructions consulted in the same session:
https://hpc.cs.technion.ac.il/clusters/newton/how-to-launch-jobs/
