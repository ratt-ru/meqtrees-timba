#!/usr/bin/python

from qt import QPixmap

# A QPixMap wrapper defers initialization of a pixmap until the pixmap
# is actually retrieved with the pm() method for the first time.
class QPixmapWrapper(object):
  def __init__(self,xpmstr):
    self._xpmstr = xpmstr;
    self._pm = None;
  def pm (self):
    if self._pm is None:
      self._pm = QPixmap(self._xpmstr);
    return self._pm;

exclaim = QPixmapWrapper([ "14 14 3 1",
          "       c None",
          ".      c red",
          "X      c yellow",
          "              ",
          "     ....     ",
          "    ......    ",
          "    ......    ",
          "    ......    ",
          "    ......    ",
          "    ......    ",
          "     ....     ",
          "     ....     ",
          "      ..      ",
          "              ",
          "      ..      ",
          "     ....     ",
          "      ..      " ]);
          
cancel = QPixmapWrapper([ "20 20 4 1",
                          "  c None",
                          ". c #FF0000",
                          "X c #C00000",
                          "o c None",
                          "                    ",
                          "                    ",
                          "                    ",
                          "                    ",
                          "                    ",
                          "     .       ..     ",
                          "     ..     .XX     ",
                          "     .X.   .X       ",
                          "     .XXX .X        ",
                          "      XXX.X         ",
                          "       XXXX         ",
                          "       .XXXX        ",
                          "      .X XXXX       ",
                          "     .X   XXXX      ",
                          "     .     XXXX     ",
                          "     X              ",
                          "                    ",
                          "                    ",
                          "                    ",
                          "                    "]);

check = QPixmapWrapper(["20 20 4 1",
                        "  c None",
                        ". c #00FF00",
                        "X c #00C000",
                        "o c None",
                        "                    ",
                        "                    ",
                        "                    ",
                        "               X    ",
                        "              .     ",
                        "              X     ",
                        "             X      ",
                        "            .X      ",
                        "            .       ",
                        "    .      .X       ",
                        "    ..    .X        ",
                        "    .X.   .X        ",
                        "    .XXX .X         ",
                        "     XXXXXX         ",
                        "      XXXXX         ",
                        "       XXXX         ",
                        "        XX          ",
                        "                    ",
                        "                    ",
                        "                    "]);
          
pause_green = QPixmapWrapper(["22 15 4 1",
                       "  c None",
                       ". c #303030",
                       "X c #00FF00",
                       "o c None",
                       "                      ",
                       "      XXX.   XXX.     ",
                       "     XXX..  XXX..     ",
                       "     XXX..  XXX..     ",
                       "     XXX..  XXX..     ",
                       "     XXX..  XXX..     ",
                       "     XXX..  XXX..     ",
                       "     XXX..  XXX..     ",
                       "     XXX..  XXX..     ",
                       "     XXX..  XXX..     ",
                       "     XXX..  XXX..     ",
                       "     XXX..  XXX..     ",
                       "     XXX.   XXX.      ",
                       "                      ",
                       "                      " ]);
pause_normal = QPixmapWrapper(["22 15 4 1",
                       "  c None",
                       ". c #303030",
                       "X c #0000FF",
                       "o c None",
                       "                      ",
                       "      XXX.   XXX.     ",
                       "     XXX..  XXX..     ",
                       "     XXX..  XXX..     ",
                       "     XXX..  XXX..     ",
                       "     XXX..  XXX..     ",
                       "     XXX..  XXX..     ",
                       "     XXX..  XXX..     ",
                       "     XXX..  XXX..     ",
                       "     XXX..  XXX..     ",
                       "     XXX..  XXX..     ",
                       "     XXX..  XXX..     ",
                       "     XXX.   XXX.      ",
                       "                      ",
                       "                      " ]);






