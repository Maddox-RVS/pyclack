from ..terminal import CursorController as cc
from rich.text import Text as rText
from rich.console import Console
from ..terminal import Stdout
from .text import Text
import rich

class FrameBuilder:
    '''
    A class for building frames out of Text objects.
    '''

    def __init__(self):
        '''
        Initialize a FrameBuilder object with an empty list of lines.    
        '''
        
        self.lines: list[Text] = []

    def add_line(self, line: Text) -> None:
        '''
        Add a line to the frame. Appends the given Text object to the list of lines in the frame.
        '''
        
        self.lines.append(line)

    def build(self) -> tuple[Text, ...]:
        '''
        Build the frame and return a tuple of Text objects representing the lines in the frame.
        '''
        
        return tuple(self.lines)

class RenderFrame:
    '''
    A class responsible for rendering frames in the terminal. It manages a collection of Text objects and provides 
    methods to draw and clear frames, as well as to calculate the number of lines covered by the frame.
    '''

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

    def lines_covered(self) -> int:
        '''
        Get the number of lines covered by the frame if printed to the terminal.
        '''

        console: Console = Console()
        total_lines: int = 0
        for frame_line in self._create_raw_frame().splitlines():
            wrapped = rText(frame_line).wrap(console, console.width)
            total_lines += max(1, len(wrapped))
        return total_lines

    def draw_frame(self, *lines: Text) -> str:
        '''
        Draw a frame with the given Text objects. If a frame is already drawn, it will be cleared before drawing the new frame.
        '''

        if self.lines: Stdout.write(cc.move_to_line_start_and_clear(self.lines_covered()))
        self.lines = lines
        frame: str = self._create_formatted_frame()
        rich.print(frame)

    def clear_frame(self) -> None:
        '''
        Clear the current frame.
        '''

        if self.lines:
            Stdout.put(cc.move_to_line_start_and_clear(self.lines_covered()))
            self.lines = ()