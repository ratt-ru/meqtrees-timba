pragma include once

# debug_methods.g
#   defines a set of standard debug methods inside a Glish object
#
#   Example of use:
#
#   const classname := function (parameters,verbose=1)
#   {
#     self := [=];
#     public := [=];
#     define_debug_methods(self,public,verbose)
#
const define_debug_methods := function (ref self,ref public,initverbose=1)
{
  self.verbose := initverbose;
  
  # dprint(level,...)
  #   prints if level is <= current verbosity level
  const public.dprint := function (level,...)
  {
    wider self;
    if( level <= self.verbose )
      print spaste('[== ',self.appid,' ==] ',...);
    return T;
  }
  # dprintf(level,format,...)
  #   printfs if level is <= current verbosity level
  const public.dprintf := function (level,format,...)
  {
    wider self;
    if( level <= self.verbose )
      print spaste('[== ',self.appid,' ==] ',sprintf(format,...));
    return T;
  }
  # setverbose(level)
  #   Sets the verbosity level 
  const public.setverbose := function (level)
  {
    wider self;
    return self.verbose := level;
  }
  # private versions od dprint/dprintf also defined for convenience
  const self.dprint := ref public.dprint;
  const self.dprintf := ref public.dprintf;
  
  return T;
}
