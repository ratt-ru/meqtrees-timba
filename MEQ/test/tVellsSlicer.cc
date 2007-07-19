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

#include "../src/VellsSlicer.h"
    
using namespace Meq;
    
int main ()
{
  Axis::addAxis("U");
  Axis::addAxis("V");
  Axis::addAxis("L");
  Axis::addAxis("M");

  {
  // 2D test
  int nc = 2;
  LoShape shape;
  shape.resize(3,nc);
  Vells in(0.0,shape);
  blitz::Array<double,3> arr(in.getArray<double,3>());
  // fill with values, using each decimal digit as the axis index
  arr = 9000+blitz::tensor::i*100 +
        blitz::tensor::j*10 +
        blitz::tensor::k;
  cout<<"Source array: "<<arr<<endl;
  
  // create output array
  Vells out(0.0,shape);
  
  // now we're going to slice the output along axes 2 and 3, and
  // the input along axes 4 and 5, and assign slices of the input
  // to the output
  VellsSlicer<double,1> slout(out,0);
  ConstVellsSlicer<double,1> slin(in,1);
  
  int nsl = 0;
  for( ; slin.valid(); slin.incr(),slout.incr(),nsl++ )
  {
    cout<<"Slice "<<nsl<<":"<<slin.array()<<endl;
    slout.array() = slin.array();
  }
  
  cout<<nsl<<" slices processed.\n";
      
  cout<<"Output array: "<<out.getArray<double,3>();
  }
  
  {
  // create a 5D source vells
  LoShape shape(2,4,5,5,4);
  Vells in(0.0,shape);
  blitz::Array<double,5> arr(in.getArray<double,5>());
  // fill with values, using each decimal digit as the axis index
  arr = 900000+blitz::tensor::i*1e+4 +
        blitz::tensor::j*1e+3 +
        blitz::tensor::k*1e+2 +
        blitz::tensor::l*1e+1 +
        blitz::tensor::m;
  cout<<"Source array: "<<arr<<endl;
  
  // create output array
  Vells out(0.0,shape);
  
  // now we're going to slice the output along axes 1 and 3, and
  // the input along axes 2 and 4, and assign slices of the input
  // to the output
  VellsSlicer<double,2> slout(out,1,3);
  ConstVellsSlicer<double,2> slin(in,4,2);
  
  int nsl = 0;
  for( ; slin.valid(); slin.incr(),slout.incr(),nsl++ )
  {
    cout<<"Slice "<<nsl<<":"<<slin.array()<<endl;
    slout = slin();
  }
  cout<<nsl<<" slices processed.\n";
      
  cout<<"Output array: "<<out.getArray<double,5>();
  }
  
  return 0;
}
