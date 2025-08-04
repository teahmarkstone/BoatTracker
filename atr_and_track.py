import cv2
import time
import warnings
from ultralytics import YOLO

from arduino import Arduino
from classifier import Classifier
from tracker import Tracker
from camera import Camera

warnings.filterwarnings("ignore", category=FutureWarning)

class BoatATR:
    def __init__(self, pan_pid, tilt_pid, persist=0):
        self.class_ids = [0]
        self.cam_id = 0
        self.model_name = 'best.pt'
        self.arduino = Arduino()
        self.camera = Camera(self.cam_id)
        self.classifier = Classifier(self.model_name, self.class_ids)
        self.tracker = Tracker(pan_pid, tilt_pid)

        self.last_time = time.time()

        self.last_detection = None # reformatted detections are ((x1, y1, x2, y2), conf, classId)
        self.time_of_last_detect = 0
        self.frames_since_last_detect = 0
        self.persist = persist

        # Search Mode states
        self.search_mode = False
        self.search_pan_left = True
        self.search_tilt_down = False
        self.search_mode_pan, self.search_mode_tilt = self.arduino.last_command

        self.camera.load_camera()
        self.classifier.load_model()
        self.arduino.reset()                
    
    def run(self):
        ret = True
        while (ret):
            # Gets frame and zooms if zoom set
            ret, frame = self.camera.update()
            if not ret:
                break
            # Get detections from classifier
            detections = self.classifier.predict_target(frame)
            # If we are sweep searching for the target 
            if self.search_mode:
                if len(detections) > 0:
                    self.search_mode = False
                else: 
                    self.sweep()
            else:
                self.track_mode(frame, detections)
            
            cv2.imshow('Boat ATR', frame)
            cv2.waitKey(5)
        self.camera.close_camera()
        cv2.destroyAllWindows()
    
    def track_mode(self, frame, detections):
        current_time = time.time()
        dt = current_time - self.last_time
        self.last_time = current_time

        # if we have detections
        if len(detections) > 0:
            self.time_of_last_detect = current_time
            self.frames_since_last_detect = 0
            # sort detections by confidence and get the most confident detection
            top_detect = sorted(detections, key=lambda x: x[1], reverse=True)[0]
            self.last_detection = top_detect
        else:
            self.frames_since_last_detect += 1
        # use last seen detection to keep the tracker steady
        if self.last_detection:
            # annotate frame with bounding box
            frame = self.classifier.annotate_frame(frame, [self.last_detection])
            # get tracking commands from tracker
            pan, tilt, zoom = self.tracker.update(frame, self.last_detection, dt)
            
            self.arduino.send_pan_tilt(pan, tilt)
            self.camera.set_zoom(zoom)

        # If we haven't gotten a new detection in x frames, stop maintaining last seen -- TUNE THIS OUTSIDE
        if self.frames_since_last_detect > self.persist:
            self.last_detection = None

        # Zoom out if we haven't seen the target in 5 seconds
        if current_time - self.time_of_last_detect > 5:
            print("Target Lost: Zooming Out")
            target_zoom = 1.0 
            self.camera.set_zoom(target_zoom) 

        # Start sweep search if we haven't seen the target in 10 seconds
        if current_time - self.time_of_last_detect > 10 and not self.search_mode:
            print('Target (Still) Lost: Starting Search Mode')
            # set start of the search to our current position
            self.search_mode_pan, self.search_mode_tilt = self.arduino.last_command
            self.search_mode = True

    def sweep(self):
        # panning to the left
        if self.search_pan_left:
            self.search_mode_pan -= 1
            if self.search_mode_pan <= -85:
                # Reverse pan direction once we have traveled all the way left
                self.search_pan_left = False
                # Change tilt at the end of the pan 
                if self.search_tilt_down:
                    self.search_mode_tilt += 3
                    # Reverse tilt direction if we reach the bottom of the tilt
                    if self.search_mode_tilt >= 85:
                        self.search_tilt_down = False
                else:
                    self.search_mode_tilt -= 3
                    # Reverse tilt direction if we reach top of tilt
                    if self.search_mode_tilt <= 5:
                        self.search_tilt_down = True
        # panning to the right
        else:
            self.search_mode_pan += 1
            if self.search_mode_pan >= 85:
                # Reverse pan direction once we have traveled all the way right
                self.search_pan_left = True
                # Change tilt at the end of the pan  
                if self.search_tilt_down:
                    self.search_mode_tilt += 3
                    # Reverse tilt direction if we reach the bottom of the tilt
                    if self.search_mode_tilt >= 85:
                        self.search_tilt_down = False
                else:
                    self.search_mode_tilt -= 3
                    # Reverse tilt direction if we reach top of tilt
                    if self.search_mode_tilt <= 5:
                        self.search_tilt_down = True
        # Command PTZ camera with new pan tilt
        self.arduino.send_pan_tilt(self.search_mode_pan, self.search_mode_tilt)



def main():
    pan_pid = (0.1, 0.01, 0.5)
    tilt_pid = (0.1, 0.01, 0.5)
    atr = BoatATR(pan_pid, tilt_pid)
    atr.run()

if __name__ == "__main__":
    main()