import json
import os
import signal

import logger

class CommandInterpreter:

    def __init__(self, tts_engine, sound_player, status, available_engines, app_config):
        self.tts_engine = tts_engine
        self.sound_player = sound_player
        self.status = status
        self.app_config = app_config
        self._available_engines = available_engines

        self._command_mapping = {
            "/stop": (None, "stops the current playback and empty the queue of commands/tts"),  #handled before in the pipeline
            "/exit": (self._stop_app, "Stops the application"),
            "/help": (self._display_help, "displays the help text to list commands and explain the app expected input"),
            "/listOutputs": (self._list_output_devices, "lists all output devices available to help fill the config file"),
            "/listVoices": (self._list_engine_voices, "lists all available voices for the current engine tts, to help fill the config file"),
            "/voice": (self._change_engine_voice, "Changes the current used tts voice by giving a key that must be present in the config.json file"),
            "/helpEngine": (self._example_config_for_engine, "For a given engine argument, gives an example config to put in the config.json file"),
            "/setOutputs": (self._set_output_devices, "Force the usage of output devices, using index separated by comma. This Bypass the original config"),
            "/voiceName": (self._change_engine_voice_name, "Allows to temporary change the voice key used by the TTS Engine"),
            "/voicePitch": (self._change_engine_voice_pitch, "Allows to temporary change the voice pitch used by the TTS Engine (value positive for higher pitch, negative for lower pitch"),
            "/voiceSpeed": (self._change_engine_voice_speed, "Allows to temporary change the voice speed used by the TTS Engine (speed multiplier (ex 1.5 to speed up by 50%)"),
            "/saveConfig": (self._save_config, "Allows to write the config file with the current voice settings and outputs")
        }

    async def handle_entry(self, text_entry):
        # handle the command, knowing the / is still in the entry
        try:
            entries = [entry.strip() for entry in text_entry.strip().split(" ")]
            action, doc = self._command_mapping[entries[0]]
            await action(*entries[1:])
        except (KeyError, IndexError):
            logger.log_error(f"Unknown command {text_entry}")

    async def _display_help(self, *args):
        help_doc = (f"This program handles the text entry provided depending on the text ans config."
                    f"\nDifferent text/commands can be given in one go by separating them using ';'."
                    f"\nFor example '/help;Hello world'. Every text that doesn't start with a forward slash will be threated by the tts_engine to be synthesized."
                    f"\nThe available commands are:")
        for k,v in self._command_mapping.items():
            help_doc += f"\n\t- {k}: {v[1]}"
        logger.log_info(help_doc)

    async def _stop_app(self, *args):
        os.kill(os.getpid(), signal.SIGTERM)

    async def _list_output_devices(self, *args):
        devices = self.sound_player.get_audio_devices()
        devices_as_string = "".join(f"\n\t{v}. {k}" for k,v in devices.items())
        logger.log_info(f"Available output devices are:{devices_as_string}")

    async def _list_engine_voices(self, *args):
        voices = await self.tts_engine.get_all_voices_async()
        voices_as_string = "".join(f"\n\t{voice}" for voice in voices)
        logger.log_info(f"Available voices for current engine ({self.tts_engine.EXAMPLE_CONFIG["tts_engine"]}) are:{voices_as_string}")

    async def _change_engine_voice(self, *args):
        try:
            voice_key = args[0]
            self.tts_engine.change_voice(voice_key)
        except IndexError:
            logger.log_warn(f"This command requires an argument. The possible voices keys (one to be given as argument) are [{', '.join(self.tts_engine.voice_dict.keys())}]")

    async def _change_engine_voice_name(self, *args):
        try:
            voice_name = args[0]
            await self.tts_engine.change_voice_name_async(voice_name)
        except IndexError:
            logger.log_warn(f"This command requires an argument. The possible voices keys (one to be given as argument) are [{', '.join(self.tts_engine.voice_dict.keys())}]")

    async def _change_engine_voice_pitch(self, *args):
        try:
            pitch = float(args[0])
            self.tts_engine.current_pitch = pitch
        except (IndexError, ValueError):
            logger.log_warn(f"This command requires an argument. The value given must be a valid float (like 1.5) positive or negative (eg -1.5)")

    async def _change_engine_voice_speed(self, *args):
        try:
            speed = float(args[0])
            if speed <= 0:
                raise ValueError
            self.tts_engine.current_speed = speed
        except (IndexError, ValueError):
            logger.log_warn(f"This command requires an argument. The value given must be a valid positive float (like 1.5)")

    async def _example_config_for_engine(self, *args):
        config_engine = None
        try:
            engine = args[0]
            config_engine = self._available_engines[engine]
        except (KeyError, IndexError):
            pass

        if not config_engine:
            logger.log_warn(f"This command requires an argument. The possible engines (and arguments) are [{', '.join(self._available_engines.keys())}]")
        else:
            doc = f"The engine '{engine}' expects a config of the form :\n"
            doc += json.dumps(config_engine.EXAMPLE_CONFIG, indent=2)
            logger.log_info(doc)

    async def _set_output_devices(self, *args):
        try:
            output_indexes = args[0].split(',')
            output_devices = self.sound_player.get_audio_devices()
            new_output_device_names = [k for k,v in output_devices.items() if f"{v}" in output_indexes]

            if "default" in output_indexes:
                new_output_device_names.insert(0, "default")

            if new_output_device_names:
                await self.sound_player.change_output_devices(*new_output_device_names)
            else:
                logger.log_warn(f"No change applied as the output indexes could not be mapped ({output_indexes})")

        except IndexError:
            logger.log_warn(f"This command requires an argument. You need to input output device index values, separated by a comma. To know which output devices are available, use '/listOutputs' ")

    async def _save_config(self, *args):
        self.tts_engine.save_current_config()
        self.app_config.save_config()
