SUBDIRS	= .
  
LOCALHDRS = 

LOCALSRCS = \
    Constant.cc Parm.cc Freq.cc Time.cc Grid.cc Selector.cc Composer.cc Paster.cc \
    Add.cc Subtract.cc Multiply.cc Divide.cc FMod.cc Sin.cc Cos.cc Exp.cc Pow.cc \
    Sqr.cc Asin.cc Acos.cc Sqrt.cc Conj.cc ToComplex.cc Polar.cc UVW.cc \
    LMN.cc Log.cc Cosh.cc Sinh.cc Tan.cc Tanh.cc VisPhaseShift.cc Condeq.cc \
    Identity.cc Solver.cc Ceil.cc Floor.cc Atan.cc \
    Pow2.cc Pow3.cc Pow4.cc Pow5.cc Pow6.cc Pow7.cc Pow8.cc \
    Abs.cc Fabs.cc Norm.cc Arg.cc Real.cc Imag.cc \
    MergeFlags.cc ReqSeq.cc ReqMux.cc LMRaDec.cc ParAngle.cc\
    ReductionFunction.cc Min.cc Max.cc Mean.cc \
    Sum.cc Product.cc NElements.cc Transpose.cc \
    Stripper.cc DataCollect.cc DataConcat.cc HistoryCollect.cc AzEl.cc LongLat.cc\
    BlitzRandom.cc NoiseNode.cc RandomNoise.cc GaussNoise.cc ZeroFlagger.cc StdDev.cc Rms.cc \
    WSum.cc WMean.cc Negate.cc Invert.cc \
    MatrixMultiply.cc MatrixInvert22.cc UVBrick.cc UVInterpol.cc \
    Stokes.cc PatchComposer.cc FFTBrick.cc UVInterpolWave.cc \
    GridPoints.cc Resampler.cc ModRes.cc \
    CasaParmTable.cc ParmTableUtils.cc ParmDBInterface.cc \
    FITSImage.cc Compounder.cc FITSWriter.cc FITSReader.cc \
    FITSSpigot.cc FITSDataMux.cc FITSUtils.cc \
    PrivateFunction.cc MaxLocation.cc MinLocation.cc\
    RADec.cc ObjectRADec.cc CoordTransform.cc LST.cc\
    StationBeam.cc ShapeletVisTf.cc Bessel.cc VisPhaseShiftArg.cc TFSmearFactor.cc



DOCHDRS		= $(LOCALHDRS) \
            $(addsuffix .h,$(basename $(LOCALSRCS))) 

lib_LTLIBRARIES 	= libmeqnodes.la

libmeqnodes_la_SOURCES 	= $(DOCHDRS) $(LOCALSRCS) \
  AID-MeqNodes-Registry.cc

check_PROGRAMS = 

include $(top_srcdir)/Makefile.common
include $(lofar_sharedir)/Makefile.aids


AM_CPPFLAGS = -DMAKE_LOFAR_SYMBOLS_GLOBAL

## for older (pre-July 06) versions of aips++, Solver node may
## report compilation errors. Use the macro below to work around,
## or run lofarconf with --with-old-lsqfit.
# AM_CPPFLAGS = -DUSE_OLD_LSQFIT
