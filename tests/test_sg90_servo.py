import RPi.GPIO as GPIO
import time


GPIO.setmode(GPIO.BCM)


servoPIN = 13

GPIO.setup(servoPIN, GPIO.OUT)


pwm = GPIO.PWM(servoPIN, 50)


pwm.start(0)

def set_angle(angle):
    duty = 2.5 + (10.0 * angle / 180.0)

    GPIO.output(servoPIN, True)
    pwm.ChangeDutyCycle(duty)
    time.sleep(0.5) 

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

except KeyboardInterrupt:
    print("\nProgram stopped by user")

finally:
    pwm.stop()
    GPIO.cleanup()
