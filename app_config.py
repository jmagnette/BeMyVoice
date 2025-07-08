import json


class AppConfig:
    DEFAULT_CONFIG = {
        "engine": {
            "tts_engine": "edgeTTS",
            "voices": [
                {"key": "fr-f", "voice":"fr-FR-DeniseNeural"},
                {"key": "fr-h", "voice":"fr-FR-HenriNeural"}
            ]
        },
        "outputs": [
            "default"
        ],
        "hotkeys": {
            "toggle_overlay": "ctrl+shift+plus"
        },
        "overlay": {
            "x": 100,
            "y": 100,
            "width": 400,
            "height": 100
        }
    }


    def __init__(self, config_file_path):
        self.config_path = config_file_path
        self.loaded_config = self.DEFAULT_CONFIG

    @property
    def engine_config(self):
        return self.loaded_config["engine"]

    @property
    def outputs_config(self):
        return self.loaded_config["outputs"]

    @property
    def hotkeys_config(self):
        return self.loaded_config["hotkeys"]

    @property
    def overlay_config(self):
        return self.loaded_config["overlay"]


    def load_config(self):
        try:
            # Try to load existing settings
            with open(self.config_path, "r") as f:
                self.loaded_config = json.load(f)

        except FileNotFoundError:
            with open(self.config_path, "w") as f:
                json.dump(self.DEFAULT_CONFIG, f, indent=4)
