# Mangue Baja Team Telemetry System

[Leia em Português](./README_PT.md)

This repository was created by me for the Mangue Baja team, of which I am proudly a member.

Efficient and elegant code is very important, so feel free to explore the source code.  

If you are from another team, you are welcome to use it according to the license (I will know!).  

Don’t forget to leave a star, thank you!  

---

## Why Things Are the Way They Are

### Backend in Python

The backend (server) in Python has its pros and cons. At first, I considered using C, Go, or Rust. However, Python proved more useful—not only due to its simpler syntax, which makes the code more understandable for the whole team, but also because of the large number of libraries related to connectivity.  

With Python, I was able to easily implement MQTT, WebSocket, API routing, and more. Considering this, and given the performance offered by FastAPI, I chose Python for now.  

That said, I would eventually like to move the backend to C or Rust.  

### Frontend in React-TS

The frontend in React-TS is very useful since it provides a development environment with a wide variety of React libraries and the speed and type safety of TypeScript.  

Using plain JavaScript, it wasn’t possible to render more than 20 data points per second on the charts. Now, with React, the interface smoothly renders all the telemetry data we need, without noticeable latency.  

### Starter

The "starter" script wasn’t an option—it was a necessity for the team.  

If a non-technical member needs to use the interface, running a shell script is nearly impossible (especially since most people use Windows). Asking them to install prerequisites, start the backend, and then launch the interface from the terminal is simply too much.  

The starter saves time and makes the system accessible to everyone—not just members with electronics or programming knowledge.  

---

## Features / TODO

### Starter
- Simple installer and launcher [X]  
- Turn the starter into an app hub [ ]  
- Complete documentation [ ]  

### Backend (server)
- Telemetry broadcast via MQTT [X]  
- Data storage with SQLite [X]  
- Data simulation for testing [X]  
- ENV-based authentication [X]  
- Telemetry broadcast via LoRa [ ]  
- Replay of past sessions [ ]  
- Debug and ECU "box" interface [ ]  
- Apply filters from iLogger [ ]  
- Build executable [ ]  

### Frontend (interface)
- Data reception and processing [X]  
- Real-time map [X]  
- Real-time car model [X]  
- Real-time serial analysis [X]  
- Display of temperatures, speed, RPM, accelerations, GPS position, and angle [X]  
- Battery status [X]  
- Graphs for speed, RPM, temperatures, and accelerations [X]  
- Replay interface [ ]  
- Predictive failure neural network [ ]  
- Debug and ECU "box" interface [ ]  
- Data visualization page for iLogger [ ]  
- Build executable [ ]  

---

## How to Use

### Technologies
- Python 3.11+  
- FastAPI + Uvicorn  
- MQTT (aiomqtt / paho-mqtt)  
- SQLite  
- React + Vite (frontend)  

---

#### Project Structure
```
.
├── LICENSE
├── README.md
├── interface/        # Frontend (React + Vite + TypeScript)
├── server/           # Backend (Python + FastAPI + MQTT)
```

---

#### Backend (server)

**1. Create and activate a virtual environment**

```bash
cd server
python3 -m venv venv
source venv/bin/activate   # Linux/macOS
venv\Scriptsctivate      # Windows
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Configure environment variables**  
Create a `.env` file based on `credentials.env`, containing:

```
HOSTNAME=broker.example.com
PORT=1883
USERNAME=user
PASSWORD=pass
```

**4. Run the server**
```bash
python3 run.py
```

Make sure to adjust the code for the CAN package of your car.  

_Read the code!_  

---

#### Frontend (interface)

**1. Install dependencies**
```bash
cd interface
npm install
```

**2. Make necessary adjustments**  
If using a different CAN package/protocol, modify:  
`./interface/src/hooks/useTelemetry.ts`  
`./interface/src/pages/Dashboard.ts`  
(and others if needed).  

**3. Run the application**
```bash
npm run dev
```

The interface will be available at:  
👉 [http://localhost:5173](http://localhost:5173)  

---

## Reminders

Thank you for using our software! Please remember to always respect the license.  
