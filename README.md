# vibrotactile-tutorial

Python で振動波形をデザインし、振動子から提示するまでのチュートリアルです。
進め方・ハードウェア構成・各プログラムの説明は **tutorial.pdf** を参照してください。

## ファイル

| ファイル | 内容 |
|---|---|
| tutorial.pdf | チュートリアル本体（日本語） |
| hardware_setup.png | ハードウェア構成図 |
| step1.py | 波形をデザインして 1 チャンネルで再生 |
| step2.py | スレッドでステレオ L/R を同時再生 |
| step2_2.py | 2 台のオーディオデバイスを同時再生 |
| step3.py | 2 チャンネルの同期と遅延（`DELAY`）の制御 |
| step4.py | 2 台 × ステレオ L/R ＝ 4 チャンネルの同期・遅延制御 |

## 準備

```
pip install numpy sounddevice
```
