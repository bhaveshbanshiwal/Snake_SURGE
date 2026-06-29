# ESP32 and SG90 Servos Wiring Guide

This guide details how to wire your 10 SG90 servos, the ESP32 (38-pin), and the Ambrane 20000mAh Power Bank using a breadboard.

> [!WARNING]
> **DO NOT** power the servos directly from the ESP32's 5V/VIN pins. The power draw of 10 servos will instantly fry the ESP32.
> **DO NOT** use the 12V adapters for the SG90 servos. They run on a strict maximum of 6V.

## 1. Prepare the Power Bank Cable
1. Take a spare standard USB Type-A cable.
2. Cut the connector off the non-USB end (the side that would normally plug into a phone).
3. Strip the outer insulation back to reveal the internal wires.
4. Cut away the Green and White data wires.
5. Strip the tips of the **Red (5V Positive)** and **Black (Ground)** wires.

## 2. Powering the Breadboard
1. Plug the USB-A end into your **Ambrane 22.5W Power Bank**.
2. Connect the bare **Red wire** to the **Red (+) Power Rail** on your breadboard.
3. Connect the bare **Black wire** to the **Blue/Black (-) Ground Rail** on your breadboard.

## 3. Powering the ESP32
1. Power the ESP32 by connecting it to your PC via its own micro-USB/USB-C cable. 
   *(This provides power to the ESP32 and allows serial communication from `app.py`).*
2. > [!IMPORTANT]
   > **Common Ground (Crucial Step):** Run a jumper wire from any **GND** pin on the ESP32 to the **Blue/Black (-) Ground Rail** on the breadboard. Without this, the PWM signals will not work, and the servos will twitch uncontrollably.

## 4. Connecting the Servos
For all 10 SG90 Servos, connect them as follows:

| Servo Wire Color | Connection |
| :--- | :--- |
| **Red** (VCC) | **Red (+)** Power Rail on Breadboard |
| **Brown/Black** (GND) | **Blue/Black (-)** Ground Rail on Breadboard |
| **Yellow/Orange** (Signal) | ESP32 GPIO Pins (See mapping below) |

### ESP32 GPIO Mapping
The firmware (`firmware.ino`) maps the 10 servos (Motor 1 through 10) to the following ESP32 GPIO pins:

* Motor 1: GPIO 13
* Motor 2: GPIO 14
* Motor 3: GPIO 15
* Motor 4: GPIO 16
* Motor 5: GPIO 17
* Motor 6: GPIO 18
* Motor 7: GPIO 19
* Motor 8: GPIO 21
* Motor 9: GPIO 22
* Motor 10: GPIO 23

## Usage
1. Flash the `firmware/firmware.ino` code to your ESP32 using the Arduino IDE.
2. Ensure the Ambrane power bank is turned on (you may need to press the side button).
3. Update your `app.py` or main entry point to use `src.esp32_sg90.esp32_interface.DynamixelInterface` instead of the original `src.dynamixel_interface.DynamixelInterface`.
4. Run your python script!
