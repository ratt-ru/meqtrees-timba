# The CVS path is Timba/PyApps/test/tdl_tutorial.tdl.
# LASTEDIT: 2006.10.12

#
#% $Id$ 
#
#
# Copyright (C) 2002-2007
# The MeqTree Foundation & 
# ASTRON (Netherlands Foundation for Research in Astronomy)
# P.O.Box 2, 7990 AA Dwingeloo, The Netherlands
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>,
# or write to the Free Software Foundation, Inc., 
# 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

from Timba.TDL    import *
from os           import *
from math         import *  
from Timba.Meq    import meq
from Timba.Trees  import JEN_bookmarks	   # for bookmarks

Settings.forest_state.cache_policy = 100;
Settings.orphans_are_roots = True;    # If True, orphans always retained.
solver = 'solver';


def Book_Mark(Node=None, page='BookMark', record_browser=0):
  """ Function for easy bookmarking. bookmarks with the same name will
  go on the same page
  """
  JEN_bookmarks.create(Node, page=page,viewer='Result Plotter')
  if record_browser:
    JEN_bookmarks.create(Node, page=page,viewer='Record Browser')
    pass
  pass


def create_func(ns, name='Sin', function='Sin', coeff=1):
  #create_func(ns, solver, 'Sin', 10)
  x    = ns["x"](coeff) << Meq.Parm([0,coeff])  
  funk = ns[name]       << Meq[function](x)
  Book_Mark(x,    function)
  Book_Mark(funk, function)
  return funk


def _define_forest (ns):
  """ automatically called to define the forest. 'ns' is a NodeScope object""";
  system('clear;')

  # Create the variable
  guess  = 0             # initial guess -> result of solver depends on this
  x      = ns.x << Meq.Parm(guess, node_groups='Parm')


  # Create the condeq with the 2 things that will be matched
  condeq = ns["Condeq"] << Meq.Condeq (
    12,                  # tries to solve: 12 = x^2+4x   (so x=-6, x=2)
    Meq.Add(
    Meq.Pow(x,2),
    Meq.Multiply(4,x))
    )

  # Create the solver
  solver_node = ns[solver]   << Meq.Solver (
    num_iter     = 10,    # num iters solver will match children of condeq 
    debug_level  = 10,
    solvable     = "x",             # the variable to solve for
    children     = condeq
    )
  
  # Bookmarks
  Book_Mark(condeq,      "Solver")  # result should go to zero
  Book_Mark(solver_node, "Solver")  # result should go to zero
  Book_Mark(x,           "Solver")  # gives you (an) answer
  pass


def _test_forest (mqs,parent):      # run tests on the forest
  """ If 'test' option is set to true, this method is automatically called
  """
  cells_1D  = meq.cells  (meq.domain(-1,1,0,2*pi),num_time=100, num_freq=1)
  cells_2D  = meq.cells  (meq.domain(-1,1,0,2*pi),num_time=100, num_freq=10)
  request   = meq.request(cells_1D,eval_mode=1);
  exec_001  = mqs.meq('Node.Execute',record(name=solver,request=request));
  exec_002  = mqs.meq('Save.Forest' ,record(file_name='tmp.meqforest'))
  print exec_001
  pass


def _tdl_job__somename (mqs,parent):
  print "_tdl_job__somename executed"
  pass


if __name__ == '__main__':  # Callable from shell
  Timba.TDL._dbg.set_verbose(5);
  ns = NodeScope();
  _define_forest(ns);       # define forest
  ns.Resolve();             # resolves nodes
  pass

