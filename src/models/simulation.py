import os
import beamngpy
import numpy as np
from shapely.geometry import Point
from typing import List
from beamngpy import BeamNGpy
from src.models import SimulationFactory, Player, RoadProfiler

CRASHED = 1
NO_CRASH = 0
LOW, MED, HIGH = "LOW", "MED", "HIGH"
VERSION = beamngpy.__version__


class Simulation:
    def __init__(self, name, sim_factory: SimulationFactory, need_teleport: bool = False, debug: bool = False):
        self.sim_factory = sim_factory
        self.name = name
        self.roads: List[beamngpy.Road] = sim_factory.generate_roads()
        self.players: List[Player] = sim_factory.generate_players()
        self.targets: {} = sim_factory.generate_targets()
        self.status: int = NO_CRASH
        self.debug: bool = debug
        self.center_point = sim_factory.get_center_scenario()
        self.need_teleport = sim_factory.generate_accelerator(debug=debug) if need_teleport else False

    @staticmethod
    def init_simulation() -> BeamNGpy:
        if VERSION == "1.23":
            bng_home = "D:\\BeamNG.drive-0.25.0.0.DEV13908"
            bng_research = "D:\\BeamNG.drive-0.25.0.0.DEV13908_userpath"
        else:
            bng_home = os.getenv('BNG_HOME')
            bng_research = os.getenv('BNG_RESEARCH')
        host = '127.0.0.1'
        port = 64257
        return BeamNGpy(host, port, bng_home, bng_research)

    @staticmethod
    def disable_vehicle_ai(vehicle: beamngpy.vehicle):
        vehicle.ai_set_mode('disable')
        if VERSION == "1.23":
            vehicle.set_velocity(0)
        else:
            vehicle.ai_set_speed(0, 'set')
        vehicle.control(throttle=0, steering=0, brake=0, parkingbrake=0)
        vehicle.update_vehicle()

    @staticmethod
    def collect_vehicle_position_and_timer(beamng: BeamNGpy, player: Player) -> Player:
        vehicle = player.vehicle
        if VERSION == "1.23":
            pos = beamng.poll_sensors(vehicle)["state"]["pos"]
            current_position = (pos[0], pos[1])
            current_timer = beamng.poll_sensors(vehicle)["timer"]["time"]
            player.collect_positions(current_position)
            player.collect_timers(current_timer)
        else:
            current_position = (vehicle.state['pos'][0], vehicle.state['pos'][1])
            player.collect_positions_only(current_position)

        return player

    def get_vehicles_distance(self, debug: bool = False) -> float:
        v1, v2 = self.players[0].vehicle, self.players[1].vehicle
        p1, p2 = Point(v1.state['pos'][0], v1.state['pos'][1]), Point(v2.state['pos'][0], v2.state['pos'][1])
        distance = p1.distance(p2)

        # Debug line
        if debug is True:
            print("Distances between vehicles: ", distance)

        return distance

    @staticmethod
    def render_debug_line(bng_instance: BeamNGpy, road_pf: RoadProfiler):
        if VERSION == "1.23":
            bng_instance.add_debug_spheres(coordinates=road_pf.points,
                                           radii=road_pf.radii,
                                           rgba_colors=road_pf.sphere_colors)
        else:
            bng_instance.add_debug_line(road_pf.points, road_pf.sphere_colors,
                                        spheres=road_pf.spheres, sphere_colors=road_pf.sphere_colors,
                                        cling=True, offset=0.1)

    @staticmethod
    def trigger_vehicle(player: Player, distance_report: float = None, debug: bool = False) -> bool:
        is_trigger = False
        # The car stills wait until their current distance <= distance_to_trigger
        if distance_report is not None and player.distance_to_trigger > distance_report:
            is_trigger = True

        # Trigger normal vehicles which move in the beginning
        if distance_report is None and player.distance_to_trigger == -1:
            is_trigger = True

        # Add vehicle to a scenario
        if is_trigger:
            vehicle = player.vehicle
            road_pf = player.road_pf
            if len(road_pf.script) > 2:
                vehicle.ai_set_mode("manual")
                vehicle.ai_set_script(road_pf.script, cling=False)

        # Debug line
        if debug is True:
            print(f'Alert! The vehicle starts to move. Distance to Trigger/Current Distance: '
                  f'{str(round(player.distance_to_trigger, 2))}/{str(round(distance_report, 2))}')
        return is_trigger

    @staticmethod
    def trigger_vehicle_teleport(player: Player):
        vehicle = player.vehicle
        vehicle.ai_set_mode("manual")
        vehicle.ai_set_script(script=player.accelerator.script)

    def get_data_outputs(self) -> {}:
        data_outputs = {}
        for player in self.players:
            # data_outputs[player.vehicle.vid] = player.get_damage()
            dam_values = list(set([c["damage"] for c in player.get_damage()]))
            if len(dam_values) > 3:
                from src.models import KMeans
                k_means = KMeans(dam_values).model
                km_dict = {LOW: [], MED: [], HIGH: []}
                labels = k_means.predict(sorted(k_means.cluster_centers_.tolist()))  # low, med, high ids
                for comp in player.get_damage():
                    value = comp["damage"]
                    label = k_means.predict(np.array(value).reshape(-1, 1))
                    if label == labels[0]:  # LOW
                        km_dict[LOW].append(comp)
                    elif label == labels[1]:  # MED
                        km_dict[MED].append(comp)
                    else:  # HIGH
                        km_dict[HIGH].append(comp)
                # Get the MED and HIGH damage components
                data_outputs[player.vehicle.vid] = [comp for k in km_dict if k != LOW for comp in km_dict[k]]
            else:
                data_outputs[player.vehicle.vid] = player.get_damage()
        return data_outputs

    def enable_free_cam(self, bng: BeamNGpy):
        cam_pos = self.center_point
        cam_dir = (0, 1, -60)
        bng.set_free_camera(cam_pos, cam_dir)

    def teleport(self, beamng: BeamNGpy, players: [Player]) -> bool:
        for player in players:
            vehicle = player.vehicle
            road_pf = player.road_pf
            timer = beamng.poll_sensors(vehicle)["timer"]["time"]
            if VERSION == "1.23":
                current_pos = beamng.poll_sensors(vehicle)["state"]["pos"]
            else:
                current_pos = (vehicle.state['pos'][0], vehicle.state['pos'][1], vehicle.state['pos'][2])

            target_pos = list(player.pos)
            target_pos[2] = current_pos[2]
            target_pos = tuple(target_pos)

            n_script = []
            for n in player.road_pf.script:
                n_script.append(
                    {
                        'x': n['x'],
                        'y': n['y'],
                        'z': 0,
                        't': n['t'] + timer
                    }
                )

            cmd = f'scenetree.findObject(\'{vehicle.vid}\'):setPositionNoPhysicsReset(vec3{target_pos})'
            beamng.queue_lua_command(cmd)
            vehicle.ai_set_mode("manual")
            vehicle.ai_set_script(script=n_script, cling=False)
            self.render_debug_line(beamng, road_pf)
        return True
