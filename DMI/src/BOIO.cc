#include <stdio.h>
#include "DMI/BOIO.h"
#include "DMI/DynamicTypeManager.h"
    
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
    case READ:    mstr = "rb"; break;
    case WRITE:   mstr = "wb"; break;
    case APPEND:  mstr = "ab"; break;
    default:      Throw("open(): invalid mode");
  }
  fp = fopen(filename.c_str(),mstr);
  FailWhen( !fp,"error opening file "+filename );
  fname = filename;
  fmode = mode;
  have_header = False;
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
TypeId BOIO::read (ObjRef &ref)
{
  FailWhen(fmode != READ,"not open for reading");
  TypeId tid = nextType();
  if( !tid )
    return 0;
  have_header = False;
  // read array of block sizes
  size_t sizes[header.nblocks];
  if( feof(fp)  || fread(&sizes,sizeof(sizes),1,fp) != 1 )
    return 0;
  // allocate and read in blocks  
  BlockSet set(header.nblocks);
  for( int i=0; i<header.nblocks; i++ )
  {
    SmartBlock *block = new SmartBlock(sizes[i]);
    set[i] <<= block;
    if( fread(block->data(),sizes[i],1,fp) != 1 )
      return 0;
  }
  // create object
  BlockableObject *obj = DynamicTypeManager::construct(tid,set);
  FailWhen(!obj,"failed to construct "+tid.toString() );
  ref <<= obj;
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
  have_header = True;
  if( feof(fp) || fread(&header,sizeof(header),1,fp) != 1 )
    header.tid = 0;
  return header.tid;
}

// writes object to file
// Returns number of bytes actually written
//##ModelId=3DB949AE0266
size_t BOIO::write (const BlockableObject &obj)
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
  for( int i=0; i<set.size(); i++ )
    sizes[i] = set[i]->size();
  FailWhen( fwrite(&sizes,sizeof(sizes),1,fp) != 1,"write error" );
  // write out the blocks
  for( int i=0; i<set.size(); i++ )
  {
    FailWhen( fwrite(set[i]->data(),sizes[i],1,fp) != 1,"write error" );
    written += sizes[i];
  }
 
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
