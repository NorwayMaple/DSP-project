# write out WAVE file

import wave

class WaveData:
    __init__(self, fname = None)
        if fname:
            with wave.open(fname, 'rb') as file:
				self.nchannels = file.getnchannels() # Check that this actually works for stereo
				self.sample_width = file.getsampwidth()
				self.frame_rate = file.getframerate()
				self.nframes = file.getnframes()
				self.data = file.readframes(nframes)
		else:
		    self.nchannels = 1
		    self.sample_width = 2
		    self.frame_rate = 44100
		    self.nframes = 44100
		    self.data = b''

    def write(self, fname)
        # open file 
		file = wave.open(fname, 'wb')
		# set parameters
		file.setparams((self.nchannels, self.sample_width, self.frame_rate, self.nframes,
						'NONE', 'noncompressed'))
		file.writeframes(self.data)
		file.close()