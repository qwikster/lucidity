import configparser # TODO: ADD FORMATTERS, DONE? TEST, NEED NEXT FUNCTIONS, VERY GOOD
import time

def test_func():
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
    
    def get_themes(self) -> list: # get list of theme names
        return self.storage.sections()
    
    def get_colors(self, theme: str) -> list: # returns 2d list [[name, r, g, b], [name, r, g, b]...]
        result = []

        for i in self.storage[theme]:
            temp = [i]
            temp.append(self.rgb_str_to_list(self.storage[theme][i]))
            result.append(temp)
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
            return("Malformed RGB string")

        if bg:
            return f"\x1b[48;2;{RGB}m"
        else:
            return f"\x1b[38;2;{RGB}m"
    
    def current_theme(self) -> list:
        return self.get_colors(self.current)
    
    def new_theme(self, data: list) -> None:
        '''
        creates a new theme and saves it to disk
        data - 2d list [name, [name, r, g, b], [name, r, g, b]...]
        '''
        for item in data:
            if type(item) is str: # create entry
                name = item
                self.storage[name] = {}
            else:
                key = item[0]
                self.storage[name][key] = f"{item[1]}, {item[2]}, {item[3]}"
        
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


theme = Theme('example.cfg')
prev = theme.preview("theme_name")
for i in prev:
    print(i)

data = ["theme_name", ["background", 64, 128, 255], ["color1", 255, 255, 255], ["test_col", 0, 0, 0]]
theme.new_theme(data)