TSP20: unfiltered learned remasking, up to 256 total model calls

Scope: one condition, one final checkpoint, the same100 benchmark geometries,
one deterministic trajectory per geometry. No training or extra quality tests.
Checkpoint: final500k continuation, update31250, with its trained prediction head.
Hardware: four L40S replicas on nlp-l40-2, 25 cases per replica.

Protocol:
1. Generate19 internal city fields using16 diffusion forwards.
2. One additional backbone/head forward selects an action. This forward counts.
3. Replace BOTH digit tokens of the selected city fields with MASK_ID126336.
4. Reconstruct using at most16 forwards, at most one per masked city, shortened
   at the budget boundary. Existing confidence-based whole-city commitments apply.
5. Always use the reconstructed route as the next input, including invalid,
   longer, equal-length and unchanged routes. Never retain a best route.
6. Repeat until fewer than two of the256 calls remain. Return the last route.

The stop/KEEP threshold is disabled for this fixed-budget test. Previously tried
masks are not excluded: the learned head can repeatedly choose an unchanged edit.
No external tour lengths or reference optimum enter the trajectory. The trained
head retains its existing route-validity feature and gain/feasibility outputs.
City00 remains fixed at both ends, internal city values are in01..19, and the
format is fixed. Uniqueness is not enforced. This preserves the trained decoder.

Save actual mask-token positions/IDs, every commitment, every reconstructed route,
head scores, per-cycle counts and the final response token IDs. Score all stages
independently after inference. Primary metrics use the final route, never the best
intermediate route. Earlier128-call filtered results are historical context only:
this test also changes budget and stopping rules, so it is not a single-factor
comparison. Deterministic repetition is a possible failure mode to report.

Estimate (extrapolated):14–18 allocation minutes,0.91–1.20 GPU-hours, queue time
unknown. Hard job limit25minutes. CPU verification passed before GPU submission.
