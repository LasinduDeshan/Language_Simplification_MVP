"""CLI script to run quality validation across governed dataset layers."""
import os
import sys
import argparse
import asyncio

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "backend")))

from app.database.db import SessionLocal, Base, engine
from app.datasets.quality.orchestrator import QualityOrchestrator
from app.datasets.quality.schemas import ValidationRunCreateRequestV1


async def main():
    parser = argparse.ArgumentParser(description="Run Stage 15 Quality Validation on Governed Datasets")
    parser.add_argument("--layer", default="all", choices=["all", "adaptation_test_set", "simplification_corpus", "lexicons", "interaction_exports"])
    parser.add_argument("--no-nlp", action="store_true", help="Disable NLP-assisted linguistic rules")
    parser.add_argument("--enable-llm", action="store_true", help="Enable optional LLM advisory evaluation")
    args = parser.parse_args()

    # Ensure tables exist
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        orchestrator = QualityOrchestrator(db=db, base_path=repo_root)

        req = ValidationRunCreateRequestV1(
            dataset_layer=args.layer,
            dataset_version="0.1.0",
            quality_rule_set_version="1.0.0",
            enable_nlp=not args.no_nlp,
            enable_llm_review=args.enable_llm
        )

        run = orchestrator.create_run(req, created_by="cli_runner")
        print(f"[*] Starting Validation Run '{run.run_id}' for layer '{run.dataset_layer}'...")
        
        completed_run = await orchestrator.execute_validation_run(
            run_id=run.run_id,
            enable_nlp=not args.no_nlp,
            enable_llm_review=args.enable_llm
        )

        print("\n==================================================================")
        print("STAGE 15 QUALITY VALIDATION EXECUTION SUMMARY")
        print("==================================================================")
        print(f"Run ID:                  {completed_run.run_id}")
        print(f"Status:                  {completed_run.status}")
        print(f"Total Records:           {completed_run.total_records}")
        print(f"Passed:                  {completed_run.passed_count}")
        print(f"Failed:                  {completed_run.failed_count}")
        print(f"Manual Review Required:  {completed_run.review_required_count}")
        print(f"Quarantined:             {completed_run.quarantined_count}")
        print("==================================================================")

    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(main())
