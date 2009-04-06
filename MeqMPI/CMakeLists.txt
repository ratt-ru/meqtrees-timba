MEQPACKAGE(MeqMPI MEQ)
set(meqMpi_includes
    src/AID-MeqMPI.h
    src/MeqMPI.h
    src/MPIProxy.h
    src/TID-MeqMPI.h
    src/TypeIter-MeqMPI.h
)
INCLUDE_SETUP(MeqMPI ${meqMpi_includes})
set(meqMpi_src
    src/AID-MeqMPI-Registry.cc
    #src/Dummy.cc
    src/MeqMPI.cc
    src/MeqMPI_commands.cc
    #src/MPIProxy.cc
    )
add_library(meqmpi ${meqMpi_src})
install(TARGETS meqmpi DESTINATION ${LIBRARY_INSTALL_DIR})
MEQPACKAGE_ADD_LIBRARIES(meqmpi)
