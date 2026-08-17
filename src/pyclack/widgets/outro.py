from ..renderer import Theme, RenderFrame, Text, FrameBuilder, Style
from ..prompts.util import build_message_close
from ..terminal import CursorController as cc
from ..prompts.prompt_base import PromptBase
from ..config import get_active_theme
from ..terminal import Stdout
from typing import override

def outro(message: str, custom_style: Style | None = None) -> None:
    '''
    Display an exit message.

    Args:
        message (str): The message to display to the user.
        custom_style (Style | None, optional): The custom style to use for the outro.
    '''
    
    Outro(message, custom_style)

class Outro(PromptBase):
    '''
    A class to display an exit message.
    '''

    def __init__(self, message: str, custom_style: Style | None):
        '''
        Initialize an Outro prompt with the given message.

        Args:
            message (str): The message to display to the user.
            custom_style (Style | None): The custom style to use for the outro.
        '''

        self.message: str = message
        self.custom_style: Style | None = custom_style
        self.render_frame: RenderFrame = RenderFrame()

        super().__init__()
        super().activate()

    @override
    def handle_submit(self) -> bool:
        theme: Theme = get_active_theme()
        connector_bar_vertical: str = theme.symbols.connector_bar_vertical.resolve()
        connector_bar_end: str = theme.symbols.connector_bar_end.resolve()
        prefix: Text = Text(f'{connector_bar_vertical}  ', theme.muted)
        closing_prefix: Text = Text(f'{connector_bar_end}  ', theme.muted)

        text_style: Style = self.custom_style if self.custom_style else theme.text
        frame_builder: FrameBuilder = FrameBuilder()
        frame_builder.add_line(prefix)
        outro_text_lines: list[Text] = build_message_close(self.message, text_style, prefix, closing_prefix)
        frame_builder.add_lines(*outro_text_lines)
        frame: tuple[Text, ...] = frame_builder.build()
        self.render_frame.draw_frame(*frame)

        Stdout.put(cc.show_cursor())
        return True