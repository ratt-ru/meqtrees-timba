include 'mqsinit_test.g'

const meqsink_test := function (gui=use_gui)
{
  # remove output column from table
  print'Removing PREDICTED_DATA column, please ignore error messages'
  tbl := table('test.ms',readonly=F);
  tbl.removecols('PREDICTED_DATA');
  tbl.done();
  
  if( is_fail(mqsinit(verbose=1,gui=gui)) )
  {
    print mqs;
    fail;
  }

  # initialize meq.server
  mqs.init([output_col="PREDICT"],
      output=[write_flags=F,predict_column='PREDICTED_DATA'],
      wait=T);
  
  # create a small subtree
  defval1 := array(as_double(1),2,2);
  defval2 := array(as_double(2),1,1);
  addrec := meq.node('MeqSubtract','compare',children="spigot1 spigot2");
  print mqs.meq('Create.Node',addrec);
  # create spigot (note! for now, a spigot MUST be created first)
  spigrec1 := meq.node('MeqSpigot','spigot1');
  spigrec1.input_col := 'DATA';
  spigrec1.station_1_index := 1;
  spigrec1.station_2_index := 2;
#  spigrec.flag_mask := -1;
#  spigrec.row_flag_mask := -1;
  print mqs.meq('Create.Node',spigrec1);
  spigrec2 := meq.node('MeqSpigot','spigot2');
  spigrec2.input_col := 'DATA';
  spigrec2.station_1_index := 1;
  spigrec2.station_2_index := 2;
  print mqs.meq('Create.Node',spigrec2);
  # create sink
  sinkrec := meq.node('MeqSink','sink1',children="compare");
  sinkrec.output_col := 'PREDICT'; 
  sinkrec.station_1_index := 1;
  sinkrec.station_2_index := 2;
  print mqs.meq('Create.Node',sinkrec);
  
  # resolve its children
  print mqs.resolve('sink1',F);
  
  # activate input agent and watch the fireworks
  global inputrec;
  inputrec := [ ms_name = 'test.ms',data_column_name = 'DATA',tile_size=5,
                selection = [=]  ];
  mqs.init(input=inputrec); 
}

const meqsel_test := function (gui=use_gui)
{
  if( is_fail(mqsinit(verbose=4,gui=gui)) )
  {
    print mqs;
    fail;
  }
  # create a small subtree
  defval1 := array(as_double(1),2,2);
  defval2 := array(as_double(2),1,1);
  defval3 := array(as_double(3),1,1);
  print mqs.meq('Create.Node',meq.parm('parm1',defval1));
  print mqs.meq('Create.Node',meq.parm('parm2',defval2));
  print mqs.meq('Create.Node',meq.parm('parm3',defval3));
  print mqs.meq('Create.Node',meq.parm('parm4',defval1));
  print mqs.meq('Create.Node',meq.parm('parm5',defval2));
  print mqs.meq('Create.Node',meq.parm('parm6',defval3));
  print mqs.meq('Create.Node',meq.node('MeqComposer','compose1',children="parm1 parm2 parm3"));
  print mqs.meq('Create.Node',meq.node('MeqComposer','compose2',children="parm3 parm5 parm6"));
  rec := meq.node('MeqSelector','select1',children="compose1");
  rec.index := [1,5];
  print mqs.meq('Create.Node',rec);
  rec := meq.node('MeqSelector','select2',children="compose2");
  rec.index := [1,5];
  print mqs.meq('Create.Node',rec);
  print mqs.meq('Create.Node',meq.node('MeqComposer','compose3',children="select1 select2"));
  rec := meq.node('MeqSelector','select3',children="compose3");
  rec.index := [2,3,4];
  print mqs.meq('Create.Node',rec);
  
  # resolve children
  print mqs.resolve('select3');
  
  global cells,request,res;
  cells := meq.cells(meq.domain(0,10,0,10),20,3);
  request := meq.request(cells);
  res := mqs.meq('Node.Execute',[name='select3',request=request],T);
  print res;
}

const state_test_init := function (gui=use_gui)
{
  if( is_fail(mqsinit(verbose=4,gui=F)) )
  {
    print mqs;
    fail;
  }
  mqs.meq('Clear.Forest');
  # create a small subtree
  defval1 := array(as_double(1),1,1);
  defval2 := array(as_double(2),1,1);
  defval3 := array(as_double(3),1,1);
  print mqs.meq('Create.Node',meq.parm('parm1',defval1));
  print mqs.meq('Create.Node',meq.parm('parm2',defval2));
  print mqs.meq('Create.Node',meq.parm('parm3',defval3));
  print mqs.meq('Create.Node',meq.parm('parm4',defval1));
  print mqs.meq('Create.Node',meq.parm('parm5',defval2));
  print mqs.meq('Create.Node',meq.parm('parm6',defval3));
  print mqs.meq('Create.Node',meq.node('MeqComposer','compose1',children="parm1 parm2 parm3"));
  print mqs.meq('Create.Node',meq.node('MeqComposer','compose2',children="parm4 parm5 parm6"));
  rec := meq.node('MeqSelector','select1',children="compose1");
  rec.index := 1;
  rec.node_groups := hiid("a b");
  print mqs.meq('Create.Node',rec);
  rec := meq.node('MeqSelector','select2',children="compose2");
  rec.index := 1;
  rec.node_groups := hiid("a b");
  print mqs.meq('Create.Node',rec);
  print mqs.meq('Create.Node',meq.node('MeqComposer','compose3',children="select1 select2"));
  
  # resolve children
  print mqs.resolve('compose3');
}

const state_test := function (gui=use_gui)
{
  if( !is_record(mqs) )
    state_test_init(gui=gui);
  mqs.setdebug('Glish',5);
  
  # get indices
  ni_sel1 := mqs.getnodestate('select1').nodeindex;
  ni_sel2 := mqs.getnodestate('select2').nodeindex;
  
  global cells,request,res;
  cells := meq.cells(meq.domain(0,10,0,10),20,3);
  request := meq.request(cells);
  
#  mqs.setdebug("DMI Glish MeqServer glishclientwp meq.server Dsp",5);
  mqs.setdebug("Glish",5);

  res1 := mqs.meq('Node.Execute',[name='compose3',request=request],T);
  req1 := request;
  print res1;
  
  request := meq.request(cells);
  request.add_state('a','select1',[index=2]);
  request.add_state('b',ni_sel2,[index=3]);
  res2 := mqs.meq('Node.Execute',[name='compose3',request=request],T);
  req2 := request;
  print res2;
  
  request := meq.request(cells);
  request.add_state('a',"select1 select2",[index=3]);
  res3 := mqs.meq('Node.Execute',[name='compose3',request=request],T);
  req3 := request;
  print res3;
  
  request := meq.request(cells);
  request.add_state('b','select1',[index=2]);
  request.add_state('b',"",[index=1]);
  res4 := mqs.meq('Node.Execute',[name='compose3',request=request],T);
  req4 := request;
  print res4;
  
  print 'Expecting 1,1: ',res1,req1;
  print 'Expecting 2,3: ',res2,req2;
  print 'Expecting 3,3: ',res3,req3;
  print 'Expecting 2,1: ',res4,req4;
}

const freq_test := function (gui=use_gui)
{
  meqsel_test();
  mqs.setverbose(5);
  mqs.setdebug("MeqNode",4);
  dom:=meq.domain(10,20,10,20);
  cells:=meq.cells(dom,10,3);
  mqs.meq('Create.Node',[class='MeqFreq',name='f']);
  print a:=mqs.meq('Node.Execute',[name='f',request=meq.request(cells)],T);
}

const solver_test := function (gui=use_gui,verbose=4,publish=T)
{
  if( is_fail(mqsinit(verbose=verbose,gui=gui,debug=F)) )
  {
    print mqs;
    fail;
  }
  mqs.setdebug('MeqSolver',5);
  # create parms and condeq
#  defval1 := array([3.,0.5,0.5,0.1],2,2);
#  defval2 := array([2.,10.,2.,10. ],2,2);
  defval1 := 1;
  defval2 := 0;
  print mqs.meq('Create.Node',meq.parm('a',defval1,groups='Parm'));
  print mqs.meq('Create.Node',meq.parm('b',defval2,groups='Parm'));
  print mqs.meq('Create.Node',meq.node('MeqCondeq','condeq1',children="a b"));
  # create solver
  global rec;
  rec := meq.node('MeqSolver','solver1',children="condeq1",groups='Solver');
  rec.default := [ num_iter = 3 ];
  rec.solvable := meq.solvable_list("a");
  rec.parm_group := hiid('Parm');
  print mqs.meq('Create.Node',rec);
  
  for( n in "a condeq1" )
    print mqs.meq('Node.Publish.Results',[name=n,enable=T]);
  
  global cells,cells2,request,request2,res,res2,st1,st2,st3;
  
  # resolve children
  print mqs.resolve('solver1');
  
  st1 := mqs.getnodestate('a');
  cells  := meq.cells(meq.domain(0,.5,0,.5),num_freq=4,num_time=4);
  cells2 := meq.cells(meq.domain(.5,1,.5,1),num_freq=4,num_time=4);
  request := meq.request(cells,calc_deriv=2);
  
  cmdrec := [ clear_matrix=F,invert_matrix=F,num_iter=5,save_polcs=F ];
  meq.add_command(request,'Solver','solver1',cmdrec);
  
  request2 := meq.request(cells2,calc_deriv=0);
  res := mqs.meq('Node.Publish.Results',[name='condeq1'],T);
  res := mqs.meq('Node.Execute',[name='solver1',request=request],T);
  print res;
  st2 := mqs.getnodestate('a');
  print st2.solve_polcs;
  res2 := mqs.meq('Node.Execute',[name='a',request=request2],T);
  print res2;
  st3 := mqs.getnodestate('a');
  print st3.solve_polcs;
}

const save_test := function (clear=F)
{
  print 'saving forest';
  print mqs.meq('Save.Forest',[file_name='forest.sav'],T);
}

const load_test := function (gui=use_gui)
{
  if( is_fail(mqsinit(verbose=4,gui=gui)) )
  {
    print mqs;
    fail;
  }
  print 'loading forest';
  print mqs.meq('Load.Forest',[file_name='forest.sav'],T);
  print mqs.meq('Get.Node.List',[=],T);
}

const mep_test := function (gui=use_gui)
{
  tablename := 'test.mep';
  print 'Initializing MEP table ',tablename;
  
  include 'meq/meptable.g';
  pt := meq.meptable(tablename,create=T);
  pt.putdef('a');
  pt.putdef('b');
  pt.done();
  
  if( is_fail(mqsinit(verbose=4,gui=gui)) )
  {
    print mqs;
    fail;
  }
  mqs.setdebug('MeqParm',5);
  
  defrec := meq.parm('a');
  defrec.table_name := tablename;
  print mqs.meq('Create.Node',defrec);
  
  global cells,request,res;
  cells := meq.cells(meq.domain(0,1,0,1),4,4);
  request := meq.request(cells,calc_deriv=0);
  
  res := mqs.meq('Node.Publish.Results',[name='a'],T);
  res := mqs.meq('Node.Execute',[name='a',request=request],T);
}

const mep_grow_test := function (gui=use_gui)
{
  if( is_fail(mqsinit(verbose=4,gui=gui)) )
  {
    print mqs;
    fail;
  }
  mqs.setdebug('MeqParm',5);
  
  polc := meq.polc(array([1,1,1,0],2,2),domain=meq.domain(0,1,0,1));
  polc.grow_domain := T;
  print 'Polc is ',polc;
  defrec := meq.parm('a',polc,groups='Parm');
  mqs.meq('Create.Node',defrec,T);
  
  global cells,request,res1,res2;
  cells := meq.cells(meq.domain(0,1,0,1),4,4);
  request := meq.request(cells,calc_deriv=1);
  
  mqs.meq('Node.Publish.Results',[name='a'],T);
  res1 := mqs.meq('Node.Execute',[name='a',request=request],T);

  cells := meq.cells(meq.domain(0,2,0,2),4,4);
  request := meq.request(cells,calc_deriv=1);
  
  res2 := mqs.meq('Node.Execute',[name='a',request=request],T);
}


const flagger_test := function (verbose=4,gui=use_gui)
{
  if( is_fail(mqsinit(verbose=verbose,gui=gui)) )
  {
    print mqs;
    fail;
  }
  # mqs.setdebug('MeqParm',5);
  global domain,cells,request;
  domain := meq.domain(-1,1,-1,1);
  cells := meq.cells(domain,8,8);
  request := meq.request(cells);
  
  # create polc for this domain
  polc := meq.polc(array([0,.5,.5,0],2,2),domain=domain);
  defrec := meq.parm('a',polc,groups='Parm');
  mqs.meq('Create.Node',defrec,T);
  
  # create flagger for >0
  defrec := meq.node('MeqZeroFlagger','flag1',children="a");
  defrec.oper := 'gt';
  defrec.flag_bit := 1;
  mqs.meq('Create.Node',defrec,T);
  # create flagger for <0
  defrec := meq.node('MeqZeroFlagger','flag2',children="a");
  defrec.oper := 'lt';
  defrec.flag_bit := 2;
  mqs.meq('Create.Node',defrec,T);
  # create flagger for >=0
  defrec := meq.node('MeqZeroFlagger','flag3',children="a");
  defrec.oper := 'ge';
  defrec.flag_bit := 4;
  mqs.meq('Create.Node',defrec,T);
  # create flagger for <=0
  defrec := meq.node('MeqZeroFlagger','flag4',children="a");
  defrec.oper := 'le';
  defrec.flag_bit := 8;
  mqs.meq('Create.Node',defrec,T);
  # create flagger for ==0
  defrec := meq.node('MeqZeroFlagger','flag5',children="a");
  defrec.oper := 'eq';
  defrec.flag_bit := 16;
  mqs.meq('Create.Node',defrec,T);
  # create flagger for !=0
  defrec := meq.node('MeqZeroFlagger','flag6',children="a");
  defrec.oper := 'ne';
  defrec.flag_bit := 32;
  mqs.meq('Create.Node',defrec,T);

  # create merge of everything
  defrec := meq.node('MeqMergeFlags','flag',children="flag1 flag2 flag3 flag4 flag5 flag6");
  mqs.meq('Create.Node',defrec,T);
  
  # create function
  defrec := meq.node('MeqAdd','add1',children="flag flag1 flag2 flag3");
  defrec.flag_mask := [ 8+16,-1,-1,-1];
  mqs.meq('Create.Node',defrec,T);
  
  # create another function
  defrec := meq.node('MeqAdd','add2',children="flag4 flag5 flag");
  defrec.flag_mask := 12;
  mqs.meq('Create.Node',defrec,T);

  # create another function
  defrec := meq.node('MeqAdd','add3',children="flag1 flag2 flag3");
  mqs.meq('Create.Node',defrec,T);
  
  # create another function
  defrec := meq.node('MeqAdd','add4',children="flag1 flag2 flag3");
  defrec.flag_mask := 0;
  mqs.meq('Create.Node',defrec,T);
  
  # create another function
  defrec := meq.node('MeqAdd','add5',children="flag1 flag2 flag3");
  defrec.flag_mask := -1;
  mqs.meq('Create.Node',defrec,T);
  
  mqs.resolve('add1',T);
  mqs.resolve('add2',T);
  mqs.resolve('add3',T);
  mqs.resolve('add4',T);
  mqs.resolve('add5',T);
  
  global res1,res2,res3,res4,res5;
  res1 := mqs.meq('Node.Execute',[name='add1',request=request],T);
  res2 := mqs.meq('Node.Execute',[name='add2',request=request],T);
  res3 := mqs.meq('Node.Execute',[name='add3',request=request],T);
  res4 := mqs.meq('Node.Execute',[name='add4',request=request],T);
  res5 := mqs.meq('Node.Execute',[name='add5',request=request],T);
#   result := mqs.meq('Node.Execute',[name='flag2',request=request],T);
#   result := mqs.meq('Node.Execute',[name='flag3',request=request],T);
#   result := mqs.meq('Node.Execute',[name='flag4',request=request],T);
#   result := mqs.meq('Node.Execute',[name='flag5',request=request],T);
#   result := mqs.meq('Node.Execute',[name='flag6',request=request],T);

  return result;
}

# test resolution coupler 
const rs_test := function (flags=[],flag_mask=-1,flag_bit=0,flag_density=.5)
{
  if( is_fail(mqsinit(verbose=verbose,gui=gui)) )
  {
    print mqs;
    fail;
  }
  # mqs.setdebug('MeqParm',5);
  global domain,cells,req,cells2,req2,cells3,req3,cells4,req4;
  global res,res2,res3,res4;
  
  domain := meq.domain(-1,1,-1,1);
  
  # create polc for this domain
  polc := meq.polc(array([1,.5,.5,0],2,2),domain=domain);
  defrec := meq.parm('a',polc,groups='Parm');
  defrec.solvable := T;
  mqs.meq('Create.Node',defrec,T);
  defrec := meq.node('MeqResampler','rs',children="a")
  defrec.integrate := T;
  defrec.flag_mask := flag_mask;
  defrec.flag_bit := flag_bit;
  defrec.flag_density := flag_density;
  mqs.meq('Create.Node',defrec,T);
  
  # this rqid will be re-used for all requests. What we do is clear the
  # cache of the Resampler node, then send up a request with the same ID
  # but different cells. The parm returns the original (cached) result, and
  # the Resampler integrates or extends it
  rqid := meq.rqid(0);
  # first, init the cache of the parm node
  cells := meq.cells(domain,2,2);
  req := meq.request(cells,rqid=rqid,calc_deriv=0);
  res := mqs.execute('a',req);
  # add flags to cache, if specified
  if( len(flags) )
  {
    res := mqs.getnodestate('a').cache_result;
    res.vellsets[1].flags := array(flags,2,2);
    mqs.meq('Node.Set.State',[name='a',state=[cache_result=res]],T);
  }
  
  res := mqs.execute('rs',req);

  cells2 := meq.cells(domain,1,1);
  req2 := meq.request(cells2,rqid=rqid,calc_deriv=2);
  mqs.meq('Node.Clear.Cache',[name='rs'],T);
  res2 := mqs.execute('rs',req2);

  cells3 := meq.cells(domain,4,2);
  req3 := meq.request(cells3,rqid=rqid,calc_deriv=2);
  mqs.meq('Node.Clear.Cache',[name='rs'],T);
  res3 := mqs.execute('rs',req3);
  
  cells4 := meq.cells(domain,1,4);
  req4 := meq.request(cells3,rqid=rqid,calc_deriv=2);
  mqs.meq('Node.Clear.Cache',[name='rs'],T);
  res4 := mqs.execute('rs',req4);
  
  print res.result.vellsets[1];
  print res2.result.vellsets[1];
  print res3.result.vellsets[1];
  print res4.result.vellsets[1];
}

const ars_test := function ()
{
  if( is_fail(mqsinit(verbose=verbose,gui=gui)) )
  {
    print mqs;
    fail;
  }
  # mqs.setdebug('MeqParm',5);
  global domain,cells,req,cells,res;
  
  domain := meq.domain(0,1,0,1);
  cells := meq.cells(domain,4,4);
  
  polc_a := meq.polc(array([1,.5,.5,0],2,2),domain=domain);
  polc_b := meq.polc(array([1,.5,.5,0],2,2),domain=domain);
  polc_c := meq.polc(array([1,-.5,-.5,0],2,2),domain=domain);
  
  mqs.meq('Create.Node',meq.parm('a',polc_a,groups='Parm'),T);
  mqs.meq('Create.Node',meq.parm('b',polc_b,groups='Parm'),T);
  mqs.meq('Create.Node',meq.parm('c',polc_c,groups='Parm'),T);
  
  defrec := meq.node('MeqModRes','modres1',children="a");
  defrec.factor := [-2,-4];
  mqs.meq('Create.Node',defrec,T);
  
  defrec := meq.node('MeqModRes','modres2',children="b");
  defrec.num_cells := [4,8];
  mqs.meq('Create.Node',defrec,T);
  
  defrec := meq.node('MeqAdd','add1',children="modres1 c");
  defrec.auto_resample := 1;
  mqs.meq('Create.Node',defrec,T);
  
  defrec := meq.node('MeqAdd','add2',children="modres2 c");
  defrec.auto_resample := -1;
  mqs.meq('Create.Node',defrec,T);
  
  defrec := meq.node('MeqComposer','compose',children="add1 add2");
  mqs.meq('Create.Node',defrec,T);
  
  print mqs.resolve('compose',T);
  
  req := meq.request(cells,calc_deriv=0);
  res := mqs.execute('compose',req);
  
  print res;
}

const stress_test := function (n=10000,verbose=0)
{
  if( is_fail(mqsinit(verbose=verbose,gui=gui)) )
  {
    print mqs;
    fail;
  }
  mqs.setdebug('MeqNode',0);
  mqs.setdebug('MeqForest',0);
  mqs.setdebug('MeqSink',0);
  mqs.setdebug('MeqSpigot',0);
  mqs.setdebug('MeqVisHandler',0);
  mqs.setdebug('MeqServer',0);
  mqs.setdebug('meqserver',0);
  
#  mqs.setdebug('Dsp',1);
#  mqs.setdebug('OctoEventSink',3);
#  mqs.setdebug('OctoEventMux',3);
  
  global domain,cells,req,cells,res;
  
  # create record for small subtree
  rec := [ class='MeqAdd',children=
          [ a=[class='MeqAdd',children=[a=[class='MeqConstant',value=0]]],
            b=[class='MeqAdd',children="c"],
            c=[class='MeqAdd',children="c"],
            d=[class='MeqAdd',children="c"] ] ];
  for( i in 1:n )
  {
    print 'Creating tree ',i;
    rec.name := spaste('root',i);
    rec.children.a.name := spaste('a',i);
    rec.children.b.name := spaste('b',i);
    rec.children.c.name := spaste('c',i);
    rec.children.d.name := spaste('d',i);
    rec.children.a.children.a.name := 
      rec.children.b.children :=
      rec.children.c.children :=
      rec.children.d.children := spaste('const',i);
    mqs.meq('Create.Node',rec,wait_reply=F,silent=T); # wait_reply=((i%10)==0),silent=T); 
    mqs.resolve(rec.name,wait_reply=F,silent=T);
  }
  print 'getting node list';
  list := mqs.getnodelist();
  print 'got it'
  for( i in 1:len(list) )
  {
    print list[i];
  }
}

