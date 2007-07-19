# file: ../JEN/util/plotresiduals.py

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

import fileinput
from numarray import *

k = 0
data = []
nsamp = 0
for line in fileinput.input('debug_S0.ext'):
    k += 1
    print '\n**',k,':',line
    ss = line.split(' ')
    n1 = int(ss[0])
    ss = ss[1:]
    nss = len(ss)
    print n1,nss,nss/n1,':'
    if k==1:
        nc = n1
        cc = []
        for i in range(nss):
            if not ss[i]=='':
                # print '- float(',ss[i],') =',float(ss[i])
                s = ss[i].split('\n')
                cc.append(s[0])
        print 'nc=',nc,':',len(cc),cc
    elif nss==nc*4:
        nsamp += 1
        for i in range(nss):
            data.append(float(ss[i]))
        print '--',k,nsamp,len(data)

vv = array(data)
print dir(vv)
vv.resize(n1,nc,4)
print shape(vv)
print '\n ** vv[0,:,0]','\n',vv[0,:,0]
print '\n ** vv[:,0,0]','\n',vv[:,0,0]
print '\n ** vv[0,0,:]','\n',vv[0,0,:]


