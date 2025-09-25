import configparser # TODO: ADD FORMATTERS, DONE? TEST, NEED NEXT FUNCTIONS, VERY GOOD
import threading
import time
import sys
from queue import Queue, Empty

if sys.platform.startswith("win"):
    import msvcrt
else:
    import termios
    import tty
    import select

actual_print = print
buffer = ""

def print(*v, sep = " ", end = "\n", flush = False) -> None:
    global buffer
    buffer += sep.join(v) + end
    if flush:
        print_buffer()

def print_buffer():
    global buffer
    actual_print(buffer, end="")
    buffer = ""

class Theme:
    def __init__(self, path: str):
        self.path = path
        self.storage = configparser.ConfigParser()
        self.storage.read(self.path)

        self.current = self.storage["DEFAULT"]["current_theme"]
        self.load_theme(self.current)
        
    def load_theme(self, name: str): # loads current theme into theme object's variables
        for key, value in self.storage[name].items():
            if key == "current_theme": # breaks b/c DEFAULT propagates everywhere
                continue
            elif key == "background":
                setattr(self, f"col_{key}", self.get_termcol(self.rgb_str_to_list(value), bg = True))
            else:
                setattr(self, f"col_{key}", self.get_termcol(self.rgb_str_to_list(value)))

        self.col_reset = "\x1b[0m"
        self.col_clear = "\x1b[2J \x1b[H"
        
        self.storage["DEFAULT"]["current_theme"] = name
        with open(self.path, 'w') as configfile:
            self.storage.write(configfile)
    
    def get_themes(self) -> list: # get list of theme names
        return self.storage.sections()
    
    def get_colors(self, theme: str) -> list: # returns 2d list [[name, r, g, b], [name, r, g, b]...]
        result = []
        for key, value in self.storage[theme].items():
            if key == "current_theme":
                continue
            rgb = self.rgb_str_to_list(value)
            result.append([key, rgb[0], rgb[1], rgb[2]])
        return result
    
    def rgb_str_to_list(self, str_in: str) -> list[int]:
        parts = [x.strip() for x in str_in.split(",")]

        if len(parts) != 3:
            raise ValueError(f"Not a valid RGB string: {str_in!r}")
        return [int(x) for x in parts]
    
    def hex_to_rgb(self, str_in: str) -> list:
        h = str_in.lstrip('#')
        return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
    
    def get_termcol(self, list_in: list, bg = False) -> str: # input a rgb list
        try:
            RGB = f"{list_in[0]};{list_in[1]};{list_in[2]}"
        except Exception:
            raise ValueError # Malformed RGB string

        if bg:
            return f"\x1b[48;2;{RGB}m"
        else:
            return f"\x1b[38;2;{RGB}m"
    
    def current_theme(self) -> list:
        return self.get_colors(self.current)
    
    def new_theme(self, data: dict) -> None:
        """
        Creates a new theme and saves it to disk.
        data: dict of the form
        {
            "theme_name": {
                "title": [r, g, b],
                "text": [r, g, b],
                ...
            }
        }
        """
        for theme_name, colors in data.items():
            self.storage[theme_name] = {}
            for key, rgb in colors.items():
                if len(rgb) != 3:
                    raise ValueError(f"Invalid RGB for {key}: {rgb!r}")
                self.storage[theme_name][key] = f"{rgb[0]}, {rgb[1]}, {rgb[2]}"
        
        with open(self.path, 'w') as configfile:
            self.storage.write(configfile)

        self.storage.read(self.path)

    def preview(self, name: str) -> list:
        result = []

        for key, value in self.storage[name].items():
            if key == "current_theme":
                continue
            if key == "background":
                result.append(self.get_termcol(self.rgb_str_to_list(value), bg = True) + f"{key}")
            else:
                result.append(self.get_termcol(self.rgb_str_to_list(value)) + f"{key}")

        return result

    def print_box_drawing(self):
        print("┌ ┬ ┐  ╔ ╦ ╗  ┏ ┳ ┓  │ ┃ ║ ")
        print("├ ┼ ┤  ╠ ╬ ╣  ┣ ╋ ┫  ─ ━ ═ ")
        print("└ ┴ ┘  ╚ ╩ ╝  ┗ ┻ ┛ ╭ ╮ ╰ ╯")
        print("                           ")
        print("╒ ╤ ╕  ╓ ╥ ╖   ╌ ╍    ╎ ╏  ")
        print("╞ ╪ ╡  ╟ ╫ ╢   ┄ ┅    ┆ ┇  ")
        print("╘ ╧ ╛  ╙ ╨ ╜   ┈ ┉    ┊ ┋  ")

class Listener:
    def __init__(self):
        self.active = True
        self.old_settings = ""
        self.fd = None
        self.uses_windows = False
        self.listening = True
        self.last_press = 0
        self.arr = 0.1

        self.key_queue = Queue(maxsize=0)

        if sys.platform.startswith("win"):
            self.uses_windows = True
        
        listener_thread = threading.Thread(target=self.key_listener, args=(self.handle_key,), daemon=True)
        listener_thread.start()
        
    def handle_key(self, key: str):
        if (time.time() - self.last_press) < self.arr:
            return None
        self.last_press = float(time.time())
        try:
            self.key_queue.put_nowait(key)
        except Exception as e:
            actual_print(f"couldn't put key into queue: {key}, exception: {e}")

    def key_listener(self, callback):
        if self.uses_windows:
            while True:
                if msvcrt.kbhit():
                    key = msvcrt.getch().decode("utf-8", errors="ignore")
                    callback(key)

        else:
            self.fd = sys.stdin.fileno()
            self.old_settings = termios.tcgetattr(self.fd)
            
            try:
                tty.setcbreak(self.fd)
                while True:
                    if self.listening:
                        dr, _, _ = select.select([sys.stdin], [], [], 0.05)
                        if dr: 
                            try:
                                key = sys.stdin.read(1)
                                callback(key)
                            except Exception as e:
                                    actual_print(f"Reading key failed: {e}")

            finally:
                termios.tcsetattr(self.fd, termios.TCSADRAIN, self.old_settings)

    def toggle_listening(self, enable: bool):
        self.listening = enable

    def pop(self): # do not forget to finish it
        try:
            return self.key_queue.get_nowait()
        except Empty:
            return None
    
    def done(self):
        try:
            self.key_queue.task_done()
        except ValueError:
            actual_print("done() called without matching get() check, don't do that!!!")

    def safe_input(self, prompt = "> "):
        self.toggle_listening(False)
    
        if not sys.platform.startswith("win"):
            termios.tcsetattr(self.fd, termios.TCSADRAIN, self.old_settings)
        try:
            return input(prompt)
        finally:
            if not sys.platform.startswith("win"):
                tty.setcbreak(self.fd)
            self.toggle_listening(True)

theme = Theme('example.cfg')
prev = theme.preview("solarized")
for i in prev:
    print(i)

print_buffer()
# theme.new_theme({
#     "solarized": {
#         "title": [255, 255, 255],
#         "text": [131, 148, 150],
#         "error": [220, 50, 47]
#     }
# })

listener = Listener()
listener.arr = 0

while(1):
    pop = listener.pop()
    if pop is not None:
        actual_print(pop)
        listener.done()
