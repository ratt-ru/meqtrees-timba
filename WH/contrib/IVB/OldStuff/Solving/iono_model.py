from Timba.TDL import *
import math
from Meow import Context

"""This module now implements the various ionospheric models used for
simulations. Each model is implemented by a function with the following
signature:
  model(ns,piercings,za_cos,source_list)
piercings and za_cos specify the per-source, per-station piercing points
The return value is something that can be qualified with (name,station)
to get the TEC value for that source and station.
""";


def sine_tid_model (ns,pp,sources):
  """This implements a 1D sine wave moving over the array""";
  stations = Context.array.stations();
  ns.delta_time = Meq.Time() - (ns.time0<<0);
  ns.tid_x_ampl << tid_x_ampl_0*TEC0 + (tid_x_ampl_1hr-tid_x_ampl_0)*TEC0/3600.*ns.delta_time;
  ns.tid_y_ampl << tid_y_ampl_0*TEC0 + (tid_y_ampl_1hr-tid_y_ampl_0)*TEC0/3600.*ns.delta_time;
  tid_x_rate = tid_x_speed_kmh/(2.*tid_x_size_km);   # number of periods per hour
  tid_y_rate = tid_y_speed_kmh/(2.*tid_y_size_km);   # number of periods per hour
  for src in sources:
    for s in stations:
      px = ns.px(src.name,s) << Meq.Selector(pp(src.name,s),index=0); 
      py = ns.py(src.name,s) << Meq.Selector(pp(src.name,s),index=1); 
      ns.tecs(src.name,s) << (TEC0 +   \
                              ns.tid_x_ampl*Meq.Sin(2*math.pi*(px/(2*1000*tid_x_size_km) + \
                                                               ns.delta_time*tid_x_rate/3600.))     + \
                              ns.tid_y_ampl*Meq.Cos(2*math.pi*(py/(2*1000*tid_y_size_km) + \
                                                               ns.delta_time*tid_y_rate/3600.)))
  return ns.tecs

def make_zeta_jones (ns, tecs, sources):
  stations = Context.array.stations()
  for src in sources:
    for s in stations:
      ns.Z(src.name,s) << Meq.Polar(1,-25*3e8*ns.tecs(src.name,s)/Meq.Freq())
  return ns.Z

TDLCompileOption('TEC0',"Base TEC value",[0,5,10],more=float);

TDLCompileMenu('Sine TID model options',
  TDLOption('tid_x_ampl_0',"Relative TID-X amplitude at t=0",[0,0.01,0.02,0.05,0.1],more=float),
  TDLOption('tid_x_ampl_1hr',"Relative TID-X amplitude at t=1hr",[0,0.002,0.01,0.02,0.05,0.1],more=float),
  TDLOption('tid_x_size_km',"TID-X size, in km",[25,50,100,200,1000],more=int),
  TDLOption('tid_x_speed_kmh',"TID-X speed, in km/h",[25,50,100,200,300,500],more=int),
  TDLOption('tid_y_ampl_0',"Relative TID-Y amplitude at t=0",[0,0.01,0.02,0.05,0.1],more=float),
  TDLOption('tid_y_ampl_1hr',"Relative TID-Y amplitude at t=1hr",[0,0.002,0.01,0.02,0.05,0.1],more=float),
  TDLOption('tid_y_size_km',"TID-Y size, in km",[25,50,100,200,1000],more=int),
  TDLOption('tid_y_speed_kmh',"TID-Y speed, in km/h",[25,50,100,200,300,500],more=int))
