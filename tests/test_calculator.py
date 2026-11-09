import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src/gest-calc"))
from calculator import Calculator, evaluate


class CalculationTests(unittest.TestCase):
    def test_operations_and_precedence(self):
        for expression, expected in {"2+3": "5", "8-10": "-2", "6*7": "42",
                                     "8/4": "2", "2+3*4": "14", "8/4*2": "4",
                                     "0.1+0.2": "0.3", "5*-2": "-10", "-0": "0"}.items():
            with self.subTest(expression=expression):
                self.assertEqual(evaluate(expression), expected)

    def test_invalid_inputs(self):
        for expression in ("", "2+", "1/0", "1..2", "2**3", "print(1)", "9" * 61):
            with self.subTest(expression=expression), self.assertRaises(ValueError):
                evaluate(expression)

    def test_editing_and_reset(self):
        calc = Calculator()
        for key in "12<+3=":
            calc.press(key)
        self.assertEqual(calc.expression, "4")
        calc.press("7")
        self.assertEqual(calc.expression, "7")
        calc.press("C")
        self.assertEqual(calc.expression, "")
        self.assertEqual(calc.previous, "")

    def test_continue_result_and_negative_operand(self):
        calc = Calculator()
        for key in "5*-2=+3=":
            calc.press(key)
        self.assertEqual(calc.expression, "-7")

    def test_error_recovery_and_decimal(self):
        calc = Calculator()
        for key in "1/0=":
            calc.press(key)
        self.assertTrue(calc.error)
        for key in "<2=":
            calc.press(key)
        self.assertEqual(calc.expression, "0.5")
        for key in "C.1.2":
            calc.press(key)
        self.assertEqual(calc.expression, "0.12")


if __name__ == "__main__":
    unittest.main()
