#-----------------------------------------------------------------------------
# viewer: A fast loading minimal service  implementation of the viewer
#-----------------------------------------------------------------------------
pragma include once;
include 'gdisplay.g';
include 'unset.g';

const qvmessage := subsequence(txt='Loading...') {
    its := [=];
    self.gui := function() {
	wider its;
	tk_hold();
	its.f := frame(title='Message');
	its.m := message(its.f,text=txt);
	its.b := button(its.f,text='Done',background='red',
			foreground='white');
	whenever its.b->press do { self.done();};
	tk_release();
    }
    whenever self->text do {
	its.f->map();
	its.m->text($value);
    }
    self.dismiss := function() {
	its.f->unmap();
    }
    self.gui();
    self.done := function() {
	wider its,self;
	its.f->unmap();
	its.b := F;
	its.m := F;
	its.f := F;
	val its:=F;
	val self := F;
    }
    return T;
}

qvm:= qvmessage('Loading Display Library ...');
const ddlgtk := init_glishtk();
# load the pgplot and gdisplay modules into this new client
tmp := load_gpgplot(ddlgtk);
tmp := load_gdisplay(ddlgtk);
# add in the icon path
aipspath := split(environ.AIPSPATH)
libexec := spaste(aipspath[1], '/', aipspath[2], '/libexec');
tmp := ['.', spaste(libexec, '/icons')];
ddlgtk.tk_iconpath(tmp);

# the "real" viewer
const quickview := subsequence(filename=unset,type='raster', 
			       ws=ddlgtk, logger=F) {
    its := [=];
    its.logger := logger;
    if (is_unset(filename)) { 
	print 'no input file given'; exit;
    }
    its.name := filename;
    its.ws := ws;
    its.gui := [=];
    self.gui := function() {
	wider its;
	str := split(filename,'/');
	if (is_agent(its.logger)) {
	    its.logger->text(spaste('Loading \'',str[len(str)],'\''));
	}
	its.ws.tk_hold();
	its.dd := its.ws.displaydata('raster', filename, 'image');
	if (is_fail(its.dd)) {
	    print its.dd::message;exit;
	}
	str := spaste('AIPS++ Viewer - ',str[len(str)]);
	opt := [axislabelswitch=[value=T],resample=[value='bilinear']];	
	t := its.dd->setoptions(opt);
	opt := its.dd->getoptions();
	its.minmax := opt.minmaxhist.value;
	its.origminmax := opt.minmaxhist.value;
	its.gui.f := its.ws.frame(title=str);
	its.gui.pc := its.ws.pixelcanvas(its.gui.f,450,450);
	# need flashing colors
	if (is_fail(its.gui.pc)) {
	    if (!any(split(to_lower(its.gui.pc::message)) == 'visual') &&
		!any(split(to_lower(its.gui.pc::message)) == 'visuals')) {
		its.gui.f := F;
		its.gui.f := its.ws.frame(title=str,newcmap=T);
		its.gui.pc := its.ws.pixelcanvas(its.gui.f,450,450);
	    }
	} 

	if (is_fail(its.gui.pc)) {
	    print its.gui.pc::message;exit;
	}
	its.gui.pd := its.ws.paneldisplay(its.gui.pc,1,1);
	t := its.gui.pc->standardfiddler(Display::K_Pointer_Button2);
	t := its.gui.pc->mapfiddler(Display::K_Pointer_Button3);    
	t := its.gui.pd->settoolkey("zoomer", Display::K_Pointer_Button1);
	# disable these tools
	t := its.gui.pd->settoolkey("rectangle", 0);
	t := its.gui.pd->settoolkey("polygon", 0);
	t := its.gui.pd->settoolkey("positioner", 0);
	t := its.gui.pd->settoolkey("panner", 0);
	t := its.gui.pd->settoolkey("polyline", 0);
	t := its.gui.pd->add(its.dd);
	its.gui.track := its.ws.message(its.gui.f,fill='x',width=450,
					relief='groove',
					text='No position to report');
	its.length := its.gui.pd->zlength();
	if (its.length>1) {
            its.gui.ani := its.ws.mwcanimator();
	    its.gui.ani->add(its.gui.pd);
	    its.gui.anif := its.ws.frame(its.gui.f,side='left',relief='ridge');
	    its.gui.anilabel := its.ws.label(its.gui.anif,'Channel No:');
	    its.gui.slider := its.ws.scale(its.gui.anif,start=1,
					   end=its.length,width=10,
					   length=400);
	    its.gui.scalefwd := its.scaleforward(its.gui.slider);

	    whenever its.gui.scalefwd->message do {
		zindex := [=];
		zindex.name := "zIndex";
		zindex.value := as_integer($value-1);
		zindex.increment := 1;
		its.gui.ani->setlinearrestriction(zindex);
	    }

	}
	its.gui.minmaxf := its.ws.frame(its.gui.f,side='left',relief='ridge',
					expand='x');
	its.gui.minamxlabel := its.ws.label(its.gui.minmaxf,'Data Min/Max:');
	its.gui.minentry := its.ws.entry(its.gui.minmaxf,width=12);
	its.gui.minentry->insert(as_string(its.minmax[1]));
	its.gui.maxentry := its.ws.entry(its.gui.minmaxf,width=12);
	its.gui.maxentry->insert(as_string(its.minmax[2]));
	its.gui.resetb := its.ws.button(its.gui.minmaxf,'Reset');
	whenever its.gui.resetb->press do {
	    its.minmax := its.origminmax;
	    its.ws.tk_hold();
	    its.gui.minentry->delete("start","end");
	    its.gui.minentry->insert(as_string(its.origminmax[1]));
	    its.gui.maxentry->delete("start","end");
	    its.gui.maxentry->insert(as_string(its.origminmax[2]));	    
	    its.dd->setoptions([minmaxhist=[value=its.origminmax]]);
	    its.ws.tk_release();
	}
	whenever its.gui.minentry->return do {
	    its.minmax[1] := as_float($value);
	    its.dd->setoptions([minmaxhist=[value=its.minmax]]);
	}
	whenever its.gui.maxentry->return do {
	    its.minmax[2] := as_float($value);
	    its.dd->setoptions([minmaxhist=[value=its.minmax]]);
	}
	its.ws.tk_release();
	whenever self->message do {
	    x := $value;
	    its.gui.ani->setlinearrestriction(x);
	}
	its.gui.viewerb := its.ws.button(its.gui.f,'Full Viewer...');
	whenever its.gui.viewerb->press do {
	    its.gui.f->unmap();
	    if (is_agent(its.logger)) {
		its.logger->text('Loading full viewer...');
	    }
	    global dp,dd;
	    global ddlws;
	    include 'widgetserver.g';
	    # insert ddlgtk into widgetserver
	    const ddlws := widgetserver(whichgtk=ddlgtk);
	    include 'viewer.g';
	    stat :=its.gui.pc->status();
	    dv.hold();
	    dd := dv.loaddata(its.name,'raster');
	    dd.setoptions(its.dd->getoptions());
	    dp := dv.newdisplaypanel(width=stat.width,
				     height=stat.height,

				     autoregister=T);
	    dp.register(dd);
	    if (is_agent(its.gui.slider)) {
		x := its.gui.slider->value();
		dp.animator().goto(as_integer(x));
	    }
	    dv.release();
	    if (is_agent(its.logger)) {
		its.logger.done();
	    }
	    self.done();
	}
	whenever its.dd->motion do {
	    tval := $value.formattedvalue;
	    tpos := $value.formattedworld;
	    its.gui.track->text(spaste(tval,' at ',tpos));
	}
	whenever its.gui.f->killed do { exit;};
	if (is_agent(its.logger)) {
	    its.logger.dismiss();
	}
    }

    self.done := function() {
	wider its,self;
	its.gui.pd->remove(its.dd);
	its.dd := F;
	its.gui.ani := F;
	its.gui.pd := F;
	its.gui.pc := F;
	val its := F;
	val self := F;
    }
    # stupid scale widget needs this to event forwarding
    const its.scaleforward := subsequence(widget) {	
    pits.widget := widget;
    whenever pits.widget->value do {
	x := $value;
	self->message(x);
    }
}

    self.gui();
}

tmp := argv[len(argv)];
if (is_string(tmp)) {
    qv := quickview(tmp, logger=qvm);
} else {
    fail 'No input file specified.';
    exit;
}
