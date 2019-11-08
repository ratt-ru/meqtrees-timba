#include <casacore/ms/MeasurementSets/MeasurementSet.h>
#include <casacore/tables/Tables/ArrayColumn.h>
#include <casacore/tables/Tables/ScalarColumn.h>
#include <casacore/tables/Tables/ArrColDesc.h>
#include <casacore/tables/Tables/ScaColDesc.h>
#include <casacore/tables/DataMan/TiledStManAccessor.h>
#include <casacore/tables/DataMan/TiledColumnStMan.h>
#include <casacore/tables/DataMan/IncrementalStMan.h>

#include <iostream>
using namespace std;
using namespace casacore;

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
    // add BITFLAG_ROW column, if needed
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
    if( td.isColumn("BITFLAG") )
    {
      cout<<"BITFLAG column already present in this MS\n";
    }
    else // add BITFLAG column, if needed
    {
      // determine cell shape
      if( !td.isColumn("DATA") )
      {
        cerr<<"This MS is missing a DATA column. Cannot determine flag shape.\n""";
        return 1;
      }
      const ColumnDesc &cd_data = td.columnDesc("DATA");
      // determine storage manager to use. If DATA column uses a TiledColumnStMan, use that,
      // else use default
      IPosition tileshape;
      bool tiled_stman = false;
      string dmtype = cd_data.dataManagerType();
      cout<<"DATA column storage manager type is "<<dmtype<<endl;
      if( cd_data.isFixedShape() && dmtype.length() > 5 && !dmtype.compare(0,5,"Tiled") )
      {
        tiled_stman = true;
        // get tile shape from storage manager of FLAG column
        ROTiledStManAccessor acc(ms,cd_data.dataManagerGroup());
        tileshape = acc.tileShape(0);
        cout<<"BITFLAG column will use a TiledColumnStMan storage manager with tile shape "
            <<tileshape<<endl;
      }
      else
        cout<<"BITFLAG column will use a default storage manager\n";
      // if DATA column has a fixed shape, create a BITFLAG column of the same shape
      if( cd_data.isFixedShape() )
      {
        cout<<"Adding BITFLAG column with fixed shape: "<<cd_data.shape()<<endl;
        ArrayColumnDesc<Int> cd_bitflag("BITFLAG",
                              "added by addbitflagcol utility",
                              cd_data.shape(),
                              ColumnDesc::Direct|ColumnDesc::FixedShape);
        if( tiled_stman )
        {
          TiledColumnStMan stman("Tiled_BITFLAG",tileshape);
          ms.addColumn(cd_bitflag,stman);
        }
        else
          ms.addColumn(cd_bitflag);
      }
      // else variable shape (potentially different with each DDID)
      else
      {
        cout<<"Adding BITFLAG column with variable shape\n";;
        // create description for BITFLAG column
        ArrayColumnDesc<Int> cd_bitflag("BITFLAG",
                              "added by addbitflagcol utility",
                              cd_data.ndim());
        // tiled stman requires fixed shape, so commenting this out for now
/*        if( tiled_stman )
        {
          TiledColumnStMan stman("Tiled_BITFLAG",tileshape);
          ms.addColumn(cd_bitflag,stman);
        }
        else*/
        ms.addColumn(cd_bitflag);
        cout<<"Initializing variable-shaped BITFLAG column\n";;
        // damn you variable-shaped columns. Loop over MS to fill BITFLAG
        ROTableColumn datacol(ms,"DATA");
        ArrayColumn<Int> bitflagcol(ms,"BITFLAG");
        for( int irow = 0; irow < ms.nrow(); irow ++ )
          if( datacol.isDefined(irow) )
            bitflagcol.put(irow,Array<Int>(datacol.shape(irow),0));
      }
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
