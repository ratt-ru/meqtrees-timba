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
                 descr='<descr>',
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
        print '   - TDLOptionMenu(s):'
        for key in self._TDLOptionMenu.keys():
            print '     - '+str(key)+': '+str(self._TDLOptionMenu[key])
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
        self._jones[jchar] = jones
        if True:
            # Re-initialise the underlying Joneset object:
            Joneset22.Joneset22.__init__(self, ns=jones.ns,
                                         # ns=jones.nodescope(),
                                         name='<placeholder>',
                                         quals=[], kwquals={},
                                         namespace=None,                                 # <---- !!
                                         descr='<descr>',
                                         stations=jones.stations(),
                                         polrep=jones.polrep(),
                                         telescope=jones._telescope,
                                         band=jones._band,
                                         simulate=False)
        self._update_object_labels(jones)  
        self._update_jseq_options(jchar, recurse=True)  # used in TDL menu
        return True


    def _update_object_labels (self, new):
        """Helper function"""
        self.name = ''                                  # NB: What about name-qualifier?
        for jchar in self._jones.keys():
            self.name += jchar
        # First create a new Jonset22 object with name/quals/descr that are
        # suitable combinations of those of the contributing Joneset22 objects: 
        name = new.name[0]
        descr = new.name+': '+new.descr()
        # self._stations = new.stations()
        # self._polrep = new.polrep()
        if False:
            qq = new.p_get_quals(remove=[new.name])
            for jones in joneslist[1:]:
                name += jones.name[0]
                descr += '\n '+jones.name+': '+jones.descr()
                qq = jones.p_get_quals(merge=qq, remove=[jones.name])
                qq.extend(new.p_quals2list(quals))
                jnew = Joneset22(ns, name=name+'Jones',
                                 quals=qq, stations=stations) 
        return True


    def _update_jseq_options (self, ss, recurse=False):
        """Helper function"""
        if not ss in self._jseq_options:
            self._jseq_options.append(ss)
        if recurse:
            # Service: Make a few 'standard' combinations:
            cc = self._jones.keys()
            if ('G' in cc) and ('D' in cc):
                self._update_jseq_options ('GD')
                if ('F' in cc):
                    self._update_jseq_options ('GDF')
        return True


    #-------------------------------------------------------------------
    # TDLOptions
    #-------------------------------------------------------------------

    def _callback_jseq (self, jseq):
        """Callback function used whenever jseq is changed by the user"""
        if jseq==None: jseq = []
        self._joneseq = []
        for jchar in self._jones.keys():
            if jchar in jseq:
                self._joneseq.append(jchar)             # selected list
            for key in ['jones','solvable']:
                jkey = jchar+'_'+key
                if self._TDLOption.has_key(jkey):
                    self._TDLOption[jkey].show(jchar in jseq)
        # self.TDL_solvable()         # temporary
        return True


    def TDLCompileOptionsMenu (self, key='jones', show=True):
        """Re-implementetion of the Joneset22 function for interaction
        with its TDLCompileOptions menu(s).
        The 'show' argument may be used to show or hide the menu.
        This can be done repeatedly, without duplicating the menu.
        """
        if not self._TDLOptionMenu.has_key(key):        # create menu only once
            oolist = []
            for jchar in self._jones.keys():
                oo = self._jones[jchar].TDLCompileOptionsMenu(key)
                jkey = jchar+'_'+key
                self._TDLOption[jkey] = oo
                oolist.append(oo)

            name = self.name
            # if self.tdloption_namespace:
            #     name += ' ('+str(self.tdloption_namespace)+')'

            if key=='jones':
                name += ' options'
                prompt = 'Selected Jones matrix sequence'
                oo = TDLCompileOption('jseq', prompt, 
                                      self._jseq_options, more=str,
                                      namespace=self);
                self._TDLOption['jseq'] = oo
                self._TDLOption['jseq'].when_changed(self._callback_jseq)

            elif key=='solvable':
                name += ' solvable'

            self._TDLOptionMenu[key] = TDLCompileMenu(name, *oolist)

        # Show/hide the menu as required (can be done repeatedly):
        self._TDLOptionMenu[key].show(show)
        return self._TDLOptionMenu[key]

    #-------------------------------------------------------------------

    def TDL_solvable (self, trace=False):
        """Get a list of the selected groups (or tags?) of solvable MeqParms"""
        jseq = self._TDLOption['jseq'].value
        if jseq==None: return []
        if not isinstance(jseq, str): return []
        slist = []
        for jchar in self._jones.keys():
            if trace: print ' - jchar:',jchar,
            if jchar in jseq:
                jkey = jchar+'_solvable'
                if self._TDLOption.has_key(jkey):
                    ss = self._TDLOption[jkey].value
                    if trace: print ': ss =',ss,'->',
                    if isinstance(ss, str):
                        slist.append(ss)
                    elif isinstance(ss, (list,tuple)):
                        slist.extend(ss)
            if trace: print '  slist =',slist
        if trace: print '** TDL_solvable(): jseq =',jseq,'->',slist
        return slist


    #------------------------------------------------------------------------

    def make_jones_matrix (self, station):
        """Make the Jones matrix for the specified station, by multiplying
        the corresponding matrices from the selected jonesets"""
        self._locked = True              # lock the object from here onwards...
        jj = self._joneseq               # list of selected jones matrices
        jj = self._jones.keys()          # ....temporary.....
        if len(jj)==0:
            raise ValueError, '** joneseq is empty'

        # If only one Jones matrix, multiplication is not necessary:
        if len(jj)==1:
            jones = self._jones[jj[0]]
            snode = jones(station)
            if True:                     # Just to make th
                self._matrixet = jones._matrixet 
                # self._matrixet(station) << snode
            return snode

        # Multiply two or more Jones matrices:
        qnode = self.ns[self.name]                   
        if not qnode.must_define_here(self):
            s = '** '+str(self.name)+': nodename clash: '+str(qnode)
            raise ValueError, s
        cc = []
        for j in jj:
            cc.append(self._jones[j](station))
        qnode(station) << Meq.MatrixMultiply(*cc)
        self._matrixet = qnode
        return qnode(station)



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

if 0:
    jseq = JonesSequence22()
    jseq.add_jones(Joneset22.GJones())
    jseq.add_jones(Joneset22.BJones())
    # jseq.display()
    jseq.TDLCompileOptionsMenu()
    jseq.TDLCompileOptionsMenu('solvable')
    jseq.display()


def _define_forest(ns):

    cc = []
    jj = []
    simulate = True

    if 0:
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

    if 0:
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

    if 0:
        jseq = Joneseq22 (ns, jj, quals='mmm')
        cc.append(jseq.p_bundle())
        cc.append(jseq.p_compare('GphaseA','GphaseB'))
        cc.append(jseq.p_plot_rvsi())
        cc.append(jseq.visualize('*'))
        jseq.display(full=True)
        jseq.history().display(full=True)

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
        jseq = JonesSequence22(ns)
        jseq.display()

    if 1:
        jones = Joneset22.GJones(ns, quals='3c84', simulate=True)
        jseq.add_jones(jones)
        jones.display(full=True, recurse=10)

    if 1:
        jones = Joneset22.BJones(ns, quals=['3c84'], simulate=False, telescope='WSRT', band='21cm')
        jseq.add_jones(jones)
        jones.display(full=True)

    if 0:
        jones = Joneset22.FJones(ns, polrep='linear',simulate=True )
        # jones = FJones(ns, polrep='circular', quals='3c89', simulate=True)
        jj.append(jones)
        jones.visualize()
        jones.display(full=True, recurse=12)

    if 0:
        jones = Joneset22.JJones(ns, quals=['3c84'], diagonal=True, simulate=True)
        jj.append(jones)
        jones.display(full=True)

    if 1:
        jseq.make_jones_matrices(trace=True)
        jseq.display()


    if 0:
        jseq.TDLCompileOptionsMenu()
        jseq.display()
        jseq.history().display(full=True)

    if 0:
        jseq = Joneseq22 (ns, jj, quals='mmm')
        jseq.display(full=True)
        jseq.history().display(full=True)


#===============================================================
    
