# python-vibrotactile-waveform

2 つの正弦波バーストを ISI を空けて並べ、背景にピンクノイズを重ねた振動刺激を作り、
WAV ファイルと波形の画像（PNG）に書き出すチュートリアルです。
各プログラムの説明は **tutorial.pdf** を参照してください。

## ファイル

| ファイル | 内容 |
|---|---|
| tutorial.pdf | チュートリアル本体（日本語） |
| step1.py | 正弦波バーストを 1 つ作り、ランプ（立ち上がり・立ち下がり）をつける |
| step2.py | バーストを 2 つ、`ISI` を空けて並べる |
| step3.py | 背景にピンクノイズ（`NOISE_AMPLITUDE`）を重ねる |
| step4.py | 波形を `output/` に WAV と PNG で書き出す |
| step5.py | ISI × パルス振幅 × ノイズ振幅の全条件をまとめて書き出す |

## 準備

```
pip install numpy sounddevice matplotlib scipy
```

## 実行

```
cd python-vibrotactile-waveform
python step4.py
```

`output/isi200ms_pulse0.5_noise0.2.wav` と `.png` が作られます。
