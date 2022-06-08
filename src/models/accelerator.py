import numpy as np
from matplotlib import pyplot as plt
from src.models.road_profiler import RoadProfiler

LEFT = 0
RIGHT = 1


class Accelerator:
    def __init__(self, side, speed):
        self.sphere_colors = list()
        self.spheres = list()
        self.points = list()
        self.script = list()
        self.radii = list()
        self.speed = speed
        if side == LEFT:
            self.orig = (-769.1, 400.8, 0)
        else:
            self.orig = (769.1, 400.8, 0)
        self.rot_quat = (0, 0, 1, 0)

    def setup(self, is_debug: bool = False):
        orig = self.orig
        trajectory = list()
        color = [1.0, 0.0, 0.0, 1]

        for i in range(1000):
            trajectory.append([
                # 4 * np.sin(np.radians(i)) + orig[0],
                # i * 2 + orig[1],
                orig[0],
                i*2 + orig[1],
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
