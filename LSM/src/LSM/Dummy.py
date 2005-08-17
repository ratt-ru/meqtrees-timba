from qt import *
from LSM_GUI import *

######################################################
# Helper classes and methods for the GUI
#Singleton Class to make sure there is only one 
# instance of QApplication class
class Singleton:
  __single=None
  app=None # both these are class attributes, not instance attributes
  def __init__(self,args):
   if Singleton.__single:
     raise Singleton.__single
   Singleton.__single=self
   Singleton.app=QApplication(args)

def Handle(args,x=Singleton):
 try:
  single=x(args)
 except Singleton,s:
  single=s
 return single.app

class Dummy:
    def __init__(self,lsm_object,args):
     self.lsm=lsm_object
     self.myargs=args
     self.app=None
     self.win=None
    def display(self,**kw):
     if kw.has_key('app') and (kw['app']=='create'):
       self.app=Handle(self.myargs)
     else:
       self.app=qApp

     self.win=LSMWindow(self.lsm) 
     self.win.show()
     self.app.connect(self.app,SIGNAL("lastWindowClosed()"),
        self.app, SLOT("quit()"))
     self.app.exec_loop()


#######################################################
