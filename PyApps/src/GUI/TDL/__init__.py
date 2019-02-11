from PyQt4.Qt import *
from Kittens.widgets import PYSIGNAL

from Timba.GUI import browsers
from Timba.GUI.pixmaps import pixmaps
from Timba import Grid

try:
  from .TDLEditor_qscintilla import TDLEditor
except:
  from .TDLEditor_standard import TDLEditor
  
from .TDLErrorFloat import TDLErrorFloat
from .TDLOptionsDialog import TDLOptionsDialog



class TDLFileDataItem (Grid.DataItem):
  """represents a GridDataItem for a TDL script""";
  def __init__ (self,pathname):
    # read the file (exception propagated outwards on error)
    ff = open(pathname);
    text = ff.read();
    ff.close();
    basename = os.path.basename(pathname);
    # create the item
    udi = '/tdlfile/'+pathname;
    name = basename;
    caption = '<b>'+basename+'</b>';
    desc = 'TDL file '+pathname;
    Grid.DataItem.__init__(self,udi,name=name,caption=caption,desc=desc,data=text,viewer=TDLBrowser,refresh=None);
    # add extra pathname attribute for tdl objects
    self.tdl_pathname = pathname;


class TDLBrowser(browsers.GriddedPlugin):
  _icon = pixmaps.text_tdl;
  viewer_name = "TDL Browser";

  def __init__(self,gw,dataitem,cellspec={},default_open=None,**opts):
    browsers.GriddedPlugin.__init__(self,gw,dataitem,cellspec=cellspec);
    self._wedit = TDLEditor(self.wparent());
    self.set_widgets(self.wtop(),dataitem.caption,icon=self.icon());
    if dataitem.data is not None:
      self.set_data(dataitem);
    QObject.connect(self.wtop(),PYSIGNAL("fontChanged()"),self.wtop().adjust_editor_font);

  def wtop (self):
    return self._wedit;
  def editor (self):
    return self._wedit;

  def set_data (self,dataitem,default_open=None,**opts):
    _dprint(3,'set_data ',dataitem.udi);
    pathname = getattr(dataitem,'tdl_pathname',None);
    self._wedit.load_file(pathname,text=dataitem.data);

  def highlight (self,color=True):
    browsers.GriddedPlugin.highlight(self,color);
    self._wedit.has_focus(bool(color));

Grid.Services.registerViewer(str,TDLBrowser,priority=10,check_udi=lambda x:x.endswith('_tdl'));

