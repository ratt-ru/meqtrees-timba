pragma include once
include 'meq/meqtypes.g'
include 'meq/meptable.g'


const fill_uvw := function (msname,mepname,ddid=0,name="%s.%d",create=T)
{
  ms := table(msname);
  mep := meq.meptable(mepname,create=create);
  # everything is relative to ant1, so select entries relative to it
  mss := ms.query(paste('DATA_DESC_ID==',ddid,'&& ANTENNA1==0'));

  ant2 := mss.getcol('ANTENNA2');
  uvw  := mss.getcol('UVW');
  time := mss.getcol('TIME');
  int  := mss.getcol('INTERVAL');
  
  parmnames := "U V W";
  # fill in zero for station 0
  for( j in 1:3 )
  {
    parmname := sprintf(name,parmnames[j],1);
    mep.put(parmname,values=0);
  }
  # loop over entries to generate polcs for UVWs
  for( i in 1:mss.nrows() )
  {
    if( ant2[i] != 0 )
    {
      trange := time[i] + [-int[i],int[i]]/2;
      for( j in 1:3 )
      {
        parmname := sprintf(name,parmnames[j],ant2[i]+1);
        mep.put(parmname,values=uvw[j,i],timerange=trange);
      }
    }
  }
}
