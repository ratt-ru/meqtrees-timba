//  test_repeater.cc: tests repeaters and their agents
//
//  Copyright (C) 2002
//  ASTRON (Netherlands Foundation for Research in Astronomy)
//  P.O.Box 2, 7990 AA Dwingeloo, The Netherlands, seg@astron.nl
//
//  This program is free software; you can redistribute it and/or modify
//  it under the terms of the GNU General Public License as published by
//  the Free Software Foundation; either version 2 of the License, or
//  (at your option) any later version.
//
//  This program is distributed in the hope that it will be useful,
//  but WITHOUT ANY WARRANTY; without even the implied warranty of
//  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//  GNU General Public License for more details.
//
//  You should have received a copy of the GNU General Public License
//  along with this program; if not, write to the Free Software
//  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
//
//  $Id$

#include "../src/MSVisInputAgent.h"
#include "../src/MSVisOutputAgent.h"
#include <DMI/DataArray.h>

#include <AppAgent/AppControlAgent.h>

// this function checks the agent for any events and prints them out
void checkEvents (AppAgent &agent)
{
  if( !agent.hasEvent() )
  {
    cout<<"No events pending.\n";
    return;
  }
  int count = 0;
  while( agent.hasEvent() )
  {
    FailWhen1( count++ > 100, "Too many events. I bet the agent is not flushing them." );
    HIID name;
    DataRecord::Ref data;
    bool res = agent.getEvent(name,data);
    FailWhen1( !res,"Oops, hasEvents() is True but getEvent() has failed. Debug your agent." );
    cout<<"getEvent: "<<name.toString()<<" data: "<<data.sdebug(10)<<endl;
    if( data.valid() )
    {
      // if event has data, check for a message field and print that
      string msg = (*data)[AidMessage].as_string("");
      if( msg != "" )
        cout<<"Event message: "<<msg<<endl;
    }
  }
}
    
int main (int argc,const char *argv[])
{
  using namespace MSVisAgentVocabulary;
  
  try 
  {
    Debug::setLevel("MSVisAgent",2);
    Debug::setLevel("DataRepeater",2);
    Debug::setLevel("OctoAgent",2);
    Debug::initLevels(argc,argv);

    // initialize top-level parameter record
    DataRecord::Ref dataref;
    DataRecord &toprecord = dataref <<= new DataRecord;

    DataRecord &args = toprecord[MSVisInputAgent::FParams()] <<= new DataRecord;
    
      args[FMSName] = "test.ms";
      args[FDataColumnName] = "DATA";
      args[FTileSize] = 10;

      // setup selection
      DataRecord &select = *new DataRecord;
      args[FSelection] <<= select;

        select[FDDID] = 0;
        select[FFieldIndex] = 1;
        select[FChannelStartIndex] = 10;
        select[FChannelEndIndex]   = 20;
        select[FSelectionString] = "ANTENNA1=1 && ANTENNA2=2";
        
    DataRecord &outargs = *new DataRecord;
    dataref()[MSVisOutputAgent::FParams()] <<= outargs;
    
      outargs[FWriteFlags]  = True;
      outargs[FFlagMask]    = 0xFF;
      
      outargs[FDataColumn]      = "";
      outargs[FPredictColumn]   = "MODEL_DATA";
      outargs[FResidualsColumn] = "RESIDUAL_DATA";

    cout<<"=================== creating input agent ======================\n";
    // create agent
    MSVisInputAgent agent;
    checkEvents(agent);
  
    cout<<"=================== creating output agent ======================\n";
    // create agent
    MSVisOutputAgent outagent;
    checkEvents(outagent);

    cout<<"=================== initializing input agent ==================\n";
    bool res = agent.init(dataref);
    cout<<"init(): "<<res<<endl;
    checkEvents(agent);
    cout<<"hasHeader(): "<<agent.hasHeader()<<endl;
    cout<<"hasTile(): "<<agent.hasTile()<<endl;

    if( !res )
    {
      cout<<"init has failed, exiting...\n";
      return 1;
    }
    
//    MeasurementSet ms("test.ms",Table::Update);
    
    cout<<"=================== initializing output agent ================\n";
    // initialize parameter record
    res = outagent.init(dataref);
    cout<<"init(): "<<res<<endl;
    checkEvents(outagent);

    if( !res )
    {
      cout<<"init has failed, exiting...\n";
      return 1;
    }

    cout<<"=================== getting header ============================\n";
    DataRecord::Ref header;
    cout<<"getHeader(): "<<agent.getHeader(header)<<endl;
    cout<<header->sdebug(10)<<endl;
    checkEvents(agent);

    cout<<"=================== putting header ============================\n";
    cout<<"putHeader(): "<<outagent.putHeader(header)<<endl;
    checkEvents(outagent);
       
    cout<<"=================== copying tiles =============================\n";
    int state = 1;
    while( state > 0 )
    {
      VisTile::Ref tile;
      cout<<"getNextTile(): "<<(state=agent.getNextTile(tile))<<endl;
      checkEvents(agent);
      if( state > 0 )
      {
        cout<<tile->sdebug(10)<<endl;
        // add columns to tile
        LoShape shape = tile->data().shape();
        VisTile::Format::Ref newformat;
        newformat <<= new VisTile::Format(tile->format());
        newformat().add(VisTile::PREDICT,Tpfcomplex,tile->data().shape())
                   .add(VisTile::RESIDUALS,Tpfcomplex,tile->data().shape());
        // fill the columns
        tile().wpredict()   = -tile->data();
        tile().wresiduals() = conj(tile->data());

        cout<<"putNextTile(): "<<outagent.putNextTile(tile)<<endl;
        checkEvents(outagent);
      }
    }

    cout<<"=================== end of run ================================\n";
    cout<<"hasHeader(): "<<agent.hasHeader()<<endl;
    cout<<"hasTile(): "<<agent.hasTile()<<endl;
    checkEvents(agent);
    checkEvents(outagent);

    agent.close();
    outagent.close();
  } 
  catch ( std::exception &exc ) 
  {
    cout<<"Exiting with exception: "<<exc.what()<<endl;  
    return 1;
  }
  
  return 0;  
}
