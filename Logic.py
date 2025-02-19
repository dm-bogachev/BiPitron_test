import random
from threading import Thread, Event
import cv2
import logging
import math

from LogicConfig import LogicConfig
from FrameGrabber import FrameGrabber
from Robot import Robot
from Vision import Vision
logger = logging.getLogger()


class Logic(Thread):
    def __init__(self):
        super().__init__()
        self.config = LogicConfig()
        self.stop_event = Event()
        logger.info(f'Initialized logic handler class')
        self.fg = FrameGrabber()
        self.v = Vision()
        self.robot = Robot()
        self.robot.start()

    def __check_intersection(self, line1, line2):
        x11, y11, x12, y12 = line1
        x21, y21, x22, y22 = line2
        # Equation of line 1: a1*x + b1*y + c1 = 0
        a1 = y11 - y12
        b1 = x12 - x11
        c1 = x11 * y12 - x12 * y11
        # Equation of line 2: a2*x + b2*y + c2 = 0
        a2 = y21 - y22
        b2 = x22 - x21
        c2 = x21 * y22 - x22 * y21

        # Determinant
        det = a1 * b2 - a2 * b1
        if det == 0:
            return None
        else:
            x = (b1 * c2 - b2 * c1) / det
            y = (a2 * c1 - a1 * c2) / det
            if min(x11, x12) < x < max(x11, x12) and min(y11, y12) < y < max(y11, y12) and \
               min(x21, x22) < x < max(x21, x22) and min(y21, y22) < y < max(y21, y22):
                return True
            else:
                return False

    def __rotate_point(self, center, point, angle):
        cx, cy = center
        px, py = point
        # Convert angle to radians
        angle_rad = angle * (3.141592653589793 / 180.0)
        # Translate point to origin
        temp_x = px - cx
        temp_y = py - cy
        # Rotate point
        rotated_x = temp_x * math.cos(angle_rad) - temp_y * math.sin(angle_rad)
        rotated_y = temp_x * math.sin(angle_rad) + temp_y * math.cos(angle_rad)
        # Translate point back
        new_x = rotated_x + cx
        new_y = rotated_y + cy
        return new_x, new_y

    def __get_gripper_angle(self, selected_object):
        gt2 = self.config['round_gripper_thickness']*10/2
        gl2 = self.config['round_gripper_length']*10/2
        bb_lines = []   
        logger.info("Checking 0 angle")
        # Get all lines on screen
        for obj in self.objects:
            if obj[5] == selected_object[5]:
                continue
            xmin, ymin, xmax, ymax = obj[4]
            lines = (
                (xmin, ymin, xmax, ymax),
                (xmin, ymin, xmin, ymax),
                (xmax, ymax, xmax, ymin),
                (xmax, ymax, xmin, ymax)
            )
            for line in lines:
                bb_lines.append(line)
        # Get basic line
        x0, y0, _ = selected_object[3]
        gripper_lines = (
            (x0*10 - gl2, y0*10 - gt2, x0*10 + gl2, y0*10 - gt2),
            (x0*10 - gl2, y0*10 + gt2, x0*10 + gl2, y0*10 + gt2)
        )
        intersection = False
        for line in gripper_lines:
            for bb_line in bb_lines:
                if self.__check_intersection(line, bb_line):
                    intersection = True
        # If crossing, get new angle
        new_angle = -1
        if intersection:
            logger.info("Intersection found")
            for angle in self.config['check_angles']:
                logger.info(f"Checking {angle} angle")
                # Get new coordinates
                glinex11, gliney11 = self.__rotate_point(
                    (x0, y0), (x0*10 - gl2, y0*10 - gt2), angle)
                glinex12, gliney12 = self.__rotate_point(
                    (x0, y0), (x0*10 + gl2, y0*10 - gt2), angle)
                glinex21, gliney21 = self.__rotate_point(
                    (x0, y0), (x0*10 - gl2, y0*10 + gt2), angle)
                glinex22, gliney22 = self.__rotate_point(
                    (x0, y0), (x0*10 + gl2, y0*10 + gt2), angle)
                gripper_lines = (
                    (glinex11, gliney11, glinex12, gliney12),
                    (glinex21, gliney21, glinex22, gliney22)
                )
                intersection = False
                for line in gripper_lines:
                    for bb_line in bb_lines:
                        if self.__check_intersection(line, bb_line):
                            intersection = True
                if not intersection:
                    new_angle = angle
                    logger.info("Success")
                    return new_angle
                logger.info("Intersection found")
        else:
            return 0
        return -1

    def next_object(self):
        pass
        if self.objects:
            while True:
                try_object = random.choice(self.objects)
                if try_object[0] == 'Rounds':
                    self.selected_objects = [
                        obj for obj in self.objects if obj[1] == 1]
                    if len(self.selected_objects) > 0:
                        new_object = random.choice(self.selected_objects)
                        new_angle = self.__get_gripper_angle(new_object)
                        if new_angle == -1:
                            continue
                        new_object[3][2] = new_angle
                        return new_object
                    else:
                        return None
                else:
                    # new_angle = self.__get_gripper_angle(try_object)
                    # if new_angle == -1:
                    #     continue
                    # try_object[3][2] = new_angle
                    return try_object
        else:
            return None

    def run(self):
        logger.info(f'Logic handler thread started')
        while not self.stop_event.is_set():
            self.frame = self.fg.get_frame()
            self.objects = self.v.predict(self.frame)
            self.__temp = self.frame.copy()
            self.display_frame = cv2.resize(
                self.__temp, (1920, 1080), interpolation=cv2.INTER_AREA)

    def stop(self):
        self.stop_event.set()
        logger.info(f'Logic handler thread stopped')
