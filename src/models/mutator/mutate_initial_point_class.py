import numpy as np
from shapely.geometry import LineString, Point
from src.models.mutator import Mutator
from src.models.ac3rp import Vehicle
from src.models.ac3rp import common


class MutateInitialPointClass(Mutator):
    """
    Concrete Mutator provide an implementations of the Initial Point Mutator interface.
    """

    @staticmethod
    def visualization(vehicle, points, mutated_point):
        from descartes import PolygonPatch
        import matplotlib.pyplot as plt
        dist_x, dist_y = 0, 0

        def plot_roads(plt, roads):
            for i, road in enumerate(roads):
                road_nodes = road.road_nodes
                road_poly = LineString([(t[0] + dist_x, t[1] + dist_y) for t in road_nodes]).buffer(
                    road.road_width, cap_style=2,
                    join_style=2)
                road_patch = PolygonPatch(road_poly, fc='gray', ec='dimgray')
                plt.gca().add_patch(road_patch)
                xs = [p[0] + dist_x for p in road_nodes]
                ys = [p[1] + dist_y for p in road_nodes]
                plt.plot(xs, ys, '-', color="#9c9c9c")

        fig = plt.figure()
        plt.clf()
        plot_roads(plt, [vehicle.road_data["road"]])
        for point in points:
            if common.is_inside_polygon(Point(point[0], point[1]), vehicle.road_data["road_poly"]):
                plt.plot(point[0], point[1], '.', color="green")
            else:
                plt.plot(point[0], point[1], '.', color="red")

        plt.plot(mutated_point[0], mutated_point[1], 'o', color="black")

        plt.gca().set_aspect("equal")
        plt.show()

    def process(self, vehicle: Vehicle, is_random=False) -> Vehicle:
        # Not working for parked car
        if len(vehicle.movement.trajectory) == 1:
            return vehicle

        # Define an expected distance to move an initial point
        expected_distance = self.random_value() if is_random else self.mutate_value(0)
        vehicle_lst = LineString(vehicle.movement.get_driving_points())

        # Looking for mutated point as a new origin with given expected_distance and vehicle_lst
        mutated_point = None

        # A threshold to reset expected_distance, it can be any number e.g 10, 20, 50, 100, etc.
        threshold_reset_distance = 50

        # Run until point staying the road
        count_iteration = 0
        while mutated_point is None:
            # Generate points within line
            # points = common.mutate_initial_point(lst=vehicle_lst,
            #                                      delta=vehicle.road_data["mutate_equation"],
            #                                      distance=expected_distance, num_points=1)
            # Generate point in circle
            points = common.mutate_initial_point(lst=vehicle_lst,
                                                 mode=2, num_points=50,
                                                 minR=expected_distance, maxR=expected_distance)

            filtered_points = list()
            for p in points:
                # Since we have one generated point, so convert a new point to Point object
                point = Point(p[0], p[1])
                # Check if the new point stays in the vehicle road
                if common.is_inside_polygon(point, vehicle.road_data["road_poly"]):
                    filtered_points.append(point)

            if len(filtered_points) > 0:
                # Select the first point
                random_idx = np.random.choice(list(range(0, len(filtered_points))))
                mutated_point = filtered_points[random_idx]

                # Debug
                # self.visualization(vehicle, points, (mutated_point.x, mutated_point.y))

            count_iteration += 1
            if count_iteration % threshold_reset_distance == 0:
                expected_distance = self.random_value() if is_random else self.mutate_value(0)
                print(f'MutateInitialPointClass object took {count_iteration} iterations to find the mutated point!')

        # With a new origin, we can compute a new mutated driving actions (LineString) for vehicle
        mutated_driving_action = common.translate_ls_to_new_origin(lst=vehicle_lst,
                                                                   new_origin=mutated_point)
        # Replace the old driving actions by a new one
        vehicle.movement.set_driving_actions(list(mutated_driving_action.coords))
        return vehicle
