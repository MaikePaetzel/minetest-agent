"""
A Module that offers different types of real time speech recognition.
"""

import queue
import threading
from retico.core import abstract
from retico.core.text.common import SpeechRecognitionIU
from retico.core.audio.common import AudioIU

#from google.cloud import speech_v1 as gspeech
#from google.cloud.speech_v1 import types

from google.cloud import speech


class GoogleASRModule(abstract.AbstractModule):
    """A Module that recognizes speech by utilizing the Google Speech API."""

    def __init__(self, language="en-US", nchunks=20, rate=16000, **kwargs):
        """Initialize the GoogleASRModule with the given arguments.

        Args:
            language (str): The language code the recognizer should use.
            nchunks (int): Number of chunks that should trigger a new
                prediction.
            rate (int): The framerate of the input audio
        """
        super().__init__(**kwargs)
        self.language = language
        self.nchunks = nchunks
        self.rate = rate

        self.client = None
        self.streaming_config = None
        self.responses = None

        self.audio_buffer = queue.Queue()

        self.latest_input_iu = None

    @staticmethod
    def name():
        return "Google ASR Module"

    @staticmethod
    def description():
        return "A Module that incrementally recognizes speech."

    @staticmethod
    def input_ius():
        return [AudioIU]

    @staticmethod
    def output_iu():
        return SpeechRecognitionIU

    def process_iu(self, input_iu):
        print("ASR Processing IU")
        self.audio_buffer.put(input_iu.raw_audio)
        if not self.latest_input_iu:
            self.latest_input_iu = input_iu
        return None

    @staticmethod
    def _extract_results(response):
        predictions = []
        text = None
        stability = 0.0
        confidence = 0.0
        final = False
        for result in response.results:
            if not result or not result.alternatives:
                continue

            if not text:
                final = result.is_final
                stability = result.stability
                text = result.alternatives[0].transcript
                confidence = result.alternatives[0].confidence

            if not final:
                continue
            predictions.append(
                (
                    result.alternatives[0].transcript,
                    result.stability,
                    result.alternatives[0].confidence,
                    result.is_final,
                )
            )
        print("ASR", [predictions, text, stability, confidence, final])
        return predictions, text, stability, confidence, final

    def _generator(self):
        print(self.is_running)
        while True:
            # Use a blocking get() to ensure there's at least one chunk of
            # data, and stop iteration if the chunk is None, indicating the
            # end of the audio stream.
            import time
            time.sleep(.1)
            #print("ASR left buffer qsize", self._left_buffers[0].qsize())

            try:
                chunk = self.audio_buffer.get()
            except queue.Empty:
                continue
            print("ASR got chunk", chunk)
            if chunk is None:
                return
            yield chunk

    def ignore(self):
        while False:
            #data = [chunk]
            #yield data

            # Now consume whatever other data's still buffered.
            while True:
                try:
                    chunk = self.audio_buffer.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break

            yield b"".join(data)

    def _produce_predictions_loop(self):
        for response in self.responses:
            p, t, s, c, f = self._extract_results(response)
            if p:
                output_iu = self.create_iu(self.latest_input_iu)
                self.latest_input_iu = None
                output_iu.set_asr_results(p, t, s, c, f)
                if f:
                    output_iu.committed = True
                self.append(output_iu)

    def setup(self):
        self.client = speech.SpeechClient()

        config =  speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=self.rate,
            language_code=self.language,
        )
        self.streaming_config = speech.StreamingRecognitionConfig(config=config)

    def prepare_run(self):
        requests = (
            speech.StreamingRecognizeRequest(audio_content=content)
            for content in self._generator()
        )
        self.responses = self.client.streaming_recognize(
            self.streaming_config, requests
        )
        t = threading.Thread(target=self._produce_predictions_loop)
        print("Starting gspeech")
        t.start()

    def shutdown(self):
        self.audio_buffer.put(None)
