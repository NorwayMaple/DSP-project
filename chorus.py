"""
chorus.py
"""
import argparse
from wave_data import WaveData
from generate_note import generateNote
  

if __name__ == '__main__':
    # This needs to be changed to raise an error if no arg is given and note.wav does not exist
    parser = argparse.ArgumentParser(description="Generating sounds with Karplus String Algorithm.")
    # add arguments
    parser.add_argument('--file', default='note.wav', type=str, required=False)
    args = parser.parse_args()
    wave_data = WaveData(args.file)
    if wave_data.data == b'': # You can also run generate_note.py first and won't run into this problem
        generateNote(wave_data, 440)
    new_file_name = '%s_chorus.wav' % args.file[:-4]
    wave_data.chorus()
    wave_data.write(new_file_name)
