LLaDA TSP20: 300,000 examples with masks covering 5-8 cities

Authorized: 30 October 2026. Continue the model trained in the last experiment.
Parent: llada-tsp20-500k-remask-dup03-4l40-20261028-be3024,
        results/checkpoint-031250, trained adapter AND prediction head.
The parent files are verified by SHA256 and exact loaded-tensor comparisons.
AdamW starts fresh. This experiment adds 300k examples, one epoch / 18,750 updates.

All geometries are fresh TSP20 instances. There are no additional clean examples,
development geometries, test geometries, or scheduled quality evaluations.
Every training record has two views: masked reconstruction and full-route mask
scoring. Every selected and assessed mask is a contiguous segment of 5-8 internal
city positions; both digit tokens per city are masked together. The first/final
zero stays visible in correction inputs. Candidate IDs retain the parent mapping.

Construction: 50% perturbations of optimal tours, 30% heuristic tours (20%
nearest-neighbor and 10% nearest-neighbor plus 2-opt), 10% duplicate/missing-city
routes, and 10% optimal KEEP controls. Heuristic local optima become zero-gain
controls. All controls also receive a 5-8-city denoising view, with the unchanged
current tour as target, while teaching the selector zero gain. This keeps every
record within the minimum-mask contract and gives every record two passes.

Exact conditional solver labels nine candidate actions initially. It searches
remaining allowed actions if necessary to find an improving edit, otherwise
records local KEEP. The teacher holds unmasked positions fixed. Only assessed
actions receive selector loss. These labels measure oracle conditional gain,
not improvement observed from an LLaDA rollout. This is supervised training.

Loss per record: masked-token CE + 0.3 duplicate loss + 0.1 selector loss.
Selector: Huber gain loss + feasibility BCE + 0.1 pairwise-ranking loss.
Existing rank-64 LoRA and the trained 1,320,834-parameter prediction head train
together; the original LLaDA base, embeddings and vocabulary head stay frozen.
LR: LoRA 1e-5; prediction head 3e-4. AdamW weight decay 0.01; cosine schedule,
5% warmup; gradient clipping 1.0. BF16 forwards, FP32 trainable parameters.

Hardware: four L40S GPUs on Newton's canonical node nlp-l40-2 (requested as
nlp-l40s-2), accessed using SSH. Effective batch 16: four sequential records per
GPU. There are 600,000 forward/backward views in the full training epoch.

One allocation runs two disposable short profiles (3 warmup + 7 timed updates
each), checks measured cost and gradient consistency, then reloads the original
parent adapter and head for full training. Profile weights are never reused.
The training gate rejects a projected upper duration over 19 hours. The Slurm
allocation limit is 20 hours; it is not a measured or promised completion time.

Initial estimate: approximately 14-17 hours on four L40S GPUs for training,
including routine checkpoint/loading overhead; roughly 56-68 GPU-hours. CPU
data preparation, transfer, queueing and interruption recovery are separate.
Check profile/estimate.json for the measured update after the quick test.

Open results/report.html for the normal experiment page. Status is a saved
snapshot, not a background monitor. Training weights remain on Newton.
