if( any(argv == '-runtest' ) ) {
  root_path := './'
  meq_path  := './'
  app_path  := './'
} else {
  root_path := ''
  meq_path  := 'meq/'
  app_path  := 'appagent/'
}
  
default_debuglevels := [ MeqSolver=5 ];
                          
include spaste(app_path,'/app_defaults.g')
include spaste(root_path,'dmitypes.g')
include spaste(root_path,'octopussy.g')
include spaste(app_path,'/app_proxy.g')
include spaste(meq_path,'/meqserver.g')
include spaste(meq_path,'/meptable.g')

set_breakpoint := any(argv == '-bp');
                      
# inits a meqserver
const mqsinit := function (verbose=default_verbosity,debug=[=],gui=use_gui)
{
  global mqs;
  if( !is_record(mqs) )
  {
    mqs := meq.server(verbose=verbose,options="-d0 -meq:M:O:MeqServer",gui=gui);
    if( is_fail(mqs) )
      fail;
    mqs.init([output_col="PREDICT"],wait=F);
    if( !( is_boolean(debug) && !debug ) )
    {
      for( lev in field_names(default_debuglevels) )
        mqs.setdebug(lev,default_debuglevels[lev]);
      if( is_record(debug) )
        for( lev in field_names(debug) )
          mqs.setdebug(lev,debug[lev]);
    }
  }
}

const tile_test := function (stage=0,gui=use_gui,debug=[=],
                            verbose=default_verbosity)
{
  global mqs;
  mqsinit(debug=debug,verbose=verbose,gui=gui)
  mqs.meq('Clear.Forest');

  # define true parameter values. Solutions will start from zero
  mqs.meq('Debug.Set.Level',[debug_level=100]);
  
  mqs.meq('Create.Node',meq.parm('c',meq.polc(array([0.,1.,1.,-.5],2,2))));
  rec := meq.parm('x',meq.polc([0.,0.]),groups='Parm');
  rec.tiling := [time=4,freq=4];
  rec.cache_policy := 100;
  mqs.meq('Create.Node',rec);
  mqs.meq('Create.Node',meq.node('MeqCondeq','eq',[cache_policy=100],children="c x"));

  rec := meq.node('MeqSolver','solver',[cache_policy=100],children="eq");
  rec.num_iter := 5;
  rec.parm_group := hiid('Parm');
  rec.solvable := meq.solvable_list("x");
  mqs.meq('Create.Node',rec);

  # resolve children
  mqs.resolve('solver',wait_reply=T);
  
  for( n in "x c eq" )
    mqs.meq('Node.Publish.Results',[name=n]);
    
  if( any(argv=='-bp') )
  {
    mqs.meq('Debug.Set.Level',[debug_level=100]);
    mqs.meq('Node.Set.Breakpoint',[name='eq']);
  }
    

  # execute request on x and y parms to load polcs and get original values
  global cells,request,res;
  cells := meq.cells(meq.domain(0,1,0,1),num_freq=20,num_time=20);
  request := meq.request(cells,rqid=meq.rqid(),eval_mode=0);
  print 'executing',request;
  res := mqs.meq('Node.Execute',[name='x',request=request],T);
   
  res := mqs.meq('Save.Forest',[file_name='tile_test.forest.save']);

  # execute request on solver
  request := meq.request(cells,eval_mode=1);
  res := mqs.meq('Node.Execute',[name='solver',request=request],T);
}

tile_test(0);
