# MXM_polynomials.py:

# A Solver Tree with on the one side a Parm with a polc and on the other side
# The polc written out as a tree

 
#********************************************************************************
# Initialisation:
#********************************************************************************

from Timba.TDL import *
from Timba.Meq import meq

Settings.forest_state.cache_policy = 100
Settings.forest_state.bookmarks = []


def _define_forest (ns, **kwargs):
    solvables=[];
    polc_tree = make_polc_tree(ns,[3,2],parm_list=solvables,label="polc_tree")
    polc_tree_name=polc_tree.name;
    
    ft_32=[[1,2],[3,4],[5,0]]; # the coefficients of the Polc
    ns.cdq<<Meq.condeq(polc_tree,
        ns.parm<<Meq.Parm(ft_32,node_groups='Parm'));

    ns.solver<<Meq.Solver(ns.cdq,
                          num_iter=10,
                          solvable=solvables,
                          epsilon=1e-4,
                          last_update=True);

    # When running the script, first display the bookmarks, since some of the nodes wont have a result cached after the run
    bm = record(name='result',page=
                [ record(viewer='Result Plotter',udi='/node/parm', publish=True, pos=(0,0)),
                  record(viewer='Result Plotter',udi='/node/'+polc_tree_name, publish=True, pos=(0,1)),
                  record(viewer='Result Plotter',udi='/node/cdq', publish=True, pos=(1,0)),
                  record(viewer='Result Plotter',udi='/node/solver', publish=True, pos=(1,1))
                  ])
    Settings.forest_state.bookmarks.append(bm)
    
    
def _tdl_job_execute (mqs, parent):
    """Execute the solver"""
    domain = meq.domain(1,10,1,10)                            # (f1,f2,t1,t2)
    cells = meq.cells(domain, num_freq=10, num_time=11)
    request = meq.request(cells, rqtype='ev')
    result = mqs.meq('Node.Execute',record(name='solver', request=request))
    return result


 
#********************************************************************************
# Help functions
#********************************************************************************


def make_polc_tree(ns,shape=[1,1],parm_list=[],label=''):
    """make tree for polynomial, to compare with direct polc,
    returns tree root + list of parms""" 
    if len(shape)==1:
        shape.append(1);
    old_root=None;
    time=None;
    freq=None;
    
    max_order = max(2,max(shape[0]-1,shape[1]-1)); 
    for t in range(shape[0]):
        for f in range(shape[1]):
            #rank in time and freq
            revt=shape[0]-t-1;
            revf=shape[1]-f-1;
            #ignore triangle, i.e. coeffs Cnm with n+m > max(n,m)
            if (revt+revf) > max_order :
                continue;
            #create the leave nodes - Parms
            mult = ns.c(label,t=str(revt),f=str(revf)) << Meq.Parm(0.,node_groups='Parm');
            # create time node
            if not time and revt>0:
                time=ns.time<<Meq.Time();
            # create freq node
            if not freq and revt>0:
                freq=ns.freq<<Meq.Freq();
                
            if revt > 0 or revf > 0:
                mult = Meq.Multiply(ns.c(label,t=str(revt),f=str(revf)),power_tf(revt,revf,time,freq))
            new_root=mult;
            if old_root:
                new_root = ns.add(label,t=str(revt),f=str(revf))<<Meq.Add(mult,old_root);
            old_root =new_root;
            parm_list.append( ns.c(label,t=str(revt),f=str(revf)).name);
    return old_root;

def power_tf(t =0,f=0, time=None, freq=None):
    """ creates power nodes of freq/time"""
        
    powft=None;
    for i in range(t):
        if powft:
            powft=powft*time;
        else:
            powft=time;
    for i in range(f):
        if powft:
            powft=powft*freq;
        else:
            powft=freq;
    return powft;
