from rich.text import Text as rText
from rich.console import Console
from typing import Optional
from .themes import Style
import shutil

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
        self.texts: tuple['Text'] = texts
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

    def get_formatted_text(self) -> str:
        '''
        Get the text with formatting applied, including concatenation of additional Text objects.
        '''

        formatted_text = self.text

        # Apply formatting to the text
        if self.style:
            if self.style.bg_color:
                formatted_text = f'[on {self.style.bg_color}]{formatted_text}[/on {self.style.bg_color}]'
            if self.style.fg_color:
                formatted_text = f'[{self.style.fg_color}]{formatted_text}[/{self.style.fg_color}]'
            if self.style.bold:
                formatted_text = f'[bold]{formatted_text}[/bold]'
            if self.style.underline:
                formatted_text = f'[underline]{formatted_text}[/underline]'
            if self.style.italic:
                formatted_text = f'[italic]{formatted_text}[/italic]'
            if self.style.strikethrough:
                formatted_text = f'[strike]{formatted_text}[/strike]'

        for text in self.texts:
            formatted_text += text.get_formatted_text()

        return formatted_text