import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt

FREQUENCY = 250
PULSE_DURATION = 0.1
PULSE_AMPLITUDE = 0.5
RAMP = 0.01
SAMPLERATE = 44100

t = np.linspace(0, PULSE_DURATION, int(SAMPLERATE * PULSE_DURATION), endpoint=False)
pulse = PULSE_AMPLITUDE * np.sin(2 * np.pi * FREQUENCY * t)

n_ramp = int(SAMPLERATE * RAMP)
envelope = np.ones(len(pulse))
envelope[:n_ramp] = np.linspace(0, 1, n_ramp)
envelope[-n_ramp:] = np.linspace(1, 0, n_ramp)
pulse = (pulse * envelope).astype(np.float32)

sd.play(pulse, SAMPLERATE)
sd.wait()

plt.plot(t * 1000, pulse)
plt.xlabel("Time (ms)")
plt.ylabel("Amplitude")
plt.show()
