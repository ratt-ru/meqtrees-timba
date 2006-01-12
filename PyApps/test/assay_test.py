# pull this first to skip all GUI definitions and includes
from Timba.Apps import app_nogui
from Timba.Apps import assayer

import sys
import traceback

# testing branch
if __name__ == '__main__':

  ass = assayer.assayer("tdl_test");
  ass.compile("tdl_test.tdl");
  ass.watch_node('x','cache.result');
  stat = ass.run(watch="solver/cache.result",inspect=("x/cache.result","solver/cache.result"));
  if stat:
    print "ASSAY FAILED: ",stat;
  sys.exit(stat);
