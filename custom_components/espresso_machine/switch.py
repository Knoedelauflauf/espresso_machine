import asyncio

from homeassistant.components.switch import SwitchEntity
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    CONF_POWER_ON_BEHAVIOR,
    DEFAULT_POWER_ON_BEHAVIOR,
    XENIA_DOMAIN,
    PowerOnBehavior,
)
from .coordinator import XeniaConfigEntry, XeniaDataUpdateCoordinator
from .xenia import MachineStatus, SteamBoilerStatus


async def async_setup_entry(
    hass: HomeAssistant, entry: XeniaConfigEntry, async_add_entities
):
    coordinator = entry.runtime_data

    power_switch = XeniaPowerSwitch(coordinator, entry)
    steam_boiler_switch = XeniaSteamBoilerSwitch(coordinator, entry)

    async_add_entities([power_switch, steam_boiler_switch], True)


class XeniaPowerSwitch(CoordinatorEntity[XeniaDataUpdateCoordinator], SwitchEntity):
    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._entry_id = entry.entry_id
        self._attr_name = "Xenia Power"
        self._attr_unique_id = f"{XENIA_DOMAIN}_xenia_power_{self.coordinator.config_entry.data[CONF_HOST]}"

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
    def is_on(self):
        ma_status = self.coordinator.data.overview.ma_status
        return ma_status in [
            MachineStatus.ON,
            MachineStatus.BREWING,
            MachineStatus.DRAINING,
        ]

    async def async_turn_on(self, **kwargs):
        behavior = self.coordinator.config_entry.options.get(
            CONF_POWER_ON_BEHAVIOR, DEFAULT_POWER_ON_BEHAVIOR
        )
        if behavior == PowerOnBehavior.STEAM_ON:
            await self.coordinator.xenia.machine_turn_on()
        elif behavior == PowerOnBehavior.STEAM_OFF:
            await self.coordinator.xenia.machine_turn_on(False)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        await self.coordinator.xenia.machine_turn_off()
        await self.coordinator.async_request_refresh()


class XeniaSteamBoilerSwitch(
    CoordinatorEntity[XeniaDataUpdateCoordinator], SwitchEntity
):
    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._entry_id = entry.entry_id
        self._attr_name = "Steam Boiler Power"
        self._attr_unique_id = f"{XENIA_DOMAIN}_steam_boiler_power_{self.coordinator.config_entry.data[CONF_HOST]}"

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
    def available(self) -> bool:
        return self.coordinator.data.overview.ma_status in [
            MachineStatus.ON,
            MachineStatus.BREWING,
            MachineStatus.DRAINING,
        ]

    @property
    def is_on(self):
        return self.coordinator.data.overview.sb_status == SteamBoilerStatus.ON

    async def async_turn_on(self, **kwargs):
        await self.coordinator.xenia.sb_turn_on()
        await asyncio.sleep(1)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        await self.coordinator.xenia.sb_turn_off()
        await asyncio.sleep(1)
        await self.coordinator.async_request_refresh()
