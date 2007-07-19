# History:
# - 2006.10.31: creation
# - 2006.11.01: added Rot, Ell, Diag functions
#               note: these functions only take MeqNodes, not polcs
#                     if needed: see MeqModel.py
# - 2006.11.07: added rprint() and format_array(), for easy printing
#               added possibility to time_band to provide starting time
#               in absolute minutes
# - 2006.11.08: added possibility to freq_band to provide starting channel
#               in absolute channels (not tested yet)
# - 2006.11.13: added set_uvw_node()
# - 2006.11.15: added time_tiled_parm()
#               added scaledParm()
# - 2006.11.16: added polc_parm()
#               added random_coeff()
# - 2006.11.17: changed time_tiled_parm() into sawtooth()
# - 2006.11.20: added arcmin_per_hour(), arcsec_per_hour(),
#                     arcmin_per_obs(),  arcsec_per_obs()
# - 2006.11.24: added time_freq_band()
#               corrected small error in freq_band()
# - 2006.11.30: added search_node()
# - 2006.12.05: added calc_FOV()



# imports
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

from   Timba.TDL import *
from   Timba.Meq import meq
import math
import random
import Meow


# constants
DEG    = math.pi/180.
ARCMIN = DEG/60.0 
ARCSEC = ARCMIN/60.0
C      = 3.0E8


def set_uvw_node(ns, p=1):
  """ sets uvw, xyz, and u, v, w nodes for station 'p'
  Can be used when projected baselines are needed.
  """
  ns.radec0= Meq.Composer(ns.ra << 0, ns.dec<< 0)
  ns.xyz0  = Meq.Composer(ns.x0 << 0, ns.y0 << 0,ns.z0 << 0)
  ns.xyz(p) << Meq.Composer(ns.x(p) << 0, ns.y(p) << 0, ns.z(p) << 0)
  ns.uvw(p) << Meq.UVW(radec=ns.radec0, xyz_0=ns.xyz0, xyz=ns.xyz(p));
  ns.u(p)   << Meq.Selector(ns.uvw(p), multi=True,index=[0]);
  ns.v(p)   << Meq.Selector(ns.uvw(p), multi=True,index=[1]);
  ns.w(p)   << Meq.Selector(ns.uvw(p), multi=True,index=[2]);
  pass


def Rot(a, b=None):
  """ return rotation matrix Rot(a,b) """
  if b==None: b = a
  return Meq.Matrix22(
    Meq.Cos(a),
    Meq.Negate(Meq.Sin(a)),
    Meq.Sin(b),
    Meq.Cos(b))


def Diag(a, b=None):
  """ return diagonal matrix Diag(a,b) """
  if b==None: b = a
  return Meq.Matrix22(a,0,0,b)


def Ell(a, b=None):
  """ return ellipticity matrix Ell(a,b) """
  if b==None: b = a
  return Meq.Matrix22(
    Meq.Cos(a),                        #    cos(a)
    Meq.Sin(a) * Meq.ToComplex(0, 1),  #  i sin(a)
    Meq.Sin(b) * Meq.ToComplex(0,-1),  # -i sin(b)
    Meq.Cos(b))                        #    cos(b)


def Book_Mark(Node, page='BookMark'):
  from   Timba.Trees import JEN_bookmarks
  JEN_bookmarks.create(Node, page=page,viewer='Result Plotter')
  pass


def scaled_freq(ns):
  """ get relative frequency dependency """
  f0      = ns.freq0 << 0
  f1      = ns.freq1 << 0
  freq    = (Meq.Freq()-f0)/(f1-f0)
  return f0,f1,freq


def scaled_time(ns):
  """ get relative time dependency """
  t0      = ns.time0 << 0
  t1      = ns.time1 << 0
  time    = (Meq.Time()-t0)/(t1-t0)
  return t0,t1,time


def arcmin_per_hour(ns, arcmin):
  """ return 'arcmin' arc-minutes per hour (f(t))"""
  t0      = ns.time0 << 0
  return arcmin * ARCMIN * (Meq.Time()-t0)/3600.0


def arcsec_per_hour(ns, arcsec):
  """ return 'arcsec' arc-seconds per hour (f(t))"""
  t0      = ns.time0 << 0
  return arcsec * ARCSEC * (Meq.Time()-t0)/3600.0


def arcmin_per_obs(ns, arcmin):
  """ return 'arcmin' arc-minutes per observation (f(t))"""
  t0, t1, time = scaled_time(ns)
  return arcmin * ARCMIN * time


def arcsec_per_obs(ns, arcsec):
  """ return 'arcsec' arc-seconds per observation (f(t))"""
  t0, t1, time = scaled_time(ns)
  return arcsec * ARCSEC * time


def scaledParm(polc=[0.]):
  """ returns a parm scaled to time-domain [0,1] == 0hr-12hr """
  #HA      = ns["HA"] << pxk_tools.scaledParm([-math.pi/2, math.pi])
  starttime  = 4647002189.5  # ns.time0
  startfreq  = 1401000000.0  # ns.freq0
  time_extent= 43008.0       # ns.time1 - ns.time0
  freq_extent= 62e6          # ns.freq1 - ns.freq0
  funk       = meq.polc(polc)
  funk.offset= [float(starttime),   float(startfreq)  ]
  funk.scale = [float(time_extent), float(freq_extent)]
  return Meq.Parm(funk)


def sawtooth(ns, nparts=12, dir="time", combine=False):
  """ returns a composed parm by tiling the time/freq
  (Sawtooth function in time/freq)
  
  nparts   : num slots that the full time/freq range will be divided in
  combine  : complete sawtooth or individual components will be returned
  """
  global  cparm               # get unique ID
  try:    cparm += 1
  except: cparm  = 1
  name     = "cparm" + str(cparm)

  # Create sawtooth (domain=0) and block function (domain=1)
  if   dir=="time":
    var0,var1,var = scaled_time(ns)
    full_range    = Meq.Time()
  else:
    var0,var1,var = scaled_freq(ns)
    full_range    = Meq.Freq()
    pass

  offset    = 1e-6            # hack for first and last domain
  ns[name] << 0
  LIST     = []
  for part in range(nparts):
    
    # get right domain
    start    = var0 + part/float(nparts)*(var1-var0)
    if   part==0:        start -= offset
    elif part==nparts-1: start += offset
    slot     = (full_range - start)/(var1-var0)

    # create f(var) = var on this domain
    x        = Meq.Max( Meq.Ceil(1.0/nparts - slot)*slot*nparts, 0)
    domain   = Meq.Ceil(x)
    if combine:
      # reset values outside tile domain to 0
      LIST.append(x * domain)
    else:
      ns[name](part,domain=0) << x
      ns[name](part,domain=1) << domain
      pass
    pass
  
  if combine: return Meq.Add(*LIST)
  else      : return ns[name]
  pass


def polc_parm(ns, coeff=[[1.0,0.0],[1.0,0.0]], dir="time"):
  """ creates a composed parm that acts like a polc at every separate
  time slot. Number of time slots depends on length of 'coeff'. The
  time slots are provided by fumction sawtooth()
  coeff  : coefficients of the polcs of every timeslot.
  """
  nparts   = len(coeff)                   # number of slots
  compparm = sawtooth(ns, nparts, dir)
  
  LIST     = []
  for part in range(nparts):              # loop tiles
    x        = compparm(part, domain=0)
    domain   = compparm(part, domain=1)
    polcparm = 0
    for c in range(len(coeff[part])):     # loop coefs per tile
      polcparm  += coeff[part][c] * Meq.Pow(x,c)
      pass

    # reset values outside tile domain to 0
    LIST.append(polcparm * domain)
    pass
  return Meq.Add(*LIST)


def random_coeff(num=12, min=0.9, max=1.1):
  """ Returns a list of 'num' coefficients in range [min,max]
  Can be used together with polc_parm().
  """
  coeff = []
  end   = random.uniform(min,max)
  for i in range(12):
    start = end
    end   = random.uniform(min,max)
    coeff.append([start, end-start])
    pass
  return coeff
      

def time_band(ns, t_start=0.5, t_min=10, kind='real',
              t_from=None, t_from_end=None):
  """ Makes a time-band function (useful for transients / RFI)
  t_start    : move start-time of time-band
  t_from     : absolute start-time of time-band (min)
  t_from_end : absolute start-time of time-band (min), from end 
  t_min      : band-time in minutes
  """
  # set ID of transient
  global  num_t
  try:    num_t += 1
  except: num_t  = 1
    
  # get relative time dependency
  t0,t1,time = scaled_time(ns)
  if   t_from     is not None: # use absolute starting time
    t_start = (t_from*60.0) / (t1-t0)
    pass
  elif t_from_end is not None: # use absolute starting time, from end
    t_start = 1.0 - (t_from_end*60) / (t1-t0 + 60)
    pass
  time       = time + 0.5 - t_start  # move time of transient
  n          = (t1-t0)/(t_min*60)    # obs-time / n = transient-time

  if   kind=='box':      # make box-function
    stairs_t   = ns.stairs_t (num_t) << \
                 Meq.Negate(Meq.Abs(Meq.Floor(time*n - n/2))) + 1
    band_t     = ns.time_band(num_t) << (stairs_t + Meq.Abs(stairs_t))/2
  elif kind=='real':     # make 'real' profile
    t_trans    = 30.0/t_min
    func2      = ns.func2(num_t) << Meq.Multiply(0.003,Meq.Time()-t0-3600) 
    func1      = ns.func1(num_t) << \
                 3 * Meq.Atan(func2) * Meq.Exp(-t_trans*func2) 
    band_t     = ns.time_band(num_t)<< Meq.Max(0.0,func1) 
    pass
  
  #Book_Mark(band_t, 't/nu band')
  return band_t


def freq_band(ns, f_start=0.5, nchan=3, f_from=None, f_from_end=None):
  """ Makes a frequency-band function
  f_start : move start-freq of narrow-band
  f_from     : absolute start-channel of freq-band
  f_from_end : absolute start-channel of freq-band, from end
  nchan   : width of band in channels
  """
  # set ID of frequency-band
  global  num_f
  try:    num_f += 1
  except: num_f  = 1
  f0,f1,freq = scaled_freq(ns)
  if nchan==0:
    # transient brightness scales with freq
    band_f     = ns.freq_band(num_f) << freq
    pass
  else:
    # make narrow band (transient only visible in certain channels)
    chans      = ns.num_channels << 0
    if   f_from     is not None: # use absolute starting channel
      f_start = ns.fstart(f_from) << f_from / (chans-1E-3)
      pass
    elif f_from_end is not None: # use absolute starting channel, from end
      f_start = 1.0 - f_from_end / (chans-1E-3)
      pass
    freq       = freq + 0.5 - f_start    # move start-freq
    n          = chans / nchan           # freq-band / n = narrow-band
    stairs_f   = ns.stairs_f (num_f) << \
                 Meq.Negate(Meq.Abs(Meq.Floor(freq*n - n/2))) + 1
    band_f     = ns.freq_band(num_f) << \
                 (stairs_f + Meq.Abs(stairs_f))/2
    pass
  
  Book_Mark(band_f, 't/nu band')
  return band_f


def time_freq_band(ns, parts=32, bookmarks=False):
  """ Makes a movie of snapshots in time, put in different channels.
  Works best when number of channels in MS is multiple of 'parts'
  parts   : number of part to divide time/freq in
  """
  band       = []
  t0,t1,time = scaled_time(ns)
  f0,f1,freq = scaled_freq(ns)
  chans      = ns.num_channels << 0
  
    
  for part in range(parts):

    # get start position in time/freq
    start      = part/(1.0*parts)
    if   part==0:       start -=1E-6
    elif part==parts-1: start +=1E-6

    # get time band
    time_s     = time + 0.5 - start      # move start-time
    stairs_t   = Meq.Negate(Meq.Abs(Meq.Floor(time_s*parts - parts/2))) +1
    band_t     = ns.time_band(part) << (stairs_t + Meq.Abs(stairs_t))/2
    if part < 16 and bookmarks: Book_Mark(band_t, 't band')

    # get frequency band
    freq_s     = freq + 0.5 - start      # move start-freq
    stairs_f   = Meq.Negate(Meq.Abs(Meq.Floor(freq_s*parts - parts/2))) +1
    band_f     = ns.freq_band(part) << (stairs_f + Meq.Abs(stairs_f))/2
    if part < 16 and bookmarks: Book_Mark(band_f, 'f band')
    
    band.append(band_t * band_f)
    pass
  band   = ns.time_freq_band << Meq.Add(*band)
  if bookmarks: Book_Mark(band, "time_freq_band")  
  return band


def rprint(rec):
  """ Prints a record recursively up to 2nd level """
  for subkey0 in rec.keys():
    print subkey0
    try:
      for subkey1 in rec[subkey0].keys():
        print "  ", subkey1
        try:
          for subkey2 in rec[subkey0][subkey1].keys():
            print "     ", subkey2
            pass
          pass
        except: pass
        pass
      pass
    except: pass
    pass
  pass
 

def format_array(array=[], format="%f"):
  """ returns array as string in given 'format'
  """
  s  = "["
  for i in array:
    s += format % i + ", "
    pass
  s = s[0:len(s)-2] + "]"
  return s

def search_node(ns, name="", classname=""):
  if classname=="": classname=name
  print name,     "[name] :",ns.Search(return_names=True,name=name);
  print classname,"[class]:",ns.Search(return_names=True,class_name=classname)
  pass


def calc_FOV(arcmin='auto', maxrad=1.0):
  # Calculate Field Of View in arcsec
  if arcmin=='auto':
    MSNAME  = Meow.Utils.msname.upper()
    FOV_min = {
      True              : maxrad*2,            # default FOV
      "LOFAR" in MSNAME or
      "CORE"  in MSNAME or
      "FULL"  in MSNAME : max(maxrad*2, 600),  # LOFAR minimum 600' FOV
      "WSRT"  in MSNAME : max(maxrad*2,  30),  # WSRT  minimum  30' FOV
      "VLA"   in MSNAME or
      "DEMO"  in MSNAME : max(maxrad*2,   5),  # VLA   minimum   5' FOV
      }[True]
  else: FOV_min = arcmin
  
  print "FOV (arcmin): ", FOV_min  
  return FOV_min * 60.0

