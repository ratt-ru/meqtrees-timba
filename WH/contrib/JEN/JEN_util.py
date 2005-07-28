# ../Timba/PyApps/test/JEN_util.py:  
#   JEN Python utility scripts


  
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

def JEN_history (rr, name='<name>', item=0, error=0, warning=0,
                 level=3, show=0, trace=1):
  indent = level*'..'
  s1 = 'JEN_history ('+name+'):'
  hkey = '_history'

  if not rr.has_key(hkey):
    rr[hkey] = dict(log={}, error={}, warning={})

  if isinstance(item, str):
    if not rr[hkey].has_key('log'): rr.history['log'] = {}
    s = indent+str(item)
    if trace: print s1,s
    n = len(rr[hkey]['log'])
    rr[hkey]['log'][n] = s

  if isinstance(error, str):
    if not rr[hkey].has_key('error'): rr.history['error'] = {}
    s = '** ERROR ** '+indent+str(error)
    n = len(rr[hkey]['error'])
    print s1,s
    rr[hkey]['error'][n] =s

  if isinstance(warning, str):
    if not rr[hkey].has_key('warning'): rr.history['warning'] = {}
    s = '** WARNING ** '+indent+str(warning)
    n = len(rr[hkey]['warning'])
    print s1,s
    rr[hkey]['warning'][n] = s

  if show:
    JEN_display (rr[hkey], name, 'JEN_history')
  return rr


#=======================================================================
# Display any Python object(v):

def JEN_display (v, name='<name>', txt='', full=0, indent=0):
  if indent==0: print '\n** display of Python object:',name,': (',txt,'):'
  print '**',indent*'.',name,':',
    
  if isinstance(v, (str, list, dict, tuple)):
    # sizeable types (otherwise, len(v) gives an error):
    slen = '['+str(len(v))+']'

    if isinstance(v, str):
      print 'str',slen,
      print '=',v
      
    elif isinstance(v, list):
      # for i in range(len(v)):
        # print '- list item',i,':',type(v[i])
        # print v[i].__class__, (v[i].__class__ == <class 'Timba.dmi.record'>)
        # print dir(v[i])
      print 'list',slen,
      if len(v) == 1:
        print '=',[v[0]]
      elif len(v) < 5:
        print '=',v
      else:
        print '=',[v[0],'...',v[len(v)-1]]

    elif isinstance(v, tuple):
      print 'tuple',slen,
      print '=',v
          
    elif isinstance(v, dict):
      print 'dict',slen,':'
      keys = v.keys()
      n = len(keys)
      types = {}
      for key in keys: types[type(v[key])] = 1
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
    rr = {}
    JEN_history(rr, item='item1', trace=1)
    JEN_history(rr, item='item2', trace=1)
    JEN_history(rr, error='item3')
    JEN_history(rr, warning='item3')
    JEN_history(rr, item='item3', trace=1)
    JEN_history(rr, show=1)

  if 0:
    dd = dict(y=[56], o=89)
    aa = dict(a=range(3), b='xxx', cc=['aa','bb'], d=[2], e=dd)
    JEN_display(aa, 'aa')

  if 0:
    pp = JEN_pp(dict(d=56), _help=dict(a=5), a=1, b=2, c='g', trace=1)
    # pp = JEN_pp(a=1, b=2, c='g')
    JEN_display(pp, 'pp', txt='outside')

  print '\n*** End of test of JEN_util.py:\n' 

