import numpy as np
import sounddevice as sd
import threading

FREQUENCY = 250
DURATION = 2
AMPLITUDE = 0.5
SAMPLERATE = 44100

t = np.linspace(0, DURATION, int(SAMPLERATE * DURATION), endpoint=False)
wave = (AMPLITUDE * np.sin(2 * np.pi * FREQUENCY * t)).astype(np.float32)

def play(channel):
    stereo = np.zeros((len(wave), 2), dtype=np.float32)
    stereo[:, channel] = wave
    with sd.OutputStream(samplerate=SAMPLERATE, channels=2) as stream:
        stream.write(stereo)

left = threading.Thread(target=play, args=(0,))
right = threading.Thread(target=play, args=(1,))
left.start()
right.start()
left.join()
right.join()
