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

#ifndef DMI_BOIO_h
#define DMI_BOIO_h 1

#include <DMI/BObj.h>
#include <DMI/TypeInfo.h>

namespace DMI
{

// BOIO - DMI::BObj I/O class
// Stores a BO to/from a data file
//##ModelId=3DB949AE0042
class BOIO
{
  ImportDebugContext(DebugDMI);
  public:
    //##ModelId=3DB949AE0048
      typedef enum {
        CLOSED,READ,WRITE,APPEND,
      } FileMode;

    //##ModelId=3DB949AE024E
      BOIO ();

    //##ModelId=3DB949AE024F
      BOIO (const string &filename,int mode = READ);

    //##ModelId=3DB949AE0254
      ~BOIO ();

      bool isOpen () const
      { return fp !=0; }

      // attaches to a file
    //##ModelId=3DB949AE0255
      int open (const string &filename,int mode = READ);

      // closes file
    //##ModelId=3DB949AE025B
      int close ();

      // Reads object attaches to ref. Returns its TypeId, or
      // 0 for no more objects
    //##ModelId=3DB949AE025C
      TypeId readAny (ObjRef &ref);

      template<class T>
      bool read (CountedRef<T> &ref);

      // Stream form of the read operation. Returns true if an object
      // was read
    //##ModelId=3DB949AE0260
      template<class T>
      bool operator >> (CountedRef<T> &ref)
      { return read(ref); }

      // return the current seek offset in the file
      long ftell ();

      // seeks the fp to the given offset
      void fseek (long offset);

      // rewinds file to start
      void rewind ();

      // flushes file
      void flush ();

      // returns TypeId of next object in stream (or 0 for EOF)
    //##ModelId=3DB949AE0265
      TypeId nextType ();

      // writes object to file.
      // Returns number of bytes actually written
    //##ModelId=3DB949AE0266
      size_t write (const DMI::BObj &obj);

      // Stream form of the write operation
    //##ModelId=3DB949AE026A
      BOIO & operator << (const ObjRef &ref)
      { write(ref.deref()); return *this; }

    //##ModelId=3DB949AE026F
      BOIO & operator << (const DMI::BObj &obj)
      { write(obj); return *this; }

    //##ModelId=3E53C7990224
      int fileMode () const;

    //##ModelId=3E54BDE70210
      const string & fileName () const;

    //##ModelId=3E54BDE70228
      string stateString () const;

  private:
    //##ModelId=3DB949AE004D
      typedef struct {
        TypeId tid;
        int   nblocks;
      } ObjHeader;

    //##ModelId=3DB949AE023F
      FILE *fp;
    //##ModelId=3E54BDE701DB
      string fname;
    //##ModelId=3DB949AE0241
      int  fmode;
    //##ModelId=3DB949AE0243
      bool have_header;
    //##ModelId=3DB949AE0245
      ObjHeader header;
};

//##ModelId=3E53C7990224
inline int BOIO::fileMode () const
{
  return fmode;
}

//##ModelId=3E54BDE70210
inline const string & BOIO::fileName () const
{
  return fname;
}

template<>
inline bool BOIO::read (CountedRef<DMI::BObj> &ref)
{ return readAny(ref) != 0; }

template<class T>
inline bool BOIO::read (CountedRef<T> &ref)
{
  TypeId tid = nextType();
  if( !tid )
    return 0;
  FailWhen( tid != DMITypeTraits<T>::typeId,
      "expecting object of type "+typeIdOf(T).toString()+
      ", boio file contains "+tid.toString());
  return readAny(ref.ref_cast((DMI::BObj*)0)) != 0;
}

};
#endif
