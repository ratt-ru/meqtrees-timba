

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

__metaclass__ = type

import re, numarray
from numarray import fromstring, UInt16, UInt8

_nonspace = re.compile('\\S+')

class InvalidImage(Exception): pass

def _next_token(data, pos):
    while True:
        match = _nonspace.search(data, pos)
        text, pos = match.group(0), match.end()
        if not text.startswith('#'):
            break
        pos = data.index('\n', pos) + 1
    return int(text), pos

class Image:

    def __init__(self, data):
        try:
            self._parse(data)
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception, e:
            raise InvalidImage(e)

    def _get_maxval(self):
        return self._maxval

    maxval = property(_get_maxval)

    def _get_pixels(self):
        return self._pixels

    pixels = property(_get_pixels)

    def _parse(self, data):
        assert data.startswith('P5')
        pos = 2
        self._width, pos = _next_token(data, pos)
        self._height, pos = _next_token(data, pos)
        self._maxval, pos = _next_token(data, pos)
        pixels = data[pos+1:]
        assert 0 < self._maxval < 65536
        shape = (self._width, self._height)
        if self._maxval < 256:
            typeobj = UInt8
        else:
            typeobj = UInt16
        self._pixels = fromstring(pixels, typeobj, shape)
