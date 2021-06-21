"""
A Module that offers different types of real time speech recognition.
"""

import logging
import queue
import threading

import numpy as np
import torch
from retico.core import abstract
from retico.core.audio.common import AudioIU
from retico.core.text.common import SpeechRecognitionIU
from transformers import (Speech2TextForConditionalGeneration,
                          Speech2TextProcessor)


class HuggingfaceASRModule(abstract.AbstractModule):
    # https://huggingface.co/transformers/model_doc/speech_to_text.html

    """A Module that recognizes speech using huggingface asr model"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.model = Speech2TextForConditionalGeneration.from_pretrained(
            "facebook/s2t-small-librispeech-asr"
        )
        self.processor = Speech2TextProcessor.from_pretrained(
            "facebook/s2t-small-librispeech-asr"
        )
        self.sampling_rate = 16_000
        self.audio_buffer = queue.Queue()
        self.latest_input_iu = None

    @staticmethod
    def name():
        return "Huggingface ASR Module"

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
        self.audio_buffer.put(input_iu.raw_audio)
        if not self.latest_input_iu:
            self.latest_input_iu = input_iu
        return None

    def predict(self, audio):
        audio_as_numpy = (
            np.frombuffer(audio, dtype=np.int16).astype(np.float32) / 2 ** 15
        )
        inputs = self.processor(
            audio_as_numpy, sampling_rate=self.sampling_rate, return_tensors="pt"
        )
        generated_ids = self.model.generate(
            input_ids=inputs["input_features"], attention_mask=inputs["attention_mask"]
        )
        transcription = self.processor.batch_decode(generated_ids)[0]
        output_iu = self.create_iu(self.latest_input_iu)
        output_iu.set_asr_results(
            [(transcription, 1, 1, True)], transcription, 1, 1, True
        )
        output_iu.committed = True
        return output_iu

    def loop(self):
        while True:
            # Use a blocking get() to ensure there's at least one chunk of
            # data, and stop iteration if the chunk is None, indicating the
            # end of the audio stream.
            logging.info("asr loop")
            chunk = self.audio_buffer.get()
            if chunk is None:
                continue
            self.append(self.predict(chunk))
            if not self.is_running:
                break

    def setup(self):
        pass

    def prepare_run(self):
        t = threading.Thread(target=self.loop)
        logging.info("starting loop thread")
        t.start()
        logging.info("started loop thread")

    def shutdown(self):
        self.audio_buffer.put(None)