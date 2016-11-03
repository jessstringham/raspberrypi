from subprocess import call


def speak(say_wa):
    call([
        "echo", say_wa, "|",
        "espeak", "-v", "english", "--stdout", "|",
        "aplay"])
