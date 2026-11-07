# SurGe Web Dashboard & Pi Deployment Guide

This folder contains the complete Gen 3 and Gen 2.1 web dashboard with 3D motion control, real-time PyBullet simulation, telemetry streaming, multi-user operator leases, and phone control.

## Running Locally

From the project root:
```bash
pip install -r requirements.txt
python web_app.py
```
Or directly from the `website` directory:
```bash
python website/web_app.py
```
Open your browser at `http://localhost:5000/gen3` or `http://localhost:5000/`.

---

## On the Raspberry Pi

Copy the repository or the `website` folder onto the Pi. These steps assume 64-bit Raspberry Pi OS with Python 3 and a laptop that can reach the Pi over the local network.

### 1. Install Dependencies
```bash
sudo apt update
sudo apt install -y python3-venv python3-dev build-essential
python3 -m venv .venv
.venv/bin/python -m pip install -r website/requirements.txt
```

### 2. Start Server
```bash
.venv/bin/python website/web_app.py --host 0.0.0.0 --port 5000
```

Leave the server running. For the physical robot, plug the ESP32 transmitter into the Pi via USB. Choose its Linux serial port in the dashboard (`/dev/ttyUSB0` or `/dev/ttyACM0`). If permission errors occur, run:
```bash
sudo usermod -aG dialout "$USER"
```
Then log out and back in.

## On the Laptop
Enable SSH on the Pi. Open a terminal on your laptop to tunnel the port:
```bash
ssh -N -L 127.0.0.1:5000:127.0.0.1:5000 PI_USER@PI_IP
```
Browse to `http://localhost:5000/gen3` and log in as Shashank, Bhavesh, or Mahima.

* **Main 3D Dashboard:** `http://localhost:5000/gen3`
* **Planar Controller (Gen 2.1):** `http://localhost:5000/`
* **Phone Controller:** `http://localhost:5000/phone`

## 3D Motions (Controller Steering)

In the Simulation workspace:
1. Select **3D Motions · controller steered** from the gait preset list and click **Load preset**.
2. Connect the simulation engine and enable the Simulation controller.
3. Hold **LB**, press **A**, then hold **RT** to move.
4. Left stick (Left/Right) sets travel direction; (Up/Down) raises the head up to 30° or lowers it to the ground.
5. The 3D STEER viewport shows the heading and head pitch in real-time.
