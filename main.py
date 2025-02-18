import time
import logging

logger = logging.getLogger()
logging.basicConfig()
logger.setLevel(logging.DEBUG)

from Logic import Logic
logic = Logic()
logic.start()

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

import cv2
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

def generate_frames():
    while True:
        frame = logic.display_frame
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.get("/video_feed")
def video_feed():
    return StreamingResponse(generate_frames(), media_type="multipart/x-mixed-replace; boundary=frame")

# Logic API
@app.get("/logic/next_object")
def next_object():
    a = logic.next_object()
    return logic.next_object()

# Vision API
@app.get("/vision/get_models")
def get_models():
    return logic.v.get_models()

@app.get("/vision/set_model")
def set_model(model: str):
    if model in logic.v.get_models():
        logic.v.set_model(model)
        return {"model_set": model}
    else:
        return {"error": "Model not found"}

@app.get("/vision/get_model")
def get_model():
    return {"model": logic.v.current_model}

@app.get("/vision/get_confidence")
def get_confidence(model: str):
    if model in logic.v.get_models():
        return {"confidence": logic.v.config['minimal_confidences'][model]}
    else:
        return {"error": "Model not found"}

@app.get("/vision/set_confidence")
def set_confidence(model: str, confidence: float):
    if model in logic.v.get_models():
        logic.v.config['minimal_confidences'][model] = confidence
        return {"confidence_set": confidence}
    else:
        return {"error": "Model not found"}

@app.get("/vision/get_objects")
def get_objects():
    return logic.objects

@app.get("/vision/get_display_box")
def get_display_box():
    return {"display_box": logic.v.config['display_box']}

@app.get("/vision/set_display_box")
def set_display_box(display_box: bool):
    logic.v.config['display_box'] = display_box
    return {"display_box": display_box}

@app.get("/vision/get_display_pose")
def get_display_pose():
    return {"display_pose": logic.v.config['display_pose']}

@app.get("/vision/set_display_pose")
def set_display_pose(display_pose: bool):
    logic.v.config['display_pose'] = display_pose
    return {"display_pose": display_pose}

@app.get("/vision/get_display_coordinates")
def get_display_coordinates():
    return {"display_coordinates": logic.v.config['display_coordinates']}

@app.get("/vision/set_display_coordinates")
def set_display_coordinates(display_coordinates: bool):
    logic.v.config['display_coordinates'] = display_coordinates
    return {"display_coordinates": display_coordinates}

@app.get("/vision/get_display_confidence")
def get_display_confidence():
    return {"display_confidence": logic.v.config['display_confidence']}

@app.get("/vision/set_display_confidence")
def set_display_confidence(display_confidence: bool):
    logic.v.config['display_confidence'] = display_confidence
    return {"display_confidence": display_confidence}

    # @app.get("/vision/get_display_config")
    # def get_display_config():
    #     return {
    #         "display_box": logic.v.config['display_box'],
    #         "display_pose": logic.v.config['display_pose'],
    #         "display_coordinates": logic.v.config['display_coordinates'],
    #         "display_confidence": logic.v.config['display_confidence']
    #     }

    # @app.post("/vision/set_display_config")
    # def set_display_config(display_box: bool = None, display_pose: bool = None, display_coordinates: bool = None, display_confidence: bool = None):
    #     if display_box is not None:
    #         logic.v.config['display_box'] = display_box
    #     if display_pose is not None:
    #         logic.v.config['display_pose'] = display_pose
    #     if display_coordinates is not None:
    #         logic.v.config['display_coordinates'] = display_coordinates
    #     if display_confidence is not None:
    #         logic.v.config['display_confidence'] = display_confidence
    #     return {"display_config_updated": True}

# FrameGrabber API
@app.get("/framegrabber/set_exposure")
def set_exposure(exposure: int):
    if 162 <= exposure <= 900000:
        logic.fg.set_exposure(exposure)
        return {"exposure_set": exposure}
    else:
        return {"error": "Exposure value out of range. Must be between 162 and 900000."}

@app.get("/framegrabber/get_exposure")
def get_exposure():
    return {"exposure": logic.fg.get_exposure()}

@app.get("/framegrabber/get_markers_x_distance")
def get_markers_x_distance():
    return {"markers_x_distance": logic.fg.config['markers_x_distance']}

@app.get("/framegrabber/get_markers_y_distance")
def get_markers_y_distance():
    return {"markers_y_distance": logic.fg.config['markers_y_distance']}

@app.get("/framegrabber/set_markers_x_distance")
def set_markers_x_distance(distance: int):
    if 0 <= distance <= 900000:
        logic.fg.config['markers_x_distance'] = distance
        return {"markers_x_distance": distance}
    else:
        return {"error": "Distance value out of range. Must be between 0 and 900000."}

@app.get("/framegrabber/set_markers_y_distance")
def set_markers_y_distance(distance: int):
    if 0 <= distance <= 900000:
        logic.fg.config['markers_y_distance'] = distance
        return {"markers_y_distance": distance}
    else:
        return {"error": "Distance value out of range. Must be between 0 and 900000."}

@app.get("/framegrabber/calibrate")
def calibrate():
    logic.fg.calibrate()
    return {"calibrated": True}

@app.get("/framegrabber/uncalibrate")
def uncalibrate():
    logic.fg.uncalibrate()
    return {"calibrated": False}

# Robot API
@app.get("/robot/connection")
def robot_status():
    return {"connected": logic.robot.connection.connected}

@app.get("/robot/pick")
def robot_pick(class_id: str, x: float, y: float, a: float = None):
    if a is not None:
        return logic.robot.send_pick(class_id, (x, y, a))
    else:
        return logic.robot.send_pick(class_id, (x, y) )

@app.get("/robot/measurement")
def robot_measurement(result: bool):
    return logic.robot.send_measurement_request(result)