# BeMyVoice
Project whose purpose is to provide a tool, in the form of a simple overlay, allowing people to enter text or command to generate sound that can then be streamed to a virtual microphone for example

Beware this was downgraded to python 3.12 as PyAudio and Pydub depends on audioop that was deprecated than removed in python 3.13. Once those libraries ar updated, feel free to updated to a more recent python distribution.

For the pyAudio Wheel, if you are using a different version of python (than 3.12) or have a different system architecture, you can check :
https://pypi.org/project/PyAudio/#files