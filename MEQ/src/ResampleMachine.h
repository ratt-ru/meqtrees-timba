//# ResampleMachine.h: helper class for resampling VellSets
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

#ifndef MEQ_RESAMPLEMACHINE_H
#define MEQ_RESAMPLEMACHINE_H
    
#include <MEQ/Cells.h>
#include <MEQ/VellSet.h>

namespace Meq {

// A ResampleMachine performs resampling of VellSets from one Cells to another.
// The version implemented here only supports integer resamplings (i.e. where
// the input/output grids along each axis are regular supersets or subsets of 
// each other) by a fixed factor. Increasing resolution is referred to here as
// upsampling (or expansion), decreasing is called integrating.
// For the time being, upsampling is done by repeating the value within the
// block of cells; linear interpolation will be supported in the future.
// Note that the machine supports a mixed mode, where one axis is integrated,
// and the other is upsampled. In this case, integration  of the input to a 
// "supercell" is performed first (supercells are obtained by using the
// lowest resolution along each axis); the supercell is then upsampled. 
// Note that domains are currently not checked but really should be.
// If the input VellSet contains flags, these will be applied to the input;
// flagged values are omitted from integration or averaging, and the output
// is normalized as appropriate. 
// The machine can work with integrated values or samplings. For the time being,
// it is assumed that cell sizes are regular (i.e. the cells are the same and
// completely cover each regular segment), and no adjustment for cell sizes
// is done.
    
class ResampleMachine
{
public:
  ResampleMachine ();

  ResampleMachine (const Cells &output);

  ResampleMachine (const Cells &output,const Cells &input);

  void setOutputRes (const Cells &);

  void setInputRes  (const Cells &);

  void setRes       (const Cells &output,const Cells &input)
  { setOutputRes(output); setInputRes(input); }
  
  // ResampleMachine is valid if both resolutions are already set
  bool valid () const
  { return inres.valid() && outres.valid(); }
  
  bool isIdentical () const
  { return identical; }
  
  void setFlagMask (int fm)
  { flag_mask = fm; }
  
  void setFlagBit (int fb)
  { flag_bit = fb; }
  
  void setFlagDensity (float fd)
  { flag_density = fd; }
  
  void setFlagPolicy (int fm,int fb,float fd)
  { flag_mask = fm; flag_bit = fb; flag_density = fd; }

  void apply (VellSet::Ref &out,const VellSet::Ref &in,bool integrated);
  
  VellSet::Ref apply (const VellSet::Ref &in,bool integrated)
  { VellSet::Ref out; apply(out,in,integrated); return out; }
      
      
private:
  Cells::Ref inres;
  Cells::Ref outres;

  // resamples vells according to current setup (see below)
  Vells::Ref resampleVells (const Vells &in);
    
  // templated helper function for above, which does the actual work
  template<class T>
  void doResample (Vells::Ref &voutref,const blitz::Array<T,2> &in);

  int flag_mask;
  
  int flag_bit;
  
  float flag_density;

  // All members below are used by resampleVells() to do the actual
  // resampling. These are meant to be set up in setInputRes(), before calling
  // resampleVells() repeatedly on all input Vells.
  
  // flag: resolutions are identical, so do nothing
  bool identical;
  // shape of output Vells
  LoShape outshape;    
  // # of cells to integrate in X/Y (1 if expanding)
  int     nsum[2];
  // # of cells to expand by in X/Y (1 if integrating)
  int     nexpand[2];  
  // renormalization factor applied to output cell after summing up 
  // the input cells. This incorporates averaging/integration. Since we only
  // deal with integer resamplings for now, this is a single value for all
  // cells
  double renorm_factor;
  // output renormalization matrix, incorporating renotrm_factor, plus 
  // partially flagged integrations, etc.
  // Note that only the top left corner of each "supercell" is actually 
  // computed and used. A "supercell" is the cell corresponding to the 
  // coarsest resolution:
  // * when expanding, the supercell is the input cell
  // * when integrating, the supercell is the output cell
  // * when doing both, the supercell is composed of the two largest extents
  //   in both dimensions 
  LoMat_double renorm;
  
  // pointer to output flags, 0 if no flagging
  VellSet::FlagArrayType *outflags;
  
  // pointer to input flags, 0 if no flagging
  const VellSet::FlagArrayType *inflags;
};  


} // namespace Meq


#endif
