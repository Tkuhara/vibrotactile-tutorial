import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile

FREQUENCY = 250
PULSE_DURATION = 0.1
RAMP = 0.01
PRE_TIME = 0.5
POST_TIME = 0.5
NOISE_SEED = 0
SAMPLERATE = 44100
OUTPUT_DIR = "output"
ISI_LIST = [0.05, 0.1, 0.2]
PULSE_AMPLITUDE_LIST = [0.3, 0.5]
NOISE_AMPLITUDE_LIST = [0, 0.1, 0.2]


def make_wave(isi, pulse_amplitude, noise_amplitude):
    t = np.linspace(0, PULSE_DURATION, int(SAMPLERATE * PULSE_DURATION), endpoint=False)
    pulse = pulse_amplitude * np.sin(2 * np.pi * FREQUENCY * t)

    n_ramp = int(SAMPLERATE * RAMP)
    envelope = np.ones(len(pulse))
    envelope[:n_ramp] = np.linspace(0, 1, n_ramp)
    envelope[-n_ramp:] = np.linspace(1, 0, n_ramp)
    pulse = pulse * envelope

    pre = np.zeros(int(SAMPLERATE * PRE_TIME))
    gap = np.zeros(int(SAMPLERATE * isi))
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

    return (bursts + noise_amplitude * pink).astype(np.float32)


os.makedirs(OUTPUT_DIR, exist_ok=True)
for isi in ISI_LIST:
    for pulse_amplitude in PULSE_AMPLITUDE_LIST:
        for noise_amplitude in NOISE_AMPLITUDE_LIST:
            wave = make_wave(isi, pulse_amplitude, noise_amplitude)
            if np.max(np.abs(wave)) > 1:
                print("Warning: the waveform exceeds 1.0 and will be clipped.")

            name = f"isi{isi * 1000:.0f}ms_pulse{pulse_amplitude}_noise{noise_amplitude}"
            wavfile.write(f"{OUTPUT_DIR}/{name}.wav", SAMPLERATE, wave)

            time_axis = np.arange(len(wave)) / SAMPLERATE
            plt.figure(figsize=(10, 4))
            plt.plot(time_axis * 1000, wave, linewidth=0.5)
            plt.title(name)
            plt.xlabel("Time (ms)")
            plt.ylabel("Amplitude")
            plt.ylim(-1, 1)
            plt.tight_layout()
            plt.savefig(f"{OUTPUT_DIR}/{name}.png", dpi=150)
            plt.close()
            print(f"Saved {name}")
