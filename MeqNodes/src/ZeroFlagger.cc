//# ZeroFlagger.cc: a trivial flagger: flags ==0 or !=0
//#
//# Copyright (C) 2003
//# ASTRON (Netherlands Foundation for Research in Astronomy)
//# P.O.Box 2, 7990 AA Dwingeloo, The Netherlands, seg@astron.nl
//#
//# This program is free software; you can redistribute it and/or modify
//# it under the terms of the GNU General Public License as published by
//# the Free Software Foundation; either version 2 of the License, or
//# (at your option) any later version.
//#
//# This program is distributed in the hope that it will be useful,
//# but WITHOUT ANY WARRANTY; without even the implied warranty of
//# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//# GNU General Public License for more details.
//#
//# You should have received a copy of the GNU General Public License
//# along with this program; if not, write to the Free Software
//# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
//#
//# $Id$

#include <MeqNodes/ZeroFlagger.h>

namespace Meq {

//##ModelId=400E5355029C
ZeroFlagger::ZeroFlagger()
  : Node(1), // 1 child expected
    flagbit_(1),oper_(AidNE)
{}

//##ModelId=400E5355029D
ZeroFlagger::~ZeroFlagger()
{}

void ZeroFlagger::setStateImpl (DataRecord &rec,bool initializing)
{
  Node::setStateImpl(rec,initializing);
  // get flag bit
  rec[FFlagBit].get(flagbit_,initializing);
  // get operation
  DataRecord::Hook oper(rec,FOper);
  if( oper.exists() )
  {
    HIID op;
    if( oper.type() == TpHIID )
      op = oper.as<HIID>();
    else if( oper.type() == Tpstring )
      op = HIID(oper.as<string>());
    else
      NodeThrow1("illegal "+FOper.toString()+" state field");
    if( op.size() != 1 )
      NodeThrow1("illegal "+FOper.toString()+"="+op.toString()+" state field");
    oper_ = op.front();
  }
  else if( initializing )
    oper = oper_;
}

int ZeroFlagger::getResult (Result::Ref &resref, 
                            const std::vector<Result::Ref> &childres,
                            const Request &request,bool)
{
  DbgAssert(childres.size() == 1 );
  // copy child result to output; privatize for writing since we intend
  // to modify flags
  resref = childres[0];
  resref.privatize(DMI::WRITE);
  Result & result = resref();
  // check # of input vellsets
  int nvs = result.numVellSets();
  // loop over vellsets
  for( int iplane = 0; iplane < nvs; iplane++ )
  {
    VellSet &vs = result.vellSetWr(iplane);
    // get main values 
    const Vells &value = vs.getValue();
    if( value.isComplex() )
    {
      NodeThrow1("complex values not allowed in comparison");
    }
    // get pointer to flags -- init flags if needed
    VellSet::FlagArrayType & flags = vs.getOptColWr<VellSet::FLAGS>();
    // apply operation
    if( value.isArray() )
    {
      const LoMat_double &val = value.getRealArray();
      using blitz::where;
      switch( oper_.id() )
      {
        case AidEQ_int: flags |= where(val == 0 , flagbit_ , 0);
                        break;
        case AidNE_int: flags |= where(val != 0 , flagbit_ , 0);
                        break;
        case AidLT_int: flags |= where(val <  0 , flagbit_ , 0);
                        break;
        case AidGT_int: flags |= where(val >  0 , flagbit_ , 0);
                        break;
        case AidLE_int: flags |= where(val <= 0 , flagbit_ , 0);
                        break;
        case AidGE_int: flags |= where(val >= 0 , flagbit_ , 0);
                        break;
        default:
            NodeThrow1("illegal operation configured: "+oper_.toString());
      }
    }
    else
    {
      // value is single scalar
      double val = *(value.realStorage());
      switch( oper_.id() )
      {
        case AidEQ_int: flags |= (val == 0 ? flagbit_ : 0);
                        break;
        case AidNE_int: flags |= (val != 0 ? flagbit_ : 0);
                        break;
        case AidLT_int: flags |= (val <  0 ? flagbit_ : 0);
                        break;
        case AidGT_int: flags |= (val >  0 ? flagbit_ : 0);
                        break;
        case AidLE_int: flags |= (val <= 0 ? flagbit_ : 0);
                        break;
        case AidGE_int: flags |= (val >= 0 ? flagbit_ : 0);
                        break;
        default:
            NodeThrow1("illegal operation configured: "+oper_.toString());
      }
    }
    
  }
  // return 0 flag, since we don't add any dependencies of our own
  return 0;
}

} // namespace Meq
