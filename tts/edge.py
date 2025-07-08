import os
import tempfile
import edge_tts
from pydub import AudioSegment

import logger


class EdgeTTS:
    EXAMPLE_CONFIG = {
            "tts_engine": "edgeTTS",
            "voices": [
                {"key": "fr-f", "voice":"fr-FR-DeniseNeural"},
                {"key": "fr-h", "voice":"fr-FR-HenriNeural"}
            ]
        }

    def __init__(self, configuration, *args):
        self.config = configuration
        self.voice_dict = {x["key"]: x for x in self.config["voices"]}
        self.current_key = self.config["voices"][0]["key"]
        self.current_voice = self.voice_dict[self.current_key]["voice"]

    def change_voice(self, voice_key):
        try:
            self.current_voice = self.voice_dict[voice_key]["voice"]
            self.current_key = voice_key
        except KeyError:
            logger.log_error(f"The given voice key '{voice_key}' does not exist in the configs.")

    async def synthesize(self, text):
        temp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        temp.close()
        communicate = edge_tts.Communicate(text=text, voice=self.current_voice)
        await communicate.save(temp.name)
        audio = AudioSegment.from_mp3(temp.name)
        temp_wav = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        temp_wav.close()
        audio.export(temp_wav.name, format="wav")

        os.remove(temp.name)

        return temp_wav.name

