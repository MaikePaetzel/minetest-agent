import logging
from pathlib import Path

import numpy as np
from retico.core import abstract, audio, text
import TTS
from TTS.utils.manage import ModelManager
from TTS.utils.synthesizer import Synthesizer


class MozillaTTS(abstract.AbstractModule):
    @staticmethod
    def name():
        return "TransformerTTS Module"

    @staticmethod
    def description():
        return "A module that uses TransformerTTS to synthesize audio."

    @staticmethod
    def input_ius():
        return [text.common.GeneratedTextIU, text.common.TextIU]

    @staticmethod
    def output_iu():
        return audio.common.SpeechIU

    def __init__(self):
        super().__init__()
        self.sample_rate = 22050
        self.sample_width = 1  # 1024 = win_length??

    def setup(self):
        model_name = "tts_models/en/ek1/tacotron2"

        path = Path(TTS.__file__).parent / ".models.json"
        manager = ModelManager(path)

        model_path, config_path, model_item = manager.download_model(model_name)
        vocoder_name = model_item["default_vocoder"]
        vocoder_path, vocoder_config_path, _ = manager.download_model(vocoder_name)

        self.synthesizer = Synthesizer(model_path, config_path)
        print("TTS setup")

    def generate(self, text):
        logging.info(f"generating speech for text {text}")
        wav = np.array(self.synthesizer.tts(text))
        wav_norm = wav * (32767 / max(0.01, np.max(np.abs(wav))))
        return wav_norm.astype(np.int16).tobytes()

    def process_iu(self, input_iu):
        output_iu = self.create_iu(input_iu)
        raw_audio = self.generate(input_iu.get_text())
        nframes = len(raw_audio) / self.sample_width
        output_iu.set_audio(
            raw_audio, nframes, self.synthesizer.output_sample_rate, self.sample_width
        )
        if hasattr(output_iu, "dispatch"):
            output_iu.dispatch = input_iu.dispatch
        return output_iu
