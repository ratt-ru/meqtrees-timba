#ifndef _BOIO_h
#define _BOIO_h 1
    
    
#include "DMI/BlockableObject.h"
  
// BOIO - BlockableObject I/O class
// Stores a BO to/from a data file  
//##ModelId=3DB949AE0042
class BOIO
{
  public:
    //##ModelId=3DB949AE0048
      typedef enum { 
        READ,WRITE,APPEND 
      } FileMode;
  
    //##ModelId=3DB949AE024E
      BOIO ();
  
    //##ModelId=3DB949AE024F
      BOIO (const string &filename,int mode = READ);
      
    //##ModelId=3DB949AE0254
      ~BOIO ();
  
      // attaches to a file
    //##ModelId=3DB949AE0255
      int open (const string &filename,int mode = READ);
      
      // closes file
    //##ModelId=3DB949AE025B
      int close ();
  
      // Reads object attaches to ref. Returns its TypeId, or 
      // 0 for no more objects
    //##ModelId=3DB949AE025C
      TypeId read (ObjRef &ref);

      // Stream form of the read operation. Returns True if an object
      // was read
    //##ModelId=3DB949AE0260
      bool operator >> (ObjRef &ref)
      { return read(ref) != 0; } 
      
      // returns TypeId of next object in stream (or 0 for EOF)
    //##ModelId=3DB949AE0265
      TypeId nextType ();
      
      // writes object to file.
      // Returns number of bytes actually written
    //##ModelId=3DB949AE0266
      size_t write (const BlockableObject &obj);
      
      // Stream form of the write operation
    //##ModelId=3DB949AE026A
      BOIO & operator << (const ObjRef &ref)
      { write(ref.deref()); return *this; } 
      
    //##ModelId=3DB949AE026F
      BOIO & operator << (const BlockableObject &obj)
      { write(obj); return *this; } 
  
  private:
    //##ModelId=3DB949AE004D
      typedef struct {
        TypeId tid;
        int   nblocks;
      } ObjHeader;
      
    //##ModelId=3DB949AE023F
      FILE *fp;
    //##ModelId=3DB949AE0241
      int  fmode;
    //##ModelId=3DB949AE0243
      bool have_header;
    //##ModelId=3DB949AE0245
      ObjHeader header;
};    
    
    
#endif
