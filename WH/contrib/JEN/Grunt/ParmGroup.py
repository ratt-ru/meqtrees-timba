# file: ../Grunt/ParmGroup.py

# History:
# - 25dec2006: creation
# - 03jan2007: re-implemented as a specialization of class NodeGroup
# - 03jan2007: created another specialization class SimulatedParmGroup

# Description:

# The ParmGroup class encapsulates a named group of MeqParm nodes,
# or subtrees that generate simulated values for MeqParm nodes.
# ParmGroups are created in modules that implement bits of a
# Measurement Equation that contain parameters, e.g. instrumental
# Jones matrices, or LSM source models. They may be used for
# solving or visualization. They are also useful for generating
# user interfaces that offer a choice of solvers, etc.

#==========================================================================

from Timba.TDL import *
from Timba.Meq import meq

from Timba.Contrib.JEN.Grunt import NodeGroup 

from Timba.Contrib.JEN.util import JEN_bookmarks
from Timba.Contrib.JEN import MG_JEN_dataCollect

from copy import deepcopy
import random
import math



#==========================================================================

class ParmGroup (NodeGroup.NodeGroup):
    """Class that represents a group of (somehow related) MeqParm nodes"""

    def __init__(self, ns, label='<pg>',
                 nodelist=[],
                 quals=[], descr=None, tags=[], node_groups=[],
                 color='blue', style='circle', size=8, pen=2,
                 parmtable=None,
                 default=None, override=None, rider=None):

        NodeGroup.NodeGroup.__init__(self, ns=ns, label=label,
                                     quals=quals, descr=descr, tags=tags, 
                                     color=color, style=style, size=size, pen=pen,
                                     nodelist=nodelist,
                                     rider=rider)

        # Copy (and check) some input arguments:
        self._parmtable = parmtable       # name of (AIPS++) table of MeqParm values
        self._node_groups = deepcopy(node_groups)
        if not isinstance(self._node_groups,(list,tuple)):
            self._node_groups = [self._node_groups]
        if not 'Parm' in self._node_groups:
            self._node_groups.append('Parm')

        # Information needed to create MeqParm nodes (see create_entry())
        self._default = deepcopy(default)
        if not isinstance(self._default, dict): self._default = dict()
        self._default.setdefault('c00', 1.0)  
        self._default.setdefault('unit', None)      
        self._default.setdefault('tfdeg', None)
        self._default.setdefault('funklet_shape', None)
        self._default.setdefault('subtile_size', None)
        self._default.setdefault('use_previous', True)
        self._default.setdefault('auto_save', False)
        self._default.setdefault('save_all', False)
        self._default.setdefault('reset_funklet', False)

        # The information may be overridden:
        self._override = dict()
        if isinstance(override, dict):
            for tag in tags:
                if override.has_key(tag):                     # relevant for this ParmGroup
                    self._override = deepcopy(override[tag])  # copy ony the relevant part
        self.override_default(self._override)
        
        return None
                
    #-------------------------------------------------------------------

    def override_default (self, rr=None, trace=True):
        """Helper function to override the values of named fields in self._default
        with the values of fields with the same name in rr"""
        if trace: print '** .override_default():'
        dd = self._default
        for key in rr.keys():
            if dd.has_key(key):
                was = dd[key]
                dd[key] = rr[key]
                print '-',key,':',was,'->',dd[key]
            else:
                raise ValueError,'key ('+key+') not recognised in: '+str(dd.keys())
        self._default = dd
        return True
        

    #-------------------------------------------------------------------

    def display_specific(self, full=False):
        """Print the specific part of the summary of this object"""
        print ' * parmtable = '+str(self.parmtable())
        print ' * default ('+str(len(self._default))+'):'
        for key in self._default.keys():
            print '   - '+str(key)+' = '+str(self._default[key])
        print ' * override ('+str(len(self._override))+'):'
        for key in self._override.keys():
            print '   - '+str(key)+' = '+str(self._override[key])
        print '   - node_groups: '+str(self._node_groups)
        return True

    #-------------------------------------------------------------------

    def parmtable(self):
        """Return the name of the (AIPS++) table that contains the
        MeqParm values. If None, the default values are used."""
        return self._parmtable


    #======================================================================
    # Create a new ParmGroup entry (i.e. a MeqParm node)
    #======================================================================

    def create_entry (self, qual=None):
        """Create an entry, i.e. MeqParm node, or a simulation subtree,
        and append it to the nodelist"""

        # If in a qualifier (qual) is specified, append it to the temporary quals list: 
        quals = self._quals.get(append=qual)

        # If subtile_size is specified (i.e. nonzero and not None), assume an integer.
        # This specifies the size (nr of cells) of the solution-tile in the time-direction.
        # This means that separate solutions are made for these tiles, which tile the domain.
        # Tiled solutions are efficient, because they reduce the node overhead
        # For the moment, only time-tiling is enabled...
        tiling = record()
        if self._default['subtile_size']:
            tiling.time = self._default['subtile_size']

        # Use the shape (of coeff array, 1-relative) if specified.
        # Otherwise, use the [tdeg,fdeg] polc degree (0-relative)
        shape = self._default['funklet_shape']           #............??
        if shape==None:
            shape = [0,0]
            if not self._default['tfdeg']==None:
                shape = deepcopy(self._default['tfdeg']) # just in case.....
            shape[0] += 1                                # make 1-relative              
            shape[1] += 1                                # make 1-relative
            
        node = self._ns.parm(*quals) << Meq.Parm(self._default['c00'],        ## funklet=..
                                                 shape=shape,
                                                 tiling=tiling,
                                                 save_all=self._default['save_all'],
                                                 auto_save=self._default['auto_save'],
                                                 reset_funklet=self._default['reset_funklet'],
                                                 use_previous=self._default['use_previous'],
                                                 table_name=self.parmtable(),
                                                 node_groups=self._node_groups,
                                                 tags=self._tags)

        # Append the new node to the internal nodelist:
        self.append_entry(node, plot_label=qual)
        return node


    #==========================================================================================

    def from_TDL_NodeSet():

        #------------------------------------------------------------------------
        
        # NB: If use_previous==True, the MeqParm will use its current funklet (if any)
        #     as starting point for the next snippet solution, unless a suitable funklet
        #     was found in the MeqParm table. If False, it will use the default funklet first.

        # Future (MXM, 10 jan 2006):
        # - default is a scalar, default = 1.0
        #   - NB: If neither init_funklet nor shape (nor table), then the shape
        #         of the default (default_value, really) still determines the solution...
        # - new keywords:
        #   - [polctype_]shape = [1,1,...]    [ntime, nfreq, ..]
        #     - 1-based,
        #     - default=None
        #     - shape overrides the shape of the initialising funklet, e.g. from parmtable
        #   - init_funklet = None
        #     - used for non-polc funklets, e.g. = polclog(0)
        #     - and for initialisation of other coeff than c00, e.g. polc([[],[]]) 

        # If subtile_size is specified (i.e. nonzero and not None), assume an integer.
        # This specifies the size (nr of cells) of the solution-tile in the time-direction.
        # This means that separate solutions are made for these tiles, which tile the domain.
        # Tiled solutions are efficient, because they reduce the node overhead
        # For the moment, only time-tiling is enabled...

        tiling = record()
        if rider['subtile_size']:
            tiling.time = rider['subtile_size']

        # The default value:
        if default==None:
            default = rider['c00_default']

        # Use the shape (of coeff array, 1-relative) if specified.
        # Otherwise, use the [tdeg,fdeg] polc degree (0-relative)
        shape = rider['funklet_shape']                   #............??
        if shape==None:
            shape = [0,0]
            if not rider['tfdeg']==None:
                shape = deepcopy(rider['tfdeg'])         # just in case.....
            # print key,'** shape =',shape
            shape[0] += 1                                # make 1-relative              
            shape[1] += 1                                # make 1-relative

        # Make the new MeqParm node (if necessary):
        node = ns[key](**quals)
        if compounder_children:
            parm = ns[key](**quals)
            if not parm.initialized():                   # made only once
                parm << Meq.Parm(init_funklet=init_funklet,
                                 tiling=tiling,
                                 use_previous=rider['use_previous'],
                                 reset_funklet=rider['reset_funklet'],
                                 auto_save=rider['auto_save'],
                                 save_all=rider['save_all'],
                                 node_groups=self.node_groups(),
                                 table_name=self.parmtable())
                self.NodeSet.set_MeqNode(parm, group=parmgroup)

            # The Compounder has more qualifiers than the Parm.
            # E.g. EJones_X is per station, but the compounder and its
            # children (l,m) are for a specific source (q=3c84)
            group = parmgroup                            # e.g. 'EJones'
            if isinstance(qual2, dict):
                for qkey in qual2.keys():
                    s1 = str(qual2[qkey])
                    quals[qkey] = s1
                    group += '_'+s1                      # e.g. 'EJones_3c84'
            node = ns[key](**quals)
            if not node.initialized():                   # made only once
                cc = compounder_children
                if not isinstance(cc, (list, tuple)): cc = [cc]
                cc.append(parm)
                node << Meq.Compounder(children=cc, common_axes=common_axes)
                self.NodeSet.set_MeqNode(node, group=group)
                self.NodeSet.append_MeqNode_eval(parm.name, append=node)

        elif node.initialized():                           # node already exists
            # Don't do anything, but return the existing node.
            pass

        elif init_funklet:
            node << Meq.Parm(init_funklet=init_funklet,
                             ### shape=shape,             # DON'T
                             # perturbation=1e-7,       # scale*1e-7
                             tiling=tiling,
                             use_previous=rider['use_previous'],
                             reset_funklet=rider['reset_funklet'],
                             auto_save=rider['auto_save'],
                             save_all=rider['save_all'],
                             node_groups=self.node_groups(),
                             table_name=self.parmtable())
            self.NodeSet.set_MeqNode(node, group=parmgroup)
            
        else:
            node << Meq.Parm(funklet=default,
                             shape=shape,
                             tiling=tiling,
                             save_all=rider['save_all'],
                             auto_save=rider['auto_save'],
                             reset_funklet=rider['reset_funklet'],
                             use_previous=rider['use_previous'],
                             node_groups=self.node_groups(),
                             table_name=self.parmtable())
            self.NodeSet.set_MeqNode(node, group=parmgroup)

        # Return the rootnode (MeqParm of MeqCompounder):
        return node




    #======================================================================
    # Function to fill the object with test data:
    #======================================================================

    def test(self):
        """Helper function to put in some standard entries for testing"""
        self.create_entry()
        self.create_entry(5)
        self.create_entry(6)
        return True








#==========================================================================
#==========================================================================
#==========================================================================
#==========================================================================


class SimulatedParmGroup (NodeGroup.NodeGroup):
    """Class that represents a group of nodes (subtrees) that simulate
    a group of MeqParm nodes (often used in conjunction with class ParmGroup)"""

    def __init__(self, ns, label='<pg>',
                 nodelist=[],
                 quals=[], descr=None, tags=[], node_groups=[],
                 color='blue', style='circle', size=8, pen=2,
                 simul=None, default=None, override=None,
                 rider=None):

        NodeGroup.NodeGroup.__init__(self, ns=ns, label=label,
                                     quals=quals, descr=descr, tags=tags, 
                                     color=color, style=style, size=size, pen=pen,
                                     nodelist=nodelist,
                                     rider=rider)

        # Make sure that tags/quals of the created nodes reflect the fact
        # that this is a simulated parameter.
        self._tags.append('simul')                     # ....??
        self._quals.append('simul')

        # The default value(s) of the MeqParm that is being simulated:
        self._default = deepcopy(default)
        if not isinstance(self._default, dict): self._default = dict()
        self._default.setdefault('c00', 0.0)
        self._default.setdefault('unit', None)
        
        # Information to create a simulation subtree (see create_entry())
        self._simul = deepcopy(simul)
        if not isinstance(self._simul, dict): self._simul = dict()
        self._simul.setdefault('default_value', self._default['c00'])           
        self._simul.setdefault('unit', self._default['unit'])           
        self._simul.setdefault('stddev', 0.1)          # stddev of default value (relative!) 
        self._simul.setdefault('Psec', 1000.0)         # Period of time variation (cos)
        self._simul.setdefault('Psec_stddev', 0.1)     # stddev of Psec (relative!)
        self._simul.setdefault('PMHz', -1.0)           # Period (MHz) of freq variation (cos)
        self._simul.setdefault('PMHz_stddev', 0.1)     # stddev of PMHz (relative!)
        self._simul.setdefault('scale', None)          # used to calculate absolute stddev
        if self._simul['scale']==None:
            self._simul['scale'] = abs(self._simul['default_value'])  #   use the (non-zero!) default value
            if self._simul['scale']==0.0: self._simul['scale'] = 1.0

        # The information may be overridden:
        self._override = dict()
        if isinstance(override, dict):
            for tag in tags:
                if override.has_key(tag):                     # relevant for this ParmGroup
                    self._override = deepcopy(override[tag])  # copy ony the relevant part
        self.override_simul(self._override)
        
        return None
                
    #-------------------------------------------------------------------

    def override_simul (self, rr=None, trace=True):
        """Helper function to override the values of named fields in self._simul
        with the values of fields with the same name in rr"""
        if trace: print '** .override_simul():'
        dd = self._simul
        for key in rr.keys():
            if dd.has_key(key):
                was = dd[key]
                dd[key] = rr[key]
                print '-',key,':',was,'->',dd[key]
            else:
                raise ValueError,'key ('+key+') not recognised in: '+str(dd.keys())
        self._simul = dd
        return True
        
    #-------------------------------------------------------------------

    def display_specific(self, full=False):
        """Print the specific part of the summary of this object"""
        print ' * simul ('+str(len(self._simul))+'):'
        for key in self._simul.keys():
            print '   - '+key+' = '+str(self._simul[key])
        print ' * default ('+str(len(self._default))+'):'
        for key in self._default.keys():
            print '   - '+str(key)+' = '+str(self._default[key])
        print ' * override ('+str(len(self._override))+'):'
        for key in self._override.keys():
            print '   - '+str(key)+' = '+str(self._override[key])
        return True


    #-------------------------------------------------------------------

    def create_entry (self, qual=None):
        """Create an entry, i.e. a simulation subtree, that simulates
        a MeqParm node that varies with time and/or frequency, and append
        it to the nodelist"""

        # If in a qualifier (qual) is specified, append it to the temporary quals list: 
        quals = self._quals.get(append=qual)

        pp = self._simul                                    # Convenience
            
        # Expression used:
        #  default + fampl*cos(2pi*time/Psec) + tampl*cos(2pi*freq/PHz),
        #  where tampl, Psec, fsec, PHz may all vary from node to node.

        # The default value is the one that would be used for a regular
        # (i.e. un-simulated) MeqParm in a ParmGroup (see above) 
        default_value = self._ns.default_value(*quals) << Meq.Constant(pp['default_value'])



        # Calculate the time variation:
        time_variation = None
        if pp['Psec']>0.0:
            tvar = self._ns.time_variation(*quals)
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
            time = self._ns << Meq.Time()
            # time = self._ns << (time - 4e9)                 # ..........?
            pi2 = 2*math.pi
            costime = tvar('cos') << Meq.Cos(pi2*time/Psec)
            time_variation = tvar << Meq.Multiply(ampl,costime)

        # Calculate the freq variation:
        freq_variation = None
        if pp['PMHz']>0.0:
            fvar = self._ns.freq_variation(*quals) 
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
            freq = self._ns << Meq.Freq()
            pi2 = 2*math.pi
            cosfreq = fvar('cos') << Meq.Cos(pi2*freq/PHz)
            freq_variation = fvar << Meq.Multiply(ampl,cosfreq)

        # Add the time/freq variation to the default value:
        cc = [default_value]
        if freq_variation: cc.append(freq_variation)
        if time_variation: cc.append(time_variation)
        node = self._ns.simulparm(*quals) << Meq.Add(children=cc, tags=self._tags)

        # Append the new node to the internal nodelist:
        self.append_entry(node)
        return node






    #======================================================================

    def test(self):
        """Helper function to put in some standard entries for testing"""
        self.create_entry(5)
        self.create_entry()
        self.create_entry(6)
        return True







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

    if 0:
        pg1 = ParmGroup(ns, 'pg1', rider=dict(matrel='m21'))
        pg1.test()
        pg1.display()

        if 0:
            dcoll = pg1.visualize()
            pg1.display_subtree (dcoll, txt='dcoll')

    if 1:
        simul = dict(Psec=500, PMHz=100)
        # simul = dict(Psec=-1, PMHz=-1)           # negative means ignore
        default = dict(value=-1.0)
        pg2 = SimulatedParmGroup(ns, 'pg2', simul=simul, default=default)
        pg2.test()
        pg2.display()



#===============================================================
    
