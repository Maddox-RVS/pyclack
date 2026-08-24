from rich.style import Style as rStyle
from rich.text import Text as rText
from rich.console import Console
from .themes import Style
from typing import Any
from copy import copy

class Text:
    '''
    A class representing a piece of text with optional formatting attributes such as background color, foreground color, 
    bold, underline, italic, and strikethrough. It can also contain additional Text objects to concatenate.
    '''

    def __init__(self, 
        text: str = '',
        style: Style | None = None,
        inner_text: Text | None = None):
        '''
        Initialize a Text object.

        Args:
            text (str): The main text content.
            inner_text (Text, optional): An additional Text object to concatenate.
            style (Style, optional): The style to apply to the text.
        '''

        if style is not None and not isinstance(style, Style):
            raise TypeError(f'style must be an instance of Style or None, got {type(style).__name__}')

        if inner_text is not None and not isinstance(inner_text, Text):
            raise TypeError(f'inner_text must be an instance of Text or None, got {type(inner_text).__name__}')

        self.text: str = text
        self.style: Style | None = style
        self.inner_text: Text | None = inner_text

    @staticmethod
    def assemble(*parts) -> Text:
        '''
        A static method to create a Text object by concatenating multiple parts, which can be strings, tuples of (text, style), or other Text objects.

        Args:
            *parts: A variable number of parts to concatenate. Each part can be a string, a tuple of (text, style), or another Text object.

        Returns:
            Text: A new Text object that represents the concatenation of all provided parts.

        Raises:
            TypeError: If any part is not a string, a tuple of (text, style), or a Text object.
        '''

        def coerce(obj: Any):
            if isinstance(obj, Text): return obj
            if isinstance(obj, tuple):
                text, style = obj
                return Text(text, style=style)
            if isinstance(obj, str): return Text(obj)
            raise TypeError(f"Unsupported part in Text.assemble: {type(obj).__name__}")

        parts = [coerce(obj) for obj in parts]
        result = parts[0]
        for t in parts[1:]:
            result = result + t
        return result

    def lines_covered(self) -> int:
        '''
        Get the number of lines covered by the raw text if printed to the terminal (including additional Text objects).

        Returns:
            int: The number of lines covered by the text.
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

        Returns:
            str: The raw text content.
        '''

        return self.text

    def get_raw_text(self) -> str:
        '''
        Get the raw text without any formatting, but including concatenation of additional Text objects.

        Returns:
            str: The raw text content with concatenated additional Text objects.
        '''

        return self.text + self.inner_text.get_raw_text() if self.inner_text else self.text

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
                    strike=self.style.strikethrough,
                    dim=self.style.dim) if self.style else rStyle()
            formatted_text.append(self.text, style=rich_style)

        if self.inner_text:
            formatted_text.append_text(self.inner_text.get_formatted_text())

        return formatted_text

    def __add__(self, other: Any):
        if isinstance(other, str): other = Text(other)

        if not isinstance(other, Text):
            return NotImplemented

        result = Text(self.text, self.style)
        if self.inner_text is None:
            result.inner_text = other
        else:
            inner_text = result.inner_text = copy(self.inner_text)
            while inner_text.inner_text is not None:
                inner_text.inner_text = copy(inner_text.inner_text)
                inner_text = inner_text.inner_text
            inner_text.inner_text = other

        return result

    def __len__(self):
        return len(self.get_raw_text())