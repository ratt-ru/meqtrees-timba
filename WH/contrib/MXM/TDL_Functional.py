# Helper class to compose the the function string for functionals

from Timba.Meq import meq


class Functional:
    def __init__(self,function="",parlist=[],Npar=0):
        """create the function_string, function is a string with parameters p0,...,pN, parlist is list of parramters.
        This can be either another functional or a number initializing the parameter. For simplicity one should  specify the number of parameters
        in this functional (so WITHOUT counting the nr. of pars in other subfunctionals)"""

        if Npar<=0:
            print "Please Specify number of parameters, assuming",len(parlist);
            Npar=self._npar=len(parlist);
        self._function=function;
        self._start_par=0;
        self._npar=Npar;
        self._last_par=Npar;
        self._coeff=[];
            

        tmp_start_par=0;
        for par in range(Npar):
            this_par=0;
            if(len(parlist)>par):
                this_par=parlist[par];
            if isinstance(this_par,Functional):
                this_par.setStartPar(tmp_start_par);
                fstr="("+this_par.getFunction()+")";
                n=this_par.getNpar();
                if n>1:
                    self._shift(tmp_start_par+1,n-1);#shifts all later par with step n
                self._coeff[len(self._coeff):]=this_par.getCoeff();
                par_str = "p"+str(tmp_start_par);
                self._replace_str(par_str,fstr);
                tmp_start_par+=n;
            else:
                tmp_start_par+=1;
                self._coeff.append(this_par);



    
    def _shift(self,start,shift):
        for n in range(self._last_par-1,start-1,-1):
            old_par_str="p"+str(n);
            new_par_str="p"+str(n+shift);
            self._replace_str(old_par_str,new_par_str);
        self._last_par+=shift;

    def _reverse_shift(self,start,shift):
        for n in range(start,self._last_par):
            old_par_str="p"+str(n);
            new_par_str="p"+str(n-shift);
            self._replace_str(old_par_str,new_par_str);
        self._last_par-=shift;
    

    def _replace_str(self,old,new):
        #print "replacing",old,"with",new,"in",self._function;
        self._function = self._function.replace(old,new);
        #print "new string",self._function;

    def getFunction(self):
        return self._function;

    def getNpar(self):
        return self._npar;

    def getCoeff(self):
        return self._coeff;

    def setStartPar(self,start):
        #print "setting start_par",start,self._start_par;
        if start >  self._start_par:
            self._shift(self._start_par,start-self._start_par);
        if start< self._start_par:
            self._reverse_shift(self._start_par,self._start_par-start);
            

        self._start_par=start;


    def setCoeff(self,i,cf):
        if i<self._npar:
            self._coeff[i]=cf;


    def getFunklet(self):
        funklet=meq.polc(coeff=self._coeff,subclass=meq._funklet_type);
        funklet.function=self._function;
        return funklet;




def create_polc(shape=[1,1],coeff=[]):
    """helper function,creates functional for polc with shape shape,
    you can initialize any parameters by specifying coeff, coeff will be assumed 0 for all missing """
    func=""
    if len(shape)==1: 
        shape.append(1);
    if shape[0]==0:
        shape[0]=1;
    if shape[1]==0:
        shape[1]=1;
    nr_par=0;
    startp=0;
    for i in range(shape[1]):
        for j in range(shape[0]):
            nr_par=nr_par+1;
            if(len(coeff)<nr_par):
                coeff.append(0.);
            func=func+'p'+str(startp);
            for i2 in range(j):
                func = func + '*'+ "x0";
            for i1 in range(i):
                func = func + '*'+ "x1";
            func = func + "+"
            startp=startp+1;
    #remove last +
  
    fstr= func[0:len(func)-1];  
    return Functional(fstr,coeff,nr_par);

    
