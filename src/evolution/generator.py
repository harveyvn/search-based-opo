import copy
from src.models.ac3rp import CrashScenario
from src.models.mutator import Transformer


class Generator:
    @staticmethod
    def generate_random_from(scenario: CrashScenario, transformer: Transformer):
        # Create a new crash scenario
        return transformer.mutate_random_from(copy.deepcopy(scenario))
