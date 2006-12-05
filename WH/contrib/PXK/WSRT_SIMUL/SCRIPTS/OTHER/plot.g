#! /bin/bash -f
# glish/aips++ script to check the data
# CREATION: 2006.10.04

pragma include once
include 'pgplotter.g'

x := 1:100
y := sin(x/5)
y2 := cos(x/3)
pg:=pgplotter()
pg.plotxy1(x,y,'X','Y','Sample')
pg.plotxy1(x,y2)              # Adds to plot with new colour
#pg.done()



#
x:=(-100:100)/10
y:=sin(x)*exp(x/5)
#
pg:=pgplotter()
pg.env(-10,10,-7,7,1,0)
pg.lab('X Axis','Y Axis','A Clever Plot')
pg.sci(4)   # set color index [2=red, 3=green, 4=blue]
pg.sls(4)   # set line style
pg.line(x,y)
pg.sls(1)
pg.sci(2)
pg.ptxt(-8,5,0,0,'Runaway sinusoid')
pg.arro(-6,4.5,0,1)




# Create some data to plot:
x1 := 1:100; y1 := (x1/10)^2
x2 := 1:50; y2 := log(x2)
x3 := -1000:1000
y3 := sin(x3/100)*cos(x3/100)
im := array(0,100,100)
for (i in 1:100) 
 for (j in 1:100)
  { 
  im[i,j] := i/50+sin(j/10)+random(0,10)/10
  }
# and plot the 4-panels:
pg := pgplotter()
pg.subp(2,2)
pg.env(min(x1),max(x1),min(y1),max(y1),1,0)
pg.line(x1,y1)
pg.env(min(x2),max(x2),min(y2),max(y2),0,0)
pg.line(x2,y2)
pg.env(min(x3),max(x3),min(y3),max(y3),0,0)
pg.line(x3,y3)
pg.env(1,100,1,100,1,0)
pg.gray(im,-1,4,[0,1,0,0,0,1])





pg := pgplotter();
x := 1:100;
y1a := sin(x/10);
y1b := cos(x/10);
y2 := sqrt(x);
pg.plotxy1(x,y1a,'X Index','Sine Function','Title');
pg.plotxy1(x,y1b,,'Cosine Function');
pg.plotxy2(x,y2,,'SQRT Function');
pg.ptxt(105,5.5,270,0.5,'SQRT (X)');







# Create some data to plot:
x1 := 1:100; 
y1 := sin(x1)
x2 := 1:100; 
y2 := log(x2)

# and plot the 4-panels:
pg := pgplotter()
pg.subp(2,1)
# xmin, xmax, ymin, ymax, square, axis [-2 -> 2, 20, 20, 30]
pg.env(min(x1),max(x1),min(y1),max(y1),0,0) 
pg.line(x1,y1)
pg.env(min(x2),max(x2),min(y2),max(y2),0,0)
pg.line(x2,y2)#,plotlines=F, ptsymbol=4)
#pg.lab('X Axis','Y Axis','Title')

