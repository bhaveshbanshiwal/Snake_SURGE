# Hardware Comparison & Bill of Materials (Budget: ₹1,00,000)

With your budget increased to **1 Lakh (₹1,00,000)**, we can upgrade key components for better reliability, higher torque, and smoother control loops, while still keeping the project fully affordable. 

Below is a detailed comparison of the **Baseline** hardware versus the **Better Alternatives** that fit within your new budget.

---

## 1. Core Actuators (Servos) - *Require 12 Units*
The actuators are the most critical part of the torque-controlled snake robot.

| Component Option | Specs & Torque | Approx. Cost (12 Units) | Pros / Cons | Verdict |
| :--- | :--- | :--- | :--- | :--- |
| **[Baseline]** Feetech STS3215 | 3.0 Nm, Potentiometer Encoder | ~₹30,000 (₹2.5k ea) | **Pros:** Very cheap, decent torque.<br>**Cons:** Prone to jitter, lower lifespan under load. | Good for basic prototyping. |
| **[Upgrade]** Feetech STS3032 / STS3246 | 3.0 - 4.5 Nm, Magnetic Encoder | ~₹48,000 (₹4k ea) | **Pros:** 360° magnetic encoders provide *extremely* smooth velocity/position feedback crucial for PID torque control.<br>**Cons:** Slightly more expensive. | **Highly Recommended.** Fits the budget and dramatically improves control quality. |
| **[Premium]** Dynamixel XL430-W250-T | 1.5 Nm, Contactless Absolute | ~₹84,000 (₹7k ea) | **Pros:** Industry standard, incredible Dynamixel SDK support.<br>**Cons:** Lower stall torque (1.5 Nm) than Feetech, takes up most of your budget. | Only if you heavily prioritize software ecosystem over sheer torque. |

*(Note: The originally requested Dynamixel XH540-W270-R costs ~₹30k each, meaning 12 units would cost ₹3.6 Lakhs, which is still out of scope).*

---

## 2. Microcontroller / "Brain"
The controller needs to handle complex Bellows Model math and 50-100Hz PID loops for 12 motors simultaneously.

| Component Option | Specs | Approx. Cost | Pros / Cons | Verdict |
| :--- | :--- | :--- | :--- | :--- |
| **[Baseline]** ESP32 Dev Board | 240MHz, Dual Core | ~₹500 | **Pros:** Cheap, has Bluetooth/WiFi for mobile app.<br>**Cons:** Floating-point math for 12 PID loops might limit control frequency. | Great for starter kit. |
| **[Upgrade]** Teensy 4.1 | 600MHz ARM Cortex-M7 | ~₹3,500 | **Pros:** Blisteringly fast math processing. Flawless high-speed serial comms.<br>**Cons:** No built-in WiFi/Bluetooth. | **Best for Control Loop.** Add an ESP32 alongside it purely for Bluetooth if needed. |
| **[Premium]** Raspberry Pi 4/5 + U2D2 | Full Linux OS | ~₹8,000 | **Pros:** Allows ROS (Robot Operating System) integration, computer vision.<br>**Cons:** Overkill for basic rolling, requires tethering or complex battery setup. | Good for future upgrades, but complex for now. |

---

## 3. Power Supply
Powering 12 servos at stall torque requires serious current (Up to 40A-50A peak at 12V).

| Component Option | Specs | Approx. Cost | Pros / Cons | Verdict |
| :--- | :--- | :--- | :--- | :--- |
| **[Baseline]** Generic 12V 40A SMPS | 480W Generic | ~₹2,000 | **Pros:** Very cheap.<br>**Cons:** Noisy power output, can fail spectacularly under spike loads. | Not recommended for 12 high-torque motors. |
| **[Upgrade]** Mean Well LRS-450-12 | 12V 37.5A Industrial | ~₹5,000 | **Pros:** Industry gold standard for reliability and clean power.<br>**Cons:** Larger footprint. | **Highly Recommended.** Protects your expensive servos from voltage spikes. |
| **[Untethered]** 3S LiPo Battery Setup | 11.1V 5000mAh 50C + Charger | ~₹6,000 | **Pros:** Makes the snake robot completely wireless/untethered.<br>**Cons:** Voltage drops as it discharges (affecting torque), fire risk if mishandled. | Buy this *after* tethered testing is complete. |

---

## 4. Mechanical, Wiring & Miscellaneous
These components ensure the robot doesn't melt its own wires or rip itself apart.

| Component | Baseline Option | Better Alternative | Approx. Cost |
| :--- | :--- | :--- | :--- |
| **Signal Converter** | Generic TTL to RS485 (₹500) | **Waveshare TTL to RS485 Isolated** (Protects microcontroller from motor feedback spikes) | ~₹1,500 |
| **Wiring** | Standard 18 AWG Wire (₹300) | **14 AWG High-Strand Silicone Wire** (Handles 50A without melting, highly flexible for snake joints) | ~₹1,000 |
| **Joint Bearings** | None (Plastic-on-plastic) (₹0) | **F623ZZ Flange Bearings** (Takes the mechanical load off the servo horn, preventing snapped shafts) | ~₹1,500 |
| **Robot Skin** | Corrugated Drain Pipe (₹500) | **Braided Expandable Rubber Sleeving** (Expands as the snake bends, provides excellent ground traction) | ~₹2,000 |

---

## Summary Recommendation for ₹1 Lakh Budget

If you want the **highest quality build** that stays well within ₹1,00,000, we recommend this specific configuration:

1. **Servos:** 12x Feetech STS3032 (Magnetic Encoders) ➔ ~₹48,000
2. **Controller:** Teensy 4.1 + ESP32 (For Bluetooth) ➔ ~₹4,000
3. **Power:** Mean Well LRS-450-12 (Tethered) + Waveshare Isolated TTL ➔ ~₹6,500
4. **Mechanical & Wiring:** 14 AWG Silicone wire, Flange Bearings, Braided Rubber Skin, M2/M3 Screws ➔ ~₹5,000

**Total High-Quality Build Cost: ~₹63,500 INR**

*(This leaves nearly ₹36,500 in your budget for spare servos, a high-capacity LiPo battery setup later, or paying for the university's 3D printing materials).*
