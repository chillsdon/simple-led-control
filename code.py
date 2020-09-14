import time
import board
import pulseio
import digitalio
from adafruit_debouncer import Debouncer

pin = digitalio.DigitalInOut(board.D2)
pin.direction = digitalio.Direction.INPUT
pin.pull = digitalio.Pull.UP
switch = Debouncer(pin)

E = pulseio.PWMOut(board.A3, frequency=5000, duty_cycle=0)

led = digitalio.DigitalInOut(board.D13)
led.direction = digitalio.Direction.OUTPUT

# constants
# maxDutyCycle = 59636  # 3V
maxDutyCycle = 62749  # 3.16V
# 0.00x = x milliseconds
fadeInterval = 0.05

slowFadePercentStep = 1
fastFadePercentStep = 5

# variables
curentDutyCycle = 0
mode = 1
maxMode = 5
timestamp = time.monotonic()  # initial value
fade_percent = 0
fade_up = True
led_value = True
percentFadeStep = slowFadePercentStep

def percentageToDutyCycle(percentage):
    return int(percentage * maxDutyCycle / 100)

while True:
    switch.update()

    # if the button is pressed, cycle mode
    if switch.fell:
        print("button pressed")
        # toggle the inbuilt LED to indicate the button was pressed
        led.value = led_value
        led_value = not led_value

        # toggle the mode
        mode = mode + 1

        if mode > maxMode:
            mode = 1

        if mode == 4 or mode == 5:
            fade_percent = 0
            timestamp = time.monotonic()  # resample entering mode

            if mode == 4:
                percentFadeStep = slowFadePercentStep

            if mode == 5:
                percentFadeStep = fastFadePercentStep

    if mode == 1:
        print("mode 1 = on @ 10% brightness")
        curentDutyCycle = percentageToDutyCycle(10)

    if mode == 2:
        print("mode 2 = on at 40% brightness")
        curentDutyCycle = percentageToDutyCycle(40)

    if mode == 3:
        print("mode 3 = on at 100% brightness")
        curentDutyCycle = percentageToDutyCycle(100)

    if mode == 4 or mode == 5:
        print("mode 4 or 5 = fading")
        now = time.monotonic()

        if now - timestamp > fadeInterval:
            print("Fade...")

            if fade_up:
                fade_percent = fade_percent + percentFadeStep

                if fade_percent > 100:
                    fade_percent = 100 - percentFadeStep
                    fade_up = False

            else:
                fade_percent = fade_percent - percentFadeStep

                if fade_percent < 0:
                    fade_percent = percentFadeStep
                    fade_up = True

            curentDutyCycle = percentageToDutyCycle(fade_percent)

            # move the timestamp on
            timestamp = now

    # set the duty cycle no matter what mode you are in
    # but only if it has changed
    if curentDutyCycle != E.duty_cycle:
        E.duty_cycle = curentDutyCycle