import os

# Project root directory (3 levels up from backend/app/datasets/common)
DATASETS_COMMON_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(DATASETS_COMMON_DIR, "..", "..", "..", ".."))

DATA_DIR = os.path.join(PROJECT_ROOT, "data")

# 1. Adaptation Test Set paths
ADAPTATION_TEST_SET_DIR = os.path.join(DATA_DIR, "adaptation_test_set")
ADAPTATION_C1_SAMPLES_DIR = os.path.join(ADAPTATION_TEST_SET_DIR, "en", "component1_samples")
ADAPTATION_C2_AR_SAMPLES_DIR = os.path.join(ADAPTATION_TEST_SET_DIR, "en", "component2_ar_samples")
ADAPTATION_C3_LOCAL_SAMPLES_DIR = os.path.join(ADAPTATION_TEST_SET_DIR, "en", "component3_local_samples")
ADAPTATION_DRAFT_CONTRACTS_DIR = os.path.join(ADAPTATION_TEST_SET_DIR, "draft_contracts")
ADAPTATION_ID_MAPPINGS_DIR = os.path.join(ADAPTATION_TEST_SET_DIR, "id_mappings")
ADAPTATION_RELEASES_DIR = os.path.join(ADAPTATION_TEST_SET_DIR, "releases")

# 2. Simplification Corpus paths
SIMPLIFICATION_CORPUS_DIR = os.path.join(DATA_DIR, "simplification_corpus")
SIMPLIFICATION_DRAFT_DIR = os.path.join(SIMPLIFICATION_CORPUS_DIR, "en", "draft")
SIMPLIFICATION_REVIEW_DIR = os.path.join(SIMPLIFICATION_CORPUS_DIR, "en", "review_queue")
SIMPLIFICATION_APPROVED_DIR = os.path.join(SIMPLIFICATION_CORPUS_DIR, "en", "approved")
SIMPLIFICATION_ANNOTATIONS_DIR = os.path.join(SIMPLIFICATION_CORPUS_DIR, "annotations")
SIMPLIFICATION_ID_MAPPINGS_DIR = os.path.join(SIMPLIFICATION_CORPUS_DIR, "id_mappings")
SIMPLIFICATION_RELEASES_DIR = os.path.join(SIMPLIFICATION_CORPUS_DIR, "releases")

# 3. Interaction Dataset paths
INTERACTION_DATASET_DIR = os.path.join(DATA_DIR, "interaction_dataset")
INTERACTION_PRIVATE_DIR = os.path.join(INTERACTION_DATASET_DIR, "private")
INTERACTION_DEIDENTIFIED_DIR = os.path.join(INTERACTION_DATASET_DIR, "deidentified_exports")
INTERACTION_ID_MAPPINGS_DIR = os.path.join(INTERACTION_DATASET_DIR, "id_mappings")
INTERACTION_RESEARCH_RELEASES_DIR = os.path.join(INTERACTION_DATASET_DIR, "research_releases")

# 4. Lexicons
LEXICONS_EN_DIR = os.path.join(DATA_DIR, "lexicons", "en")

# 5. Legacy Paths
LEGACY_APPLICATION_TASKS = os.path.join(DATA_DIR, "application_tasks", "seed_tasks.json")
LEGACY_VOCABULARY = os.path.join(DATA_DIR, "vocabulary_dictionary", "seed_vocabulary.json")
LEGACY_GRAMMAR_CASES = os.path.join(DATA_DIR, "grammar_test_cases", "seed_grammar_cases.json")
