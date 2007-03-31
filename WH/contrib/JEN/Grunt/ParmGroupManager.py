# file: ../Grunt/ParmGroupManager.py

# History:
# - 04jan2007: creation (extracted from Matrix22.py)
# - 30mar2007: adapted to QualScope etc

# Description:

# The ParmGroupManager class encapsulates a number of ParmGroups
# e.g. ParmGroups or SimulatedParmGroups.
# It is used in classes like Matrix22. 

#======================================================================================

from Timba.TDL import *
from Timba.Meq import meq

import Meow

from Timba.Contrib.JEN.Grunt import NodeGroup 
from Timba.Contrib.JEN.Grunt import ParmGroup 
from Timba.Contrib.JEN.Grunt import Qualifiers

from Timba.Contrib.JEN.util import JEN_bookmarks
from Timba.Contrib.JEN import MG_JEN_dataCollect

from copy import deepcopy
import re

#======================================================================================

class ParmGroupManager (object):
    """Class that encapsulates a number of ParmGroups
    e.g. ParmGroups or SimulatedParmGroups."""

    def __init__(self, ns, quals=[], label='pgm',
                 parent='<parent object>'):
        # self._ns = ns                                # node-scope (required)
        self._label = label                          # label of the matrix 
        self._parent = str(parent)                   # its parent object (string)

        # Node-name qualifiers:
        self._ns = Meow.QualScope(ns, quals=quals)

        # ParmGroup objects:
        self._parmgroup = dict()                     # available ParmGroup objects (solvable)
        self._simparmgroup = dict()                  # available SimulatedParmGroup objects 
        self._pgog = dict()                          # used for define_gogs()
        self._sgog = dict()                          # used for define_gogs()
        self._dummyParmGroup = ParmGroup.ParmGroup('dummy')    # used for its printing functions...
        return None


    #-------------------------------------------------------------------

    def label(self):
        """Return the ParmGroupManager object label""" 
        return self._label

    #-------------------------------------------------------------------

    def NodeGroup_keys (self):
        """Return a list of NodeGroup keys"""
        keys = []
        for key in self._parmgroup.keys():
            if not isinstance(self._parmgroup[key], NodeGroup.NodeGog):
                keys.append(key)
        for key in self._simparmgroup.keys():
            if not isinstance(self._simparmgroup[key], NodeGroup.NodeGog):
                keys.append(key)
        return keys

    def NodeGog_keys (self):
        """Return a list of NodeGog keys"""
        keys = []
        for key in self._parmgroup.keys():
            if isinstance(self._parmgroup[key], NodeGroup.NodeGog):
                keys.append(key)
        for key in self._simparmgroup.keys():
            if isinstance(self._simparmgroup[key], NodeGroup.NodeGog):
                keys.append(key)
        return keys

    #-------------------------------------------------------------------

    def oneliner(self):
        """Return a one-line summary of this object"""
        # ss = str(type(self))
        ss = '<class ParmGroupManager>'
        ss += '  '+str(self.label())
        ss += ' (n='+str(len(self.NodeGroup_keys()))
        ss += '+'+str(len(self.NodeGog_keys()))+')'
        ss += ' quals='+str(self._ns._qualstring())
        return ss


    def display(self, txt=None, full=True):
        """Print a summary of this object"""
        print ' '
        print '** '+self.oneliner()
        if txt: print ' * (txt='+str(txt)+')'
        print ' * parent: '+self._parent
        #...............................................................
        print ' * Available NodeGroup objects ('+str(len(self.NodeGroup_keys()))+'):'
        for key in self._parmgroup.keys():
            pg = self._parmgroup[key]
            if not isinstance(pg, NodeGroup.NodeGog):
                print '  - '+str(pg.oneliner())
        for key in self._simparmgroup.keys():
            spg = self._simparmgroup[key]
            if not isinstance(spg, NodeGroup.NodeGog):
                print '  - '+str(spg.oneliner())
        #...............................................................
        print ' * Available NodeGog (Groups of NodeGroups) objects ('+str(len(self.NodeGog_keys()))+'): '
        for key in self._parmgroup.keys():
            pg = self._parmgroup[key]
            if isinstance(pg, NodeGroup.NodeGog):
                print '  - '+str(pg.oneliner())
        for key in self._simparmgroup.keys():
            spg = self._simparmgroup[key]
            if isinstance(spg, NodeGroup.NodeGog):
                print '  - (sim) '+str(spg.oneliner())
        #...............................................................
        if full:
            print self.tabulate()
        #...............................................................
        print '**\n'
        return True


    def display_NodeGroups(self, full=False):
        """Display all its NodeGroup and NodeGog objects"""
        print '\n******** .display_NodeGroups(full=',full,'):'
        print '           ',self.oneliner()
        for key in self._parmgroup.keys():
            self._parmgroup[key].display(full=full)
        for key in self._simparmgroup.keys():
            self._simparmgroup[key].display(full=full)
        print '********\n'
        return True

    #-------------------------------------------------------------------

    def tabulate (self, parmgroup='*', ss='', trace=False):
        """Make an entry (one or more rows) in a table.
        To be used to make a summary table of NodeGroups (e.g. ParmGroups).
        This can be re-implemented by derived classes."""
        keys = self.parmgroup2keys(parmgroup, severe=True, trace=trace)
        ss += '\n** Tabulated (parmgroup='+str(parmgroup)+'): '
        ss += str(self.oneliner())
        ss += '\n'
        for key in keys:
            if key in self._parmgroup.keys():
                ss = self._parmgroup[key].tabulate(ss)
            elif key in self._simparmgroup.keys():
                ss = self._simparmgroup[key].tabulate(ss)
        ss += '\n**\n'
        return ss


    #--------------------------------------------------------------

    def parmgroup2keys(self, parmgroup='*', severe=True, trace=False):
        """Helper function to convert the specified parmgroup(s) into
        a list of (existing) keys in self._parmgroup."""
        if trace: print
        pgs = deepcopy(parmgroup)                          # do NOT modify parmgroup
        if not isinstance(pgs,(list,tuple)): pgs = [pgs]
        avk = self._parmgroup.keys()                       # available keys
        avk.extend(self._simparmgroup.keys())
        keys = []
        for key in pgs:
            if key in avk:                                 # available
                keys.append(key)
                if trace: print '  - include parmgroup:',key,': ->',keys
            else:                                          # not available
                print '** parmgroup ',key,' not recognised in:',avk
                if severe:                                 # be difficult about it
                    raise ValueError, '** parmgroup '+str(key)+' not recognised in:'+str(avk)
        return keys

    #--------------------------------------------------------------

    def solvable(self, parmgroup='*', severe=True, trace=False):
        """Return the list of MeqParms in the specified parmgroup(s)"""
        keys = self.parmgroup2keys(parmgroup, severe=severe, trace=trace)
        parmlist = []
        for key in keys:
            if self._parmgroup.has_key(key):
                parmlist.extend(self._parmgroup[key].nodelist())
        if trace: print '** pgm.solvable(',parmgroup,') ->',len(parmlist)
        return parmlist
    

    def visualize(self, parmgroup='*', bookpage='ParmGroup', folder=None):
        """Visualise the specified parmgroups. Return a single root node."""
        keys = self.parmgroup2keys(parmgroup, severe=False)
        cc = []
        for key in keys:
            cc.append(self._parmgroup[key].collector(bookpage=bookpage, folder=folder))
        # Return a single root node for the visualization subtree:
        if len(cc)==0: return False
        if len(cc)==1: return cc[0]
        return self._ns << Meq.Composer(children=cc)

    
    def constraint_condeqs(self, parmgroup='*'):
        """Get a list of constraint-condeqs (nodes) from the specified parmgroups."""
        keys = self.parmgroup2keys(parmgroup, severe=True, trace=trace)
        cc = []
        for key in pgs:
            condeq = self._parmgroup[key].constraint_condeq()
            if condeq:
                if isinstance(condeq,list):
                    cc.extend(condeq)
                else:
                    cc.append(condeq)
        return cc
    

    def solver_label(self, parmgroup='*', severe=True, remove='Jones', trace=False):
        """Return a more or less descriptive label for a solver node,
        constructed from the specified parmgroup(s)"""
        keys = self.parmgroup2keys(parmgroup, severe=severe, trace=trace)
        if parmgroup=='*' and self._parmgroup.has_key(parmgroup):
            keys = self._parmgroup['*'].labels()           # label may become too long...
            if len(keys)>2:
                label = '_all'                             # better ?
                if trace: print '** pgm.label(',parmgroup,') ->',label
                return label
        label = ''
        for key in keys:
            label += '_'
            s1 = key
            if remove:
                s1 = self.substitute (s1, sub=remove, with='')
            label += str(s1)
        if trace: print '** pgm.label(',parmgroup,') ->',label
        return label


    def substitute (self, ss=None, sub=None, with=''):
        """Helper function to sub the given substring"""
        if True:
            # Temporary, until I master the use of string variables (sub,with)..........!!
            matchstr = re.compile(r'Jones')
            return matchstr.sub(r'', ss)
        if sub==None: return ss
        sb = deepcopy(sub)
        if not isinstance(sub, (list,tuple)): sb=[sb]
        for sb1 in sb:
            matchstr = re.compile(rsb1)
            ss = matchstr.sub(rwith, ss)
        return ss

    #--------------------------------------------------------------

    def solvable_groups(self):
        """Return the available parmproup names."""
        return self._parmgroup.keys()

    def parmgroup(self, key=None):
        """Return the specified ParmGroup (object)"""
        return self._parmgroup[key]

    #-----------------------------------------------------------------------------
    
    def merge(self, other, trace=True):
        """Helper function to merge its relevant NodeGroups/Gogs with those of another
        ParmGroupManager object"""
        if trace: print '\n** merge():'

        if False:
            # Obsolete?
            all = []
            if self._parmgroup.has_key('*'):
                if trace: print 'self[*]:',self._parmgroup['*']
                all.extend(self._parmgroup['*'].group())
            if other._parmgroup.has_key('*'):
                if trace: print 'other[*]:',other._parmgroup['*']
                all.extend(other._parmgroup['*'].group())
            if len(all)>0:
                self._parmgroup['*'] = NodeGroup.NodeGog(self._ns, '*', group=all)    

        for key in other._parmgroup.keys():
            if not self._parmgroup.has_key(key):
                self._parmgroup[key] = other._parmgroup[key]
            else:
                # Assume NodeGog....
                self._parmgroup[key].append_entry(other._parmgroup[key].group())

        for key in other._simparmgroup.keys():
            if not self._simparmgroup.has_key(key):
                self._simparmgroup[key] = other._simparmgroup[key]
            else:
                # Assume NodeGog....
                self._simparmgroup[key].append_entry(other._simparmgroup[key].group())

        if trace: print '**\n'
        return True


    #-----------------------------------------------------------------------------
    # Definition of (groups of) parmgroups: 
    #-----------------------------------------------------------------------------

    def define(self, ns, key, quals=[], descr=None, tags=[], 
               default=None, constraint=None, override=None,
               simul=None, simulate=False,
               rider=None, trace=False):
        """Helper function to define a named (key+quals) (Simulated)ParmGroup
        object. There are two modes:
        - In normal mode (simulate=False), a ParmGroup object is created,
          whose create_parmgroup_entry() method creates regular MeqParms.
        - Otherwise (simulate=True), a SimulatedParmGroup object is created,
          whose .create_parmgroup_entry() method produces subtrees that
          simulate MeqParm behaviour. Both classes are derived from NodeGroup.
        NB: simulate = (simulate or self._simulate).....
        """

        # Make a safe copy of the extra qualifiers (quals):
        uquals = deepcopy(quals)
        if not isinstance(uquals,(list,tuple)): uquals=[uquals]

        # The parmgroup key (name) is qkey, i.e. the specified key plus any qualifiers,
        # (e.g. source name), both from the nodescope and specified via quals.
        # For instance, qkey could be: 'Gphase_3c84'
        qkey = deepcopy(key)
        for qual in ns.quals:
            qkey += '_'+str(qual)
        for qual in uquals:
            qkey += '_'+str(qual)
        
        # Tags are used for two different mechanisms for selecting subsets of parms
        # that are to be solved for simultaneously:
        # - They are attached to the MeqParms, to allow selection with the nodescope
        #   .search() mechanism. This is used by the Meow parms.
        # - They are also used to create groups of (Simulated)ParmGroups (gogs), which
        #   offer some more services than the Meow parms.
        ptags = deepcopy(tags)                           # start from given tags
        if not isinstance(ptags,(list,tuple)): ptags = [ptags]
        utags = []
        for tag in ptags:
            if not tag in utags:
                utags.append(tag)                        # remove doubles
        for qual in uquals:
            if not qual in utags:
                utags.append(qual)                       # include qualifiers


        # Specific information may be attached to the ParmGroup via its rider.
        # if not isinstance(rider, dict): rider = dict()

        # OK, define the relevant ParmGroup:
        if simulate:
            pg = ParmGroup.SimulatedParmGroup (ns, label=qkey,
                                               quals=uquals,
                                               basename=key,
                                               descr=descr,
                                               tags=utags,
                                               simul=simul,
                                               default=default,
                                               override=override,
                                               rider=rider) 
            self._simparmgroup[qkey] = pg

        else:
            node_groups = ['Parm']                      # used by MeqParm node....
            pg = ParmGroup.ParmGroup (ns, label=qkey, 
                                      quals=uquals,
                                      basename=key,
                                      descr=descr,
                                      default=default,
                                      constraint=constraint,
                                      tags=utags,
                                      node_groups=node_groups,
                                      override=override,
                                      rider=rider)
            self._parmgroup[qkey] = pg


        # Collect information for define_gogs():
        # trace = True
        if trace: print '\n** define(',key,qkey,'): utags=',utags
        ignore = [qkey]
        for tag in utags:
            if not tag in ignore: 
                if simulate:
                    self._sgog.setdefault(tag, [])
                    self._sgog[tag].append(pg)
                    if trace: print '--- len(sgog[',tag,']) ->',len(self._sgog[tag])
                else: 
                    self._pgog.setdefault(tag, [])
                    self._pgog[tag].append(pg)
                    if trace: print '--- len(pgog[',tag,']) ->',len(self._pgog[tag])

        # Return the newly defined object:
        return pg


    #-----------------------------------------------------------------------------

    def define_gogs(self, name='ParmGroupManager', trace=False):
        """Helper function to define NodeGogs, i.e. groups of ParmGroups.
        It uses the information gleaned from the tags in define()"""

        if trace: print '\n** define_gogs(',name,'):'

        # First collect the primary groups (i.e. not gogs) in pg and spg (to be used below):
        pg = []
        for key in self._parmgroup.keys():
            if type(self._parmgroup[key])==ParmGroup.ParmGroup:
                pg.append(self._parmgroup[key])
        spg = []
        for key in self._simparmgroup.keys():
            if type(self._simparmgroup[key])==ParmGroup.SimulatedParmGroup:
                spg.append(self._simparmgroup[key])
            

        # Then make gogs for the tag-groups collected in .define()
        # If the gog already exists, append the new entries.
        for key in self._pgog.keys():
            if len(self._pgog[key])<=0:
                pass
            elif not self._parmgroup.has_key(key):
                self._parmgroup[key] = NodeGroup.NodeGog (self._ns, label=key,
                                                          descr='<descr>', 
                                                          group=self._pgog[key])
            elif type(self._parmgroup[key])==NodeGroup.NodeGog:
                self._parmgroup[key].append_entry(self._pgog[key])
            else:
                raise TypeError,'parmgroup['+key+'] is not a NodeGog: '+str(type(self._parmgroup[key])) 
            if trace: print '--- pgog',key,'(',len(self._pgog[key]),') ->',self._parmgroup[key].len()

        for key in self._sgog.keys():
            if len(self._sgog[key])<=0:
                pass
            elif not self._simparmgroup.has_key(key):
                self._simparmgroup[key] = NodeGroup.NodeGog (self._ns, label=key,
                                                             descr='<descr>', 
                                                             group=self._sgog[key])
            elif type(self._simparmgroup[key])==NodeGroup.NodeGog:
                self._simparmgroup[key].append_entry(self._sgog[key])
            else:
                raise TypeError,'simparmgroup['+key+'] is not a NodeGog: '+str(type(self._simparmgroup[key]))  
            if trace: print '--- sgog',key,'(',len(self._sgog[key]),') ->',self._simparmgroup[key].len()


        # Make the overall parmgroup(s) last, using the pg/spg collected before.
        # (Otherwise it gets in the way of the automatic group finding process).
        # for key in [name,'*']:
        for key in ['*']:
            if len(pg)>0:
                if not self._parmgroup.has_key(key):
                    self._parmgroup[key] = NodeGroup.NodeGog (self._ns, label=key, group=pg,
                                                              descr='all '+name+' parameters')
                elif type(self._parmgroup[key])==NodeGroup.NodeGog:
                    self._parmgroup[key].append_entry(pg)
                else:
                    raise TypeError,'parmgroup['+key+'] is not a NodeGog' 
                if trace: print '---',key,'(',len(pg),') ->',self._parmgroup[key].len()

            if len(spg)>0:
                if not self._simparmgroup.has_key(key):
                    self._simparmgroup[key] = NodeGroup.NodeGog (self._ns, label=key, group=spg,
                                                                 descr='all simulated '+name+' parameters')
                elif type(self._simparmgroup[key])==NodeGroup.NodeGog:
                    self._simparmgroup[key].append_entry(spg)
                else:
                    raise TypeError,'simparmgroup['+key+'] is not a NodeGog' 
                if trace: print '---',key,'(',len(spg),') ->',self._simparmgroup[key].len()

        if trace: print '**\n'
        return None


    #-----------------------------------------------------------------------------
    #-----------------------------------------------------------------------------

    def test (self, names=['first','second','third'], simulate=True):
        """Helper function to make some test-groups"""
        for name in names:
            pg = self.define(self._ns, name,
                             # quals='xxx',
                             descr='...'+name,
                             default=dict(c00=10.0, unit='rad', tfdeg=[0,0],
                                          subtile_size=1),
                             simul=dict(Psec=3, stddev=0.01, PMHz=9.9),
                             simulate=simulate,
                             tags=['test'])
            for index in range(4):
                node = pg.create_entry(index)

        # Make some secondary (composite) ParmGroups:
        self.define_gogs()
        return True







     
#===============================================================
# Test routine (with meqbrowser):
#===============================================================

def _define_forest(ns):

    cc = []

    pgm = ParmGroupManager(ns, quals=[])
    pgm.test()
    # cc.append(pgm.visualize())
    pgm.display(full=True)

    ns.result << Meq.Composer(children=cc)
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

    if 0:
        matchstr = re.compile(r'Jones')
        print matchstr.sub(r'xxx', 'abcJonesABS')

    if 1:
        pgm = ParmGroupManager(ns, quals=['3c84','xxx'], label='HH')
        pgm.test(['GJones','Gphase','Ggain'], simulate=True)
        pgm.display_NodeGroups(full=False)
        pgm.display(full=True)
        # pgm.tabulate(parmgroup='*')

        if 1:
            pgm.solvable(trace=True)
            pgm.solvable('Gphase', trace=True)
            pgm.solvable('xxx', severe=False, trace=True)
        
        if 1:
            pgm.solver_label(trace=True)
            pgm.solver_label('Gphase', trace=True)
            pgm.solver_label('xxx', severe=False, trace=True)
        


#===============================================================
    
