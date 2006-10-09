from Timba.dmi import *

def PlotPage (*rows):
  bklist = [];
  
  for irow,onerow in enumerate(rows):
    for icol,node in enumerate(onerow):
      bklist.append(record(
        viewer="Result Plotter",
        udi="/node/"+node,
        pos=(irow,icol)));
        
  return bklist;
