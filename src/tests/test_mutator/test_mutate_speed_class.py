import json
import unittest

from src.models.mutator import mutator as mutator_model
from src.models import categorize_mutator
from src.models import CONST
from src.models.ac3rp import CrashScenario


class TestMutateSpeedClass(unittest.TestCase):
    def test_probability_equal_5(self):
        mutator = categorize_mutator({
            "type": CONST.MUTATE_SPEED_CLASS,
            "probability": 5,
            "params": {"mean": 0, "std": 15, "min": 10, "max": 50}
        })
        expected = 5
        self.assertEqual(expected, mutator.probability)

    def test_mutator_is_speed_mutator(self):
        mutator = categorize_mutator({
            "type": CONST.MUTATE_SPEED_CLASS,
            "probability": 5,
            "params": {"mean": 0, "std": 15, "min": 10, "max": 50}
        })
        self.assertEqual(mutator_model.SpeedCreator, type(mutator))

    def test_vehicle_has_new_speed(self):
        with open("../../ciren/148154/data.json") as file:
            scenario_data = json.load(file)
        scenario = CrashScenario.from_json(crisce_json_data=scenario_data)
        vehicle = scenario.vehicles[0]
        old_speed = vehicle.get_speed()

        mutator = categorize_mutator({
            "type": CONST.MUTATE_SPEED_CLASS,
            "probability": 0.5,
            "params": {"mean": 0, "std": 15, "min": 10, "max": 50}
        })
        self.assertNotEqual(old_speed, mutator.mutate(vehicle).get_speed())
