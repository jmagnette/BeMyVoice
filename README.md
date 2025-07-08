# BeMyVoice
Project whose purpose is to provide a tool, in the form of a simple overlay, allowing people to enter text or command to generate sound that can then be streamed to a virtual microphone for example

The project currently supports only EdgeTTS.

# Dependencies
Even it is not mandatory, the app was written to output to a virtual microphone to bring the voice (tts generation) to any application. Targeted towards windows users, the free solution found was to use VB Audio. You can download the exe to install it here:
https://vb-audio.com/Cable/index.htm

# First steps
To install the app, just download the exe from the release tab.

At first run, the "config.json" file will be created next to the exe. It is in that file that you can parametrise what you want, which engine, voices, ...

The app also offers different commands that can be input in the overlay. Type "/help" to get the list of available commands.

The display shortcut can be set via the config file. The default is "ctrl+shift+plus".

The overlay offers different interactions:
- You can toggle the overlay by doing the shortcut. It can be hidden by pressing Escape while focused on it.
- If you type a text and type on Enter, the text is processed and the overlay stays open, to allow to chain texts. 
- If you press on "ctrl+enter", the text will be processed the same, but the overlay will close. 
- Pressing Up/Down in the text field allows to get the history of inputs that will replace the current text entry (up to 10 element of history). 
- You can chain multiple text and commands in one go, by separating them by a ";". This will result in the same as typing and entering them one by one, so they will be queued.

You can drag the overlay window by dragging the grey square. The position is not stored in the config file, it is just for the current session.

The command line and app language is English, to be able to be used by the many, but the voices chosen for the tts engine can be anything.

# Engines
## Edge TTS
Edge TTS is the Azure "free/demo" version. It supports only a subset of voices and can have some limitations. 
This TTS was chosen as it provides enough without having to configure too much on client side.

# Technicality
    Beware this was downgraded to python 3.12 as PyAudio and Pydub depends on audioop that was deprecated than removed in python 3.13. Once those libraries ar updated, feel free to updated to a more recent python distribution.

    For the pyAudio Wheel, if you are using a different version of python (than 3.12) or have a different system architecture, you can check :
    https://pypi.org/project/PyAudio/#files

# Support
If this app has helped you and allowed you to smile, don't hesitate to share it !

You can also share that smile with me on https://ko-fi.com/jmagnette (but no obligation to ! )