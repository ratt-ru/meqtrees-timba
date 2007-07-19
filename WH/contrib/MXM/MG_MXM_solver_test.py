# standard preamble
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
from math import *
# Timba.TDL.Settings.forest_state is a standard TDL name. 
# This is a record passed to Set.Forest.State. 
Settings.forest_state.cache_policy = 100;

# Make sure our solver root node is not cleaned up
Settings.orphans_are_roots = True;

#some defaults
def_eps=1e-4; #epsilon
def_lup=False;#last_update
def_niter=20; # number of iterations
def_tiling=record(freq=1)


solver_list=[];
cd_list=[];
# default 'measured' arrays:
#
c00=10;
t_2=[[1],[2]];
f_2=[[1,2]];
ft_22=[[1,2],[3,4]]
ft_23=[[1,2,3],[4,5,0]];
ft_23noise=[[0,0,0],[0,0,.1]];
ft_32=[[1,2],[3,4],[5,0]];
ft_32noise=[[0,0],[0,0],[0,.1]];
ft_33=[[1,2,3],[4,5,0],[6,0,0]];
ft_33noise=[[0,0,0],[0,0,0],[0,0,.1]];



def _define_forest(ns):
    """Several test on the solver, increasing complexity"""
    #simple test, 2 math. equal trees, one with two parms tthe other written out
    ns.cd11<<Meq.Condeq((ns.c11<<Meq.Parm(make_polc([3,2]),node_groups='Parm',tiling=def_tiling)),Meq.Parm(ft_32));

    ns.solver11<<Meq.Solver(ns.cd11,num_iter=def_niter,debug_level=10,solvable=["c11"],epsilon=def_eps,last_update=def_lup)

    solver_list.append('solver11');
    cd_list.append('cd11');

    solvables=[];
    ns.cd12<<Meq.condeq(make_pol_tree(ns,[3,2],parm_list=solvables,label="cd12"),Meq.Parm(ft_32));
    ns.solver12<<Meq.Solver(ns.cd12,num_iter=def_niter,debug_level=10,solvable=solvables,epsilon=def_eps,last_update=def_lup);
    
    solver_list.append('solver12');
    cd_list.append('cd12');

    # same with  an extra solvable parm.. to make the rank drop
    ns.cd121<<Meq.Condeq(((ns.c121<<Meq.Parm(make_polc([3,2]),node_groups='Parm',tiling=def_tiling))
                          +(ns.extra121<<Meq.Parm(0,node_groups='Parm',tiling=def_tiling))),
                          Meq.Parm(ft_32));
    ns.solver121<<Meq.Solver(ns.cd121,num_iter=def_niter,debug_level=10,solvable=["c121","extra121"],epsilon=def_eps,last_update=def_lup)

    solver_list.append('solver121');
    cd_list.append('cd121');

    
    solvables=[];
    ns.cd122<<Meq.condeq((make_pol_tree(ns,[3,2],solvables,"cd122")+(ns.extra122<<Meq.Parm(0,node_groups='Parm',tiling=def_tiling))),
                         Meq.Parm(ft_32));
    solvables.append('extra122');
    ns.solver122<<Meq.Solver(ns.cd122,num_iter=def_niter,debug_level=10,solvable=solvables,epsilon=def_eps,last_update=def_lup)
    solver_list.append('solver122');
    cd_list.append('cd122');

    # same with  noise
    ns.cd21<<Meq.Condeq((ns.c21<<Meq.Parm(make_polc([3,2]),node_groups='Parm',tiling=def_tiling)),(Meq.Parm(ft_32)+Meq.Parm(ft_32noise)));
    ns.solver21<<Meq.Solver(ns.cd21,num_iter=def_niter,debug_level=10,solvable=["c21"],epsilon=def_eps,last_update=def_lup)

    solver_list.append('solver21');
    cd_list.append('cd21');

    
    solvables=[];
    ns.cd22<<Meq.condeq(make_pol_tree(ns,[3,2],solvables,"cd22"),(Meq.Parm(ft_32)+Meq.Parm(ft_32noise)));
    ns.solver22<<Meq.Solver(ns.cd22,num_iter=def_niter,debug_level=10,solvable=solvables,epsilon=def_eps,last_update=def_lup)
    solver_list.append('solver22');
    cd_list.append('cd22');


    # same with  noise and an extra solvable parm.. to make the rank drop
    ns.cd221<<Meq.Condeq(((ns.c221<<Meq.Parm(make_polc([3,2]),node_groups='Parm',tiling=def_tiling))
                          +(ns.extra221<<Meq.Parm(0,node_groups='Parm',tiling=def_tiling))),
                          (Meq.Parm(ft_32)+Meq.Parm(ft_32noise)));
    ns.solver221<<Meq.Solver(ns.cd221,num_iter=def_niter,debug_level=10,solvable=["c221","extra221"],epsilon=def_eps,last_update=def_lup)

    solver_list.append('solver221');
    cd_list.append('cd221');

    
    solvables=[];
    ns.cd222<<Meq.condeq((make_pol_tree(ns,[3,2],solvables,"cd222")+(ns.extra222<<Meq.Parm(0,node_groups='Parm',tiling=def_tiling))),
                         (Meq.Parm(ft_32)+Meq.Parm(ft_32noise)));
    solvables.append('extra222');
    ns.solver222<<Meq.Solver(ns.cd222,num_iter=def_niter,debug_level=10,solvable=solvables,epsilon=def_eps,last_update=def_lup)
    solver_list.append('solver222');
    cd_list.append('cd222');



    #introduce extra nodes for testing, eg.
    #real + imag
    ns.cd31<<Meq.Condeq(Meq.ToComplex(ns.c31_real<<Meq.Parm(make_polc([3,2]),node_groups='Parm',tiling=def_tiling),ns.c31_imag<<Meq.Parm(make_polc([3,2]),node_groups='Parm',tiling=def_tiling)),
                        Meq.ToComplex((Meq.Parm(ft_32)+Meq.Parm(ft_32noise)),(Meq.Parm(ft_32)+Meq.Parm(ft_32noise))))
    ns.solver31<<Meq.Solver(ns.cd31,num_iter=def_niter,debug_level=10,solvable=["c31_real","c31_imag"],epsilon=def_eps,last_update=def_lup)
    solver_list.append('solver31');
    cd_list.append('cd31');

    solvables=[];
    ns.real<<make_pol_tree(ns,[3,2],solvables,"cd32_real");
    ns.imag<<make_pol_tree(ns,[3,2],solvables,"cd32_imag");
    ns.cd32<<Meq.Condeq(Meq.ToComplex(ns.real,ns.imag),Meq.ToComplex((Meq.Parm(ft_32)+Meq.Parm(ft_32noise)),(Meq.Parm(ft_32)+Meq.Parm(ft_32noise))))
    ns.solver32<<Meq.Solver(ns.cd32,num_iter=def_niter,debug_level=10,solvable=solvables,epsilon=def_eps,last_update=def_lup)
    solver_list.append('solver32');
    cd_list.append('cd32');


    #introduce tensor nodes
    mat22m=Meq.Matrix22(Meq.ToComplex((Meq.Parm(ft_32)+Meq.Parm(ft_32noise)),(Meq.Parm(ft_32)+Meq.Parm(ft_32noise))),0,0,Meq.ToComplex((Meq.Parm(ft_32)+Meq.Parm(ft_32noise)),(Meq.Parm(ft_32)+Meq.Parm(ft_32noise))));
    mat22p = Meq.Matrix22(Meq.Tocomplex(ns.c41_real1<<Meq.Parm(make_polc([3,2]),node_groups='Parm',tiling=def_tiling),ns.c41_imag1<<Meq.Parm(make_polc([3,2]),node_groups='Parm',tiling=def_tiling)),0,0,
                          Meq.Tocomplex(ns.c41_real2<<Meq.Parm(make_polc([3,2]),node_groups='Parm',tiling=def_tiling),ns.c41_imag2<<Meq.Parm(make_polc([3,2]),node_groups='Parm',tiling=def_tiling)))

    ns.cd41<<Meq.Condeq(mat22p,mat22m);
    ns.solver41<<Meq.Solver(ns.cd41,num_iter=def_niter,debug_level=10,solvable=["c41_real1","c41_imag1","c41_real2","c41_imag2"],epsilon=def_eps,last_update=def_lup);
    solver_list.append('solver41');
    cd_list.append('cd41');


    solvables=[];
    ns.real1<<make_pol_tree(ns,[3,2],solvables,"cd42_real1");
    ns.imag1<<make_pol_tree(ns,[3,2],solvables,"cd42_imag1");
    ns.real2<<make_pol_tree(ns,[3,2],solvables,"cd42_real2");
    ns.imag2<<make_pol_tree(ns,[3,2],solvables,"cd42_imag2");

    mat22p=Meq.Matrix22(Meq.ToComplex(ns.real1,ns.imag1),0,0,Meq.ToComplex(ns.real2,ns.imag2))
    ns.cd42<<Meq.Condeq(mat22p,mat22m);    
    ns.solver42<<Meq.Solver(ns.cd42,num_iter=def_niter,debug_level=10,solvable=solvables,epsilon=def_eps,last_update=def_lup)
    solver_list.append('solver42');
    cd_list.append('cd42');

    rs_children=[];
    def_solver_page='solvers';
    solver_page=def_solver_page
    n=0;
    np=1;
    for solvername in solver_list:
        n=n+1;
        if n>4:
            np=np+1;
            solver_page=def_solver_page+str(np);
            n=1;
        make_bookmark(ns[solvername],page=solver_page)
        rs_children.append(ns[solvername]);
    ns.reqseq<<Meq.ReqSeq(children=rs_children);
    def_cd_page='condeqs'
    cd_page=def_cd_page;
    n=0;
    np=1;
    for cdname in cd_list:
        n=n+1;
        if n>4:
            np=np+1;
            cd_page=def_cd_page+str(np);
            n=1;
        make_bookmark(ns[cdname],page=cd_page)

def _test_forest (mqs,parent):
  """test_forest() is a standard TDL name. When a forest script is
  loaded by, e.g., the browser, and the "test" option is set to true,
  this method is automatically called after define_forest() to run a 
  test on the forest. The 'mqs' argument is a meqserver proxy object.
  """;
  cells = meq.cells(meq.domain(0,1,0,1),num_freq=10,num_time=10);
  request = meq.request(cells,eval_mode=1);
  #  for solvername in solver_list:
  #      mqs.meq('Node.Execute',record(name=solvername,request=request),wait=True);
  mqs.meq('Node.Execute',record(name='reqseq',request=request),wait=True);

def make_polc(shape=[1,1]):
    """make polc filled with 0"""
    if len(shape)==1:
        shape.append(1);
    pa=[];
    for i in range(shape[0]):
        pa.append([0.])
        for j in range(shape[1]-1):
            pa[i].append(0.)

    return meq.polc(pa);


def make_pol_tree(ns,shape=[1,1],parm_list=[],label=''):
    """make tree for polynomial, to compare with direct polc,
    returns tree root + list of parms""" 
    if len(shape)==1:
        shape.append(1);
    old_root=None;
    
    max_order = max(2,max(shape[0]-1,shape[1]-1)); 
    for t in range(shape[0]):
        for f in range(shape[1]):
            revt=shape[0]-t-1;
            revf=shape[1]-f-1;
            #ignore triangle
            if (revt+revf) > max_order :
                continue;
            mult = ns.c(label,t=str(revt),f=str(revf)) << Meq.Parm(0.,node_groups='Parm',tiling=def_tiling);
            if revt > 0 or revf > 0:
                mult = Meq.Multiply(ns.c(label,t=str(revt),f=str(revf)),power_tf(revt,revf))
            new_root=mult;
            if old_root:
                new_root = Meq.Add(mult,old_root);
            old_root =new_root;
            parm_list.append( ns.c(label,t=str(revt),f=str(revf)).name);
    return old_root;

def power_tf(t,f):
    """ creates power nodes of freq/time"""
    powft=None;
    for i in range(t):
        if powft:
            powft=powft*Meq.Time();
        else:
            powft=Meq.Time();
    for i in range(f):
        if powft:
            powft=powft*Meq.Freq();
        else:
            powft=Meq.Freq();
    return powft;


def make_bookmark(node=None, page=None, viewer='Result Plotter'):
  """define bookmark/page"""
  Settings.forest_state.setdefault('bookmarks',[])
  bms = Settings.forest_state.bookmarks
  bm = record(viewer=viewer, publish=True,name=node.name,udi='/node/'+node.name)  
  if not page==None:
    found=False;
    for i in range(len(bms)):
      if bms[i].has_key('page'):
        if bms[i].name == page:
          found = True;                                   
          n=len(bms[i].page) 
          gr_sz=int(sqrt(n))+1;
           
          if n<(gr_sz*(gr_sz-1)):
                rownr=gr_sz-1;
                colnr=0;
                if rownr>0:
                      colnr=n%(rownr*(gr_sz-1))
          else:
                colnr=gr_sz-1;
                rownr=0;
                if colnr>0:
                      rownr=n%(colnr*gr_sz);
                
          bm.pos=(rownr,colnr);
          
          bms[i].page.append(bm)
          break;
    if not found:
      bm.pos=[0,0];
      bms.append(record(name=page, page=[bm]))
  else:
    bms.append(bm);
  Settings.forest_state.bookmarks=bms;
  
# this is the testing branch, executed when the script is run directly
# via 'python script.py'

if __name__ == '__main__':
#  from Timba.Meq import meqds 
  Timba.TDL._dbg.set_verbose(5);
  ns = NodeScope();
  _define_forest(ns);
  # resolves nodes
  ns.Resolve();

