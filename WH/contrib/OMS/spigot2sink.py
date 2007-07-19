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
from Timba.Meq import meq


def _define_forest(ns):
    ms_name = "D1.MS"
    station_list        = range(3)
    ifr_list = [(ant1, ant2) for ant1 in station_list for ant2 in station_list if ant1 < ant2]

    ## we create a VisDataMux explicitly, though this is not really necessary
    # ns.vdm << Meq.VisDataMux();
    for ant1,ant2 in ifr_list:
      ns.spigot(ant1,ant2) << Meq.Spigot(station_1_index=ant1,station_2_index=ant2);
      ns.sink(ant1,ant2) << Meq.Sink(ns.spigot(ant1,ant2),station_1_index=ant1,station_2_index=ant2);


def create_inputrec(msname, tile_size=10):
    inputrec=record()
    inputrec.ms_name          = msname
    inputrec.data_column_name = 'DATA'
    inputrec.tile_size        = tile_size
    inputrec.python_init = 'read_msvis_header.py'
    return inputrec

def create_outputrec(output_column='CORRECTED_DATA'):
    outputrec=record()
    outputrec.write_flags=False
    outputrec.predict_column=output_column
    return outputrec

def _test_forest (mqs,parent):
    msname          = 'D1.MS'
    inputrec        = create_inputrec(msname, tile_size=10)
    outputrec       = create_outputrec()
    
    req = meq.request();
    req.input = record(ms=inputrec);
#    req.input.python_init = 'Timba/read_msvis_header.py';
    req.output = record(ms=outputrec);

    mqs.publish('sink:1:2');
    mqs.execute('VisDataMux',req,wait=False);


Settings.forest_state.cache_policy = 100 #100
Settings.orphans_are_roots = True

if __name__ == '__main__':
    Timba.TDL._dbg.set_verbose(5);
    ns = NodeScope();
    _define_forest(ns);
    ns.Resolve();
    pass
