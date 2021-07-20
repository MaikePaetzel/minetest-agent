import argparse
from multiprocessing import Queue, Process
import time
import requests

from aiohttp import web

import rasa.cli.run

from agent.droidlet_action_server import get_action_endpoint
from agent.droidlet_agent import Robo, run

import logging

from retico.core.audio.io import SpeakerModule, MicrophoneModule
from retico.dialogue.manager.rasa_http import RasaHTTP
from retico.modules.google.google_asr import GoogleASRModule
from retico.modules.gui_input.gui_input import GuiInputModule
from retico.modules.mozilla_tts.mozilla_tts import MozillaTTSHTTP, get_synthesizer_endpoint

from agent.droidlet_agent import MinetestWorld, Robo
import os



def run_retico():
    m_asr = GoogleASRModule()
    m_rasa = RasaHTTP()
    m_tts = MozillaTTSHTTP()
    m_speaker = SpeakerModule(m_tts.sample_rate)

    m_asr.subscribe(m_rasa)
    m_rasa.subscribe(m_tts)
    m_tts.subscribe(m_speaker)

    m_asr.setup()
    m_rasa.setup()
    m_tts.setup()
    m_speaker.setup()

    m_asr.run(run_setup=False)
    m_rasa.run(run_setup=False)
    m_tts.run(run_setup=False)
    m_speaker.run(run_setup=False)


def main():

    # run text synthesis server

    def run_synthesis_server_webapp():
        logging.basicConfig(level=logging.DEBUG)
        synthesizer_endpoint = get_synthesizer_endpoint()
        web.run_app(synthesizer_endpoint, port=5060, print=logging.info)

    p_synthesizer = Process(target=run_synthesis_server_webapp, daemon=True)
    p_synthesizer.start()
    print("run.main: started tts synthesis endpoint")

    # start rasa and action server

    action_server_to_brain_queue = Queue()
    action_server = get_action_endpoint(action_server_to_brain_queue)
    robo = Robo(action_server_to_brain_queue)

    # run rasa action server

    def run_action_server_webapp():
        logging.basicConfig(level=logging.DEBUG)
        web.run_app(action_server, port=5055, print=logging.info)

    p_rasa_actions = Process(target=run_action_server_webapp, daemon=True)
    p_rasa_actions.start()
    print("run.main: started action server")

    # run rasa dialogue manager

    def run_rasa():
        logging.basicConfig(level=logging.DEBUG)
        rasa_args = argparse.Namespace()
        rasa_args.endpoints = 'dialog_manager/rasa_dm/endpoints.yml'
        rasa_args.credentials = None
        rasa_args.remote_storage = None
        rasa_args.enable_api = True
        rasa_args.model = '/home/nrg/potsdam/embagent/minetest-agent/dialog_manager/rasa_dm/models/20210719-133830.tar.gz'
        rasa.cli.run.run(rasa_args)

    p_rasa = Process(target=run_rasa, daemon=True)
    p_rasa.start()
    print("run.main: starting rasa")

    # wait for rasa to load

    while True:
        try:
            print("run.main: waiting for rasa")
            requests.get("http://localhost:5005")
            print("run.main: rasa is ready")
            break
        except Exception:
            time.sleep(3)

    # run retico

    time.sleep(5)
    p_retico = Process(target=run_retico, daemon=True)
    p_retico.start()
    print("run.main: started retico")

    # agent running

    world = MinetestWorld(server="127.0.0.1", playername="Minehart", password="", port=29999)
    agent = Robo(action_server_to_brain_queue, world)

    # while loop

    while not agent._shutdown:
        try:
            #print("Stepping agent")
            agent.step()
        except Exception as e:
            print("run.main: got exception")
            print(e)
            agent.handle_exception(e)
        time.sleep(1)


if __name__ == "__main__":
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/nrg/potsdam/embagent/minetest-agent/creds.json"
    logging.basicConfig(level=logging.INFO)
    main()