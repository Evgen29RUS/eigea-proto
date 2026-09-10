from typing import List, Dict
from hypothesis import Hypothesis
from dependency_graph import DependencyGraph

class DistinguishabilityAnalyzer:
    """
    Определяет, какие гипотезы согласуются с наблюдением,
    учитывая возможные отказы в общих компонентах.
    """
    def __init__(self, hypotheses: List[Hypothesis], graph: DependencyGraph):
        self.hypotheses = hypotheses
        self.graph = graph

    def possible_hypotheses(self, action: str, observation: Dict[str, str]) -> List[Hypothesis]:
        possible = []
        for h in self.hypotheses:
            expected = h.expected_for(action)
            if self._is_explainable(expected, observation):
                possible.append(h)
        return possible

    def _is_explainable(self, expected: Dict[str, str], observed: Dict[str, str]) -> bool:
        """
        Объясняет расхождение между expected и observed через отказ одного или нескольких
        общих компонентов. Если все несовпадающие сенсоры имеют хотя бы один общий компонент,
        то расхождение объяснимо. Если нет общего компонента – гипотеза отбрасывается.
        """
        mismatched = []
        for sensor, exp_val in expected.items():
            obs_val = observed.get(sensor)
            if obs_val is None:
                continue
            if exp_val != obs_val:
                mismatched.append(sensor)

        if not mismatched:
            return True

        # Находим пересечение компонентов для всех несовпадающих сенсоров
        common_components = None
        for sensor in mismatched:
            comps = set(self.graph.sensor_components.get(sensor, []))
            if common_components is None:
                common_components = comps
            else:
                common_components = common_components.intersection(comps)
            if not common_components:
                return False
        return True