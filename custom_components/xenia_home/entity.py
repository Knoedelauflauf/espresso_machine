"""Base entity for Xenia Espresso Machine integration."""

from homeassistant.const import CONF_HOST
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import XENIA_DOMAIN
from .coordinator import XeniaDataUpdateCoordinator


class XeniaEntity(CoordinatorEntity[XeniaDataUpdateCoordinator]):
    """Base entity for Xenia Espresso Machine."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: XeniaDataUpdateCoordinator) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information about this Xenia espresso machine."""
        machine = self.coordinator.machine_data
        fw_version = machine.fw_version()
        esp_fw_version = machine.esp_fw_version()
        if fw_version and esp_fw_version:
            sw_version = f"{fw_version}/{esp_fw_version}"
        return DeviceInfo(
            identifiers={(XENIA_DOMAIN, self.coordinator.config_entry.data[CONF_HOST])},
            name="Xenia Espresso Machine",
            manufacturer="Xenia Espresso GmbH",
            model="DBL",
            sw_version=sw_version,
        )
