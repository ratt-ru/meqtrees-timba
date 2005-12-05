# TDL_MSauxinfo.py
#
# Author: J.E.Noordam
#
# Short description:
#    An MSauxinfo object contains auxiliary info from an AIPS++ Measurement Set 
#
# History:
#    - 04 dec 2005: creation
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

class MS (TDL_common.Super):
    """An MS object contains auxiliary (i.e. non-data) MS info"""
    
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
            ss.append(indent2+'- __nodes_xpos['+skey+'] -> '+str(self.__nodes_xpos[skey]))
            ss.append(indent2+'- __nodes_ypos['+skey+'] -> '+str(self.__nodes_ypos[skey]))
            ss.append(indent2+'- __nodes_zpos['+skey+'] -> '+str(self.__nodes_zpos[skey]))
        if len(self.__nodes_dxpos)>0:
            ss.append(indent1+'* relative positions (3x'+str(len(self.__nodes_dxpos))+'):')
            skey = skeys[len(skeys)-1]
            ss.append(indent2+'- __nodes_dxpos['+skey+'] -> '+str(self.__nodes_dxpos[skey]))
            ss.append(indent2+'- __nodes_dypos['+skey+'] -> '+str(self.__nodes_dypos[skey]))
            ss.append(indent2+'- __nodes_dzpos['+skey+'] -> '+str(self.__nodes_dzpos[skey]))
        if self.__dcoll_xvsy:
            ss.append(indent1+'* .dcoll_xvsy() -> '+str(self.__dcoll_xvsy))
        if self.__dcoll_zvsy:
            ss.append(indent1+'* .dcoll_zvsy() -> '+str(self.__dcoll_zvsy))
        
        if end: TDL_common.Super.display_end(self, ss)
        return ss

    def clear(self):
        """Clear the MSauxinfo interface object"""
        self.__MSname = 'undefined'
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
        self.__xyz = dict()
        self.__nodes_xyz = dict()
        self.__nodes_xpos = dict()
        self.__nodes_ypos = dict()
        self.__nodes_zpos = dict()
        self.__nodes_dxpos = dict()
        self.__nodes_dypos = dict()
        self.__nodes_dzpos = dict()
        self.__dcoll_xvsy = None
        self.__dcoll_zvsy = None
        # self.__refpos = record()
        return True


    def station_keys(self): return self.__station_keys

    def node_xyz(self, key=None):
        """Return the requested node_xyz(s)"""
        if not key: return self.__nodes_xyz                # all
        return self.__nodes_xyz[key]                       # one


    def station_config_default(self, stations=range(15)):
        """Create a a default station configuration"""
        # NB: Stations might also be a list of names.....
        self.clear_config()
        for k in range(len(stations)):
            skey = TDL_radio_conventions.station_key(k)
            self.__station_keys.append(skey)               # list of station keys
            vk = float(k)
            self.__xyz[skey] = array([vk,-vk,vk/10])       # dummy x,y,z positions (m)
            print '-',k,skey,self.__xyz[skey]
        print
        return True

    def node_radec0(self): return self.__node_radec0
    def node_ra0(self): return self.__node_ra0
    def node_dec0(self): return self.__node_dec0

    def create_radec_nodes(self, ns):
        """Create the (RA,DEC) nodes expected by read_MS_auxinfo(hdr)
        and bundle them into radec-nodes (input for MeqUVW nodes)"""
        if self.__node_radec0: return True                 # Do once only....
        self.__node_ra0 = ns.ra0 << Meq.Constant(0.0)
        self.__node_dec0 = ns.dec0 << Meq.Constant(1.0)
        self.__node_radec0 = ns.radec0 << Meq.Composer(self.__node_ra0,self.__node_dec0)
        return True

    def create_nodes(self, ns):
        """Create all nodes expected by read_MS_auxinfo(hdr)"""
        self.create_radec_nodes(ns)
        self.create_xyz_nodes(ns)
        return True

    def create_xyz_nodes(self, ns, parm=True):
        """Create the (x,y,z) nodes expected by read_MS_auxinfo(hdr)
        and bundle them into xyz-nodes (input for MeqUVW nodes)"""
        if len(self.__nodes_xyz)>0: return True            # Do once only....
        for skey in self.station_keys():
            xyz = []
            for pkey in self.__xyzpos_keys:
                if pkey=='xpos': v = self.__xyz[skey][0]
                if pkey=='ypos': v = self.__xyz[skey][1]
                if pkey=='zpos': v = self.__xyz[skey][2]
                # Create node expected by read_MS_auxinfo(hdr):
                name = pkey+':s='+skey                     # expected node name 
                if parm:
                    node = ns[name] << Meq.Parm(v)         # solve for station pos...
                else:
                    node = ns[name] << Meq.Constant(v)     # constant station pos
                if pkey=='xpos': self.__nodes_xpos[skey] = node
                if pkey=='ypos': self.__nodes_ypos[skey] = node
                if pkey=='zpos': self.__nodes_zpos[skey] = node
                xyz.append(node)
            # Make xyz 'tensor' nodes per station: 
            name = 'xyzpos:s='+skey                        # expected node name 
            self.__nodes_xyz[skey] = ns[skey] << Meq.Composer(children=xyz)
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


    def dcoll(self, ns):
        """Make a list of all dataCollect nodes"""
        dcoll = []
        dcoll.append(self.dcoll_xvsy(ns))
        dcoll.append(self.dcoll_zvsy(ns))
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
                                    y_axis='xpos (N-S, relative)',
                                    x_axis='ypos (E-W, relative)')
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
                                    y_axis='zpos (relative)',
                                    x_axis='ypos (E-W, relative)')
            name = 'dcoll_'+key
            node = ns[name] << Meq.DataCollect(children=cc, attrib=attrib,
                                               top_label=hiid('visu'))
            self.__dcoll_zvsy = node
        return self.__dcoll_zvsy



















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
        obj = MS(label='initial')

    if 1:
        obj.station_config_default()
        obj.create_nodes(ns)

    if 0:
        obj.make_dpos_nodes(ns)

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









 

