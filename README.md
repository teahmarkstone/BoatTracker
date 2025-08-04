# Boat Tracking System

A real-time computer vision system for automatic boat detection, tracking, and following using a pan-tilt-zoom (PTZ) camera controlled via Arduino.

## Overview

This system combines YOLO object detection with PID control to automatically track boats in real-time video feeds. When a boat is detected, the system uses a PTZ camera to keep the target centered in the frame, automatically adjusting pan, tilt, and zoom parameters. If the target is lost, the system enters a sweep search mode to relocate it.

## Features

- **Real-time boat detection** using YOLOv11 deep learning model
- **Automatic PTZ camera control** via Arduino serial communication
- **PID-based tracking** for smooth and stable target following
- **Intelligent zoom control** that adapts based on target size and position
- **Search mode** that automatically sweeps the area when target is lost
- **Persistence handling** to maintain tracking through brief occlusions
- **GPU acceleration** support for improved performance

## System Architecture

The system consists of several modular components:

- **BoatATR**: Main orchestrator handling detection, tracking, and search modes
- **Camera**: Video capture and digital zoom functionality
- **Classifier**: YOLO-based object detection and frame annotation
- **Tracker**: PID controller for smooth camera movements
- **Arduino**: Serial communication interface for hardware control
- **PIDController**: Generic PID implementation for control systems

## Hardware Requirements

- **Camera**: USB webcam or IP camera compatible with OpenCV
- **Arduino**: Microcontroller for PTZ camera control
- **PTZ Camera System**: Pan-tilt mechanism with servo motors
- **Serial Connection**: USB cable between computer and Arduino

## Software Dependencies

```bash
pip install opencv-python
pip install ultralytics
pip install pyserial
pip install torch torchvision  # For GPU acceleration
pip install numpy
```

## Installation

1. Clone or download the project files
2. Install the required Python packages (see dependencies above)
3. Ensure you have a trained YOLO model file named `best.pt` in the project directory
4. Connect your Arduino to the appropriate COM port (default: COM3)
5. Upload the corresponding Arduino sketch to handle pan-tilt commands

## Configuration

### Arduino Setup
- Default port: `COM3`
- Baud rate: `9600`
- Command format: `P{pan}T{tilt}\n`
- Pan/tilt range: -90° to +90°

### Camera Settings
- Default camera ID: `0` (first available camera)
- Zoom range: 1.0x to 2.0x
- Resolution: Depends on camera capabilities

### PID Tuning
Default PID parameters for pan and tilt control:
```python
pan_pid = (0.1, 0.01, 0.5)   # (Kp, Ki, Kd)
tilt_pid = (0.1, 0.01, 0.5)  # (Kp, Ki, Kd)
```

## Usage

### Basic Operation
```python
from atr_and_track import BoatATR

# Initialize with PID parameters
pan_pid = (0.1, 0.01, 0.5)
tilt_pid = (0.1, 0.01, 0.5)
atr = BoatATR(pan_pid, tilt_pid)

# Start tracking
atr.run()
```

### Manual Arduino Control
```python
from arduino import Arduino

arduino = Arduino(port='COM3')

# Manual pan/tilt control
arduino.send_pan_tilt(45, 30)  # Pan 45°, Tilt 30°

# Interactive mode
arduino.run_user_input()  # Enter commands like "90 45"

# Reset to home position
arduino.reset()

# Close connection
arduino.close_connection()
```

## System Behavior

### Tracking Mode
- Detects boats using YOLO model
- Maintains target in center of frame using PID control
- Adjusts zoom based on target size and centering
- Handles brief occlusions with persistence mechanism

### Search Mode
- Activates after 10 seconds without target detection
- Performs systematic sweep pattern across pan/tilt range
- Returns to tracking mode when target is reacquired
- Zooms out after 5 seconds of target loss

### Zoom Control
- Automatically adjusts zoom to maintain optimal target size
- Target fill ratio: 60% of frame
- Limits zoom when target is not well-centered
- Range: 1.0x to 2.0x magnification

## File Structure

```
├── atr_and_track.py    # Main application and BoatATR class
├── arduino.py          # Arduino serial communication
├── camera.py           # Camera capture and zoom control
├── classifier.py       # YOLO detection and annotation
├── tracker.py          # PID-based tracking controller
├── pid.py              # PID controller implementation
└── best.pt             # Trained YOLO model (not included)
```

## Customization

### Model Training
To use your own detection model:
1. Train a YOLO model on your specific boat dataset
2. Replace `best.pt` with your trained model
3. Update `class_ids` in BoatATR initialization if needed

### Hardware Adaptation
- Modify `Arduino` class for different communication protocols
- Adjust pan/tilt limits in `tracker.py` for your hardware
- Update zoom parameters in `camera.py` for different ranges

### Performance Tuning
- Adjust PID parameters for your specific hardware characteristics
- Modify persistence settings for different tracking scenarios
- Tune search pattern parameters in the `sweep()` method

## Troubleshooting

### Common Issues
- **No serial connection**: Check COM port and Arduino connection
- **Poor detection**: Verify YOLO model compatibility and lighting conditions
- **Unstable tracking**: Tune PID parameters or increase smoothing window
- **Camera not found**: Check camera ID and OpenCV installation

### Performance Optimization
- Enable GPU acceleration for YOLO inference
- Reduce camera resolution for faster processing
- Adjust detection confidence threshold in classifier
- Implement multi-threading for concurrent operations

## License

This project is provided as-is for educational and research purposes. Please ensure compliance with local regulations when using automated tracking systems.

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve the system's functionality and robustness.
