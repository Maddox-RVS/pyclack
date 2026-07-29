from pyclack.renderer import Text
import rich

def main() -> None:
    text: Text = Text(
        'Normal',
        Text(
            'Blue',
            Text(
                'Yellow',
                Text(
                    'Bold',
                    Text(
                        'Underline',
                        Text(
                            'Italic',
                            Text(
                                'Strikethrough',
                                fg_color='blue',
                                bg_color='yellow',
                                bold=True,
                                underline=True,
                                italic=True,
                                strikethrough=True
                            ),
                            fg_color='blue',
                            bg_color='yellow',
                            bold=True,
                            underline=True,
                            italic=True
                        ),
                        fg_color='blue',
                        bg_color='yellow',
                        bold=True,
                        underline=True
                    ),
                    fg_color='blue',
                    bg_color='yellow',
                    bold=True
                ),
                fg_color='blue',
                bg_color='yellow'
            ),
            fg_color='blue'
        )
    )

    rich.print(text.get_formatted_text())

if __name__ == "__main__":
    main()