//
//% $Id$ 
//
//
// Copyright (C) 2002-2007
// The MeqTree Foundation & 
// ASTRON (Netherlands Foundation for Research in Astronomy)
// P.O.Box 2, 7990 AA Dwingeloo, The Netherlands
//
// This program is free software; you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation; either version 2 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program; if not, see <http://www.gnu.org/licenses/>,
// or write to the Free Software Foundation, Inc., 
// 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
//

#ifndef APPAGENT_SRC_FILECHANNEL_H_HEADER_INCLUDED_CA2F6569
#define APPAGENT_SRC_FILECHANNEL_H_HEADER_INCLUDED_CA2F6569

#include <AppAgent/EventChannel.h>
#include <AppAgent/AID-AppAgent.h>    
    
#include <deque>
    
namespace AppAgent
{    

//##Documentation
//## FileChannel is an abstract base class for channels that read their 
//## events from a file.
//## It has an internal event stream and a pure virtual refillStream() 
//## method which should be implemented to refill the event stream, which
//## should be done by calling the putOnStream() method.
//##ModelId=3EB9163E00AF
class FileChannel : public EventChannel
{
  public:
    FileChannel ()
    {};  
    
    //##ModelId=3EB9169701B4
    //##Documentation
    //## gets event from file
    virtual int getEvent ( HIID &id,ObjRef &data,
                           const HIID &mask,
                           int wait = AppEvent::WAIT,
                           HIID &source = _dummy_hiid );

    //##ModelId=3EB916A5000E
    //##Documentation
    //## checks for event in stream, refills stream from file if empty
    virtual int hasEvent (const HIID &mask = HIID(),HIID &out = _dummy_hiid);
    
  protected:
    //##ModelId=3EB92AEF01C3
    //##Documentation
    //## called to put more objects on the stream. Returns SUCCESS if something
    //## was put on, or <0 code (ERROR/CLOSED/whatever). Should call
    //## putOnStream() to put new objects on the stream. 
    //## Once channel is out of objects, should return CLOSED (but never call
    //## close() itself).
    virtual int refillStream () =0;
    
    //##ModelId=3EB92AEE0279
    //## helper method -- places an event on the internal stream
    void putOnStream (const HIID &id,const ObjRef &ref,const HIID &source=HIID());
    
  private:
    //##ModelId=3EB91663019B
    FileChannel(const FileChannel& right);
    //##ModelId=3EB916630210
    FileChannel& operator=(const FileChannel& right);
    
    //##ModelId=3EC2434403DC
    typedef struct { HIID id; HIID source; ObjRef ref; } StreamEntry;
    
    //##ModelId=3EC24345039F
    std::deque<StreamEntry> input_stream_;
    
};

};
#endif /* APPAGENT_SRC_FILECHANNEL_H_HEADER_INCLUDED_CA2F6569 */
