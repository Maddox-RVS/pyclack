from pyclack.renderer import Text, Style
import rich

def main() -> None:
    style1: Style = Style(fg_color='blue')
    style2: Style = Style(fg_color='blue', bg_color='yellow')
    style3: Style = Style(fg_color='blue', bg_color='yellow', bold=True)
    style4: Style = Style(fg_color='blue', bg_color='yellow', bold=True, underline=True)
    style5: Style = Style(fg_color='blue', bg_color='yellow', bold=True, underline=True, italic=True)
    style6: Style = Style(fg_color='blue', bg_color='yellow', bold=True, underline=True, italic=True, strikethrough=True)

    text: Text = Text('Normal',
        Text('Blue',
             Text('Yellow',
                  Text('Bold',
                       Text('Underline',
                            Text('Italic',
                                 Text('Strikethrough',
                                       style=style6),
                                 style=style5),
                            style=style4),
                       style=style3),
                  style=style2),
             style=style1)
    )

    rich.print(text.get_formatted_text())

if __name__ == "__main__":
    main()