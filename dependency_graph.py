from typing import Dict, List, Set

class DependencyGraph:
    """
    Граф зависимостей сенсоров от общих компонентов.
    sensor_components: {sensor: [component1, component2, ...]}
    """
    def __init__(self, sensor_components: Dict[str, List[str]]):
        self.sensor_components = sensor_components

    def shared_components(self, sensor1: str, sensor2: str) -> List[str]:
        c1 = set(self.sensor_components.get(sensor1, []))
        c2 = set(self.sensor_components.get(sensor2, []))
        return list(c1 & c2)

    def get_all_components(self) -> Set[str]:
        return set().union(*self.sensor_components.values())

    def sensors_for_component(self, component: str) -> List[str]:
        return [s for s, comps in self.sensor_components.items() if component in comps]

    def partition_by_component(self) -> Dict[str, List[str]]:
        """
        Группирует сенсоры по первому общему компоненту (упрощение).
        """
        groups = {}
        for sensor, comps in self.sensor_components.items():
            if comps:
                key = comps[0]
                groups.setdefault(key, []).append(sensor)
        return groups