//##ModelId=3DB964F20068
//## begin module%1.4%.codegen_version preserve=yes
//   Read the documentation to learn more about C++ code generator
//   versioning.
//## end module%1.4%.codegen_version

//## begin module%3D809CE902E2.cm preserve=no
//	  %X% %Q% %Z% %W%
//## end module%3D809CE902E2.cm

//## begin module%3D809CE902E2.cp preserve=no
//## end module%3D809CE902E2.cp

//## Module: TableTile%3D809CE902E2; Package specification
//## Subsystem: VisCube%3D809CF3019C
//## Source file: F:\lofar9\oms\LOFAR\src-links\VisCube\TableTile.h

#ifndef TableTile_h
#define TableTile_h 1

//## begin module%3D809CE902E2.additionalIncludes preserve=no
#include "DMI/Common.h"
#include "DMI/DMI.h"
//## end module%3D809CE902E2.additionalIncludes

//## begin module%3D809CE902E2.includes preserve=yes
//## end module%3D809CE902E2.includes

// BlockableObject
#include "DMI/BlockableObject.h"
//## begin module%3D809CE902E2.declarations preserve=no
//## end module%3D809CE902E2.declarations

//## begin module%3D809CE902E2.additionalDeclarations preserve=yes
//## end module%3D809CE902E2.additionalDeclarations


//## begin TableTile%3D808C5C013D.preface preserve=yes
//## end TableTile%3D808C5C013D.preface

//## Class: TableTile%3D808C5C013D
//## Category: VisCube%3D809C7602DD
//## Subsystem: VisCube%3D809CF3019C
//## Persistence: Transient
//## Cardinality/Multiplicity: n



class TableTile : public BlockableObject  //## Inherits: <unnamed>%3D81B4CF03D5
{
  //## begin TableTile%3D808C5C013D.initialDeclarations preserve=yes
  public:
    //##ModelId=3DB964F2006E
      class ColDesc
      {
        public:
        //##ModelId=3DB964F30304
          int elsize,nelem,offset;
          
        //##ModelId=3DB964F30308
          ColDesc( int es,int ne=1,int off=0 ) 
            : elsize(es),nelem(ne),offset(offs) 
          {}
      };
      
  //## end TableTile%3D808C5C013D.initialDeclarations

  public:
    //##ModelId=3DB964F20071
    //## begin TableTile::Format%3D85A91F008C.preface preserve=yes
    //## end TableTile::Format%3D85A91F008C.preface

    //## Class: Format%3D85A91F008C
    //## Category: VisCube%3D809C7602DD
    //## Subsystem: VisCube%3D809CF3019C
    //## Persistence: Transient
    //## Cardinality/Multiplicity: n



    class Format 
    {
      //## begin TableTile::Format%3D85A91F008C.initialDeclarations preserve=yes
      //## end TableTile::Format%3D85A91F008C.initialDeclarations

      public:
        //##ModelId=3DB964F3031B
        //## Constructors (generated)
          Format(const Format &right);

        //##ModelId=3DB964F3031F
        //## Constructors (specified)
          //## Operation: Format%3D85D865033F
          Format (int ncol = 0);

        //##ModelId=3DB964F30323
        //## Assignment Operation (generated)
          Format & operator=(const Format &right);


        //##ModelId=3DB964F30327
        //## Other Operations (specified)
          //## Operation: init%3D85DC01012A
          Format & init (BlockRef &ref);

        //##ModelId=3DB964F3032C
          //## Operation: init%3D85AC45024B
          Format & init (int ncol);

        //##ModelId=3DB964F30330
          //## Operation: add%3D85ABE701BA
          Format & add (int icol, int elsize, int nelem = 1);

        //##ModelId=3DB964F30338
          //## Operation: maxcol%3D85AE7A02D0
          int maxcol () const;

        //##ModelId=3DB964F3033A
          //## Operation: rowsize%3D85BFAA0272
          int rowsize () const;

        //##ModelId=3DB964F3033C
          //## Operation: offset%3D85C43A0272
          int offset (int icol) const;

        //##ModelId=3DB964F30341
          //## Operation: elsize%3D85C44300F8
          int elsize (int icol) const;

        //##ModelId=3DB964F30346
          //## Operation: nelem%3D85C4490350
          int nelem (int icol) const;

        //##ModelId=3DB964F3034B
          //## Operation: ref%3D85DA280225
          BlockRef ref () const;

        //##ModelId=3DB964F3034D
          //## Operation: dataSize%3D85AD8401DC
          size_t dataSize () const;

        //##ModelId=3DB964F3034F
          //## Operation: dataSize%3D85ACBF000C
          static size_t dataSize (int maxcol);

        // Additional Public Declarations
          //## begin TableTile::Format%3D85A91F008C.public preserve=yes
          //## end TableTile::Format%3D85A91F008C.public

      protected:
        // Additional Protected Declarations
          //## begin TableTile::Format%3D85A91F008C.protected preserve=yes
          //## end TableTile::Format%3D85A91F008C.protected

      private:
        // Additional Private Declarations
          //## begin TableTile::Format%3D85A91F008C.private preserve=yes
          //## end TableTile::Format%3D85A91F008C.private

      private:
        //##ModelId=3DB964F3030D
        //## implementation
        // Data Members for Class Attributes

          //## Attribute: block%3D85ACA60150
          //## begin TableTile::Format::block%3D85ACA60150.attr preserve=no  private: BlockRef {U} 
          BlockRef block;
        //##ModelId=3DB964F30316
          //## end TableTile::Format::block%3D85ACA60150.attr

        // Additional Implementation Declarations
          //## begin TableTile::Format%3D85A91F008C.implementation preserve=yes
          void *data;
          
        //##ModelId=3DB964F30354
          int &  _maxcol  ()         const { return data[0]; }
        //##ModelId=3DB964F30357
          int &  _rowsize ()         const { return data[1]; }
        //##ModelId=3DB964F30359
          int &  _elsize  (int icol) const { return data[(icol*3)+2]; }
        //##ModelId=3DB964F3035E
          int &  _nelem   (int icol) const { return data[(icol*3)+3]; }
        //##ModelId=3DB964F30364
          int &  _offset  (int icol) const { return data[(icol*3)+4]; }
          //## end TableTile::Format%3D85A91F008C.implementation
    };

    //##ModelId=3DB964F303C8
    //## begin TableTile::Format%3D85A91F008C.postscript preserve=yes
    //## end TableTile::Format%3D85A91F008C.postscript

    //## Constructors (generated)
      TableTile();

    //##ModelId=3DB964F303C9
      TableTile(const TableTile &right);

    //##ModelId=3DB964F303DC
    //## Constructors (specified)
      //## Operation: TableTile%3D80ADF10232
      TableTile (const TableTile &other, int flags = DMI::WRITE);

    //##ModelId=3DB964F40019
      //## Operation: TableTile%3D819CDF00DF
      TableTile (const TableTile::Format &form, int nr = 0);

    //##ModelId=3DB964F4003E
    //## Destructor (generated)
      ~TableTile();

    //##ModelId=3DB964F4003F
    //## Assignment Operation (generated)
      TableTile & operator=(const TableTile &right);


    //##ModelId=3DB964F40052
    //## Other Operations (specified)
      //## Operation: init%3D81A34900E0
      void init (const TableTile::Format &form, int nr = 0);

    //##ModelId=3DB964F40077
      //## Operation: isWritable%3D81BAC5015C
      bool isWritable () const;

    //##ModelId=3DB964F4007A
      //## Operation: wpdata%3D80ADBD027D
      char * wpdata ();

    //##ModelId=3DB964F4007B
      //## Operation: addRows%3D80B0F202BA
      void addRows (int nr);

    //##ModelId=3DB964F4008E
      //## Operation: addColumn%3D85D59B008F
      void addColumn (int icol, int elsize, int nelem = 1);

    //##ModelId=3DB964F400C6
      //## Operation: addColumns%3D85DA77012E
      void addColumns (const TableTile::Format &form);

    //##ModelId=3DB964F400D9
      //## Operation: merge%3D80B07C01B6
      void merge (const TableTile &other);

    //##ModelId=3DB964F400EC
      //## Operation: clone%3D81B56602CE; C++
      //	Abstract method for cloning an object. Should allocate a new object
      //	with "new" and return pointer to it. If DMI::WRITE is specified,
      //	then a writable clone is required.
      //	The depth argument specifies cloning depth (the DMI::DEEP flag
      //	means infinite depth). If depth=0, then any nested refs should only
      //	be copy()d. ). If depth>0, then nested refs should be copied and
      //	privatize()d , with depth=depth-1.
      //	The DMI::DEEP flag  corresponds to infinitely deep cloning. If this
      //	is set, then depth should be ignored, and nested refs should be
      //	privatize()d with DMI::DEEP.
      //
      //	 Otherwise, nested refs should be copied & privatized  with
      //	depth=depth-1 and the DMI::DEEP flag passed on.
      virtual CountedRefTarget* clone (int flags = 0, int depth = 0) const;

    //##ModelId=3DB964F40112
      //## Operation: fromBlock%3D81B57003CD
      //	Creates object from a set of block references. Appropriate number of
      //	references are removed from the head of the BlockSet. Returns # of
      //	refs removed.
      virtual int fromBlock (BlockSet& set);

    //##ModelId=3DB964F40126
      //## Operation: toBlock%3D81B57B036E
      //	Stores an object into a set of blocks. Appropriate number of refs
      //	added to tail of BlockSet. Returns # of block refs added.
      virtual int toBlock (BlockSet &set) const;

    //##ModelId=3DB964F4013A
      //## Operation: objectType%3D81B58000EB
      //	Returns the class TypeId
      virtual TypeId objectType () const = 0;

    //##ModelId=3DB964F4013C
      //## Operation: privatize%3D81B58C0369
      //	Virtual method for privatization of an object.
      //	The depth argument determines the depth of privatization and/or
      //	cloning (see CountedRefBase::privatize()). If depth>0, then any
      //	nested refs should be privatize()d as well, with depth=depth-1.
      //	The DMI::DEEP flag  corresponds to infinitely deep privatization. If
      //	this is set, then depth should be ignored, and nested refs should be
      //	privatize()d with DMI::DEEP.
      //	If depth=0 (and DMI::DEEP is not set), then privatize() is
      //	effectively a no-op. However, if your class has a 'writable'
      //	property, it should be changed in accordance with the DMI::WRITE
      //	and/or DMI::READONLY flags.
      virtual void privatize (int flags = 0, int depth = 0);

    //##ModelId=3DB964F40162
    //## Get and Set Operations for Class Attributes (generated)

      //## Attribute: pdata%3D81B8EB02EB
      const char * pdata () const;

    //##ModelId=3DB964F40164
      //## Attribute: ncol%3D81B9A10044
      int ncol () const;

    //##ModelId=3DB964F40166
      //## Attribute: nrow%3D85CC940254
      int nrow () const;

    //##ModelId=3DB964F40168
    //## Get and Set Operations for Associations (generated)

      //## Association: VisCube::<unnamed>%3D85A92F01BB
      //## Role: TableTile::format%3D85A9300072
      const Format& format () const;

  public:
    // Additional Public Declarations
      //## begin TableTile%3D808C5C013D.public preserve=yes
      //## end TableTile%3D808C5C013D.public

  protected:
    // Additional Protected Declarations
      //## begin TableTile%3D808C5C013D.protected preserve=yes
      //## end TableTile%3D808C5C013D.protected

  private:
    // Additional Private Declarations
      //## begin TableTile%3D808C5C013D.private preserve=yes
      //## end TableTile%3D808C5C013D.private

  private:
    //##ModelId=3DB964F3036D
    //## implementation
    // Data Members for Class Attributes

      //## Attribute: datablock%3D809B8F00A0
      //## begin TableTile::datablock%3D809B8F00A0.attr preserve=no  private: BlockRef {U} 
      BlockRef datablock;
    //##ModelId=3DB964F30379
      //## end TableTile::datablock%3D809B8F00A0.attr

      //## begin TableTile::pdata%3D81B8EB02EB.attr preserve=no  public: char * {U} 
      char *pdata_;
    //##ModelId=3DB964F30381
      //## end TableTile::pdata%3D81B8EB02EB.attr

      //## begin TableTile::ncol%3D81B9A10044.attr preserve=no  public: int {U} 
      int ncol_;
    //##ModelId=3DB964F30388
      //## end TableTile::ncol%3D81B9A10044.attr

      //## begin TableTile::nrow%3D85CC940254.attr preserve=no  public: int {U} 
      int nrow_;
    //##ModelId=3DB964F30391
      //## end TableTile::nrow%3D85CC940254.attr

    // Data Members for Associations

      //## Association: VisCube::<unnamed>%3D85A92F01BB
      //## begin TableTile::format%3D85A9300072.role preserve=no  public: TableTile::Format { -> 1VHgN}
      Format format_;
    //##ModelId=3DB964F303A2
      //## end TableTile::format%3D85A9300072.role

    // Additional Implementation Declarations
      //## begin TableTile%3D808C5C013D.implementation preserve=yes
      // pointer to start of header data
      const ColDesc *pcoldesc;
      // this is the number of columns present in the header
    //##ModelId=3DB964F303B5
      int maxcol;
    //##ModelId=3DB964F4016A
      size_t headerSize ()  { return sizeof(int) + hdrcol*sizeof(ColDesc) };
      //## end TableTile%3D808C5C013D.implementation
};

//##ModelId=3DB964F30338
//## begin TableTile%3D808C5C013D.postscript preserve=yes
//## end TableTile%3D808C5C013D.postscript

// Class TableTile::Format 


//## Other Operations (inline)
inline int TableTile::Format::maxcol () const
{
  //## begin TableTile::Format::maxcol%3D85AE7A02D0.body preserve=yes
  return _maxcol();
  //## end TableTile::Format::maxcol%3D85AE7A02D0.body
}

//##ModelId=3DB964F3033A
inline int TableTile::Format::rowsize () const
{
  //## begin TableTile::Format::rowsize%3D85BFAA0272.body preserve=yes
  return _rowsize();
  //## end TableTile::Format::rowsize%3D85BFAA0272.body
}

//##ModelId=3DB964F3033C
inline int TableTile::Format::offset (int icol) const
{
  //## begin TableTile::Format::offset%3D85C43A0272.body preserve=yes
  return _offset(icol);
  //## end TableTile::Format::offset%3D85C43A0272.body
}

//##ModelId=3DB964F30341
inline int TableTile::Format::elsize (int icol) const
{
  //## begin TableTile::Format::elsize%3D85C44300F8.body preserve=yes
  return _elsize(icol);
  //## end TableTile::Format::elsize%3D85C44300F8.body
}

//##ModelId=3DB964F30346
inline int TableTile::Format::nelem (int icol) const
{
  //## begin TableTile::Format::nelem%3D85C4490350.body preserve=yes
  return _nelem(icol);
  //## end TableTile::Format::nelem%3D85C4490350.body
}

//##ModelId=3DB964F3034B
inline BlockRef TableTile::Format::ref () const
{
  //## begin TableTile::Format::ref%3D85DA280225.body preserve=yes
  return block.copy(DMI::READONLY);
  //## end TableTile::Format::ref%3D85DA280225.body
}

//##ModelId=3DB964F3034D
inline size_t TableTile::Format::dataSize () const
{
  //## begin TableTile::Format::dataSize%3D85AD8401DC.body preserve=yes
  return dataSize(maxcol());
  //## end TableTile::Format::dataSize%3D85AD8401DC.body
}

//##ModelId=3DB964F3034F
inline size_t TableTile::Format::dataSize (int maxcol)
{
  //## begin TableTile::Format::dataSize%3D85ACBF000C.body preserve=yes
  return (2+3*maxcol)*sizeof(int);
  //## end TableTile::Format::dataSize%3D85ACBF000C.body
}

// Class TableTile 


//##ModelId=3DB964F40077
//## Other Operations (inline)
inline bool TableTile::isWritable () const
{
  //## begin TableTile::isWritable%3D81BAC5015C.body preserve=yes
  return !datablock.valid() || datablock.isWritable();
  //## end TableTile::isWritable%3D81BAC5015C.body
}

//##ModelId=3DB964F40162
//## Get and Set Operations for Class Attributes (inline)

inline const char * TableTile::pdata () const
{
  //## begin TableTile::pdata%3D81B8EB02EB.get preserve=no
  return pdata_;
  //## end TableTile::pdata%3D81B8EB02EB.get
}

//##ModelId=3DB964F40164
inline int TableTile::ncol () const
{
  //## begin TableTile::ncol%3D81B9A10044.get preserve=no
  return ncol_;
  //## end TableTile::ncol%3D81B9A10044.get
}

//##ModelId=3DB964F40166
inline int TableTile::nrow () const
{
  //## begin TableTile::nrow%3D85CC940254.get preserve=no
  return nrow_;
  //## end TableTile::nrow%3D85CC940254.get
}

//##ModelId=3DB964F40168
//## Get and Set Operations for Associations (inline)

inline const TableTile::Format& TableTile::format () const
{
  //## begin TableTile::format%3D85A9300072.get preserve=no
  return format_;
  //## end TableTile::format%3D85A9300072.get
}

//## begin module%3D809CE902E2.epilog preserve=yes
//## end module%3D809CE902E2.epilog


#endif


// Detached code regions:
#if 0
//## begin TableTile::Format::Format%3D80A3200150.initialization preserve=yes
    : offsets_(maxcol,0),ncol_(0),size_(0)
//## end TableTile::Format::Format%3D80A3200150.initialization

//## begin TableTile::Format::offset%3D809F4C0010.body preserve=yes
  return offsets_[i];
//## end TableTile::Format::offset%3D809F4C0010.body

#endif
