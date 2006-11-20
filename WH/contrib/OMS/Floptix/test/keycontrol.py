#!/usr/bin/python2.3

import motor_control
import sys
import tty
import termios

class Getch:
    def __call__(self):
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch
        
getch = Getch();


if __name__ == "__main__":
  motor_control.init('/dev/ttyS0');

  controls = {
    '1': (1,0,1),
    '2': (2,0,1),
    '3': (3,0,1),
    '4': (4,0,1),
    '5': (5,0,1),
    '6': (6,0,1),
    '7': (7,0,1),
    'q': (1,1,1),
    'w': (2,1,1),
    'e': (3,1,1),
    'r': (4,1,1),
    't': (5,1,1),
    'y': (6,1,1),
    'u': (7,1,1),
    '!': (1,0,10),
    '@': (2,0,10),
    '#': (3,0,10),
    '$': (4,0,10),
    '%': (5,0,10),
    '^': (6,0,10),
    '&': (7,0,10),
    'Q': (1,1,10),
    'W': (2,1,10),
    'E': (3,1,10),
    'R': (4,1,10),
    'T': (5,1,10),
    'Y': (6,1,10),
    'U': (7,1,10),
    'X': (None,None,None),
    'x': (None,None,None)
  };
  
  print "1234567 or QWERTYU moves motors; [Shift] to move x10, X to exit"
  while True:
    char = getch();
    if char in controls:
      (motor,direction,step) = controls[char];
      if motor is None:
        break;
      print "motor",motor,"dir",direction,"steps",step;
      motor_control.move(motor,direction,step);
