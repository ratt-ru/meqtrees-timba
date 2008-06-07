# file: ../JEN/demo/EasyTwig.py:
#
# Author: J.E.Noordam
#
# Short description:
#    Utility functions for making little subtrees (twigs)
#    and unique nodestubs/nodenames.
#
# History:
#   - 07 june 2008: creation (from EasyTwig.py)
#
# Remarks:
#
# Description:
#


 
#********************************************************************************
# Initialisation:
#********************************************************************************

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

Settings.forest_state.cache_policy = 100
Settings.forest_state.bookmarks = []

import Meow.Bookmarks
from Timba.Contrib.JEN.util import JEN_bookmarks

# import copy
import math
# import random




#===============================================================================
# Test forest:
#===============================================================================

def _define_forest (ns, **kwargs):
    """Just for testing the various utility functions"""

    trace = False
    # trace = True
    cc = []
    
    twigs = []
    for name in twig_names(trace=trace):
        twigs.append(twig(ns,name))

    names = []
    names = ['polynomialf3t2']
    for name in names:
        twigs.append(twig(ns,name))

    twig_bundle = ns.twig_bundle << Meq.Composer(*twigs)
    cc.append(twig_bundle)
    JEN_bookmarks.create(twigs)

    ns.rootnode << Meq.Composer(*cc)

    # Finished:
    return True

#------------------------------------------------------------------------------------

def _test_forest (mqs,parent,wait=False):
  from Timba.Meq import meq
  nf2 = 10
  nt2 = 5
  cells = meq.cells(meq.domain(-nf2,nf2,-nt2,nt2),
                    num_freq=2*nf2+1,num_time=2*nt2+1);
  print '\n-- cells =',cells,'\n'
  request = meq.request(cells,rqtype='e1');
  a = mqs.meq('Node.Execute',record(name='rootnode',request=request),wait=wait)
  return True




#====================================================================================
# Functions for (unique) nodename/stub generation:
#====================================================================================

def nodename (ns, rootname, *quals, **kwquals):
    """
    Helper function that forms a nodename from the given rootname and
    list (*) and keyword (**) qualifiers.
    """
    stub = nodestub (ns, rootname, *quals, **kwquals)
    return stub.name

#-------------------------------------------------------------------------

def unique_name (ns, rootname, *quals, **kwquals):
    """
    Helper function that forms a unique nodename from the given rootname and
    list (*) and keyword (**) qualifiers.
    """
    stub = unique_stub (ns, rootname, *quals, **kwquals)
    return stub.name

#-------------------------------------------------------------------------

def nodestub (ns, rootname, *quals, **kwquals):
    """
    Helper function that forms a nodestub from the given rootname and
    list (*) and keyword (**) qualifiers.
    """
    stub = ns[rootname]
    if len(quals)>0:
        stub = stub(*quals)
    if len(kwquals)>0:
        stub = stub(**kwquals)

    if False:
        s = '** QR.nodestub('+str(rootname)+','+str(quals)+','+str(kwquals)+')'
        s += ' -> '+str(stub)
        print s
    return stub

#-------------------------------------------------------------------------

def unique_stub (ns, rootname, *quals, **kwquals):
    """Helper function that forms a unique (i.e. uninitialized) nodestub
    from the given information.
    NB: Checking whether the proposed node has already been initialized
    in the given nodescope (ns) may be not an entirely safe method,
    when using unqualified nodes....
    """
    # First make a nodestub:
    stub = nodestub(ns, rootname, *quals, **kwquals)

    # Decode the uniquifying parameter (see below):
    ss = rootname.split('|')
    n = 0
    nameroot = rootname
    if len(ss)==3:                       # assume: <nameroot>|<n>|
        n = int(ss[1])
        nameroot = ss[0]

    # Safety valve:
    if n>100:
        print s1
        raise ValueError,'** max of uniqueness parameter exceeded'

    # Testing:
    if False:
        if n<3:
            stub << n               
        s = (n*'--')+' initialized: '
        s += ' '+str(stub.initialized())            # the correct way
        s += ' '+str(ns[stub].initialized())        # .....?
        s += ' '+str(ns[stub.name].initialized())   # .....
        print s

    # Check whether the node already exists (i.e. initialized...):
    if stub.initialized():
        # Recursive: Try again with a modified rootname.
        # (using the incremented uniquifying parameter n)
        newname = nameroot+'|'+str(n+1)+'|'
        return unique_stub(ns, newname, *quals, **kwquals)

    # Return the unique (!) nodestub:
    return stub
   


#====================================================================================
# Functions dealing with finding nodes in a tree:
#====================================================================================

def find_parms (tree, trace=False):
    """Get a list of all the MeqParm nodes in the given tree"""
    return find_nodes (tree, meqtype='MeqParm', trace=trace)


def find_nodes (tree, meqtype='MeqParm', level=0, trace=False):
    """Get a list of nodes of the specified type from the given tree.
    """
    prefix = level*'..'
    if level==0:
        if trace:
            s1 = '** .find_nodes('+str(tree)+','+meqtype+'):'
    nn = []
    if getattr(tree,'children', None):
        for child in tree.children:
            c1 = child[1]
            if c1.classname==meqtype:
                nn.append(c1)
            nn.extend(find_nodes(c1, meqtype=meqtype, level=level+1, trace=trace))
    if level==0:
        if trace:
            print prefix,s1,'found',len(nn),'nodes'
            for i,n in enumerate(nn):
                print '   -',i,':',str(n)
            print
    return nn
    


#====================================================================================
# Functions dealing with standard input twigs:
#====================================================================================

def twig_names (cat='default', include=None, first=None, trace=False):
    """Return a group (category) of valid twig names"""
    if cat=='all':
        names = []
    elif cat=='noise':
        names = ['noise1','noise3','noise5']
    else:                                      # default category
        names = ['f','t','f+t','ft','f**2','gaussian_ft','noise3','cxft']

    # Specific names may be included:
    if isinstance(include,str):
        include = [include]
    if isinstance(include, (list,tuple)):
        names.extend(include)

    # A specific name may be put first (the default):
    if isinstance(first, str):
        if first in names:
            names.remove(first)
        names.insert(0,first)
        
    if trace:
        print '** EasyTwig.twig_names(',cat,include,' first=',first,'):',names
    return names

#-----------------------------------------------------------------------------------

def twig(ns, name, test=False, trace=False):
    """Return a standard (name) subtree (a twig), to be used as input for
    demonstrations in QR_... nodules.
    Reuse if it exists already. Create it if necessary.
    If test=True, just test whether the name is recognized.... 
    """
    recognized_axes = ['f','t','L','M']    
    s1 = '** EasyTwig.twig('+str(name)+', test='+str(test)+'):'

    # print s1,name.split('pow')

    # Derive and condition the nodename:
    nodename = name
    nodename = nodename.replace('.',',')    # avoid dots (.) in the nodename

    # Check whether the node already exists (i.e. is initialized...)
    stub = nodestub(ns, nodename)
    node = None
    if stub.initialized():                  # node already exists
        node = stub                         # return it

    elif name in ['zero']:
        node = stub << Meq.Constant(0.0)
    elif name in ['one','unity']:
        node = stub << Meq.Constant(1.0)

    elif name in ['f','freq','MeqFreq']:
        node = stub << Meq.Freq()
    elif name in ['t','time','MeqTime']:
        node = stub << Meq.Time()
    elif name in ['l','L','MeqL']:
        node = stub << Meq.Grid(axis='L')
    elif name in ['m','M','MeqM']:
        node = stub << Meq.Grid(axis='M')
        
    elif name in ['nf']:
        node = stub << Meq.NElements(twig(ns,'f'))
    elif name in ['nt']:
        node = stub << Meq.NElements(twig(ns,'t'))
    elif name in ['nft']:
        node = stub << Meq.NElements(twig(ns,'ft'))
       
    elif name in ['f+t','t+f']:
        node = stub << Meq.Add(twig(ns,'f'),twig(ns,'t'))
    elif name in ['f+t+L+M']:
        node = stub << Meq.Identity(twig(ns,'sumftLM'))

    elif name in ['tf','ft','f*t','t*f']:
        node = stub << Meq.Multiply(twig(ns,'f'),twig(ns,'t'))
    elif name in ['LM','ML','L*M','M*L']:
        node = stub << Meq.Multiply(twig(ns,'L'),twig(ns,'M'))
    elif name in ['f*t*L*M']:
        node = stub << Meq.Identity(twig(ns,'prodftLM'))
    elif name in ['ftLM','ftL','ftM','fLM','tLM']:
        node = stub << Meq.Identity(twig(ns,'prod'+name))

    elif name in ['cft','cxft']:
        node = stub << Meq.ToComplex(twig(ns,'f'),twig(ns,'t'))
    elif name in ['ctf','cxtf']:
        node = stub << Meq.ToComplex(twig(ns,'t'),twig(ns,'f'))
    elif name in ['cLM','cxLM']:
        node = stub << Meq.ToComplex(twig(ns,'L'),twig(ns,'M'))
        
    elif name in ['f2','f**2']:
        node = stub << Meq.Sqr(twig(ns,'f'))
    elif name in ['t2','t**2']:
        node = stub << Meq.Sqr(twig(ns,'t'))
    elif name in ['L2','L**2']:
        node = stub << Meq.Sqr(twig(ns,'L'))
    elif name in ['M2','M**2']:
        node = stub << Meq.Sqr(twig(ns,'M'))

    elif name in ['f2+t2','t2+f2']:
        node = stub << Meq.Identity(twig(ns,'sumf2t2'))
        
    elif name in ['f**t']:
        node = stub << Meq.Pow(twig(ns,'f'),twig(ns,'t'))
    elif name in ['t**f']:
        node = stub << Meq.Pow(twig(ns,'t'),twig(ns,'f'))

    elif len(name.split('expnoise'))>1:               # e.g. 'expnoise2.5'
        ss = name.split('expnoise')[1]
        node = stub << Meq.Exp(twig(ns,'noise'+ss))

    elif len(name.split('gaussian'))>1:               # e.g. 'gaussianft'
        ss = name.split('gaussian')[1]
        for s in recognized_axes:
            ss = ss.replace(s,s+'2')                  # e.g. ft -> f2t2 
        node = stub << Meq.Exp(Meq.Negate(twig(ns,'sum'+ss)))

    elif len(name.split('expnegsum'))>1:              # e.g. 'expnegsumf0t1L2M'
        ss = name.split('expnegsum')[1]
        node = stub << Meq.Exp(Meq.Negate(twig(ns,'sum'+ss)))

    #.....................................................................
    # do these last (their short names might be subsets of other names...)
    #.....................................................................

    elif len(name.split('range'))>1:                  # e.g. 'range4' 
        ss = name.split('range')
        node = stub << Meq.Constant(range(int(ss[1])))

    elif len(name.split('noise'))>1:                  # e.g. 'noise2.5'
        ss = name.split('noise')[1]
        node = stub << Meq.GaussNoise(stddev=float(ss))

    elif len(name.split('prod'))>1:                   # e.g. 'prodf0t1L2M'
        ss = name.split('prod')[1]
        node = combine_ftLM(ns, stub, ss, default=1.0, meqclass='Multiply') 

    elif len(name.split('sum'))>1:                    # e.g. 'sumf0t1L2M'
        ss = name.split('sum')[1]
        node = combine_ftLM(ns, stub, ss, default=0.0, meqclass='Add') 

    elif len(name.split('pow'))==2:                   # e.g. 'fpow3'
        ss = name.split('pow')
        if ss[0] in recognized_axes:     
            node = twig(ns,ss[0])
            if ss[1] in '2345678':                    # MeqPow2 ... MeqPow8 
                node = stub << getattr(Meq,'Pow'+ss[1])(node)
                
    #............................................................
    if node==None:
        if test:                                               # testing mode
            return False                                       # False: name is invalid ....
        # Otherwise, always return an initialized node:
        node = stub << Meq.Constant(0.123456789)               # a safe (?) number
        s1 += '                ** (name not recognized!) **'
        trace = True

    if trace:
        s1 += ' -> '+str(node)
        # print dir(node)
        if getattr(node,'children', None):
            cc = node.children
            for c in cc:
                s1 += '  '+str(c[1])
        print s1

    if test:                                                  # testing mode
        return True                                           # True: name is valid (recognized)

    # Return the (root)node of the twig:
    return node                        

#----------------------------------------------------------------

def combine_ftLM(ns, stub, ss, default=0.0, meqclass='Multiply'):
    """Combine the children in cc, using the specified meqclass"""
    vv = decode_ftLM(ss, trace=True)
    cc = []
    for key in vv.keys():
        power = vv[key]
        if key=='c':                              # constant (float)
            cc.append(ns << vv[key])           
        elif power==1:                            # linear
            cc.append(twig(ns,key))
        elif power>1:                             # ignore power<0
            cc.append(twig(ns,key+'pow'+str(power)))
    if len(cc)==0:
        node = stub << Meq.Constant(default)      # use nodename
    elif len(cc)==1:
        node = stub << Meq.Identity(cc[0])        # use nodename
    else:
        node = stub << getattr(Meq,meqclass)(*cc)      
    return node

#................................................................

def decode_ftLM (s, trace=False):
    """Helper function to unravel the string (s), which is assumed
    to have the format f2t1L3M0"""
    ss = s                                       # the copy will be modified
    vv = dict()
    
    for vc in ['M','L','t','f']:                 # reverse order
        ss = ss.split(vc)
        if len(ss)==1:                           # vc not present in ss
            vv[vc] = -1
        elif ss[1]=='':                          # vc not followed by number 
            vv[vc] = 1
        else:                                    # vc followed by integer
            vv[vc] = int(ss[1])
        ss = ss[0]                               # next vc

    # Assume that the remainder is a constant (float)
    if len(ss)>0:
        vv['c'] = float(ss)

    if trace:
        print '\n** .decode_ftLM(',s,') ->',vv,'  (ss=',ss,' len=',len(ss),')'
    return vv

#----------------------------------------------------------------

def polynomial (ns, name='polynomial', fdeg=2, tdeg=3, full=False, trace=False):
    """Make a polynomial subtree"""
    if trace:
        print '\n** polynomial(',name,fdeg,tdeg,'):'
    # Make the polynomial terms (nodes):
    cc = []
    ftmax = max(fdeg+1,tdeg+1)           # defines bottom-right corner
    for f in range(fdeg+1):
        for t in range(tdeg+1):
            if full or (f+t)<ftmax:
                parmstub = unique_stub(ns,'parm',f,t)
                parm = parmstub << Meq.Parm(0)
                if f==0 and t==0:
                    cc.append(parm)
                else:
                    prodft = twig(ns,'prod'+'f'+str(f)+'t'+str(t), trace=trace)
                    cc.append(ns.term(f,t) << Meq.Multiply(parm,prodft))
    # Add all the terms together:
    nodestub = unique_stub(ns, name+'f'+str(fdeg)+'t'+str(tdeg))
    # nodestub = unique_stub(ns, name, fdeg=fdeg, tdeg=tdeg)
    node = nodestub << Meq.Add(*cc)
    if trace:
        print '   ->',str(node),len(node.children),'terms\n'
    return node




#=====================================================================================
# Standalone test (without the browser):
#=====================================================================================

if __name__ == '__main__':

   print '\n** Start of standalone test of: EasyTwig.py:\n' 
   ns = NodeScope()

      
   if 0:
       twig_names(trace=True)

   if 1:
       names = twig_names()
       names = ['fpow3','tpow6']
       names.extend(['prodf3t1','prodf3L1M','prod3.56'])
       names.extend(['sumf3t1','sum-6f3L1M','sum3.56'])
       names.extend(['f+t','f2','f**2','ft'])
       names.extend(['gaussianft','gaussian'])
       names.extend(['expnoise4','expnegsum-2fLM3'])
       for name in names:
           twig(ns, name, trace=True)
           
   if 0:
       twig(ns, 'f', trace=True)
       twig(ns, 'ft', trace=True)
       twig(ns, 'f**t', trace=True)
       twig(ns, 't**f', trace=True)
       twig(ns, 'f+t', trace=True)
       twig(ns, 'range3', trace=True)
       twig(ns, 'noise3.5', trace=True)
       twig(ns, 'dummy', trace=True)

   if 0:
       twig = polynomial(ns, trace=True)
       nn = find_parms(twig, trace=True)

   #------------------------------------------------

   if 0:
       decode_ftLM('f3t4L5M6', trace=True)
       decode_ftLM('ft4L5M6', trace=True)
       decode_ftLM('fL5M6', trace=True)
       decode_ftLM('L', trace=True)
       decode_ftLM('LM', trace=True)
       decode_ftLM('L0M', trace=True)
       decode_ftLM('', trace=True)
       decode_ftLM('3.6fL5M6', trace=True)
       # decode_ftLM('ML', trace=True)    # wrong order: error


   #------------------------------------------------

   if 0:
      stub = nodestub(ns,'xxx',5,-7,c=8,h=9)
      print '\n nodestub() ->',str(stub),type(stub)
      stub << 5.6
      stub = unique_stub(ns,'xxx',5,-7,c=8,h=9)
      print '\n unique_stub() ->',str(stub),type(stub)
      if 0:
         if 1:
            print '\n dir(stub):',dir(stub),'\n'
         print '- stub.name:',stub.name
         print '- stub.basename:',stub.basename
         print '- stub.classname:',stub.classname
         print '- stub.quals:',stub.quals
         print '- stub.kwquals:',stub.kwquals
         print '- stub.initialized():',stub.initialized()
      if 0:
         node = stub << 3.4
         print '\n node = stub << 3.4   ->',str(node),type(node)
         if 1:
            print '\n dir(node):',dir(node),'\n'
         print '- node.name:',node.name
         print '- node.basename:',node.basename
         print '- node.classname:',node.classname
         print '- node.quals:',node.quals
         print '- node.kwquals:',node.kwquals
         print '- node.initialized():',node.initialized()

      if 1:
         print '.nodename() ->',nodename(ns,'xxx',5,-7,c=8,h=9)
         print '.unique_name() ->',unique_name(ns,'xxx',5,-7,c=8,h=9)

   print '\n** End of standalone test of: EasyTwig.py:\n' 

#=====================================================================================



