# Wireless Flashing (OTA) Guide

The Snake SURGE project supports **Over-The-Air (OTA) updates**, allowing you to flash new code to the ESP32 receiver wirelessly without plugging in a USB cable. This is especially useful for preventing USB port crashes caused by power spikes from the servos.

## Wi-Fi Credentials
The ESP32 broadcasts its own Wi-Fi Hotspot (Access Point) specifically for this purpose. The credentials are defined in `src/esp32_st3215/secrets.h`:

- **Wi-Fi Network Name (SSID):** `Snake_SURGE_OTA`
- **Wi-Fi Password:** `snake12345`

## Initial Setup (One-Time USB Flash)
To enable wireless flashing, the ESP32 must have the OTA capability flashed onto it at least once via USB:
1. Unplug the servos from the ESP32 to prevent power spikes.
2. Plug the ESP32 into your computer via a data USB cable.
3. Open `esp32_st3215.ino` in the Arduino IDE.
4. Select your standard COM port and click **Upload**.
5. Once uploaded, unplug the USB and reconnect the servos. Power the system using the battery.

## Flashing Wirelessly (Every Time After)
Once the initial setup is complete, you can flash the ESP32 wirelessly at any time:
1. Turn on the Snake SURGE battery to power the ESP32.
2. On your computer, click your Wi-Fi icon and connect to the **`Snake_SURGE_OTA`** network using the password **`snake12345`**.
3. Open the Arduino IDE.
4. Go to **Tools -> Port**. Underneath the regular COM ports, you will see a new section called **Network Ports**.
5. Select the port named **`Snake-ESP32 at [IP Address]`**.
6. Click **Upload**.

The Arduino IDE will compile and send the new firmware wirelessly through the air directly to the ESP32! You can leave all servos and batteries plugged in while doing this.
