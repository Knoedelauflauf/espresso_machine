from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import XENIA_DOMAIN
from .coordinator import XeniaConfigEntry, XeniaDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: XeniaConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    coordinator = entry.runtime_data
    async_add_entities([XeniaWaterTankSensor(coordinator)])


class XeniaWaterTankSensor(
    CoordinatorEntity[XeniaDataUpdateCoordinator], BinarySensorEntity
):
    def __init__(self, coordinator: XeniaDataUpdateCoordinator):
        super().__init__(coordinator)
        self._attr_has_entity_name = True
        self._attr_name = "Water Tank Empty"
        self._attr_unique_id = (
            f"{self.coordinator.config_entry.data[CONF_HOST]}_water_tank_empty"
        )
        self._attr_device_class = BinarySensorDeviceClass.PROBLEM
        self._attr_icon = "mdi:water-off"

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
    def is_on(self) -> bool:
        # is_on = True means "problem" (tank empty)
        # Sensor returns 0 when empty, >0 when water present
        return self.coordinator.data.overview_single.pu_sens_water_tank_level == 0
