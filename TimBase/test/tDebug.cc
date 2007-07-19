//  tDebug.cc: Test program for Debug class
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
//
//  $Log$
//  Revision 1.3  2006/01/31 12:23:10  smirnov
//  Common renamed to TimBase
//
//  Revision 1.2  2006/01/31 10:30:15  cvs
//  %lofarcvsmv%: Moved from LOFAR/Timba/TimBase/test, creating new revision
//
//  Revision 1.1  2005/01/17 13:27:33  smirnov
//  %[ER: 16]%
//  Branching off a version of Common
//
//  Revision 1.7  2004/10/08 10:18:13  loose
//  %[ER: 30]%
//
//  Debug class now resides in namespace LOFAR.
//
//  Revision 1.6  2004/01/15 15:48:40  smirnov
//  %[ER: 16]%
//  Changed default definition of sdebug() to return the Debug context name
//
//  Revision 1.5  2003/12/01 12:48:25  loose
//  %[ER: 61]%
//  Moved Exception class from namespace LCS to namespace LOFAR.
//
//  Revision 1.4  2003/11/28 14:44:12  diepen
//  %[ER: 38]%
//  First version of classes to create blobs
//
//  Revision 1.3  2003/10/29 13:54:38  smirnov
//  %[ER: 16]%
//  Cleaned up debug context definition macros
//
//  Revision 1.2  2003/09/29 15:44:09  smirnov
//  %[ER: 16]%
//  Based Debug (and Assert) errors off of LCS::Exception.
//  Cleaned up Assert macros.
//
//  Revision 1.1  2003/08/21 11:20:33  diepen
//  Moved Common to LCS
//
//  Revision 1.5  2002/11/26 08:02:54  diepen
//  %[BugId: 76]%
//  Added test of AssertMsg
//
//  Revision 1.4  2002/09/04 11:16:24  schaaf
//  %[BugId: 87]%
//
//  Put back class constroctor calls in method f()
//  Inserted extra code to prevent "unused variable" warings
//


#include "TimBase/Debug.h"

using namespace LOFAR;
using namespace DebugDefault;

void a()
{
  TRACERPF4 ("msg1");
  TRACERPFN4 (trac1,"msg2");
  TRACER4("intermediate");
  cout << "a debug: " << getDebugContext().name() << endl;
}




class XX
{
public:
  XX() {cout << "XX debug: " << getDebugContext().name() << endl;}
  LocalDebugContext;
};
InitDebugContext(XX,"XXD");

class ZZ
{
public:
  ZZ() {cout << "ZZ debug: " << getDebugContext().name() << endl;}
  LocalDebugContext;
};
InitDebugContext(ZZ,"ZZD");

class YY
{
public:
  YY() {cout << "YY debug: " << getDebugContext().name() << endl;}
  ImportDebugContext(XX);
};

#ifdef getDebugContext
#undef getDebugContext
#endif

void f()
{
  YY y1;
  XX x;
  ZZ z;
  YY y2;
  cout << "f debug: " << getDebugContext().name() << endl;
 
  // Some dirty code to prevent "unused variable" warnings during compilation
  void* ptr;
  ptr = (void*)&y1;
  ptr = (void*)&x;
  ptr = (void*)&z;
  ptr = (void*)&y2;
}


int main()
{
  // Use highest trace level.
  getDebugContext().setLevel(3);
  a();
  f();

  int i0=0;
  int i1=1;
  try {
    AssertMsg (i0==i1, "should give exception");
  } catch (LOFAR::Exception& x) {
    cout << "caught LOFAR::Exception" <<endl;
    cout << x.what() << endl;
  } catch (std::exception& x) {
    cout << "caught unexpected std::exception" <<endl;
    cout << x.what() << endl;
    return 1;
  } catch (...) {
    cout << "caught unknown exception" <<endl;
    return 1;
  }  
  return 0;
}
