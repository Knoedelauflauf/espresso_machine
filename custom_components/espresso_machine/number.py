from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Final

from homeassistant.components.number import (
    NumberDeviceClass,
    NumberEntity,
    NumberEntityDescription,
)
from homeassistant.const import CONF_HOST, EntityCategory, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import XENIA_DOMAIN
from .coordinator import (
    XeniaConfigEntry,
    XeniaCoordinatorData,
    XeniaDataUpdateCoordinator,
)


@dataclass(frozen=True)
class XeniaEntityDescriptionMixinNumber:
    value_fn: Callable[[XeniaCoordinatorData], StateType]
    set_fn: Callable[[XeniaDataUpdateCoordinator, float], None]


@dataclass(frozen=True)
class XeniaNumberEntityDescription(
    NumberEntityDescription, XeniaEntityDescriptionMixinNumber
):
    entity_category_fn: (
        Callable[[XeniaCoordinatorData], EntityCategory | None] | None
    ) = None


NUMBER_TYPES: Final[tuple[XeniaNumberEntityDescription, ...]] = (
    XeniaNumberEntityDescription(
        key="brew_group_set_temperature",
        name="Brewgroup Set Temperature",
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        entity_category=EntityCategory.CONFIG,
        value_fn=lambda data: data.overview_single.bg_set_temp,
        set_fn=lambda coordinator, v: coordinator.xenia.set_bg_set_temp(v),
        native_min_value=80.0,
        native_max_value=105.0,
        native_step=0.5,
    ),
    XeniaNumberEntityDescription(
        key="brew_boiler_set_temperature",
        name="Brewboiler Set Temperature",
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        entity_category=EntityCategory.CONFIG,
        value_fn=lambda data: data.overview_single.bb_set_temp,
        set_fn=lambda coordinator, v: coordinator.xenia.set_bb_set_temp(v),
        native_min_value=80.0,
        native_max_value=105.0,
        native_step=0.5,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: XeniaConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    coordinator = entry.runtime_data
    async_add_entities(
        XeniaNumber(coordinator, description) for description in NUMBER_TYPES
    )


class XeniaNumber(CoordinatorEntity[XeniaDataUpdateCoordinator], NumberEntity):
    def __init__(
        self,
        coordinator: XeniaDataUpdateCoordinator,
        entity_description: XeniaNumberEntityDescription,
    ):
        super().__init__(coordinator)
        self._attr_has_entity_name = True
        self.entity_description = entity_description
        self._attr_unique_id = (
            f"{self.coordinator.config_entry.data[CONF_HOST]}_{entity_description.key}"
        )
        self._attr_native_min_value = entity_description.native_min_value
        self._attr_native_max_value = entity_description.native_max_value
        self._attr_native_step = entity_description.native_step

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
    def native_value(self) -> StateType:
        return self.entity_description.value_fn(self.coordinator.data)

    @property
    def entity_category(self) -> EntityCategory | None:
        if self.entity_description.entity_category_fn is not None:
            return self.entity_description.entity_category_fn(self.coordinator.data)
        return super().entity_category

    async def async_set_native_value(self, value: float) -> None:
        try:
            await self.entity_description.set_fn(self.coordinator, float(value))
        finally:
            await self.coordinator.async_request_refresh()
