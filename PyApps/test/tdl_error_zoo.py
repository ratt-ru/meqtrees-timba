from Timba.TDL import *

### tdl_error_zoo.py
### This script is deliberately full of errors. We use it to test TDL error reporting.
###

## Uncomment this to test syntax error reporting.
#  import tdl_error2
## (Unfortunately, it is impossible to make this into a compile-time TDL option, since
## errors that arise at the import stage prevent compile-time options from showing up!)



# Note that errors are caught at different stages of TDL processing, and some of them 
# are not recoverable. This makes it impossible to test for all of them at once. Therefore,
# we provide several different "types" or error tests, and select one with a compile-time
# option below:
#  * Python errors are caught immediately, and typically produce a single error message
#  * All sorts of TDL errors (node definitions, mostly) are accumulated and reported
#    all at once after the script is run.
#  * Some things, such as uninitialized nodes, are checked for at the last stage ("resolve").


# this list will contain all the possible testing functions
error_types = [];

import tdl_error1
from tdl_error1 import CALL


def python_errors (ns):
  """generates a python error""";
  tdl_error1.make_python_error();

error_types.append(python_errors);


def tdl_node_errors (ns,nested=False):
  ns.x << 0;
  ns.y << 0;
  
  # errors raised in NodeDef
  # children specified by both args and keyword
  ns.y1 << Meq.Add(1,2,3,4,children=[ns.a,ns.d]);
  y2 = ns.y2;
  ns.y1 << Meq.Add(1,2,3,4,children=[ns.a,ns.d]);
  # children specified by name that doesn't exist
  ns.y1 << Meq.Add("x","x1");
  # children of an illegal type
  ns.y1 << Meq.Add(list());
  # tags illegal
  ns.y1 << Meq.Add(tags=123);
  
  # binding with an illegal argument
  ns.y1 << list();
  y2 = ns.y1(2);
  y2(4) << list();
  
  # redefining a node
  ns.x << Meq.Parm(0,tiling=record(time=1),node_groups='Parm');
  
  #...and some more elaborate ways to redefine a node
  x = ns.x;
  x1 = ns.x(1);
  x1 << 0;
  ns.x(2) << 0;
  ns['x:1'] << 1;
  x2 = ns.x(2);
  x2 << 1; 
  
  # ...also through nodescopes and subscopes
  ns1 = ns.Subscope('a');
  ns1.a << 0;
  ns['a::a'] << 1;
  ns2 = ns.QualScope(1,2);
  ns2.a << 0;
  ns.a(1,2) << 1;
  
  # now for some uninitialized nodes
  b = ns.b;
  ns.x3 << Meq.Add(b);
  
  # and finally, a nested call to check the stack functions
  if not nested:
    CALL(tdl_node_errors,ns,nested=True);
  
error_types.append(tdl_node_errors);


def _define_forest (ns,**kwargs):
  # call function selected by compile-time option below
  test_function(ns);






# This selects the kinds of errors that will be tested for. Since errors are caught at 
# different stages of TDL processing, we need several different functions to test all the stages.
# Refer to comments in the functions above for details
TDLCompileOption('test_function',"Test what kind of errors",error_types);





if __name__ == '__main__':
  Timba.TDL._dbg.set_verbose(5);
  ns = NodeScope();
  define_forest(ns);
  ns.Resolve();
