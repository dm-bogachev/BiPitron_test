import cv2

class Webcamera():
    
    def __init__(self, camera_address = 0):
        self.camera = cv2.VideoCapture(camera_address)

    def open(self):
        pass

    def set_exposure(self, exposure):
        pass

    def get_frame(self):
        ret, frame = self.camera.read()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if not ret:
            raise Exception("Failed to capture image")
        return frame