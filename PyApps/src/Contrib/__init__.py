import os
import os.path

def _tryWaterhole (path):
  global __path__;
  if os.path.isdir(path):
    __path__.insert(0,os.path.join(path,"contrib"));
    print "Using Waterhole at %s"%path;
    print "You may set the MEQTREES_WATERHOLE_PATH environment variable to override this."
    return True;
  return False;

def _setWaterholePath ():
  # check for explicit WATERHOLE_PATH first
  varname = 'MEQTREES_WATERHOLE_PATH';
  path = os.environ.get(varname,None);
  if path:
    if not _tryWaterhole(path):
      print "Warning: your %s environment variable is set to"%varname;
      print "%s, but this is not a valid directory."%path;
      print "The Waterhole will not be available."
    return;
  # else look in standard places
  standard_paths = [ "~/Waterhole",
                "/usr/local/MeqTrees/Waterhole","/usr/local/lib/MeqTrees/Waterhole",
                "/usr/local/Waterhole","/usr/local/lib/Waterhole",
                "/usr/MeqTrees/Waterhole","/usr/lib/MeqTrees/Waterhole",
                "/usr/Waterhole","/usr/lib/Waterhole" ];
  for path in standard_paths:
    path = os.path.expanduser(path);
    if _tryWaterhole(path):
      return;
  # none found
  print "Warning: no Waterhole found. The Waterhole will not be available."
  print "You may check out a Waterhole using the following command:"
  print "  $ cd ~; svn co svn://lofar9.astron.nl/var/svn/repos/trunk/Waterhole"
  print "If you have a Waterhole in a non-standard location, please set the"
  print "%s environment variable to point to it."%varname;

_setWaterholePath();