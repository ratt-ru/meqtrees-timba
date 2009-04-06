MEQPACKAGE(LSM OCTOPython OCTOPUSSY )
set(lsm_includes
)
INCLUDE_SETUP(LSM ${lsm_includes})

set(lsm_src 
            
    )

add_library(lsm ${lsm_src})
install(TARGETS lsm DESTINATION ${LIBRARY_INSTALL_DIR})
MEQPACKAGE_ADD_LIBRARIES(lsm)
