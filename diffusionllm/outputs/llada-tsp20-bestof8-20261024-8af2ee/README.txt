TSP20 best-of-8 evaluation of the final 100k-example LLaDA LoRA adapter

Requested node: nlp-l40-1. One NVIDIA L40S, four CPU cores, 64 GiB host memory,
12-hour maximum allocation. Existing model cache and environment are reused.
No downloads, training, RL, route repair, or automatic retry/requeue.

100 exact same validation cases as the after-training evaluation. Each gets
eight fresh independently seeded samples at temperature 0.7. The eight do not
include the earlier temperature-0 answer. The native chat template, nearest-
neighbor prompt hints, 512 output positions, 128 passes, BF16 base and FP32
LoRA weights match the training evaluation. The original pinned official
sampler is unchanged; samples run sequentially with batch size one.

The shortest mathematically valid bracketed closed tour wins. Every city must
appear exactly once before closing the cycle; any start/direction is allowed.
Strict output-format compliance is reported separately. Selection uses distances
recomputed from coordinates, not the model's reported objective or the reference
optimum. If all eight answers are invalid, the group is invalid and the first
answer is retained for inspection. All 800 answers and full token canvases are
saved. Best-of-1/2/4 prefix results isolate selection gains at the same temperature.

Before the 800 samples, one additional temperature-0 answer must reproduce the
historical 512-token output exactly. All 100 prompt token arrays and loaded
adapter weights must also match the recorded training evaluation. This replay
is a validation check and is excluded from the eight candidates.

Existing HiGHS MILP references include connected tours, zero reported MIP gaps,
and primal/dual agreement, using float64 unrounded Euclidean costs. Their route
lengths and certificates are validated before launch. The mean optimality gap
is defined only on valid tours. This is reused validation data, not an untouched
test set; no new decoding settings will be chosen after inspecting the results.

Each candidate is saved atomically. A group enters best-of-8 metrics only after
all eight candidates are present. A partial/interrupted run is never called
completed. This attempt does not resume automatically. Final completion also
requires Slurm COMPLETED with exit code 0:0.

Local entry point: results/report.html. Dashboard: ../../dashboard.html.
Run-local register_dashboard.py is the benchmark skill's dashboard helper with
the description corrected for this fine-tuned model and a candidate-file link.

Official scheduler instructions checked 2026-10-24:
https://hpc.cs.technion.ac.il/clusters/newton/how-to-launch-jobs/
https://hpc.cs.technion.ac.il/clusters/newton/partitions-accounts-and-qos/
