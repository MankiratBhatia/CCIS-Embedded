# Test Plan and Validation

## 1. Pre-power checks (multimeter)
- [ ] 5 V rail reads about 5.0 V, 3.3 V rail about 3.3 V, all grounds common
- [ ] MQ-135 divider output (node) is below 3.3 V with the sensor powered
- [ ] ACS712 divider output reads about 1.67 V with no load (2.5 V × 2/3)

## 2. Individual sensor tests (Person 1 → Person 2)

| Sensor | Test | Expected | Result |
|---|---|---|---|
| DHT22 | Read in room, then hold warm hand near it | Plausible temp and humidity, values rise | |
| PIR | Wave hand, then stay still for 1 min | OUT goes HIGH on motion, LOW after delay | |
| MQ-135 | Baseline in clean air, then alcohol swab or lighter gas near it | Raw value rises noticeably | |
| ACS712 | No load, then known load | Offset about 2500 mV; current near rated value | |
| Wi-Fi | Serial Monitor | "WiFi connected" | |
| Firebase POST | Serial Monitor | `POST 200` and new entry under `/readings/ccis01` | |
| OLED (optional) | Observe | Values update every 15 s | |
| Relay (optional) | Empty room with load on | Relay switches off after 5 min idle | |

## 3. ACS712 calibration
1. Power up with the load disconnected. The firmware prints `ACS offset = ... mV`.
2. Connect a load of at least 60 W (bulb or heater) through the sensor terminals.
3. Compare the printed current with a clamp meter or the rating (P ÷ 230 V).
4. If the error is consistent, adjust `ACS_MV_PER_A` in the firmware.

## 4. Validation: predicted vs reference energy

Run each load for at least 10 minutes. Reference energy = rated watts × hours ÷ 1000, or a plug-in energy meter reading.

| Load | Rated / meter (W) | CCIS measured avg (W) | Duration (min) | Reference kWh | CCIS kWh | Error (%) |
|---|---|---|---|---|---|---|
| Bulb | | | | | | |
| Fan or iron | | | | | | |
| Load 3 | | | | | | |

`Error % = |CCIS kWh − Reference kWh| / Reference kWh × 100`

## 5. Idle-waste test
1. Turn the load on and stay in the PIR's view for 2 minutes: `occupied = 1`.
2. Leave the room for more than 5 minutes: `idle_waste` should become 1 and the idle kWh should rise.
3. Return: `occupied` goes back to 1.

Record the Serial Monitor output and a dashboard screenshot for the report.

## 6. Cost (for the report)

| Item | Cost (₹) |
|---|---|
| ESP32 DevKit V1 | |
| MQ-135 | |
| ACS712 20 A | |
| DHT22 | |
| HC-SR501 | |
| Misc (breadboard, wires, resistors, cable) | |
| **Total** | |
