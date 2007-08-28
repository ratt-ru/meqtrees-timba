# file: ../Grunt/Executor.py

# History:
# - 25aug2007: creation

# Description:

# The Grunt Executor class makes it easier for the user to execute
# trees in various ways. 



#======================================================================================

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
from Timba.Meq import meq

# import Meow

from Timba.Contrib.JEN.Grunt import OptionManager

# from copy import deepcopy

#======================================================================================

class Executor (object):
    """The Grunt Executor class makes it easy to execute trees in various ways"""

    def __init__(self, mode='single',
                 namespace=None):

        self.name = 'exec'
        self._frameclass = 'Grunt.Executor'       # for reporting

        self._OM = OptionManager.OptionManager(self.name, namespace=namespace)

        self._dims = []                           # control variable

        self.define_options(mode)

        self.request_counter = 0                  # see .request()
        
        # Finished:
        return None


    #===============================================================
    # Display of the contents of this object:
    #===============================================================

    def oneliner(self):
        """Return a one-line summary of this object"""
        ss = 'Grunt.Executor:'
        ss += ' '+str(self.name)
        ss += '  '+str(self._dims)
        return ss


    def display(self, txt=None, full=False, recurse=3, OM=True, level=0):
        """Print a summary of this object"""
        prefix = '  '+(level*'  ')+'ex'
        if level==0: print
        print prefix,' '
        print prefix,'** '+self.oneliner()
        if txt: print prefix,'  * (txt='+str(txt)+')'
        print prefix,'  * domain() -> '+str(self.domain())
        #...............................................................
        print prefix,'  * '+self._OM.oneliner()
        if OM: self._OM.display(full=False, level=level+1)
        #...............................................................
        print prefix,'**'
        if level==0: print
        return True



    #===================================================================
    # Options management:
    #===================================================================

    def make_TDLRuntimeOptionMenu (self, **kwargs):
        """Make the TDL menu of run-time options"""
        return self._OM.make_TDLRuntimeOptionMenu(**kwargs)
    
    
    #-------------------------------------------------------------------

    def define_options(self, mode):
        """Define the various options in its OptionManager object"""

        # Individual options in the main menu (i.e. submenu=None):
        submenu = 'runtime.'
        opt = ['single','time_sequence','freq_sequence','4D']
        self._OM.define(submenu+'mode', mode,
                        opt=opt, more=str,
                        prompt='forest execution mode',
                        callback=self._callback_mode,
                        doc = """The following Executor modes are supported:
                        Changing the mode will change the visible options. 
                        """)

        self.submenu_dim (dim='time',
                          unit=['s','min','hr','day'],
                          start=[0.0,1.0,10.0],
                          size=[1.0,10.0,100.0],
                          num_cells=[11,1,2,5,21,31,51,101],
                          step=[1.0,10.0,100.0],
                          num_steps=[1,2,5,10,20,50,100])

        self.submenu_dim (dim='freq',
                          unit=['MHz','Hz','kHz','GHz'],
                          start=[0.0,1.0,10.0,100.0],
                          size=[1.0,10.0,100.0],
                          num_cells=[10,1,2,5,20,30,50,100],
                          step=[1.0,10.0,100.0],
                          num_steps=[1,2,5,10,20,50,100])

        # Finished
        return True

    #-------------------------------------------------------------------

    def add_extra_dim (self, dim=None, unit=[None]):
        """Convenience function to include standard dimensions"""

        if dim in ['l','m']:
            self.submenu_dim (dim=dim,
                              unit=['rad','deg'],
                              start=[0.0,1.0,10.0,100.0],
                              size=[1.0,10.0,100.0],
                              num_cells=[9,1,2,5,21,31,51,101],
                              step=[1.0,10.0,100.0],
                              num_steps=[1,2,5,10,20,50,100])

        elif dim in ['x','y','z']:
            self.submenu_dim (dim=dim,
                              unit=['m'],
                              start=[0.0,1.0,10.0,100.0],
                              size=[1.0,10.0,100.0],
                              num_cells=[9,1,2,5,21,31,51,101],
                              step=[1.0,10.0,100.0],
                              num_steps=[1,2,5,10,20,50,100])


        elif isinstance(dim,str):
            if not isinstance(unit,list):
                unit = [unit]
            self.submenu_dim (dim=dim, unit=unit)

        return True


    #-------------------------------------------------------------------

    def submenu_dim (self, dim='x', unit=['m'],
                     start=[0.0], size=[1.0],
                     num_cells=[10,1,2,5,20,50,100],
                     step=[1.0], num_steps=[1,2,5,10,100]):
        """Generic function to make a dimension-menu"""

        if dim in self._dims:
            raise ValueError, 'duplication of dims'
        self._dims.append(dim)
        
        submenu = 'runtime.'+dim+'.'
        self._OM.define(submenu+'unit', unit[0],
                        prompt=dim+'_unit',
                        opt=unit,
                        doc='unit along '+dim+'-axis')
        self._OM.define(submenu+'start', start[0],
                        prompt='domain start',
                        opt=start, more=float,
                        doc='"lower" edge of the domain')
        self._OM.define(submenu+'size', size[0],
                        prompt='domain size',
                        opt=size, more=float,
                        doc='domain size in '+dim+' dimension')
        self._OM.define(submenu+'num_cells', num_cells[0],
                        prompt='nr of cells',
                        opt=num_cells, more=int,
                        doc='nr of domain cells in '+dim+' dimension')

        submenu += 'sequence.'
        self._OM.define(submenu+'step', step[0],
                        prompt='step size',
                        opt=step, more=float,
                        doc='size (units!) of a step')
        self._OM.define(submenu+'num_steps', num_steps[0],
                        prompt='nr of '+dim+' steps',
                        opt=num_steps, more=int,
                        doc='nr of steps in the sequence')
        return True

    #----------------------------------------------------------------

    def tmult (self, trace=False):
        """Helper function to calculate the time unit mult.factor"""
        tunit = self._OM['time.unit']
        if tunit=='s':
            tmult = 1.0
        elif tunit=='min':
            tmult = 60.0
        elif tunit=='hr':
            tmult = 3600.0
        elif tunit=='day':
            tmult = 60.0*3600.0
        return tmult

    
    def fmult (self, trace=False):
        """Helper function to calculate the freq unit mult.factor"""
        funit = self._OM['freq.unit']
        if funit=='Hz':
            fmult = 1.0
        elif funit=='kHz':
            fmult = 1e3
        elif funit=='MHz':
            fmult = 1e6
        elif funit=='GHz':
            fmult = 1e9
        return fmult

    #-------------------------------------------------------------------


    def _callback_dim (self, dim):
        """Function called whenever TDLOption 'dim' changes.
        It adjusts the hiding of options according to 'dim'."""

        if dim=='single':
            self._OM.hide('time_sequence')
            self._OM.hide('freq_sequence')
        elif dim=='time_sequence':
            self._OM.show('time_sequence')
            self._OM.hide('freq_sequence')
        elif dim=='freq_sequence':
            self._OM.hide('time_sequence')
            self._OM.show('freq_sequence')

        menu = self._OM.TDLMenu('runtime')
        if menu:
            menu.set_summary('(dim='+dim+')')

        return True
        
    #.....................................................................

    def _callback_mode (self, mode):
        """Function called whenever TDLOption _mode changes.
        It adjusts the hiding of options according to 'mode'."""

        if mode=='single':
            self._OM.hide('.sequence')
        elif mode=='time_sequence':
            self._OM.hide('.sequence')
            self._OM.show('time.sequence')
        elif mode=='freq_sequence':
            self._OM.hide('.sequence')
            self._OM.show('freq.sequence')

        menu = self._OM.TDLMenu('runtime')
        if menu:
            menu.set_summary('(mode='+mode+')')

        return True
        

    #=========================================================================
    # Forest execution:
    #=========================================================================

    def execute (self, mqs, parent, start='result', trace=True):
        """Execute the forest, starting at the named node (start)"""

        nodename = start
        if is_node(start):
            nodename = start.nodename
        if trace:
            print '\n** .execute(',str(nodename),'):'
        if not isinstance(nodename,str):
            s = '\n** Execute: invalid nodename: '+str(nodename)
            raise ValueError,s

        mode = self._OM['runtime.mode']

        if mode=='time_sequence':
            tmult = self.tmult()
            submenu = 'time.sequence.'
            toff = 0.0 
            for i in range(self._OM[submenu+'num_steps']):
                if trace:
                    print '---',i,' toff =',toff,'s'
                domain = self.domain (t0=toff, trace=trace)
                cells = self.cells (domain=domain, trace=trace)
                request = self.request (cells=cells, trace=trace)
                result = mqs.meq('Node.Execute',record(name=nodename, request=request))
                toff += self._OM[submenu+'step']*tmult

        elif mode=='freq_sequence':
            fmult = self.fmult()
            submenu = 'freq.sequence.'
            foff = 0.0
            for i in range(self._OM[submenu+'num_steps']):
                if trace:
                    print '---',i,' foff =',foff,'Hz'
                domain = self.domain (f0=foff, trace=trace)
                cells = self.cells (domain=domain, trace=trace)
                request = self.request (cells=cells, trace=trace)
                result = mqs.meq('Node.Execute',record(name=nodename, request=request))
                foff += self._OM[submenu+'step']*fmult

        elif mode=='4D':
            """Execute the forest with a 4D request (freq,time,l,m).
            NB: This does NOT work on a Compounder node!"""
            domain = meq.gen_domain(time=(0.0,1.0),freq=(1,10),l=(-0.1,0.1),m=(-0.1,0.1))
            cells = meq.gen_cells(domain=domain, num_time=4, num_freq=5, num_l=6, num_m=7)
            # request = meq.request(cells, rqtype='ev')
            request = self.request (cells=cells, trace=trace)
            result = mqs.meq('Node.Execute',record(name='result', request=request))
       
        else:
            # Assume mode=='single' (domain)
            domain = self.domain (trace=trace)
            cells = self.cells (domain=domain, trace=trace)
            request = self.request (cells=cells, trace=trace)
            result = mqs.meq('Node.Execute',record(name=nodename, request=request))

        # Finished:
        if trace:
            print '** -> result =',type(result),'\n'
        return result


    #-------------------------------------------------------------------

    def request (self, cells=None, trace=False):
        """Helper function to make a request"""
        if not cells:
            cells = self.cells(trace=trace)
        # request = meq.request(cells, rqtype='ev')      # does not renew the request....
        self.request_counter += 1
        rqid = meq.requestid(self.request_counter)
        if trace:
            print '** rqid(',self.request_counter,') =',rqid
        request = meq.request(cells, rqid=rqid)
        return request

    
    #-------------------------------------------------------------------
    

    def cells (self, domain=None, trace=False):
        """Helper function to make a cells"""
        if not domain:
            domain = self.domain(trace=trace)
        pp = dict()
        for dim in self._dims:
            pp['num_'+dim] = self._OM[dim+'.num_cells']
        # cells = meq.cells(domain, num_freq=num_freq, num_time=num_time)
        cells = meq.gen_cells(domain, **pp)
        if trace:
            print '** cells: ', pp
            print '** domain(cells) =',str(domain)
            print '** cells =',cells,'\n'
        return cells


    #-------------------------------------------------------------------


    def domain (self, f0=0.0, t0=0.0, trace=False):
        """Make a domain from the internal information.
        The offsets f0(Hz)=0 and t0(s)=0 are for making sequences.
        """

        offset = dict(freq=f0, time=t0)         # -> argument!

        pp = dict()
        for dim in self._dims:
            mult = 1.0
            if dim=='freq': mult = self.fmult()
            if dim=='time': mult = self.tmult()
            offset.setdefault(dim, 0.0)
            v0 = offset[dim]
            v1 = v0+self._OM[dim+'.start']*mult
            v2 = v1+self._OM[dim+'.size']*mult
            pp[dim] = (v1,v2)

        domain = meq.gen_domain(**pp)
        # domain = meq.gen_domain(time=(0.0,1.0),freq=(1,10),l=(-0.1,0.1),m=(-0.1,0.1))

        if trace:
            print '** domain =',str(domain)
        return domain
       
    
      
    
    





#=============================================================================
#=============================================================================
#=============================================================================
# Test routine (with meqbrowser):
#=============================================================================

if 1:
    xtor = Executor()
    xtor._OM.define ('compile.mode', '2D', opt=['2D','4D'])
    xtor.add_extra_dim('l')
    xtor.add_extra_dim('m')
    # xtor.add_extra_dim('x')
    # xtor.add_extra_dim('y')
    xtor._OM.make_TDLCompileOptionMenu()
    # xtor.display()

def _define_forest(ns):

    cc = []

    time = ns.time << Meq.Time()
    freq = ns.freq << Meq.Freq()
    if xtor._OM['compile.mode']=='4D':
        L = ns.L << Meq.Grid(axis='l')
        M = ns.M << Meq.Grid(axis='m')
        ftlm = ns.ftlm << Meq.Add(time, freq, L, M)
        cc.append(ftlm)
    else:
        freqtime = ns.freqtime << Meq.Add(time, freq)
        cc.append(freqtime)

    xtor.display('final', full=False)

    if len(cc)==0: cc.append(ns.dummy<<1.1)
    ns.result << Meq.Composer(children=cc)
    xtor.make_TDLRuntimeOptionMenu()
    return True



#---------------------------------------------------------------

Settings.forest_state.cache_policy = 100

def _tdl_job_execute (mqs, parent):
    """Execute the forest with the specified options (domain etc),
    starting at the named node"""
    return xtor.execute(mqs, parent, start='result')
    
def _tdl_job_display (mqs, parent):
    """Just display the current contents of the Executor object"""
    xtor.display('_tdl_job')
       
def _tdl_job_display_full (mqs, parent):
    """Just display the current contents of the Executor object"""
    xtor.display('_tdl_job', full=True)
       


       










#===============================================================
# Test routine:
#===============================================================

if __name__ == '__main__':
    ns = NodeScope()


    if 1:
        xtor = Executor()
        xtor.display('initial')

    if 1:
        xtor.make_TDLRuntimeOptionMenu()

    if 0:
        xtor.domain(trace=True)
        # xtor.cells(trace=True)
        # xtor.request(trace=True)

    if 1:
        xtor.display('final')



#===============================================================

