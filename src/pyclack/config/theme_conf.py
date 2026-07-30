from ..renderer import Theme, Themes

active_theme: Theme = Themes.DEFAULT

def set_active_theme(theme: Theme) -> None:
    '''
    Set the active theme for the application. This function updates the global variable `active_theme` to the provided theme.

    Args:
        theme (Theme): The theme to set as active.
    '''

    active_theme = theme

def get_active_theme() -> Theme:
    '''
    Get the currently active theme for the application.

    Returns:
        Theme: The currently active theme.
    '''

    return active_theme