
array = None;
observation = None;

def set (array=None,observation=None):
  """Sets the global Meow context."""
  for arg in 'array','observation':
    val = locals().get(arg,None);
    if val is not None:
      globals()[arg] = val;
  
def get_array (array1):
  """Resolves 'array1' argument: returns array1 if it is non-false, else
  returns the global array, or throws an error if none is set."""
  arr = array1 or array;
  if not arr:
    raise ValueError,"'array' must be set in global Meow.Context, or supplied explicitly";
  return arr;
  
def get_observation (obs1):
  """Resolves 'obs1' argument: returns obs1 if it is non-false, else
  returns the global observation, or throws an error if none is set."""
  obs = obs1 or observation;
  if not obs:
    raise ValueError,"'observation' must be set in global Meow.Context, or supplied explicitly";
  return obs;
  
def get_dir0 (dir0):
  """Resolves 'dir0' argument: returns dir0 if it is non-false, else
  returns the global observation's phase center, or throws an error 
  if none is set."""
  if dir0:
    return dir0;
  if not observation:
    raise ValueError,"'observation' must be set in global Meow.Context, or a 'dir0' supplied explicitly";
  return observation.phase_centre;

vdm = None;


  
