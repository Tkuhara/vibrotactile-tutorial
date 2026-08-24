import numpy as np
import sounddevice as sd

FREQUENCY = 250
DURATION = 2
AMPLITUDE = 0.5
SAMPLERATE = 44100

t = np.linspace(0, DURATION, int(SAMPLERATE * DURATION), endpoint=False)
wave = (AMPLITUDE * np.sin(2 * np.pi * FREQUENCY * t)).astype(np.float32)

sd.play(wave, SAMPLERATE)
sd.wait()
