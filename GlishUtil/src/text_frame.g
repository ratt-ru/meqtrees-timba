pragma include once
include 'widgetserver.g'

const text_frame := function (parent,disabled=T,
                              size=[60,20],wrap='none',text='',ref ws=dws)
{
  rec := [=];
  rec.disabled := disabled;
  rec.tf := ws.frame(parent,side='left',borderwidth=0);
  rec.text := ws.text(rec.tf,disabled=disabled,text=text,
        relief='sunken',width=size[1],height=size[2],wrap=wrap);
  rec.vsb := ws.scrollbar(rec.tf);
  whenever rec.vsb->scroll do
      rec.text->view($value);
  whenever rec.text->yscroll do
      rec.vsb->view($value);
  if( wrap == 'none' )
  {
    rec.bf := ws.frame(parent,side='right',borderwidth=0,expand='x');
    rec.pad := ws.frame(rec.bf,
                expand='none',width=23,height=23,relief='groove');
  
    rec.hsb := ws.scrollbar(rec.bf,orient='horizontal');
    whenever rec.hsb->scroll do
      rec.text->view($value);
    whenever rec.text->xscroll do
        rec.hsb->view($value);
  }
  
  const rec.done := function ()
  {
    wider rec;
    rec.text := F;
    rec.pad := F;
    rec.tf := F;
    rec.bf := F;
    rec := [=];
  }
      
  const rec.settext := function (text)
  {
    wider rec;
    if( rec.disabled )
      rec.text->enable();
    rec.text->delete('1.0','99999.99999');
    rec.text->append(text);
    rec.text->see('0.0')
    if( rec.disabled )
      rec.text->disable();
  }
  
  return ref rec;
}
  
