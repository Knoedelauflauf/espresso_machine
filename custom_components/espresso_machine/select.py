from homeassistant.components.select import SelectEntity
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    CONF_POWER_ON_BEHAVIOR,
    DEFAULT_POWER_ON_BEHAVIOR,
    POWER_ON_BEHAVIOR_OPTIONS,
    XENIA_DOMAIN,
)
from .coordinator import XeniaConfigEntry, XeniaDataUpdateCoordinator

DEFAULT_NAME = "Power on Behavior Select"


async def async_setup_entry(
    hass: HomeAssistant, entry: XeniaConfigEntry, async_add_entities
):
    coordinator = entry.runtime_data
    async_add_entities([PowerOnBehaviorSelect(coordinator, entry)])


class PowerOnBehaviorSelect(
    CoordinatorEntity[XeniaDataUpdateCoordinator], SelectEntity
):
    _default_name = DEFAULT_NAME
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._entry_id = entry.entry_id
        self._attr_name = "Xenia Power on Behavior"
        self._attr_unique_id = f"{XENIA_DOMAIN}_xenia_power_on_behavior_{self.coordinator.config_entry.data[CONF_HOST]}"
        self._attr_options = POWER_ON_BEHAVIOR_OPTIONS

    @property
    def device_info(self):
        return {
            "identifiers": {
                (XENIA_DOMAIN, self.coordinator.config_entry.data[CONF_HOST])
            },
            "name": "Xenia Espresso Machine",
            "manufacturer": "Xenia Espresso GmbH",
            "model": "DBL",
        }

    @property
    def current_option(self) -> str:
        return self.coordinator.config_entry.options.get(
            CONF_POWER_ON_BEHAVIOR, DEFAULT_POWER_ON_BEHAVIOR
        )

    async def async_select_option(self, option: str) -> None:
        if option not in POWER_ON_BEHAVIOR_OPTIONS:
            return
        new_opts = dict(self.coordinator.config_entry.options)
        new_opts[CONF_POWER_ON_BEHAVIOR] = option
        self.hass.config_entries.async_update_entry(
            self.coordinator.config_entry, options=new_opts
        )
        self.async_write_ha_state()
