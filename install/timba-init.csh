#!/bin/csh.
# timba-init.csh
# source this file into your .cshrc to have all Timba paths set up at login

if (! $?TIMBA_PATH) then
  setenv TIMBA_PATH $HOME/Timba
endif

if (! -d $TIMBA_PATH/install) then
  echo "Warning: cannot find Timba install under $TIMBA_PATH"
  echo "If Timba is installed elsewhere, please set your TIMBA_PATH variable appropriately."
else
  setenv DEFAULT_PATH $PATH
  setenv DEFAULT_LD_LIBRARY_PATH $LD_LIBRARY_PATH
  setenv DEFAULT_PYTHON_PATH $PYTHONPATH


alias _timba-setup "set arg1 = \\!^ ; setenv PATH ${DEFAULT_PATH}:$TIMBA_PATH/install/$arg1/bin ; setenv PYTHONPATH ${DEFAULT_PYTHON_PATH}:$TIMBA_PATH/install/$arg1/libexec/python ; setenv LD_LIBRARY_PATH ${DEFAULT_LD_LIBRARY_PATH}:$TIMBA_PATH/install/$arg1/lib ; echo "Using Timba install $TIMBA_PATH/install/$arg1""

_timba-setup current
endif
