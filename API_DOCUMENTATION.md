# Xenia Espresso Machine API Documentation

Documentation of the Xenia Espresso API based on  
https://www.xenia-espresso.de/api.html

## Base URL

```
http://{host}/api/v2/
```

## GET Endpoints

### `/api/v2/status`

Minimal status check.

**Response:**
```json
{"MA_STATUS": 0}
```

---

### `/api/v2/overview`

Comprehensive overview of all real-time sensor data.

**Response Parameters:**

| Parameter                 | Type   | Description                          |
| ------------------------- | ------ | ------------------------------------ |
| `MA_STATUS`               | uint8  | Machine status (see enum below)      |
| `MA_EXTRACTIONS`          | uint32 | Number of extractions                |
| `MA_OPERATING_HOURS`      | uint32 | Operating hours                      |
| `MA_CLOCK`                | uint32 | System clock                         |
| `MA_CUR_PWR`              | float  | Current power consumption (amperes)  |
| `MA_MAX_PWR`              | uint16 | Maximum amperes                      |
| `MA_ENERGY_TOTAL_KWH`     | float  | Total energy consumption in kWh      |
| `MA_LAST_EXTRACTION_ML`   | string | Last extraction volume               |
| `BG_SENS_TEMP_A`          | float  | Brew group temperature (sensor)      |
| `BG_LEVEL_PW_CONTROL`     | uint16 | Brew group PWM control               |
| `BB_SENS_TEMP_A`          | float  | Brew boiler temperature (sensor)     |
| `BB_LEVEL_PW_CONTROL`     | uint16 | Brew boiler PWM control              |
| `PU_SENS_PRESS`           | float  | Pump pressure (bar)                  |
| `PU_LEVEL_PW_CONTROL`     | uint16 | Pump PWM control                     |
| `PU_SET_LEVEL_PW_CONTROL` | uint16 | Pump target PWM                      |
| `SB_SENS_PRESS`           | float  | Steam boiler pressure (bar)          |
| `SB_STATUS`               | uint8  | Steam boiler status (see enum below) |

---

### `/api/v2/overview_single`

Configuration values and setpoints.

**Response Parameters:**

| Parameter                  | Type     | Description                    |
| -------------------------- | -------- | ------------------------------ |
| `BG_SET_TEMP`              | float    | Brew group target temperature  |
| `BB_SET_TEMP`              | float    | Brew boiler target temperature |
| `PU_SET_PRESS`             | float    | Pump target pressure           |
| `SB_SET_PRESS`             | float    | Steam boiler target pressure   |
| `PU_SENS_WATER_TANK_LEVEL` | int      | Water tank level               |
| `MA_MAC`                   | string   | MAC address                    |
| `MA_EXTRACTIONS_START`     | int      | Extraction counter start value |
| `PSP`                      | int      | ?                              |
| `POP_UP`                   | int/null | Pop-up message (optional)      |

---

## POST Endpoints

### `/api/v2/machine/control`

Controls the machine state.

**Content-Type:** `application/x-www-form-urlencoded`

**Body:**

```json
{"action": "0"}
```

**Action Values:**

| Value | Meaning                                          |
| ----- | ------------------------------------------------ |
| `0`   | OFF – Turn machine off                           |
| `1`   | ON – Turn machine on (with steam boiler)         |
| `2`   | ECO – Enable ECO mode                            |
| `3`   | SB_OFF – Turn steam boiler off (legacy?)         |
| `4`   | SB_ON – Turn steam boiler on (legacy?)           |
| `5`   | ON_SB_OFF – Turn machine on without steam boiler |

---

### `/api/v2/toggle_sb`

Turns the steam boiler on or off.

**Content-Type:** `application/x-www-form-urlencoded`

**Body:**

```json
{"TOGGLE": true}
```

or

```json
{"TOGGLE": false}
```

---

### `/api/v2/inc_dec`

Sets brew group and brew boiler temperature simultaneously.

**Content-Type:** `application/x-www-form-urlencoded`

**Body:**

```json
{"BG_SET_TEMP": "93.0", "BB_SET_TEMP": "93.0"}
```

---

### `/api/v2/inc_dec_bb`

Sets only the brew boiler temperature.

**Content-Type:** `application/x-www-form-urlencoded`

**Body:**

```json
{"BB_SET_TEMP": "93.0"}
```

---

## Enums

### MachineStatus (`MA_STATUS`)

| Value | Status   | Description                    |
| ----- | -------- | ------------------------------ |
| 0     | OFF      | Machine is off                 |
| 1     | ON       | Machine is on and heating      |
| 2     | ECO      | ECO mode (standby, no heating) |
| 3     | BREWING  | Active extraction              |
| 4     | DRAINING | Draining / cooling down        |

---

### SteamBoilerStatus (`SB_STATUS`)

| Value | Status |
| ----- | ------ |
| 1     | OFF    |
| 2     | ON     |

---

## Undocumented Features

The following features exist on the machine but are not controllable via the API:

* **ECO timer**: Time until the machine automatically switches to ECO mode
* **Auto-off timer**: Automatic shutdown
* **Scheduler / schedules**: Automatic power on/off

These settings must be configured directly on the device.

---

## Example: Python API Call

```python
import aiohttp

async def turn_on_machine(host: str):
    url = f"http://{host}/api/v2/machine/control"
    data = '{"action":"1"}'
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=data, headers=headers) as resp:
            resp.raise_for_status()
```
