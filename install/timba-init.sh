# timba-init.sh
# source this file into your .bashrc to have all Timba paths set up at login


if [ -z "$TIMBA_PATH" ]; then
  # under bash, we can figure out the name of our script, and extract the path
  if [ "$BASH_SOURCE" != "" ]; then
    if [ "${BASH_SOURCE[0]/Timba\//}" != "${BASH_SOURCE[0]}" ]; then
      export TIMBA_PATH="${BASH_SOURCE[0]/Timba\/*/Timba}"
      # if we end up with a relative path, make it absolute
      if [ "${TIMBA_PATH#/}" = "$TIMBA_PATH" ]; then
        export TIMBA_PATH=`pwd`/$TIMBA_PATH
      fi
    fi
  fi
  if [ -z "$TIMBA_PATH" ]; then
    export TIMBA_PATH=$HOME/Timba
  fi
  echo "Using \$TIMBA_PATH $TIMBA_PATH"
fi

if [ ! -d $TIMBA_PATH/install ]; then
  echo "Warning: cannot find Timba install under $TIMBA_PATH"
  echo "If Timba is installed elsewhere, please set your TIMBA_PATH variable appropriately."
else
  if [ "$PRE_TIMBA_PATH" == "" ]; then
    export PRE_TIMBA_PATH=$PATH
  fi
  if [ "$PRE_TIMBA_LD_LIBRARY_PATH" == "" ]; then
    export PRE_TIMBA_LD_LIBRARY_PATH=$LD_LIBRARY_PATH
  fi
  if [ "$PRE_TIMBA_PYTHONPATH" == "" ]; then
    export PRE_TIMBA_PYTHONPATH=$PYTHONPATH
  fi

  _timba-setup()
  {
    if [ ! -d $TIMBA_PATH/install/$1/bin ]; then
      echo "Timba build variant $1 not found" 
    else
      export PATH=$PRE_TIMBA_PATH:$TIMBA_PATH/install/$1/bin
      export PYTHONPATH=$PRE_TIMBA_PYTHONPATH:.:$TIMBA_PATH/install/$1/libexec/python
      export LD_LIBRARY_PATH=$PRE_TIMBA_LD_LIBRARY_PATH:$TIMBA_PATH/install/$1/lib
      echo "Using Timba install $TIMBA_PATH/install/$1"
    fi
  }

  _timba-setup current
fi
