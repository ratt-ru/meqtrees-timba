# pull this first to skip all GUI definitions and includes
from Timba.Apps import app_nogui
from Timba.Apps import assayer

import sys
import traceback
import os

# testing branch
if __name__ == '__main__':
  os.system("killall -9 meqserver meqserver-opt");
  
  ass = assayer.assayer("tdl_test");

  ass.compile("tdl_test.tdl");

  ass.init_test("default");

  ass.watch('x/cache.request_id');
  ass.watch('x/cache.result');

  ass.run();

  ass.inspect("x/cache.result");
  ass.inspect("solver/cache.result");

  stat = ass.finish();

  if stat:
    print "ASSAY FAILED: ",stat;
  else:
    print "ASSAY SUCCEEDED";
    
  
