#include "TableFormat.h"
#include "DMI/TypeInfo.h"

namespace VisCube 
{
    
//##ModelId=3DB964F30069
TableFormat::ColumnFormat 
  TableFormat::nullColumn = { 0,0,0 };


// Class TableFormat 

//##ModelId=3DB964F300AD
TableFormat::TableFormat(const TableFormat &right)
    : DMI::BObj()
{
  operator = (right);
}

//##ModelId=3DB964F300C6
TableFormat::TableFormat (int ncol)
{
  init(ncol);
}


//##ModelId=3DB964F300DF
TableFormat::~TableFormat()
{
  block.unlock();
}


//##ModelId=3DB964F300E0
TableFormat & TableFormat::operator=(const TableFormat &right)
{
  if( &right != this )
  {
    if( right.block.valid() )
      block.copy(right.block);
    else
      block.detach();
    cols = right.cols;
    shapes = right.shapes;  
  }
  return *this;
}


//##ModelId=3DB964F300F8
bool TableFormat::operator==(const TableFormat &right) const
{
  if( &right == this )
    return true;
  // since refs are only == when both valid and pointing to the same target,
  // having the same cached block implies equality of formats
  if( block == right.block )
    return true;
  if( maxcol() != right.maxcol() )
    return false;
  for( int i=0; i<maxcol(); i++ )
    if( type(i) || right.type(i) )
    {
      if( type(i) != right.type(i) || cellsize(i) != right.cellsize(i) ||
          shapes[i] != right.shapes[i] )
        return false;
    }
  return true;
}

//##ModelId=3DB964F30112
bool TableFormat::operator!=(const TableFormat &right) const
{
  return ! operator==(right);
}



//##ModelId=3DB964F3012B
TableFormat & TableFormat::init (int ncol)
{
  // clear cached block
  block.unlock().detach();
  cols.resize(ncol);
  cols.assign(ncol,nullColumn);
  shapes.resize(ncol);
  shapes.assign(ncol,LoShape());
  return *this;
}

//##ModelId=3DB964F30145
TableFormat & TableFormat::add (int icol, TypeId type, const LoShape & shp)
{
  FailWhen1(icol>=maxcol(),"column index out of range");
  FailWhen1(cols[icol].type != 0,"column already defined");
  // clear cached block
  block.unlock().detach();
  // fill in column format entry
  const TypeInfo &tinfo = TypeInfo::find(type);
  cols[icol].type = type;
  cols[icol].size = tinfo.size;
  shapes[icol] = shp;
  // compute cell size
  cols[icol].cellsize = tinfo.size;
  for( uint i=0; i<shp.size(); i++ )
    cols[icol].cellsize *= shp[i];
  return *this;
}

//##ModelId=3DB964F30258
CountedRefTarget* TableFormat::clone (int , int ) const
{
  return new TableFormat(*this);
}

//##ModelId=3DB964F3027D
int TableFormat::fromBlock (BlockSet& set)
{
  block.unlock();
  set.pop(block);
  block.lock();
  // unpack stuff from block
  FailWhen(block->size()<sizeof(Header),"corrupt block");
  const Header *hdr = block->pdata<Header>();
  FailWhen(BObj::checkHeader(hdr)!=1,"block count mismatch in header");
  FailWhen(block->size()!=sizeof(Header)+hdr->cf_size+hdr->cs_size,"corrupt block");
  const char *ptr = block->cdata() + sizeof(Header);
  ColumnFormatPacker::unpack(cols,ptr,hdr->cf_size);
  ptr += hdr->cf_size;
  ColumnShapePacker::unpack(shapes,ptr,hdr->cs_size);
  return 1;
}

//##ModelId=3DB964F30297
int TableFormat::toBlock (BlockSet &set) const
{
  // if no block cached, create one and pack info into it
  typedef SeqPacker<FormatVector,BinPacker<ColumnFormat> > ColumnFormatPacker;
  if( !block.valid() )
  {
    // computes size and creates block
    size_t cf_size = ColumnFormatPacker::packSize(cols),
           cs_size = ColumnShapePacker::packSize(shapes),
           totsize = cf_size + cs_size;
    SmartBlock *pb = new SmartBlock(sizeof(Header) + totsize);
    block.attach(pb).lock();
    // store info
    Header *hdr = pb->pdata<Header>();
    BObj::fillHeader(hdr,1);
    hdr->cf_size = cf_size;
    hdr->cs_size = cs_size;
    char *ptr = pb->cdata() + sizeof(Header);
    ptr += ColumnFormatPacker::pack(cols,ptr,totsize);
    ptr += ColumnShapePacker::pack(shapes,ptr,totsize);
    DbgFailWhen(totsize,"pack size mismatch");
  }
  set.push(block);
  return 1;
}


//##ModelId=3DD3BEEF0147
string TableFormat::sdebug ( int detail,const string &,const char *name ) const
{
  using Debug::append;
  using Debug::appendf;
  using Debug::ssprintf;
  
  string out;
  if( detail >= 0 ) // basic detail
  {
    appendf(out,"%s/%08x",name?name:"TableFormat",(int)this);
  }
  if( detail == 1 || detail == -1 )   // normal detail
  {
    // show total # of defined columns
    int count = 0;
    for( int icol=0; icol<maxcol(); icol++ )
      if( defined(icol) )
        count++;
    appendf(out,"%d/%d cols",count,maxcol());
  }
  else if( detail > 1 || detail < -1 )
  {
    // show "#:type:N[xN2[xN3]]" for every defined column
    for( int icol=0; icol<maxcol(); icol++ )
      if( defined(icol) )
      {
        LoShape shp = shape(icol);
        string desc = ssprintf("%d:%s",icol,type(icol).toString().c_str());
        if( ndims(icol) )
        {
          desc += "(";
          for( int j=0; j<ndims(icol); j++ )
          {
            if( j ) 
              desc += "x";
            desc += ssprintf("%d",shp[j]);
          }
          desc += ")";
        }
        append(out,desc);
      }
  }
  return out;
}


};
