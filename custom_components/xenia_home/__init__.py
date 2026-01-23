"""Xenia Espresso Machine integration."""

import logging

from aiohttp import ClientError

from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import PLATFORMS
from .coordinator import XeniaConfigEntry, XeniaDataUpdateCoordinator
from .xenia import XeniaMachineData

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: XeniaConfigEntry) -> bool:
    """Set up Xenia from a config entry."""
    host = entry.data[CONF_HOST]
    session = async_get_clientsession(hass)
    coordinator = XeniaDataUpdateCoordinator(hass, entry, host, session)
    try:
        coordinator.machine_data = await coordinator.xenia.get_machine()
    except (ClientError, TimeoutError, OSError) as err:
        _LOGGER.debug("Machine info fetch failed: %s", err)
        coordinator.machine_data = XeniaMachineData.from_dict({})
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: XeniaConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
