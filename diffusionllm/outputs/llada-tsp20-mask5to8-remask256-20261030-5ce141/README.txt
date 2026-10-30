TSP20 new 300k continuation: same 100 subjects, 256 total model calls

Checkpoint: [cluster-home]/llada-tsp20-300k-mask5to8-4l40s-20261030-508fc3/results/checkpoint-018750

One condition, one seed schedule (42 + case index), four independent L40S replicas, 25 cases each. No training or extra comparison run. Reuse existing 100 geometries, prompts, references and ordering byte-for-byte.

Initial generation uses 16 passes. The trained head then scores only the 54 contiguous masks of 5–8 internal city positions, on valid and invalid routes alike. One selector call plus up to 16 useful generation calls per block counts against a total cap of 256. Both digit tokens are actually masked; unselected fields remain fixed. Typically a block uses 5–8 reconstruction calls, with a shorter last block if budget requires. No permutation enforcement. No objective acceptance rule, best-tour retention, KEEP stop threshold or exclusion of repeated actions. Always return the latest completed route.

Objectives are independently recomputed after generation using unrounded Euclidean distances, including the closing edge. Invalid tours have no valid objective/gap. Historical comparison reuses saved previous results; it changes both checkpoint and permitted mask sizes, so it is not an isolated weight-only comparison.

Expected allocation: about 13–17 minutes / 0.85–1.10 GPU-hours, extrapolated from the previous comparable 100-case run (12m48s actual). Queue and transfers are additional. Hard job cap is 25 minutes.
