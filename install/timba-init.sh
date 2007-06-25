# timba-init.sh
# source this file into your .bashrc to have all Timba paths set up at login


if [ "$TIMBA_PATH" == "" ]; then
  export TIMBA_PATH=$HOME/Timba
fi

if [ ! -d $TIMBA_PATH/install ]; then
  echo "Warning: cannot find Timba install under $TIMBA_PATH"
  echo "If Timba is installed elsewhere, please set your TIMBA_PATH variable appropriately."
else
  export DEFAULT_PATH=$PATH
  export DEFAULT_LD_LIBRARY_PATH=$LD_LIBRARY_PATH
  export DEFAULT_PYTHONPATH=$PYTHONPATH

  _timba-setup()
  {
    export PATH=$DEFAULT_PATH:$TIMBA_PATH/install/$1/bin
    export PYTHONPATH=$DEFAULT_PYTHONPATH:.:$TIMBA_PATH/install/$1/libexec/python
    export LD_LIBRARY_PATH=$DEFAULT_LD_LIBRARY_PATH:$TIMBA_PATH/install/$1/lib
    echo "Using Timba install $TIMBA_PATH/install/$1"
  }

  _timba-setup current
fi
