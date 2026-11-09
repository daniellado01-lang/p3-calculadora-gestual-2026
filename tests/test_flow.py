"""Comprueba que los selectores producen las operaciones previstas."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src/gest-calc"))
from calculator import Calculator
from gestures import DwellSelector, PinchSelector


class FlowTests(unittest.TestCase):
    def test_dwell_calculation_with_repeated_digits(self):
        selector, calculator = DwellSelector(), Calculator()
        now = 0
        for key in "11+3=":
            selector.update(None, .8, now)
            selector.update(key, .8, now + .1)
            selected = selector.update(key, .8, now + 1.2)
            self.assertEqual(selected, key)
            calculator.press(selected)
            self.assertIsNone(selector.update(key, .8, now + 2))
            now += 3
        self.assertEqual(calculator.expression, "14")

    def test_pinch_calculation_and_reset(self):
        selector, calculator = PinchSelector(), Calculator()
        now = 0
        for key in "2+3=C":
            selector.update(key, .8, now)
            selector.update(key, .8, now + .3)
            selector.update(key, .2, now + .4)
            selected = selector.update(key, .2, now + .6)
            self.assertEqual(selected, key)
            calculator.press(selected)
            if key == "=":
                self.assertEqual(calculator.expression, "5")
            now += 1
        self.assertEqual(calculator.expression, "")


if __name__ == "__main__":
    unittest.main()
