import click
import json
import platform
import numpy as np
from src.models import SimulationFactory, Simulation, SimulationScore, SimulationExec
from src.models.ac3rp import CrashScenario
from src.models.constant import CONST
from experiment import Experiment
from visualization import Scenario as VehicleTrajectoryVisualizer, ExperimentVisualizer

import warnings
warnings.filterwarnings('ignore')


@click.group()
def cli():
    pass


@cli.command()
@click.option('--scenario', required=True, type=click.Path(exists=True), multiple=False,
              help="Input accident sketch for generating the simulation")
@click.pass_context
def plot_ac3r(ctx, scenario):
    # Pass the context of the command down the line
    ctx.ensure_object(dict)

    """Take a JSON scenario file and plot the AC3R data points."""
    VehicleTrajectoryVisualizer.plot_ac3r(scenario)


@cli.command()
@click.option('--scenario', required=True, type=click.Path(exists=True), multiple=False,
              help="Input accident sketch for generating the simulation")
@click.pass_context
def plot_ac3rp(ctx, scenario):
    # Pass the context of the command down the line
    ctx.ensure_object(dict)

    """Take a JSON scenario file and plot the AC3RPlus data points."""
    VehicleTrajectoryVisualizer.plot_ac3rp(scenario)


@cli.command()
@click.option('--scenario', required=True, type=click.Path(exists=True), multiple=False,
              help="Input accident sketch for generating the simulation")
@click.pass_context
def run_from(ctx, scenario):
    # Pass the context of the command down the line
    ctx.ensure_object(dict)

    """Take a JSON scenario file and run the entire search algorithm."""
    with open(scenario) as file:
        crisce_data = json.load(file)

    try:
        with open(scenario.replace("data", "text")) as file:
            ac3r_data = json.load(file)
    except Exception as e:
        print("Text file not found!")
        ac3r_data = None

    sim_factory = SimulationFactory(CrashScenario.from_json(crisce_data, ac3r_data))
    simulation = Simulation(sim_factory=sim_factory, name=scenario.split('\\')[1], need_teleport=True, debug=False)

    # Running on Windows only
    if platform.system() == CONST.WINDOWS:
        SimulationExec(simulation=simulation, is_birdview=False).execute(timeout=20)
        print(f'Simulation Score: {SimulationScore(simulation).calculate(debug=True)}')
        print(f'Expected Score: {SimulationScore(simulation).get_expected_score(debug=False)}')


@cli.command()
@click.option('--scenario', required=True, type=click.Path(exists=True), multiple=False,
              help="Input accident sketch for generating the simulation")
def search_from(ctx, scenario):
    # Pass the context of the command down the line
    ctx.ensure_object(dict)
    experiment: Experiment = Experiment(scenario)
    experiment.run()


def execute_searching_from(scenario_files):
    single_mutator = [
        {
            "type": CONST.MUTATE_SPEED_CLASS,
            "probability": 0.5,
            "params": {"mean": 0, "std": 15, "min": 10, "max": 50}
        },
    ]

    multi_mutators = [
        {
            "type": CONST.MUTATE_SPEED_CLASS,
            "probability": 0.5,
            "params": {"mean": 0, "std": 15, "min": 10, "max": 50}
        },
        {
            "type": CONST.MUTATE_INITIAL_POINT_CLASS,
            "probability": 0.5,
            "params": {"mean": 0, "std": 1, "min": -5, "max": 5}
        },
    ]

    for mutator_dict in [{"name": "single", "mutators": single_mutator},
                         {"name": "multi", "mutators": multi_mutators}]:
        for scenario in scenario_files:
            case_name = scenario["name"]
            path = scenario["path"]
            # Random Search
            for i in np.arange(start=1, stop=11, step=1):
                sim_name: str = f'{(mutator_dict["name"].title() + "_Random")}_{str(i)}'
                print(f'Case {case_name}: Level {sim_name}...')
                exp: Experiment = Experiment(file_path=path,
                                             case_name=case_name,
                                             simulation_name=sim_name,
                                             mutators=mutator_dict["mutators"],
                                             method_name=CONST.RANDOM,
                                             epochs=30)
                exp.run()

            # OpO Search
            for i in np.arange(start=1, stop=11, step=1):
                sim_name: str = f'{(mutator_dict["name"].title() + "_OpO")}_{str(i)}'
                print(f'Case {case_name}: Level {sim_name}...')
                exp: Experiment = Experiment(file_path=path,
                                             case_name=case_name,
                                             simulation_name=sim_name,
                                             mutators=mutator_dict["mutators"],
                                             method_name=CONST.OPO,
                                             epochs=30)
                exp.run()
            print("=========")


# make sure we invoke cli
if __name__ == '__main__':
    # cli()
    # exit()
    scenarios = [
        # {"name": "148154", "path": "ciren/148154/data.json"},
        # {"name": "129224", "path": "ciren/129224/data.json"},
        # {"name": "99817", "path": "ciren/99817/data.json"},
        # {"name": "117021", "path": "ciren/117021/data.json"},
        # {"name": "171831", "path": "ciren/171831/data.json"},
        # {"name": "100271", "path": "ciren/100271/data.json"},
        # {"name": "103378", "path": "ciren/103378/data.json"},
        # {"name": "105203", "path": "ciren/105203/data.json"},
        # {"name": "105222", "path": "ciren/105222/data.json"},
        # {"name": "108812", "path": "ciren/108812/data.json"},
        # {"name": "119839", "path": "ciren/119839/data.json"},
        # {"name": "119489", "path": "ciren/119489/data.json"},
        # {"name": "120013", "path": "ciren/120013/data.json"},
        # {"name": "120305", "path": "ciren/120305/data.json"},
        # {"name": "121520", "path": "ciren/121520/data.json"},
        # {"name": "122080", "path": "ciren/122080/data.json"},
        # {"name": "128066", "path": "ciren/128066/data.json"},
        # {"name": "128697", "path": "ciren/128697/data.json"},
        # {"name": "137748", "path": "ciren/137748/data.json"},
        # {"name": "122168", "path": "ciren/122168/data.json"},
    ]

    execute_searching_from(scenarios)

    scenarios = [
        # ["ciren/99817/data.json", [1.4, 1.75], [1.1, 1.95]],
        # ["ciren/100271/data.json", [-1, 1.95], [-2.25, 3.25]],
        # ["ciren/103378/data.json", [1.6, 1.85], [1.45, 1.95]],
        # ["ciren/105203/data.json", [-0.75, 1.85], [-2.5, 2.75]],
        # ["ciren/105222/data.json", [1.75, 1.81], [1.6, 1.9]],
        #
        # ["ciren/108812/data.json", [-1.25, 1.95], [-3, 3.25]],
        # ["ciren/117021/data.json", [1.65, 1.72], [1.55, 1.75]],
        # ["ciren/119489/data.json", [-1.25, 1.95], [-3, 3.25]],
        # ["ciren/119839/data.json", [1.6, 1.72], [1.5, 1.78]],
        # ["ciren/120013/data.json", [1.74, 1.81], [1.6, 1.9]],
        #
        # ["ciren/120305/data.json", [1.575, 1.81], [1.45, 1.95]],
        # ["ciren/121520/data.json", [1.58, 1.82], [1.45, 1.9]],
        # ["ciren/122080/data.json", [1.4, 1.72], [1.1, 1.87]],
        # ["ciren/128066/data.json", [-0.5, 2], [-1.5, 3]],
        # ["ciren/128697/data.json", [1.58, 1.82], [1.45, 1.95]],
        #
        # ["ciren/129224/data.json", [1.35, 1.75], [1.25, 1.9]],
        # ["ciren/137748/data.json", [1.5, 1.75], [1.35, 1.8]],
        # ["ciren/148154/data.json", [1.55, 1.85], [1.45, 1.95]],
        # ["ciren/171831/data.json", [-1, 2], [-1.5, 3]],
        # ["ciren/122168/data.json", [1.725, 1.82], [1.5, 1.9]],
    ]

    for s in scenarios:
        soo = ExperimentVisualizer(s[0], s[1], s[2])
        soo.visualize()
        soo.visualize_box_plot()

