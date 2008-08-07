# file: ../JEN/demo/EasyFormat.py:
#
# Author: J.E.Noordam
#
# Short description:
#    Utility functions for formatting values, records etc into strings 
#
# History:
#   - 29 jul 2008: creation
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
# from Timba.Meq import meq
# from Timba.meqkernel import set_state

# Settings.forest_state.cache_policy = 100

import copy
import math
import pylab       







#============================================================================
# Function to format a (short) string that represent a value:
#============================================================================

def format_value(v, name=None, nsig=4, trace=False):
    """
    Format a string that summarizes the given value (v).
    If v is a node, use its initrec.value field, if any.
    If a name is specified, prepend it.
    The argument nsig[=4] is the desired nr of significant digits.
    """
    vin = v
    if is_node(v):
        ss = '(node)'
        vin = '(node)'
        if getattr(v,'initrec',None):
            initrec = v.initrec()
            v1 = getattr(initrec,'value',None)
            if not v1==None:
                ss = format_value(v1, nsig=nsig)
    elif isinstance(v,(complex)):
        ss = format_float(v, nsig=nsig)
    elif isinstance(v,(int)):
        ss = str(v)
    elif isinstance(v,(float)):
        ss = format_float(v, nsig=nsig)
    elif isinstance(v,(list,tuple)):
        ss = format_list(v)
    elif isinstance(v,dict):
        ss = '(dict/record): '+str(v.keys())
    elif isinstance(v,str):
        ss = '"'+str(v)+'"'
    else:
        ss = str(v)

    if isinstance(name,str):
        ss = name+'='+ss

    if trace:
        print '** format_value(',vin,type(v),name,nsig,') ->',ss
    return ss

#-----------------------------------------------------------------------

def format_list(vv):
    """
    Helper function
    """
    ss = '(list)'
    if not isinstance(vv,(list,tuple)):
        ss += '(not a list, but: '+str(type(vv))+')'
    elif len(vv)==0:
        ss += '...empty...'
    elif not isinstance(vv[0],(int,float,complex)):
        ss += ' (n='+str(len(vv))+'):'
        ss += ' not numeric, vv[0]='+str(vv[0])
    else:
        ss += ' (n='+str(len(vv))+'):'
        vmin = 1e20
        vmax = -1e20
        for v in vv:
            vmin = min(vmin,v)
            vmax = max(vmax,v)
        ss += ' (min='+format_float(vmin)+')'
        ss += ' (max='+format_float(vmax)+')'
    return ss

#-----------------------------------------------------------------------

def format_float(v, name=None, nsig=4, trace=False):
    """Helper function to format a string that represents the given value.
    Contrary to its name, it handles complex, int and float. 
    The argument nsig[=4] is the desired nr of significant digits.
    """
    if isinstance(v,complex):
        s1 = format_float(v.real)
        s2 = format_float(v.imag)
        if v.imag<0:
            ss = '('+s1+s2+'j)'
        else:
            ss = '('+s1+'+'+s2+'j)'
    elif not isinstance(v,float):
        ss = str(v)
    elif v==0.0:
        ss = '0.0'
    else:
        vabs = abs(v)
        log10 = math.log(10.0)
        nlog = int(math.log(vabs)/log10)
        q = 10.0**float(nsig-nlog)
        if vabs>1e10:
            ss = str(v)
        elif vabs>1e3:
            ss = str(int(v))
        elif vabs<1e-5:
            ss = str(v)
        else:
            v1 = int(v*q)/q
            ss = str(v1)
            # print '===',v,vabs,nlog,q,ss
    if isinstance(name,str):
        ss = name+'='+ss
    return ss

#================================================================================
# Format a record:
#================================================================================

def format_record(rr, txt=None, ss=None, level=0, full=False, mode='str'):
    """
    Format the given record
    """
    prefix = '\n ..'+(level*'..')+' '
    if level==0:
        ss = '\n** format_record(): '+str(txt)+' ('+str(type(rr))+'):'
        
    for key in rr.keys():
        if getattr(rr[key],'mean',None):              # e.g. numarray...
            vv = rr[key]
            # print dir(vv)
            nel = vv.nelements()
            stddev = 0.0
            if nel>1:
                if getattr(vv,'stddev',None):    # numarray...
                    stddev = vv.stddev()
                elif getattr(vv,'std',None):     # numpy
                    stddev = vv.std()
                else:
                    stddev = '??'
            ss += prefix+str(key)+': n='+str(nel)
            ss += '   mean='+str(vv.mean())
            ss += '   stddev='+str(stddev)
            ss += '   [min,max]='+str([vv.min(),vv.max()])
            if full:
                ss += prefix+str(key)+' ('+str(type(rr[key]))+') = '+str(rr[key])
                
        elif not isinstance(rr[key],dict):
            ss += prefix+str(key)+' ('+str(type(rr[key]))+') = '+str(rr[key])

    for key in rr.keys():
        if isinstance(rr[key],dict):
            ss += prefix+str(key)+':'
            ss = format_record(rr[key], ss=ss, level=level+1, full=full)

    if level==0:
        ss += '\n**\n'
        if mode=='list':
            ss = ss.split('\n')
    return ss


#============================================================================
# Function to format a function call:
#============================================================================

def format_function_call (function_name, **kwargs):
    """
    Format a string that summarizes a function call
    """
    ss = '<br><dl><dt><font color="blue">\n'
    ss += 'Call to function: '+str(function_name)+'():'
    ss += '\n</font><dd>\n'

    for key in kwargs.keys():
        if key=='kwargs' and isinstance(kwargs['kwargs'],dict):
            pass
        else:
            s = '- '+str(key)+' = '
            s += format_value(kwargs[key])
            ss += s+'<br>\n'

    if kwargs.has_key('kwargs'):
        kw = kwargs['kwargs']
        if isinstance(kw,dict):
            for key in kw.keys():
                s = '-- '+str(key)+' = '
                s += format_value(kw[key])
                ss += s+'<br>\n'
                
    # Finished:
    ss += '</dl><br>\n'
    # print ss
    return ss
      

#=====================================================================================
# Standalone test (without the browser):
#=====================================================================================

if __name__ == '__main__':

   print '\n** Start of standalone test of: EasyFormat.py:\n' 

   if 0:
       format_value(3, 'int', trace=True)
       format_value(3.4, 'float', trace=True)
       format_value(complex(3,4), 'complex', trace=True)
       format_value(range(100), 'list', trace=True)
       format_value(ns << Meq.Constant(4.5), 'node', trace=True)

   if 0:
       format_value(123.456, trace=True)
       format_value(12.3456, trace=True)
       format_value(1.23456, trace=True)
       format_value(0.123456, trace=True)
       format_value(0.0123456, trace=True)
       format_value(0.00123456, trace=True)

   print '\n** End of standalone test of: EasyFormat.py:\n' 

#=====================================================================================



