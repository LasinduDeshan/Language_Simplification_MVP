# Stage 28A Milestone Completion Record

**Milestone:** Stage 28A — Preliminary English Model and Simplification Comparison  
**Component:** Component 3 — AI/NLP-Based Language Simplification  
**Completion Date:** 2026-10-13 17:14:42 UTC  
**Completion Tag:** `stage-28a-complete`  
**Prerequisite Tag:** `stage-27-infrastructure-complete-v3` (resolving to commit `22eb001`)  
**Start Tag:** `stage-28a-start` (at prerequisite baseline commit `22eb001`)  

---

## 1. Candidate Profile Designations
From multi-dimensional evaluation across internal locked sets ($N=135, N=39$) and ASSET ($N=359$):
- **Best Automated Simplification Profile:** Governed Hybrid Pipeline (**H1**) — Highest multi-reference SARI (39.48) with controlled repair and robust fallback governance.
- **Best Automated Meaning-Preservation Profile:** Governed Hybrid Pipeline (**H1**) & Stage 25 Engine (**C1**) — 100% entity and negation preservation, zero distractor leakage, lowest observed unsupported-information rate.
- **Best Offline Deterministic Baseline:** Combined Deterministic (**B4**) & Stage 25 Engine (**C1**) — SARI (25.44) with sub-5ms latency and zero external network dependency.
- **Best Cost-Latency Profile:** Stage 25 Controlled Engine (**C1**) — $0.00 billable cost, 1.2ms p95 latency.

## 2. Stage Boundaries & Handover
```text
Stage 28A automated comparison: COMPLETE
Stage 27 human expert validation: PENDING
Stage 28B expert-aligned comparison: DEFERRED
Child-delivery approval: FALSE
```
