"""
A Module that offers different types of real time speech recognition.
"""

import logging
import threading
import time

import numpy as np
from retico.core import abstract
from retico.core.text.common import TextIU


import PySimpleGUI as sg

log = logging.getLogger(__name__)

class GuiInputModule(abstract.AbstractProducingModule):
    """A Module that allows sending input downstream via a gui"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.latest_input_iu = None

    @staticmethod
    def name():
        return "Gui Input Module"

    @staticmethod
    def description():
        return "A Module that allows sending input downstream via a gui"

    @staticmethod
    def output_iu():
        return TextIU

    def process_iu(self, input_iu):
        return input_iu

    def _run(self):
        log.info("_run called")
        self.prepare_run()
        self.is_running = True
        while self.is_running:
            with self.mutex:
                event, values = self.window.read()
                bot_msg = values[0].strip()
                if bot_msg == "":
                    continue
                output_iu = self.create_iu()
                output_iu.payload = bot_msg
                self.append(output_iu)

        self.shutdown()

    def setup(self):
        pass

    def prepare_run(self):
        layout = [
            [sg.Text('Say something to the bot'), sg.InputText()],
            [sg.Button('Send')]
        ]
        self.window = sg.Window('Bot Input', layout)

    def shutdown(self):
        self.window.close()