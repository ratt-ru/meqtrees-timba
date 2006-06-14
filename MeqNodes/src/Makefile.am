SUBDIRS	= .
  
LOCALHDRS = 

LOCALSRCS = \
    Constant.cc Parm.cc Freq.cc Time.cc Grid.cc Selector.cc Composer.cc Paster.cc \
    Add.cc Subtract.cc Multiply.cc Divide.cc  Sin.cc Cos.cc Exp.cc Pow.cc \
    Sqr.cc Asin.cc Acos.cc Sqrt.cc Conj.cc ToComplex.cc Polar.cc UVW.cc \
    LMN.cc Log.cc Cosh.cc Sinh.cc Tan.cc Tanh.cc VisPhaseShift.cc Condeq.cc \
    Identity.cc Solver.cc Ceil.cc Floor.cc Atan.cc \
    Pow2.cc Pow3.cc Pow4.cc Pow5.cc Pow6.cc Pow7.cc Pow8.cc \
    Abs.cc Fabs.cc Norm.cc Arg.cc Real.cc Imag.cc \
    MergeFlags.cc ReqSeq.cc ReqMux.cc \
    ReductionFunction.cc Min.cc Max.cc Mean.cc \
    Sum.cc Product.cc NElements.cc Transpose.cc \
    Stripper.cc DataCollect.cc DataConcat.cc HistoryCollect.cc AzEl.cc \
    BlitzRandom.cc NoiseNode.cc RandomNoise.cc GaussNoise.cc ZeroFlagger.cc StdDev.cc \
    WSum.cc WMean.cc Negate.cc Invert.cc \
    MatrixMultiply.cc MatrixInvert22.cc UVBrick.cc UVInterpol.cc \
    Stokes.cc PatchComposer.cc FFTBrick.cc UVInterpolWave.cc \
    GridPoints.cc Resampler.cc ModRes.cc \
    CompiledFunklet.cc ParmTable.cc ParmDBInterface.cc \
    FITSImage.cc Compounder.cc FITSWriter.cc FITSReader.cc Functional.cc
# Functional.cc


DOCHDRS		= $(LOCALHDRS) \
            $(addsuffix .h,$(basename $(LOCALSRCS))) 

lib_LTLIBRARIES 	= libmeqnodes.la

libmeqnodes_la_SOURCES 	= $(DOCHDRS) $(LOCALSRCS) \
  AID-MeqNodes-Registry.cc

check_PROGRAMS = 

# place scripts into libexec/glish/meq
glishdir = $(libexecdir)/glish/meq
dist_glish_SCRIPTS = meptable.g

include $(top_srcdir)/Makefile.common
include $(lofar_sharedir)/Makefile.aids


# AM_CPPFLAGS = -DMAKE_LOFAR_SYMBOLS_GLOBAL 

# use these flags for old (pre 20/04/2006) aips++ versions
AM_CPPFLAGS = -DMAKE_LOFAR_SYMBOLS_GLOBAL -DUSE_OLD_LSQFIT
