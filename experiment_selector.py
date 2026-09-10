from typing import Optional, List

class ExperimentSelector:
    """
    Выбирает следующее действие для увеличения различимости.
    """
    def __init__(self, possible_actions: List[str]):
        self.possible_actions = possible_actions
        self.action_index = 0

    def select_action(self, remaining_hypotheses: List) -> Optional[str]:
        if len(remaining_hypotheses) <= 1:
            return None
        action = self.possible_actions[self.action_index % len(self.possible_actions)]
        self.action_index += 1
        return action