import json
import unittest

from src.models.mutator import mutator as mutator_model
from src.models import categorize_mutator, CONST
from src.models.ac3rp import CrashScenario


class TestMutateInitialPointClass(unittest.TestCase):
    def test_probability_equal_10(self):
        mutator = categorize_mutator({
            "type": CONST.MUTATE_INITIAL_POINT_CLASS,
            "probability": 10,
            "params": {"mean": 0, "std": 15, "min": 10, "max": 50}
        })
        expected = 10
        self.assertEqual(expected, mutator.probability)

    def test_mutator_is_speed_mutator(self):
        mutator = categorize_mutator({
            "type": CONST.MUTATE_INITIAL_POINT_CLASS,
            "probability": 5,
            "params": {"mean": 0, "std": 15, "min": 10, "max": 50}
        })
        self.assertEqual(mutator_model.InitialPointCreator, type(mutator))

    def test_handle_exception_when_no_mutator_type_found(self):
        expected = Exception
        with self.assertRaises(expected):
            mutator = categorize_mutator({
                "type": 'X',
                "probability": 5,
                "params": {"mean": 0, "std": 15, "min": 10, "max": 50}
            })

    def test_vehicle_has_new_initial_point(self):
        with open("../ciren/148154/data.json") as file:
            scenario_data = json.load(file)
        scenario = CrashScenario.from_json(crisce_json_data=scenario_data)
        vehicle = scenario.vehicles[0]

        old_intial_point = vehicle.movement.get_driving_points()[0]

        mutator = categorize_mutator({
            "type": CONST.MUTATE_INITIAL_POINT_CLASS,
            "probability": 0.5,
            "params": {"mean": 0, "std": 1, "min": -10, "max": 10}
        })
        new_initial_point = mutator.mutate(vehicle).movement.get_driving_points()[0]
        self.assertNotEqual(old_intial_point, new_initial_point)
