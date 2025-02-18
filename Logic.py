import logging

from FrameGrabber import FrameGrabber
from Robot import Robot
from Vision import Vision
logger = logging.getLogger()

import cv2
from threading import Thread, Event
import random

class Logic(Thread):
    def __init__(self):
        super().__init__()
        self.stop_event = Event()
        logger.info(f'Initialized logic handler class')
        self.fg = FrameGrabber()
        self.v = Vision()
        self.robot = Robot()
        self.robot.start()

    def next_object(self):
        if self.objects:
            return random.choice(self.objects)
        else:
            return None
        # models = self.config['class_names']
        # current_index = models.index(self.current_model)
        # next_index = (current_index + 1) % len(models)
        # self.current_model = models[next_index]
        # return self.current_model

    def run(self):
        logger.info(f'Logic handler thread started')
        while not self.stop_event.is_set():
            self.frame = self.fg.get_frame()
            self.objects = self.v.predict(self.frame)
            self.__temp = self.frame.copy()
            self.display_frame = cv2.resize(self.__temp, (1920, 1080), interpolation=cv2.INTER_AREA)
            

    def stop(self):
        self.stop_event.set()
        logger.info(f'Logic handler thread stopped')