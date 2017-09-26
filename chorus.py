"""
chorus.py
"""

import sys, os
import time, random 
import wave, argparse, pygame 
import numpy as np
from collections import deque
from matplotlib import pyplot as plt

# show plot of algorithm in action?
gShowPlot = False

# notes of a Pentatonic Minor scale
# piano C4-E(b)-F-G-B(b)-C5
pmNotes = {'C4': 262, 'Eb': 311, 'F': 349, 'G':391, 'Bb':466}

# write out WAVE file
def writeWAVE(fname, data):
    # open file 
    file = wave.open(fname, 'wb')
    # WAV file parameters 
    nChannels = 1
    sampleWidth = 2
    frameRate = 44100
    nFrames = 44100
    # set parameters
    file.setparams((nChannels, sampleWidth, frameRate, nFrames,
                    'NONE', 'noncompressed'))
    file.writeframes(data)
    file.close()

# generate note of given frequency
def generateNote(freq):
    nSamples = 44100
    sampleRate = 44100
    N = int(sampleRate/freq)
    # initialize ring buffer
    buf = deque([random.random() - 0.5 for i in range(N)])
    # plot of flag set 
    if gShowPlot:
        axline, = plt.plot(buf)
    # init sample buffer
    samples = np.array([0]*nSamples, 'float32')
    for i in range(nSamples):
        samples[i] = buf[0]
        avg = 0.995*0.5*(buf[0] + buf[1])
        buf.append(avg)
        buf.popleft()  
        # plot of flag set 
        if gShowPlot:
            if i % 1000 == 0:
                axline.set_ydata(buf)
                plt.draw()
      
    # samples to 16-bit to string
    # max value is 32767 for 16-bit
    samples = np.array(samples * 32767, 'int16')
    return samples.tostring()
    
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
    
    
def chorus(data, buffer_length = 1764, lfo = None, num_instruments = 8, ave_delay = 600, lfo_range = 600, freq = 16):
# The buffer has to be big enough to fit the max delay
    samples = np.fromstring(data, 'int16')
    samples = (samples / 32767).astype('float32')
    chorus = np.array([0]*samples.size, 'float32')
    #Mad the below and ndarray of buffers
    #buf = deque([0]*buffer_length) Make this a numpy array of buffers
    bufs = np.zeros((num_instruments, buffer_length))
    if lfo is None:
        lfo = generateLFO(length = samples.size, freq = freq, ave_delay = ave_delay, lfo_range = lfo_range )
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
    return chorus.tostring()
        
    
# play a wav file
class NotePlayer:
    # constr
    def __init__(self):
        pygame.mixer.pre_init(44100, -16, 1, 2048)
        pygame.init()
        # dictionary of notes
        self.notes = {}
    # add a note
    def add(self, fileName):
        self.notes[fileName] = pygame.mixer.Sound(fileName)
    # play a note
    def play(self, fileName):
        try:
            self.notes[fileName].play()
        except:
            print(fileName + ' not found!')

# main() function
def main():
    # declare global var
    global gShowPlot

    parser = argparse.ArgumentParser(description="Generating sounds with Karplus String Algorithm.")
    # add arguments
    parser.add_argument('--display', action='store_true', required=False)
    parser.add_argument('--play', action='store_true', required=False)
    parser.add_argument('--piano', action='store_true', required=False)
    args = parser.parse_args()

    # show plot if flag set
    if args.display:
        gShowPlot = True
        plt.ion()

    # create note player
    nplayer = NotePlayer()

    print('creating notes...')
    for name, freq in list(pmNotes.items()):
        fileName = name + '.wav' 
        if not os.path.exists(fileName) or args.display:
            data = generateNote(freq) 
            print('creating ' + fileName + '...')
            writeWAVE(fileName, data) 
        else:
            print('fileName already created. skipping...')
        
        # add note to player
        nplayer.add(name + '.wav')
        
        # play note if display flag set
        if args.display:
            nplayer.play(name + '.wav')
            time.sleep(0.5)
    
    # play a random tune
    if args.play:
        while True:
            try: 
                nplayer.playRandom()
                # rest - 1 to 8 beats
                rest = np.random.choice([1, 2, 4, 8], 1, 
                                        p=[0.15, 0.7, 0.1, 0.05])
                time.sleep(0.25*rest[0])
            except KeyboardInterrupt:
                exit()

    # random piano mode
    if args.piano:
        while True:
            for event in pygame.event.get():
                if (event.type == pygame.KEYUP):
                    print("key pressed")
                    nplayer.playRandom()
                    time.sleep(0.5)
  
# call main
if __name__ == '__main__':
    main()
