# Provides GUI services to TDL applications when running under the browser.
# When running in batch mode, most of these map to no-ops

meqbrowser = None;

# message categories
Normal = 0;
Event  = 1;
Error  = 2;

message_category_names=dict(Normal="normal",Event="event",Error="error");

def log_message (message,category=Normal):
  """Logs a message with the browser, or prints to console"""; 
  if meqbrowser:
    meqbrowser.log_message(message,category=category);
  else:
    if category == Normal:
      print "TDL message: %s\n"%message;
    else:
      print "TDL %s message: %s"%(message_category_names.get(category,""),message);
      
def purr (dirname,watchdirs,show=True,pounce=True):
  """If browser is running, attaches Purr tool to the given directories."""
  if meqbrowser:
    meqbrowser.attach_purr(dirname,watchdirs,pounce=pounce,show=show);

