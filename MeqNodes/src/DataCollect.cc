//# DataCollect.cc: prototype visualization node
//#
//# Copyright (C) 2002-2007
//# ASTRON (Netherlands Foundation for Research in Astronomy)
//# and The MeqTree Foundation
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

#include "DataCollect.h"
#include <DMI/List.h>
#include <DMI/Vec.h>
#include <MeqNodes/AID-MeqNodes.h>
    

namespace Meq {

const HIID FTopLabel = AidTop|AidLabel;
const HIID FValue    = AidValue;
const HIID FAttrib   = AidAttrib;
const HIID FLabel    = AidLabel;


DataCollect::DataCollect()
  : Node(-2), // at least 1 child must be present
    top_label_(AidPlot|AidData)
//    group_label_(AidData),
//    item_label_(AidData)
{
  attrib_ <<= new DMI::Record;
  children().setFailPolicy(AidIgnore);
  stepchildren().setFailPolicy(AidIgnore);
  enableMultiThreadedPolling();
}

DataCollect::~DataCollect()
{
}


void DataCollect::setStateImpl (DMI::Record::Ref &rec,bool initializing)
{
  Node::setStateImpl(rec,initializing);
  // get/init labels from state record
  rec[FTopLabel].get(top_label_,initializing);
//  rec[FGroupLabel].get(group_label_,initializing);
//  rec[FItemLabel].get(item_label_,initializing);
  // get attribute record
  if( rec[FAttrib].exists() )
    attrib_ = rec[FAttrib].ref();
  // get labels field
  if( rec[FLabel].exists() )
    labels_ = rec[FLabel].ref();
  else if( initializing ) // initialize labels with child names
  {
    DMI::Vec &lbl = rec[FLabel] <<= new DMI::Vec(Tpstring,numChildren());
    labels_ <<= &lbl;
    for( int i=0; i<numChildren(); i++ )
      lbl[i] = children().getChild(i).name();
  }
}


int DataCollect::getResult (Result::Ref &resref, 
                       const std::vector<Result::Ref> &child_result,
                       const Request &request, bool newreq)
{
// attaches new result to countedref (for returning to caller), and 
// inits a local variable to point to it.
// 0 means 0 VellSets in it
  Result & result = resref <<= new Result(0);

  DMI::Record &toprec = result[top_label_] <<= new DMI::Record;

  // put a copy of attributes into the subrecord
  if( attrib_.valid() )
    toprec[FAttrib] <<= attrib_.copy();
  if( labels_.valid() )
    toprec[FLabel] <<= labels_.copy();

// create a list for children's Vells, and put it into the subrecord
// Better to always use a list since we don't really know if a given 
// child's Vells will be scalar or array -- easier to figure
// this out on the python side
  DMI::List &vallist = toprec[FValue] <<= new DMI::List;

// put stuff in list. Note that a child result may contain several vellsets,
// so we just loop over them and collect everything into a flat list
  for( int i=0; i<numChildren(); i++ ) 
  {
    const Result &chres = *child_result[i];
    // plot record in child result? (0 if none)
    const DMI::Record *chplot = chres[top_label_].as_po<DMI::Record>();
    int nvs = chres.numVellSets();
    // count of how many things need to be inserted: one for a valid
    // child plot record, and one per each valid VellSet
    int count = chplot ? 1 : 0;
    for( int j=0; j<chres.numVellSets(); j++ )
      if( !chres.vellSet(j).isFail() )
        count++;
    // Determine how to insert. If only one thing to insert (i.e. 
    // one main value, or one plot record), insert directly into value
    // list, else insert a little sublist of stuff. If there's nothing
    // to insert, mark this by an empty sublist (since we must always have 
    // one entry per child)
    DMI::List * plist;
    if( count == 1 )
      plist = &vallist;
    else
      vallist.addBack(plist = new DMI::List);
    // insert plot record, if any
    if( chplot )
      plist->addBack(chplot);
    // insert main values, if any
    for( int j=0; j<chres.numVellSets(); j++ )
      if( !chres.vellSet(j).isFail() )
        plist->addBack(&(chres.vellSet(j).getValue()));
  }
  return 0;
}

} // namespace Meq
