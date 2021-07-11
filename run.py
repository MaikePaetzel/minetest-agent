import argparse
from multiprocessing import Queue, Process
import time
import requests

from aiohttp import web

import rasa.cli.run

from agent.droidlet_action_server import get_action_endpoint
from agent.droidlet_agent import Robo

import logging

from retico.core.audio.io import SpeakerModule
from retico.dialogue.manager.rasa_http import RasaHTTP
from retico.modules.gui_input.gui_input import GuiInputModule
from retico.modules.mozilla_tts.mozilla_tts import MozillaTTS


def run_retico():
    m_input = GuiInputModule()
    m_rasa = RasaHTTP()
    m_tts = MozillaTTS()
    m_speaker = SpeakerModule(m_tts.sample_rate)

    m_input.subscribe(m_rasa)
    m_rasa.subscribe(m_tts)
    m_tts.subscribe(m_speaker)

    m_input.setup()
    m_rasa.setup()
    m_tts.setup()
    m_speaker.setup()

    m_input.run(run_setup=False)
    m_rasa.run(run_setup=False)
    m_tts.run(run_setup=False)
    m_speaker.run(run_setup=False)


def main():
    # minecraft server running

    pass

    # miney running

    action_server_to_brain_queue = Queue()
    action_server = get_action_endpoint(action_server_to_brain_queue)
    robo = Robo(action_server_to_brain_queue)

    # run rasa action server

    def run_webapp():
        logging.basicConfig(level=logging.DEBUG)
        web.run_app(action_server, port=5055, print=logging.info)

    p_rasa_actions = Process(target=run_webapp, daemon=True)
    p_rasa_actions.start()
    logging.info("Started action server")

    # run rasa dialogue manager

    def run_rasa():
        logging.basicConfig(level=logging.DEBUG)
        rasa_args = argparse.Namespace()
        rasa_args.endpoints = 'dialog_manager/rasa_dm/endpoints.yml'
        rasa_args.credentials = None
        rasa_args.remote_storage = None
        rasa_args.enable_api = True
        rasa_args.model = 'dialog_manager/rasa_dm/models/20210709-111210.tar.gz'
        rasa.cli.run.run(rasa_args)

    p_rasa = Process(target=run_rasa, daemon=True)
    p_rasa.start()
    print("Starting rasa")

    # wait for rasa to load

    while True:
        try:
            print("Waiting for rasa")
            requests.get("http://localhost:5005")
            print("Rasa is ready")
            break
        except Exception:
            time.sleep(3)

    # run retico

    time.sleep(5)
    p_retico = Process(target=run_retico, daemon=True)
    p_retico.start()
    logging.info("Started retico")

    # agent running

    # while loop

    try:
        while True:
            if not action_server_to_brain_queue.empty():
                print(action_server_to_brain_queue.get_nowait())
            time.sleep(2)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()