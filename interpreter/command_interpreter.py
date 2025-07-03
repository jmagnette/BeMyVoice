import logger


class CommandInterpreter:

    def __init__(self, tts_engine, sound_player, interrupt):
        self.tts_engine = tts_engine
        self.sound_player = sound_player
        self.interrupt = interrupt

        self._command_mapping = {
            "/stop": (None, "stops the current playback and empty the queue of commands/tts"),  #handled before in the pipeline
            "/help": (self._display_help, "displays the help text to list commands and explain the app expected input"),
            "/listOutputs": (self._list_output_devices, "lists all output devices available to help fill the config file")
        }

    async def handle_entry(self, text_entry):
        # handle the command, knowing the / is still in the entry
        try:
            action, doc = self._command_mapping[text_entry.strip()]
            action(text_entry)
        except KeyError:
            logger.log_error(f"Unknown command {text_entry}")

    def _display_help(self, *args):
        logger.log_info("I should output help doc")
        help_doc = (f"This program handles the text entry provided depending on the text ans config."
                    f"\nDifferent text/commands can be given in one go by separating them using ';'."
                    f"\nFor example '/help;Hello world'. Every text that doesn't start with a forward slash will be threated by the tts_engine to be synthesized."
                    f"\nThe available commands are:")
        for k,v in self._command_mapping.items():
            help_doc += f"\n\t- {k}: {v[1]}"
        logger.log_info(help_doc)

    def _list_output_devices(self, *args):
        devices = self.sound_player.get_audio_devices()
        devices_as_string = "".join(f"\n\t{v}. {k}" for k,v in devices.items())
        logger.log_info(f"Available output devices are:{devices_as_string}")
