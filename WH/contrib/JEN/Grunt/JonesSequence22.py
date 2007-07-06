# file: ../Grunt/JonesSequence22.py

# History:
# - 30jun2007: creation (from Joneset22.py)

# Description:

# The JonesSequence22 class is derived from the class Joneset22
# It encapsulates a sequence (matrix product) of 2x2 Jones matrices.

#======================================================================================

from Timba.TDL import *
from Timba.Meq import meq

import Meow

from Timba.Contrib.JEN.Grunt import Joneset22

from copy import deepcopy

#======================================================================================

class JonesSequence22 (Joneset22.Joneset22):
    """A JonesSequence22 that is a station-by-station matrix multiplication of
    one or more Joneset22 matrices (or other matrices that obey the Jones contract)."""

    def __init__(self, ns=None, name='',
                 quals=[], kwquals={},
                 descr='Sequence (product) of Jones matrices',
                 simulate=False):

        # If simulate, use subtrees that simulate MeqParm behaviour:
        self._simulate = simulate

        # Initialise its Matrixet22 object:
        Joneset22.Joneset22.__init__(self, ns=ns, name=name)

        # The constituent Jones matrices are kept in a dict.
        # These may be objects that obeys the Jones contract.
        self._jones = dict()
        self._joneseq = []
        self._jseq_options = [None]
        self._locked = False

        # Finished:
        return None

    #-------------------------------------------------------------------

    def display_specific(self, full=False):
        """Print the specific part of the summary of this object"""
        print '   - stations ('+str(len(self.stations()))+'): '+str(self.stations())
        print '   - locked: '+str(self._locked)
        print '   - constituent jones objects:'
        for key in self._jones.keys():
            jones = self._jones[key]
            print '     - '+str(key)+':  '+str(jones.oneliner())
        print '   - jseq_options: '+str(self._jseq_options)
        print '   - selected joneseq: '+str(self._joneseq)
        print '   - TDLCompileOptionsMenu: '+str(self._TDLCompileOptionsMenu)
        print '   - TDLOption(s):'
        for key in self._TDLOption.keys():
            oo = self._TDLOption[key]
            if getattr(oo, 'value', None):
                print '     - '+str(key)+' = '+str(self._TDLOption[key].value)
            else:
                print '     - '+str(key)+': '+str(self._TDLOption[key])
        return True

    #------------------------------------------------------------------------
    # Add a new Jones matrix (object):
    #------------------------------------------------------------------------

    def add_jones (self, jones, jchar=None):
        """Add a Jones matrix to the internal record.
        Do some checks, and condition it."""
        if self._locked:
            raise ValueError,'** JonesSequence22 is locked'
        if jchar==None:
            jchar = jones.name[0]                       # e.g. 'G'
        if jchar in self._jones.keys():
            raise ValueError,'** Duplicate Jones matrix in sequence'

        if len(self._jones)==0:
            # Initialise the underlying Joneset22 object with the
            # essential information of the FIRST jones matrix
            Joneset22.Joneset22.__init__(self, ns=self.ns, name=self.name,                 
                                         namespace=self.namespace(),
                                         descr=self.descr(), 
                                         stations=jones.stations(),
                                         polrep=jones.polrep())

        elif not self.compatible(jones, severe=True):
            # Check whether subsequent jones matrices are compatible
            raise ValueError,'jonesets not compatible'

        # OK, accept and update: 
        self._jones[jchar] = jones
        self._jseq_options.append(jchar)
        jjchar = ''
        for jchar in self._jones.keys():
            jjchar += jchar
        self.name = 'jseq_'+jjchar              
        if len(self._jones.keys())>1:
            self._jseq_options.append(jjchar)
        self._descr = self.descr() + '\n  - '+str(jones.descr())
        self.history(subappend=jones.history())
        return True


    #-------------------------------------------------------------------
    # TDLOptions
    #-------------------------------------------------------------------

    def TDLCompileOptionsMenu (self, name='corrupting', show=True):
        """Re-implementation of the Joneset22 function for interaction
        with its TDLCompileOptions menu.
        The 'show' argument may be used to show or hide the menu.
        This can be done repeatedly, without duplicating the menu.
        """
        if not self._TDLCompileOptionsMenu:            # create menu only once
            prompt = 'Selected Jones matrix sequence'
            oo = TDLCompileOption('jseq', prompt, 
                                  self._jseq_options, more=str,
                                  namespace=self);
            self._TDLOption['jseq'] = oo
            self._TDLOption['jseq'].when_changed(self._callback_jseq)
            oolist = [oo]

            for jchar in self._jones.keys():
                jones = self._jones[jchar]
                oo = jones.TDLCompileOptionsMenu(name='')
                self._TDLOption[jchar] = oo
                oolist.append(oo)

            prompt = 'options for '
            if name:
                prompt += '('+str(name)+') '
            prompt += self.name
            if self.tdloption_namespace:
                prompt += ' ('+str(self.tdloption_namespace)+')'
            self._TDLCompileOptionsMenu = TDLCompileMenu(prompt, *oolist)

        # Show/hide the menu as required (can be done repeatedly):
        self._TDLCompileOptionsMenu.show(show)
        return self._TDLCompileOptionsMenu

    #..................................................................

    def _callback_jseq (self, jseq):
        """Callback function used whenever jseq is changed by the user"""
        if jseq==None: jseq = ''
        if not isinstance(jseq, str):
            jseq = self._TDLOption['jseq'].value
        self._joneseq = []
        for jchar in self._jones.keys():
            if jchar in jseq:
                self._joneseq.append(jchar)      # list of selected jones matrices
            for key in [jchar, 'solve_'+jchar]:
                if self._TDLOption.has_key(key):
                    self._TDLOption[key].show(jchar in jseq)
        self.TDL_tobesolved (trace=True)         # ....temporary....?
        return True


    #-------------------------------------------------------------------

    def TDLSolveOptionsMenu (self, name=None, show=True):
        """Re-implementation of the Joneset22 function for interaction
        with its TDLSolveOptions menu.
        The 'show' argument may be used to show or hide the menu.
        This can be done repeatedly, without duplicating the menu.
        """
        if not self._TDLSolveOptionsMenu:            # create menu only once
            oolist = []
            for jchar in self._jones.keys():
                jones = self._jones[jchar]
                oo = jones.TDLSolveOption()
                key = 'solve_'+jchar
                self._TDLOption[key] = oo
                self._TDLOption[key].when_changed(self._callback_tobesolved)
                oolist.append(oo)

            prompt = 'solve for '
            if name:
                prompt += '('+str(name)+') '
            prompt += self.name
            if self.tdloption_namespace:
                prompt += ' ('+str(self.tdloption_namespace)+')'
            self._TDLSolveOptionsMenu = TDLCompileMenu(prompt, *oolist)
            self._callback_jseq(0)

        # Show/hide the menu as required (can be done repeatedly):
        self._TDLSolveOptionsMenu.show(show)
        return self._TDLSolveOptionsMenu

    #..................................................................

    def _callback_tobesolved (self, dummy):
        """Callback function for whenever a parmgroup selection is changed"""
        # print '\n** dummy =',dummy
        self.TDL_tobesolved (trace=True)
        

    def TDL_tobesolved (self, trace=False):
        """Get a list of the selected parmgroups (or tags?) of MeqParms
        that have been selected for solving."""
        jseq = self._TDLOption['jseq'].value
        if jseq==None: return []
        if not isinstance(jseq, str): return []
        slist = []
        for jchar in self._jones.keys():
            if trace: print ' - jchar:',jchar,
            if jchar in jseq:
                key = 'solve_'+jchar
                if self._TDLOption.has_key(key):
                    ss = self._TDLOption[key].value
                    if trace: print ': ss =',ss,'->',
                    if isinstance(ss, str):
                        slist.append(ss)
                    elif isinstance(ss, (list,tuple)):
                        slist.extend(ss)
            if trace: print '  slist =',slist
        if trace: print '** TDL_tobesolved(): jseq =',jseq,'->',slist
        return slist



    #------------------------------------------------------------------------
    # The Jones contract (called by Joneset22.__call__())
    #------------------------------------------------------------------------

    def make_jones_matrix (self, station):
        """Make the Jones matrix for the specified station, by multiplying
        the corresponding matrices from the selected jonesets"""
        self._locked = True              # lock the object from here onwards...
        jj = self._joneseq               # list of selected jones matrices
        # jj = self._jones.keys()          # ....temporary.....
        if len(jj)==0:
            raise ValueError, '** joneseq is empty'

        # If only one Jones matrix, multiplication is not necessary:
        if len(jj)==1:
            jones = self._jones[jj[0]]
            jones.nodescope(self.ns)                        # ....!
            snode = jones(station)
            self._matrixet = jones._matrixet 
            self.p_merge(jones)                             # parmgroups
            return snode

        # Multiply two or more Jones matrices:
        qnode = self.ns[self.name]                   
        if not qnode.must_define_here(self):
            s = '** '+str(self.name)+': nodename clash: '+str(qnode)
            raise ValueError, s
        cc = []
        for j in jj:
            jones = self._jones[j]
            jones.nodescope(self.ns)                        # ....!
            cc.append(jones(station))
            self.p_merge(jones)                             # parmgroups
        qnode(station) << Meq.MatrixMultiply(*cc)
        self._matrixet = qnode
        return qnode(station)













#=================================================================================================
# Make a Joneset22 object that is a sequence (matrix multiplication) of Jones matrices
# Obsolete....
#=================================================================================================

def Joneseq22_obsolete (ns, joneslist=None, quals=None):
    """Return a Jones22 object that contains an (item-by-item) matrix multiplication
    of the matrices of the list (joneslist) of two or more Joneset22 objects."""


    if len(joneslist)==0:
        raise ValueError, 'joneslist should have at least one item'
    
    elif len(joneslist)==1:
        jnew = joneslist[0]
        return jnew
    
    # First create a new Jonset22 object with name/quals/descr that are
    # suitable combinations of those of the contributing Joneset22 objects: 
    first = joneslist[0]
    name = first.name[0]
    descr = first.name+': '+first.descr()
    stations = first.stations()
    qq = first.p_get_quals(remove=[first.name])
    for jones in joneslist[1:]:
        name += jones.name[0]
        descr += '\n '+jones.name+': '+jones.descr()
        qq = jones.p_get_quals(merge=qq, remove=[jones.name])
    qq.extend(first.p_quals2list(quals))
    jnew = Joneset22(ns, name=name+'Jones',
                     polrep=first.polrep(),
                     quals=qq, stations=stations) 

    # Then create the new Jones matrices by matrix-multiplication:
    jnew.history('.Joneseq22(): Matrix multiplication of '+str(len(joneslist))+' Jones matrices')
    qnode = jnew.ns.Joneseq
    for i in jnew.list_indices():
        cc = []
        for jones in joneslist:
            cc.append(jones._matrixet(*i))
        qnode(*i) << Meq.MatrixMultiply(*cc)
    jnew.matrixet(new=qnode)
    
    # Merge the parmgroups of the various Jones matrices:
    for jones in joneslist:
        jnew.p_merge(jones)
        jnew.history(subappend=jones.history())

    # Return the new Joneset22 object:
    return jnew








     
#===============================================================
# Test routine (with meqbrowser):
#===============================================================

if 1:
    simulate = False
    jseq = JonesSequence22()
    GJones = Joneset22.GJones(simulate=simulate)
    BJones = Joneset22.BJones(simulate=simulate)
    FJones = Joneset22.FJones(simulate=simulate)
    JJones = Joneset22.JJones(simulate=simulate)
    jseq.add_jones(GJones)
    jseq.add_jones(BJones)
    jseq.add_jones(FJones)
    jseq.add_jones(JJones)
    # jseq.display()
    jseq.TDLCompileOptionsMenu()
    jseq.TDLSolveOptionsMenu()
    jseq.display()



def _define_forest(ns):

    cc = []

    jseq.make_jones_matrices(ns('3c567'))
    jseq.display()
    # cc.append(jseq.bundle())

    if len(cc)==0: cc.append(ns.dummy<<1.1)
    ns.result << Meq.Composer(children=cc)
    return True


#---------------------------------------------------------------

def _tdl_job_execute (mqs, parent):
    """Execute the forest, starting at the named node"""
    domain = meq.domain(1.0e8,1.1e8,1,1000)                            # (f1,f2,t1,t2)
    cells = meq.cells(domain, num_freq=1, num_time=100)
    request = meq.request(cells, rqtype='ev')
    result = mqs.meq('Node.Execute',record(name='result', request=request))
    return result
       


#===============================================================
# Test routine:
#===============================================================

if __name__ == '__main__':
    ns = NodeScope()
    jj = []

    if 1:
        jseq = JonesSequence22()
        jseq.display()

    if 1:
        jones = Joneset22.GJones(ns, quals='3c84', simulate=False)
        jseq.add_jones(jones)
        jones.display(full=True, recurse=10)

    if 1:
        jones = Joneset22.BJones(ns, quals=['3c84'], simulate=False,
                                 telescope='WSRT', band='21cm')
        jseq.add_jones(jones)
        jones.display(full=True)

    if 0:
        jones = Joneset22.FJones(ns, polrep='linear',simulate=True )
        # jones = FJones(ns, polrep='circular', quals='3c89', simulate=True)
        jseq.add_jones(jones)
        jones.display(full=True, recurse=12)

    if 0:
        jones = Joneset22.JJones(ns, quals=['3c84'], diagonal=True, simulate=True)
        jseq.add_jones(jones)
        jones.display(full=True)

    #...............................................................

    if 1:
        jseq.TDLCompileOptionsMenu()
        jseq.TDLSolveOptionsMenu()
        jseq.make_jones_matrices(ns('3c844')('repeel'), trace=True)

    if 1:
        jseq.display()
        jseq.history().display(full=True)


#===============================================================
    
