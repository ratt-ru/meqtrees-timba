SUBDIRS	= .

LOCALHDRS = MeqVocabulary.h RequestId.h Meq.h VellsSlicer.h VellsSlicerWithFlags.h NodeFace.h

LOCALSRCS = \
  Axis.cc Domain.cc   Cells.cc Request.cc RequestId.cc \
  Vells.cc VellSet.cc VellsSlicer.cc VellsSlicerWithFlags.cc Result.cc \
  Funklet.cc Polc.cc ComposedPolc.cc PolcLog.cc ParmTable.cc FastParmTable.cc \
  Node.cc NodeNursery.cc Function.cc TensorFunction.cc \
  Rider.cc SymdepMap.cc Forest.cc MTPool.cc Spline.cc

## removed for now, as it needs to be re-worked for the new Vells
## structure
# ResampleMachine.cc 

DOCHDRS		= $(LOCALHDRS) \
            $(addsuffix .h,$(basename $(LOCALSRCS))) 

lib_LTLIBRARIES 	= libmeq.la

libmeq_la_SOURCES 	= $(DOCHDRS) $(LOCALSRCS) \
  Node_commands.cc Node_init.cc AID-Meq-Registry.cc
  
libmeq_la_LIBADD = -lblitz

check_PROGRAMS = 

# --- end generate defrec maps

include $(top_srcdir)/Makefile.common
include $(lofar_sharedir)/Makefile.aids

AM_CPPFLAGS = -DMAKE_LOFAR_SYMBOLS_GLOBAL
