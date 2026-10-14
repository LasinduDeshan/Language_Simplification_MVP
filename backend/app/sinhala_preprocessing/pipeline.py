"""
Master Pipeline module for Stage 30 Sinhala Preprocessing.
Executes deterministic, auditable, and fail-closed preprocessing flow:
  Raw capture -> Validation -> Normalization -> Script Analysis ->
  Sentence Segmentation -> Tokenization -> Features -> Quality Routing ->
  Audit Logging -> Governed Record Generation.
"""

import hashlib
from typing import List, Optional
from app.sinhala_preprocessing.schemas import (
    OperationRecord,
    QualityFlag,
    SentenceRecord,
    SinhalaPreprocessingRecord,
    TerminalDisposition,
    TokenRecord
)
from app.sinhala_preprocessing.config import get_frozen_configuration
from app.sinhala_preprocessing.validator import validate_unicode_text, REPLACEMENT_CHARACTER
from app.sinhala_preprocessing.normalizer import normalize_nfc, normalize_whitespace
from app.sinhala_preprocessing.graphemes import count_graphemes
from app.sinhala_preprocessing.script_analyzer import analyze_script_composition
from app.sinhala_preprocessing.sentence_segmenter import segment_sentences
from app.sinhala_preprocessing.tokenizer import tokenize_text
from app.sinhala_preprocessing.feature_builder import build_preprocessing_features
from app.sinhala_preprocessing.quality_router import resolve_terminal_disposition
from app.sinhala_preprocessing.audit import log_audit_event

def preprocess_sinhala_text(
    raw_text: str,
    record_id: str = "SI-PRE-000001",
    language: str = "si",
    locale: str = "si-LK",
    text_role: str = "prose"
) -> SinhalaPreprocessingRecord:
    config_data = get_frozen_configuration()
    cfg_version = config_data["configuration_version"]
    cfg_sha256 = config_data["configuration_sha256"]

    # 1. Capture raw representation and metrics
    raw_sha256 = hashlib.sha256(raw_text.encode("utf-8")).hexdigest()
    raw_bytes = len(raw_text.encode("utf-8"))
    raw_cps = len(raw_text)
    raw_graphemes = count_graphemes(raw_text)

    # 2. Validation
    val_res = validate_unicode_text(raw_text)
    all_flags: List[QualityFlag] = list(val_res.flags)
    operations: List[OperationRecord] = []
    sentences: List[SentenceRecord] = []
    tokens: List[TokenRecord] = []

    # Fast-fail for invalid Unicode (prohibited controls or pre-existing U+FFFD)
    if val_res.disposition == TerminalDisposition.REJECTED_INVALID_UNICODE:
        features = build_preprocessing_features(
            raw_text, raw_text, sentences, tokens, operations
        )
        record = SinhalaPreprocessingRecord(
            record_id=record_id,
            language=language,
            locale=locale,
            script="Sinh",
            text_role=text_role,
            raw_text=raw_text,
            raw_text_sha256=raw_sha256,
            raw_utf8_byte_count=raw_bytes,
            raw_code_point_count=raw_cps,
            raw_grapheme_count=raw_graphemes,
            normalized_text=raw_text,
            normalized_text_sha256=raw_sha256,
            normalized_utf8_byte_count=raw_bytes,
            normalized_code_point_count=raw_cps,
            normalized_grapheme_count=raw_graphemes,
            normalization_form="NFC",
            normalization_changed=False,
            operations=operations,
            sentences=sentences,
            tokens=tokens,
            features=features,
            quality_flags=all_flags,
            final_disposition=TerminalDisposition.REJECTED_INVALID_UNICODE,
            disposition_reason_code=val_res.reason_code,
            configuration_version=cfg_version,
            configuration_sha256=cfg_sha256
        )
        log_audit_event(
            record_id=record_id,
            raw_sha256=raw_sha256,
            normalized_sha256=raw_sha256,
            final_disposition=TerminalDisposition.REJECTED_INVALID_UNICODE.value,
            disposition_reason_code=val_res.reason_code,
            quality_flags=[f.value for f in all_flags],
            operation_count=0,
            sentence_count=0,
            token_count=0,
            grapheme_count=raw_graphemes
        )
        return record

    # 3. Normalization (NFC & Whitespace)
    nfc_text, nfc_ops = normalize_nfc(raw_text, rule_version=cfg_version)
    operations.extend(nfc_ops)
    if nfc_ops:
        if QualityFlag.NORMALIZATION_CHANGED not in all_flags:
            all_flags.append(QualityFlag.NORMALIZATION_CHANGED)

    ws_text, ws_ops = normalize_whitespace(nfc_text, text_role=text_role, rule_version=cfg_version)
    operations.extend(ws_ops)
    if ws_ops:
        if QualityFlag.NORMALIZATION_CHANGED not in all_flags:
            all_flags.append(QualityFlag.NORMALIZATION_CHANGED)

    normalized_text = ws_text
    norm_sha256 = hashlib.sha256(normalized_text.encode("utf-8")).hexdigest()
    norm_bytes = len(normalized_text.encode("utf-8"))
    norm_cps = len(normalized_text)
    norm_graphemes = count_graphemes(normalized_text)
    norm_changed = (normalized_text != raw_text)

    # Invariant: Zero replacement characters introduced by pipeline
    if REPLACEMENT_CHARACTER not in raw_text:
        assert REPLACEMENT_CHARACTER not in normalized_text, (
            "FATAL DEFECT: Replacement character U+FFFD was introduced by normalization pipeline!"
        )

    # 4. Script Composition Analysis
    script_res = analyze_script_composition(
        normalized_text,
        declared_language=language,
        declared_locale=locale
    )
    for f in script_res.flags:
        if f not in all_flags:
            all_flags.append(f)

    # 5. Sentence Segmentation
    sentences = segment_sentences(normalized_text)

    # 6. Tokenization
    token_counter = 0
    for s in sentences:
        s_tokens = tokenize_text(s.text, base_offset=s.start_code_point)
        for t in s_tokens:
            # Re-index tokens sequentially
            t.token_index = token_counter
            token_counter += 1
            tokens.append(t)

    # 7. Features
    features = build_preprocessing_features(
        raw_text=raw_text,
        normalized_text=normalized_text,
        sentences=sentences,
        tokens=tokens,
        operations=operations
    )

    # 8. Terminal Disposition Routing
    final_disp, reason = resolve_terminal_disposition(
        validator_disposition=val_res.disposition,
        validator_reason=val_res.reason_code,
        script_disposition=script_res.disposition,
        script_reason=script_res.reason_code,
        quality_flags=all_flags,
        operations=operations
    )

    # 9. Audit Logging (privacy-safe: hashes and counts only)
    log_audit_event(
        record_id=record_id,
        raw_sha256=raw_sha256,
        normalized_sha256=norm_sha256,
        final_disposition=final_disp.value,
        disposition_reason_code=reason,
        quality_flags=[f.value for f in all_flags],
        operation_count=len(operations),
        sentence_count=len(sentences),
        token_count=len(tokens),
        grapheme_count=norm_graphemes
    )

    # 10. Record Construction
    return SinhalaPreprocessingRecord(
        record_id=record_id,
        language=language,
        locale=locale,
        script="Sinh",
        text_role=text_role,
        raw_text=raw_text,
        raw_text_sha256=raw_sha256,
        raw_utf8_byte_count=raw_bytes,
        raw_code_point_count=raw_cps,
        raw_grapheme_count=raw_graphemes,
        normalized_text=normalized_text,
        normalized_text_sha256=norm_sha256,
        normalized_utf8_byte_count=norm_bytes,
        normalized_code_point_count=norm_cps,
        normalized_grapheme_count=norm_graphemes,
        normalization_form="NFC",
        normalization_changed=norm_changed,
        operations=operations,
        sentences=sentences,
        tokens=tokens,
        features=features,
        quality_flags=all_flags,
        final_disposition=final_disp,
        disposition_reason_code=reason,
        configuration_version=cfg_version,
        configuration_sha256=cfg_sha256
    )
