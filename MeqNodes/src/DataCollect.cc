//# DataCollect.cc: prototype visualization node
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
#include <MeqNodes/DataCollect.h>
#include <MeqNodes/Condeq.h>
#include <MeqNodes/ParmTable.h>
#include <MeqNodes/AID-MeqNodes.h>
#include <casa/Arrays/Matrix.h>
#include <casa/Arrays/Vector.h>
    

namespace Meq {

using namespace VellsMath;

const HIID FTopLabel = AidTop|AidLabel;
const HIID FGroupLabel = AidGroup|AidLabel;
const HIID FItemLabel = AidItem|AidLabel;
// we use FValue too, but it's already defined somewhere for us in MeqVocabulary
// const HIID FValue    = AidValue;
const HIID FAttrib   = AidAttrib;

DataCollect::DataCollect()
  : Node(-1,0,1), // at least 1 child must be present
    top_label_(AidPlot|AidData),
    group_label_(AidData),
    item_label_(AidData)
{
  attrib_ <<= new DataRecord;
  disableFailPropagation();
}

DataCollect::~DataCollect()
{
}


void DataCollect::setStateImpl (DataRecord &rec,bool initializing)
{
  Node::setStateImpl(rec,initializing);
  // get/init labels from state record
  rec[FTopLabel].get(top_label_,initializing);
  rec[FGroupLabel].get(group_label_,initializing);
  rec[FItemLabel].get(item_label_,initializing);
  // get attribute record
  if( rec[FAttrib].exists() )
    attrib_ = rec[FAttrib].ref();
}


int DataCollect::getResult (Result::Ref &resref, 
                       const std::vector<Result::Ref> &child_result,
                       const Request &request, bool newreq)
{
// attaches new result to countedref (for returning to caller), and 
// inits a local variable to point to it.
// 0 means 0 VellSets in it
	Result & result = resref <<= new Result(0);

/// no cells in result, since it won't have a Vells either
// // Use cells of first child (they ought to be the same across children 
// // anyway -- we can check later on, but if they're not the same, 
// // someone's put the tree together wrong). We will verify
// // shapes only below, it's faster and easier
// 	const Cells &res_cells = child_result[0]->cells();
// 	const LoShape &res_shape = res_cells.shape();
// 	result.setCells(res_cells);

	DataRecord &toprec = result[top_label_] <<= new DataRecord;
	DataRecord &subrec = toprec[group_label_] <<= new DataRecord;
	DataRecord &datarec = subrec[item_label_] <<= new DataRecord;

  // put a copy of attributes ino the subrecord
  datarec[FAttrib] <<= attrib_.copy();

// create a list for children's Vells, and put it into the subrecord
// Better to always use a list since we don't really know if a given 
// child's Vells will be scalar or array -- easier to figure
// this out on the python side
	DataList &list = datarec[FValue] <<= new DataList;

// put stuff in list. Note that a child result may contain several vellsets,
// so we just loop over them and collect everything into a flat list
  int nlist=0;
	for( int i=0; i<numChildren(); i++ ) 
  {
    const Result &chres = *child_result[i];
    for( int j=0; j<chres.numVellSets(); j++ )
      if( !chres.vellSet(j).isFail() )
  		  list[nlist++] <<= chres.vellSet(j).getValue().getDataArray();
	}
 	return 0;
}

} // namespace Meq
