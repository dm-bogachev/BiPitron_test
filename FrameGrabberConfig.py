import json
import logging
import os

logger = logging.getLogger()

class FrameGrabberConfig:
    def __init__(self):
        self.__load_config()

    def __save_config(self):
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'camera_config.json'), 'w') as f:
            json.dump(self.__config, f)

    def __load_config(self):
        try:
            with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'camera_config.json'), 'r') as f:
                self.__config = json.load(f)
        except FileNotFoundError:
            logger.error('Config file not found')
            self.__config = {}
            self.__config['exposure'] = 10000
            self.__config['markers_x_distance'] = 4100
            self.__config['markers_y_distance'] = 2860
            self.__config['camera_type'] = 'hik'
            self.__config['webcamera_address'] = 0
            self.__save_config()
    
    def __getitem__(self, key):
        return self.__config[key]
    
    def __setitem__(self, key, value):
        self.__config[key] = value
        self.__save_config()

if __name__ == '__main__':
    config = FrameGrabberConfig()
    print(config['exposure'])


