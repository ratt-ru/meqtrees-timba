//# Request.cc: The request for an evaluation of an expression
//#
//# Copyright (C) 2002
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

#include "Request.h"
#include "Node.h"
#include "MeqVocabulary.h"

namespace Meq {

static NestableContainer::Register reg(TpMeqRequest,True);

//##ModelId=3F8688700056
Request::Request()
: itsCalcDeriv(0),itsClearSolver(false),itsNumSteps(-1),
  itsCells(0),hasRider_(false)
{
}

//##ModelId=3F8688700061
Request::Request (const DataRecord &other,int flags,int depth)
: DataRecord  (other,flags,depth),
  itsCalcDeriv(0),itsClearSolver(false),itsNumSteps(-1),
  itsCells(0),hasRider_(false)
{
  validateContent();
}

//##ModelId=400E535403DD
Request::Request (const Cells& cells,int calcDeriv,const HIID &id,int cellflags)
: itsClearSolver(false),itsNumSteps(-1),itsCells(0),hasRider_(false)
{
  setCells(cells,cellflags);
  setId(id);
  setCalcDeriv(calcDeriv);
}

//##ModelId=400E53550016
Request::Request (const Cells * cells, int calcDeriv, const HIID &id,int cellflags)
: itsClearSolver(false),itsNumSteps(-1),itsCells(0),hasRider_(false)
{
  setCells(cells,cellflags);
  setId(id);
  setCalcDeriv(calcDeriv);
}

// Set the request id.
//##ModelId=3F8688700075
void Request::setId (const HIID &id)
{
  (*this)[FRequestId] = itsId = id;
}

void Request::setCalcDeriv (int calc)
{ 
  (*this)[FCalcDeriv] = itsCalcDeriv = calc; 
}

void Request::setClearSolver (bool clearSolver)
{ 
  (*this)[FClearSolver] = itsClearSolver = clearSolver; 
}

void Request::setNumSteps (int numSteps)
{ 
  (*this)[FNumSteps] = itsNumSteps = numSteps; 
}

//##ModelId=3F868870006E
void Request::setCells (const Cells * cells,int flags)
{
  itsCells = flags&DMI::CLONE ? new Cells(*cells) : cells;
  DataRecord::replace(FCells,itsCells,flags|DMI::READONLY);
}

//##ModelId=400E53550049
void Request::validateContent ()
{
  Thread::Mutex::Lock lock(mutex());
  // ensure that our record contains all the right fields, and that they're
  // indeed writable. Setup shortcuts to their contents
  try
  {
    // get cells field
    Hook hcells(*this,FCells);
    if( hcells.exists() )
      itsCells = hcells.as_p<Cells>();
    else
      itsCells = 0;
    // request ID
    itsId = (*this)[FRequestId].as<HIID>(HIID());
    // calc-deriv flag
    itsCalcDeriv = (*this)[FCalcDeriv].as<int>(0);
    // clearsolver flag
    itsClearSolver = (*this)[FClearSolver].as<bool>(false);
    // nr of solvesteps 
    itsNumSteps = (*this)[FNumSteps].as<int>(-1);
   // rider
    validateRider();
  }
  catch( std::exception &err )
  {
    cerr<<"Failed request: "<<sdebug(10);
    Throw(string("validate of Request record failed: ") + err.what());
  }
  catch( ... )
  {
    Throw("validate of Request record failed with unknown exception");
  }  
}

void Request::validateRider ()
{
  hasRider_ = DataRecord::hasField(FRider);
}

int Request::remove (const HIID &id)
{ 
  if( id == FCells || id == FRequestId || id==FCalcDeriv
      || id==FClearSolver || id==FNumSteps)
    Throw("remove(" + id.toString() +" from a Meq::Request not allowed"); 
  return DataRecord::remove(id);
}

void Request::processRider (Node &node) const
{
  if( !hasRider() )
    return;
  cdebug(3)<<"  processing request rider"<<endl;
  const DataRecord &rider = (*this)[FRider].as<DataRecord>();
  const std::vector<HIID> & groups = node.getNodeGroups();
  for( uint i=0; i<groups.size(); i++ )
  {
    Hook hgroup(rider,groups[i]);
    if( hgroup.exists() )
    {
      cdebug(3)<<"    found CSR for group "<<groups[i]<<endl;
      DataRecord::Ref group = hgroup.ref();
      // check for command_all entry
      {
        Hook hlist(group,FCommandAll);
        if( hlist.exists() )
        {
          cdebug(4)<<"    found "<<FCommandAll<<", calling processCommands()"<<endl;
          node.processCommands(hlist.as<DataRecord>(),*this);
        }
      }
      // process command_by_list (pattern matching list)
      {
        Hook hlist(group,FCommandByList);
        if( hlist.exists() )
        {
          DataField &list = hlist.as_wr<DataField>();
          cdebug(3)<<"      checking "<<list.size()<<" list entries"<<endl;
          bool matched = false;
          for( int i=0; i<list.size() && !matched; i++ )
          {
            DataRecord &entry = list[i].as_wr<DataRecord>();
            std::vector<string> names;
            std::vector<int> indices;
            Hook hnames(entry,FName),
                 hindices(entry,FNodeIndex);
            if( hnames.exists() ) // get list of names, if any
              names = hnames;
            if( hindices.exists() ) // get list of node indices, if any
              indices = hindices;
            cdebug(4)<<"        "<<indices.size()<<" indices, "
                     <<names.size()<<" names"<<endl;
            matched = ( std::find(indices.begin(),indices.end(),node.nodeIndex())
                          != indices.end() ||
                        std::find(names.begin(),names.end(),node.name())
                          != names.end() ||
                        ( names.empty() && indices.empty() ) );
            // call appropriate handlers if node was matched
            if( matched )
            {
              cdebug(4)<<"        node matched, calling processCommands()"<<endl;
              node.processCommands(entry,*this);
            }
          }
          if( !matched ) {
            cdebug(3)<<"      no matches in list"<<endl;
          }
        }
      }
      // process command_by_nodeindex list
      {
        Hook hlist(group,FCommandByNodeIndex);
        if( hlist.exists() && hlist[node.nodeIndex()].exists() )
        {
          cdebug(4)<<"    found "<<FCommandByNodeIndex<<"["<<node.nodeIndex()<<"], calling processCommands()"<<endl;
          node.processCommands(hlist.as<DataRecord>(),*this);
        }
      }
    }
  }
}



} // namespace Meq
