from subprocess import call


def speak(say_wa):
    echo_string = "'{0}'".format(say_wa.replace("'", "'\''"))

    call([
        "echo", echo_string, "|",
        "espeak", "-v", "english", "--stdout", "|",
        "aplay"])
