include 'mqsinit_test.g'
include 'table.g'
include 'measures.g'
include 'quanta.g'

# helper func
# creates fully-qualified node name, by pasting a bunch of suffixes after
# the name, separated by dots.
const fq_name := function (name,...) 
{
  res := name;
  for( i in 1:num_args(...) )
  {
    q := nth_arg(i,...);
    if( !is_string(q) || q )
      res := paste(res,q,sep='.');
  }
  return res;
}

# creates common nodes:
#   'ra0' 'dec0':       phase center
const create_common_parms := function (ra0,dec0)
{
  mqs.createnode(meq.parm('ra0',ra0));
  mqs.createnode(meq.parm('dec0',dec0));
}

# creates all source-related nodes and subtrees:
#   'stokesI':          flux
#   'ra' 'dec':         source position
#   'lmn','n':          LMN coordinates, N coordinate
# src specifies the source suffix ('' for none)
const create_source_subtrees := function (sti,ra,dec,src='')
{
  # meq.parm(), meq.node() return init-records
  # mqs.createnode() actually creates a node from an init-record.
  
  mqs.createnode(meq.parm(fq_name('stokes_i',src),sti,groups="a"));
  # note the nested-record syntax here, to create child nodes implicitly
  mqs.createnode(meq.node('MeqLMN',fq_name('lmn',src),children=[
                  ra_0  ='ra0',
                  dec_0 ='dec0',
                  ra    =meq.parm(fq_name('ra',src),ra,groups="a"),
                  dec   =meq.parm(fq_name('dec',src),dec,groups="a")]));
  mqs.createnode(meq.node('MeqSelector',fq_name('n',src),[index=3],
                            children=fq_name("lmn",src)));
}

# builds an init-record for a "dft" tree for one station (st)
const sta_dft_tree := function (st,src='')
{
  global ms_antpos; # station positions from MS
  global mepuvw;    # MEP table with UVWs
  pos := ms_antpos[st];
  # create a number of UVW nodes, depending on settings
  uvwlist := dmi.list();
  # parms from MEP table
  if( mepuvw )
  {
    dmi.add_list(uvwlist,
      meq.node('MeqComposer',fq_name('mep.uvw',st),children=meq.list(
        meq.node('MeqParm',fq_name('U',st),[table_name=mepuvw]),
        meq.node('MeqParm',fq_name('V',st),[table_name=mepuvw]),
        meq.node('MeqParm',fq_name('W',st),[table_name=mepuvw])
      )) );
  }
  # const values based on what was read from the MS
  if( !is_boolean(ms_antuvw) )
  {
    dmi.add_list(uvwlist,
      meq.node('MeqComposer',fq_name('ms.uvw',st),children=meq.list(
        meq.node('MeqConstant',fq_name('u',st),[value=ms_antuvw[1,st]]),
        meq.node('MeqConstant',fq_name('v',st),[value=ms_antuvw[2,st]]),
        meq.node('MeqConstant',fq_name('w',st),[value=ms_antuvw[3,st]])
      )) );
  }
  # finally, this node computes UVWs directly
  dmi.add_list(uvwlist,
            meq.node('MeqUVW',fq_name('uvw',st),children=[
                         x = meq.parm(fq_name('x',st),pos.x),
                         y = meq.parm(fq_name('y',st),pos.y),
                         z = meq.parm(fq_name('z',st),pos.z),
                         ra = 'ra0',dec = 'dec0',
                         x_0='x0',y_0='y0',z_0='z0' ]));
                        
  uvw := meq.node('MeqReqSeq',fq_name('uvw.seq',st),[result_index=1,link_or_create=T],children=uvwlist);
    
  # builds an init-rec for a node called 'dft.N' with two children: 
  # lmn and uvw.N
  dft := meq.node('MeqStatPointSourceDFT',fq_name('dft0',src,st),[link_or_create=T],children=[
              lmn = fq_name('lmn',src),uvw=uvw ]);
  # add antenna gains/phases
  gain := meq.node('MeqPolar',fq_name('G',st),[link_or_create=T],children=meq.list(
              meq.parm(fq_name('GA',st),1.0,groups="a"),
              meq.parm(fq_name('GP',st),0.0,groups="a") ) );
              
  return meq.node('MeqMultiply',fq_name('dft',src,st),[link_or_create=T],
                    children=meq.list(dft,gain));
}

# builds an init-record for a "dft" tree for source 'src' and two stations (st1,st2)
const ifr_source_predict_tree := function (st1,st2,src='')
{
  return meq.node('MeqMultiply',fq_name('predict',src,st1,st2),children=meq.list(
      fq_name('stokes_i',src),
      meq.node('MeqPointSourceDFT',fq_name('dft',src,st1,st2),children=[
               st_dft_1 = sta_dft_tree(st1,src),
               st_dft_2 = sta_dft_tree(st2,src),
               n = fq_name('n',src) ] ) ));
}

# builds an init-record for a sum of "dft" trees for all sources and st1,st2
const ifr_predict_tree := function (st1,st2,src=[''])
{
  if( len(src) == 1 )
    return ifr_source_predict_tree(st1,st2,src);
  list := dmi.list();
  for( s in src ) 
    dmi.add_list(list,ifr_source_predict_tree(st1,st2,s));
  return meq.node('MeqAdd',fq_name('predict',st1,st2),children=list);
}

# creates nodes shared among trees: source parms, array center (x0,y0,z0)
const make_shared_nodes := function (stokesi=1,dra=0,ddec=0,src=[''])
{
  global ms_phasedir;
  ra0  := ms_phasedir[1];  # phase center
  dec0 := ms_phasedir[2];
  # setup source parameters and subtrees
  create_common_parms(ra0,dec0);
  for( i in 1:len(src) ) {
    print src[i];
    print create_source_subtrees(stokesi[i],ra0+dra[i],dec0+ddec[i],src[i]);
  }
  # setup zero position
  global ms_antpos;
  names := "x0 y0 z0";
  for( i in 1:3 )
    mqs.createnode(meq.node('MeqConstant',names[i],[value=ms_antpos[1][i]]));
}

# builds a predict tree for stations st1, st2
const make_predict_tree := function (st1,st2,src=[''])
{
  sinkname := fq_name('sink',st1,st2);
  if( len(src) == 1 )
    pred := ifr_predict_tree(st1,st2,src);
  else 
  {
    list := dmi.list();
    for( s in src ) 
      dmi.add_list(list,ifr_predict_tree(st1,st2,s));
    pred := meq.node('MeqAdd',fq_name('predict',st1,st2),children=list);
  }
  # create a sink
  mqs.createnode(meq.node('MeqSink',sinkname,
                         [ output_col      = 'PREDICT',   # init-rec for sink
                           station_1_index = st1,
                           station_2_index = st2,
                           corr_index      = [1] ],children=dmi.list(
                            ifr_predict_tree(st1,st2,src)
                           )));
  return sinkname;
}

# builds a read-predict-subtract tree for stations st1, st2
const make_subtract_tree := function (st1,st2,src=[''])
{
  sinkname := fq_name('sink',st1,st2);
  
  # create a sink & subtree attached to it
  # note how meq.node() can be passed a record in the third argument, to specify
  # other fields in the init-record
  mqs.createnode(
    meq.node('MeqSink',sinkname,
                         [ output_col      = 'PREDICT',
                           station_1_index = st1,
                           station_2_index = st2,
                           corr_index      = [1] ],
                         children=meq.list(
      meq.node('MeqSubtract',fq_name('sub',st1,st2),children=meq.list(
        meq.node('MeqSelector',fq_name('xx',st1,st2),[index=1],children=meq.list(
          meq.node('MeqSpigot',fq_name('spigot',st1,st2),[ 
            station_1_index=st1,
            station_2_index=st2,
            input_column='DATA'])
        )),
        ifr_predict_tree(st1,st2,src)
      ))
    ))
  );
  return sinkname;
}


# builds a solve tree for stations st1, st2
const make_solve_tree := function (st1,st2,src=[''],subtract=F)
{
  sinkname := fq_name('sink',st1,st2);
  predtree := ifr_predict_tree(st1,st2,src);
  predname := predtree.name;
  mqs.createnode(predtree);
  
  # create condeq tree (solver will plug into this)
  mqs.createnode(
    meq.node('MeqCondeq',fq_name('ce',st1,st2),children=meq.list(
      predname,
      meq.node('MeqSelector',fq_name('xx',st1,st2),[index=1],children=meq.list(
        meq.node('MeqSpigot',fq_name('spigot',st1,st2),[ 
              station_1_index=st1,
              station_2_index=st2,
              input_column='DATA'])
      ))
    ))
  );
  # create subtract sub-tree
  if( subtract )
    mqs.createnode(meq.node('MeqSubtract',subname:=fq_name('sub',st1,st2),
                      children=[fq_name('xx',st1,st2),predname]));
  else
    subname := fq_name('spigot',st1,st2);
  
  
  # create root tree (plugs into solver & subtract)     
  mqs.createnode(
    meq.node('MeqSink',sinkname,[ output_col      = 'PREDICT',
                                  station_1_index = st1,
                                  station_2_index = st2,
                                  corr_index      = [1] ],children=meq.list(
      meq.node('MeqReqSeq',fq_name('seq',st1,st2),[result_index=2],
        children=['solver',subname])
   ))
 );

  return sinkname;
}

# reads antenna positions and phase center from MS,
# puts them into global variables
const get_ms_info := function (msname='test.ms',uvw=T)
{
  global ms_phasedir,ms_antpos;
  
  ms := table(msname);
  msant := table(ms.getkeyword('ANTENNA'));
  pos := msant.getcol('POSITION');
  num_ant := msant.nrows();
  msant.done();
  
  time0 := ms.getcell('TIME',1);
  
  # convert position to x y z
  ms_antpos := [=];
  for(i in 1:len(pos[1,]))
    ms_antpos[i] := [ x=pos[1,i],y=pos[2,i],z=pos[3,i] ];
    
  msfld := table(ms.getkeyword('FIELD'));
  ms_phasedir := msfld.getcol('PHASE_DIR');
  msfld.done();
  
  if( uvw )
  {
    global ms_antuvw;
    ms_antuvw := array(0.,3,num_ant);
    mss := ms.query('DATA_DESC_ID==0');
    # get UVW coordinates from ms
    ant1 := mss.getcol('ANTENNA1');
    ant2 := mss.getcol('ANTENNA2');
    uvw  := mss.getcol('UVW');
    mask1 := ant1 == 0;
    uvw0 := uvw[,mask1];
    ant2 := ant2[mask1];
    for( a2 in 2:num_ant )
    {
      t := uvw0[,ant2==(a2-1)];
      if( len(t) != 3 )
      {
        print 'cannot use UVWs from MS if more than one time slot';
        fail 'cannot use UVWs from MS if more than one time slot';
      }
      ms_antuvw[,a2] := t;
    }
    print 'Antenna UVWs:',ms_antuvw;
  }
  
  # get some UVWs, just for shits and giggles
  a0 := ms_antpos[1];
  pos0 := dm.position('itrf',dq.unit(a0.x,'m'),dq.unit(a0.y,'m'),dq.unit(a0.z,'m'));
  a1 := ms_antpos[1];
  a2 := ms_antpos[2];
  ba1 := dm.baseline('itrf',dq.unit(a2.x-a1.x,'m'),dq.unit(a2.y-a1.y,'m'),dq.unit(a2.z-a1.z,'m'));
  ba2 := dm.baseline('itrf',dq.unit(a1.x,'m'),dq.unit(a1.y,'m'),dq.unit(a1.z,'m'));
  dm.doframe(pos0);
  dm.doframe(dm.direction('j2000',dq.unit(ms_phasedir[1],"rad"),dq.unit(ms_phasedir[2],"rad")));
  dm.doframe(dm.epoch('utc',dq.unit(time0,'s')));
  local uvw1a;
  local dot;
  uvw1b := dm.touvw(ba1,dot,uvw1a);
  uvw1c := dm.addxvalue(uvw1b);
  uvw2b := dm.touvw(ba2,dot,uvw2a);
  uvw2c := dm.addxvalue(uvw2b);
  
  ms.done();  
  
  print 'Antenna position 1: ',ms_antpos[1];
  print 'Antenna position 2: ',ms_antpos[2];
  print 'Phase dir: ',ms_phasedir[1],' ',ms_phasedir[2];
  print 'UVW1a:',uvw1a;
  print 'UVW1b:',uvw1b;
  print 'UVW1c:',uvw1c;
  print 'UVW2a:',uvw2a;
  print 'UVW2b:',uvw2b;
  print 'UVW2c:',uvw2c;
  print 'Does this look sane?';
  
  return T;
}


const reexec := function (node='dft.a.4',nfreq=10,ntime=10)
{
  global rqid;
  st := mqs.getnodestate(node);
  dom := st.request.cells.domain;
  cells := meq.cells(dom,nfreq,ntime);
  req := meq.request(cells,hiid());
  mqs.execute(node,req);
  print 'you should be looking at node ',node;
  print 'cells are: ',cells;
  print 'domain was: ',cells;
}

use_initcol := T;       # initialize output column with zeroes

# predict=T:  predict tree only (writes predict to output column)
# subtract=T: predict+subtract trees (writes residual to output column)
# solve=T,subtract=T: solve+subtract trees (writes residual to output column)
# solve=T,subtract=F: solve but no subtract
#
# run=F: build trees and stop, run=T: run over the measurement set
const do_test := function (predict=F,subtract=F,solve=F,run=T,
    msname='test.ms',
    outcol='PREDICTED_DATA',        # output column of MS
    stset=1:4,                      # stations for which to make trees
    msuvw=F,                        # use UVW values from MS
    mepuvw=F,                       # use UVW from MEP table (should be filled already)
    load='',                        # load forest from file 
    save='',                        # save forest to file
    set_breakpoint=F,               # set breakpoint on solver
    publish=3)    # node publish: higher means more detail
{
  # clear output column in MS
  # (I still can't get this to work from C++, hence this bit of glish here)
  if( use_initcol )
  {
    print 'Clearing',outcol,'column, please ignore error messages'
    tbl := table(msname,readonly=F);
    desc := tbl.getcoldesc(outcol);
    if( is_fail(desc) )
      desc := [=];
    # insert column anew, if no shape
    if( has_field(desc,'shape') )
      cellshape := desc.shape;
    else
    {
      if( len(desc) )
        tbl.removecols(outcol);
      cellshape := tbl.getcell('DATA',1)::shape;
      desc := tablecreatearraycoldesc(outcol,complex(0),2,shp);
      tbl.addcols(desc);
    }
    # insert zeroes
    tbl.putcol(outcol,array(complex(0),cellshape[1],cellshape[2],tbl.nrows()));
    tbl.done();
  }

  # read antenna positions, etc.  
  get_ms_info(msname,uvw=msuvw);
  
  # initialize meqserver (see mqsinit_test.g)
  if( is_fail(mqsinit()) )
  {
    print mqs;
    fail;
  }
  mqs.track_results(F);

  mqs.meq('Clear.Forest',[=]);
  # load forest if asked
  if( load )
    mqs.meq('Load.Forest',[file_name=load])
  else # else build trees
  {  
    # create common nodes (source parms and such)
    dra :=  30 * pi/(180*60*60); # perturb position by # seconds
    ddec := 30 * pi/(180*60*60);
#    dra := ddec := 0;
    make_shared_nodes(src_sti,src_dra,src_ddec,src_names);

    # make a solver node (since it's only one)
    if( solve )
    {
      # accumulate list of IFR condeqs
      condeqs := [];
      for( st1 in stset )
        for( st2 in stset )
          if( st1 < st2 )
            condeqs := [condeqs,fq_name('ce',st1,st2)];
      # solvable parms
      solvables := "stokes_i.a ra.a dec.a stokes_i.b ra.b dec.b";      
      if( solve_gains )
        for( st in stset[2:len(stset)] )
          solvables := [solvables,fq_name('GA',st)];
      if( solve_phases )
        for( st in stset[2:len(stset)] )
          solvables := [solvables,fq_name('GP',st)];
      # note that child names will be resolved later
      global solver_defaults;
      rec := meq.node('MeqSolver','solver',[
          parm_group = hiid("a"),
          default    = solver_defaults,
          solvable   = meq.solvable_list(solvables) ],
        children=condeqs);
      mqs.createnode(rec);
    }
    if( publish>0 )
    {
      for( s in src_names )
      {
        mqs.meq('Node.Publish.Results',[name=fq_name("ra",s)]);
        mqs.meq('Node.Publish.Results',[name=fq_name("dec",s)]);
        mqs.meq('Node.Publish.Results',[name=fq_name("stokes_i",s)]);
      }
    }
    rootnodes := [];
    # make predict/condeq trees
    for( st1 in stset )
      for( st2 in stset )
        if( st1 < st2 )
        {
          if( solve )
          {
            rootnodes := [rootnodes,make_solve_tree(st1,st2,src=src_names,subtract=subtract)];
            if( publish>1 )
              mqs.meq('Node.Publish.Results',[name=fq_name('ce',st1,st2)]);
          }
          else if( subtract )
            rootnodes := [rootnodes,make_subtract_tree(st1,st2,src_names)];
          else
            rootnodes := [rootnodes,make_predict_tree(st1,st2,src_names)];
          if( publish>2 )
            mqs.meq('Node.Publish.Results',[name=fq_name('predict',st1,st2)]);
        }
    # resolve children on all root nodes
#    print 'Root nodes are: ',rootnodes;
    print "Resolving root nodes";
    for( r in rootnodes )
      mqs.resolve(r);
  }
  # save forest if requested
  if( save )
    mqs.meq('Save.Forest',[file_name=save]);
  
  # get a list of nodes
  nodelist := mqs.getnodelist(children=T);
  # print 'Nodes: ',nodelist.name;
  
  # enable publishing of solver results
  if( solve && publish>0 ) {
    mqs.meq('Node.Publish.Results',[name='solver']);
#    mqs.meq('Node.Publish.Results',[name=fq_name('dft.b',4,8)]);
#    mqs.meq('Node.Publish.Results',[name=fq_name('U',8)]);
  }
  
  if( set_breakpoint )
    mqs.meq('Node.Set.Breakpoint',[name='solver']);
  mqs.meq('Debug.Set.Level',[debug_level=100]);

  # run over MS
  if( run )
    do_run();
}

const do_run := function ()
{
  # activate input and watch the fur fly  
  global inputrec,outputrec;
  mqs.init([mandate_regular_grid=T,output_col='PREDICT'],input=inputrec,output=outputrec); 
}


msname := 'test.ms';
# msname := 'test-wsrt.ms';
mepuvw := T;
filluvw := any(argv=='-filluvw');
solve_gains := any(argv=='-gains');
solve_phases := any(argv=='-phases');
set_breakpoint := any(argv=='-bp');

src_dra  := ([0,142.5]+0) * pi/(180*60*60); # perturb positions by # seconds
src_ddec := ([0,128]+0) * pi/(180*60*60);
src_sti  := [1,1]   + 0.1;
src_names := "a b";


# fill UVW parms from MS if requested
if( mepuvw )
{
  include 'meq/msuvw_to_mep.g'
  mepuvw := msname ~ s/.ms/.mep/;
  if( filluvw )
    fill_uvw(msname,mepuvw);
}
else
  mepuvw := F;

solver_defaults := [ num_iter=10,save_polcs=F,last_update=F ];

inputrec := [ ms_name = msname,data_column_name = 'DATA',tile_size=5,
              selection = [ channel_start_index=1,channel_end_index=1 ] ];
outputrec := [ write_flags=F,predict_column=outcol ]; 

do_test(msname=msname,solve=T,subtract=F,run=T,
#  st1set=[1:5]*4,st2set=[1:5]*4,
#  st1set=[1:21]*4,st2set=[1:21]*4,
  stset=1+[0:3]*4,
#  st1set=1+[0:20]*4,st2set=1+[0:20]*4,
#  st1set=1:100,st2set=1:100,
  set_breakpoint=set_breakpoint,
  publish=1,mepuvw=mepuvw,msuvw=msuvw);
#do_test(solve=T,run=T,publish=2,load='solve-100.forest');

print 'errors reported:',mqs.num_errors();

