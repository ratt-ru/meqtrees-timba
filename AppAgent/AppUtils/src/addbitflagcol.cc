#include <ms/MeasurementSets/MeasurementSet.h>
#include <tables/Tables/ArrayColumn.h>
#include <tables/Tables/ScalarColumn.h>
#include <tables/Tables/ArrColDesc.h>
#include <tables/Tables/ScaColDesc.h>
#include <tables/Tables/TiledStManAccessor.h>
#include <tables/Tables/TiledColumnStMan.h>
#include <tables/Tables/IncrementalStMan.h>

#include <iostream>
using namespace std;
using namespace casa;

int main (int argc,char *argv[])
{
  if( argc!=2 )
  {
    cerr<<argv[0]<<": adds BITFLAG/BITFLAG_ROW columns to an MS\n";
    cerr<<"Usage: "<<argv[0]<<" MS_name\n";
    return 1;
  }
  char *msname = argv[1];
  try
  {
    MeasurementSet ms(msname,TableLock(TableLock::AutoNoReadLocking),Table::Update);
    const TableDesc &td = ms.tableDesc();
    if( td.isColumn("BITFLAG") )
    {
      cout<<"BITFLAG column already present in this MS\n";
    }
    else // add BITFLAG column
    {
      // determine cell shape
      if( !td.isColumn("DATA") )
      {
        cerr<<"This MS is missing a DATA column. Cannot determine flag shape.\n""";
        return 1;
      }
      const ColumnDesc &cd_data = td.columnDesc("DATA");
      cout<<"DATA column shape is "<<cd_data.shape()<<endl;
      // create description for BITFLAG column
      ArrayColumnDesc<Int> cd_bitflag("BITFLAG",
                            "added by addbitflagcol utility",
                            cd_data.shape(),
                            ColumnDesc::Direct|ColumnDesc::FixedShape);
      // tiled column -- add a tiled data manager
      string dmtype = cd_data.dataManagerType();
      cout<<"DATA column storage manager type is "<<dmtype<<endl;
      if( dmtype.length() > 5 && !dmtype.compare(0,5,"Tiled") )
      {
        // get tile shape from storage manager of FLAG column
        ROTiledStManAccessor acc(ms,cd_data.dataManagerGroup());
        IPosition tileShape(acc.tileShape(0));
        // create a tiled storage manager with the same shape
        TiledColumnStMan stman("Tiled_BITFLAG",acc.tileShape(0));
        cout<<"Creating new column BITFLAG using a TiledColumnStMan storage manager with tile shape "
            <<acc.tileShape(0)<<endl;
        ms.addColumn(cd_bitflag,stman);
      }
      // else add using a standard data manager
      else
      {
        cout<<"Creating new column BITFLAG using a default storage manager"<<endl;
        ms.addColumn(cd_bitflag);
      }
    }
    if( td.isColumn("BITFLAG_ROW") )
    {
      cout<<"BITFLAG_ROW column already present in this MS\n";
    }
    else // add BITFLAG_ROW column
    {
      cout<<"creating new column BITFLAG_ROW using an IncrementalStMan storage manager"<<endl;
      ScalarColumnDesc<Int> coldesc("BITFLAG_ROW","added by addbitflagcol utility");
      IncrementalStMan stman("ISM_BITFLAG_ROW");
      ms.addColumn(coldesc,stman);
    }
    ms.flush();
    return 0;
  }
  catch( std::exception &exc )
  {
    cerr<<"Caught exception: "<<exc.what()<<endl;
    return 1;
  }
  catch( ... )
  {
    cerr<<"Caught unknown exception, exiting.\n";
    return 1;
  }
}