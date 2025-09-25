# the friendly manual ☺
`pip install luciditycli`

## Quick Start
`from luciditycli import Theme, Listener, print, print_buffer, actual_print, safe_input`
Let's set up a basic instance of both the theme and the listener.
```
theme = Theme('example.cfg')
listener = Listener()
```
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
    name = safe_input("Pick a name > ")
    for i in fields:
        colors.append(theme.safe_input(f"Pick a color for {i}s (#hex / r, g, b): "))
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
    

Some helpful functions:
- `rgb_str_to_list(string)`: Return a "255, 255, 255" string as [255, 255, 255]. Useful for
- `get_termcol(list, bg)`: Takes a [255, 255, 255] list and returns the ASCII escape code for it. THe parameter `bg` determines whether it is the terminal background color.
- `hex_to_rgb(hex)`: Returns a hex code as an RGB list
- `theme.print_box_drawing()` A helpful list of Unicode box drawing characters
