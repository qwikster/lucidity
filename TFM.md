# the friendly manual ☺
`pip install luciditycli`

## Quick Start
Let's set up a basic instance of both the theme and the listener.
```
theme = Theme('example.cfg')
listener = Listener()
```

### Theme system
`from luciditycli import Theme, Listener, print, print_buffer, actual_print, safe_input`

If you haven't created a theme file, you can initialize one with `theme.create_themefile(path)`. Make sure to do this only once.

The program will load your theme in to memory automatically, but you may select one with `theme.load_theme(path)`. This choice is persistent between program runs.

Call `theme.get_themes()` to return a list of themes, and `theme.get_colors()` (or `theme.current_theme()`) to return a list of colors in `[[name, r, g, b], [name, r, g, b]...]`

Call `theme.preview()` to get a list of strings with *the colors applied to the names*.

The most complicated function: `theme.new_theme(dict)`. The data structure:
```
{
    "theme_name": {
        "title": [r, g, b],
        "text": [r, g, b],
        ...
    }
}
```
Here's an example of how you might construct this data:
```
def new_theme():
    fields = ["background", "title", "text", "error", "prompt"]
    colors = []
    name = listener.safe_input("Pick a name > ")
    for i in fields:
        colors.append(listener.safe_input(f"Pick a color for {i}s (#hex / r, g, b): "))
    for i in colors:
        if "#" in i:
            colors[colors.index(i)] = theme.hex_to_rgb(i)
        else:
            colors[colors.index(i)] = theme.rgb_str_to_list(i)
    theme.new_theme({
        name: {
            fields[0]: colors[0],
            fields[1]: colors[1],
            fields[2]: colors[2],
            fields[3]: colors[3],
            fields[4]: colors[4],
        }
    })
```

Note that any field named `background` will automatically be called as a background color. There is currently no way to represent placeholders for multiple, but `get_termcol()` might help.

Some helpful functions:
- `rgb_str_to_list(string)`: Return a "255, 255, 255" string as [255, 255, 255]. Useful for
- `get_termcol(list, bg)`: Takes a [255, 255, 255] list and returns the ASCII escape code for it. The parameter `bg` determines whether it is the terminal background color.
- `hex_to_rgb(hex)`: Returns a hex code as an RGB list
- `theme.print_box_drawing()` A helpful list of Unicode box drawing characters

To refer to the theme's variables, enter:
`theme.col_background` (replacing `background` with your field's name)
example: `f"{theme.col_text} This is a piece of text. {theme.col_error} This is BAD!!`

Call `col_reset` to reset both the background and foreground color.
Call `col_clear` to clear the screen and move the cursor to the top left.

### Listener system
This library contains an input listener system.

> [!INFO]
> You must use the built in `safe_input` module to get terminal input while a listener is running.

To prevent odd behavior called by the Windows terminal, use the module's `print()` function instead of the builtin, and use `print_buffer()` once you've printed a full menu. `actual_print()` is in the namespace to ignore the buffer, or you can define your own at the top of your file (before the import!) as `print_name = print`

The listener is active from the start. Call `listener.toggle_listening(False)` to toggle it off, or otherwise. This will allow you to use `input()` or other terminal functions.

Kill the listener thread before you delete the class instance for any reason. Set `listener.quit = True`. You may reinitialize an instance by calling its `listener.__init__()`

To set up a listener menu:
```
while(True):
    pop = listener.pop()
    if pop is not None:
        actual_print(pop)
        listener.done()
    if pop == "q":
        listener.done()
        listener.quit = True
        sys.quit(0)
    if pop == ...: # rest of loop logic goes here!
        listener.done()
    else:
        actual_print("Invalid key!")
    
    # Rest of main program loop goes here
```
Call `listener.pop()` to get an item, then call `listener.done()` when you've handled it to clear the entry. If you need to get input from the listener inside that function, call `done()` BEFORE the call.