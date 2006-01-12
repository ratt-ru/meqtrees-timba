
# pull this first to skip all GUI definitions and includes
from Timba.Apps import app_nogui

from Timba.Apps import meqserver
from Timba.TDL import Compile
from Timba.Meq import meqds

import sys
import traceback

# testing branch
if __name__ == '__main__':
  mqs = meqserver.default_mqs(wait_init=5);

  print 'meqserver state:',mqs.state;

  (mod,msg) = Compile.compile_file(mqs,'tdl_test.tdl');

  mod._test_forest(mqs,None);

  req = mqs.getnodestate('solver').request;

  res = mqs.execute('x',req,wait=True);

  print res;
    
