from pyclack.renderer import RenderFrame, Text
import time

def main():
    frame = RenderFrame()
    frame_text: tuple[Text, ...] = (
        Text('-----------------------------'),
        Text('This is a render frame test!', fg_color='green', bold=True),
        Text('Here are some cool looking symbols:', fg_color='black', bg_color='blue'),
        Text('★ ☆ ✪ ✫ ✬ ✭ ✮ ✯', fg_color='yellow', bg_color='black'),
        Text('-----------------------------')
    )
    drawn_frame = frame.draw_frame(*frame_text)

    time.sleep(3) # Wait for 3 seconds before clearing the frame

    frame_text = (
        Text('-----------------------------'),
        Text('The frame has been cleared!', fg_color='red', bold=True),
        Text('This is the new frame content.', fg_color='black', bg_color='yellow'),
        Text('-----------------------------')
    )
    drawn_frame = frame.draw_frame(*frame_text)

    time.sleep(3) # Wait for 3 seconds before clearing the frame

    message: str = (
        'This is a test of the text wrapping functionality. '
        'Hopefully it works correctly. '
        'This is going to be some very long text that will be displayed in the frame. '
        'We want to see how the text wrapping behaves when the text exceeds the width of the terminal window. '
        'Let\'s add even more text to make sure it wraps properly. '
        'Let\'s see if this works as expected. '
    )

    frame_text = (
        Text('-----------------------------'),
        Text(message, fg_color='blue', bold=True),
        Text('-----------------------------')
    )
    drawn_frame = frame.draw_frame(*frame_text)

    time.sleep(3) # Wait for 3 seconds before clearing the frame

    frame.clear_frame() # Clear the frame

if __name__ == "__main__":
    main()