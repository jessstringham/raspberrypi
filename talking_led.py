import argparse
import contextlib
import sys
import wave

import numpy as np
import pyaudio

CHUNK = 2048


def light_io(led, np_data):
    # for now, this averages the amplitude for the arbitrary sample.
    # I could make this have a higher resolution, and fill in multiple
    # points in between.
    m = np.mean(np.absolute(np_data))
    # super advanced scale
    a = float(m) / 50
    if a > 100:
        a = 100
    led.set_brightness(a)


@contextlib.contextmanager
def audio_stream(wf):
    p = pyaudio.PyAudio()

    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)

    yield stream

    stream.stop_stream()
    stream.close()
    p.terminate()


def run(filename, chunk, led):
    wf = wave.open(filename, 'rb')

    pyaudio_format = pyaudio.get_format_from_width(wf.getsampwidth())
    if pyaudio_format == pyaudio.paInt16:
        width = np.int16
    else:
        sys.exit("add a mapping from this pyaudio format to width")

    with audio_stream(wf) as stream:
        data = wf.readframes(chunk)
        while data != '':
            stream.write(data)
            light_io(led, np.fromstring(data, dtype=width))
            data = wf.readframes(chunk)


if __name__ == '__main__':
    import io_helpers

    parser = argparse.ArgumentParser(
        description='Turn a wav into glowy lights.')
    parser.add_argument('wav_file')
    parser.add_argument('--led-location', type=int,
                        default=7, help='GPIO.BOARD LED location')
    args = parser.parse_args()

    io_helpers.GPIO.setmode(io_helpers.GPIO.BOARD)
    led = io_helpers.DimmerLED(args.led_location)

    run(args.wav_file, CHUNK, led)
