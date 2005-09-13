script_name = 'MG_JEN_dataCollect.py'
last_changed = 'h10sep2005'

# Short description:
#   Some visualisation subtrees

# Author: Jan Noordam (JEN), Dwingeloo

# History:
# - 24 aug 2005: creation

# Copyright: The MeqTree Foundation 

#================================================================================
# Import of Python modules:

from Timba.TDL import *

from numarray import *
# from string import *
from copy import deepcopy

from Timba.Contrib.JEN import MG_JEN_exec
from Timba.Contrib.JEN import MG_JEN_forest_state
from Timba.Contrib.JEN import MG_JEN_twig



#================================================================================
# Required functions:
#================================================================================


#--------------------------------------------------------------------------------
# Tree definition routine (may be executed from the browser):
# To be used as example, for experimentation, and automatic testing.

def _define_forest (ns):
   MG_JEN_exec.on_entry (ns, script_name)

   # Generate a list (cc) of one or more node bundles (bb):
   cc = []

   # Make 'clouds' of nodes scattered (stddev) around mean:
   xx = MG_JEN_twig.cloud (ns, n=3, name='xx', qual=None, stddev=1, mean=complex(10))
   yy = MG_JEN_twig.cloud (ns, n=3, name='yy', qual=None, stddev=1, mean=complex(0))
   zz = MG_JEN_twig.cloud (ns, n=3, name='zz', qual=None, stddev=1, mean=complex(0,-2))
 
   # Make dataCollect nodes of type 'realvsimag' for the various clouds:
   bb= [] 
   scope = 'scope1'
   dd = []
   dc = dcoll(ns, xx, scope=scope, tag='xx', color='red', errorbars=True)  
   bb.append(dc['dcoll'])
   dd.append(dc)

   dc = dcoll(ns, yy, scope=scope, tag='yy', color='blue', errorbars=False)
   bb.append(dc['dcoll']) 
   dd.append(dc)
 
   dc = dcoll(ns, zz, scope=scope, tag='zz', color='magenta', errorbars=True)
   bb.append(dc['dcoll']) 
   dd.append(dc)

   # Concatenate the dataCollect nodes in dd:
   dc = dconc(ns, dd, scope=scope, tag='combined') 
   bb.append(dc['dcoll'])
   cc.append(MG_JEN_exec.bundle(ns, bb, 'realvsimag', show_parent=False))
 
   # Test of type = spectra:
   bb = []
   dc = dcoll(ns, xx, scope='scope2', type='spectra') 
   bb.append(dc['dcoll'])  
   cc.append(MG_JEN_exec.bundle(ns, bb, 'spectra', show_parent=False))

   # Finished: 
   return MG_JEN_exec.on_exit (ns, script_name, cc)


#================================================================================
# Available styles (as used by AGW):
#================================================================================

#	if (type=='color') {
#           ss := 'black';
#	    ss := [ss,"red blue darkGreen magenta"];
#	    ss := [ss,"darkGray darkMagenta darkRed darkYellow"];
#	    ss := [ss,"darkBlue darkCyan gray"];
#	    ss := [ss,"yellow lightGray cyan green"];
#	    # ss := [ss,"none white"];
#	} else if (type=='spectrum_color') {
#	    ss := "hippo grayscale brentjens";
#	} else if (type=='symbol') {
#	    ss := "circle rectangle square ellipse";
#	    ss := [ss, "xcross cross triangle diamond"];
#	    # ss := [ss,"none"];
#	} else if (type=='line_style') {
#	    ss := "dots lines steps stick";
#	    ss := [ss, "SolidLine DashLine DotLine DashDotLine DashDotDotLine"];
#	    ss := [ss, "solidline dashline dotline dashdotline dashdotdotline"];
#	    # ss := [ss,"none"];



#================================================================================
# Importable function(s): The essence of a MeqGraft (MG) script.
# To be imported into user scripts. 
#================================================================================


def dcoll (ns, node=[], **pp):
   """visualises the given node(s) and return a dcoll dict"""

   uniqual = MG_JEN_forest_state.uniqual('MG_JEN_dataCollect::dcoll()')

   # Supply default arguments:
   pp.setdefault('scope', '<scope>')    # 'scope (e.g. rawdata)'
   pp.setdefault('tag', '<tag>')        # plot tag (e.g. allcorrs)
   pp.setdefault('title',False )        # plot title
   pp.setdefault('insert', False)       # if node given, insert dconc node
   pp.setdefault('xlabel', '<xlabel>')  # x-axis label
   pp.setdefault('ylabel', '<ylabel>')  # y-axis label
   pp.setdefault('color', 'red')        # plot color
   pp.setdefault('style','dot' )        # plot style
   pp.setdefault('size', 10)            # plot size
   pp.setdefault('type', 'realvsimag')  # plot type (realvsimag or spectra)
   pp.setdefault('errorbars', False)    # if True, plot stddev as crosses around mean
   pp.setdefault('bookmark', False)     # name of dcoll bookmark (False=none)
   pp.setdefault('bookpage', False)     # name of bookpage to be used (False=none)
   pp = record(pp)
   
   
   # Initialise the output dict:
   dcoll = dict(stripped=[], mean=[], stddev=[], input=pp, attrib=None,
                dcoll_mean=None, dcoll_stddev=None, dcoll=None)
   
   # Make sure that the input is a list:
   if not isinstance(node, (list, tuple)): node = [node]
   
   # Make the visualisation chains per node:
   for i in range(len(node)):
      stripped = ns << Meq.Stripper (node[i])
      dcoll['stripped'].append (stripped)
      if pp.type == 'realvsimag':
         dcoll['mean'].append (ns << Meq.Mean(stripped))
         if pp.errorbars:
            dcoll['stddev'].append (ns << Meq.StdDev(stripped))
            

   # Make dataCollection node(s):
   # Initialise the plot attribute record (changed below):
   scope_tag = str(pp.scope)+'_'+str(pp.tag)
   dcoll_name = 'dcoll_'+scope_tag
   if not isinstance(pp.title, str): pp.title = scope_tag
   attrib = record(plot=record(), tag=pp.tag)
   if pp.type == 'spectra':
      attrib['plot'] = record(type=pp.type, title=pp.title,
                              spectrum_color='hippo',
                              x_axis=pp.xlabel, y_axis=pp.ylabel)
      dcoll['dcoll'] = ns[dcoll_name](uniqual) << Meq.DataCollect(children=dcoll['stripped'],
                                                                 top_label=hiid('visu'),
                                                                 attrib=attrib)

   else:
      # Assume pp.type == 'realvsimag'
      attrib['plot'] = record(type=pp.type, title=pp.title,
                              color=pp.color,
                              symbol='circle', symbol_size=pp.size,
                              mean_circle=1, mean_circle_color=pp.color,
                              mean_circle_style='DashLine', mean_arrow=1)
    
    
      if not pp.errorbars:
         # Indicate just the mean values of the child results:
         dcoll['dcoll'] = ns[dcoll_name](uniqual) << Meq.DataCollect(children=dcoll['mean'],
                                                                    top_label=hiid('visu'),
                                                                    attrib=attrib)
      else:
         # Indicate the stddev of the child results with 'error bars':

         # Make a separate dcoll for the means:
         attr = deepcopy(attrib)
         if not isinstance(attr.tag, list): attr.tag = [attr.tag]
         attr.tag.append('Mean')
         dc_mean = ns[dcoll_name+'_mean'] << Meq.DataCollect(children=dcoll['mean'],
                                                            top_label=hiid('visu'),
                                                            attrib=attr)
         dcoll['dcoll_mean'] = dc_mean
         
         # Make a separate dcoll for the stddevs:
         attr = deepcopy(attrib)
         if not isinstance(attr.tag, list): attr.tag = [attr.tag]
         attr.tag.append('StdDev')
         dc_stddev = ns[dcoll_name+'_stddev'] << Meq.DataCollect(children=dcoll['stddev'],
                                                                top_label=hiid('visu'),
                                                                attrib=attr)
         dcoll['dcoll_stddev'] = dc_stddev
         
         # Combine the mean and stddev dcolls:
         attr = deepcopy(attrib)
         attr.plot.stddev_circle=1
         attr.plot.stddev_circle_color=pp.color
         attr.plot.stddev_circle_style='DotLine'
         attr.plot.value_tag = 'Mean'
         attr.plot.error_tag = 'StdDev'
         dcoll['dcoll'] = ns[dcoll_name](uniqual) << Meq.DataCollect(children=[dc_mean, dc_stddev],
                                                                    top_label=hiid('visu'),
                                                                    attrib=attr)

   # Attach the attribute record to the output record, for later use:
   dcoll['attrib'] = attrib
   dcoll['tag'] = dcoll['attrib']['tag']            # used by JEN_dconc() below
   
   # Optionally, make a bookmark for the dconc node:
   if isinstance(pp.bookpage, str):
      bm = MG_JEN_forest_state.bookmark (dconc['dcoll'], page=pp.bookpage)
   elif isinstance(pp.bookmark, str):
      bm = MG_JEN_forest_state.bookmark (dconc['dcoll'], pp.bookmark)
      
   # If an insert-node is specified, make the dconc node a step-child of a
   # MeqSelector node just before it, to issue requests:
   if not isinstance(pp.insert, bool):
      output = ns[scope_tag+'_branch'](uniqual) << Meq.Selector(insert, stepchildren=dcoll['dcoll'])
      return output
   
   # Otherwise, return the dcoll record, with root node dcoll['dcoll']
   return dcoll



#=========================================================================================
# Concatenate the given dcolls (dicts, see above) into a dconc node
#=========================================================================================

def dconc (ns, dcoll, **pp):

   uniqual = MG_JEN_forest_state.uniqual('MG_JEN_dataCollect::dconc()')
 
  # Supply default arguments:
   pp.setdefault('scope', '<scope>')      # 'scope (e.g. rawdata)'
   pp.setdefault('tag', '<tag>')          # plot tag (e.g. allcorrs)
   pp.setdefault('title',False )          # plot title
   pp.setdefault('insert', False)         # if node given, insert dconc node
   pp.setdefault('xlabel', '<xlabel>')    # x-axis label
   pp.setdefault('ylabel', '<ylabel>')    # y-axis label
   pp.setdefault('bookmark', False)       # name of dcoll bookmark (False=none)
   pp.setdefault('bookpage', False)       # name of bookpage to be used (False=none)
   pp = record(pp)


   # Initialise the output dict:
   dconc = dict(input=pp, cc=[], attrib=None, dcoll=None)

   scope_tag = str(pp.scope)+'_'+str(pp.tag)
   dconc_name = 'dconc_'+scope_tag
   if not isinstance(pp.title, str): pp.title = scope_tag
   
   attrib = record(plot=record(), tag=['dconc'])
   attrib.plot.title = pp.title
   
   # Collect the dcoll nodes in a list (cc):
   if not isinstance(dcoll, (list, tuple)): dcoll = [dcoll]
   for i in range(len(dcoll)):
      dconc['cc'].append(dcoll[i]['dcoll'])     #
      # NB: See the discussion with AGW below....
      # attrib['tag'].append(dcoll[i]['tag'])     # concatenate the dcoll tags (uniqual?)
    
   # Make concatenations (dconc) node:
   dconc['dcoll'] = ns[dconc_name](uniqual) << Meq.DataCollect(children=dconc['cc'],
                                                     top_label=hiid('visu'),
                                                     attrib=attrib)

   # Optionally, make a bookmark for the dconc node:
   if isinstance(pp.bookpage, str):
      bm = MG_JEN_forest_state.bookmark (dconc['dcoll'], page=pp.bookpage)
   elif isinstance(pp.bookmark, str):
      bm = MG_JEN_forest_state.bookmark (dconc['dcoll'], pp.bookmark)

   # If an insert-node is specified, make the dconc node a step-child of a
   # MeqSelector node just before it, to issue requests:
   if not isinstance(pp.insert, bool):
      output = ns[dconc_name+'_branch'](uniqual) << Meq.Selector(insert, stepchildren=dconc['dcoll'])
      return output

   # Otherwise, just return the dconc record:
   return dconc



#================================================================================
# From: bugzilla-daemon@astron.nl
# To: noordam@astron.nl
# Subject: [Bug 238] dataConcat only uses the color of its FIRST child only
# Date: Fri, 26 Aug 2005 03:28:25 +0200

# http://lofar9.astron.nl/bugzilla/show_bug.cgi?id=238

# ------- Additional Comments From Tony.Willis@nrc-cnrc.gc.ca  2005-08-26 03:28 -------
# This is a feature not a bug!! I ran the current version of WSRT_cps.tdl as
# checked into CVS and had a look at the DataConcat node 'dconc_rawdata_paral'. At
# its top level we have the tag ('dconc', 'XX', 'YY'). The two lower levels have tags
# "XX", and "YY" respectively. Since the higher level tag 'contains' the lower
# level ones, the implication is that at the higher level we 'envelop' the lower
# level ones and use 'common' attributes - the first ones found. Since the color
# 'red' is first in the list, it is used everywhere. If you had used just the tag
# 'dconc' at the parent level, you should have obtained plots with separate colors.

# I believe that we agreed on the above behaviour, although my plotting_rules
# text only says:

# # A few parameters, such as the attrib.tag field, are amalgamated
# as we go through the tree. 

# So if you had top level tag 'dconc' at the lower level you would have e.g.
# dconc+XX as the leaf tag. However since your top level tag ("dconc", XX", 'YY")
# already contains XX there is nothing to amalgamate! (I suppose we are using
# something vaguely equivalent to set theory here!)

# I shall leave the bug open in case you wish to complain ...

#************************************************************************************

# From: Tony Willis <Tony.Willis@nrc-cnrc.gc.ca>
# To: noordam@astron.nl, smirnov@astron.nl
# cc: twillis@drao.nrc.ca
# Subject: curent plotting rules - summary
# Date: Mon, 31 Jan 2005 19:29:44 -0800 (PST)

# Hi Chaps

# Plotting rules - current status

# Firstly and most important, plotting attributes are given to a
# MeqDataCollect mode as part of an 'attrib' record. The 'attrib'
# record itself is part of an 'extra' record along with
# a "Visu" specification. e.g.

# mqs.meq('Create.Node',meq.node('MeqDataCollect','xx',children=child_str1,
# extra = [top_label = hiid("Visu"), attrib=attrib_rec_yx]));

# The 'attrib' record itself, can contain either or both a 'plot' or
# 'tag' subrecord. e.g. the 'attrib_rec_yx' record given above could
# be constructed as:

# attrib_yx1 := [color="black", plot_type= "spectra"];
# attrib_rec_yx := [=]
# attrib_rec_yx.plot := attrib_yx1
# attrib_rec_yx.tag := "YX test"

# In glish, 'tag' fields should be specified within double quotes, as above.
# This will cause them to be turned into a vector of strings e.g. ('YX','test')

# The 'plot' subrecord, will contain a record of allowable plotting
# specifications e.g. as shown above
# attrib_yx1 := [color="black", plot_type= "spectra"];

# A visualization tree can be constructed by joining a number of
# MeqDataCollect nodes into a Meqtree. Each MeqDataCollect 'Visu' node
# can be given its own 'attrib' record of plotting information
# as shown above. Since each MeqDataCollect can have its own set of
# plotting parameters, a series of rules has been specified regarding
# how plot parameters given at various levels in the tree are combined
# to form a 'final set of plot specifications when several MeqDataCollect
# nodes have been joined together into a tree.

# For most parameters, a downstream (toward the root of the tree)
# specification overrides an upstream (toward the leaves of the tree)
# specification.  So, for instance, individual
# leaves of a tree might be told to plot 'spectra' but if a parent
# root node has been told to plot 'realvsimag' then if the user
# clicks on the parent 'Visu' node, a 'realvsimag' plot will be produced.

# A few parameters, such as the attrib.tag field, are amalgamated
# as we go through the tree.

# Only leaf nodes in the tree have actual plot data. As we traverse a
# 'Visu' tree a list of attribute records is collected. When we
# get to a leaf node, the leaf node goes through the list of attribute
# records to obtain the actual parameters it will use to construct
# its part of the plot. The attribute list is in the order
# root -> ... -> leaf, so for those attibutes where a parent's value
# overrides those of a child, as soon as a particular attribute is found
# it is ignored for the remainder of the list.

# We now give a list of the attrib.plot key words  and their
# allowable values. For those keywords with choices, the default,
# if nothing is specified, is the first value in the list.
# e.g. the default for color is 'blue' while the default
# spectrum_color for a 'spectra' plot is 'hippo' - the color
# display used in the HippoDraw package.


# Key word                           allowable values
# _________________                 _______________________________
# plot_type | type                   realvsimag | spectra

# The following key_words have meaning for a 'realvsimag' plot

# mean_circle                            F | T

# stddev_circle (not yet available)      F | T

# mean_arrow                             F | T

# symbol_size                        integer number (default = 10 pixels)

# symbol                                 one of
#                         'circle' 'none' 'rectangle' 'square' 'ellipse'
#                         'none 'xcross' 'cross' 'triangle' 'diamond'

# line_style                             one of
#                  'dots' 'lines' 'steps' 'stick' 'none'
#                  'SolidLine' 'DashLine' 'DotLine' 'DashDotLine' 'DashDotDotLine'
#                  'solidline' 'dashline' 'dotline' 'dashdotline' 'dashdotdotline'

# (Note: line_style is not used that much at present, but feel free to
# experiment and find out what, if anything, appears!)

# value_tag                          single word

# error_tag                          single word

# title                              string - in Glish surrounded by single
#                                    quotation (') marks

# color                                  one of
#                     'blue' 'black' 'cyan' 'gray' 'green' 'none'
#                     'magenta' 'red' 'white' 'yellow' 'darkBlue' 'darkCyan'
#                     'darkGray' 'darkGreen' 'darkMagenta' 'darkRed' 'darkYellow'
#                     'lightGray'

# legend (glish record)
# with fields  - plot                glish string
#              - popup               glish string
# (popup is not yet implemented)
# The contents of 'legend' are amalgamated as we traverse a tree.

# x_axis                             glish string
# y_axis                             glish string


# The following key_word has meaning for a 'spectra' plot

# spectrum_color                        one of
#                                'hippo' 'grayscale' 'brentjens'

# Notes on key words:

# value_tag and error_tag:
# If a MeqDataCollect leaf node ends up getting both a value_tag and a error_tag
# keyword it will assume that it is to produce a special variant of
# the realvsimag plot in which there are two data sources, one with 'values' and
# a second with the 'errors' associated with the values. If the leaf node
# has a 'tag' field which contains the 'value_tag' label, then the
# leaf node knows it is handling the data values. If a leaf node has a tag
# which contains the 'error_tag' label then it knows that it is handling
# the associated 'error' data.

# Note - more to come but this is a start ....

# Cheers

# Tony
# ___________
# Tony Willis
# National Research Council   Tony.Willis@nrc-cnrc.gc.ca
# Box 248                     (250)493-2277
# Penticton, BC  V2A 6J9      fax: 493-7767
# Government of Canada        Gouvernement du Canada








#********************************************************************************
#********************************************************************************
#********************************************************************************
#********************************************************************************
#********************************************************************************
# Initialisation and testing routines
# NB: this section should always be at the end of the script
#********************************************************************************

#-------------------------------------------------------------------------
# The forest state record will be included automatically in the tree.
# Just assign fields to: Settings.forest_state[key] = ...

MG_JEN_forest_state.init(script_name)



#-------------------------------------------------------------------------
# Meqforest execution routine (may be called from the browser):
# The 'mqs' argument is a meqserver proxy object.

def _test_forest (mqs, parent):
   # The following call shows the default settings explicity:
   # return MG_JEN_exec.meqforest (mqs, parent, nfreq=20, ntime=19, f1=0, f2=1, t1=0, t2=1, trace=False) 

   # There are some predefined domains:
   # return MG_JEN_exec.meqforest (mqs, parent, domain='lofar')   # (100-110 MHz)
   # return MG_JEN_exec.meqforest (mqs, parent, domain='21cm')    # (1350-1420 MHz)

   # NB: It is also possible to give an explicit request, cells or domain
   # NB: In addition, qualifying keywords will be used when sensible

   # If not explicitly supplied, a default request will be used.
   return MG_JEN_exec.meqforest (mqs, parent)



#-------------------------------------------------------------------------
# Test routine to check the tree for consistency in the absence of a server

if __name__ == '__main__':
   print '\n*******************\n** Local test of:',script_name,':\n'

   if 1:
      MG_JEN_exec.without_meqserver(script_name, callback=_define_forest)

   ns = NodeScope()

   if 0:
      rr = 0
      # ............
      # MG_JEN_exec.display_object (rr, 'rr', script_name)
      # MG_JEN_exec.display_subtree (rr, script_name, full=1)

   print '\n** End of local test of:',script_name,'\n*******************\n'
       
#********************************************************************************
#********************************************************************************




