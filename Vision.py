import logging
logger = logging.getLogger()
from ultralytics import YOLO
import torch
import os
import cv2

from Colors import *
from VisionConfig import VisionConfig

class Vision:

    def __init_torch_device(self):
        logger.info('Checking GPU availability')
        if torch.cuda.is_available():
            logger.info('Using CUDA GPU accelerator')
            torch.cuda.set_device(0)
            self.device = 'cuda'
        else:
            logger.info('GPU accelerator not found. Using CPU')
            self.device = 'cpu'

    def __load_models(self):
        self.models = {}
        for model in self.config['models']:
            logger.info(f"Loading model {model} from {self.config['models'][model]}")
            _model = YOLO(os.path.join(os.path.dirname(os.path.abspath(__file__)), "models", self.config['models'][model]))
            _model.to(self.device)
            self.models[model] = _model
            logger.info(f"Model {model} loaded")
            
    def get_models(self):
        return self.config['class_names']

    def set_model(self, model):
        self.current_model = model

    def __init__(self):
        self.config = VisionConfig()
        self.__init_torch_device()
        self.current_model = self.config['class_names'][0]
        self.__load_models()


    def predict(self, frame):
        model = self.current_model
        _model = self.models[model]
        logger.info(f"Predicting with {model}")
        objects = []
        results = _model.predict(frame, verbose=False)
        for result in results:
            colors = [COLOR_GREEN, COLOR_RED]
            object_boxes = result.boxes.data.tolist()
            if self.config['model_type'][model] == 'pose':
                object_keypoints = result.keypoints.data.tolist()

            for i in range(len(object_boxes)):
                box_data = object_boxes[i]
                if self.config['model_type'][model] == 'pose':
                    keypoints_data = object_keypoints[i]
                _class = int(result.boxes.cls[i].item())
                name = result.names[_class]
                confidence = box_data[4]

                if float(confidence) < self.config['minimal_confidences'][model]:
                    continue
                confidence = int(confidence*100)/100
                xmin, ymin, xmax, ymax = int(box_data[0]), int(box_data[1]), int(box_data[2]), int(box_data[3])
                cv2.rectangle(frame, (xmin, ymin) , (xmax, ymax), colors[_class], 3)
                cv2.putText(frame, f"{name}:{confidence}", (xmin, ymin - 50), cv2.FONT_HERSHEY_SIMPLEX, 1, colors[_class], 4)

                objects.append((confidence, (xmin, ymin, xmax, ymax)))
        return objects

if __name__ == '__main__':
    logging.basicConfig()
    logger.setLevel(logging.DEBUG)

    vision = Vision()
