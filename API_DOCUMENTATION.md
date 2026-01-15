# Xenia Espresso Machine API Documentation

Dokumentation der Xenia Espresso API basierend auf https://www.xenia-espresso.de/api.html

## Base URL

```
http://{host}/api/v2/
```

## GET Endpoints

### `/api/v2/status`

Minimaler Status-Check.

**Response:**
```json
{"MA_STATUS": 0}
```

### `/api/v2/overview`

Umfassende Übersicht aller Echtzeit-Sensordaten.

**Response Parameter:**

| Parameter | Typ | Beschreibung |
|-----------|-----|--------------|
| `MA_STATUS` | uint8 | Maschinen-Status (siehe Enum unten) |
| `MA_EXTRACTIONS` | uint32 | Anzahl der Extraktionen |
| `MA_OPERATING_HOURS` | uint32 | Betriebsstunden |
| `MA_CLOCK` | uint32 | System-Clock |
| `MA_CUR_PWR` | float | Aktuelle Leistungsaufnahme (Ampere) |
| `MA_MAX_PWR` | uint16 | Maximale Ampere |
| `MA_ENERGY_TOTAL_KWH` | float | Gesamtenergieverbrauch in kWh |
| `MA_LAST_EXTRACTION_ML` | string | Letzte Extraktionsmenge |
| `BG_SENS_TEMP_A` | float | Brühgruppen-Temperatur (Sensor) |
| `BG_LEVEL_PW_CONTROL` | uint16 | Brühgruppen PWM-Steuerung |
| `BB_SENS_TEMP_A` | float | Brühkessel-Temperatur (Sensor) |
| `BB_LEVEL_PW_CONTROL` | uint16 | Brühkessel PWM-Steuerung |
| `PU_SENS_PRESS` | float | Pumpendruck (bar) |
| `PU_LEVEL_PW_CONTROL` | uint16 | Pumpen PWM-Steuerung |
| `PU_SET_LEVEL_PW_CONTROL` | uint16 | Pumpen Soll-PWM |
| `SB_SENS_PRESS` | float | Dampfkessel-Druck (bar) |
| `SB_STATUS` | uint8 | Dampfkessel-Status (siehe Enum unten) |

### `/api/v2/overview_single`

Konfigurationswerte und Sollwerte.

**Response Parameter:**

| Parameter | Typ | Beschreibung |
|-----------|-----|--------------|
| `BG_SET_TEMP` | float | Brühgruppen Soll-Temperatur |
| `BB_SET_TEMP` | float | Brühkessel Soll-Temperatur |
| `PU_SET_PRESS` | float | Pumpen Soll-Druck |
| `SB_SET_PRESS` | float | Dampfkessel Soll-Druck |
| `PU_SENS_WATER_TANK_LEVEL` | int | Wassertank-Füllstand |
| `MA_MAC` | string | MAC-Adresse |
| `MA_EXTRACTIONS_START` | int | Extraktionszähler Start |
| `PSP` | int | ? |
| `POP_UP` | int/null | Pop-up Meldung (optional) |

## POST Endpoints

### `/api/v2/machine/control`

Steuert den Maschinenzustand.

**Content-Type:** `application/x-www-form-urlencoded`

**Body:**
```json
{"action": "0"}
```

**Action Values:**

| Wert | Bedeutung |
|------|-----------|
| `0` | OFF - Maschine ausschalten |
| `1` | ON - Maschine einschalten (mit Dampfkessel) |
| `2` | ECO - ECO-Modus aktivieren |
| `3` | SB_OFF - Dampfkessel ausschalten (legacy?) |
| `4` | SB_ON - Dampfkessel einschalten (legacy?) |
| `5` | ON_SB_OFF - Maschine einschalten ohne Dampfkessel |

### `/api/v2/toggle_sb`

Schaltet den Dampfkessel ein/aus.

**Content-Type:** `application/x-www-form-urlencoded`

**Body:**
```json
{"TOGGLE": true}
```
oder
```json
{"TOGGLE": false}
```

### `/api/v2/inc_dec`

Setzt Brühgruppen- und Brühkessel-Temperatur gleichzeitig.

**Content-Type:** `application/x-www-form-urlencoded`

**Body:**
```json
{"BG_SET_TEMP": "93.0", "BB_SET_TEMP": "93.0"}
```

### `/api/v2/inc_dec_bb`

Setzt nur die Brühkessel-Temperatur.

**Content-Type:** `application/x-www-form-urlencoded`

**Body:**
```json
{"BB_SET_TEMP": "93.0"}
```

## Enums

### MachineStatus (MA_STATUS)

| Wert | Status | Beschreibung |
|------|--------|--------------|
| 0 | OFF | Maschine ist aus |
| 1 | ON | Maschine ist an und heizt |
| 2 | ECO | ECO-Modus (Standby, kein Heizen) |
| 3 | BREWING | Aktive Extraktion |
| 4 | DRAINING | Entwässern/Abkühlen |

### SteamBoilerStatus (SB_STATUS)

| Wert | Status |
|------|--------|
| 1 | OFF |
| 2 | ON |

## Nicht dokumentierte Features

Die folgenden Features existieren auf der Maschine, sind aber nicht über die API steuerbar:

- **ECO-Timer**: Zeit bis die Maschine automatisch in den ECO-Modus wechselt
- **Auto-Off Timer**: Automatische Abschaltung
- **Scheduler/Zeitpläne**: Automatisches Ein-/Ausschalten

Diese Einstellungen müssen direkt am Gerät vorgenommen werden.

## Beispiel: Python API-Aufruf

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
