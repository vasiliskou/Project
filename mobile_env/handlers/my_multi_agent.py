from typing import Dict

import gymnasium
import numpy as np

from mobile_env.handlers.handler import Handler


class CustomMAHandler(Handler):
    features = [
        "connections",
        "snrs",
        "utility",
        "bcast",
        "stations_connected",
    ]

    @classmethod
    def ue_obs_size(cls, env) -> int:
        return sum(env.feature_sizes[ftr] for ftr in cls.features)

    @classmethod
    def action_space(cls, env) -> gymnasium.spaces.Dict:
        # return gymnasium.spaces.Dict(
        #     {
        #         ue.ue_id: gymnasium.spaces.Discrete(env.NUM_STATIONS + 1)
        #         for ue in env.users.values()
        #     }
        # )
        return gymnasium.spaces.Dict(
            {
                ue.ue_id: gymnasium.spaces.Discrete(2)
                for ue in env.users.values()
            }
        )


    @classmethod
    def observation_space(cls, env) -> gymnasium.spaces.Dict:
        # size = cls.ue_obs_size(env)
        # space = {
        #     ue_id: gymnasium.spaces.Box(low=-1, high=1, shape=(size,), dtype=np.float32)
        #     for ue_id in env.users
        # }
        size = 2
        space = {
            ue_id: gymnasium.spaces.Box(low=0.0 , high=100.0, shape=(size,), dtype=np.float32)
            for ue_id in env.users
        }

        return gymnasium.spaces.Dict(space)

    @classmethod
    def reward(cls, env):
        """UE's reward is their utility and the avg. utility of nearby BSs."""
        # # compute average utility of UEs for each BS
        # # set to lower bound if no UEs are connected
        # bs_utilities = env.station_utilities()

        # def ue_utility(ue):
        #     """Aggregates UE's own and nearby BSs' utility."""
        #     # ch eck what BS-UE connections are possible
        #     connectable = env.available_connections(ue)

        #     # utilities are broadcasted, i.e., aggregate utilities of BSs
        #     # that are in range of the UE
        #     ngbr_utility = sum(bs_utilities[bs] for bs in connectable)

        #     # calculate rewards as average weighted by
        #     # the number of each BSs' connections
        #     ngbr_counts = sum(len(env.connections[bs]) for bs in connectable)

        #     return (ngbr_utility + env.utilities[ue]) / (ngbr_counts + 1)

        # rewards = {ue.ue_id: ue_utility(ue) for ue in env.active}
        # return rewards
        
        # Initialize an empty dictionary to store QoE values for each UE
        qoe_values = {}

        # Iterate over each UE and collect its QoE value
        for ue_id, ue in env.users.items():
            qoe = ue.buffer.get_qoe()

            # Ensure that QoE values are in a valid range, e.g., 0 to 5
            assert 0 <= qoe <= 5, "QoE values must be in the valid range (0 to 5)"

            # Add the QoE value to the dictionary
            qoe_values[ue_id] = qoe

        return qoe_values

    @classmethod
    def observation(cls, env) -> Dict[int, np.ndarray]:
        """Select features for MA setting & flatten each UE's features."""

        # # get features for currently active UEs
        # active = set([ue.ue_id for ue in env.active if not env.time_is_up])
        # features = env.features()
        # features = {ue_id: obs for ue_id, obs in features.items() if ue_id in active}

        # # select observations for multi-agent setting from base feature set
        # obs = {
        #     ue_id: [obs_dict[key] for key in cls.features]
        #     for ue_id, obs_dict in features.items()
        # }

        # # flatten each UE's Dict observation to vector representation
        # obs = {
        #     ue_id: np.concatenate([o for o in ue_obs]) for ue_id, ue_obs in obs.items()
        # }
        # return obs

        # Initialize an empty dictionary to store observations
        obs = {}

        # Iterate over each user equipment
        for ue_id, ue in env.users.items():
            # Get the latency for the UE
            latency = ue.buffer.get_latency()
            service_rate = ue.buffer.service_rate

            # Ensure the latency is within the defined range
            latency = np.clip(latency, 0.0, 100.0)
            service_rate = np.clip(service_rate, 0.0, 100.0)

            # Create an observation array for the UE with the correct shape
            ue_observation = np.array([latency, service_rate], dtype=np.float32)

            # Add the observation array to the observations dictionary
            obs[ue_id] = ue_observation

        return obs

    @classmethod
    def action(cls, env, action: Dict[int, int]):
        """Base environment by default expects action dictionary."""
        return action
