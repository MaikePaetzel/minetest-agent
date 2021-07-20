from retico.core.audio.io import SpeakerModule, MicrophoneModule
#from retico.dialogue.manager.rasa_http import RasaHTTP
#from retico.modules.google.asr import GoogleASRModule
from retico.modules.google.google_asr import GoogleASRModule
#from retico.modules.gui_input.gui_input import GuiInputModule
#from retico.modules.mozilla_tts.mozilla_tts import MozillaTTS
#from retico.core.debug.console import DebugModule
import os
import time

def run():
    #m_mic = MicrophoneModule(1200)
    print("create asr", flush=True)
    m_asr = GoogleASRModule()
    print("created asr", flush=True)
    #m_debug = DebugModule()

    #m_mic.subscribe(m_asr)
    #m_asr.subscribe(m_debug)

    #m_mic.setup()
    #m_asr.setup()
    #m_debug.setup()

    #print("running mic")
    #m_mic.run()
    #print("run mic")

    m_asr.run()
    print("run asr", flush=True)
    #m_debug.run()

    print("running", flush=True)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/nrg/potsdam/embagent/minetest-agent/creds.json"
    run()