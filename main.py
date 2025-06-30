import os
import sys
from pydub import AudioSegment
from pydub.utils import which

import logger

# Load configuration
if getattr(sys, 'frozen', False):
    # Running as EXE
    base_path = os.path.dirname(sys.executable)
else:
    # Running as script
    base_path = os.path.abspath(".")

CONFIG_PATH = os.path.join(base_path, "config.json")
AudioSegment.converter = which(os.path.join(base_path,"dependencies", "ffmpeg.exe"))


from be_my_voice import BeMyVoice


if __name__ == '__main__':
    try:
        app = BeMyVoice(CONFIG_PATH)
        app.run_infinite()
    except Exception as ex:
        logger.log_error(ex)
        input("\nPress Enter to exit...")