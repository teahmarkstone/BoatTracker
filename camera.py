import cv2
import numpy as np
ZOOM_MAX = 2.0
ZOOM_MIN = 1.0

class Camera:
    def __init__(self, camera_id=0):
        self.camera_id = camera_id
        self.stream = None
        self.curr_zoom = 1.0
    
    def load_camera(self):
        self.stream = cv2.VideoCapture(self.camera_id)
    
    def close_camera(self):
        self.stream.release()
    
    def get_frame(self): 
        return self.stream.read()
    
    def update(self):
        ret, frame = self.stream.read()
        frame = self.zoom(frame)
        return ret, frame
    
    def set_zoom(self, zoom):
        self.curr_zoom = np.clip(zoom, ZOOM_MIN, ZOOM_MAX)
    
    def zoom(self, frame):
        h, w = frame.shape[:2]

        # Calculate crop size
        new_w = int(w / self.curr_zoom)
        new_h = int(h / self.curr_zoom)

        # Calculate top-left corner for centered crop
        x1 = (w - new_w) // 2
        y1 = (h - new_h) // 2
        x2 = x1 + new_w
        y2 = y1 + new_h

        # Crop and resize back to original size
        cropped = frame[y1:y2, x1:x2]
        zoomed = cv2.resize(cropped, (w, h), interpolation=cv2.INTER_LINEAR)
        return zoomed

    

    