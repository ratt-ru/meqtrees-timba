#!/usr/bin/python

import math

##############################################
### common definitions for the GUI
### and utility functions
##############################################

# GUI Zoom Modes
GUI_ZOOM_NONE=0
GUI_ZOOM_WINDOW=1 # turn on by menu selection
GUI_ZOOM_START=2 # turn on by first mouse click, after ZOOM_WINDOW
GUI_SELECT_WINDOW=3 # turn on by menu, window for selecting sources
GUI_SELECT_START=4 # turn on by first mouse click, after SELECT_WINDOW

# after the first mouse  click, in ZOOM_WINDOW mode, draw zoom window (show())
# after the mouse released in this mode, set zoom mode to GUI_ZOOM_WINDOW
# and zoom, hide zoom window. by menu selection, can set to GUI_ZOOM_NONE


# define constants for RTTI values of special canvasview objects
POINT_SOURCE_RTTI=1001
PATCH_RECTANGLE_RTTI=1002
PATCH_IMAGE_RTTI=1003

# PUnit types
POINT_TYPE= 0
PATCH_TYPE= 1


######## binary search
def bin_search(xarr,x,i_start,i_end):
  # xarr: [-inf,...,+inf] array so x must be within, also xarr 
  #  must be sorted
  # x: the value to search for
  # i_start,i_end: indices of the array to search for x,
  #  at start, these will be [0,len(xarr)-1]
  # return k, such that x_{k} <= x < x_{k+1}
  # in case an error, return -1

  # trivial case
  if i_start==i_end:
   if  xarr[i_start]==x:
     return i_start
   else:
     print "bin search error 1"
     return -1

  # trivial case with length 2 array
  if i_end==i_start+1:
   if x>=xarr[i_start] and\
     x<xarr[i_end]:
    return i_start
   else:
    print "bin search error 2"
    return -2

  # compare with the mid point
  i=(i_start+i_end)/2
  if x >=xarr[i] and\
     x<xarr[i+1]:
   return i
  else:
   # go to lower half or the upper half of array
   if x < xarr[i]:
    return bin_search(xarr,x,i_start,i)
   else:
    return bin_search(xarr,x,i,i_end)


  # will not get here
  print "bin search error 3"
  return -3



####### Radians to RA=[hr,min,sec]
## Rad=(hr+min/60+sec/60*60)*pi/12
def radToRA(rad):
  tmpval=rad*12.0/math.pi
  hr=int(tmpval)
  tmpval=tmpval-hr
  tmpval=tmpval*60
  mins=int(tmpval)
  tmpval=tmpval-mins
  tmpval=tmpval*60
  sec=int(tmpval)
  return [hr%24,mins%60,sec%60]

####### Radians to Dec=[hr,min,sec]
## Rad=(hr+min/60+sec/60*60)*pi/180
def radToDec(rad):
  tmpval=rad*180.0/math.pi
  hr=int(tmpval)
  tmpval=tmpval-hr
  tmpval=tmpval*60
  mins=int(tmpval)
  tmpval=tmpval-mins
  tmpval=tmpval*60
  sec=int(tmpval)
  return [hr%180,mins%60,sec%60]


########## metric form
### [0,1000)  -
### [1000,1000000) /10^3 k
### [10^6,10^9) /10^6 M
### [10^9,10^12) /10^9 G
### [10^12,..) /10^12 T
# input value=val, format string=format
# output, value+suffix (k,M,G,T)
def stdForm(val,format):
 vl=abs(val)
 if vl <1e3:
  tmpstr=" "
  vlformat=format%vl
 elif vl<1e6:
  tmpstr="k"
  vlformat=format%(vl/1e3)
 elif vl<1e9:
  tmpstr="M"
  vlformat=format%(vl/1e6)
 elif vl<1e12:
  tmpstr="G"
  vlformat=format%(vl/1e9)
 else:
  tmpstr="T"
  vlformat=format%(vl/1e12)

 return [vlformat,tmpstr]

