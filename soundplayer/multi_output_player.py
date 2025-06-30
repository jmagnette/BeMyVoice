import pyaudio

import logger


class MultiOutputPlayer:

    def __init__(self, configuration):
        self.config = configuration
        self.output_devices = []

        # checking settings
        available_devices = self.get_audio_devices()
        is_in_error = False
        for device_name in self.config:
            if device_name != "default" and device_name != "file" and device_name not in available_devices.keys():
                is_in_error = True
                logger.log_error(f"Config output device '{device_name}' is not present")

        if is_in_error:
            raise "Issue with config regarding outputs"

    def get_audio_devices(self):
        p = pyaudio.PyAudio()
        devices = {}
        for i in range(p.get_device_count()):
            info = p.get_device_info_by_index(i)
            if info['maxOutputChannels'] > 0:  # Filter for output-capable devices
                devices[info['name']] = i
        p.terminate()
        return devices