# This file is generated automatically -- do not edit
# Original file name: /home/oms/LOFAR/CEP/CPA/PSS4/MeqNodes/src/defrecs_MeqNodes.g
# Generated on Mon Nov 22 16:07:56 CET 2004

# Defines the default init records ("defrecs") for all the nodes in a 
# given package. This file is meant to be included inside a function that 
# fills out the defrecs.
# 
#
# ---------- class MeqMergeFlags
# generated from /home/oms/LOFAR/CEP/CPA/PSS4/MeqNodes/src/MergeFlags.h
#
r := _meqdefrec_map.MeqNode;
r::description := 'Merges (bitwise-ORs) the flags supplied by all its children. \
                   The output result is a copy of the first child\'s input result,  \
                   but all the flags are merged.';
r.flag_mask := -1;
r.flag_mask::description := 'Flag mask to apply during merge. -1 means full mask. This can \
                             be a single mask, or a vector of one mask per child.';
_meqdefrec_map.MeqMergeFlags := r;
#
# ---------- class MeqSelector
# generated from /home/oms/LOFAR/CEP/CPA/PSS4/MeqNodes/src/Selector.h
#
r := _meqdefrec_map.MeqNode;
r::description := 'A MeqSelector selects one or more results from the result set of its child. \
                   Must have exactly one child.';
r.index := [];
r.index::description := 'Indices (1-based) of results to be selected.';
_meqdefrec_map.MeqSelector := r;
#
# ---------- class MeqSolver
# generated from /home/oms/LOFAR/CEP/CPA/PSS4/MeqNodes/src/Solver.h
#
r := _meqdefrec_map.MeqNode;
r::description := '***UPDATE THIS*** \
                   Represents a solver, \
                   A MeqSolver can have an arbitrary number of children. \
                   Only the results from the children that are a MeqCondeq are used. \
                   The other children can be other solvers that wait for this solver \
                   to finish.';
r.num_step := 1  ;
r.num_step::description := 'number of iterations to do in a solve';
r.epsilon := 0;
r.epsilon::description := 'convergence criterium; not used at the moment';
r.usesvd := false;
r.usesvd::description := 'Use singular value decomposition in solver?';
r.parm_group := hiid('parm');
r.parm_group::description := 'HIID of the parameter group to use. ';
r.solvable := [=];
r.solvable::description := 'Command record which is sent up in the rider of the first request \
                            (as req.rider.<parm_group>). This is meant to set parms to solvable.  \
                            The simplest way to create this is by using meq.solvable_list(\"names\"),  \
                            which returns such a record, given a  vector of solvable parm names.  \
                            It is also possible to create more elaborate command records from scratch, \
                            if more sophisticated manipulation of state is required.';
_meqdefrec_map.MeqSolver := r;
#
# ---------- class MeqReqSeq
# generated from /home/oms/LOFAR/CEP/CPA/PSS4/MeqNodes/src/ReqSeq.h
#
r := _meqdefrec_map.MeqNode;
r::description := 'Forwards its request to all children in sequence (i.e. each child is   \
                   activated only after the previous child has returned). Returns the result \
                   of one designated child.';
r.result_index := 1;
r.result_index::description := 'Which child\'s result to return.';
_meqdefrec_map.MeqReqSeq := r;
#
# ---------- class MeqConstant
# generated from /home/oms/LOFAR/CEP/CPA/PSS4/MeqNodes/src/Constant.h
#
r := _meqdefrec_map.MeqNode;
r::description := 'Represents a constant node. A MeqConstant cannot have any children.';
r.value := 0.0  ;
r.value::description := 'value of constant - expected double/complex double scalar';
r.integrated := F  ;
r.integrated::description := 'if true, constant represents an integration -- result value will be  \
                              multiplied by cell size';
_meqdefrec_map.MeqConstant := r;
#
# ---------- class MeqComposer
# generated from /home/oms/LOFAR/CEP/CPA/PSS4/MeqNodes/src/Composer.h
#
r := _meqdefrec_map.MeqNode;
r::description := 'A MeqComposer concatenates the results of all its children  \
                   into a single result.';
r.contagious_fail := F;
r.contagious_fail::description := 'If true, then a fail in any child result causes the composer to generate \
                                   a complete fail -- i.e., a result composed entirely of fails. \
                                   If false (default), then fail vellsets from children are collected and  \
                                   passed along with valid vellsets.';
_meqdefrec_map.MeqComposer := r;
#
# ---------- class MeqParm
# generated from /home/oms/LOFAR/CEP/CPA/PSS4/MeqNodes/src/Parm.h
#
r := _meqdefrec_map.MeqNode;
r::description := 'Represents a parameter, either created on-the-fly (a default \
                   value must then be supplied), or read from a MEP database. \
                   A MeqParm cannot have any children.';
r.polcs := [=];
r.polcs::description := 'active polcs. One or more meqpolc() objects may be provided. These \
                         will be reused for subsequent requests if the domains match, or \
                         if the inf_domain or grow_domain attributes are specified.';
r.solve_polcs := [=];
r.solve_polcs::description := 'active solvable polcs. A single meqpolc() object may be provided. This \
                               will be reused for subsequent solvable requests if the domains match, or \
                               if the grow_domain attribute is specified.';
r.default := [=];
r.default::description := 'default polc. A meqpolc() object. This is used when an applicable \
                           polc is not found in the table, or a table is not provided.';
r.integrated := F  ;
r.integrated::description := 'if true, the parm represents an integration -- result value will be  \
                              multiplied by cell size';
r.table_name := '' ;
r.table_name::description := 'MEP table name. If empty, then the default parameter value is used';
r.parm_name := '' ;
r.parm_name::description := 'MEP parm name used to look inside the table. If empty, then the node  \
                             name is used instead.';
r.auto_save := F ;
r.auto_save::description := 'if T, then any updates to a polc are saved into the MEP table  \
                             automatically (for example, after each solve iteration). Default  \
                             behaviour is to only save when specified via a request rider (e.g., \
                             at the end of a solve).';
_meqdefrec_map.MeqParm := r;
