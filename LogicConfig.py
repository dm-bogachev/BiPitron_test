import json
import logging
import os

logger = logging.getLogger()

class LogicConfig:
    def __init__(self):
        self.__load_config()

    def __save_config(self):
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logic_config.json'), 'w') as f:
            json.dump(self.__config, f)

    def __load_config(self):
        try:
            with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logic_config.json'), 'r') as f:
                self.__config = json.load(f)
        except FileNotFoundError:
            logger.error('Config file not found')
            self.__config = {}
            self.__config['round_gripper_thickness'] = 14
            self.__config['round_gripper_length'] = 26
            self.__config['check_angles'] = [90, -45, 45, -60, 60, -30, 30]
            self.__save_config()
    
    def __getitem__(self, key):
        return self.__config[key]
    
    def __setitem__(self, key, value):
        self.__config[key] = value
        self.__save_config()

if __name__ == '__main__':
    config = LogicConfig()
    print(config['round_gripper_thickness'])


