from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.database.models import Task, LearnerProfile
from app.datasets.adaptation_test_set.repository import AdaptationTestSetRepository
from app.datasets.common.draft_models import DraftAdaptationRecord

class LegacyTaskRepositoryAdapter:
    """
    Adapter ensuring backward compatibility with existing TaskRepository calls
    while delegating to AdaptationTestSetRepository and SQLite models.
    Supports instant rollback via configuration.
    """
    def __init__(self, adaptation_repo: Optional[AdaptationTestSetRepository] = None):
        self.adaptation_repo = adaptation_repo or AdaptationTestSetRepository()

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

    def get_adaptation_test_activities(self) -> List[DraftAdaptationRecord]:
        return self.adaptation_repo.get_all_activities()

    def get_child_activity(self, activity_id: str) -> Optional[Dict[str, Any]]:
        return self.adaptation_repo.get_child_activity(activity_id)

    def get_full_activity_record(self, activity_id: str) -> Optional[DraftAdaptationRecord]:
        return self.adaptation_repo.get_full_activity_record(activity_id)
