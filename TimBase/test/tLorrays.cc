//#  tLorrays.cc: test program for Lorray classes
//#
//#  Copyright (C) 2002
//#  ASTRON (Netherlands Foundation for Research in Astronomy)
//#  P.O.Box 2, 7990 AA Dwingeloo, The Netherlands, seg@astron.nl
//#
//#  This program is free software; you can redistribute it and/or modify
//#  it under the terms of the GNU General Public License as published by
//#  the Free Software Foundation; either version 2 of the License, or
//#  (at your option) any later version.
//#
//#  This program is distributed in the hope that it will be useful,
//#  but WITHOUT ANY WARRANTY; without even the implied warranty of
//#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//#  GNU General Public License for more details.
//#
//#  You should have received a copy of the GNU General Public License
//#  along with this program; if not, write to the Free Software
//#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
//#
//#  $Id$

#include <lofar_config.h>
#include <Common/lofar_iostream.h>

using namespace LOFAR;

#ifdef HAVE_BLITZ

#include <Common/Lorrays.h>

int main ()
{
  LoVec_double vec1(3);
  vec1 = 1,2,3;
  cout<<"vec1: "<<vec1<<endl;
  
  LoMat_double mat1(3,3);
  mat1 = 1,2,3,
         4,5,6,
         7,8,9;
  cout<<"mat1: "<<mat1<<endl;
  
  LoMat_double mat2(3,3);
  mat2  = mat1 + mat1;
  cout<<"mat2: "<<mat2<<endl;
  
  LoMatShape shape2(5,5);
  
  LoMat_double mat3(shape2);
  cout<<"mat3: "<<mat3<<endl;
  
  LoMatPos pos(3,3);
  cout<<"mat3(3,3): "<<mat3(pos)<<endl;
  exit(0);
}

#else

int main()
{
  cout << "Not tested (Blitz not configured)" << endl;
  exit(0);
}

#endif
