class TtsInterpreter:
    def __init__(self, tts_engine, sound_player):
        self.tts_engine = tts_engine
        self.sound_player = sound_player

    async def handle_entry(self, text_entry):
        # handle the entry for tts
        pass