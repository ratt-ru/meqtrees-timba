// -----------------------------------------------------------------------
// access as STL vectors 
// -----------------------------------------------------------------------

// some out-of-line templates for hooks
// Define an get_vector<> template. This should work for all
// contiguous containers.
// This copies data so is not very efficient, but is quite
// convenient where sizes are small.
template<class T>
bool NestableContainer::Hook::get_vector (std::vector<T> &value,bool must_exist) const
{
  int n;
  const T *data = as_po(n,Type2Type<T>());
  if( !data )
    return False;
  value.resize(n);
  value.assign(data,data+n);
  return True;
}

// -----------------------------------------------------------------------
// assignment of Lorrays
// this will create a new DataArray object, or else assign to the underlying
// array. Note the void return type -- we may not have an array object to
// return at all (i.e. when the underlying data is not held in an Array)
// -----------------------------------------------------------------------
template<class T,int N> 
void NestableContainer::Hook::operator = (const blitz::Array<T,N> &other) const
{
  bool haveArray;
  void * target = prepare_assign_array(haveArray,typeIdOf(T),other.shape());
  if( !target )             // no object - create new field
  {
    ObjRef ref(new DataArray(other,DMI::WRITE),DMI::ANONWR);
    assign_objref(ref,0);
  }
  else if( haveArray )       // got array object - use assignment
  {
    blitz::Array<T,N> *pdest = static_cast<blitz::Array<T,N>*>(target);
    if( pdest->shape() != other.shape() )
      ThrowExc(ConvError,"can't assign array: shape mismatch");
    (*pdest) = other;
  }
  else                      // got pointer to data - use flat copy
  {
    blitz::Array<T,N> dest(static_cast<T*>(target),other.shape(),blitz::neverDeleteData);
    dest = other;
  }
}

// -----------------------------------------------------------------------
// assign_sequence
// helper function to assign sequences of non-arrayable types
// -----------------------------------------------------------------------
template<class T,class Iter> 
void NestableContainer::Hook::assign_sequence(uint size,Iter begin,Iter end,Type2Type<T>) const
{ 
  const int tid = DMITypeTraits<T>::typeId;
  T * ptr = static_cast<T*>( assign_vector(tid,size) ); 
  for( ; begin != end; begin++ )
    *ptr++ = *begin; 
}


