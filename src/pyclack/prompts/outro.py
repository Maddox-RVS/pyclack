from ..renderer import Theme, RenderFrame, Text, FrameBuilder
from ..terminal import CursorController as cc
from .util import build_wrapped_input_lines
from ..config import get_active_theme
from typing import override, Optional
from .prompt_base import PromptBase
from .. terminal import Stdout

def outro(message: str) -> None:
    '''
    Display an exit message.
    '''
    
    Outro(message)

class Outro(PromptBase):
    '''
    A class to display an exit message.
    '''

    def __init__(self, message: str):
        '''
        Initialize an Outro prompt with the given message.
        '''

        self.message: str = message
        self.render_frame: RenderFrame = RenderFrame()

        super().__init__()
        super().activate()

    @override
    def handle_submit(self) -> bool:
        theme: Theme = get_active_theme()
        frame_builder: FrameBuilder = FrameBuilder()
        connector_text: Text = Text(theme.symbols.connector_bar_vertical.resolve(), style=theme.muted)
        frame_builder.add_line(connector_text)
        outro_text_lines: list[Text] = build_wrapped_input_lines(self.message, 0, theme.text, theme.muted)
        last_index: int = len(outro_text_lines) - 1
        outro_text_lines[last_index] = Text(theme.symbols.connector_bar_end.resolve(), Text(outro_text_lines[last_index].get_raw_text()[1:], style=theme.text), style=theme.muted)
        for line in outro_text_lines: frame_builder.add_line(line)
        frame: tuple[Text, ...] = frame_builder.build()
        self.render_frame.draw_frame(*frame)

        Stdout.put(cc.show_cursor())
        return True