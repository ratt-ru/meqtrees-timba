from Timba.TDL import *
from Timba.Meq import meq
from Timba.Contrib.MXM.MimModule.PiercePoints import *
import Meow

R_earth=6378135. # Radius (m) of earth at somewhere.
HH = 300000.     # Altitude (m) of TID waves 

def compile_options():
    return [TDLCompileOption("TEC0","Zero offset TEC value",[1.,5.,10.],more=float,
                             doc="""TEC0"""),
            TDLCompileOption("Wavelength_x","Wavelength Longitude (km)",[250.,500.,1000.],more=float),
            TDLCompileOption("Wavelength_y","Wavelength Lattitude (km)",[250.,500.,1000.],more=float),
            TDLCompileOption("Speed_x","Phase speed Longitude (km/h)",[300.,600.,1200.],more=float),
            TDLCompileOption("Speed_y","Phase speed Lattitude (km/h)",[300.,600.,1200.],more=float),
            TDLCompileOption("Amp_x","Relative amplitude Longitude",[0.0,0.01,0.02,0.05,0.1],more=float),
            TDLCompileOption("Amp_y","Relative amplitude Lattitude",[0.0,0.01,0.02,0.05,0.1],more=float)];

    
# include TID in x and y direction as two orthogonal sine-waves TECx and TECy: TEC = Sec(z)*(TECx+TECy)+TEC0
# Wave in one direction TECx = TEC(x,t) = A(x)*TEC0*sin[(2pi/1000*lambda)*(x-v*t/3.6)]
# Variabes in these equations:
#  - TEC0 = absolute TEC value on which variations are build
#  - A(x,y) = wave amplitude in x, y direction relative to TEC0
#  - lambda(x,y) = wavelength in x, y direction in km
#  - v(x,y) = phase speed in x, y direction in km/h
#  - phi0 = zero-point phase offset, for the time being this is set to 0 in both x and y
#
# Units for x and y should be in meters relative to the reference antenna zenith pierce point

class TID_MIM(PiercePoints):
    """Create MIM_model with travelling waves as function of the pierc points"""


    def __init__(self,ns,name,sources,stations=None,height=300,ref_station=1,tags="iono"):
        PiercePoints.__init__(self,ns,name,sources,stations,height);
        self.ref_station=ref_station;
        self._add_parm(name="TEC0",value=Meow.Parm(TEC0),tags=tags)
        self._add_parm(name="Amp_x",value=Meow.Parm(Amp_x),tags=tags)
        self._add_parm(name="Amp_y",value=Meow.Parm(Amp_y),tags=tags)
        self._add_parm(name="Wavelength_x",value=Meow.Parm(Wavelength_x),tags=tags)
        self._add_parm(name="Wavelength_y",value=Meow.Parm(Wavelength_y),tags=tags)
        self._add_parm(name="Speed_x",value=Meow.Parm(Speed_x),tags=tags)
        self._add_parm(name="Speed_y",value=Meow.Parm(Speed_y),tags=tags)


    def make_time(self):
        if not self.ns['time'].initialized():
            self.ns['time'] << Meq.Time();
        return self.ns['time'];

    def make_tec(self,tags=[]):
        self.make_xy_pp(ref_station=self.ref_station);
        time = self.make_time();
        ns = self.ns;
        # Get the pp positions
        # I should be able to use x and y directly here
        #lon = ns['pp']('lon');
        #lat = ns['pp']('lat');
        # Why does this not work? Work-around below does work
        PP_x = ns['pp']('x');
        PP_y = ns['pp']('y');

        
        T0= self._parm("TEC0");
        Ax= self._parm("Amp_x");
        Ay= self._parm("Amp_y");
        Wx= self._parm("Wavelength_x");
        Wy= self._parm("Wavelength_y");
        Vx= self._parm("Speed_x");
        Vy= self._parm("Speed_y");

        for station in self.stations:
            for src in self.src:
                tec = ns['tec'](src,station);
                sec = ns['sec'](src,station);
                if not tec.initialized():
                    # Work-around to get x,y positions for pierce-point
                    tec << T0 + sec*\
                        (Ax*T0*Meq.Sin((2*math.pi/(1000*Wx))*(PP_x(src,station)-Vx*time/3.6)) + \
                         Ay*T0*Meq.Sin((2*math.pi/(1000*Wy))*(PP_y(src,station)-Vy*time/3.6)))
                        
        return  ns['tec'];
