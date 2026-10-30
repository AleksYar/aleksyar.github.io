Live terminal access to the latest two LLaDA checkpoints

Start on this Mac:
bash [workspace]/newton/chat-latest-checkpoints.command

Checkpoint choices:
/model latest   — final additional-300k checkpoint 018750 (default)
/model previous — final 500k checkpoint 031250

/reset — start a new conversation
/paste — multiline prompt; finish with /send on a separate line
/exit  — disconnect; the session remains available until its time limit
/stop  — terminate the service and release its GPU

Generation: 256 calls, 256-token response canvas, one block, temperature 0, seed 42.
The selected trained LoRA stays enabled for every prompt. The TSP-specific
selector head is not invoked. No city slots, vocabulary filtering, fixed route
format, external repair, or learned-remasking loop is used. This is ordinary
LLaDA text generation, not the specialized historical TSP benchmark protocol.

Newton job 1469393: one NVIDIA L40S on nlp-l40-1.
Allocation: 30 October 2026, 20:41:26–21:41:26 Asia/Jerusalem.
Maximum allocation: 1 GPU-hour. No training or benchmark sweep.
Checkpoint reloads are checked against their saved tensors and SHA256 hashes.
Two service verification requests are separate from a quality evaluation.
Prompts, answers, and raw generated tokens are saved privately in
[cluster-home]/llada-live-checkpoints-20261030-8d4c2a/transcripts.jsonl.

SSH authentication and the session must remain active. The launcher reconnects
the private tunnel; it never submits a replacement GPU job. After the allocation
ends, a new live session must be requested.
