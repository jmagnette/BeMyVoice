import threading

import asyncio
import time
import tkinter as tk
import keyboard
import logger
from app_config import AppConfig
from tts.edge import EdgeTTS
from interpreter.command_interpreter import CommandInterpreter
from interpreter.tts_interpreter import TtsInterpreter
from soundplayer.multi_output_player import MultiOutputPlayer


def start_async_loop(app):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    app.loop = loop
    app.queue = asyncio.Queue()
    loop.create_task(app.worker())
    loop.run_forever()


class BeMyVoice:
    ENGINE_DICT = {
        "edgeTTS": EdgeTTS
    }


    def __init__(self, config_path):
        self.app_config = AppConfig(config_path)
        self.app_config.load_config()

        self._init_engine(self.app_config.engine_config)
        self._init_sound_player()
        self._init_interpreters()

        # overlay init
        self.root = None
        self.entry = None
        self.offset_x = 0
        self.offset_y = 0
        self._create_overlay_window()

        self.loop = None
        self.queue = None
        self.interrupted = False

    def _init_engine(self, engine_config):
        try:
            engine_type = self.ENGINE_DICT[engine_config["tts_engine"]]
            self.tts_engine = engine_type(engine_config)
        except KeyError:
            logger.log_error(f"incorrect engine key defined in config file. Supported engine are [{', '.join(self.ENGINE_DICT.keys())}]")
            raise

    def _init_sound_player(self):
        self.sound_player = MultiOutputPlayer(self.app_config.outputs_config)

    def _init_interpreters(self):
        self.tts_interpreter = TtsInterpreter(self.tts_engine, self.sound_player)
        self.command_interpreter = CommandInterpreter(self.tts_engine, self.sound_player)

    def _create_overlay_window(self):
        self.root = tk.Tk()
        self.root.attributes("-topmost", True)
        self.root.overrideredirect(True)  # Hide window frame

        overlay_config = self.app_config.overlay_config
        self.root.geometry(f"{overlay_config["width"]}x{overlay_config["height"]}+{overlay_config["x"]}+{overlay_config["y"]}")
        self.root.withdraw()

        self.entry = tk.Entry(self.root, font=("Segoe UI", 16))
        self.entry.pack(padx=20, pady=30, fill="both", expand=True)

        self.entry.bind("<Return>", self._on_enter)
        self.entry.bind("<Control-Return>", self._on_ctrl_enter)

        self.root.bind("<Escape>", lambda e: self.hide_overlay())
        self.root.bind("<Button-1>", self._start_move)
        self.root.bind("<B1-Motion>", self._do_move)

    def toggle_overlay(self):
        if self.root.state() == "withdrawn":
            self.show_overlay()
        else:
            self.hide_overlay()

    def show_overlay(self):
        self.root.deiconify()
        self.root.lift()
        self.entry.focus_set()

    def hide_overlay(self):
        self.root.withdraw()

    def _start_move(self, event):
        self.offset_x = event.x
        self.offset_y = event.y

    def _do_move(self, event):
        x = self.root.winfo_x() + event.x - self.offset_x
        y = self.root.winfo_y() + event.y - self.offset_y
        self.root.geometry(f"+{x}+{y}")

    def _on_enter(self, event=None):
        self._handle_input()
        self.entry.delete(0, tk.END)
        self.hide_overlay()

    def _on_ctrl_enter(self, event=None):
        self._handle_input()
        self.entry.delete(0, tk.END)
        # Overlay stays visible

    def _interrupt(self):
        logger.log_info("[TTS] Interrupt received — clearing queue")
        self.interrupted = True
        while not self.queue.empty():
            try:
                self.queue.get_nowait(); self.queue.task_done()
            except:
                break

        self.interrupted = False

    async def worker(self):
        while True:
            entry = await self.queue.get()

            if self.interrupted:
                self.queue.task_done()
                continue

            if entry.strip().startswith("/"):
                await self.command_interpreter.handle_entry(entry.strip())
            else:
                await self.tts_interpreter.handle_entry(entry.strip())

            self.queue.task_done()

    def _handle_input(self):
        user_input = self.entry.get()

        if user_input.strip() == "/stop":
            self._interrupt()
        else:
            entries = user_input.split(";")
            for entry in entries:
                try:
                    asyncio.run_coroutine_threadsafe(self.queue.put(entry), self.loop)
                except RuntimeError:
                    logger.log_error("⚠️ Async loop not running — cannot send item.")

    def run_infinite(self):
        logger.log_info("✅ Type-to-Speak Overlay running.")
        toggle_hotkey = self.app_config.hotkeys_config["toggle_overlay"]
        keyboard.add_hotkey(toggle_hotkey, self.toggle_overlay)
        logger.log_info(f"💡 Press '{toggle_hotkey}' to toggle the overlay window.")
        logger.log_info("🛑 Press Ctrl+C in terminal to quit.")

        threading.Thread(target=start_async_loop, args=(self,), daemon=True).start()
        self.root.mainloop()