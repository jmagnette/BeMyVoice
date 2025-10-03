import os
import sys
import logger


# Load configuration
if getattr(sys, 'frozen', False):
    # Running as EXE
    base_path = os.path.dirname(sys.executable)
else:
    # Running as script
    base_path = os.path.abspath(".")

CONFIG_PATH = os.path.join(base_path, "config.json")


install_path = os.path.abspath(".")
ffmpeg_path = os.path.join(install_path, "dependencies", "ffmpeg")
os.environ["PATH"] = ffmpeg_path + os.pathsep + os.environ.get("PATH", "")


from be_my_voice import BeMyVoice


if __name__ == '__main__':
    try:
        app = BeMyVoice(CONFIG_PATH, os.path.join(base_path, "resources"))
        app.run_infinite()
    except Exception as ex:
        logger.log_error(ex)
        input("\nPress Enter to exit...")