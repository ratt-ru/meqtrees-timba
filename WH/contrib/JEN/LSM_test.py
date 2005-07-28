# LSM_test.py

#!/usr/bin/python
from LSM import *
import re
import math
infile=open('3C343.txt','r')
all=infile.readlines()
infile.close()

# regexp pattern
pp=re.compile(r"""
   ^(?P<col1>\S+)  # column 1 'NVSS'
   \s*             # skip white space
   (?P<col2>[A-Za-z]\w+\+\w+)  # source name i.e. 'J163002+631308'
   \s*             # skip white space
   (?P<col3>\d+)   # RA angle - hr 
   \s*             # skip white space
   (?P<col4>\d+)   # RA angle - min 
   \s*             # skip white space
   (?P<col5>\d+(\.\d+)?)   # RA angle - sec
   \s*             # skip white space
   (?P<col6>\d+(\.\d+)?)   # eRA angle - sec
   \s*             # skip white space
   (?P<col7>\d+)   # Dec angle - hr 
   \s*             # skip white space
   (?P<col8>\d+)   # Dec angle - min 
   \s*             # skip white space
   (?P<col9>\d+(\.\d+)?)   # Dec angle - sec
   \s*             # skip white space
   (?P<col10>\d+(\.\d+)?)   # eDec angle - sec
   \s*             # skip white space
   (?P<col11>\d+)   # freq
   \s*             # skip white space
   (?P<col12>\d+(\.\d+)?)   # brightness - Flux
   \s*             # skip white space
   (?P<col13>\d*\.\d+)   # brightness - eFlux
   \s*
   \S+
   \s*$""",re.VERBOSE)

# create empty LSM
l=LSM()

linecount=0
# read each source and insert to LSM
for eachline in all:
 v=pp.search(eachline)
 if v!=None:
   linecount+=1
   #print v.group('col2'), v.group('col12')
   s=Source(v.group('col2'))
   source_RA=float(v.group('col3'))+(float(v.group('col5'))/60.0+float(v.group('col4')))/60.0
   source_RA*=math.pi/12.0
   source_Dec=float(v.group('col7'))+(float(v.group('col9'))/60.0+float(v.group('col8')))/60.0
   source_Dec*=math.pi/180.0
   l.insertSource(s,brightness=eval(v.group('col12')),RA=source_RA,Dec=source_Dec)
 
   #l.dump()
print "Inserted %d sources" % linecount 


# print LSM
#l.dump()

#display LSM
l.display()

