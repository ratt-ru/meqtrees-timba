# TDL_MSauxinfo.py
#
# Author: J.E.Noordam
#
# Short description:
#    An MSauxinfo object contains auxiliary info from an AIPS++ Measurement Set 
#
# History:
#    - 04 dec 2005: creation
#    - 05 jan 2006: added dcoll v vs w
#    - 11 jan 2006: used in MG_JEN_Joneset::KJones()
#
# Full description:
#   The MS is read by the kernel when the tree is executed,
#   using the script read_MS_auxinfo.py.
#   The latter sets the state of a number of leaf nodes (MeqConstant/MeqParm)
#   that have to be created beforehand. This is one of the functions of
#   the MS object.
#


#=================================================================================
# Preamble:
#=================================================================================

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
from Timba.Meq import meq                     # required for _create_beam()
# from copy import deepcopy
from numarray import *
from math import *

from Timba.Trees import TDL_common
from Timba.Trees import TDL_Leaf
from Timba.Trees import TDL_radio_conventions




#**************************************************************************************
# Class MS: (example of single-element Antenna)
#**************************************************************************************

class MSauxinfo (TDL_common.Super):
    """An MSauxinfo object contains auxiliary (i.e. non-data) MS info"""
    
    def __init__(self, **pp):
        
        pp.setdefault('type', 'MSauxinfo')               # object type
        pp.setdefault('label', pp['type'])

        TDL_common.Super.__init__(self, **pp)

        self.__color_xyz = 'blue'
        self.__color_uv = 'red'
        self.__color_uw = 'magenta'
        self.__color_rxyz = 'green'
        self.__color_ruvw = 'darkGreen'

        self.clear()


    def MSname(self, new=None):
        """Get/set the name of the MS. If new, clear the object"""
        if new:
            self.MSname = new
            self.clear()
        return self.__MSname

    def oneliner(self):
        """Return a one-line summary of the available MS info"""
        s = TDL_common.Super.oneliner(self)
        # .......
        return s

    def display(self, txt=None, full=False, end=True):
        """Display (print) the available MS aux info"""
        ss = TDL_common.Super.display(self, txt=txt, end=False)
        indent1 = TDL_common.Super.display_indent1(self)
        indent2 = TDL_common.Super.display_indent2(self)
        ss = TDL_common.Super.display(self, txt=txt, end=False)

        skeys = self.station_keys()
        ss.append(indent1+'* .node_ra0()    -> '+str(self.node_ra0()))
        ss.append(indent1+'* .node_dec0()   -> '+str(self.node_dec0()))
        ss.append(indent1+'* .node_radec0() -> '+str(self.node_radec0()))
        ss.append(indent1+'* .nodes_xyz()  ('+str(len(self.__nodes_xyz))+'):')
        for skey in skeys:
            node = self.node_xyz(skey)
            ss.append(indent2+'- .node_xyz('+skey+') -> '+str(node))
        if True:
            ss.append(indent1+'* individual axis positions (3x'+str(len(self.__nodes_xpos))+'):')
            skey = skeys[len(skeys)-1]
            ss.append(indent2+'- __nodes_xpos['+skey+'] = '+str(self.__nodes_xpos[skey]))
            ss.append(indent2+'- __nodes_ypos['+skey+'] = '+str(self.__nodes_ypos[skey]))
            ss.append(indent2+'- __nodes_zpos['+skey+'] = '+str(self.__nodes_zpos[skey]))
        if len(self.__nodes_dxpos)>0:
            ss.append(indent1+'* relative positions (3x'+str(len(self.__nodes_dxpos))+'):')
            skey = skeys[len(skeys)-1]
            ss.append(indent2+'- __nodes_dxpos['+skey+'] = '+str(self.__nodes_dxpos[skey]))
            ss.append(indent2+'- __nodes_dypos['+skey+'] = '+str(self.__nodes_dypos[skey]))
            ss.append(indent2+'- __nodes_dzpos['+skey+'] = '+str(self.__nodes_dzpos[skey]))
        if len(self.__nodes_station_uvw)>0:
            ss.append(indent1+'* __nodes_station_uvw  ('+str(len(self.__nodes_station_uvw))+')')
        if len(self.__nodes_uvw)>0:
            ss.append(indent1+'* __nodes_uvw  ('+str(len(self.__nodes_uvw))+')')
            ss.append(indent2+'- __nodes_ucoord  ('+str(len(self.__nodes_ucoord))+')')
            ss.append(indent2+'- __nodes_vcoord  ('+str(len(self.__nodes_vcoord))+')')
            ss.append(indent2+'- __nodes_wcoord  ('+str(len(self.__nodes_wcoord))+')')
        ss.append(indent1+'* __root_MSauxinfo = '+str(self.__root_MSauxinfo))
        ss.append(indent1+'* .dcoll_xvsy() -> '+str(self.__dcoll_xvsy))
        ss.append(indent1+'* .dcoll_zvsy() -> '+str(self.__dcoll_zvsy))
        ss.append(indent1+'* .dcoll_uvsv() -> '+str(self.__dcoll_uvsv))
        ss.append(indent1+'* .dcoll_uvsw() -> '+str(self.__dcoll_uvsw))
        ss.append(indent1+'* .dcoll_vvsw() -> '+str(self.__dcoll_vvsw))
        
        if end: TDL_common.Super.display_end(self, ss)
        return ss

    def clear(self):
        """Clear the MSauxinfo interface object"""
        self.__MSname = 'undefined'
        self.__root_MSauxinfo = None
        self.__root_nodes = dict()
        self.__node_radec0 = None
        self.__node_ra0 = None
        self.__node_dec0 = None
        self.clear_config()
        return True

    def clear_config(self):
        """Clear the station configuration"""
        # self.__station_name = []
        self.__xyzpos_keys = ['xpos','ypos','zpos']        # part of expected names
        self.__station_keys = []
        self.__s12 = dict()                                # ifr tuples (skey1,skey2)

        self.__xyz = dict()
        self.__nodes_xyz = dict()

        self.__nodes_xpos = dict()
        self.__nodes_ypos = dict()
        self.__nodes_zpos = dict()

        self.__nodes_dxpos = dict()
        self.__nodes_dypos = dict()
        self.__nodes_dzpos = dict()

        self.__nodes_station_uvw = dict()
        self.__nodes_uvw = dict()
        self.__nodes_ucoord = dict()
        self.__nodes_vcoord = dict()
        self.__nodes_wcoord = dict()

        self.__dcoll_xvsy = None
        self.__dcoll_zvsy = None
        self.__dcoll_uvsv = None
        self.__dcoll_uvsw = None
        self.__dcoll_vvsw = None
        # self.__refpos = record()
        return True


    #--------------------------------------------------------------------
    # Interaction with phase centre coordinates
    #--------------------------------------------------------------------

    def radec0(self, ns=None, new=None):
        """Get/set RA,DEC of the uv-data phase centre"""
        if new:
            # Make new station_uvw nodes.....
            pass
        self.create_radec_nodes(ns)
        return self.__node_radec0

    def ra0(self, new=None):
        """Get/set RA of phase centre"""
        print '.ra0(): not yet implemented'
        if new:
            # Make new station_uvw nodes.....
            pass
        # return self.__node_ra0

    def dec0(self, new=None):
        """Get/set DEC of phase centre"""
        print '.dec0(): not yet implemented'
        if new:
            # Make new station_uvw nodes.....
            pass
        # return self.__node_dec0

    #--------------------------------------------------------------------

    def node_radec0(self): return self.__node_radec0
    def node_ra0(self): return self.__node_ra0
    def node_dec0(self): return self.__node_dec0

    def station_keys(self): return self.__station_keys

    def node_xyz(self, key=None):
        """Return the requested station xyz node(s)"""
        if not key: return self.__nodes_xyz                # all
        if not self.__nodes_xyz.has_key(key):
            print '** .node_xyz(',key,'): not recognised in:',self.__nodes_xyz.keys()
            return False
        return self.__nodes_xyz[key]                       # one

    def node_station_uvw(self, key=None, ns=None):
        """Return the requested station uvw node(s)"""
        if len(self.__nodes_station_uvw)==0:
            if ns: self.create_station_uvw_nodes(ns)
        if not key: return self.__nodes_station_uvw        # all
        if not self.__nodes_station_uvw.has_key(key):
            print '** .node_station_uvw(',key,'): not recognised in:',self.__nodes_station_uvw.keys()
            return False
        return self.__nodes_station_uvw[key]               # one


    def node_uvw(skey1, skey2, ns=None):
        """Return the requested (ifr) uvw node."""
        if len(self.__nodes_uvw)==0:                       # not created yet
            self.make_uvw_nodes(ns)                        # create uvw nodes
        key = str(skey1)+'_'+str(skey2)                    # ifr key 
        if self.__nodes_uvw.has_key(key):
            return self.__nodes_uvw[key]
        print '\n** .node_uvw(): ifr key not recognised:',key,'\n' 
        return False

    #--------------------------------------------------------------------

    def station_config_default(self, stations=range(15)):
        """Create a a default station configuration.
        If 15, it includes the LOFAR/WHAT station near RT8"""
        # NB: Stations might also be a list of names.....
        self.clear_config()
        for k in range(len(stations)):
            skey = TDL_radio_conventions.station_key(k)
            self.__station_keys.append(skey)               # list of station keys
            vk = float(k)
            self.__xyz[skey] = array([vk,-vk,vk/10])       # dummy x,y,z positions (m)
            # print '-',k,skey,self.__xyz[skey]
        # print
        return True

    def create_nodes(self, ns, stations=None):
        """Create all nodes expected by read_MS_auxinfo(hdr)"""
        if not self.__root_MSauxinfo:                      # do once only...
            if not stations==None:
                self.station_config_default(stations=stations)
            self.create_radec_nodes(ns)
            self.create_xyz_nodes(ns)
            # Attach them to a single root node (to avoid meqbrowser clutter)
            cc = []
            for key in self.__root_nodes.keys():
                cc.append(self.__root_nodes[key])
            self.__root_MSauxinfo = ns.MSauxinfo << Meq.Composer(children=cc)
        return self.__root_MSauxinfo

    def create_radec_nodes(self, ns):
        """Create the (RA,DEC) nodes expected by read_MS_auxinfo(hdr)
        and bundle them into radec-nodes (input for MeqUVW nodes)"""
        if self.__node_radec0: return True                 # Do once only....
        self.__node_ra0 = ns.ra0 << Meq.Constant(0.0)
        self.__node_dec0 = ns.dec0 << Meq.Constant(1.0)
        self.__node_radec0 = ns.radec0 << Meq.Composer(self.__node_ra0,self.__node_dec0)
        # Attach them to a single root node (to avoid meqbrowser clutter)
        self.__root_nodes['radec0'] = ns.MSauxinfo_radec0 << Meq.Composer(self.__node_radec0)
        return True

    def create_xyz_nodes(self, ns, parm=False):
        """Create the (x,y,z) nodes expected by read_MS_auxinfo(hdr)
        and bundle them into xyz-nodes (input for MeqUVW nodes)"""
        if len(self.__nodes_xyz)>0: return True            # Do once only....
        cc = []
        for skey in self.station_keys():
            xyz = []
            for pkey in self.__xyzpos_keys:
                if pkey=='xpos': v = self.__xyz[skey][0]
                if pkey=='ypos': v = self.__xyz[skey][1]
                if pkey=='zpos': v = self.__xyz[skey][2]
                # Create node expected by read_MS_auxinfo(hdr):
                name = pkey+':s='+skey                     # expected node name 
                parm = False                               # inhibit this option..........!!
                if parm:
                    # NB: This does not work, because read_MS_auxinfo(hdr)
                    #     does not update the state of a MeqParm......!!
                    node = ns[name] << Meq.Parm(v)         # solve for station pos...
                else:
                    node = ns[name] << Meq.Constant(v)     # constant station pos
                if pkey=='xpos': self.__nodes_xpos[skey] = node
                if pkey=='ypos': self.__nodes_ypos[skey] = node
                if pkey=='zpos': self.__nodes_zpos[skey] = node
                xyz.append(node)
                cc.append(node)
            # Make xyz 'tensor' nodes per station: 
            name = 'xyzpos:s='+skey                        # expected node name 
            self.__nodes_xyz[skey] = ns[skey] << Meq.Composer(children=xyz)
            cc.append(self.__nodes_xyz[skey])              #
        # Attach them to a single root node (to avoid meqbrowser clutter)
        self.__root_nodes['xyz'] = ns.MSauxinfo_xyz << Meq.Composer(children=cc)
        return True


    def create_station_uvw_nodes(self, ns):
        """Create station-based MeqUVW nodes related to (ra0,dec0)"""
        print '\n** create_station_uvw_nodes(): ',len(self.__nodes_station_uvw),'\n'
        if len(self.__nodes_station_uvw)>0: return True    # Do once only....
        first = True
        cc = []
        for skey in self.station_keys():
            if first:
                xyz0 = self.__nodes_xyz[skey]              # reference position
                first = False
            # Tensor node of 3 STATION uvw coordinates:
            name = 'uvw:s='+skey+':q=radec0'
            self.__nodes_station_uvw[skey] = ns[name] << Meq.UVW(radec=self.__node_radec0,
                                                                 xyz_0=xyz0,
                                                                 xyz=self.__nodes_xyz[skey])
            cc.append(self.__nodes_station_uvw[skey])      #
        # Attach them to a single root node (to avoid meqbrowser clutter)
        self.__root_nodes['station_uvw'] = ns.MSauxinfo_uvw << Meq.Composer(children=cc)
        self.history('** .create_station_uvw_nodes()')
        return True




    #-------------------------------------------------------------------------------
    # Functions for generating dataCollect nodes (plotting)
    #-------------------------------------------------------------------------------


    def make_dpos_nodes(self, ns):
        """Make nodes with relative positions, for plotting"""
        if len(self.__nodes_dxpos)>0: return True          # do only once
        first = True
        for skey in self.station_keys():
            if first:
                x0 = self.__nodes_xpos[skey]
                y0 = self.__nodes_ypos[skey]
                z0 = self.__nodes_zpos[skey]
                first = False
            self.__nodes_dxpos[skey] = ns << Meq.Subtract(self.__nodes_xpos[skey],x0)
            self.__nodes_dypos[skey] = ns << Meq.Subtract(self.__nodes_ypos[skey],y0)
            self.__nodes_dzpos[skey] = ns << Meq.Subtract(self.__nodes_zpos[skey],z0)
        return True


    def make_uvw_nodes(self, ns):
        """Make nodes with ifr-based uvw."""
        if len(self.__nodes_uvw)>0: return True           # do only once
        self.create_station_uvw_nodes(ns)                 # just in case
        skeys = self.station_keys()
        for i in range(len(skeys)):
            for j in range(len(skeys)):
                if j>i:
                    ikey = skeys[i]+'_'+skeys[j]          # ifr key ....??
                    self.__s12[ikey] = (skeys[i],skeys[j])

                    # Tensor node with 3 (u,v,w) coordinates:
                    name = 'uvw'+':s1='+skeys[i]+':s2='+skeys[j]
                    node = ns[name] << Meq.Subtract(self.__nodes_station_uvw[skeys[i]],
                                                    self.__nodes_station_uvw[skeys[j]])
                    self.__nodes_uvw[ikey] = node

                    # Make separate nodes, for plotting:
                    name = 'ucoord'+':s1='+skeys[i]+':s2='+skeys[j]
                    self.__nodes_ucoord[ikey] = ns[name] << Meq.Selector(node, index=0)
                    name = 'vcoord'+':s1='+skeys[i]+':s2='+skeys[j]
                    self.__nodes_vcoord[ikey] = ns[name] << Meq.Selector(node, index=1)
                    name = 'wcoord'+':s1='+skeys[i]+':s2='+skeys[j]
                    self.__nodes_wcoord[ikey] = ns[name] << Meq.Selector(node, index=2)
        return True


    def dcoll(self, ns):
        """Make a list of all dataCollect nodes"""
        dcoll = []
        dcoll.append(self.dcoll_xvsy(ns))
        dcoll.append(self.dcoll_zvsy(ns))
        dcoll.append(self.dcoll_uvsv(ns))
        dcoll.append(self.dcoll_uvsw(ns))
        dcoll.append(self.dcoll_vvsw(ns))
        return dcoll
    

    def dcoll_xvsy(self, ns):
        """Make dataCollect node for plotting (relative) x vs y"""
        if not self.__dcoll_xvsy: 
            self.make_dpos_nodes(ns)                       # self.__nodes_dpos
            key = 'xvsy'                                   # dx vs dy
            cc = []
            for skey in self.station_keys():
                name = key+':s='+skey
                node = ns[name] << Meq.ToComplex(self.__nodes_dypos[skey],
                                                 self.__nodes_dxpos[skey])
                cc.append(node)
            attrib = record(plot=record(), tag=key)
            attrib['plot'] = record(type='realvsimag',
                                    title=' array configuration (x vs y)',
                                    color=self.__color_xyz,
                                    y_axis='xpos (N-S, relative) (m)',
                                    x_axis='ypos (E-W, relative) (m)')
            name = 'dcoll_'+key
            node = ns[name] << Meq.DataCollect(children=cc, attrib=attrib,
                                               top_label=hiid('visu'))
            self.__dcoll_xvsy = node
        return self.__dcoll_xvsy


    def dcoll_zvsy(self, ns):
        """Make dataCollect node for plotting (relative) z vs y"""
        if not self.__dcoll_zvsy: 
            self.make_dpos_nodes(ns)                       # self.__nodes_dpos
            key = 'zvsy'                                   # dz vs dy
            cc = []
            for skey in self.station_keys():
                name = key+':s='+skey
                node = ns[name] << Meq.ToComplex(self.__nodes_dypos[skey],
                                                 self.__nodes_dzpos[skey])
                cc.append(node)
            attrib = record(plot=record(), tag=key)
            attrib['plot'] = record(type='realvsimag',
                                    title=' array configuration (z vs y)',
                                    color=self.__color_xyz,
                                    y_axis='zpos (relative) (m)',
                                    x_axis='ypos (E-W, relative) (m)')
            name = 'dcoll_'+key
            node = ns[name] << Meq.DataCollect(children=cc, attrib=attrib,
                                               top_label=hiid('visu'))
            self.__dcoll_zvsy = node
        return self.__dcoll_zvsy


    def dcoll_uvsv(self, ns):
        """Make dataCollect node for plotting u vs w"""
        if not self.__dcoll_uvsv: 
            self.make_uvw_nodes(ns)                        # just in case
            key = 'uvsv'                                   # dz vs dy
            cc = []
            for ikey in self.__s12.keys():
                s12 = self.__s12[ikey]
                name = key+':s1='+s12[0]+':s2='+s12[1]
                node = ns[name] << Meq.ToComplex(self.__nodes_vcoord[ikey],
                                                 self.__nodes_ucoord[ikey])
                cc.append(node)

            attrib = record(plot=record(), tag=key)
            attrib['plot'] = record(type='realvsimag', title=' (snapshot) uv-coverage',
                                    color=self.__color_uv,
                                    x_axis='u_coord (m)', y_axis='v_coord (m)')
            name = 'dcoll_'+key
            node = ns[name] << Meq.DataCollect(children=cc, attrib=attrib,
                                               top_label=hiid('visu'))
            self.__dcoll_uvsv = node
        return self.__dcoll_uvsv


    def dcoll_uvsw(self, ns):
        """Make dataCollect node for plotting u vs w"""
        if not self.__dcoll_uvsw: 
            self.make_uvw_nodes(ns)                        # just in case
            key = 'uvsw'                           
            cc = []
            for ikey in self.__s12.keys():
                s12 = self.__s12[ikey]
                name = key+':s1='+s12[0]+':s2='+s12[1]
                node = ns[name] << Meq.ToComplex(self.__nodes_wcoord[ikey],
                                                 self.__nodes_ucoord[ikey])
                cc.append(node)

            attrib = record(plot=record(), tag=key)
            attrib['plot'] = record(type='realvsimag', title=' u vs w',
                                    color=self.__color_uv,
                                    x_axis='u_coord (m)', y_axis='w_coord (m)')
            name = 'dcoll_'+key
            node = ns[name] << Meq.DataCollect(children=cc, attrib=attrib,
                                               top_label=hiid('visu'))
            self.__dcoll_uvsw = node
        return self.__dcoll_uvsw


    def dcoll_vvsw(self, ns):
        """Make dataCollect node for plotting v vs w"""
        if not self.__dcoll_vvsw: 
            self.make_uvw_nodes(ns)                        # just in case
            key = 'vvsw'                                   
            cc = []
            for ikey in self.__s12.keys():
                s12 = self.__s12[ikey]
                name = key+':s1='+s12[0]+':s2='+s12[1]
                node = ns[name] << Meq.ToComplex(self.__nodes_wcoord[ikey],
                                                 self.__nodes_vcoord[ikey])
                cc.append(node)

            attrib = record(plot=record(), tag=key)
            attrib['plot'] = record(type='realvsimag', title=' v vs w',
                                    color=self.__color_uv,
                                    x_axis='v_coord (m)', y_axis='w_coord (m)')
            name = 'dcoll_'+key
            node = ns[name] << Meq.DataCollect(children=cc, attrib=attrib,
                                               top_label=hiid('visu'))
            self.__dcoll_vvsw = node
        return self.__dcoll_vvsw



















#========================================================================
# Helper routines:
#========================================================================

# Counter service (use to automatically generate unique node names)

_counters = {}

def _counter (key, increment=0, reset=False, trace=False):
    global _counters
    _counters.setdefault(key, 0)
    if reset: _counters[key] = 0
    _counters[key] -= increment
    if trace: print '** MS: _counters(',key,') =',_counters[key]
    return _counters[key]






#========================================================================
# Test routine:
#========================================================================

if __name__ == '__main__':
    print '\n*******************\n** Local test of: TDL_MSauxinfo.py:\n'
    from Timba.Trees import TDL_display
    # from Timba.Trees import JEN_record
    ns = NodeScope()
    
    if 1:
        obj = MSauxinfo(label='initial')

    if 1:
        obj.station_config_default()
        obj.create_nodes(ns)

    if 0:
        obj.make_dpos_nodes(ns)

    if 0:
        obj.create_station_uvw_nodes(ns)
        obj.make_uvw_nodes(ns)
        obj.dcoll_uvsv(ns)
        obj.dcoll_uvsw(ns)

    if 0:
        obj.dcoll_xvsy(ns)
        obj.dcoll_zvsy(ns)

    if 1:
        dcoll = obj.dcoll(ns)
        dcoll = ns.dcoll << Meq.Composer(children=dcoll)
        TDL_display.subtree(dcoll, 'dcoll', full=True, recurse=5)

    if 1:
        # Display the final result:
        # TDL_display.subtree(..., full=True, recurse=5)
        obj.display('final result')
    print '\n*******************\n** End of local test of: TDL_MSauxinfo.py:\n'



#============================================================================================









 

