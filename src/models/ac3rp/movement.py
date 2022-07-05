from src.models.ac3rp import segment
from shapely.geometry import Point
import numpy


class Movement:
    """
    The Movement class declares the interface that capture all driving action of vehicle.

    Args:
        trajectory (list): e.g.
            [
                (x1,y1,speed), (x2,y2,speed), (x3,y3,speed)
            ]
    """

    def __init__(self, trajectory):
        self.trajectory = trajectory

    def get_driving_points(self):
        """
        Translate list of driving actions to list of continuous points
        """
        return [(action[0], action[1]) for action in self.trajectory]

    def set_driving_actions(self, new_trajectory):
        """
        Replace the current the list of trajectory with new points
        """
        for i, action in enumerate(self.trajectory):
            tmp_action = list(action)
            tmp_action[0] = new_trajectory[i][0]
            tmp_action[1] = new_trajectory[i][1]
            self.trajectory[i] = tuple(tmp_action)

    def set_speed(self, speed):
        """
        Replace the current speed the list of trajectory with new speed value
        """
        for i, action in enumerate(self.trajectory):
            tmp_action = list(action)
            tmp_action[2] = speed
            self.trajectory[i] = tuple(tmp_action)

    def get_mean_speed(self):
        """
        Return the average speed of trajectories
        """
        return numpy.mean([i[2] for i in self.trajectory])

    def get_speeds(self):
        """
        Return the list of speed from different driving action
        """
        return [i[2] for i in self.trajectory]

    def __str__(self):
        return str(self.__class__) + ": " + str(self.__dict__)
