from ..renderer import Theme, RenderFrame, Text, FrameBuilder
from ..prompts.util import build_message_close
from ..terminal import CursorController as cc
from ..prompts.prompt_base import PromptBase
from ..config import get_active_theme
from ..terminal import Stdout
from typing import override

def cancel(message: str) -> None:
    '''
    Display a cancellation message to the user.
    '''
    
    Cancel(message)

class Cancel(PromptBase):
    '''
    A class to display a cancellation message to the user.
    '''
    
    def __init__(self, message: str):
        '''
        Initialize a Cancel prompt with the given message.

        Args:
            message (str): The cancellation message to display to the user.
        '''
        
        super().__init__()
        
        self.message: str = message
        self.render_frame: RenderFrame = RenderFrame()
        
        self.activate()

    @override
    def handle_active(self, key: str | None) -> bool:
        Stdout.put(cc.hide_cursor())
        
        theme: Theme = get_active_theme()
        connector_bar_vertical: str = theme.symbols.connector_bar_vertical.resolve()
        connector_bar_end: str = theme.symbols.connector_bar_end.resolve()
        prefix_muted: Text = Text(f'{connector_bar_vertical}  ', theme.muted)
        closing_prefix_muted: Text = Text(f'{connector_bar_end}  ', theme.muted)

        frame_builder: FrameBuilder = FrameBuilder()
        frame_builder.add_line(prefix_muted)
        cancel_lines: list[Text] = build_message_close(
            self.message,
            theme.cancel,
            prefix_muted,
            closing_prefix_muted)
        frame_builder.add_lines(*cancel_lines)

        frame: tuple[Text, ...] = frame_builder.build()
        self.render_frame.draw_frame(*frame)

        Stdout.put(cc.show_cursor())
        return True