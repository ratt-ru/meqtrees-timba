default_debuglevels := [  MeqNode       =3,
                          MeqForest     =3,
                          MeqSink       =3,
                          MeqSpigot     =3,
                          MeqVisHandler =3,
                          MeqServer     =3,
                          meqserver     =1      ];

include 'meq/meqserver.g'
  
# inits a meq.server
const mqsinit := function (verbose=default_verbosity,debug=[=])
{
  global mqs;
  if( !is_record(mqs) )
  {
    mqs := meq.server(verbose=verbose,options="-d0 -meq:M:M:MeqServer");
    if( is_fail(mqs) )
      fail;
    mqs.init([output_col="PREDICT",mandate_regular_grid=T],wait=T);
    if( is_record(debug) )
    {
      for( lev in field_names(default_debuglevels) )
        mqs.setdebug(lev,default_debuglevels[lev]);
      for( lev in field_names(debug) )
        mqs.setdebug(lev,debug[lev]);
    }
  }
  return mqs;
}
