# TDL_Parmset.py
#
# Author: J.E.Noordam
#
# Short description:
#    A Parmset object encapsulates group(s) of MeqParms
#
# History:
#    - 20 dec 2005: creation, from TDL_Joneset.py
#    - 02 jan 2006: replaced the functions in TDL_Joneset.py (etc)
#    - 05 jan 2006: added make_condeq() etc
#    - 09 jan 2006: tile_size -> subtile_size
#    - 20 jan 2006: register() -> parmgroup()
#    - 21 jan 2006: function tf_polc() from MG_JEN_funklet.py
#    - 24 feb 2006: adopted new MXM MeqParm init keywords
#
# Full description:
#   The (many) MeqParms of a Measurement Equation are usually solved in groups
#   (e.g. GJones phases for all stations, etc). The Parmset object provides a
#   convenient way to define and use such groups in various ways. 
#   A Joneset object contains a Parmset, which is used when solvers are defined.
#
#   A Parmset object contains the following main components:
#   - A list of named parmgroups, i.e. lists of MeqParm node names. 
#   - A list of named solvegroups, i.e. lists of one or more parmgroup names.
#
#   A Parmset object contains the following services:
#   - Creation of a named parmgroup, and addition of members.
#   - Definition of a new MeqParm node (with all its various options)
#     (this function may be used by itself too)
#   - Definition of a solvegroup as a list of parmgroup names
#   - Creation of MeqCondeq nodes for standard condition equations
#     (e.g. to equate the sum of the GJones phases to zero)
#   - A buffer to temporarily hold new MeqParms by their 'root' name
#     (this is useful where simular MeqParms are defined with different
#     qualifiers, e.g. for the different stations in a Joneset)
#   - etc


#=================================================================================
# Preamble:
#=================================================================================

from Timba.TDL import *

from copy import deepcopy
from random import *
from math import *
from numarray import *

from Timba.Trees import TDL_common
from Timba.Trees import TDL_radio_conventions




#=================================================================================
# Class Parmset
#=================================================================================


class Parmset (TDL_common.Super):
    """A Parmset object encapsulates an (arbitrary) set of MeqParm nodes"""

    def __init__(self, **pp):

        # Input arguments:
        pp.setdefault('unsolvable', False)           # if True, do NOT store parmgroup/solvegroup info
        pp.setdefault('parmtable', None)             # name of MeqParm table (AIPS++)

        TDL_common.Super.__init__(self, type='Parmset', **pp)

        self.__unsolvable = pp['unsolvable']
        self.__parmtable = pp['parmtable']
        self.check_parmtable_extension()
        self.clear()
        return None



    def clear(self):
        """Clear the object"""
        self.__quals = dict()                        # record of default node-name qualifiers
        self.__parmgroup = dict()
        self.__default_value = dict()
        self.__pg_rider = dict()
        self.__condeq = dict()
        self.__solvegroup = dict()
        self.__plot_color = TDL_radio_conventions.plot_color()
        self.__plot_style = TDL_radio_conventions.plot_style()
        self.__plot_size = TDL_radio_conventions.plot_size()
        self.__MeqParm = dict()
        self.__buffer = dict()
        self.__node_groups = ['Parm']

    def unsolvable(self):
        """If True, no parmgroup/solvegroup info is stored"""
        return self.__unsolvable

    def quals(self, new=None, clear=False):
        """Get/set the default MeqParm node-name qualifier(s)"""
        if clear:
            self.__quals = dict()
        if isinstance(new, dict):
            for key in new.keys():
                self.__quals[key] = str(new[key])
        return self.__quals
        
    def buffer(self):
        """Get the temporary helper record self.__buffer"""
        return self.__buffer

#--------------------------------------------------------------------------------
            
    def oneliner(self):
        """Make a one-line summary of this Parmset object"""
        s = TDL_common.Super.oneliner(self)
        # if len(self.quals())>0:
        s += ' quals='+str(self.quals())
        s += ' pg:'+str(len(self.parmgroup()))
        s += ' sg:'+str(len(self.solvegroup()))
        s += ' cq:'+str(len(self.condeq()))
        # s += ' '+str(self.node_groups())
        if self.unsolvable():
            s += ' unsolvable'
        else:
            s += ' parmtable='+str(self.parmtable())
        return s


    def display(self, txt=None, full=False):
        """Display a description of the contents of this Parmset object"""
        ss = TDL_common.Super.display (self, txt=txt, end=False)
        indent1 = 2*' '
        indent2 = 6*' '
 
        ss.append(indent1+' - Registered parmgroups ('+str(len(self.parmgroup()))+'):')
        for key in self.parmgroup().keys():
          pgk = self.parmgroup()[key]
          n = len(pgk)
          if full or n<3:
            ss.append(indent2+' - '+key+' ( '+str(n)+' ): '+str(pgk))
          else:
            ss.append(indent2+' - '+key+' ( '+str(n)+' ): '+pgk[0]+' ... '+pgk[n-1])

        ss.append(indent1+' - parmtable   = '+str(self.parmtable()))
        ss.append(indent1+' - node_groups = '+str(self.node_groups()))
        ss.append(indent1+' - unsolvable  = '+str(self.unsolvable()))

        ss.append(indent1+' - Defined solvegroups ('+str(len(self.solvegroup()))+'):')
        for key in self.solvegroup().keys():
            ss.append(indent2+' - '+key+' :     parmgroups: '+str(self.solvegroup()[key]))

        ss.append(indent1+' - parmgroup riders (pg_rider):')
        for key in self.parmgroup().keys():
            if len(self.pg_rider()[key])>0:
                ss.append(indent2+' - '+key+': '+str(self.pg_rider()[key]))
 
        ss.append(indent1+' - parmgroup condeq definitions ('+str(len(self.__condeq))+'):')
        for key in self.__condeq.keys():
            ss.append(indent2+' - '+key+': '+str(self.__condeq[key]))

        if full:
            ss.append(indent1+' - Contents of temporary buffer:')
            for key in self.buffer().keys():
                ss.append(indent2+' - '+key+': '+str(self.buffer()[key]))

        ss.append(indent1+' - Available MeqParm nodes ( '+str(self.len())+' ):')
        if full or self.len()<10:
            for key in self.keys():
                ss.append(indent2+' - '+key+' : '+str(self.__MeqParm[key]))
        else:
            keys = self.keys()
            n = len(keys)-1
            ss.append(indent2+' - first: '+keys[0]+' : '+str(self.__MeqParm[keys[0]]))
            ss.append(indent2+'   ....')
            ss.append(indent2+' - last:  '+keys[n]+' : '+str(self.__MeqParm[keys[n]]))
        return TDL_common.Super.display_end (self, ss)




#--------------------------------------------------------------------------------
# Functions related to MeqParm nodes: 
#--------------------------------------------------------------------------------

    def __getitem__(self, key):
        """Get a named (key) MeqParm node"""
        # This allows indexing by key and by index nr:
        if isinstance(key, int): key = self.__MeqParm.keys()[key]
        return self.__MeqParm[key]

    def __setitem__(self, key, value):
        """Set a named (key) MeqParm node"""
        self.__MeqParm[key] = value
        return self.__MeqParm[key]

    def MeqParm(self):
        """The list of MeqParm nodes"""
        return self.__MeqParm
    def len(self):
        """The number of MeqParm nodes in MeqParm"""
        return len(self.__MeqParm)
    def keys(self):
        """The list of MeqParm keys (names)"""
        return self.__MeqParm.keys()
    def has_key(self, key):
        """Test whether MeqParm contains an item with the specified key"""
        return self.keys().__contains__(key)

    def node_groups(self, new=None):
        """Get/set node_groups (input for MeqParm definition)"""  
        if not new==None:
            if not isinstance(new, (tuple, list)): new = [new]
            for png in new:
                if not self.__node_groups.__contains__(png):
                    self.__node_groups.append(png)
        return self.__node_groups


    def parmtable(self, new=None):
        """Get/set the parmtable (MeqParm table) name""" 
        if isinstance(new, str):
            self.__parmtable = new
            self.check_parmtable_extension()
        return self.__parmtable

    def check_parmtable_extension(self):
        """Helper function for .parmtable()"""
        if isinstance(self.__parmtable, str):
            ss = self.__parmtable.split('.')
            if len(ss)==1: self.__parmtable += '.mep'
            return self.__parmtable.split('.')[1]
        return True

    #-------------------------------------------------------------------------------------

    def define_MeqParm(self, ns, key=None, qual=None, parmgroup=None,
                       default=None, shape=None, tfdeg=None, 
                       node_groups='Parm',
                       use_previous=True, subtile_size=None):
        """Convenience function to create a MeqParm node"""
        
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
        if subtile_size:
            tiling.time = subtile_size

        # The node-name qualifiers are the superset of the default ones
        # and the ones specified in this function call:
        quals = deepcopy(self.quals())          # just in case.....
        if isinstance(qual, dict):
            for qkey in qual.keys():
                quals[qkey] = str(qual[qkey])

        # The default value:
        if parmgroup==None:
            parmgroup = key
        if default==None:
            default = self.__default_value[parmgroup]

        # Use the shape (of coeff array, 1-relative) if specified.
        # Otherwise, use the [tdeg,fdeg] polc degree (0-relative)
        if shape==None:
            shape = [0,0]
            if not tfdeg==None:
                shape = deepcopy(tfdeg)         # just in case.....
            shape[0] += 1              
            shape[1] += 1

        # Make the new MeqParm node:
        node = ns[key](**quals) << Meq.Parm(default,
                                            shape=shape,
                                            tiling=tiling,
                                            use_previous=use_previous,
                                            node_groups=self.node_groups(),
                                            table_name=self.parmtable())

        # Store the new node:
        nodename = node.name
        self.__MeqParm[nodename] = node                 # record of named nodes 
        self.__parmgroup[parmgroup].append(nodename)    # 
        print '\n** MeqParm[',nodename,'] ->',node 

        # Put the node stub into the internal MeqParm buffer for later use:
        # This buffer is a service that allows access to the most recently
        # defined MeqParms by means of their parmgroup name, rather than
        # their full name:
        self.__buffer[parmgroup] = node
        return node







#--------------------------------------------------------------------------------
# Functions related to parmgroups:
#--------------------------------------------------------------------------------

    def parmgroup (self, key=None, **pp):
        """Get/create the named (key) parmgroup"""
        if key==None:                       # no parmgroup specified
            return self.__parmgroup         #   return the entire record
        elif self.__parmgroup.has_key(key): # parmgroup already exists
            return self.__parmgroup[key]    #   return it
        else:
            # Parmgroup does not exist yet: Create it:
            pp.setdefault('default', 1.0)       # default value (usually c00)
            pp.setdefault('color', None)        # plot color
            pp.setdefault('style', 'circle')    # plot style
            pp.setdefault('size', 10)           # size of plotted symbol
            pp.setdefault('default', 1.0)       # default MeqParm value for this parmgroup
            pp.setdefault('rider', dict())      # optional: record with named extra information
            self.__parmgroup[key] = []
            self.__pg_rider[key] = pp['rider']
            self.__default_value[key] = pp['default']
            self.__plot_color[key] = pp['color']
            self.__plot_style[key] = pp['style']
            self.__plot_size[key] = pp['size']
            qq = TDL_common.unclutter_inarg(pp)
            self.history('** Created parmgroup: '+key+':   '+str(qq))
            self.define_solvegroup(key, parmgroup=[key])
            return key                          # return the actual key name


    def pg_rider(self): return self.__pg_rider
    def plot_color(self): return self.__plot_color
    def plot_style(self): return self.__plot_style
    def plot_size(self): return self.__plot_size
    def default_value(self): return self.__default_value


    def parm_names(self, parmgroup=None, select='*', trace=False):
        """Return a list of parmgroup MeqParm node names"""
        if trace: print '\n** .parm_names(',parmgroup,select,'):'
        node_names = self.parmgroup(parmgroup) # list of MeqParm node-names
        parms = []
        n = len(node_names)
        if n==0:
            pass
        elif select=='first':               # select the first of each parmgroup
            parms.append(node_names[0])     # append a single node name
        elif select=='last':                # select the last of each parmgroup
            parms.append(node_names[n-1])   # append a single node name
        else:
            parms.extend(node_names)        # append entire parmgroup
        if trace: print '  ->',len(parms),':',parms,'\n'
        return parms


    def parm_nodes(self, parmgroup=None, select='*', trace=False):
        """Return a list of parmgroup MeqParm nodes"""
        trace = True
        if trace: print '\n** .parm_nodes(',parmgroup,select,'):'
        node_names = self.parm_names(parmgroup=parmgroup, select=select, trace=True)
        if not isinstance(node_names, list): return False
        nodes = []
        for name in node_names:
            print '- parm_nodes():',name,self.__MeqParm.has_key(name)
            nodes.append(self.__MeqParm[name])
        # Return a list of solvable MeqParm nodes:
        if trace: print '  ->',len(nodes),':',nodes,'\n'
        return nodes

#--------------------------------------------------------------------------------
# Functions related to condeqs:
#--------------------------------------------------------------------------------

    def define_condeq(self, parmgroup=None, unop='Add', value=0.0, select='*', trace=True):
        """Provide information for named (key) condeq equations"""
        if not self.__parmgroup.has_key(parmgroup):
            print '\n** parmgroup not recognised in:',self.__parmgroup.keys(),'\n'
            return False
        # Make the name (key) of the condeq defnition:
        key = parmgroup
        if select=='first':
            key += '_first'
            if unop=='Add': unop = None
            if unop=='Multiply': unop = None
        elif select=='last':
            key += '_last'
            if unop=='Add': unop = None
            if unop=='Multiply': unop = None
        elif unop=='Add':
            key += '_sum'
        elif unop=='Multiply':
            key += '_prod'
            if value==0: value = 1.0
        key += '='+str(value)
        if self.__condeq.has_key(key): key += '_2'
        if self.__condeq.has_key(key): key += '_2'
        if self.__condeq.has_key(key): key += '_2'
        # Look ahead to the possibility of a unop sequence:
        if unop:
            if not isinstance(unop,(list,tuple)): unop = [unop]
        # Make the dict that defines the condition equation (see .condeq())
        self.__condeq[key] = dict(parmgroup=parmgroup, select=select, unop=unop, value=value)
        if trace: print '\n** .define_condeq(',key,'):',self.__condeq[key],'\n'
        return key

 
    def condeq(self, key=None):
       """Access to condeq definitions"""
       if not key: return self.__condeq
       if self.__condeq.has_key(key):
           return self.__condeq[key]
       return False
   
        
    def make_condeq(self, ns=None, key=None):
       """Make a condeq node, using the specified (key) condeq definition"""
       funcname = '::make_condeq()'
       if not self.__condeq.has_key(key):
           print '\n**',funcname,':',key,'not recognised in:',self.__condeq.keys()
           return False
       rr = self.condeq(key)
       nodes = self.parm_nodes(rr['parmgroup'], select=rr['select'])
       uniqual = _counter(funcname, increment=-1)
       node = nodes[0]
       if rr['unop']:
           unop = rr['unop'][0]                    # for the moment
           if unop in ['Add','Multiply']:
               name = key.split('=')[0]
               node = ns[name](uniqual) << getattr(Meq, unop)(children=nodes)
       condeq = ns['Condeq_'+key](uniqual) << Meq.Condeq(node, rr['value'])
       return condeq


#--------------------------------------------------------------------------------
# Functions related to solvegroups:
#--------------------------------------------------------------------------------

    def define_solvegroup(self, key=None, parmgroup=None):
      """Derive a new solvegroup by combining existing parmgroups:
      These are used when defining a solver downstream (see Cohset)."""
      trace = False
      if trace: print '\n** .define_solvegroup(',key,parmgroup,'):'
      if parmgroup==None: return False                              # error?

      # NB: This is inhibited if Parmset is set 'unsolvable' (e.g. for simulated uv-data) 
      if self.unsolvable(): return False

      if not isinstance(parmgroup, list): parmgroup = [parmgroup]   
      self.__solvegroup[key] = parmgroup                            # list of existing parmgroup keys
      return True


    def solvegroup (self, key=None):
        """Get the named (key) solvegroup"""
        if key==None:
            return self.__solvegroup
        if self.__solvegroup.has_key(key):
            return self.__solvegroup[key]
        print '\n** solvegroup name not recognised: ',key
        print '     choose from:',self.solvegroup().keys(),'\n'
        return None

#--------------------------------------------------------------------------------

    def sg_rider(self, solvegroup=None, key=None, trace=False):
        """Collect (merge) the specified (key) rider info for the specified solvegroup(s)"""
        if not isinstance(solvegroup, (list, tuple)): solvegroup = [solvegroup]
        if trace: print '\n** .sg_rider(',solvegroup,key,'):'
        cc = []                                     # assume list items(...!!?) 
        for sgname in solvegroup:                   # solvegroup may be multiple
            sg = self.solvegroup(sgname)
            if not sg: return False                 # solvegroup not found
            for pgname in sg:                       # parmgroup name
                pg_rider = self.pg_rider()[pgname]  # parmgroup rider dict
                if not pg_rider.has_key(key): return False
                items = pg_rider[key]               # assume that items is a list...!!?
                if not isinstance(items,(list,tuple)): items = [items]
                for item in items:
                    if not item in cc: cc.append(item)  # merge into unique list.....!!?
        # Return a merged list of unique items of the 
        if trace: print '  ->',len(cc),':',cc,'\n'
        return cc

    def solveparm_names(self, solvegroup=None, select='*', trace=False):
        """Collect a list of (names of) solvable MeqParms"""
        if not isinstance(solvegroup, (list, tuple)): solvegroup = [solvegroup]
        if trace: print '\n** .solveparm_names(',solvegroup,select,'):'
        parms = []                                  # list of solvable node-names
        for sgname in solvegroup:                   # solvegroup may be multiple
            sg = self.solvegroup(sgname)
            if not sg: return False                 # solvegroup not found
            for pgname in sg:                       # parmgroup name
                node_names = self.parmgroup(pgname) # list of MeqParm node-names
                n = len(node_names)
                if select=='first':                 # select the first of each parmgroup
                    parms.append(node_names[0])     # append a single node name
                elif select=='last':                # select the last of each parmgroup
                    parms.append(node_names[n-1])   # append a single node name
                else:
                    parms.extend(node_names)        # append entire parmgroup
        # Return a list of solvable MeqParm node names:
        if trace: print '  ->',len(parms),':',parms,'\n'
        return parms


    def solveparm_nodes(self, solvegroup=None, select='*', trace=False):
        if trace: print '\n** .solveparm_nodes(',solvegroup,select,'):'
        names = self.solveparm_names(solvegroup=solvegroup, select=select, trace=False)
        if not isinstance(names, list): return False
        nodes = []
        for name in names:
            nodes.append(self.__MeqParm[name])
        # Return a list of solvable MeqParm nodes:
        if trace: print '  ->',len(nodes),':',nodes,'\n'
        return nodes


#---------------------------------------------------------------------------

    def cleanup(self):
      """Remove empty parmgroups/solvegroups"""
      removed = []
      for key in self.__parmgroup.keys():
        if len(self.__parmgroup[key])==0:
          self.__parmgroup.__delitem__(key)
          removed.append(key)
      # Remove solvegroups that have parmgroup members that do not exist:
      for skey in self.__solvegroup.keys():
        ok = True
        for key in self.__solvegroup[skey]:
          if not self.__parmgroup.has_key(key):
            ok = False
        if not ok: self.__solvegroup.__delitem__(skey)
      self.history ('.cleanup(): removed parmgroup(s): '+str(removed))
      return True


    def update(self, Parmset=None):
        """Update the solvegroup/parmgroup info from another Parmset object"""
        if Parmset==None: return False
        if self.unsolvable():
            self.history(append='not updated from (unsolvable): '+Parmset.oneliner())
        elif not Parmset.unsolvable():

            # NB: update OVERWRITES existing fields with new versions!
            # print 'Parmset.update(): self.__parmgroup:\n    ',self.__parmgroup
            if True:
                self.__parmgroup.update(Parmset.parmgroup())
            # print '    ',self.__parmgroup,'\n'

            self.__pg_rider.update(Parmset.pg_rider())
            self.__condeq.update(Parmset.condeq())
            self.__MeqParm.update(Parmset.MeqParm())
            self.__solvegroup.update(Parmset.solvegroup())
            self.__plot_color.update(Parmset.plot_color())
            self.__plot_style.update(Parmset.plot_style())
            self.__plot_size.update(Parmset.plot_size())
            self.__default_value.update(Parmset.default_value())
            self.history(append='updated from (not unsolvable): '+Parmset.oneliner())
        else:
            # A Parmset that is 'unsolvable' has no solvegroups.
            # However, its parmgroups might interfere with parmgroups
            # of the same name (e.g. Gphase) from solvable Parmsets.
            # Therefore, its parm info should NOT be copied here.
            self.history(append='not updated from (unsolvable): '+Parmset.oneliner())
        return True


#----------------------------------------------------------------------
#   methods used in saving/restoring the Parmset
#----------------------------------------------------------------------
    def clone(self):
        """clone self such that no NodeStubs are present. This 
           is needed to save the Parmset."""
        
        #create new Parmset
        newp=Parmset()
        newp.__unsolvable=self.__unsolvable
        newp.__parmtable=self.__parmtable
        newp.__quals=self.__quals
        newp.__parmgroup=self.__parmgroup
        newp.__pg_rider=self.__pg_rider
        newp.__condeq=self.__condeq
        newp.__solvegroup=self.__solvegroup
        newp.__plot_color=self.__plot_color
        newp.__plot_style = self.__plot_style
        newp.__plot_size = self.__plot_size
        # do not copy buffer
        newp.__node_groups=self.__node_groups
        # convert MeqParm to a dict of strings
        newp.__MeqParm={}
        for key in self.__MeqParm.keys():
             pgk=self.__MeqParm[key]
             if isinstance(pgk,Timba.TDL.TDLimpl._NodeStub):
               newp.__MeqParm[key]={'__type__':'nodestub','name':pgk.name}
             else:
               newp.__MeqParm[key]=pgk

        return newp

    def restore(self,oldp,ns):
        """ recreate the Parmset from a saved version 'oldp'"""
        self.__unsolvable=oldp.__unsolvable
        self.__parmtable=oldp.__parmtable
        self.__quals=oldp.__quals
        self.__parmgroup=oldp.__parmgroup
        self.__pg_rider=oldp.__pg_rider
        self.__condeq=oldp.__condeq
        self.__solvegroup=oldp.__solvegroup
        self.__plot_color=oldp.__plot_color
        self.__plot_style = oldp.__plot_style
        self.__plot_size = oldp.__plot_size
        # do not copy buffer
        self.__node_groups=oldp.__node_groups
        # recreate links to NodeStubs, which have to exist in the 
        # nodescope 'ns'
        self.__MeqParm={}
        mydict=oldp.__MeqParm
        for key in mydict.keys():
           pgk=mydict[key]
           if isinstance(pgk,dict):
               if pgk.has_key('__type__') and pgk['__type__']=='nodestub':
                   # look for canonical name
                   alist=string.split(pgk['name'],":q=")
                   #print alist
                   nodestub=None
                   if len(alist)==1:
                      nodestub=ns[alist[0]]
                      self.__MeqParm[pgk['name']]=nodestub
                   else:
                      wstr="nodestub=ns."+alist[0]+"(q='"+alist[1]+"')"
                      exec wstr
                      self.__MeqParm[pgk['name']]=nodestub

 

#===========================================================================================
#===========================================================================================
#===========================================================================================
#===========================================================================================

#===========================================================================================
# Copied from MG_JEN_funklet.py
#===========================================================================================


#-------------------------------------------------------------------------------------
# Make a 'standard' freq-time polc with the following features:
# - fdeg and tdeg give the polynomial degree in these dimensions
# - the constant coeff (c00) is specified explicitly
# - the other coeff are generated with an algorithm:
#   - first they are all set to the same value (=scale)
#   - then they are 'attenuated' (more for higher-order coeff)
#   - their sign is alternated between -1 and 1
# - If stddev>0, a 'proportional' random number is added to each coeff

def polc_ft (c00=1, fdeg=0, tdeg=0, scale=1, mult=1/sqrt(10), stddev=0): 
 
   # If the input is a polc (funklet) already, just return it ......??
   if isinstance(c00, dmi_type('MeqFunklet')):
	return c00

   # Create a coeff array with the correct dimensions.
   # All coeff have the same value (=scale), see also below
   scale = float(scale)
   coeff = resize(array(scale), (tdeg+1,fdeg+1))

   # Multiply each coeff with sign*mult**(i+j)
   # If mult<1, this makes the higher-order coeff smaller
   sign = 1.0
   for i in range(tdeg+1):
      for j in range(fdeg+1):
         factor = mult**(i+j)                               # depends on polynomial degree                
         coeff[i,j] *= (sign*factor)                        # attenuate, and apply the sign
         if (i+j)==0: coeff[0,0] = c00                      # override the constant coeff c00
         if stddev > 0:
            # Optional: Add some gaussian scatter to the coeff value
            # NB: If stddev=0, the coeff values are fully predictable!
            coeff[i,j] += gauss(0.0, stddev*factor)         # add 'proportional' scatter,    
         sign *=-1                                          # negate the sign for the next coeff                                 

  # NB: Should we set the lower-right triangle coeff to zero?  

  # Make the polc:
   polc = meq.polc(coeff)
   return polc


# NB: The polcs generated with this function are given to MeqParms as default funklets.
#     This is their ONLY use....
#     However, the MeqParm default funklets are used if no other funklets are known.
#     When used, their domains are ignored: It is assumed that their coeff are valid
#     for the requested domain, which may be anything....
#     So: It  might be reasonable to demand that MeqParms default funklets are c00 only!?
#     However: If the requested domain is automatically scaled back to (0-1) (under what
#              conditions?), the polc_ft() should be tested with requested domain (0-1)
#     After all, it IS nice to be able to make a (t,f) variable MeqParm.......



#======================================================================
# Make a polclog for a freq-dependent spectral index:
#======================================================================

# regular polc (comparison): v(f,t) = c00 + c01.t + c10.f + c11.f.t + ....
#
# polclog:
#            I(f) = I0(c0 + c1.x + c2.x^2 + c3.x^3 + .....)
#            in which:  x = 10log(f/f0)
#
# if c2 and higher are zero:           
#            I(f) = 10^(c0 + c1.10log(f/f0)) = (10^c0) * (f/f0)^c1
#                 = I0 * (f/f0)^SI  (classical spectral index formula)
#            in which: c0 = 10log(I0)  and c1 is the classical S.I. (usually ~0.7)   
#
# so:        I(f) = 10^SIF
# NB: If polclog_SIF is to be used as multiplication factor for (Q,U,V),
#     use: fmult = ns.fmult() << Meq.Parm(polclog(SI, I0=1.0), i.e. SIF[0] = 0.0)



def polclog_SIF (I0=1.0, SI=-0.7, f0=1e6):
   SIF = [log(I0)/log(10)]                               # SIF[0] = 10log(I0). (Python log() is e-log)
   # NB: what if I0 is polc???
   if not isinstance(SI, list): SI = [SI]
   SIF.extend(SI)                                             # NB: SIF[1] = classical S.I.
   SIF = array(SIF)
   SIF = reshape(SIF, (1,len(SIF)))               # freq coeff only....
   polclog = meq.polclog(SIF)                        # NB: the default f0 = 1Hz!
   polclog.axis_list = record(freq=f0)                # the default is f0=1Hz
   # print oneliner(polclog, 'polclog_SIF')
   return polclog

#    if len(SI) == 1:
#       print type(ns)
#       parm['I0'] = (ns.I0(q=pp['name']) << Meq.Parm(pp['I0']))
#       parm['SI'] = (ns.SI(q=pp['name']) << Meq.Parm(pp['SI']))
#       freq = (ns.freq << Meq.Freq())
#       fratio = (ns.fratio(q=pp['name']) << (freq/pp['f0']))
#       fmult = (ns.fmult(q=pp['name']) << Meq.Pow(fratio, parm['SI']))
#       iquv[n6.I] = (ns[n6.I](q=pp['name']) << (parm['I0'] * fmult))


#---------------------------------------------------------------------
# Make a StokesI(q=source) node based on a polclog:

def polclog_flux (ns, source=None, I0=1.0, SI=-0.7, f0=1e6, stokes='stokesI'):
   # print
   # source = MG_JEN_forest_state.autoqual('MG_JEN_funklet_flux', qual=source)
   uniqual = _counter('polclog_flux', increment=-1)

   polclog = polclog_predefined(source, I0=I0, SI=SI, f0=f0, stokes=stokes)
   SIF = ns['SIF_'+stokes](q=source) << Meq.Parm(polclog)
   node = ns[stokes](q=source) << Meq.Pow(10.0, SIF)
   # print '** polclog_flux(',source,') ->',SIF,'->',node
   return node

#---------------------------------------------------------------------
# Make a fmult(q=source) node based on a polclog:
# This may be used to multiply StokesQ,U,V.....

def polclog_fmult (ns, source=None, SI=-0.7, f0=1e6):
   source = MG_JEN_forest_state.autoqual('MG_JEN_funklet_fmult', qual=source)
   uniqual = _counter('polclog_fmult', increment=-1)
      
   # polclog = polclog_predefined(source, I0=1.0, SI=SI, f0=f0, stokes='stokesI')
   # def polclog_predefined (source='<source>', SI=-0.7, I0=1.0, f0=1e6, stokes='stokesI'):
      # polclog['stokesI'] = polclog_SIF (SI=SI, I0=I0, f0=f0)
      # return polclog[stokes]

   polclog = polclog_SIF (SI=SI, I0=I0, f0=f0)

   SIF = ns.SIF(q=source) << Meq.Parm(polclog)
   node = ns.mult(q=source) << Meq.Pow(10.0, SIF)
   # node = ns << Meq.Pow(10.0, SIF)               # <--- better?
   # print '** polclog_fmult(',source,') ->',SIF,'->',node
   return node




#========================================================================
# Helper routines:
#========================================================================

# Counter service (use to automatically generate unique node names)

_counters = {}

def _counter (key, increment=0, reset=False, trace=True):
    global _counters
    _counters.setdefault(key, 0)
    if reset: _counters[key] = 0
    _counters[key] += increment
    if trace: print '** Parmset: _counters(',key,') =',_counters[key]
    return _counters[key]






#========================================================================
# Test routine:
#========================================================================

if __name__ == '__main__':
    print '\n*******************\n** Local test of: TDL_Parmset.py:\n'
    from numarray import *
    from Timba.Trees import TDL_display
    from Timba.Trees import TDL_Joneset
    from Timba.Contrib.JEN import MG_JEN_funklet
    # from Timba.Trees import JEN_record
    ns = NodeScope()
    nsim = ns.Subscope('_')
    
    # stations = range(3)
    ps = Parmset(label='initial', polrep='circular')
    ps.display('initial')

    if 0:
        print '** dir(ps) ->',dir(ps)
        print '** ps.__doc__ ->',ps.__doc__
        print '** ps.__str__() ->',ps.__str__()
        print '** ps.__module__ ->',ps.__module__
        print

    if 0:
        ps.parmtable('xxx')

    if 0:
        print ps.parmtable('cal_BJones')
        print ps.check_parmtable_extension()


    if 1:
        # Create a Joneset object
        pp = dict(stations=range(3), c00_Gampl=1.0, c00_Gphase=0.0)
        js = TDL_Joneset.Joneset(label='test', **pp)
        js.display()
        js.Parmset.display()
    
    if 1:
        # Register the parmgroups:
        a1 = js.parmgroup('Gampl', ipol=1, color='red', style='diamond', size=10, corrs='paral1')
        a2 = js.parmgroup('Gampl', ipol=2, color='blue', style='diamond', size=10, corrs='paral2')
        p1 = js.parmgroup('Gphase', ipol=1, color='magenta', style='diamond', size=10, corrs='paral1')
        p2 = js.parmgroup('Gphase', ipol=2, color='cyan', style='diamond', size=10, corrs='paral2')

        # MeqParm node_groups: add 'G' to default 'Parm':
        js.Parmset.node_groups('G')

        # Define extra solvegroup(s) from combinations of parmgroups:
        js.Parmset.define_solvegroup('GJones', [a1, p1, a2, p2])
        js.Parmset.define_solvegroup('Gpol1', [a1, p1])
        js.Parmset.define_solvegroup('Gpol2', [a2, p2])
        js.Parmset.define_solvegroup('Gampl', [a1, a2])
        js.Parmset.define_solvegroup('Gphase', [p1, p2])
    
        for station in pp['stations']:
            skey = TDL_radio_conventions.station_key(station)        
            # Define station MeqParms (in ss), and do some book-keeping:  
            qual = dict(s=skey)
            for Gampl in [a1,a2]:
                default = MG_JEN_funklet.polc_ft (c00=pp['c00_Gampl'])
                js.Parmset.define_MeqParm (ns, Gampl, qual=qual, default=default)

            for Gphase in [p1,p2]:
                default = MG_JEN_funklet.polc_ft (c00=pp['c00_Gphase'])
                js.Parmset.define_MeqParm (ns, Gphase, qual=qual, default=default)

        ps = js.Parmset
        ps.define_condeq(p1, unop='Add', value=0.0)
        ps.define_condeq(p2, unop='Add', value=0.0)
        ps.define_condeq(a1, unop='Multiply', value=1.0)
        ps.define_condeq(a2, unop='Multiply', value=1.0)
        ps.define_condeq(p1, select='first', value=0.0)
        ps.display(full=True)

    if 0:
        for key in ps.condeq().keys():
            condeq = ps.make_condeq(ns, key)
            TDL_display.subtree(condeq, key, full=True, recurse=5)

    if 0:
        print
        for key in ps.parmgroup().keys():
            print '- parmgroup:',key,':',ps.parmgroup(key)
        print

    if 0:
        print
        for key in ps.solvegroup().keys():
            print '- solvegroup:',key,':',ps.solvegroup(key)
        print

    if 0:
        print
        for sg in ps.solvegroup().keys():
            ps.sg_rider(sg, key='condeq_corrs', trace=True)
        print

    if 0:
        select = '*'
        # select = 'first'
        # select = 'last'
        for key in ps.solvegroup().keys():
            ps.solveparm_names(key, select=select, trace=True)
            ps.solveparm_nodes(key, select=select, trace=True)
        print
        
    if 0:
        select = '*'
        # select = 'first'
        select = 'last'
        for key in ps.parmgroup().keys():
            ps.parm_names(key, select=select, trace=True)
            ps.parm_nodes(key, select=select, trace=True)
        print
        

    if 0:
        # Display the final result:
        # k = 0 ; TDL_display.subtree(ps[k], 'ps['+str(k)+']', full=True, recurse=3)
        ps.display('final result')

    print '\n*******************\n** End of local test of: TDL_Parmset.py:\n'




#============================================================================================









 

