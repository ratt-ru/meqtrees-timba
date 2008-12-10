
import sys
import os
import time
import os.path
import re
import sets
import fnmatch
import imp
import traceback

import Purr

from Purr import Config
import Timba.utils

_verbosity = Timba.utils.verbosity(name="render");
dprint = _verbosity.dprint;
dprintf = _verbosity.dprintf;

def renderDefault (dp,relpath):
  """Fall-back rendering method (if all else fails), renders DP as a link""";
  return """<A HREF="%s%s">%s</A>"""%(relpath,dp.filename,dp.filename);

class DefaultRenderer (object):
  # this gives a short ID for the class (used in GUIs and such)
  renderer_id = "link";
  
  # this gives a documentation string. You can use rich text here
  renderer_doc = """<P>The "link" renderer shows data products as simple HTML links.<P>""";
  
  # this is set (by addRenderer() below) to the file modification time of the module containing
  # the renderer. Decisions on whether to re-render costly products are made based on this mtime.
  module_mtime = 0;
  
  """This is a base class for data product rendering plugins.""";
  def canRender (filename):
    """The canRender() method of a renderer class is called for every new data product.
    It determines whether the DP can be rendered by this class. 
    It should return False if the DP cannot be rendered, or else a number giving the
    priority of the renderer. Lower-priority renderers will be offered to the user
    as defaults."""
    return 1000000;
  canRender = staticmethod(canRender);
  
  def __init__ (self,dp,refresh=False):
    """A renderer is initialized with a LogEntry.DataProduct object.
    If a renderer has been initialized, it is guaranteed to be used, so any "heavy" activity
    such as making of thumbnails, etc. can already be undertaken here.
    If refresh=True, any document caches should be ignored and everything should be rerendered from scratch.
    """
    self.dp = dp;
    self.refresh = refresh;
    # setup some convenient attributes
    # filename: base filename of DP (w/o path)
    self.filename  = dp.filename;
    # dirname: directory of DP
    self.dirname   = os.path.dirname(dp.fullpath);
    # base name of DP, without extension
    self.basename  = os.path.splitext(dp.filename)[0];
    # base path to DP, without extension
    self.basepath  = os.path.splitext(dp.fullpath)[0];
    # modification time of DP
    self.file_mtime = os.path.getmtime(dp.fullpath);
    #
    
  def subproductPath (self,ext):
    """Makes a subproduct filename by appending 'ext' to the subproduct directory.
    Returns a (filename,fullpath) tuple.""";
    ext = ext.lstrip("-");
    basename = os.path.join(os.path.basename(self.dp.subproduct_dir()),ext);
    fullpath = os.path.join(self.dp.subproduct_dir(),ext);
    return basename,fullpath;
  
  def subproductUpToDate (self,fpath):
    """Returns True if the path is up-to-date w.r.t. our data product: i.e. exists, and is no older 
    than the DP itself, or the module itself (the last check ensures that subproducts are remade
    if the rendering code changes.)""";
    if self.refresh:
      return False;
    if not os.path.exists(self.dp.subproduct_dir()):
      os.mkdir(self.dp.subproduct_dir());
## This caused many re-rendering whenever a plugin got recompiled, so I disabled it.
## Need to add a control for re-rendering.
##    if os.path.exists(fpath) and os.path.getmtime(fpath) >= max(self.file_mtime,self.module_mtime):
    if os.path.exists(fpath) and os.path.getmtime(fpath) >= self.file_mtime:
      dprintf(3,"subproduct %s is up-to-date, no need to remake\n",fpath);
      return True;
    else:
      dprintf(3,"subproduct %s is out of date, need to remake\n",fpath);
      dprintf(4,"subproduct timestamp %s, file %s, module %s\n",
        time.strftime("%x %X",time.localtime((os.path.exists(fpath) or 0) and os.path.getmtime(fpath))),
        time.strftime("%x %X",time.localtime(self.file_mtime)),
        time.strftime("%x %X",time.localtime(self.module_mtime)));
      return False;
  
  def subproduct (self,ext):
    """Makes a subproduct filename by calling subproductPath(), then calls
    subproductUpToDate() to determine if it is up-to-date.
    Returns tuple of basename,path,uptodate
    """;
    fname,fpath = self.subproductPath(ext);
    return fname,fpath,self.subproductUpToDate(fpath);
  
  # This is a dict of renderer-specific options. 
  options = {};
  # Its life is a bit interesting because:
  #   1. If subclass X adds new options (via addOption() below), this dict is copied
  #     and reassigned to X.options, so X has its own class-specific copy
  #   2. If subclass Y (subclass of X) add yet more options, the dict is copied again.
  #     so now both X and Y have class-specific copies.
  #   3. If y is an instance of Y, and y.setOption() is called, the dict is copied again
  #     and reassigned to y.options, so y has its own instance-specific copy. 
  # _options_owner is set to the owner of the current dict. It is initially DefaultRenderer,
  # then in case (1) it is X, in (2) it is Y, and in (3) it is y itself.
  _options_owner = None;
  
  def addOption (classobj,name,default,dtype=str,doc=None):
    """Adds a renderer option named 'name', with the given default value.
    'dtype' must be a callable to convert a string to an option.
    'doc' is a doc string.
    Options will be initialized from config file here.
    """;
    # make a class-specific copy of the current option set
    if classobj._options_owner is not classobj:
      classobj.options = dict(DefaultRenderer.options);
      classobj._options_owner = classobj;
    # overrid default value from config file
    if dtype is bool:
      value = Config.getbool(name,default);
    else:
      value = dtype(Config.get(name,default));
    # insert into dict
    classobj.options[name] = (value,default,dtype,doc);
  addOption = classmethod(addOption);
  
  def getOption(self,name):
    """gets the current setting for the option.""";
    return self.options[name][0];
  
  def setOption(self,name,value):
    # make an instance-specific copy of the current option set
    if self._options_owner is not self:
      self.options = dict(self.options);
      self._options_owner = self;
    return self.options[name][0];

  # provide default implementations of rendering methods

  def renderLink (self,relpath=""):
    """renderInline() is called to render a link to the DP inline (e.g. embedded in text).
    relpath specifies a relative path to the DP location (relative to the HTML page being
    rendered), so should be added to all links. It is guaranteed to end with an "/" if not
    empty.
    Return value should be aa valid HTML string.""";
    return renderDefault(self.dp,relpath);
  
  def renderThumbnail (self,relpath=""):
    """renderThumbnail() is called to render a thumbnail of the DP (e.g. in Data Product tables).
    relpath is as for renderLink() above.
    Return value should be aa valid HTML string, or None or "" if thumbnails are not available.""";
    return "";
  
  def renderLinkComment (self,relpath=""):
    """renderLinkComment() is called to render the DP in link:comment form, as a separate paragraph.
    relpath is as for renderLink() above.
    Return value should be a valid HTML string.""";
    items = [];
    link = self.renderLink(relpath) or "";
    if link:
      items.append(link);
    comment = self.dp.comment or "";
    if comment:
      comment = comment.replace("<","&lt;").replace(">","&gt;");
      items.append(comment);
    if items:
      return "<P>"+": ".join((items))+"</P>";
    else:
      return "";
  
  def renderVerbose (self,relpath=""):
    """renderVerbose() is called to render a verbose version of the DP (e.g. as a separate
    paragraph).
    relpath is as for renderLink() above.
    Return value should be a valid HTML string.
    Default version renders as link:comment""";
    return self.renderThumbnail(relpath) or self.renderLinkComment(relpath);
  
  def renderInTable (self,relpath=""):
    """renderInTable() is called to render a data product in a table
    relpath is as for renderLink() above.
    Return value should be empty, or a valid HTML string (usually delimited by <TR></TR> tags).
    Default implementation renders thumbnail,comment and link in three table cells.""";
    thumb   = self.renderThumbnail(relpath) or "";
    comment = self.renderLinkComment(relpath) or "";
    if thumb:
      return "\n".join(
        [ "    <TR>" ] +
        [ "      <TD>%s</TD>"%element for element in thumb,comment ] +
        [ "    </TR>\n" ]);
    else:
      return """
        <TR><TD COLSPAN=2>%s</TD></TR>\n"""%comment;
  
available_renderers = {};
youngest_renderer = 0;

def addRenderer (renderer_class,module_name,module_file):
  global available_renderers;
  rdrid = renderer_class.renderer_id;
  rdrclass,mod = available_renderers.get(rdrid,(None,None));
  if rdrclass:
    raise RuntimeError,"renderer '%s' already registered by module '%s'"%(rdrid,mod);
  renderer_class.module_mtime = mtime = os.path.getmtime(module_file);
  global youngest_renderer;
  youngest_renderer = max(mtime,youngest_renderer);
  available_renderers[rdrid] = renderer_class,module_name;
  dprintf(1,"registered renderer '%s', mtime %s\n",renderer_class.__name__,
            time.strftime("%x %X",time.localtime(renderer_class.module_mtime)));
  
def numRenderers ():
  global available_renderers;
  return len(available_renderers);
  
def getRenderers (filename):
  """For a given DP, returns a list of renderer ids giving
  the renderers that support the source file type""";
  global available_renderers;
  renderers = [];
  for rdrid,(renderer,module) in available_renderers.iteritems():
    try:
      priority = renderer.canRender(filename);
    except:
      print """Error in renderer: %s.canRender("%s"):"""%(rdrid,filename);
      traceback.print_exc();
      priority = None;
    if priority:
      renderers.append((priority,rdrid));
  # sort by priority
  renderers.sort(lambda a,b:cmp(a[0],b[0]));
  # return list of IDs. Note that "none" should always be available and working
  return [ a[1] for a in renderers ] or ["link"];
  
def makeRenderer (rdrid,dp,refresh=False):
  """Creates a renderer object with the given rdrid, and attaches it the given DP.
  Failing that, creates a default renderer.""";
  try:
    return available_renderers[rdrid][0](dp,refresh=refresh);
  except:
    print """Error creating renderer %s for %s:"""%(rdrid,dp.fullpath);
    traceback.print_exc();
    return DefaultRenderer(dp);
  
def _callRender (renderer,method,relpath,fallback="%s"):
  try:
    return getattr(renderer,method)(relpath=relpath);
  except:
    dp = getattr(renderer,'dp',None);
    print """Error calling %s.%s for %s"""%(renderer,method,dp and dp.fullpath);
    traceback.print_exc();
    # if a fallback is specified (and does not contain %s), return that
    if fallback.find("%s") < 0:
      return fallback;
    # else render default
    if dp:
      return fallback%renderDefault(dp,relpath);
    else:
      return "&lt;rendering error&gt;"
  
def renderLink (renderer,relpath=""):
  """calls renderLink() on the specified renderer. On error, falls back to renderDefault()""";
  return _callRender(renderer,"renderLink",relpath);

def renderThumbnail (renderer,relpath=""):
  """calls renderThumbnail() on the specified renderer. On error, returns empty string""";
  return _callRender(renderer,"renderThumbnail",relpath,fallback="");

def renderVerbose (renderer,relpath=""):
  """calls renderVerbose() on the specified renderer. On error, falls back to renderDefault()""";
  return _callRender(renderer,"renderVerbose",relpath,fallback="<P>%s</P>");

def renderInTable (renderer,relpath=""):
  """calls renderLink() on the specified renderer. On error, falls back to renderDefault()""";
  return _callRender(renderer,"renderInTable",relpath,fallback="<TR><TD>%s</TD></TR>");


addRenderer(DefaultRenderer,"built-in",__file__);

# we don't really need this, but it's better to import it here rather than from a plugin, since
# then we detect errors sooner
import CachingRenderer