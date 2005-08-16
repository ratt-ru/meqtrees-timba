SUBDIRS	= .
  
LOCALHDRS = 

LOCALSRCS = \
    Constant.cc Parm.cc Freq.cc Time.cc Selector.cc Composer.cc Paster.cc \
    Add.cc Subtract.cc Multiply.cc Divide.cc  Sin.cc Cos.cc Exp.cc Pow.cc \
    Sqr.cc Asin.cc Acos.cc Sqrt.cc Conj.cc ToComplex.cc Polar.cc UVW.cc \
    LMN.cc Log.cc Cosh.cc Sinh.cc Tan.cc Tanh.cc VisPhaseShift.cc Condeq.cc \
    Solver.cc Ceil.cc Floor.cc Atan.cc \
    Pow2.cc Pow3.cc Pow4.cc Pow5.cc Pow6.cc Pow7.cc Pow8.cc \
    Abs.cc Fabs.cc Norm.cc Arg.cc Real.cc Imag.cc MergeFlags.cc ReqSeq.cc  \
    ReductionFunction.cc Min.cc Max.cc Mean.cc \
    Sum.cc Product.cc NElements.cc Transpose.cc \
    Stripper.cc DataCollect.cc DataConcat.cc AzEl.cc \
    BlitzRandom.cc NoiseNode.cc RandomNoise.cc GaussNoise.cc ZeroFlagger.cc StdDev.cc \
    ParmTable.cc WSum.cc WMean.cc Negate.cc Invert.cc \
    MatrixMultiply.cc MatrixInvert22.cc UVBrick.cc UVInterpol.cc \
    Stokes.cc PatchComposer.cc FFTBrick.cc

## commented out for now:    
## ModRes.cc Resampler.cc ZeroFlagger.cc 
## Atan2.cc Nelements.cc Posdiff.cc Sum.cc Product.cc

DOCHDRS		= $(LOCALHDRS) \
            $(addsuffix .h,$(basename $(LOCALSRCS))) 

lib_LTLIBRARIES 	= libmeqnodes.la

libmeqnodes_la_SOURCES 	= $(DOCHDRS) $(LOCALSRCS) \
  AID-MeqNodes-Registry.cc

check_PROGRAMS = 

# this defines the name of the local defrec script
# DEFREC_MAP = $(srcdir)/defrecs_$(PACKAGE).g

# this rule shouldn't require any changes
MAKEDEFREC = $(lofar_sharedir)/../Timba/MEQ/src/makedefrecs.pl
$(DEFREC_MAP): $(DOCHDRS) $(MAKEDEFREC)
	$(MAKEDEFREC) $@ $(addprefix $(srcdir)/,$(DOCHDRS))
# ---------
  
# place scripts into libexec/glish/meq
glishdir = $(libexecdir)/glish/meq
dist_glish_SCRIPTS = $(DEFREC_MAP) meptable.g

defrecs: 
# $(DEFREC_MAP)

all install: defrecs

.PHONY: defrecs

# --- end generate defrec maps

include $(lofar_sharedir)/Makefile.common
include $(lofar_sharedir)/Makefile.aids

AM_CPPFLAGS = -DMAKE_LOFAR_SYMBOLS_GLOBAL
