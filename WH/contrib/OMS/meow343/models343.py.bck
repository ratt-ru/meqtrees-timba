from Timba.TDL import *
import Meow

TDLCompileMenu("Source model options",
  TDLOption("_343_1_Iorder","3C343.1 I freq degree",[0,1,2,3],more=int,default=1),
  TDLOption("_343_1_Qorder","3C343.1 Q freq degree",[0,1,2,3],more=int,default=1),
  TDLOption("_343_Iorder","3C343 I freq degree",[0,1,2,3],more=int,default=3),
  TDLOption("_343_Qorder","3C343 Q freq degree",[0,1,2,3],more=int,default=3)
);

def m343_bright_duo (ns,tablename=''):
  return [ 
    Meow.PointSource(ns,name="3C343.1",
                     I=Meow.Parm(1,freq_deg=_343_1_Iorder,table_name=tablename),
                     Q=Meow.Parm(0,freq_deg=_343_1_Qorder,table_name=tablename),
                     direction=(4.356645791155902,1.092208429052697)),
    Meow.PointSource(ns,name='3C343',
                     I=Meow.Parm(1,freq_deg=_343_Iorder,table_name=tablename),
                     Q=Meow.Parm(0,freq_deg=_343_Qorder,table_name=tablename),
                     direction=(4.3396003966265599,1.0953677174056471)),
  ];

def m343_bright_duo_spi (ns,tablename=''):
  return [ 
    Meow.PointSource(ns,name="3C343.1",
                     I=Meow.Parm(1,freq_deg=_343_1_Iorder,table_name=tablename),
                     Q=Meow.Parm(0,freq_deg=_343_1_Qorder,table_name=tablename),
                     spi=Meow.Parm(0,table_name=tablename),
                     direction=(4.356645791155902,1.092208429052697)),
    Meow.PointSource(ns,name='3C343',
                     I=Meow.Parm(1,freq_deg=_343_Iorder,table_name=tablename),
                     Q=Meow.Parm(0,freq_deg=_343_Qorder,table_name=tablename),
                     spi=Meow.Parm(0,table_name=tablename),
                     direction=(4.3396003966265599,1.0953677174056471)),
  ];
