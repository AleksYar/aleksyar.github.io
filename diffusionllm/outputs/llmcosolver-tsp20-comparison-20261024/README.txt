TSP20 / LLMCoSolver baseline preparation — 24 October 2026

Open report.html for the comparison. comparison.json contains exact values.
This folder has no LLMCoSolver weights or generated baseline answers.
No GPU job was submitted. The published checkpoint folder reports an expired link.

What is ready
- The exact 100 TSP20 validation geometries from the latest LLaDA 100k run.
- Native LLMCoSolver Alpaca prompts, including the same two-neighbor hints.
- Exact full-precision references, retaining the saved MILP certificates.
- Pinned upstream source at f6388991d243c0aa91d9ee7e2fa18ed1c9e72477 (MIT license).
- A local-only causal-LM inference runner that saves every candidate and token ID,
  uses strict tour scoring, and supports greedy or separate best-of-8 evaluation.
- An independent rescore of all 100 LLaDA answers and replay of the upstream scorer.

Validation executed locally
  python run_baseline.py --validate-only
  python prepare_comparison.py
The preparation audit also needs NumPy. In this workspace the project .venv works.
The inference path has NOT been GPU-tested, and no new CUDA environment is installed.

Checkpoint access and identity
The author linked a shared OneDrive folder in GitHub issues #2, #4, #5 and #6.
The common link currently says “Sorry, the link has expired.”
Issue #2 reports base_model_name_or_path=unsloth/Meta-Llama-3.1-8B in a shared
adapter, even though the default training model is unsloth/Qwen2.5-7B. The author
recommends using the base model specified by the adapter. Do not merge into Qwen
without checking the actual adapter. Issue #6 confirms CVRP SFT/RL checkpoints;
it does not establish availability of a TSP SFT-only checkpoint.
Getting the original trained model requires a renewed link or a local copy.
No message has been sent to the authors.

Before executing a real baseline
1. Obtain a TSP checkpoint and verify its training stage and adapter base model.
2. Make a fresh run directory; keep this preparation and its hashes intact.
3. Prepare an isolated CUDA environment compatible with that checkpoint. The
   earlier LLaDA environment uses Transformers 4.38.2; do not assume it supports
   the released Llama checkpoint. Do not upgrade the working LLaDA environment.
4. Download and pin the correct base and tokenizer outside a GPU allocation.
   This runner only loads local files, with offline mode and trust_remote_code=False.
5. Verify current Newton account/partition, storage, GPU spelling and job budget.
   Use an allocated GPU, never the login node. Start with one greedy answer per case.
6. Inside that allocation, call run_baseline.py with --model-dir, optional
   --adapter-dir, --base-model-id matching adapter metadata, --stage sft or sft_rl,
   and --out naming a fresh attempt directory. The runner records checkpoint hashes.
   Its default soft limit is 6,600 seconds; set a matching scheduler hard cap with
   time reserved for scoring. No runtime estimate has been measured for this model.
7. Collect answers, candidates, scores, run provenance and Slurm accounting.
   Rescore and register the executed attempt separately in the experiment dashboard.

Fair comparison
Primary: same 100 TSP20 geometries; one greedy answer; no repair; native prompt
wrappers; identical coordinate and nearest-neighbor information; strict route
validation; gap only on valid tours, plus validity and within-1%-of-optimum over
all requested cases. Route length is recomputed from coordinates.
Secondary: a separately named best-of-8 run, selecting the shortest valid tour.
Repository defaults are temperature 0.7 / top-p 0.9. The paper states top-p 0.7.
Record this choice explicitly rather than describing the defaults as exact replication.
The current 100 cases are validation/development data observed during training.
Use a fresh disjoint test set for the final comparison after fixing settings.

An alternative if original weights remain inaccessible is to train Qwen2.5-7B
on exactly our 100k TSP20 examples. This would compare autoregressive and diffusion
SFT with matched data; it would not reproduce the paper's 500k mixed-size training.
No new fine-tuning job has been prepared or submitted here.
