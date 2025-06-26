import tempfile
import edge_tts
from pydub import AudioSegment


class EdgeTTS:
    def __init__(self, configuration, *args):
        self.config = configuration
        self.voice_dict = self.config["Voices"]
        self.current_key, self.current_voice = self.voice_dict.items()[0]

    async def synthesize(self, text):
        temp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        temp.close()
        communicate = edge_tts.Communicate(text=text, voice=self.current_voice)
        await communicate.save(temp.name)
        audio = AudioSegment.from_mp3(temp.name)
        temp_wav = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        temp_wav.close()
        audio.export(temp_wav.name, format="wav")

        return temp_wav

