# file: ../Grunt/ParameterizationPlus.py

# History:
# - 26may2007: creation
# - 07jun2007: allow {100~10%}
# - 07jun2007: p_deviation_expr()
# - 08jun2007: p_quals2list() and p_tags2list()
# - 03jul2007: added .nodescope(new=None)
# - 09jul2007: introduced ParmGroup class
# - 17jul2007: .quals2list() and .tags2list()

# Description:

# The Grunt ParameterizationPlus class is derived from the
# Meow Parameterization class. It adds some extra functionality
# for groups of similar parms, which may find their way into the
# more official Meow system eventually.

# Compatibility:
# - The Grunt.ParameterizationPlus class is derived from Meow.Parameterization
# - Convert an object derived from Meow.Parameterization. Its parmdefs are
#   copied into a single parmgroup.

#======================================================================================

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

import Meow

from Timba.Contrib.JEN.Grunt import ParmGroupManager
from Timba.Contrib.JEN.Grunt import NodeList
from Timba.Contrib.JEN.Grunt import display
from Timba.Contrib.JEN.Expression import Expression

from copy import deepcopy

#======================================================================================

class ParameterizationPlus (Meow.Parameterization):
    """The Grunt ParameterizationPlus class is derived from the
    Meow Parameterization class. It adds some extra functionality
    for groups of similar parms, which may find their way into the
    more official Meow system eventually."""

    def __init__(self, ns=None, name=None,
                 quals=[], kwquals={},
                 namespace=None,
                 framework='Grunt', classname=None,
                 merge=None):

        # Scopify ns, if necessary:
        if is_node(ns):
            ns = ns.QualScope()        

        # Make sure that there is a nodescope (Required by Meow.Parameterization)
        if ns==None:
            ns = NodeScope()

        #------------------------------------
        # NB: What about dropping quals/kwquals completely, since these may be
        #     introduced by passing ns as a node, rather than a nodescope.
        #     See also the function .nodescope()
        # Eventually.... (perverse coupling)? 
        #------------------------------------

        name = str(name)                           # just in case....

        # Make a string for reporting:
        self._frameclass = classname
        if not isinstance(self._frameclass,str):
            ss = str(type(self)).split('.')
            ss = ss[len(ss)-1].split("'")
            self._frameclass = ss[0]
        if isinstance(framework,str):
            self._frameclass = framework+'.'+self._frameclass
        # print '\n** frameclass =',self._frameclass,'\n'
            

        # Make a little more robust 
        quals = self.quals2list(quals)

        # Avoid duplication of qualifiers:
        if ns:
            qq = ns['dummy'].name.split(':')       # make a list (qq) of qualifiers
            for q in qq:
                if q in quals: quals.remove(q)
            if name in quals: quals.remove(name)

        Meow.Parameterization.__init__(self, ns, name,
                                       quals=quals,
                                       kwquals=kwquals)

        # TDL Options:
        self.tdloption_namespace = namespace    
        self._TDLCompileOptionsMenu = None   
        self._TDLCompileOption = dict()
        self.tdloption_reset = dict()
        for key in self.tdloption_reset.keys():
            setattr(self, key, self.tdloption_reset[key])

        # The pgm has the qualified ns, and the same namespace.....
        self._pgm = ParmGroupManager.ParmGroupManager(self.ns,
                                                      parent=self.name,
                                                      namespace=namespace)
                                                      
        # Optional: Copy the parameterization of another object:
        if merge:
            self._pgm.merge(merge, trace=False)
        
        return None


    #---------------------------------------------------------------


    def nodescope (self, ns=None):
        """Get/set the internal nodescope (can also be a node)"""
        if ns:
            if is_node(ns):
                self.ns = ns.QualScope()        
            else:
                self.ns = ns
            # Pass the new nodescope on to its parmgroup(s):
            self._pgm.nodescope(self.ns)
        # Always return the current nodescope:
        return self.ns


    def namespace(self, prepend=None, append=None):
        """Return the namespace string (used for TDL options etc).
        If either prepend or apendd strings are defined, attach them.
        NB: Move to the ParameterizationPlus class?
        """
        if prepend==None and append==None:
            return self.tdloption_namespace                    # just return the namespace
        # Include the namespace in a string:
        ss = ''
        if isinstance(prepend, str): ss = prepend+' '
        if self.tdloption_namespace:
            ss += '{'+str(self.tdloption_namespace)+'}'
        if isinstance(append, str): ss += ' '+append
        return ss
    

    #===============================================================
    # Display of the contents of this object:
    #===============================================================

    def p_oneliner(self):
        """Return a one-line summary of this object"""
        ss = 'Grunt.ParameterizationPlus:'
        ss += ' '+str(self.name)
        ss += '  ('+str(self.ns['<>'].name)+')'
        return ss


    def p_display(self, txt=None, full=False, recurse=3):
        """Print a summary of this object"""
        print ' '
        print '** '+self.p_oneliner()
        if txt: print '  * (txt='+str(txt)+')'
        #...............................................................
        print '  * TDLCompileOptionsMenu: '+str(self._TDLCompileOptionsMenu)
        for key in self._TDLCompileOption.keys():
            oo = self._TDLCompileOption[key]
            noexist = -1.23456789
            if getattr(oo, 'value', noexist)==noexist:
                print '    - '+str(key)+': '+str(self._TDLCompileOption[key])
            else:
                tdlvalue = self._TDLCompileOption[key].value
                selfvalue = getattr(self, key, noexist)
                if tdlvalue==selfvalue:
                    print '    - '+str(key)+' = '+str(tdlvalue)
                else:
                    print '    - '+str(key)+' = '+str(tdlvalue)+' != '+str(selfvalue)
        #..............................................................
        print '  * options (default, reset): '+str(self.tdloption_reset)
        if isinstance(self.tdloption_reset,dict):
            rr = dict()
            for key in self.tdloption_reset:
                value = getattr(self, key)
                if not value==self.tdloption_reset[key]:
                    rr[key] = value
            print '  * options (actual, if different from default): '+str(rr)
        #...............................................................
        if self._parmdefs:
            print '  * Meow _parmdefs ('+str(len(self._parmdefs))+') (value,tags,solvable):'
            if full:
                for key in self._parmdefs:
                    rr = list(deepcopy(self._parmdefs[key]))
                    rr[0] = str(rr[0])
                    print '    - ('+key+'): '+str(rr)
            print '  * Meow.Parm options (in _parmdefs):'
            if full:
                for key in self._parmdefs:
                    value = self._parmdefs[key][0]
                    if isinstance(value, Meow.Parm):
                        print '    - ('+key+'): (='+str(value.value)+') '+str(value.options)
            print '  * Meow _parmnodes ('+str(len(self._parmnodes))+'):'
            if full:
                for key in self._parmnodes:
                    rr = self._parmnodes[key]
                    print '    - ('+key+'): '+str(rr)
        #...............................................................
        self._pgm.display(self.oneliner(), full=full)
        #...............................................................
        print '**\n'
        return True


    #===================================================================
    # TDLOptions:
    #===================================================================

    def TDLCompileOptionsMenu (self, show=True, reset=True, solving=True):
        """Generic function for interaction with its TDLCompileOptions menu.
        The latter is created (once), by calling the specific function(s)
        .TDLCompileOptions(), which should be re-implemented by derived classes.
        The 'show' argument may be used to show or hide the menu. This can be done
        repeatedly, without duplicating the menu.
        """

        # print '\n**',self.oneliner(),self._TDLCompileOptionsMenu,'\n'
        
        # if not self._TDLCompileOptionsMenu:        # create the menu only once
        if True and not self._TDLCompileOptionsMenu:

            oolist = self.TDLCompileOptions()
            oolist.extend(self._pgm.TDLCompileOptions(reset=False,
                                                      solving=solving))
            if reset:
                key = '_reset'
                if not self._TDLCompileOption.has_key(key):
                    doc = """If True, reset all options to their original default values.
                    (presumably these are sensible values, supplied by the module designer.)
                    This is done recursively for all menus below this one."""
                    prompt = self.name+':  reset to original defaults'
                    self._TDLCompileOption[key] = TDLOption(key, prompt, [False, True],
                                                            doc=doc, namespace=self)
                    self._TDLCompileOption[key].when_changed(self._callback_reset)
                oolist.append(self._TDLCompileOption[key])

            prompt = self.namespace(prepend='options for '+self._frameclass+':  '+self.name)
            self._TDLCompileOptionsMenu = TDLCompileMenu(prompt, *oolist)

        else:
            print '\n** menu not recreated:',self.oneliner(),'\n'

        # Show/hide the menu as required (can be done repeatedly):
        self._TDLCompileOptionsMenu.show(show)
        return self._TDLCompileOptionsMenu

    #..................................................................

    def TDLCompileOptions (self):
        """Define a list of TDL options that control the structure of the
        Jones matrix.
        This function should be re-implemented by derived classes."""
        oolist = []

        # NB: Each call to TDLOption(key,...) (re)creates a local variable self.<key>,
        #     which is used internally. If the module is to be used without TDLOptions,
        #     these variables should be created by the constructor, and given the
        #     ('design') values specified by constructor arguments.
        #     These original values should also be kept in self.tdloption_reset[key],
        #     to be used for resetting the option values to a known state. In the
        #     future this original value should be held by the TDLOption object,
        #     to be used with its function .reset(). For the moment, we will do it
        #     externally, via self.tdloption_reset.

        if False:                    # temporary, just for testing and example
            key = 'xxx'
            doc = 'explanation for xxx....'
            opt = range(3)
            if not self._TDLCompileOption.has_key(key):
                self._TDLCompileOption[key] = TDLOption(key, 'prompt_xxx', opt, more=int,
                                                        doc=doc, namespace=self)
                self.tdloption_reset[key] = opt[0]           # .... temporary .....
            oolist.append(self._TDLCompileOption[key])

        # Finished: Return a list of options:
        return oolist

    #---------------------------------------------------------------------

    def _callback_reset(self, reset):
        """Function called whenever TDLOption _reset changes."""
        if reset and self._TDLCompileOptionsMenu:
            self.reset_options(trace=True)
            self._TDLCompileOption['_reset'].set_value(False, callback=False,
                                                       save=True)
        return True

    #.....................................................................

    def reset_options(self, trace=False):
        """Helper function to reset the TDLCompileOptions and their local
        counterparts to the original default values (in self.tdloption_reset). 
        """
        trace = True
        if trace:
            print '\n** _reset_options(): ',self.oneliner()
        print  '** self.tdloption_reset =',self.tdloption_reset
        for key in self.tdloption_reset.keys():
            was = getattr(self,key)
            new = self.tdloption_reset[key]
            setattr(self, key, new)
            if self._TDLCompileOption.has_key(key):
                self._TDLCompileOption[key].set_value(new, save=True)
                new = self._TDLCompileOption[key].value
                if trace:
                    print ' -',key,':',was,' -> ',getattr(self,key),
                    if not new==getattr(self,key):
                        print '** TDLOption =',new,'!?',
            else:
                if trace: print ' -',key,':',was,' -> ',getattr(self,key),
            if trace:
                if not new==was: print '           ** changed **',
                print
        if trace: print

        # Reset the pgm options also:
        if self._pgm:
            self._pgm.reset_options(trace=trace)
        return True
        


    #===============================================================
    # Some useful helper functions (available to all derived classes)
    #===============================================================

    def tags2list (self, tags):
        """Helper function to make sure that the given tags are a list"""
        if tags==None: return []
        if isinstance(tags, (list, tuple)): return list(tags)
        if isinstance(tags, str): return tags.split(' ')
        s = '** cannot convert tag(s) to list: '+str(type(tags))+' '+str(tags)
        raise TypeError, s

    def quals2list (self, quals):
        """Helper function to make sure that the given quals are a list"""
        if quals==None: return []
        if isinstance(quals, (list,tuple)): return list(quals)
        if isinstance(quals, str): return quals.split(' ')
        return [str(quals)]

    #----------------------------------------------------------------

    def get_quals (self, merge=None, remove=None):
        """Helper function to get a list of the current nodescope qualifiers"""
        quals = (self.ns.dummy).name.split(':')
        quals.remove(quals[0])
        if isinstance(merge,list):
            for q in merge:
                if not q in quals:
                    quals.append(q)
        if isinstance(remove,list):
            for q in remove:
                if q in quals:
                    quals.remove(q)
        return quals





#=============================================================================
#=============================================================================
#=============================================================================
# Test routine (with meqbrowser):
#=============================================================================


if 0:
    pp1 = ParameterizationPlus(name='GJones', quals='3c84')
    pp1._pgm.group_define('Gphase', tiling=3, mode='nosolve')
    pp1._pgm.group_define('Ggain', default=1.0, freq_deg=2)
    pp1._pgm.TDLCompileOptionsMenu()
    pp1._pgm.display('initial')



def _define_forest(ns):

    cc = []
    pp1.nodescope(ns)

    if len(cc)==0: cc.append(ns.dummy<<1.1)
    ns.result << Meq.Composer(children=cc)
    return True



#---------------------------------------------------------------

def _tdl_job_2D_tf (mqs, parent):
    """Execute the forest with a 2D request (freq,time), starting at the named node"""
    domain = meq.domain(1.0e8,1.1e8,0,2000)                            # (f1,f2,t1,t2)
    cells = meq.cells(domain, num_freq=10, num_time=100)
    request = meq.request(cells, rqtype='ev')
    result = mqs.meq('Node.Execute',record(name='result', request=request))
    return result
       










#===============================================================
# Test routine:
#===============================================================


if __name__ == '__main__':
    ns = NodeScope()

    if 1:
        pp1 = ParameterizationPlus(ns, name='GJones',
                                   # kwquals=dict(tel='WSRT', band='21cm'),
                                   quals='3c84')
        pp1._pgm.group_define('Gphase', tiling=3, mode='nosolve')
        pp1._pgm.group_define('Ggain', default=1.0, freq_deg=2)
        pp1.TDLCompileOptionsMenu()
        pp1._pgm.display('initial')

    if 1:
        e0 = Expression.Expression(ns, 'e0', '{a}+{b}*[t]-{e}**{f}+{100~10}', simul=False)
        e0.display()
        if 0:
            pp3 = ParameterizationPlus(ns, 'e0', merge=e0)
            pp3._pgm.display('after merge', full=True)
        if 1:
            pp1._pgm.merge(e0, trace=True)
            pp1._pgm.display('after merge', full=True)
            pp1.p_display(full=True)



#===============================================================

