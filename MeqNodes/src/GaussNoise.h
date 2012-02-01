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

#ifndef MEQNODES_GAUSSNOISE_H
#define MEQNODES_GAUSSNOISE_H

#include <MEQ/Function.h>
#include <MeqNodes/BlitzRandom.h>
#include <MeqNodes/NoiseNode.h>
#include <MEQ/MeqVocabulary.h>

#include <MeqNodes/TID-MeqNodes.h>
#pragma aidgroup MeqNodes
#pragma types #Meq::GaussNoise
#pragma aid StdDev Seed Mean Complex

namespace Meq {    

//##ModelId=400E530400AB
class GaussNoise : public NoiseNode
{
public:
    //##ModelId=400E535502AC
  GaussNoise();
    //##ModelId=400E535502AD
  virtual ~GaussNoise();
  
    //##ModelId=400E535502B3
  virtual TypeId objectType() const
  { return TpMeqGaussNoise; }

protected:
  // sets up state from state record
  virtual void setStateImpl (DMI::Record::Ref &rec,bool initializing);

  // Virtual method to be redefined by subclasses. Fills a Vells of the given shape with noise.
  virtual Vells fillNoise (const Vells::Shape &shape,const std::vector<std::vector<const Vells *> > &children);
  

  // current standard deviation
  dcomplex mean_;
  double stddev_;
  // random number generator
  RndGen::Normal<double> generator_;
  
  bool complex_;
};

} // namespace Meq

#endif
