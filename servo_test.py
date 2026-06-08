import RPi.GPIO as GPIO
import time

# Set the GPIO mode to BCM (Broadcom SOC channel names)
GPIO.setmode(GPIO.BCM)

# Define the GPIO pin connected to the servo
servoPIN = 13

# Set the pin as an output
GPIO.setup(servoPIN, GPIO.OUT)

# Create a PWM instance on the servo pin with a frequency of 50Hz (standard for SG90)
pwm = GPIO.PWM(servoPIN, 50)

# Start PWM with a duty cycle of 0 (servo is initially off)
pwm.start(0)

def set_angle(angle):
    """
    Sets the servo to a specific angle.
    Duty cycle calculation for SG90:
    - 2.5% to 12.5% duty cycle corresponds to 0 to 180 degrees
    """
    duty = 2.5 + (10.0 * angle / 180.0)
    # Turn on the pin to allow PWM signal to move the servo
    GPIO.output(servoPIN, True)
    pwm.ChangeDutyCycle(duty)
    time.sleep(0.5) # Wait for the servo to reach the position
    # Turn off the pin to prevent jitter
    GPIO.output(servoPIN, False)
    pwm.ChangeDutyCycle(0)

try:
    print("Testing SG90 Servo on GPIO 13. Press Ctrl+C to stop.")

    while True:
        for i in range(0, 160, 40):
            print(f"Moving to {i}")
            set_angle(i)
            time.sleep(0.5)

        for i in range(160, 0, -40):
            print(f"Moving to {i}")
            set_angle(i)
            time.sleep(0.5)

    # while True:
    #     print("Moving to 0 degrees")
    #     set_angle(0)
    #     time.sleep(1)

    #     print("Moving to 90 degrees")
    #     set_angle(90)
    #     time.sleep(1)

    #     print("Moving to 180 degrees")
    #     set_angle(180)
    #     time.sleep(1)

    #     print("Moving back to 90 degrees")
    #     set_angle(90)
    #     time.sleep(1)

except KeyboardInterrupt:
    print("\nProgram stopped by user")

finally:
    # Clean up the GPIO pins
    pwm.stop()
    GPIO.cleanup()
