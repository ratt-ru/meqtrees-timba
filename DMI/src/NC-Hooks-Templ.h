// -----------------------------------------------------------------------
// access as STL vectors 
// -----------------------------------------------------------------------
// some out-of-line templates for hooks
// Define an as_vector<> template. This should work for all
// contiguous containers.
// This copies data so is not very efficient, but is quite
// convenient where sizes are small.
template<class T>
std::vector<T> NestableContainer::ConstHook::as_vector (Type2Type<T>) const
{
  int n;
  const T *data = as_p(n,Type2Type<T>());
  return std::vector<T>(data,data+n);
}

// second version provides a default value
template<class T>
std::vector<T> NestableContainer::ConstHook::as_vector (const std::vector<T> &deflt) const
{
  ContentInfo info;
  const T * ptr = as_impl_p(&deflt[0],info,True);
  return ptr == &deflt[0] ? deflt : std::vector<T>(ptr,ptr+info.size);
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
    FailWhen(pdest->shape() != other.shape(),"can't assign array: shape mismatch");
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
  T * ptr = static_cast<T*>( prepare_vector(tid,size) ); 
  for( ; begin != end; begin++ )
    *ptr++ = *begin; 
}


