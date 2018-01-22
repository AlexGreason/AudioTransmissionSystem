import numpy as np
import matplotlib.pyplot as plt
import scipy.fftpack
import scipy.signal as signal

import pyaudio
import struct
import time
from scipy.signal import savgol_filter


def playData(data, samplerate):
    p = pyaudio.PyAudio()
    data = struct.pack('h' * len(data), *data)
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=samplerate, output=True, frames_per_buffer=len(data)//2)
    starttime = time.time()
    stream.write(data)


def beep(duration, freq, volume=1, samplerate = 44100):
    CHUNK = int(samplerate * duration)
    xf = np.linspace(0, duration, CHUNK)
    data = np.sin(xf * 2 * np.pi * freq)
    data = np.array(data * volume * (2**15)-1, dtype="int16")
    playData(data, samplerate)


def static(duration, seed = 0, volume=1, samplerate = 44100):
    samplerate = samplerate
    CHUNK = int(samplerate * duration)
    np.random.seed(seed)
    data = np.random.normal(0, 1, CHUNK)
    data = np.array(data * volume * (2**15)-1, dtype="int16")
    playData(data, samplerate)


def filteredstatic(duration, lowfreq, highfreq, volume=1, seed=0, samplerate = 44100):
    samplerate = samplerate
    data = filteredstaticdata(duration, lowfreq, highfreq, volume=volume, seed=seed, samplerate = samplerate)
    playData(data, samplerate)

def filteredstaticdata(duration, lowfreq, highfreq, volume=1, seed=0, samplerate = 44100):
    samplerate = samplerate
    CHUNK = int(samplerate * duration)
    np.random.seed(seed)
    data = np.clip(np.random.normal(0, 1, CHUNK), -1, 1)
    data = butter_bandpass_filter(data, lowfreq, highfreq, samplerate)
    data /= max(abs(data))
    data = np.array(data * volume * (2**15)-1, dtype="int16")
    return data


def prepdata(data, samplerate = 44100):
    yf = scipy.fftpack.fft(data)
    xf = np.linspace(0.0, samplerate // 2, len(data) // 2)

    minfreq = 1000
    maxfreq = 10000

    minindex = int(len(data) / 2 * minfreq / (samplerate // 2))
    maxindex = min(len(data) // 2, int(len(data) / 2 * maxfreq / (samplerate // 2)))
    print(minindex, maxindex)
    print("band noise:", sum(np.abs(yf[minindex:maxindex])))
    xs, ys = (xf[minindex:maxindex], np.abs(yf[minindex:maxindex]))
    return xs, ys


def liveplot(data, freqplot):
    #data = data[-1000000:]
    xs, ys = prepdata(data)
    freqplot.updateplot(xs, ys)


def plot(data, samplerate = 44100):
    xs, ys = prepdata(data, samplerate = samplerate)
    fig, ax = plt.subplots()
    ax.plot(xs, ys)
    plt.show()

def butter_bandpass(lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = signal.butter(order, [low, high], btype='band')
    return b, a


def butter_bandpass_filter(data, lowcut, highcut, fs, order=5):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = signal.lfilter(b, a, data)
    return y


def filterdata(data, win, samplerate = 44100):
    filtered = butter_bandpass_filter(data, 1000, 10000, samplerate)
    filtered = signal.convolve(filtered, win, mode='full')
    filtered = butter_bandpass_filter(filtered, 5000, 10000, samplerate)
    filtered = abs(filtered)
    filtered = abs(savgol_filter(filtered, 101, 3))
    filtered = butter_bandpass_filter(filtered, 100, 1000, samplerate)
    filtered = abs(filtered)
    return filtered


def removeBursts(data, threshold, window, maxremove):
    maxval = max(abs(data)) / np.average(abs(data))
    n = 0
    while maxval > threshold and n < maxremove:
        n += 1
        print(n)
        maxpos = abs(data).argmax()
        for i in range(maxpos - window//2, maxpos + window//2):
            data[i] = 0
        maxval = max(abs(data)) / np.average(abs(data))
    return data


def stddev(data, truestart, goal, samplerate = 44100):
    win = goal[::-1]
    filtered = filterdata(data, win, samplerate = samplerate)
    significance = (filtered - np.average(filtered)) / np.std(filtered)
    f, t, Sxx = signal.spectrogram(significance, samplerate)
    return((abs(filtered[truestart + len(goal)]) - np.average(filtered)) / np.std(filtered))