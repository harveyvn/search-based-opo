import math
import numpy as np
from matplotlib import pyplot as plt
from src.models.road_profiler import RoadProfiler

LEFT = 0
RIGHT = 1


class Accelerator:
    def __init__(self, side, speed, rotation):
        self.sphere_colors = list()
        self.spheres = list()
        self.points = list()
        self.script = list()
        self.radii = list()
        self.speed = speed
        if side == LEFT:
            self.orig = (0, 0, 0)
        else:
            self.orig = (500, 500, 0)
        self.rotation = rotation[2] + 180

    def setup(self, is_debug: bool = False):
        # Using an initial rotation of the car
        # Generate a trajectory
        orig = self.orig
        trajectory = list()
        color = [1.0, 0.0, 0.0, 1]

        for i in range(500):
            trajectory.append([
                orig[0] + i * np.around(np.sin(math.radians(self.rotation)), decimals=5),
                orig[1] + i * np.around(np.cos(math.radians(self.rotation)), decimals=5),
                self.speed
            ])

        road_pf = RoadProfiler()
        road_pf.compute_ai_script(trajectory=trajectory, color=color)

        self.spheres = road_pf.spheres
        self.points = road_pf.points
        self.sphere_colors = road_pf.sphere_colors
        self.script = road_pf.script
        self.radii = road_pf.radii

        if is_debug:
            xs = [p[0] for p in self.points]
            ys = [p[1] for p in self.points]
            plt.plot(xs, ys, '.', color=color)
            plt.show()
