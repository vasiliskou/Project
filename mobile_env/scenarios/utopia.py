from mobile_env.core.base import MComCore
from mobile_env.core.entities import BaseStation, UserEquipment
from mobile_env.core.util import deep_dict_merge

# my imports
from typing import Dict, List, Set, Tuple
from mobile_env.core.my_entities import myUserEquipment
from mobile_env.core.schedules import MyScheduler


class Utopia(MComCore):
    def __init__(self, config={}, render_mode=None):
        # set unspecified parameters to default configuration
        config = deep_dict_merge(self.default_config(), config)
        config["width"], config["height"] = 200, 300

        stations = [
            (50, 100),
            (100, 100),
        ]

        stations = [(x, y) for x, y in stations]
        stations = [
            BaseStation(bs_id, pos, **config["bs"])
            for bs_id, pos in enumerate(stations)
        ]

        num_ues = 4
        # ues = [UserEquipment(ue_id, **config["ue"]) for ue_id in range(num_ues)]
        # users
        ues = [
            myUserEquipment(ue_id=1, service_type = "URLLC", velocity=0, snr_tr=config["ue"]["snr_tr"], noise=config["ue"]["noise"],height=config["ue"]["height"]),
            myUserEquipment(ue_id=2, service_type = "MIOT",velocity=0, snr_tr=config["ue"]["snr_tr"], noise=config["ue"]["noise"],height=config["ue"]["height"]),
            myUserEquipment(ue_id=3, service_type = "CV",velocity=0, snr_tr=config["ue"]["snr_tr"], noise=config["ue"]["noise"],height=config["ue"]["height"]),
            myUserEquipment(ue_id=4, service_type = "URLLC",velocity=0, snr_tr=config["ue"]["snr_tr"], noise=config["ue"]["noise"],height=config["ue"]["height"]),
        ]


        super().__init__(stations, ues, config, render_mode)

    @classmethod
    def default_config(cls):
        config = super().default_config()
        config["bs"]["bw"] = 50e6  # Update bandwidth
        config["ep_time"] = 10
        config["scheduler"] = MyScheduler

        return config

    def apply_action(self, action: int, ue: UserEquipment) -> None:
        # do not apply update to connections if NOOP_ACTION is selected
        if action == self.NOOP_ACTION or ue not in self.active:
            return

    def reset(self, *, seed=None, options=None):
        obs, info = super().reset(seed=None, options = None)

        # generate new initial positons of UEs
        square_coordinates = [
          (25, 65),
          (25,130),
          (125,65),
          (125,130)
        ]
        for ue, coord in zip(self.users.values(), square_coordinates):
          ue.x, ue.y = coord

        # set BS-UE connections: only during the 1st step
        if(self.time==0):
            bs = self.stations[0]
            self.connections[bs].add(self.users[1])
            self.connections[bs].add(self.users[2])
            bs = self.stations[1]
            self.connections[bs].add(self.users[3])
            self.connections[bs].add(self.users[4])

        return obs, info

    def step(self, actions: Dict[int, int]):
        observation, rewards, terminated, truncated, info = super().step(actions)


        # Set theoretical macimum capacity for each UE
        for bs in self.stations.values():
            conns = self.connections[bs]
            # compute SNR & max. data rate for each connected user equipment
            snrs = [self.channel.snr(bs, ue) for ue in conns]
            # UE's max. data rate achievable when BS schedules all resources to it
            for snr, ue in zip(snrs, conns):
                max_allocation = self.channel.datarate(bs, ue, snr)
                self.users[ue.ue_id].buffer.snr = snr # store the SNR for each user
                self.users[ue.ue_id].buffer.set_theoretical_maximum_capacity(max_allocation)


        # Generate traffic for the Services
        for user in self.users.values():
            user.buffer.generate_traffic()


        # Apply action for each UE
        for user_id, action in actions.items():
            self.users[user_id].buffer.apply_action(action)


        # Send data for each Service
        for (bs, ue), drate in self.datarates.items():
            self.users[ue.ue_id].buffer.send_traffic()
            
        # Calculate the latency for each UE
        for user in self.users.values():
            res = user.buffer.get_latency()
            
        # Calculate the QoE
        for user in self.users.values():
            qoe = user.buffer.get_qoe()

        return observation, rewards, terminated, truncated, info
