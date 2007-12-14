from Timba.TDL import *
import Meow
from Timba.Contrib.MXM.MimModule import MIM_model
from Timba.Contrib.MXM.MimModule.xyzComponent import xyzComponent
from Timba.Contrib.MXM.MIM.GPS_MIM import read_gps
#First get sources and stations
from Timba.Contrib.MXM.MimModule import Stations;
stations = Stations.Stations();
# station/sat name lists


def _define_forest(ns):
    #make pynodes, xyzcomponent for sources
    sources = stations.Sat_list();
    stats = stations.Stat_list();
    sats=[];
    for sat in sources:
        tecnode = ns.pynodepos(sat) << Meq.PyNode(class_name="PyNodeSatPos",module_name='MyPyNodes',sat_nr=sat)
        sats.append(xyzComponent(ns,str(sat),tecnode));
    rot_matrix = read_gps.create_ref_stat_pos(ns,stats);
      
    return None;
