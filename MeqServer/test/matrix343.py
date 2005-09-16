from Timba.TDL import *
from Timba.Meq import meq
from numarray import *

class PointSource:
    name = ''
    ra   = 0.0
    dec  = 0.0
    IQUV      = zeros(4)*0.0
    IQUVorder = zeros(4)*0.0
    table  = ''

    def __init__(self, name='', ra=0.0, dec=0.0,
                 I=0.0, Q=0.0, U=0.0, V=0.0,
                 Iorder=0, Qorder=0, Uorder=0, Vorder=0,
                 table=''):
        self.name   = name
        self.ra     = ra
        self.dec    = dec
        self.IQUV   = array([I,Q,U,V])
        self.IQUVorder = array([Iorder,Qorder,Uorder,Vorder])
        self.table  = table
        pass
    pass




def forest_global_constants(ns, num_ant):
    ns.ra0   = Meq.Constant(0.0)
    ns.dec0  = Meq.Constant(0.0)
    ns.radec0= Meq.Composer(ns.ra0, ns.dec0)
    
    ns.x0   = Meq.Constant(0.0)
    ns.y0   = Meq.Constant(0.0)
    ns.z0   = Meq.Constant(0.0)

    for i in range(num_ant):
        station= str(i+1)
        
        ns['x.'+station] = Meq.Constant(0.0)
        ns['y.'+station] = Meq.Constant(0.0)
        ns['z.'+station] = Meq.Constant(0.0)

        ns['xyz.'+str(station)]=Meq.Composer(ns['x.'+station],
                                             ns['y.'+station],
                                             ns['z.'+station])
    pass



def create_initial_source_model(tablename=''):
    source_model = []
    src_3C343_1 = PointSource(name='3C343_1',
                              I=1.0, Q=0.0, U=0.0, V=0.0,
                              Iorder=1, Qorder=1,
                              ra=4.356645791155902,dec=1.092208429052697,
                              table=tablename)
    src_3C343 = PointSource(name='3C343',
                            I=1.0, Q=0.0, U=0.0, V=0.0,
                            Iorder=3, Qorder=3,
                            ra=4.3396003966265599,dec=1.0953677174056471,
                            table=tablename)
    source_model.append(src_3C343_1)
    source_model.append(src_3C343)
    return source_model





def forest_source_subtrees(ns, source):
    IQUVpolcs =[None]*4

    STOKES=["I","Q","U","V"]
    
    for (i,stokes) in enumerate(STOKES):
        if(source.IQUV[i] != None):
            IQUVpolcs[i] = meq.polc(zeros(source.IQUVorder[i]+1)*0.0)
            IQUVpolcs[i].coeff[0] = source.IQUV[i]
            pass
        ns.stokes(stokes, source.name) << Meq.Parm(IQUVpolcs[i],
                                                  table=source.table)
        pass    

    ns.xx(source.name) << (ns.stokes("I",source.name)+ns.stokes("Q",source.name))*0.5
    ns.yx(source.name) << Meq.ToComplex(ns.stokes("U",source.name),ns.stokes("V",source.name))*0.5
    ns.xy(source.name) << Meq.Conj(ns.yx(source.name))
    ns.yy(source.name) << (ns.stokes("I",source.name)-ns.stokes("Q",source.name))*0.5

    ra    = ns.ra   (source.name) << Meq.Parm(source.ra)
    dec   = ns.dec  (source.name) << Meq.Parm(source.dec)
    radec = ns.radec(source.name) << Meq.Composer(ra, dec)
    lmn   = ns.lmn  (source.name) << Meq.LMN(radec_0 = ns.radec0, radec = radec)
    n     = ns.n    (source.name) << Meq.Selector(lmn, index=2)

    ns.lmn_minus1(source.name) << Meq.Paster(lmn, n-1, index=2)
   
    ns.coherency(source.name) << Meq.Matrix22(ns.xx(source.name),
                                        ns.xy(source.name),
                                        ns.yx(source.name),
                                        ns.yy(source.name))/ns.n(source.name)
    pass




def _define_forest(ns):
    mep_table_name = '3C343.mep'
    source_mep_tablename= 'sourcemodel.mep'

    source_model=create_initial_source_model(source_mep_tablename)

    forest_global_constants(ns, 16)
    for source in source_model:
        forest_source_subtrees(ns, source)
    pass




def create_inputrec(msname, tile_size=1500):
    inputrec=record()

    inputrec.ms_name          = msname
    inputrec.data_column_name = 'DATA'
    inputrec.tile_size        = tile_size
    inputrec.selection = record(channel_start_index=25,\
                                channel_end_index=40,\
                                selection_string='')
    inputrec.python_init = 'read_msvis_header.py'
    
    return inputrec



def create_outputrec(output_column='CORRECTED_DATA'):
    outputrec=record()

    outputrec.write_flags=False
    outputrec.predict_column=output_column
    
    return outputrec


def create_solver_defaults(num_iter=6):
    solver_defaults=record()
    solver_defaults.num_iter     = num_iter
    solver_defaults.save_funklets= True
    solver_defaults.last_update  = True
    return solver_defaults




def _test_forest(mqs, parent):
    pass


def _tdl_job_source_flux_fit_no_calibration(mqs, parent):
    msname          = '3C343.MS'
    inputrec        = create_inputrec(msname)
    outputrec       = create_outputrec()
    solver_defaults = create_solver_defaults()


    print inputrec
    print outputrec
    print solver_defaults

    mqs.init(record(mandate_regular_grid=False),\
                    input=inputrec, output=outputrec)
    pass





def _tdl_job_phase_solution_with_given_fluxes(mqs, parent):
    pass

def _tdl_job_gain_solution_with_given_fluxes(mqs, parent):
    pass






Settings.forest_state.cache_policy = 100;
Settings.orphans_are_roots = True;

if __name__ == '__main__':

    
    Timba.TDL._dbg.set_verbose(5);
    ns = NodeScope();
    _define_forest(ns);

   
    ns.Resolve();
    pass
