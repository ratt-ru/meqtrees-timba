# file: ../JEN/demo/EasyTwig.py:
#
# Author: J.E.Noordam
#
# Short description:
#    Utility functions for making little subtrees (twigs)
#
# History:
#   - 07 jun 2008: creation (from EasyTwig.py)
#   - 22 jun 2008: split off EasyNode.py
#   - 30 jun 2008: implemented noise()
#   - 30 jun 2008: implemented cloud()
#   - 02 jul 2008: split off EasyBundle.py
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

from Timba.Contrib.JEN.QuickRef import EasyNode as EN

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

    # Standard twig categories:
    for cat in twig_cats():
        twigs = []
        print '\n\n****** twig_cat =',cat
        for name in twig_names(cat):
            t = twig(ns, name, trace=True)
            JEN_bookmarks.create(t, page=name, folder=cat, recurse=2)
            twigs.append(t)
        cc.append(ns[cat] << Meq.Composer(*twigs))
        JEN_bookmarks.create(twigs, cat, folder='twig_categoriess')

    # Some extra twigs:
    names = []
    # names = ['polyparm_f3t2']
    for name in names:
        t = twig(ns,name)
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

def unique_list (ss, trace=False):
    """Helper function to remove doubles from the given list (ss)
    """
    if trace:
        print '\n** unique_list(',ss,'):'
    if isinstance(ss, list):
        ss.reverse()
        for item in copy.copy(ss):
            if trace: print '-',item,':',
            while ss.count(item)>1:
                ss.remove(item)
                if trace: print ss,
            if trace: print
        ss.reverse()
    if trace:
        print '   ->',ss
    return ss

#-----------------------------------------------------------------------------------

def shape2length (shape=1, trace=False):
    """
    Helper function to change a shape into a length.
    """
    if isinstance(shape,int):
        shape = [shape]
    nel = 1
    for i in shape:
        nel *= i
    return nel
    

#====================================================================================
# Functions dealing with standard input twigs:
#====================================================================================

def twig_cats (trace=False):
    """Return a list of twig categories"""
    cats = []
    cats.extend(['axes','complex','tensor'])
    cats.extend(['gaussian','expnegsum'])
    # cats.extend(['Expression'])
    cats.extend(['prod','sum'])
    cats.extend(['constants'])
    cats.extend(['polyparm','cpscoh'])
    cats.extend(['noise','offset'])
    # cats.extend([])
    return cats

#-----------------------------------------------------------------------------------

def twig_names (cat='default', include=None, first=None, trace=False):
    """Return a group (category, cat) of valid twig names"""

    names = []
    
    if isinstance(cat,(list,tuple)):
        # The specified cat may be a list of categories: just concatenate.
        for cat1 in cat:
            names.extend(twig_names(cat1))

    elif cat=='axes':
        names = ['f','t','L','M']
        names.extend(['X','Y','Z'])
    elif cat=='constants':
        names = ['clight','pi','pi2','pi4','2pi','e_ln','sqrt2','sqrt3']
        names.extend(['c_light','k_Boltzman','G_gravity','e_charge','h_Planck'])
    elif cat=='complex':
        names = ['cx_ft','cx_tf','cx_LM','cx_XY']
    elif cat=='sum':
        names = ['sum_f2t3','sum_f2tc-3.3','sum_f2t2L2M2']
    elif cat=='prod':
        names = ['prod_f2t3','prod_c-3.3f2t','prod_f2t2L2M2']
    elif cat=='noise':
        names = ['noise_s1','noise_s3.5','expnoise_s2','noise_r2.5',
                 'noise_a0.1','noise_a0.0p1.0','noise_a0.01']
    elif cat=='tensor':
        names = ['range_4','range_10','tensor_ftLM']
    elif cat=='offset':
        names = ['offset_s4','offset_a2p1m1','offset_r2']
        names.extend(['offset_n6s4','offset_a2p3','offset_r2m-1+3j'])
    elif cat=='gaussian':
        names = ['gaussian_f','gaussian_ft','gaussian_ftLM']
    elif cat=='expnegsum':
        names = ['expnegsum_f2','expnegsum_c1.5ft2','expnegsum_f2t2L2M2']
    elif cat=='polyparm':
        names = ['polyparm_f2','polyparm_t2',
                 'polyparm_ft2','polyparm_f2t',
                 'polyparm_f4t4','polyparm_f2t2L2M2',
                 'polyparm_tLMXYZ']
    elif cat=='cpscoh':
        names = ['cpscohlin_I10','cpscohcir_V-0.1']
        names.extend(['KuvLM_','KuvLM_L2M3'])
    elif cat=='Expression':
        names = ['{ampl}*exp(-({af}*[f]**2+{at}*[t]**2))']

    elif cat=='all':
        names = twig_names(twig_cats())
    else:
        # default category
        names = ['f','t','L','M','prod_ft2','sum_L2M2',
                 'f**t','range_3','noise_s3','cx_ft']

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
    names = unique_list(names)
        
    if trace:
        print '** EasyTwig.twig_names(',cat,include,' first=',first,'):',names
    return names

#-----------------------------------------------------------------------------------

def apply_unop (ns, node, unop=None, trace=False):
    """
    Apply zero or more unary operations to the given node(s).
    (node may be a list of nodes).
    """
    s = '** ET.apply_unop('+str(type(node))+','+str(unop)+'):'
    if unop==None:
        return node
    elif isinstance(unop,str):
        unop = [unop]
    if isinstance(node,(list,tuple)):
        for i,node1 in enumerate(node):
            for unop1 in unop:
                node1 = ns << getattr(Meq,unop1)(node1)
            node[i] = node1
            if trace:
                print s,'->',i,str(node[i])
    else:
        for unop1 in unop:
            node = ns << getattr(Meq,unop1)(node)
        if trace:
            print s,'->',str(node)
    return node

#-----------------------------------------------------------------------------------

def noisetwig(ns, spec='s1m0', nodename=None, quals=None, kwquals=None,
              shape=1, help=None, unop=None, trace=False):
    """
    Syntax:
    .    node = ET.noisetwig(ns, spec, nodename=None, quals=None, kwquals=None,
    .                        shape=1, help=None, unop=None)

    Generate a noise-twig, according to the specification.
    - s (stddev) [=1.0]:        real, >0
    - m (mean) [=0.0]:          if complex (a+bj), the result is complex
    - a (stddev of ampl):       if >0, use MeqPolar (default=p)
    - p (stddev of phase):      if >0, MeqPolar (default=a)
    - r (stddev of real part):  if >0, use MeqToComplex (default=i)
    - i (stddev of imag part):  if >0, use MeqToComplex (default=r)
    If a/p and r/i both specified (>0), MeqPolar (a/p) takes precedence.
    If shape is specified (e.g. 3, or [2,2]) make a tensor node.
    """

    s = '** ET.noisetwig('+str(spec)+','+str(nodename)+'):'
    if trace:
        print '\n',s

    if not isinstance(nodename, str):
        nodename = 'noise'
        nodename += '_'+str(spec)
    stub = EN.unique_stub(ns, nodename, quals=quals, kwquals=kwquals)

    nel = shape2length(shape)             # nr of tensor elements
    if nel>1:
        # If tensor, recursive:
        cc = []
        for k in range(nel):
            if quals:
                cc.append(noisetwig(ns, spec, quals+[k], kwquals=kwquals))
            else:
                cc.append(noisetwig(ns, spec, quals=k, kwquals=kwquals))
        node = stub << Meq.Composer(*cc)
        EN.orphans(node)

    else:
        # A single noise-twig node:
        dekey = dict(s=1.0, m=0.0, r=-1.0, i=-1.0, a=-1.0, p=-1.0)
        vv = decode(spec, dekey, trace=False)

        is_complex = True
        if vv['a']>0 or vv['p']>0:
            if vv['p']<0: vv['p'] = vv['a']
            if vv['a']<0: vv['a'] = vv['p']
            dampl = stub('dampl')(stddev=str(vv['a'])) << Meq.GaussNoise(stddev=vv['a'])
            dphase = stub('dphase')(stddev=str(vv['p'])) << Meq.GaussNoise(stddev=vv['p'])
            var = stub('dpolar') << Meq.Polar(dampl,dphase)
            
        elif vv['r']>0 or vv['i']>0:
            if vv['i']<0: vv['i'] = vv['r']
            if vv['r']<0: vv['r'] = vv['i']
            dreal = stub('dreal')(stddev=str(vv['r'])) << Meq.GaussNoise(stddev=vv['r'])
            dimag = stub('dimag')(stddev=str(vv['i'])) << Meq.GaussNoise(stddev=vv['i'])
            var = stub('dcomplex') << Meq.ToComplex(dreal,dimag)

        elif vv['s']>0:
            is_complex = False
            var = stub('dfloat')(stddev=str(vv['s'])) << Meq.GaussNoise(stddev=vv['s'])

        else:
            s += 's, a or r should be specified (>0): '+str(spec)
            raise ValueError, s

        # Add a mean value (if required):
        if vv['m'] or (isinstance(vv['m'],complex) and not is_complex):
            mean = stub('mean')(str(vv['m'])) << Meq.Constant(vv['m'])
            node = stub << Meq.Add(mean,var)
        else:
            node = var

    # Finishing touches on the twig node:
    if unop:
        node = apply_unop (ns, node, unop, trace=trace)
    if trace:
        print EN.format_tree(node, full=True)
    return node


#-----------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------

def random_offset (ns, spec='s1', nodename=None, quals=None, kwquals=None,
                   shape=1, help=None, unop=None, trace=False):
    """
    Syntax:
    .    node = ET.random_offset(ns, spec, nodename=None, quals=None, kwquals=None,
    .                       parent=None, help=None, unop=None)

    Generate a random_offset of one MeqConstant node, according to the specification.
    - s (stddev) [=1.0]:        real, >0
    - m (mean) [=0.0]:          if complex (a+bj), the result is complex
    - a (stddev of ampl):       if >0, use MeqPolar (default=p)
    - p (stddev of phase):      if >0, MeqPolar (default=a)
    - r (stddev of real part):  if >0, use MeqToComplex (default=i)
    - i (stddev of imag part):  if >0, use MeqToComplex (default=r)
    If a/p and r/i both specified (>0), MeqPolar (a/p) takes precedence.
    """

    s = '** ET.random_offset('+str(spec)+','+str(nodename)+'):'
    if trace:
        print '\n',s

    if not isinstance(nodename, str):
        nodename = 'random_offset'
        nodename += '_'+str(spec)
    stub = EN.unique_stub(ns, nodename, quals=quals, kwquals=kwquals)

    nel = shape2length(shape)             # nr of tensor elements
    if nel>1:
        # If tensor, recursive:
        cc = []
        for k in range(nel):
            if quals:
                cc.append(random_offset(ns, spec, quals+[k], kwquals=kwquals))
            else:
                cc.append(random_offset(ns, spec, quals=k, kwquals=kwquals))
        node = stub << Meq.Composer(*cc)

    else:
        dekey = dict(s=1.0, m=0.0, r=-1.0, i=-1.0, a=-1.0, p=-1.0)
        vv = decode(spec, dekey, trace=False)

        mean = vv['m']
        if isinstance(mean,complex):
            rmean = mean.real
            imean = mean.imag
        else:
            rmean = float(mean)
            imean = 0.0

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

        node = stub(EN.format_value(v)) << Meq.Constant(v)

    # Finishing touches on the list (cc) of nodes:
    if unop:
        node = apply_unop (ns, node, unop, trace=trace)
    if trace:
        print EN.format_tree(node, full=True)
    return node

#-----------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------

def twig (ns, spec,
          nodename=None, quals=None, kwquals=None,
          help=None, shape=None,
          unop=None, stddev=0.0, noise=0.0,
          severe=True, trace=False):
    """
    Return a little subtree (a twig), specified by the argument 'spec'.
    - The name of the rootnode of the twig is composed of 'nodename' (or 'spec'
    .    if no nodename specified) and any nodename-qualifiers (quals=[list], kwquals=dict()).
    - If unop is specified (e.g. 'Cos', or ['Cos','Sin'], apply to the final twig node.
    - If stddev>0, add a gaussian offset (MeqConstant) to the final twig node.
    - If noise>0, add gaussian noise (MeqGaussNoise) to the final twig node.
    - If severe: give an error if spec not recognized (otherwise return a Constant node)

    The following forms of 'spec' (string) are recognized:  

    - f,t,L,M,X,Y,Z                :  Grid(axis=freq/time/L/M/X/Y/Z)
    - cx_ft, cx_tf, cx_LM, cx_XY   :  Complex twigs
    - f**t, t**f, f+t, ft          :
    
    - range_4        :  a 4-element (0,1,2,3) 'tensor' node
    - noise_s3.5     :  GaussNoise(stddev=3.5)                stddev>0
    - expnoise_s4    :  Exp(GaussNoise(stddev=4))             generate peaks, for flagging
    - cloud_n5s2m-4  :  cloud of n=5 MeqConstant nodes, with stddev (s) and mean (m) 

    Twig specs often have an 'ftLM' string, which specifies powers of f,t,L,M.
    For instance, f2t4L0 means f**2, t**4 and L**0 (=1). For instance:
    - sum_f2t2       :  f**2 + t**2
    - sum_c-3.4t0L3  :  -3.4 + t**0 + L**3
    - prod_c5f1t2L3M4 :  5(f**1)(t**2)(L**3)(M**4)
    NB: The ORDER of the variables in the ftLM string MUST be f,t,L,M  

    - tensor_ftM     :  3-element (f,t,M) 'tensor' node 
    - gaussian_ftLM  :  4D Gaussian, around 0.0, width=1.0 
    - expnegsum_f2t2 :  exp(-(f**2 + t**2))                   equivalent to gaussian_ft
    - polyparm_L3M4  :  polynomial in L,M, with MeqParms      use EN.find_parms(twig) 
    - polyparm_tLMXYZ :  polynomial in t,L,M,X,Y,Z with MeqParms    MIM
    - cpscohlin_I2Q-0.1 : 2x2 matrix of CPS cohaerencies (polrep=linear) 
    - cpscohcir_I10V0.01 : 2x2 matrix of CPS cohaerencies (polrep=circular) 

    An already existing (i.e. a node of that name is initialized) twig is re-used.
    If the twig name is not recognized, a constant node is generated.

    Cookie: If the twig name contains square [] or curly {} brackets,
    a (JEN) Expression tree is generated.

    """
    recognized_axes = ['f','t','L','M']       # used below...

    s1 = '--- EasyTwig.twig('+str(spec)
    if nodename: s1 += ', '+str(nodename)
    if quals: s1 += ', quals='+str(quals)
    if kwquals: s1 += ', kwquals='+str(kwquals)
    s1 += '):  '

    # If no nodename specified, use spec
    if nodename==None:
        nodename = 'twig'
        nodename += '_'+str(spec)

    stub = EN.nodestub(ns, nodename, quals=quals, kwquals=kwquals)
    # unique_stub = EN.unique_stub(ns, nodename, quals=quals, kwquals=kwquals)
    node = None
    is_complex = False

    if stub.initialized():                  # node already exists
        # Check whether the node already exists (i.e. is initialized...)
        node = stub                           # return it
    #....................................................................

    elif spec in ['zero']:
        node = stub << Meq.Constant(0.0)
    elif spec in ['one','unity']:
        node = stub << Meq.Constant(1.0)

    elif spec in ['f','freq','MeqFreq']:
        node = stub << Meq.Freq()
    elif spec in ['t','time','MeqTime']:
        node = stub << Meq.Time()
    elif spec in ['l','L','MeqL']:
        node = stub << Meq.Grid(axis='L')
    elif spec in ['m','M','MeqM']:
        node = stub << Meq.Grid(axis='M')
    elif spec in ['x','X','MeqX']:
        node = stub << Meq.Grid(axis='X')
    elif spec in ['y','Y','MeqY']:
        node = stub << Meq.Grid(axis='Y')
    elif spec in ['z','Z','MeqZ']:
        node = stub << Meq.Grid(axis='Z')
        
    elif spec in ['nf']:
        node = stub << Meq.NElements(twig(ns,'f'))
    elif spec in ['nt']:
        node = stub << Meq.NElements(twig(ns,'t'))
    elif spec in ['nft']:
        node = stub << Meq.NElements(twig(ns,'ft'))
       
    elif spec in ['f+t','t+f']:
        node = stub << Meq.Add(twig(ns,'f'),twig(ns,'t'))
    elif spec in ['f+t+L+M']:
        node = stub << Meq.Identity(twig(ns,'sum_ftLM'))

    elif spec in ['tf','ft','f*t','t*f']:
        node = stub << Meq.Multiply(twig(ns,'f'),twig(ns,'t'))
    elif spec in ['LM','ML','L*M','M*L']:
        node = stub << Meq.Multiply(twig(ns,'L'),twig(ns,'M'))
    elif spec in ['XYZ','X*Y*Z']:
        node = stub << Meq.Multiply(twig(ns,'X'),twig(ns,'Y'),twig(ns,'Z'))
    elif spec in ['f*t*L*M']:
        node = stub << Meq.Identity(twig(ns,'prod_ftLM'))
    elif spec in ['ftLM','ftL','ftM','fLM','tLM']:
        node = stub << Meq.Identity(twig(ns,'prod_'+spec))

    elif spec in ['cx_ft']:
        node = stub << Meq.ToComplex(twig(ns,'f'),twig(ns,'t'))
        is_complex = True
    elif spec in ['cx_tf']:
        node = stub << Meq.ToComplex(twig(ns,'t'),twig(ns,'f'))
        is_complex = True
    elif spec in ['cx_LM']:
        node = stub << Meq.ToComplex(twig(ns,'L'),twig(ns,'M'))
        is_complex = True
    elif spec in ['cx_XY']:
        node = stub << Meq.ToComplex(twig(ns,'X'),twig(ns,'Y'))
        is_complex = True
        
    elif spec in ['f2','f**2']:
        node = stub << Meq.Sqr(twig(ns,'f'))
    elif spec in ['t2','t**2']:
        node = stub << Meq.Sqr(twig(ns,'t'))
    elif spec in ['L2','L**2']:
        node = stub << Meq.Sqr(twig(ns,'L'))
    elif spec in ['M2','M**2']:
        node = stub << Meq.Sqr(twig(ns,'M'))

    elif spec in ['f2+t2','t2+f2']:
        node = stub << Meq.Identity(twig(ns,'sum_f2t2'))
        
    elif spec in ['f**t']:
        node = stub << Meq.Pow(twig(ns,'f'),twig(ns,'t'))
    elif spec in ['t**f']:
        node = stub << Meq.Pow(twig(ns,'t'),twig(ns,'f'))

    elif len(spec.split('gaussian_'))>1:               # e.g. 'gaussian_ft'
        ss = spec.split('gaussian_')[1]
        for s in recognized_axes:
            ss = ss.replace(s,s+'2')                  # e.g. ft -> f2t2 
        node = stub << Meq.Exp(Meq.Negate(twig(ns,'sum_'+ss)))

    elif len(spec.split('expnegsum_'))>1:              # e.g. 'expnegsum_f0t1L2M'
        ss = spec.split('expnegsum_')[1]
        node = stub << Meq.Exp(Meq.Negate(twig(ns,'sum_'+ss)))

    elif len(spec.split('tensor_'))>1:                # e.g. 'tensor_ftLM'
        ss = spec.split('tensor_')[1]
        cc = []
        for s in ss:
            cc.append(twig(ns,s))
        if len(cc)>0:
            node = stub << Meq.Composer(*cc)
        shape = len(cc)

    elif len(spec.split('polyparm_'))>1:             # e.g. 'polyparm_f0t1L2M'
        ss = spec.split('polyparm_')[1]
        node = polyparm(ns, 'polyparm', ftLM=ss, trace=False)

    elif len(spec.split('cpscohlin_'))>1:            # e.g. 'cpscohlin_I10Q0.1U-0.1V0.01'
        is_complex = True
        shape = [2,2]
        ss = spec.split('cpscohlin_')[1]
        node = cpscoh(ns, 'cpscoh', IQUV=ss, polrep='linear', trace=False)

    elif len(spec.split('cpscohcir_'))>1:            # e.g. 'cpscohcir_I10Q0.1U-0.1V0.01'
        is_complex = True
        shape = [2,2]
        ss = spec.split('cpscohcir_')[1]
        node = cpscoh(ns, 'cpscoh', IQUV=ss, polrep='circular', trace=False)

    elif len(spec.split('KuvLM_'))>1:                # e.g. 'KuvLM_'
        ss = spec.split('KuvLM_')[1]
        node = KuvLM(ns, ss, trace=False)
        # def KuvLM (ns, uvLM=None, name='KuvLM', quals=None, kwquals=None,


    #.....................................................................
    # Some useful constants etc:
    #.....................................................................

    elif spec in ['c_light','clight']:
        v = 2.9979250e8
        s = 'velocity of light in vacuum (m/s)'
        node = stub(EN.format_value(v)) << Meq.Constant(v, quickref_help=s) 
    elif spec in ['e_charge']:
        v = 1.6021917e-19
        s = 'electron charge (C)'
        node = stub(EN.format_value(v)) << Meq.Constant(v, quickref_help=s) 
    elif spec in ['h_Planck']:
        # def const_h2pi_Planck(ns): return MeqConstant(ns, h_Planck/(2*pi), spec='h_Planck_Js/2pi')
        v = 6.626196e-34
        s = 'Planck constant (Js)'
        node = stub(EN.format_value(v)) << Meq.Constant(v, quickref_help=s) 
    elif spec in ['k_Boltzmann','k_Boltzman']:
        # def const_k_Jy(ns): return MeqConstant(ns, k_Boltzmann/1e-26, spec='k_Jy/K')
        # def const_2k_Jy(ns): return MeqConstant(ns, 2*k_Boltzmann/1e-26, spec='2k_Jy/HzK')
        v = 1.380622e-23
        s = 'Boltzmann constant (J/K)'
        node = stub(EN.format_value(v)) << Meq.Constant(v, quickref_help=s) 
    elif spec in ['G_gravity','G_gravitation']:
        v = 6.6732e-11
        s = 'Gravity constant (Nm2/kg2)'
        node = stub(EN.format_value(v)) << Meq.Constant(v, quickref_help=s) 

    elif spec in ['e_ln']:
        v = math.e
        s = 'natural logarithm (e)'
        node = stub(EN.format_value(v)) << Meq.Constant(v, quickref_help=s) 
    elif spec in ['pi']:
        v = math.pi
        node = stub(EN.format_value(v)) << Meq.Constant(v)
    elif spec in ['2pi','2*pi']:
        v = 2*math.pi
        node = stub(EN.format_value(v)) << Meq.Constant(v)
    elif spec in ['pi2','pi/2']:
        v = 0.5*math.pi
        node = stub(EN.format_value(v)) << Meq.Constant(v)
    elif spec in ['pi4','pi/4']:
        v = 0.25*math.pi
        node = stub(EN.format_value(v)) << Meq.Constant(v)
    elif spec in ['sqrt2']:
        v = math.sqrt(2.0)
        node = stub(EN.format_value(v)) << Meq.Constant(v)
    elif spec in ['sqrt3']:
        v = math.sqrt(3.0)
        node = stub(EN.format_value(v)) << Meq.Constant(v)

    elif spec in ['wavelength','wvl','lambda']:
        node = stub << Meq.Divide(twig(ns,'f'),twig(ns,'clight'),
                                  quickref_help='wavelength (m)') 
        
    #.....................................................................
    # do these last (their short specs might be subsets of other specs...)
    #.....................................................................

    elif len(spec.split('range_'))>1:                  # e.g. 'range_4' 
        ss = spec.split('range_')
        node = stub << Meq.Constant(range(int(ss[1])))

    elif len(spec.split('prod_'))>1:                   # e.g. 'prod_f0t1L2M'
        ss = spec.split('prod_')[1]
        node = combine_ftLMXYZ(ns, stub, ss, default=1.0, meqclass='Multiply') 

    elif len(spec.split('sum_'))>1:                    # e.g. 'sum_f0t1L2M'
        ss = spec.split('sum_')[1]
        node = combine_ftLMXYZ(ns, stub, ss, default=0.0, meqclass='Add') 

    elif len(spec.split('pow_'))==2:                   # e.g. 'fpow_3'
        ss = spec.split('pow_')
        if ss[0] in recognized_axes:                   # f,t,L,M,...
            node = twig(ns,ss[0])        
            if ss[1] in '2345678':                     # MeqPow2 ... MeqPow8 
                node = stub << getattr(Meq,'Pow'+ss[1])(node)

    elif len(spec.split('expnoise_'))>1:               # e.g. 'expnoise_s2.5'
        ss = spec.split('expnoise_')[1]
        node = noisetwig(ns, ss, unop='Exp')
        stddev = 0.0

    elif len(spec.split('noise_'))>1:                  # e.g. 'noise_s2.5'
        # Do this one last of the noises...
        ss = spec.split('noise_')[1]
        node = noisetwig(ns, ss)
        stddev = 0.0

    elif len(spec.split('offset_'))>1:                 # e.g. 'offset_s3'
        ss = spec.split('offset_')[1]
        node = random_offset(ns, ss, trace=False)

    #............................................................

    elif ('[' in spec) or (']' in spec) or ('{' in spec) or ('}' in spec):
        # import Expression
        from Timba.Contrib.JEN.Expression import Expression
        expr = Expression.Expression(ns, 'EasyTwig', expr=spec)
        expr.display('EasyTwig()')
        node = expr.MeqFunctional()
                
    #............................................................

    if not is_node(node):
        if severe:
            s = '\n** ET.twig(',+str(spec)+'): spec not recognized\n'
            raise ValueError,s
        else:
            # Always return an initialized node:
            node = stub << Meq.Constant(0.123456789)                   # a safe (?) number
            trace = True                                               # ensure trace message

    #............................................................

    if unop:
        node = apply_unop(ns, node, unop, trace=False)
        if isinstance(unop,(list,tuple)):
            stub = stub(*unop)
        else:
            stub = stub(unop)

    if noise>0:
        # Optionally, add gaussian noise (MeqGaussNoise) to the final result
        if is_complex:
            nspec = 'r'+str(noise)
        else:
            nspec = 's'+str(noise)
        if shape==None:
            noisy = noisetwig(ns, nspec, quals=quals, kwquals=kwquals, trace=False)
        else:
            noisy = noisetwig(ns, nspec, shape=shape, quals=quals, kwquals=kwquals, trace=False)
        stub = stub('noisy')
        node = stub << Meq.Add(node, noisy)

    if stddev>0:
        # Optionally, add a random (gaussian) offset (MeqConstant) to the final result
        if is_complex:
            nspec = 'r'+str(stddev)
        else:
            nspec = 's'+str(stddev)
        if shape==None:
            offset = random_offset(ns, nspec, quals=quals, kwquals=kwquals, trace=False)
        else:
            offset = random_offset(ns, nspec, shape=shape,
                                   quals=quals, kwquals=kwquals, trace=False)
        stub = stub('offset')
        node = stub << Meq.Add(node, offset)

    #............................................................

    if trace:
        print '\n**',s1
        print EN.format_tree(node, full=True)

    # Return the (root)node of the twig:
    return node                        


#----------------------------------------------------------------
#----------------------------------------------------------------

def combine_ftLMXYZ(ns, stub, spec, default=0.0,
                    meqclass='Multiply', trace=False):
    """
    Combine (Multiply,Add) the terms (nodes) specified in spec.
    These will be powers of f,t,L,M,X,Y,Z, and perhaps a constant.
    """
    # trace = True
    if trace:
        print '\n** ET.combine_ftLMXYZ(',spec,default,meqclass,'):'
    dekey = dict(c=default, f=-1, t=-1, L=-1, M=-1, X=-1, Y=-1, Z=-1)
    vv = decode (spec, dekey, trace=trace)
    cc = []
    for key in vv.keys():
        power = vv[key]
        if key=='c':                              # constant (float)
            if not (vv[key]==default):            # ignore if default value
                cc.append(ns << vv[key])           
        elif power==1:                            # linear
            cc.append(twig(ns,key))
        elif power>1:                             # ignore power<0
            cc.append(twig(ns,key+'pow_'+str(power)))
    if len(cc)==0:
        node = stub << Meq.Constant(default)      # use nodename
    elif len(cc)==1:
        node = stub << Meq.Identity(cc[0])        # use nodename
    else:
        node = stub << getattr(Meq,meqclass)(*cc)
    if trace:
        print EN.format_tree(node)
    return node

#----------------------------------------------------------------

def decode_ftLMXYZ (s, trace=False):
    dekey = dict(f=-1, t=-1, L=-1, M=-1, X=-1, Y=-1, Z=-1)
    return decode (s, dekey, trace=trace)

#................................................................

def decode (spec, dekey=None, override=None, trace=False):
    """
    Decode the given spec-string according to the keys and default
    values of dict 'dekey'. Return a dict with decoded (or default)
    values for all keys in dekey.
    If override is specified (dict), the values of its fields
    override the values of the corresponding output fields.
    """
    if not isinstance(spec,str):
        spec = ''
    if trace:
        print '\n** .decode(',spec,', dekey=',dekey,override,'):'
    
    rr = dict()
    for key in dekey.keys():
        rr[key] = dekey[key]             # default value
        s = spec.split(key)
        if len(s)==2:
            rr[key] = s[1]
            if rr[key]=='': rr[key] = '1'
        if trace:
            if isinstance(rr[key],str):
                print '- rr[',key,'] = ',rr[key],type(rr[key])
            else:
                print '- rr[',key,'] = ',rr[key],type(rr[key]),'(default value)'

    count = 0
    has_strings = True
    while has_strings and count<10:
        count += 1
        has_strings = False
        if trace:
            print 'count=',count
        for key in rr.keys():
            if isinstance(rr[key],str):
                try:
                    # If any of the conversions fails, revert to except:
                    if 'j' in rr[key]:                    # 'j' in spec-string
                        v = complex(rr[key])              #   assume complex is meant (..?)
                    elif isinstance(dekey[key],int):      # default is int
                        v = int(rr[key])                  #   convert to int
                    elif isinstance(dekey[key],bool):     # default is bool
                        v = bool(rr[key])                 #   convert to bool
                    elif isinstance(dekey[key],complex):  # default is complex
                        v = complex(rr[key])              #   convert to complex (..?)
                    elif isinstance(dekey[key],float):    # default is float
                        v = float(rr[key])                #   convert to float 
                    else:
                        v = float(rr[key])                # always try to convert (..?)
                    rr[key] = v
                    if trace:
                        print '- rr[',key,'] ->',rr[key],type(rr[key])
                except:
                    # One of the above conversions has failed:
                    has_strings = True
                    keys = rr.keys()
                    keys.remove(key)
                    for key1 in keys:             # for all but the present key
                        s = rr[key].split(key1)   # see whether it still is in rr[key]
                        if len(s)==2:
                            rr[key] = s[0]
                            if rr[key]=='': rr[key] = '1'   # no value behind key
                            if trace:
                                print '-',key1,': rr[',key,'] = (string)',rr[key]
    if trace:
        print '    ->',rr
    if isinstance(override,dict):
        for key in override.keys():
            rr[key] = override[key]
            if trace:
                print '-- override:',key,'->',rr[key]
    if has_strings:
        s = 'still some undecoded string values in: '+str(rr)
        raise ValueError,s
    
    return rr



#====================================================================================
# Polynomial:
#====================================================================================

def polyparm (ns, name='polyparm', ftLM=None,
              fdeg=0, tdeg=0, Ldeg=0, Mdeg=0,
              Xdeg=0, Ydeg=0, Zdeg=0,
              pname='polyparm',
              full=False, trace=False):
    """
    Make a polynomial subtree (up to 4D, f,t,L,M), with MeqParn coeff.
    """

    if isinstance(ftLM, str):
        # The polynomial degree may be specified by 'ftLM' string:
        # (for compatibility with twig())
        vv = decode_ftLMXYZ(ftLM, trace=False)
        fdeg = max(0,vv['f'])
        tdeg = max(0,vv['t'])
        Ldeg = max(0,vv['L'])
        Mdeg = max(0,vv['M'])
        Xdeg = max(0,vv['X'])
        Ydeg = max(0,vv['Y'])
        Zdeg = max(0,vv['Z'])
        
    if trace:
        print '\n** polyparm(',name,ftLM,fdeg,tdeg,Ldeg,Mdeg,'):'


    # Make a list (cc) of polynomial terms (nodes):
    cc = []
    degmax = max(fdeg+1,tdeg+1,Mdeg+1,Ldeg+1,Xdeg+1,Ydeg+1,Zdeg+1)   # cutting the corner
    for f in range(fdeg+1):
        for t in range(tdeg+1):
            for L in range(Ldeg+1):
                for M in range(Mdeg+1):
                    for X in range(Xdeg+1):
                        for Y in range(Ydeg+1):
                            for Z in range(Zdeg+1):
                                sum_ftLM = f+t+L+M+X+Y+Z         # total degree of term
                                if full or sum_ftLM<degmax:                  # cutting the corner
                                    quals = []
                                    if fdeg>0: quals.append(f)
                                    if tdeg>0: quals.append(t)
                                    if Ldeg>0: quals.append(L)
                                    if Mdeg>0: quals.append(M)
                                    if Xdeg>0: quals.append(X)
                                    if Ydeg>0: quals.append(Y)
                                    if Zdeg>0: quals.append(Z)
                                    parmstub = EN.unique_stub(ns, pname, quals=quals)  # default: 'polyparm'
                                    termstub = EN.unique_stub(ns, 'polyterm', quals=quals)
                                    default_value = 0.1**sum_ftLM            # slightly non_zero
                                    parm = parmstub << Meq.Parm(default_value)
                                    if sum_ftLM==0:                          # the constant term
                                        term = termstub << Meq.Identity(parm)
                                    else:
                                        pname = 'prod_'
                                        if fdeg>0: pname += 'f'+str(f)
                                        if tdeg>0: pname += 't'+str(t)
                                        if Ldeg>0: pname += 'L'+str(L)
                                        if Mdeg>0: pname += 'M'+str(M)
                                        if Xdeg>0: pname += 'X'+str(X)
                                        if Ydeg>0: pname += 'Y'+str(Y)
                                        if Zdeg>0: pname += 'Z'+str(Z)
                                        prodft = twig(ns, pname, trace=trace)
                                        term = termstub << Meq.Multiply(parm,prodft)
                                    cc.append(term)

    # Add all the terms together:
    if isinstance(ftLM,str):
        sname = name+'_'+ftLM
    else:
        sname = name
        if fdeg>0: sname += 'f'+str(fdeg)
        if tdeg>0: sname += 't'+str(tdeg)
        if Ldeg>0: sname += 'L'+str(Ldeg)
        if Mdeg>0: sname += 'M'+str(Mdeg)
        if Xdeg>0: sname += 'X'+str(Xdeg)
        if Ydeg>0: sname += 'Y'+str(Ydeg)
        if Zdeg>0: sname += 'Z'+str(Zdeg)
    nodestub = EN.unique_stub(ns, sname)
    node = nodestub << Meq.Add(*cc)
    if trace:
        print '   ->',str(node),len(node.children),'terms\n'
        EN.find_parms(node, trace=trace)
    return node


#======================================================================================
# Cohaerency matrices:
#======================================================================================


def cpscoh (ns, name='cpscoh', quals=None, kwquals=None,
            IQUV=None, polrep='linear', trace=False):
    """
    Make a 2x2 cohaerency matrix, of the specified polarisation,
    for a central point source (cps), i.e. independent of u,v,w,L,M.
    The IQUV string contains information about I,Q,U,V.
    """
    if trace:
        print '\n** cpscoh(',name, quals, kwquals, IQUV, polrep,'):'

    dekey = dict(I=1.0, Q=0.0, U=0.0, V=0.0)
    vv = decode(IQUV, dekey, trace=False)
    [quals,kwquals] = EN.check_quals(quals, kwquals)
                      
    I = EN.reusenode(ns,'stokesI', vv['I'], *(quals+[vv['I']]), **kwquals)
    Q = 0.0
    if vv['Q']:
        Q = EN.reusenode(ns,'stokesQ', vv['Q'], *(quals+[vv['Q']]), **kwquals)
    if polrep=='circular':
        iU = 0.0
        if vv['U']:
            iU = EN.reusenode(ns,'i*stokesU', Meq.ToComplex(0.0,vv['U']),
                              *(quals+[vv['U']]), **kwquals)
        V = 0.0
        if vv['V']:
            V = EN.reusenode(ns,'stokesV', vv['V'], *(quals+[vv['V']]), **kwquals)
        RR = EN.reusenode(ns,'RR', (I+V), *quals, **kwquals)
        RL = EN.reusenode(ns,'RL', (Q+iU), *quals, **kwquals)
        LR = EN.reusenode(ns,'LR', (Q-iU), *quals, **kwquals)
        LL = EN.reusenode(ns,'LL', (I-V), *quals, **kwquals)
        coh = EN.unique_node(ns,name, Meq.Matrix22(RR,RL,LR,LL),
                             *(quals+[IQUV,polrep]), **kwquals)
    else:
        U = 0.0
        if vv['U']:
            U = EN.reusenode(ns,'stokesU', vv['U'], *(quals+[vv['U']]), **kwquals)
        iV = 0.0
        if vv['V']:
            iV = EN.reusenode(ns,'i*stokesV', Meq.ToComplex(0.0,vv['V']),
                              *(quals+[vv['V']]), **kwquals)
        XX = EN.reusenode(ns,'XX', (I+Q), *quals, **kwquals)
        XY = EN.reusenode(ns,'XY', (U+iV), *quals, **kwquals)
        YX = EN.reusenode(ns,'YX', (U-iV), *quals, **kwquals)
        YY = EN.reusenode(ns,'YY', (I-Q), *quals, **kwquals)
        coh = EN.unique_node(ns,name, Meq.Matrix22(XX,XY,YX,YY),
                             *(quals+[IQUV,polrep]), **kwquals)
            
    if trace:
        print EN.format_tree(coh, full=True)
    return coh


#-------------------------------------------------------------------------------

def KuvLM (ns, uvLM=None, name='KuvLM', quals=None, kwquals=None,
           trace=False):
    """Make a KJones phase factor: KuvLM = exp(i(u*L+v*M)
    The uvLM string contains information about u,v,L,M.
    e.g. uvLM='u1.2M-2.3'
    """
    if trace:
        print '\n** cohmat(',name, uvLM,'):'

    dekey = dict(u=1.0, v=1.0, L=1.0, M=1.0)
    vv = decode(uvLM, dekey, trace=False)
    [quals,kwquals] = EN.check_quals(quals, kwquals)

    Lpos = EN.unique_stub(ns,'Lpos', *quals+[vv['L']], **kwquals) << vv['L']
    Mpos = EN.unique_stub(ns,'Mpos', *quals+[vv['M']], **kwquals) << vv['M']
    ucoord = EN.unique_stub(ns,'ucoord', *quals+[vv['u']], **kwquals) << vv['u']
    vcoord = EN.unique_stub(ns,'vcoord', *quals+[vv['v']], **kwquals) << vv['v']

    uL= vv['u']*vv['L']
    vM = vv['v']*vv['M']
    uLvM = uL + vM
    cuLvM = complex(0.0,uLvM)
    uL = EN.unique_stub(ns,'u*L', *quals+[uL], **kwquals) << Meq.Multiply(ucoord,Lpos)
    vM = EN.unique_stub(ns,'v*M', *quals+[vM], **kwquals) << Meq.Multiply(vcoord,Mpos)
    uLvM = EN.unique_stub(ns,'u*L+v*M', *quals+[uLvM], **kwquals) << Meq.Add(uL,vM)

    kwquals.update(vv)
    karg = EN.unique_stub(ns,'karg', *quals+[cuLvM], **kwquals) << Meq.ToComplex(0.0, uLvM)
    node = EN.unique_stub(ns,name, *quals, **kwquals) << Meq.Exp(karg)

    if trace:
        print EN.format_tree(node, full=True)
    return node

#-------------------------------------------------------------------------------

def cohmat (ns, name='cohmat', quals=None, kwquals=None,
            IQUV=None, polrep='linear',
            stddev=0.0, trace=False):
    """Make a 2x2 cohaerency matrix, of the specified polarisation.
    The IQUV string contains information about I,Q,U,V,u,v,L,M.
    If stddev>0, some noise is added.
    """

    if isinstance(IQUV, str):
        dekey = dict(I=1.0, Q=0.0, U=0.0, V=0.0, u=1.0, v=1.0, L=0.0, M=0.0)
        vv = decode(IQUV, dekey, trace=False)
        
    if trace:
        print '\n** cohmat(',name, IQUV, polrep,'):'

    time = twig(ns,'t')
    freq = twig(ns,'f')
    lpos = twig(ns,'L')
    mpos = twig(ns,'M')
    pi2 = twig(ns,'pi2')

    # wvl = twig(ns,'lambda')
    # HA = EN.unique_stub(ns,'HA') << time*(math.pi/(12.0*3600.0))
    # DEC = EN.unique_stub(ns,'DEC') << math.pi/6.0
    # cosHA = ns << Meq.Cos(HA)
    # sinHA = ns << Meq.Sin(HA)
    # sinDEC = ns << Meq.Sin(DEC)
    # sinHAsinDEC = ns << Meq.Multiply(sinHA,sinDEC)
    
    ucoord = EN.unique_stub(ns,'ucoord', quals, kwquals) << vv['u']
    vcoord = EN.unique_stub(ns,'vcoord', quals, kwquals) << vv['v']
    uvlm = EN.unique_stub(ns,'ulvm', quals, kwquals) << Meq.Add(ucoord*lpos,vcoord*mpos)
    karg = EN.unique_stub(ns,'karg', quals, kwquals) << Meq.ToComplex(0.0, pi2*uvlm) 
    KJones = EN.unique_stub(ns,'KJones', quals, kwquals) << Meq.Exp(karg)

    # ....Needs a little thought....
    # Assume that quals deal with baselines (u,v) and kwquals deal with source...
    # For the source, only initialize nodes if not yet done (test the first one?)
    # This is a general twig-issue....

    # if not EN.nodestub(ns,'stokesI', kwquals=kwquals).initialized():   ....no good....
    if True:
        I = EN.unique_stub(ns,'stokesI', kwquals=kwquals) << vv['I']
        Q = EN.unique_stub(ns,'stokesQ', kwquals=kwquals) << vv['Q']
        if polrep=='circular':
            iU = EN.unique_stub(ns,'i*stokesU', kwquals=kwquals) << Meq.ToComplex(0.0,vv['U'])
            V = EN.unique_stub(ns,'stokesV', kwquals=kwquals) << vv['V']
            AA = EN.unique_stub(ns,'RR', kwquals=kwquals) << (I+V)
            AB = EN.unique_stub(ns,'RL', kwquals=kwquals) << (Q+iU)
            BA = EN.unique_stub(ns,'LR', kwquals=kwquals) << (Q-iU)
            BB = EN.unique_stub(ns,'LL', kwquals=kwquals) << (I-V)
        else:
            U = EN.unique_stub(ns,'stokesU', kwquals=kwquals) << vv['U']
            iV = EN.unique_stub(ns,'i*stokesV', kwquals=kwquals) << Meq.ToComplex(0.0,vv['V'])
            AA = EN.unique_stub(ns,'XX', kwquals=kwquals) << (I+Q)
            AB = EN.unique_stub(ns,'XY', kwquals=kwquals) << (U+iV)
            BA = EN.unique_stub(ns,'YX', kwquals=kwquals) << (U-iV)
            BB = EN.unique_stub(ns,'YY', kwquals=kwquals) << (I-Q)
        cps = EN.unique_stub(ns,'cps', kwquals=kwquals) << Meq.Matrix22(AA,AB,BA,BB)
    
    coh = EN.unique_stub(ns,'coh', quals, kwquals) << Meq.Multiply(cps,KJones)

    if stddev>0:
        q = stddev
        noise = EN.unique_stub(ns,'cohnoise', quals, kwquals) << Meq.Matrix22(complex(random.gauss(0,q),random.gauss(0,q)),
                                                                              complex(random.gauss(0,q),random.gauss(0,q)),
                                                                              complex(random.gauss(0,q),random.gauss(0,q)),
                                                                              complex(random.gauss(0,q),random.gauss(0,q)))
        coh = EN.unique_stub(ns,'noisycoh', quals, kwquals) << Meq.Add(coh,noise)
        
    if trace:
        print EN.format_tree(coh, full=True)
    return coh


#=====================================================================================
# Standalone test (without the browser):
#=====================================================================================

if __name__ == '__main__':

   print '\n** Start of standalone test of: EasyTwig.py:\n' 
   ns = NodeScope()

      
   if 1:
       quals = None
       kwquals = None
       # quals = range(3)
       cats = twig_cats()
       # cats = ['sum','prod','expnegsum']
       cats = ['offset','tensor']
       stddev = 0.0
       noise = 0.0
       unop = 'Cos'
       unop = ['Cos','Sin']
       # unop = None
       stddev = 0.11
       noise = 0.22
       nodename = None
       nodename = 'bob'
       for cat in cats:
           print '\n\n\n'
           print '***************************************************************************'
           print '** twig_cat =',cat,'  quals=',quals,'  kwquals=',kwquals, ' stddev=',stddev,'  nodename=',nodename
           print '***************************************************************************'
           for spec in twig_names(cat):
               twig(ns, spec, quals=quals, kwquals=kwquals,
                    nodename=nodename,
                    unop=unop, stddev=stddev, noise=noise,
                    severe=True, trace=True)

   if 0:
       names = []
       names.extend(['fpow_3','tpow_6'])
       names.extend(['prod_f3t1','prod_f3L1M','prod_3.56'])
       names.extend(['sum_f3t1','sum_-6f3L1M','sum_3.56'])
       names.extend(['f+t','f2','f**2','ft'])
       names.extend(['gaussian_ft'])
       names.extend(['expnoise_4','expnegsum_-2fLM3'])
       names = []
       names.extend(['polyparm_f2t2LM'])
       names.extend(['polyparm_LM'])
       names.extend(['polyparm_XYZ'])
       for name in names:
           twig(ns, name, trace=True)
           
   if 0:
       twig(ns, 'f', trace=True)
       twig(ns, 'ft', trace=True)
       twig(ns, 'f**t', trace=True)
       twig(ns, 't**f', trace=True)
       twig(ns, 'f+t', trace=True)
       twig(ns, 'range_3', trace=True)
       twig(ns, 'noise_3.5', trace=True)
       twig(ns, 'dummy', trace=True)

   if 0:
      twig(ns, 'f', trace=True)
      twig(ns, 'f', quals=range(3), trace=True)
      twig(ns, 'f', quals=[4], trace=True)
      twig(ns, 'f', quals=5, trace=True)
      twig(ns, 'f', quals=[None], trace=True)
      twig(ns, 'f', kwquals=dict(a=2,b=6), trace=True)
      twig(ns, 'f', quals=range(2), kwquals=dict(a=2,b=6), trace=True)


   if 0:
       t = polyparm(ns, fdeg=1, tdeg=2, Ldeg=1, Mdeg=1, trace=True)
       nn = EN.find_parms(t, trace=True)

   if 0:
       expr = '[f]+[t]'
       expr = '[f]+[t]*{alpha}'
       expr = '{a}*exp(-({b}*[f]**2+{c}*[t]**2))'
       t = twig(ns,expr, trace=True)
       nn = EN.find_parms(t, trace=True)

   if 0:
       noise(ns, trace=True)
       noise(ns, 'm1+0j', trace=True)
       noise(ns, 's10m-1+0j', trace=True)
       noise(ns, 'a10m-1+0j', trace=True)
       noise(ns, 'r1i2', trace=True)

   #------------------------------------------------

   if 0:
       cpscoh(ns, 'cpscoh', quals=['3c84'], IQUV='Q-0.1U3',
              polrep='circular', trace=True) 
       cpscoh(ns, 'cpscoh', quals='Moon', IQUV='Q-0.1U3',
              polrep='linear', trace=True) 

   if 0:
       KuvLM(ns, uvLM='u3v5L2', quals='2c67', trace=True) 


   if 0:
       dekey = dict(f=-1, t=-1, L=-1, M=-1, X=-1, Y=-1, Z=-1)
       decode('f3t4L5M6', dekey, trace=True)
       decode('ft4L5M6', dekey, trace=True)

   if 0:
       ss = range(4)
       ss.extend([1,'a'])
       ss.extend([1,1,3,7,'a',2,2,2])
       print EN.unique_list(ss, trace=True)
       print 'ss (after) =',ss

   print '\n** End of standalone test of: EasyTwig.py:\n' 

#=====================================================================================



