# file: create_MS_interface_nodes.py

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
from Timba.Trees import TDL_radio_conventions
from math import *


#===============================================================================
# Create a small subtree of nodes that are expected by the function
# that reads information from the MS:

def create_MS_interface_nodes(ns, stations=range(14), sep9A=36, ra0=0.0, dec0=1.0):
   """Create a small subtree of nodes with reserved names, that are expected by
   the function that reads information from the MS"""

   # The various node-names are returned in a structured record
   rr = record(xyz=record(), uvw=record(), dcoll=record())  

   # The created nodes are tied together in a dummy root node,
   # to avoid clutter in the browser
   root = []                                            # see below

   #--------------------------------------------------------------------------------
   # Tensor node with 2 observation phase centre coords:
   ra0 = ns.ra0 << Meq.Constant(ra0)
   dec0 = ns.dec0 << Meq.Constant(dec0)
   node = ns.radec0 << Meq.Composer(ra0, dec0)
   root.append(node)
   rr.radec0 = node.name 

   #--------------------------------------------------------------------------------
   # Station positions:
   pkeys = ['xpos','ypos','zpos']
   vrefpos = record(xpos=0, ypos=0, zpos=0)          # reference pos value
   dcoll = record(xpos=[], ypos=[], zpos=[], xvsy=[], zvsy=[])

   rr.sep9A = sep9A                                  # separation (m) between 9 and A(10)
   rr.stations = stations
   rr.station_keys = []
   rr.vxyz = record()
   rr.refpos = record()
   node_xyz = dict()
   node_uvw = dict()
   xyz0 = dict()
   first = True
   zoffset = 0.001                      
   for station in stations:
      skey = TDL_radio_conventions.station_key(station)
      rr.station_keys.append(skey)                   # list of station keys

      xyz = dict()
      rr[skey] = record()
      rr.vxyz[skey] = record()
      for pkey in pkeys:
          name = pkey+':s='+skey
          value = 0.0                                # dummy position (m) 
          if pkey=='zpos':                           # non-zero, but small (mm) 
             zoffset *= -1                           # toggle sign
             value = zoffset*station
          if pkey=='ypos':             
             value = -(station*144)                  # 1D E-W array (WSRT-like)
             sep09 = 9*144                           # separation (m) between 0 and 9
             if station==10: value = -(sep09 + rr.sep9A)   
             if station==11: value = -(sep09 + rr.sep9A + 72)   
             if station==12: value = -(sep09 + sep09 + rr.sep9A)          # 0A = 9C  
             if station==13: value = -(sep09 + sep09 + rr.sep9A + 72)     # 0B = 9D
          if station==14:                            # station: WHAT 
             if pkey=='xpos': value = -100
             if pkey=='ypos': value = -(8.5*144)
             if pkey=='zpos': value = 1.5
          value += vrefpos[pkey]                     # add reference position
          rr.vxyz[skey][pkey] = value                # keep for ifrs below
          node = ns[name] << Meq.Constant(value)
          xyz[pkey] = node                           # used for composer nodes
          rr[skey][pkey] = node.name           

      # Array reference position coords:
      if first: 
         node = ns.xyz0 << Meq.Composer(xyz['xpos'],xyz['ypos'],xyz['zpos'])
         root.append(node)
         rr.xyz0 = node.name 
         for pkey in pkeys:
            name = pkey+'0'
            rr.refpos[name] = xyz[pkey].name
            xyz0[pkey] = xyz[pkey]
         first = False

      # Make nodes with relative positions, for plotting:
      dxyz = dict()
      for pkey in pkeys:
         name = 'rel_'+pkey+':s='+skey
         node = ns[name] << Meq.Subtract(xyz[pkey],xyz0[pkey])
         dxyz[pkey] = node                           # used for x vs y below
         dcoll[pkey].append(node)                    # collect for dcoll nodes

      # Make 'complex' node for plotting (relative) x vs y:
      key = 'xvsy'                                   # dx vs dy
      name = key+':s='+skey
      node = ns[name] << Meq.ToComplex(dxyz['ypos'],dxyz['xpos'])
      dcoll[key].append(node)                        # collect for dcoll nodes

      # Make 'complex' node for plotting (relative) z vs y:
      key = 'zvsy'                                   # dz vs dy
      name = key+':s='+skey
      node = ns[name] << Meq.ToComplex(dxyz['ypos'],dxyz['zpos'])
      dcoll[key].append(node)                        # collect for dcoll nodes

      # Tensor node of 3 station position coordinates:
      name = 'xyz:s='+skey
      node = ns[name] << Meq.Composer(xyz['xpos'],xyz['ypos'],xyz['zpos'])
      root.append(node)
      node_xyz[skey] = node                          # used for ifrs below
      rr.xyz[skey] = node.name

      # Tensor node of 3 STATION uvw coordinates:
      name = 'uvw:s='+skey
      node = ns[name] << Meq.UVW(radec= ns.radec0, xyz_0=ns.xyz0, xyz=node)
      node_uvw[skey] = node                          # used for ifrs below
      root.append(node)
      rr.uvw[skey] = node.name 


   #--------------------------------------------------------------------------------
   # Calculate ifr-baselines etc:
   rr.ifr_keys = []
   rr.ifr_skeys = record()
   rr.vrxyz = record()

   rr.dxyz = record()
   rr.d2xyz = record()
   rr.rxyz = record()
   dcoll.rxyz = []

   rr.duvw = record()
   rr.d2uvw = record()
   rr.ruvw = record()
   dcoll.ruvw = []

   dcoll.uvsv = []
   dcoll.uvsw = []
   # dcoll.wcoord = []

   for s1 in stations:
      skey1 = TDL_radio_conventions.station_key(s1)
      x1 = rr.vxyz[skey1]['xpos']
      y1 = rr.vxyz[skey1]['ypos']
      z1 = rr.vxyz[skey1]['zpos']
      for s2 in stations:
         if s2>s1:                                          # ignore autocorrs
            skey2 = TDL_radio_conventions.station_key(s2)    
            key = TDL_radio_conventions.ifr_key(s1,s2) 
            rr.ifr_keys.append(key)                         # list of ifr keys
            rr.ifr_skeys[key] = (skey1,skey2)

            # Calculate the dummy(!) WSRT baseline lengths:
            dx = rr.vxyz[skey2]['xpos']-x1
            dy = rr.vxyz[skey2]['ypos']-y1
            dz = rr.vxyz[skey2]['zpos']-z1
            rr.vrxyz[key] = sqrt(dx**2 + dy**2 + dz**2)     # value (float)

            # Make nodes that gives the xyz-distance (rxyz) for the ifr:
            # (Alternative: Use a (new) node MeqLength node that calculates sqrt(sum(tensor**2)))
            name = 'dxyz:s1='+skey1+':s2='+skey2            # diff
            node = ns[name] << Meq.Subtract(node_xyz[skey1], node_xyz[skey2])
            # rr.dxyz[key] = node.name
            name = 'd2xyz:s1='+skey1+':s2='+skey2           # diff**2
            node = ns[name] << Meq.Sqr(node)
            # rr.d2xyz[key] = node.name
            name = 'rxyz:s1='+skey1+':s2='+skey2            # sqr(diff**2)
            node = ns[name]  << Meq.Sqrt(ns << Meq.Add(node))
            rr.rxyz[key] = node.name
            root.append(node)
            dcoll.rxyz.append(node)

            # Make nodes that gives the uvw-distance (ruvw) for the ifr:
            # (Alternative: Use a (new) node MeqLength node that calculates sqrt(sum(tensor**2)))
            name = 'duvw:s1='+skey1+':s2='+skey2            # diff
            node = ns[name] << Meq.Subtract(node_uvw[skey1], node_uvw[skey2])
            duvw = node                                     # used below
            # rr.duvw[key] = node.name
            name = 'd2uvw:s1='+skey1+':s2='+skey2           # diff**2
            node = ns[name] << Meq.Sqr(node)
            # rr.d2uvw[key] = node.name
            name = 'ruvw:s1='+skey1+':s2='+skey2            # sqr(diff**2)
            node = ns[name]  << Meq.Sqrt(ns << Meq.Add(node))
            rr.ruvw[key] = node.name
            root.append(node)
            dcoll.ruvw.append(node)

            # Extract the individual (u,v,w) nodes for plotting:
            ucoord = ns['ucoord:s1='+skey1+':s2='+skey2] << Meq.Selector(duvw, index=0)
            vcoord = ns['vcoord:s1='+skey1+':s2='+skey2] << Meq.Selector(duvw, index=1)
            wcoord = ns['wcoord:s1='+skey1+':s2='+skey2] << Meq.Selector(duvw, index=2)

            # Make 'complex' node for plotting u vs v:
            node = ns['uvsv:s1='+skey1+':s2='+skey2] << Meq.ToComplex (ucoord, vcoord)
            dcoll.uvsv.append(node)                         # collect for dcoll nodes

            # Make 'complex' node for plotting u vs w:
            node = ns['uvsw:s1='+skey1+':s2='+skey2] << Meq.ToComplex (ucoord, wcoord)
            dcoll.uvsw.append(node)                         # collect for dcoll nodes

            # Plot the w-coord separately (along the imaginary axis):
            # node = ns['w_plot:s1='+skey1+':s2='+skey2] << Meq.ToComplex (0.0, wcoord)
            # dcoll.wcoord.append(node)                       # collect for dcoll nodes


   #--------------------------------------------------------------------------------
   # Get redundant spacings (for the dummy WSRT array!):
   rr.redun = record(group=record(), pairs=record())        # ifrs to be used for redun
   crit = 0.1                                               # redundancy criterion (m)
   for i in range(len(rr.ifr_keys)-1):
      ifr1 = rr.ifr_keys[i]
      ifr1_last = None
      r1 = rr.vrxyz[ifr1]
      gkey = str(round(r1))                                 # group key
      for j in range(i+1,len(rr.ifr_keys)):
         ifr2 = rr.ifr_keys[j]
         dr = abs(rr.vrxyz[ifr2] - r1)
         if dr<crit:                                        # close enough: redundant
            if not rr.redun.group.has_key(gkey): rr.redun.group[gkey] = []
            if not rr.redun.group[gkey].__contains__(ifr1):
               rr.redun.group[gkey].append(ifr1)
            if not rr.redun.group[gkey].__contains__(ifr2):
               rr.redun.group[gkey].append(ifr2)
            if not rr.redun.pairs.has_key(gkey): rr.redun.pairs[gkey] = []
            if not ifr1==ifr1_last:                         # ...
               rr.redun.pairs[gkey].append((ifr1,ifr2))       
               ifr1_last = ifr1
               # print '- redundant spacing:',i,j,':',(ifr1,ifr2),': gkey =',gkey,' dr =',dr,' (m)'



   # Make a list of ifrs (keys) to be used for align (selgcal)
   rr.align = []
   smin = min(stations)                                    # minimum WSRT telescope (e.g. 0)
   smax = smin
   for station in range(10):
      if stations.__contains__(station): smax = station    # max fixed WSRT telescope
   ss = [smax,10,11,12,13,14]                              # depend on rr.sep9A==72?
   for station in ss:
      if stations.__contains__(station):
         rr.align.append(TDL_radio_conventions.ifr_key(smin,station))
   

   #--------------------------------------------------------------------------------
   # Make dataCollect nodes from children collected in dcoll-record:
   #--------------------------------------------------------------------------------

   color_xyz = 'blue'
   color_uv = 'red'
   color_uw = 'magenta'
   color_rxyz = 'green'
   color_ruvw = 'darkGreen'


   # ------------- Station xpos vs ypos (fake complex):
   key = 'xvsy'
   attrib = record(plot=record(), tag=key)
   attrib['plot'] = record(type='realvsimag', title=' array configuration (x vs y)',
                           color=color_xyz,
                           y_axis='xpos (N-S, relative)',
                           x_axis='ypos (E-W, relative)')
   name = 'dcoll_MS_'+key
   node = ns[name] << Meq.DataCollect(children=dcoll[key], attrib=attrib,
                                      top_label=hiid('visu'))
   rr.dcoll[key] = node.name

   # ------------- Station zpos vs ypos (fake complex):
   key = 'zvsy'
   attrib = record(plot=record(), tag=key)
   attrib['plot'] = record(type='realvsimag', title=' array configuration (z vs y)',
                           color=color_xyz,
                           y_axis='zpos (relative)',
                           x_axis='ypos (E-W, relative)')
   name = 'dcoll_MS_'+key
   node = ns[name] << Meq.DataCollect(children=dcoll[key], attrib=attrib,
                                      top_label=hiid('visu'))
   rr.dcoll[key] = node.name


   # ------------- Baseline lengths (xyz):
   key = 'rxyz'
   attrib = record(plot=record(), tag=key)
   attrib['plot'] = record(type='realvsimag', title=' baseline length (m)',
                           color=color_rxyz, x_axis=key, y_axis='...')
   name = 'dcoll_MS_'+key
   node = ns[name] << Meq.DataCollect(children=dcoll[key], attrib=attrib,
                                      top_label=hiid('visu'))
   rr.dcoll[key] = node.name


   # ------------- Ifr ucoord vs vcoord (fake complex):
   key = 'uvsv'
   attrib = record(plot=record(), tag=key)
   attrib['plot'] = record(type='realvsimag', title=' (snapshot) uv-coverage',
                           color=color_uv, x_axis='u_coord', y_axis='v_coord')
   name = 'dcoll_MS_'+key
   node = ns[name] << Meq.DataCollect(children=dcoll[key], attrib=attrib,
                                      top_label=hiid('visu'))
   rr.dcoll[key] = node.name


   # ------------- Ifr ucoord vs wcoord (fake complex):
   key = 'uvsw'
   attrib = record(plot=record(), tag=key)
   attrib['plot'] = record(type='realvsimag', title=' u vs w',
                           color=color_uw, x_axis='u_coord', y_axis='w_coord')
   name = 'dcoll_MS_'+key
   node = ns[name] << Meq.DataCollect(children=dcoll[key], attrib=attrib,
                                      top_label=hiid('visu'))
   rr.dcoll[key] = node.name


   # ------------- Baseline lengths (uvw):
   key = 'ruvw'
   attrib = record(plot=record(), tag=key)
   attrib['plot'] = record(type='realvsimag', title=' baseline length (wvl)',
                           color=color_ruvw, x_axis=key, y_axis='...')
   name = 'dcoll_MS_'+key
   node = ns[name] << Meq.DataCollect(children=dcoll[key], attrib=attrib,
                                      top_label=hiid('visu'))
   rr.dcoll[key] = node.name


   #--------------------------------------------------------------------------------
   # Tie the interface root nodes together by a dummy root node,
   # to avoid clutter in the browser.
   node = ns.ms_interface_nodes << Meq.Add(*root)
   rr.root = node.name

   #--------------------------------------------------------------------------------
   # Finished: Return a record (rr) of node-names: 
   return rr





#====================================================================================
# For comparison: The OMS version 
#====================================================================================

def create_MS_interface_nodes_old(ns, num_ant=14):
   """Create a small subtree of nodes with reserved names, that are expected by
   the function that reads information from the MS"""

   # All nodes are tied together in a common root, to avoid clutter:
   cc = []

   # Field (pointing) centre:
   cc.append(ns.ra0 << 0.0)
   cc.append(ns.dec0 << 1.0)

   # Antenna positions:
   coords = ('x','y','z')
   for iant in range(num_ant):
      sn = str(iant+1)
      for (j,label) in enumerate(coords):
         cc.append(ns[label+'.'+sn] << 0.0)

   # Array reference position (x,y,z):
   for (j,label) in enumerate(coords):
      cc.append(ns[label+'0'] << 0.0)

   # Tie them all together by a single root node.
   # This is to avoid clutter of the list of root-nodes in the browser,
   # in the case where they are not connected to the tree for some reason.
   root = ns.ms_interface_nodes << Meq.Add(*cc)
   print '\n** create_MS_interface_nodes(): -> root =',root,'\n'
   rr = record(aa=1, root=root.name)
   print 'rr =',type(rr),':',rr
   return rr



#====================================================================================
# For comparison, here is the function from matrix343.py
#====================================================================================

def forest_measurement_set_info(ns, num_ant=14):
   """Copied from natrix343.py, and slightly adapted"""

   # All nodes are tied together in a common root, to avoid clutter:
   cc = []

   cc.append(ns.ra0 << Meq.Constant(0.0))
   cc.append(ns.dec0 << Meq.Constant(0.0))
   cc.append(ns.radec0 << Meq.Composer(ns.ra0, ns.dec0))
   
   for i in range(num_ant):
      station= str(i+1)
      cc.append(ns.x(s=station) << Meq.Constant(0.0))
      cc.append(ns.y(s=station) << Meq.Constant(0.0))
      cc.append(ns.z(s=station) << Meq.Constant(0.0))
      if i == 0:
         cc.append(ns.xyz0 << Meq.Composer(ns.x(s=station), ns.y(s=station),ns.z(s=station)))
        
      cc.append(ns.xyz(s=station)  << Meq.Composer(ns.x(s=station),
                                                   ns.y(s=station),
                                                   ns.z(s=station)))
      cc.append(ns.uvw(s=station) << Meq.UVW(radec= ns.radec0,
                                             xyz_0= ns.xyz0,
                                             xyz  = ns.xyz(s=station)))

   # Tie them all together by a single root node.
   # This is to avoid clutter of the list of root-nodes in the browser,
   # in the case where they are not connected to the tree for some reason.
   root = ns.ms_interface_nodes << Meq.Add(*cc)
   print '\n** forest_measurement_set_info(): -> root =',root,'\n'
   return root





#========================================================================
# Test routine:
#========================================================================

if __name__ == '__main__':
    print '\n*******************\n** Local test of: create_MS_interface_nodes.py **\n'
    from numarray import *
    from Timba.Contrib.JEN import MG_JEN_exec
    ns = NodeScope()
    scope = 'create_MS_interface_nodes()'
    
    if 1:
       stations = range(0,14)
       stations = range(2,14)
       stations = range(0,12)
       stations = [3,4,5,8,9,13]
       rr = create_MS_interface_nodes(ns, stations=stations, sep9A=72)
       MG_JEN_exec.display_object(rr, 'rr', scope, full=True)
       # MG_JEN_exec.display_subtree(ns[rr.rxyz[rr.ifr_keys[0]]], 'ns[rr.rxyz[rr.ifr_keys[0]]]', full=True)
       # MG_JEN_exec.display_subtree(ns[rr.ruvw[rr.ifr_keys[0]]], 'ns[rr.ruvw[rr.ifr_keys[0]]]', full=True)
       # MG_JEN_exec.display_subtree(ns[rr.xyz[rr.station_keys[1]]], 'ns[rr.xyz[rr.station_keys[1]]]', full=True)
       # MG_JEN_exec.display_subtree(ns[rr.uvw[rr.station_keys[1]]], 'ns[rr.uvw[rr.station_keys[1]]]', full=True)
       for key in rr.dcoll.keys():
          MG_JEN_exec.display_subtree(ns[rr.dcoll[key]], 'ns[rr.dcoll['+key+']', full=True)
          pass

    print '\n*******************\n** End of local test of: create_MS_interface_nodes.py **\n'

#============================================================================================

