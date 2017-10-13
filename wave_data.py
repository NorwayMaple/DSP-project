# write out WAVE file

import wave
import os
import numpy as np

class WaveData:
    def __init__(self, fname):
        try:
            with wave.open(fname, 'rb') as file:
                self.nchannels = file.getnchannels() # Check that this actually works for stereo
                self.sample_width = file.getsampwidth()
                self.frame_rate = file.getframerate()
                self.nframes = file.getnframes()
                self.data = file.readframes(self.nframes)
        except FileNotFoundError:
            self.nchannels = 1
            self.sample_width = 2
            self.frame_rate = 44100
            self.nframes = 44100
            self.data = b''

    def write(self, fname):
        # open file 
        with wave.open(fname, 'wb') as file:
            # set parameters
            file.setparams((self.nchannels, self.sample_width, self.frame_rate, self.nframes,
                            'NONE', 'noncompressed'))
            file.writeframes(self.data)
            
    def generateLFO(self, length = 44100, rate = 44100, ave_delay = 40, lfo_range = 40, freq = 8):
        LFO = np.array([0]*length, 'int16')
        for i in range(length):
            LFO[i]=((lfo_range*freq*(i%(rate//freq))//rate)+ave_delay-(lfo_range//2))*rate//1000000
        return LFO

    def chorus(self, buffer_length = 1764, lfo = None, num_instruments = 8, ave_delay = 600, lfo_range = 600, freq = 16): # also make into a class method?
    # The buffer has to be big enough to fit the max delay
        if self.sample_width == 1:
            samples = np.fromstring(self.data, 'int8')
            samples = (samples / 127).astype('float32')
        elif self.sample_width == 2:
            samples = np.fromstring(self.data, 'int16')
            samples = (samples / 32767).astype('float32')
        else:
            raise Exception('Sample widths other than 1 or 2 not supported')
        chorus = np.array([0]*samples.size, 'float32')
        bufs = np.zeros((num_instruments, buffer_length))
        if lfo is None:
            lfo = self.generateLFO(length = samples.size, freq = freq, ave_delay = ave_delay, lfo_range = lfo_range)
        lfo_init_pointers = np.random.randint(samples.size, size = num_instruments)
        for i in range(samples.size):
            buffer_wrap = i + lfo_init_pointers >= samples.size
            bufs[:, i % buffer_length] = samples[i - self.nchannels * lfo[i + lfo_init_pointers - buffer_wrap * samples.size]] # This is wrong, it doesnt use var lfo
            chorus[i] = bufs[:, i % buffer_length].sum() / num_instruments
            if i > 4995 and i < 5000:
                print('debug')
                print(lfo[i + lfo_init_pointers - buffer_wrap * samples.size])
                print(i - lfo[i + lfo_init_pointers - buffer_wrap * samples.size])
                print(bufs[:, i % buffer_length])
                print(bufs[0, i%buffer_length:(i+15)%buffer_length])
        if self.sample_width == 1:
            chorus = np.array(chorus * 127, 'int8')
        elif self.sample_width == 2:
            chorus = np.array(chorus * 32767, 'int16')
        else:
            raise Exception('Sample widths other than 1 or 2 not supported')
        self.data = chorus.tobytes()