"""
TODO

Need to create a good way to exit when desired.
When controller is run with dry_run=False,
program is impossible to close. A clean way to exit
main loop would fix this.

"""

from Keyboard import *
from threading import Thread
from art import pretty_progress_bar


class KeyboardController:
    """
    keys_down dict records which keys are currently pressed down
    True is pressed and False is released

    keys holds key code commands for certain actions. The action
    name maps to its corresponding key code.
    """
    keys_down = {
        'jump' : False,
        'left' : False,
        'right': False,
        'fire' : False,
    }
    key_command_codes = {
        'jump' : ' ',
        'left' : 'a',
        'right': 'd',
        'fire' : 'e',
    }

    def __init__(self, mot, color1, color2):
        """
        Creates keyboard object using Quarts package.

        dry_run indicates whether or not to actually
        simulate pressing keys. Is extremely useful
        for testing.

        verbose indicated whether to be loud about
        what object is doing with keys.

        :param mot: multi object tracking object
        :param color1: name of primary color controller
        :param color2: name of secondary color controller
        """
        self.keyboard = Keyboard()
        self.mot = mot

        self.color1 = color1
        self.color2 = color2

        self.dry_run = True
        self.verbose = True

        # self.abort = abort

    def burst_compare(self, condition, action_name):
        """
        Presses then releases key if condition is met
        nothing otherwise.

        :param condition: boolean for comparision
        :param action_name: key letter code
        :return: None
        """
        if condition:
            if not self.dry_run:
                if self.verbose:
                    print(action_name, 'burst')
                self.keyboard.KeyDown(self.key_command_codes[action_name])
                time.sleep(0.2)
                self.keyboard.KeyUp(self.key_command_codes[action_name])
                # self.keyboard.Type(self.key_command_codes[action_name])

    def compare(self, condition, action_name):
        """
        Presses key down if condition is met.
        Releases key if condition not met.

        :param condition: boolean value for comparision
        :param action_name: key letter code from self.keys
        :return: None
        """
        if condition:
            if not self.keys_down[action_name]:
                if self.verbose:
                    print(action_name, 'down')
                if not self.dry_run:
                    self.keyboard.KeyDown(self.key_command_codes[action_name])
                self.keys_down[action_name] = True
        else:
            if self.keys_down[action_name]:
                if not self.dry_run:
                    self.keyboard.KeyUp(self.key_command_codes[action_name])
            self.keys_down[action_name] = False

    def main_loop(self):
        """
        main loop for keyboard controller

        gets tracking object data from MOT, then
        checks conditions, then simulates button
        pressing or releasing

        :return: None
        """
        center_point = self.mot.center_point

        screen_width = center_point[0] * 2
        screen_height = center_point[1] * 2

        time.sleep(1)
        pretty_progress_bar(
            3,
        )

        # while int(time.time()) - start <= 10:
        while not self.mot.abort:
            object1_position = self.mot.position(self.color1)[0]
            object2_velocity = self.mot.speed(self.color2)
            # print(object2_velocity)

            self.compare(object1_position[0] < 0.25 * screen_width, 'left')
            self.compare(object1_position[0] > 0.75 * screen_width, 'right')
            self.compare(object1_position[1] < 0.25 * screen_height, 'jump')
            self.burst_compare(object2_velocity > 150, 'fire')

        # print('KEYBOARD ABORT')

    def run(self):
        Thread(name='', target=self.main_loop).start()
