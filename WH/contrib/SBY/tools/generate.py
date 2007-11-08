#!/usr/bin/python
#
# Generate all available HTML documentation in Timba python module.
# Sarod Yatawatta - with a little help from my friends
#
import os, sys, pydoc, string

def import_libs(ldir):
    """ Imports the libs, returns a list of the libraries. 
    Pass in dir to scan """
    #print ldir
    dir_list=[]
    dir_list.append(ldir)
    library_list = ['Timba'] 
   
    while  len(dir_list)>0:
     dir=dir_list.pop(0) 
     if os.path.isdir(os.path.abspath(dir)):
      # must be a directory
      for f in os.listdir(os.path.abspath(dir)):       
        module_name, ext = os.path.splitext(f) # Handles no-extension files, etc.
        print module_name
        print ext
        if ext == '.pyc' or ext=='.py': # Important, ignore .pyc/other files.
            try:
             print 'importing module: Timba.%s' % (module_name)
             sl=string.split(dir,'/')
             while sl[0]!='Timba':
              sl.pop(0)
             module_name_prefix=""
             while len(sl)>0:
              module_name_prefix=module_name_prefix+sl.pop(0)+"."
             library_list.append(module_name_prefix+module_name)
            except:
             pass
        elif ext=='' and module_name != 'CVS': 
           print 'Directory %s' % module_name
           dir_list.append(dir+'/'+module_name)
           try:
            print 'importing module: Timba.%s' % (module_name)
            sl=string.split(dir,'/')
            while sl[0]!='Timba':
              sl.pop(0)
            module_name_prefix=""
            while len(sl)>0:
              module_name_prefix=module_name_prefix+sl.pop(0)+"."
            library_list.append(module_name_prefix+module_name)

           except:
            pass
 
     #print dir_list
    return library_list

###############################################################################

def filter_builtins(module):
    """ Filter out the builtin functions, methods from module and duplicates """

    # Default builtin list    
    built_in_list = ['__builtins__', '__doc__', '__file__', '__name__']
    
    # Append anything we "know" is "special"
    # Allows your libraries to have methods you will not try to exec.
    built_in_list.append('special_remove')

    # get the list of methods/functions from the module
    module_methods = dir(module) # Dir allows us to get back ALL methods on the module.

    for b in built_in_list:
        if b in module_methods:
            module_methods.remove(b)

    #print module_methods
    return module_methods

###############################################################################


def main():
    #dir='/home/sarod/Timba/install/symlinked/libexec/python/Timba'
    dir='/net/cedar/home/sarod/Timba/install/symlinked/libexec/python/Timba'
    prfx='Timba.install.symlinked.libexec.python.'
    lib_list = import_libs(dir)
    # generate pydoc here
    print lib_list
    for l in lib_list:
      f=l.split(prfx)
      if len(f)>1:
        ll=f[1]
      else:
        ll=f[0]
      try:
       module = __import__(ll)
       pydoc.writedoc(ll)
      except:
       pass
   
    dir='/net/cedar/home/sarod/Timba/install/symlinked/libexec/python/Meow'
    lib_list = import_libs(dir)
    # generate pydoc here
    print lib_list
    for l in lib_list:
      f=l.split(prfx)
      if len(f)>1:
        ll=f[1]
      else:
        ll=f[0]
      try:
       module = __import__(ll)
       pydoc.writedoc(ll)
      except:
       pass
        
if __name__ == "__main__":
     main()
