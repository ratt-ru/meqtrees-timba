//  VisFileInputAgent.h: common base class for VisInputAgents that read files
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

#ifndef _VISAGENT_VISFILEINPUTAGENT_H
#define _VISAGENT_VISFILEINPUTAGENT_H 1

#include <AppAgent/InputAgent.h>
#include <AppAgent/FileAgentBase.h>

namespace AppAgent
{    

namespace VisAgent 
{

//##ModelId=3DF9FECD0159
//##Documentation
//## VisFileInputAgent implements some common features & services for agents
//## that get their input from a static data file (e.g., AIPS++ MSs, BOIO
//## files).
class FileInputAgent : public InputAgent, public FileAgentBase
{
  private:
    //##ModelId=3F5F43650320
      DMI::Record::Ref  header_;

      
  protected:
    //##ModelId=3E42458601D7
      FileInputAgent(const HIID &initf)
        : InputAgent(initf) {}
 
    // returns header by reference
    //##ModelId=3F5F43650340
      DMI::Record &  header     ()
      { return header_.dewr(); }

    // initializes an empty header
    //##ModelId=3F5F43650356
      DMI::Record &  initHeader ();
 
  public:
      
    //##ModelId=3F5F4365036A
      virtual int getHeader (DMI::Record::Ref &hdr,int wait = AppEvent::WAIT);
  
    //##ModelId=3F5F436503B9
      virtual int hasHeader ();
      
    //##ModelId=3F5F436503CF
      virtual int hasTile   ();
      
      //##ModelId=3E2C299201D6
      //##Documentation
      //## Reports current state of agent. Default version always reports success
      virtual int state() const;

      //##ModelId=3E2C2999029A
      //##Documentation
      //## Reports current state as a string
      virtual string stateString() const;
      

      
  private:
    //##ModelId=3DF9FECE00FC
    FileInputAgent ();
    //##ModelId=3E42407D0044
    FileInputAgent (const FileInputAgent& right);
    //##ModelId=3E42407D02D4
    FileInputAgent& operator= (const FileInputAgent& right);

};




} // namespace VisAgent

};

#endif
    
