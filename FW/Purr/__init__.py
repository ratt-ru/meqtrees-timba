# init debug printing
import Timba.utils
_verbosity = Timba.utils.verbosity(name="purr");
dprint = _verbosity.dprint;
dprintf = _verbosity.dprintf;

import Timba.GUI.pixmaps 
pixmaps = Timba.GUI.pixmaps.PixmapCache("purr");


import Timba.Apps.config
Config = Timba.Apps.config.section("Purr");

from LogEntry import DataProduct,LogEntry
from MainWindow import MainWindow
from Editors import *
from Purrer import *

import Parsers

