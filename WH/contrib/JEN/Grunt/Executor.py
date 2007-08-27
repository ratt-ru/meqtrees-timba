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
        opt = ['single','time_sequence','freq_sequence']
        self._OM.define('mode', mode, cat='runtime',
                        opt=opt, more=str,
                        prompt='forest execution mode',
                        callback=self._callback_mode,
                        doc = """The following Executor modes are supported:
                        Changing the mode will change the visible options. 
                        """)

        submenu = 'freq_domain'
        self._OM.define('funit', 'MHz', submenu=submenu, cat='runtime',
                        prompt='freq_unit',
                        opt=['Hz','kHz','MHz','GHz'],
                        doc='unit of frequency')
        self._OM.define('fstart', 1.0, submenu=submenu, cat='runtime',
                        prompt='domain start',
                        opt=[1.0,10.0], more=float,
                        doc='domain start freq')
        self._OM.define('df', 10.0, submenu=submenu, cat='runtime',
                        prompt='domain width',
                        opt=[10.0,100.0], more=float,
                        doc='domain size in the freq dimension')
        self._OM.define('num_freq', 10, submenu=submenu, cat='runtime',
                        prompt='nr of freq cells',
                        opt=[1,10,20,30,50,100], more=int,
                        doc='nr of freq cells in the domain')

        submenu = 'time_domain'
        self._OM.define('tunit', 's', submenu=submenu, cat='runtime',
                        prompt='time_unit',
                        opt=['s','min','hr','day'],
                        doc='unit of time')
        self._OM.define('tstart', 0.0, submenu=submenu, cat='runtime',
                        prompt='domain start',
                        opt=[0.0,1.0,10.0], more=float,
                        doc='domain start time')
        self._OM.define('dt', 1.0, submenu=submenu, cat='runtime',
                        prompt='domain length',
                        opt=[1.0,10.0,100.0], more=float,
                        doc='domain size in the time dimension')
        self._OM.define('num_time', 10, submenu=submenu, cat='runtime',
                        prompt='nr of time cells',
                        opt=[1,11,21,31,51,101], more=int,
                        doc='nr of time cells in the domain')

        submenu = 'x_domain'
        self._OM.define('xunit', 'rad', submenu=submenu, cat='runtime',
                        prompt='x_unit',
                        opt=['rad','m'],
                        doc='unit along x-axis')
        self._OM.define('xstart', 0.0, submenu=submenu, cat='runtime',
                        prompt='domain start',
                        opt=[0.0,1.0,10.0,100.0], more=float,
                        doc='domain x-start')
        self._OM.define('dx', 1.0, submenu=submenu, cat='runtime',
                        prompt='domain size',
                        opt=[1.0,10.0,100.0], more=float,
                        doc='domain size in the x dimension')
        self._OM.define('num_x', 10, submenu=submenu, cat='runtime',
                        prompt='nr of x cells',
                        opt=[1,11,21,31,51,101], more=int,
                        doc='nr of x cells in the domain')

        submenu = 'y_domain'
        self._OM.define('yunit', 'rad', submenu=submenu, cat='runtime',
                        prompt='y_unit',
                        opt=['rad','m'],
                        doc='unit along y-axis')
        self._OM.define('ystart', 0.0, submenu=submenu, cat='runtime',
                        prompt='domain start',
                        opt=[0.0,1.0,10.0,100.0], more=float,
                        doc='domain y-start')
        self._OM.define('dy', 1.0, submenu=submenu, cat='runtime',
                        prompt='domain size',
                        opt=[1.0,10.0,100.0], more=float,
                        doc='domain size in the y dimension')
        self._OM.define('num_y', 10, submenu=submenu, cat='runtime',
                        prompt='nr of y cells',
                        opt=[1,11,21,31,51,101], more=int,
                        doc='nr of y cells in the domain')

        submenu = 'time_sequence'
        self._OM.define('toff', 0.0, submenu=submenu, cat='runtime',
                        prompt='start offset',
                        opt=[0.0,1.0,10.0], more=float,
                        doc='initial offset')
        self._OM.define('tstep', 1.0, submenu=submenu, cat='runtime',
                        prompt='step size',
                        opt=[1.0,10.0,100.0], more=float,
                        doc='size (units!) of a time step')
        self._OM.define('num_time_steps', 10, submenu=submenu, cat='runtime',
                        prompt='nr of time steps',
                        opt=[1,2,5,10,20,50,100], more=int,
                        doc='nr of steps in the sequence')

        submenu = 'freq_sequence'
        self._OM.define('foff', 0.0, submenu=submenu, cat='runtime',
                        prompt='start offset',
                        opt=[0.0,1.0,10.0], more=float,
                        doc='initial offset')
        self._OM.define('fstep', 1.0, submenu=submenu, cat='runtime',
                        prompt='step size',
                        opt=[1.0,10.0,100.0], more=float,
                        doc='size (units!) of a freq step')
        self._OM.define('num_freq_steps', 10, submenu=submenu, cat='runtime',
                        prompt='nr of freq steps',
                        opt=[1,2,5,10,20,50,100], more=int,
                        doc='nr of steps in the sequence')

        # Finished
        return True


    #-------------------------------------------------------------------

    def _tdl_job_4D_tflm (mqs, parent):
        """Execute the forest with a 4D request (freq,time,l,m).
        NB: This does NOT work on a Compounder node!"""
        domain = meq.gen_domain(time=(0.0,1.0),freq=(1,10),l=(-0.1,0.1),m=(-0.1,0.1))
        cells = meq.gen_cells(domain=domain, num_time=4, num_freq=5, num_l=6, num_m=7)
        request = meq.request(cells, rqtype='ev')
        result = mqs.meq('Node.Execute',record(name='result', request=request))
        return result
       

       

    #.....................................................................

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

        if self._OM.TDLMenu():
            self._OM.TDLMenu().set_summary('(dim='+dim+')')

        return True
        
    #.....................................................................

    def _callback_mode (self, mode):
        """Function called whenever TDLOption _mode changes.
        It adjusts the hiding of options according to 'mode'."""

        if mode=='single':
            self._OM.hide('time_sequence')
            self._OM.hide('freq_sequence')
        elif mode=='time_sequence':
            self._OM.show('time_sequence')
            self._OM.hide('freq_sequence')
        elif mode=='freq_sequence':
            self._OM.hide('time_sequence')
            self._OM.show('freq_sequence')

        if self._OM.TDLMenu():
            self._OM.TDLMenu().set_summary('(mode='+mode+')')

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

        mode = self._OM['mode']

        if mode=='time_sequence':
            tmult = self.tmult()
            toff = self._OM['toff']*tmult 
            for i in range(self._OM['num_time_steps']):
                toff += self._OM['tstep']*tmult
                if trace:
                    print '---',i,' toff =',toff,'s'
                domain = self.domain (t0=toff, trace=trace)
                cells = self.cells (domain=domain, trace=trace)
                request = self.request (cells=cells, trace=trace)
                result = mqs.meq('Node.Execute',record(name=nodename, request=request))

        elif mode=='freq_sequence':
            fmult = self.fmult()
            foff = self._OM['foff']*fmult 
            for i in range(self._OM['num_freq_steps']):
                foff += self._OM['fstep']*fmult
                if trace:
                    print '---',i,' foff =',foff,'Hz'
                domain = self.domain (f0=foff, trace=trace)
                cells = self.cells (domain=domain, trace=trace)
                request = self.request (cells=cells, trace=trace)
                result = mqs.meq('Node.Execute',record(name=nodename, request=request))

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
        cells = meq.cells(domain,
                          num_freq=self._OM['num_freq'],
                          num_time=self._OM['num_time'])
        if trace:
            print '** cells: num_freq/time=',self._OM['num_freq'],self._OM['num_time']
            print '** domain(cells) =',str(domain)
        return cells


    #-------------------------------------------------------------------

    def tmult (self, trace=False):
        """Helper function to calculate the time unit mult.factor"""
        tunit = self._OM['tunit']
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
        funit = self._OM['funit']
        if funit=='Hz':
            fmult = 1.0
        elif funit=='kHz':
            fmult = 1e3
        elif funit=='MHz':
            fmult = 1e6
        elif funit=='GHz':
            fmult = 1e9
        return fmult


    def domain (self, f0=0.0, t0=0.0, trace=False):
        """Make a domain from the internal information.
        The offsets f0(Hz)=0 and t0(s)=0 are for making sequences.
        """
        fmult = self.fmult()
        f1 = f0+self._OM['fstart']*fmult
        f2 = f1+self._OM['df']*fmult

        tmult = self.tmult()
        t1 = t0+self._OM['tstart']*tmult
        t2 = t1+self._OM['dt']*tmult
        
        # domain = meq.domain(f1,f2,t1,t2)
        domain = meq.gen_domain(time=(t1,t2),freq=(f1,f2))
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
    # xtor.display()

def _define_forest(ns):

    cc = []

    time = ns.time << Meq.Time()
    freq = ns.freq << Meq.Freq()
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
    xtor.display()
       


       










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

