//# DataConcat.cc: prototype visualization node
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

#include <MEQ/Request.h>
#include <MEQ/Vells.h>
#include <MEQ/Function.h>
#include <MEQ/MeqVocabulary.h>
#include <DMI/DynamicTypeManager.h>
#include <DMI/DataList.h>
#include <MeqNodes/DataConcat.h>
#include <MeqNodes/Condeq.h>
#include <MeqNodes/ParmTable.h>
#include <MeqNodes/AID-MeqNodes.h>
#include <casa/Arrays/Matrix.h>
#include <casa/Arrays/Vector.h>
    

namespace Meq {

using namespace VellsMath;

const HIID FTopLabel = AidTop|AidLabel;
const HIID FSkeleton = AidSkeleton;

DataConcat::DataConcat()
  : Node(-1,0,1), // at least 1 child must be present
    top_label_("Plot.Data")
{
  skel_ <<= new DataRecord;
  disableFailPropagation();
}

DataConcat::~DataConcat()
{
}


void DataConcat::setStateImpl (DataRecord &rec,bool initializing)
{
  Node::setStateImpl(rec,initializing);
  // get/init list top-level label from state record. 
  rec[FTopLabel].get(top_label_,initializing);
  // get/init skeleton record
  if( rec[FSkeleton].exists() )
    skel_ = rec[FSkeleton].ref();
}


int DataConcat::getResult (Result::Ref &resref, 
                       const std::vector<Result::Ref> &child_result,
                       const Request &, bool)
{
  std::vector<Thread::Mutex::Lock> child_reslock(numChildren());
  lockMutexes(child_reslock,child_result);
// attaches new result to countedref (for returning to caller), and 
// inits a local variable to point to it.
// 0 means 0 VellSets in it
	Result & result = resref <<= new Result(0);
  
  // init top-level record by creating a private deep-copy of the skeleton
  DataRecord &toprec = result[top_label_] <<= new DataRecord(*skel_,DMI::WRITE|DMI::PRIVATIZE|DMI::DEEP);
  for( int j=0; j<numChildren(); j++ )
  {
    const Result &chres = *child_result[j];
    // merge corresponding top-level record from each child.
    // DataRecord has a convenient merge() method for this.
    // The true/false arguemtn tells it whether to overwrite existing
    // fields or not
    if( chres[top_label_].exists() )
    {
      const DataRecord &child_toprec = chres[top_label_].as<DataRecord>();
      // iterate over all fields in the child's top-level record
      HIID id;
      NestableContainer::Ref ncref;
      DataRecord::Iterator iter = child_toprec.initFieldIter();
      while( child_toprec.getFieldIter(iter,id,ncref) )
      {
        // cast the field reference to a sub-record -- this will throw an exception
        // if the field is not a DataRecord, but in this case we're entitled to fail anyway
        const DataRecord &child_subrec = *(ncref.ref_cast<DataRecord>());
        // if subrecord already exists in the top-level record, merge child into it
        if( toprec[id].exists() )
          toprec[id].as_wr<DataRecord>().merge(child_subrec);
        else // else init with a deep-copy of child
          toprec[id] <<= new DataRecord(child_subrec,DMI::WRITE|DMI::PRIVATIZE|DMI::DEEP);
      }
    }
  }
 	return 0;
}

} // namespace Meq
