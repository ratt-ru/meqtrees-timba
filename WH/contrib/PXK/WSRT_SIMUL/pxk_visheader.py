#!/usr/bin/python
# Updates various nodes in the tree based on the visibility
# header. Uses the naming convetion from Contrib.OMS

# History:
# - 2006.10.31: creation
# - 2006.11.13: added function 'print_relative_ant_pos'
# - 2006.11.14: added printing MS info from header
# - 2006.11.27: improved printing MS info


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

from Timba.meqkernel import set_state
from math import sqrt


def process_vis_header (hdr):
    """handler for the visheader""";


    # phase center
    (ra0,dec0) = hdr.phase_ref;
    try:
        set_state('ra',value=ra0);
        set_state('dec',value=dec0);
        pass
    except: pass;

    print ''
    print '[pxk_visheader] phase centre: ', ra0,dec0
    print '[pxk_visheader] data column : ', hdr.data_column_name
    print '[pxk_visheader] num antenna : ', hdr.num_antenna
    print '[pxk_visheader] chan incr   : ', hdr.channel_increment
    print '[pxk_visheader] chan start  : ', hdr.channel_start_index
    print '[pxk_visheader] chanwidth[0]: ', hdr.channel_width[0]
    print '[pxk_visheader] cwd         : ', hdr.cwd
    print '[pxk_visheader] data type   : ', hdr.data_type
    print '[pxk_visheader] data shape  : ', hdr.original_data_shape
    print '[pxk_visheader] correlations: ', hdr.corr
    print '[pxk_visheader] ms_name     : ', hdr.ms_name

    # antenna positions
    antpos  = []
    pos     = hdr.antenna_pos;
    if pos.rank != 2 or pos.shape[0] != 3:
        raise ValueError,'incorrectly shaped antenna_pos';
    
    nant   = pos.shape[1];
    coords = ('x','y','z');
    for iant in range(nant):
        sn          = str(iant+1);
        this_antpos = [iant, []]
        
        # since some antennas may be missing from the tree, ignore errors
        try:
            for (j,label) in enumerate(coords):
                #print '[pxk_visheader] ',label+':'+sn, 'value = ',pos[j,iant]
                this_antpos[1].append(pos[j,iant]) # antenna positions
                set_state(label+':'+sn,value=pos[j,iant]);
                pass
            antpos.append(this_antpos)
            pass
        except: pass;
        pass
    
    # array reference position
    try:
        for (j,label) in enumerate(coords):
            set_state(label+'0',value=pos[j,0]);
            pass
        pass
    except: pass;
    
    # time extent
    (t0,t1) = hdr.time_extent;
    print '[pxk_visheader] time extent : ',t0,t1;
    try:
        set_state('time0',value=t0);
        set_state('time1',value=t1);
        pass
    except: pass;
    
    # freq range
    f0,f1 = hdr.channel_freq[0],hdr.channel_freq[-1];
    print '[pxk_visheader] freq range  : ',f0,f1;
    try:
        set_state('freq0',value=f0);
        set_state('freq1',value=f1);
        pass
    except: pass;
    
    # number of channels
    num_channels = len(hdr.channel_freq)
    print '[pxk_visheader] num_channels: ',num_channels;
    try:
        set_state('num_channels', value=float(num_channels));
        pass
    except: pass;
    
    # print antenna positions
    print_relative_ant_pos (antpos)
    pass


def print_relative_ant_pos(ant_pos=[[0,[0,0,0]]]):
    """ Print relative antenna positions """
    #for ant in ant_pos: print ant; pass

    rel_ant_pos = []
    rel_dist    = []
    print "\n ant      rel_x      rel_y      rel_z   ",
    print "rel_dist  incr (m)\n"
    for ant in range(len(ant_pos)):
        rel_ant_pos.append([])
        rel_ant_pos[ant].append(ant_pos[ant][0])
        # relative positions
        for i in range(3):
            rel_ant_pos[ant].append(ant_pos[ant][1][i] - ant_pos[0][1][i])
            pass
        rel_ant_pos[ant].append(
            sqrt(sum([i**2 for i in rel_ant_pos[ant][1:4]])) )
        print "%4i %10.3f %10.3f %10.3f   %9.3f   %7.0f" % (
            rel_ant_pos[ant][0] + 1, 
            rel_ant_pos[ant][1], 
            rel_ant_pos[ant][2], 
            rel_ant_pos[ant][3], 
            rel_ant_pos[ant][4],
            (rel_ant_pos[ant][4] - rel_ant_pos[max(ant-1,0)][4])
            )
        pass
    pass
