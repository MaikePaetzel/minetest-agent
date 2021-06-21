from retico.core import abstract, text

import requests
import logging
import urllib


class RasaHTTP(abstract.AbstractModule):
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
        return [text.common.SpeechRecognitionIU, text.common.TextIU]

    @staticmethod
    def output_iu():
        return text.common.GeneratedTextIU

    def on_player_message(self, input_iu):
        # rasa run --enable-api
        # rasa run actions
        # curl -XPOST http://localhost:5005/webhooks/rest/webhook -d '{"sender": "test_user","message": "Move that wooden"}
        # action server should then forward intents to bot brain
        text = input_iu.get_text()
        logging.info(f"Sending text to rasa {text}")
        req = self.session.post(self.user_endpoint, json={"sender": self.rasa_user_channel, "message": text})
        req.raise_for_status()
        res = req.json()
        if len(res) == 0:
            return None
        return res[0]["text"]

    def on_bot_message(self, bot_utterance_iu):
        bot_utterance_name = bot_utterance_iu.get_text()
        logging.info(f"Sending bot command to rasa {text}")
        req_data = {"name": bot_utterance_name, "policy": "string", "confidence": 1}
        req = self.session.post(self.execute_endpoint, json=req_data)
        req.raise_for_status()
        res = req.json()["messages"]
        if len(res) == 0:
            return None
        return res[0]["text"]

    def __init__(self, endpoint="http://localhost:5005", forward_after_final=True, **kwargs):
        super().__init__(**kwargs)
        self.forward_after_final = forward_after_final
        self.rasa_user_channel = "player"
        self.user_endpoint = urllib.parse.urljoin(endpoint, "webhooks/rest/webhook")
        self.execute_endpoint = urllib.parse.urljoin(endpoint, f"conversations/{self.rasa_user_channel}/execute")
        self.session = requests.Session()

    def process_iu(self, input_iu):
        if isinstance(input_iu, text.common.SpeechRecognitionIU):
            if self.forward_after_final and not input_iu.final:
                return
        response = self.on_player_message(input_iu)
        if response is None:
            return
        output_iu = self.create_iu(input_iu)
        output_iu.payload = response
        output_iu.dispatch = True
        return output_iu