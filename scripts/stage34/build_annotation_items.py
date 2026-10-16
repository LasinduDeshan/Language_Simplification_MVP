"""
Stage 34 — Build Annotation Items and Generate Assignments Script (WP4)
Loads canonical corpus records, generates deterministic expertise-aware assignments,
and records data/sinhala_expert_validation/assignments/assignment_ledger.jsonl.
"""

import hashlib
import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from app.datasets.sinhala_expert_validation.assignment import generate_assignments
from app.datasets.sinhala_expert_validation.eligibility import ReviewerRegistry
from app.datasets.sinhala_expert_validation.enums import ExperienceBand, ReviewerRole, TrainingStatus
from app.datasets.sinhala_expert_validation.sampling import load_canonical_items
from app.datasets.sinhala_expert_validation.schemas import CompetencyDeclarations, ReviewerEligibility

ASSIGNMENT_DIR = PROJECT_ROOT / "data" / "sinhala_expert_validation" / "assignments"
ASSIGNMENT_FILE = ASSIGNMENT_DIR / "assignment_ledger.jsonl"
CONFIG_FILE = PROJECT_ROOT / "data" / "sinhala_expert_validation" / "registry" / "stage34_configuration.json"


def compute_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def setup_panel() -> ReviewerRegistry:
    registry = ReviewerRegistry()

    reviewers = [
        ReviewerEligibility(
            reviewer_id="REV-S34-001",
            roles=[ReviewerRole.SINHALA_LINGUIST],
            qualification_evidence_ref="protected://stage34/reviewers/REV-S34-001/evidence.json",
            years_relevant_experience_band=ExperienceBand.FIVE_TO_9,
            native_or_professional_sinhala_proficiency=True,
            ages_4_to_8_experience=False,
            competency_declarations=CompetencyDeclarations(
                meaning_preservation=True,
                grammatical_acceptability=True,
                morphology_preservation=True,
                fluency_naturalness=True,
                simplicity_improvement=True,
                vocabulary_suitability=True,
                sentence_structure_suitability=True,
                developmental_suitability=False,
            ),
            conflict_declaration_completed=True,
            consent_version="S34-CONSENT-V1",
            consent_version_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            training_status=TrainingStatus.QUALIFIED,
        ),
        ReviewerEligibility(
            reviewer_id="REV-S34-002",
            roles=[ReviewerRole.SINHALA_LINGUIST],
            qualification_evidence_ref="protected://stage34/reviewers/REV-S34-002/evidence.json",
            years_relevant_experience_band=ExperienceBand.TEN_PLUS,
            native_or_professional_sinhala_proficiency=True,
            ages_4_to_8_experience=False,
            competency_declarations=CompetencyDeclarations(
                meaning_preservation=True,
                grammatical_acceptability=True,
                morphology_preservation=True,
                fluency_naturalness=True,
                simplicity_improvement=True,
                vocabulary_suitability=True,
                sentence_structure_suitability=True,
                developmental_suitability=False,
            ),
            conflict_declaration_completed=True,
            consent_version="S34-CONSENT-V1",
            consent_version_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            training_status=TrainingStatus.QUALIFIED,
        ),
        ReviewerEligibility(
            reviewer_id="REV-S34-003",
            roles=[ReviewerRole.EARLY_CHILDHOOD_EDUCATOR],
            qualification_evidence_ref="protected://stage34/reviewers/REV-S34-003/evidence.json",
            years_relevant_experience_band=ExperienceBand.FIVE_TO_9,
            native_or_professional_sinhala_proficiency=True,
            ages_4_to_8_experience=True,
            competency_declarations=CompetencyDeclarations(
                meaning_preservation=True,
                grammatical_acceptability=True,
                morphology_preservation=False,
                fluency_naturalness=True,
                simplicity_improvement=True,
                vocabulary_suitability=True,
                sentence_structure_suitability=True,
                developmental_suitability=True,
            ),
            conflict_declaration_completed=True,
            consent_version="S34-CONSENT-V1",
            consent_version_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            training_status=TrainingStatus.QUALIFIED,
        ),
        ReviewerEligibility(
            reviewer_id="REV-S34-004",
            roles=[ReviewerRole.EARLY_CHILDHOOD_EDUCATOR],
            qualification_evidence_ref="protected://stage34/reviewers/REV-S34-004/evidence.json",
            years_relevant_experience_band=ExperienceBand.TEN_PLUS,
            native_or_professional_sinhala_proficiency=True,
            ages_4_to_8_experience=True,
            competency_declarations=CompetencyDeclarations(
                meaning_preservation=True,
                grammatical_acceptability=True,
                morphology_preservation=False,
                fluency_naturalness=True,
                simplicity_improvement=True,
                vocabulary_suitability=True,
                sentence_structure_suitability=True,
                developmental_suitability=True,
            ),
            conflict_declaration_completed=True,
            consent_version="S34-CONSENT-V1",
            consent_version_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            training_status=TrainingStatus.QUALIFIED,
        ),
        ReviewerEligibility(
            reviewer_id="REV-S34-005",
            roles=[ReviewerRole.CHILD_DEVELOPMENT_SPECIALIST],
            qualification_evidence_ref="protected://stage34/reviewers/REV-S34-005/evidence.json",
            years_relevant_experience_band=ExperienceBand.FIVE_TO_9,
            native_or_professional_sinhala_proficiency=True,
            ages_4_to_8_experience=True,
            competency_declarations=CompetencyDeclarations(
                meaning_preservation=True,
                grammatical_acceptability=False,
                morphology_preservation=False,
                fluency_naturalness=True,
                simplicity_improvement=True,
                vocabulary_suitability=True,
                sentence_structure_suitability=True,
                developmental_suitability=True,
            ),
            conflict_declaration_completed=True,
            consent_version="S34-CONSENT-V1",
            consent_version_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            training_status=TrainingStatus.QUALIFIED,
        ),
        ReviewerEligibility(
            reviewer_id="REV-S34-006",
            roles=[ReviewerRole.INDEPENDENT_ADJUDICATOR],
            qualification_evidence_ref="protected://stage34/reviewers/REV-S34-006/evidence.json",
            years_relevant_experience_band=ExperienceBand.TEN_PLUS,
            native_or_professional_sinhala_proficiency=True,
            ages_4_to_8_experience=True,
            competency_declarations=CompetencyDeclarations(
                meaning_preservation=True,
                grammatical_acceptability=True,
                morphology_preservation=True,
                fluency_naturalness=True,
                simplicity_improvement=True,
                vocabulary_suitability=True,
                sentence_structure_suitability=True,
                developmental_suitability=True,
            ),
            conflict_declaration_completed=True,
            consent_version="S34-CONSENT-V1",
            consent_version_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            training_status=TrainingStatus.QUALIFIED,
        ),
        ReviewerEligibility(
            reviewer_id="REV-S34-TEAM1",
            roles=[ReviewerRole.SINHALA_LINGUIST],
            qualification_evidence_ref="protected://stage34/reviewers/REV-S34-TEAM1/evidence.json",
            years_relevant_experience_band=ExperienceBand.THREE_TO_4,
            native_or_professional_sinhala_proficiency=True,
            ages_4_to_8_experience=False,
            competency_declarations=CompetencyDeclarations(
                meaning_preservation=True,
                grammatical_acceptability=True,
                morphology_preservation=True,
                fluency_naturalness=True,
                simplicity_improvement=True,
                vocabulary_suitability=False,
                sentence_structure_suitability=False,
                developmental_suitability=False,
            ),
            conflict_declaration_completed=True,
            consent_version="S34-CONSENT-V1",
            consent_version_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            training_status=TrainingStatus.EXCLUDED,
            is_project_team_member=True,
        ),
    ]

    for rev in reviewers:
        registry.register_reviewer(rev)

    return registry


def build_and_assign():
    ASSIGNMENT_DIR.mkdir(parents=True, exist_ok=True)

    items = load_canonical_items()
    assert len(items) == 150, f"Expected 150 items, got {len(items)}"

    registry = setup_panel()
    panel_check = registry.verify_panel_composition()
    assert panel_check["is_valid"], f"Panel check failed: {panel_check}"

    qualified = registry.to_sanitized_records()
    assignments = generate_assignments(items, qualified, seed=1034)

    with open(ASSIGNMENT_FILE, "w", encoding="utf-8") as f:
        for asn in assignments:
            f.write(json.dumps(asn, ensure_ascii=False) + "\n")

    asn_hash = compute_sha256(ASSIGNMENT_FILE)

    # Update stage34 configuration with assignment ledger hash
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        config = json.load(f)

    if "frozen_hashes" not in config:
        config["frozen_hashes"] = {}
    config["frozen_hashes"]["assignment_ledger_hash"] = asn_hash
    config["total_items"] = len(items)
    config["total_assignments"] = len(assignments)

    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

    print(f"Generated {len(assignments)} assignments across {len(items)} items.")
    print(f"Assignment ledger: {ASSIGNMENT_FILE}")
    print(f"Assignment ledger hash: {asn_hash}")


if __name__ == "__main__":
    build_and_assign()
