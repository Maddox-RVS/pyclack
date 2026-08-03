from ..renderer import Text, RenderFrame, FrameBuilder, Theme, Style
from ..prompts.util import build_wrapped_input_lines
from ..config import get_active_theme
from typing import Optional, Callable
from ..prompts import PromptBase
from datetime import date as ddate

def date(message: str, 
        initial_date: ddate, 
        min_date: ddate, 
        max_date: ddate, 
        cancellation_message: str = 'Operation Cancelled',
        default_date: Optional[ddate] = None,
        validate: Optional[Callable[[ddate], Optional[str]]] = None) -> ddate:
    prompt: Date = Date(message, initial_date, min_date, max_date, cancellation_message, default_date, validate)
    return prompt.selected_date

class Date(PromptBase):
    def __init__(self,
                message: str,
                initial_date: ddate,
                min_date: ddate,
                max_date: ddate,
                cancellation_message: str = 'Operation Cancelled',
                default_date: Optional[ddate] = None,
                validate: Optional[Callable[[ddate], Optional[str]]] = None):
        super().__init__()

        self.selected_date: ddate = initial_date

        super().activate()

    def handle_active(self, key: Optional[str]) -> bool:
        pass

    def handle_submit(self) -> bool:
        pass

    def handle_error(self, key: Optional[str]) -> bool:
        pass

    def handle_cancel(self):
        pass