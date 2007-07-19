## LAST EDIT: 2005.12.23   # Is values always [x][2][2] ??

#import numarray as newName
#from numarray import *
#from Numeric  import *
#from string   import *
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

from   pylab        import *
from   getParmTable import *
import os




## FUNCTIONS ################################################################
def getValues(TABLE, KEY):
    # check if KEY exists; if so return values
    if not TABLE.has_key(KEY):
        print "NO KEY NAMED", "'", KEY, "'"
        sys.exit()
        pass
    else:
        return TABLE[KEY]
    pass

def PLOT(x, y, style='b',col=[0,0,1],
         fig=None, subx=1,suby=1,subn=1,
         xlab='', ylab='', t='', leg='', lab=None):
    figure(fig)
    subplot(subx,suby,subn, axisbg=(1.0, 1.0, 1.0));
    line = plot(x, y, style, label=lab)
    #setp(line, 'markerfacecolor', 'orange')
    #setp(line, linewidth=2, color='r')
    #setp(line, linewidth=2, color=col)
    
    xlabel(xlab); ylabel(ylab); title(t)
    if leg!='': legend((leg, ''), 'upper right', shadow=False)

    grid(True)
    pass

def subTable(TABLE, indices):
    # create sub table
    len_table       = len(TABLE[TABLE.keys()[0]])
    keys            = TABLE.keys()
    KEYS            = [[col,[]] for col in keys]
    SUB_TABLE       = dict(KEYS);

    # fill sub table
    for row in indices:
        for col in range(len(keys)):
            SUB_TABLE[keys[col]].append(TABLE[keys[col]][row])
            pass
        pass

    # If KEY is list of arrays/lists, then make array of arrays/lists
    for key in keys:
        if type(SUB_TABLE[key][0]) == numarraycore.NumArray or \
               type(SUB_TABLE[key][0]) == types.ListType:
            SUB_TABLE[key] = array(SUB_TABLE[key])
            pass
        pass
    
    return SUB_TABLE

def sliceTable(TABLE, num_skip=4):
    # return polarizations of TABLE (i.e. XXreal, XXimag, YYreal, YYimag)
    len_table   = len(TABLE[TABLE.keys()[0]])
    SLICE_TABLE = [subTable(TABLE, arange(0,len_table, num_skip)+i) \
                   for i in range(num_skip)]
    return SLICE_TABLE

def getAxes(R):
    # returns the length of each axis, in an array
    if size(R)>1:
        DIM = []
        while size(R)>1:
            DIM.append(len(R))
            R   = R[0]
            pass
        pass
    else:
        DIM = [R]
        pass
    return DIM

def multiFor(L, iter):
    # loop over all axes of L, except for the last one
    for i in range(L[iter]):
        if iter < len(L)-2:  # skip last and current
            multiFor(L, iter+1)
            print "L[",iter,"]:", L[iter], "  i:", i
            pass
        pass
    pass

def getValuesArray(TABLE, KEY):
    # Function puts all values from KEY in new Array of dimension 1
    all_values  = getValues(TABLE, KEY)
    ax          = getAxes(all_values)
    ax.reverse()
    len_ax      = len(ax)
    #multiFor(ax, 0)

    values  = []
    if   len_ax == 1:        # 1 array with values
        return all_values, ax
    elif len_ax == 2:
        for i in range(ax[0]):
            values.append(all_values[:,i])
            pass
        pass
    elif len_ax == 3:        # 2 arrays with values
        for i in range(ax[0]):
            for j in range(ax[1]):
                values.append(all_values[:,i,j])
                pass
            pass
        pass
    elif len_ax == 4:        # 3 arrays with values
        for i in range(ax[0]):
            for j in range(ax[1]):
                for k in range(ax[2]):
                    values.append(all_values[:,i,j,k])
                    pass
                pass
            pass
        pass
    #AX = ax
    return values, ax

def RGB(R, G, B):
    RGB_str = '#'
    RGB_str +=str(994400)
    print RGB_str
    #return RGB_str
    return '#ff3366'



## MAIN #####################################################################
NAME            = "A963.mep.dat"
TABLE           = getTable(NAME, 1)


# create polarization tables, XXreal, XXimag, YYreal, YYimag
POL_TABLE       = sliceTable(TABLE,4)
[XXreal,ax]     = getValuesArray(POL_TABLE[0], 'VALUES')
[XXimag,ax]     = getValuesArray(POL_TABLE[1], 'VALUES')
[YYreal,ax]     = getValuesArray(POL_TABLE[2], 'VALUES')
[YYimag,ax]     = getValuesArray(POL_TABLE[3], 'VALUES')


# Plotting etc.
x_axis          = range(len(XXreal[0]))
t               = []
for i in range(len(XXreal)):
    xlab    = 'all baselines, all timesteps'
    t.append('polc[' + str(i) + ']')
    COL     = ['r','g','b','y']
    PLOT(x=x_axis, y=XXreal[i], style=COL[i%len(COL)],col=[0,0,0],
         fig=1, subx=ax[0],suby=ax[1],subn=1+i,
         xlab=xlab, ylab='XXreal', t=t[i]);
    legend((t[i], ''), 'upper right')
    pass

subplots_adjust(wspace=0.3, hspace=0.4)
savefig('test_001.png')
show()


# Next step : put data in classes, and create adaptable
# plotting routines
