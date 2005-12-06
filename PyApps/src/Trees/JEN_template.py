# JEN_template.py:
#
# Author: J.E.Noordam
#
# Short description:
#    Template for little python module
#
# History:
#    - 04 dec 2005: creation
#
# Full description:
#


#================================================================================
# Preamble
#================================================================================

from Timba.TDL import *
from Timba.Trees import JEN_record




#********************************************************************************
#********************************************************************************
#******************** PART VI: Standalone test routines *************************
#********************************************************************************
#********************************************************************************

if __name__ == '__main__':
   print '\n****************\n** Local test of: JEN_template.py:\n'
   from Timba.Trees import JEN_record


   if 1:
      pp = dict(aa=3, bb=4)
      JEN_record.display_object(pp,'pp','...')
   print '\n** End of local test of: JEN_template.py \n*************\n'

#********************************************************************************



