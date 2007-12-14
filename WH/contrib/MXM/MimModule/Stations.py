from Timba.TDL import *
from Timba.Contrib.MXM.MimModule import xyzComponent


tot_stat_list = ['7odm','agmt','alam','alpp','alut','ana1','aoa1','apex','argu','arm1','arm2','ashm','ast1','avry','azah','azbk','azcl','azcn','azco','azgb','azkr','azmo','azpe','azry','azsc','azu1','bamo','bar1','batm','bbdm','bbry','bcwr','beat','bemt','bepk','bgis','bill','bkap','bkms','bkr1','blsa','blyt','bmhl','bmry','bran','brpk','bsry','btdm','bull','burn','bvpp']
tot_stat_list +=['ca99','cact','cand','carh','cast','cat1','cat2','cbhs','cccc','ccco','cccs','cdmt','ceda','cgdm','chab','chil','chlo','chms','cho1','cirx','cjms','clar','clov','cmbb','cme1','cmod','cmp9','cnpp','coon','copr','cosa','coso','cot1','cot2','cotd','cpbn','cram','crat','crbt','crfp','crhs','crrs','cru1','csci','csdh','csn1','csst','ctdm','ctms','cuhs','cvhs','dam2','dam3','ddmn','desc','dhlg','dshs','dsme','dssc','dvle','dvlw','dvne','dvpb','dyer','dyhs','ecfs','echo','edpp','egan','elko','elsc','eout','ese2','esrw','ewpp','farb','fern','fgst','fmtp','fmvt','foot','fred','fst1','fvpk','fxhs','fzhs'];
tot_stat_list += ['gabb','garl','gdec','ghrp','glrs','gmrc','gnps','gol2','gold','gosh','gvrs','hbco','hcmn','hcro','hebe','hell','her2','hivi','hnps','hol3','holp','hopb','hotk','hunt','hurr','hvys','i40a','iid2','imps','islk','ivco','jnpr','john','jplm','kayo','kbrc','knol','krac','kyvw','lacr','land','lapc','lasc','lbc1','lbc2','lbch','ldes','ldsw','leep','lewi','lfrs','lice','linj','litt','ljrn','lkn1','ll01','llas','lmut','lnc1','lnco','lnmt','long','lors','lows','ltut','lutz','lvms','lvwd','masw','mat2','mdmt','merc','mexi','mhcb','mhms','mida','midv','mig1','mine','mins','mjpk','mlfp','mnmc','modb','moil','monb','moni','monp','mput','mpwd','msob','mta1','musb','mvfd','mwtp','myt1','naiu','nbps','ndap','neva','news','nhrg','nmgr','noco','nope','nopk','nsss','nvbr','nvlm','nvtr','oaes','oeoc','oghs','ohln','opbl','opcl','opcp','oprd','ores','ork1','ormt','orvb','ovls','oxmt','oxyc','ozst'];
tot_stat_list += ['p002','p003','p005','p009','p011','p012','p015','p016','p028','p056','p057','p058','p059','p060','p066','p067','p068','p069','p071','p072','p073','p074','p075','p076','p080','p081','p082','p084','p085','p086','p087','p088','p089','p095','p099','p102','p104','p105','p106','p107','p108','p110','p111','p112','p113','p114','p117','p118','p119','p121','p122','p127','p128','p130','p132','p133','p134','p139','p140','p146','p148','p156','p157','p158','p159','p160','p161','p162','p163','p164','p165','p166','p167','p168','p169','p170','p171','p175','p181','p182','p183','p187','p188','p189','p190','p196','p197','p198','p199','p200','p206','p210','p212','p213','p217','p218','p222','p224','p225','p226','p227','p228','p229','p230','p231','p233','p234','p238','p240','p242','p244','p247','p252','p255','p256','p257','p259','p260','p261','p262','p264','p265','p266','p267','p268','p270','p271','p272','p273','p274','p275','p278','p280','p281','p282','p283','p284','p285','p287','p288','p290','p293','p294','p295','p296','p297','p300','p301','p302','p303','p304','p305','p306','p307','p309','p312','p313','p314','p316','p317','p318','p324','p326','p332','p338','p341','p344','p345','p348','p349','p370','p380','p388','p464','p467','p470','p471','p472','p473','p474','p476','p477','p478','p479','p480','p482','p483','p484','p485','p486','p490','p491','p494','p495','p496','p497','p498','p499','p500','p501','p502','p504','p505','p506','p507','p508','p509','p511','p514','p515','p516','p523','p525','p526','p527','p528','p529','p530','p532','p533','p536','p537','p539','p540','p541','p543','p544','p546','p547','p549','p551','p553','p554','p556','p558','p559','p560','p561','p562','p563','p564','p565','p566','p567','p570','p571','p572','p576','p577','p579','p581','p583','p584','p586','p588','p591','p594','p595','p600','p601','p606','p607','p610','p611','p612','p615','p617','p618','p621','p622','p623','p626','p630','p631','p632','p642','p643','p646','p655','p672','p674','p725','pbpp','perl','phin','phlb','pin1','pin2','pkdb','pkrd','plo5','pmhs','pmob','pmtn','poin','pomm','potr','ppbf','ppt5','psap','psdm','ptrb','pve3','pvhs','pvrs','qcy2','qhtp','quin','rail','ramt','rbut','rca2','rdmt','rdom','rep2','rep3','rep4','rhcl','rnch','rock','roge','rstp','rsvy','rths','ruby','rump','ryan','sa24','sa27','sa31','sa46','sa48','sacy','saob','sawc','sbcc','sbrn','scia','scip','sdhl','sfdm','sghs','sgps','shin','shld','shos','sibe','silk','sio3','skul','skyb','slac','slcu','sli4','slid','slms','smel','smyc','snhs','sni1','sodb','somt','spic','spk1','spms','spmx','srp1','srs1','stri','sutb','svin','tabl','tate','tblp','thal','thcp','tibb','tilc','tiva','tjrn','toiy','tono','torp','tost','trak','trnd','troy','tung','twms','uclp','ucsb','unr1','upsa','usc1','usgc','uslo','usmx','van1','vdcy','vimt','vine','vnco','vncx','vndp','vnps','vons','vtis','vyas','watc','wchs','wgpp','whc1','whyt','widc','wkpk','wlsn','wmap','wnra','womt','wrhs','wwmt','ybhb','zlc1','zoa1','zoa2'];



wide_stat_list = ['her2','sa27','usmx','p388','burn','mdmt','cme1','p157','p028','nmgr','p107','azcn','oxyc','silk','vdcy','p525',];

small_stat_list = ['vdcy','oxyc','silk','mta1','usc1','gvrs','nopk','bkms','holp'];
selected_sat_list = [21,7,18,22,3,14,1,31,25,11,20,23,16,13,27,8,28,17,9,4,2,24,5];

class Satellites(object):
    def __init__(self,sat_list):
        self._selected_sat_list =sat_list;
    def list(self):
        return self._selected_sat_list;


class Stations(object):
    def __init__(self):
        self._stat_info = record();
        self._stat_options_list={};
        self._selected_stat_list=[];
        for stat in tot_stat_list:
            opts = self._stat_info[stat]=record();
            opts.tdloption_namespace = stat;
            self._stat_options_list[stat] = TDLOption("use",
                                                      stat,True,namespace=opts);

        self._wide_stat_options_list =[];
        self._small_stat_options_list =[];
        
        for stat in wide_stat_list:
            self._wide_stat_options_list.append(self._stat_options_list[stat]);

        for stat in small_stat_list:
            self._small_stat_options_list.append(self._stat_options_list[stat]);


        self._stations_list_option =   TDLCompileOption('stat_list_name',"Get List of Stations",['wide','small']);
        self._wide_list =  TDLCompileMenu("Switch on/off stations by hand",*self._wide_stat_options_list)
        self._small_list = TDLCompileMenu("Switch on/off stations by hand",*self._small_stat_options_list)
        # Define a callback to be called whenever the stat_file option changes
        # This particular callback will get the stat_list from the file
        self._stations_list_option.when_changed(self._create_stat_list);

        #satellites
        self._sat_info = record();
        self._sat_options_list=[];
        self._sats = Satellites(selected_sat_list);
        for sat in self._sats.list():
            sat_str = str(sat);
            opts = self._sat_info[sat_str]=record();
            opts.tdloption_namespace = str(sat);
            self._sat_options_list.append(TDLOption("use",
                                                    str(sat),True,namespace=opts));
        self._sat_list = TDLCompileMenu("Switch on/off satellites by hand",*self._sat_options_list)

         
        #TDLCompileMenu("stations",self._stations_list_option,self._wide_list,self._small_list);


    def _create_stat_list(self,stat_list_name):
        if stat_list_name=='wide':
            self._wide_list.show(1);
            self._small_list.show(0);
            self._selected_stat_list =  wide_stat_list;
        if stat_list_name=='small':
            self._wide_list.show(0);
            self._small_list.show(1);
            self._selected_stat_list =  small_stat_list;


        
    def Stat_list(self):
        statl = [];
        for stat in self._selected_stat_list:
            if self._stat_info[stat]['use']:
                statl.append(stat);

        
        return statl;

    def Sat_list(self):
        satl = [];
        for sat in self._sats.list():
            if self._sat_info[str(sat)]['use']:
                satl.append(sat);

        
        return satl;
