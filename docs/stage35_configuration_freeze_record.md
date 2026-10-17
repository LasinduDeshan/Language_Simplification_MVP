# Stage 35 Configuration Freeze Record

**Stage:** Stage 35 — Comparative Evaluation of Gemini, mT5, and mBART for Sinhala Simplification  
**Bundle Version:** 3.0.0  
**Master Configuration SHA-256:** `c440736e1de5f8960c133f8f8a800566e6809a22922b5bc0cf8deabbc67d2de8`  
**Governed Run Authorization ID:** `AUTH-S35-LOCKED-TEST-AUTHORIZED-RUN-001`  
**Prerequisite Anchor Commit:** `79c0f2619096869090615090b662e9ce9c8e2a7e`  
**Pre-Run Freeze Established:** `true`  
**Frozen Timestamp:** `2026-10-17T07:51:52.172067+00:00`  
**First Locked Request Timestamp:** `2026-10-17T08:03:24Z`  

---

## 1. Pre-Run Sealing Invariant
The master configuration freeze bundle was generated and cryptographically sealed at `2026-10-17T07:51:52.172067+00:00`, which strictly precedes the first locked-test execution timestamp of `2026-10-17T08:03:24Z`. No model parameters, prompt templates, decoding configurations, evaluator specifications, decision thresholds, or accounting rules were altered after the freeze timestamp.

---

## 2. Frozen Artifacts Inventory (20 Controlled Files)

| Role | Artifact Path | SHA-256 Digest |
|---|---|---|
| `PROMPT_TEMPLATE` | `data/model_comparison/stage35/registry/stage35_prompt_template.json` | `0000b7346093c8564dff0ef3eaca703986d1322ad4abbc7fc23ed03f68c15d84` |
| `DECODING_CONFIG` | `data/model_comparison/stage35/registry/stage35_decoding_config.json` | `39a606a2a1e257245e9cbade6fe2af6d3432653a6f7342f6b1c26f749fe0ffd7` |
| `SAFETY_SETTINGS` | `data/model_comparison/stage35/registry/stage35_safety_settings.json` | `a2352cceb1665bb1d37999c6e2286d0dd13df9f506eba4f600c089e6dab72cc5` |
| `EVALUATOR_MODEL_CONFIG` | `data/model_comparison/stage35/registry/stage35_evaluator_spec.json` | `0e24374b31591107544db8d5c9a397aa31e102f0bee562085f7521996bc7e56a` |
| `METRIC_SPECIFICATION` | `data/model_comparison/stage35/registry/stage35_metrics_and_gates_spec.json` | `68761344720a70bfe641be478c4d29b3dac9d0e5336dd4e33f0ce5e67179e595` |
| `ELIGIBILITY_AND_DECISION_THRESHOLDS` | `data/model_comparison/stage35/registry/stage35_eligibility_and_decision_thresholds.json` | `c89412291e95c2a60ecacb92fdb7aca4c6d1b541ab299f844ccba0fb659c4d0e` |
| `AUTHORIZATION_RECORD` | `data/model_comparison/stage35/registry/stage35_authorization_record.json` | `556e3c03fe4651dda30f1be6fd4b9397c80c76ec56ff871f80a965dd4402f4ad` |
| `VALIDATION_RUN_RECORD` | `data/model_comparison/stage35/registry/stage35_validation_run_record.json` | `8a63c16de39bf1a4c2797675515c2ea7c00d0809a0af6f7bb099670e412d3b28` |
| `RETRY_AND_FAILURE_POLICY` | `data/model_comparison/stage35/registry/stage35_retry_and_failure_policy.json` | `273ab31fd3820c887acf4e528ce96d5b45c4fe0505e1d02176de5b3a29161f41` |
| `SOFTWARE_DEPENDENCY_LOCK` | `data/model_comparison/stage35/registry/stage35_software_dependency_lock.json` | `d207abf513f3128a7abfad6f90b372ac50a619dd5246213503eb2d974522135b` |
| `CODE_COMMIT_RECORD` | `data/model_comparison/stage35/registry/stage35_code_commit_record.json` | `dc3dfa455f701500962eef258eab8a2c6d8336b367510e3d560703b4b150dc27` |
| `MODEL_REGISTRY` | `data/model_comparison/stage35/registry/stage35_model_registry.json` | `31fcf12b1da53de1b335268975645b8357ee57ec16adc3932f8eebec8efcb1bb` |
| `DENOMINATOR_MANIFEST` | `data/model_comparison/stage35/registry/stage35_locked_test_denominators.json` | `84d20c3f9e20e8e6e3906847809f0c97fb44ce97664a4a1d31b2ff4764a6a66b` |
| `OPERATIONAL_POLICY` | `data/model_comparison/stage35/registry/stage35_operational_policy.json` | `3a8afc95ef45d26dd734d442c16a6303cd02f6ada4a87bed6743f17349582c48` |
| `SCHEMAS` | `backend/app/model_comparison/stage35/schemas.py` | `a00ccd4054f1893abcca2466a856611b6b008d17071031f363a2d02140f3df48` |
| `STORAGE_MANAGER` | `backend/app/model_comparison/stage35/storage.py` | `f0aa23148594ae99358c237dc953d3ef5880c24425adecf227abbad7840cedd4` |
| `ADAPTERS` | `backend/app/model_comparison/stage35/adapters.py` | `5048d4269f1f0500f19572231b7745de727a4e651ca5e3351009bba3ef226c44` |
| `EVALUATOR_LOGIC` | `backend/app/model_comparison/stage35/evaluator.py` | `db5dcbea20ebe7f561d3f632e75d6553b2150b1f11fcc1ae7091b40a0fa5b8fe` |
| `RUNNER_LOGIC` | `backend/app/model_comparison/stage35/runner.py` | `efa8972f5987560653778ab18c7f5e7eb3cf1a47e1632e32d4407879b798330c` |
| `DATASET_BRIDGE` | `backend/app/model_comparison/stage35/dataset_bridge.py` | `fc1f45afd0b295dbf9e663e9bad831ae1c1788725f7af5eb1f4a7ae321e5ed51` |
