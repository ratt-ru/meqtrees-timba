# file: ../JEN/demo/EasyTwig.py:
#
# Author: J.E.Noordam
#
# Short description:
#    Utility functions for making little subtrees (twigs)
#
# History:
#   - 07 june 2008: creation (from EasyTwig.py)
#   - 22 june 2008: split off EasyNode.py
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
    return True

#------------------------------------------------------------------------------------

def _tdl_job_execute_1D (mqs,parent,wait=False):
  from Timba.Meq import meq
  cells = meq.cells(meq.domain(0.1,2,-1,1),             # f1,f2,t1,t2
                    num_freq=50,num_time=1);
  request = make_request(cells)
  mqs.meq('Node.Execute',record(name='rootnode',request=request),wait=wait)
  return True

#------------------------------------------------------------------------------------

def _tdl_job_execute_2D (mqs,parent,wait=False):
  from Timba.Meq import meq
  cells = meq.cells(meq.domain(0.001,2,-2,2),             # f1,f2,t1,t2
                    num_freq=20,num_time=11)
  request = make_request(cells)
  mqs.meq('Node.Execute',record(name='rootnode',request=request),wait=wait)
  return True

#------------------------------------------------------------------------------------

def _tdl_job_execute_3D (mqs,parent,wait=False):
  from Timba.Meq import meq
  dd = record(X=(-1,1), Y=(-2,2), Z=(-3,3))
  cc = record(num_X=11, num_Y=12, num_Z=13)
  cells = meq.gen_cells(meq.gen_domain(**dd), **cc) 
  request = make_request(cells)
  mqs.meq('Node.Execute',record(name='rootnode',request=request),wait=wait)
  return True

#------------------------------------------------------------------------------------

def _tdl_job_execute_4D (mqs,parent,wait=False):
  from Timba.Meq import meq
  dd = record(freq=(0.01,2), time=(-2,2), L=(-1,1), M=(-1,1))
  cc = record(num_freq=20, num_time=21, num_L=11, num_M=11)
  cells = meq.gen_cells(meq.gen_domain(**dd), **cc) 
  request = make_request(cells)
  mqs.meq('Node.Execute',record(name='rootnode',request=request),wait=wait)
  return True

#------------------------------------------------------------------------------------

def _tdl_job_execute_5D (mqs,parent,wait=False):
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
# Some helper fuctions:
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


#====================================================================================
# Functions dealing with standard input twigs:
#====================================================================================

def twig_cats (trace=False):
    """Return a list of twig categories"""
    cats = []
    cats.extend(['axes','complex','noise','tensor'])
    cats.extend(['gaussian','expnegsum'])
    cats.extend(['polyparm'])
    # cats.extend(['Expression'])
    cats.extend(['prod','sum'])
    cats.extend(['constants'])
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
    elif cat=='noise':
        names = ['noise_1','noise_3.5','expnoise_2','cxnoise_2.5',
                 'polarnoise_0.1','phasenoise_0.2','amplnoise_0.01']
    elif cat=='tensor':
        names = ['range_4','range_10','tensor_ftLM']
    elif cat=='gaussian':
        names = ['gaussian_f','gaussian_ft','gaussian_ftLM']
    elif cat=='expnegsum':
        names = ['expnegsum_f2','expnegsum_1.5ft2','expnegsum_f2t2L2M2']
    elif cat=='polyparm':
        names = ['polyparm_f2','polyparm_t2',
                 'polyparm_ft2','polyparm_f2t',
                 'polyparm_f4t4','polyparm_f2t2L2M2',
                 'polyparm_tLMXYZ']
    elif cat=='Expression':
        names = ['{ampl}*exp(-({af}*[f]**2+{at}*[t]**2))']
    elif cat=='sum':
        names = ['sum_f2t3','sum_-3.3f2t','sum_f2t2L2M2']
    elif cat=='prod':
        names = ['prod_f2t3','prod_-3.3f2t','prod_f2t2L2M2']

    elif cat=='all':
        names = twig_names(twig_cats())
    else:
        # default category
        names = ['f','t','L','M','prod_ft2','sum_L2M2',
                 'f**t','range_3','noise_3','cx_ft']

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

def twig(ns, name, quals=None, kwquals=None,
         test=False, help=None, stddev=0.0, trace=False):
    """
    Return a little subtree (a twig), specified by its name,
    and any name-qualifiers (quals=[list] and/or kwquals=dict()).
    If stddev>0, add gaussian noise to the final twig node.

    - f,t,L,M,X,Y,Z                :  Grid(axis=freq/time/L/M/X/Y/Z)
    - cx_ft, cx_tf, cx_LM, cx_XY   :  Complex twigs
    - f**t, t**f, f+t, ft          :
    
    - range_4        :  a 4-element (0,1,2,3) 'tensor' node
    - noise_3.5      :  GaussNoise(stddev=3.5)                stddev>0
    - expnoise_4     :  Exp(GaussNoise(stddev=4))             generate peaks, for flagging
    - cxnoise_3      :  complex noise, with same stddev in real and imag         
    - polarnoise_3   :  complex noise, with same stddev in ampl(w.r.t 1) and phase         
    - phasenoise_3   :  complex noise, with stddev in phase only (rad, w.r.t. 0)        
    - amplnoise_3    :  complex noise, with stddev in ampl only (w.r.t. 1)        

    Twig specs often have an 'ftLM' string, which specifies powers of f,t,L,M.
    For instance, f2t4L0 means f**2, t**4 and L**0 (=1). For instance:
    - sum_f2t2       :  f**2 + t**2
    - sum_-3.4t0L3   :  -3.4 + t**0 + L**3
    - prod_5f1t2L3M4 :  5(f**1)(t**2)(L**3)(M**4)
    NB: The ORDER of the variables in the ftLM string MUST be f,t,L,M  

    - tensor_ftM     :  3-element (f,t,M) 'tensor' node 
    - gaussian_ftLM  :  4D Gaussian, around 0.0, width=1.0 
    - expnegsum_f2t2 :  exp(-(f**2 + t**2))                   equivalent to gaussian_ft
    - polyparm_L3M4  :  polynomial in L,M, with MeqParms      use EN.find_parms(twig) 
    - polyparm_tLMXYZ  :  polynomial in t,L,M,X,Y,Z with MeqParms    MIM 

    An already existing (i.e. a node of that name is initialized) twig is re-used.
    If the twig name is not recognized, a constant node is generated.

    Cookie: If the twig name contains square [] or curly {} brackets,
    a (JEN) Expression tree is generated.

    """

    s1 = '--- EasyTwig.twig('+str(name)
    if quals: s1 += ', quals='+str(quals)
    if kwquals: s1 += ', kwquals='+str(kwquals)
    if test: s1 += ', test='+str(test)
    s1 += '):  '

    recognized_axes = ['f','t','L','M']    

    # Derive and condition the nodename:
    nodename = name
    # nodename = nodename.replace('.',',')    # avoid dots (.) in the nodename

    stub = EN.nodestub(ns, nodename, quals=quals, kwquals=kwquals)

    # Check whether the node already exists (i.e. is initialized...)
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
    elif name in ['x','X','MeqX']:
        node = stub << Meq.Grid(axis='X')
    elif name in ['y','Y','MeqY']:
        node = stub << Meq.Grid(axis='Y')
    elif name in ['z','Z','MeqZ']:
        node = stub << Meq.Grid(axis='Z')
        
    elif name in ['nf']:
        node = stub << Meq.NElements(twig(ns,'f'))
    elif name in ['nt']:
        node = stub << Meq.NElements(twig(ns,'t'))
    elif name in ['nft']:
        node = stub << Meq.NElements(twig(ns,'ft'))
       
    elif name in ['f+t','t+f']:
        node = stub << Meq.Add(twig(ns,'f'),twig(ns,'t'))
    elif name in ['f+t+L+M']:
        node = stub << Meq.Identity(twig(ns,'sum_ftLM'))

    elif name in ['tf','ft','f*t','t*f']:
        node = stub << Meq.Multiply(twig(ns,'f'),twig(ns,'t'))
    elif name in ['LM','ML','L*M','M*L']:
        node = stub << Meq.Multiply(twig(ns,'L'),twig(ns,'M'))
    elif name in ['XYZ','X*Y*Z']:
        node = stub << Meq.Multiply(twig(ns,'X'),twig(ns,'Y'),twig(ns,'Z'))
    elif name in ['f*t*L*M']:
        node = stub << Meq.Identity(twig(ns,'prod_ftLM'))
    elif name in ['ftLM','ftL','ftM','fLM','tLM']:
        node = stub << Meq.Identity(twig(ns,'prod_'+name))

    elif name in ['cx_ft']:
        node = stub << Meq.ToComplex(twig(ns,'f'),twig(ns,'t'))
    elif name in ['cx_tf']:
        node = stub << Meq.ToComplex(twig(ns,'t'),twig(ns,'f'))
    elif name in ['cx_LM']:
        node = stub << Meq.ToComplex(twig(ns,'L'),twig(ns,'M'))
    elif name in ['cx_XY']:
        node = stub << Meq.ToComplex(twig(ns,'X'),twig(ns,'Y'))
        
    elif name in ['f2','f**2']:
        node = stub << Meq.Sqr(twig(ns,'f'))
    elif name in ['t2','t**2']:
        node = stub << Meq.Sqr(twig(ns,'t'))
    elif name in ['L2','L**2']:
        node = stub << Meq.Sqr(twig(ns,'L'))
    elif name in ['M2','M**2']:
        node = stub << Meq.Sqr(twig(ns,'M'))

    elif name in ['f2+t2','t2+f2']:
        node = stub << Meq.Identity(twig(ns,'sum_f2t2'))
        
    elif name in ['f**t']:
        node = stub << Meq.Pow(twig(ns,'f'),twig(ns,'t'))
    elif name in ['t**f']:
        node = stub << Meq.Pow(twig(ns,'t'),twig(ns,'f'))

    elif len(name.split('expnoise_'))>1:               # e.g. 'expnoise_2.5'
        ss = name.split('expnoise_')[1]
        node = stub << Meq.Exp(twig(ns,'noise_'+ss))

    elif len(name.split('cxnoise_'))>1:               # e.g. 'cxnoise_2.5'
        ss = name.split('cxnoise_')[1]
        real = stub('real') << Meq.GaussNoise(stddev=float(ss))
        imag = stub('imag') << Meq.GaussNoise(stddev=float(ss))
        node = stub << Meq.ToComplex(real,imag)

    elif len(name.split('polarnoise_'))>1:            # e.g. 'polarnoise_2.5'
        ss = name.split('polarnoise_')[1]
        dampl = stub('dampl') << Meq.GaussNoise(stddev=float(ss))
        ampl = stub('ampl') << Meq.Add(1.0, dampl)
        phase = stub('phase') << Meq.GaussNoise(stddev=float(ss))
        node = stub << Meq.Polar(ampl,phase)

    elif len(name.split('phasenoise_'))>1:            # e.g. 'phasenoise_2.5'
        ss = name.split('phasenoise_')[1]
        phase = stub('phase') << Meq.GaussNoise(stddev=float(ss))
        node = stub << Meq.Polar(1.0, phase)

    elif len(name.split('amplnoise_'))>1:            # e.g. 'phasenoise_2.5'
        ss = name.split('amplnoise_')[1]
        dampl = stub('dampl') << Meq.GaussNoise(stddev=float(ss))
        ampl = stub('ampl') << Meq.Add(1.0, dampl)
        node = stub << Meq.Polar(ampl, 0.0)

    elif len(name.split('gaussian_'))>1:               # e.g. 'gaussian_ft'
        ss = name.split('gaussian_')[1]
        for s in recognized_axes:
            ss = ss.replace(s,s+'2')                  # e.g. ft -> f2t2 
        node = stub << Meq.Exp(Meq.Negate(twig(ns,'sum_'+ss)))

    elif len(name.split('expnegsum_'))>1:              # e.g. 'expnegsum_f0t1L2M'
        ss = name.split('expnegsum_')[1]
        node = stub << Meq.Exp(Meq.Negate(twig(ns,'sum_'+ss)))

    elif len(name.split('tensor_'))>1:                # e.g. 'tensor_ftLM'
        ss = name.split('tensor_')[1]
        cc = []
        for s in ss:
            cc.append(twig(ns,s))
        if len(cc)>0:
            node = stub << Meq.Composer(*cc)

    elif len(name.split('polyparm_'))>1:             # e.g. 'polyparm_f0t1L2M'
        ss = name.split('polyparm_')[1]
        node = polyparm(ns, 'polyparm', ftLM=ss, trace=trace)

    elif len(name.split('cohlin_'))>1:               # e.g. 'cohlin_I10Q0.1U-0.1V0.01'
        ss = name.split('cohlin_')[1]
        node = cohmat(ns, 'cohlin', IQUV=ss, polrep='linear',
                      stddev=stddev, trace=trace)

    elif len(name.split('cohcir_'))>1:               # e.g. 'cohcir_I10Q0.1U-0.1V0.01'
        ss = name.split('cohcir_')[1]
        node = cohmat(ns, 'cohcir', IQUV=ss, polrep='circular',
                      stddev=stddev, trace=trace)

    #.....................................................................
    # Some useful constants etc:
    #.....................................................................

    elif name in ['c_light','clight']:
        s = 'velocity of light in vacuum (m/s)'
        node = stub << Meq.Constant(2.9979250e8, quickref_help=s) 
    elif name in ['e_charge']:
        s = 'electron charge (C)'
        node = stub << Meq.Constant(1.6021917e-19, quickref_help=s) 
    elif name in ['h_Planck']:
        # def const_h2pi_Planck(ns): return MeqConstant(ns, h_Planck/(2*pi), name='h_Planck_Js/2pi')
        s = 'Planck constant (Js)'
        node = stub << Meq.Constant(6.626196e-34, quickref_help=s) 
    elif name in ['k_Boltzmann','k_Boltzman']:
        # def const_k_Jy(ns): return MeqConstant(ns, k_Boltzmann/1e-26, name='k_Jy/K')
        # def const_2k_Jy(ns): return MeqConstant(ns, 2*k_Boltzmann/1e-26, name='2k_Jy/HzK')
        s = 'Boltzmann constant (J/K)'
        node = stub << Meq.Constant(1.380622e-23, quickref_help=s) 
    elif name in ['G_gravity','G_gravitation']:
        s = 'Gravity constant (Nm2/kg2)'
        node = stub << Meq.Constant(6.6732e-11, quickref_help=s) 

    elif name in ['e_ln']:
        s = 'natural logarithm (e)'
        node = stub << Meq.Constant(math.e, quickref_help=s) 
        
    elif name in ['pi']:
        node = stub << Meq.Constant(math.pi)
    elif name in ['2pi','2*pi']:
        node = stub << Meq.Constant(2*math.pi)
    elif name in ['pi2','pi/2']:
        node = stub << Meq.Constant(0.5*math.pi)
    elif name in ['pi4','pi/4']:
        node = stub << Meq.Constant(0.25*math.pi)

    elif name in ['sqrt2']:
        node = stub << Meq.Sqrt(2.0)
    elif name in ['sqrt3']:
        node = stub << Meq.Sqrt(3.0)

    elif name in ['wavelength','wvl','lambda']:
        node = stub << Meq.Divide(twig(ns,'f'),twig(ns,'clight'),
                                  quickref_help='wavelength (m)') 
        
    #.....................................................................
    # do these last (their short names might be subsets of other names...)
    #.....................................................................

    elif len(name.split('range_'))>1:                  # e.g. 'range_4' 
        ss = name.split('range_')
        node = stub << Meq.Constant(range(int(ss[1])))

    elif len(name.split('noise_'))>1:                  # e.g. 'noise_2.5'
        ss = name.split('noise_')[1]
        node = stub << Meq.GaussNoise(stddev=float(ss))

    elif len(name.split('prod_'))>1:                   # e.g. 'prod_f0t1L2M'
        ss = name.split('prod_')[1]
        node = combine_ftLM(ns, stub, ss, default=1.0, meqclass='Multiply') 

    elif len(name.split('sum_'))>1:                    # e.g. 'sum_f0t1L2M'
        ss = name.split('sum_')[1]
        node = combine_ftLM(ns, stub, ss, default=0.0, meqclass='Add') 

    elif len(name.split('pow_'))==2:                   # e.g. 'fpow_3'
        ss = name.split('pow_')
        if ss[0] in recognized_axes:     
            node = twig(ns,ss[0])
            if ss[1] in '2345678':                    # MeqPow2 ... MeqPow8 
                node = stub << getattr(Meq,'Pow'+ss[1])(node)

    #............................................................

    elif ('[' in name) or (']' in name) or ('{' in name) or ('}' in name):
        # import Expression
        from Timba.Contrib.JEN.Expression import Expression
        expr = Expression.Expression(ns, 'EasyTwig', expr=name)
        expr.display('EasyTwig()')
        node = expr.MeqFunctional()
                
    #............................................................

    if node==None:
        if test:                                               # testing mode
            return False                                       # False: name is invalid ....
        # Otherwise, always return an initialized node:
        node = stub << Meq.Constant(0.123456789)               # a safe (?) number
        s1 += '                ** (name not recognized!) **'
        trace = True

    if stddev>0:
        # Optionally, add gaussian noise to the final result
        # Not yet implemented (what should the nodename be?)
        # NB: Except in cohmat(...., stddev=stddev)
        pass

    if trace:
        s1 += ' -> '+str(node)
        # print dir(node)
        if getattr(node,'children', None):
            cc = node.children
            s1 += '  children('+str(len(cc))+'):' 
            for c in cc:
                s1 += '  '+str(c[1])
            s1 += ')'
        if getattr(node,'initrec', None):
            initrec = node.initrec()
            # print initrec
            v = getattr(initrec,'value',None)
            if isinstance(v,(int,float,complex)):
                s1 += '  (value='+str(v)+')' 
        print '\n**',s1

    if test:                                                  # testing mode
        return True                                           # True: name is valid (recognized)

    # Return the (root)node of the twig:
    return node                        

#----------------------------------------------------------------

def combine_ftLM(ns, stub, ss, default=0.0, meqclass='Multiply'):
    """Combine the children in cc, using the specified meqclass"""
    vv = decode_ftLM(ss, trace=False)
    cc = []
    for key in vv.keys():
        power = vv[key]
        if key=='c':                              # constant (float)
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
    return node

#----------------------------------------------------------------
#----------------------------------------------------------------

def decode_coh (s, trace=False):
    dekey = dict(I=1.0, Q=0.0, U=0.0, V=0.0, u=1.0, v=1.0, L=0.0, M=0.0)
    return decode (s, dekey, trace=trace)

def decode_ftLM (s, trace=False):
    dekey = dict(f=-1, t=-1, L=-1, M=-1)
    return decode (s, dekey, trace=trace)

def decode_ftLMXYZ (s, trace=False):
    dekey = dict(f=-1, t=-1, L=-1, M=-1, X=-1, Y=-1, Z=-1)
    return decode (s, dekey, trace=trace)

#................................................................

def decode (ss, dekey=None, trace=False):
    """Decode the given substring according to the keys and default
    values of dict 'dekey'. Return a dict with decoded (or default)
    values for all keys in dekey.
    """
    if trace:
        print '\n** .decode(',ss,dekey,'):'
    
    rr = dict()
    for key in dekey.keys():
        rr[key] = dekey[key]             # default value
        s = ss.split(key)
        if len(s)==2:
            rr[key] = s[1]
            if rr[key]=='': rr[key] = '1'
        if trace:
            print '- rr[',key,'] = ',rr[key],type(rr[key])

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
                    if isinstance(dekey[key],int):
                        v = int(rr[key])
                    else:
                        v = float(rr[key])
                    rr[key] = v
                    if trace:
                        print '- rr[',key,'] ->',rr[key],type(rr[key])
                except:
                    has_strings = True
                    keys = rr.keys()
                    keys.remove(key)
                    for key1 in keys:
                        s = rr[key].split(key1)
                        if len(s)==2:
                            rr[key] = s[0]
                            if rr[key]=='': rr[key] = '1'
                            if trace:
                                print '-',key1,': rr[',key,'] = (string)',rr[key]
    if trace:
        print '    ->',rr
    return rr


#----------------------------------------------------------------
#----------------------------------------------------------------

def cohmat (ns, name='cohmat', quals=None, kwquals=None,
            IQUV=None, polrep='linear',
            stddev=0.0, trace=False):
    """Make a 2x2 cohaerency matrix, of the specified polarisation.
    The IQUV string contains information about I,Q,U,V,u,v,L,M.
    If stddev>0, some noise is added.
    """

    if isinstance(IQUV, str):
        dekey = dict(I=1.0, Q=0.0, U=0.0, V=0.0, u=1.0, v=1.0, L=0.0, M=0.0)
        vv = decode(IQUV, dekey, trace=True)
        
    if trace:
        print '\n** cohmat(',name, IQUV, polrep,'):'

    time = twig(ns,'t')
    freq = twig(ns,'f')
    pi2 = twig(ns,'pi2')
    # wvl = twig(ns,'lambda')
    # HA = EN.unique_stub(ns,'HA') << time*(math.pi/(12.0*3600.0))
    # DEC = EN.unique_stub(ns,'DEC') << math.pi/6.0
    # cosHA = ns << Meq.Cos(HA)
    # sinHA = ns << Meq.Sin(HA)
    # sinDEC = ns << Meq.Sin(DEC)
    # sinHAsinDEC = ns << Meq.Multiply(sinHA,sinDEC)
    
    lpos = twig(ns,'L')
    mpos = twig(ns,'M')
    ucoord = EN.unique_stub(ns,'ucoord') << vv['u']
    vcoord = EN.unique_stub(ns,'vcoord') << vv['v']
    uvlm = EN.unique_stub(ns,'ulvm') << Meq.Add(ucoord*lpos,vcoord*mpos)
    karg = EN.unique_stub(ns,'karg') << Meq.ToComplex(0.0, pi2*uvlm) 
    KJones = EN.unique_stub(ns,'KJones') << Meq.Exp(karg)

    I = EN.unique_stub(ns,'stokesI') << vv['I']
    Q = EN.unique_stub(ns,'stokesQ') << vv['Q']
    if polrep=='circular':
        iU = EN.unique_stub(ns,'i*stokesU') << Meq.ToComplex(0.0,vv['U'])
        V = EN.unique_stub(ns,'stokesV') << vv['V']
        AA = EN.unique_stub(ns,'RR') << (I+V)
        AB = EN.unique_stub(ns,'RL') << (Q+iU)
        BA = EN.unique_stub(ns,'LR') << (Q-iU)
        BB = EN.unique_stub(ns,'LL') << (I-V)
    else:
        U = EN.unique_stub(ns,'stokesU') << vv['U']
        iV = EN.unique_stub(ns,'i*stokesV') << Meq.ToComplex(0.0,vv['V'])
        AA = EN.unique_stub(ns,'XX') << (I+Q)
        AB = EN.unique_stub(ns,'XY') << (U+iV)
        BA = EN.unique_stub(ns,'YX') << (U-iV)
        BB = EN.unique_stub(ns,'YY') << (I-Q)
    cps = EN.unique_stub(ns,'cps') << Meq.Matrix22(AA,AB,BA,BB)
    coh = EN.unique_stub(ns,'coh') << Meq.Multiply(cps,KJones)

    if stddev>0:
        q = stddev
        noise = EN.unique_stub(ns,'cohnoise') << Meq.Matrix22(complex(random.gauss(0,q),random.gauss(0,q)),
                                                           complex(random.gauss(0,q),random.gauss(0,q)),
                                                           complex(random.gauss(0,q),random.gauss(0,q)),
                                                           complex(random.gauss(0,q),random.gauss(0,q)))
        coh = EN.unique_stub(ns,'noisycoh') << Meq.Add(coh,noise)
        
    if trace:
        print '   ->',str(coh)
        print EN.format_tree(coh)
    return coh

#----------------------------------------------------------------

def polyparm (ns, name='polyparm', ftLM=None,
              fdeg=0, tdeg=0, Ldeg=0, Mdeg=0,
              Xdeg=0, Ydeg=0, Zdeg=0,
              pname='polyparm',
              full=False, trace=False):
    """Make a polynomial subtree (up to 4D, f,t,L,M), with parms.
    """

    if isinstance(ftLM, str):
        # The polynomial degree may be specified by 'ftLM' string:
        # (for compatibility with twig())
        vv = decode_ftLMXYZ(ftLM, trace=True)
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
        sname = name+ftLM
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




#=====================================================================================
# Standalone test (without the browser):
#=====================================================================================

if __name__ == '__main__':

   print '\n** Start of standalone test of: EasyTwig.py:\n' 
   ns = NodeScope()

      
   if 1:
       for cat in twig_cats():
           print '\n\n** twig_cat =',cat
           for name in twig_names(cat):
               twig(ns, name, trace=True)

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
       

   #------------------------------------------------

   if 1:
       dekey = dict(I=1.0, Q=0.0, U=0.0, V=0.0)
       decode('Q-0.1U3', dekey, trace=True)
       cohmat(ns, 'cohmat', quals=[1,2], IQUV='Q-0.1U3', polrep='linear', stddev=0.0, trace=True) 

   if 0:
       dekey = dict(f=-1, t=-1, L=-1, M=-1, X=-1, Y=-1, Z=-1)
       decode('f3t4L5M6', dekey, trace=True)
       decode('ft4L5M6', dekey, trace=True)

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


   if 0:
       ss = range(4)
       ss.extend([1,'a'])
       ss.extend([1,1,3,7,'a',2,2,2])
       print EN.unique_list(ss, trace=True)
       print 'ss (after) =',ss

   print '\n** End of standalone test of: EasyTwig.py:\n' 

#=====================================================================================



