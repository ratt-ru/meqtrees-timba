# file: ../Grunt/SimulParm.py

# History:
# - 10apr2007: creation (from ParmGroup.py)

# Description:

# A SimulParm object defines a subtree (node) that can be attached
# to a Meow.Parm definition.

#==========================================================================

from Timba.TDL import *
from Timba.Meq import meq

import Meow

from Timba.Contrib.JEN.Grunt import display 

from Timba.Contrib.JEN.util import JEN_bookmarks
# from Timba.Contrib.JEN import MG_JEN_dataCollect

from copy import deepcopy
import random
import math


Settings.forest_state.cache_policy = 100


#==========================================================================
#==========================================================================
#==========================================================================
#==========================================================================


class SimulParm (Meow.Parameterization):
    """Class that representes a subtree that simulates the behaviour of a
    MeqParm node."""

    def __init__(self, ns, name,
                 value=0.0, stddev=0.0,
                 quals=[], kwquals={},
                 factor=None, term=None,
                 color='blue', style='circle', size=8, pen=2,
                 descr=None, tags=[]):

        Meow.Parameterization.__init__(self, ns=ns, name=name,
                                       quals=quals, kwquals=kwquals)

        self._def = [dict(mode='init', value=value, stddev=stddev, qual='init')]
        self._counter = dict(index=-1)
        self._usedval = dict()        
        self._index = 0

        # There is a limited possibility to specify the SimulParm behaviour
        # in the constructor, e.g. by factor=dict(ampl=0.4, Psec=300) etc
        # Note that one may EITHER specify a factor or a term, but not both.
        # This is to avoid any confsion about the order.
        # For more complicated bahaviour, use the factor() or term() functions
        # explicitly.
        if isinstance(factor,dict):
            self.factor(**factor)
        elif isinstance(term,dict):
            self.term(**term)
        
        return None
                
    #-------------------------------------------------------------------

    def oneliner(self):
        """Return a one-line summary of this object"""
        ss = '<SimulParm>'
        ss += ' %14s'%(self.name)
        ss += '  1/'+str(len(self._def))+':'+str(self._def[0])
        ss += '  '+str(self._counter)
        return ss

    def display(self, full=False):
        """Display a summary of this object"""
        print '\n** '+self.oneliner()
        print '  * Counter: '+str(self._counter)
        print '  * Definition:'
        for rr in self._def:
            rr1 = deepcopy(rr)
            rr1.__delitem__('mode')
            rr1.__delitem__('qual')
            rr1.__delitem__('stddev')
            print '    - '+str(rr['qual'])+': '+str(rr1)
        print '  * stddev records:'
        for rr in self._def:
            print '    - '+str(rr['qual'])+': '+str(rr['stddev'])
        print '**\n'
        return True

    #-------------------------------------------------------------------

    def factor(self, **rr):
        """Attach a time/freq-dependent factor to the subtree"""
        if not isinstance(rr, dict):
            s1 = '.factor(rr): rr should be a dict, not: '+str(type(rr))
            raise ValueError,s1
        rr['mode'] = 'factor'
        rr.setdefault('ampl', 1.0)
        rr.setdefault('Psec', None)
        rr.setdefault('PHz', None)
        rr.setdefault('phase', 0.0)
        rr.setdefault('stddev', None)
        return self.append(rr)


    def term(self, **rr):
        """Attach a time/freq-dependent term to the subtree"""
        if not isinstance(rr, dict):
            s1 = '.term(rr): rr should be a dict, not: '+str(type(rr))
            raise ValueError,s1
        rr['mode'] = 'term'
        rr.setdefault('ampl', 1.0)
        rr.setdefault('Psec', None)
        rr.setdefault('PHz', None)
        rr.setdefault('phase', 0.0)
        rr.setdefault('stddev', None)
        return self.append(rr)


    def binop (self, binop='Add', node=None):
        """Attach the given subtree (node) by means of the specified binary
        operation (e.g. 'Add' or 'Multiply')"""
        rr = dict(mode='binop', binop=binop, node=node, stddev=None)
        return self.append(rr)

    #-------------------------------------------------------------------

    def _get_value(self, name, rr):
        """Helper function"""
        if not isinstance(rr['stddev'],dict): rr['stddev'] = dict()
        value = deepcopy(rr[name])
        if rr['stddev'].has_key(name):
            value = random.gauss(value, rr['stddev'][name])
        self._usedval[name] = value
        return value

    #...................................................................

    def _make_subtree(self, rr, qual=[], show=False):
        """Make the subtree specified by rr"""

        name = rr['qual']
        if not qual:
            qnode = self.ns[name]
        elif isinstance(qual,(list,tuple)):
            qnode = self.ns[name](*qual)
        else:
            qnode = self.ns[name](qual)
        if qnode.initialized(): return qnode

        # Make the cosine argument: 2pi*((t/Psec)+(f/PHz))
        pi2 = 2*math.pi
        targ = None
        farg = None
        if rr['Psec']:
            time = qnode('time') << Meq.Time()
            Psec = qnode('Psec') << self._get_value('Psec', rr)
            targ = qnode('targ') << Meq.Divide(pi2*time,Psec)
        if rr['PHz']:
            freq = qnode('freq') << Meq.Freq()
            PHz = qnode('PHz') << self._get_value('PHz', rr)
            farg = qnode('farg') << Meq.Divide(pi2*freq,PHz)
        arg = None
        if targ and farg:
            # NB: The two period-terms are ADDED (not subtracted),
            #     so that they serve as a phase-term for each other,
            #     and do not affect the periods.
            arg = qnode('arg') << Meq.Add(targ,farg)
        elif targ:
            arg = targ
        elif farg:
            arg = farg
        else:
            raise ValueError,'neither Psec nor PHz specified'

        # Make the full ampl*cos(arg):
        cosarg = qnode('cos') << Meq.Cos(arg)
        ampl = qnode('ampl') << self._get_value('ampl', rr)
        qnode << Meq.Multiply(ampl,cosarg)

        # Finished:
        if show:
            display.subtree(qnode)
        # print '** SimulParm:',self.name,': _usedval=',self._usedval
        return qnode

    #-------------------------------------------------------------------

    def append(self, rr):
        """Attach a subtree definition record"""
        mode = rr['mode']
        self._counter.setdefault(mode,0)
        self._counter[mode] += 1
        rr['qual'] = mode+str(self._counter[mode])
        self._def.append(rr)
        return rr

        
    def next(self):
        """Create a another subtree (node) with an automatically increased index/qual.
        If stddev has been defined, the control values will be varied accordingly."""
        self._counter['index'] += 1
        return self.create(qual=self._counter['index'])
    

    def create(self, qual=None, show=False):
        """Create a subtree (node) with the specified qualifier(s)"""

        name = 'SimulParm'
        if not qual:
            qnode = self.ns[name]
        elif isinstance(qual,(list,tuple)):
            qnode = self.ns[name](*qual)
        else:
            qnode = self.ns[name](qual)

        for rr in self._def:
            if rr['mode']=='init':
                value = random.gauss(rr['value'], rr['stddev'])
                curr = qnode('init') << Meq.Constant(value)
            elif rr['mode']=='factor':
                factor = self._make_subtree(rr, qual=qual)
                curr = qnode('mult_'+rr['qual']) << Meq.Multiply(curr,factor)
            elif rr['mode']=='term':
                term = self._make_subtree(rr, qual=qual)
                curr = qnode('add_'+rr['qual']) << Meq.Add(curr,term)
            elif rr['mode']=='binop':
                pass  
            else:
                pass
        qnode << Meq.Identity(curr)
        if show: display.subtree(qnode)
        return qnode
    










#===============================================================
# Test routine (with meqbrowser):
#===============================================================

def _define_forest(ns):
    
    cc = []
    
    # Make a list of subtrees created by SimulParm objects:
    sp = []
    spnames = []
    pnames = []
    for i in range(3):
        spname = 'sp'+str(i)
        spnames.append(spname)
        pnames.append('p'+str(i))            # used for solver below
        sp1 = SimulParm(ns, spname)
        sp1.term(Psec=100+10*i, PHz=None, stddev=dict(ampl=0.1*i, Psec=i))
        ## sp1.factor(Psec=None, PHz=10000000, stddev=dict(ampl=0.1*i, Psec=i))
        sp.append(sp1.create())              # list of (subtree) nodes
        sp1.display()
    cc.append(ns.SimulParm << Meq.Composer(children=sp, plot_label=spnames))
    bookpage = 'parms'
    JEN_bookmarks.create(ns.SimulParm, page=bookpage, viewer='Collections Plotter')


    if True:
        # 'Misuse' the last sp1 object to create the MeqParm counterparts
        # of the SumulParm subtrees:
        pp = []
        for pname in pnames:
            sp1._add_parm(pname, Meow.Parm(), tags=['test'])
            pp.append(sp1._parm(pname))

        # The condeqs compare the SimulParms and their counterparts:
        condeqs = []
        labels = []
        for i in range(len(pp)):
            labels.append(pnames[i]+'_'+spnames[i])
            condeqs.append(ns.condeq(i) << Meq.Condeq(pp[i],sp[i]))

        # Make the solver:
        solver = ns.solver << Meq.Solver(children=condeqs, solvable=pp)

        # Bundle the solver and its associated visualisers with a reqseq:
        rsc = [solver]
        rsc.append(ns.Condeqs << Meq.Composer(children=condeqs, plot_label=labels))
        rsc.append(ns.Parm << Meq.Composer(children=pp, plot_label=pnames))
        cc.append(ns.solver_reqseq << Meq.ReqSeq(children=rsc))

        JEN_bookmarks.create(solver, page=bookpage)
        JEN_bookmarks.create(ns.Condeqs, page=bookpage, viewer='Collections Plotter')
        JEN_bookmarks.create(ns.Parm, page=bookpage, viewer='Collections Plotter')


    ns.result << Meq.Composer(children=cc)
    return True

#---------------------------------------------------------------

def _tdl_job_execute (mqs, parent):
    """Execute the forest, starting at the named node"""
    domain = meq.domain(1.0e8,1.1e8,1,100)                            # (f1,f2,t1,t2)
    cells = meq.cells(domain, num_freq=10, num_time=100)
    request = meq.request(cells, rqtype='ev')
    result = mqs.meq('Node.Execute',record(name='result', request=request))
    return result
       
def _tdl_job_sequence (mqs, parent):
    """Execute the forest, starting at the named node"""
    for t in range(-5,5):
      t1 = t                      
      t2 = t1+1
      domain = meq.domain(1.0e8,1.1e8,t1,t2)                           # (f1,f2,t1,t2)
      cells = meq.cells(domain, num_freq=1, num_time=3)
      request = meq.request(cells, rqid=meq.requestid(t+100))
      result = mqs.meq('Node.Execute',record(name='result', request=request))
    return result
       
       


#===============================================================
# Test routine:
#===============================================================

if __name__ == '__main__':
    ns = NodeScope()

    sp1 = SimulParm(ns, 'sp1')
    # sp1 = SimulParm(ns, 'sp1', factor=dict(Psec=1000, PHz=1e8, stddev=dict(ampl=0.1, Psec=100)))
    # print sp1.oneliner()
    sp1.term(ampl=100, PHz=5e8, stddev=dict(ampl=0.1, PHz=100))
    # sp1.factor(Psec=1000, PHz=1e8, stddev=dict(ampl=0.1, Psec=100))
    # sp1.binop()
    sp1.display()
    sp1.create(qual=[], show=True)
    # sp1.create(show=True)
    # sp1.next()
    # sp1.next()
    # sp1.next()



#===============================================================
    
