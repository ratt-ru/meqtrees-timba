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

from Timba import utils
from Timba.dmi import *
from Timba.TDL import TDLimpl
from Timba.TDL.TDLimpl import *
from Timba.TDL.MeqClasses import Meq
from Timba.TDL import Settings
from Timba.TDL.TDLOptions import TDLOption,TDLMenu,TDLJob,TDLOptionSeparator
from Timba.TDL.TDLOptions import TDLCompileOption,TDLRuntimeOption,TDLRuntimeJob
from Timba.TDL.TDLOptions import TDLCompileOptionSeparator,TDLRuntimeOptionSeparator
from Timba.TDL.TDLOptions import TDLCompileOptions,TDLRuntimeOptions
from Timba.TDL.TDLOptions import TDLCompileMenu,TDLRuntimeMenu
from Timba.TDL.TDLOptions import TDLFileSelect,TDLDirSelect,TDLStealOptions

_dbg = TDLimpl._dbg;
_dprint = _dbg.dprint;
_dprintf = _dbg.dprintf;

# test code follows
#
if __name__ == '__main__':
  # stations list
  STATIONS = list(range(1,15));
  # 3 sources
  SOURCES = ('a','b','c');

  #--- these are generated automatically from the station list
  # list of ifrs as station pairs: each entry is two indices, (s1,s2)
  IFRS   = [ (s1,s2) for s1 in STATIONS for s2 in STATIONS if s1<s2 ];
  # list of ifr strings of the form "s1-s2"
  QIFRS  = [ '-'.join(map(str,ifr)) for ifr in IFRS ];
  # combined list: each entry is ("s1-s2",s1,s2)
  QQIFRS = [ ('-'.join(map(str,ifr)),) + ifr for ifr in IFRS ];

  # global node scope & repository
  ns = NodeScope();
  # init some node groups
  SOLVERS = NodeGroup('solvers');

  #------- create nodes for instrumental model
  # some handy aliases
  ZERO = ns.zero() << Meq.Constant(value=0);
  UNITY = ns.unity() << Meq.Constant(value=1);

  PHASE_CENTER_RA  = ns.ra0() << Meq.Parm();
  PHASE_CENTER_DEC = ns.dec0() << Meq.Parm();

  STATION_UWV = {};
  STATION_POS = {};

  ARRAY_POS = ns.xyz0() << Meq.Composer(
    ns.x0() << Meq.Parm(0),
    ns.y0() << Meq.Parm(0),
    ns.z0() << Meq.Parm(0) );

  # create station-related nodes and branches
  for s in STATIONS:
    STATION_POS[s] = ns.xyz(s) << Meq.Composer(
      ns.x(s) << Meq.Parm(0),
      ns.y(s) << Meq.Parm(0),
      ns.z(s) << Meq.Parm(0) );
    STATION_UWV[s] = ns.stuwv(s) << Meq.UWV(children={
      'xyz': STATION_POS[s],
      'xyz0': ARRAY_POS,
      'ra': PHASE_CENTER_RA,
      'dec': PHASE_CENTER_DEC
    });
    # create per-source station gains
    for (q,src) in enumerate(SOURCES):
      ns.G(s,q=q) << Meq.Composer(
        ns.Gxx(s,q=q) << Meq.Polar(Meq.Parm(),Meq.Parm()), ZERO,
        ZERO, ns.Gyy(s,q=q) << Meq.Polar(Meq.Parm(),Meq.Parm()),
      dims=[2,2]);
    # alternative: single gain with no direction dependence
    # ns.G(s) << Meq.Composer(
    #    ns.Gxx(s) << Meq.Polar(Meq.Parm(),Meq.Parm()), ZERO,
    #    ZERO, ns.Gyy(s) << Meq.Polar(Meq.Parm(),Meq.Parm()),
    #  dims=[2,2]);

  # this function returns a per-station gain node, given a set of qualifiers
  def STATION_GAIN (s=s,q=q,**qual):
    # **qual swallows any remaining qualifiers
    return ns.G(s,q=q);
    # note alternative for no direction dependence:
    # def STATION_GAIN (s=s,**qual):
    #   return ns.G(s);

  #------- end of instrumental model

  #------- create model for unpolarized point source
  # References instrumental model: STATION_GAIN(s,**qual), STATION_UWV[s].
  # Returns unqualified predict node, should be qualified with ifr string.
  def makeUnpolarizedPointSource (ns,**qual):
    ns.lmn() << Meq.LMN(children={
        'ra':   ns.ra() << Meq.Parm(),
        'dec':  ns.dec() << Meq.Parm(),
        'ra0':  PHASE_CENTER_RA,
        'dec0': PHASE_CENTER_DEC
    });
    ns.stokes_i() << Meq.Parm();
    # create per-station term subtrees
    for s in STATIONS:
      ns.sdft(s) << Meq.MatrixMultiply(
        STATION_GAIN(s,**qual),
        Meq.StatPSDFT(ns.lmn(),STATION_UWV[s])
      );
    # create per-baseline predicters
    for (q,s1,s2) in QQIFRS:
      ns.predict(q) << Meq.Multiply(
          ns.stokes_i(),
          ns.dft(q) << Meq.DFT(ns.sdft(s1),ns.sdft(s2)),
      );
    return ns.predict;

  #------- create peeling unit
  # inputs: an unqualified input node, will be qualified with ifr string.
  # predicters: list of unqualified predict nodes, will be qualified with ifr string.
  # Returns unqualified output node, should be qualified with ifr string.
  def peelUnit (inputs,predicters,ns):
    for q in QIFRS:
      # create condeq branch
      ns.condeq(q) << Meq.Condeq(
        ns.measured(q) << Meq.PhaseShift(children=inputs(q)),
        ns.predicted(q) << Meq.Add(*[prd(q) for prd in predicters])
      );
      # create subtract branch
      ns.subtract(q) << Meq.Subtract(ns.measured(q),ns.predicted(q));
    # creates solver and sequencers
    ns.solver() << Meq.Solver(*[ns.condeq(q) for q in QIFRS]);
    for q in QIFRS:
      ns.reqseq(q) << Meq.ReqSeq(ns.solver(),ns.subtract(q));
    # returns root nodes of unit
    return ns.reqseq;

  # create source predictors, each in its own subscope
  predicter = {};
  for (q,src) in enumerate(SOURCES):
    predicter[q] = makeUnpolarizedPointSource(ns.Subscope('predict',src),q=q);

  # create spigots
  for q in QIFRS:
    ns.spigot(q) << Meq.Spigot();

  # chain peel units, by connecting outputs to inputs. First input
  # is spigot.
  inputs = ns.spigot;
  for (q,src) in enumerate(SOURCES):
    ns_pu = ns.Subscope('peelunit',q);
    inputs = peelUnit(inputs,list(predicter.values()),ns=ns_pu);
    SOLVERS << ns_pu.solver();

  # create sinks, connect them to output of last peel unit
  for q in QIFRS:
    ns.ROOT << ns.sink(q) << Meq.Sink(inputs(q));

  # create data collectors (this simply shows off the use of arbitrary node
  # groupings)
  ns.ROOT << ns.solver_collect() << Meq.DataCollect(*list(SOLVERS.values()));

  # deliberately create an orphan branch. This checks orphan collection.
  # this whole branch should go away, and so should the UNITY node, which
  # is not used anywhere
  ns.orphan() << Meq.Add(Meq.Const(value=0),UNITY,Meq.Add(UNITY,ZERO));

  # resolve all nodes
  ns.Resolve();
