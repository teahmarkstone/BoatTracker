import serial
import time

class Arduino:
    def __init__(self, port='COM3', baudrate=9600, timeout=1):
        self.arduino = serial.Serial(port=port, baudrate=baudrate, timeout=timeout)
        self.last_command = (0, 90)
        self.home = (0, 90)
        time.sleep(2)
    
    def send_pan_tilt(self, pan, tilt):
        command = f'P{pan}T{tilt}\n'
        self.last_command = (pan, tilt)
        self.arduino.write(command.encode('utf-8'))
    
    def reset(self):
        self.send_pan_tilt(self.home[0], self.home[1])

    def close_connection(self):
        self.arduino.close()
        print("Serial connection closed.")
    
    def run_user_input(self):
        while True:
            user_input = input("> ").strip()
            if user_input.lower() == 'exit':
                break
            try:
                pan_str, tilt_str = user_input.split()
                pan = int(pan_str)
                tilt = int(tilt_str)
                self.send_pan_tilt(pan, tilt)
            except ValueError:
                print("Invalid input. Enter two integers separated by a space (e.g., '90 45').")
            finally:
                self.close_connection()