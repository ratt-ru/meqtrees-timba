//# Resampler.h: resamples result resolutions
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

#ifndef MEQNODES_RESAMPLER_H
#define MEQNODES_RESAMPLER_H
    
#include <MEQ/Node.h>
#include <MEQ/AID-Meq.h>

#include <MeqNodes/TID-MeqNodes.h>
#pragma aidgroup MeqNodes
#pragma types #Meq::Resampler 
#pragma aid Integrate Flag Density Mode Common Axes

// The comments below are used to automatically generate a default
// init-record for the class 

//defrec begin MeqResampler
//  Resamples the Vells in its child's Result to the Cells of the parent's
//  Request. Current version ignores cell centers, sizes, domains, etc.,
//  and goes for a simple integrate/expand by an integer factor.
//field: flag_mask -1
//  Flag mask applied to child's result. -1 for all flags, 0 to ignore 
//  flags. Flagged values are ignored during integration.
//field: flag_bit 0
//  Flag bit(s) used to indicate flagged integrated results. If 0, then 
//  flag_mask&input_flags is used.
//field: flag_density 0.5
//  Critical ratio of flagged/total pixels for integration. If this ratio
//  is exceeded, the integrated pixel is flagged.
//field: mode
//  mode 1 (interpolate): 
//  mode 2 (integrate): 
//field: common_axes []
//  the axes in this vector will be copied from the result to the request,
//  in other words preserve this axes regardless of the request
//defrec end

namespace Meq {    

class Resampler : public Node
{
public:
  Resampler();

  virtual ~Resampler();

  virtual TypeId objectType() const
  { return TpMeqResampler; }
  
  

protected:
  virtual void setStateImpl (DMI::Record::Ref &rec,bool initializing);
    
  virtual int getResult (Result::Ref &resref, 
                         const std::vector<Result::Ref> &childres,
                         const Request &req,bool newreq);
  
private:
  int flag_mask;
	int mode;
  int flag_bit;
  float flag_density;

	std::vector<HIID> keep_axes_;
};


// put the code here
class ResampleMachine 
{

protected:
/////////////////////////////////////
//auxiliary classes needed by the resample machine
// edges
class Bedge {
public:
  int id; //incoming node number
  double w; //weight
  Bedge(int idd=0,double ww=0):id(idd),w(ww) {}
  friend std::ostream &operator<<(std::ostream &o,const Bedge &f) {
		o<<"{"<<f.id<<", "<<f.w<<"}";
		return o;
	}
};
// nodes
class Bnode {
public:
  Bnode(int count=0) {
   elist_.resize(count);
  }
  ~Bnode() {
    elist_.clear();
   }
  void append(Bedge &T) {
   elist_.push_back(const_cast<Bedge &>(T));
  }
  void print(void) {
   std::cout<<"Edges "<<elist_.size()<<std::endl;
   std::copy(elist_.begin(),elist_.end(),std::ostream_iterator<Bedge>(std::cout," "));
   std::cout<<std::endl;
  }
  std::list<Bedge>::iterator begin(void) {
   return elist_.begin();
  }
  std::list<Bedge>::iterator end(void) {
   return elist_.end();
  }

private:
  std::list<Bedge> elist_;
  int id_;  //??
};

class Bgraph {
  std::vector<Bnode> onodes_; //we only store the output node list 
  int count_;
public: 
  Bgraph(int count=0) { 
    onodes_.resize(count);
    count_=count;
  }
  ~Bgraph() {
     onodes_.clear();
     count_=0;
   }  
   Bnode &get(int idx) {
    return onodes_[idx];
   }

   void print(void) {
    for (unsigned int i=0; i<onodes_.size(); i++) {
      std::cout<<"node "<<i<<std::endl; 
      Bnode &b=get(i);
      b.print();
    }
   }
  void resize(int count) { 
    onodes_.resize(count);
    count_=count;
  }
  int size(void) { 
    return onodes_.size();
  }
     
};
/////////////////////////////////////
protected:
	 int flag_mask_;
	 int flag_bit_;
	 float flag_density_;
	 bool identical_;


    inline int bin_search(blitz::Array<double,1> xarr,double x,int i_start,int i_end);
    inline int bin_search(std::vector<double> xarr,double x,int i_start,int i_end);


public:
   ResampleMachine(int parms) {
	  flag_mask_=-1;
    flag_bit_=0;
    flag_density_=0.5;
    identical_=false;		
	 }
	 virtual ~ResampleMachine() {}

	 bool isIdentical() const
	 { return identical_; }

	 void setFlagPolicy(int flag_mask, int flag_bit, float flag_density)
	 { flag_mask_= flag_mask; flag_bit_=flag_bit; flag_density_=flag_density; }

	 virtual int apply(const VellSet &in, VellSet &out) {
				return -1;
	 }

	 virtual int print() {
				return -1;
	 }
   virtual void setup( const Cells &in, const Cells &out) {}

};




/////////////////////////////////
class Integrator: public ResampleMachine {
				public:
					Integrator(int parms):ResampleMachine(parms) {
					}
					~Integrator() {}
					int apply( const VellSet &in, VellSet &out ); 
					int print() {
						cout<<"Integrator print"<<endl;
						return 0;
					}
					
       void setup(const Cells &in, const Cells &out);
	 //Bipartite graphs for each axis
	 std::vector<Bgraph> bx_;

	 int nx_,ny_; // size of the resampled (new) cells
   int nx0_,ny0_; // input cell sizes
	 blitz::Array<double,2> cell_weight_;

  template<class T> int  
   do_resample(
				blitz::Array<T,2> A,  blitz::Array<T,2> B ); 
  template<class T> int  
   do_resample( 
				blitz::Array<T,2> A,  blitz::Array<T,2> B,  
			  VellsFlagType *Fp, bool has_flags, blitz::Array<VellsFlagType,2> Aflag);


  void insert(int incell,int cell1, int cell2, int axis,
	blitz::Array<double,1> incellsize,blitz::Array<double,1> outcellsize,
	blitz::Array<double,1> incenter,blitz::Array<double,1> outcenter);


};

class Interpolator: public ResampleMachine {
				public:
					Interpolator(int parms):ResampleMachine(parms) {

					}
					~Interpolator() {}
					int apply( const VellSet &in, VellSet &out );

					int print() {
						cout<<"Interpolator print"<<endl;
						return 0;
					}

       void setup(const Cells &in, const Cells &out);
	 //in-out cells as arrays
  std::vector<blitz::Array<double,1> > incells_; 
  std::vector<blitz::Array<int,1> > xindex_; 
  std::vector<blitz::Array<double,1> > outcells_; 

     		//cubic hermite interpolation
        template<class T> void pchip_int(blitz::Array<double,1> xin, blitz::Array<T,1> yin, int n, blitz::Array<double,1> xout,  blitz::Array<T,1> yout, int m, blitz::Array<int,1> xindex);
				//special for complex
        void pchip_int(blitz::Array<double,1> xin, blitz::Array<dcomplex,1> yin, int n, blitz::Array<double,1> xout,  blitz::Array<dcomplex,1> yout, int m, blitz::Array<int,1> xindex);

        Vells * really_apply(const Vells &in, std::vector<int> indim, std::vector<int> outdim, std::vector<int> totdim);

};





//////////////////////////////////////////
class ResamplerFactory {
		public:
		  typedef enum {
					INTERPOLATOR =0x00001,
					INTEGRATOR=0x00002,
			} MachineType;

			ResampleMachine *create(MachineType mode, int parms) {
         if (mode==ResamplerFactory::INTEGRATOR) {
							return new Integrator(parms);
				 } else {
							return new Interpolator(parms);
				 }
			}

};




} // namespace Meq

#endif
