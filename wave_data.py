# write out WAVE file

import wave

class WaveData:
    __init__(self, fname)
        file = wave.open(fname, 'rb')
        self.nchannels = file.getnchannels()
        self.sample_width = file.getsampwidth()
        self.frame_rate = file.getframerate()
        self.nframes = file.getnframes()
        self.data = file.readframes(nframes)

    def write(self, fname)
        # open file 
		file = wave.open(fname, 'wb')
		# set parameters
		file.setparams((self.nchannels, self.sample_width, self.frame_rate, self.nframes,
						'NONE', 'noncompressed'))
		file.writeframes(self.data)
		file.close()