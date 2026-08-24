import numpy as np
import sounddevice as sd
import threading
import time

DEVICE_1 = 1
DEVICE_2 = 2
FREQUENCY = 250
DURATION = 2
AMPLITUDE = 0.5
SAMPLERATE = 44100
DELAY_1 = 0
DELAY_2 = 0.2
DELAY_3 = 0.4
DELAY_4 = 0.6

print(sd.query_devices())

t = np.linspace(0, DURATION, int(SAMPLERATE * DURATION), endpoint=False)
wave = (AMPLITUDE * np.sin(2 * np.pi * FREQUENCY * t)).astype(np.float32)

barrier = threading.Barrier(4)

def play(device, channel, delay):
    stereo = np.zeros((len(wave), 2), dtype=np.float32)
    stereo[:, channel] = wave
    with sd.OutputStream(samplerate=SAMPLERATE, channels=2, device=device) as stream:
        barrier.wait()
        time.sleep(delay)
        stream.write(stereo)

thread_1 = threading.Thread(target=play, args=(DEVICE_1, 0, DELAY_1))
thread_2 = threading.Thread(target=play, args=(DEVICE_1, 1, DELAY_2))
thread_3 = threading.Thread(target=play, args=(DEVICE_2, 0, DELAY_3))
thread_4 = threading.Thread(target=play, args=(DEVICE_2, 1, DELAY_4))
thread_1.start()
thread_2.start()
thread_3.start()
thread_4.start()
thread_1.join()
thread_2.join()
thread_3.join()
thread_4.join()
