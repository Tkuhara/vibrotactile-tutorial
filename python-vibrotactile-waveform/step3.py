import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt

FREQUENCY = 250
PULSE_DURATION = 0.1
PULSE_AMPLITUDE = 0.5
RAMP = 0.01
ISI = 0.2
PRE_TIME = 0.5
POST_TIME = 0.5
NOISE_AMPLITUDE = 0.2
NOISE_SEED = 0
SAMPLERATE = 44100

t = np.linspace(0, PULSE_DURATION, int(SAMPLERATE * PULSE_DURATION), endpoint=False)
pulse = PULSE_AMPLITUDE * np.sin(2 * np.pi * FREQUENCY * t)

n_ramp = int(SAMPLERATE * RAMP)
envelope = np.ones(len(pulse))
envelope[:n_ramp] = np.linspace(0, 1, n_ramp)
envelope[-n_ramp:] = np.linspace(1, 0, n_ramp)
pulse = pulse * envelope

pre = np.zeros(int(SAMPLERATE * PRE_TIME))
gap = np.zeros(int(SAMPLERATE * ISI))
post = np.zeros(int(SAMPLERATE * POST_TIME))
bursts = np.concatenate([pre, pulse, gap, pulse, post])

rng = np.random.default_rng(NOISE_SEED)
white = rng.standard_normal(len(bursts))
spectrum = np.fft.rfft(white)
freqs = np.fft.rfftfreq(len(bursts), 1 / SAMPLERATE)
spectrum[0] = 0
spectrum[1:] = spectrum[1:] / np.sqrt(freqs[1:])
pink = np.fft.irfft(spectrum, len(bursts))
pink = pink / np.max(np.abs(pink))
noise = NOISE_AMPLITUDE * pink

wave = (bursts + noise).astype(np.float32)
time_axis = np.arange(len(wave)) / SAMPLERATE

if np.max(np.abs(wave)) > 1:
    print("Warning: the waveform exceeds 1.0 and will be clipped.")

sd.play(wave, SAMPLERATE)
sd.wait()

plt.subplot(2, 1, 1)
plt.plot(time_axis * 1000, wave)
plt.xlabel("Time (ms)")
plt.ylabel("Amplitude")
plt.subplot(2, 1, 2)
plt.loglog(freqs[1:], np.abs(np.fft.rfft(noise))[1:])
plt.xlabel("Frequency (Hz)")
plt.ylabel("Noise magnitude")
plt.tight_layout()
plt.show()
