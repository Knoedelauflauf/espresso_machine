from typing import Literal

XENIA_DOMAIN = "espresso_machine"
PLATFORMS = ["select", "sensor", "switch"]
DEFAULT_HOST = "xenia.local"

CONF_POWER_ON_BEHAVIOR = "power_on_behavior"

PowerOnBehavior = Literal["steam_on", "steam_off"]

POWER_ON_BEHAVIOR_STEAM_ON: PowerOnBehavior = "steam_on"
POWER_ON_BEHAVIOR_STEAM_OFF: PowerOnBehavior = "steam_off"

POWER_ON_BEHAVIOR_OPTIONS: list[PowerOnBehavior] = [
    POWER_ON_BEHAVIOR_STEAM_ON,
    POWER_ON_BEHAVIOR_STEAM_OFF,
]

DEFAULT_POWER_ON_BEHAVIOR: PowerOnBehavior = POWER_ON_BEHAVIOR_STEAM_ON
