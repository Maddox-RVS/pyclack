from collections.abc import Iterable, AsyncIterable
from ...config import get_active_theme
from .util import render_iterable
from ...renderer import Theme

def message(iterable: Iterable[str] | AsyncIterable[str]) -> None:
    theme: Theme = get_active_theme()
    connector_bar_vertical: str = theme.symbols.connector_bar_vertical.resolve()
    render_iterable(iterable, f'{connector_bar_vertical}  ', theme.muted)

def info(iterable: Iterable[str] | AsyncIterable[str]) -> None:
    theme: Theme = get_active_theme()
    log_level_info: str = theme.symbols.log_level_info.resolve()
    render_iterable(iterable, f'{log_level_info}  ', theme.active)

def step(iterable: Iterable[str] | AsyncIterable[str]) -> None:
    theme: Theme = get_active_theme()
    step_marker_submit: str = theme.symbols.step_marker_submit.resolve()
    render_iterable(iterable, f'{step_marker_submit}  ', theme.submit)