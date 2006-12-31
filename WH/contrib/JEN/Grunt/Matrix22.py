# file: ../Grunt/Matrix22.py

# History:
# - 29dec2006: creation (extracted from Jones.py) 

# Description:

# The Matrix22 class encapsulates groups of 2x2 matrices,
# e.g. Jones matrices, or cohaerency matrices. 

#======================================================================================

from Timba.TDL import *
from Timba.Meq import meq

from ParmGroup import *

# from Timba.Contrib.JEN.Grunt import ParmGroup
from Timba.Contrib.JEN.util import JEN_bookmarks
from Timba.Contrib.JEN import MG_JEN_dataCollect

from copy import deepcopy

#======================================================================================

class Matrix22 (object):
    """Class that represents a set of 2x2 matrices.
    It is inherited by the Jones class and the Cohsat class.  
    It also contains the named ParmGroup objects that encapsulate
    groups of MeqParm nodes (or their simulation subtrees)"""

    def __init__(self, ns, scope=[], label='M', indices=[], simulate=False):
        self._ns = ns                                # node-scope (required)
        self._label = label                          # label of the matrix 
        self._scope = deepcopy(scope)                # scope -> used for nodename qualifiers
        if not isinstance(self._scope,(list,tuple)):
            self._scope = [self._scope]
        if not label in self._scope:
            self._scope.insert(0,label)  
        self._simulate = simulate                    # if True, use simulation subtrees (i.s.o. MeqParms)
        if self._simulate:
            self._scope.append('simul')

        self._matrix = None                          # the actual matrices (contract!)
        self._indices = indices                      # list of matrix 'indices' (e.g. stations)

        self._matrel = dict(m11=None, m12=None, m21=None, m22=None)  # Matrix22 matrix elements (contract!)
        self._matrel_index = dict(m11=[0,0], m12=[0,1], m21=[1,0], m22=[1,1])
        self._matrel_style = dict(m11='circle', m12='xcross', m21='xcross', m22='circle')
        self._matrel_color = dict(m11='red', m12='magenta', m21='darkCyan', m22='blue')

        self._parmgroup = dict()                     # available parameter group objects
        self._composite = dict()                     # see define_composite_parmgroups()
        self._dummyParmGroup = ParmGroup('dummy')
        self._dcoll = None
        return None

    #-------------------------------------------------------------------

    def label(self):
        """Return the Matrix22 object label""" 
        return self._label

    def scope(self, append=None):
        """Return the object scope (e.g. the peeling source name).
        Optionally, append the given qualifiers to the returned scope.
        The scope is translated into nodename qualifiers. It can be a list.""" 
        scope = deepcopy(self._scope)
        if not append==None:
            if not isinstance(scope,(list,tuple)):
                scope = [scope]
            if isinstance(append,(list,tuple)):
                scope.extend(append)
            else:
                scope.append(append)
        return scope

    #-------------------------------------------------------------------

    def indices(self, new=None):
        """Get/set the list of (matrix) indices"""
        if new:
            self._indices = new
        return self._indices


    def matrix(self, new=None):
        """Get/set the 2x2 matrices themselves"""
        if new:
            self._matrix = new
        return self._matrix

    #-------------------------------------------------------------------

    def matrel(self, key='m11', return_nodes=False):
        """Return the specified matrix element(s)"""
        if not self._matrel.has_key(key):
            return False                                # invalid key.....
        if not self._matrel[key]:                       # do only once
            scope = self.scope()
            name = self.label()+'_'+key[1:]
            for s in self.indices():
                index = self._matrel_index[key]
                node = self._ns[name](*scope)(s) << Meq.Selector(self._matrix(s),
                                                                 index=index)
            self._matrel[key] = self._ns[name](*scope)

        # Return a list of nodes, if required:
        if return_nodes:
            nodes = []
            for s in self.indices():
                nodes.append(self._matrel[key](s))
            return nodes
        
        # Otherwise, return the 'contract':
        return self._matrel[key] 

    #-------------------------------------------------------------------

    def oneliner(self):
        """Return a one-line summary of this object"""
        ss = str(type(self))
        ss += '  '+str(self._label)
        ss += '  n='+str(len(self._indices))
        ss += '  scope='+str(self._scope)
        # if self._simulate: ss += ' (simulate)'
        return ss

    def display(self, txt=None, full=False):
        """Print a summary of this object"""
        print ' '
        print '** '+self.oneliner()
        if txt: print ' * (txt='+str(txt)+')'
        print ' * Available indices ('+str(len(self.indices()))+'): '+str(self.indices())
        #...............................................................
        print ' * Available matrices ('+str(len(self.indices()))+'): '
        if self._matrix:
            for s in self.indices():
                print '  - '+str(s)+': '+str(self.matrix()(s))
            print ' * The first two matrices:'
            for i in range(len(self.indices())):
                if i<2:
                    node = self.matrix()(self.indices()[i])
                    self._dummyParmGroup.display_subtree(node, txt=str(i), recurse=2)
        #...............................................................
        print ' * Available ParmGroup objects ('+str(len(self.parmgroups()))+'): '
        for key in self.parmgroups():
            if not self._parmgroup[key]._composite:
                print '  - '+str(self._parmgroup[key].oneliner())
        for key in self.parmgroups():
            if self._parmgroup[key]._composite:
                print '  - '+str(self._parmgroup[key].oneliner())
        #...............................................................
        print ' * Extracted matrix elements: '
        for key in self._matrel.keys():
            print '  - '+str(key)+': '+str(self._matrel[key])
        #...............................................................
        print ' * Visualization subtree: '
        if self._dcoll:
            self._dummyParmGroup.display_subtree(self._dcoll, txt=':',
                                                 show_initrec=False, recurse=1)
        print '   - matrel_index: '+str(self._matrel_index)
        print '   - matrel_color: '+str(self._matrel_color)
        print '   - matrel_style: '+str(self._matrel_style)
        #...............................................................
        print '**\n'
        return True

    #-------------------------------------------------------------------

    def define_parmgroup(self, name, descr=None,
                         default=0.0, tags=[],
                         Tsec=1000.0, Tstddev=0.1,
                         scale=1.0, stddev=0.1,
                         pg=None):
        """Helper function to define a named ParmGroup object"""

        # ....
        node_groups = ['Parm']
        # node_groups.extend(self._scope)               # <---------- !!!

        # Make sure that the group name is in the list of node tags:
        ptags = deepcopy(tags)
        if not isinstance(ptags,(list,tuple)): ptags = [ptags]
        if not name in ptags: ptags.append(name)

        # OK, define the ParmGroup:
        self._parmgroup[name] = ParmGroup (self._ns, name=name, scope=self._scope,
                                           descr=descr, default=default,
                                           tags=ptags, node_groups=node_groups,
                                           simulate=self._simulate,
                                           Tsec=Tsec, Tstddev=Tstddev,
                                           scale=scale, stddev=stddev,
                                           pg=pg)

        # Collect information for define_composite_parmgroups():
        for tag in ptags:
            if not tag in [name]:
                self._composite.setdefault(tag, [])
                self._composite[tag].append(self._parmgroup[name])

        # Finished:
        return self._parmgroup[name]

    #.....................................................................................

    def define_composite_parmgroups(self, name='Matrix22'):
        """Helper function to define composite ParmGroups.
        It uses the information gleaned from the tags in define_ParmGroup()"""
        print '\n** define_composite_parmgroups(',name,'):'
        # First collect the primary ParmGroups in pg:
        pg = []
        for key in self._parmgroup.keys():
            pg.append(self._parmgroup[key])
            print '-',name,key
        # Then make separate composites, as defined by the tags above:
        for key in self._composite.keys():
            print '-',key,len(self._composite[key])
            self.define_parmgroup(key, descr='<descr>', pg=self._composite[key])
        self.define_parmgroup(name, descr='all '+name+' parameters', pg=pg)
        return None

    #.....................................................................................

    def parmgroups(self):
        """Return the available parmgroup names""" 
        return self._parmgroup.keys()
    
    def parmgroup(self, key=None):
        """Return the specified parmgroup (object)""" 
        return self._parmgroup[key]

    def display_parmgroups(self, full=False, composite=False):
        """Display its ParmGroup objects"""
        print '\n******** .display_parmgroups(full=',full,', composite=',composite,'):'
        print '           ',self.oneliner()
        for key in self.parmgroups():
            if composite or (not self._parmgroup[key]._composite):
                self._parmgroup[key].display(full=full)
        print '********\n'
        return True

    def parmlist(self, keys='*'):
        """Return the list of nodes from the specified parmgroup(s)"""
        if keys=='*': keys = self._parmgroup.keys()
        if not isinstance(keys,(list,tuple)): keys = [keys]
        nodelist = []
        for key in keys:
            if self._parmgroup.has_key(key):
                nodelist.extend(self._parmgroup[key].nodelist())
            else:
                print '** parmgroup not recognised:',key
                return None
        print '\n** parmlist(',keys,'):'
        for node in nodelist: print ' -',node
        print 
        return nodelist

    #-------------------------------------------------------------------

    def multiply(self, other):
        """Multiply with the given Matrix22 object"""
        name = self.label()+other.label()
        scope = self.scope()
        for s in self._indices:
            self._ns[name](*scope)(s) << Meq.MatrixMultiply(self._matrix(s),
                                                            other._matrix(s))
        # Update the Matrix22 object attributes:
        self._matrix = self._ns[name](*scope)
        self._label += other._label
        self._parmgroup.update(other._parmgroup)
        return True

    #-------------------------------------------------------------------

    def compare(self, other):
        """Compare with the given Matrix22 object"""
        return True

    #-------------------------------------------------------------------

    def visualize (self, bookpage='Matrix22', folder=None):
        """Visualise the 4 complex matrix elements of all station
        Matrix22 matrices in a single real-vs-imag plot. Different
        matrix elements (m11,m12,m21,m22) have different styles
        and colors, which are the same for all Matrix22 matrices."""
        if not self._dcoll:
            scope = self.scope()
            dcoll_scope = self.label()
            for s in scope:
                dcoll_scope += '_'+s 
            dcolls = []
            for key in self._matrel.keys():  
                cc = self.matrel(key, return_nodes=True) 
                rr = MG_JEN_dataCollect.dcoll (self._ns, cc, 
                                               scope=dcoll_scope,
                                               tag=key,
                                               color=self._matrel_color[key],
                                               style=self._matrel_style[key],
                                               size=8, pen=2,
                                               type='realvsimag', errorbars=True)
                dcolls.append(rr)
                # Make a combined plot of all the matrix elements:
                # NB: nodename -> dconc_scope_tag
            rr = MG_JEN_dataCollect.dconc(self._ns, dcolls, scope=dcoll_scope,
                                          tag=' ', bookpage=None)
        # Return the dataConcat node:
        self._dcoll = rr['dcoll']
        JEN_bookmarks.create(self._dcoll, self.label(),
                             page=bookpage, folder=folder)
        return self._dcoll


    #------------------------------------------------------------------------------
    #------------------------------------------------------------------------------

    def test (self):
        """Helper function to make some test-matrices"""
        scope = self.scope()
        label = self.label()
        keys = self._matrel.keys()
        index = 0
        indices = []
        for key in keys:
            index += 1
            indices.append(index)
            self.define_parmgroup(key, descr='matrix element: '+key,
                                  default=index/10.0, stddev=0.01,
                                  tags=['test'])
            mm = dict(m11=0.0, m12=0.0, m21=0.0, m22=0.0)
            mm[key] = self._parmgroup[key].create_entry(index)
            mm[key] = self._ns << Meq.Polar(1.0,mm[key])
            mat = self._ns[label](*scope)(index) << Meq.Matrix22(mm['m11'],mm['m12'],
                                                                 mm['m21'],mm['m22'])
        # Store the matrices and the list if indices:
        self.indices(new=indices)
        self.matrix(new=self._ns[label](*scope))

        # Make some secondary (derived) ParmGroups:
        self.define_composite_parmgroups()
        return True







     
#===============================================================
# Test routine (with meqbrowser):
#===============================================================

def _define_forest(ns):

    dcolls = []
    simulate = True

    mat = Matrix22(ns, scope=[], simulate=simulate)
    mat.test()
    dcolls.append(mat.visualize())
    mat.display(full=True)

    ns.result << Meq.Composer(children=dcolls)
    return True

#---------------------------------------------------------------

def _tdl_job_execute (mqs, parent):
    """Execute the forest, starting at the named node"""
    domain = meq.domain(1.0e8,1.1e8,1,10)                            # (f1,f2,t1,t2)
    cells = meq.cells(domain, num_freq=10, num_time=11)
    request = meq.request(cells, rqtype='ev')
    result = mqs.meq('Node.Execute',record(name='result', request=request))
    return result
       


#===============================================================
# Test routine:
#===============================================================

if __name__ == '__main__':
    ns = NodeScope()

    if 1:
        m1 = Matrix22(ns, scope=['3c84','xxx'], label='HH', simulate=False)
        m1.test()
        m1.visualize()
        m1.display_parmgroups(full=False, composite=True)
        m1.display(full=True)

    if 0:
        m1.parmlist()
        m1.parmlist('test')

    if 0:
        nn = m1.matrel(return_nodes=False)
        m1.display(full=True)
        print '\n** matrel result:'
        for s in m1.indices():
            print '--',s,':',nn(s)
        print '-- (',6,'):',nn(6)     # !!
        print
        nn = m1.matrel(return_nodes=True)

    if 0:
        m1.matrel('m11')
        m1.matrel('m12')
        m1.matrel('m21')
        m1.matrel('m22')
        m1.display(full=True)


#===============================================================
    
