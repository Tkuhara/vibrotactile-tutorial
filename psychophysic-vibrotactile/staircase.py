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

START_AMPLITUDE = 0.3   # 開始振幅
STEP = 0.02             # 振幅の刻み
MIN_AMPLITUDE = 0.0     # 振幅の下限
MAX_AMPLITUDE = 1.0     # 振幅の上限
N_DOWN = 1              # 何回連続「はい」で下げるか（1 = 1up-1down: 50%, 2 = 1up-2down: 70.7%）
N_REVERSALS = 8         # 反転がこの回数に達したら終了
N_DISCARD = 2           # 閾値計算で捨てる最初の反転数
MAX_TRIALS = 60         # 最大試行数

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
    print("\n 試行   振幅    (+ = はい, - = いいえ, * = 反転)")
    for i, amplitude, felt, reversal in rows:
        bar = "█" * round(amplitude / MAX_AMPLITUDE * 50)
        print(f" {i:3d} {amplitude:6.3f} |{bar} {'+' if felt else '-'}{' *' if reversal else ''}")


def save(rows):
    os.makedirs("results", exist_ok=True)
    path = f"results/{SUBJECT}_staircase_{time.strftime('%Y%m%d_%H%M%S')}.csv"
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["trial", "amplitude", "felt", "reversal"])
        writer.writerows(rows)
    print(f"\n 保存しました: {path}")


rows = []
reversals = []
amplitude = START_AMPLITUDE
direction = 0           # +1 = 上げた, -1 = 下げた, 0 = まだ動いていない
yes_count = 0
print(f"\n=== 階段法 (Staircase, 1up-{N_DOWN}down) ===")
print(f" 振動を感じたら [{YES_KEY}]、感じなければ [{NO_KEY}] を押してください。[{QUIT_KEY}] で中断。")
print(" 何かキーを押すと開始します。")
get_key()

try:
    while len(reversals) < N_REVERSALS and len(rows) < MAX_TRIALS:
        print(f"\n----- 試行 {len(rows) + 1} -----")
        felt = trial(amplitude)
        yes_count = yes_count + 1 if felt else 0
        # 「いいえ」で上げる、N_DOWN 回連続「はい」で下げる、それ以外は同じ振幅
        move = 0
        if not felt:
            move = 1
        elif yes_count >= N_DOWN:
            move = -1
            yes_count = 0
        reversal = move != 0 and direction != 0 and move != direction
        if reversal:
            reversals.append(amplitude)
        rows.append([len(rows) + 1, amplitude, int(felt), int(reversal)])
        if move != 0:
            direction = move
            amplitude = round(min(max(amplitude + move * STEP, MIN_AMPLITUDE), MAX_AMPLITUDE), 6)
        time.sleep(ITI)
finally:
    if rows:
        show_graph(rows)
        used = reversals[N_DISCARD:]
        print("\n 反転点:", ", ".join(f"{x:.3f}" for x in reversals))
        if used:
            print(f" 閾値（最初の {N_DISCARD} 個を除く反転点の平均）: {np.mean(used):.4f}")
        save(rows)
