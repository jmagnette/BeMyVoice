import threading
import os
import asyncio
import tkinter as tk
from PIL import Image, ImageTk
import keyboard
import logger
from app_config import AppConfig
from status import Status
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


    def __init__(self, config_path, resources_path):
        self.history = []
        self.history_index = -1
        self.resources_path = resources_path
        self.app_config = AppConfig(config_path)
        self.app_config.load_config()

        self.status = Status()
        self.status.must_stop = False

        self._init_engine(self.app_config.engine_config)
        self._init_sound_player()
        self._init_interpreters()

        # overlay init
        self.root = None
        self.drag_handle = None
        self.entry = None
        self.offset_x = 0
        self.offset_y = 0
        self._create_overlay_window()

        self.loop = None
        self.queue = None

    def _init_engine(self, engine_config):
        try:
            engine_type = self.ENGINE_DICT[engine_config["tts_engine"]]
            self.tts_engine = engine_type(engine_config)
        except KeyError:
            logger.log_error(f"incorrect engine key defined in config file. Supported engine are [{', '.join(self.ENGINE_DICT.keys())}]")
            raise

    def _init_sound_player(self):
        self.sound_player = MultiOutputPlayer(self.app_config.outputs_config, self.status)

    def _init_interpreters(self):
        self.tts_interpreter = TtsInterpreter(self.tts_engine, self.sound_player, self.status)
        self.command_interpreter = CommandInterpreter(self.tts_engine, self.sound_player, self.status, self.ENGINE_DICT, self.app_config)

    def _create_overlay_window(self):
        self.root = tk.Tk()
        self.root.attributes("-topmost", True)
        self.root.overrideredirect(True)  # Hide window frame

        overlay_config = self.app_config.overlay_config
        self.root.geometry(f"{overlay_config["width"]}x{overlay_config["height"]}+{overlay_config["x"]}+{overlay_config["y"]}")
        self.root.withdraw()

        # Frame to hold everything on one line
        self.entry_frame = tk.Frame(self.root)
        self.entry_frame.pack(fill="x", padx=5, pady=5)

        self.drag_handle = tk.Frame(self.entry_frame, width=30, height=30)
        self.drag_handle.pack(side="left")

        image = Image.open(os.path.join(self.resources_path, "ArrowCross.png")).convert("RGBA")
        image = image.resize((30, 30), Image.LANCZOS)
        bg_color = (240, 240, 240, 255)  # RGBA for 'gray' background
        bg = Image.new("RGBA", image.size, bg_color)
        bg.paste(image, (0, 0), image)

        self.move_image = ImageTk.PhotoImage(image)

        self.move_label = tk.Label(self.drag_handle, image=self.move_image, bd=0)
        self.move_label.pack(expand=False)

        self.entry = tk.Entry(self.entry_frame, font=("Segoe UI", 16))
        self.entry.pack(side="left", fill="x", padx=5, expand=True)

        self.status_canvas = tk.Canvas(self.entry_frame, width=30, height=30, highlightthickness=0)
        self.status_canvas.pack(side="right")
        # Draw the circle and store its id
        self.status_circle = self.status_canvas.create_oval(
            5, 5, 25, 25, fill="green", outline=""
        )
        self.update_status(False)

        self.entry.bind("<Return>", self._on_enter)
        self.entry.bind("<Control-Return>", self._on_ctrl_enter)
        self.entry.bind("<Up>", self._on_up)
        self.entry.bind("<Down>", self._on_down)

        self.root.bind("<Escape>", lambda e: self.hide_overlay())
        self.move_label.bind("<Button-1>", self._start_move)
        self.move_label.bind("<B1-Motion>", self._do_move)

    def toggle_overlay(self):
        if self.root.state() == "withdrawn":
            self.show_overlay()
        else:
            self.hide_overlay()

    def update_status(self, is_busy):
        self.status.is_busy = is_busy
        # Change color depending on state
        new_color = "red" if is_busy else "green"
        self.status_canvas.itemconfig(self.status_circle, fill=new_color)

    def show_overlay(self):
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()
        self.entry.focus_set()
        self.entry.after(100, self.entry.focus_force)

    def hide_overlay(self):
        self.root.withdraw()

    def _start_move(self, event):
        self.offset_x = event.x
        self.offset_y = event.y

    def _do_move(self, event):
        x = self.root.winfo_x() + event.x - self.offset_x
        y = self.root.winfo_y() + event.y - self.offset_y
        self.root.geometry(f"+{x}+{y}")

    def _on_down(self, event=None):
        if self.history_index != -1 and self.history_index < len(self.history) - 1:
            self.history_index += 1
        else:
            self.history_index = -1
        self._set_text_from_history()

    def _on_up(self, event=None):
        if self.history_index < 0:
            self.history_index = len(self.history) - 1
        elif self.history_index > 0:
            self.history_index -= 1
        self._set_text_from_history()

    def _set_text_from_history(self):
        self.entry.delete(0, tk.END)
        if self.history_index >= 0:
            self.entry.insert(tk.END, self.history[self.history_index])

    def _on_enter(self, event=None):
        self._handle_input()
        self.entry.delete(0, tk.END)
        # Overlay stays visible

    def _on_ctrl_enter(self, event=None):
        self._handle_input()
        self.entry.delete(0, tk.END)
        self.hide_overlay()

    def _interrupt(self):
        logger.log_info("[TTS] Interrupt received — clearing queue")
        self.status.must_stop = True
        while not self.queue.empty():
            try:
                self.queue.get_nowait(); self.queue.task_done()
            except:
                break

    async def worker(self):
        while True:
            entry = await self.queue.get()
            self.update_status(True)

            if self.status.must_stop:
                self.queue.task_done()
                continue

            try:
                if entry.strip().startswith("/"):
                    await self.command_interpreter.handle_entry(entry.strip())
                else:
                    await self.tts_interpreter.handle_entry(entry.strip())

            except Exception as ex:
                logger.log_error(f"Unexpected error in worker: {ex}")

            finally:
                self.queue.task_done()
                self.update_status(False)

    def _handle_input(self):
        self.status.must_stop = False
        user_input = self.entry.get()
        self.history.append(user_input)
        self.history = self.history[-10:]
        self.history_index = -1

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

        threading.Thread(target=start_async_loop, args=(self,), daemon=True).start()
        self.root.mainloop()