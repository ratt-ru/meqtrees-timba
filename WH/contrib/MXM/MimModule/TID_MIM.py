from Timba.TDL import *
from Timba.Meq import meq
from Timba.Contrib.MXM.MimModule  import PiercePoints
import Meow

def compile_options():
    return PiercePoints.compile_options() + [TDLCompileOption("Fac_long","2pi/WaveLength Longitude",[1.,5.,10.],more=float,
                             doc="""Wave = Amp_lon*Sin(lon*factor_lon+a*t)+Amp_lat*Sin(lat*factor_lat+b*t)"""),
            TDLCompileOption("Fac_lat","2pi/WaveLength Lattitude",[1.,5.,10.],more=float,
                             doc="""Wave = Amp_lon*Sin(lon*factor_lon+a*t)+Amp_lat*Sin(lat*factor_lat+b*t)"""),
            TDLCompileOption("T_long","Frequency Longitude (a)",[1.,5.,10.],more=float,
                             doc="""Wave = Amp_lon*Sin(lon*factor_lon+a*t)+Amp_lat*Sin(lat*factor_lat+b*t)"""),
            TDLCompileOption("T_lat","Frequency Lattitude (b)",[1.,5.,10.],more=float,
                             doc="""Wave = Amp_lon*Sin(lon*factor_lon+a*t)+Amp_lat*Sin(lat*factor_lat+b*t)"""),
            TDLCompileOption("Amp_long","Amplitude Longitude",[1.,5.,10.],more=float,
                             doc="""Wave = Amp_lon*Sin(lon*factor_lon+a*t)+Amp_lat*Sin(lat*factor_lat+b*t)"""),
            TDLCompileOption("Amp_lat","Amplitude Lattitude",[1.,5.,10.],more=float,
                             doc="""Wave = Amp_lon*Sin(lon*factor_lon+a*t)+Amp_lat*Sin(lat*factor_lat+b*t)""")];


    



class MIM(PiercePoints.PiercePoints):
    """Create MIM_model with travelling waves as function of the pierc points"""


    def __init__(self,ns,name,sources,stations=None,height=300,ref_station=None,tags="iono"):
        PiercePoints.PiercePoints.__init__(self,ns,name,sources,stations,height);
        self.ref_station=ref_station;
        self._add_parm(name="Amp_long",value=Meow.Parm(Amp_long),tags=tags)
        self._add_parm(name="Amp_lat",value=Meow.Parm(Amp_lat),tags=tags)
        self._add_parm(name="Fac_long",value=Meow.Parm(Fac_long),tags=tags)
        self._add_parm(name="Fac_lat",value=Meow.Parm(Fac_lat),tags=tags)
        self._add_parm(name="T_long",value=Meow.Parm(T_long),tags=tags)
        self._add_parm(name="T_lat",value=Meow.Parm(T_lat),tags=tags)


    def make_time(self):
        if not self.ns['time'].initialized():
            self.ns['time'] << Meq.Time();
        return self.ns['time'];

    def make_tec(self):
        self.make_longlat_pp(ref_station=self.ref_station);
        time = self.make_time();
        ns = self.ns;
        lon = ns['pp']('lon');
        lat = ns['pp']('lat');

        
        ALo= self._parm("Amp_long");
        ALa= self._parm("Amp_lat");
        FLo= self._parm("Fac_long");
        FLa= self._parm("Fac_lat");
        TLo= self._parm("T_long");
        TLa= self._parm("T_lat");



        for station in self.stations:
            for src in self.src:
                tec = ns['tec'](src,station);
                sec = ns['sec'](src,station);
                if not tec.initialized():
                    Mim = ALo*Meq.Sin(lon(src,station)*FLo+TLo*time)+ALa*Meq.Sin(lat(src,station)*FLa+TLa*time)*sec;
                    tec<<Mim 
        
        
        return  ns['tec'];
