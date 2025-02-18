from HikCamera.HikCamera import *
from Colors import *
from ArucoDetector import *
from FrameGrabberConfig import *

import logging
logger = logging.getLogger()


class FrameGrabber:
    def __init__(self):
        logger.info('Initializing frame grabber')
        self.config = FrameGrabberConfig()
        self.M = None
        try:
            self.M = np.load('calibration_data.npy')
            logger.info('Calibration data loaded')
        except Exception:
            logger.error('Calibration data not found')
            pass

        logger.info('Initializing camera')
        self.camera = Camera()
        self.camera.open()
        self.camera.set_exposure(self.config['exposure'])

        self.aruco = ArucoDetector()

    def uncalibrate(self):
        self.M = None
        logger.info('Calibration data removed')

    def calibrate(self):
        logger.info('Begin calibration')
        gray = self.camera.get_frame()
        frame = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        markers = self.aruco.detectMarkers(gray)

        cv2.drawMarker(frame, markers[0].bottomLeft, COLOR_BLUE, markerSize=6)
        logger.info(f'Found {len(markers)} markers')
        if len(markers) >= 4:
            start_p = np.float32(
                [markers[1].topRight, markers[3].bottomRight, markers[2].bottomLeft, markers[0].topLeft])
            dest_p = np.float32([[0, 0], [self.config['markers_x_distance'], 0], [
                                self.config['markers_x_distance'], self.config['markers_y_distance']], [0, self.config['markers_y_distance']]])
            self.M = cv2.getPerspectiveTransform(start_p, dest_p)
            np.save("calibration_data", self.M)
            logger.info('Calibration data updated')

    def set_exposure(self, exposure):
        self.camera.set_exposure(exposure)
        self.config['exposure'] = exposure

    def get_exposure(self):
        return self.config['exposure']

    def get_frame(self):
        gray = self.camera.get_frame()
        frame = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

        try:
            h,  w = frame.shape[:2]
            result = cv2.warpPerspective(frame, self.M, [self.config['markers_x_distance'], self.config['markers_y_distance']])
            markers = self.aruco.detectMarkers(result)
            for id, marker in markers.items():
                cv2.drawMarker(result, marker.center, COLOR_PINK, cv2.MARKER_CROSS, 15, 8)
                points = np.array([marker.topLeft, marker.topRight, marker.bottomRight, marker.bottomLeft], np.int32)
                points = points.reshape((-1, 1, 2))
                cv2.polylines(result, [points], isClosed=True, color=COLOR_PINK, thickness=2)

            return result
        except Exception:
            markers = self.aruco.detectMarkers(frame)
            for id, marker in markers.items():
                cv2.drawMarker(frame, marker.center, COLOR_PINK, cv2.MARKER_CROSS, 15, 8)
                points = np.array([marker.topLeft, marker.topRight, marker.bottomRight, marker.bottomLeft], np.int32)
                points = points.reshape((-1, 1, 2))
                cv2.polylines(frame, [points], isClosed=True, color=COLOR_PINK, thickness=2)
            return frame


if __name__ == '__main__':
    logging.basicConfig()
    logger.setLevel(logging.DEBUG)
    cv2.namedWindow("Frame", cv2.WINDOW_FREERATIO)
    framer = FrameGrabber()
    while True:
        frame = framer.get_frame()
        markers = framer.aruco.detectMarkers(frame)
        if len(markers) > 0:
            for id, marker in markers.items():
                cv2.drawMarker(frame, marker.center, COLOR_PINK,
                               cv2.MARKER_CROSS, 15, 8)
        cv2.imshow("Frame", frame)
        cmd = cv2.waitKey(1)
        if cmd == ord('c'):
            framer.calibrate()
        if cmd == ord('q'):
            break