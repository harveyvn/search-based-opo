import time
import traceback
from beamngpy import Scenario, BeamNGpy
from src.libraries.libs import cal_speed
from src.models import Simulation
from src.models.player import Player
from src.models.simulation_data import VehicleStateReader, SimulationDataCollector
from src.models.simulation_data import SimulationParams, SimulationDataContainer

CRASHED = 1
NO_CRASH = 0


class SimulationExec:
    def __init__(self, simulation: Simulation, is_birdview: bool = False):
        self.simulation = simulation
        self.beamng = self.simulation.init_simulation()
        self.scenario = None
        self.is_birdview: bool = is_birdview

    def bring_up(self):
        self.beamng.open(launch=True)

        self.scenario = Scenario("smallgrid", self.simulation.name)

        # Import roads from scenario obj to beamNG instance
        for road in self.simulation.roads:
            self.scenario.add_road(road)

        # Import vehicles from scenario obj to beamNG instance
        for player in self.simulation.players:
            if self.simulation.need_teleport:
                self.scenario.add_vehicle(player.vehicle, pos=player.accelerator.orig,
                                          rot=player.rot, rot_quat=player.rot_quat)
            else:
                self.scenario.add_vehicle(player.vehicle, pos=player.pos,
                                          rot=player.rot, rot_quat=player.rot_quat)

        # Enable bird view
        if self.is_birdview:
            cam_pos = self.simulation.center_point
            cam_dir = (0, 1, -60)
            self.beamng.set_free_camera(cam_pos, cam_dir)

        self.scenario.make(self.beamng)

        self.beamng.set_deterministic()

        self.beamng.load_scenario(self.scenario)

        self.beamng.start_scenario()

        # Pause the simulator only after loading and starting the scenario
        self.beamng.pause()

    def execute(self, timeout: int = 60):
        is_teleport = False
        is_valid_to_teleport = [False, False]
        start_time = 0
        is_crash = False
        # Condition to start the 2nd vehicle after driving 1st for a while
        # -1: 1st and 2nd start at the same time
        distance_to_trigger = -1
        vehicleId_to_trigger = 0
        sim_data_collectors = self.init_data_collector()

        try:
            self.bring_up()
            # Drawing debug line and forcing vehicle moving by given trajectory
            idx = 0
            for player in self.simulation.players:
                vehicle = player.vehicle
                road_pf = player.road_pf
                if player.distance_to_trigger > 0:
                    distance_to_trigger = player.distance_to_trigger
                    vehicleId_to_trigger = idx
                # ai_set_script not working for parking vehicle, so
                # the number of node from road_pf.script must > 2
                if len(road_pf.script) > 2:
                    if self.simulation.need_teleport:
                        vehicle.ai_set_script(script=player.accelerator.script)
                        self.beamng.add_debug_spheres(coordinates=player.accelerator.points,
                                                      radii=player.accelerator.radii,
                                                      rgba_colors=player.accelerator.sphere_colors)
                    else:
                        vehicle.ai_set_script(script=road_pf.script)
                        self.beamng.add_debug_spheres(coordinates=road_pf.points,
                                                      radii=road_pf.radii,
                                                      rgba_colors=road_pf.sphere_colors)

                idx += 1

            # We need to compute distance between vehicles if and only if one of two vehicle
            # has a distance_to_trigger property > 0
            # In addition, this variable will prevent the function keep running after 2nd car moving
            is_require_computed_distance = distance_to_trigger > -1
            # Update the vehicle information
            sim_data_collectors.start()
            start_time = time.time()

            # Begin a scenario
            while time.time() < (start_time + timeout):
                # Record the vehicle state for every 10 steps
                self.beamng.step(10)
                sim_data_collectors.collect()

                # Compute the distance between two vehicles
                if is_require_computed_distance:
                    distance_change = self.simulation.get_vehicles_distance(debug=self.simulation.debug)
                    # Trigger the 2nd vehicle
                    if self.simulation.trigger_vehicle(player=self.simulation.players[vehicleId_to_trigger],
                                                       distance_report=distance_change,
                                                       debug=self.simulation.debug):
                        is_require_computed_distance = False  # No need to compute distance anymore

                for i, player in enumerate(self.simulation.players):
                    # Find the position of moving car
                    self.simulation.collect_vehicle_position_and_timer(self.beamng, player)
                    # Collect the damage sensor information
                    vehicle = player.vehicle
                    # Check whether the imported vehicle existed in beamNG instance or not
                    if bool(self.beamng.poll_sensors(vehicle)) is False:
                        raise Exception("Exception: Vehicle not found in bng_instance!")
                    sensor = self.beamng.poll_sensors(vehicle)['damage']
                    if sensor['damage'] != 0:  # Crash detected
                        # Disable AI control
                        self.simulation.disable_vehicle_ai(vehicle)
                        is_crash = True

                    if self.simulation.need_teleport:
                        # Calculate current speed
                        cur_speed = 0
                        if len(player.positions) > 2:
                            cur_speed = cal_speed(player.get_pos_and_timer_at(-2), player.get_pos_and_timer_at(-1))

                        # Check if vehicle reaches certain speed
                        if (player.speed < cur_speed < player.speed + 0.5) and not is_valid_to_teleport[i]:
                            is_valid_to_teleport[i] = True

                # Trigger teleport
                if any(cond is True for cond in is_valid_to_teleport) and not is_teleport:
                    is_teleport = self.teleport(self.beamng, self.simulation.players)

            self.clean(is_crash)
            sim_data_collectors.end(success=True)

            # Save the last position of vehicle
            for player in self.simulation.players:
                self.simulation.collect_vehicle_position_and_timer(self.beamng, player)

        except Exception as ex:
            sim_data_collectors.save()
            sim_data_collectors.end(success=False, exception=ex)
            traceback.print_exception(type(ex), ex, ex.__traceback__)
            self.close()
        finally:
            sim_data_collectors.save()
            self.close()
            print("Simulation Time: ", time.time() - start_time)
            print("is_teleport: ", is_teleport)

    def clean(self, is_crash: bool):
        # Analyze the scenario:
        # - Set a status to a scenario
        # - Collect broken part of vehicles
        if not is_crash:
            print("Timed out!")
        else:
            status_players = [NO_CRASH] * len(self.simulation.players)  # zeros list e.g [0, 0]
            for i, player in enumerate(self.simulation.players):
                vehicle = player.vehicle
                sensor = self.beamng.poll_sensors(vehicle)['damage']
                if sensor['damage'] != 0:
                    if not sensor['part_damage']:
                        # There is a case that a simulation reports a crash damage
                        # without any damaged components
                        # player.collect_damage({"etk800_any": {"name": "Any", "damage": 0}})
                        status_players[i] = NO_CRASH
                        print("Crash detected! But no broken component is specified!")
                    else:
                        status_players[i] = CRASHED
                        print("Crash detected!")
                        player.collect_damage(sensor['part_damage'])

            if CRASHED in status_players:  # [1, 0] or [0, 1]
                self.simulation.status = CRASHED

    def close(self):
        try:
            if self.beamng:
                self.beamng.close()
        except Exception as ex:
            traceback.print_exception(type(ex), ex, ex.__traceback__)

    def init_data_collector(self) -> SimulationDataContainer:
        # Prepare simulation data collection
        simulation_id = time.strftime('%Y-%m-%d--%H-%M-%S', time.localtime())
        simulation_name = 'beamng_executor/sim_$(id)'.replace('$(id)', simulation_id)
        sim_data_collectors = SimulationDataContainer(debug=self.simulation.debug)
        for i in range(len(self.simulation.players)):
            player = self.simulation.players[i]
            vehicle_state = VehicleStateReader(player.vehicle, self.beamng)
            sim_data_collectors.append(
                SimulationDataCollector(player.vehicle,
                                        self.beamng,
                                        SimulationParams(beamng_steps=50,
                                                         delay_msec=int(25 * 0.05 * 1000)),
                                        vehicle_state_reader=vehicle_state,
                                        simulation_name=simulation_name + "_v" + str(i + 1))
            )
        return sim_data_collectors

    def teleport(self, beamng: BeamNGpy, players: [Player]) -> bool:
        for player in players:
            vehicle = player.vehicle
            road_pf = player.road_pf
            timer = beamng.poll_sensors(vehicle)["timer"]["time"]
            current_pos = beamng.poll_sensors(vehicle)["state"]["pos"]

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
            self.beamng.queue_lua_command(cmd)
            vehicle.ai_set_script(script=n_script, cling=True)
            self.beamng.add_debug_spheres(coordinates=road_pf.points,
                                          radii=road_pf.radii,
                                          rgba_colors=road_pf.sphere_colors)
        return True
