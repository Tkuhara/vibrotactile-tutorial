# vibrotactile-tutorial

Python で振動刺激を作り、振動子から提示し、心理物理実験で感度を測るまでのチュートリアルです。

## 構成

| フォルダ | 内容 |
|---|---|
| [python-vibrotactile/](python-vibrotactile/) | 振動波形のデザインと提示（1〜4 チャンネル、同期・遅延制御） |
| [psychophysic-vibrotactile/](psychophysic-vibrotactile/) | 心理物理実験のサンプル（極限法・階段法による検出閾値の測定） |

`python-vibrotactile` → `psychophysic-vibrotactile` の順に進めてください。

## 準備

```
pip install numpy sounddevice
```
