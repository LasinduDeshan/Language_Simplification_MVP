"""
Stage 26 Gemini Quota and Throttling Manager.
Enforces Google Gemini free-tier RPM and daily quota constraints, provides intelligent backoff,
distinguishes transient rate limits from daily exhaustion, and supports resumable execution ledgers.
"""
import os
import json
import time
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple, Set


class GeminiQuotaManager:
    """
    Manages API call rate, daily usage tracking, backoff, and execution persistence.
    """
    MAX_REQUESTS_PER_MINUTE: int = 12
    MIN_DELAY_SECONDS: float = 5.0
    MAX_REQUESTS_PER_DAY: int = 500
    DAILY_SAFETY_RESERVE: int = 20
    USABLE_DAILY_REQUESTS: int = 480

    def __init__(
        self,
        ledger_path: Optional[Path] = None,
        min_delay_seconds: float = 5.0,
        max_daily_requests: int = 480,
    ):
        self.ledger_path = Path(ledger_path) if ledger_path else None
        self.min_delay_seconds = min_delay_seconds
        self.max_daily_requests = max_daily_requests
        self.last_request_timestamp: float = 0.0
        self.request_timestamps: List[float] = []
        self.daily_request_count: int = 0
        self.current_day_str: str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        self.ledger: Dict[str, Dict[str, Any]] = {}

        if self.ledger_path and self.ledger_path.exists():
            self._load_ledger()

    def _load_ledger(self) -> None:
        try:
            with open(self.ledger_path, "r", encoding="utf-8") as f:
                records = json.load(f)
                if isinstance(records, list):
                    for r in records:
                        key = self._get_record_key(r.get("source_group_id", ""), r.get("support_level", ""))
                        self.ledger[key] = r
                elif isinstance(records, dict):
                    self.ledger = records
        except Exception:
            self.ledger = {}

    @staticmethod
    def _get_record_key(source_group_id: str, support_level: str) -> str:
        return f"{source_group_id}::{support_level.lower()}"

    def can_proceed(self) -> Tuple[bool, str]:
        """
        Verifies if daily quota allows dispatching another request.
        """
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        if today != self.current_day_str:
            self.current_day_str = today
            self.daily_request_count = 0

        if self.daily_request_count >= self.max_daily_requests:
            return False, f"Daily quota limit reached: {self.daily_request_count}/{self.max_daily_requests} (Safety reserve preserved: {self.DAILY_SAFETY_RESERVE})"
        return True, "OK"

    def wait_for_slot(self) -> float:
        """
        Sleeps if necessary to strictly enforce RPM limit (12 RPM) and minimum delay (5.0s).
        Returns the duration slept in seconds.
        """
        now = time.perf_counter()
        duration_slept = 0.0

        # 1. Enforce minimum delay between calls
        elapsed_since_last = now - self.last_request_timestamp
        if self.last_request_timestamp > 0 and elapsed_since_last < self.min_delay_seconds:
            sleep_needed = self.min_delay_seconds - elapsed_since_last
            time.sleep(sleep_needed)
            duration_slept += sleep_needed

        # 2. Enforce 12 RPM window
        now = time.perf_counter()
        cutoff = now - 60.0
        self.request_timestamps = [t for t in self.request_timestamps if t > cutoff]

        if len(self.request_timestamps) >= self.MAX_REQUESTS_PER_MINUTE:
            oldest = self.request_timestamps[0]
            sleep_needed = 60.0 - (now - oldest) + 0.1
            if sleep_needed > 0:
                time.sleep(sleep_needed)
                duration_slept += sleep_needed

        self.last_request_timestamp = time.perf_counter()
        self.request_timestamps.append(self.last_request_timestamp)
        self.daily_request_count += 1
        return duration_slept

    @staticmethod
    def classify_error(status_code: int, response_text: str = "") -> str:
        """
        Distinguishes rate limit (transient 429 / RPM) from daily quota exhaustion (ResourceExhausted / PerDay).
        """
        text_lower = response_text.lower()
        if status_code == 429:
            if "perday" in text_lower or "daily" in text_lower or "free_tier_usage_limit" in text_lower or "quota_exceeded" in text_lower:
                return "DAILY_QUOTA_FAILED"
            return "RATE_LIMIT_FAILED"
        elif status_code in (403, 400):
            if "quota" in text_lower or "resource_exhausted" in text_lower:
                return "DAILY_QUOTA_FAILED"
            return "OTHER_FAILED"
        return "OTHER_FAILED"

    @staticmethod
    def calculate_hash(content: str) -> str:
        """
        Generates SHA-256 hash of content.
        """
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def record_completed(
        self,
        request_id: str,
        run_id: str,
        dataset_split: str,
        source_group_id: str,
        support_level: str,
        http_status: int,
        execution_status: str,
        native_output_received: bool,
        fallback_used: bool,
        resolved_model: str,
        latency_ms: float,
        configuration_hash: str,
        output_text: str,
        error_message: Optional[str] = None,
        finish_reason: Optional[str] = None,
        attempt_count: int = 1,
        token_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Persists a single request result into ledger.
        """
        output_hash = self.calculate_hash(output_text) if output_text else ""
        record = {
            "request_id": request_id,
            "run_id": run_id,
            "dataset_split": dataset_split,
            "source_group_id": source_group_id,
            "support_level": support_level.lower(),
            "http_status": http_status,
            "execution_status": execution_status,
            "native_output_received": native_output_received,
            "fallback_used": fallback_used,
            "resolved_model": resolved_model,
            "latency_ms": round(latency_ms, 2),
            "configuration_hash": configuration_hash,
            "output_hash": output_hash,
            "output_text": output_text,
            "error_message": error_message,
            "finish_reason": finish_reason or ("STOP" if native_output_received else None),
            "attempt_count": attempt_count,
            "token_metadata": token_metadata or {},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        key = self._get_record_key(source_group_id, support_level)
        self.ledger[key] = record

        if self.ledger_path:
            self._save_ledger()

        return record

    def _save_ledger(self) -> None:
        if not self.ledger_path:
            return
        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.ledger_path, "w", encoding="utf-8") as f:
            json.dump(list(self.ledger.values()), f, indent=2)

    def is_already_completed(self, source_group_id: str, support_level: str) -> bool:
        """
        Checks if item was already successfully completed in ledger.
        """
        key = self._get_record_key(source_group_id, support_level)
        record = self.ledger.get(key)
        if not record:
            return False
        # Only completed live successes are skipped
        return record.get("execution_status") in ("LIVE_SUCCESS", "live_provider_inference") and record.get("native_output_received", False)

    def get_completed_record(self, source_group_id: str, support_level: str) -> Optional[Dict[str, Any]]:
        key = self._get_record_key(source_group_id, support_level)
        return self.ledger.get(key)

    def get_summary_counts(self) -> Dict[str, int]:
        counts = {
            "LIVE_SUCCESS": 0,
            "RATE_LIMIT_FAILED": 0,
            "DAILY_QUOTA_FAILED": 0,
            "FALLBACK_GENERATED": 0,
            "OTHER_FAILED": 0,
            "NOT_ATTEMPTED": 0,
        }
        for r in self.ledger.values():
            st = r.get("execution_status", "")
            if st in counts:
                counts[st] += 1
            elif st == "live_provider_inference" and r.get("native_output_received"):
                counts["LIVE_SUCCESS"] += 1
            elif r.get("fallback_used"):
                counts["FALLBACK_GENERATED"] += 1
            else:
                counts["OTHER_FAILED"] += 1
        return counts
