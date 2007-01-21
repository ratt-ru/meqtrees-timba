# file: ../Grunt/ParmGroupManager.py

# History:
# - 04jan2007: creation (extracted from Matrix22.py) 

# Description:

# The ParmGroupManager class encapsulates a number of ParmGroups
# e.g. ParmGroups or SimulatedParmGroups.
# It is used in classes like Matrix22. 

#======================================================================================

from Timba.TDL import *
from Timba.Meq import meq

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

    def __init__(self, ns, quals=[], label='pgm'):
        self._ns = ns                                # node-scope (required)
        self._label = label                          # label of the matrix 

        # Node-name qualifiers:
        self._quals = Qualifiers.Qualifiers(quals)

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

    def quals(self, append=None, prepend=None, exclude=None, merge=None):
        """Return the nodename qualifier(s), with temporary modifications"""
        return self._quals.get(append=append, prepend=prepend, exclude=exclude, merge=merge)


    #-------------------------------------------------------------------

    def oneliner(self):
        """Return a one-line summary of this object"""
        ss = str(type(self))
        ss += '  '+str(self.label())
        ss += '  quals='+str(self.quals())
        return ss


    def display(self, txt=None, full=False):
        """Print a summary of this object"""
        print ' '
        print '** '+self.oneliner()
        if txt: print ' * (txt='+str(txt)+')'
        #...............................................................
        print ' * Available NodeGroup objects: '
        for key in self._parmgroup.keys():
            pg = self._parmgroup[key]
            if not isinstance(pg, NodeGroup.NodeGog):
                print '  - '+str(pg.oneliner())
        for key in self._simparmgroup.keys():
            spg = self._simparmgroup[key]
            if not isinstance(spg, NodeGroup.NodeGog):
                print '  - (sim) '+str(spg.oneliner())

        print ' * Available NodeGog (Groups of NodeGroups) objects: '
        for key in self._parmgroup.keys():
            pg = self._parmgroup[key]
            if isinstance(pg, NodeGroup.NodeGog):
                print '  - '+str(pg.oneliner())
        for key in self._simparmgroup.keys():
            spg = self._simparmgroup[key]
            if isinstance(spg, NodeGroup.NodeGog):
                print '  - (sim) '+str(spg.oneliner())
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


    #--------------------------------------------------------------

    def solvable(self, parmgroup='*', severe=True, trace=False):
        """Return the list of MeqParms in the specified parmgroup(s)"""
        if trace: print
        pgs = deepcopy(parmgroup)
        if not isinstance(pgs,(list,tuple)): pgs = [pgs]
        keys = self._parmgroup.keys()
        parmlist = []
        for key in pgs:
            if key in keys:
                parmlist.extend(self._parmgroup[key].nodelist())
                if trace: print '  - include parmgroup:',key,': len(solvable) ->',len(parmlist)
            elif severe:
                if trace: print '** .solvable(): parmgroup ',key,' not recognised in:',pgs
                raise ValueError, '** parmgroup '+str(key)+' not recognised in:'+str(pgs)
        if trace: print '** pgm.solvable(',parmgroup,') ->',len(parmlist)
        return parmlist
    

    def solver_label(self, parmgroup='*', severe=True, remove='Jones', trace=False):
        """Return a more or less descriptive label for a solver node,
        constructed from the specified parmgroup(s)"""
        if trace: print
        pgs = deepcopy(parmgroup)
        if pgs=='*': pgs = self._parmgroup['*'].labels()
        if not isinstance(pgs,(list,tuple)): pgs = [pgs]
        keys = self._parmgroup.keys()
        label = ''
        for key in pgs:
            if key in keys:
                # if len(label)>0 : label += '_'
                label += '_'
                s1 = key
                if remove:
                    s1 = self.substitute (s1, sub=remove, with='')
                label += str(s1)
                if trace: print '  - include parmgroup:',key,': s ->',label
            elif severe:
                if trace: print '** .solver_label(): parmgroup ',key,' not recognised in:',pgs
                raise ValueError, '** parmgroup '+str(key)+' not recognised in:'+str(pgs)
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
    
    def merge(self, other):
        """Helper function to merge its relevant NodeGroups/Gogs with those of another
        ParmGroupManager object"""
        all = []
        if self._parmgroup.has_key('*'):
            print 'self[*]:',self._parmgroup['*']
            all.extend(self._parmgroup['*'].group())
        if other._parmgroup.has_key('*'):
            print 'other[*]:',other._parmgroup['*']
            all.extend(other._parmgroup['*'].group())
        self._parmgroup.update(other._parmgroup)
        self._simparmgroup.update(other._simparmgroup)
        rider = self._make_pgog_rider(all)
        self._parmgroup['*'] = NodeGroup.NodeGog(self._ns, '*', group=all,
                                                 rider=rider)    
        return True


    #-----------------------------------------------------------------------------

    def define_parmgroup(self, name, descr=None, tags=[], 
                         default=None, override=None,
                         simul=None, simulate=False,
                         rider=None):
        """Helper function to define a named (Simulated)ParmGroup object."""

        # There are two modes: In normal mode (simulate=False), a ParmGroup
        # is initialised, whose create_entry() method creates regular MeqParms.
        # Otherwise, a SimulatedParmGroup is initialises, whose .create_entry()
        # method produces subtrees that simulate MeqParm behaviour.

        # ....
        node_groups = ['Parm']
        # node_groups.extend(self.quals())               # <---------- !!!

        # Make sure that the group name is in the list of node tags:
        ptags = deepcopy(tags)
        if not isinstance(ptags,(list,tuple)): ptags = [ptags]
        if not name in ptags: ptags.append(name)

        # Specific information is attached to the ParmGroup via its rider.
        if not isinstance(rider, dict): rider = dict()

        # OK, define the relevant ParmGroup:
        if simulate:
            spg = ParmGroup.SimulatedParmGroup (self._ns, label=name,
                                                quals=self.quals(),
                                                descr=descr,
                                                tags=ptags,
                                                simul=simul,
                                                default=default,
                                                override=override,
                                                rider=rider) 
            self._simparmgroup[name] = spg

        else:
            pg = ParmGroup.ParmGroup (self._ns, label=name, 
                                      quals=self.quals(),
                                      descr=descr,
                                      default=default,
                                      tags=ptags,
                                      node_groups=node_groups,
                                      override=override,
                                      rider=rider)
            self._parmgroup[name] = pg

        # Collect information for define_gogs():
        for tag in ptags:
            if not tag in [name]:
                if simulate:
                    self._sgog.setdefault(tag, [])
                    self._sgog[tag].append(self._simparmgroup[name])
                else:
                    self._pgog.setdefault(tag, [])
                    self._pgog[tag].append(self._parmgroup[name])

        # Finished:
        return True

    #-----------------------------------------------------------------------------

    def create_parmgroup_entry(self, key=None, qual=None):
        """Create an entry with the specified qual in the specified (key)
        (Simulated)ParmGroup (object)"""
        if self._simparmgroup.has_key(key):
            return self._simparmgroup[key].create_entry(qual)
        else:
            return self._parmgroup[key].create_entry(qual)

    #-----------------------------------------------------------------------------

    def define_gogs(self, name='ParmGroupManager', trace=False):
        """Helper function to define NodeGogs, i.e. groups of ParmGroups.
        It uses the information gleaned from the tags in define_parmgroup()"""

        if trace: print '\n** define_gogs(',name,'):'

        # First collect the primary ParmGroups in pg and spg:
        pg = []
        for key in self._parmgroup.keys():
            if trace: print '- pg:',key
            pg.append(self._parmgroup[key])
        spg = []
        for key in self._simparmgroup.keys():
            if trace: print '- spg:',key
            spg.append(self._simparmgroup[key])
            
        # Then make separate gogs, as defined by the common tags:
        for key in self._pgog.keys():
            rider = self._make_pgog_rider(self._pgog[key])
            if trace:
                print '- pgog:',key,rider
                for g in self._pgog[key]: print '   - ',g.label()
            self._parmgroup[key] = NodeGroup.NodeGog (self._ns, label=key, descr='<descr>', 
                                                      group=self._pgog[key],rider=rider)
        for key in self._sgog.keys():
            if trace:
                print '- sgog:',key
                for g in self._sgog[key]: print '   - ',g.label()
            self._simparmgroup[key] = NodeGroup.NodeGog (self._ns, label=key, descr='<descr>', 
                                                         group=self._sgog[key])

        # Make the overall parmgroup(s) last, using the pg collected first:
        # (Otherwise it gets in the way of the automatic group finding process).
        for label in [name,'*']:
            if len(pg)>0:
                rider = self._make_pgog_rider(pg)
                if trace:
                    print '- pg overall:',label,rider
                    for g in pg: print '   - ',g.label()
                self._parmgroup[label] = NodeGroup.NodeGog (self._ns, label=label, group=pg, rider=rider,
                                                            descr='all '+name+' parameters')
            if len(spg)>0:
                if trace:
                    print '- spg overall:',label
                    for g in spg: print '   - ',g.label()
                self._simparmgroup[label] = NodeGroup.NodeGog (self._ns, label=label, group=spg,
                                                               descr='all simulated '+name+' parameters')
        return None

    #-----------------------------------------------------------------------------

    def _make_pgog_rider(self, group=[]):
        """Helper function to make a NodeGog rider from the riders of
        the given group (list) of ParmGroups"""
        # If any of the groups has matrel=='*' (all), return that.
        for pg in group:
            if pg.rider('matrel')=='*': return dict(matrel='*')
        # Otherwise, collect a list:
        mm = []
        for pg in group:
            mg = pg.rider('matrel')
            if not isinstance(mg,(list,tuple)): mg = [mg]
            for m in mg:
                if not m in mm:
                    mm.append(m)
        return dict(matrel=mm)


    #-----------------------------------------------------------------------------
    #-----------------------------------------------------------------------------

    def test (self, names=['first','second','third']):
        """Helper function to make some test-groups"""
        quals = self.quals()
        for name in names:
            self.define_parmgroup(name, descr='...'+name,
                                  default=10.0,
                                  simul=dict(stddev=0.01),
                                  tags=['test'])
            for index in range(4):
                node = self.create_parmgroup_entry(name, index)

        # Make some secondary (composite) ParmGroups:
        self.define_gogs()
        return True







     
#===============================================================
# Test routine (with meqbrowser):
#===============================================================

def _define_forest(ns):

    cc = []

    pgm = ParmGroupManager(ns, quals=[], simulate=True)
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
        pgm = ParmGroupManager(ns, quals=['3c84','xxx'], label='HH', simulate=False)
        pgm.test(['GJones','Gphase','Ggain'])
        pgm.display_NodeGroups(full=False)
        pgm.display(full=True)

        if 1:
            pgm.solvable(trace=True)
            pgm.solvable('Gphase', trace=True)
            pgm.solvable('xxx', severe=False, trace=True)
        
        if 1:
            pgm.solver_label(trace=True)
            pgm.solver_label('Gphase', trace=True)
            pgm.solver_label('xxx', severe=False, trace=True)
        


#===============================================================
    
