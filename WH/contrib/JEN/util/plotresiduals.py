# file: ../JEN/util/plotresiduals.py

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


