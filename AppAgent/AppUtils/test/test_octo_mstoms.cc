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
#include <VisAgent/InputAgent.h>
#include <VisAgent/OutputAgent.h>
#include <MSVisAgent/MSInputSink.h>
#include <MSVisAgent/MSOutputSink.h>
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
    DataRecord::Ref params1ref;
    DataRecord & params1 = params1ref <<= new DataRecord;
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
        
    OctoAgent::EventMultiplexer::Ref mux1(
        new OctoAgent::EventMultiplexer(AidVisRepeater),DMI::ANONWR);
    VisAgent::InputAgent::Ref inagent1(
        new VisAgent::InputAgent(new MSVisAgent::MSInputSink,DMI::ANONWR,AidInput),DMI::ANONWR);
    VisAgent::OutputAgent::Ref outagent1(
        new VisAgent::OutputAgent(mux1().newSink(),AidOutput),DMI::ANONWR);
    AppControlAgent::Ref controlagent1(
        new AppControlAgent(mux1().newSink(),AidControl),DMI::ANONWR);
    inagent1().attach(mux1().eventFlag());
//    controlagent1().attach(mux1().eventFlag());
    Octopussy::dispatcher().attach(mux1,DMI::WRITE);
    
    VisRepeater::Ref repeater1(DMI::ANONWR);
    repeater1()<<inagent1<<outagent1<<controlagent1;
    
    cout<<"=================== creating output repeater ===================\n";
      // initialize parameter record
    DataRecord::Ref params2ref;
    DataRecord & params2 = params2ref <<= new DataRecord;
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
        ctrlargs[FAutoExit] = True;
        ctrlargs[FEventMapIn] <<= new DataRecord;
          ctrlargs[FEventMapIn][HaltEvent] = HIID("Input.VisRepeater.Stop");
        ctrlargs[FEventMapOut] <<= new DataRecord;
          ctrlargs[FEventMapOut][InitNotifyEvent] = HIID("Output.VisRepeater.Init");
    }
        
    OctoAgent::EventMultiplexer::Ref mux2(
        new OctoAgent::EventMultiplexer(AidVisRepeater),DMI::ANONWR);
    VisAgent::InputAgent::Ref inagent2(
        new VisAgent::InputAgent(mux2().newSink(),AidInput),DMI::ANONWR);
//    MSVisAgent::MSOutputAgent outagent2(AidOutput);
    VisAgent::OutputAgent::Ref outagent2(
        new VisAgent::OutputAgent(new BOIOSink,DMI::ANONWR,AidOutput),DMI::ANONWR);
    AppControlAgent::Ref controlagent2(
        new AppControlAgent(mux2().newSink(),AidControl),DMI::ANONWR);
    outagent2().attach(mux2().eventFlag());
//    controlagent2().attach(mux2().eventFlag());
    
    Octopussy::dispatcher().attach(mux2,DMI::WRITE);
    
    VisRepeater::Ref repeater2(DMI::ANONWR);
    repeater2()<<inagent2<<outagent2<<controlagent2;
    
    cout<<"=================== launching output thread ================\n";
    controlagent1().preinit(params1ref);
    controlagent2().preinit(params2ref);
    
    Thread::ThrID id1,id2;
    
    id2 = repeater2().runThread(False);
    // wait for it to start
    cout<<"=================== waiting for output thread to start =====\n";
    repeater2().control().waitUntilLeavesState(AppState::INIT);
    
    cout<<"=================== launching input thread =================\n";
    // now run the input repeater
    id1 = repeater1().runThread(False),
    
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
