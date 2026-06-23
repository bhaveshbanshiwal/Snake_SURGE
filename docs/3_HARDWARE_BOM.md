# Hardware Bill of Materials (Budget: ₹1,00,000)

This document contains the finalized hardware required to build the 10-motor **SURGE-SNAKE** using the Dynamixel ecosystem. 

With a budget of **1 Lakh (₹1,00,000)** and standardizing on the **Dynamixel XL330-M288** motors, the project comes in significantly under budget, leaving plenty of room for spares, future sensor upgrades, and high-quality mechanical components.

---

## 1. Core Actuators (Servos) - *Require 10 Units*

| Component | Specs & Torque | Approx. Cost (10 Units) | Role in Robot |
| :--- | :--- | :--- | :--- |
| **Dynamixel XL330-M288-T** | 0.5 Nm, 5V, Contactless Absolute Encoder | ~₹30,000 (₹3k ea) | The core joints of the snake. Provides extremely precise position, velocity, and current (load) feedback crucial for obstacle avoidance. |
| **Spare Motors** | Same as above | ~₹6,000 (2 extra) | Highly recommended to buy 2 spares in case of gear stripping during extreme physical testing. |

---

## 2. Computing Brain & Interface

The Dynamixel motors require a dedicated USB interface to talk to your computer or Raspberry Pi.

| Component | Specs | Approx. Cost | Role in Robot |
| :--- | :--- | :--- | :--- |
| **Robotis U2D2** | USB to TTL Converter | ~₹4,500 | Plugs into your PC/Pi and outputs the 3-pin TTL data signal for the Dynamixel motors. |
| **Robotis U2D2 Power Hub Board (PHB)** | Power Injector | ~₹1,500 | Mounts to the U2D2. Combines the data signal with raw 5V power so the motors don't fry your USB port. |
| **Raspberry Pi 4 (Optional)** | 4GB RAM, Linux OS | ~₹5,500 | If you want the snake untethered from your laptop, the Pi will run the `main.py` Python code onboard. |

---

## 3. Power Supply

The **XL330-M288** motors require **5 Volts** (not 12V!). Powering 10 motors at stall torque requires roughly 10 Amps to 15 Amps of current.

| Component Option | Specs | Approx. Cost | Pros / Cons |
| :--- | :--- | :--- | :--- |
| **Mean Well LRS-100-5 (Tethered)** | 5V, 20A Industrial SMPS | ~₹2,000 | **Pros:** Extremely reliable, clean power for testing on a desk.<br>**Cons:** Keeps the snake tethered to the wall. |
| **2S LiPo Battery + 5V UBEC (Untethered)** | 7.4V LiPo + 10A 5V Step-Down | ~₹3,500 | **Pros:** Makes the snake fully wireless.<br>**Cons:** Requires careful voltage monitoring and a fire-safe charger. |

---

## 4. Wiring & Mechanical Setup

| Component | Specs | Approx. Cost |
| :--- | :--- | :--- |
| **Dynamixel X3P Cables** | 100mm to 150mm lengths (Pack of 10) | ~₹1,500 | Daisy-chains the data and power from one motor to the next. |
| **F623ZZ Flange Bearings** | For opposite side of servo horn | ~₹1,000 | Takes the mechanical load off the servo horn, preventing snapped shafts. |
| **Braided Expandable Sleeving** | Rubberized mesh tube | ~₹2,000 | Acts as the "skin" of the snake. Expands as it bends and provides traction against the floor. |
| **M2 & M2.5 Machine Screws** | Assorted Kit | ~₹500 | For mounting the 3D printed brackets to the Dynamixels. |

---

## Summary Recommendation 

**Total Estimated Cost: ~₹52,500 INR** (out of ₹1,00,000 budget)

Standardizing on the **Dynamixel XL330-M288** is highly efficient. It operates at 5V, saving weight on batteries, and integrates perfectly with the official Robotis `dynamixel_sdk`. The Python code provided in this repository is designed specifically for this exact hardware list.
