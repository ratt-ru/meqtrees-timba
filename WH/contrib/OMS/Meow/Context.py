
array = None;
observation = None;

def set (array=None,observation=None):
  """Sets the global Meow context."""
  for arg in 'array','observation':
    val = locals().get(arg,None);
    if val is not None:
      globals()[arg] = val;



  
