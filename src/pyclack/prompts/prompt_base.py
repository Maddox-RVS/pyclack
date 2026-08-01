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
        '''
        Activate the prompt by transitioning to the active state and starting the state machine.
        '''

        self.current_state = PromptState.ACTIVE
        self._active()

    def handle_active(self, key: Optional[str]) -> bool: 
        '''
        Handle the active state of the prompt. This method should be overridden by subclasses to implement custom behavior for the active state.

        Args:
            key (Optional[str]): The key pressed by the user, or None if no key was pressed. The first key pressed will always be None when entering the active state, and subsequent keys will be passed to this method.

        Returns:
            bool: True if the prompt should advance to the next state, False otherwise. (`True -> Submit state`, `False -> Active state`)
        '''

        return True

    def handle_submit(self) -> bool: 
        '''
        Handle the submit state of the prompt. This method should be overridden by subclasses to implement custom behavior for the submit state.

        Returns:
            bool: True if the prompt should advance to the next state, False otherwise. (`True -> Exit state machine`, `False -> Error state`)
        '''

        return True

    def handle_error(self, key: Optional[str]) -> bool: 
        '''
        Handle the error state of the prompt. This method should be overridden by subclasses to implement custom behavior for the error state.

        Args:
            key (Optional[str]): The key pressed by the user, or None if no key was pressed. The first key pressed will always be None when entering the error state, and subsequent keys will be passed to this method.

        Returns:
            bool: True if the prompt should advance to the next state, False otherwise. (`True -> Active state`, `False -> Error state`)
        '''

        return True

    def handle_cancel(self) -> None: 
        '''
        Handle the cancel state of the prompt. This method should be overridden by subclasses to implement custom behavior for the cancel state.
        This state leads to no other, the state machine will exit after this state is handled. This method should raise a `CancelException` to 
        indicate that the prompt was cancelled.

        Raises:
            CancelException: Raised to indicate that the prompt was cancelled.
        '''

        raise CancelException('Operation cancelled.')

    def _active(self, propogation_key: Optional[str] = None) -> None:
        '''
        State machine for the active state of the prompt. This method handles user input and transitions between states based on the user's actions.

        Args:
            propogation_key (Optional[str]): A key propogated from the error state to the active state. This key will be passed to the `_handle_active` method as the first key pressed in the active state. None indicates that no key was propogated from the error state.
        '''

        if self.handle_active(None): self.current_state = PromptState.SUBMIT

        cancelled: bool = False

        while self.current_state == PromptState.ACTIVE:
            try:
                key: str = propogation_key
                if not propogation_key: key = KeyReader.readkey()
                if key == 'ESC' or key == 'CTRL_C': 
                    cancelled = True
                    break
                advance_next_state: bool = self.handle_active(key)
                if advance_next_state: break
                else: propogation_key = None
            except KeyboardInterrupt:
                cancelled = True
                break

        if cancelled:
            self.current_state = PromptState.CANCEL
            self._cancel()
        else:
            self.current_state = PromptState.SUBMIT
            self._submit()

    def _submit(self) -> None:
        '''
        State machine for the submit state of the prompt. This method handles user input and transitions between states based on the user's actions.
        '''

        advance_next_state: bool = self.handle_submit()
        if advance_next_state: return
        else:
            self.current_state = PromptState.ERROR
            self._error()

    def _error(self) -> None:
        '''
        State machine for the error state of the prompt. This method handles user input and transitions between states based on the user's actions.
        '''

        if self.handle_error(None): self.current_state = PromptState.ACTIVE
        
        cancelled: bool = False
        propogate_key: Optional[str] = None

        while self.current_state == PromptState.ERROR:
            try:
                key: str = KeyReader.readkey()
                if key == 'ESC' or key == 'CTRL_C': 
                    cancelled = True
                    break
                advance_next_state: bool = self.handle_error(key)
                if advance_next_state: 
                    propogate_key = key
                    break
            except KeyboardInterrupt:
                cancelled = True
                break

        if cancelled:
            self.current_state = PromptState.CANCEL
            self._cancel()
        else:
            self.current_state = PromptState.ACTIVE
            if self.propogate_key_after_error: self._active(propogation_key=propogate_key)
            else: self._active()

    def _cancel(self) -> None:
        '''
        State machine for the cancel state of the prompt. This method handles user input and transitions between states based on the user's actions.
        This state leads to no other, the state machine will exit after this state is handled.
        '''

        self.handle_cancel()