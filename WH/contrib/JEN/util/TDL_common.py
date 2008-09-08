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
#    - 25 feb 2006: added unclutter_inarg()  (used by other functions too)
#    - 06 mar 2006: added automatic error/warning printing to .history()
#    - 06 mar 2006: .history() will return False if error/warning
#    - 07 mar 2006: added ._fieldict()
#    - 07 mar 2006: .history() -> ._history() (upward compatible)
#    - 08 mar 2006: copied TDL_Cohset .rider() to ._rider()
#    - 08 mar 2006: implemented ._save() and ._restore()
#    - 08 mar 2006: implemented ._clear() and ._history()
#    - 09 mar 2006: added format_initrec(node)
#    - 11 mar 2006: added ._listuple()
#    - 12 mar 2006: added ._updict() and ._updict_rider()
#
# Remarks:
#


#***************************************************************************************
# Preamble
#***************************************************************************************

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

        ## self.clear()
        self.__errors = 0
        self.__warnings = 0

        # Initialise the rider record (see ._rider())
        self.__rider = dict()

        # Start the object history (see ._history()):
        s = str(self.__origin)+': Created '+str(self.type())+' object with label: '+str(self.label())
        self.history(s, reset=True)
        self.history('inarg = '+str(unclutter_inarg(pp)))

        # Finished: The __init__ function MUST return None
        return None

    def __del__(self):
        """Destructor"""
        pass

    def clear(self):
        """Expected to be overwritten."""
        return True

    def _clear(self):
        """May be used in a (redefined) .clear() function"""
        self._history(reset=True)
        self._rider(clear=True)
        return True

    def label(self, new=None):
        """Get/set the obect label"""
        if isinstance(new, str): self.__label = new
        return self.__label
    def type(self):
        """Return the obect type"""
        return self.__type
    def tlabel(self):
        """Return a simple identified string"""
        return self.__type+':'+self.__label
    def errors(self):
        """Return the nr of accumulated errors (if any)"""
        return self.__errors
    def warnings(self):
        """Return the nr of accumulated warnings (if any)"""
        return self.__warnings
    def ok(self):
        """Test whether the object is OK (no errors or warnings)"""
        return (self.__errors==0 and self.__warnings==0)

    def __str__(self):
        return self.oneliner()

    def oneliner(self):
        """Generic part of a one-line summary of this object"""
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

    def display_indent1(self):
        """Standard indentation, used in .display()"""
        return 2*' '
    def display_indent2(self):
        """Standard indentation, used in .display()"""
        return 6*' '


    def display(self, txt=None, end=True, full=False):
        """Generic part of displaying the contents of this object in an organised way.
        The specific part is added in the object itself"""
        indent1 = self.display_indent1()
        indent2 = self.display_indent2()
        ss = []
        if txt==None: txt = self.label() 
        ss.append('** '+self.type()+'.display('+str(txt)+'):')
        ss.append(indent1+self.oneliner())

        #-----------------------------------
        s1 = '* .ok() -> '+str(self.ok())
        s1 += ': .errors() -> '+str(self.errors())
        s1 += ' .warnings() -> '+str(self.warnings())
        ss.append(indent1+s1)

        #-----------------------------------
        rr = self._rider()
        if not full:
            ss.append(indent1+'* Object rider ('+str(len(rr))+' entries): (not shown)')
            ss.append(indent2+'- rider field-names: '+str(rr.keys()))
        else:
            ss.append(indent1+'* Object rider ('+str(len(rr))+' entries):')
            for key in rr.keys():
                # ss.append(indent2+'* '+str(key)+': '+str(type(rr[key])))
                qq = unclutter(rr[key])
                ss.append(indent2+'* '+str(key)+': '+str(type(rr[key]))+' = '+str(qq))

        #-----------------------------------
        hh = self._history()
        if not full:
            ss.append(indent1+'* Object history ('+str(len(hh))+' entries): (not shown)')
        else:
            ss.append(indent1+'* Object history ('+str(len(hh))+' entries):')
            for i in range(len(hh)):
                ss.append(indent2+'* '+str(i)+': '+hh[i])

        #-----------------------------------
        ss.append(indent1+' * ============')
        if end: ss = self.display_end(ss)
        return ss

    def display_insert_object (self, ss, object=None, full=False):
        """Insert the .display() of another object"""
        indent1 = self.display_indent1()
        nn = object.display(full=full, doprint=False, pad=False)
        for s in nn:
            ss.append('.'+indent1+s)
        return ss

    def display_end(self, ss=[], pad=True, doprint=True):
        """Called at the end of a .display() function"""
        if pad: ss[0] = '\n'+ss[0]
        ss.append('** end of '+self.type()+'.display()')
        if pad: ss.append('\n')
        if doprint:
            for s in ss: print s
        return ss


    def copy(self, label=None):
        """Return a (re-labelled) 'deep' copy of this object""" 
        new = deepcopy(self)                                       # copy() is not enough...
        if label==None: label = '('+self.label()+')'               # Enclose old label in ()
        new.label(label)                                           # re-label (always)
        self.history(append='copied to '+self.type()+': '+new.label())
        new.history(append='copied from '+self.type()+': '+self.label()+' -> '+new.label(),
                    reset=False, indent=True)
        return new


    #---------------------------------------------------------------------------------
    # Interaction with the object history (also contains errors/warnings)
    #---------------------------------------------------------------------------------

    def history(self, append=None, error=None, warning=None, reset=False,
                indent=False, trace=False):
        """Obsolete version of self._history()"""
        return self._history(append=append, error=error, warning=warning,
                             reset=reset, indent=indent, trace=trace)

    def _history(self, append=None, error=None, warning=None, reset=False,
                indent=False, trace=False):
        """Simple mechanisms for storing the object history, including errors/warnings"""
        if reset: self.__history = []
        if indent:
            for i in range(len(self.__history)):
                self.__history[i] = '...'+self.__history[i]      # indent the old stuff
        if not append==None:
            s1 = str(append)
            self.__history.append(s1)
            if trace: print s1
        ok = True
        if not error==None:
            self.__errors += 1
            s1 = '** ERROR ** '+str(error)
            self.__history.append(s1)
            print '\n',self.tlabel(),':',s1,'\n'
            ok = False
        if not warning==None:
            self.__warnings += 1
            s1 = '** WARNING ** '+str(warning)
            self.__history.append(s1)
            print '\n',self.tlabel(),':',s1,'\n'
            ok = False
        if not ok:               # 
            return False         # this allows False return of the calling function 
        return self.__history    # return the entire history....



    #-----------------------------------------------------------------------------------
    # An object may carry arbitrary information in its 'rider' record 
    #-----------------------------------------------------------------------------------

    def _rider(self, key=None, append=None, clear=False, report=False):
        """Interaction with rider info (lists) of various named (key) categories"""
        if not isinstance(key, str):                  # no key specified
            if clear: self.__rider = {}               # clear the entire rider dict
            return self.__rider                       # return the entire rider dict

        # A append item has been specified:
        if append:                                    # append item(s) to the specified rider
            if clear:
                self.__rider[key] = []                # clear the rider BEFORE appending item(s)
                clear = False                         # do not clear afterwards, of course
            self.__rider.setdefault(key,[])           # create the rider (key) if necessary
            if isinstance(append, (tuple, list)):     # assume list of items
                self.__rider[key].extend(append)
            else:                                     # assume single item
                self.__rider[key].append(append)

        # Prepare the return value:
        if self.__rider.has_key(key):
            cc = self.__rider[key]                    # copy the existing rider BEFORE clearing
            if clear: self.__rider[key] = []          # clear the rider, if required
            return cc                                 # Return a list (as it was before clearing)

        # Not found, but always return a list:
        if report: print '\n** _rider(',key,'): not recognised in:',self.__rider.keys()
        return []



    #---------------------------------------------------------------------------------
    # Miscelleneous helper functions (rather useful):
    #---------------------------------------------------------------------------------

    def _format_rider_summary (self, rr, name=None):
        """Format a summary of the given rider record rr"""
        if not isinstance(rr, dict):
            return 'rider='+str(type(rr)) 
        elif len(rr)==0:
            return ''
        elif len(rr)<3:
            qq = unclutter_inarg(rr)
            return ',  rider = '+str(qq)
        return ',  rider length = '+str(len(rr))


    def _dictitem(self, rr=None, item=None, key=None, name=None, default=None, trace=False):
        """Get the specified item (e.g. color) from the specified dicts (key, None=all)
        in the given dict (rr). If rr==None, the object's own 'rider' dict is assumed."""
        if rr==None: rr = self._rider()
        s1 = '._dictitem('+str(type(rr))+', '+str(item)+', '+str(key)+')'
        if trace: print '\n**',s1,
        if not isinstance(rr, dict): return default
        if not isinstance(item, str): return default
        cc = dict()
        for rkey in rr.keys():
            if rr[rkey].has_key(item):
                cc[rkey] = rr[rkey][item]
        if trace: print '-> cc =',cc,
        result = self._fieldict (cc, key=key, name=s1, default=default)
        if trace: print '->',result
        return result


    def _listuple (self, value=None,
                   vtype=None, trace=False):
        """Make sure that the given value is a list or a tuple"""
        tval = type(value)
        if not isinstance(value, (list, tuple)):
            if vtype==None or isinstance(value, vtype):
                value = [value]
            else:
                return self.history(error=str(value)+' has wrong type: '+str(type(value))+' != '+str(vtype))
        if trace: print '**',self.tlabel(),'._listuple(',tval,type,') ->',len(value),value
        return value                                # return list/tuple


    def _fieldict (self, rr=dict(), key=None, default=None,
                   clear=False, name='<name>', trace=False):
        """Return the specified field (key) from the given dict (rr).
        If clear==True, clear the field (key) of the entire dict (key==None)."""
        if key==None:                               # no field specified
            if clear: rr = dict()                   #   clear the entire dict
            return rr                               #   return the entire dict
        elif not isinstance(rr, dict):
            return self.history(error=str(name)+': rr not a dict, but: '+str(type(rr)))
        else:
            if not isinstance(key, (list, tuple)): key = [key]
            cc = dict()                             # initialise the result
            for k in key:
                if not isinstance(k, str): 
                    self.history(error=str(name)+': key type is:'+str(type(k)))
                    cc[k] = default                 # ....?
                elif not rr.has_key(k):             # field (k) not recognised....
                    self.history(error=str(name)+': key not recognised: '+k)
                    cc[k] = default                 # ....?
                else:                               # rr has the specified field (k)
                    if clear:
                        if isinstance(rr[k], dict):
                            rr[k] = dict()          # empty dict
                        elif isinstance(rr[k], (list, tuple)):
                            rr[k] = []              # empty list
                    cc[k] = rr[k]                   # collected output
            if len(key)==1: return cc[key[0]]       # only one key asked: return the value
            return cc                               # multiple keys asked: return a dict
        # Problem: return the default value:
        return default


    def _updict_rider (self, rider=dict(), trace=False):
        """Updict its own rider record with another"""
        return self._updict (self.__rider, other=rider, name='_rider', trace=trace)


    def _updict (self, rr=dict(), other=dict(), name=None, level=1, trace=False):
        """Version of rr.update (other -> rr) that is really a merge.
        The difference lies in the treatment of existing lists and dicts.
        Procedure: Go through the fields (key) of the contributing dict (other):
        - If rr[key] does not exist, just copy other[key] (like rr.update(other).
        - If rr[key] is a list/tuple (this is the most useful case):
          - extend rr[key] with the items of other[key], avoiding doubles.
        - If rr[key] is a dict:
          - if other[key] is also a dict: recurse: self._updict(rr[key],other[key')
          - otherwise, rr[key]['_updict_'] = other[key]  
        - otherwise: overwrite rr[key] with other[key] (like rr.update(other))"""
        if not isinstance(rr, dict): return False
        if not isinstance(other, dict): return False
        prefix = (level*'..')+'._updict('+str(name)+'): '
        for key in other.keys():                       # for all keys of 'other'
            if not rr.has_key(key):                    # rr[key] does not exist
                rr[key] = other[key]                   #   create it
                self._history(prefix+str(key)+': copied: '+str(type(rr[key])))
            elif isinstance(rr[key], (list,tuple)):    # rr[key] is a list
                qq = other[key]                        #   append other[key], avoiding doubles
                if not isinstance(qq, (list,tuple)): qq = [qq]
                aa = []
                for item in qq:
                    if not item in rr[key]:
                        aa.append(item)
                        rr[key].append(item)
                self._history(prefix+str(key)+': extended list with ('+str(len(aa))+'): '+str(aa))
            elif isinstance(rr[key], dict):            # rr[key] is dict
                if isinstance(other[key], dict):       #   other[key] is also a dict
                    self._updict (rr[key], other[key], name=name, level=level+1)     # recursive 
                else:                                  #   other[key] is not a dict
                    rr[key]['_updict_'] = other[key]   #     attach to rr[key] as a special field.... 
                    self._history(prefix+str(key)+': attached [_updict_]:',str(type(other[key])))
            else:                                      # rr[key] is something else
                rr[key] = other[key]                   #   overwrite it.........??
        return True


    #---------------------------------------------------------------------------------
    # Saving/restoring (nodestubs require special care) 
    #---------------------------------------------------------------------------------

    def _save(self, filename=None):
        """Save the object in a file... Not very useful?
        (Not implemented yet)"""
        return True

    def _restore(self, filename=None):
        """Save the object in a file... Not very useful?
        (Not implemented yet)"""
        return True



    #---------------------------------------------------------------------------------
    # Some ideas for functions to be added:



#========================================================================
# Helper routines:
#========================================================================


_counters = {}

def _counter (key, increment=0, reset=False, trace=True):
    """Counter service (use to automatically generate unique node names)"""
    global _counters
    _counters.setdefault(key, 0)
    if reset: _counters[key] = 0
    _counters[key] += increment
    if trace: print '** Super: _counters(',key,') =',_counters[key]
    return _counters[key]


#--------------------------------------------------------------------------

def unclutter(pp):
    """Strip the given input argument record/list (pp) to avoid clutter (e.g. when printing it)"""
    return unclutter_inarg(pp)


def unclutter_inarg(pp):
    """Strip the given input argument record/list (pp) to avoid clutter (e.g. when printing it)"""
    # Dont use deepcopy because it cannot handle nodestubs 
    ## qq = deepcopy(pp)

    if isinstance(pp, (list, tuple)):
        qq = replace_nodestubs(pp)
                
    elif isinstance(pp, dict):
        qq = {}                                               # strip a copy
        for key in pp.keys():
            v = pp[key]
            if isinstance(v, Timba.TDL.TDLimpl._NodeStub):    # avoid clutter
                qq[key] = key+': <nodestub>'+str(v.name)
            elif isinstance(v, dict):                         # avoid clutter
                if key=='_JEN_inarg_CTRL_record:':
                    pass
                else:
                    qq[key] = str(type(v))+'['+str(len(v))+']'
            elif isinstance(v, (list,tuple)):                 # avoid clutter
                v = replace_nodestubs(v)
                qq[key] = str(type(v))+'['+str(len(v))+'] = '
                nmax = 3
                if len(v)>nmax:
                    qq[key] += str(v[:nmax])+'...'
                else:
                    qq[key] += str(v)
            else:
                qq[key] = v

    elif isinstance(pp, Timba.TDL.TDLimpl._NodeStub):         # avoid clutter
        qq = '<nodestub>'+str(pp.name)
    else:                                                     # any other type
        # Error message?
        qq = False
    return qq


#---------------------------------------------------------------------------

def is_nodestub(node):
    """Test whether a node is a nodestub (type)"""
    return isinstance(node, Timba.TDL.TDLimpl._NodeStub)

def replace_nodestubs(vv):
    """Replace any nodestub(s) in vv with something more readable"""
    if not isinstance(vv, (list,tuple)): return vv
    ww = []
    for v in vv:
        if isinstance(v, Timba.TDL.TDLimpl._NodeStub):
            ww.append('<nodestub>'+str(v.name))
        else:
            ww.append(v)
    return ww
        

def is_nodescope(ns):
    """Test whether ns is a nodsecope (type)"""
    return isinstance(ns, Timba.TDL.TDLimpl._NodeScope)

#--------------------------------------------------------------------------

def encode_nodestubs(rr=None):
    """encode the nodestubs in the given dict (needed for saving)"""
    if not isinstance(rr, dict): return rr
    dictout = dict()
    for key in rr.keys():
        if isinstance(rr[key], Timba.TDL.TDLimpl._NodeStub):
            dictout[key] = {'__type__':'nodestub','name':rr[key].name}
        else:
            dictout[key] = rr[key]
    return dictout


def decode_nodestubs(ns, rr=None):
    """convert an dict (rr) of encoded nodestubs (rr) back to nodestubs
    in named fields of a new dict (dictout). NB: It is assumed that the
    nodes already exist in the given nodescope (ns)"""
    if not isinstance(rr, dict): return rr
    dictout = dict()
    for key in rr.keys():
        if isinstance(rr[key], dict):
            cc = rr[key]
            if cc.has_key('__type__') and cc['__type__']=='nodestub':
                # split off the name qualifiers (if any):
                ss = string.split(cc['name'],':')    # split on qualifier colons
                nodestub = None
                if len(ss)==1:                       # no qualifiers
                    nodestub = ns[ss[0]]
                else:                                
                    seval = 'nodestub=ns[\''+ss[0]+'\']'
                    for i in range(1,len(ss)):
                        seval += '(\''+ss[i]+'\')'   # repaste the qualifier
                    # print 'seval =',seval
                    exec seval
                dictout[cc['name']] = nodestub
    return dictout

#-------------------------------------------------------------------------------

def format_initrec (node=None, trace=False):
    """Format the init record of the given node"""
    if not isinstance(node, Timba.TDL.TDLimpl._NodeStub):
        return 'node='+str(type(node))
    initrec = deepcopy(node.initrec())               # just in case....
    if len(initrec.keys()) > 1:
        hide = ['name','class','defined_at','children','stepchildren','step_children']
        for field in hide:
            if initrec.has_key(field):
                initrec.__delitem__(field)
            if initrec.has_key('default_funklet'):
                coeff = initrec.default_funklet.coeff
                initrec.default_funklet.coeff = [coeff.shape,coeff.flat]
    if trace: print '  ',initrec
    return str(initrec)


#---------------------------------------------------------------------------------

def common_quals(cc=[], trace=False):
    """Find the common qualifiers if the given list of nodes"""
    funcname = 'TDL_common.common_quals():'
    if trace: print '\n**',funcname
    if not isinstance(cc, (list, tuple)): cc = [cc]
    if len(cc)==0: return dict()
    if len(cc)==1: return cc[0].kwquals
    quals = cc[0].kwquals
    count = dict()
    for key in quals.keys():
        count[key] = 1
    for node in cc[1:]: 
        if trace: print '-',node.quals,':',node.kwquals
        kwquals = node.kwquals
        for key in quals.keys():
            if kwquals.has_key(key):
                if kwquals[key]==quals[key]:
                    count[key] += 1
    cq = dict()
    for key in quals.keys():
        if count[key]>1:
            cq[key] = quals[key]
    if trace: print '->',cq,'\n'
    return cq




#========================================================================
# Test routine:
#========================================================================

if __name__ == '__main__':
    from numpy import *
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
        node = ns << 0
        print node
        print 'type(node) =',type(node)
        print 'type(type(node)) =',type(type(node))
        print type(node)==Timba.TDL.TDLimpl._NodeStub
        print isinstance(node, Timba.TDL.TDLimpl._NodeStub)

        print 'type(ns) =',type(ns)
        print type(ns)==Timba.TDL.TDLimpl.NodeScope
        print isinstance(ns, Timba.TDL.TDLimpl.NodeScope)

    if 0:
        name = 'mean(stripper(visu)):-2:XX:s1=0:s2=1'
        node = ns['mean(stripper(visu))'](-2)('XX')(s1=0)(s2=1) << Meq.Constant(-1)
        rr = encode_nodestubs(dict(node=node))
        print rr
        xx = decode_nodestubs(ns,rr)
        print xx

    if 1:
        r = sup._listuple('string', trace=True); print r
        r = sup._listuple(dict(a='dict'), trace=True); print r
        r = sup._listuple(['list'], trace=True); print r
        r = sup._listuple(10.0, trace=True); print r
        r = sup._listuple(('tuple',), trace=True); print r
        r = sup._listuple('string', vtype=type(''), trace=True); print r
        r = sup._listuple(10, vtype=type(''), trace=True); print r
        if not r: print '...'
        print
      
    if 0:
        # Display the final result:
        # k = 0 ; MG_JEN_exec.display_subtree(sup[k], 'sup['+str(k)+']', full=True, recurse=3)
        sup.display('final result')


#============================================================================================









 

