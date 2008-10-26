# file: ../JEN/demo/EasyBundle.py:
#
# Author: J.E.Noordam
#
# Short description:
#    Utility functions for making bundles of subtrees (twigs)
#
# History:
#   - 02 jul 2008: creation (from EasyTwig.py)
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

from Timba.Contrib.JEN.Easy import EasyNode as EN
from Timba.Contrib.JEN.Easy import EasyTwig as ET
from Timba.Contrib.JEN.Easy import EasyFormat as EF

import copy
import math
import random




#===============================================================================
# Test forest:
#===============================================================================

def _define_forest (ns, **kwargs):
    """Just for testing the various utility functions"""

    trace = False
    # trace = True
    cc = []

    # Standard bundle categories:
    for cat in bundle_cats():
        bundles = []
        print '\n\n****** bundle_cat =',cat
        for name in bundle_names(cat):
            t = bundle(ns, name, trace=trace)
            JEN_bookmarks.create(t, page=name, folder=cat, recurse=2)
            bundles.append(t)
        cc.append(ns[cat] << Meq.Composer(*bundles))
        JEN_bookmarks.create(bundles, cat, folder='bundle_categoriess')

    # Some extra bundles:
    names = []
    # names = ['polyparm_f3t2']
    for name in names:
        t = bundle(ns,name)
        cc.append(t)
        JEN_bookmarks.create(t, page=name, recurse=2)

    # Finished:
    ns.rootnode << Meq.Composer(*cc)
    EN.bundle_orphans(ns)
    return True

#------------------------------------------------------------------------------------

def _tdl_job_execute_1D_f (mqs,parent,wait=False):
  from Timba.Meq import meq
  cells = meq.cells(meq.domain(0.1,2,-1,1),             # f1,f2,t1,t2
                    num_freq=50,num_time=1);
  request = make_request(cells)
  mqs.meq('Node.Execute',record(name='rootnode',request=request),wait=wait)
  return True

#------------------------------------------------------------------------------------

def _tdl_job_execute_2D_ft (mqs,parent,wait=False):
  from Timba.Meq import meq
  cells = meq.cells(meq.domain(0.001,2,-2,2),             # f1,f2,t1,t2
                    num_freq=20,num_time=11)
  request = make_request(cells)
  mqs.meq('Node.Execute',record(name='rootnode',request=request),wait=wait)
  return True

#------------------------------------------------------------------------------------

def _tdl_job_execute_3D_XYZ (mqs,parent,wait=False):
  from Timba.Meq import meq
  dd = record(X=(-1,1), Y=(-2,2), Z=(-3,3))
  cc = record(num_X=11, num_Y=12, num_Z=13)
  cells = meq.gen_cells(meq.gen_domain(**dd), **cc) 
  request = make_request(cells)
  mqs.meq('Node.Execute',record(name='rootnode',request=request),wait=wait)
  return True

#------------------------------------------------------------------------------------

def _tdl_job_execute_4D_ftLM (mqs,parent,wait=False):
  from Timba.Meq import meq
  dd = record(freq=(0.01,2), time=(-2,2), L=(-1,1), M=(-1,1))
  cc = record(num_freq=20, num_time=21, num_L=11, num_M=11)
  cells = meq.gen_cells(meq.gen_domain(**dd), **cc) 
  request = make_request(cells)
  mqs.meq('Node.Execute',record(name='rootnode',request=request),wait=wait)
  return True

#------------------------------------------------------------------------------------

def _tdl_job_execute_5D_ftXYZ (mqs,parent,wait=False):
  from Timba.Meq import meq
  dd = record(freq=(0.01,2), time=(-2,2), X=(-1,1), Y=(-2,2), Z=(-3,3))
  cc = record(num_freq=20, num_time=21, num_X=11, num_Y=12, num_Z=13)
  cells = meq.gen_cells(meq.gen_domain(**dd), **cc) 
  request = make_request(cells)
  mqs.meq('Node.Execute',record(name='rootnode',request=request),wait=wait)
  return True

#------------------------------------------------------------------------------------

request_counter = 0

def make_request (cells, rqtype=None):
    """Make a request"""
    global request_counter
    request_counter += 1
    rqid = meq.requestid(request_counter)
    return meq.request(cells, rqid=rqid)



#====================================================================================
# Misc helper fuctions:
#====================================================================================




#====================================================================================
# Functions dealing with standard input bundles:
#====================================================================================

def bundle_cats (trace=False):
    """Return a list of bundle categories"""
    cats = []
    cats.extend(['cloud'])
    # cats.extend([])
    return cats

#-----------------------------------------------------------------------------------

def bundle_names (cat='default', include=None, first=None, trace=False):
    """Return a group (category, cat) of valid bundle names"""

    names = []
    
    if isinstance(cat,(list,tuple)):
        # The specified cat may be a list of categories: just concatenate.
        for cat1 in cat:
            names.extend(bundle_names(cat1))

    elif cat=='cloud':
        names = ['cloud_n6s4','cloud_a2p3','cloud_r2m-1+3j']

    elif cat=='all':
        names = bundle_names(bundle_cats())
    else:
        # default category
        names = ['cloud_n6s4']

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

    # Avoid doubles:
    names = ET.unique_list(names)
        
    if trace:
        print '** EasyBundle.bundle_names(',cat,include,' first=',first,'):',names
    return names


#-----------------------------------------------------------------------------------

def bundle (ns, spec,
            n=-1, noise=0.0, stddev=0.0,
            nodename=None, quals=None, kwquals=None,
            help=None, shape=None, unop=None, parent=None,
            severe=False, trace=False):
    """
    Return a bundle of nodes (subtrees), specified by the argument 'spec'.
    Normally, this will be a list of nodes (unless a parent is specified, see below).

    <code_lines>
    import EasyBundle as EB
    [nodes] = EB.bundle (ns, spec,
    nodestub=None,
    nodename=None, quals=None, kwquals=None,
    unop=None, stddev=0.0, noise=0.0,
    parent=None,
    severe=True)
    </code_lines>

    Mandatory arguments:
    <li> ns: nodescop
    <li> spec: twig specification string (see below)

    Optional arguments:
    <li> n[=-1]: If n>1, spec is used to generate a bundle of n twigs (see EasyTwig.py) 
    <li> nodestub[=None]: If specified, used for all twig nodes
    <li> nodename[=None]: If not specified, a default name will be made (from spec etc)
    <li> quals[=None]: If a list, used to qualify nodename
    <li> kwquals[=None]: If a dict, used to qualify nodename
    <li> unop=[None]: If specified (e.g. 'Cos', or ['Cos','Sin'], apply to the final bundle nodes.
    <li> stddev[=0.0]: If >0, add a gaussian offset (MeqConstant) to the final twig node.
    <li> noise[=0.0]: If >0, add gaussian noise (MeqGaussNoise) to the final twig node.
    <li> parent[=None]: if specified (e.g. 'Composer'), return a single parent node.
    <li> severe[=True]: If True, give an error if spec not recognized (otherwise return a Constant node)

    The following forms of 'spec' (string) are recognized:  
    <li> cloud_n5s2m-4  :  cloud of n=5 MeqConstant nodes, with stddev (s) and mean (m) 

    """
    recognized_axes = ['f','t','L','M']       # used below...

    s1 = '--- EasyBundle.bundle('+str(spec)
    if n>0: s1 += ', '+str(n)+'twigs'
    if nodename: s1 += ', '+str(nodename)
    if quals: s1 += ', quals='+str(quals)
    if kwquals: s1 += ', kwquals='+str(kwquals)
    s1 += '):  '

    cc = None

    #....................................................................

    if n>0:
        # If n>0, make a bundle of twigs, using spec:
        cc = []
        for i in range(n):
            qq = EN.append2quals(i, quals)
            node = ET.twig(ns, spec,
                           noise=noise, stddev=stddev,
                           nodename=nodename, quals=qq, kwquals=kwquals,
                           severe=severe, trace=trace)
            cc.append(node)
                

    elif len(spec.split('cloud_'))>1:                                # e.g. 'cloud_s3'
        # Make a 'cloud' of values with random distribution:
        ss = spec.split('cloud_')[1]
        cc = cloud(ns, ss, nodename=nodename, trace=False)

    #............................................................

    if not cc:
        # Problem: no nodes in cc.
        if True or severe:
            s = '** bundle spec not recognized: '+str(spec)
            raise ValueError,s

    #............................................................

    if unop:
        # Optional: apply unary operation(s) on all nodes in cc:
        cc = apply_unop(ns, cc, unop, trace=False)

    #............................................................

    if parent:
        # If parent specified (e.g. 'Composer'), return a single parent node:
        if not isinstance(nodename,str):
            nodename = 'bundle'
            nodename += '_'+str(spec)
        stub = EN.unique_stub(ns, nodename, quals=quals, kwquals=kwquals)
        if isinstance(unop,(list,tuple)):
            stub = stub(*unop)
        else:
            stub = stub(unop)
        node = stub << getattr(Meq,parent)(*cc)
        if trace:
            print '\n**',s1,'->',str(node)
            print EN.format_tree(node, full=True)
        return node

    else:
        # Return the bundle (list of nodes):
        if trace:
            print '\n**',s1,'->',len(cc),' cc[0]=',str(cc[0])
            print EN.format_tree(cc, full=True)
        return cc                        




#-----------------------------------------------------------------------------------

def vis22 (ns, IQUV='Q0.1', nuv=10, L=0.0, M=0.0,
           urms=1.0, vrms=1.0, pzd=0.0, polrep='linear',
           nodename=None, quals=None, kwquals=None,
           parent=None, help=None, unop=None, trace=False):
    """
    Make a bundle of 2x2 cohaerency matrices.
    """
    if trace:
        print '\n** EB.vis22(',IQUV,nuv,L,M,urms,vrms,'):'
    coh = ET.cpscoh (ns, name='cpscoh', quals=None, kwquals=None,
                     IQUV=IQUV, polrep=polrep, trace=trace)
    stub = EN.unique_stub(ns, 'vis22')

    PZD = None
    if not pzd==0.0:
        c = math.cos(pzd)
        s = math.sin(pzd)
        PZD = stub('PZD') << Meq.Composer(1.0,complex(c,s),complex(c,-s),1.0,
                                          dims=[2,2])
        coh = stub('cpscoh*PZD') << Meq.Multiply(coh,PZD)

    cc = []
    for i in range(nuv):
        u = EF.format_value(random.gauss(0,urms), nsig=2)
        v = EF.format_value(random.gauss(0,vrms), nsig=2)
        K = ET.KuvLM (ns, uvLM='u'+str(u)+'v'+str(v)+'L'+str(L)+'M'+str(M),
                      name='K', quals=i, kwquals=None, trace=trace)
        node = stub(i) << Meq.Multiply(coh,K)
        cc.append(node)
        if trace:
            print '-',i,': u=',u,' v=',v,' K=',str(K),'->',str(node)
    orphan = stub << Meq.Composer(*cc)
    EN.orphans(orphan)
    if trace:
        print EN.format_tree(orphan, full=False)
    return cc

#-----------------------------------------------------------------------------------

def cloud (ns, spec='n3s1', nodename=None, quals=None, kwquals=None,
           parent=None, help=None, unop=None, override=None, trace=False):
    """
    <code_lines>
    import EasyBundle as EB
    node = EB.cloud(ns, spec, nodename=None, quals=None, kwquals=None,
    parent=None, help=None, unop=None)
    </code_lines>

    Generate a cloud of MeqConstant nodes, according to the specification.
    <li> n (nr of nodes) [=3]      nr of nodes in the cloud
    <li> s (stddev) [=1.0]:        real, >0
    <li> m (mean) [=0.0]:          if complex (a+bj), the result is complex
    <li> a (stddev of ampl):       if >0, use MeqPolar (default=p)
    <li> p (stddev of phase):      if >0, MeqPolar (default=a)
    <li> r (stddev of real part):  if >0, use MeqToComplex (default=i)
    <li> i (stddev of imag part):  if >0, use MeqToComplex (default=r)
    
    If a/p and r/i both specified (>0), MeqPolar (a/p) takes precedence.

    If parent is specified (e.g. 3, or [2,2]) make a tensor node.

    If parent=='noparent', return the first (and only?) node.
    """

    s = '** ET.cloud('+str(spec)+','+str(nodename)+'):'
    if trace:
        print '\n',s

    append_value = False
    if not isinstance(nodename, str):
        append_value = True
        nodename = 'cloud'
        nodename += '_'+str(spec)
    stub = EN.unique_stub(ns, nodename, quals=quals, kwquals=kwquals)

    dekey = dict(n=3, s=1.0, m=0.0, r=-1.0, i=-1.0, a=-1.0, p=-1.0)
    vv = ET.decode(spec, dekey, override=override, trace=False)
    nel = max(vv['n'],1)
    mean = vv['m']
    if isinstance(mean,complex):
        rmean = mean.real
        imean = mean.imag
    else:
        rmean = float(mean)
        imean = 0.0

    cc = []
    vsum = 0.0
    vsumsq = 0.0
    for i in range(nel):
        if vv['a']>0 or vv['p']>0:
            if vv['p']<0: vv['p'] = vv['a']
            if vv['a']<0: vv['a'] = vv['p']
            amean = abs(mean)
            pmean = math.atan2(rmean,imean)
            ampl = amean + random.gauss(0,vv['a'])
            phase = pmean + random.gauss(0,vv['p'])
            v = ampl*complex(math.cos(phase),math.sin(phase))
            
        elif vv['r']>0 or vv['i']>0:
            if vv['i']<0: vv['i'] = vv['r']
            if vv['r']<0: vv['r'] = vv['i']
            v = mean + complex(random.gauss(0,vv['r']),random.gauss(0,vv['i']))

        elif vv['s']>0:
            v = mean + random.gauss(0, vv['s'])

        else:
            s += 's, a or r should be specified (>0): '+str(spec)
            raise ValueError, s

        if nel==1:
            c = stub(EF.format_value(v)) << Meq.Constant(v)
        elif append_value:
            c = stub(i)(EF.format_value(v)) << Meq.Constant(v)
        else:
            c = stub(i) << Meq.Constant(v)

        if trace:
            print '--',i,':',v,str(c)
        cc.append(c)
        vsum += v
        vsumsq += v*v

    if False:
        # Check the statistics (testing only):
        vmean = vsum/max(1,len(cc))
        vrms = math.sqrt(vsumsq/max(1,len(cc))-(vmean*vmean))
        print ':: vmean=',vmean,' (',mean,')   vrms=',vrms
    
    if parent:
        if parent=='noparent':
            # Return the first (and only?) node:
            node = cc[0]
        else:
            # Use a parent node (e.g. Composer) to bundle the cloud nodes:
            node = stub << getattr(Meq,parent)(*cc)
        if unop:
            node = apply_unop(ns, node, unop, trace=trace)
        if trace:
            print EN.format_tree(node, full=True)
        return node

    else:
        # Finishing touches on the list (cc) of nodes:
        if unop:
            for k,c in enumerate(cc):
                cc[k] = apply_unop (ns, c, unop, trace=trace)
        # Initialize the stub anyhow, to force uniqueness.... 
        EN.orphans(stub << Meq.Composer(*cc))
        if trace:
            print EN.format_tree(cc, full=True)
        return cc

#-----------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------



#=====================================================================================
# Standalone test (without the browser):
#=====================================================================================

if __name__ == '__main__':

   print '\n** Start of standalone test of: EasyBundle.py:\n' 
   ns = NodeScope()

      
   if 0:
       quals = None
       kwquals = None
       # quals = range(3)
       cats = bundle_cats()
       cats = ['cloud']
       unop = 'Cos'
       unop = ['Cos','Sin']
       unop = None
       nodename = None
       nodename = 'pop'
       for cat in cats:
           print '\n\n\n'
           print '***************************************************************************'
           print '** bundle_cat =',cat,'  quals=',quals,'  kwquals=',kwquals,'  nodename=',nodename,'  unop=',unop
           print '***************************************************************************'
           for spec in bundle_names(cat):
               bundle(ns, spec, quals=quals, kwquals=kwquals,
                      nodename=nodename,
                      unop=unop, trace=True)

   if 1:
       cc = vis22(ns, nuv=3, pzd=1.0, trace=True)

   if 0:
       cats = ET.twig_cats()
       # cats = ['axes','complex','tensor']
       # cats = ['axes']
       for cat in cats:
           for spec in ET.twig_names(cat):
               bundle(ns, spec, n=5, trace=True)
           

   if 0:
       names = []
       names.extend(['expnoise_4','expnegsum_-2fLM3'])
       for name in names:
           bundle(ns, name, trace=True)
           
   if 0:
       cloud(ns, 'n5', 'xxx', trace=True)
       cloud(ns, 'n7', 'xxx', trace=True)
       cloud(ns, 'r1', 'rrr', trace=True)
       cloud(ns, 'a1', 'rrr', trace=True)

   print '\n** End of standalone test of: EasyBundle.py:\n' 

#=====================================================================================



