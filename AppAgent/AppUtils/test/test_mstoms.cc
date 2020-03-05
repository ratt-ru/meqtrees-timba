//  test_mstoms.cc: tests VisRepeater with two MS agents
//
//  Copyright (C) 2002-2007
//  ASTRON (Netherlands Foundation for Research in Astronomy)
//  and The MeqTree Foundation
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
#include <AppAgent/InputAgent.h>
#include <AppAgent/OutputAgent.h>
#include <AppUtils/MSInputSink.h>
#include <AppUtils/MSOutputSink.h>
#include "../src/VisRepeater.h"

using namespace casacore;

int main (int argc,const char *argv[])
{
  using namespace AppAgent;
  using namespace MSVisAgent;
  using namespace AppControlAgentVocabulary;
  
  try 
  {
    // this is needed to keep the ms from going crazy
    MeasurementSet ms1("test.ms",Table::Old);
    MeasurementSet ms2("test.ms",Table::Update);
    // comment the above two lines out, and MeasurementSet constructor
    // in MSVisOutputAgent will wind up the stack
  
    Debug::setLevel("VisRepeater",4);
    Debug::setLevel("MSVisAgent",4);
    Debug::setLevel("AppControlAgent",4);
    Debug::initLevels(argc,argv);

      // initialize parameter record
    DMI::Record::Ref paramref;
    DMI::Record &params = paramref <<= new DMI::Record;
    params[FThrowError] = true;
    
    DMI::Record &args = params[AidInput] <<= new DMI::Record;
      args[FMSName] = "test.ms";
      args[FDataColumnName] = "DATA";
      args[FTileSize] = 10;
      // setup selection
      DMI::Record &select = args[FSelection] <<= new DMI::Record;
        select[FDDID] = 0;
        select[FFieldIndex] = 0;
        select[FChannelStartIndex] = 10;
        select[FChannelEndIndex]   = 20;
        select[FSelectionString] = "ANTENNA1=1 && ANTENNA2=2";
        
    DMI::Record &outargs = params[AidOutput] <<= new DMI::Record;
      outargs[FWriteFlags]  = true;
      outargs[FFlagMask]    = 0xFF;
      outargs[FDataColumn]  = "MODEL_DATA";
      
    DMI::Record &ctrlargs = params[AidControl] <<= new DMI::Record;
      ctrlargs[FAutoExit] = true;

    cout<<"=================== creating input agent =======================\n";
    VisAgent::InputAgent::Ref inagent(
      new VisAgent::InputAgent(new MSVisAgent::MSInputSink),DMI::SHARED);
  
    cout<<"=================== creating output agent ======================\n";
    VisAgent::OutputAgent::Ref outagent(
      new VisAgent::OutputAgent(new MSVisAgent::MSOutputSink),DMI::SHARED);
    
    cout<<"=================== creating control agent =====================\n";
    AppControlAgent::Ref controlagent(
      new AppControlAgent,DMI::SHARED);
    
    cout<<"=================== creating event flag ========================\n";
    AppEventFlag::Ref eventflag(DMI::ANONWR);
    inagent().attach(eventflag());
    outagent().attach(eventflag());
    controlagent().attach(eventflag());
    
    cout<<"=================== creating repeater ==========================\n";
    VisRepeater::Ref repeater;
    repeater <<= new VisRepeater;
    repeater()<<inagent<<outagent<<controlagent;

    cout<<"=================== running repeater ===========================\n";
    controlagent().preinit(paramref);
    repeater().run();
    
    cout<<"=================== end of run ================================\n";
  } 
  catch ( std::exception &exc ) 
  {
    cout<<"Exiting with exception: "<<exc.what()<<endl;  
    return 1;
  }
  
  return 0;  
}
