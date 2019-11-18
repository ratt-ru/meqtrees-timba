from Timba import parmtables

# open table
tab = parmtables.FastParmTable('test.fmep');

# this returns a list of all unique domains in the table. The "domain index"
# mentioned below is simply an offset into this list
domlist = tab.domain_list();
print("============ domains in table:",len(domlist));

# this returns a list of all available funklets in the table.
# each list element is a tuple of (name,domain_index,domain)
funklist = tab.funklet_list();
print("============ funklets in table:",len(funklist));
print(funklist[0]);

# This returns one funklet, given a parmname and a domain_index
# If funklet does not exist, returns None
fx = tab.get_funklet('x',0);
ffoo = tab.get_funklet('foo',0);
print("============ funklet x:",fx);
print("============ funklet foo:",ffoo);

# This returns all funklets for a given parmname that overlap a given domain
domain = domlist[0];
funks = tab.get_funklets_for_domain('x',domain);
print("============ overlapping funklets for 'x':",len(funks));
funks = tab.get_funklets_for_domain('foo',domain);
print("============ overlapping funklets for 'foo':",len(funks));

# Now let's open another table for writing (we can also modify test.fmep,
# but since its checked into subversion, that's a bad idea)
tab1 = parmtables.FastParmTable('test1.fmep');
print("============ domains in new table:",len(tab1.domain_list()));
print("============ funklets in new table:",len(tab1.funklet_list()));

# let's store some funklets
# First argument is a parmname, second argument is a funklet record (which
# always includes a domain)
tab1.put_funklet('y',tab.get_funklet('x',0));
tab1.put_funklet('y',tab.get_funklet('x',1));
tab1.put_funklet('z',tab.get_funklet('y',0));
tab1.put_funklet('z',tab.get_funklet('y',1));
print("============ domains in new table:",len(tab1.domain_list()));
print("============ funklets in new table:",len(tab1.funklet_list()));

# Now delete some funklets
# This deletes a funklet by parmname and domain index. Exception will
# be thrown if funklet doesn't exist
tab1.delete_funklet('y',0);
tab1.delete_funklet('y',1);
print("============ funklets in new table:",len(tab1.funklet_list()));
# This deletes all funklets for given parmname
tab1.delete_funklet('z');
print("============ funklets in new table:",len(tab1.funklet_list()));

