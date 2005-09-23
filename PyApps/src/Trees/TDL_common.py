# TDL_common.py

# file: .../Timba/PyApps/src/Trees/TDL_common.py
#
# Author: J.E.Noordam
#
# Short description:
#   Contains a common superclass to be inherited by TDL objects like TDL_Cohset.py
#   Also some other functions of common usefulness... 
#
# History:
#    - 05 sep 2005: creation
#    - 10 sep 2005: more or less stable
#
# Remarks:
#


#***************************************************************************************
# Preamble
#***************************************************************************************

from Timba.TDL import *
from copy import deepcopy

from Timba import utils
_dbg = utils.verbosity(0, name='tutorial')
_dprint = _dbg.dprint                    # use: _dprint(2, "abc")
_dprintf = _dbg.dprintf                  # use: _dprintf(2, "a = %d", a)
# run the script with: -dtutorial=3
# level 0 is always printed



#***************************************************************************************
# Super class with common inheritable funtions (also used by Cohset)
#***************************************************************************************

class Super:
    """Common services for TDL objects like TDL_Cohset, TDL_Joneset, TDL_Sixpack"""

    def __init__(self, **pp):

        pp.setdefault('label', '<object label>')
        pp.setdefault('type', '<object type>')
        pp.setdefault('origin', '<origin>')

        self.__label = pp['label']
        self.__type = pp['type']
        self.__origin = pp['origin']
        pp.__delitem__('label')
        pp.__delitem__('type')
        pp.__delitem__('origin')

        # self.clear()
        self.__errors = 0
        self.__warnings = 0

        # Start the object history:
        s = str(self.__origin)+': Created '+str(self.type())+' object with label: '+str(self.label())
        self.history(s, reset=True)

        # Deal with the extra constructor arguments (if any):
        self.history('inarg = '+str(pp))
        s = s+' inarg = '+str(pp)
        # print '\n**',s,'\n'

        return None

    def __del__(self):
        # print '** Goodbye',self.type().self.name()
        pass

    def label(self, new=None):
        if isinstance(new, str): self.__label = new
        return self.__label
    def type(self): return self.__type
    def errors(self): return self.__errors
    def warnings(self): return self.__warnings
    def ok(self): return (self.__errors==0 and self.__warnings==0)

    def __str__(self):
        return self.oneliner()

    def oneliner(self):
        s = '*'
        s += ' '+str(self.type())+':'
        s += ' '+str(self.label())
        if self.ok():
            s += ' (ok)'
        else:
            s += ' ** NOT OK!! **'
            s += ', errors='+str(self.errors())
            s += ', warnings='+str(self.warnings())
        return s

    def display(self, txt=None, end=True):
        indent1 = 2*' '
        indent2 = 6*' '
        ss = []
        ss.append('\n** '+self.type()+'.display('+str(txt)+'):')
        ss.append(indent1+self.oneliner())
        ss.append(indent1+'* .ok() -> '+str(self.ok())+': .errors() -> '+str(self.errors())+' .warnings() -> '+str(self.warnings()))
        hh = self.history()
        ss.append(indent1+'* Object history ('+str(len(hh))+' entries):')
        for i in range(len(hh)):
                  ss.append(indent2+'* '+str(i)+': '+hh[i])
        # ss.append(indent1+'*')
        if end: ss = self.display_end(ss)
        return ss

    def display_end(self, ss=[]):
        ss.append('** end of '+self.type()+'.display()\n')
        for s in ss: print s
        return ss


    def copy(self, label=None):
        # Return a (re-labelled) 'deep' copy of this jonesset: 
        new = deepcopy(self)                                    # copy() is not enough...
        if label==None: label = '('+self.label()+')'               # Enclose old label in ()
        new.label(label)                                          # re-label (always)
        self.history(append='copied to '+self.type()+': '+new.label())
        new.history(append='copied from '+self.type()+': '+self.label()+' -> '+new.label(),
                    reset=False, indent=True)
        return new

    # Simple mechanisms for storing the object history, including errors/warnings:

    def history(self, append=None, error=None, warning=None, reset=False, indent=False):
        if reset: self.__history = []
        if indent:
            for i in range(len(self.__history)):
                self.__history[i] = '...'+self.__history[i]      # indent the old stuff
        if not append==None:
            self.__history.append(str(append))
        if not error==None:
            self.__errors += 1
            self.__history.append('** ERROR ** '+str(error))
        if not warning==None:
            self.__warnings += 1
            self.__history.append('** WARNING ** '+str(warning))
        return self.__history


    # Some ideas for functions to be added:

    def save(self, filename=None):
        # Save the object in a file... Not very useful?
        pass

    def clear(self):
        # Called from self.__init__() above. Expected to be overwritten.
        pass


#========================================================================
# Helper routines:
#========================================================================

# Counter service (use to automatically generate unique node names)

_counters = {}

def _counter (key, increment=0, reset=False, trace=True):
    global _counters
    _counters.setdefault(key, 0)
    if reset: _counters[key] = 0
    _counters[key] += increment
    if trace: print '** Super: _counters(',key,') =',_counters[key]
    return _counters[key]


#----------------------------------------------------------------
# Some 'universal' plot styles:

def plot_color(key=None):
    rr = dict(XX='red', XY='magenta', YX='darkCyan', YY='blue')
    rr['RR'] = rr['XX']
    rr['RL'] = rr['XY']
    rr['LR'] = rr['YX']
    rr['LL'] = rr['YY']
    if key==None: return rr
    if rr.has_key(key): return rr[key]
    return False
    
def plot_style(key=None):
    rr = dict(XX='circle', XY='xcross', YX='xcross', YY='circle')
    rr['RR'] = rr['XX']
    rr['RL'] = rr['XY']
    rr['LR'] = rr['YX']
    rr['LL'] = rr['YY']
    if key==None: return rr
    if rr.has_key(key): return rr[key]
    return False

def plot_size(key=None):
    rr = dict(XX=10, XY=7, YX=7, YY=10)
    rr['RR'] = rr['XX']
    rr['RL'] = rr['XY']
    rr['LR'] = rr['YX']
    rr['LL'] = rr['YY']
    if key==None: return rr
    if rr.has_key(key): return rr[key]
    return False


# Plot style information
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



#========================================================================
# Test routine:
#========================================================================

if __name__ == '__main__':
    from numarray import *
    from Timba.Contrib.JEN import MG_JEN_exec
    ns = NodeScope()
    nsim = ns.Subscope('_')
    
    sup = Super(label='initial', type='Super', origin='TDL_common')
    sup.display('initially')

    if 0:
        print '** dir(sup) ->',dir(sup)
        print '** sup.__doc__ ->',sup.__doc__
        print '** sup.__module__ ->',sup.__module__
        print

    if 0:
        # Inherited functions (from Super):
        print '** sup.history() ->',sup.history()
        sup1 = sup.copy()
        sup1.display('copied')


    if 0:
        # Display the final result:
        # k = 0 ; MG_JEN_exec.display_subtree(sup[k], 'sup['+str(k)+']', full=True, recurse=3)
        sup.display('final result')


#============================================================================================









 

