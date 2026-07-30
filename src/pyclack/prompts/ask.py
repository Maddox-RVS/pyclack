from ..renderer import Themes, RenderFrame, Text, FrameBuilder, Style
from ..terminal import CursorController as cc
from typing import Callable, Optional
from .prompt_base import PromptBase
from ..terminal import Stdout

def ask(message: str, 
        placeholder: Optional[str], 
        initial_value: Optional[str], 
        validate: Optional[Callable[[str], bool]]) -> str:
    '''
    Ask the user for input with a message, placeholder, initial value, and validation function.
    '''
    
    prompt: Ask = Ask(message, placeholder, initial_value, validate)
    return prompt.input_buffer

class Ask(PromptBase):
    def __init__(self,
            message: str,
            placeholder: Optional[str] = None,
            initial_value: Optional[str] = None,
            validate: Optional[Callable[[str], bool]] = None):
        '''
        Initialize an Ask prompt with the given message, placeholder, initial value, and validation function.
        '''

        self.message: str = message
        self.placeholder: Optional[str] = placeholder
        self.initial_value: Optional[str] = initial_value
        self.validate: Optional[Callable[[str], bool]] = validate

        self.render_frame: RenderFrame = RenderFrame()
        self.input_buffer: str = initial_value if initial_value is not None else ''
        self.input_index: int = 0
        
        super().__init__(
            self._handle_active, 
            self._handle_submit, 
            self._handle_error, 
            self._handle_cancel)

        super().activate()

    def _handle_active(self, key: str) -> bool:
        # Update the input buffer based on the key pressed
        if key == 'BACKSPACE': # Remove character at input_index in input_buffer
            self.input_buffer = self.input_buffer[:max(0, self.input_index - 1)] + self.input_buffer[self.input_index:]
            self.input_index = max(0, self.input_index - 1)
        elif key == 'ENTER': return True # Advance to the next state (submit)
        elif key == 'LEFT': self.input_index = max(0, self.input_index - 1) # Move input_index once to the left
        elif key == 'RIGHT': self.input_index = min(len(self.input_buffer), self.input_index + 1) # Move input_index once to the right
        else:
            map: dict[str, str] = {
                'SPACE': ' ',
                'TAB': '\t',
                'UP': '',
                'DOWN': ''}  
            char: str = map.get(key, key)
            self.input_buffer = self.input_buffer[:self.input_index] + char + self.input_buffer[self.input_index:]
            self.input_index = min(len(self.input_buffer), self.input_index + 1)

        # Create and render next frame based on the current input buffer and state
        frame_builder: FrameBuilder = FrameBuilder()
        frame_builder.add_line(
            Text(Themes.DEFAULT.symbols.step_marker_active.unicode_symbol, 
                Text(f'  {self.message}', style=Style(bold=True)), 
            style=Themes.DEFAULT.active))

        input_buffer_text: Optional[Text] = None
        cursor_hover_style: Style = Style(
                                    fg_color=Themes.DEFAULT.muted.fg_color,
                                    bg_color='white')

        if self.placeholder and len(self.input_buffer) <= 0:
            first_char: str = self.placeholder[0]
            rest_of_str: str = self.placeholder[1:]

            input_buffer_text = Text(Themes.DEFAULT.symbols.connector_bar_vertical.unicode_symbol, 
                                    Text('  ', Text(f'{first_char}', Text(f'{rest_of_str}', style=Themes.DEFAULT.muted), style=cursor_hover_style)),
                                style=Themes.DEFAULT.active)
        else:
            first = self.input_buffer[:self.input_index]
            middle = self.input_buffer[self.input_index : self.input_index + 1]
            last = self.input_buffer[self.input_index + 1 :]
            if len(middle) == 0 and len(last) == 0: middle = ' '

            input_buffer_text = Text(Themes.DEFAULT.symbols.connector_bar_vertical.unicode_symbol, 
                                    Text(f'  {first}', Text(middle, Text(last), style=cursor_hover_style)),
                                style=Themes.DEFAULT.active)
        frame_builder.add_line(input_buffer_text)

        frame_builder.add_line(Text(Themes.DEFAULT.symbols.connector_bar_end.unicode_symbol, style=Themes.DEFAULT.active))

        frame: RenderFrame = frame_builder.build()
        self.render_frame.draw_frame(*frame)

    def _handle_submit(self) -> bool:
        # Implement the logic for handling submit state
        pass

    def _handle_error(self, key: str) -> bool:
        # Implement the logic for handling error state
        pass

    def _handle_cancel(self) -> None:
        # Implement the logic for handling cancel state
        pass