import logging

from FrameGrabber import FrameGrabber
from Robot import Robot
from Vision import Vision
logger = logging.getLogger()

import time
from threading import Thread, Event

class Logic(Thread):
    def __init__(self):
        super().__init__()
        self.stop_event = Event()
        logger.info(f'Initialized logic handler class')
        self.fg = FrameGrabber()
        self.v = Vision()
        self.robot = Robot()
        self.robot.start()

    def run(self):
        logger.info(f'Logic handler thread started')
        while not self.stop_event.is_set():
            self.frame = self.fg.get_frame()
            self.objects = self.v.predict(self.frame)
            self.display_frame = self.frame.copy()

    def stop(self):
        self.stop_event.set()
        logger.info(f'Logic handler thread stopped')