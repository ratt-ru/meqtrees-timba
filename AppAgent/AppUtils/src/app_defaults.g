pragma include once

default_verbosity := 1;
max_debug := 1;

if( has_field(environ,'verbose') )
  default_verbosity := as_integer(environ.verbose);
if( has_field(environ,'debug') )
  max_debug := as_integer(environ.debug);

if( !is_record(default_debuglevels) )
  default_debuglevels := [=];

for( f in 1:len(default_debuglevels) )
  default_debuglevels[f] := min(max_debug,default_debuglevels[f]);

print '======= Default verbosity level: ',default_verbosity;
print '=======         Max debug level: ',max_debug;

# find debug levels of form -dContext=level in the environment strings
for( f0 in field_names(environ) )
{
  f := f0;
  if( f =~ s/^-d(.*)$/$1/ )
  {
    lev := default_debuglevels[f] := as_integer(environ[f0]);
    print '=======  Overriding debug level: ',f,'=',lev;
  }
}
# find debug levels of form -dContext=level in the command-line args
# also scan for other options
for( arg in argv )
{
  if( arg == '-nostart' )
    use_nostart := T;
  else if( arg == '-suspend' )
    use_suspend := T;
  else if( arg == '-valgrind' )
    use_valgrind := T;
  else if( arg == '-gui' )
    use_gui := T;
  else if( arg =~ s/^-d(.*)=(.*)$/$1$$$2/ )
  {
    default_debuglevels[arg[1]] := lev := as_integer(arg[2]);
    print '=======  Overriding debug level: ',arg[1],'=',lev;
  }
}

  
