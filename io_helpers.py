import subprocess


def speak(say_wa):
    echo_string = "'{0}'".format(say_wa.replace("'", "'\''"))

    echo = subprocess.Popen(['echo', echo_string], stdout=subprocess.PIPE)
    espeak = subprocess.Popen(["espeak", "-v", "english", "--stdout"],
                              stdin=echo.stdout, stdout=subprocess.PIPE)
    echo.stdout.close()
    subprocess.Popen(['aplay'], stdin=espeak.stdout)
    espeak.stdout.close()
