from ..renderer import Text, RenderFrame, FrameBuilder, Theme, Style
from ..prompts.util import build_wrapped_input_lines
from ..config import get_active_theme
from typing import Optional, Callable
from ..prompts import PromptBase
from datetime import date

def date(message: str, 
        initial_date: date, 
        min_date: date, 
        max_date: date, 
        cancellation_message: str = 'Operation Cancelled',
        default_date: Optional[date],
        validate: Optional[Callable[[date], Optional[str]]] = None) -> date:
    pass

class Date(PromptBase):
    def __init__(self):
        super().__init__()

        super().activate()

    def handle_active(self, key: str) -> bool:
        pass

    def handle_submit(self) -> bool:
        pass

    def handle_error(self, key: str) -> bool:
        pass

    def handle_cancel(self):
        pass