from ..terminal import KeyReader
from typing import Any, Optional
from enum import Enum

class CancelException(Exception):
    '''
    Exception raised when a prompt is cancelled.
    '''

    def __init__(self, message: str, value: Optional[str] = None):
        '''
        Initialize a CancelException with the given message.
        '''

        super().__init__(message)
        self.value: Optional[str] = value

class PromptState(Enum):
    INITIAL = 'initial'
    ACTIVE = 'active'
    SUBMIT = 'submit'
    CANCEL = 'cancel'
    ERROR = 'error'

class PromptBase:
    def __init__(self):
        '''
        Initialize a PromptBase object with the given handlers for different prompt states.
        '''
        
        self.current_state: PromptState = PromptState.INITIAL
        self.propogate_key_after_error: bool = False

    def activate(self) -> None:
        self.current_state = PromptState.ACTIVE
        self._active()

    def _handle_active(self, key: Optional[str]) -> bool: True
    def _handle_submit(self) -> bool: True
    def _handle_error(self, key: Optional[str]) -> bool: True
    def _handle_cancel(self) -> None: pass

    def _active(self, propogation_key: Optional[str] = None) -> None:
        if self._handle_active(None): self.current_state = PromptState.SUBMIT

        cancelled: bool = False

        while self.current_state == PromptState.ACTIVE:
            key: str = propogation_key
            if not propogation_key: key = KeyReader.readkey()
            if key == 'ESC' or key == 'CTRL_C': 
                cancelled = True
                break
            advance_next_state: bool = self._handle_active(key)
            if advance_next_state: break
            else: propogation_key = None

        if cancelled:
            self.current_state = PromptState.CANCEL
            self._cancel()
        else:
            self.current_state = PromptState.SUBMIT
            self._submit()

    def _submit(self) -> None:
        advance_next_state: bool = self._handle_submit()
        if advance_next_state: return
        else:
            self.current_state = PromptState.ERROR
            self._error()

    def _error(self) -> None:
        if self._handle_error(None): self.current_state = PromptState.ACTIVE
        
        cancelled: bool = False
        propogate_key: Optional[str] = None

        while self.current_state == PromptState.ERROR:
            key: str = KeyReader.readkey()
            if key == 'ESC' or key == 'CTRL_C': 
                cancelled = True
                break
            advance_next_state: bool = self._handle_error(key)
            if advance_next_state: 
                propogate_key = key
                break

        if cancelled:
            self.current_state = PromptState.CANCEL
            self._cancel()
        else:
            self.current_state = PromptState.ACTIVE
            if self.propogate_key_after_error: self._active(propogation_key=propogate_key)
            else: self._active()

    def _cancel(self) -> None:
        self._handle_cancel()