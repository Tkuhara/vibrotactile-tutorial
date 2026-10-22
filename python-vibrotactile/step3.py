import numpy as np
import sounddevice as sd
import threading
import time

FREQUENCY = 250
DURATION = 2
AMPLITUDE = 0.5
SAMPLERATE = 44100
DELAY = 0.5

t = np.linspace(0, DURATION, int(SAMPLERATE * DURATION), endpoint=False)
wave = (AMPLITUDE * np.sin(2 * np.pi * FREQUENCY * t)).astype(np.float32)

barrier = threading.Barrier(2)

def play(channel, delay):
    stereo = np.zeros((len(wave), 2), dtype=np.float32)
    stereo[:, channel] = wave
    with sd.OutputStream(samplerate=SAMPLERATE, channels=2) as stream:
        barrier.wait()
        time.sleep(delay)
        stream.write(stereo)

left = threading.Thread(target=play, args=(0, 0))
right = threading.Thread(target=play, args=(1, DELAY))
left.start()
right.start()
left.join()
right.join()
