//  test_mstoms.cc: tests VisRepeater with two MS agents
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

#include <AppAgent/AppControlAgent.h>
#include <AppAgent/BOIOSink.h>
#include <MSVisAgent/MSInputAgent.h>
#include <MSVisAgent/MSOutputAgent.h>
#include <OctoAgent/EventMultiplexer.h>
#include <OCTOPUSSY/Octopussy.h>
#include "../src/VisRepeater.h"

int main (int argc,const char *argv[])
{
  using namespace MSVisAgent;
  using namespace AppControlAgentVocabulary;
  using namespace VisRepeaterVocabulary;
  using namespace OctoAgent;
  
  try 
  {
    // this is needed to keep the ms from going crazy
    MeasurementSet ms1("test.ms",Table::Old);
    MeasurementSet ms2("test.ms",Table::Update);
    // comment the above two lines out, and MeasurementSet constructor
    // in MSVisOutputAgent will wind up the stack
  
    Debug::setLevel("VisRepeater",4);
    Debug::setLevel("MSVisAgent",4);
    Debug::setLevel("VisAgent",4);
    Debug::setLevel("OctoEventMux",4);
    Debug::setLevel("OctoEventSink",4);
    Debug::setLevel("BOIOSink",4);
    Debug::setLevel("AppControl",4);
    Debug::setLevel("Dsp",1);
    Debug::initLevels(argc,argv);
    
    cout<<"=================== starting OCTOPUSSY thread ==================\n";
    Octopussy::initThread(True);

    cout<<"=================== creating input repeater ====================\n";
      // initialize parameter record
    DataRecord params1;
    {
      params1[FThrowError] = True;
      DataRecord &args = params1[AidInput] <<= new DataRecord;
        args[FMSName] = "test.ms";
        args[FDataColumnName] = "DATA";
        args[FTileSize] = 10;
        // setup selection
        DataRecord &select = args[FSelection] <<= new DataRecord;
          select[FDDID] = 0;
          select[FFieldIndex] = 1;
          select[FChannelStartIndex] = 10;
          select[FChannelEndIndex]   = 20;
          select[FSelectionString] = "ANTENNA1=1 && ANTENNA2=2";

      DataRecord &outargs = params1[AidOutput] <<= new DataRecord;
        outargs[FEventMapOut] <<= new DataRecord;
          outargs[FEventMapOut][VisAgent::HeaderEvent] = VisAgent::HeaderEvent;
          outargs[FEventMapOut][VisAgent::TileEvent]   = VisAgent::TileEvent;

      DataRecord &ctrlargs = params1[AidControl] <<= new DataRecord;
        ctrlargs[FAutoExit] = True;
        ctrlargs[FEventMapIn] <<= new DataRecord;
          ctrlargs[FEventMapIn][InitNotifyEvent] = HIID("Output.VisRepeater.Init");
        ctrlargs[FEventMapOut] <<= new DataRecord;
          ctrlargs[FEventMapOut][StopNotifyEvent] = HIID("Input.VisRepeater.Stop");
    }
        
    OctoAgent::EventMultiplexer mux1(AidVisRepeater);
    MSVisAgent::MSInputAgent inagent1(AidInput);
    VisAgent::OutputAgent outagent1(mux1.newSink(),AidOutput);
    AppControlAgent controlagent1(mux1.newSink(),AidControl);
    inagent1.attach(mux1.eventFlag());
    controlagent1.attach(mux1.eventFlag());
    
    Octopussy::dispatcher().attach(&mux1,DMI::WRITE);
    
    VisRepeater repeater1(inagent1,outagent1,controlagent1);
    
    cout<<"=================== creating output repeater ===================\n";
      // initialize parameter record
    DataRecord params2;
    {
      params2[FThrowError] = True;

      DataRecord &args = params2[AidInput] <<= new DataRecord;
        args[FEventMapIn] <<= new DataRecord;
          args[FEventMapIn][VisAgent::HeaderEvent] = VisAgent::HeaderEvent;
          args[FEventMapIn][VisAgent::TileEvent]   = VisAgent::TileEvent;

      DataRecord &outargs = params2[AidOutput] <<= new DataRecord;
          outargs[AppEvent::FBOIOFile] = "test.boio";
          outargs[AppEvent::FBOIOMode] = "write";
//        outargs[FWriteFlags]  = True;
//        outargs[FFlagMask]    = 0xFF;
//        outargs[FDataColumn]      = "MODEL_DATA";

      DataRecord &ctrlargs = params2[AidControl] <<= new DataRecord;
        ctrlargs[FEventMapIn] <<= new DataRecord;
          ctrlargs[FEventMapIn][HaltEvent] = HIID("Input.VisRepeater.Stop");
        ctrlargs[FEventMapOut] <<= new DataRecord;
          ctrlargs[FEventMapOut][InitNotifyEvent] = HIID("Output.VisRepeater.Init");
    }
        
    OctoAgent::EventMultiplexer mux2(AidVisRepeater);
    VisAgent::InputAgent inagent2(mux2.newSink(),AidInput);
//    MSVisAgent::MSOutputAgent outagent2(AidOutput);
    VisAgent::OutputAgent outagent2(new BOIOSink,DMI::ANONWR,AidOutput);
    AppControlAgent controlagent2(mux2.newSink(),AidControl);
    outagent2.attach(mux2.eventFlag());
    controlagent2.attach(mux2.eventFlag());
    
    Octopussy::dispatcher().attach(&mux2,DMI::WRITE);
    
    VisRepeater repeater2(inagent2,outagent2,controlagent2);
    
    cout<<"=================== launching output thread ================\n";
    DataRecord::Ref ref1(params1),ref2(params2);
    Thread::ThrID id1,id2;
    
    id2 = repeater2.runThread(ref2,False);
    // wait for it to start
    cout<<"=================== waiting for output thread to start =====\n";
    repeater2.control().waitUntilLeavesState(AppState::INIT);
    
    cout<<"=================== launching input thread =================\n";
    // now run the input repeater
    id1 = repeater1.runThread(ref1,False),
    
    cout<<"=================== rejoining threads =========================\n";
    id1.join();
    id2.join();
    
    cout<<"=================== stopping OCTOPUSSY ========================\n";
    Octopussy::stopThread();
    
    cout<<"=================== end of run ================================\n";
  }
  catch ( std::exception &exc ) 
  {
    cout<<"Exiting with exception: "<<exc.what()<<endl;  
    return 1;
  }
  
  return 0;  
}
