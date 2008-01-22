from Timba.TDL import *
from Timba.Meq import meq
from Timba.Contrib.MXM.MimModule.PiercePoints import *
import Meow

#Include 2 wave TID, giving for each wave the wavelength, direction, speed
#and relative amplitude. The phase offset for both waves is set to 0.
#


def compile_options():
    return [TDLCompileOption("TEC0","Zero offset TEC value",[1.,5.,10.],more=float,),
            TDLCompileOption("Wavelength_1","Wavelength first wave (km)",[250.,500.,1000.],more=float),
            TDLCompileOption("Wavelength_2","Wavelength second wave (km)",[250.,500.,1000.],more=float),
            TDLCompileOption("Speed_1","Speed first wave (km/h)",[300.,600.,1200.],more=float),
            TDLCompileOption("Speed_2","Speed second wave (km/h)",[300.,600.,1200.],more=float),
            TDLCompileOption("Theta_1","Direction first wave (degrees)",[15.,30.,45.,60.,75.,90.],more=float,doc="""Angle of propagation, counter clock-wise from East"""),
            TDLCompileOption("Theta_2","Direction second wave (degrees)",[15.,30.,45.,60.,75.,90.],more=float,doc="""Angle of propagation, counter clock-wise from East"""),
            TDLCompileOption("Amp_1","Relative amplitude first wave",[0.0,0.01,0.02,0.05,0.1],more=float),
            TDLCompileOption("Amp_2","Relative amplitude second wave",[0.0,0.01,0.02,0.05,0.1],more=float)];

    
class TID_MIM(PiercePoints):
    """Create MIM_model with travelling waves as function of the pierc points"""


    def __init__(self,ns,name,sources,stations=None,height=300,ref_station=1,tags="iono"):
        PiercePoints.__init__(self,ns,name,sources,stations,height);
        self.ref_station=ref_station;
        self._add_parm(name="TEC0",value=Meow.Parm(TEC0),tags=tags)
        self._add_parm(name="Amp_1",value=Meow.Parm(Amp_1),tags=tags)
        self._add_parm(name="Amp_2",value=Meow.Parm(Amp_2),tags=tags)
        self._add_parm(name="Wavelength_1",value=Meow.Parm(Wavelength_1),tags=tags)
        self._add_parm(name="Wavelength_2",value=Meow.Parm(Wavelength_2),tags=tags)
        self._add_parm(name="Speed_1",value=Meow.Parm(Speed_1),tags=tags)
        self._add_parm(name="Speed_2",value=Meow.Parm(Speed_2),tags=tags)
        self._add_parm(name="Theta_1",value=Meow.Parm(Theta_1),tags=tags)
        self._add_parm(name="Theta_2",value=Meow.Parm(Theta_2),tags=tags)


    def make_time(self):
        if not self.ns['time'].initialized():
            self.ns['time'] << Meq.Time();
        return self.ns['time'];

    def make_tec(self,tags=[]):
        self.make_xy_pp(ref_station=self.ref_station);
        time = self.make_time();
        ns = self.ns;
        # Get the pp positions
        PP_x = ns['pp']('x');
        PP_y = ns['pp']('y');

        
        T0= self._parm("TEC0");
        A1= self._parm("Amp_1");
        A2= self._parm("Amp_2");
        W1= self._parm("Wavelength_1");
        W2= self._parm("Wavelength_2");
        V1= self._parm("Speed_1");
        V2= self._parm("Speed_2");
        # convert direction angle to radians
        TH1= self._parm("Theta_1")*math.pi/180;
        TH2= self._parm("Theta_2")*math.pi/180;

        for station in self.stations:
            for src in self.src:
                tec = ns['tec'](src,station);
                sec = ns['sec'](src,station);
                if not tec.initialized():
                    # Work-around to get x,y positions for pierce-point
                    tec << T0 + sec*( \
                  A1*T0*Meq.Cos((2*math.pi/(1000*W1))*(Meq.Cos(TH1)*PP_x(src,station)-V1*time/3.6))+\
                  A1*T0*Meq.Cos((2*math.pi/(1000*W1))*(Meq.Sin(TH1)*PP_y(src,station)-V1*time/3.6))+
                  A2*T0*Meq.Cos((2*math.pi/(1000*W2))*(Meq.Cos(TH2)*PP_x(src,station)-V2*time/3.6))+\
                  A2*T0*Meq.Cos((2*math.pi/(1000*W2))*(Meq.Sin(TH2)*PP_y(src,station)-V2*time/3.6)))
                                                
        return  ns['tec'];
