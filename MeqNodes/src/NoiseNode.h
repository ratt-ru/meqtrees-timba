//# GaussNoise.h: Give Gauss noise
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
//# $Id$

#ifndef MEQNODES_NOISENODE_H
#define MEQNODES_NOISENODE_H

#include <MEQ/TensorFunction.h>

namespace Meq {    

// state field to specify active axes
const HIID FAxesIndex = AidAxes|AidIndex;

//##ModelId=400E530400AB
// Abstract base class for noise generators
// Basically, this provides handling of output shapes
class NoiseNode : public TensorFunction
{
  public:
    NoiseNode (int nchildren=-1,const HIID *labels = 0,int nmandatory=-1);
  
  protected:
    virtual void computeResultCells (Cells::Ref &ref,const std::vector<Result::Ref> &childres,const Request &request);
    virtual LoShape getResultDims (const vector<const LoShape *> &input_dims);
    virtual void evaluateTensors (std::vector<Vells> & out,   
        const std::vector<std::vector<const Vells *> > &args );
      
    // Virtual method to be redefined by subclasses. Fills a Vells of the given shape with noise.
    virtual Vells fillNoise (const Vells::Shape &shape,const std::vector<std::vector<const Vells *> > &children) =0;
    
    // sets up axes from state record
    virtual void setStateImpl (DMI::Record::Ref &rec,bool initializing);
    
    // active axes -- if empty, shape of input cells will be used
    std::vector<int> axes_;
    
    // dims of output
    Result::Dims dims_;

    // shape of output
    Vells::Shape shape_;
};

} // namespace Meq

#endif
