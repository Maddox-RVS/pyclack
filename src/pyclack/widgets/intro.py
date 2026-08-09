from ..prompts.util import build_wrapped_input_lines, build_wrapped_styled_input_lines
from ..renderer import Theme, RenderFrame, Text, FrameBuilder, Style
from ..terminal import CursorController as cc
from ..prompts.prompt_base import PromptBase
from typing import override, Optional
from ..config import get_active_theme
from ..terminal import Stdout

def intro(title: str, custom_style: Optional[Style] = None) -> None:
    '''
    Display an introductory message with a title.

    Args:
        title (str): The title to display to the user.
        custom_style (Optional[Style]): The custom style to use for the intro.
    '''
    
    Intro(title, custom_style)

class Intro(PromptBase):
    '''
    A class to display an introductory message with a title.
    '''

    def __init__(self, title: str, custom_style: Optional[Style] = None):
        '''
        Initialize an Intro prompt with the given title.

        Args:
            title (str): The title to display to the user.
            custom_style (Optional[Style]): The custom style to use for the intro.
        '''

        self.title: str = title
        self.custom_style: Optional[Style] = custom_style
        self.render_frame: RenderFrame = RenderFrame()

        super().__init__()
        super().activate()

    @override
    def handle_submit(self) -> bool:
        theme: Theme = get_active_theme()
        connector_bar_start: str = theme.symbols.connector_bar_start.resolve()
        connector_bar_vertical: str = theme.symbols.connector_bar_vertical.resolve()
        prefix_muted: Text = Text(f'{connector_bar_vertical}  ', theme.muted)

        text_style: Style = self.custom_style if self.custom_style else theme.text
        title_text: Text = Text(self.title, text_style)
        frame_builder: FrameBuilder = FrameBuilder()
        title_text_lines: list[Text] = build_wrapped_styled_input_lines(title_text, prefix_muted, 0)
        title_formatted: str = title_text_lines[0].get_raw_text()[3:] if not text_style.bg_color else f' {title_text_lines[0].get_raw_text()[3:]} '
        title_text_lines[0] = Text(connector_bar_start, theme.muted) + '  ' + Text(title_formatted, text_style)
        for line in title_text_lines: frame_builder.add_line(line)
        frame: tuple[Text, ...] = frame_builder.build()
        self.render_frame.draw_frame(*frame)

        Stdout.put(cc.show_cursor())
        return True