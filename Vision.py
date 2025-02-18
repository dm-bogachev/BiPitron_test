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

    def prediction_cases(self, model, box_data, keypoints_data = None, frame = None):
        kp = keypoints_data
        if model == 'Rounds':
            xmin, ymin, xmax, ymax = int(box_data[0]), int(box_data[1]), int(box_data[2]), int(box_data[3])
            center_x = (xmin + xmax) // 2
            center_y = (ymin + ymax) // 2
            logger.info(f"Center coordinates: ({center_x/10}, {center_y/10})")
            return [int(center_x), int(center_y), 0]
        if model == 'Smalls':
            topx, topy, midx, midy, botx, boty = int(kp[0][0]),int(kp[0][1]),int(kp[1][0]),int(kp[1][1]),int(kp[2][0]),int(kp[2][1])
            cv2.circle(frame, (topx, topy), 10, COLOR_RED, -1)
            cv2.circle(frame, (botx, boty), 10, COLOR_BLUE, -1)
            if topy < boty:
                alpha = 0
            else:
                alpha = 1800
            #pickx, picky = int((xmin+xmax)/2), int((ymin+ymax)/2)
            return [int(midx), int(midy), alpha]
        if model == 'Longs':
            topx, topy, midx, midy, botx, boty = int(kp[0][0]),int(kp[0][1]),int(kp[1][0]),int(kp[1][1]),int(kp[2][0]),int(kp[2][1])
            cv2.circle(frame, (topx, topy), 10, COLOR_RED, -1)
            cv2.circle(frame, (botx, boty), 10, COLOR_BLUE, -1)
            if topy < boty:
                alpha = 1800
            else:
                alpha = 0
            #pickx, picky = int((xmin+xmax)/2), int((ymin+ymax)/2)
            return [int(midx), int(midy), alpha]
        ## Extra code for extra models

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
                if self.config['display_box']:
                    cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), colors[_class], 3)
                if self.config['display_confidence']:
                    cv2.putText(frame, f"{name}:{confidence}", (xmin, ymin - 50), cv2.FONT_HERSHEY_SIMPLEX, 1, colors[_class], 4)

                if self.config['model_type'][model] == 'detect':
                    return_data = self.prediction_cases(model, box_data)
                    if self.config['display_pose']:
                        cv2.circle(frame, (return_data[0], return_data[1]), 10, colors[_class], -1)
                    if self.config['display_coordinates']:
                        cv2.putText(frame, f"({return_data[0]/10}, {return_data[1]/10})", (xmin, ymin - 20), cv2.FONT_HERSHEY_SIMPLEX, 1, colors[_class], 4)
                if self.config['model_type'][model] == 'pose':
                    return_data = self.prediction_cases(model, box_data, keypoints_data, frame)
                    if self.config['display_pose']:
                        cv2.circle(frame, (return_data[0], return_data[1]), 10, colors[_class], -1)
                    if self.config['display_coordinates']:
                        cv2.putText(frame, f"({return_data[0]/10}, {return_data[1]/10})", (xmin, ymin - 20), cv2.FONT_HERSHEY_SIMPLEX, 1, colors[_class], 4)

                return_data = [coord / 10 for coord in return_data]
                objects.append((model, _class, confidence, return_data))
        return objects

if __name__ == '__main__':
    logging.basicConfig()
    logger.setLevel(logging.DEBUG)

    vision = Vision()
