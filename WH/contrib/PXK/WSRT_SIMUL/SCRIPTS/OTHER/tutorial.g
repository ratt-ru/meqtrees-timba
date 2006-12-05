Glish tutorial - arrays, records, events 
---------------------------------------

Glish is

   1) A vector-oriented scripting language somewhat like perl.  It includes
      GUI building capabilities based on tcl/tk.

   2) A system for building loosely-coupled distributed systems, it's like
      a glue for coordinating independent "client" processes and mediating
      communication between them.  The client processes may be written as
      Glish scripts or C++ programs.


Quick intro to Glish from a user's rather than programmer's perspective but
assuming familiarity with basic programming constructs.

Glish data types:

   Numeric              Non-numeric
   -------              -----------
   boolean              string
   byte                 record
   short                function
   integer              agent
   float                reference
   double               fail
   complex              file
   dcomplex             regex

Glish also has the usual programming constructs: loops, conditionals,
functions, etc.  Details available from the Glish programming manual
http://www.atnf.csiro.au/aips++/docs/reference/Glish/Glish.html.



1) Arrays (actually vectors)

Glish is vector-oriented language, most operations work the same way for
vectors and scalars.

Arrays are multidimensional vectors - not particularly important.  Will
concentrate on vectors.

grus-201% glish
Glish version 2.6. 

- v := [T,T,F,T,F]      # Dynamically creates boolean vector of length 5

- print v               # Print the value of v

[T T F T F]             

- v                     # Implicit print - only in interactive mode

[T T F T F]


- length(v)             # Print the number of elements

5

- v[3]                  # Print the 3rd element

F

- v[3] := 4             # Sets v[3] and casts the WHOLE vector to integer type

- v

[1 1 4 1 0]


- 3:5                   # 3:5 is shorthand for [3,4,5]

[3 4 5]

- v[3:5]                # Subarray indexing: 3rd, 4th, and 5th element

[4 1 0]

- f := v[3,4,5]         # Syntax error!  Generates a "fail" value

warning, v[3, 4, 5] invalid array addressing


- f                     # f contains a "fail" value




- pi * [0.5, 1.0, 1.5, 2.0]^2

[0.785398 3.14159 7.06858 12.5664]

- print x := [1:4]

[1 2 3 4]


- s := 'glish'          # String assignment

string

- s[2:3] := "is swish"  # String vector shorthand - "..."

- s

glish is swish          # Note, vector notation missing - aaargh!


- print a := [1:3, 4:6] # Creates a vector.

[1 2 3 4 5 6]

- print b := [1:8]      # Create a vector of length 6

[1 2 3 4 5 6 7 8]



2) Records

Vectors are homogeneous, all elements are the same type.

Records are data structures, similar to C structs.


grus-201% glish
Glish version 2.6.

- r := [=];            # Empty record
- r.a := 'abc'
- r.b := [1,2,3]
- r.c := [=];          # Subfield is also a record
- r.c.a := 'x'
- r.c.b := pi
- print r
[a=abc, b=[1 2 3] , c=[a=x, b=3.14159]] 

- r.b[2]

2

- r.c

[a=x, b=3.14159] 


- field_names(r)        # Get record field names

a b c

- has_field(r, 'c')     # Does the record have this field?

T

- length(r)             # How many fields does it have?

3


3) Events

Glish has "agent" variables which respond to events.


grus-201% glish
Glish version 2.6.

- f := frame()                          # Create window


- b := button(f, 'Press me!')           # Create button

- l := label(f, '', fill='x', relief='ridge')

- whenever b->press do { l->text('Not so hard!') }

- f := frame(side='left')               # Destroy old frame and create new

- b1 := button(f, 'B1', value=1)

- b2 := button(f, 'B2', value=2)

- b2.name := 'B2'                       # Add a name into the agent record

- whenever b1->press, b2->press do { print $name, $value, $agent }
