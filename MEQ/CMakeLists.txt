MEQPACKAGE(MEQ OCTOPython OCTOPUSSY )
set(meq_includes
            src/AID-Meq.h
            src/Axis.h
            src/Cells.h
            src/ComposedPolc.h
            src/Domain.h
            src/FastParmTable.h
            src/Forest.h
            src/Function.h
            src/Funklet.h
            src/Meq.h
            src/MeqVocabulary.h
            src/MTPool.h
            src/NodeFace.h
            src/Node.h
            src/NodeNursery.h
            src/ParmTable.h
            src/Polc.h
            src/PolcLog.h
            src/Request.h
            src/RequestId.h
            src/ResampleMachine.h
            src/Result.h
            src/Rider.h
            src/Spline.h
            src/SymdepMap.h
            src/TensorFunction.h
            src/TID-Meq.h
            src/TypeIter-Meq.h
            src/VellSet.h
            src/Vells.h
            src/VellsSlicer.h
            src/VellsSlicerWithFlags.h
)
INCLUDE_SETUP(MEQ ${meq_includes})

set(meq_src 
            src/AID-Meq-Registry.cc 
            src/Axis.cc 
            src/Cells.cc 
            src/ComposedPolc.cc 
            src/Domain.cc
            src/FastParmTable.cc
            src/Forest.cc
            src/Function.cc 
            src/Funklet.cc 
            src/MTPool.cc 
            src/Node.cc 
            src/Node_commands.cc 
            src/Node_init.cc 
            src/NodeNursery.cc 
            src/ParmTable.cc 
            src/Polc.cc 
            src/PolcLog.cc 
            src/Request.cc 
            src/RequestId.cc 
            #src/ResampleMachine.cc 
            src/Result.cc 
            src/Rider.cc 
            src/Spline.cc 
            src/SymdepMap.cc 
            src/TensorFunction.cc 
            src/Vells.cc 
            src/VellSet.cc 
            src/VellsSlicer.cc 
            src/VellsSlicerWithFlags.cc )

add_library(meq ${meq_src})
install(TARGETS meq DESTINATION ${LIBRARY_INSTALL_DIR})
MEQPACKAGE_ADD_LIBRARIES(meq)
