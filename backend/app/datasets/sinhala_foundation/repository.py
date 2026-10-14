"""
Repository for Stage 29 Sinhala Foundation content persistence and verification.
"""
import sqlite3
from typing import List, Optional, Tuple
from pathlib import Path
from .schemas import LocalizedContentRecord

class SinhalaFoundationRepository:
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            from app.core.config import settings
            self.db_path = settings._DEFAULT_DB
        else:
            self.db_path = db_path
            
        self._shared_conn = None
        if self.db_path == ":memory:":
            self._shared_conn = sqlite3.connect(":memory:")
            self._shared_conn.row_factory = sqlite3.Row
            
        self._ensure_table_exists()

    def _get_connection(self) -> sqlite3.Connection:
        if self._shared_conn is not None:
            return self._shared_conn
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def close(self):
        if self._shared_conn is not None:
            self._shared_conn.close()
            self._shared_conn = None

    def _ensure_table_exists(self):
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS sinhala_foundation_records (
                    content_id TEXT PRIMARY KEY,
                    language TEXT NOT NULL,
                    locale TEXT NOT NULL,
                    text_role TEXT NOT NULL,
                    text_value TEXT NOT NULL,
                    source_type TEXT NOT NULL,
                    validation_status TEXT NOT NULL,
                    research_eligible INTEGER NOT NULL,
                    approved_for_child_delivery INTEGER NOT NULL,
                    requires_expert_review INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.commit()

    def save_record(self, record: LocalizedContentRecord) -> bool:
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT OR REPLACE INTO sinhala_foundation_records (
                    content_id, language, locale, text_role, text_value,
                    source_type, validation_status, research_eligible,
                    approved_for_child_delivery, requires_expert_review
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                record.content_id,
                record.language,
                record.locale,
                record.text_role,
                record.text_value,
                record.source_type,
                record.validation_status,
                1 if record.research_eligible else 0,
                1 if record.approved_for_child_delivery else 0,
                1 if record.requires_expert_review else 0
            ))
            conn.commit()
            return True

    def get_record(self, content_id: str) -> Optional[LocalizedContentRecord]:
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM sinhala_foundation_records WHERE content_id = ?;", (content_id,))
            row = cur.fetchone()
            if not row:
                return None
            return LocalizedContentRecord(
                content_id=row["content_id"],
                language=row["language"],
                locale=row["locale"],
                text_role=row["text_role"],
                text_value=row["text_value"],
                source_type=row["source_type"],
                validation_status=row["validation_status"],
                research_eligible=bool(row["research_eligible"]),
                approved_for_child_delivery=bool(row["approved_for_child_delivery"]),
                requires_expert_review=bool(row["requires_expert_review"])
            )

    def delete_record(self, content_id: str) -> bool:
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM sinhala_foundation_records WHERE content_id = ?;", (content_id,))
            conn.commit()
            return cur.rowcount > 0

    def list_records_by_language(self, language: str) -> List[LocalizedContentRecord]:
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM sinhala_foundation_records WHERE language = ? ORDER BY content_id;", (language,))
            rows = cur.fetchall()
            return [
                LocalizedContentRecord(
                    content_id=r["content_id"],
                    language=r["language"],
                    locale=r["locale"],
                    text_role=r["text_role"],
                    text_value=r["text_value"],
                    source_type=r["source_type"],
                    validation_status=r["validation_status"],
                    research_eligible=bool(r["research_eligible"]),
                    approved_for_child_delivery=bool(r["approved_for_child_delivery"]),
                    requires_expert_review=bool(r["requires_expert_review"])
                ) for r in rows
            ]
