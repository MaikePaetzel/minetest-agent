import logging
import sys

from retico.core.audio.io import SpeakerModule
from retico.dialogue.manager.rasa_http import RasaHTTP
from retico.modules.huggingface.asr import HuggingfaceASRModule
from retico.modules.mozilla_tts.mozilla_tts import MozillaTTS
from retico.modules.wavplayer.wavplayer import WavplayerModule


def huggingface_asr():
    sound_files = [
        "assets/audio/retico_test/hello.wav",
        "assets/audio/retico_test/move_wooden_block.wav",
        "assets/audio/retico_test/stop.wav",
    ]
    m1 = WavplayerModule(sound_files, 5)
    m11 = SpeakerModule(22050)
    m2 = HuggingfaceASRModule() # en-US or de-DE or ....
    #m3 = CallbackModule(callback=lambda x: print("%s: %s (%f) - %s" % ("CallbackModule", x.text, x.stability, x.final)))
    m4 = RasaHTTP()
    m5 = MozillaTTS()
    #m6 = AudioDispatcherModule(5000, m5.sample_rate)
    #m6 = DelayedNetworkModule(1)
    m7 = SpeakerModule(m5.sample_rate)

    m1.subscribe(m2)
    m1.subscribe(m11)
    #m2.subscribe(m3)
    m2.subscribe(m4)
    m4.subscribe(m5)
    m5.subscribe(m7)
    #m6.subscribe(m7)

    m1.setup()
    m11.setup()
    m2.setup()
    #m3.setup()
    m4.setup()
    m5.setup()
    #m6.setup()
    m7.setup()

    logging.info("All setup")

    m1.run(run_setup=False)
    m11.run(run_setup=False)
    m2.run(run_setup=False)
    #m3.run(run_setup=False)
    m4.run(run_setup=False)
    m5.run(run_setup=False)
    #m6.run(run_setup=False)
    m7.run(run_setup=False)

    input()

    m1.stop()
    m11.stop()
    m2.stop()
    #m3.stop()
    m4.stop()
    m5.stop()
    #m6.stop()
    m7.stop()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    if sys.argv[1] == "huggingface_asr":
        huggingface_asr()
