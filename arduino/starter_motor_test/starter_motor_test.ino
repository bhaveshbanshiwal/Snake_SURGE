#include "BluetoothSerial.h"
// NOTE: You will need to include your specific Servo Library here.
// For example, if using Feetech: #include <SCServo.h>

#if !defined(CONFIG_BT_ENABLED) || !defined(CONFIG_BLUEDROID_ENABLED)
#error Bluetooth is not enabled! Please run `make menuconfig` to and enable it
#endif

// Initialize Bluetooth Serial
BluetoothSerial SerialBT;

// --- Hardware Pins ---
// ESP32 Hardware Serial 2 pins (used to communicate with the Servo TTL adapter)
#define RXD2 16
#define TXD2 17

// --- Motor Settings ---
int currentSpeed = 0;
int motorID = 1; // Default ID of the first servo

void setup() {
  // Initialize Serial Monitor for debugging via USB
  Serial.begin(115200);
  
  // Initialize Bluetooth Serial
  SerialBT.begin("SnakeRobot_BT"); // This is the name you will see on your phone!
  Serial.println("Bluetooth Started! Ready to pair.");

  // Initialize Hardware Serial 2 for the Servo communication
  Serial2.begin(1000000, SERIAL_8N1, RXD2, TXD2);
  
  // Initialize Servo Library here (e.g., Feetech, Dynamixel, Hiwonder)
  // sms_sts.pSerial = &Serial2;
  // delay(1000);
  
  Serial.println("Starter Kit Initialized. Send commands via Bluetooth App.");
  Serial.println("Commands:");
  Serial.println("  ROLL <speed>  (e.g., ROLL 100)");
  Serial.println("  STOP");
}

void loop() {
  // Check if we received any commands from the Bluetooth App
  if (SerialBT.available()) {
    String command = SerialBT.readStringUntil('\n');
    command.trim(); // Remove whitespace/newlines

    if (command.startsWith("ROLL")) {
      // Extract the speed value
      String speedStr = command.substring(5);
      currentSpeed = speedStr.toInt();
      
      Serial.print("Command received: ROLL at speed ");
      Serial.println(currentSpeed);
      SerialBT.print("Rolling at speed: ");
      SerialBT.println(currentSpeed);
      
      // --- INSERT SERVO COMMAND HERE ---
      // Command the servo to spin continuously (Wheel Mode)
      // Example for Feetech:
      // sms_sts.WriteSpe(motorID, currentSpeed, 0); // speed, acceleration
      
    } 
    else if (command == "STOP") {
      currentSpeed = 0;
      Serial.println("Command received: STOP");
      SerialBT.println("Motor Stopped.");
      
      // --- INSERT SERVO COMMAND HERE ---
      // Stop the servo
      // Example for Feetech:
      // sms_sts.WriteSpe(motorID, 0, 0);
      
    } 
    else {
      SerialBT.println("Unknown command. Use: ROLL <speed> or STOP");
    }
  }

  // To make the motor motion robust, you could optionally read feedback here
  // For example, read Load (Torque) and prevent it from stalling
  /*
  int load = readServoLoad(motorID);
  if (load > MAX_SAFE_LOAD) {
     SerialBT.println("WARNING: Overload detected! Stopping.");
     // stop motor...
  }
  */
  
  delay(10); // Small delay to prevent watchdog reset
}
