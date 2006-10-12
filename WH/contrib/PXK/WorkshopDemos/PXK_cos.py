# The CVS path is Timba/PyApps/test/tdl_tutorial.tdl.
from Timba.TDL         	import *
from os              	import *
from math         	import *  
from Timba.Meq 		import meq
from Timba.Trees        import JEN_bookmarks	   # for bookmarks
from Timba.Contrib.JEN	import MG_JEN_forest_state
from Timba.Contrib.JEN  import MG_JEN_exec


Settings.forest_state.cache_policy = 100;
Settings.orphans_are_roots = True; 	   # If true, orphans always retained.
solver = "solver"


def Book_Mark(Node=None, page='BookMark', record_browser=0):
  """ Function for easy bookmarking. bookmarks with the same name will
  go on the same page
  """
  JEN_bookmarks.create(Node, page=page,viewer='Result Plotter')
  if record_browser:
    JEN_bookmarks.create(Node, page=page,viewer='Record Browser')
    pass
  pass


def _define_forest (ns):
  """ automatically called to define the forest. 'ns' is a NodeScope object
  """
  #os.system('clear;')
  function = 'Cos';
  x        = ns["x"]     << Meq.Parm(meq.polc([0,1]) );
  cos      = ns[solver]  << Meq.Cos(children=x);
  Book_Mark(x,   "Cos(x)")
  Book_Mark(cos, "Cos(x)")
  pass

  
def _test_forest (mqs,parent):   # run tests on the forest
  """ If 'test' option is set to true, this method is automatically called
  """
  domain	= meq.domain (-1,1,0,2*pi)
  cells_1D	= meq.cells  (domain, num_time=100, num_freq=1);
  cells_2D	= meq.cells  (domain, num_time=100, num_freq=10);
  request	= meq.request(cells_1D, eval_mode=1);
  
  mqs.meq('Node.Execute',record(name=solver,request=request));
  pass
