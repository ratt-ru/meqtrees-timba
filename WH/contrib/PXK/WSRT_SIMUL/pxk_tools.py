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


# imports
from   Timba.TDL import *
from   Timba.Meq import meq
import math


# constants
DEG    = math.pi/180.
ARCMIN = DEG/60.0 



def set_uvw_node(ns, p=1):
  """ sets uvw, xyz, and u, v, w nodes for station 'p' """
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
  
  Book_Mark(band_t, 't/nu band')
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
    if   f_from     is not None: # use absolute starting channel
      f_start = (f_from) / (f1-f0)
      pass
    elif f_from_end is not None: # use absolute starting channel, from end
      f_start = 1.0 - (f_from_end) / (f1-f0 + 1)
      pass
    freq       = freq + 0.5 - f_start    # move start-freq
    chans      = ns.num_channels << 0
    n          = chans / nchan           # freq-band / n = narrow-band
    stairs_f   = ns.stairs_f (num_f) << \
                 Meq.Negate(Meq.Abs(Meq.Floor(freq*n - n/2))) + 1
    band_f     = ns.freq_band(num_f) << \
                 (stairs_f + Meq.Abs(stairs_f))/2
    pass
  
  Book_Mark(band_f, 't/nu band')
  return band_f


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

