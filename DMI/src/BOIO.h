#ifndef _BOIO_h
#define _BOIO_h 1
    
    
#include "DMI/BlockableObject.h"
  
// BOIO - BlockableObject I/O class
// Stores a BO to/from a data file  
class BOIO
{
  public:
      typedef enum { 
        READ,WRITE,APPEND 
      } FileMode;
  
      BOIO ();
  
      BOIO (const string &filename,int mode = READ);
      
      ~BOIO ();
  
      // attaches to a file
      int open (const string &filename,int mode = READ);
      
      // closes file
      int close ();
  
      // Reads object attaches to ref. Returns its TypeId, or 
      // 0 for no more objects
      TypeId read (ObjRef &ref);

      // Stream form of the read operation. Returns True if an object
      // was read
      bool operator >> (ObjRef &ref)
      { return read(ref) != 0; } 
      
      // returns TypeId of next object in stream (or 0 for EOF)
      TypeId nextType ();
      
      // writes object to file.
      // Returns number of bytes actually written
      size_t write (const BlockableObject &obj);
      
      // Stream form of the write operation
      BOIO & operator << (ObjRef &ref)
      { write(ref.deref()); return *this; } 
      
      BOIO & operator << (const BlockableObject &obj)
      { write(obj); return *this; } 
  
  private:
      typedef struct {
        TypeId tid;
        int   nblocks;
      } ObjHeader;
      
      FILE *fp;
      int  fmode;
      bool have_header;
      ObjHeader header;
};    
    
    
#endif
