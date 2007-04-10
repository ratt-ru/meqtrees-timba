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

# from Timba.Contrib.JEN.util import JEN_bookmarks
# from Timba.Contrib.JEN import MG_JEN_dataCollect

from copy import deepcopy
import random
import math




#==========================================================================
#==========================================================================
#==========================================================================
#==========================================================================


class SimulParm (Meow.Parameterization):
    """Class that representes a subtree that simulates the behaviour of a
    MeqParm node."""

    def __init__(self, ns, name, quals=[], kwquals={},
                 value=0.0, stddev=0.0,
                 color='blue', style='circle', size=8, pen=2,
                 descr=None, tags=[]):

        Meow.Parameterization.__init__(self, ns=ns, name=name,
                                       quals=quals, kwquals=kwquals)

        self._def = [dict(mode='init', value=value, stddev=stddev, qual='init')]
        self._counter = dict(index=0)
        self._index = 0
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

    def factor(self, ampl=1.0, Psec=None, PHz=None, phase=0.0, stddev=None):
        """Attach a time-dependent factor to the subtree"""
        rr = dict(mode='factor', ampl=ampl, Psec=Psec, PHz=PHz,
                  phase=phase, stddev=stddev)
        return self.append(rr)

    def term(self, ampl=1.0, Psec=None, PHz=None, phase=0.0, stddev=None):
        """Attach a time-dependent factor to the subtree"""
        rr = dict(mode='term', ampl=ampl, Psec=Psec, PHz=PHz,
                  phase=phase, stddev=stddev)
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
        value = rr[name]
        if rr['stddev'].has_key(name):
            value = random.gauss(value, rr['stddev'][name])
        return value

    def _make_subtree(self, rr, qual=[]):
        """Make the subtree specified by rr"""
        node = self.ns[rr['qual']](qual)
        if node.initialized(): return node
        ampl = node('ampl') << self._get_value('ampl', rr)
        pi2 = 2*math.pi
        if rr['Psec']:
            time = node('time') << Meq.Time()
            Psec = node('Psec') << self._get_value('Psec', rr)
            arg = node('arg') << Meq.Divide(pi2*time,Psec)
        elif rr['PHz']:
            freq = node('freq') << Meq.Freq()
            PHz = node('PHz') << self._get_value('PHz', rr)
            arg = node('arg') << Meq.Divide(pi2*freq,PHz)
        else:
            return False
        cosa = node('cos') << Meq.Cos(arg)
        node << Meq.Multiply(ampl,cosa)
        display.subtree(node)
        return node

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
        """Create a another subtree with an automatically increased index"""
        self._counter['index'] += 1
        return self.create(qual=self._counter['index'])
    

    def create(self, qual=[]):
        """Create a subtree with the specified qualifier(s)"""
        node = self.ns['SimulParm'](qual)
        for rr in self._def:
            if rr['mode']=='init':
                value = random.gauss(rr['value'], rr['stddev'])
                curr = node('init') << Meq.Constant(value)
            elif rr['mode']=='factor':
                factor = self._make_subtree(rr, qual=qual)
                curr = node('mult_'+rr['qual']) << Meq.Multiply(curr,factor)
            elif rr['mode']=='term':
                term = self._make_subtree(rr, qual=qual)
                curr = node('add_'+rr['qual']) << Meq.Add(curr,term)
            elif rr['mode']=='binop':
                pass  
            else:
                pass
        node << Meq.Identity(curr)
        display.subtree(node)
        return node
    

    #-------------------------------------------------------------------


    def create_member (self, quals=None):
        """Create an entry, i.e. a simulation subtree, that simulates
        a MeqParm node that varies with time and/or frequency, and append
        it to the nodelist"""

        # print '\n** create_member(',quals,'):',self.oneliner(),'\n'

        ns = self._ns._derive(append=quals, prepend=self._basename)

        pp = self._simul                                    # Convenience
            
        # Expression used:
        #  default + fampl*cos(2pi*time/Psec) + tampl*cos(2pi*freq/PHz),
        #  where tampl, Psec, fsec, PHz may all vary from node to node.

        # The default value is the one that would be used for a regular
        # (i.e. un-simulated) MeqParm in a ParmGroup (see above) 
        default_value = ns.default_value << Meq.Constant(pp['default_value'])


        # Calculate the time variation:
        time_variation = None
        if pp['Psec']>0.0:
            tvar = ns.time_variation
            ampl = 0.0
            if pp['stddev']:                                # variation of the default value
                stddev = pp['stddev']*pp['scale']           # NB: pp['stddev'] is relative
                ampl = random.gauss(ampl, stddev)
            ampl = tvar('ampl') << Meq.Constant(ampl)
            Psec = pp['Psec']                               # variation period (sec)
            if pp['Psec_stddev']:
                stddev = pp['Psec_stddev']*pp['Psec']       # NB: Psec_stddev is relative
                Psec = random.gauss(pp['Psec'], stddev) 
            Psec = tvar('Psec') << Meq.Constant(Psec)
            time = ns.time << Meq.Time()
            # time = ns << (time - 4e9)                     # ..........?
            pi2 = 2*math.pi
            costime = tvar('cos') << Meq.Cos(pi2*time/Psec)
            time_variation = tvar << Meq.Multiply(ampl,costime)

        # Calculate the freq variation:
        freq_variation = None
        if pp['PMHz']>0.0:
            fvar = ns.freq_variation 
            ampl = 0.0
            if pp['stddev']:                                # variation of the default value
                stddev = pp['stddev']*pp['scale']           # NB: pp['stddev'] is relative
                ampl = random.gauss(ampl, stddev)
            ampl = fvar('ampl') << Meq.Constant(ampl)
            PMHz = pp['PMHz']                               # variation period (MHz)
            if pp['PMHz_stddev']:
                stddev = pp['PMHz_stddev']*pp['PMHz']       # NB: PMHz_stddev is relative
                PMHz = random.gauss(pp['PMHz'], stddev) 
            PHz = PMHz*1e6                                  # convert to Hz
            PHz = fvar('PHz') << Meq.Constant(PHz)
            freq = ns.freq << Meq.Freq()
            pi2 = 2*math.pi
            cosfreq = fvar('cos') << Meq.Cos(pi2*freq/PHz)
            freq_variation = fvar << Meq.Multiply(ampl,cosfreq)

        # Add the time/freq variation to the default value:
        cc = [default_value]
        if freq_variation: cc.append(freq_variation)
        if time_variation: cc.append(time_variation)
        ns = self._ns._derive(append=quals)
        node = ns[self._basename] << Meq.Add(children=cc, tags=self._tags)

        # Append the new node to the internal nodelist:
        self.append_member(node)
        return node










#===============================================================
# Test routine (with meqbrowser):
#===============================================================

def _define_forest(ns):

    cc = []

    pg1 = ParmGroup(ns, 'pg1', rider=dict(matrel='m21'))
    pg1.test()
    cc.append(pg1.visualize())
    nn1 = pg1.nodelist()
    print 'nn1 =',nn1

    pg2 = SimulatedParmGroup(ns, 'pg2')
    pg2.test()
    cc.append(pg2.visualize())
    nn2 = pg2.nodelist()
    print 'nn2 =',nn2

    condeqs = []
    for i in range(len(nn1)):
        print '- i =',i
        condeqs.append(ns.condeq(i) << Meq.Condeq(nn1[i],nn2[i]))
    solver = ns.solver << Meq.Solver(children=condeqs, solvable=nn1)
    JEN_bookmarks.create(solver, page='solver')
    cc.append(solver)
        



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

    sp1 = SimulParm(ns, 'sp1')
    print sp1.oneliner()
    sp1.term(ampl=100, PHz=5e8, stddev=dict(ampl=0.1, PHz=100))
    sp1.factor(Psec=1000, stddev=dict(ampl=0.1, Psec=100))
    # sp1.binop()
    sp1.next()
    # sp1.next()
    # sp1.next()



#===============================================================
    
