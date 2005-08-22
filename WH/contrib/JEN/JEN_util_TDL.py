#   ../Timba/WH/contrib/JEN/JEN_util_TDL.py:  
#   JEN utility functions for TDL scripts

print '\n',100*'*'
print '** JEN_util_TDL.py    h30jul/h13aug2005'

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

def JEN_display_NodeScope (ns, txt='<txt>', trace=1):
    print '\n*** display of NodeScope (',txt,'):'
    print '** - ns.__class__ -> ',ns.__class__
    print '** - ns.__repr__ -> ',ns.__repr__
    # print '** - ns.__init__() -> ',ns.__init__()              # don't !!
    print '** - ns.__str__ -> ',ns.__str__
    print '** - ns.__new__ -> ',ns.__new__
    print '** - ns.__hash__ -> ',ns.__hash__
    # print '** - ns.__reduce__() -> ',ns.__reduce__()
    # print '** - ns.__reduce_ex__() -> ',ns.__reduce_ex__()
    print '** - ns._name -> ',ns._name
    print '** - ns.name -> ',ns.name
    print '** - ns._constants -> ',ns._constants
    print '** - ns._roots -> ',ns._roots
    print '** - ns.ROOT -> ',ns.ROOT
    print '** - ns.__weakref__ -> ',ns.__weakref__
    print '** - ns.__dict__ -> ',type(ns.__dict__),'[',len(ns.__dict__),']'
    print '** - ns.__contains__ -> ',ns.__contains__
    print '** - ns.GetErrors() -> ',ns.GetErrors()
    # print '** - ns.MakeConstant(1) -> ',ns.MakeConstant(1)
    print '** - ns.MakeUniqueName -> ',ns.MakeUniqueName
    print '** - ns._uniqueName_counters -> ',ns._uniqueName_counters
    print '** - ns.SubScope() -> ',ns.SubScope()
    print '** - ns.Subscope -> ',ns.Subscope                   # takes 2 arguments
    print '** - ns.Resolve() -> ',ns.Resolve()
    print '**'
    print '** - dir(ns) -> ',dir(ns)

    print '**'
    JEN_display (ns.AllNodes(),'ns.AllNodes()', full=1)
    print '** - ns.AllNodes() -> ',type(ns.AllNodes()),'[',len(ns.AllNodes()),']'
    print '** - ns.Repository() -> ',type(ns.Repository()),'[',len(ns.Repository()),']'
    JEN_display (ns.RootNodes(),'ns.RootNodes()', full=1)
    root = ns.RootNodes()
    for key in root.keys():
        JEN_display_subtree (root[key],'root['+key+']', full=1)
        
    print '**'
    print '** - ns.__doc__ -> ',ns.__doc__
    print '*** End of NodeScope ()\n'

   
#==================================================================================
# Helper functions to get specific info from nodestub:
#==================================================================================

#-----------------------------------------------------------------------
# Display Timba NodeStub object (node):

def JEN_display_NodeStub (node, txt='<txt>', trace=1):
    print '\n***** Display of NodeStub (',txt,'):'
    print '** - node:',node
    print '** - node.name -> ',node.name
    print '** - node.basename -> ',node.basename
    print '** - node.classname -> ',node.classname
    print '** - node.quals -> ',node.quals
    print '** - node.kwquals -> ',node.kwquals
    print '** - node.parents -> ',node.parents
    print '** - node.Parents -> ',node.Parents
    print '** - node.scope -> ',node.scope
    print '** - node.slots -> ',node.slots

    print '**'
    print '** - node.initialized() -> ',node.initialized()
    print '** - node.initrec() -> ',node.initrec()
    print '** - node._initrec -> ',node._initrec
    print '** - node.bind -> ',node.bind
    print '** - node._qualify -> ',node._qualify
    print '** - node.qadd() -> ',node.qadd()
    print '** - node.qmerge() -> ',node.qmerge()

    print '**'
    print '** - dir(node) -> ',dir(node)

    print '**'
    print '** - node.__class__ -> ',node.__class__
    print '** - node.__repr__ -> ',node.__repr__
    print '** - node.__str__() -> ',node.__str__()
    print '** - node.__call__() -> ',node.__call__()
    print '** - node.__copy__() -> ',node.__copy__()
    print '** - node.__deepcopy__ -> ',node.__deepcopy__
    print '** - node.__weakref__ -> ',node.__weakref__
    print '** - node.__dict__ -> ',type(node.__dict__),'[',len(node.__dict__),']'
    print '** - node.__module__ -> ',node.__module__
    print '** - node._caller -> ',node._caller
    print '** - node._debuginfo -> ',node._debuginfo

    print '**'
    print '** - node.children (',len(node.children),'):'
    for i in range(len(node.children)):
        c = node.children[i];
        print '**   - child',i,':',c.__class__,' c[0]=',c[0],', c[1]=',c[1]

    print '** - node.stepchildren (',len(node.stepchildren),'):'
    for i in range(len(node.stepchildren)):
        c = node.stepchildren[i];
        print '**   - stepchild',i,':',c.__class__,' sc[0]=',c[0],', sc[1]=',c[1]

    print '**'
    print '** - node.__doc__ -> ',node.__doc__
    print '***** End of NodeStub\n'

 
#-----------------------------------------------------------------------

def JEN_get_initrec (node, trace=0):
    initrec = node.initrec()
    if trace: print '\n** JEN_get_initrec(',node.name,'):',initrec,'\n'
    return initrec

#-----------------------------------------------------------------------

def JEN_get_dims (node, trace=0):
    initrec = JEN_get_initrec (node)
    if not isinstance(initrec, record):
        dims = [-1]
    elif initrec.has_key('dims'):
        dims = initrec.dims
    elif node.classname == 'MeqSpigot':
        dims = [2,2]
    elif node.classname == 'MeqParm':
        dims = [1]
    elif node.classname == 'MeqConstant':
        dims = list(initrec.value.shape);
    elif node.classname == 'MeqComposer':
        dims = [len(node.children)];
    elif node.classname == 'MeqSelector':
        dims = [1]
        # if initrec.has_key('multi') and initrec.multi:
        if initrec.has_key('index'):
            dims = [len(initrec.index)];
    else:
        dims = [-1]
    if trace: print '\n** JEN_get_dims(',node.name,'): ->',dims,'\n'
    return dims

#------------------------------------------------------------------
# Helper functions to extract kwquals and quals from lists of nodes
#------------------------------------------------------------------

def JEN_kwquals (cc=[], trace=0):
    if isinstance(cc, tuple): cc = list(cc)
    if not isinstance(cc, list): cc = [cc]
    kwquals = {}
    for i in range(len(cc)):
       kwquals.update(cc[i].kwquals)
       if trace: print '-',i,cc[i],': kwquals =',kwquals
    return kwquals

def JEN_quals (cc=[], trace=0):
    if isinstance(cc, tuple): cc = list(cc)
    if not isinstance(cc, list): cc = [cc]
    quals = []
    for i in range(len(cc)):
       quals.extend(list(cc[i].quals))
       if trace: print '-',i,cc[i],': quals =',quals
    return JEN_unique(quals)

#------------------------------------------------------------------
# Make sure that the elements of the list cc are unique 

def JEN_unique (cc=[], trace=0):
    if not isinstance(cc, list): return cc
    bb = []
    for c in cc:
        if not bb.__contains__(c): bb.append(c)
    if trace: print '** JEN_unique(',cc,') -> ',bb
    return bb


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
          for j in range(len(node.stepchildren)):
              print ' ',indent,'    .stepchildren[',j,']:',node.stepchildren[j][1]
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
              for j in range(len(node[1].stepchildren)):
                  print ' ',indent,'    .stepchildren[',j,']:',node[1].stepchildren[j][1]
                  # JEN_display_subtree (node[1].stepchildren[j], level=level+1,
                  #                     recurse=recurse-1, count=count, full=full)
              for i in range(len(node[1].children)):
                  JEN_display_subtree (node[1].children[i], level=level+1,
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

#----------------------------------------------------------------------
# Helper function to apply zero or more unary operations
# on the input node:

def JEN_apply_unop (ns, unop=False, node=0, trace=0):
    if unop == None: return node
    if isinstance(unop, bool): return node
    if isinstance(unop, str): unop = [unop]
    if not isinstance(unop, list): return node
    for unop1 in unop:
        if isinstance(unop1, str):
            node = ns << getattr(Meq, unop1)(node)
            if trace: print '** JEN_apply_unop() ->',node
    return node
        
    

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
    cc = [cos1, sin1, cos2, sin2]
    mat = (ns[name](**JEN_kwquals(cc))(*JEN_quals(cc)) << Meq.Composer(
        children=[cos1, sin1, cos2, sin2], dims=[2,2]))

    if trace: JEN_display_subtree(mat,'rotation_matrix', full=1)
    return mat


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
    cc = [cos1, isin1, isin2, cos2]
    mat = (ns[name](**JEN_kwquals(cc))(*JEN_quals(cc)) << Meq.Composer(
        children=[cos1, isin1, isin2, cos2], dims=[2,2]))

    if trace: JEN_display_subtree(mat,'ellipticity_matrix', full=1)
    return mat

#------------------------------------------------------------
# Helper function to make a 2x2 phase matrix

def JEN_phase_matrix (ns, angle=0, name=0, trace=0):
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
        m11 = (ns << Meq.Polar(1, a1))
        m22 = (ns << Meq.Polar(1, a2))

    else:
        m11 = (ns << Meq.Polar(1, a1/2))
        m22 = (ns << Meq.Polar(1, ns << Meq.Negate(a1/2)))
        
    if not isinstance(name, str): name = 'phase_matrix'
    cc = [m11, m22]
    mat = (ns[name](**JEN_kwquals(cc))(*JEN_quals(cc)) << Meq.Composer(
    # mat = (ns[name] << Meq.Composer(
    # mat = (ns[name].qxfer(a1) << Meq.Composer(
        children=[m11, 0, 0, m22], dims=[2,2]))

    if trace: JEN_display_subtree(mat,'phase_matrix', full=1)
    return mat




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

  if 0:
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
    print 'xxx =',xxx
    xxx = JEN_apply_unop (ns, ['Transpose', 'Cos'], xxx, trace=1) 
    xxx = JEN_apply_unop (ns, 'Sin', xxx, trace=1) 
    xxx = JEN_apply_unop (ns, False, xxx, trace=1)
    print 'xxx =',xxx

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
      aa = array([[1,2,3],[4,5,6]])
      # print dir(aa)
      c = ns << Meq.Constant(aa)
      print JEN_get_dims (c, trace=1)

      parm = ns.parm << Meq.Parm(6)
      c = ns << Meq.Composer(parm, parm, parm)
      print JEN_get_dims (c, trace=1)

      c = ns << Meq.Composer(parm, parm, parm, parm, dims=[2,2])
      print JEN_get_dims (c, trace=1)

  if 0:
      parm = ns.parm << Meq.Parm(6)
      cos1 = ns.cos1 << Meq.Cos(6)
      cos2 = ns.cos2 << Meq.Cos(ns.parm)
      JEN_display_subtree(cos1,'cos1', full=1)
      JEN_display_subtree(cos2,'cos2', full=1)
      
  if 0:
    JEN_unop_wavelength (ns, unop='Sqr', trace=1)

  if 0:
    print dir(ns)
    angle1 = ns.angle1('3c84', x=4, y=5) << Meq.Constant(3)
    # angle2 = ns.angle2(y=5) << Meq.Constant(-1)
    angle2 = -1
    JEN_rotation_matrix (ns, angle1, trace=1)
    JEN_rotation_matrix (ns, [angle2], trace=1)
    JEN_rotation_matrix (ns, [angle1, angle2], name='diff_angles', trace=1)

  if 0:
    angle1 = ns.angle1(x=4, y=5) << Meq.Constant(3)
    angle2 = ns.angle2(y=5) << Meq.Constant(-1)
    JEN_ellipticity_matrix (ns, angle1, trace=1)
    JEN_ellipticity_matrix (ns, [angle2], trace=1)
    JEN_ellipticity_matrix (ns, [angle1, angle2], name='diff_angles', trace=1)

  if 0:
    angle1 = ns.angle1(x=4, y=5) << Meq.Constant(3)
    angle2 = ns.angle2(y=5) << Meq.Constant(-1)
    JEN_phase_matrix (ns, angle1, trace=1)
    JEN_phase_matrix (ns, [angle2], trace=1)
    JEN_phase_matrix (ns, [angle1, angle2], name='diff_angles', trace=1)

  if 0:
    JEN_unique([2,3,3,2,5,6], trace=1)

  if 0:
    print '\n** Test of new TDL unop functionality:'
    s1 = '1'
    s2 = '5'
    # s1 = 1
    # s2 = 5
    q = '3c84'
    aa = array([[1,2,3],[4,5,6]])
    
    ns1 = ns.ns1(s1=s1) << Meq.Constant(-1)
    ns2 = ns.ns2(s2=s2) << Meq.Constant(-2)
    ns12 = ns.ns12(s1=s1, s2=s2) << Meq.Constant(-6)

    ns1q = ns.ns1q(s1=s1, q=q) << Meq.Constant(-3)
    ns2q = ns.ns2q(s2=s2, q=q) << -4
    ns12q = ns.ns12q(s1=s1, s2=s2, q=q) << Meq.Constant(-7)
    # ns2q = ns.ns2q(s2=s2, q=q) << Meq.Constant(-5)

    print ns1
    print ns2
    print ns12
    print ns1q
    print ns2q
    print ns12q

    print
    print 'aa =',aa
    print 'ns << Meq.Constant(aa) ->  ',ns << Meq.Constant(aa)

    print
    print 'ns << Meq.Sin(ns1) ->  ',ns << Meq.Sin(ns1)
    print 'ns << Meq.Sin(ns << Meq.Cos(ns1)) ->  ',ns << Meq.Sin(ns << Meq.Cos(ns1))

    print
    print 'ns << Meq.Composer(ns1,ns2) ->  ',ns << Meq.Composer(ns1,ns2)
    print 'ns << Meq.Matrix22(ns1,ns2,ns12,ns1q) ->  ',ns << Meq.Matrix22(ns1,ns2,ns12,ns1q)

    print
    print 'ns << (ns12q * ns1) ->  ',ns << (ns12q * ns1)
    print 'ns << (ns12q * ns1 / ns2) ->  ',ns << (ns12q * ns1 / ns2)

    print
    rr = record(a=2, b=6, c='c')
    print 'rr =',rr
    print 'ns.xxx(**rr) << Meq.Sin(ns1) ->  ',ns.xxx(**rr) << Meq.Sin(ns1)
    print 'ns(**rr) << Meq.Sin(ns1) ->  ',ns(**rr) << Meq.Sin(ns1)

    print

  if 0:
    print array([[0,0.1],[0.1,0]])

  if 0:
      sc = ns.stepchild << 4
      sc = [sc]
      node = ns.NAME('a',5, c=4) << Meq.Selector(5, stepchildren=sc) 
      JEN_display_NodeStub (node, 'test')

  if 1:
      # yyy = ns.yyy << Meq.Selector(children=[1], stepchildren=[2])
      # xxx = ns.xxx << -2
      JEN_display_NodeScope(ns, 'test')

  if 0:
      nsub = ns.Subscope('3c84', g=3, h=9)
      ns1 = nsub.ns1(s1='s1') << Meq.Constant(-1)
      print ns1

