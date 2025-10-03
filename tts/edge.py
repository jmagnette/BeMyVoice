import os
import tempfile
import edge_tts
from pydub import AudioSegment
import soundfile as sf

import logger


class EdgeTTS:
    EXAMPLE_CONFIG = {
            "tts_engine": "edgeTTS",
            "voices": [
                {"key": "fr-f", "voice":"fr-FR-DeniseNeural", "pitch":0, "speed":1},
                {"key": "fr-h", "voice":"fr-FR-HenriNeural", "pitch":0, "speed":1}
            ]
        }

    def __init__(self, configuration, *args):
        self.config = configuration
        self.voice_dict = {x["key"]: x for x in self.config["voices"]}
        self.current_key = self.config["voices"][0]["key"]
        self.current_voice = self.voice_dict[self.current_key]["voice"]
        self.current_pitch = float(self.voice_dict[self.current_key].get("pitch", 0))
        self.current_speed = float(self.voice_dict[self.current_key].get("speed", 1))

    async def get_all_voices_async(self):
        voices = await edge_tts.list_voices()
        return [voice['ShortName'] for voice in voices]

    def change_voice(self, voice_key):
        try:
            self.current_voice = self.voice_dict[voice_key]["voice"]
            self.current_pitch = float(self.voice_dict[voice_key].get("pitch", 0))
            self.current_speed = float(self.voice_dict[voice_key].get("speed", 1))
            self.current_key = voice_key
        except KeyError:
            logger.log_error(f"The given voice key '{voice_key}' does not exist in the configs.")

    async def change_voice_name_async(self, voice_name):
        voices = await edge_tts.list_voices()
        if voice_name not in (voice['ShortName'] for voice in voices):
            logger.log_error(f"The given voice name '{voice_name}' does not exist for the current engine.")
            return
        self.current_voice = voice_name

    async def synthesize(self, text):
        temp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        temp.close()

        # Prepare text as ssml to support Pitch and Speed without postprocessing, that gives a weird result

        # current speed is a multiplier from 0 to x, where 1 is 100%
        rate = int(self.current_speed * 100.0 - 100)

        # semitone to Hz modifier, 15Hz is taken as a rough approx
        pitch = int(15 * self.current_pitch)

        communicate = edge_tts.Communicate(text=text, rate=f"{rate:+d}%", pitch=f"{pitch:+d}Hz", voice=self.current_voice)
        await communicate.save(temp.name)
        audio = AudioSegment.from_mp3(temp.name)
        temp_wav = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        temp_wav.close()
        audio.export(temp_wav.name, format="wav")

        os.remove(temp.name)

        return temp_wav.name

    def save_current_config(self):
        for entry in self.config["voices"]:
            if entry["key"] == self.current_key:
                entry["voice"] = self.current_voice
                entry["pitch"] = self.current_pitch
                entry["speed"] = self.current_speed

