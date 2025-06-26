class CommandInterpreter:

    def __init__(self, tts_engine, sound_player, configuration):
        self.tts_engine = tts_engine
        self.sound_player = sound_player
        self.config = configuration

    async def handle_entry(self, text_entry):
        # handle the command, knowing the / is still in the entry
        pass