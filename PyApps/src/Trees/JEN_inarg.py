# JEN_inarg.py:
#
# Author: J.E.Noordam
#
# Short description:
#    Functions dealing with records of input arguments
#
# History:
#    - 04 dec 2005: creation
#
# Full description:
#    By obeying a simple (and unconstraining!) set of rules, the input
#    arguments of any function may be manipulated as a record. This has
#    many advantages.
#    An 'inarg-compatible' function has the following general structure:
#
#    from Timba.Trees import JEN_inarg
#    def myfunc(x=None, y=None, **inarg):
#        pp = JEN_inarg.inarg2pp(inarg, 'myfunc')
#        pp.setdefault('aa', value1)
#        pp.setdefault('bb', value2)
#        if JEN_inarg.getinarg(pp): return JEN_inarg.pp2inarg(pp)
#
#        # The function body, which uses the values in record pp:
#        result = .... 
#        return result
#
#    inarg = myfunc(getinarg=True)
#    JEN_inarg.modify(inarg, bb=56)
#    result = myfunc(x=1, y=-2, inarg=inarg, aa=-78)


#================================================================================
# Preamble
#================================================================================

from Timba.TDL import *
from Timba.Trees import JEN_record
from copy import deepcopy



#----------------------------------------------------------------------------
# An internal (pp) argument record has the following structure:
#  - keyword1 = value1
#  - keyword2 = value2
#  - keyword3 = value3
#  - JEN_inarg_ctrl:
#    - funcname = 'MG_JEN_Cohset::make_sinks()'
#    - [ERROR = dict()]
#    - [WARNING = dict()]

# An external (inarg) argument record has the following structure:
#  - MG_JEN_Cohset::make_sinks()
#    - keyword1 = value1
#    - keyword2 = value2
#    - keyword3 = value3
#    - JEN_inarg_ctrl
#      - funcname = 'MG_JEN_Cohset::make_sinks()'
#  - MG_JEN_Joneset::GJones()
#    - keyword4 = value4
#    - keyword5 = value5
#    - keyword6 = value6
#    - JEN_inarg_ctrl:
#      - funcname = MG_JEN_Joneset::GJones()
#      - ERROR
#        0 = error1
#        1 = error2
#    - MG_MXM_whatever::func1()
#      - keyword1 = value1
#      - keyword2 = value2
#      - keyword3 = value3
#      - JEN_inarg_ctrl
#        - funcname = 'MG_MXM_whatever::func1()'
#  - etc

def is_inarg(rr, origin='...', level=0, trace=False):
   """Test whether rr is an argument record"""
   if not isinstance(rr, dict): return False        # record is a dict too
   # Look for a valid ctrl record:
   if rr.has_key('JEN_inarg_ctrl'):
      if isinstance(rr['JEN_inarg_ctrl'], dict): return True
      return False                                  # ...??
   # Recursive:
   for key in rr.keys():
      if isinstance(rr[key], dict):
         if is_inarg(rr[key], level=level+1, trace=trace): return True
   return False

#----------------------------------------------------------------------------

def is_ok(rr, level=0, trace=False):
   """Generic test whether rr (pp or inarg) is ok"""
   if not isinstance(rr, dict): return False
   if not is_inarg(rr, 'is_ok()'): return False
   for key in rr.keys():
      if key=='JEN_inarg_ctrl':
         if not isinstance(rr[key], dict): return False
         if rr[key].has_key('ERROR'): return False
         if rr[key].has_key('WARNING'): return False
      elif isinstance(rr[key],dict):                    # recursive
         ok = is_ok(rr[key], level=level+1, trace=trace)
         if not ok: return False
   return True

#----------------------------------------------------------------------------

def prefix(level=0):
   """Make a level-dependent prefix (for tracing recursion)"""
   prefix = str(level)+':'+(level*'.')
   return prefix

#----------------------------------------------------------------------------

def ctrl(rr, key=None, value=None, delete=None, level=0, trace=False):
   """Get the (first!) JEN_inarg_ctrl record from inarg or pp (if any).
   If a field (key) is specified, return its value instead.
   If a value is specified, modify the field value first"""
   if not isinstance(rr, dict):
      return False
   elif not rr.has_key('JEN_inarg_ctrl'):     # recursive
      for key1 in rr.keys():
         if isinstance(rr[key1],dict):
            return ctrl(rr[key1], key=key, value=value, delete=delete,
                        level=level+1, trace=trace)
   else:                                      # ctrl record found
      s1 = 'JEN_inarg_ctrl(level='+str(level)+')'
      cc = rr['JEN_inarg_ctrl']               # convenience
      if not isinstance(cc, dict):
         if trace: print s1,'not a record, but:',type(cc)
      elif not key:                           # no key specified
         if trace: display(cc,'JEN_inarg_ctrl <- '+s1)
         return cc                            # return the entire ctrl record                         
      elif not value==None:                   # new value specified
         was = 'noexist'
         if cc.has_key(key): was = cc[key]
         rr['JEN_inarg_ctrl'][key] = value
         if trace: print s1,key,':',was,'->',rr['JEN_inarg_ctrl'][key]
         return rr['JEN_inarg_ctrl'][key]     # return new current value
      elif not cc.has_key(key):               # no such field
         if trace: print s1,'no such key:',key,' (in:',cc.keys(),')'
         if delete: return False              # ok
      elif delete:                            # delete the field
         if trace: print s1,'deleted key:',key,' (was:',cc[key],')'
         rr['JEN_inarg_ctrl'].__delitem__(key)
         return rr['JEN_inarg_ctrl'].has_key(key) 
      else:
         if trace: print s1,key,'=',cc[key]
         return cc[key]                       # return current value

   if level==0:
      print '** JEN_inarg.ctrl(',key,value,'): not found'
   return None

#----------------------------------------------------------------------------

def funcname(rr, trace=False):
   """Get the funcname from the inarg or pp"""
   return ctrl(rr, 'funcname')

#----------------------------------------------------------------------------

def ERROR(rr, txt=None, clear=False, trace=False):
   """Interact with the ERROR record of the JEN_inarg_ctrl field"""
   return message(rr, txt=txt, key='ERROR', clear=clear, trace=trace)

def WARNING(rr, txt=None, clear=False, trace=False):
   """Interact with the WARNING record of the JEN_inarg_ctrl field"""
   return message(rr, txt=txt, key='WARNING', clear=clear, trace=trace)

def message(rr, txt=None, key='message', clear=False, trace=False):
   """Interact with the specified record of the JEN_inarg_ctrl field"""
   s1 = 'JEN_inarg.'+key+'():'
   if clear:                                     # clear the record
      ctrl(rr,key,delete=True, trace=trace)
   if txt:                                       # message specified
      cc = ctrl(rr,key,trace=trace)
      if not cc: cc = dict()
      cc[str(len(cc))] = txt
      print '**',s1,funcname(inarg),'(total=',len(cc),'):',txt
      cc = ctrl(rr,key,cc, trace=trace)      
   if trace: display(rr,s1, full=True)
   return ctrl(rr,key,trace=trace)      

#----------------------------------------------------------------------------

def display(rr, txt=None, name=None, full=False):
   """Display the argument record (inarg or pp)"""
   if not isinstance(rr, dict):
      print '** JEN_inarg.display(rr): not a record, but:',type(rr)
      return False
   if not name:                                        # Make sure of name
      name = 'rr'
      if is_inarg(rr): name = 'inarg/pp'               # argument record
   # Work on a copy (qq):
   qq = rr
   if not is_ok(qq): full = True
   if not full: qq = strip(rr, 'JEN_inarg_ctrl')       # remove ctrl fields
   JEN_record.display_object(qq,name,txt)
   if not full: print '** NB: The JEN_inarg_ctrl records are not shown.\n'
   return True


#----------------------------------------------------------------------------

def strip(rr, key='JEN_inarg_ctrl', level=0, trace=False):
   """Strip off all instances of the named (key) field from record rr"""
   if not isinstance(rr, dict): return rr
   qq = deepcopy(rr)
   # Remove the named field if present:
   if qq.has_key(key): qq.__delitem__(key)
   # Recurse:
   for key1 in qq.keys():
      if isinstance(qq[key1], dict):
         qq[key1] = strip(qq[key1], key=key, level=level+1, trace=trace)
   return qq

#----------------------------------------------------------------------------

def getinarg(pp, check=True, strip=False, trace=False):
   """React to the presence (or not) of a getinarg field in pp""" 
   if trace:
      display(pp,'input pp to .getinarg(pp)', full=True)
   if not isinstance(pp, dict):
      print '** JEN_inarg.getinarg(pp): pp not a record, but:',type(pp) 
      return False
   if pp.has_key('getinarg'):
      # Use: if JEN_inarg.getinarg(pp): return JEN_inarg.pp2inarg(pp)
      # i.e. if True, do not execte the body of the mother function,
      #      but just return an inarg record with its default arguments
      return True
   if check:
      # At the very least, report any problems:
      if not is_ok(pp):
         display(pp,'.getinarg(): NOT OK!!')
         return True                              # do NOT execute....
   if strip:
      # Optionally, strip off the JEN_inarg_ctrl record:
      strip(pp, 'JEN_inarg_ctrl', trace=trace)
   if trace:
      display(pp,'pp to be executed', full=True)
   # Return False to cause the calling function to execute its body:
   return False
   

#----------------------------------------------------------------------------

def inarg2pp(inarg, funcname='<funcname>', trace=False):
   """Extract the relevant internal argument record (pp) from inarg"""

   # if trace: display(inarg,'input to .inarg2pp(inarg)', full=True)

   if not isinstance(inarg, dict):
      # Difficult to imagine how this could happen....
      if trace: print '-- inarg not dict'
      return inarg

   elif inarg.has_key('getinarg'):
      # Called as .func(getinarg=True): -> .pp2inarg(pp)
      # NB: inarg may contain other keyword arguments too...
      if trace: print '-- inarg has key getinarg'
      pp = inarg

   elif inarg.has_key('inarg'):
      # Called like func(inarg=inarg), extract the actual inarg record:
      s1 = '** JEN_inarg.inarg2pp(): '
      if not is_inarg(inarg['inarg']):
         print s1,'inarg is not a valid inarg: ',type(inarg)
         return False
      elif not inarg['inarg'].has_key(funcname):
         # Trying to run the function with the wrong inarg
         # (i.e. an inarg for a different funtion(s)) should result in an error:
         print s1,'inarg does not relate to function:',funcname
         return False
      elif not isinstance(inarg['inarg'][funcname], dict):
         # Trying to run the function with an invalid inarg[funcname] record
         # should result in an error:
         print s1,'inarg[',funcname,'] is not a record/dict, but:',type(inarg['inarg'][funcname])
         return False

      else:
         # The main dish: inarg contains a record of argument values for the relevant
         # function. Detach it from inarg as a bare record pp:
         pp = inarg['inarg'][funcname]

         # Now deal with any EXTRA keyword arguments in inarg, which may have been
         # supplied as:     func(inarg=inarg, aa=10, bb=-13)
         # If recognised, these OVERRIDE the values of the relevant pp fields.
         # NB: Any extra arguments that are not fields in pp are ignored, and lost!
         # NB: This feature is inhibited for nested inarg records, because they might
         #     contain keywords with the same name as its calling function.
         if not ctrl(pp, 'nested'):
            for key in inarg.keys():
               if pp.has_key(key):
                  was = pp[key]
                  pp[key] = inarg[key]
                  if trace: print s1,'overridden pp[',key,']: ',was,'->',pp[key]
               else:
                  # if trace: print s1,'ignored extra field inarg[',key,'] =',inarg[key]
                  pass

   else:
      # Assume that the function has been called 'traditionally'
      pp = inarg
      if trace: print '-- inarg traditional'

   # Attach ctrl record to pp (if necessary):
   attach_ctrl(pp, funcname)

   # Replace referenced values (if any):
   replace_reference(pp, trace=trace)

   if trace: display(pp,'pp <- .inarg2pp(inarg)', full=True)
   return pp


#----------------------------------------------------------------------------

def attach_ctrl(rr, funcname='<funcname>'):
   """Make sure that rr has a valid JEN_inarg_ctrl record"""
   if not rr.has_key('JEN_inarg_ctrl'):
      rr['JEN_inarg_ctrl'] = dict(funcname=funcname)
   elif not isinstance(rr['JEN_inarg_ctrl'], dict):
      rr['JEN_inarg_ctrl'] = dict(funcname=funcname)
   return True
   

#----------------------------------------------------------------------------

def replace_reference(rr, level=0, trace=False):
   """If the value of a field in the given record (rr) is a field name
   in the same record, replace it with the value of the referenced field"""
   # trace = True
   if not isinstance(rr, dict): return False
   if level>10:
      print 'JEN_inarg.replace_reference(): max level exceeded',level
      return False
   count = 0
   for key in rr.keys():                   # for all fields
      value = rr[key]                      # field value
      if isinstance(value, str):           # if field value is a string
         # print level,key,value
         if rr.has_key(value):             # if field value is the name of another field
            if not value==rr[value]:       # no change
               count += 1                  # count the number of replacements
               s1 = '.replace_reference('+str(level)+'): key='+key+':  '
               s1 += str(value)+' -> '+str(rr[value])
               message(rr, s1)
               rr[key] = rr[value]         # replace with the value of the referenced field
   if count>0: replace_reference(rr, level=level+1)       # repeat if necessary
   return count


#----------------------------------------------------------------------------

def define(pp, key=None, default=None, choice=None, help=None):
   """Define a pp entry with a default value, and other info.
   This is a more able version of pp.setdefault(key,value),
   which is helpful for a (future) inarg specification GUI"""
   if not isinstance(pp, dict):
      print '.inarg(): pp not a record, but:',type(pp) 
      return False
   elif pp.has_key(key):
      print '.inarg(): duplicate argument key:',key 
      return False
   # OK, make the new argument field:
   pp.setdefault(key,default)
   return True

#----------------------------------------------------------------------------

def gui(inarg):
   """Placeholder for inarg specification GUI"""
   return False

#----------------------------------------------------------------------------

def pp2inarg(pp, help=None, trace=False):
   """Turn the internal argument record pp into an inarg record"""
   # if trace: display(pp,'.pp2inarg() input pp')
   funcname = pp['JEN_inarg_ctrl']['funcname']
   if pp.has_key('getinarg'): pp.__delitem__('getinarg')
   # Make the external inarg record:
   inarg = dict()
   inarg[funcname] = pp
   if trace: display(inarg,'inarg <- .pp2inarg(pp)')
   return inarg

#----------------------------------------------------------------------------

def modify(inarg, **arg):
   """Modify the values of the specified fields in inarg"""
   if not is_inarg(inarg): return False
   if not isinstance(arg, dict): return False 
   fname = funcname(inarg)
   ok = True
   for key in arg.keys():
      print fname,key
      if inarg[fname].has_key(key):
         was = inarg[fname][key]
         inarg[fname][key] = arg[key]
         s1 = '.modify(): key='+key+':  '+str(was)+' -> '+str(inarg[fname][key])
         message(inarg,s1)
      else:
         ok = False
         ERROR(inarg,'.modify(): key not recognised:  '+key)
   if not ok:
      display(inarg,'inarg','.modify(): not ok!!', full=True)
   return True

   

#----------------------------------------------------------------------------

def attach(rr=None, inarg=None, trace=False):
   """Attach the inarg record to a (inarg or pp) record rr"""
   if not isinstance(inarg, dict):
      print '** JEN_inarg.attach(): inarg not a record, but:',type(inarg)
      return False 
   # Make sure that the composite (rr) is a record:
   if not isinstance(rr, dict): rr = dict()
   fname = funcname(inarg)
   if rr.has_key(fname):
      print '** JEN_inarg.attach(): rr duplicate funcname:',funcname
   else:
      rr[fname] = inarg[fname]
   if trace: display(rr,'rr <- JEN_inarg.attach()', full=True)
   return rr

#----------------------------------------------------------------------------

def nest(pp=None, inarg=None, trace=False):
   """Attach a nested inarg to internal argument record pp"""
   # Make sure that the ctrl record of inarg has a 'nested' field.
   # This is used in .inarg2pp() to avoid problems
   ctrl(inarg,'nested',True, trace=trace)
   return attach(pp, inarg=inarg, trace=trace)


#----------------------------------------------------------------------------

def result(rr=None, pp=None, attach=None, trace=True):
   """Attach things to the result record (rr)"""
   if not isinstance(rr, dict):
      rr = dict()

   # Attach the internal argument record (pp):
   # NB: This should be done first: rr = result(pp=pp)
   if isinstance(pp, dict):
      key = funcname(pp)

      # Make sure that rr has a JEN_inarg_ctrl record
      # NB: This allows the use of .ERROR(), .is_ok() etc
      attach_ctrl(rr, key)

      # Attach:
      rr['inarg(pp) for function: '+key] = pp

   # Attach a sub-result (anything) to rr:
   if isinstance(attach, dict):
      key = funcname(attach)
      if not isinstance(key, str): key='?funcname?'
      rr['result of function: '+key] = attach

   if trace:
      fname = funcname(rr)
      name = 'result of function: '+fname
      display(rr, 'JEN_inarg.result()', name=name, full=True)
   return rr


#********************************************************************************




#********************************************************************************
#******************** PART VI: Standalone test routines *************************
#********************************************************************************
#********************************************************************************

if __name__ == '__main__':
   print '\n****************\n** Local test of: JEN_inarg.py:\n'
   from Timba.Trees import JEN_record


   #---------------------------------------------------------------------------
   def test1(ns=None, object=None, **inarg):
      """A test function with inarg capability"""

      # Extract a bare argument record pp from inarg
      pp = inarg2pp(inarg, 'JEN_inarg::test1()', trace=True)

      # Specify the function arguments, with default values:
      pp.setdefault('aa', 45)
      pp.setdefault('bb', -19)
      pp.setdefault('ref_ref_aa', 'ref_aa')
      pp.setdefault('ref_aa', 'aa')
      pp.setdefault('nested', True)
      pp.setdefault('trace', False)
      if pp['nested']:
         # It is possible to include the default inarg records from other
         # functions that are used in the function body below:
         nest(pp, inarg=test2(getinarg=True, trace=pp['trace']), trace=pp['trace'])

      # .test(getinarg=True) -> an inarg record with default values
      if getinarg(pp, trace=pp['trace']): return pp2inarg(pp, trace=pp['trace'])

      # Execute the function body, using pp:
      # Initialise a result record (rr) with the argument record pp
      rr = result(pp=pp)
      if pp['nested']:
         # The inarg record for test2 is part of pp (see above):
         rr = result(rr, attach=test2(inarg=pp))
      cc = ctrl(rr)
      print 'ctrl =',cc
      message(rr, 'message')
      ERROR(rr, 'message')
      WARNING(rr, 'message')
      return rr


   #---------------------------------------------------------------------------
   def test2(**inarg):
      """Another test function"""

      pp = inarg2pp(inarg, 'JEN_inarg::test2()', trace=True)
      pp.setdefault('ff', 145)
      pp.setdefault('bb', -119)
      pp.setdefault('trace', False)
      if getinarg(pp, trace=pp['trace']): return pp2inarg(pp, trace=pp['trace'])

      # Initialise a result record (rr) with the argument record pp
      rr = result(pp=pp)
      return rr

   #---------------------------------------------------------------------------

   if 0:
      # Test of basic operation:
      inarg = test1(getinarg=True, trace=True)
      if 0:
         # modify(trace=True)
         # modify(inarg, trace=True)
         # modify(inarg, aa='aa', trace=True)
         modify(inarg, aa='aaaa', cc='cc', trace=True)
         display(inarg, 'after .modify()')
      result = test1(inarg=inarg, bb='override', qq='ignored', nested=False)
      
   if 0:
      # Test of .ctrl()
      inarg = test1(getinarg=True)
      tf = is_inarg(inarg)
      print 'is_inarg(inarg) ->',tf
      ok = is_ok(inarg)
      print 'is_ok(inarg) ->',ok

   if 0:
      # Test of .prefix():
      for i in range(-1,4):
         s = prefix(i)
         print 'prefix(',i,') ->',s

   if 0:
      # Test of .ctrl()
      inarg = test1(getinarg=True)
      cc = ctrl(inarg, trace=True)
      ERROR(inarg,'error 1', trace=True)
      cc = ctrl(inarg, 'nested', trace=True)
      cc = ctrl(inarg, 'nested', True, trace=True)
      cc = ctrl(inarg, trace=True)
      cc = ctrl(inarg, 'nested', delete=True, trace=True)
      cc = ctrl(inarg, 'nested', trace=True)
      cc = ctrl(inarg, trace=True)
      cc = ctrl(inarg, 'ERROR', trace=True)
      cc = ctrl(inarg, 'funcname', trace=True)
      cc = ctrl(inarg, 'funcname', 45, trace=True)
      print 'cc =',cc

   if 1:
      # Test of .message():
      inarg = test1(getinarg=True)
      ERROR(inarg,'error 1', trace=True)
      ERROR(inarg,'error 2', clear=True, trace=True)
      ERROR(inarg,'error 3', trace=True)
      WARNING(inarg,'warning 1', trace=True)
      message(inarg,'message 1', trace=True)
      WARNING(inarg, clear=True, trace=True)
      ERROR(inarg, clear=True, trace=True)

   if 0:
      # Test: Combine the inarg records of multiple functions:
      inarg1 = test1(getinarg=True)
      inarg2 = test2(getinarg=True)
      inarg = attach(inarg=inarg1, trace=True)
      attach(inarg, inarg=inarg2, trace=True)
      # attach(inarg, inarg=inarg2, trace=True)
      # r1 = test1(inarg=inarg)        # nested!
      r2 = test2(inarg=inarg)        # ok, test2 only
      # r3 = test2(inarg=inarg1)         # -> error

   if 0:
      # Test of 'regular' use, i.e. without inarg:
      r1 = test2(aa=6, xx=7, trace=True)

   if 0:
      # One of the few forbidden things:
      r1 = test1(inarg=False)            # error

   if 0:
      # Test of .strip():
      rr = test1(getinarg=True)
      JEN_record.display_object(rr,'rr','before .strip(rr)')
      qq = strip(rr, 'JEN_inarg_ctrl')
      JEN_record.display_object(qq,'qq','after .strip(rr)')
      JEN_record.display_object(rr,'rr','after .strip(rr)')

   if 0:
      rr = dict(aa=3, bb=4)
      display(rr,'rr', full=True)
   print '\n** End of local test of: JEN_inarg.py \n*************\n'

#********************************************************************************



