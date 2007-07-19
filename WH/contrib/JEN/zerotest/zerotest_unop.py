# zerotest_unop.py:


 
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

from Timba.Contrib.JEN.util import JEN_zerotest

Settings.forest_state.cache_policy = 100
Settings.forest_state.bookmarks = []



#********************************************************************************
# The function under the 'blue button':
#********************************************************************************

def _define_forest (ns, **kwargs):
   """Zerotest of unary function nodes"""

   # Make node(s) to serve as argument for the unary ops.
   x = ns.x << Meq.Freq()
   y = ns.y << Meq.Time()
   xy = ns.xy << Meq.Add(x,y)

   x10 = ns.x10 << Meq.Freq()/10
   y10 = ns.y10 << Meq.Time()/10
   xy10 = ns.xy10 << Meq.Add(x10,y10)

   cx = ns.cx << Meq.toComplex(1,x)
   xn = ns.xneg << Meq.Negate(x)

   cc = []

   #-------------------------------------------------------
   group = 'expon'

   expz = ns << Meq.Exp(xy)
   nexp = ns << Meq.Exp(ns << Meq.Negate(xy))
   expz10 = ns << Meq.Exp(xy10)
   nexp10 = ns << Meq.Exp(ns << Meq.Negate(xy10))

   zero = ns << Meq.Sqrt(ns << Meq.Sqr(xy)) - xy
   cc.append(JEN_zerotest.zerotest(ns, zero, recurse=3))

   zero = ns << Meq.Exp(ns << Meq.Log(xy)) - xy
   cc.append(JEN_zerotest.zerotest(ns, zero, recurse=3))

   zero = ns << Meq.Negate(xy) + xy
   cc.append(JEN_zerotest.zerotest(ns, zero, recurse=3))

   zero = ns << Meq.Multiply(ns << Meq.Invert(xy), xy) - 1
   cc.append(JEN_zerotest.zerotest(ns, zero, recurse=3))

   #-------------------------------------------------------
   group = 'circular'

   sinz = ns << Meq.Sin(xy)
   cosz = ns << Meq.Cos(xy)
   tanz = ns << Meq.Tan(xy)

   zero = ns << Meq.Add(ns << Meq.Sqr(sinz), ns << Meq.Sqr(cosz)) - 1
   cc.append(JEN_zerotest.zerotest(ns, zero, recurse=3))

   zero = ns << Meq.Subtract(ns << Meq.Divide(sinz,cosz),tanz)
   cc.append(JEN_zerotest.zerotest(ns, zero, recurse=3))

   sinh10 = ns << Meq.Sinh(xy10)
   cosh10 = ns << Meq.Cosh(xy10)
   tanh10 = ns << Meq.Tanh(xy10)

   zero = ns << Meq.Subtract(ns << Meq.Sqr(sinh10), ns << Meq.Sqr(cosh10)) + 1
   cc.append(JEN_zerotest.zerotest(ns, zero, recurse=3))

   zero = ns << Meq.Subtract(ns << Meq.Divide(sinh10,cosh10),tanh10)
   cc.append(JEN_zerotest.zerotest(ns, zero, recurse=3))

   zero = ns << Meq.Subtract(2*sinh10, ns << Meq.Subtract(expz10,nexp10))
   cc.append(JEN_zerotest.zerotest(ns, zero, recurse=3))

   zero = ns << Meq.Subtract(2*cosh10, ns << Meq.Add(expz10,nexp10))
   cc.append(JEN_zerotest.zerotest(ns, zero, recurse=3))

   #-------------------------------------------------------
   #-------------------------------------------------------
   #-------------------------------------------------------


   if False:
      group = 'pow'
      cc = [x,
            ns << Meq.Pow2(x), 
            ns << Meq.Pow3(x), 
            ns << Meq.Pow4(x), 
            ns << Meq.Pow5(x), 
            ns << Meq.Pow6(x), 
            ns << Meq.Pow7(x), 
            ns << Meq.Pow8(x)
            ]
      gg.append(ns[group] << Meq.Add(children=cc))
      
      group = 'circular'
      cc = [
         ns << Meq.Cos(x), 
         ns << Meq.Sin(x), 
         ns << Meq.Tan(x), 
         ns << Meq.Acos(x10), 
         ns << Meq.Asin(x10), 
         ns << Meq.Atan(x), 
         ns << Meq.Cosh(x), 
         ns << Meq.Sinh(x), 
         ns << Meq.Tanh(x)
         ]
      gg.append(ns[group] << Meq.Add(children=cc))
      
      group = 'complex'
      cc = [cx,
            ns << Meq.Abs(cx), 
            ns << Meq.Norm(cx), 
            ns << Meq.Arg(cx), 
            ns << Meq.Real(cx), 
            ns << Meq.Imag(cx), 
            ns << Meq.Conj(cx)
            ]
      gg.append(ns[group] << Meq.Add(children=cc))
      
      group = 'round'
      cc = [xn,
            ns << Meq.Abs(xn), 
            ns << Meq.Fabs(xn), 
            ns << Meq.Ceil(xn), 
            ns << Meq.Floor(xn)
            ]
      gg.append(ns[group] << Meq.Add(children=cc))

   # Finally, add all zerotest nodes for an overall zerotest:
   JEN_zerotest.zerotest(ns, ns.zerotest << Meq.Add(children=cc))

   # Finished:
   return True



#********************************************************************************
# The function under the TDL Exec button:
#********************************************************************************

def _tdl_job_execute (mqs, parent):
    """Execute the forest, starting at the named node"""
    domain = meq.domain(0.1,10,0.1,10)                            # (f1,f2,t1,t2)
    cells = meq.cells(domain, num_freq=20, num_time=20)
    request = meq.request(cells, rqtype='ev')
    result = mqs.meq('Node.Execute',record(name='zerotest', request=request))
    return result
       

def _tdl_job_negapos (mqs, parent):
    """Execute the forest, with negative and positive values in the request"""
    domain = meq.domain(-10,10,-10,10)                            # (f1,f2,t1,t2)
    cells = meq.cells(domain, num_freq=20, num_time=20)
    rqid = meq.requestid(domain_id=3)
    request = meq.request(cells, rqtype='ev', rqid=rqid)
    result = mqs.meq('Node.Execute',record(name='zerotest', request=request))
    return result
       

def _tdl_job_zero (mqs, parent):
    """Execute the forest, with zeroes in the request"""
    domain = meq.domain(-1,1,-1,1)                            # (f1,f2,t1,t2)
    cells = meq.cells(domain, num_freq=1, num_time=1)
    rqid = meq.requestid(domain_id=3)
    request = meq.request(cells, rqtype='ev', rqid=rqid)
    result = mqs.meq('Node.Execute',record(name='zerotest', request=request))
    return result

       
#********************************************************************************
#********************************************************************************




