"""
Stage 33 — Unit Tests for Pipeline Determinism.
Verifies that multiple runs on identical input produce 100% byte-identical records.
"""

import pytest
from app.sinhala_simplification.enums import CorpusView, Partition
from app.sinhala_simplification.pipeline import SimplificationPipeline
from app.sinhala_simplification.schemas import RewriteRequest, RightsProfileBinding


def test_pipeline_determinism_identical_runs():
    pipeline1 = SimplificationPipeline()
    pipeline2 = SimplificationPipeline()

    pipeline1.initialize()
    pipeline2.initialize()

    request = RewriteRequest(
        request_id="REQ-DET-001",
        record_id="REC-DET-001",
        source_storage_ref="protected://test/REC-DET-001.txt",
        source_sha256_internal="1" * 64,
        language="si",
        stage30_configuration_hash="2" * 64,
        stage31_split_manifest_hash="3" * 64,
        stage31_corpus_view=CorpusView.CANONICAL_ANALYTICAL_150,
        stage32_configuration_hash="4" * 64,
        stage32_lexicon_manifest_hash="5" * 64,
        stage33_configuration_hash="6" * 64,
        rights_profile_ids_and_versions=[RightsProfileBinding(rights_profile_id="SRC-SI-001-RP-01", version=1)],
        partition=Partition.TRAIN
    )

    text = "මෙම පරිසරය පිළිබඳව අපි සාකච්ඡා කරමු."

    out1, att1, cand1, ops1 = pipeline1.process_request(request, text)
    out2, att2, cand2, ops2 = pipeline2.process_request(request, text)

    assert out1.output_sha256_internal == out2.output_sha256_internal
    assert out1.final_disposition == out2.final_disposition
    assert len(att1) == len(att2)
    assert len(cand1) == len(cand2)
    assert len(ops1) == len(ops2)
