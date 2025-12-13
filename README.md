# Mangue Baja Telemetry System

__Current Version:__ 2.0 (Professional Refactor) Inspiration: MoTeC i2, McLaren ATLAS

## Project Scope

This project is a bespoke data acquisition and visualization tool developed by me for the Mangue Baja SAE vehicle. It serves as the bridge between our custom embedded systems (ECUs) and race engineers.

## Quick video demonstration

__Be aware that this is using simulated data (sine waves) for showcase__

https://github.com/user-attachments/assets/8abe97bf-6343-4243-8817-2ed7c73c9f20

## Development Roadmap

- Phase 1 (Legacy): Focused on basic connectivity and UI simplicity.

- Phase 2 (Current): A complete architectural overhaul based on peer review from the FSAE engineering community. This version mimics professional workflows found in top-tier motorsport tiers.

## Features

Be aware that this software is still not released, many changes are still to be made.


| Feature | Status | Description |
|:---|:---:|:---|
| **Backend & Core** | | |
| Telemetry broadcast via MQTT | ✅ | High-frequency data stream |
| Data storage with SQLite | ✅ | Local session persistence |
| Data simulation | ✅ | Test without the car using `simulador.py` |
| ENV-based authentication | ✅ | Secure connection management |
| LoRa Integration | ✅ | Long-range wireless telemetry support |
| **InfluxDB Support** | 🚧 | *Requested via feedback* - For high-performance time-series storage |
| **Frontend & Visualization** | | |
| **Dynamic Docking Interface** | ✅ | Draggable/Resizable panels (inspired by MoTeC i2) |
| Real-time GPS Map | ✅ | Live track positioning with Start/Finish line configuration |
| Car Model | ✅ | Visualizes Roll/Pitch in real-time |
| **G-G Diagram** | ✅ | Lateral vs Longitudinal acceleration scatter plot |
| **Strip Charts (Time vs Data)**| ✅ | Standard scrolling telemetry graphs |
| **X-Y Plotting** | 🚧  | Cross-plotting capabilities (e.g., RPM vs Speed) |
| **Time/Distance Toggle** | 🚧  | Switch graph X-Axis between Time and Distance travelled |
| **Analysis Tools (Roadmap)** | | *Features requested by the FSAE community* |
| **Math Channels** | 🚧 | User-defined equations (e.g., `WheelSlip = RPM/Speed`) |
| **Histograms** | 🚧 | Distribution analysis for suspension/damper tuning |
| **Multi-run Overlay** | 🚧 | Compare current live data against previous "Best Lap" logs |
| **CSV/Matlab Export** | 🚧 | Export session data for external analysis |
| iLogger / ECU Debugging | 🚧 | Dedicated interface for hardware flags and raw states |

## Community & Usage

This project is Open Source. Unlike many competition teams that keep their tools closed, I believe in open college engineering. Feel free to fork and star.

Any doubts in using the software, feel free to contact me.

## Next updates (todo list)

- [ ] Implement distance toggle on X axis
    - [ ] Calculate total distance on the backend
        - [ ] total\_distance = total\_distance + haversine(current\_pos, last\_pos)
        - [ ] Send total distance through process\_packet()
    - [ ] Enable toggle on the interface
        - [ ] Move viewModel to Telemetrycontext
        - [ ] Update chartPanel to use the total\_distance
    - [ ] Calculate lap\_distance that resets every time the car crosses the S/F area

- [ ] Add X axis option on the "add graph" button
    - [ ] Add a "select" input to choose X axis
    - [ ] Pass params as xAxisKey to chart\_panel

- [ ] Add primitive math channel
    - [ ] Implement evals on the backend
        - [ ] Implement math\_channels dict to data\_processsing.py or settings.py
        - [ ] Implement calculation logic in data\_processing.py using eval (switch to math lib later)
    - [ ] Add user-defined equations as graphs and numbers to the interface
        - [X] Add custom graphs based on a CHANNELS const
        - [ ] Add custom variables to LIVE DATA panel

- [ ] Create separate panel for bar plots and number plots

- [ ] Research viability of InfluxDB implementation

## Known issues:

- Time/Dist toggle does nothing for now
    - Creating backend solution

- Time plot looks weird (error in processing the timestamp set by the server)
    - Deciding where is best to record the timestamp (ECU vs Server)
