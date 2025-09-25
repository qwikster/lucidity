import configparser # TODO: ADD FORMATTERS, DONE? TEST, NEED NEXT FUNCTIONS, VERY GOOD
import threading
import time

def test_func():
    time.sleep(0.1)
    print("hi")

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
    
    def new_theme(self, data: list) -> None:
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
        listener_thread = threading.Thread(target=self.key_listener, args=(self.handle_key,), daemon=True)
        listener_thread.start()
        
    def handle_key(key: str):
        if key == "t":
            active = False
            theme_menu()
            active = True
            
        elif key == "q":
            global doquit # if you call sys.exit it'll just quit the listener
            doquit = True
            sys.exit(0)
            
        elif key == "u":
            global req_user
            active = False
            req_user = get_user()
            request()
            if read(api_response.TODAY, "data.username") == f"{color.ERROR}response parser brokey":
                print(f"{color.ERROR}Invalid user!")
                print_buffer()
                time.sleep(3)
                req_user = "my"
                request()
            active = True
        else:
            pass # other functions might need to go here?

theme = Theme('example.cfg')
prev = theme.preview("solarized")
for i in prev:
    print(i)

# theme.new_theme({
#     "solarized": {
#         "title": [255, 255, 255],
#         "text": [131, 148, 150],
#         "error": [220, 50, 47]
#     }
# })