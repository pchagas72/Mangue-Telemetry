# Mangue Baja Telemetry System

__Current Version:__ 2.0 (Professional Refactor) Inspiration: MoTeC i2, McLaren ATLAS

<video controls width="100%">
    <source src="./assets/2.0/demo.mp4" type="video/mp4">
    Your browser does not support the video tag.
</video>

## Project Scope

This project is a bespoke data acquisition and visualization tool developed by me for the Mangue Baja SAE vehicle. It serves as the bridge between our custom embedded systems (ECUs) and race engineers.

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
| **X-Y Plotting** | ✅ | Cross-plotting capabilities (e.g., RPM vs Speed) |
| **Time/Distance Toggle** | ✅ | Switch graph X-Axis between Time and Distance travelled |
| **Analysis Tools (Roadmap)** | | *Features requested by the FSAE community* |
| **Math Channels** | 🚧 | User-defined equations (e.g., `WheelSlip = RPM/Speed`) |
| **Histograms** | 🚧 | Distribution analysis for suspension/damper tuning |
| **Multi-run Overlay** | 🚧 | Compare current live data against previous "Best Lap" logs |
| **CSV/Matlab Export** | 🚧 | Export session data for external analysis |
| iLogger / ECU Debugging | 🚧 | Dedicated interface for hardware flags and raw states |

## Community & Usage

This project is Open Source. Unlike many competition teams that keep their tools closed, I believe in open college engineering. Feel free to fork and star.

Any doubts in using the software, feel free to contact me.
