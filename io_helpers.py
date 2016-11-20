import subprocess
import time
from collections import namedtuple

import RPi.GPIO as GPIO

# For DimmerLED
PWM_FREQUENCY = 100


class Button(object):
    """Convinience class for using RaspberryPi buttons.

     Ex:
        def do_something():
          print("something!")

        button = Button(17, do_something)
        while True:
          button.listen()
    """

    def __init__(self, button_gpio, callback):
        self._button_gpio = button_gpio
        self._callback = callback
        GPIO.setup(self._button_gpio, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def is_pressed(self):
        return not GPIO.input(self._button_gpio)

    def listen(self):
        if self.is_pressed():
            self._callback()


class LED(object):
    """Convinience class for using RaspberryPi LEDs.

     Ex:
        led = LED(7)
        led.off()  # start with it off

        led.on()
        time.sleep(.1)
        led.off()
    """

    def __init__(self, led_gpio):
        self._led_gpio = led_gpio
        GPIO.setup(self._led_gpio, GPIO.OUT)

    def on(self):
        GPIO.output(self._led_gpio, True)

    def off(self):
        GPIO.output(self._led_gpio, False)


# TODO: switch these to use `with`, so we can clean up when we're done
class DimmerLED(object):

    def __init__(self, led_gpio, *args, **kwargs):
        super(DimmerLED).__init__(led_gpio, *args, **kwargs)
        self._pwm = GPIO.PWM(self._led_gpio, PWM_FREQUENCY)
        self._pwm.start(1)

    def on(self):
        self._pwm.ChangeDutyCycle(100)

    def off(self):
        self._pwm.ChangeDutyCycle(0)

    def set_brightness(self, percent):
        self._pwm.ChangeDutyCycle(percent)


def pause():
    time.sleep(.1)

# Used for menu classes.
MenuItem = namedtuple('MenuItem', [
    'highlight_fn',  # When this item is highlighted, what should we do?
    'ok_fn',  # When this item is selected, what should we do?
])


class RotateMenu(object):
    """Creates a menu based on a list of MenuItems that can be
       interacted with two buttons.
       The first button rotates through each item and runs its highlight_fn.
       The second button selects the item and runs its ok_fn.

       Ex:
         menu = RotateMenu(12, 17, [
           MenuItem(foo, bar),
           MenuItem(baz, foobar),
         ]

         while True:
           menu.listen()
    """

    @property
    def _curr_item(self):
        return self._menu[self._curr_i]

    def _select_next_item(self):
        self._curr_i += 1
        if self._curr_i == len(self._menu):
            self._curr_i = 0

    def _ok(self):
        self._curr_item.ok_fn()
        pause()

    def _rotate(self):
        self._select_next_item()
        self._curr_item.highlight_fn()
        pause()

    def __init__(self, rotate_button_id, ok_button_id, menu):
        self._menu = menu[:]
        self._curr_i = 0
        self._rotate_button = Button(rotate_button_id, self._rotate)
        self._ok_button = Button(ok_button_id, self._ok)

    def listen(self):
        self._ok_button.listen()
        self._rotate_button.listen()


def speak(say_wa):
    echo_string = "'{0}'".format(say_wa.replace("'", "'\''"))

    echo = subprocess.Popen(['echo', echo_string], stdout=subprocess.PIPE)
    espeak = subprocess.Popen(["espeak", "-v", "english", "--stdout"],
                              stdin=echo.stdout, stdout=subprocess.PIPE)
    echo.stdout.close()
    subprocess.Popen(['aplay'], stdin=espeak.stdout)
    espeak.stdout.close()
