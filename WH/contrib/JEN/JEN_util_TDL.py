#   ../Timba/PyApps/test/JEN_util_TDL.py:  
#   JEN utility functions for TDL scripts

# preamble
from Timba.TDL import *
from Timba.Meq import meq
from random import *
from numarray import *
from copy import deepcopy

from JEN_forest_state import *
from JEN_util import *
# from JEN.JEN_util import *


#=======================================================================
# Display Timba NodeScope object (ns):

def JEN_display_NodeScope (ns, txt='<txt>'):
    print '\n*** display of NodeScope (',txt,'):'
    print dir(ns)
    ns.Resolve()
    JEN_display (ns.AllNodes(),'NodeScope.AllNodes()', full=1)
    JEN_display (ns.RootNodes(),'NodeScope.RootNodes()', full=1)
    print

#-----------------------------------------------------------------------
# Display Timba NodeStub object (node):

def JEN_display_NodeStub (node, txt='<txt>', trace=2):
    print '\n*** display of NodeStub (',txt,'):'
    print ' - node:',node
    print ' - node.basename = ',node.basename
    print ' - node.classname = ',node.classname
    print ' - node.children = ',node.children
    print ' - node.quals = ',node.quals
    print ' - node.kwquals = ',node.kwquals
    print ' - node.bind = ',node.bind
    print ' - node.initrec = ',node.initrec
    print ' - node.parents = ',node.parents
    print ' - node.scope = ',node.scope
    print ' - node.initialized = ',node.initialized
    print ' - node.slots = ',node.slots
    # print ' - dir(node) = ',dir(node)
    for i in range(len(node.children)):
      c = node.children[i];
      print 'child',i,':',c.__class__, len(c), c[0],c[1]
      print '  ',dir(c)
    JEN_display_subtree (node, trace=trace)
    print
    


#==================================================================================
# Recursively display the subtree underneath a NodeStub object (node):
#==================================================================================

def JEN_display_subtree (node, txt='<txt>', level=0,
                         recurse=1000, count={}, full=0):
  indent = level*'..'
  total = '_total_count'
  klasses = '_classes'
  if level == 0:
    print
    print '** TDL subtree (',txt,') ( recurse =',recurse,'):'
    print level,indent,node,'  ',node.initrec()
    if not full: print '   (use full=1 to display the subtree itself)'
    key = str(node)
    count = {}
    count[key] = 1
    count[total] = 1
    count[klasses] = {}
    count[klasses][node.classname] = 1
    if recurse>0:
      for i in range(len(node.children)):
        JEN_display_subtree (node.children[i], level=level+1,
                             recurse=recurse-1, count=count, full=full)
    print '** some subtree statistics:'
    for klass in count[klasses].keys():
      print '**   class:',klass,':',count[klasses][klass]
    print '** total nr of nodes scanned:',count[total]
    print

  else:
    if full: print level,indent,node[0],':',node[1],
    key = str(node[1])
    if key in count.keys():
      count[key] += 1
      if full: print '      (see above)'
    else:
      count[key] = 1
      count[total] += 1
      klass = node[1].classname
      if not count[klasses].has_key(klass): count[klasses][klass] = 0
      count[klasses][klass] += 1
      rr = node[1].initrec()
      if len(rr.keys()) > 1:
        rr = rr.copy()
        rr.__delitem__('class')
        if full: print '  ',rr,
      if recurse>0:
        if full: print
        for i in range(len(node[1].children)):
          JEN_display_subtree (node[1].children[i], level=level+1,
                               recurse=recurse-1, count=count, full=full)
        if 0:
          # later, not yet available....
          for i in range(len(node[1].step_children)):
            JEN_display_subtree (node[1].stepchildren[i], level=level+1,
                                 recurse=recurse-1, count=count, full=full)
          
      else:
        if full: print '      (further recursion inhibited)'




#===============================================================================
# Math functions:
#===============================================================================

#----------------------------------------------------------------------
# Make sure that the funklet is a funklet.
# Perturb the c00 coeff, if required

# array([[1,.3,.1],[.3,.1,0.03]])

def JEN_funklet (funkin, mean=0, stddev=0, trace=0):
  if isinstance(funkin, dmi_type('MeqFunklet')):
    funklet = deepcopy(funkin)
  elif isinstance(funkin,type(array(0))):
    funklet = meq.polc(deepcopy(funkin))
  else:
    funklet = meq.polc(deepcopy(funkin))

  if mean != 0 or stddev > 0:
    if (funklet['coeff'].rank==0):
        funklet['coeff'] += gauss(mean, stddev)
    elif (funklet['coeff'].rank==1):
        funklet['coeff'][0] += gauss(mean, stddev)
    elif (funklet['coeff'].rank==2):
        funklet['coeff'][0,0] += gauss(mean, stddev)
    elif (funklet['coeff'].rank==3):
        funklet['coeff'][0,0,0] += gauss(mean, stddev)
    elif (funklet['coeff'].rank==4):
        funklet['coeff'][0,0,0,0] += gauss(mean, stddev)
    else:
        print '\n** JEN_funklet error: rank =',funklet['coeff'].rank

  if 1:
    print '** JEN_funklet() ->',funklet
  return funklet


#----------------------------------------------------------------------
# Helper function to calculate unop(wavelength):

def JEN_wavelength (ns, unop=0, trace=0):
  clight = 2.997925e8
  freq = ns.freq << Meq.Freq()
  wvl = ns.wavelength << (2.997925e8/freq)
  if isinstance(unop, str):
    wvl = (ns << getattr(Meq,unop)(wvl))
  if trace: JEN_display_subtree(wvl,'wvl', full=1)
  return wvl

#------------------------------------------------------------
#------------------------------------------------------------
# Helper function to make a 2x2 rotation matrix

def JEN_rotation_matrix (ns, angle=0, name=0, trace=0):
    if trace: print '\n** JEN_rotation_matrix(',angle,name,')'
    different_angles = 0
    if isinstance(angle, (list, tuple)):
        a1 = angle[0]
        a2 = a1
        if len(angle)>1:
            different_angles = 1
            a2 = angle[1]
    else:
        a1 = angle
        a2 = a1
            
    if different_angles:
        cos1 = (ns << Meq.Cos(a1))
        cos2 = (ns << Meq.Cos(a2))
        sin2 = (ns << Meq.Sin(a2))
        sin1 = (ns << Meq.Sin(a1))
        sin1 = (ns << Meq.Negate(sin1))
    else:
        cos1 = (ns << Meq.Cos(a1))
        cos2 = cos1
        sin2 = (ns << Meq.Sin(a1))
        sin1 = (ns << Meq.Negate(sin2))
        
    if not isinstance(name, str): name = 'rotation_matrix'
    # rotmat = (ns << Meq.Composer(
    rotmat = (ns[name] << Meq.Composer(
        children=[cos1, sin1, sin2, cos2], dims=[2,2]))

    if trace: JEN_display_subtree(rotmat,'rotation_matrix', full=1)
    return rotmat

#------------------------------------------------------------
# Helper function to make a 2x2 ellipticity matrix

def JEN_ellipticity_matrix (ns, angle=0, name=0, trace=0):
    different_angles = 0
    if isinstance(angle, (list, tuple)):
        a1 = angle[0]
        a2 = a1
        if len(angle)>1:
            different_angles = 1
            a2 = angle[1]
    else:
        a1 = angle
        a2 = a1
            
    if different_angles:
        # NB: It is ESSENTIAL to adopt the new TDL syntax
        cos1 = (ns << Meq.Cos(a1))
        cos2 = (ns << Meq.Cos(a2))
        sin1 = (ns << Meq.Sin(a1))
        sin2 = (ns << Meq.Sin(a2))
        isin1 = (ns << Meq.ToComplex(0, sin1))
        isin2 = (ns << Meq.ToComplex(0, sin2))
        isin2 = (ns << Meq.Conj(isin2))

    else:
        cos1 = (ns << Meq.Cos(a1))
        cos2 = cos1
        sin = (ns << Meq.Sin(a1))
        isin2 = (ns << Meq.ToComplex(0, sin))
        isin1 = isin2
        
    if not isinstance(name, str): name = 'ellipticity_matrix'
    # NB: It is ESSENTIAL to adopt the new TDL syntax
    rotmat = (ns[name] << Meq.Composer(
        children=[cos1, isin1, isin2, cos2], dims=[2,2]))

    if trace: JEN_display_subtree(rotmat,'ellipticity_matrix', full=1)
    return rotmat




#===============================================================================
# Test function:
#===============================================================================

if __name__ == '__main__':
  print 
  ns = NodeScope()

  if 0:
    print gauss(0, 0.1)
    print gauss(0, 0.1)
    print gauss(0, 0.1)
    print gauss(0, 0.1)
    print gauss(0, 0.1)

  if 1:
    a = 0
    a = array([[1,0.1],[0.1,0]])
    print '=',a
    print type(a)
    array_class = type(array(0))
    print array_class
    print 'test:',isinstance(a,array_class)
    # print dir(a)
    JEN_funklet (a, stddev=0.1, trace=1)
    JEN_funklet (a, stddev=0.1, trace=1)
    JEN_funklet (a, stddev=0.1, trace=1)

  if 0:
    xxx = ns.xxx << Meq.Parm(6)
    print ns.xxx
    print xxx
    print type(xxx)
    print type(ns.xxx)
    print dir(ns.xxx)


  if 0:
    xxx = ns.xxx << Meq.Parm(6)
    print xxx
    print xxx.initrec()
    xxx = JEN_unop(ns, ['Transpose', 'Cos'], xxx) 
    print xxx
    print xxx.initrec()

  if 0:
    aa = record(a=4, b=5)
    aa = dict(a=4, b=5)
    print aa
    print dir(aa)
    print aa.has_key('a')
    print aa.has_key('e')

  if 0:
    funklet = 0
    print 'funklet (before) =',funklet
    for i in range(10):
      JEN_funklet (funklet, mean=-3, stddev=1, trace=1)
    print 'funklet (after) =',funklet

  if 0:
      parm = ns.parm << Meq.Parm(6)
      cos1 = ns.cos1 << Meq.Cos(6)
      cos2 = ns.cos2 << Meq.Cos(ns.parm)
      JEN_display_subtree(cos1,'cos1', full=1)
      JEN_display_subtree(cos2,'cos2', full=1)
      
  if 0:
    JEN_unop_wavelength (ns, unop='Sqr', trace=1)

  if 0:
    angle1 = ns.angle1(x=4, y=5) << Meq.Constant(3)
    # angle2 = ns.angle2(y=5) << Meq.Constant(-1)
    angle2 = -1
    # JEN_rotation_matrix (ns, angle1, trace=1)
    JEN_rotation_matrix (ns, [angle2], trace=1)
    JEN_rotation_matrix (ns, [angle1, angle2], name='diff_angles', trace=1)

  if 0:
    angle1 = ns.angle1(x=4, y=5) << Meq.Constant(3)
    angle2 = ns.angle2(y=5) << Meq.Constant(-1)
    JEN_ellipticity_matrix (ns, angle1, trace=1)
    JEN_ellipticity_matrix (ns, [angle2], trace=1)
    JEN_ellipticity_matrix (ns, [angle1, angle2], name='diff_angles', trace=1)

  if 0:
    # nsub = ns.Subscope(record(q='3c84'))
    nsub = ns.Subscope('3c84', g=3, h=9)
    ns1 = nsub.ns1(s1='s1') << Meq.Constant(-1)
    print ns1

  if 0:
    print '\n** Test of new TDL unop functionality:'
    s1 = '1'
    s2 = '5'
    # s1 = 1
    # s2 = 5
    q = '3c84'
    
    ns1 = ns.ns1(s1=s1) << Meq.Constant(-1)
    ns2 = ns.ns2(s2=s2) << Meq.Constant(-2)
    ns12 = ns.ns12(s1=s1, s2=s2) << Meq.Constant(-6)

    ns1q = ns.ns1q(s1=s1, q=q) << Meq.Constant(-3)
    ns2q = ns.ns2q(s2=s2, q=q) << -4
    ns12q = ns.ns12q(s1=s1, s2=s2, q=q) << Meq.Constant(-7)
    # ns2q = ns.ns2q(s2=s2, q=q) << Meq.Constant(-5)
    rr = record(a=2, b=6, c='c')

    print ns1
    print ns2
    print ns12
    print ns1q
    print ns2q
    print ns12q

    print 'ns << Meq.Sin(ns1):',ns.xxx(**rr) << Meq.Sin(ns1)

    print 'ns << Meq.Sin(ns1):',ns << Meq.Sin(ns1)
    print 'ns << Meq.Sin(ns << Meq.Cos(ns1)):',ns << Meq.Sin(ns << Meq.Cos(ns1))

    print 'ns << Meq.Composer(ns1,ns2):',ns << Meq.Composer(ns1,ns2)
    print 'ns << Meq.Matrix22(ns1,ns2,ns12,ns1q):',ns << Meq.Matrix22(ns1,ns2,ns12,ns1q)

    print 'ns << (ns12q * ns1):',ns << (ns12q * ns1)
    print 'ns << (ns12q * ns1 / ns2):',ns << (ns12q * ns1 / ns2)

  if 0:
    print array([[0,0.1],[0.1,0]])

  if 0:
    JEN_display_NodeScope(ns, 'test')

