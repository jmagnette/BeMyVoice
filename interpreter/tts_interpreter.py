import os


class TtsInterpreter:
    def __init__(self, tts_engine, sound_player, interrupt):
        self.tts_engine = tts_engine
        self.sound_player = sound_player
        self.interrupt = interrupt

    async def handle_entry(self, text_entry):
        if len(text_entry) == 0:
            return

        output_wave = await self.tts_engine.synthesize(text_entry)
        try:
            if not self.interrupt.must_stop:
                await self.sound_player.play_audio_async(output_wave)
        finally:
            if output_wave:
                os.remove(output_wave)