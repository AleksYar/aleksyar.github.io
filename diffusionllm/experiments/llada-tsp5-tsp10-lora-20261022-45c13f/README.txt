LLaDA LoRA: paired TSP5 and TSP10 experiment

STATUS
Training, scoring, reporting, checkpoint recovery, and Slurm launch scripts are
implemented. The launch status and actual Slurm IDs are recorded separately in
submission.json and launch-status.json. Do not infer a running job from these docs.

SCOPE
Two independent adapters, each initialized from untuned GSAI-ML/LLaDA-8B-Instruct.
TSP5: 10,000 training examples and 100 validation cases on one A40.
TSP10: 10,000 training examples and 100 validation cases on a second A40.
Total: 20,000 training examples and 200 validation cases.

DATA
Uniform, distinct integer coordinates in [0,999]^2; randomly assigned city IDs.
Instruction + input with two nearest-neighbor hints and distances per city.
Assistant target: a closed bracketed route plus objective rounded to 3 decimals.
Use the native LLaDA chat template. Only prompt is passed at evaluation.
Exact Held-Karp labels, unrounded Euclidean costs, start at 0, canonical reversal.
Validation geometry is excluded from training, including relabeled duplicates.
Every TSP5 label and two TSP10 examples were independently checked by exhaustive
search. Every stored route, length, and target was validated and tokenized.

FIRST RUN
One epoch, exactly 625 optimizer updates at effective batch size 16.
BF16 standard LoRA: rank 16, alpha 32, dropout 0.05, learning rate 0.0001.
Adapt attention and MLP projections within transformer blocks only.
Embeddings and output vocabulary head stay frozen. Note that LLaDA also calls its
vocabulary output layer ff_out; do not match every ff_out indiscriminately.
Microbatch 2 with 8 accumulation steps; activation checkpointing enabled.
If memory requires microbatch 1, preserve effective batch size with accumulation 16
and record the change. Do not silently switch to quantization.
AdamW, weight decay 0.01, 5% warmup, cosine decay, gradient clipping 1.0.
Maximum training sequence 1024 with dynamic padding; never truncate targets.
Use response-only masked diffusion loss and native bidirectional attention,
following the official LLaDA objective. Preserve EOS handling and inverse-mask-
probability weighting; no causal token shift or prompt corruption.
Profile throughput during the initial training updates to refine the ETA.
Save adapter, optimizer, scheduler, RNG, data position, and frozen configuration
at every 125 updates, every 15 minutes, and at the end. Verify checkpoint reload
consistency. Checkpoints are atomic and include data order and microbatch size.

EVALUATION
Generate one answer on all 100 validation cases before training and after epoch 1.
Use 512 output positions, 128 diffusion steps, one full block, temperature 0,
seed 42 for both stages and both problems. Use the official pinned sampler.
After updates 125 and 375, generate answers on the same fixed first 20 validation
cases as an intermediate diagnostic. These are subsets of the 100, not extra data.
The final epoch-1 adapter is the preselected primary result; no automatic extension
to more epochs and no selection of the best individual answer.
Report strict format compliance, complete tours, optimal tours, within-1% rate,
mean/median gap only among complete tours, missing/repeated cities, output length,
objective-value consistency, runtime, and GPU memory. Recompute route distances
from the coordinates; never trust the model's stated objective as the route cost.
Accept equivalent optimal cycles when assessing route quality. No route repair.
Store full prompts, readable answers, complete token arrays, and per-case scores.
Compare with exact optimum, nearest neighbor, and nearest neighbor + 2-opt.
These 100 cases are validation data. A later final claim needs an untouched test set.

SCHEDULING
Prepare data and verify the model cache before allocating GPUs.
Submit two separate Slurm batch jobs, requesting one A40 each; no distributed
training between the two adapters. Verify live account/partition authorization,
GPU resource spelling and job limits at submission. Preserve unique job IDs.
Set a longer, explicit wall limit after throughput profiling; the earlier 15-minute
inference cap is not sufficient. Save resumable checkpoints and preserve partial
results if a job stops; no blind resubmission or repeated baseline evaluation.
A rough planning allowance is 2-5 hours for the TSP5 experiment and 3-7 hours for
TSP10, with high uncertainty and queue time excluded. Parallel completion is
controlled by the slower experiment, not the sum. The only measured training
reference is a small QLoRA TSP20 pilot, so BF16 LoRA throughput must be measured.

REFERENCE
LLMCoSolver prompt/data structure and SFT concept are adapted; this is not a
replication of its model, trainer, data distributions, or reinforcement-learning stage.
https://github.com/Summer142857/LLMCoSolver/blob/main/Envs/TSPEnv/TSPEnv.py
https://github.com/Summer142857/LLMCoSolver/blob/main/main_train.py
https://github.com/ML-GSAI/LLaDA/blob/main/GUIDELINES.md

RUNNING AND RECONNECTING
On Newton, from this experiment directory:
  bash setup.sh
  sbatch --test-only profile.sbatch
  sbatch --parsable profile.sbatch
After the short A40 profile completes for both tasks:
  source env.sh
  "$TRAIN_PYTHON" submit.py
submit.py validates both profiles, tests each allocation, records intent and job
IDs, and prevents repeat submission. Each production job requests one A40,
4 CPUs, 48 GiB host RAM, and an 8-hour wall limit. It runs independently of SSH.

The profile uses a fresh temporary adapter for each task; it is never continued
as the production adapter. Each full experiment starts from the untuned model.

RESULTS
  report.html: combined comparison
  tsp5/results/report.html and tsp10/results/report.html: detailed reports
  tsp*/results/all-answers.txt: all prompts and readable answers
  tsp*/results/answers.jsonl: answers, full token arrays, scores, timings
  tsp*/results/adapter/: final LoRA adapter
  tsp*/results/checkpoints/: resumable adapter and optimizer state
  tsp*/results.zip: report, all answers, logs, final adapter (no full checkpoints)
  tsp*/results/status.json: current phase and optimizer update
  logs/: Slurm console logs

Checkpoint loading verifies source/data/configuration identity. A requeued job
resumes the latest checkpoint and skips saved answers. Slurm preemption can
requeue the job; a wall-limit interruption saves partial progress and requires
a deliberate resumed allocation. A time limit does not extend itself.

Do not edit code, datasets, or configuration while these experiments run. Saved
training-state.pt files are trusted files created by this experiment; do not
replace them with downloaded pickle files.
