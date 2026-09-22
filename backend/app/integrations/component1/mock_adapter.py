import os
import json
from typing import List, Optional
from app.integrations.component1.interface import Component1Interface
from app.integrations.component1.schemas import Component1ScreeningInputSchema
from app.integrations.common.errors import InvalidMockFixtureError

class Component1MockAdapter(Component1Interface):
    """
    Mock adapter reading simulated screening fixtures from data/integration_fixtures/component1_inputs/
    """
    def __init__(self, fixtures_dir: Optional[str] = None):
        if fixtures_dir is None:
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
            fixtures_dir = os.path.join(base_dir, "data", "integration_fixtures", "component1_inputs")
        self.fixtures_dir = fixtures_dir

    def _load_fixtures(self) -> List[Component1ScreeningInputSchema]:
        profiles = []
        if not os.path.exists(self.fixtures_dir):
            return profiles

        for filename in os.listdir(self.fixtures_dir):
            if filename.endswith(".json"):
                filepath = os.path.join(self.fixtures_dir, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        profile = Component1ScreeningInputSchema(**data)
                        if not profile.is_simulated:
                            raise InvalidMockFixtureError(
                                f"Mock Component 1 profile in {filename} must have is_simulated: true."
                            )
                        # Ensure research_eligible is False for simulated mock data
                        profile.research_eligible = False
                        profiles.append(profile)
                except Exception as e:
                    if isinstance(e, InvalidMockFixtureError):
                        raise
                    continue
        return profiles

    def get_screening_profile(self, learner_id: str) -> Optional[Component1ScreeningInputSchema]:
        profiles = self._load_fixtures()
        for p in profiles:
            if p.learner_id.upper() == learner_id.upper():
                return p
        return None

    def list_screening_profiles(self) -> List[Component1ScreeningInputSchema]:
        return self._load_fixtures()
