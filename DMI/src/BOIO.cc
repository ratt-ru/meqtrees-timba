#include <stdio.h>
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
BOIO::BOIO (const string &filename,int mode)
    : fp(0),fmode(CLOSED)
{
  open(filename,mode);
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
  fp = fopen(filename.c_str(),mstr);
  FailWhen( !fp,"error opening file "+filename );
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

// Reads object attaches to ref. Returns its TypeId, or 
// 0 for no more objects
//##ModelId=3DB949AE025C
TypeId BOIO::readAny (ObjRef &ref)
{
  FailWhen(fmode != READ,"not open for reading");
  TypeId tid = nextType();
  if( !tid )
    return 0;
  have_header = false;
  // read array of block sizes
  size_t sizes[header.nblocks];
  if( feof(fp)  || fread(&sizes,sizeof(sizes),1,fp) != 1 )
    return 0;
  // allocate and read in blocks  
  BlockSet set;
  for( int i=0; i<header.nblocks; i++ )
  {
    SmartBlock *block = new SmartBlock(sizes[i]);
    set.pushNew() <<= block;
    if( fread(block->data(),sizes[i],1,fp) != 1 )
      return 0;
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
  FailWhen(fmode != READ,"not open for reading");
  // if header already read in, return type
  if( have_header )
    return header.tid;
  //  else, read it in
  have_header = true;
  if( feof(fp) || fread(&header,sizeof(header),1,fp) != 1 )
    header.tid = 0;
  return header.tid;
}

// writes object to file
// Returns number of bytes actually written
//##ModelId=3DB949AE0266
size_t BOIO::write (const DMI::BObj &obj)
{
  FailWhen(fmode!=WRITE && fmode!=APPEND,"not open for writing");
  // convert object to blockset
  BlockSet set;
  obj.toBlock(set);
  // format and write header
  ObjHeader hdr;
  hdr.tid = obj.objectType();
  hdr.nblocks = set.size();
  FailWhen( fwrite(&hdr,sizeof(hdr),1,fp) != 1,"write error" );
  size_t written = sizeof(hdr);
  // format and write size array
  size_t sizes[hdr.nblocks];
  BlockSet::iterator iter = set.begin();
  for( int i=0; i<set.size(); i++,iter++ )
    sizes[i] = (*iter)->size();
  DbgAssert(iter == set.end());
  FailWhen( fwrite(&sizes,sizeof(sizes),1,fp) != 1,"write error" );
  // write out the blocks
  iter = set.begin();
  for( int i=0; i<set.size(); i++,iter++ )
  {
    FailWhen( fwrite((*iter)->data(),sizes[i],1,fp) != 1,"write error" );
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
