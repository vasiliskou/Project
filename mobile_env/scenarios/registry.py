import itertools

import gymnasium

from mobile_env.handlers.central import MComCentralHandler
from mobile_env.handlers.multi_agent import MComMAHandler
from mobile_env.scenarios.large import MComLarge
from mobile_env.scenarios.medium import MComMedium
from mobile_env.scenarios.small import MComSmall

# my imports
from mobile_env.handlers.my_multi_agent import CustomMAHandler
from mobile_env.scenarios.utopia import Utopia


# scenarios = {"small": MComSmall, "medium": MComMedium, "large": MComLarge}
scenarios = {"small": MComSmall, "medium": MComMedium, "large": MComLarge, "utopia": Utopia}

# handlers = {"ma": MComMAHandler, "central": MComCentralHandler}
handlers = {"ma": MComMAHandler, "central": MComCentralHandler, "custom_ma_handler": CustomMAHandler}

for scenario, handler in itertools.product(scenarios, handlers):
    env_name = scenarios[scenario].__name__
    config = {"handler": handlers[handler]}
    gymnasium.envs.register(
        id=f"mobile-{scenario}-{handler}-v0",
        entry_point=f"mobile_env.scenarios.{scenario}:{env_name}",
        kwargs={"config": config},
    )
