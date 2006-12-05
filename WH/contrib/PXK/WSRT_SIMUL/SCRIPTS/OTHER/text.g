#! /bin/bash -f


#http://star-www.rl.ac.uk/star/dvi/sc15.htx/node10.html

#Special characters inside PGPLOT text strings

#All escape sequences start with a backslash character ``\''. The following escape sequences are defined:

 #   \u Start a superscript, or end a subscript 
 #   \d Start a subscript, or end a superscript 
 #   \b Do not advance text pointer after plotting the previous character 
 #   \fn Switch to Normal font (1) 
 #   \fr Switch to Roman font (2) 
 #   \fi Switch to Italic font (3) 
 #   \fs Switch to Script font (4) 
 #   \\ Print a backslash character ``\'' 
 #   \x Multiplication sign ($\times$)
 #   \. Centered dot ($\cdot$)
 #   \A Ångström symbol (Å) 
 #   \gx Greek letter corresponding to roman letter x 
 #   \mn 
 #   \mnn Standard graph marker number n or nn (1-31) 
 #   \(nnnn) Character number nnnn (1 to 4 decimal digits) from the Hershey character set; the closing parenthesis may be omitted if the next character is neither a digit nor ``)''. This makes a number of special characters (e.g. mathematical, musical, astronomical, and cartographical symbols) available. See Appendix B in the PGPLOT manual for a list of available characters. 



system.resources.memory := 512


include 'pgplotter.g';                   # initialize pgplotter tool

ang:=[0:90];                             # create vector of angles (degrees)
beta:=0.75+[1:9]/40;                     # create vector of velocities

nang:=shape(ang);                        # store length of data vectors
nbeta:=shape(beta);

D:=array(0.0,nbeta,nang);                # create array, initialized with 0.0,
                                         #  of shape nbeta X nang to hold 
                                         #  Doppler factors

for (i in 1:nbeta) {                     # calculate D for all ang, beta
 gamma:=1.0/sqrt(1-beta[i]^2);
 for (j in 1:nang) {
  D[i,j]:=1.0/(gamma*(1-beta[i]*cos(ang[j]*pi/180.0)));
 }
}

mypg:=pgplotter();                       # create pgplotter tool

mypg.env(xmin=0.0,                       # draw axes with sensible limits
         xmax=90.0,
         ymin=0.5*min(D),
         ymax=1.1*max(D),
         just=0,
         axis=0);

mypg.lab(xlbl='LOS Angle',               # add axes labels and title
         ylbl='Doppler Factor',
         toplbl='Doppler Factor vs. LOS Angle');

mypg.sci(3);                             # change color to green

for (i in 1:nbeta) {                     # for each beta....

 mypg.line(xpts=ang,                     #  plot D(ang)
           ypts=D[i,]);

 mypg.ptxt(x=ang[3],                     #  label each line
           y=D[i,3],
           angle=20,
           fjust=0,
           text=spaste('\\g=', '\tex{\delta}'));
           #text=spaste('\\g=',as_string(beta[i])));

}



 mypg.ptxt(x=50, y=8,angle=0,fjust=0, text=spaste('\\gd', as_string(1234)));
 mypg.ptxt(x=50, y=7,angle=0,fjust=0, text=spaste('\\ge', as_string(1234)));
 mypg.ptxt(x=50, y=6,angle=0,fjust=0, text=spaste('\\gt', as_string(1234)));
 mypg.ptxt(x=50, y=5,angle=0,fjust=0, text=spaste('\\gg', as_string(1234)));
 mypg.ptxt(x=50, y=4,angle=0,fjust=0, text=spaste('\\gm', as_string(1234)));

















#OUTPUT:
# (only a plot)