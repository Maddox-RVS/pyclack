from rich.style import Style as rStyle
from rich.text import Text as rText
from rich.console import Console
from typing import Optional
from .themes import Style

class Text:
    '''
    A class representing a piece of text with optional formatting attributes such as background color, foreground color, 
    bold, underline, italic, and strikethrough. It can also contain additional Text objects to concatenate.
    '''

    def __init__(self, 
        text: str,
        *texts: 'Text',
        style: Optional[Style] = None):
        '''
        Initialize a Text object.

        Args:
            text (str): The main text content.
            *texts (Text): Additional Text objects to concatenate.
            style (Optional[Style]): The style to apply to the text.
        '''

        self.text: str = text
        self.texts: tuple[Text] = texts
        self.style: Optional[Style] = style

    def lines_covered(self) -> int:
        '''
        Get the number of lines covered by the raw text if printed to the terminal (including additional Text objects).
        '''

        console: Console = Console()
        total_lines: int = 0
        for line in self.get_raw_text().splitlines():
            wrapped = rText(line).wrap(console, console.width)
            total_lines += max(1, len(wrapped))
        return total_lines

    def get_raw_isolated_text(self) -> str:
        '''
        Get the raw text without any formatting or concatenation of additional Text objects.
        '''

        return self.text

    def get_raw_text(self) -> str:
        '''
        Get the raw text without any formatting, but including concatenation of additional Text objects.
        '''

        return self.text + ''.join(text.get_raw_text() for text in self.texts)

    def get_formatted_text(self) -> rText:
        '''
        Get the text with formatting applied, including concatenation of additional Text objects.

        Returns:
            rText: A rich Text object with the specified formatting and concatenated additional Text objects.
        '''

        formatted_text: rText = rText()

        if self.text:
            rich_style: rStyle = rStyle(
                    color=self.style.fg_color,
                    bgcolor=self.style.bg_color,
                    bold=self.style.bold,
                    underline=self.style.underline,
                    italic=self.style.italic,
                    strike=self.style.strikethrough) if self.style else rStyle()
            formatted_text.append(self.text, style=rich_style)

        for text in self.texts:
            formatted_text.append_text(text.get_formatted_text())

        return formatted_text