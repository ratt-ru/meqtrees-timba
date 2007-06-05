from Timba.TDL import *

Settings.forest_state.cache_policy = 100;

# fdfdf/ddd ='';

## uncomment to get an import error 
# err = err;

def make_python_error ():
  ee = err;
  err = 1;


def CALL (what,*args,**kwargs):
  """simply calls the specified function. We use it to generate a stack for error
  reporting""";
  return what(*args,**kwargs);