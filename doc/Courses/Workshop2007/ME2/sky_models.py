import math

def Grid9 ():
  return  [( 0,0),(-1.1,-1.03),(-1,0.05),(-1.2,1.07),
         ( 0.01,-.9),( 0.05,.93), 
         ( .97,-.96),( 1.04,0.0399999991011),( 1.001,.999997)];


def PerleyGates ():
  return [
    # point sources
   (0,2),(0,1),(0,0),(0,-1),(0,-1.8),             # middle 
   (-3,2,),(-2,2),(-1,2),(1,2),(2,2),(3,2),       # bottom 
   (-3,-2),(-3,-1),(-3,0),(-3,1),(-3,2),          # left post
   ( 3,-2),( 3,-1),( 3,0),( 3,1),( 3,2),          # right post
   (-2,-1.5),(-1,-2),(1,-2),(2,-1.5),             # top of gates
   # extended sources
   (1.5,0,25,1,.5,math.pi/4),      # right gate blob
   (-1.5,0,25,1,.5,-math.pi/4),    # left gate blob
   (3,-2.5,20,.3,.3,-math.pi/4),       # right post hat
   (-3,-2.5,20,.3,.3,math.pi/4),       # left post hat
  ];

def PerleyGates_ps ():
  return [
    # point sources
   (0,2),(0,1),(0,0),(0,-1),(0,-1.8),             # middle 
   (-3,2,),(-2,2),(-1,2),(1,2),(2,2),(3,2),       # bottom 
   (-3,-2),(-3,-1),(-3,0),(-3,1),(-3,2),          # left post
   ( 3,-2),( 3,-1),( 3,0),( 3,1),( 3,2),          # right post
   (-2,-1.5),(-1,-2),(1,-2),(2,-1.5),             # top of gates
   # extended sources
   (1.5,0),      # right gate blob
   (-1.5,0),    # left gate blob
   (3,-2.5),       # right post hat
   (-3,-2.5),       # left post hat
  ];


  
