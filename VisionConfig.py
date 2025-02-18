import json
import logging
import os

logger = logging.getLogger()

class VisionConfig:
    def __init__(self):
        self.__load_config()

    def __save_config(self):
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'vision_config.json'), 'w', encoding='utf-8') as f:
            json.dump(self.__config, f, ensure_ascii=False, indent=4)

    def __load_config(self):
        try:
            with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'vision_config.json'), 'r') as f:
                self.__config = json.load(f)
        except FileNotFoundError:
            logger.error('Config file not found')
            self.__config = {}
            self.__config['display_box'] = True
            self.__config['display_pose'] = True
            self.__config['display_coordinates'] = True
            self.__config['display_confidence'] = True
            self.__config['class_names'] = ["Rounds", "Smalls", "Longs"]
            self.__config['models'] = {"Rounds": "model_round.pt", "Smalls": "model_small.pt", "Longs": "model_long.pt"}    
            self.__config['minimal_confidences'] =  {"Rounds": 0.75, "Smalls": 0.75, "Longs": 0.75}
            self.__config['model_type'] = {"Rounds": "detect", "Smalls": "pose", "Longs": "pose"}
            self.__save_config()
    
    def __getitem__(self, key):
        return self.__config[key]
    
    def __setitem__(self, key, value):
        self.__config[key] = value
        self.__save_config()

if __name__ == '__main__':
    config = VisionConfig()
    print(config['models'])


