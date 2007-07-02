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
    """A Joneset22 that is a station-by-station matrix multiplication of
    one or more Joneset22 matrices."""

    def __init__(self, ns=None, name='<j>',
                 quals=[], kwquals={},
                 joneslist=[],
                 descr='<descr>',
                 simulate=False):

        # If simulate, use subtrees that simulate MeqParm behaviour:
        self._simulate = simulate

        # Initialise its Matrixet22 object:
        Joneset22.Joneset22.__init__(self, ns=ns, name=name)

        # The list of constituent Jones matrices. These may be any that
        # obeys the Jones contract:
        self._joneslist = joneslist
        self._locked = False

        # Finished:
        return None

    #-------------------------------------------------------------------

    def display_specific(self, full=False):
        """Print the specific part of the summary of this object"""
        print '   - stations ('+str(len(self.stations()))+'): '+str(self.stations())
        print '   - locked: '+str(self._locked)
        print '   - joneslist ('+str(len(self._joneslist))+'):'
        for jones in self._joneslist:
            print '      - '+str(jones.oneliner())
        return True

    #------------------------------------------------------------------------

    def append (self, jones):
        """Append a Jones matrix to the list. Do some checks, and condition it."""
        if self._locked:
            raise ValueError,'** JonesSequence22 is locked'
        self._joneslist.append(jones)
        return True

    #------------------------------------------------------------------------

    #-------------------------------------------------------------------
    # TDLOptions
    #-------------------------------------------------------------------

    def TDLCompileOptionsMenu(self):
        oo = []
        for jones in self._joneslist:
            oo.append(jones.TDLCompileOptionsMenu())
            TDLCompileMenu('Jones options', *oo)
        


    def TDLCompileOptionsMenu (self, key='jones', show=True):
        """Generic function for interaction with its TDLCompileOptions menu(s).
        The latter are created (once), by calling the specific function(s)
        .TDLCompileOptionsMenu_xxx(), which should be re-implemented by
        derived classes. The 'show' argument may be used to show or hide the
        menu. This can be done repeatedly, without duplicating the menu.
        """
        if not self._TDLOptionMenu.has_key(key):        # create menu only once
            if key=='jones':
                oolist = self.TDLCompileOptions_jones()
                name = self.name
                if self.tdloption_namespace:
                    name += ' ('+str(self.tdloption_namespace)+')'
                name += ' options'
                self._TDLOptionMenu[key] = TDLCompileMenu(name, *oolist)
            elif key=='solvable':
                co = self.TDLCompileOption_solvable()
                self._TDLOptionMenu[key] = co
            else:
                s = '** key not recognised: '+str(key)
                raise ValueError, s
        # Show/hide the menu as required (can be done repeatedly):
        self._TDLOptionMenu[key].show(show)
        return self._TDLOptionMenu[key]



    #------------------------------------------------------------------------

    def multiply (self):
        """Multiply the input matrices, and lock the result"""
        if not self._locked:
            pass
        self._locked = True
        return True



#=================================================================================================
# Make a Joneset22 object that is a sequence (matrix multiplication) of Jones matrices
#=================================================================================================

def Joneseq22 (ns, joneslist=None, quals=None):
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


def _define_forest(ns):

    cc = []
    jj = []
    simulate = True

    jones = GJones(ns, quals=[], simulate=simulate)
    jj.append(jones)
    # cc.append(jones.p_bundle(combine='Composer'))
    # cc.append(jones.p_plot_rvsi())
    # jones.bookpage(4)
    # cc.append(jones.visualize('rvsi'))          # default is rvsi
    # cc.append(jones.visualize('timetracks'))
    # cc.append(jones.visualize('spectra'))
    # jones.display(full=True)

    if 0:
        j2 = GJones(ns, quals=[], simulate=False)
        cc.append(j2.visualize())
        # j2.display(full=True)

    if 1:
        jones = BJones(ns, quals=[], simulate=simulate)
        jj.append(jones)
        # cc.append(jones.visualize())
        # cc.append(jones.visualize('spectra'))
        # jones.display(full=True)

    if 0:
        jones = JJones(ns, quals=[], simulate=simulate)
        jj.append(jones)
        # cc.append(jones.visualize())
        # jones.display(full=True)

    if 0:
        jones = FJones(ns, quals=['L'], simulate=simulate, polrep='linear')
        jj.append(jones)
        # cc.append(jones.visualize())
        jones.display(full=True)
        # jones.display_parmgroups(full=False)

    if 0:
        jones = FJones(ns, quals=['C'], simulate=simulate, polrep='circular')
        jj.append(jones)
        # cc.append(jones.visualize())
        jones.display(full=True)

    if 1:
        jseq = Joneseq22 (ns, jj, quals='mmm')
        cc.append(jseq.p_bundle())
        cc.append(jseq.p_compare('GphaseA','GphaseB'))
        cc.append(jseq.p_plot_rvsi())
        cc.append(jseq.visualize('*'))
        jseq.display(full=True)
        jseq.history().display(full=True)

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
        jseq = JonesSequence22(ns)
        jseq.display()

    if 1:
        jones = Joneset22.GJones(ns, quals='3c84', simulate=True)
        jseq.append(jones)
        jones.display(full=True, recurse=10)

    if 0:
        jones = BJones(ns, quals=['3c84'], simulate=False, telescope='WSRT', band='21cm')
        jj.append(jones)
        jones.visualize()
        jones.display(full=True)

    if 0:
        jones = FJones(ns, polrep='linear',simulate=True )
        # jones = FJones(ns, polrep='circular', quals='3c89', simulate=True)
        jj.append(jones)
        jones.visualize()
        jones.display(full=True, recurse=12)

    if 0:
        jones = JJones(ns, quals=['3c84'], diagonal=True, simulate=True)
        jj.append(jones)
        jones.display(full=True)

    if 1:
        jseq.display()
        jseq.history().display(full=True)

    if 0:
        jseq = Joneseq22 (ns, jj, quals='mmm')
        jseq.display(full=True)
        jseq.history().display(full=True)


#===============================================================
    
