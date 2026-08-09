from ..prompts.util import build_wrapped_styled_input_lines
from ..renderer import Theme, RenderFrame, Text, FrameBuilder, Style
from ..terminal import CursorController as cc
from ..prompts.prompt_base import PromptBase
from ..config import get_active_theme
from typing import override, Optional
from ..terminal import Stdout

def outro(message: str, custom_style: Optional[Style] = None) -> None:
    '''
    Display an exit message.

    Args:
        message (str): The message to display to the user.
        custom_style (Optional[Style]): The custom style to use for the outro.
    '''
    
    Outro(message, custom_style)

class Outro(PromptBase):
    '''
    A class to display an exit message.
    '''

    def __init__(self, message: str, custom_style: Optional[Style] = None):
        '''
        Initialize an Outro prompt with the given message.

        Args:
            message (str): The message to display to the user.
            custom_style (Optional[Style]): The custom style to use for the outro.
        '''

        self.message: str = message
        self.custom_style: Optional[Style] = custom_style
        self.render_frame: RenderFrame = RenderFrame()

        super().__init__()
        super().activate()

    @override
    def handle_submit(self) -> bool:
        theme: Theme = get_active_theme()
        connector_bar_vertical: str = theme.symbols.connector_bar_vertical.resolve()
        connector_bar_end: str = theme.symbols.connector_bar_end.resolve()
        prefix_muted: Text = Text(f'{connector_bar_vertical}  ', theme.muted)

        text_style: Style = self.custom_style if self.custom_style else theme.text
        outro_text: Text = Text(self.message, text_style)
        frame_builder: FrameBuilder = FrameBuilder()
        frame_builder.add_line(prefix_muted)
        outro_text_lines: list[Text] = build_wrapped_styled_input_lines(outro_text, prefix_muted, 0)
        outro_formatted: str = outro_text_lines[0].get_raw_text()[3:] if not text_style.bg_color else f' {outro_text_lines[0].get_raw_text()[3:]} '
        last_index: int = len(outro_text_lines) - 1
        outro_text_lines[last_index] = Text(connector_bar_end, theme.muted) + '  ' + Text(outro_formatted, text_style)
        for line in outro_text_lines: frame_builder.add_line(line)
        frame: tuple[Text, ...] = frame_builder.build()
        self.render_frame.draw_frame(*frame)

        Stdout.put(cc.show_cursor())
        return True