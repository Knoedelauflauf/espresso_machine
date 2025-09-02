from dataclasses import dataclass
from enum import IntEnum
import logging

from aiohttp import ClientSession

_LOGGER = logging.getLogger(__name__)


class MachineControl(IntEnum):
    OFF = 0
    ON = 1
    ECO = 2
    SB_OFF = 3
    SB_ON = 4
    ON_SB_OFF = 5

    def __str__(self):
        return self.name


class MachineStatus(IntEnum):
    OFF = 0
    ON = 1
    ECO = 2
    BREWING = 3
    DRAINING = 4
    UNKNOWN = 99

    def __str__(self):
        return self.name


class SteamBoilerStatus(IntEnum):
    OFF = 1
    ON = 2
    UNKNOWN = 99

    def __str__(self):
        return self.name


@dataclass
class XeniaOverviewData:
    ma_extractions: int
    ma_operating_hours: int
    ma_status: MachineStatus
    ma_clock: int
    ma_cur_pwr: float
    ma_max_pwr: int
    ma_energy_total_kwh: float
    bg_sens_temp_a: float
    bg_level_pw_control: int
    pu_sens_press: float
    pu_level_pw_control: int
    pu_set_level_pw_control: int
    sb_sens_press: float
    bb_sens_temp_a: float
    bb_level_pw_control: int
    sb_status: SteamBoilerStatus
    ma_last_extraction_ml: str

    @staticmethod
    def from_dict(data: dict) -> "XeniaOverviewData":
        raw_status = data.get("MA_STATUS", 99)
        try:
            machine_status_enum = MachineStatus(raw_status)
        except ValueError:
            machine_status_enum = MachineStatus.UNKNOWN
        raw_status = data.get("SB_STATUS", 99)
        try:
            sb_status_enum = SteamBoilerStatus(raw_status)
        except ValueError:
            sb_status_enum = SteamBoilerStatus.UNKNOWN
        return XeniaOverviewData(
            ma_extractions=data.get("MA_EXTRACTIONS", 0),
            ma_operating_hours=data.get("MA_OPERATING_HOURS", 0),
            ma_status=machine_status_enum,
            ma_clock=data.get("MA_CLOCK", 0),
            ma_cur_pwr=float(data.get("MA_CUR_PWR", 0.0)),
            ma_max_pwr=data.get("MA_MAX_PWR", 0),
            ma_energy_total_kwh=float(data.get("MA_ENERGY_TOTAL_KWH", 0.0)),
            bg_sens_temp_a=float(data.get("BG_SENS_TEMP_A", 0.0)),
            bg_level_pw_control=data.get("BG_LEVEL_PW_CONTROL", 0),
            pu_sens_press=float(data.get("PU_SENS_PRESS", 0.0)),
            pu_level_pw_control=data.get("PU_LEVEL_PW_CONTROL", 0),
            pu_set_level_pw_control=data.get("PU_SET_LEVEL_PW_CONTROL", 0),
            sb_sens_press=float(data.get("SB_SENS_PRESS", 0.0)),
            bb_sens_temp_a=float(data.get("BB_SENS_TEMP_A", 0.0)),
            bb_level_pw_control=data.get("BB_LEVEL_PW_CONTROL", 0),
            sb_status=sb_status_enum,
            ma_last_extraction_ml=data.get("MA_LAST_EXTRACTION_ML", "0"),
        )


@dataclass
class XeniaOverviewSingleData:
    bg_set_temp: float
    pu_set_press: float
    pu_sens_water_tank_level: int
    sb_set_press: float
    bb_set_temp: float
    psp: int
    ma_mac: str
    ma_extractions_start: int
    pop_up: int | None

    @staticmethod
    def from_dict(data: dict) -> "XeniaOverviewSingleData":
        return XeniaOverviewSingleData(
            bg_set_temp=float(data.get("BG_SET_TEMP", 0.0)),
            pu_set_press=float(data.get("PU_SET_PRESS", 0.0)),
            pu_sens_water_tank_level=int(data.get("PU_SENS_WATER_TANK_LEVEL", 0)),
            sb_set_press=float(data.get("SB_SET_PRESS", 0.0)),
            bb_set_temp=float(data.get("BB_SET_TEMP", 0.0)),
            psp=int(data.get("PSP", 0)),
            ma_mac=data.get("MA_MAC", ""),
            ma_extractions_start=int(data.get("MA_EXTRACTIONS_START", 0)),
            # pop up is optional
            pop_up=data.get("POP_UP"),
        )


class Xenia:
    def __init__(self, host: str, session: ClientSession):
        self._host = host
        self._session = session

    async def device_connected(self) -> bool:
        try:
            json_data = await self._get_overview_raw()
            if "MA_STATUS" in json_data:
                return True
        except Exception as e:
            _LOGGER.info("Connection test failed: %s", e)
            return False
        return False

    async def machine_turn_on(self, sb_on: bool = True):
        if sb_on:
            await self._control_machine(MachineControl.ON)
        else:
            await self._control_machine(MachineControl.ON_SB_OFF)

    async def machine_turn_off(self):
        await self._control_machine(MachineControl.OFF)

    async def sb_turn_on(self):
        await self._toggle_sb(True)

    async def sb_turn_off(self):
        await self._toggle_sb(False)

    async def _get_overview_raw(self) -> dict[str, any]:
        url = f"http://{self._host}/api/v2/overview"
        async with self._session.get(url, timeout=10) as resp:
            resp.raise_for_status()
            return await resp.json()

    async def get_overview(self) -> XeniaOverviewData:
        return XeniaOverviewData.from_dict(await self._get_overview_raw())

    async def get_overview_single(self) -> XeniaOverviewSingleData:
        url = f"http://{self._host}/api/v2/overview_single"
        async with self._session.get(url, timeout=10) as resp:
            resp.raise_for_status()
            return XeniaOverviewSingleData.from_dict(await resp.json())

    async def _control_machine(self, action: int):
        url = f"http://{self._host}/api/v2/machine/control"
        data = f'{{"action":"{int(action)}"}}'
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        async with self._session.post(
            url, data=data, headers=headers, timeout=5
        ) as resp:
            resp.raise_for_status()

    async def _toggle_sb(self, action: bool):
        url = f"http://{self._host}/api/v2/toggle_sb"
        data = f'{{"TOGGLE":{str(action).lower()}}}'
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        async with self._session.post(
            url, data=data, headers=headers, timeout=5
        ) as resp:
            _LOGGER.warning(f"{resp}")
            resp.raise_for_status()
