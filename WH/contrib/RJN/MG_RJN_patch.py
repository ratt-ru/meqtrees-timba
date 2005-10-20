#!/usr/bin/python

########
## This script needs to be run in the MeqBrowser,

from Timba.Contrib.RJN import RJN_sixpack

import re
import math
import random

# for Bookmarks

from Timba.Contrib.JEN import MG_JEN_forest_state
from Timba.TDL import * 
from Timba.Meq import meq

# to force caching put 100
Settings.forest_state.cache_policy = 100

# List of source names
srcnames = []


########################################################
def _define_forest(ns):
 global srcnames   
 import math
    
 # please change this according to your setup
 home_dir = os.environ['HOME']
 infile_name = home_dir + '/LOFAR/Timba/WH/contrib/RJN/test_sources.txt'
 infile=open(infile_name,'r')
 #infile=open('3C343_nvss_small.txt','r')  
 all=infile.readlines()
 infile.close()

 # regexp pattern
 pp=re.compile(r"""
   ^(?P<col1>\S+)  # column 1 'NVSS'
   \s*             # skip white space
   (?P<col2>[A-Za-z]\w+\+\w+)  # source name i.e. 'J163002+631308'
   \s*             # skip white space
   (?P<col3>\d+)   # RA angle - hr 
   \s*             # skip white space
   (?P<col4>\d+)   # RA angle - min 
   \s*             # skip white space
   (?P<col5>\d+(\.\d+)?)   # RA angle - sec
   \s*             # skip white space
   (?P<col6>\d+(\.\d+)?)   # eRA angle - sec
   \s*             # skip white space
   (?P<col7>\d+)   # Dec angle - hr 
   \s*             # skip white space
   (?P<col8>\d+)   # Dec angle - min 
   \s*             # skip white space
   (?P<col9>\d+(\.\d+)?)   # Dec angle - sec
   \s*             # skip white space
   (?P<col10>\d+(\.\d+)?)   # eDec angle - sec
   \s*             # skip white space
   (?P<col11>\d+)   # freq
   \s*             # skip white space
   (?P<col12>\d+(\.\d+)?)   # brightness - Flux
   \s*             # skip white space
   (?P<col13>\d*\.\d+)   # brightness - eFlux
   \s*
   \S+
   \s*$""",re.VERBOSE)

 # RA and Dec coordinates of the Patch Phase Center
 RA_0 = 4.35664870004
 Dec_0 = 1.09220644132

 pc_name = 'Phase Center';
 twoname = 'twopack['+pc_name+']';

 RA_root = RJN_sixpack.make_RA(pc_name,RA_0,ns);
 Dec_root = RJN_sixpack.make_Dec(pc_name,Dec_0,ns);
 tworoot = ns[twoname] << Meq.Composer(RA_root,Dec_root);
 
 child_rec = [twoname];

 lmax = 0
 mmax = 0
 linecount=0
 random.seed(0)

 # read each source and insert to LSM
 for eachline in all:
  v=pp.search(eachline)
  if v!=None:
   linecount+=1
   print v.group('col2'), v.group('col12')
   sname=v.group('col2')
   srcnames.append(sname)
   
   source_RA=float(v.group('col3'))+(float(v.group('col5'))/60.0+float(v.group('col4')))/60.0
   source_RA*=math.pi/12.0
   source_Dec=float(v.group('col7'))+(float(v.group('col9'))/60.0+float(v.group('col8')))/60.0
   source_Dec*=math.pi/180.0

   #sisif = math.log10( eval(v.group('col12')) )
   sisif = eval(v.group('col12')) 
   
   #qin = random.uniform(-0.2,0.2)
   #uin = random.uniform(-0.2,0.2)
   #vin = random.uniform(-0.01,0.01)
   #qin = 0.0;
   #uin = 0.0;
   #vin = 0.0;
   qin = 1.0;
   uin = 2.0;
   vin = 0.0;

   sixroot = RJN_sixpack.make_sixpack(srcname=sname,RA=source_RA,Dec=source_Dec,ISIF0=sisif,Qpct=qin,Upct=uin,Vpct=vin,ns=ns)

   sixname = 'sixpack[q='+sname+']';
   child_rec.append(sixname);

   lc = math.cos(source_Dec)*math.sin(RA_0-source_RA)
   lm = math.cos(Dec_0)*math.sin(source_Dec) - math.sin(Dec_0)*math.cos(source_Dec)*math.cos(RA_0-source_RA)
   
   lmax = max(lmax,abs(lc))
   mmax = max(mmax,abs(lm))
 
 sname = 'sixpack[q=testsource]';
 source_RA = RA_0 + 0.0*0.0000183944088323;
 source_Dec = Dec_0 + 2*0.0000183944088323;
 sisif = 1.0;
 qin = 1.0;
 uin = 1.0;
 vin = 1.0;

 sixroot = RJN_sixpack.make_sixpack(srcname=sname,RA=source_RA,Dec=source_Dec,ISIF0=sisif,Qpct=qin,Upct=uin,Vpct=vin,ns=ns)

 sixname = 'sixpack[q='+sname+']';
 child_rec.append(sixname);

 print "Inserted %d sources" % linecount 
 print "maximum l and m out of Phase Center", lmax, mmax

 X0 = 0.0;   # m
 Y0 = 2000.0; #m
 Z0 = 0.0;   #m

 delta  = math.pi/2;

 #PatchComposer (SixPack)
 patch_root = ns['Patch['+pc_name+']'] << Meq.PatchComposer(children=child_rec);

 #Selector (FourPack)
 select_root = ns['Select['+pc_name+']']<<Meq.Selector(children=patch_root,multi=True,index=[2,3,4,5]);

 #Stokes
 stokes_root = ns['Stokes['+pc_name+']'] << Meq.Stokes(children=select_root);

 #FFTBrick
 fft_root = ns['FFT['+pc_name+']']<<Meq.FFTBrick(children=stokes_root);

 # X0, Y0, Z0
 x0_root = ns['X0']<<Meq.Constant(X0);
 y0_root = ns['Y0']<<Meq.Constant(Y0);
 z0_root = ns['Z0']<<Meq.Constant(Z0);

 # Sin(delta), Cos(delta)
 sd_root = ns['sindelta']<<Meq.Constant(math.sin(delta));
 cd_root = ns['cosdelta']<<Meq.Constant(math.cos(delta));

 # H(t) = 2 pi t / (24*3600)
 t_root = ns['time']<<Meq.Time();
 c_root = ns['time_c']<<Meq.Constant(2.0*math.pi/3600/24);
 t2_root = ns['time2']<<Meq.Multiply(children=[t_root,c_root]);

 # Cos(H(t)), Sin(H(t))
 c_root = ns['cos']<<Meq.Cos(children=[t2_root]);
 s_root = ns['sin']<<Meq.Sin(children=[t2_root]);

 # X0*cos(H), X0*sin(H), Y0*cos(H), Y0*sin(H)
 xc_root = ns['xc']<<Meq.Multiply(children=[x0_root,c_root]);
 xs_root = ns['xs']<<Meq.Multiply(children=[x0_root,s_root]);
 yc_root = ns['yc']<<Meq.Multiply(children=[y0_root,c_root]);
 ys_root = ns['ys']<<Meq.Multiply(children=[y0_root,s_root]);

 # u
 u_root = ns['U'] << Meq.Add(children=[xs_root,yc_root]);

 #v
 v1_root = ns['v1']<<Meq.Subtract(children=[ys_root,xc_root]);
 v2_root = ns['v2'] << Meq.Multiply(children=[v1_root,sd_root]);
 cz_root = ns['cz'] << Meq.Multiply(children=[cd_root,z0_root]);
 v_root = ns['V'] << Meq.Add(children=[v2_root,cz_root]);

 #w
 w2_root = ns['w2'] << Meq.Multiply(children=[v1_root,cd_root]);
 sz_root = ns['sz'] << Meq.Multiply(children=[sd_root,z0_root]);
 w_root = ns['W'] << Meq.Subtract(children=[sz_root,w2_root]);

 #uvw
 uvw_root = ns['UVW']<<Meq.Composer(children=[u_root,v_root,w_root]);

 #UVInterpol
 interpol_root = ns['UVInterpol['+pc_name+']']<<Meq.UVInterpol(Method=3,children=[fft_root,uvw_root],additional_info=True);
 #interpol2_root = ns['UVInterpol2['+pc_name+']']<<Meq.UVInterpol(Method=1,children=[fft_root,uvw_root],additional_info=True);

 #RA,Dec,RA_0,Dec_0
 ra_array = array([source_RA/0.001]);
 dec_array=array([source_Dec/0.001]);
 ra_polc=meq.polc(coeff=ra_array);
 dec_polc=meq.polc(coeff=dec_array);
 nRA_root = ns['nRA']<<Meq.Parm(ra_polc,node_groups='Parm');
 nDec_root = ns['nDec']<<Meq.Parm(dec_polc,node_groups='Parm');
 dRA_root = ns['dRA']<<Meq.Constant(0.001);
 dDec_root = ns['dDec']<<Meq.Constant(0.001);
 RA_root = ns['RA']<<Meq.Multiply(children=[nRA_root,dRA_root]);
 Dec_root = ns['Dec']<<Meq.Multiply(children=[nDec_root,dDec_root]);
 RA0_root = ns['RA0']<<Meq.Constant(RA_0);
 Dec0_root = ns['Dec0']<<Meq.Constant(Dec_0);

 #LMN
 l_root = ns['L']<<Meq.Subtract(children=[RA_root,RA0_root]);
 m_root = ns['M']<<Meq.Subtract(children=[Dec_root,Dec0_root]);
 n_root = ns['N']<<Meq.Constant(0.0);
 lmn_root = ns['LMN']<<Meq.Composer(children=[l_root, m_root, n_root]);

 # DFT
 #dft_root = ns['DFT']<<Meq.Multiply(children=[Meq.Constant(-1.0),Meq.VisPhaseShift(lmn=lmn_root,uvw=uvw_root)]);
 dft_root = ns['DFT']<<Meq.VisPhaseShift(lmn=lmn_root,uvw=uvw_root);

 # Condeq
 select2_root = ns['Select2']<<Meq.Selector(children=interpol_root,multi=True,index=[0]);

 cond_root = ns['Condeq'] << Meq.Condeq(children=[select2_root,dft_root]);
 #cond_root = ns['Condeq'] << Meq.Condeq(children=[interpol_root,interpol2_root]);

 # Solver
 solvables = ["nDec"];
 solver_root = ns['Solver']<<Meq.Solver(children=[cond_root],num_iter=100,debug_level=20,solvable=solvables);

 # Bookmarks
 MG_JEN_forest_state.bookmark(cond_root,page="CondEq",viewer="Result Plotter");
 MG_JEN_forest_state.bookmark(select2_root,page="FT-Result",viewer="Result Plotter");
 MG_JEN_forest_state.bookmark(dft_root,page="FT-Result",viewer="Result Plotter");
 MG_JEN_forest_state.bookmark(fft_root,page="UVBrick",viewer="Result Plotter");
 MG_JEN_forest_state.bookmark(interpol_root,udi="cache/result/uvinterpol_map",page="UVBrick",viewer="Result Plotter");
 MG_JEN_forest_state.bookmark(patch_root,page="Patch Image",viewer="Result Plotter");

########################################################################

def _test_forest(mqs,parent):
 global srcnames   

 # create a cell
 from Timba.Meq import meq

 f0 = 1300e6
 f1 = 1300.001e6
 t0 = 0.0
 t1 = 86400.0
 nfreq = 1
 ntime = 10
 
 # create cell
 freqtime_domain = meq.domain(startfreq=f0, endfreq=f1, starttime=t0, endtime=t1);
 cells =meq.cells(domain=freqtime_domain, num_freq=nfreq,  num_time=ntime);

 request1 = meq.request(cells=cells, eval_mode=0 );

 #twoname = 'twopack[Phase Center]';
 #args=record(name=twoname, request=request1);
 #mqs.meq('Node.execute', args, wait=False);

 #for sname in srcnames:

   #sixname = 'sixpack[q='+sname+']';
   # print  sname,  sixname   
   #args=record(name=sixname, request=request1);
   #mqs.meq('Node.execute', args, wait=False);
  
 # Tony: execute the Patch[Phase Center] node, instead of the one I use  
 #args=record(name='Patch[Phase Center]', request=request1);
 #args=record(name='FFT[Phase Center]', request=request1);
 #args=record(name='UVInterpol[Phase Center]', request=request1);
 args=record(name='Solver', request=request1);


 mqs.meq('Node.execute', args, wait=False);
   

#####################################################################

if __name__=='__main__':
  ns=NodeScope()
  define_forest(ns)
  ns.Resolve()
  print "Added %d nodes" % len(ns.AllNodes())
  #display LSM without MeqBrowser
  #l.display(app='create')
