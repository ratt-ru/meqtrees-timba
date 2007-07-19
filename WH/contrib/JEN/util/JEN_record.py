# JEN_record.py:
#
# Author: J.E.Noordam
#
# Short description:
#    Some useful functions related to Python/TDL records: 
#
# History:
#    - 04 dec 2005: creation
#    - ...
#
# Full description:
#












#================================================================================
# Preamble
#================================================================================

#
#% $Id$ 
#
#
# Copyright (C) 2002-2007
# The MeqTree Foundation & 
# ASTRON (Netherlands Foundation for Research in Astronomy)
# P.O.Box 2, 7990 AA Dwingeloo, The Netherlands
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>,
# or write to the Free Software Foundation, Inc., 
# 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

from Timba.TDL import *

# The following bit still requires a bit of thought.....
from Timba import utils
_dbg = utils.verbosity(0, name='tutorial')
_dprint = _dbg.dprint                         # use: _dprint(2, "abc")
_dprintf = _dbg.dprintf                       # use: _dprintf(2, "a = %d", a)
# run the script with: -dtutorial=3
# level 0 is always printed



#-------------------------------------------------------------------------------
# Helper function that replaces 'referenced' values with actual ones:
#-------------------------------------------------------------------------------

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


#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------

def noexec(pp=None, MG=None, help=None):
   """Function that returns a somewhat organised record of the
   specified record (pp) of function input arguments,
   and its associated information (e.g. help)"""

   # Make sure that pp is a record
   if pp==None: pp = record()
   pp = record(pp)

   # Make sure of the help record, and attach it to pp:
   if help==None: help = record()
   help = record(help)
   for key in pp.keys():
      if not help.has_key(key):
         help[key] = '.. no help available for argument: '+key
   pp['_help'] = help

   # Check the MG-record, and attach it to pp:
   MG = MG_check(MG)
   pp['_MG'] = MG

   display_object(pp,'pp', 'MG_JEN_exec.noexec()')
   return pp
   





#----------------------------------------------------------------------------------
# Display any Python object(v):
#----------------------------------------------------------------------------------

def display_object (v, name='<name>', txt='', full=False, indent=0):
    """Display the given Python object"""
   
    if indent==0: print '\n** display of Python object:',name,': (',txt,'):'
    print '**',indent*'.',name,':',
    
    if isinstance(v, (str, list, tuple, dict, record)):
        # sizeable types (otherwise, len(v) gives an error):
        vlen = len(v)
        slen = '['+str(vlen)+']'

        if isinstance(v, str):
            print 'str',slen,
            print '=',v
      
        elif isinstance(v, list):
            print 'list',slen,
            separate = False
            types = {}
            for i in range(vlen):
                stype = str(type(v[i]))
                types[stype] = 1
                s1 = stype.split(' ')
                if s1[0] == '<class': separate = True
                if isinstance(v[i], (dict, record)): separate = True
            if len(types) > 1: separate = True

            if separate:
                print ':'
                for i in range(vlen): display_object (v[i], '['+str(i)+']', full=full, indent=indent+2)
            elif vlen == 1:
                print '=',[v[0]]
            elif full or vlen < 5:
                print '=',v
            else:
                print '=',[v[0],'...',v[vlen-1]]

        elif isinstance(v, tuple):
            print 'tuple',slen,
            print '=',v
          
        elif isinstance(v, (dict, record)):
            if isinstance(v, record):
                print 'record',slen,':'
            elif isinstance(v, dict):
                print 'dict',slen,':'
            keys = v.keys()
            n = len(keys)
            types = {}
            for key in keys: types[str(type(v[key]))] = 1
            if len(types) > 1:
                for key in v.keys(): display_object (v[key], key, full=full, indent=indent+2)
            elif full or n<10:
                for key in v.keys(): display_object (v[key], key, full=full, indent=indent+2)
            else:
                for key in [keys[0]]: display_object (v[key], key, full=full, indent=indent+2)
                if n > 20:
                    print '**',(indent+2)*' ','.... (',n-2,'more fields of the same type )'
                else:
                    print '**',(indent+2)*' ','.... ( skipped keys:',keys[1:n-1],')'
                for key in [keys[n-1]]: display_object (v[key], key, full=full, indent=indent+2) 
        

        else: 
            print type(v),'=',v

    else: 
        # All other types:
        print type(v),'=',v

    if indent == 0: print





#********************************************************************************
#********************************************************************************
#******************** PART VI: Standalone test routines *************************
#********************************************************************************
#********************************************************************************

if __name__ == '__main__':
   print '\n****************\n** Local test of: JEN_record.py:\n'

   if 1:
      rr = record(aa='bb', bb=6, ee='cc', cc='aa', dd='cc')
      display_object (rr, 'rr', 'before')
      replace_reference(rr)
      display_object (rr, 'rr', 'after')
      
   print '\n** End of local test of: JEN_record.py \n*************\n'

#********************************************************************************



