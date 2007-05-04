
# pull this first to skip all GUI definitions and includes
from Timba.Apps import app_nogui

from Timba.Apps import meqserver
from Timba.TDL import Compile
from Timba.Meq import meqds

import sys
import traceback

# testing branch
if __name__ == '__main__':
  mqs = meqserver.default_mqs(wait_init=10);
  #  mqs = meqserver.default_mqs(wait_init=5,spawn=None); # if already running


  print 'meqserver state:',mqs.state;

  (mod,ns,msg) = Compile.compile_file(mqs,'tdl_test.tdl');

  mod._test_forest(mqs,None);

  # sync=True makes sure all commands above have completed on the kernel side
  # before state is fetched
  state = mqs.getnodestate('solver',sync=True);
  req = state.request;

  res = mqs.execute('x',req,wait=True);

  print res;
    
