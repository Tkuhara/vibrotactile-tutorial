import numpy as np
import sounddevice as sd
import threading

DEVICE_1 = 1
DEVICE_2 = 2
FREQUENCY = 250
DURATION = 2
AMPLITUDE = 0.5
SAMPLERATE = 44100

print(sd.query_devices())

t = np.linspace(0, DURATION, int(SAMPLERATE * DURATION), endpoint=False)
wave = (AMPLITUDE * np.sin(2 * np.pi * FREQUENCY * t)).astype(np.float32)

def play(device):
    with sd.OutputStream(samplerate=SAMPLERATE, channels=1, device=device) as stream:
        stream.write(wave)

thread_1 = threading.Thread(target=play, args=(DEVICE_1,))
thread_2 = threading.Thread(target=play, args=(DEVICE_2,))
thread_1.start()
thread_2.start()
thread_1.join()
thread_2.join()
