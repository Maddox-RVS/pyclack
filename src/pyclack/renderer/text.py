class Text:
    def __init__(self, 
        text: str,
        *texts: 'Text',
        bg_color: str = None,
        fg_color: str = None,
        bold: bool = False,
        underline: bool = False,
        italic: bool = False,
        strikethrough: bool = False):
        '''
        Initialize a Text object.

        :param text: The text to display.
        :param texts: Additional Text objects to concatenate.
        :param bg_color: The background color of the text.
        :param fg_color: The foreground color of the text.
        :param bold: Whether the text should be bold.
        :param underline: Whether the text should be underlined.
        :param italic: Whether the text should be italic.
        :param strikethrough: Whether the text should be struck through.
        '''

        self.text: str = text
        self.texts: tuple['Text'] = texts
        self.bg_color: str = bg_color
        self.fg_color: str = fg_color
        self.bold: bool = bold
        self.underline: bool = underline
        self.italic: bool = italic
        self.strikethrough: bool = strikethrough

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
        if self.bg_color: formatted_text = f'[on {self.bg_color}]{formatted_text}[/on {self.bg_color}]'
        if self.fg_color: formatted_text = f'[{self.fg_color}]{formatted_text}[/{self.fg_color}]'
        if self.bold: formatted_text = f'[bold]{formatted_text}[/bold]'
        if self.underline: formatted_text = f'[underline]{formatted_text}[/underline]'
        if self.italic: formatted_text = f'[italic]{formatted_text}[/italic]'
        if self.strikethrough: formatted_text = f'[strike]{formatted_text}[/strike]'

        for text in self.texts:
            formatted_text += text.get_formatted_text()

        return formatted_text