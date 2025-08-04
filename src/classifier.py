import cv2
import torch 
from ultralytics import YOLO

class Classifier:
    def __init__(self, model_name, target_classes=[]):
        self.model = None
        self.target_classes = target_classes
        self.model_name = model_name
    
    def load_model(self):
        self.model = YOLO(self.model_name)
            # Use GPU if available
        if torch.cuda.is_available():
            print("CUDA found")
            device = torch.device('cuda')
        else:
            print("CUDA not found, using cpu")
            device = torch.device('cpu')
        self.model.to(device)
    
    def predict_target(self, frame):
        detections = self.model(frame)[0].boxes
        if len(detections) == 0:
            return []
        # Filter detections by class
        if len(self.target_classes) > 0:
            target_indices = [i for i, cls_id in enumerate(detections.cls.cpu()) if int(cls_id) in self.target_classes]
        else:
            target_indices = [i for i in range(0, len(detections.cls.cpu()))]
        return [(detections.xyxy.cpu()[i], detections.conf.cpu()[i], detections.cls.cpu()[i]) for i in target_indices]

    def annotate_frame(self, frame, detections):
        for detection in detections:
            x1, y1, x2, y2 = detection[0].int().tolist()
            cx, cy = ((x1 + x2) // 2, (y1 + y2) // 2)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)
            cv2.putText(frame, f"{self.model.names[int(detection[2])]} {detection[1]:.2f}", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        return frame

    


