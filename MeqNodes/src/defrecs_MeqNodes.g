# This file is generated automatically -- do not edit
# Original file name: /home/oms/LOFAR/CEP/CPA/PSS4/MeqNodes/src/defrecs_MeqNodes.g
# Generated on Thu Sep  9 20:33:05 CEST 2004

# Defines the default init records ("defrecs") for all the nodes in a 
# given package. This file is meant to be included inside a function that 
# fills out the defrecs.
# 
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
# ---------- class MeqResampler
# generated from /home/oms/LOFAR/CEP/CPA/PSS4/MeqNodes/src/Resampler.h
#
r := _meqdefrec_map.MeqNode;
r::description := 'Resamples the Vells in its child\'s Result to the Cells of the parent\'s \
                   Request. Current version ignores cell centers, sizes, domains, etc., \
                   and goes for a simple integrate/expand by an integer factor.';
r.flag_mask := -1;
r.flag_mask::description := 'Flag mask applied to child\'s result. -1 for all flags, 0 to ignore  \
                             flags. Flagged values are ignored during integration.';
r.flag_bit := 0;
r.flag_bit::description := 'Flag bit(s) used to indicate flagged integrated results. If 0, then  \
                            flag_mask&input_flags is used.';
r.flag_density := 0.5;
r.flag_density::description := 'Critical ratio of flagged/total pixels for integration. If this ratio \
                                is exceeded, the integrated pixel is flagged.';
_meqdefrec_map.MeqResampler := r;
#
# ---------- class MeqModRes
# generated from /home/oms/LOFAR/CEP/CPA/PSS4/MeqNodes/src/ModRes.h
#
r := _meqdefrec_map.MeqNode;
r::description := '***UPDATE THIS*** \
                   Changes the resolution of a parent\'s Request before passing it on to the \
                   child. Returns child result as is. Expects exactly one child.';
r.factor := [];
r.factor::description := 'If specified, changes the resolution by a fixed resampling factor.  \
                          Must be a vector of 2 values (frequency axis, time axis), or a single  \
                          value (for both axes). A value <-1 corresponds to integrating by -factor; a  \
                          value of >1 corresponds to upsampling by factor. A value of 0/1 leaves the  \
                          resolution along that axis unchanged. \
                          Currently, only integer refactorings are supported, so the node will fail \
                          if factor<-1 (i.e. integration) is not an integer factor of the original \
                          request\'s resolution.';
r.num_cells := [];
r.num_cells::description := 'If specified, changes the number of cells along each axis.  \
                             Must be a vector of 2 values (frequency axis, time axis), or a single  \
                             value (for both axes). A value of 0 leaves the resolution along that axis \
                             unchanged (resampling factor will still be applied, if specified); a  \
                             value >0 changes the number of cells and overrides the resampling factor  \
                             (if specified). \
                             Currently, only integer refactorings are supported, so the node will fail \
                             if num_cells is not a multiple or a factor of the original request\'s  \
                             resolution.';
_meqdefrec_map.MeqModRes := r;
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
# ---------- class MeqZeroFlagger
# generated from /home/oms/LOFAR/CEP/CPA/PSS4/MeqNodes/src/ZeroFlagger.h
#
r := _meqdefrec_map.MeqNode;
r::description := 'Sets flags in a VellSet based on a comparison of the main value with 0.';
r.oper := hiid('ne');
r.oper::description := 'logical operator to use (HIID or string). One of: EQ NE GE LE GT LT, \
                        for == != >= <= < >. ';
r.flag_bit := 1;
r.flag_bit::description := 'this value is ORed with the flags at all points where the  \
                            main value OPER 0 is true.';
_meqdefrec_map.MeqZeroFlagger := r;
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
