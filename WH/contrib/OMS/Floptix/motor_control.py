#
#% $Id$ 
#
#
# Copyright (C) 2002-2007
# The MeqTree Foundation & 
# ASTRON (Netherlands Foundation for Research in Astronomy)
# P.O.Box 2, 7990 AA Dwingeloo, The Netherlands
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>,
# or write to the Free Software Foundation, Inc., 
# 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

import serial
import time

motor_addresses = {};
motor_addresses[1] = 0x02;
motor_addresses[2] = 0x04;
motor_addresses[3] = 0x06;
motor_addresses[4] = 0x08;
motor_addresses[5] = 0x0A;
motor_addresses[6] = 0x0C;
motor_addresses[7] = 0x0E;

HEXAPOD_MOTORS = range(1,7);
TILT_MOTOR = 7;
ALL_MOTORS = range(1,8)

DELAY = 0.005;    # delay between characters, in seconds

port = None;


def init (portname='/dev/ttyS0'):
  global port;
  port = serial.Serial(portname,115200);


def motor_cmd (motor,direction,steps):
  addr = motor_addresses[motor];
  return "1S%02xS%02xS%02x3" % (addr,direction,steps);


def send_command (command_string):
  """writes stuff to the port, with a 3ms delay between characters""";
  for char in command_string:
    port.write(char);
    time1 = time.time()+DELAY;
    while time.time() < time1:
      time.sleep(DELAY);


def move (motor,direction,steps):
  send_command(motor_cmd(motor,direction,steps));
