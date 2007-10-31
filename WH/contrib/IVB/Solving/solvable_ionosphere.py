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

from Timba.TDL import *
import pierce_points
import Meow
from Meow import Context
from Meow import Jones,ParmGroup,Bookmarks
from Meow.Parameterization import resolve_parameter

lightspeed = 3.0E8 #(m/s)

class Iono (object):
  def __init__ (self):
    self.options = [];

  def runtime_options (self):
    return self.options;

# sources moet meegegeven worden, want pierce-points zijn functie van source EN station
# sources heeft geen default value en is niet gedefinieerd in de Meow Context
# heeft Meow een Context.sources oid?
  def compute_jones (self,nodes,sources,stations=None,label='',**kw):
    stations = stations or Context.array.stations();
    #nodes is een nodestub en geen nodescope, de nodescope moet ik hier uit de nodestub halen
    ns = nodes.Subscope();
    # Define four parameters to solve for. Can we make this an arbitrary number depending
    # on the MIM-order? Eg FOR i = 0 to mimorder DO parm(i)=Meow.Parm(0) ?
    mim_0 = Meow.Parm(0); # dit is in feite TEC0
    mim_x = Meow.Parm(0);
    mim_y = Meow.Parm(0);
    mim_xy = Meow.Parm(0);

    # Set the tagname 
    tags="mim"
    # hier worden de parameters geinitialiseerd en benoemd en ge'tag'd als solvable
    # nodename nodes.source:station:c LETOP: nodescope hier is nodes, niet ns
    # tags: tagname as set above
    m0 = resolve_parameter("mim_0",nodes('m0'),mim_0,tags=tags);
    mx = resolve_parameter("mim_x",nodes('mx'),mim_x,tags=tags);
    my = resolve_parameter("mim_y",nodes('my'),mim_y,tags=tags);
    mxy = resolve_parameter("mim_xy",nodes('mxy'),mim_xy,tags=tags);

    # maak een set pierce points
    # op deze manier wordt piercings een nodescope die alles kent wat ik in
    # de routine aan nodes heb aangemaakt.
    piercings = pierce_points.compute_pierce_points(nodes,sources);

    for src in sources:
      for p in stations:
        # selecteer de x en de y waardes van de pierce_points (deze heb ik al gemaakt in de
        # pierce_points routine) en heten x_trans en y_trans in ENU
        x = piercings.x_trans(src,p)
        y = piercings.y_trans(src,p)
        # hier maak je de feitelijke Z-jones per source, station (NB: geen matrix in dit geval)
        # eerst de tec waardes maken uit de MIM (dit moet een aparte routine worden)
        ns.tec(src,p) << m0 + mx * x + my * y + mxy * x * y
        # dan de zeta-jones waardes in de node stoppen
        # nodes is de nodestub die we gebruiken voor meqmaker, hoeft dus geen ns.nodes te zijn 
        nodes(src,p) << Meq.Polar(1,-25*lightspeed*ns.tec(src,p)/Meq.Freq())
      
    # parmgroup maakt een groep van solvable parameters en benoemd de tabel
    # waarin ze worden weggeschreven
    # moet er een ParmGroup komen voor elke mim parameter, of gaan ze samen in 1 tabel?
    # zoeken naar solvable parameters, die hebben tags = "solvable speed"
    self.pg_mim = ParmGroup.ParmGroup(label,
                                      nodes.search(tags="solvable mim"),
                                      table_name="mim.mep",
                                      bookmark=4);

    # make solvejobs
    # maak de TDL solve-job, is dit niet dezelfde als in calico-ivb?
    ParmGroup.SolveJob("cal_"+label,"Calibrate ionosphere",self.pg_mim);

    return nodes;
