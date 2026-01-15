from collections.abc import Callable
from dataclasses import dataclass
from typing import Final

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    CONF_HOST,
    EntityCategory,
    UnitOfElectricCurrent,
    UnitOfEnergy,
    UnitOfPressure,
    UnitOfTemperature,
    UnitOfTime,
)
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
class XeniaEntityDescriptionMixinSensor:
    value_fn: Callable[[XeniaCoordinatorData], StateType]


@dataclass(frozen=True)
class XeniaSensorEntityDescription(
    SensorEntityDescription, XeniaEntityDescriptionMixinSensor
):
    entity_category_fn: (
        Callable[[XeniaCoordinatorData], EntityCategory | None] | None
    ) = None


SENSOR_TYPES: Final[tuple[XeniaSensorEntityDescription, ...]] = (
    XeniaSensorEntityDescription(
        key="brew_group_temperature",
        name="Brewgroup Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:thermometer",
        value_fn=lambda data: data.overview.bg_sens_temp_a,
    ),
    XeniaSensorEntityDescription(
        key="brew_boiler_temperature",
        name="Brewboiler Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:thermometer-water",
        value_fn=lambda data: data.overview.bb_sens_temp_a,
    ),
    XeniaSensorEntityDescription(
        key="pump_pressure",
        name="Pump Pressure",
        native_unit_of_measurement=UnitOfPressure.BAR,
        device_class=SensorDeviceClass.PRESSURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:gauge",
        value_fn=lambda data: data.overview.pu_sens_press,
    ),
    XeniaSensorEntityDescription(
        key="steam_boiler_pressure",
        name="Steamboiler Pressure",
        native_unit_of_measurement=UnitOfPressure.BAR,
        device_class=SensorDeviceClass.PRESSURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:gauge-full",
        value_fn=lambda data: data.overview.sb_sens_press,
    ),
    XeniaSensorEntityDescription(
        key="electric_current",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:current-ac",
        value_fn=lambda data: data.overview.ma_cur_pwr,
    ),
    XeniaSensorEntityDescription(
        key="total_energy",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:lightning-bolt",
        value_fn=lambda data: data.overview.ma_energy_total_kwh,
    ),
    XeniaSensorEntityDescription(
        key="extractions",
        name="Extractions",
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:coffee-to-go",
        value_fn=lambda data: data.overview.ma_extractions,
    ),
    XeniaSensorEntityDescription(
        key="operating_hours",
        name="Operating Hours",
        native_unit_of_measurement=UnitOfTime.HOURS,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:clock-outline",
        value_fn=lambda data: data.overview.ma_operating_hours / 60,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: XeniaConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    coordinator = entry.runtime_data
    async_add_entities(
        XeniaSensor(coordinator, description) for description in SENSOR_TYPES
    )


class XeniaSensor(CoordinatorEntity[XeniaDataUpdateCoordinator], SensorEntity):
    def __init__(
        self,
        coordinator: XeniaDataUpdateCoordinator,
        entity_description: XeniaSensorEntityDescription,
    ):
        super().__init__(coordinator)
        self._attr_has_entity_name = True
        self.entity_description = entity_description
        self._attr_unique_id = (
            f"{self.coordinator.config_entry.data[CONF_HOST]}_{entity_description.key}"
        )

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
