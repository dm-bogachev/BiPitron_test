import cv2
import numpy as np

class ArucoMarker():
    def __init__(self, id, center, corners):
        self.id = id
        self.center = center
        [self.topLeft, self.topRight, self.bottomRight, self.bottomLeft] = corners

class ArucoDetector:    
    def __init__(self):
        self.aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_100)
        self.parameters = cv2.aruco.DetectorParameters()
        self.detector = cv2.aruco.ArucoDetector(self.aruco_dict, self.parameters)

    def detectMarkers(self, gray_frame):
        self.corners, self.idsd, self.rejected = self.detector.detectMarkers(gray_frame)
        print("Detected markers:", self.idsd)
        markers = {}
        try:
            ids = np.copy(self.idsd)
            ids = ids.flatten()
            
            for (markerCorner, markerID) in zip(self.corners, ids):   
                self.corners = markerCorner.reshape((4, 2))
                (topLeft, topRight, bottomRight, bottomLeft) = self.corners
                topRight = [int(topRight[0]), int(topRight[1])]
                bottomRight = [int(bottomRight[0]), int(bottomRight[1])]
                bottomLeft = [int(bottomLeft[0]), int(bottomLeft[1])]
                topLeft = [int(topLeft[0]), int(topLeft[1])]
                cX = int((topLeft[0] + bottomRight[0]) / 2.0)
                cY = int((topLeft[1] + bottomRight[1]) / 2.0)
                print("[INFO] ArUco marker ID: {}".format(markerID))
                markers[markerID] = ArucoMarker(markerID, [cX, cY], [topLeft, topRight, bottomRight, bottomLeft])
            return markers
        except Exception as e:
            print(e)
            return markers

if __name__ == '__main__':
    from HikCamera.HikCamera import *
    from Colors import *
    cam = Camera()
    cam.open()
    e = 10000
    cam.set_exposure(e)
    cv2.namedWindow("Frame", cv2.WINDOW_FREERATIO)

    aruco = ArucoDetector()

    while True:
        gray = cam.get_frame()
        frame = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        markers = aruco.detectMarkers(gray)

        if len(markers) > 0:
            for id, marker in markers.items():
                cv2.drawMarker(frame, marker.center, COLOR_PINK, cv2.MARKER_CROSS, 5, 8)

        cv2.imshow("Frame", frame)
        cmd = cv2.waitKey(1)
