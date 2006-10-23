from Timba.dmi import *

def PlotPage (name,*rows):
  bklist = [];
  
  if not isinstance(name,str):
    # must be just another row...
    rows = [name] + list(rows);
  
  for irow,onerow in enumerate(rows):
    for icol,node in enumerate(onerow):
      bklist.append(record(
        viewer="Result Plotter",
        udi="/node/"+node,
        pos=(irow,icol)));
        
  if not isinstance(name,str):
    return bklist;
  else:
    return record(name=name,page=bklist);
