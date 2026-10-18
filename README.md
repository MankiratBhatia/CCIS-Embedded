# Cloud-Based Carbon Intelligence System (CCIS)

A low-cost ESP32 sensor node that measures appliance current, air quality, temperature/humidity and room occupancy, streams the data to Firebase, and computes household energy use, carbon emissions and a gamified **Carbon Credit Score** with energy-saving recommendations.

Course project for **BITE401P – Embedded Systems and IoT**.

**Team:** Mankirat Bhatia (24BIT0048) · Nishit Jain (24BIT0068) · Aarav Jain (24BIT0023)

## How it works

```
Sensors  ->  ESP32 (edge)  ->  Wi-Fi / HTTPS  ->  Firebase Realtime DB  ->  Dashboard + ML (cloud)
MQ-135       filtering,        JSON payload       timestamped readings     energy, CO2, score,
ACS712       RMS current,                                                  trend prediction,
DHT22        idle detection                                                recommendations
PIR                                      Relay (optional auto cut-off) <---
```

1. **Sensing layer:** ACS712 (current), MQ-135 (air-quality proxy), DHT22 (temperature, humidity), HC-SR501 PIR (occupancy).
2. **Edge layer (ESP32):** averages samples, computes RMS current and power, tracks time since last motion, flags **idle waste** (appliance drawing power while the room is empty for 5 minutes), and sends a JSON reading every 15 s.
3. **Cloud layer:** Firebase stores timestamped readings. The dashboard (and `cloud/trend_model.py`) integrates energy, converts it to carbon, computes the score and fits a linear regression to project monthly emissions.
4. **Output layer:** web dashboard, optional OLED readout, and an optional relay that cuts off idle loads.

## Repository layout

| Path | Contents |
|---|---|
| `firmware/ccis_firmware/` | ESP32 Arduino sketch (`secrets.example.h` shows the config format) |
| `dashboard/index.html` | Web dashboard (Chart.js), live Firebase mode and demo mode |
| `cloud/` | `trend_model.py` (scikit-learn regression and score), `simulate_data.py` (test data) |
| `hardware/` | Wiring diagram and prototype photos |
| `docs/` | Review report, test plan, validation results |

## Hardware

| Component | Purpose |
|---|---|
| ESP32 DevKit V1 | Processing and Wi-Fi |
| ACS712 20 A | Appliance current (**100 mV/A**) |
| MQ-135 | Air-quality proxy (relative, not calibrated CO₂ ppm) |
| DHT22 | Temperature and humidity |
| HC-SR501 PIR | Occupancy |
| SSD1306 OLED 0.96" (optional) | Local readout |
| 5 V relay module (optional) | Automatic cut-off of idle load |
| 10 kΩ and 20 kΩ resistors | Two voltage dividers for the 5 V analog outputs |

## Wiring

See `hardware/wiring_diagram.svg` for the full diagram.

| Sensor pin | ESP32 pin | Notes |
|---|---|---|
| DHT22 DATA | GPIO4 | 3.3 V supply, 10 kΩ pull-up if bare sensor |
| PIR OUT | GPIO27 | PIR powered from 5 V (VIN), output is 3.3 V logic |
| MQ-135 AO | GPIO34 | 5 V supply, **through 10k/20k divider** |
| ACS712 OUT | GPIO35 | 5 V supply, **through 10k/20k divider** |
| OLED SDA / SCL | GPIO21 / GPIO22 | 3.3 V supply, address 0x3C |
| Relay IN | GPIO26 | 5 V supply, active-LOW on most modules |

Divider: `sensor OUT -- 10k -- node -- 20k -- GND`, node goes to the ESP32 ADC pin (output = 2/3 of input). Only ADC1 pins are used because ADC2 does not work with Wi-Fi on.

> **Safety:** never place mains wiring on the breadboard. Connect appliances only through the ACS712 screw terminals with insulated wiring, or demonstrate with a low-voltage DC load.

## Setup

### 1. Firebase
1. Create a project at console.firebase.google.com and add a **Realtime Database** (test mode for the demo).
2. Copy the database URL, for example `https://your-project-default-rtdb.firebaseio.com`.
3. Rules for the demo (tighten these for real deployment):
   ```json
   { "rules": { "readings": { ".read": true, ".write": true } } }
   ```

### 2. Firmware
1. Install the Arduino IDE and add the ESP32 board package. Select **ESP32 Dev Module**.
2. Install libraries: *DHT sensor library* and *Adafruit Unified Sensor* (plus *Adafruit SSD1306* and *Adafruit GFX* if you set `USE_OLED 1`).
3. In `firmware/ccis_firmware/`, copy `secrets.example.h` to `secrets.h` and enter your Wi-Fi name, password and Firebase URL. `secrets.h` is git-ignored.
4. Keep the load **disconnected** while the board starts: it calibrates the ACS712 zero point and waits 30 s for the PIR to warm up.
5. Upload and open the Serial Monitor at 115200 baud.

### 3. Dashboard
Open `dashboard/index.html` in a browser. Paste the Firebase URL, untick **Demo mode** and click **Apply**. Demo mode shows simulated data with no hardware or database.

### 4. Cloud model (optional)
```bash
pip install -r cloud/requirements.txt
python cloud/simulate_data.py --url <FIREBASE_URL> --count 120     # test data
python cloud/trend_model.py   --url <FIREBASE_URL> --ef 0.71 --baseline 100
```

## Calculations

- Power: `P = Irms × 230 V × PF` (resistive load assumed, PF = 1)
- Energy: `E (kWh) = Σ P × Δt / 3.6e6`
- Carbon: `CO₂ (kg) = E × grid factor` (default 0.71 kg/kWh, editable; use the current CEA value)
- Idle waste: energy used while an appliance draws power and no motion has been seen for 5 minutes
- **Carbon Credit Score** (0–100): `100 − 60 × idle_ratio − 25 × overload − 15 × air_penalty`
  - `idle_ratio` = idle kWh / total kWh
  - `overload` = (average W − baseline W) / baseline W, limited to 0–1
  - `air_penalty` = rise of the gas reading above its baseline, scaled so +50% counts as full penalty
- Monthly prediction: linear regression of cumulative kWh against time, projected to 30 days

## Limitations

- The MQ-135 gives a relative air-quality trend, not calibrated CO₂ ppm.
- ACS712 noise is about ±0.1–0.2 A, so very small standby loads cannot be measured.
- Voltage is assumed to be 230 V with PF = 1, so real power can differ for non-resistive loads.
- Measurement covers one appliance circuit, not a whole household.
- The Firebase rules and `setInsecure()` TLS in the firmware are for demonstration only.

## Team roles

| Role | Owner |
|---|---|
| Hardware assembly | |
| ESP32 firmware and testing | |
| Cloud, calculations and dashboard | |

## License
MIT
