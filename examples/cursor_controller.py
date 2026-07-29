from pyclack.terminal import CursorController, Stdout
import time

def main() -> None:
    demo_text: str = (
        'This is a demo of the CursorController class.\n'
        'It will move the cursor around, clear lines, and hide/show the cursor.\n'
        'Watch the terminal carefully to see the effects.\n'
        'This is demo text that will be used as a test.\n'
        'I need more filler lines so that I can demonstrate moving the cursor up and clearing lines.\n'
    )

    print(demo_text)

    # Move the cursor up 3 lines
    time.sleep(2)
    Stdout.put(CursorController.cursor_up(3) + 'Hello, this line was moved up 3 lines!')

    # Move the cursor down 3 lines
    time.sleep(2)
    Stdout.put(CursorController.cursor_down(3) + 'Hello, this line was moved down 3 lines!')

    # Move the cursor to column 3
    time.sleep(2)
    Stdout.put(CursorController.cursor_to_col(3) + 'Hello, this line was moved to column 3!')

    # Clear the current line
    time.sleep(2)
    Stdout.put(CursorController.clear_line() + 'This line was cleared and replaced!')

    # Move up 3 lines
    time.sleep(2)
    Stdout.put(CursorController.cursor_up(3) + 'This line was moved up 3 lines!')

    # Clear from the cursor position to the end of the line
    time.sleep(2)
    Stdout.put(CursorController.clear_to_end_of_line())

    # Clear from the cursor position and below
    time.sleep(2)
    Stdout.put(CursorController.clear_below())

    # Clear the entire screen
    time.sleep(2)
    Stdout.put(CursorController.clear_screen())

    # Hide the cursor
    time.sleep(2)
    Stdout.put(CursorController.hide_cursor() + 'The cursor is now hidden. Wait for 2 seconds to see it again.')

    # Show the cursor
    time.sleep(2)
    Stdout.put(CursorController.show_cursor())

    # Move to line start and clear below
    time.sleep(2)
    Stdout.put('This line will be cleared in 2 seconds.\n')
    Stdout.put('This line will be cleared in 2 seconds.\n')
    Stdout.put('This line will be cleared in 2 seconds.')
    time.sleep(2)
    Stdout.put(CursorController.move_to_line_start_and_clear(2))

if __name__ == "__main__":
    main()