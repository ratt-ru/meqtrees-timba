INCLUDE_DIRECTORIES(${BLITZ_INCLUDE_DIRECTORIES})
MEQPACKAGE(VisCube DMI TimBase)

set(viscube_includes
    src/AID-VisCube.h
    src/ColumnarTableTile.h
    src/TableFormat.h
    src/TID-VisCube.h
    src/TypeIter-VisCube.h
    #src/VCube.h
    #src/VCubeSet.h
    src/VisCommon.h
    src/VisVocabulary.h
    src/VTile.h
)
INCLUDE_SETUP(VisCube ${viscube_includes})

set(viscube_src
    src/AID-VisCube-Registry.cc
    src/ColumnarTableTile.cc
    src/TableFormat.cc
    #src/VCube.cc
    #src/VCubeSet.cc
    src/VisCommon.cc
    src/VTile.cc
    )
add_library(viscube ${viscube_src})
install(TARGETS viscube DESTINATION ${LIBRARY_INSTALL_DIR})
MEQPACKAGE_ADD_LIBRARIES(viscube ${BLITZ_LIBRARIES})
