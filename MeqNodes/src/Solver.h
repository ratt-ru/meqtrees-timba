//# Solver.h: Class to solve equations
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

#ifndef MEQNODES_SOLVER_H
#define MEQNODES_SOLVER_H
    
#include <MEQ/Node.h>
#include <MEQ/VellSet.h>
#include <scimath/Fitting/LSQaips.h>

#include <set>

#pragma types #Meq::Solver

#pragma aid Solve Result Incremental Solutions Tile Size

// The comments below are used to automatically generate a default
// init-record for the class 

//defrec begin MeqSolver
//  Represents a solver.
//  A MeqSolver can have an arbitrary number of children.
//field: flag_mask -1
//  Flag mask applied to condeq results. No equations are generated for
//  flagged points. Default -1 uses all flags.
//field: num_iter 3  
//  Number of iterations to do in a solve
//field: epsilon 0
//  Convergence criterium; not used at the moment
//field: use_svd T
//  Use singular value decomposition in solver?
//field: last_update F
//  Send up a final update to parms after solve
//field: save_funklets F
//  Send up a Save.Funklets command after solve
//field: parm_group hiid('parm')
//  HIID of the parameter group to use. 
//field: solvable [=]
//  Command record which is sent up in the rider of the first request
//  (as req.rider.<parm_group>). This is meant to set parms to solvable. 
//  The simplest way to create this is by using meq.solvable_list("names"), 
//  which returns such a record, given a  vector of solvable parm names. 
//  It is also possible to create more elaborate command records from scratch,
//  if more sophisticated manipulation of state is required.
//defrec end


namespace Meq {

class Request;


//##ModelId=400E5304008C
class Solver : public Node
{
public:
    //##ModelId=400E53550260
  Solver();

    //##ModelId=400E53550261
  virtual ~Solver();

  // Returns the class TypeId
    //##ModelId=400E53550263
  virtual TypeId objectType() const;

  LocalDebugContext;

protected:
    //##ModelId=400E53550267
  //##Documentation
  virtual void setStateImpl (DMI::Record::Ref &rec,bool initializing);
  
    //##ModelId=400E5355026B
  //##Documentation
  //## override this, since we poll children ourselves
  virtual int pollChildren (std::vector<Result::Ref> &child_results,
                            Result::Ref &resref,
                            const Request &req);
  
    //##ModelId=400E53550270
  //##Documentation
  //## Get the result for the given request.
  virtual int getResult (Result::Ref &resref, 
                         const std::vector<Result::Ref> &childres,
                         const Request &req,bool newreq);
  
  // solver result contains no spids
  virtual int discoverSpids (Result::Ref &,const std::vector<Result::Ref> &,
                             const Request &)
  { return 0; }
  
private:
  // this method is called from getResult() to populate spids_ (the internal
  // SpidMap) from a spidmap record returned by spid discovery.
  int populateSpidMap (const DMI::Record &spidmap_rec,const Cells &cells);

  // this method is called from getResult() to fill solver equations
  // from the given VellSet. Templated because double and dcomplex values
  // are treated differently.
  template<typename T>
  void fillEquations (const VellSet &vs);

  // helper function for fillEquations()
  template<typename T>
  inline void fillEqVectors (int npert,int uk_index[],
        const T &diff,const std::vector<Vells::ConstStridedIterator<T> > &deriv_iter);
      
  
  //##Documentation
  //## Do a solution.
  //## If it is the last iteration, the solution is put in a new request
  //## and 'sent' to the children to update the parms. Optionally the parm
  //## tables are updated too.
  //## <br> If it is not the last iteration, the solution is put in the
  //## given request, so a next iteration can first update the parms.
  //## debugRec is pointer to debug record, 0 for no debugging
  void solve (casa::Vector<double>& solution,Request::Ref &reqref,
	            DMI::Record& solRec,DMI::Record *debugRec,
              bool saveFunklets);
  
  
  // === state set from the state record
  
  int             flag_mask_;         // flag mask applied during solve
  bool            do_save_funklets_;  // save funklets after solve?
  bool            do_last_update_;    // send up final update after solve?
  bool            use_svd_;           // use SVD?
  int             max_num_iter_;      // max # of iterations
  double          min_epsilon_;       // epsilon threshold
  
  int             debug_lvl_;         // debug detail generated
  
  //##Documentation
  //## solvable parm group for this solver ("Parm" by default)
  HIID            parm_group_;
  
  // symdeps generated by the solver
  vector<HIID>    iter_symdeps_;
  int             iter_depmask_;
  
  
  // === other internal state
  
    //##ModelId=400E5355025A
  casa::LSQaips   solver_;
  int             num_spids_;
  int             num_unknowns_;
  int             num_equations_;

  // # of child whose result is currently being processed
  int cur_child_;
  
  typedef VellSet::SpidType SpidType;
  
  // spid map populated during discovery
  typedef struct
  {
    int  nuk;                         // how many unknowns per this spid (1 if not tiled)
    int  uk_index;                    // index of first unknown in vector
    int  tile_size  [Axis::MaxAxis];  // tile sizes per each axis
    int  tile_stride[Axis::MaxAxis];  // tile stride per each axis (how many uknowns are strides when we go to next tile)
    int  tile_index [Axis::MaxAxis];  // current tile index (used when filling equations)
    int  tile_uk0   [Axis::MaxAxis];  // current tile slice (used when filling equations)
  } SpidInfo;   // haha 

  typedef std::map<SpidType,SpidInfo> SpidMap;
  
  SpidMap spids_;
  
  // in addition, we need a map from nodeindices to their associated unknowns
  typedef std::set<int> IndexSet;
  typedef std::map<int,IndexSet> ParmUkMap;
  
  ParmUkMap parm_uks_;
  
  // various temporary arrays used when filling equations, we keep them here
  // as members for convenience, and to minimize reallocations
  std::vector<double> deriv_real_;
  std::vector<double> deriv_imag_;
  Vells::Strides      *strides_;
  
};


} // namespace Meq

#endif
