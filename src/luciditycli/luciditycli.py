import configparser

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
        for i in self.storage[self.current]:
            if i == "background":
                setattr(self, f"col_{i}", self.get_termcol(self.rgb_str_to_list(self.storage[self.current][i]), bg = True))
            else:
                setattr(self, f"col_{i}", self.get_termcol(self.rgb_str_to_list(self.storage[self.current][i])))
    
    def get_themes(self, name: str) -> list: # get list of theme names
        names = self.storage.sections
        names.pop(0) # DEFAULT
        return names
    
    def get_colors(self, theme: str) -> list: # returns 2d list [[name, r, g, b], [name, r, g, b]...]
        pass
    
    def rgb_str_to_list(self, input: str) -> list:
        return input.split(", ")
    
    def hex_to_rgb(self, input: str) -> list:
        pass
    
    def get_termcol(self, input: list, bg = False) -> str: # input a rgb list
        pass
    
    def current_theme(self) -> list:
        pass
    
    def new_theme(self, data: list) -> None:
        '''
        creates a new theme and saves it to disk
        data - 2d list [[name, r, g, b], [name, r, g, b]...]
        '''
        pass
    
    def print_box_drawing(self):
        print("┌ ┬ ┐  ╔ ╦ ╗  ┏ ┳ ┓  │ ┃ ║ ")
        print("├ ┼ ┤  ╠ ╬ ╣  ┣ ╋ ┫  ─ ━ ═ ")
        print("└ ┴ ┘  ╚ ╩ ╝  ┗ ┻ ┛ ╭ ╮ ╰ ╯")
        print("                           ")
        print("╒ ╤ ╕  ╓ ╥ ╖   ╌ ╍    ╎ ╏  ")
        print("╞ ╪ ╡  ╟ ╫ ╢   ┄ ┅    ┆ ┇  ")
        print("╘ ╧ ╛  ╙ ╨ ╜   ┈ ┉    ┊ ┋  ")