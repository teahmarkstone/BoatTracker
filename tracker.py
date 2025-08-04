from pid import PIDController
from camera import ZOOM_MAX, ZOOM_MIN

class Tracker:
    def __init__(self, pan_pid, tilt_pid):
        self.pan_PID = PIDController(*pan_pid)
        self.tilt_PID = PIDController(*tilt_pid)
        
        self.smoothing_window = 5
        self.pan_history = []
        self.tilt_history = []

        self.curr_zoom = 1.0
        self.curr_command = (0, 90)
    
    def update(self, frame, detection, dt):
        x1, y1, x2, y2 = detection[0].int().tolist()
        cx, cy = ((x1 + x2) // 2, (y1 + y2) // 2)
        h, w = frame.shape[:2]
        cx_img, cy_img = w // 2, h // 2

        # zoom
        box_w = x2 - x1
        box_h = y2 - y1
        target_size = max(box_w, box_h)

        target_zoom = self.calculate_zoom((cx, cy), box_w, box_h, w, h)
        self.curr_zoom = target_zoom


        # Errors relative to image center
        error_x = cx_img - cx
        error_y = cy - cy_img

        # PID computations
        pan_adjust = self.pan_PID.compute(error_x, dt)
        tilt_adjust = self.tilt_PID.compute(error_y, dt)
        current_pan, current_tilt = self.curr_command

        MAX_SHIFT = 5  # max pixels per frame
        current_pan += max(-MAX_SHIFT, min(MAX_SHIFT, pan_adjust))
        current_tilt += max(-MAX_SHIFT, min(MAX_SHIFT, tilt_adjust))

        # keep it in bounds
        current_pan = max(-90, min(90, current_pan))
        current_tilt = max(-90, min(90, current_tilt))

        self.pan_history.append(current_pan)
        self.tilt_history.append(current_tilt)

        if len(self.pan_history) > self.smoothing_window:
            self.pan_history.pop(0)
            self.tilt_history.pop(0)

        pan_smoothed = sum(self.pan_history) / len(self.pan_history)
        tilt_smoothed = sum(self.tilt_history) / len(self.tilt_history)
        self.curr_command = pan_smoothed, tilt_smoothed
        return pan_smoothed, tilt_smoothed, self.curr_zoom

    def calculate_zoom(self, boxCenter, box_width, box_height, frame_width, frame_height, target_fill_ratio=0.6):

        # Normalize bbox dimensions by current zoom to get "true" object size
        normalized_box_width = box_width / self.curr_zoom
        normalized_box_height = box_height / self.curr_zoom
        
        # Calculate current fill ratios using normalized dimensions
        width_ratio = normalized_box_width / frame_width
        height_ratio = normalized_box_height / frame_height
        
        # Use the larger ratio (limiting dimension)
        current_fill_ratio = max(width_ratio, height_ratio)
        
        # Avoid division by zero
        if current_fill_ratio < 0.01:
            return 1.0
        
        # Calculate zoom needed to achieve target fill ratio
        target_zoom = target_fill_ratio / current_fill_ratio
        target_zoom = max(ZOOM_MIN, min(target_zoom, ZOOM_MAX))

        center_score = self.center_score(boxCenter, frame_width, frame_height)
            
        # Limit zoom based on how centered the object is
        if center_score < 0.7:  # Not well centered
            max_allowed_zoom = 1.0 + (ZOOM_MAX - 1.0) * center_score
            target_zoom = min(target_zoom, max_allowed_zoom)

        return target_zoom
    
    def center_score(self, boxCenter, frame_width, frame_height):
        box_center_x, box_center_y = boxCenter
        
        # Calculate distance from frame center
        frame_center_x = frame_width / 2
        frame_center_y = frame_height / 2
        
        x_offset = abs(box_center_x - frame_center_x)
        y_offset = abs(box_center_y - frame_center_y)
        
        # Normalize to 0-1 range
        x_ratio = x_offset / (frame_width / 2)
        y_ratio = y_offset / (frame_height / 2)
        
        # Calculate center score
        total_offset = (x_ratio + y_ratio) / 2
        center_score = max(0, 1.0 - total_offset)
        return center_score
