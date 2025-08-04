/* Sweep
 by BARRAGAN <http://barraganstudio.com>
 This example code is in the public domain.

 modified 8 Nov 2013
 by Scott Fitzgerald
 https://www.arduino.cc/en/Tutorial/LibraryExamples/Sweep
*/

#include <Servo.h>

Servo servoPan;
Servo servoTilt;

void setup() {
  Serial.begin(9600);
  servoPan.attach(9);  // attaches the servo on pin 9 to the Servo object
  servoTilt.attach(10);  // attaches the servo on pin 9 to the Servo object
}

int mapValue(int val, int prevMax, int prevMin, int newMax, int newMin)
{
  return (val - prevMin) * (newMax - newMin) / (prevMax - prevMin) + newMin;
}

int mapPan(int x)
{
  return mapValue(x, 90, -90, 180, 0);
}

int mapTilt(int x)
{
  // mapping angle in degrees from [0, 180] to [10, 120]
  x = mapValue(x, 90, -90, 180, 0);
  return mapValue(x, 180, 0, 105, 15);
}

void loop() {
  if (Serial.available()) {
    String input = Serial.readStringUntil('\n');

    int pIdx = input.indexOf('P');
    int tIdx = input.indexOf('T');

    if (pIdx != -1 && tIdx != -1) {
      int pan = input.substring(pIdx + 1, tIdx).toInt();
      int tilt = input.substring(tIdx + 1).toInt();

      pan = constrain(mapPan(pan), 0, 179);
      tilt = constrain(mapTilt(tilt), 0, 179);

      servoPan.write(pan);
      servoTilt.write(tilt);
    }
  }
}
