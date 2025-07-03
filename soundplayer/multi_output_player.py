import os.path
import time

import pyaudio
import wave
import logger


class MultiOutputPlayer:

    def __init__(self, configuration, interrupt):
        self.config = configuration
        self.interrupt = interrupt

        # checking settings
        available_devices = self.get_audio_devices()
        is_in_error = False
        for device_name in self.config:
            if device_name != "default" and device_name != "file" and device_name not in available_devices.keys():
                is_in_error = True
                logger.log_error(f"Config output device '{device_name}' is not present")

        if is_in_error:
            raise "Issue with config regarding outputs"

    async def play_audio_async(self, wave_file_path):
        p = pyaudio.PyAudio()
        try:
            available_devices = self.get_audio_devices()
            streams = []
            for device_name in self.config:
                wf = wave.open(wave_file_path, 'rb')
                device_info = None
                if device_name == "default":
                    device_info = p.get_default_output_device_info()

                elif device_name == "file":
                    # That's for later, but basically, it should just write in file next to exe
                    continue

                else:
                    device_index = available_devices[device_name]
                    device_info = p.get_device_info_by_index(device_index)

                streams.append(self._create_and_read_audio_stream(wf, p, int(device_info['index'])))

            while any(stream.is_active() for stream in streams) and not self.interrupt.must_stop:
                time.sleep(0.1)

            for stream in streams:
                stream.stop_stream()
                stream.close()

        finally:
            p.terminate()

    def get_audio_devices(self):
        p = pyaudio.PyAudio()
        try:

            devices = {}
            for i in range(p.get_device_count()):
                info = p.get_device_info_by_index(i)
                if info['maxOutputChannels'] > 0:  # Filter for output-capable devices
                    devices[info['name']] = i
            return devices
        finally:
            p.terminate()

    def _create_and_read_audio_stream(self, wf, p, device_index):
        def callback(in_data, frame_count, time_info, status):
            data = wf.readframes(frame_count)
            return (data, pyaudio.paContinue)

        stream = p.open(
            format=p.get_format_from_width(wf.getsampwidth()),
            channels=wf.getnchannels(),
            rate=wf.getframerate(),  # Use audio file's rate for now
            output=True,
            output_device_index=device_index,
            stream_callback=callback
        )

        return stream
