# Snake Robot Starter Kit Manual

Welcome to the Starter Kit for the self-adaptive snake robot project! This manual focuses on testing individual motor movement (continuous rolling) using a popular microcontroller, the **ESP32**. 

The ESP32 is cheap, powerful, and has built-in Bluetooth and WiFi, allowing you to easily control your snake robot using a smartphone app.

---

## 1. Starter Kit Hardware Requirements

To begin testing independent motor rolling, you will need:
1. **ESP32 Development Board (30-pin or 38-pin)**
2. **Serial Bus Servo (1 to 4 units)** (e.g., Feetech STS3215 or Hiwonder LX-16A - verify these fit your budget)
3. **TTL to RS-485/Serial Converter** (Required to let the ESP32 communicate with the serial bus servo)
4. **12V High-Current Power Supply** (To power the servos. Do NOT power servos from the ESP32!)
5. **Breadboard and Jumper Wires**

---

## 2. Software Setup (Arduino IDE)

We will use the Arduino IDE to write and upload ("burn") code to the ESP32.

### Step 2.1: Install Arduino IDE
Download and install the latest Arduino IDE from [arduino.cc/en/software](https://www.arduino.cc/en/software).

### Step 2.2: Add ESP32 Board Support
1. Open Arduino IDE. Go to **File -> Preferences**.
2. In the "Additional Boards Manager URLs" field, paste this URL:
   `https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json`
3. Click **OK**.
4. Go to **Tools -> Board -> Boards Manager...**
5. Search for `esp32` and install the package by **Espressif Systems**.

### Step 2.3: Install Servo Libraries
Depending on which brand of serial bus servo you purchase (Feetech or Hiwonder), you will need their specific Arduino library.
1. Go to **Sketch -> Include Library -> Manage Libraries...**
2. Search for your servo brand (e.g., `SCServo` for Feetech) and install it.

---

## 3. How to Burn Codes (Flashing)

Once your code is ready, you need to "burn" (upload) it to the ESP32 so it can run independently.

1. **Connect:** Plug your ESP32 into your computer using a micro-USB or USB-C cable (make sure it's a data cable, not just for charging).
2. **Select Board:** In Arduino IDE, go to **Tools -> Board -> ESP32 Arduino** and select **"DOIT ESP32 DEVKIT V1"** (or the specific name of your ESP32 board).
3. **Select Port:** Go to **Tools -> Port** and select the COM port that appears when the ESP32 is plugged in.
4. **Compile & Upload:** Click the **Upload** button (the right-pointing arrow at the top left of the IDE). 
   - *Note:* When the console says "Connecting...", you may need to press and hold the **BOOT** button on the ESP32 until the upload starts.
5. **Done!** The code is now permanently stored on the ESP32. It will run automatically whenever the ESP32 is powered on.

---

## 4. Using the Smartphone App (Bluetooth Control)

The starter code provided uses **Bluetooth Serial**. This allows you to connect any generic Bluetooth Terminal app on your phone to send commands to the robot.

1. Download a "Bluetooth Serial Terminal" app from the Google Play Store or Apple App Store.
2. Turn on Bluetooth on your phone and pair it with the device named **"SnakeRobot_BT"**.
3. Open the app, connect to "SnakeRobot_BT".
4. Type `ROLL 50` and hit send. The motor will start rolling at speed 50!
5. Type `STOP` to halt the motor.

---

## 5. CAD & 3D Printed Parts Reference

*Note: The university will provide the 3D printed parts based on the CAD models. Do not worry about printing these yourself.*

You will need to request the following CAD files to be printed:
1. **U-Shaped Servo Housing:** The main body that encapsulates the servo.
2. **Servo Linkage Bracket:** Connects the output shaft of one servo to the back of the next.
3. **Ground-Contact Rollers/Wheels:** The outer cylindrical wheels that mount onto the servos, which will make direct contact with the ground for rolling.
