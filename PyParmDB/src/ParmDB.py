from Timba.pyparmdb import *
from Timba.dmi import *
import os

class Parmdb:
    def __init__(self,name="test",type="aips"):
        self.reopen(name,type);

        
    def getParmNames(self,pattern="*"):
        if not self._db:
            print "no db opened, try reopen"
            return;
        names=getNames(self._db,pattern);
        #print "names",names;
        return names;

    def getRange(self,pattern="*"):
        if not self._db:
            print "no db opened, try reopen"
            return;
        domain=getRange(self._db,pattern);
        #print "names",names;
        return domain;

    def getFunklets(self,name,domain="all",parentId=-1):
        if not self._db:
            print "no db opened, try reopen"
            return;
        if domain == "all" or not isinstance(domain,dmi_type('MeqDomain',record)):
            funklets = getAllValues(self._db,name,parentId);
        else:
            funklets = getValues(self._db,name,domain,parentId);
        #print "funklets",funklets;
        return funklets;
        
    def reopen(self,name="test",type="aips"):
        self._name=name;
        if os.path.isdir(name):
            
            self._db=openParmDB(name,type,False);
        else:
            print "path", name,"not existing. New parmdb will be created.";
            self._db=openParmDB(name,type,True);
        if not self._db:
            print "Opening db",name,"FAILED";
