import os
import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt
from scipy.io import wavfile

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
OUTPUT_DIR = "output"

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

name = f"isi{ISI * 1000:.0f}ms_pulse{PULSE_AMPLITUDE}_noise{NOISE_AMPLITUDE}"
os.makedirs(OUTPUT_DIR, exist_ok=True)
wavfile.write(f"{OUTPUT_DIR}/{name}.wav", SAMPLERATE, wave)

onset_1 = PRE_TIME
onset_2 = PRE_TIME + PULSE_DURATION + ISI
plt.figure(figsize=(10, 4))
plt.plot(time_axis * 1000, wave, linewidth=0.5)
plt.axvspan(onset_1 * 1000, (onset_1 + PULSE_DURATION) * 1000, color="orange", alpha=0.2)
plt.axvspan(onset_2 * 1000, (onset_2 + PULSE_DURATION) * 1000, color="orange", alpha=0.2)
plt.title(f"{FREQUENCY} Hz bursts, ISI = {ISI * 1000:.0f} ms, "
          f"pulse amplitude = {PULSE_AMPLITUDE}, noise amplitude = {NOISE_AMPLITUDE}")
plt.xlabel("Time (ms)")
plt.ylabel("Amplitude")
plt.ylim(-1, 1)
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/{name}.png", dpi=150)
print(f"Saved {OUTPUT_DIR}/{name}.wav and {OUTPUT_DIR}/{name}.png")

sd.play(wave, SAMPLERATE)
sd.wait()
plt.show()
