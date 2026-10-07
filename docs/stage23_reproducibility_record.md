# Stage 23 Reproducibility Record

**Execution Environment:** Windows / Python 3.11  
**Execution Timestamp:** 2026-09-30 07:06:53 UTC  
**Baseline Git Commit:** `ca11b78` (`stage-23-start`)  
**Pinned ASSET Commit:** `9d659040d0d8942dbc4cd65cf357563b43fd9ab4`  

---

## 1. Deterministic Execution Steps

```powershell
# 1. Acquire approved ASSET dataset
python scripts/stage23/acquire_approved_datasets.py

# 2. Run master Stage 23 pipeline
python scripts/stage23/run_asset_pipeline.py

# 3. Execute verification test suite
Push-Location backend
python -m pytest tests/datasets/external_english/ -v
python -m pytest tests/nlp_preprocessing/ -q
python -m pytest tests/complexity_analysis/ -q
python -m pytest tests/ -q
Pop-Location
```
