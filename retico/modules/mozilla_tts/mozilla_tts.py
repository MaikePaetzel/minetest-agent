import logging
from pathlib import Path

import numpy as np
from retico.core import abstract, audio, text
import TTS
from TTS.utils.manage import ModelManager
from TTS.utils.synthesizer import Synthesizer
from aiohttp import web
import urllib.parse
import requests


def get_synthesizer_endpoint():
    model_name = "tts_models/en/ek1/tacotron2"

    path = Path(TTS.__file__).parent / ".models.json"
    manager = ModelManager(path)

    model_path, config_path, model_item = manager.download_model(model_name)
    vocoder_name = model_item["default_vocoder"]
    vocoder_path, vocoder_config_path, _ = manager.download_model(vocoder_name)

    print(f"mozilla_tts.get_action_endpoint: creating synthesizer with args {model_path}, {config_path}")
    synthesizer = Synthesizer(model_path, config_path)
    print(f"mozilla_tts.get_action_endpoint: TTS synth has output rate {synthesizer.output_sample_rate}")
    print("mozilla_tts.get_action_endpoint: TTS setup")

    async def synthesize(request: web.Request):
        json = await request.json()
        wav = np.array(synthesizer.tts(json["text"]))
        wav_norm = wav * (32767 / max(0.01, np.max(np.abs(wav))))
        return web.Response(body=wav_norm.astype(np.int16).tobytes())

    app = web.Application()
    app.add_routes([web.post("/synthesize", synthesize)])

    return app


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

        print(f"mozilla_tts.MozillaTTS.setup: creating synthesizer with args {model_path}, {config_path}")
        self.synthesizer = Synthesizer(model_path, config_path)
        print("mozilla_tts.MozillaTTS.setup: TTS setup")

    def generate(self, text):
        print(f"mozilla_tts.MozillaTTS.generate: generating speech for text {repr(text)}")
        wav = np.array(self.synthesizer.tts(text))
        wav_norm = wav * (32767 / max(0.01, np.max(np.abs(wav))))
        return wav_norm.astype(np.int16).tobytes()

    def process_iu(self, input_iu):
        print(f"mozilla_tts.MozillaTTS.process_iu: have iu")
        output_iu = self.create_iu(input_iu)
        raw_audio = self.generate(input_iu.get_text())
        nframes = len(raw_audio) / self.sample_width
        output_iu.set_audio(
            raw_audio, nframes, self.synthesizer.output_sample_rate, self.sample_width
        )
        if hasattr(output_iu, "dispatch"):
            output_iu.dispatch = input_iu.dispatch
        print(f"mozilla_tts.MozillaTTS.process_iu: generated iu")
        return output_iu



class MozillaTTSHTTP(abstract.AbstractModule):
    """
    A Moduel that turns SpeechRecognitionIUs or TextIUs into GeneratedTextIUs
    that have the dispatch-flag set.
    """

    @staticmethod
    def name():
        return "ASR to TTS Module"

    @staticmethod
    def description():
        return (
            "A module that uses SpeechRecognition IUs and outputs" + " dispatchable IUs"
        )

    @staticmethod
    def input_ius():
        return [text.common.GeneratedTextIU, text.common.TextIU]

    @staticmethod
    def output_iu():
        return audio.common.SpeechIU

    def on_player_message(self, input_iu):
        text = input_iu.get_text()
        print(f"rasa_http.RasaHTTP.on_player_message: sending text to tts {text}")
        req_data = {"text": text}
        req = self.session.post(self.endpoint, json=req_data)
        req.raise_for_status()
        res = req.content
        return res

    def __init__(self, endpoint="http://localhost:5060", forward_after_final=True, **kwargs):
        super().__init__(**kwargs)
        self.forward_after_final = forward_after_final
        self.endpoint = urllib.parse.urljoin(endpoint, "synthesize")
        self.session = requests.Session()
        self.sample_rate = 22050
        self.output_sample_rate = 22050
        self.sample_width = 1  # 1024 = win_length??


    def process_iu(self, input_iu):
        print(f"mozilla_tts.MozillaTTS.process_iu: have iu")
        raw_audio = self.on_player_message(input_iu)
        output_iu = self.create_iu(input_iu)
        nframes = len(raw_audio) / self.sample_width
        output_iu.set_audio(
            raw_audio, nframes, self.output_sample_rate, self.sample_width
        )
        if hasattr(output_iu, "dispatch"):
            output_iu.dispatch = input_iu.dispatch
        print(f"mozilla_tts.MozillaTTS.process_iu: generated iu")
        return output_iu