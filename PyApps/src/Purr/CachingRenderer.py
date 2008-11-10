import Purr.Render

import os.path
import traceback

from Purr.Render import DefaultRenderer,dprint,dprintf


class CachingRenderer (DefaultRenderer):
  """This is a base class for "expensive" renderers.
  It maintains a cache of rendered HTML code, and only invokes the renderer if the cache is out of date.""";
  
  def _cacheFileExtension (self,cachetype,relpath):
    return ("-cache-%s-rel-%s.html"%(cachetype,bool(relpath))).lower();
  
  def __init__ (self,dp,refresh=False):
    DefaultRenderer.__init__(self,dp,refresh=refresh);
    self.rendercache = {};
    self._regenerated = False;
    
  def regenerate (self):
    """This is meant to be implemented by subclasses. Called if any cache element is out of date,
    to do the actual heavy work.""";
    pass;
  
  def checkCache (self,cachetype,relpath):
    """checks cache for rendered html code.
    'cachetype' can be any string (usually the name of a method, e.g. "Thumbnail", or "InTable")
    relpath is the relative path, here treated as boolean.
    If cache is up-to-date, returns tuple of cachekey,html (NB: cachekey is path to cache file)
    If cache is out of date, calls regenerate() if not already done so, and returns tuple of cachekey,None.
    """;
    cache_ext = self._cacheFileExtension(cachetype,relpath);
    filename,path = self.subproductPath(cache_ext);
    cachekey = path;
    # check already read cache, unless we're in refresh mode
    if not self.refresh:
      content = self.rendercache.get(path,None);
      if content is not None:
        return content;
      # if cache file is up-to-date, attempt to read content
      if self.subproductUpToDate(path):
        dprintf(3,"render cache %s is up-to-date, reading in\n",path);
        try:
          content = file(path).read();
        except:
          print "Error reading render cache file",path,", will regenerate";
          traceback.print_exc();
      else:
        dprintf(3,"render cache %s is out of date, will regenerate\n",path);
      # read content? cache and return
      if content is not None:
        self.rendercache[path] = content;
        return path,content;
    # else regenerate
    if not self._regenerated:
      self.regenerate();
      self._regenerated = True;
    # and return path,None to indicate no cache
    return path,None;
    
  def writeCache (self,cachekey,content):
    """stores content in cache. 'cachekey' must be the same key as returned from checkCache().
    Returns the content."""
    self.rendercache[cachekey] = content;
    try:
      file(cachekey,'w').write(content);
    except:
      print "Error writing cache file",cachekey,", will regenerate next time";
      traceback.print_exc();
    return content;
