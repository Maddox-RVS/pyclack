from ..terminal import CursorController as cc
from ..terminal import Stdout
from .text import Text
import shutil
import rich

class RenderFrame:
    def __init__(self):
        self.lines: tuple[Text, ...] = ()

    def _create_raw_frame(self) -> str:
        '''
        Create a raw frame string from the list of Text objects.
        '''

        return '\n'.join(line.get_raw_text() for line in self.lines)

    def _create_formatted_frame(self) -> str:
        '''
        Create a formatted frame string from the list of Text objects.
        '''

        return '\n'.join(line.get_formatted_text() for line in self.lines)

    def _lines_covered(self) -> int:
        '''
        Get the number of lines covered by the frame.
        '''

        columns, lines = shutil.get_terminal_size()
        frame_lines = self._create_raw_frame().splitlines()
        total_lines: int = 0
        for frame_line in frame_lines:
            total_lines += max(1, (len(frame_line) + columns - 1) // columns)  # Calculate how many lines this frame line will take up
        return total_lines

    def draw_frame(self, *lines: Text) -> str:
        '''
        Draw a frame with the given Text objects. If a frame is already drawn, it will be cleared before drawing the new frame.
        '''

        if self.lines: Stdout.put(cc.move_to_line_start_and_clear(self._lines_covered()))
        self.lines = lines
        frame: str = self._create_formatted_frame()
        rich.print(frame)

    def clear_frame(self) -> None:
        '''
        Clear the current frame.
        '''

        if self.lines:
            Stdout.put(cc.move_to_line_start_and_clear(self._lines_covered()))
            self.lines = ()