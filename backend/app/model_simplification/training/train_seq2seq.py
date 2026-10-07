"""
Stage 26 Seq2Seq Pilot Fine-Tuning Runner.
Enforces the Formal Fine-Tuning Decision Gate before running any training job.
Trains candidate seq2seq model on the 210 clean internal training pairs.
"""
import os
import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

repo_root = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.insert(0, str(repo_root / "backend"))

from app.model_simplification.training.dataset_builder import Seq2SeqDatasetBuilder


DECISION_RECORD_PATH = repo_root / "docs" / "stage26_training_decision_record.md"


def check_fine_tuning_decision_gate() -> Tuple[bool, str]:
    """
    Checks if formal fine-tuning decision is approved in the decision record.
    """
    if not DECISION_RECORD_PATH.exists():
        return False, "Decision record docs/stage26_training_decision_record.md does not exist."

    content = DECISION_RECORD_PATH.read_text(encoding="utf-8")
    if "APPROVED_FOR_PILOT_FINE_TUNING" in content:
        return True, "Approved for pilot fine-tuning"
    elif "NOT_APPROVED" in content or "NOT_REQUIRED" in content:
        return False, f"Formal fine-tuning gate is closed: {content[:100]}..."
    return False, "Unclear decision status in record."


def run_training_pipeline(
    model_name: str = "google/mt5-small",
    output_dir: Optional[Path] = None,
    num_epochs: int = 3,
    batch_size: int = 4,
    learning_rate: float = 5e-5,
) -> Dict[str, Any]:
    is_approved, reason = check_fine_tuning_decision_gate()
    if not is_approved:
        return {
            "status": "gate_blocked",
            "decision": reason,
            "trained_checkpoint": None,
        }

    out_dir = output_dir or (repo_root / "data" / "model_simplification" / "checkpoints" / "mt5_pilot_v1")
    out_dir.mkdir(parents=True, exist_ok=True)

    builder = Seq2SeqDatasetBuilder(repo_root=repo_root)
    samples = builder.build_dataset()

    try:
        import torch
        from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, Seq2SeqTrainer, Seq2SeqTrainingArguments

        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

        # Tokenize dataset
        def preprocess(data):
            inputs = [d["input_text"] for d in data]
            targets = [d["target_text"] for d in data]
            model_inputs = tokenizer(inputs, max_length=128, truncation=True, padding="max_length")
            labels = tokenizer(targets, max_length=128, truncation=True, padding="max_length")
            labels_ids = labels["input_ids"]
            # Replace padding with -100
            labels_ids = [[(l if l != tokenizer.pad_token_id else -100) for l in label] for label in labels_ids]
            model_inputs["labels"] = labels_ids
            return model_inputs

        # Simple PyTorch Dataset
        class SimpleSeq2SeqDataset(torch.utils.data.Dataset):
            def __init__(self, encodings):
                self.encodings = encodings
            def __len__(self):
                return len(self.encodings["input_ids"])
            def __getitem__(self, idx):
                return {k: torch.tensor(v[idx]) for k, v in self.encodings.items()}

        encodings = preprocess(samples)
        train_dataset = SimpleSeq2SeqDataset(encodings)

        training_args = Seq2SeqTrainingArguments(
            output_dir=str(out_dir),
            per_device_train_batch_size=batch_size,
            num_train_epochs=num_epochs,
            learning_rate=learning_rate,
            logging_steps=10,
            save_strategy="no",
            report_to="none",
        )

        trainer = Seq2SeqTrainer(
            model=model,
            args=training_args,
            train_dataset=train_dataset,
            tokenizer=tokenizer,
        )

        train_result = trainer.train()
        model.save_pretrained(str(out_dir))
        tokenizer.save_pretrained(str(out_dir))

        return {
            "status": "completed",
            "model_name": model_name,
            "train_samples": len(samples),
            "output_dir": str(out_dir),
            "loss": train_result.training_loss,
        }
    except Exception as e:
        # If transformers/torch is missing or fails on CPU, record graceful fallback
        return {
            "status": "training_unavailable",
            "reason": str(e),
            "model_name": model_name,
            "train_samples": len(samples),
            "output_dir": str(out_dir),
        }
