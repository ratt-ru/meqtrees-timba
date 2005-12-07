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
#    To be used with ANY function


#================================================================================
# Preamble
#================================================================================

from Timba.TDL import *
from Timba.Trees import JEN_record
from copy import deepcopy

#----------------------------------------------------------------------------

def display(inarg, txt=None, full=True):
   """Display the argument record"""
   # If full, also display the JEN_inarg field(s)....
   JEN_record.display_object(inarg,'inarg',txt)
   return True


#----------------------------------------------------------------------------

def is_inarg(inarg, origin='...', trace=True):
   """Test whether inarg is a regular JEN_inarg argument record"""
   if not isinstance(inarg, dict): return False        # record is a dict too
   count = 0
   for key in inarg.keys():
      if isinstance(inarg[key], dict):
         if inarg[key].has_key('JEN_inarg_ctrl'): count += 1
   if count>0: return True
   return False

#----------------------------------------------------------------------------

def extract(inarg, funcname='<funcname>', trace=True):
   """Extract the bare argument record from inarg,
   assuming that it is a field named funcname"""

   # if trace: display(inarg,'.extract() input inarg')

   if not isinstance(inarg, dict):
      # Difficult to imagine how this could happen....
      if trace: print '-- inarg not dict'
      return inarg

   elif inarg.has_key('getinarg'):
      # Called as .func(getinarg=True): -> .noexec(pp)
      # NB: inarg may contain other keyword arguments too...
      if trace: print '-- inarg has key getinarg'
      pp = inarg

   elif inarg.has_key('inarg'):
      # Called like func(inarg=inarg), extract the actual inarg record:
      s1 = '** JEN_inarg.extract(): '
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
         # If recgnised, these OVERRIDE the values of the relevant pp fields.
         # NB: Any extra arguments that are not fields in pp are ignored, and lost!
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


   # Attach some control information to pp (if necessary):
   if not pp.has_key('JEN_inarg_ctrl'):
      pp['JEN_inarg_ctrl'] = dict(funcname=funcname)
   elif not isinstance(pp['JEN_inarg_ctrl'], dict):
      pp['JEN_inarg_ctrl'] = dict(funcname=funcname)
      
   if trace: JEN_record.display_object(pp,'pp','<- .extract(inarg)')
   return pp


#----------------------------------------------------------------------------

def replace_reference(rr, up=None, level=1):
   """If the value of a field in the given record (rr) is a field name
   in the same record, replace it with the value of the referenced field"""
   if level>10: return False                 # escape from eternal loop (error!)
   count = 0
   prefix = str(level)+':'+(level*'.')
   for key in rr.keys():                     # for all fields
      value = rr[key]                        # field value
      if isinstance(value, dict):            # if field value is dict: recurse
         replace_reference(rr[key], up=rr, level=level+1)
      elif isinstance(value, str):           # if field value is a string
         if value[:3]=='../':                # if upward reference
            if isinstance(up, dict):         # if 'parent' record given      
               upfield = value.split('/')[1] # 
               for upkey in up.keys():       # search for upfield in parent record
                  count += 1                 # count the number of replacements
                  # print prefix,'-',count,'replace_with_upward: rr[',key,'] =',value,'->',up[upkey]
                  if upkey==upfield: rr[key] = up[upkey]  # replace if found
         else:
            if not value==key:                # ignore self-reference
               if rr.has_key(value):          # if field value is the name of another field
                  count += 1                  # count the number of replacements
                  # print prefix,'-',count,': replace_reference(): rr[',key,'] =',value,'->',rr[value]
                  rr[key] = rr[value]         # replace with the value of the referenced field
   if count>0: replace_reference(rr, level=level+1)       # repeat if necessary
   return count


#----------------------------------------------------------------------------

def inarg(pp, name=None, default=None, choice=None, help=None):
   """Specify an argument with a default value in pp.
   This is a more able version of pp.setdafault(name,default)"""
   if not isinstance(pp, dict):
      print '.inarg(): pp not a record, but:',type(pp) 
      return False
   elif pp.has_key(name):
      print '.inarg(): duplicate argument name:',name 
      return False
   # OK, make the new argument field:
   pp.setdefault(name,default)
   return True

#----------------------------------------------------------------------------

def noexec(pp, help=None, trace=True):
   """Turn the bare record pp into an inarg"""
   # if trace: display(pp,'.noexec() input pp')
   inarg = dict()
   funcname = pp['JEN_inarg_ctrl']['funcname']
   if pp.has_key('getinarg'): pp.__delitem__('getinarg')
   inarg[funcname] = pp
   if trace: display(inarg,'inarg <- .noexec(pp)')
   return inarg

#----------------------------------------------------------------------------

def modify(inarg, **arg):
   """Modify the values of the specified fields in inarg"""
   if not is_inarg(inarg): return False
   if not isinstance(arg, dict): return False 
   funcname = inarg.keys()[0]
   ok = True
   for key in arg.keys():
      if inarg[funcname].has_key(key):
         was = inarg[funcname][key]
         inarg[funcname][key] = arg[key]
         print '.modify():',key,':',was,'->',inarg[funcname][key]
      else:
         ok = False
         error(inarg,'.modify(): name not recognised: '+key)
   if not ok:
      display(inarg,'inarg','.modify(): not ok!!')
   return True

#----------------------------------------------------------------------------

def error(inarg, txt, trace=True):
   """Attach an error message to the JEN_inarg_ctrl field"""
   if not is_inarg(inarg): return False
   funcname = inarg.keys()[0]
   inarg[funcname]['JEN_inarg_ctrl'].setdefault('error',dict())
   key = str(len(inarg[funcname]['JEN_inarg_ctrl']['error']))
   inarg[funcname]['JEN_inarg_ctrl']['error'][key] = txt
   print '** error()',funcname,':',txt
   return True
   
#----------------------------------------------------------------------------

def warning(inarg, txt, trace=True):
   """Attach an warning message to the JEN_inarg_ctrl field"""
   if not is_inarg(inarg): return False
   funcname = inarg.keys()[0]
   inarg[funcname]['JEN_inarg_ctrl'].setdefault('warning',dict())
   key = str(len(inarg[funcname]['JEN_inarg_ctrl']['warning']))
   inarg[funcname]['JEN_inarg_ctrl']['warning'][key] = txt
   print '** warning()',funcname,':',txt
   return True
   
#----------------------------------------------------------------------------

def check(pp, strip=True, trace=True):
   """Optional function to check an parameter record pp"""
   if not isinstance(pp, dict): return False
   ok = True

   # Check the ctrl record (if any):
   if pp.has_key('JEN_inarg_ctrl'):
      ctrl = pp['JEN_inarg_ctrl']
      if isinstance(ctrl, dict):
         funcname = '??'
         if ctrl.has_key('funcname'):
            funcname = ctrl['funcname']
         s1 = '.check() '+funcname+': '
         if ctrl.has_key('error'):
            ok = False
            # print s1,'pp has errors'
         if ctrl.has_key('warning'):
            ok = False
            # print s1,'pp has warnings'
      if not ok:
         # Report problems:
         JEN_record.display_object(pp,'pp','.check(pp) ** PROBLEM **')
      if strip:
         # Optional: strip off the ctrl record:
         pp.__delitem__('JEN_inarg_ctrl')

   # Return the outcome (True/False) of the check:
   return ok

#----------------------------------------------------------------------------

def strip(rr, level=0, trace=True):
   """Strip off all JEN_inarg_ctrl records from record rr"""
   if not isinstance(rr, dict): return rr
   qq = deepcopy(rr)
   # Remove the ctrl record if present:
   if qq.has_key('JEN_inarg_ctrl'): qq.__delitem__('JEN_inarg_ctrl')
   # Recurse:
   for key in qq.keys():
      if isinstance(qq[key], dict):
         qq[key] = strip(qq[key], level=level+1, trace=trace)
   return qq

#----------------------------------------------------------------------------

def ctrl(rr, level=0, trace=False):
   """Get the JEN_inarg_ctrl record from inarg or pp (if any)"""
   if not isinstance(rr, dict):
      return False
   elif rr.has_key('JEN_inarg_ctrl'):
      cc = rr['JEN_inarg_ctrl']
      if trace: JEN_record.display_object(cc,'JEN_inarg_ctrl','<- .ctrl(rr,'+str(level)+')')
      return cc
   else:
      for key in rr.keys():
         if isinstance(rr[key],dict):
            cc = ctrl(rr[key], level=level+1, trace=trace)
            if isinstance(cc, dict): return cc
   return False

#----------------------------------------------------------------------------

def funcname(rr, trace=False):
   """Get the funcname from the inarg or pp"""
   cc = ctrl(rr)
   if isinstance(cc, dict):
      fname = cc['funcname']
      if trace: JEN_record.display_object(fname,'funcname','<- .funcname(rr)')
      return fname
   return False


#----------------------------------------------------------------------------

def attach(inarg, rr=None, trace=True):
   """Attach the inarg record to a (inarg or pp) record rr"""
   if not isinstance(inarg, dict):
      print '** JEN_inarg.attach(): inarg not a record, but:',type(inarg)
      return False 
   if not isinstance(rr, dict): rr = dict() 
   funcname = inarg.keys()[0]
   if rr.has_key(funcname):
      print '** JEN_inarg.attach(): rr duplicate funcname:',funcname
   else:
      rr[funcname] = inarg[funcname]
   if trace: JEN_record.display_object(rr,'rr','JEN_inarg.attach()')
   return rr


#********************************************************************************




#********************************************************************************
#******************** PART VI: Standalone test routines *************************
#********************************************************************************
#********************************************************************************

if __name__ == '__main__':
   print '\n****************\n** Local test of: JEN_inarg.py:\n'
   from Timba.Trees import JEN_record


   def test1(ns=None, object=None, **inarg):
      """A test function with inarg capability"""

      # Extract a bare argument record pp from inarg
      pp = extract(inarg, 'JEN_inarg::test1()')

      # Specify the function arguments, with default values:
      pp.setdefault('aa', 45)
      pp.setdefault('bb', -19)
      pp.setdefault('nested', True)
      if pp['nested']:
         # It is possible to include the default inarg records from other
         # functions that are used in the function body below:
         attach(test2(getinarg=True),pp)

      # .test(getinarg=True) -> an inarg record with default values
      if pp.has_key('getinarg'): return noexec(pp)

      # Optional: check and strip:
      fname = funcname(pp)
      if not check(pp): return False

      # Execute the function body, using pp:
      result = pp
      if pp['nested']:
         # The inarg record for test2 is part of pp (see above):
         result2 = test2(inarg=pp)
         pp['result2'] = result2
      JEN_record.display_object(result,'result','.test1()')
      return result

   def test2(**inarg):
      """Another test function"""

      pp = extract(inarg, 'JEN_inarg::test2()')
      pp.setdefault('ff', 145)
      pp.setdefault('bb', -119)
      if pp.has_key('getinarg'): return noexec(pp)
      if not check(pp): return False

      result = pp
      JEN_record.display_object(result,'result','.test2()')
      return result

   if 0:
      # Test: Call the test function in various ways:
      inarg = test1(getinarg=True)
      if 0:
         # modify()
         # modify(inarg)
         modify(inarg, aa='aa')
         # modify(inarg, aa='aaaa', cc='cc')
         display(inarg, 'after .modify()')
      result = test1(inarg=inarg, bb='override', qq='ignored', nested=False)
      

   if 0:
      # Test: Combine the inarg records of multiple functions:
      inarg1 = test1(getinarg=True)
      inarg2 = test2(getinarg=True)
      # inarg = dict()
      inarg = attach(inarg1)
      attach(inarg2,inarg)
      # attach(inarg1,inarg)
      result1 = test1(inarg=inarg)
      result2 = test2(inarg=inarg)
      result2 = test2(inarg=inarg1)

   if 0:
      result1 = test1(aa=6, xx=7)

   if 0:
      result1 = test1(inarg=False)

   if 1:
      rr = test1(getinarg=True)
      JEN_record.display_object(rr,'rr','before .strip(rr)')
      qq = strip(rr)
      JEN_record.display_object(qq,'qq','after .strip(rr)')
      JEN_record.display_object(rr,'rr','after .strip(rr)')

   if 0:
      rr = test1(getinarg=True)
      display(rr,'rr <- .test1(getinarg=True)')
      cc = ctrl(rr, trace=True)
      print cc
      fname = funcname(rr, trace=True)
      print fname


   if 0:
      pp = dict(aa=3, bb=4)
      JEN_record.display_object(pp,'pp','...')
   print '\n** End of local test of: JEN_inarg.py \n*************\n'

#********************************************************************************



