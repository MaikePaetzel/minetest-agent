import threading
import pyaudio
import queue
from google.cloud import speech
import google.api_core.exceptions as gexceptions
from retico.core import abstract
from retico.core.text.common import SpeechRecognitionIU
from retico.core.audio.common import AudioIU


# Audio recording parameters
RATE = 16000
CHUNK = int(RATE / 10)  # 100ms


class MicrophoneStream(object):
    """Opens a recording stream as a generator yielding the audio chunks."""

    def __init__(self, rate, chunk):
        self._rate = rate
        self._chunk = chunk

        # Create a thread-safe buffer of audio data
        self._buff = queue.Queue()
        self.closed = True

    def __enter__(self):
        self._audio_interface = pyaudio.PyAudio()
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,
            # The API currently only supports 1-channel (mono) audio
            # https://goo.gl/z757pE
            channels=1,
            rate=self._rate,
            input=True,
            frames_per_buffer=self._chunk,
            # Run the audio stream asynchronously to fill the buffer object.
            # This is necessary so that the input device's buffer doesn't
            # overflow while the calling thread makes network requests, etc.
            stream_callback=self._fill_buffer,
        )

        self.closed = False

        return self

    def __exit__(self, type, value, traceback):
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        # Signal the generator to terminate so that the client's
        # streaming_recognize method will not block the process termination.
        self._buff.put(None)
        self._audio_interface.terminate()

    def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
        """Continuously collect data from the audio stream, into the buffer."""
        self._buff.put(in_data)
        return None, pyaudio.paContinue

    def generator(self):
        while not self.closed:
            # Use a blocking get() to ensure there's at least one chunk of
            # data, and stop iteration if the chunk is None, indicating the
            # end of the audio stream.
            chunk = self._buff.get()
            if chunk is None:
                return
            data = [chunk]

            # Now consume whatever other data's still buffered.
            while True:
                try:
                    chunk = self._buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                    print(len(data))
                except queue.Empty:
                    break

            yield b"".join(data)




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
        #print("ASR Processing IU")
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


    def _produce_predictions_loop(self, responses):
        for response in responses:
            p, t, s, c, f = self._extract_results(response)
            if p:
                output_iu = self.create_iu(self.latest_input_iu)
                self.latest_input_iu = None
                output_iu.set_asr_results(p, t, s, c, f)
                if f:
                    output_iu.committed = True
                self.append(output_iu)

    def setup(self):
        pass

    def prepare_run(self):
        def run():
            language_code = "en-US"  # a BCP-47 language tag
            while True:
                try:
                    client = speech.SpeechClient()
                    config = speech.RecognitionConfig(
                        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                        sample_rate_hertz=RATE,
                        language_code=language_code,
                    )

                    streaming_config = speech.StreamingRecognitionConfig(
                        config=config, interim_results=True
                    )

                    with MicrophoneStream(RATE, CHUNK) as stream:
                        print("stream initialized", flush=True)
                        audio_generator = stream.generator()
                        requests = (
                            speech.StreamingRecognizeRequest(audio_content=content)
                            for content in audio_generator
                        )

                        responses = client.streaming_recognize(streaming_config, requests)

                        # Now, put the transcription responses to use.
                        self._produce_predictions_loop(responses)

                except gexceptions.OutOfRange:
                    print("Got OutOfRange exception: restarting asr processing")
                    pass


        print("start thread", flush=True)
        t = threading.Thread(target=run)
        print("Starting gspeech", flush=True)
        t.start()

    def shutdown(self):
        self.audio_buffer.put(None)