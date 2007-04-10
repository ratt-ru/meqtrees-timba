# file: ../Grunt/display_subtree.py

from copy import deepcopy

#=======================================================================

def subtree (node, txt=None, level=1,
             done=None, skip_duplicate=True,
             skip_line_before=True,
             skip_line_after=True,
             show_initrec=True, recurse=1000):
    """Helper function to display a subtree (under node) recursively"""


    if level==1:
        if skip_duplicate: done = dict()
        if skip_line_before: print
    prefix = '  '
    if txt==None: txt = node.name               #........?
    if txt: prefix += ' ('+str(txt)+')'
    prefix += level*'..'
    s = prefix
    s += ' '+str(node.classname)+' '+str(node.name)

    if skip_duplicate:
        if done.has_key(node.name):
            done[node.name] += 1
            print s,'... see above ... (',done[node.name],')'
            return True

    if show_initrec:
        initrec = deepcopy(node.initrec())
        # if len(initrec.keys()) > 1:
        hide = ['name','class','defined_at','children','stepchildren','step_children']
        for field in hide:
            if initrec.has_key(field): initrec.__delitem__(field)
            if initrec.has_key('value'):
                value = initrec.value
                # if isinstance(value,(list,tuple)):
                #     initrec.value = value.flat
            if initrec.has_key('default_funklet'):
                coeff = initrec.default_funklet.coeff
                initrec.default_funklet.coeff = [coeff.shape,coeff.flat]
        if len(initrec)>0: s += ' '+str(initrec)
    print s

    if skip_duplicate:
        done.setdefault(node.name, 0)
        done[node.name] += 1

    if recurse>0:
        # print dir(node)
        # print node.__doc__
        if node.initialized():
            for child in node.children:
                subtree (child[1], txt=txt, level=level+1, done=done,
                         show_initrec=show_initrec, recurse=recurse-1)
    if level==1:
        if skip_line_after: print
    return True


    
#=======================================================================
