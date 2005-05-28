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



const create_constants := function()
{
    mqs.createnode(meq.node('MeqConstant','one',[value=1.0]));
    mqs.createnode(meq.node('MeqConstant','half',[value=0.5]));

# create constant parameters for CLAR beam nodes
# eventually these should be a function of frequency
# HPBW of 3 arcmin = 0.00087266 radians; 1145.9156 = 1 / 0.00087266
    mqs.createnode(meq.node('MeqConstant','width_l',[value=1145.9156]));
    mqs.createnode(meq.node('MeqConstant','width_m',[value=1145.9156]));
    mqs.createnode(meq.node('MeqSqr','width_l_sq', children='width_l'));
    mqs.createnode(meq.node('MeqSqr','width_m_sq', children='width_m'));
    mqs.createnode(meq.node('MeqConstant','ln_16',[value=-2.7725887]));

}




# creates all source-related nodes and subtrees:
#   'stokesI':          flux
#   'ra' 'dec':         source position
#   'lmn','n':          LMN coordinates, N coordinate
# src specifies the source suffix ('' for none)
const create_source_subtrees := function (src, mep_table_name='')
{
    print 'in create_source_subtrees with src ', src
    global ms_timerange, ms_freqranges;

    # 0th order frequency-dependence, 2nd order time dependence
    polc_i_array := array(as_double(0),src.Iorder+1,1);
    polc_i_array[1,1] := src.I;
    
    polc_q_array := array(as_double(0),1,1);
    polc_q_array[1,1] := src.Q;
    
    polc_u_array := array(as_double(0),1,1);
    polc_u_array[1,1] := src.U;
    
    polc_v_array := array(as_double(0),1,1);
    polc_v_array[1,1] := src.V;
    
    #fmin := ms_freqranges[1][1];
    #fmax := ms_freqranges[2][1];
    #tmin := ms_timerange[1];
    #tmax := ms_timerange[2];
    polc_scale  := [1/10000.0, 1e-6];
    polc_offset := [4.47204e9,1.175e9];
    polc_i := meq.polc(polc_i_array,scale=polc_scale, offset=polc_offset);#,domain=meq.domain(fmin,fmax,tmin,tmax)); # domain: entire dataset
    polc_q := meq.polc(polc_q_array,scale=polc_scale, offset=polc_offset);#,domain=meq.domain(fmin,fmax,tmin,tmax)); # domain: entire dataset
    polc_u := meq.polc(polc_u_array,scale=polc_scale, offset=polc_offset);#,domain=meq.domain(fmin,fmax,tmin,tmax)); # domain: entire dataset
    polc_v := meq.polc(polc_v_array,scale=polc_scale, offset=polc_offset);#,domain=meq.domain(fmin,fmax,tmin,tmax)); # domain: entire dataset
    
    print polc_i;
    # meq.parm(), meq.node() return init-records
    # mqs.createnode() actually creates a node from an init-record.
    
    stokes_I_node := meq.parm(fq_name('stokes_i',src.name),polc_i,groups="a");
    stokes_Q_node := meq.parm(fq_name('stokes_q',src.name),polc_q,groups="a");
    stokes_U_node := meq.parm(fq_name('stokes_u',src.name),polc_u,groups="a");
    stokes_V_node := meq.parm(fq_name('stokes_v',src.name),polc_v,groups="a");
    if( mep_table_name != ''){
        stokes_I_node.table_name := mep_table_name;
        stokes_Q_node.table_name := mep_table_name;
        stokes_U_node.table_name := mep_table_name;
        stokes_V_node.table_name := mep_table_name;
    }
    
    IQUV_node := meq.node('MeqComposer', fq_name('IQUV',src.name),
                          [link_or_create=T,dims=[2,2]],
                          children=meq.list(stokes_I_node,
                                            stokes_Q_node,
                                            stokes_U_node,
                                            stokes_V_node));
    mqs.createnode(IQUV_node);

    # COHERENCY COMPUTATION
    xx_node  := meq.node('MeqAdd', fq_name('xx',src.name),[link_or_create=T],
                         children= meq.list(stokes_I_node.name, stokes_Q_node.name));
    yy_node  := meq.node('MeqAdd',  fq_name('yy', src.name),
                         [link_or_create=T],
                         children=meq.list(stokes_I_node.name, stokes_Q_node.name));
    yx_node  := meq.node('MeqToComplex', fq_name('yx',src.name),
                         [link_or_create=T],
                         children=meq.list(stokes_U_node.name, stokes_V_node.name));
    xy_node  := meq.node('MeqConj', fq_name('xy',src.name),
                         [link_or_create=T],
                         children=meq.list(yx_node.name));
    twice_coherency_node := meq.node('MeqComposer', fq_name('twice_coherency', src.name),
                              [link_or_create=T,dims=[2,2]],
                              children=meq.list(xx_node, xy_node, yx_node, yy_node));
    
    coherency_node := meq.node('MeqMatrixMultiply', fq_name('coherency', src.name),
                              [link_or_create=T],
#                             children=meq.list(twice_coherency_node, 'half'));
                              children=meq.list(twice_coherency_node, 'one'));
    mqs.createnode(coherency_node);

    # note the nested-record syntax here, to create child nodes implicitly
    mqs.createnode(meq.node('MeqLMN',
                            fq_name('lmn',src.name),
                            children=[
                                      ra_0  ='ra0',
                                      dec_0 ='dec0',
                                      ra    =meq.parm(fq_name('ra',src.name),src.ra,
                                                      groups="a"),
                                      dec   =meq.parm(fq_name('dec',src.name),src.dec,
                                                      groups="a")]));
    mqs.createnode(meq.node('MeqSelector',fq_name('l',src.name),[index=1],
                            children=fq_name("lmn",src.name)));
    mqs.createnode(meq.node('MeqSelector',fq_name('m',src.name),[index=2],
                            children=fq_name("lmn",src.name)));
    mqs.createnode(meq.node('MeqSelector',fq_name('n',src.name),[index=3],
                            children=fq_name("lmn",src.name)));
}



const create_station_subtrees := function (st)
{
  print 'in create_station_subtrees for st ', st
  global ms_antpos; # station positions from MS
  pos := ms_antpos[st];

  # create nodes used to calculate AzEl of field centre as seen
  # from a specific station

  # first create AzEl node for field_centre as seen from this station
  defrec_azel := meq.node('MeqAzEl',fq_name('AzEl_fc',st),children=[
                     ra ='ra0', dec ='dec0',
                     x = meq.parm(fq_name('x',st),pos.x),
                     y = meq.parm(fq_name('y',st),pos.y),
                     z = meq.parm(fq_name('z',st),pos.z)])
  mqs.createnode(defrec_azel);
  # then get azimuth and elevation of FC as seen from this station as separate
  # elements
  mqs.createnode(meq.node('MeqSelector',fq_name('AzEl_az0',st),[index=1],
                            children=fq_name('AzEl_fc',st)));
  mqs.createnode(meq.node('MeqSelector',fq_name('AzEl_el0',st),[index=2],
                            children=fq_name('AzEl_fc',st)));

  # get sine of elevation of field centre - used later to determine CLAR
  # beam broadening
  mqs.createnode(meq.node('MeqSin',fq_name('sine_el',st),children=fq_name('AzEl_el0',st)));
  # square this sine value
  mqs.createnode(meq.node('MeqSqr',fq_name('sine_el_sq',st),
                  children=fq_name('sine_el',st)));
}






# builds an init-record for a "dft" tree for one station (st)
const sta_source_dft_tree := function (st,src=[=])
{
  print 'in sta_source_dft_tree for st src ', st, ' ', src
  global ms_antpos; # station positions from MS
  global mepuvw;    # MEP table with UVWs
  pos := ms_antpos[st];
  print 'positions ', pos

# we first build up the mathematical expression of a CLAR voltage
# pattern for a source using the equations
# log16 =  (-1.0) * log(16.0);
# L,M give direction cosines of the source wrt field centre in
# AzEl coordinate frame
# L_gain = (L * L) / (widthl_ * widthl_);
# sin_factor = sqr(sin(field centre elevation));
# M_gain = (sin_factor * M * M ) / (widthm_ * widthm_);
# voltage_gain = sqrt(exp(log16 * (L_gain + M_gain)));

# see the create_station_subtrees function for creation
# of nodes used to compute Az, El of field centre

  # create AZEl node for source as seen from this station
  defrec_azel := meq.node('MeqAzEl',fq_name('az_el',st,src.name),
                  [link_or_create=T],
                  children=[
                  x = fq_name('x',st),
                  y = fq_name('y',st),
                  z = fq_name('z',st),
                  ra    = fq_name('ra',src.name),
                  dec   = fq_name('dec',src.name)])
  az_AzEl := meq.node('MeqSelector',fq_name('az_AzEl',st,src.name),[index=1],
                            children=meq.list(defrec_azel));
  el_AzEl := meq.node('MeqSelector',fq_name('el_AzEl',st,src.name),[index=2],
                            children=meq.list(defrec_azel));

  # do computation of LMN of source wrt field centre in AzEl frame
  lmn_azel := meq.node('MeqLMN',
                      fq_name('lmn_azel',st,src.name),
		      [link_or_create=T],
                      children=[
                                 ra_0  =fq_name('AzEl_az0',st),
                                 dec_0 =fq_name('AzEl_el0',st),
                                 ra    = az_AzEl,
                                 dec   = el_AzEl]);
  l_azel := meq.node('MeqSelector',fq_name('l_azel',st,src.name),[index=1],
                            children=meq.list(lmn_azel));
  m_azel := meq.node('MeqSelector',fq_name('m_azel',st,src.name),[index=2],
                            children=meq.list(lmn_azel));
  n_azel := meq.node('MeqSelector',fq_name('n_azel',st,src.name),[index=3],
                            children=meq.list(lmn_azel));
			    
  # compute CLAR voltage gain as seen for this source at this station
  # first square L and M
  l_sq := meq.node('MeqSqr',fq_name('l_sq',st,src.name),
                            children=meq.list(l_azel));
  m_sq := meq.node('MeqSqr',fq_name('m_sq',st,src.name),
                            children=meq.list(m_azel));

  # then multiply by width squared, for L, M
  l_vpsq := meq.node('MeqMultiply',fq_name('l_vpsq',st,src.name),
                            children=meq.list(l_sq,'width_l_sq'));
  m_vpsq := meq.node('MeqMultiply',fq_name('m_vpsq',st,src.name),
                            children=meq.list(m_sq,'width_m_sq'));

  # for M, adjust by sin of elevation squared
  m_vpsq_sin := meq.node('MeqMultiply',fq_name('m_vpsq_sin',st,src.name),
                            children=meq.list(m_vpsq,fq_name('sine_el_sq',st)));

  # add L and M gains together
  l_and_m_sq := meq.node('MeqAdd',fq_name('l_and_m_sq',st,src.name),
                            children=meq.list(l_vpsq, m_vpsq_sin));
  # then multiply by log 16
  v_gain := meq.node('MeqMultiply',fq_name('v_gain',st,src.name),
                            children=meq.list(l_and_m_sq, 'ln_16'));
  # raise to exponent
  exp_v_gain := meq.node('MeqExp',fq_name('exp_v_gain',st,src.name),
                          [link_or_create=T],
                          children=meq.list(v_gain));

  # and take square root to get voltage pattern
  # see below where Jones matrices are constructed for
  # actual instantiation of this node
  # v_pattern := meq.node('MeqSqrt',fq_name('v_pattern',st,src.name),
  #                       children=meq.list(exp_v_gain));

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
  print 'we are here pos x y z = ',pos.x,' ', pos.y,' ',pos.z
  dmi.add_list(uvwlist,
            meq.node('MeqUVW',fq_name('uvw',st),children=[
                         x = fq_name('x',st),
                         y = fq_name('y',st),
                         z = fq_name('z',st),
                         ra = 'ra0',dec = 'dec0',
                         x_0='x0',y_0='y0',z_0='z0' ]));
                        
  uvw := meq.node('MeqReqSeq',fq_name('uvw.seq',st),[result_index=1,
                  link_or_create=T],children=uvwlist);
    
  # builds an init-rec for a node called 'dft.N' with two children: 
  # lmn and uvw.N
  n_minus_one := meq.node('MeqSubtract', fq_name('nminusone', src.name),
                          [link_or_create=T],
                          children=meq.list(fq_name('n', src.name),
                                            'one'));
  
  lmn_minus_one := meq.node('MeqComposer', fq_name('lmnminusone', src.name),
                            [link_or_create=T],
                            children=meq.list(fq_name('l', src.name),
                                              fq_name('m', src.name),
                                              n_minus_one));
  dft := meq.node('MeqVisPhaseShift',fq_name('dft0',st,src.name),
                  [link_or_create=T],
                  children=[lmn = lmn_minus_one, uvw=uvw ]);


# add antenna gains/phases
  source_jones_list := dmi.list();
  stat_jones_list   := dmi.list();
  for( i in 1:2){
      for( j in 1:2){
          value := as_double(i==j);
          elem := spaste(i,j);
	  amp_node := 0
          if (value == 1) 
             # use voltage pattern of CLAR
              amp_node := meq.node('MeqSqrt',fq_name('JA',st,src.name,elem),
                          children=meq.list(exp_v_gain)); 
          else			  
            amp_node := meq.parm(fq_name('JA',st,src.name,elem),value,
                               groups="a");
          amp_node.table_name := 'my.mep';
          amp_node.link_or_create := T;

          phase_node :=meq.parm(fq_name('JP',st, src.name,elem),0.0, groups="a");
          phase_node.table_name := 'my.mep';
          phase_node.link_or_create := T;

#         print 'parameters for fq_name : J ', st, ' ', src.name, ' ', elem
          source_jones_elem := meq.node('MeqPolar',fq_name('J',st,src.name,elem),[link_or_create=T],
                   children=meq.list(amp_node, phase_node) );
  
          dmi.add_list(source_jones_list, source_jones_elem);
          
          stat_amp_node := meq.parm(fq_name('GA',st,elem),value,groups="a");
          stat_amp_node.table_name := 'my.mep';
          stat_amp_node.link_or_create:=T;

          stat_phase_node :=meq.parm(fq_name('GP',st,elem),0.0,groups="a");
          stat_phase_node.table_name := 'my.mep';
          stat_phase_node.link_or_create := T;

          stat_jones_elem := meq.node('MeqPolar',fq_name('G',st,elem),[link_or_create=T],
                             children=meq.list(stat_amp_node, stat_phase_node) );
          dmi.add_list(stat_jones_list, stat_jones_elem);
      }
  }
  source_stat_jones := meq.node('MeqComposer', fq_name('J',st,src.name),
                           [link_or_create=T,dims=[2,2]],
                           children=source_jones_list);
                           
  stat_jones := meq.node('MeqComposer', fq_name('G',st),
                         [link_or_create=T,dims=[2,2]],
                         children=stat_jones_list);
                         
  return meq.node('MeqMatrixMultiply',fq_name('dft',st,src.name),[link_or_create=T],
                    children=meq.list(stat_jones, source_stat_jones,dft));
}




 


# builds an init-record for a "dft" tree for source 'src' and two stations (st1,st2)
const ifr_source_predict_tree := function (st1,st2,src=[=])
{
    print 'in ifr_source_predict_tree for stns and src ', st1, ' ', st2, ' ', src
    print 'ifr_source_predict_tree calling sta_source_dft_tree for stn source ',st1,' ', src
    dft1 := sta_source_dft_tree(st1, src);
    print 'ifr_source_predict_tree calling sta_source_dft_tree for stn source ',st2,' ', src
    dft2 := sta_source_dft_tree(st2, src);
    
    conj_st2 := meq.node('MeqTranspose', fq_name('pointsource_conj', st2,src.name),
                         [link_or_create=T,conj=T],
                         children=meq.list(dft2));
    
    one_over_n  := meq.node('MeqDivide', fq_name('one_over_n',src.name),
                         [link_or_create=T],
                         children=meq.list('one',
                                           fq_name('n', src.name)));
    
    predict:=meq.node('MeqMatrixMultiply', fq_name('predict',src.name,st1,st2),
                      [link_or_create=T],
                      children=meq.list(dft1,fq_name('coherency', src.name),
                      conj_st2, one_over_n));
    return predict;
}


# builds an init-record for a sum of "dft" trees for all sources and st1,st2
const solve_ifr_predict_tree := function (st1,st2,sources)
{
  if( len(sources) == 1 )
    return ifr_source_predict_tree(st1,st2,sources);
  list := dmi.list();
  for( s in sources ) 
    dmi.add_list(list,ifr_source_predict_tree(st1,st2,s));
  return meq.node('MeqAdd',fq_name('predict',st1,st2),[cache_num_active_parents=1],children=list);
}



# builds an init-record for a sum of "dft" trees for all sources and st1,st2
const ifr_predict_tree := function (st1,st2,sources, one=T)
{
  print 'in ifr_predict_tree st1 st2 sources ', st1, st2, sources
  if( one ){
    print 'ifr_predict_tree calling ifr_source_predict_tree for stns sources ', st1,' ',st2,' ', sources
    return ifr_source_predict_tree(st1,st2,sources);
  }
  list := dmi.list();
  for( s in sources )  {
    print 'ifr_predict_tree calling ifr_source_predict_tree for source ', s
    dmi.add_list(list,ifr_source_predict_tree(st1,st2,s));
  }
  return meq.node('MeqAdd',fq_name('predict',st1,st2),[cache_num_active_parents=1],children=list);
}












# creates nodes shared among trees: source parms, array center (x0,y0,z0)
const make_shared_nodes := function (sources=[=],
                                     mep_table_name='')
{
  print 'creating shared nodes' 
  # create constants
  create_constants();
  print 'created constants' 
  
  global ms_phasedir;
  ra0  := ms_phasedir[1];  # phase center
  dec0 := ms_phasedir[2];
  # setup field centre coodinate parameters
  create_common_parms(ra0,dec0);
  print 'created field centre parameters' 

  # setup zero position
  global ms_antpos;
  names := "x0 y0 z0";
  for( i in 1:3 )
    mqs.createnode(meq.node('MeqConstant',names[i],[value=ms_antpos[1][i]]));
  print 'created X0, Y0, Z0 antenna nodes'

  # create parameters for stations
  for( i in 1:len(ms_antpos))
    print create_station_subtrees(i);
  print 'called create_station_subtrees'

  
  for( src in sources ) {
    print src.name;
    print create_source_subtrees(src, mep_table_name);
  }
  print 'called create_source_subtrees'
  print ' exiting make_shared_nodes'

}













# builds a predict tree for stations st1, st2
const make_predict_tree := function (st1,st2,sources)
{
  print 'in make_predict_tree for st1 st2 sources ', st1, ' ', st2, ' ', sources
  sinkname := fq_name('sink',st1,st2);
  if( len(sources) == 1 )
    pred := ifr_predict_tree(st1,st2,sources,T);
  else 
  {
    list := dmi.list();
    for( s in sources ) 
      print '*** calling ifr_predict_tree for source ', s
      dmi.add_list(list,ifr_predict_tree(st1,st2,s,T));
    pred := meq.node('MeqAdd',fq_name('predict',st1,st2),children=list);
  }
  # create a sink
  one := T
  if (len(sources) > 1)
    one := F
  print '*** creating Meqsink '
  mqs.createnode(meq.node('MeqSink',sinkname,
                         [ output_col      = 'PREDICT',   # init-rec for sink
                           station_1_index = st1,
                           station_2_index = st2,
                           corr_index      = [1],
                           flag_mask       = -1 ],
                           children=dmi.list(
                            ifr_predict_tree(st1,st2,sources,one)
                           )));
  print '*** called ifr_predict_tree for source ', s
  return sinkname;
}










# builds a read-predict-subtract tree for stations st1, st2
const make_subtract_tree := function (st1,st2,sources)
{
  sinkname := fq_name('sink',st1,st2);
  
  # create a sink & subtree attached to it
  # note how meq.node() can be passed a record in the third argument, to specify
  # other fields in the init-record
  mqs.createnode(
    meq.node('MeqSink',sinkname,
                         [ output_col      = '',
                           station_1_index = st1,
                           station_2_index = st2,
                           corr_index      = [1],
                           flag_mask        = -1 ],
                         children=meq.list(
      meq.node('MeqSubtract',fq_name('sub',st1,st2),children=meq.list(
          meq.node('MeqSpigot',fq_name('spigot',st1,st2),[
            station_1_index=st1,
            station_2_index=st2,
            flag_bit=4,
            input_column='DATA',
            cache_policy=-10]),
        ifr_predict_tree(st1,st2,sources)
      ))
    ))
  );
  return sinkname;
}










# builds a solve tree for stations st1, st2
const make_solve_tree := function (st1,st2,sources=[=],subtract=F,flag=F)
{
  print 'in make_solve_tree st1, st2, sources ', st1, ' ', st2, ' ', sources
  sinkname := fq_name('sink',st1,st2);
  predtree := solve_ifr_predict_tree(st1,st2,sources);
  predname := predtree.name;
  mqs.createnode(predtree);
  
  spigot_node:=meq.node('MeqSpigot',fq_name('spigot',st1,st2),
                        [station_1_index=st1,
                         station_2_index=st2,
                         flag_bit=4,
                         link_or_create=T,
                         input_column='DATA']);
  
  #print spigot_node;
  #print xx_node;
  #print yy_node;
  #print observed_i_node;
  #exit
  # create condeq tree (solver will plug into this)
  mqs.createnode(meq.node('MeqCondeq',fq_name('ce',st1,st2),
                          children=meq.list(predname, spigot_node)
                          )
                 );
  # create subtract sub-tree
  if( subtract )
  {
    subname := fq_name('sub',st1,st2);
    mqs.createnode(meq.node('MeqSubtract',subname,
                      children=[fq_name('spigot',st1,st2),predname]));
    if( !is_boolean(flag) )
    {
      datanodename:=fq_name('mof',st1,st2);
      mqs.createnode(
        meq.node('MeqMergeFlags',datanodename,children=meq.list(
          subname,
          meq.node('MeqZeroFlagger',fq_name('zf',st1,st2),[flag_bit=2,oper='GE',force_output=T],children=meq.list(
            meq.node('MeqSubtract',fq_name('zfsub',st1,st2),children=meq.list(
              meq.node('MeqAbs',fq_name('zfabs',st1,st2),children=subname),
              meq.node('MeqConstant',fq_name('of1threshold',st1,st2),[value=flag])
            ))
          ))
        ))
      );
    }
    else
      datanodename := subname;
  }
  else
    subname := fq_name('spigot',st1,st2);
  
  # create root tree (plugs into solver & subtract)     
  mqs.createnode(
    meq.node('MeqSink',sinkname,[ output_col      = '',
                                  station_1_index = st1,
                                  station_2_index = st2,
                                  corr_index      = [1], 
                                  flag_mask       = -1 ],children=meq.list(
      meq.node('MeqReqSeq',fq_name('seq',st1,st2),[result_index=2],
        children=['solver',datanodename])
   ))
 );

  return sinkname;
}











# reads antenna positions and phase center from MS,
# puts them into global variables
const get_ms_info := function (msname='test.ms',uvw=T)
{
  global ms_phasedir,ms_antpos, ms_timerange, ms_freqranges;
  
  ms := table(msname);
  msant := table(ms.getkeyword('ANTENNA'));
  pos := msant.getcol('POSITION');
  print 'ant pos ', pos
  num_ant := msant.nrows();
  msant.done();
  
  tcol := ms.getcol('TIME');
  t_min := min(tcol) - 1;
  t_max := max(tcol) + 1;
  ms_timerange := [t_min, t_max];
  tcol := F;

  freqtab := table(ms.getkeyword('SPECTRAL_WINDOW'));
  num_chan := freqtab.getcol('NUM_CHAN');
  print 'num chan ', num_chan
  chan_freqs := freqtab.getcol('CHAN_FREQ');
  print 'chan freqs ', chan_freqs
  num_spw := freqtab.nrows();
  print 'num spw ', num_spw;
  print 'CHAN_FREQ SHAPE: ', shape(chan_freqs);
  ms_freqranges := array(0.0,2,num_spw);
  for( i in 1:num_spw){
      print i;
      ms_freqranges[,i] := [min(chan_freqs[,i]), max(chan_freqs[,i])];
  }
  freqtab.close();

  time0 := ms.getcell('TIME',1);
  
  # convert position to x y z
  ms_antpos := [=];
  for(i in 1:len(pos[1,]))
    ms_antpos[i] := [ x=pos[1,i],y=pos[2,i],z=pos[3,i] ];
  print 'ms_antpos ', ms_antpos
    
  msfld := table(ms.getkeyword('FIELD'));
  ms_phasedir := msfld.getcol('PHASE_DIR');
  print 'ms phasedir ',ms_phasedir
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













# predict=T:  predict tree only (writes predict to output column)
# subtract=T: predict+subtract trees (writes residual to output column)
# solve=T,subtract=T: solve+subtract trees (writes residual to output column)
# solve=T,subtract=F: solve but no subtract
#
# run=F: build trees and stop, run=T: run over the measurement set
const do_test := function (predict=F,subtract=F,solve=F,run=T,
    flag=F,                         # supply threshold to flag output
    msname='test.ms',
    stset=1:4,                      # stations for which to make trees
    sources=[=],
    solve_fluxes=F,
    solve_gains=F,
    solve_phases=F,
    mep_table_name='',
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
    print 'outcol is ', outcol
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

# set cache to 'always on'
  mqs.meq('Set.Forest.State',[state=[cache_policy=20]])

  mqs.meq('Clear.Forest',[=]);
  # load forest if asked
  if( load )
      mqs.meq('Load.Forest',[file_name=load]);
  else # else build trees
  {
      # create common nodes (source parms and such)
      
      make_shared_nodes(sources, mep_table_name);
      
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
          solvables := "";
          if(solve_fluxes){
              for(source in sources){
                  solvables := [solvables, fq_name('stokes_i', source.name)];
              }
          }
          if( solve_gains ){
              for( st in stset[1:len(stset)] ){
                  solvables := [solvables,fq_name('GA',st,'11')];
                  solvables := [solvables,fq_name('GA',st,'22')];
              }
          }

          if( solve_phases ){
              for( st in stset[2:len(stset)] ){
                  solvables := [solvables,fq_name('GP',st,'11')];
                  solvables := [solvables,fq_name('GP',st,'22')];
              }
          }

          print solvables;

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
          for( s in sources )
          {
              mqs.meq('Node.Publish.Results',[name=fq_name("stokes_i",s.name)]);
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
                      rootnodes := [rootnodes,
                                    make_solve_tree(st1,st2,sources=sources,
                                                    subtract=subtract,
                                                    flag=flag)];
                      if( publish>1 )
                          mqs.meq('Node.Publish.Results',
                                  [name=fq_name('ce',st1,st2)]);
                  }
                  else if( subtract )
                      rootnodes := [rootnodes,
                                    make_subtract_tree(st1,st2,sources)];
                  else {
                      print '***** predicting ****** for stations ', st1, ' ', st2
                      rootnodes := [rootnodes,
                                    make_predict_tree(st1,st2,sources)];
                  }
                  if( publish>2 )
                      mqs.meq('Node.Publish.Results',
                              [name=fq_name('predict',st1,st2)]);
              }
      # resolve children on all root nodes
      # print 'Root nodes are: ',rootnodes;
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
#    mqs.meq('Node.Publish.Results',[name='GP.12']);
#    mqs.meq('Node.Publish.Results',[name='G.12']);
#    mqs.meq('Node.Publish.Results',[name='modified_i.3C343']);
#    mqs.meq('Node.Publish.Messages',[name='x.1']);
#    mqs.meq('Node.Publish.Messages',[name='dft0.3D343_1.1']);
#    mqs.meq('Node.Publish.Results',[name=fq_name('dft.b',4,8)]);
#    mqs.meq('Node.Publish.Results',[name=fq_name('U',8)]);
  }
  
  if( set_breakpoint ){
      mqs.meq('Node.Set.Breakpoint',[name='solver']);
      mqs.meq('Debug.Set.Level',[debug_level=100]);
  }

  # run over MS
  if( run )
    do_run();
}

const do_run := function ()
{
  # activate input and watch the fur fly  
  global inputrec,outputrec;
  mqs.init([mandate_regular_grid=F,output_col='PREDICT'],input=inputrec,output=outputrec); 
}




#--------------------------------------------
#
# Source flux fitting on raw data
#
#--------------------------------------------
source_flux_fit_no_calibration := function()
{
    global inputrec, outputrec,solver_defaults,msname,mepuvw;
    global outcol;
    global use_initcol;

    use_initcol := T;       # initialize output column with zeroes

    msname := 'my.ms';
    mep_table_name := 'my.mep';

    # Clear MEP table
    meptable := table(mep_table_name, readonly=F);
    nrows := meptable.nrows();
    meptable.removerows(1:nrows);
    meptable.done();

    mepuvw := F;
    filluvw := any(argv=='-filluvw');
    solve_fluxes:= T;#any(argv == '-fluxes');
    solve_gains := any(argv=='-gains');
    solve_phases := any(argv=='-phases');
    set_breakpoint := any(argv=='-bp');
    
    src_test_1 := [name="src_1",I=1.0, Q=0.0, U=0.0, V=0.0,
                    Iorder=3, ra=0.030272885, dec=0.575762621]

    src_test_2   := [name="src_2",  I=1.0, Q=0.0, U=0.0, V=0.0,
                    Iorder=3, ra=0.0306782675, dec=0.575526087]

    src_test_3 := [name="src_3",I=1.0, Q=0.0, U=0.0, V=0.0,
                    Iorder=3, ra=0.0308948646, dec=0.5762655]

    src_test_4 := [name="src_4",I=1.0, Q=0.0, U=0.0, V=0.0,
                    Iorder=3, ra=0.0308043705, dec=0.576256621]

    src_test_5 := [name="src_5",I=1.0, Q=0.0, U=0.0, V=0.0,
                    Iorder=3, ra=0.030120036, dec=0.576310965]

    src_test_6 := [name="src_6",I=1.0, Q=0.0, U=0.0, V=0.0,
                    Iorder=3, ra=0.0301734016, dec=0.576108805]

    src_test_7 := [name="src_7",I=1.0, Q=0.0, U=0.0, V=0.0,
                    Iorder=3, ra=0.0302269161, dec=0.576333355]

    src_test_8 := [name="src_8",I=1.0, Q=0.0, U=0.0, V=0.0,
                    Iorder=3, ra=0.0304215356, dec=0.575777607]

    src_test_9 := [name="src_9",I=1.0, Q=0.0, U=0.0, V=0.0,
                    Iorder=3, ra=0.0307416105, dec=0.576347166]

    src_test_10 := [name="src_10",I=1.0, Q=0.0, U=0.0, V=0.0,
                    Iorder=3, ra=0.0306878027, dec=0.575851951]

    src_test_11 := [name="src_11",I=1.0, Q=0.0, U=0.0, V=0.0,
                    Iorder=3, ra=0.030272885, dec=0.575762621]

    sources := [a= src_test_1,
#               b= src_test_11]
                b= src_test_2,
                c= src_test_3,
                d= src_test_4,
                e= src_test_5,
                f= src_test_6,
                g= src_test_7,
                h= src_test_8,
                i= src_test_9,
                j= src_test_10]

    print sources;
    
# fill UVW parms from MS if requested
    if( mepuvw )
    {
        include 'meq/msuvw_to_mep.g'
            mepuvw := msname ~ s/.ms/.mep/;
        if( filluvw )
            print 'calling fill_uvw'
            fill_uvw(msname,mepuvw);
            print 'passed fill_uvw'
    }
    else
        mepuvw := F;
    
    outcol := 'PREDICTED_DATA';
    solver_defaults := [ num_iter=6,save_funklets=T,last_update=T ];
    
    inputrec := [ ms_name = msname,data_column_name = 'DATA',
                 tile_size=1500,# clear_flags=T,
                 selection = [ channel_start_index=1,
                              channel_end_index=1 ,
                              selection_string=''] ];
    
    outputrec := [ write_flags=F,predict_column=outcol ];
    
    print 'calling do_test'
#   res := do_test(msname=msname,solve=T,subtract=T,run=T,flag=F,
    res := do_test(msname=msname,predict=T,solve=F,subtract=F,run=T,flag=F,
                   stset=[1:14],
                   sources=sources,
                   solve_fluxes=solve_fluxes,
                   solve_gains=solve_gains,
                   solve_phases=solve_phases,
                   set_breakpoint=set_breakpoint,
                   mep_table_name=mep_table_name,
                   publish=1,mepuvw=mepuvw,msuvw=msuvw);
#                  publish=1,mepuvw=mepuvw,msuvw=T);
    print 'called do_test'
    
    
    print res;
    
    print 'errors reported:',mqs.num_errors();
}





#--------------------------------------------
#
# Source flux fitting on raw data
#
#--------------------------------------------
phase_solution_with_given_fluxes := function()
{
    global inputrec, outputrec,solver_defaults,msname,mepuvw;
    global outcol;
    global use_initcol

    use_initcol := F;       # initialize output column with zeroes

    msname := 'my.ms';
    mep_table_name := 'my.mep';
    
    # Clear MEP table
    meptable := table(mep_table_name, readonly=F);
    nrows := meptable.nrows();
    meptable.removerows(1:nrows);
    meptable.done();
    
    mepuvw := F;
    filluvw := any(argv=='-filluvw');
    solve_fluxes:= any(argv == '-fluxes');
    solve_gains := any(argv=='-gains');
    solve_phases := T;#any(argv=='-phases');
    set_breakpoint := any(argv=='-bp');
    
    src_3C343_1 := [name="3C343_1",I=5.35113, Q=0.0, U=0.0, V=0.0,
                    Iorder=1,
                    ra=4.356645791155902,dec=1.092208429052697];
    src_3C343   := [name="3C343",  I=1.60887, Q=0.0, U=0.0, V=0.0,
                    Iorder=3,
                    ra=4.3396003966265599,dec=1.0953677174056471];
    
    sources := [a=src_3C343_1,
                b=src_3C343];
    print sources;
    
    
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
    
    outcol := 'PREDICTED_DATA';
    solver_defaults := [ num_iter=6,save_funklets=T,last_update=T ];
    
    inputrec := [ ms_name = msname,data_column_name = 'DATA',
                 tile_size=1500,# clear_flags=T,
                 selection = [ channel_start_index=1,
                              channel_end_index=1, 
                              selection_string=''] ];
    
    outputrec := [ write_flags=F,predict_column=outcol ]; 
    
    res := do_test(msname=msname,solve=T,subtract=T,run=T,flag=F,
                   stset=1:2,
                   sources=sources,
                   solve_fluxes=solve_fluxes,
                   solve_gains=solve_gains,
                   solve_phases=solve_phases,
                   set_breakpoint=set_breakpoint,
                   mep_table_name=mep_table_name,
                   publish=1,mepuvw=mepuvw,msuvw=msuvw);
    
    
    print res;
    
    print 'errors reported:',mqs.num_errors();
}



source_flux_fit_no_calibration();
#phase_solution_with_given_fluxes();

