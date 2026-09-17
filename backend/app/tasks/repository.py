import json
import os
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.database.models import Task, LearnerProfile

BASE_DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "data"))

class TaskRepository:
    def __init__(self):
        self.vocabulary_cache = None

    def get_all_tasks(self, db: Session, active_only: bool = True) -> List[Task]:
        query = db.query(Task)
        if active_only:
            query = query.filter(Task.is_active == True)
        return query.all()

    def get_task_by_id(self, db: Session, task_id: str) -> Optional[Task]:
        return db.query(Task).filter((Task.id == task_id) | (Task.task_code == task_id)).first()

    def get_all_learners(self, db: Session) -> List[LearnerProfile]:
        return db.query(LearnerProfile).all()

    def get_learner_by_id(self, db: Session, learner_id: str) -> Optional[LearnerProfile]:
        return db.query(LearnerProfile).filter(
            (LearnerProfile.id == learner_id) | (LearnerProfile.learner_code == learner_id)
        ).first()

    def get_vocabulary_dictionary(self) -> List[Dict[str, Any]]:
        if self.vocabulary_cache is None:
            vocab_file = os.path.join(BASE_DATA_DIR, "vocabulary_dictionary", "seed_vocabulary.json")
            if os.path.exists(vocab_file):
                with open(vocab_file, "r", encoding="utf-8") as f:
                    self.vocabulary_cache = json.load(f)
            else:
                self.vocabulary_cache = []
        return self.vocabulary_cache

    def get_word_replacement(self, word: str, child_age: int) -> Optional[Dict[str, Any]]:
        vocab = self.get_vocabulary_dictionary()
        word_lower = word.lower()
        for entry in vocab:
            if entry["word"].lower() == word_lower:
                if child_age < entry["minimum_age"]:
                    return entry
        return None

task_repository = TaskRepository()
