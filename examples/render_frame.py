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

    time.sleep(3)  # Wait for 3 seconds before clearing the frame

    frame_text = (
        Text('-----------------------------'),
        Text('The frame has been cleared!', fg_color='red', bold=True),
        Text('This is the new frame content.', fg_color='black', bg_color='yellow'),
        Text('-----------------------------')
    )
    drawn_frame = frame.draw_frame(*frame_text)

    time.sleep(3)  # Wait for 3 seconds before clearing the frame

    frame.clear_frame()  # Clear the frame

if __name__ == "__main__":
    main()