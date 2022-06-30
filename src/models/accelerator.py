import math
import numpy as np
from shapely.geometry import LineString
from src.models.road_profiler import RoadProfiler

LEFT = 0
RIGHT = 1


class Accelerator:
    def __init__(self, eps, side, speed, rotation, orig=(0, 0, 0)):
        self.sphere_colors = list()
        self.spheres = list()
        self.points = list()
        self.script = list()
        self.radii = list()
        self.speed = speed
        if side == LEFT:
            x = -eps + orig[0]
            y = -eps + orig[1]
        else:
            x = eps + orig[0]
            y = eps + orig[1]
        self.orig = (x, y, 0)
        self.rotation = rotation[2] + 180

    def setup(self, is_debug: bool = False):
        # Using an initial rotation of the car
        # Generate a trajectory
        orig = self.orig
        trajectory = list()
        color = [1.0, 0.0, 0.0, 1]

        for i in range(200):
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

    def get_lst(self):
        return LineString([(t[0], t[1]) for t in self.points])
