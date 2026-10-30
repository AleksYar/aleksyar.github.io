TSP10:100 fresh geometries;zero-shot transfer of the final TSP20-trained500k checkpoint and prediction head.
No new training. Adapter and head weights unchanged and verified by hashes.
The paired request contains200 cases total(100TSP10,100TSP40),one condition,one repetition each.

Protocol
Initial reconstruction uses 9 useful calls. Each subsequent block uses one backbone/head selector call, inserts real MASK token126336 at both digit positions for selected cities,and reconstructs in at most16 useful calls. Each completion is adopted regardless of validity or length. Keep/stop threshold and tried-action exclusion are disabled. The256-call cap includes all selector and reconstruction calls. A final block may be shortened to fit;stop with fewer than two calls left. Return the last completed route. No uniqueness constraint;city00 and formatting are fixed.

Variable-size implementation
The same learned head matrices score relative features;indexing uses N,relative positions divide by N-1,and neighboring positions wrap modulo N. Candidate masks remain all pairs and contiguous segments of length3..8;invalid tours additionally allow singletons. Decoder choices cover city01 through09. City00 cannot occur inside the tour. This changes size-dependent indexing only. AtN=20 the action ordering,prompt,token encoding,and head outputs were checked against the original implementation.

Data and scoring
100 distinct geometries,seed29112026,distinct integer coordinates in[0,999]^2. Existing same-size local data were scanned for overlap;none found. Exact reference routes and CPU nearest-neighbor/2opt baselines are stored separately and never passed to the model. TSP10 uses Held-Karp;TSP40 uses MILP with subtour cuts and saved optimality certificate. Primary objective is independently recomputed from unrounded Euclidean distances including the closing edge. Invalid routes have undefined objective/gap.

Resources and full paired cost
Two sequential jobs,each four independent L40S model replicas onnlp-l40-2;25cases per GPU. Estimated GPU allocation for both jobs33-52minutes,2.2-3.5GPU-hours,plus unknown queue/transfer time. Extrapolated from the completed TSP20 run,not a new-size measurement. Scheduler caps20min(TSP10)and55min(TSP40)are safety limits,not runtime estimates. The first ordinary cases refine timing;no extra profiling cases. CPU geometry/reference preparation took5.7seconds total.

All settings,input data,and runtime sources are frozen before submission. Offline reporting and dashboard helpers are outside the runtime fingerprint.
