from ..prompts.util import build_wrapped_lines, build_message_header
from ..renderer import Theme, RenderFrame, Text, FrameBuilder
from ..terminal import CursorController as cc
from ..prompts.prompt_base import PromptBase
from ..config import get_active_theme
from ..terminal import Stdout
from typing import override
import shutil

def note(title: str, message: str) -> None:
    '''
    Displays a note to the user with a title and message.
    '''

    Note(title, message)

class Note(PromptBase):
    '''
    A class that displays a note to the user with a title and message.
    '''

    def __init__(self, title: str, message: str):
        '''
        Initializes a Note instance.

        Args:
            title (str): The title of the note.
            message (str): The message of the note.
        '''

        super().__init__()

        self.title: str = title
        self.message: str = message

        self.render_frame: RenderFrame = RenderFrame()
        
        self.activate()

    def _chunkify(self, string: str, max_line_len: int) -> list[str]:
        '''
        Splits a string into chunks of a specified maximum line length.

        Args:
            string (str): The string to be chunked.
            max_line_len (int): The maximum length of each chunk.

        Returns:
            list[str]: A list of string chunks.
        '''

        def _chunk(string: str, max_line_len: int) -> list[str]:
            return [string[i:i+max_line_len] for i in range(0, len(string), max_line_len)]

        pieces: list[str] = string.split('\n')
        chunks: list[str] = []
        for piece in pieces:
            piece_chunks: list[str] = _chunk(piece, max_line_len)
            for chunk in piece_chunks: chunks.append(chunk)
        return chunks

    @override
    def handle_active(self, key: str | None) -> bool:
        Stdout.put(cc.hide_cursor())
        
        theme: Theme = get_active_theme()
        step_marker_submit: str = theme.symbols.step_marker_submit.resolve()
        connector_bar_vertical: str = theme.symbols.connector_bar_vertical.resolve()
        box_drawing_bottom_right_corner: str = theme.symbols.box_drawing_bottom_right_corner.resolve()
        box_drawing_horizontal_bar: str = theme.symbols.box_drawing_horizontal_bar.resolve()
        box_drawing_left_connector: str = theme.symbols.box_drawing_left_connector.resolve()
        box_drawing_top_right_corner: str = theme.symbols.box_drawing_top_right_corner.resolve()
        prefix_muted: Text = Text(f'{connector_bar_vertical}  ', theme.muted)
        
        frame_builder: FrameBuilder = FrameBuilder()

        frame_builder.add_line(prefix_muted)

        cols, _ = shutil.get_terminal_size()
        max_chars_per_line: int = cols - (len(prefix_muted) * 2)
        title_chunks: list[str] = self._chunkify(self.title, max_chars_per_line)
        message_chunks: list[str] = self._chunkify(self.message, max_chars_per_line)
        longest_line_len: int = max(len(title_chunks[-1]), max(len(line) for line in message_chunks))

        for i, chunk in enumerate(title_chunks):
            prefix_custom: Text = prefix_muted
            if i == 0: prefix_custom = Text(f'{step_marker_submit}  ', theme.submit)
            
            chunk_text: Text = prefix_custom + Text(chunk, theme.text)
            if i == len(title_chunks) - 1:
                padding_amount: int = longest_line_len - len(chunk)
                padding_text: Text = Text(f'{box_drawing_horizontal_bar}' * padding_amount, theme.muted)
                chunk_text = Text.assemble(
                    prefix_custom,
                    (chunk, theme.text),
                    ' ',
                    padding_text,
                    (box_drawing_horizontal_bar, theme.muted),
                    (box_drawing_top_right_corner, theme.muted))
            frame_builder.add_line(chunk_text)

        seperator_text: Text = Text.assemble(
            prefix_muted,
            ' ' * longest_line_len,
            (f'  {connector_bar_vertical}', theme.muted))
        frame_builder.add_line(seperator_text)

        for chunk in message_chunks:
            padding_amount = longest_line_len - len(chunk)
            padding_text = Text(' ' * padding_amount, theme.text)
            chunk_text = Text.assemble(
                prefix_muted,
                (chunk, theme.text),
                padding_text,
                (f'  {connector_bar_vertical}', theme.muted))
            frame_builder.add_line(chunk_text)

        frame_builder.add_line(seperator_text)

        bottom_line_text: Text = Text.assemble(
            (f'{box_drawing_left_connector}', theme.muted),
            (f'{box_drawing_horizontal_bar}' * (longest_line_len + 4), theme.muted),
            (f'{box_drawing_bottom_right_corner}', theme.muted))
        frame_builder.add_line(bottom_line_text)

        frame: tuple[Text, ...] = frame_builder.build()
        self.render_frame.draw_frame(*frame)

        Stdout.put(cc.show_cursor())
        return True