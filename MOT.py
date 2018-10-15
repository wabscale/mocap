# https://pythonprogramming.net/loading-video-python-opencv-tutorial/?completed=/loading-images-python-opencv-tutorial/
# https://pypi.python.org/pypi/pyobjc-framework-Quartz
# https://raw.githubusercontent.com/kenorb/kenorb/master/scripts/python/Quartz/keyboard.py
# https://pypi.python.org/pypi/opencv-python
# https://thecodacus.com/opencv-object-tracking-colour-detection-python/#.WpgiRRPwbOQ
# https://www.pyimagesearch.com/2015/09/14/ball-tracking-with-opencv/

import cv2
import numpy as np
import time

cap = cv2.VideoCapture(0)


class FixedQueue:
    def __init__(self, cap=20):
        """
        fixed circular queue
        :param cap: the amount of data the queue should hold
        """
        self.data = [None] * int(cap)
        self.front_end = 0
        self.size = 0

    def __len__(self):
        return self.size

    def __iter__(self):
        for index in range(len(self)):
            if self[index] is not None:
                yield self[index]

    def __getitem__(self, index):
        adjusted_index = (self.front_end + index) % len(self.data)
        return self.data[adjusted_index]

    def is_empty(self):
        return len(self) == 0

    def enqueue(self, obj):
        """
        adds object to queue
        will delete oldest value

        :param obj: object to be added
        :return: None
        """
        back_end = (self.front_end + self.size + 1) % len(self.data)
        if self.size < len(self.data) - 1:
            self.size += 1
        else:
            self.front_end = (self.front_end + 1) % len(self.data)
        self.data[back_end] = obj

    def top(self):
        """
        :return: oldest value in queue
        """
        # print(self.size)
        return self.data[(self.front_end + self.size) % len(self.data)] if self.size > 0 else 0, 0


class HsvColor:
    # https://en.wikipedia.org/wiki/HSL_and_HSV#HSV

    # http://rgb.to/html-color-names/1
    # http://rgb.to/save/json/color/red

    # https://qph.ec.quoracdn.net/main-qimg-f3cb680891e3cbea6f3258eef13c233c
    # https://image.slidesharecdn.com/01presentationhuehistograms-150707215651-lva1-app6892/95/about-perception-and-hue-histograms-in-hsv-space-5-638.jpg?cb=1436307525

    def __init__(self, name, h, s, v, sensitivity=30):
        """
        creates Hue Saturation Value Object

        :param name: name of color
        :param h: hue
        :param s: saturation
        :param v: value
        :param sensitivity: the amount of give between lower and upper color values
        """
        self.name = name
        self.hue = h
        self.saturation = s
        self.value = v
        self.sensitivity = sensitivity

    def lower_hsv(self):
        """
        :return: lower hsv (hue saturation value) values as numpy array
        """
        return np.array([self.hue - self.sensitivity, self.saturation, self.value])

    def upper_hsv(self):
        """
        :return: upper hsv (hue saturation value) values as numpy array
        """
        return np.array([self.hue + self.sensitivity, 255, 255])


class Point:
    """
    holds 2 dimensional coordinates
    and timestamp
    """
    def __init__(self, pos, timestamp=None):
        """
        point object
        :param pos: (x, y) coordinates
        :param timestamp: utc float of time of point creation
        """
        self.pos = pos
        if timestamp is None:
            self.timestamp = float(time.time())
        else:
            self.timestamp = timestamp

    def __getitem__(self, index):
        return self.pos[index]

    def __str__(self):
        return str(self.pos) + " : " + str(self.timestamp)


class ColorTrackingObject:
    def __init__(self, color_object):
        """
        sets up tracking object with positions queue,
        color object and the name of the color
        :param color_object:
        """
        self.positions = FixedQueue(10)
        self.color = color_object
        self.color_name = color_object.name

    def lower_hsv(self):
        """
        :return: lower hsv (hue saturation value) values
        """
        return self.color.lower_hsv()

    def upper_hsv(self):
        """
        :return: lower hsv (hue saturation value) values
        """
        return self.color.upper_hsv()

    def add_point(self, p):
        """
        adds point and timestamp to data
        :param p: point object
        :return:
        """
        self.positions.enqueue(p)

    def position(self):
        """
        :return: last recorded position
        """
        return self.positions.top()

    def __str__(self):
        return str(self.positions.top())


class MOT:
    hsv_codes = {
        # 'green': HsvColor('green', 60, 50, 50),
        'green': HsvColor('green', 60, 50, 50),
        'blue': HsvColor('blue', 110, 50, 50),
        'red': HsvColor('red', 20, 50, 50)
    }

    def __init__(self, *args):
        """
        sets up tracking_objects based on colors provided in args
        also records the center point of the screen

        :param args: iterable list of color names in strings
        """
        # self.cap = cv2.VideoCapture(0)

        self.tracking_objects = {
            color_name: ColorTrackingObject(self.hsv_codes[color_name])
            for color_name in set(args)
        }

        self.sensitivity = 30

        _, frame = cap.read()
        frame = self.resize(frame)
        self.center_point = len(frame[0]) // 2, len(frame) // 2
        self.abort = False
        # self.run()

    def speed(self, color_name):
        """
        averages the differences between recorded
        positions divided by the time

        * limited by amount of data recorded

        :param color_name: color of tracked object
        :return: average speed of the object
        """
        positions = self.tracking_objects[color_name].positions
        if len(positions) < 2:
            return 0
        speed_diffs = [
            abs(self.avg(self.dxt_dyt(positions[index], positions[index + 1])))
            for index in range(len(positions) - 1)
        ]

        avg_speed = self.avg(speed_diffs)
        return avg_speed

    def direction(self, color_name):
        """
        averages the differences in the x and y directions
        then uses trig to get its angle in degrees

        * limited by amount of data recorded

        :param color_name: color of tracked object
        :return: angle between 0 and 360 degrees
        """
        positions = self.tracking_objects[color_name].positions
        if len(positions) < 2:
            return 0

        pos_diffs = [
            self.dx_dy(positions[index], positions[index + 1])
            for index in range(len(positions) - 1)
        ]

        avg_pos_diffs = [self.avg(list(map(
            lambda x: x[0],
            pos_diffs
        ))), self.avg(list(map(
            lambda x: x[1],
            pos_diffs
        )))]

        if avg_pos_diffs[0] == 0:
            return 0

        rise_over_run = abs(avg_pos_diffs[1] / avg_pos_diffs[0])
        avg_pos_diffs[0] = -avg_pos_diffs[0]
        avg_pos_diffs[1] = -avg_pos_diffs[1]

        angle = np.arctan(rise_over_run) * (180 / np.pi)

        if avg_pos_diffs[0] < 0 < avg_pos_diffs[1]:
            return 180 - angle
        elif avg_pos_diffs[0] < 0 > avg_pos_diffs[1]:
            return 180 + angle
        elif avg_pos_diffs[0] > 0 > avg_pos_diffs[1]:
            return 360 - angle
        else:
            return angle

    def velocity(self, color_name):
        """
        returns the direction and speed of tracked object

        :param color_name:
        :return: ( direction, speed )
        """
        direction = self.direction(color_name)
        speed = self.speed(color_name)

        return int(direction), int(speed / 10)

    def position(self, color):
        """
        :param color: color of tracked object
        :return: position object for specified tracked color
        """
        return self.tracking_objects[color].position()

    def track_object_by_color(self, frame, tracking_object):
        """
        :param frame:
        :param tracking_object:
        :return: mask_object, (x, y), color_name
        """
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        lower_color = tracking_object.lower_hsv()
        upper_color = tracking_object.upper_hsv()
        
        mask = cv2.inRange(hsv, lower_color, upper_color)
        mask = cv2.erode(mask, None, iterations=10)
        mask = cv2.dilate(mask, None, iterations=2)

        contours = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]

        center = self.center_point

        # only proceed if at least one contour was found
        if len(contours) > 0:
            # find the largest contour in the mask, then use
            # it to compute the minimum enclosing circle and
            # centroid
            c = max(contours, key=cv2.contourArea)
            (x, y), radius = cv2.minEnclosingCircle(c)
            moment = cv2.moments(c)
            center = (int(moment["m10"] / moment["m00"]), int(moment["m01"] / moment["m00"]))

            if radius > 1:
                # draw the circle and centroid on the frame,
                # then update the list of tracked points
                cv2.circle(frame, center, int(radius), (0, 255, 255), 2)
                cv2.circle(frame, center, 5, (0, 0, 255), -1)

        return mask, center, tracking_object.color_name

    def run(self):
        """
        main MOT loop

        reads and analyzes webcam feed frame by frame
        updates all tracking objects with new information
        on each pass

        :return: None
        """
        print('MOT starting')
        while True:
            # start = float(time.time())
            _, frame = cap.read()
            frame = self.resize(frame)
            frame = cv2.flip(frame, 1)
            self.draw_lines(frame)
            tracking_data = []
            for object_to_track in self.tracking_objects.values():
                tracking_data.append(self.track_object_by_color(frame, tracking_object=object_to_track))

            # cv2.imshow('res', cv2.bitwise_and(frame, frame, mask=sum(map(lambda x: x[0], tracking_data))))
            cv2.imshow('frame', frame)

            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):
                print('MOT ABORT')
                self.abort = True
                cap.release()
                cv2.destroyAllWindows()
                break

            utc_timestamp = self.utc_now()

            for tracked_object in tracking_data:
                p = Point(tracked_object[1], utc_timestamp)
                self.tracking_objects[tracked_object[2]].add_point(p)

    @staticmethod
    def dxt_dyt(point1, point2):
        """
        :param point1: Point object
        :param point2: Point object
        :return: dx/time, dy/time
        """
        elapsed = point2.timestamp - point1.timestamp
        dx = (point2[0] - point1[0]) / elapsed
        dy = (point2[1] - point1[1]) / elapsed
        return dx, dy

    @staticmethod
    def dx_dy(point1, point2):
        """
        :param point1: point1: Point object
        :param point2: point2: Point object
        :return: dx, dy
        """
        dx = point2[0] - point1[0]
        dy = point2[1] - point1[1]
        return dx, dy

    @staticmethod
    def utc_now():
        """
        :return: current utc float
        """
        return float(time.time())

    @staticmethod
    def avg(data):
        """
        :param data: data to be operated on
        :return: average of values in data
        """
        return sum(data) / len(data)

    @staticmethod
    def resize(img, width=680, height=440):
        """
        :param img: image to be resized
        :param width: new width
        :param height: new height
        :return: resized image
        """
        return cv2.resize(img, (width, height))

    @staticmethod
    def draw_lines(img):
        width = len(img[0])
        height = len(img)

        cv2.line(img, (int(width * 0.25), 0), (int(width * 0.25), height), (0, 0, 255), 1)
        cv2.line(img, (int(width * 0.75), 0), (int(width * 0.75), height), (0, 0, 255), 1)
        cv2.line(img, (0, int(height * 0.25)), (width, int(height * 0.25)), (225, 0, 255), 1)


if __name__ == '__main__':
    MOT('blue', 'green').run() #'green') #, 'blue')

cv2.destroyAllWindows()
