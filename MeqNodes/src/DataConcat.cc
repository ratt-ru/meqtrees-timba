//# DataConcat.cc: prototype visualization node
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

#include "DataConcat.h"
#include <DMI/List.h>
#include <DMI/Vec.h>
#include <MeqNodes/AID-MeqNodes.h>
    

namespace Meq {

const HIID FTopLabel = AidTop|AidLabel;
//const HIID FValue    = AidValue;
const HIID FAttrib   = AidAttrib;
const HIID FLabel    = AidLabel;

DataConcat::DataConcat()
  : top_label_("Plot.Data")
{
}

DataConcat::~DataConcat()
{
}

void DataConcat::setStateImpl (DMI::Record::Ref &rec,bool initializing)
{
  Node::setStateImpl(rec,initializing);
  // get/init labels from state record
  rec[FTopLabel].get(top_label_,initializing);
  // get attribute record -- boolean false means clear
  if( rec[FAttrib].exists() )
    if( rec[FAttrib].type() == Tpbool )
      attrib_.detach();
    else
      attrib_ = rec[FAttrib].ref();
}

int DataConcat::getResult (Result::Ref &resref, 
                       const std::vector<Result::Ref> &child_result,
                       const Request &, bool)
{
// attaches new result to countedref (for returning to caller), and 
// inits a local variable to point to it.
// 0 means 0 VellSets in it
  Result & result = resref <<= new Result(0);
  
  // init top-level record 
  DMI::Record &toprec = result[top_label_] <<= new DMI::Record;
  // insert attributes, if any
  // if none are specified in the state record, then we'll use
  // the first Attrib record we find in a child result
  bool haveattr = attrib_.valid();
  if( haveattr )
    toprec[FAttrib] <<= attrib_.copy();
  // concatenate all child plot records into value list
  DMI::List &value_list = toprec[FValue] <<= new DMI::List;
  std::vector<int> nval(numChildren(),0);
  bool has_labels = false;
  for( int ich=0; ich<numChildren(); ich++ )
  {
    const DMI::Record *chplot = child_result[ich][top_label_].as_po<DMI::Record>();
    if( chplot )
    {
      // get list of values -- must exist
      const DMI::List *pval = (*chplot)[FValue].as_p<DMI::List>();
      nval[ich] = pval->size();
      value_list.append(*pval);
      // do we have a labels?
      const DMI::Vec *plbl = (*chplot)[FLabel].as_po<DMI::Vec>();
      has_labels |= plbl && plbl->size();
      // if we have no attrs yet, try to get them too
      DMI::Record::Hook attr(*chplot,FAttrib);
      if( !haveattr && attr.isRef() )
      {
        haveattr = true;
        toprec[FAttrib] <<= attr.ref();
      }
    }
  }
  // now, build list of labels if any were found
  if( has_labels )
  {
    DMI::Vec &labels = toprec[FLabel] <<= new DMI::Vec(Tpstring,value_list.size());
    int nlab = 0;
    for( int ich=0; ich<numChildren(); ich++ )
    {
      const DMI::Record *chplot = child_result[ich][top_label_].as_po<DMI::Record>();
      if( chplot )
      {
        // have we got any labels in this plot record? copy them
        const DMI::Vec *plbl = (*chplot)[FLabel].as_po<DMI::Vec>();
        if( plbl && plbl->size() )
        {
          FailWhen(plbl->size()!=nval[ich],
              "mismatch in sizes of Value/Label fields of child plot record");
          for( int i=0; i<nval[ich]; i++ )
            labels[nlab++] = (*plbl)[i].as<string>();
        }
        else // if none, then fill with empty strings to keep alignment with Value list
        {
          for( int i=0; i<nval[ich]; i++ )
            labels[nlab++] = "";
        }
      }
    }
  }
  
  return 0;
}

} // namespace Meq
