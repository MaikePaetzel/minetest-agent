import logging
import queue
import threading
import time
import wave

from retico.core import abstract
from retico.core.audio.common import AudioIU


class WavplayerModule(abstract.AbstractProducingModule):
    """A module that produces IUs containing audio signals that are captures by
    a microphone."""

    @staticmethod
    def name():
        return "WavplayerModule"

    @staticmethod
    def description():
        return "A producing module that plays a list of wav files."

    @staticmethod
    def output_iu():
        return AudioIU

    def __init__(self, file_list, delay, rate=44100, sample_width=2, **kwargs):
        """
        Initialize the Microphone Module.

        Args:
            chunk_size (int): The number of frames that should be stored in one
                AudioIU
            rate (int): The frame rate of the recording
            sample_width (int): The width of a single sample of audio in bytes.
        """
        super().__init__(**kwargs)
        self.rate = rate
        self.sample_width = sample_width

        self.file_list = file_list
        self.delay = delay
        self.audio_buffer = queue.Queue()

    def process_iu(self, input_iu):
        if not self.audio_buffer:
            return None
        data, nframes, framerate, sampwidth = self.audio_buffer.get()
        output_iu = self.create_iu()
        output_iu.set_audio(data, nframes, framerate, sampwidth)
        return output_iu

    def setup(self):
        """Set up the microphone for recording."""
        pass

    def prepare_run(self):
        logging.info("Calling prepare_run")

        def run():
            for f in self.file_list:
                logging.info(f"sending {f}")
                with wave.open(f) as w:
                    nframes = w.getnframes()
                    framerate = w.getframerate()
                    print(f"framerate {framerate}")
                    sampwidth = w.getsampwidth()
                    self.audio_buffer.put(
                        (w.readframes(nframes), nframes, framerate, sampwidth)
                    )
                logging.info(f"done sending {f}")
                time.sleep(self.delay)

        t = threading.Thread(target=run)
        t.start()

    def shutdown(self):
        """Close the audio stream."""
        self.audio_buffer = queue.Queue()
