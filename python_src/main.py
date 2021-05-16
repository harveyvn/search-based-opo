import click
import json
import time
from visualization import VehicleTrajectoryVisualizer
from models import SimFactory, Simulation
from models.ac3rp import CrashScenario


@click.group()
def cli():
    pass


@cli.command()
@click.argument('scenario_file', type=click.Path(exists=True))
def plot_ac3r(scenario_file):
    """Take a JSON scenario file and plot the AC3R data points."""
    VehicleTrajectoryVisualizer.plot_ac3r(scenario_file)


@cli.command()
@click.argument('scenario_file', type=click.Path(exists=True))
def plot_ac3rp(scenario_file):
    """Take a JSON scenario file and plot the AC3RPlus data points."""
    VehicleTrajectoryVisualizer.plot_ac3rp(scenario_file)


@cli.command()
@click.argument('scenario_file', type=click.Path(exists=True))
def run_from_scenario(scenario_file):
    """Take a JSON scenario file and run the entire search algorithm."""
    with open(scenario_file) as file:
        scenario_data = json.load(file)
    sim_factory = SimFactory(CrashScenario.from_json(scenario_data))
    simulation = Simulation(sim_factory)
    simulation.execute_scenario(time.time() + 60 * 1)


# make sure we invoke cli
if __name__ == '__main__':
    cli()
