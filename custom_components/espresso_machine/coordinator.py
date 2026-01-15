import asyncio
from dataclasses import dataclass
from datetime import timedelta
import logging

from aiohttp import ClientSession

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .xenia import Xenia, XeniaOverviewData, XeniaOverviewSingleData

_LOGGER = logging.getLogger(__name__)

type XeniaConfigEntry = ConfigEntry[XeniaDataUpdateCoordinator]


@dataclass
class XeniaCoordinatorData:
    """Data Type of XeniaDataUpdateCoordinator's data."""

    overview: XeniaOverviewData
    overview_single: XeniaOverviewSingleData


class XeniaDataUpdateCoordinator(DataUpdateCoordinator[XeniaCoordinatorData]):
    """Xenia device data update coordinator."""

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        host: str,
        session: ClientSession,
    ) -> None:
        """Initialize the Xenia device coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=config_entry.entry_id,
            update_interval=timedelta(seconds=30),
            config_entry=config_entry,
        )
        self.data = XeniaCoordinatorData(
            XeniaOverviewData.from_dict({}), XeniaOverviewSingleData.from_dict({})
        )
        self.xenia = Xenia(host, session)

    async def _async_update_data(self) -> XeniaCoordinatorData:
        try:
            overview = await self.xenia.get_overview()
            await asyncio.sleep(0.25)
            overview_single = await self.xenia.get_overview_single()

            if overview.ma_status == MachineStatus.BREWING:
                self.update_interval = timedelta(seconds=1)
            elif overview.ma_status in [MachineStatus.ON, MachineStatus.DRAINING]:
                self.update_interval = timedelta(seconds=5)
            else:
                self.update_interval = timedelta(seconds=30)

            return XeniaCoordinatorData(overview, overview_single)
        except Exception as err:
            raise UpdateFailed(f"Xenia fetch failed: {err}") from err
