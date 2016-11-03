import subprocess

import RPi.GPIO as GPIO


GPIO.setmode(GPIO.BOARD)


class Button(object):

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

    def __init__(self, led_gpio):
        self._led_gpio = led_gpio
        GPIO.setup(self._led_gpio, GPIO.OUT)
        self.off()  # start with it off

    def on(self):
        GPIO.output(self._led_gpio, True)

    def off(self):
        GPIO.output(self._led_gpio, False)


def speak(say_wa):
    echo_string = "'{0}'".format(say_wa.replace("'", "'\''"))

    echo = subprocess.Popen(['echo', echo_string], stdout=subprocess.PIPE)
    espeak = subprocess.Popen(["espeak", "-v", "english", "--stdout"],
                              stdin=echo.stdout, stdout=subprocess.PIPE)
    echo.stdout.close()
    subprocess.Popen(['aplay'], stdin=espeak.stdout)
    espeak.stdout.close()
