from ..terminal import KeyReader
from typing import Any, Optional
from enum import Enum

class PromptState(Enum):
    INITIAL = 'initial'
    ACTIVE = 'active'
    SUBMIT = 'submit'
    CANCEL = 'cancel'
    ERROR = 'error'

class PromptBase:
    def __init__(self,
            handle_active: callable[[str], bool],
            handle_submit: callable[[], bool],
            handle_error: callable[[str], bool],
            handle_cancel: callable[[], None]):
        '''
        Initialize a PromptBase object with the given handlers for different prompt states.
        '''
        
        self.current_state: PromptState = PromptState.INITIAL

        self.handle_active: callable[[str], bool] = handle_active
        self.handle_submit: callable[[], bool] = handle_submit
        self.handle_error: callable[[str], bool] = handle_error
        self.handle_cancel: callable[[], None] = handle_cancel

    def activate(self) -> None:
        self.current_state = PromptState.ACTIVE
        self._active()

    def _active(self) -> None:
        self.handle_active('')

        cancelled: bool = False

        while self.current_state == PromptState.ACTIVE:
            key: str = KeyReader.readkey()
            if key == 'ESC' or key == 'CTRL_C': 
                cancelled = True
                break
            advance_next_state: bool = self.handle_active(key)
            if advance_next_state: break

        if cancelled:
            self.current_state = PromptState.CANCEL
            self._cancel()
        else:
            self.current_state = PromptState.SUBMIT
            self._submit()

    def _submit(self) -> None:
        advance_next_state: bool = self.handle_submit()
        if advance_next_state: return
        else:
            self.current_state = PromptState.ERROR
            self._error()

    def _error(self) -> None:
        cancelled: bool = False

        while self.current_state == PromptState.ERROR:
            key: str = KeyReader.readkey()
            if key == 'ESC' or key == 'CTRL_C': 
                cancelled = True
                break
            advance_next_state: bool = self.handle_error(key)
            if advance_next_state: break

        if cancelled:
            self.current_state = PromptState.CANCEL
            self._cancel()
        else:
            self.current_state = PromptState.ACTIVE
            self._active()

    def _cancel(self) -> None:
        self.handle_cancel()