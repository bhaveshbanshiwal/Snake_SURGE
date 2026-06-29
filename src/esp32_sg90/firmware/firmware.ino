#include <ESP32Servo.h>

// Array of 10 servos
Servo servos[10];

// The GPIO pins chosen for the 10 servos on a standard 38-pin ESP32.
// These pins support PWM output.
const int servoPins[10] = {13, 14, 15, 16, 17, 18, 19, 21, 22, 23};

void setup() {
  Serial.begin(115200);
  
  // Attach all 10 servos and initialize to 90 degrees (1500us)
  for (int i = 0; i < 10; i++) {
    // Standard min/max pulse width for SG90 is approx 500us to 2500us
    servos[i].attach(servoPins[i], 500, 2500);
    servos[i].writeMicroseconds(1500);
  }
}

void loop() {
  // Check if data is available on the Serial port
  if (Serial.available() > 0) {
    // Read the incoming command until a newline character
    String command = Serial.readStringUntil('\n');
    command.trim(); // Remove whitespace/CRLF
    
    // Parse the command (format expected: "motor_id:pulse_width")
    int colonIndex = command.indexOf(':');
    if (colonIndex > 0) {
      int motorId = command.substring(0, colonIndex).toInt();
      int pulseWidth = command.substring(colonIndex + 1).toInt();
      
      // Motor IDs are 1-indexed (1 to 10) in the Python script
      int arrayIndex = motorId - 1;
      
      if (arrayIndex >= 0 && arrayIndex < 10) {
        // Clamp pulse width to safe limits for SG90 (0 to 180 degrees)
        if (pulseWidth < 500) pulseWidth = 500;
        if (pulseWidth > 2500) pulseWidth = 2500;
        
        // Write the position to the servo
        servos[arrayIndex].writeMicroseconds(pulseWidth);
      }
    }
  }
}
