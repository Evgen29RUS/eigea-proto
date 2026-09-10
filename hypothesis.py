from typing import Dict, List

class Hypothesis:
    """
    Гипотеза о состоянии мира.
    expected_obs: {action: {sensor: value}}
    """
    def __init__(self, id: str, description: str, expected_obs: Dict[str, Dict[str, str]]):
        self.id = id
        self.description = description
        self.expected_obs = expected_obs

    def expected_for(self, action: str) -> Dict[str, str]:
        return self.expected_obs.get(action, {})

    def __repr__(self):
        return f"Hypothesis({self.id}, {self.description})"