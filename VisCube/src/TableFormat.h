#ifndef VisCube_TableFormat_h
#define VisCube_TableFormat_h 1

#include "DMI/BlockableObject.h"
#include "DMI/Packer.h"
#include "VisCube/VisCommon.h"
#include "VisCube/TID-VisCube.h"
    
#pragma type #TableFormat
    
//##ModelId=3DB964F20032
//##Documentation
//## TableFormat is used to describe the layout of a table. This is a
//## BlockableObject, so it may be placed in containers, shipped across the
//## netowkr, etc.
class TableFormat : public BlockableObject
{
  public:
      
    //##ModelId=3DB964F300AD
    //##Documentation
    //## Copy constructor.
      TableFormat(const TableFormat &right);

    //##ModelId=3DB964F300C6
    //##Documentation
    //## Creates empty format intended for a maximum of ncol columns. Ncol is
    //## simply the maximum column index that will be available, any columns
    //## between 0 and ncol-1 may be left undefined.
      TableFormat (int ncol = 0);

    //##ModelId=3DB964F300DF
      ~TableFormat();

    //##ModelId=3DB964F300E0
    //##Documentation
    //## Assignment op
      TableFormat & operator=(const TableFormat &right);

    //##ModelId=3DB964F300F8
    //##Documentation
    //## Equality operators. Two formats are considered equal if they define
    //## the same set of columns with the same types and equal dimensions.
      bool operator==(const TableFormat &right) const;

    //##ModelId=3DB964F30112
      bool operator!=(const TableFormat &right) const;


    //##ModelId=3DB964F3012B
    //##Documentation
    //## Initializes format for ncol columns; clears old data (if any)
      TableFormat & init (int ncol);

    //##ModelId=3DB964F30145
    //##Documentation
    //## Define column number icol as having the specified type and cell shape.
    //## If no shape is specified, a scalar column is defined. The column may
    //## not have been defined previously. Note that add() returns *this,
    //## so you can easily string together calls (format.add(...).add(...)) to
    //## initialize an entire format in a single statement.
      TableFormat & add (int icol, TypeId type, const LoShape & shp = LoShape());


    //##ModelId=3DB964F301D5
    //##Documentation
    //## Returns the maximum number of columns available for definition (this
    //## is the ncol argument from constructor and init())
      int maxcol () const;

    //##ModelId=3DB964F302B2
    //##Documentation
    //## Returns true if column icol is defined
      bool defined (int icol) const
      { return type(icol) != 0; }

    //##ModelId=3DB964F301D8
    //##Documentation
    //## Returns type of column icol (0 if undefined)
      TypeId type (int icol) const;

    //##ModelId=3DB964F301F1
    //##Documentation
    //## Returns the size in bytes of a single cell element (that is, the array
    //## element type, if column is an array column)
      int elsize (int icol) const;

    //##ModelId=3DB964F3020B
    //##Documentation
    //## Returns the dimensionality of a column cell: 0 for scalar column, 1
    //## for a vector column, etc.
      int ndims (int icol) const;

    //##ModelId=3DB964F30224
    //##Documentation
    //## Returns the size, in bytes, of a single cell
      int cellsize (int icol) const;

    //##ModelId=3DB964F3023E
    //##Documentation
    //## Returns the shape of a column cell (empty shape for scalar columns)
      const LoShape & shape (int icol) const;

    //##ModelId=3DB964F30258
    //##Documentation
    //## standard cloning method. All arguments are ignored since this is a
    //## very basic object. Note that privatize is left unimplemented, as well.
      virtual CountedRefTarget* clone (int  = 0, int  = 0) const;
    //##ModelId=3DB964F3027D
      virtual int fromBlock (BlockSet& set);
    //##ModelId=3DB964F30297
      virtual int toBlock (BlockSet &set) const;
    //##ModelId=3DB964F302B0
      virtual TypeId objectType () const;

    //##ModelId=3DD3BEEF0147
    //##Documentation
    //## standard debug info method, depending on level includes:
    //## 0: class name & object address
    //## 1: # of defined columns and max columns
    //## 2: types and shapes of defined columns
      string sdebug ( int detail = 1,const string &prefix = "",
                      const char *name = 0 ) const;
      
    //##ModelId=3DB964F302CC
      DefineRefTypes(TableFormat,Ref);

  protected:
    // Additional Protected Declarations

  private:
    // Additional Private Declarations

  private:
    //##ModelId=3DB964F2003C
      typedef struct {
        TypeId type;
        int size,cellsize;
      } ColumnFormat;

    //##ModelId=3DB964F20040
      typedef vector<ColumnFormat> FormatVector;
    //##ModelId=3DB964F20049
      typedef vector<LoShape>  ShapesVector;

    //##ModelId=3DB964F30069
      static ColumnFormat nullColumn;

      // reference to cached datablock (for a fromBlock/toBlock operation)
    //##ModelId=3DB964F30077
      BlockRef block;
      // vector of column formats
    //##ModelId=3DB964F30087
      FormatVector cols;
      // vector of column shapes (for arrays columns)
    //##ModelId=3DB964F30099
      ShapesVector shapes;

      // declare typedefs for specific packers
    //##ModelId=3DB964F2004E
      typedef SeqPacker<FormatVector,BinPacker<ColumnFormat> > ColumnFormatPacker;
    //##ModelId=3DB964F20052
      typedef SeqPacker<ShapesVector,SeqPacker<LoShape> > ColumnShapePacker;
};

DefineRefTypes(TableFormat,TableFormatRef);

//##ModelId=3DB964F301D5
inline int TableFormat::maxcol () const
{
  return cols.size();
}

//##ModelId=3DB964F301D8
inline TypeId TableFormat::type (int icol) const
{
  return cols[icol].type;
}

//##ModelId=3DB964F301F1
inline int TableFormat::elsize (int icol) const
{
  return cols[icol].size;
}

//##ModelId=3DB964F3020B
inline int TableFormat::ndims (int icol) const
{
  return shapes[icol].size();
}

//##ModelId=3DB964F30224
inline int TableFormat::cellsize (int icol) const
{
  return cols[icol].cellsize;
}

//##ModelId=3DB964F3023E
inline const LoShape & TableFormat::shape (int icol) const
{
  return shapes[icol];
}


//##ModelId=3DB964F302B0
inline TypeId TableFormat::objectType () const
{
  return TpTableFormat;
}

#endif
