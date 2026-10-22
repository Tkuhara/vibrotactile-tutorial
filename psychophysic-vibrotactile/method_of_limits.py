import csv
import os
import sys
import time

import numpy as np
import sounddevice as sd

# ===== 実験ごとに変更する変数 =====
SUBJECT = "test"        # 参加者 ID（結果ファイル名に使用）
DEVICE = None           # 出力デバイス番号（None = 既定のデバイス, sd.query_devices() で確認）
CHANNEL = 0             # 0 = L, 1 = R
FREQUENCY = 250         # 振動周波数 [Hz]
DURATION = 1.0          # 刺激時間 [s]
RAMP = 0.01             # 立ち上がり・立ち下がり時間 [s]（クリック音防止）
SAMPLERATE = 44100

START_LOW = 0.0         # 上昇系列の開始振幅
START_HIGH = 0.3        # 下降系列の開始振幅
STEP = 0.01             # 振幅の刻み
MAX_AMPLITUDE = 1.0     # 振幅の上限
N_SERIES = 6            # 系列数（上昇 → 下降 → 上昇 … の順）

READY_TIME = 1.0        # 「準備」表示から刺激までの時間 [s]
ITI = 1.0               # 試行間隔 [s]
YES_KEY = "y"           # 「感じた」
NO_KEY = "n"            # 「感じない」
QUIT_KEY = "q"          # 中断（それまでの結果は保存）


def get_key():
    if os.name == "nt":
        import msvcrt
        while msvcrt.kbhit():
            msvcrt.getwch()
        return msvcrt.getwch().lower()
    import termios
    import tty
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setcbreak(fd)
        termios.tcflush(fd, termios.TCIFLUSH)
        return sys.stdin.read(1).lower()
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)


def play(amplitude):
    t = np.arange(int(SAMPLERATE * DURATION)) / SAMPLERATE
    wave = amplitude * np.sin(2 * np.pi * FREQUENCY * t)
    n = int(SAMPLERATE * RAMP)
    wave[:n] *= np.linspace(0, 1, n)
    wave[-n:] *= np.linspace(1, 0, n)
    stereo = np.zeros((len(wave), 2), dtype=np.float32)
    stereo[:, CHANNEL] = wave
    sd.play(stereo, SAMPLERATE, device=DEVICE)
    sd.wait()


def trial(amplitude):
    print("\n   準備 ...", flush=True)
    time.sleep(READY_TIME)
    print("   ■■■■■  振動中  ■■■■■", flush=True)
    play(amplitude)
    print(f"   感じましたか？   [{YES_KEY}] はい   [{NO_KEY}] いいえ", flush=True)
    while True:
        key = get_key()
        if key == QUIT_KEY:
            sys.exit()
        if key in (YES_KEY, NO_KEY):
            print("   → はい" if key == YES_KEY else "   → いいえ")
            return key == YES_KEY


def show_graph(rows):
    print("\n 試行  系列   振幅    (+ = はい, - = いいえ)")
    for i, (series, direction, amplitude, felt) in enumerate(rows, 1):
        bar = "█" * round(amplitude / MAX_AMPLITUDE * 50)
        print(f" {i:3d}  {series}{direction:>5} {amplitude:6.3f} |{bar} {'+' if felt else '-'}")


def save(rows):
    os.makedirs("results", exist_ok=True)
    path = f"results/{SUBJECT}_limits_{time.strftime('%Y%m%d_%H%M%S')}.csv"
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["series", "direction", "amplitude", "felt"])
        writer.writerows(rows)
    print(f"\n 保存しました: {path}")


rows = []
thresholds = []
print("\n=== 極限法 (Method of Limits) ===")
print(f" 振動を感じたら [{YES_KEY}]、感じなければ [{NO_KEY}] を押してください。[{QUIT_KEY}] で中断。")
print(" 何かキーを押すと開始します。")
get_key()

try:
    for s in range(N_SERIES):
        ascending = s % 2 == 0
        amplitude = START_LOW if ascending else START_HIGH
        previous = None
        print(f"\n----- 系列 {s + 1} / {N_SERIES} -----")
        while 0 <= amplitude <= MAX_AMPLITUDE:
            felt = trial(amplitude)
            rows.append([s + 1, "up" if ascending else "down", amplitude, int(felt)])
            # 上昇系列は初めて「はい」、下降系列は初めて「いいえ」で終了
            if felt == ascending:
                thresholds.append(amplitude if previous is None else (amplitude + previous) / 2)
                break
            previous = amplitude
            amplitude = round(amplitude + (STEP if ascending else -STEP), 6)
            time.sleep(ITI)
        time.sleep(ITI)
finally:
    if rows:
        show_graph(rows)
        print("\n 各系列の閾値:", ", ".join(f"{x:.3f}" for x in thresholds))
        if thresholds:
            print(f" 平均閾値: {np.mean(thresholds):.4f}")
        save(rows)
