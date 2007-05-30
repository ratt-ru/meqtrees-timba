
import Timba.utils
_dbg = Timba.utils.verbosity(0,name='trut');
_dprint = _dbg.dprint;
_dprintf = _dbg.dprintf;

from Unit import Unit
from File import File
from Main import run_files

# error types
class ParseError (RuntimeError):
  pass;
class TestError (RuntimeError):
  pass;
class UnexpectedError (RuntimeError):
  pass;