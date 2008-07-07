"""
The QuickRef module offers a quick reference to MeqTrees.
When used in the meqbrowser, it generates example subtrees
for user-selected categories, which can be executed (with
user-defined request domains) to inspect the result.

Lots of bookmarks are generated for easy inspection.
In addition, the relevant section of the hierarchical
help-string can be inspected at each level, by displaying
any node in the tree with the Record Browser. Look for
the field 'quickref_help'.

The entire hierarchical help (for the selected categories)
may be shown/printed/saved as well.

The QuickRef module gets its information from an arbitrary number
of contributing QR_... modules. Such modules may be generated by
any MeqTrees contributor, following a number of simple rules.
(Look for instance at the module QR_MeqNodes.py)
"""

# file: ../JEN/demo/QuickRef.py:
#
# Author: J.E.Noordam
#
# Short description:
#    A quick reference to all MeqTree nodes and subtrees.
#    It makes actual nodes, and prints help etc

#
# History:
#   - 23 may 2008: creation
#   - 07 jun 2008: added 4D (L,M)
#
# Remarks:
#
#   - AGW: Middle-clicking a node in the browser could display its quickref_help
#          (field in the state record) just like right-click option in the various plotter(s)....
#          The quickref_help is in the form of a record.
#          Tony already has a popup uption for selecting from multiple vellsets,
#          which includes an expansion tree. The quickref_help popup needs the same.
#
#   - AGW: Left-clicking a node displays the state record, except the Composer...
#          It would be nice if it were easier to invoke the relevant plotter...
#          (at this moment it takes to many actions, and the new display is confusing)
#
#   - OMS: Can we plot the result of each request in a sequence while it is running....?
#          (this problem may have been solved....)
#
#   - AGW: Flag-information is lost when a panel is floated in a separate window.
#          Also in the plot-memory... (Try unary_elementary sqrt(noise3))
#
#   - AGW: When a panel is floated, it is no longer possible to view it ("view using")
#          with another viewer (e.g. the Record Browser). This is inconvenient, but
#          not a show-stopper, since one can change viewers before floating the panel.
#          NB: Strangely enough, a floating view DOES update when re-executing (??) 
#
#   - AGW: However, after one has de-floated a panel, it re-appears in its panel, but it
#          is no longer possible to view it with another viewer
#          ("None-type object does not have an attribute 'udi'", or something like that...)
#
#   - AGW: When the flags are "toggled" the colorbar scale does not change,
#          and neither do the mean/stddev in the top-right corner...
#
#   - OMS: Meow.Bookmarks needs a folder option.... (Mind yiou, I probably do not
#          understand it properly. I will use my own bookmarks for the moment)
#
#   - OMS: Is there a way to attach fields like a quickref_help record to the
#          state record (initrec?) of an existing node?
#
#   - AGW: Can we have a QuickRef Viewer? It would be a version of the Record Browser
#          that displays only the (opened!) quickref_help field of the state record in a panel.
#          This would allow me to make bookmarks with this viewer, of nodes that contain a
#          particularly useful/relevant quickref_help.
#
#   - OMS: The page tabs in the right panel of the browser are too large, because their
#          letters are too large. In this way, they run off the page too quickly.
#          Can we have smaller letters, and multi-line tabs? 
#
#   - AGW: Right-click plotting in Log scale does not work if 1D data
#          (it only produces a colorbar...)
#          NB: it is only offered as an option when doing 1D after 2D...
#
#   - OMS: TDLOption separator (None): gives problems.... (should I rebuild?)
#          Same with TDLRuntimeOptionSeparator()
#          It complains that the option name has to be a string....
#
#   - OMS: What does determine the order in which the TDLOption values are read from
#          the tdlconf file? Their order in that file?
#
#   - AGW/OMS: The result plotter does not always refresh when switching
#          from 4D to 2D, even in the rqid is changed (see EasyTwig, polynomial)
#
#   - AGW: I often use the Composer to display the values of a group of scalar nodes
#          in a single panel. It would be nice if each value could be labelled, just
#          as the composer/inspector tracks are labelled with 'plot_labels'.
#          Can we use plot_labels for this too? (after all, it is the Result Plotter)
#
#   - OMS: For clarity, I often put parameter values in the names of nodes that are
#          displayed via a bookmark page. This means that, when I change the parameters
#          via TDL options the names of the displayed nodes change. When I re-execute,
#          the bookpage does not update. This is annoying, partly because I have to search
#          for the page in the bookmarks. But also because the user may not realise that
#          this has happened, and is thus looking at the wrong picture.
#          Can we have some (automatic?) bookpage refresh option, that uses the bookpage
#          name (which after all has not changed)?
#
#   - OMS: QuickRef always gives lots of errors of the type: "tensor dimensions of child
#          result 1 does not math the others". Executing EasyTwig is a good way to study
#          this problem.
#
#   - OMS: (this one is serious!) When I include the TDLCompileMenu from more than one
#          QR module to the compile menu of QuickRef, they do not appear....!
#
# Description:
#


 
#********************************************************************************
# Initialisation:
#********************************************************************************

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
from Timba.Meq import meq

Settings.forest_state.cache_policy = 100
Settings.forest_state.bookmarks = []

from Timba.Contrib.JEN.QuickRef import QuickRefUtil as QRU
# from Timba.Contrib.JEN.QuickRef import EasyTwig as ET
# from Timba.Contrib.JEN.QuickRef import EasyNode as EN


#********************************************************************************
#********************************************************************************

failed =  ': ... module not available ...'

if True:
   try:
      module = 'MeqNodes'
      from Timba.Contrib.JEN.QuickRef import QR_MeqNodes        
      avail_MeqNodes = True
   except:
      QR_MeqNodes = TDLCompileOption('avail_'+module,
                                     'QR_'+module+failed, [False])
   try:
      module = 'UserNodes'
      from Timba.Contrib.JEN.QuickRef import QR_UserNodes        
      avail_UserNodes = True
   except:
      QR_UserNodes = TDLCompileOption('avail_'+module,
                                      'QR_'+module+failed, [False])
   try:
      module = 'execution'
      from Timba.Contrib.JEN.QuickRef import QR_execution        
      avail_execution = True
   except:
      QR_execution = TDLCompileOption('avail_'+module,
                                      'QR_'+module+failed, [False])
   try:
      module = 'template'
      from Timba.Contrib.JEN.QuickRef import QR_template        
      avail_template = True
   except:
      QR_template = TDLCompileOption('avail_'+module,
                                     'QR_'+module+failed, [False])
   try:
      module = 'solving'
      from Timba.Contrib.JEN.QuickRef import QR_solving        
      avail_solving = True
   except:
      QR_solving = TDLCompileOption('avail_'+module,
                                    'QR_'+module+failed, [False])
   try:
      module = 'TreeDefinition'
      from Timba.Contrib.JEN.QuickRef import QR_TreeDefinition        
      avail_TreeDefinition = True
   except:
      QR_TreeDefinition = TDLCompileOption('avail_'+module,
                                     'QR_'+module+failed, [False])

   try:
      module = 'PyNodePlot'
      from Timba.Contrib.JEN.QuickRef import QR_PyNodePlot        
      avail_PyNodePlot = True
   except:
      QR_PyNodePlot = TDLCompileOption('avail_'+module,
                                       'QR_'+module+failed, [False])



modules = ['MeqNodes','execution','solving',
           'UserNodes','PyNodePlot','TreeDefinition','template']
for module in modules:
   print '-',module,':',eval('avail_'+module)



#--------------------------------------------------------------------------------

TDLCompileMenu("QuickRef Categories:",
               TDLOption('opt_allcats',"override: include all categories", False),
               
               # TDLMenu("QR_MeqTree: general items", QR_general, toggle='opt_general'),
               # TDLMenu("QR_MeqBrowser: Using the meqbrowser", QR_MeqBrowser, toggle='opt_MeqBrowser'),

               TDLMenu("QR_TreeDefinition: Defining trees", QR_TreeDefinition, toggle='opt_TreeDefinition'),
               TDLMenu("QR_execution: Requests and Results", QR_execution, toggle='opt_execution'),
               TDLMenu("QR_MeqNodes: Overview of available nodes", QR_MeqNodes, toggle='opt_MeqNodes'),
               TDLMenu("QR_UserNodes: user-defined nodes", QR_UserNodes, toggle='opt_UserNodes'),
               TDLMenu("QR_solving: Solving for MeqParm values", QR_solving, toggle='opt_solving'),
               TDLMenu("QR_PyNodePlot: pynodes for plotting", QR_PyNodePlot, toggle='opt_PyNodePlot'),

               # TDLMenu("QR_boilerplate: swollen text", QR_boilerplate, toggle='opt_boilerplate'),

               TDLMenu("QR_template: Template/help for making QR modules", QR_template, toggle='opt_template'),
               toggle='opt_QuickRef',
               )




#-------------------------------------------------------------------------------

def _define_forest (ns, **kwargs):

   # Make bundles of (bundles of) categories of nodes/subtrees:
   global rider
   rider = QRU.create_rider()                # CollatedHelpRecord object
   rootnodename = 'QuickRef'                # The name of the node to be executed...
   path = rootnodename                      # Root of the path-string

   cc = []

   if avail_TreeDefinition and (opt_allcats or opt_TreeDefinition):   
      cc.append(QR_TreeDefinition.QR_TreeDefinition(ns, path, rider=rider))

   if avail_execution and (opt_allcats or opt_execution):   
      cc.append(QR_execution.QR_execution(ns, path, rider=rider))

   if avail_MeqNodes and (opt_allcats or opt_MeqNodes):   
      cc.append(QR_MeqNodes.QR_MeqNodes(ns, path, rider=rider))

   if avail_UserNodes and (opt_allcats or opt_UserNodes):   
      cc.append(QR_UserNodes.QR_UserNodes(ns, path, rider=rider))

   if avail_solving and (opt_allcats or opt_solving):   
      cc.append(QR_solving.QR_solving(ns, path, rider=rider))

   if avail_PyNodePlot and (opt_allcats or opt_PyNodePlot):   
      cc.append(QR_PyNodePlot.QR_PyNodePlot(ns, path, rider=rider))

   if avail_template and (opt_allcats or opt_template):   
      cc.append(QR_template.QR_template(ns, path, rider=rider))

   # Make the outer bundle (of node bundles):
   QRU.bundle (ns, path, nodes=cc, help=__doc__, rider=rider)

   # Finished:
   return True
   


#********************************************************************************
#********************************************************************************

def _tdl_job_execute_1D_f (mqs, parent):
   return QRU._tdl_job_execute_f (mqs, parent, rootnode='QuickRef')

def _tdl_job_execute_2D_ft (mqs, parent):
   return QRU._tdl_job_execute_ft (mqs, parent, rootnode='QuickRef')

def _tdl_job_execute_4D_ftLM (mqs, parent):
   return QRU._tdl_job_execute_ftLM (mqs, parent, rootnode='QuickRef')

def _tdl_job_execute_sequence (mqs, parent):
   return QRU._tdl_job_execute_sequence (mqs, parent, rootnode='QuickRef')

#-------------------------------------------------------------------------------

def _tdl_job_m (mqs, parent):
   return QRU._tdl_job_m (mqs, parent)

def _tdl_job_print_doc (mqs, parent):
   return QRU._tdl_job_print_doc (mqs, parent, rider, header='QuickRef')

def _tdl_job_print_hardcopy (mqs, parent):
   return QRU._tdl_job_print_hardcopy (mqs, parent, rider, header='QuickRef')

def _tdl_job_show_doc (mqs, parent):
   return QRU._tdl_job_show_doc (mqs, parent, rider, header='QuickRef')

def _tdl_job_save_doc (mqs, parent):
   return QRU._tdl_job_save_doc (mqs, parent, rider, filename='QuickRef')



#=====================================================================================
# Standalone test (without the browser):
#=====================================================================================

if __name__ == '__main__':

   print '\n** Start of standalone test of: QuickRef.py:\n' 
   ns = NodeScope()

   if 0:
      _define_forest(ns)
      if 1:
         print rider.format()
            

   print '\n** End of standalone test of: QuickRef.py:\n' 

#=====================================================================================


