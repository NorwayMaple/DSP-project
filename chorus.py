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
    
def chorus(data, buffer_length = 441, num_instruments = 2): # Next step:  Figure out why we use ring buffers instead of just doing the delay by subtracting from the index in an iteraiton (see Chrome bookmark), and if I need multiple buffers or multiple locaitons on the same buffer to make the chorusing effect?  Which one is more efficient
    # not sure what order of magnitude buffer_length should be
    samples = np.fromstring(data, 'int16')
    samples = (samples / 32767).astype('float32')
    chorus = np.array([0]*samples.size, 'float32')
    buffers = [deque([0]*((buffer_length * i // num_instruments-1)+1)) for i in range(1, num_instruments)]
    for i in range(samples.size):
        buf_vals = np.array(samples[i], 'float32')
        for buf in buffers:
            np.append(buf_vals, buf[0])
            buf.append(samples[i])
            buf.popleft()
        chorus[i] = np.mean(buf_vals)
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
