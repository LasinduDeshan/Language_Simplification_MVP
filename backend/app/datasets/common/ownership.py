"""
Standard component ownership constants for Stage 13 data governance.
"""

OWNER_COMPONENT_1 = "component_1"
OWNER_COMPONENT_2_AR = "component_2_ar"
OWNER_COMPONENT_3 = "component_3"
OWNER_COMPONENT_4 = "component_4"

VALID_DATA_OWNERS = [
    OWNER_COMPONENT_1,
    OWNER_COMPONENT_2_AR,
    OWNER_COMPONENT_3,
    OWNER_COMPONENT_4
]

POLICY_NONE = "none"
POLICY_PRESENTATION_ONLY = "presentation_only"
POLICY_INSTRUCTION_ONLY = "instruction_only"
POLICY_CONTROLLED = "controlled"

VALID_ADAPTATION_POLICIES = [
    POLICY_NONE,
    POLICY_PRESENTATION_ONLY,
    POLICY_INSTRUCTION_ONLY,
    POLICY_CONTROLLED
]

DATASET_OWNERSHIP_MATRIX = {
    "adaptation_test_set": {
        "canonical_owner": "Component 3",
        "role": "Local test set for simplification/adaptation evaluation",
        "privacy": "internal_test"
    },
    "simplification_corpus": {
        "canonical_owner": "Component 3",
        "role": "Original to child-friendly simplified text pairs",
        "privacy": "team_governed"
    },
    "interaction_dataset": {
        "canonical_owner": "Component 3 (Operational) / Component 4 (Longitudinal Analytics)",
        "role": "Private learner session interactions and attempt evidence",
        "privacy": "private_learner_evidence"
    },
    "production_activity_bank": {
        "canonical_owner": "Component 2 (AR) / Curriculum Authoring",
        "role": "Production interactive activity catalog",
        "privacy": "upstream_authoring"
    },
    "screening_risk_profile": {
        "canonical_owner": "Component 1",
        "role": "DLD screening risk indicator snapshot (read-only)",
        "privacy": "read_only_screening"
    }
}

def is_component3_owner(layer_name: str) -> bool:
    """Returns True if Component 3 is the canonical owner of the data layer."""
    info = DATASET_OWNERSHIP_MATRIX.get(layer_name)
    if not info:
        return False
    return "Component 3" in info.get("canonical_owner", "")

def get_layer_owner(layer_name: str) -> str:
    """Returns the canonical owner string for a data layer."""
    info = DATASET_OWNERSHIP_MATRIX.get(layer_name)
    if not info:
        return "Unknown"
    return info.get("canonical_owner", "Unknown")
