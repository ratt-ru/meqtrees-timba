//## begin module%1.4%.codegen_version preserve=yes
//   Read the documentation to learn more about C++ code generator
//   versioning.
//## end module%1.4%.codegen_version

//## begin module%3D809CE902EC.cm preserve=no
//	  %X% %Q% %Z% %W%
//## end module%3D809CE902EC.cm

//## begin module%3D809CE902EC.cp preserve=no
//## end module%3D809CE902EC.cp

//## Module: TableTile%3D809CE902EC; Package body
//## Subsystem: VisCube%3D809CF3019C
//## Source file: F:\lofar9\oms\LOFAR\src-links\VisCube\TableTile.cc

//## begin module%3D809CE902EC.additionalIncludes preserve=no
//## end module%3D809CE902EC.additionalIncludes

//## begin module%3D809CE902EC.includes preserve=yes
//## end module%3D809CE902EC.includes

// TableTile
#include "VisCube/TableTile.h"
//## begin module%3D809CE902EC.declarations preserve=no
//## end module%3D809CE902EC.declarations

//## begin module%3D809CE902EC.additionalDeclarations preserve=yes
int TableTile::Format::dummy_data[2] = { 0,0 };
//## end module%3D809CE902EC.additionalDeclarations


// Class TableTile::Format 

TableTile::Format::Format(const TableTile::Format &right)
  //## begin Format::Format%3D85A91F008C_copy.hasinit preserve=no
  //## end Format::Format%3D85A91F008C_copy.hasinit
  //## begin Format::Format%3D85A91F008C_copy.initialization preserve=yes
  //## end Format::Format%3D85A91F008C_copy.initialization
{
  //## begin TableTile::Format::Format%3D85A91F008C_copy.body preserve=yes
  operator = (right);
  //## end TableTile::Format::Format%3D85A91F008C_copy.body
}

//##ModelId=3DB964F3031F
TableTile::Format::Format (int ncol)
  //## begin TableTile::Format::Format%3D85D865033F.hasinit preserve=no
  //## end TableTile::Format::Format%3D85D865033F.hasinit
  //## begin TableTile::Format::Format%3D85D865033F.initialization preserve=yes
  //## end TableTile::Format::Format%3D85D865033F.initialization
{
  //## begin TableTile::Format::Format%3D85D865033F.body preserve=yes
  init(ncol);
  //## end TableTile::Format::Format%3D85D865033F.body
}


//##ModelId=3DB964F30323
TableTile::Format & TableTile::Format::operator=(const TableTile::Format &right)
{
  //## begin TableTile::Format::operator=%3D85A91F008C_assign.body preserve=yes
  if( &right == this )
    return *this;
  block.copy(other.block,DMI::READONLY);
  data = const_cast<void*>(block->data());
  return *this;
  //## end TableTile::Format::operator=%3D85A91F008C_assign.body
}



//##ModelId=3DB964F30327
//## Other Operations (implementation)
Format & TableTile::Format::init (BlockRef &ref)
{
  //## begin TableTile::Format::init%3D85DC01012A.body preserve=yes
  block.xfer(ref);
  data = const_cast<void*>(block->data());
  return *this;
  //## end TableTile::Format::init%3D85DC01012A.body
}

//##ModelId=3DB964F3032C
Format & TableTile::Format::init (int ncol)
{
  //## begin TableTile::Format::init%3D85AC45024B.body preserve=yes
  block <<= new SmartBlock(dataSize(ncol),DMI::ZERO);
  data = block().data();
  _maxcol(ncol) = ncol;
  return *this;
  //## end TableTile::Format::init%3D85AC45024B.body
}

//##ModelId=3DB964F30330
Format & TableTile::Format::add (int icol, int elsize, int nelem)
{
  //## begin TableTile::Format::add%3D85ABE701BA.body preserve=yes
  FailWhen(icol >= maxcol(),"column index out of range");
  FailWhen(_nelem(icol),"column already defined");
  // block is essentially privatize-on-write
  if( !block.isWritable() )
    block.privatize(DMI::WRITE);
  _nelem(icol) = nelem;
  _elsize(icol) = elsize;
  int offs = rowsize(), align = offs%elsize;
  if( align )
    offs += (elsize-align);
  _offset(icol) = offs;
  _rowsize() = offs + elsize*nelem;
  return *this;
  //## end TableTile::Format::add%3D85ABE701BA.body
}

// Additional Declarations
//##ModelId=3DB964F303C8
  //## begin TableTile::Format%3D85A91F008C.declarations preserve=yes
  //## end TableTile::Format%3D85A91F008C.declarations

// Class TableTile 

TableTile::TableTile()
  //## begin TableTile::TableTile%3D808C5C013D_const.hasinit preserve=no
  //## end TableTile::TableTile%3D808C5C013D_const.hasinit
  //## begin TableTile::TableTile%3D808C5C013D_const.initialization preserve=yes
  : nrow_(0)
  //## end TableTile::TableTile%3D808C5C013D_const.initialization
{
  //## begin TableTile::TableTile%3D808C5C013D_const.body preserve=yes
  //## end TableTile::TableTile%3D808C5C013D_const.body
}

//##ModelId=3DB964F303C9
TableTile::TableTile(const TableTile &right)
  //## begin TableTile::TableTile%3D808C5C013D_copy.hasinit preserve=no
  //## end TableTile::TableTile%3D808C5C013D_copy.hasinit
  //## begin TableTile::TableTile%3D808C5C013D_copy.initialization preserve=yes
  //## end TableTile::TableTile%3D808C5C013D_copy.initialization
{
  //## begin TableTile::TableTile%3D808C5C013D_copy.body preserve=yes
  //## end TableTile::TableTile%3D808C5C013D_copy.body
}

//##ModelId=3DB964F303DC
TableTile::TableTile (const TableTile &other, int flags)
  //## begin TableTile::TableTile%3D80ADF10232.hasinit preserve=no
  //## end TableTile::TableTile%3D80ADF10232.hasinit
  //## begin TableTile::TableTile%3D80ADF10232.initialization preserve=yes
    nrow_(nr)
  //## end TableTile::TableTile%3D80ADF10232.initialization
{
  //## begin TableTile::TableTile%3D80ADF10232.body preserve=yes
  format_ = other.format_;
  datablock.copy(other.datablock,flags);
  pdata_ = datablock->data();
  //## end TableTile::TableTile%3D80ADF10232.body
}

//##ModelId=3DB964F40019
TableTile::TableTile (const TableTile::Format &form, int nr)
  //## begin TableTile::TableTile%3D819CDF00DF.hasinit preserve=no
  //## end TableTile::TableTile%3D819CDF00DF.hasinit
  //## begin TableTile::TableTile%3D819CDF00DF.initialization preserve=yes
  //## end TableTile::TableTile%3D819CDF00DF.initialization
{
  //## begin TableTile::TableTile%3D819CDF00DF.body preserve=yes
  init(form,nr);
  //## end TableTile::TableTile%3D819CDF00DF.body
}


//##ModelId=3DB964F4003E
TableTile::~TableTile()
{
  //## begin TableTile::~TableTile%3D808C5C013D_dest.body preserve=yes
  //## end TableTile::~TableTile%3D808C5C013D_dest.body
}


//##ModelId=3DB964F4003F
TableTile & TableTile::operator=(const TableTile &right)
{
  //## begin TableTile::operator=%3D808C5C013D_assign.body preserve=yes
  format_ = other.format_;
  datablock.copy(other.datablock,DMI::PRESERVE_RW);
  pdata_ = datablock->data();
  //## end TableTile::operator=%3D808C5C013D_assign.body
}



//##ModelId=3DB964F40052
//## Other Operations (implementation)
void TableTile::init (const TableTile::Format &form, int nr)
{
  //## begin TableTile::init%3D81A34900E0.body preserve=yes
  FailWhen(nr<0,"illegal numer of rows");
  // allocate block
  format_ = form;
  nrow_ = nr;
  datablock <<= new SmartBlock(format_.rowsize()*nrow_,DMI::ZERO);
  pdata_ = datablock->data();
  //## end TableTile::init%3D81A34900E0.body
}

//##ModelId=3DB964F4007A
char * TableTile::wpdata ()
{
  //## begin TableTile::wpdata%3D80ADBD027D.body preserve=yes
  DbgFailWhen( pdata_ && !isWritable(),"r/w access violation" );
  return const_cast<char*>(pdata_);
  //## end TableTile::wpdata%3D80ADBD027D.body
}

//##ModelId=3DB964F4007B
void TableTile::addRows (int nr)
{
  //## begin TableTile::addRows%3D80B0F202BA.body preserve=yes
  FailWhen(nr<0,"illegal numer of rows");
  if( !nr )
    return;
  size_t oldsize = datablock.valid() ? datablock->size() : 0;
         addsize = format_.rowsize()*nr;
  BlockRef newblock(new SmartBlock(oldsize+addsize),DMI::ANOWR);
  char * newdata = newblock->data();
  if( oldsize )
    memcpy(newdata,datablock->data(),oldsize);
  memset(newdata+oldsize,0,addsize);
  datablock.xfer(newblock);
  nrow_ += nr;
  //## end TableTile::addRows%3D80B0F202BA.body
}

//##ModelId=3DB964F4008E
void TableTile::addColumn (int icol, int elsize, int nelem)
{
  //## begin TableTile::addColumn%3D85D59B008F.body preserve=yes
  //## end TableTile::addColumn%3D85D59B008F.body
}

//##ModelId=3DB964F400C6
void TableTile::addColumns (const TableTile::Format &form)
{
  //## begin TableTile::addColumns%3D85DA77012E.body preserve=yes
  //## end TableTile::addColumns%3D85DA77012E.body
}

//##ModelId=3DB964F400D9
void TableTile::merge (const TableTile &other)
{
  //## begin TableTile::merge%3D80B07C01B6.body preserve=yes
  //## end TableTile::merge%3D80B07C01B6.body
}

//##ModelId=3DB964F400EC
CountedRefTarget* TableTile::clone (int flags, int depth) const
{
  //## begin TableTile::clone%3D81B56602CE.body preserve=yes
  return new TableTile(*this,flags|DMI::FORCE_CLONE);
  //## end TableTile::clone%3D81B56602CE.body
}

//##ModelId=3DB964F40112
int TableTile::fromBlock (BlockSet& set)
{
  //## begin TableTile::fromBlock%3D81B57003CD.body preserve=yes
  format_.init(set.pop());
  set.pop(datablock);
  size_t sz = datablock->size();
  nrow_ = sz/format_.rowsize();
  FailWhen(sz%format_.rowsize(),"data block size does not match format");
  return 2;
  //## end TableTile::fromBlock%3D81B57003CD.body
}

//##ModelId=3DB964F40126
int TableTile::toBlock (BlockSet &set) const
{
  //## begin TableTile::toBlock%3D81B57B036E.body preserve=yes
  set.push(format_.ref());
  set.push(datablock.copy(DMI::READONLY));
  return 2;
  //## end TableTile::toBlock%3D81B57B036E.body
}

//##ModelId=3DB964F4013C
void TableTile::privatize (int flags, int depth)
{
  //## begin TableTile::privatize%3D81B58C0369.body preserve=yes
  if( datablock.valid() )
    datablock.privatize(flags,depth);
  //## end TableTile::privatize%3D81B58C0369.body
}

// Additional Declarations
  //## begin TableTile%3D808C5C013D.declarations preserve=yes
  //## end TableTile%3D808C5C013D.declarations

//## begin module%3D809CE902EC.epilog preserve=yes
//## end module%3D809CE902EC.epilog


