#!/usr/bin/python2.3

import motor_control
import time

if __name__ == "__main__":
  motor_control.init('/dev/ttyS0');

  print "Moving to inward position";
  # move motors inwards to limit, 20x255 steps just to be sure
  for step in range(30):
    print step,"/ 30";
    for motor in motor_control.ALL_MOTORS:
      motor_control.move(motor,0,255);
    time.sleep(1);
    
  print "Moving outward to home position";
  # move motors outward 10x255 steps -- home position
  for step in range(10):
    print step,"/ 10";
    for motor in motor_control.ALL_MOTORS:
      motor_control.move(motor,1,255);
    time.sleep(1);
