from hypothesis import Hypothesis
from dependency_graph import DependencyGraph
from distinguishability import DistinguishabilityAnalyzer
from experiment_selector import ExperimentSelector
from authority_gate import AuthorityGate

def run_scenario(name, action_sequence, observations_sequence, hypotheses, graph):
    print(f"\n=== {name} ===")
    analyzer = DistinguishabilityAnalyzer(hypotheses, graph)
    gate = AuthorityGate()
    selector = ExperimentSelector(action_sequence)

    for i, (action, obs) in enumerate(zip(action_sequence, observations_sequence)):
        print(f"\nStep {i+1}: action = {action}")
        print(f"Observation: {obs}")

        possible = analyzer.possible_hypotheses(action, obs)
        print(f"Possible hypotheses: {[h.id for h in possible]}")

        decision = gate.decide(possible)
        print(f"Decision: {decision}")

        if decision == "COMMIT":
            print("✅ COMMIT granted.")
            return True
        elif decision == "FAIL":
            print("❌ FAIL: no hypothesis fits.")
            return False
        # REFUSE – продолжаем с следующим действием (но в симуляции последовательность уже задана)

    print("No COMMIT reached.")
    return False


def main():
    # Гипотезы:
    # H0: лампа выключена (изначально OFF)
    # H1: лампа включена (изначально ON)
    # Мы моделируем, что после действия toggle состояние меняется.
    # ВАЖНО: в реальном агенте мы не знаем истинного состояния, поэтому гипотезы отражают разные миры.
    H0 = Hypothesis(
        id="H0",
        description="Lamp is OFF (initially off, toggles to ON)",
        expected_obs={
            "turn_off": {"camera": "OFF", "photodiode": "OFF", "current": "OFF"},
            "turn_on":  {"camera": "ON",  "photodiode": "ON",  "current": "ON"},
            "toggle":   {"camera": "ON",  "photodiode": "ON",  "current": "ON"}  # из OFF -> ON
        }
    )
    H1 = Hypothesis(
        id="H1",
        description="Lamp is ON (initially on, toggles to OFF)",
        expected_obs={
            "turn_off": {"camera": "OFF", "photodiode": "OFF", "current": "OFF"},
            "turn_on":  {"camera": "ON",  "photodiode": "ON",  "current": "ON"},
            "toggle":   {"camera": "OFF", "photodiode": "OFF", "current": "OFF"}  # из ON -> OFF
        }
    )

    hypotheses = [H0, H1]

    # ---------- T1: независимые сенсоры ----------
    # Лампа физически ON, выполняем toggle -> становится OFF.
    # Все сенсоры независимы, поэтому H1 после toggle ожидает OFF, и наблюдения совпадают.
    graph_independent = DependencyGraph({
        "camera": ["cam_hw"],
        "photodiode": ["adc1"],
        "current": ["adc2"]
    })

    run_scenario(
        "T1: Independent sensors, lamp ON, toggle -> OFF",
        action_sequence=["toggle", "toggle"],
        observations_sequence=[
            {"camera": "OFF", "photodiode": "OFF", "current": "OFF"},  # после toggle лампа OFF
            {"camera": "OFF", "photodiode": "OFF", "current": "OFF"}   # повтор для устойчивости
        ],
        hypotheses=hypotheses,
        graph=graph_independent
    )

    # ---------- T2: коррелированные сенсоры (общий MCU) ----------
    # Лампа физически OFF, но все сенсоры (зависимые от MCU) показывают ON.
    # После turn_off гипотезы обе ожидают OFF, но наблюдения ON.
    # Так как все сенсоры разделяют общий компонент, расхождение объяснимо,
    # и обе гипотезы остаются.
    graph_correlated = DependencyGraph({
        "camera": ["mcu"],
        "photodiode": ["mcu"],
        "current": ["mcu"]
    })

    run_scenario(
        "T2: Correlated sensors (shared MCU), lamp OFF, all sensors lie (show ON)",
        action_sequence=["turn_off", "turn_off"],
        observations_sequence=[
            {"camera": "ON", "photodiode": "ON", "current": "ON"},
            {"camera": "ON", "photodiode": "ON", "current": "ON"}
        ],
        hypotheses=hypotheses,
        graph=graph_correlated
    )

    # ---------- T3: активное вмешательство разрешает неоднозначность ----------
    # Теперь сенсоры camera и photodiode разделяют MCU (могут лгать), а current независим.
    # Начальное состояние: лампа OFF, camera/photodiode показывают ON (MCU врёт),
    # current показывает OFF (честно). Выполняем toggle, лампа включается,
    # current показывает ON, camera/photodiode всё ещё ON.
    # Тогда H0 (OFF) после toggle ожидает ON, и всё согласуется; H1 (ON) после toggle ожидает OFF,
    # и current (ON) противоречит (так как current должен был бы показать OFF после выключения).
    graph_partial = DependencyGraph({
        "camera": ["mcu"],
        "photodiode": ["mcu"],
        "current": ["adc2"]
    })

    run_scenario(
        "T3: Partial correlation, active toggle resolves ambiguity",
        action_sequence=["turn_off", "toggle"],
        observations_sequence=[
            {"camera": "ON", "photodiode": "ON", "current": "OFF"},  # после turn_off (но lamp off, MCU лжёт)
            {"camera": "ON", "photodiode": "ON", "current": "ON"}    # после toggle, лампа стала ON, current честен
        ],
        hypotheses=hypotheses,
        graph=graph_partial
    )


if __name__ == "__main__":
    main()