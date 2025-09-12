# pip install sounddevice numpy
import numpy as np
import sounddevice as sd

sr = 44100          # サンプリング周波数(Hz)
freq = 440          # 再生する周波数(Hz)：A4
dur = 2.0           # 時間(秒)
t = np.linspace(0, dur, int(sr*dur), endpoint=False)
wave = 0.2 * np.sin(2*np.pi*freq*t)  # 音量は0.2に抑える

sd.play(wave, sr)
sd.wait()

