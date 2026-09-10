from typing import List
from hypothesis import Hypothesis

class AuthorityGate:
    """
    Принимает решение COMMIT / REFUSE / FAIL.
    """
    @staticmethod
    def decide(possible_hypotheses: List[Hypothesis]) -> str:
        if len(possible_hypotheses) == 0:
            return "FAIL"
        elif len(possible_hypotheses) == 1:
            return "COMMIT"
        else:
            return "REFUSE"