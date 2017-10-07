from wave_data import WaveData 
from collections import deque
import random
import numpy as np
import argparse


# generate note of given frequency using Karplus algorithm
def generateNote(wave_data, freq):
    nSamples = 44100 # Is this needed now that you have the WaveData object
    sampleRate = 44100 # ditto
    N = int(wave_data.frame_rate/freq)
    # initialize ring buffer
    buf = deque([random.random() - 0.5 for i in range(N)])
    # plot of flag set 
    # init sample buffer
    samples = np.array([0]*wave_data.nframes, 'float32')
    for i in range(wave_data.nframes):
        samples[i] = buf[0]
        avg = 0.995*0.5*(buf[0] + buf[1])
        buf.append(avg)
        buf.popleft() 
      
    # samples to 16-bit to string
    # max value is 32767 for 16-bit
    samples = np.array(samples * 32767, 'int16')
    wave_data.data = samples.tobytes()
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Generating sounds with Karplus String Algorithm.")
    # add arguments
    parser.add_argument('--freq', default=440, type=int, required=False)
    args = parser.parse_args()   
    wave_data = WaveData()
    generateNote(int(args.freq), wave_data)
    wave_data.write('note.wav')