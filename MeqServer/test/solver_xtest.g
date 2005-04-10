if( any(argv == '-runtest' ) ) {
  root_path := './'
  meq_path  := './'
  app_path  := './'
} else {
  root_path := ''
  meq_path  := 'meq/'
  app_path  := 'appagent/'
}
  
default_debuglevels := [  MeqNode       =1,
                          MeqForest     =1,
                          MeqSink       =1,
                          MeqSpigot     =1,
                          MeqVisHandler =1,
                          MeqServer     =1,
                          meqserver     =1 ];
                          
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

const solver_test := function (stage=0,gui=use_gui,debug=[=],
                            verbose=default_verbosity,bp=set_breakpoint)
{
  global mqs;
  mqsinit(debug=debug,verbose=verbose,gui=gui)
  mqs.meq('Clear.Forest');

  # define true parameter values. Solutions will start from zero
  x0 := 2.; y0 := 1.;
  
  if( stage == 0 )
  {
    mqs.meq('Debug.Set.Level',[debug_level=100]);
    mqs.set_axes("freq time x y z");
    # use default record for parms
    mqs.meq('Create.Node',meq.parm('x',meq.polc(0),groups='Parm'));
    mqs.meq('Create.Node',meq.parm('y',meq.polc(0),groups='Parm'));
    mqs.meq('Create.Node',meq.parm('z',meq.polc(array([1,.5,.5,0],2,2),axis="x z"),groups='Parm'));
    mqs.meq('Create.Node',meq.node('MeqConstant','z1',[value=complex(0,0)]));
    mqs.meq('Create.Node',meq.node('MeqConstant','zero',[value=0.0]));
    mqs.meq('Create.Node',meq.node('MeqConstant','null'));
    #
    #mqs.meq('Create.Node',meq.parm('z',meq.polc(array([1,.5,.5,0],2,2),axis="x z"),groups='Parm'));
    #mqs.meq('Create.Node',meq.node('MeqConstant','z1',[value=complex(0,0)]));
  }
  else if( stage == 1 )
  {
    # use table for parms
    tablename := 'solver_test.mep';
    pt := meq.meptable(tablename,create=T);
    pt.putdef('x',0);
    pt.putdef('y',0);
    pt.done();
    x := meq.parm('x',groups='Parm');
    x.table_name := tablename;
    y := meq.parm('y',groups='Parm');
    y.table_name := tablename;
    mqs.meq('Create.Node',x);
    mqs.meq('Create.Node',y);
  }
  
  # stages 0 and 1: create forest
  if( stage != 2 )
  {
    cc := [ a1=1,b1=1,a2=1,b2=-1 ]; 
    cc.c1 := cc.a1*x0 + cc.b1*y0;
    cc.c2 := cc.a2*x0 + cc.b2*y0;
    for( f in field_names(cc) )
      mqs.meq('Create.Node',meq.parm(f,meq.polc(array([cc[f],1e-8,1e-8,0],2,2))));
    cc1 := [ noisefreq=10,noiselevel=.1 ];      
    for( f in field_names(cc1) )
      mqs.meq('Create.Node',meq.parm(f,meq.polc(cc1[f])));
    mqs.meq('Create.Node',meq.node('MeqMultiply','a1x',children="a1 x"));
    mqs.meq('Create.Node',meq.node('MeqMultiply','a2x',children="a2 x"));
    mqs.meq('Create.Node',meq.node('MeqMultiply','b1y',children="b1 y"));
    mqs.meq('Create.Node',meq.node('MeqMultiply','b2y',children="b2 y"));
    mqs.meq('Create.Node',meq.node('MeqAdd','lhs1',children="a1x b1y"));
    mqs.meq('Create.Node',meq.node('MeqAdd','lhs2',children="a2x b2y"));
    
    mqs.createnode(
      meq.node('MeqAdd','c1n',children=meq.list(
        'c1',
        meq.node('MeqMultiply','c1n1',children=meq.list(
          'noiselevel',
          meq.node('MeqSin','c1n1a',children=meq.list(
            meq.node('MeqMultiply','c1n1aa',children=meq.list(
              meq.node('MeqFreq','c1n1aaa'),'noisefreq'
            ))
          ))
        )),
        meq.node('MeqMultiply','c1n2',children=meq.list(
          'noiselevel',
          meq.node('MeqCos','c1n2a',children=meq.list(
            meq.node('MeqMultiply','c1n2aa',children=meq.list(
              meq.node('MeqTime','c1n2aaa'),'noisefreq'
            ))
          ))
        ))
      ))
    );
    mqs.createnode(
      meq.node('MeqAdd','c2n',children=meq.list(
        'c2',
        meq.node('MeqMultiply','c2n1',children=meq.list(
          'noiselevel',
          meq.node('MeqCos','c2n1a',children=meq.list(
            meq.node('MeqMultiply','c2n1aa',children=meq.list(
              meq.node('MeqFreq','c2n1aaa'),
              'noisefreq'
            ))
          ))
        )),
        meq.node('MeqMultiply','c2n2',children=meq.list(
          'noiselevel',
          meq.node('MeqSin','c2n2a',children=meq.list(
            meq.node('MeqMultiply','c2n2aa',children=meq.list(
              meq.node('MeqTime','c2n2aaa'),
              'noisefreq'
            ))
          ))
        ))
      ))
    );
    mqs.meq('Create.Node',meq.node('MeqCondeq','eq1',children="lhs1 c1n"));
    mqs.meq('Create.Node',meq.node('MeqCondeq','eq2',children="lhs2 c2n",
      step_children=meq.list(
        'math_test','tensor_test',
        meq.node('MeqMergeFlags','mergeflags',children=meq.list(
          meq.node('MeqAdd','sc_add',children=meq.list(
            meq.node('MeqAdd','sc_add1',children=meq.list(
              meq.node('MeqTime','sc_time'),
              meq.node('MeqMultiply','sc_2freq',children=meq.list(
                meq.node('MeqFreq','sc_freq'),
                meq.node('MeqConstant','sc_2',[value=2])
              )),
              meq.node('MeqGaussNoise','g1'),
              meq.node('MeqGaussNoise','g2',[stddev=3.0],children=meq.list(
                'sc_freq'
              )),
              meq.node('MeqAdd','ga3',children=meq.list(
                meq.node('MeqGaussNoise','g3',[stddev=3.0,axes_index=[0]]),
                'sc_time'
              ))
            )),
            meq.node('MeqFreq','sc_freq1')
          )),
          meq.node('MeqZeroFlagger','flag',[flag_bit=2,oper='LE'],children=meq.list(
            meq.node('MeqGaussNoise','g4')
          ))
        ))
      ))
    );
    mqs.meq('Create.Node',
      meq.node('MeqAdd','math_test',children=meq.list(
        meq.node('MeqMean','mtmean',children='g4'),
        meq.node('MeqMin','mtmin',children='g4'),
        meq.node('MeqMax','mtmax',children='g4'),
        meq.node('MeqSum','mtsum',children='g4'),
        meq.node('MeqProduct','mtprod',children='g4'),
        meq.node('MeqNElements','mtnelements',children='g4'),
        meq.node('MeqMean','mtmean1',children='flag'),
        meq.node('MeqMin','mtmin1',children='flag'),
        meq.node('MeqMax','mtmax1',children='flag'),
        meq.node('MeqSum','mtsum1',children='flag'),
        meq.node('MeqProduct','mtprod1',children='flag'),
        meq.node('MeqNElements','mtnelements1',children='flag')
      ))
    );
    
    mqs.meq('Create.Node',
      meq.node('MeqAdd','tensor_test',children=meq.list(
        meq.node('MeqConstant','matc1',[value=array([1.,2,3,1],2,2)]),
        meq.node('MeqConstant','matc2',[value=array([2.,1,1,3],2,2)]),
        meq.node('MeqConstant','matc3',[value=array([.5,-.5,.5,.5],2,2)]),
        meq.node('MeqMatrixMultiply','matm1',children="matc1 matc2"),
        meq.node('MeqMatrixMultiply','matm2',children=meq.list(
          meq.node('MeqMatrixMultiply','matm6',children=meq.list(
            'matc1',  
            meq.node('MeqConstant','matv1',[value=array([4.,2],2,1)])
          )),
          'matv2'
        )),
        meq.node('MeqMatrixMultiply','matm3',children=meq.list(
          'matc2',
          meq.node('MeqMatrixMultiply','matm4',children=meq.list(
            'matv1',
            meq.node('MeqConstant','matv2',[value=array([1.,2],1,2)])
          )),
          meq.node('MeqMatrixMultiply','matm5',children="matv2 matv1")
        )),
        meq.node('MeqMatrixMultiply','matm7',children=meq.list(
          'matc1',
          meq.node('MeqComposer','matcomp1',[dims=[2,2]],children="x zero zero y")
        )),
        meq.node('MeqMatrixMultiply','matm8',children=meq.list(
          'matc1',
          meq.node('MeqComposer','matcomp2',[dims=[2,2]],children="x null null y")
        )),
        meq.node('MeqMatrixMultiply','matm9',children=meq.list(
          'matc1',
          meq.node('MeqAdd','matadd2',children=meq.list(
            meq.node('MeqComposer','matcomp3',[dims=[2,2]],children="x null zero zero"),
            meq.node('MeqComposer','matcomp4',[dims=[2,2]],children="zero null null y"),
            meq.node('MeqComposer','matcomp5',[dims=[2,2]],children="zero zero null zero")
          ))
        ))
      ),step_children=meq.list(
        meq.node('MeqSelector','matsel1',[index=[2,3]],children=meq.list(
          meq.node('MeqMatrixMultiply','matm10',children=meq.list(
            meq.node('MeqConstant','matv4',[value=[0.,1,2,3]]),
            meq.node('MeqConstant','matv5',[value=array([2.,0,1,3],1,4)])
          ))
        )),
        meq.node('MeqSelector','matsel2',[index=[12]],children="matm10"),
        meq.node('MeqComposer','matcomp6',[dims=[3,4]],children=meq.list(
          meq.node('MeqSelector','matsel3',[index=[0,3]],children="matm10"),
          meq.node('MeqSelector','matsel4',[index=[4,0]],children="matm10"),
          meq.node('MeqConstant','matv6',[value=[3.,1,2,3]])
        )),
        meq.node('MeqSelector','matsel5',children="matm10"),
        meq.node('MeqSelector','matsel6',[index=[1,2,6],multi=T],children="matm10"),
        meq.node('MeqSelector','matsel7',[index=[1,2,20],multi=T],children="matm10"),
        meq.node('MeqSelector','matsel8',[index=[0,20,2]],children="matm10"),
        meq.node('MeqSelector','matsel9',[index=[0,20]],children="matm10"),
        meq.node('MeqPaster','matpaste1',[index=[0,2]],children="matm10 matv6"),
        meq.node('MeqPaster','matpaste2',[index=[2,0]],children="matm10 matv5"),
        meq.node('MeqPaster','matpaste3',[index=[2,0]],children="matm10 matv6"),
        meq.node('MeqPaster','matpaste4',[index=[2,2]],children="matm10 matv6"),
        meq.node('MeqPaster','matpaste5',[index=[2,3,7,9],multi=T],children="matm10 matv6"),
        meq.node('MeqPaster','matpaste6',[index=[2,3,7],multi=T],children="matm10 matv6"),
        meq.node('MeqPaster','matpaste7',[index=[2]],children="matm10 matm5"),
        meq.node('MeqTranspose','mattrans1',children="matv4"),
        meq.node('MeqTranspose','mattrans2',children="matv5"),
        meq.node('MeqTranspose','mattrans3',children="matm10"),
        meq.node('MeqTranspose','mattrans4',[conj=T],children=meq.list(
          meq.node('MeqToComplex','matcmpl1',children=meq.list(
            meq.node('MeqTranspose','mattrans5',children="matv5"),
            "matv4"
          ))
        ))
      ))
    );
    
    # create solver
    global rec;
    rec := meq.node('MeqSolver','solver',children="eq1 eq2");
    rec.default := [ num_iter = 5 ];
    rec.parm_group := hiid('Parm');
    rec.solvable := meq.solvable_list("x y");
    mqs.meq('Create.Node',rec);

    # resolve children
    mqs.resolve('solver',wait_reply=T);
    mqs.resolve('z',wait_reply=T);
    mqs.resolve('z1',wait_reply=T);

#    for( n in "eq1 lhs1 c1 a1x x" )
    for( n in "x y z eq1 eq2" )
      mqs.meq('Node.Publish.Results',[name=n]);
    
    # execute request on z to try out new-style cells
    global dom1,cells1,request1,res1;
    dom1 := meq.domain(axis="x y z",start=[0,0,0],end=[1,1,1])
    cells1 := meq.cells(dom1,ncells=[2,3,4]);
    request1 := meq.request(cells1,rqid=meq.rqid(),calc_deriv=0);
    print 'executing',request1;
    res1 := mqs.meq('Node.Execute',[name='z',request=request1],T);
    res1 := mqs.meq('Node.Execute',[name='z1',request=request1],T);

    # execute request on x and y parms to load polcs and get original values
    global cells,request,res;
    cells := meq.cells(meq.domain(0,1,0,1),num_freq=4,num_time=3);
    request := meq.request(cells,rqid=meq.rqid(),calc_deriv=0);
    print 'executing',request;
    res := mqs.meq('Node.Execute',[name='x',request=request],T);
    res := mqs.meq('Node.Execute',[name='y',request=request],T);
   
    res := mqs.meq('Save.Forest',[file_name='solver_test.forest.save']);
  }
  else # stage 2: simply load the forest
  {
    res := mqs.meq('Load.Forest',[file_name='solver_test.forest.save']);
    mqs.meq('Node.Clear.Cache',[name='solver',recursive=T]);
    mqs.meq('Node.Publish.Results',[name='x']);
    mqs.meq('Node.Publish.Results',[name='y']);
  }
  global stx0,stx1,sty0,sty1,xs,ys;
  
  stx0 := mqs.getnodestate('x');
  sty0 := mqs.getnodestate('y');
  if( stx0.funklet.coeff != 0 || sty0.funklet.coeff != 0 )
  {
    print '======================= stage ',stage,': init failed';
    return F;
  }
  # set breakpoint if requested
  if( bp )
  {
    mqs.meq('Debug.Set.Level',[debug_level=100]);
    mqs.meq('Node.Set.Breakpoint',[name='eq1']);
  }
  
  # execute request on solver
  global cells,request,res;
  cells := meq.cells(meq.domain(0,1,0,1),num_freq=4,num_time=3);
  request := meq.request(cells,calc_deriv=1);
  res := mqs.meq('Node.Execute',[name='solver',request=request],T);
  print res;
  
  # get new values of x and y
  stx1 := mqs.getnodestate('x');
  sty1 := mqs.getnodestate('y');

  xs := stx1.funklet.coeff;
  ys := sty1.funklet.coeff;

  print sprintf("Expected values: %10.10f %10.10f",x0,y0);
  print sprintf("Original values: %10.10f %10.10f",stx0.funklet.coeff,sty0.funklet.coeff);
  print sprintf("Solution:        %10.10f %10.10f",xs,ys);

  if( abs(x0-xs) < 1e-2*abs(x0) && abs(y0-ys) < 1e-2*abs(y0) )
  {
    print '======================= stage ',stage,': solve succeeded';
    return T;
  }

  print '======================= stage ',stage,': solve failed';
  return F;
}

if( any(argv == '-runtest' ) )
{
  global use_suspend,use_nostart;
  use_suspend := use_nostart := F;
  for( stage in 0:2 )
    if( !solver_test(stage=stage,gui=F,debug=[MeqNode=5],verbose=0) )
      exit 1;
  exit 0;
}
