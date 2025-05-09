"""
This Raspberry Pi code was developed by newbiely.com
This Raspberry Pi code is made available for public use without any restriction
For comprehensive instructions and wiring diagrams, please visit:
https://newbiely.com/tutorials/raspberry-pi/raspberry-pi-rotary-encoder
"""


import RPi.GPIO as GPIO
import time

# Pin numbers on Raspberry Pi
CLK_PIN = 7   # GPIO7 connected to the rotary encoder's CLK pin
DT_PIN = 8    # GPIO8 connected to the rotary encoder's DT pin
SW_PIN = 25   # GPIO25 connected to the rotary encoder's SW pin

DIRECTION_CW = 0
DIRECTION_CCW = 1

counter = 0
direction = DIRECTION_CW
CLK_state = 0
prev_CLK_state = 0

button_pressed = False
prev_button_state = GPIO.HIGH

# Configure GPIO pins
GPIO.setmode(GPIO.BCM)
GPIO.setup(CLK_PIN, GPIO.IN)
GPIO.setup(DT_PIN, GPIO.IN)
GPIO.setup(SW_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Read the initial state of the rotary encoder's CLK pin
prev_CLK_state = GPIO.input(CLK_PIN)

try:
    while True:
        # Read the current state of the rotary encoder's CLK pin
        CLK_state = GPIO.input(CLK_PIN)

        # If the state of CLK is changed, then pulse occurred
        # React to only the rising edge (from LOW to HIGH) to avoid double count
        if CLK_state != prev_CLK_state and CLK_state == GPIO.LOW:
            # If the DT state is HIGH, the encoder is rotating in counter-clockwise direction
            # Decrease the counter          
            if GPIO.input(DT_PIN) == GPIO.HIGH:
                counter -= 1
                direction = DIRECTION_CCW
            else:
                # The encoder is rotating in clockwise direction => increase the counter
                counter += 1
                direction = DIRECTION_CW
            
            # time.sleep(0.1)
            print("Rotary Encoder:: direction:", "CLOCKWISE" if direction == DIRECTION_CW else "ANTICLOCKWISE",
                  "- count:", counter)

        # Save last CLK state
        prev_CLK_state = CLK_state

        # State change detection for the button
        button_state = GPIO.input(SW_PIN)
        if button_state != prev_button_state:
            time.sleep(0.1)  # Add a small delay to debounce
            if button_state == GPIO.LOW:
                print("The button is pressed")
                button_pressed = True
            else:
                button_pressed = False

        prev_button_state = button_state

except KeyboardInterrupt:
    GPIO.cleanup()  # Clean up GPIO on program exit
