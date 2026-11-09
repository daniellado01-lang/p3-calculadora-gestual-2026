import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src/gest-calc"))
from gestures import DwellSelector, PinchSelector, pinch_ratio


class GestureTests(unittest.TestCase):
    def setUp(self):
        self.selector = PinchSelector()

    def arm(self):
        self.selector.update("7", 0.8, 0)
        self.selector.update("7", 0.8, 0.3)

    def test_one_click_per_pinch(self):
        self.arm()
        self.assertIsNone(self.selector.update("7", 0.2, 0.4))
        self.assertEqual(self.selector.update("7", 0.2, 0.6), "7")
        self.assertIsNone(self.selector.update("7", 0.2, 2))
        self.selector.update("7", 0.8, 3)
        self.selector.update("7", 0.8, 3.3)
        self.selector.update("7", 0.2, 3.4)
        self.assertEqual(self.selector.update("7", 0.2, 3.6), "7")

    def test_closed_hand_on_entry_does_not_click(self):
        self.assertIsNone(self.selector.update("7", 0.2, 0))
        self.assertIsNone(self.selector.update("7", 0.2, 1))

    def test_loss_of_tracking_requires_release(self):
        self.arm()
        self.selector.update(None, None, 0.4)
        self.assertIsNone(self.selector.update("7", 0.2, 1))

    def test_target_change_cancels(self):
        self.arm()
        self.selector.update("8", 0.2, 0.4)
        self.assertIsNone(self.selector.update("8", 0.2, 0.6))

    def test_short_pinch_is_ignored(self):
        self.arm()
        self.selector.update("7", 0.2, 0.4)
        self.assertIsNone(self.selector.update("7", 0.8, 0.45))

    def test_hysteresis_does_not_release_lock(self):
        self.arm()
        self.selector.update("7", 0.2, 0.4)
        self.selector.update("7", 0.2, 0.6)
        self.selector.update("7", 0.45, 0.7)
        self.assertIsNone(self.selector.update("7", 0.2, 1))

    def test_scale_invariance_and_small_hand(self):
        landmarks = [SimpleNamespace(x=0, y=0) for _ in range(21)]
        landmarks[17].x = .2
        landmarks[8].x = .04
        self.assertAlmostEqual(pinch_ratio(landmarks, 640, 480), .2)
        self.assertAlmostEqual(pinch_ratio(landmarks, 1280, 960), .2)
        self.assertIsNone(pinch_ratio(landmarks, 10, 10))


class DwellTests(unittest.TestCase):
    def test_selection_and_no_repeat(self):
        selector = DwellSelector()
        self.assertIsNone(selector.update("2", .8, 0))
        self.assertIsNone(selector.update("2", .8, .5))
        self.assertEqual(selector.update("2", .8, 1.1), "2")
        self.assertIsNone(selector.update("2", .8, 3))
        selector.update(None, .8, 4)
        selector.update("2", .8, 5)
        self.assertEqual(selector.update("2", .8, 6.1), "2")

    def test_change_or_loss_cancels_countdown(self):
        selector = DwellSelector()
        selector.update("2", .8, 0)
        self.assertIsNone(selector.update("3", .8, .9))
        self.assertIsNone(selector.update("3", .8, 1.1))
        selector.update(None, None, 1.2)
        self.assertIsNone(selector.update("3", .8, 3))


if __name__ == "__main__":
    unittest.main()
