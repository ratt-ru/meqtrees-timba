#!/usr/bin/python2.3

import motor_control

if __name__ == "__main__":
  motor_control.init('/dev/ttyS0');

  # move motors inwards to limit, 20x255 steps just to be sure
  for step in range(20):
    for motor in motor_control.HEXAPOD_MOTORS:
      motor_control.move(motor,0,255);
    
  # move motors outward 10x255 steps -- home position
  for step in range(10):
    for motor in motor_control.HEXAPOD_MOTORS:
      motor_control.move(motor,1,255);
