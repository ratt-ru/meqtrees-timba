//# Solver.h: Class to solve equations
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

#ifndef MEQNODES_SOLVER_H
#define MEQNODES_SOLVER_H
    
#include <MEQ/Node.h>
#include <MEQ/VellSet.h>
#include <scimath/Fitting/LSQaips.h>

#include <set>

#pragma types #Meq::Solver

#pragma aid Solve Result Incremental Solutions Tile Tiles Info Size Iterations 
#pragma aid Converged Array Convergence Quota Tiling Tilings Super Size Stride
#pragma aid Total SS Uk Unknown Unknowns Spid Set Stride Map Colin LM Factor MT 
#pragma aid Begin End Deriv Balanced Equations Ready String 
#pragma aid Debug File Interrupt Solution Flush Tables

// The comments below are used to automatically generate a default
// init-record for the class 

//defrec begin MeqSolver
//  Represents a solver.
//  A MeqSolver can have an arbitrary number of children.
//field: flag_mask -1
//  Flag mask applied to condeq results. No equations are generated for
//  flagged points. Default -1 uses all flags.
//field: eval_mode 1
//  Use single or double derivatives.
//field: num_iter 3  
//  Number of iterations to do in a solve
//field: epsilon 0
//  Convergence criterium
//field: convergence_quota_ 0.8
//  When doing a subtiled solution, how many subsolvers have to converge
//  before the result is deemed to have converged (i.e. 0.8 = 80%)
//field: use_svd T
//  Use singular value decomposition in solver?
//field: last_update F
//  Send up a final update to parms after solve
//field: save_funklets F
//  Send up a Save.Funklets command after solve
//field: flush_tables F
//  Flush parmtables at end of every solution. Default is not to flush.
//field: parm_group hiid('parm')
//  HIID of the parameter group to use. 
//field: solvable [=]
//  Command record which is sent up in the rider of the first request
//  (as req.rider.<parm_group>). This is meant to set parms to solvable. 
//  The simplest way to create this is by using meq.solvable_list("names"), 
//  which returns such a record, given a  vector of solvable parm names. 
//  It is also possible to create more elaborate command records from scratch,
//  if more sophisticated manipulation of state is required.
//  field: debug_file='filename'
//  Write condeq residuals after each call to getResult()
//  If not specified, not written.
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
  virtual int pollChildren (Result::Ref &resref,
                            std::vector<Result::Ref> &childres,
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

  // this method is called from getResult() to fill in a request rider
  // using the current solution
  void fillRider (Request::Ref &reqref,bool save_funklets,bool converged);
  
  // === state set from the state record
  typedef struct
  {
    bool            use_svd;        // use SVD?
    double          epsilon;        // epsilon threshold
    double          epsilon_deriv;  // epsilon derivative threshold. New Apr 06
    bool            is_balanced;    // assume balanced equations? New Apr 06
    double          colin_factor;   // colinearity factor, passed to LSQFit.set(double,double)
    double          lm_factor;      // L-M factor, passed to LSQFit.set(double,double)
    int             max_iter;       // equal to Solver::max_num_iter_
  } SolverSettings;
  
  int             eval_mode_;         // 1 for single, 2 for double-deriv
  int             flag_mask_;         // flag mask applied during solve
  bool            do_save_funklets_;  // save funklets after solve?
  bool            do_last_update_;    // send up final update after solve?
  bool            do_flush_tables_;   // flush parmtables at end of solution
  int             max_num_iter_;      // max # of iterations
  double          conv_quota_;        // convergence quota
  SolverSettings  settings_;
  
  int             debug_lvl_;         // debug detail generated
  
  //##Documentation
  //## solvable parm group for this solver ("Parm" by default)
  HIID            parm_group_;
  
  // symdeps generated by the solver
  vector<HIID>    iter_symdeps_;
  int             iter_depmask_;
  
  
  // === other internal state
  
    //##ModelId=400E5355025A
  int             num_spids_;
  int             num_unknowns_;
  int             num_equations_;
  
  LoShape         cells_shape_;
  
  int             num_conv_;    // how many subsolvers have converged
  int             need_conv_;   // how many subsolvers need to converge
  
  int             cur_iter_;    // current iteration

  // # of child whose result is currently being processed
  int cur_child_;
  
  typedef VellSet::SpidType SpidType;
  
  // A DimVector is simply an int[Axis::MaxAxis] that is intialized with 0's.
  // This is a useful shorthand class, since we use a lot of these 
  // when figuring out tilings
  class DimVector 
  {
    private: 
      int dims[Axis::MaxAxis];
    public: 
      DimVector ()
      { clear(); }
    
      int operator [] (int i) const
      { return dims[i]; }
      
      int & operator [] (int i) 
      { return dims[i]; }
      
      bool operator < (const DimVector &other) const
      { 
        bool equal = true;
        for(int i=0; i<Axis::MaxAxis; i++)
          if( dims[i] > other.dims[i] )
            return false;
          else if( dims[i] < other.dims[i] )
            equal = false;
        return !equal;
      }
      
      bool operator == (const DimVector &other) const
      { 
        return !memcmp(dims,other.dims,sizeof(dims));
      }
      
      bool operator != (const DimVector &other) const
      { 
        return !( (*this) == other );
      }
      
      int operator = (int x)
      { 
        for(int i=0; i<Axis::MaxAxis; i++)
          dims[i] = x;
        return x;
      }
      
      HIID asHIID () const
      { 
        HIID id;
        id.resize(Axis::MaxAxis); 
        for( int i=0; i<Axis::MaxAxis; i++ )
          id[i] = dims[i];
        return id;
      }
        
      void clear ()
      { memset(dims,0,sizeof(dims)); }
  };
  
  // since we have many spids but generally only a handful of distinct tilings,
  // we maintain info for each unique tiling rather than each spid.
  // The Tiling class holds information for a tiling of an N-dimensional
  // Vells (whose dimensions are usually determined by the request Cells).
  // Since we always process a Vells element-by-element with the last dimension
  // iterating fastest, Tiling provides functions for keep track of which tile
  // we are in at any given point.
  class Tiling
  {
    public:
      DimVector        num_tiles;     // number of tiles per axis (0 if axis not defined)
      DimVector        tile_size;     // tile size per axis       (0 if axis not defined)
      DimVector        tile_stride;   // tile stride per axis (how many tiles to skip when going to next tile along this axis, 0 if not defined)
      int              total_tiles;   // total number of tiles
      
      // these data members change as we advance over a hypercube
      DimVector        dimcount;      // dimension counter, updated during equation filling
      int              cur_tile;      // current tile number, updated during equation filling
      bool             active;        // flag: tiling is active, updated during equation filling
      
      // once we have determined the solver tiling (which is the least common
      // multiple of all other tilings, taken along each axis, and hence
      // called the super-tiling), this vector is filled with the 
      // super-tile # corresponding to tile #N in this tiling
      std::vector<int> super_tile;
      
      Tiling ()
      : total_tiles(0)
      {};
      
      // creates a tiling for the given tile sizes and the given hypercube shape
      Tiling (const DimVector &tsz,const DimVector &shape)
      { init(tsz,shape); }
      
      // initializes, given tile sizes and hypercube shape
      void init (const DimVector &tsz,const DimVector &shape);
      
      void activate ()     // activates tiling
      {
        if( !active )
        {
          active = true;
          dimcount.clear();
          cur_tile = 0;
        }
      }
      
      void deactivate ()    // deactivates tiling
      { active = false; }
      
      // Advances tiling for a given hypercube advance. ndim tells how many
      // hypercube dimension indices have advanced. That is, index
      // number idim has been incremented, while indices idim+1 to N have
      // rolled over to 0, and indices 0 to idim-1 have not changed.
      // Updates dimcounts and cur_tile, and returns true if tile number 
      // has changed.
      bool advance (int idim);
      
      // creates a record describing the tiling
      DMI::Record::Ref asRecord () const;
  };

  // map of all tilings used for current set of spids, filled in during
  // spid discovery
  typedef std::map<DimVector,Tiling> TilingMap;
  TilingMap tilings_;
  
  // pointer into map, points to tiling of the solver
  Tiling * psolver_tiling_;
  
  // overall spid tiling map populated during discovery
  class SpidInfo // ha ha
  {
    public:
      int  nodeindex;                   // node associated with this spid
      int  nuk;                         // how many unknowns/subtiles per this spid (1 if not tiled)
      Tiling *ptiling;                  // which tiling it uses
      std::vector<int> ssuki;           // subsolver index of unknown per tile number
        // (for tile N, ssuki[N] tells which unknown corresponds to
        // this tile in the subsolver for tile N)
      
      // creates a record describing the spid
      DMI::Record::Ref asRecord () const;
  };
  
  typedef std::map<SpidType,SpidInfo> SpidMap;
  SpidMap spids_;
  
  // this is a subsolver structure for a solver tile
  // (corresponding to one block of a block-diagonal matrix)
  class Subsolver
  {
    public:
      casa::LSQaips   solver;
      int             nuk;     // number of unknowns in this solver
      int             neq;     // number of equations in this solver
      
      SolverSettings  settings;
      bool            use_debug;  // should the solver fill debug info?
      
      // this info is maintained during a solution
      casa::Vector<double>  solution; // current solution vector from solver
      // matrix of incremental solutions, allocated sirectly in state record
      LoMat_double    incr_solutions;
      
      // info for current solve step
      uint rank;
      double fit;
      double chi0;     // input chi^2
      double chi;      // chi^2 after solve loop
      bool solFlag;
      DMI::Record::Ref metrics;       // metric record
      DMI::Record::Ref debugrec;      // debug record -- only filled in debug mode
      
      // raised once solver has converged to a solution
      bool converged; 
      
      // constructor
      Subsolver ()
      : nuk(0),converged(false)
      {}

      // called prior to starting a solution.
      // inits the solver object and various internals.
      // uk0 is a global count of unknowns, which is incremented by this subsolver's count.
      // incr_sol is a global matrix of incremental solutions. The subsolver
      // uses a slice of it: [*,uk0:uk0+nuk-1]
      void initSolution (int &uk0,LoMat_double &incr_sol,
                         const SolverSettings &set,bool usedebug=false);
      
      // expecutes one solve step based on accumulated equations, 
      // returns true if converged.
      // if already converged, does nothing and returns true immediately
      bool solve (int step);
      
  };
  
  std::vector<Subsolver> subsolvers_;    // each subsolver has its own structure
  
  // In addition, we need a map from nodeindices to their associated unknowns.
  // ParmUkMap maps a parm to a SpidSet.
  // A SpidSet maps each spid to a num_subsolvers x 2 matrix.
  // For each subsolver #i, the range of unknowns correspodning to this spid
  // is given by the interval [M(i,0),M(i,1)).
  // (Since a spid subtile may be smaller than a subsolver tile, a spid
  // may have multiple unknowns in each subsolver).
  // Since map guarantees ordering by key, we can simply iterate over SpidSet
  // to fill updates for each parm in the right order, i.e. by increasing spid.
  typedef std::map<SpidType,LoMat_int> SpidSet;
  class ParmUkInfo
  {
    public:
      SpidSet spidset;
      int nuk;
      ParmUkInfo () 
      : nuk(0) {}
  };
  typedef std::map<int,ParmUkInfo> ParmUkMap;
  
  ParmUkMap parm_uks_;
  
  // various temporary arrays used when filling equations, we keep them here
  // as members for convenience, and to minimize reallocations
  std::vector<double> deriv_real_;
  std::vector<double> deriv_imag_;
  Vells::Strides      *strides_;
  

  // helper function -- returns number of subsolvers
  int numSubsolvers () const
  { return subsolvers_.size(); }
  
  // helper function for fillEquations() to fill a particular subsolver
  template<typename T>
  inline void fillEqVectors (Subsolver &ss,int npert,int uk_index[],
        const T &diff,const std::vector<Vells::ConstStridedIterator<T> > &deriv_iter,
        double weight);
      
  
  // mt-related methods and members
  bool mt_solve_;
  std::vector<Thread::ThrID> worker_threads_;
  Thread::Mutex worker_mutex_;
  
  // start/stop worker pool
  void startWorkerThreads ();
  void stopWorkerThreads ();

  // run a worker thread loop
  static void * runWorkerThread (void *solver);
  void * workerLoop ();
  
  
  // Processes subsolvers in a loop, until all complete, or an exception
  // occurs. 
  void processSolversLoop ();
  
  // Activates all worker threads to process subsolvers.
  // Process what we can in this thread, and returns when all jobs are 
  // complete.
  void activateSubsolverWorkers ();
  // activates a worker thread to flush parm tables
  void flushTablesInWorkerThread ();
  
  
  int wt_num_ss_;         // number of subsolvers taken by workers
  int wt_num_active_;     // number of active workers. A worker is finished
      // either with an exception, or when wt_num_ss_>=numSubsolvers(),
      // then it decrements this value. see processSolversLoop().
      // This value is also assigned to to wake up the worker threads.
  bool wt_flush_tables_;  // flag: if true, worker was woken to call ParmTableUtils::flushTables();
  // condition var to signal when a worker thread is completed
  Thread::Condition worker_cond_;
  
  // exceptions raised by workers are accumulated here
  DMI::ExceptionList wt_exceptions_; 

  // set to True to interrupt solving, reset at start of each solution
  bool interrupt_;
  
  //for writing debug output
  std::string debug_filename_;
  bool write_debug_;
  
  
  
};


} // namespace Meq

#endif
