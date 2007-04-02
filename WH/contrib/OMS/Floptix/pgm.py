

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
