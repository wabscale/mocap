#!/usr/bin/python3

# abort = False

from MOT import MOT
from KeyboardController import KeyboardController
from art import generate_ascii_art


def main():
    print(generate_ascii_art('\"Studying\"', color='blue', frame='red'))

    color1 = 'blue'
    color2 = 'green'

    multi_object_tracker = MOT(
        color1,
        color2,
    )

    key_controller = KeyboardController(
        multi_object_tracker,
        color1,
        color2,
    )

    key_controller.run()  # non blocking
    multi_object_tracker.run()


if __name__ == '__main__':
    main()


