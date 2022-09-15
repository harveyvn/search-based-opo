import json
import os
from pathlib import Path
from typing import List
from bisect import bisect_left
from shapely.geometry import Point
import scipy.stats as ss

ROOT: Path = Path(os.path.abspath(os.path.join(os.path.dirname(__file__))))
PATH_TEST = str(ROOT.joinpath("../tests"))
PATH_DATA = str(ROOT.joinpath("../data"))


def _collect_police_report(path):
    with open(path) as file:
        report_data = json.load(file)
    return report_data


def VD_A(treatment: List[float], control: List[float]):
    """
    Computes Vargha and Delaney A index
    A. Vargha and H. D. Delaney.
    A critique and improvement of the CL common language
    effect size statistics of McGraw and Wong.
    Journal of Educational and Behavioral Statistics, 25(2):101-132, 2000
    The formula to compute A has been transformed to minimize accuracy errors
    See: http://mtorchiano.wordpress.com/2014/05/19/effect-size-of-r-precision/
    :param treatment: a numeric list
    :param control: another numeric list
    :returns the value estimate and the magnitude
    """
    m = len(treatment)
    n = len(control)

    if m != n:
        raise ValueError("Data d and f must have the same length")

    r = ss.rankdata(treatment + control)
    r1 = sum(r[0:m])

    # Compute the measure
    # A = (r1/m - (m+1)/2)/n # formula (14) in Vargha and Delaney, 2000
    A = (2 * r1 - m * (m + 1)) / (2 * n * m)  # equivalent formula to avoid accuracy errors

    levels = [0.147, 0.33, 0.474]  # effect sizes from Hess and Kromrey, 2004
    magnitude = ["negligible", "small", "medium", "large"]
    scaled_A = (A - 0.5) * 2

    magnitude = magnitude[bisect_left(levels, abs(scaled_A))]
    estimate = A

    return estimate, magnitude


def cal_speed(p1, p2):
    time = abs(p2[2] - p1[2])
    if time == 0:
        return 0

    p1 = Point(p1[0], p1[1])
    p2 = Point(p2[0], p2[1])
    dist = p1.distance(p2)

    if dist / time < 0.5:
        return 0
    return dist / time


def teleport_vehicle_keep_physics(beamng, vid, pos):
    cmd = f'scenetree.findObject(\'{vid}\'):setPositionNoPhysicsReset(vec3{pos})'
    print('Running command:', cmd)
    beamng.queue_lua_command(cmd)