include "octopussy.g"

# oct := octopussy(server="./test/glish_reflector -dGlishClientWP=4 -dReflectorWP=4",options=options,suspend=F);
oct := octopussy(server="./test/glish_reflector -d0",options=options,suspend=F);

if( is_fail(oct) || !oct.connected() )
  fail 'unable to connect to server';

# start the system
oct.start();

run := T;
count := 1;
rec := [ A="a string", B=0, C=array(1.0,10,10,10),D=[] ];

readline()

while( run && count >=0 )
{
  oct.publish("Reflect.A",rec);
  
  print "waiting...";
  msg := oct.receive(value);
  if( is_fail(msg) )
  {
    print "Receive failed: ",msg;
    run := F;
  }
  else
  {
    print "Received: ",msg;
    print "value: ",value;
    print "id:", msg::id;
    print "to:", msg::to;
    print "from:", msg::from;
    print "priority", msg::priority;
    print "state", msg::state;
  }
  
  count := count-1;
}

send := function(rec)
{
  oct.publish("Reflect.A",rec);
  print "waiting...";
  msg := oct.receive();
  if( is_fail(msg) )
  {
    print "Receive failed: ",msg;
    run := F;
  }
  else
  {
    print "id:", msg::id;
    print "to:", msg::to;
    print "from:", msg::from;
    print "priority", msg::priority;
    print "state", msg::state;
  }
  return msg;
}
