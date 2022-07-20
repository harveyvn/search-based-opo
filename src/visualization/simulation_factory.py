from shapely.geometry import LineString
from descartes import PolygonPatch
from matplotlib import pyplot as plt
import pytz
from datetime import datetime


class VizSimFactory:
    def __init__(self, sim_fac):
        self.sf = sim_fac

    def plot_generate_accelerator(self):
        berlin_now = datetime.now(pytz.timezone('Europe/Berlin')).strftime("%Y%m%d_%I%M%S")
        dist_x, dist_y = 0, 0
        fig = plt.gcf()
        colors = [["#82ABF5", "#0000FF"], ["#FC6565", "#FF0000"]]

        # Render roads
        for i, road in enumerate(self.sf.scenario.roads):
            road_nodes = road.road_nodes
            lst = LineString([(t[0] + dist_x, t[1] + dist_y) for t in road_nodes])
            road_poly = lst.buffer(road.road_width, cap_style=2, join_style=2)
            road_patch = PolygonPatch(road_poly, fc="gray", ec="dimgray")
            plt.gca().add_patch(road_patch)
            xs = [p[0] + dist_x for p in road_nodes]
            ys = [p[1] + dist_y for p in road_nodes]
            plt.plot(xs, ys, '-', color="#9c9c9c")

        # Render vehicles
        for i, vehicle in enumerate(self.sf.scenario.vehicles):
            trajectory_points = vehicle.movement.trajectory
            xs = [p[0] for p in trajectory_points]
            ys = [p[1] for p in trajectory_points]
            plt.plot(xs, ys, '.-', label=vehicle.name, color=colors[i][0])
            # Highlight the endpoint to know the direction of the car
            plt.plot([xs[-1]], [ys[-1]], 'X', label=vehicle.name, color=colors[i][1])

        # Render accelerator
        for i, player in enumerate(self.sf.players):
            trajectory_points = player.accelerator.points
            xs = [p[0] for p in trajectory_points]
            ys = [p[1] for p in trajectory_points]
            plt.plot(xs, ys, '.-', color=colors[i][0])
            # Highlight the endpoint to know the direction of the car
            plt.plot([xs[-1]], [ys[-1]], 'X', color=colors[i][1])

        plt.title(f'AC3R generate_accelerator')
        plt.gca().set_aspect('equal')
        plt.show()
        fig.savefig(f'debug/generate_accelerator_{berlin_now}.png', bbox_inches="tight")
