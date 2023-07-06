import math
import struct
import time

import pyaudio


def main():
  p = pyaudio.PyAudio()
  chunk = 2048
  stream = p.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, output=False, frames_per_buffer=chunk)

  # Calculate the decibel level
  while True:
    data = stream.read(chunk)
    rms = math.sqrt(sum([(struct.unpack("<h", data[i:i+2])[0] / 32767.0) ** 2 for i in range(0, len(data), 2)]) / chunk)
    if rms > 0:
      decibel = 20 * math.log10(rms)
    else: 
      decibel = 0
    print("Decibel level:", decibel)

if __name__ == '__main__':
  main()