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

#include <stdio.h>
#include <errno.h>
#include <string.h>
#include "BOIO.h"
#include "DynamicTypeManager.h"

namespace DMI
{

//##ModelId=3DB949AE024E
BOIO::BOIO ()
    : fp(0),fmode(CLOSED)
{
}

//##ModelId=3DB949AE0254
BOIO::~BOIO ()
{
  if( fp )
    fclose(fp);
}


//##ModelId=3DB949AE024F
BOIO::BOIO (const string &fname,int mode)
    : fp(0),fmode(CLOSED)
{
  open(fname,mode);
}

// attaches to a file
//##ModelId=3DB949AE0255
int BOIO::open (const string &filename,int mode)
{
  close();
  const char *mstr;
  switch( mode )
  {
    case BOIO::READ:    mstr = "rb"; break;
    case BOIO::WRITE:   mstr = "wb"; break;
    case BOIO::APPEND:  mstr = "ab"; break;
    default:      Throw("open(): invalid mode");
  }
  fp = fopen64(filename.c_str(),mstr);
  FailWhen( !fp,"error opening boio file "+fname+": "+strerror(errno) );
  fname = filename;
  fmode = mode;
  have_header = false;
  return 1;
}

// closes file
//##ModelId=3DB949AE025B
int BOIO::close ()
{
  if( fp )
  {
    fclose(fp);
    fp = 0;
    fmode = CLOSED;
    fname = "";
  }
  return 1;
}

long BOIO::ftell ()
{
  FailWhen(!fp,"boio file not open");
  return ::ftell(fp);
}

void BOIO::fseek (long offset)
{
  FailWhen(!fp,"boio file not open");
  ::fseek(fp,offset,SEEK_SET);
}

void BOIO::rewind ()
{
  FailWhen(!fp,"boio file not open");
  ::rewind(fp);
}

void BOIO::flush ()
{
  if( fp )
    ::fflush(fp);
}

// Reads object attaches to ref. Returns its TypeId, or
// 0 for no more objects
//##ModelId=3DB949AE025C
TypeId BOIO::readAny (ObjRef &ref)
{
  FailWhen(fmode != READ,"boio file "+fname+": not open for reading");
  TypeId tid = nextType();
  if( !tid )
    return 0;
  have_header = false;
  // read array of block sizes
  size_t sizes[header.nblocks];
  if( fread(&sizes,sizeof(sizes),1,fp) != 1 )
  {
    FailWhen(ferror(fp),"error reading boio file "+fname+": "+strerror(errno));
    Throw("error reading file "+fname+": unexpected EOF");
  }
  // allocate and read in blocks
  BlockSet set;
  for( int i=0; i<header.nblocks; i++ )
  {
    SmartBlock *block = new SmartBlock(sizes[i]);
    set.pushNew() <<= block;
    if( fread(block->data(),sizes[i],1,fp) != 1 )
    {
      FailWhen(ferror(fp),"error reading boio file "+fname+": "+strerror(errno));
      Throw("error reading file "+fname+": unexpected EOF");
    }
  }
  // create object
  ref = DynamicTypeManager::construct(tid,set);
  FailWhen(!ref.valid(),"failed to construct "+tid.toString() );
  return tid;
}

// returns TypeId of next object in stream (or 0 for EOF)
//##ModelId=3DB949AE0265
TypeId BOIO::nextType ()
{
  FailWhen(fmode != READ,"boio file "+fname+": not open for reading");
  // if header already read in, return type
  if( have_header )
    return header.tid;
  //  else, read it in
  header.tid = 0;
  have_header = true;
  if( feof(fp) )
    return 0;
  else if( fread(&header,sizeof(header),1,fp) != 1 )
  {
    FailWhen(ferror(fp),"error reading boio file "+fname+": "+strerror(errno));
    // check for EOF again
    if( feof(fp) )
      return 0;
    Throw("unknown error reading file "+fname);
  }
  return header.tid;
}

// writes object to file
// Returns number of bytes actually written
//##ModelId=3DB949AE0266
size_t BOIO::write (const DMI::BObj &obj)
{
  FailWhen(fmode!=WRITE && fmode!=APPEND,"boio file "+fname+": not open for writing");
  // convert object to blockset
  BlockSet set;
  obj.toBlock(set);
  // format and write header
  ObjHeader hdr;
  hdr.tid = obj.objectType();
  hdr.nblocks = set.size();
  FailWhen(fwrite(&hdr,sizeof(hdr),1,fp)!= 1,"error writing boio file "+fname+": "+strerror(errno));
  size_t written = sizeof(hdr);
  // format and write size array
  size_t sizes[hdr.nblocks];
  BlockSet::iterator iter = set.begin();
  for( int i=0; i<set.size(); i++,iter++ )
    sizes[i] = (*iter)->size();
  DbgAssert(iter == set.end());
  FailWhen( fwrite(&sizes,sizeof(sizes),1,fp) != 1,"error writing boio file "+fname+": "+strerror(errno));
  // write out the blocks
  iter = set.begin();
  for( int i=0; i<set.size(); i++,iter++ )
  {
    FailWhen( fwrite((*iter)->data(),sizes[i],1,fp) != 1,"error writing boio file "+fname+": "+strerror(errno));
    written += sizes[i];
  }
  DbgAssert(iter == set.end());
  return written;
}


//##ModelId=3E54BDE70228
string BOIO::stateString () const
{
  if( !fp )
    return "(closed)";
  string out = fname;
  switch( fmode )
  {
    case READ: out += "(r)"; break;
    case WRITE: out += "(w)"; break;
    case APPEND: out += "(a)"; break;
  }
  return out;
}

};
