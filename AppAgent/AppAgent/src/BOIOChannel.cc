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

#include "BOIOChannel.h"
#include <DMI/Exception.h>

namespace AppAgent
{    

InitDebugContext(BOIOChannel,"BOIOChannel");

using namespace AppEvent;
    
//##ModelId=3E53C59D00EB
int BOIOChannel::init (const DMI::Record &data)
{
  if( FileChannel::init(data) < 0 )
    return state();
  string file = data[FBOIOFileName].as<string>("");  
  FailWhen(!file.length(),FBOIOFileName.toString()+" not specified");
  char mode = toupper( data[FBOIOFileMode].as<string>("R")[0] );  
  if( mode == 'R' )
  {
    boio.open(file,BOIO::READ);
    cdebug(1)<<"opened file "<<file<<" for reading\n";
  }
  else if( mode == 'W' )
  {
    boio.open(file,BOIO::WRITE);
    cdebug(1)<<"opened file "<<file<<" for writing\n";
  }    
  else if( mode == 'A' )
  {
    boio.open(file,BOIO::APPEND);
    cdebug(1)<<"opened file "<<file<<" for appending\n";
  }
  else
  {
    Throw("unknown file access mode: "+mode);
  }
  return setState(OPEN);
}

//##ModelId=3E53C5A401E1
void BOIOChannel::close (const string &str)
{
  FileChannel::close();
  boio.close();
  setState(CLOSED,str);
}

//##ModelId=3EC23EF30079
int BOIOChannel::refillStream()
{
  if( boio.fileMode() != BOIO::READ )
    return WAIT;
  for(;;)
  {
    ObjRef ref;
    TypeId tid = boio.readAny(ref);
    if( tid == 0 )
    {
      cdebug(1)<<"EOF on BOIO file, closing"<<endl;
      return CLOSED;
    }
    else if( tid != TpDMIRecord )
    {
      cdebug(2)<<"unexpected object ("<<tid<<") in BOIO file, ignoring"<<endl;
      // go back for another event
      continue;
    }
    // else process the DMI::Record
    try
    {
      DMI::Record &rec = ref.ref_cast<DMI::Record>().dewr();
      const HIID &id = rec[AidEvent].as<HIID>();
      const HIID &addr = rec[AidAddress].as<HIID>();
      ObjRef dataref;
      if( rec[AidData].exists() )
        rec[AidData].detach(&dataref);
      putOnStream(id,dataref,addr);
      return SUCCESS;
    }
    catch( std::exception &exc )
    {
      cdebug(2)<<"error getting event from BOIO: "<<exceptionToString(exc)<<endl;
      // go back for another event
    }
  }
}

//##ModelId=3E8C252801E8
bool BOIOChannel::isEventBound (const HIID &,AtomicID)
{
  return boio.fileMode() == BOIO::WRITE || boio.fileMode() == BOIO::APPEND;
}

//##ModelId=3E53C5C2003E
void BOIOChannel::postEvent (const HIID &id,const ObjRef &data,AtomicID,const HIID &dest)
{
  if( boio.fileMode() == BOIO::WRITE || boio.fileMode() == BOIO::APPEND )
  {
    cdebug(3)<<"storing event "<<id<<endl;
    DMI::Record rec;
    rec[AidEvent] = id;
    rec[AidAddress] = dest;
    if( data.valid() )
      rec[AidData] <<= data;
    boio << ObjRef(rec,DMI::EXTERNAL);
  }
  else
  {
    cdebug(3)<<"no file open for writing, dropping event "<<id<<endl;
  }
}

//##ModelId=3E53C5CE0339
string BOIOChannel::sdebug(int detail, const string &prefix, const char *name) const
{
  using Debug::append;
  using Debug::appendf;
  using Debug::ssprintf;
  
  string out;
  if( detail >= 0 ) // basic detail
  {
    appendf(out,"%s/%p",name?name:"BOIOChannel",this);
  }
  if( detail >= 1 || detail == -1 )
  {
    append(out,boio.stateString());
  }
  
  return out;
}

};
