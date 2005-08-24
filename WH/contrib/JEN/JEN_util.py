# ../Timba/WH/contrib/JEN/JEN_util.py:  
#   JEN Python utility scripts

print '\n',100*'*'
print '** JEN_util.py    h30jul/h08aug2005'

from Timba.TDL import *
  
#=======================================================================
# Deal with input arguments (opt):

def JEN_pp (pp={}, _funcall='<funcall>', _help={}, _prompt={}, **default):

    # Create missing fields in pp with the default values given in **default:
    for key in default.keys():
        if not pp.has_key(key): pp[key] = default[key]

    # Identifying info:
    pp['_funcall'] = _funcall
    
    # Eventually, this record may evolve into a input GUI:
    # NB: This field appears to be dropped in pp = record(pp)....?
    # print '_help =',_help
    if len(_help) > 0: pp['_help'] = _help
    if len(_prompt) > 0: pp['_prompt'] = _prompt

    # Make sure of some default fields:
    if not pp.has_key('trace'):
        pp['trace'] = 0
        if pp.has_key('_help'): pp['_help']['trace'] = 'if >0, trace execution'

    if pp['trace']: JEN_display(pp, 'pp', txt='exit of JEN_pp()')
    return pp

#-----------------------------------------------------------------------------------------
# use: if no arguments, return JEN_pp_noexec(pp)
# NB: After record(JEN_pp()), _help etc have disappeared.....!

def JEN_pp_noexec (pp={}, txt='JEN_util.JEN_pp_noexec(pp)', trace=0):
    if trace: JEN_display(pp, 'pp', txt=txt)
    return pp



#========================================================================================
# Append an log/error/warning message to the given dict/record

def JEN_history_new (rr=0, *item, **pp):
    
    # Deal with input parameters (pp):
    if True:
        pp.setdefault('error', False)           # if True, an error has occured
        pp.setdefault('warning', False)         # if True, issue a warning
        pp.setdefault('show', False)            # if True, show the accumulated history
        pp.setdefault('level', 1)               # indentation level
        pp.setdefault('hkey', '_history')       # field-name in rr
        pp.setdefault('htype', 'dict')          # if record, fill a record
        pp.setdefault('trace', True)            # if True, 
        pp = record(pp)
    else:
        pp = record(JEN_pp (pp, 'WSRT_coh::coh_solver(ns, **pp)',
                            _help=dict(error='if True, an error has occured',
                                       warning='if True, issue a warning',
                                       show='if True, show the accumulated history',
                                       hkey='field-name in rr',
                                       htype='if record, fill a record',
                                       level='indentation level'),
                            error=False, warning=False, show=False,
                            level=1, hkey='_history', htype='dict')) 
        if isinstance(rr, int): return JEN_pp_noexec(pp, trace=pp.trace)
    
    print '\n pp =',pp
    print '*item =',type(item),len(item),item
    print 'str(item) =',str(item)
    # return
    
    indent = pp.level*'..'
    if not isinstance(pp.hkey, str): pp.hkey = '_history'
    s1 = '** '+pp.hkey+':'

    if not rr.has_key(pp.hkey):
        if pp.htype=='record':
            rr[pp.hkey] = record(log=record(), ERROR=record(), WARNING=record())
        else:
            rr[pp.hkey] = dict(log={}, ERROR={}, WARNING={})

    if isinstance(item, str):
        s = indent+str(item)
        if trace: print s1,s
        n = len(rr[pp.hkey]['log'])
        rr[hkey]['log'][n] = s

    if isinstance(pp.error, str):
        s2 = ' ** ERROR ** '
        s = indent+str(pp.error)
        n = len(rr[pp.hkey]['ERROR'])
        print s1,s2,s
        rr[hkey]['ERROR'][n] = s
        n = len(rr[pp.hkey]['log'])
        rr[hkey]['log'][n] = s+s2

    if isinstance(pp.warning, str):
        s2 = ' ** WARNING ** '
        s = indent+str(pp.warning)
        n = len(rr[pp.hkey]['WARNING'])
        print s1,s2,s
        rr[hkey]['WARNING'][n] = s
        n = len(rr[pp.hkey]['log'])
        rr[pp.hkey]['log'][n] = s+s2

    if pp.show:
        JEN_display (rr[pp.hkey], pp.hkey, pp.hkey)
    return rr

#========================================================================================
# Append an log/error/warning message to the given dict/record

def JEN_history (rr, item=0, error=0, warning=0, show=0, 
                     level=1, hkey='_history', htype='dict', trace=1):
    
    indent = level*'..'
    if not isinstance(hkey, str): hkey = '_history'
    s1 = '** '+hkey+':'

    if not rr.has_key(hkey):
        if htype=='record':
            rr[hkey] = record(log=record(), ERROR=record(), WARNING=record())
        else:
            rr[hkey] = dict(log={}, ERROR={}, WARNING={})

    if isinstance(item, str):
        s = indent+str(item)
        if trace: print s1,s
        n = len(rr[hkey]['log'])
        rr[hkey]['log'][n] = s

    if isinstance(error, str):
        s2 = ' ** ERROR ** '
        s = indent+str(error)
        n = len(rr[hkey]['ERROR'])
        print s1,s2,s
        rr[hkey]['ERROR'][n] = s
        n = len(rr[hkey]['log'])
        rr[hkey]['log'][n] = s+s2

    if isinstance(warning, str):
        s2 = ' ** WARNING ** '
        s = indent+str(warning)
        n = len(rr[hkey]['WARNING'])
        print s1,s2,s
        rr[hkey]['WARNING'][n] = s
        n = len(rr[hkey]['log'])
        rr[hkey]['log'][n] = s+s2

    if show:
        JEN_display (rr[hkey], hkey, hkey)
    return rr


#=======================================================================
# Display the contents of a given class

def JEN_display_class (klass, txt='<txt>', trace=1):
    print '\n***** Display of class(',txt,'):'
    print '** - klass.__class__ ->',klass.__class__
    rr = dir(klass)
    for attr in rr:
        v = klass[attr]
        print '** - ',attr,':',type(v),':',v
        v = eval('klass.'+attr)
        print '** - ',attr,':',type(v),':',v
    print '***** End of class\n'
    

#=======================================================================
# Display any Python object(v):

def JEN_display (v, name='<name>', txt='', full=0, indent=0):
    if indent==0: print '\n** display of Python object:',name,': (',txt,'):'
    print '**',indent*'.',name,':',
    
    if isinstance(v, (str, list, tuple, dict, record)):
        # sizeable types (otherwise, len(v) gives an error):
        vlen = len(v)
        slen = '['+str(vlen)+']'

        if isinstance(v, str):
            print 'str',slen,
            print '=',v
      
        elif isinstance(v, list):
            print 'list',slen,
            separate = False
            types = {}
            for i in range(vlen):
                stype = str(type(v[i]))
                types[stype] = 1
                s1 = stype.split(' ')
                if s1[0] == '<class': separate = True
                if isinstance(v[i], (dict, record)): separate = True
            if len(types) > 1: separate = True

            if separate:
                print ':'
                for i in range(vlen): JEN_display (v[i], '['+str(i)+']', indent=indent+2)
            elif vlen == 1:
                print '=',[v[0]]
            elif vlen < 5:
                print '=',v
            else:
                print '=',[v[0],'...',v[vlen-1]]

        elif isinstance(v, tuple):
            print 'tuple',slen,
            print '=',v
          
        elif isinstance(v, (dict, record)):
            if isinstance(v, record):
                print 'record',slen,':'
            elif isinstance(v, dict):
                print 'dict',slen,':'
            keys = v.keys()
            n = len(keys)
            types = {}
            for key in keys: types[str(type(v[key]))] = 1
            if len(types) > 1:
                for key in v.keys(): JEN_display (v[key], key, indent=indent+2)
            elif n < 10:
                for key in v.keys(): JEN_display (v[key], key, indent=indent+2)
            elif full:
                for key in v.keys(): JEN_display (v[key], key, indent=indent+2)
            else:
                for key in [keys[0]]: JEN_display (v[key], key, indent=indent+2)
                if n > 20:
                    print '**',(indent+2)*' ','.... (',n-2,'more fields of the same type )'
                else:
                    print '**',(indent+2)*' ','.... ( skipped keys:',keys[1:n-1],')'
                for key in [keys[n-1]]: JEN_display (v[key], key, full=full, indent=indent+2) 
        

        else: 
            print type(v),'=',v

    else: 
        # All other types:
        print type(v),'=',v

    if indent == 0: print



#=======================================================================
# Test function
#=======================================================================

if __name__ == '__main__':
    print '\n*** Start of test of JEN_util.py:' 
  
    if 0:
        ns = NodeScope()
        JEN_display_class(ns)

    if 1:
        rr = {}
        JEN_history_new (rr, 'item1', 'item2', 4, 5, show=True, trace=1)
        JEN_history_new (rr, show=True, trace=1)

    if 0:
        rr = {}
        JEN_history(rr, 'item1', trace=1)
        # JEN_history(rr, 'item2', level=2, trace=1)
        # JEN_history(rr, error='item3', level=3)
        # JEN_history(rr, warning='item4')
        # JEN_history(rr, 'item5', trace=1)
        # JEN_history(rr, show=1)

    if 0:
        dd = dict(y=[56], o=89)
        aa = dict(a=range(3), b='xxx', cc=['aa','bb'], d=[2], e=dd)
        JEN_display(aa, 'aa')

    if 0:
        pp = JEN_pp(dict(d=56), _help=dict(a=5), a=1, b=2, c='g', trace=1)
        # pp = JEN_pp(a=1, b=2, c='g')
        JEN_display(pp, 'pp', txt='outside')

    if 0:
        aa = record()
        print type(aa)
        # print isinstance(aa, dmi_type('Timba.dmi.record'))
        print isinstance(aa, dmi_type('MeqFunklet', record))

        # _funklet_type = dmi_type('MeqFunklet',record);
        # _polc_type = dmi_type('MeqPolc',_funklet_type);
        # _polclog_type = dmi_type('MeqPolcLog',_polc_type);
        # _domain_type = dmi_type('MeqDomain',record);
        # _cells_type = dmi_type('MeqCells',record);
        # _request_type = dmi_type('MeqRequest',record);

    print '\n*** End of test of JEN_util.py:\n' 

