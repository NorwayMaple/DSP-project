"""
chorus.py
"""

import time, random 
import wave, argparse, pygame 
import numpy as np
from collections import deque
from matplotlib import pyplot as plt
from wave_data import WaveData
from generate_note import generateNote
    
def generateLFO(length = 44100, rate = 44100, ave_delay = 40, lfo_range = 40, freq = 8):
    LFO = np.array([0]*length, 'int16')
    for i in range(length):
        #y1=delay-range/2 y2=delay+range/2 x1=0 x2=(rate/freq)%i
        #y2-y1=range x2-x1=(rate/freq)%i
        #(y2-y1)/(x2-x1)=range*freq/rate
        #(x-x1)=i%(rate/freq)
        #(y2-y1)(x-x1)/(x2-x1)=range*freq*(i%(rate/freq))/rate
        #((y2-y1)(x-x1)/(x2-x1))+y1 = (range*freq*(i%(rate/freq))/rate) + delay - range/2
        LFO[i]=((lfo_range*freq*(i%(rate//freq))//rate)+ave_delay-(lfo_range//2))*rate//1000000
        #LFO[i]=(lfo_range*freq*(i%(rate//freq))//rate)+ave_delay-(lfo_range//2)*rate//1000
        #LFO[i]=(lfo_range*freq*(i%(rate//freq)))+ave_delay*rate-(lfo_range*rate//2)//1000


    return LFO
    
    
def chorus(data, buffer_length = 1764, lfo = None, num_instruments = 8, ave_delay = 600, lfo_range = 600, freq = 16): # also make into a class method?
# The buffer has to be big enough to fit the max delay
    samples = np.fromstring(data, 'int16')
    samples = (samples / 32767).astype('float32')
    chorus = np.array([0]*samples.size, 'float32')
    #Mad the below and ndarray of buffers
    #buf = deque([0]*buffer_length) Make this a numpy array of buffers
    bufs = np.zeros((num_instruments, buffer_length))
    if lfo is None:
        lfo = generateLFO(length = samples.size, freq = freq, ave_delay = ave_delay, lfo_range = lfo_range)
    lfo_init_pointers = np.random.randint(samples.size, size = num_instruments)
    for i in range(samples.size):
        buffer_wrap = i + lfo_init_pointers >= samples.size
        # this is how you'd do it in R
        bufs[:, i % buffer_length] = samples[i - lfo[i + lfo_init_pointers - buffer_wrap * samples.size]] # This is wrong, it doesnt use var lfo
        #The following was vectorized above
        #for j in range(num_instruments): #Should this be the outer loop?, also, could this be done in a vectorized way with numpy?
        #    if i + lfo_init_pointer >= samples.size:
        #        bufs[j, i % buffer_length] = samples[i - lfo[i + lfo_init_pointer[j] - samples.size]]
        #    else:
        #        bufs[j, i % buffer_length] = samples[i - lfo[i + lfo_init_pointer]]
        chorus[i] = bufs[:, i % buffer_length].sum() / num_instruments
#        chorus[i] = (buf[0] + samples[lfo[i]]) / 2
    #    chorus[i] = samples[i]/2 + buf[0]/2
     #   buf.append(samples[i])
      #  buf.popleft()
        if i > 4995 and i < 5000:
            print('debug')
            print(lfo[i + lfo_init_pointers - buffer_wrap * samples.size])
            print(i - lfo[i + lfo_init_pointers - buffer_wrap * samples.size])
            print(bufs[:, i % buffer_length])
            print(bufs[0, i%buffer_length:(i+5)%buffer_length])
            #You changed 1000 to 100000
    chorus = np.array(chorus * 32767, 'int16')
    return chorus.tobytes()
        
    
# play a wav file
class NotePlayer:
    # constr
    def __init__(self):
        pygame.mixer.pre_init(44100, -16, 1, 2048)
        pygame.init()
        # dictionary of notes
        self.sounds = {}
    # add a note
    def add(self, fileName):
        self.sounds[fileName] = pygame.mixer.Sound(fileName)
    # play a note
    def play(self, fileName):
        try:
            self.sounds[fileName].play()
        except:
            print(fileName + ' not found!')
  
# call main
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Generating sounds with Karplus String Algorithm.")
    # add arguments
    parser.add_argument('--file', default='note.wav', type=str, required=False)
    args = parser.parse_args()
    wave_data = WaveData(args.file)
    new_file_name = '%s_chorus.wav' % args.file[:-4]
    wave_data.write(chorus(wave_data.data))
