import numpy as np
import wave
import os
import time
from gnuradio import gr
from pydub import AudioSegment
from pydub.generators import Sine

class save_mp3_on_trigger(gr.sync_block):
    """
    Embedded Python Block that records float samples into an MP3 file when a trigger signal is detected.
    Input 1 is the float audio stream. Input 2 is the float trigger signal.
    """
    def __init__(self, sample_rate=48000):
        gr.sync_block.__init__(
            self,
            name="save_mp3_on_trigger",
            in_sig=[np.float32, np.float32],  # Float samples and trigger signal
            out_sig=None
        )
        self.sample_rate = sample_rate
        self.recording = False
        self.audio_buffer = []
        self.output_dir = "recordings"
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def start_new_recording(self):
        timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
        self.filename = os.path.join(self.output_dir, f"recording_{timestamp}.wav")
        self.audio_buffer = []
        print(f"Recording started: {self.filename}")

    def stop_and_save(self):
        if self.audio_buffer:
            temp_wav = self.filename
            with wave.open(temp_wav, 'w') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(self.sample_rate)
                wf.writeframes(np.array(self.audio_buffer, dtype=np.int16).tobytes())
            
            audio = AudioSegment.from_wav(temp_wav)
            mp3_filename = temp_wav.replace(".wav", ".mp3")
            audio.export(mp3_filename, format="mp3")
            os.remove(temp_wav)  # Delete temporary WAV file
            print(f"Saved recording: {mp3_filename}")
        self.audio_buffer = []

    def work(self, input_items, output_items):
        samples = input_items[0]
        trigger = input_items[1]
        
        for i in range(len(samples)):
            if trigger[i] == 1:
                if not self.recording:
                    self.recording = True
                    self.start_new_recording()
                self.audio_buffer.append(int(samples[i] * 32767))
            elif self.recording:
                self.stop_and_save()
                self.recording = False

        return len(samples)
