# This file is generated automatically -- do not edit
# Original file name: /home/oms/LOFAR/Timba/MeqNodes/src/defrecs_MeqNodes.g
# Generated on Mon Apr 18 23:26:03 CEST 2005

# Defines the default init records ("defrecs") for all the nodes in a 
# given package. This file is meant to be included inside a function that 
# fills out the defrecs.
# 
#
# ---------- class MeqTranspose
# generated from /home/oms/LOFAR/Timba/MeqNodes/src/Transpose.h
#
r := _meqdefrec_map.MeqNode;
r::description := 'A MeqTranspose tranposes a matrix. Only one child is expected. The child \
                   must return a tensor rank <=2 result. Matrices are transposed, vectors \
                   are turned into a 1xN tensor, and scalars pass through unchanged.';
r.conj := F;
r.conj::description := 'If true, does a complex transpose-and-conjugate operation.';
_meqdefrec_map.MeqTranspose := r;
#
# ---------- class MeqSelector
# generated from /home/oms/LOFAR/Timba/MeqNodes/src/Selector.h
#
r := _meqdefrec_map.MeqNode;
r::description := 'A MeqSelector selects one or more results from the result set of its child. \
                   Must have exactly one child.';
r.index := [];
r.index::description := 'Index (1-based) of results to be selected. If more than one index is \
                         supplied, it is interpreted according to the \'multi\' field below.';
r.multi := F;
r.multi::description := 'If false (default): a multiple-element index is treated as a tensor index  \
                           that selects a single element or a slice. Child result must be a tensor  \
                           of the same rank as there are elements in \'index\'. A \'-1\' at \
                           any position in \'index\' indicates a slice along the corresponding axis. \
                         If true: a multiple-element index is treated as a set of scalar indices,  \
                           and the corresponding number of output vellsets is produced.';
_meqdefrec_map.MeqSelector := r;
#
# ---------- class MeqSolver
# generated from /home/oms/LOFAR/Timba/MeqNodes/src/Solver.h
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
# ---------- class MeqComposer
# generated from /home/oms/LOFAR/Timba/MeqNodes/src/Composer.h
#
r := _meqdefrec_map.MeqNode;
r::description := 'A MeqComposer concatenates the results of all its children  \
                   into a single result.';
r.dims := F;
r.dims::description := 'If specified, a vector of tensor dimensions to compose a tensor \
                        result.';
r.contagious_fail := F;
r.contagious_fail::description := 'If true, then a fail in any child result causes the composer to generate \
                                   a complete fail -- i.e., a result composed entirely of fails. \
                                   If false (default), then fail vellsets from children are collected and  \
                                   passed along with valid vellsets.';
_meqdefrec_map.MeqComposer := r;
#
# ---------- class MeqReqSeq
# generated from /home/oms/LOFAR/Timba/MeqNodes/src/ReqSeq.h
#
r := _meqdefrec_map.MeqNode;
r::description := 'Forwards its request to all children in sequence (i.e. each child is   \
                   activated only after the previous child has returned). Returns the result \
                   of one designated child.';
r.result_index := 1;
r.result_index::description := 'Which child\'s result to return.';
_meqdefrec_map.MeqReqSeq := r;
#
# ---------- class MeqParm
# generated from /home/oms/LOFAR/Timba/MeqNodes/src/Parm.h
#
r := _meqdefrec_map.MeqNode;
r::description := 'Represents a parameter, either created on-the-fly (a default \
                   value must then be supplied), or read from a MEP database. \
                   A MeqParm cannot have any children.';
r.funklet := [=];
r.funklet::description := 'active funklet. A funklet object (e.g. meq.polc()) may be provided.  \
                           This will be reused for subsequent requests if the domains match, or \
                           if no domain is specified.';
r.default := [=];
r.default::description := 'default funklet. A funklet object (e.g. meq.polc()) may be provided.  \
                           This is used when an applicable funklet is not found in the table, or  \
                           a table is not provided.';
r.integrated := F  ;
r.integrated::description := 'if true, the parm represents an integration -- result value will be  \
                              multiplied by cell size';
r.table_name := '' ;
r.table_name::description := 'MEP table name. If empty, then the default parameter value is used';
r.parm_name := '' ;
r.parm_name::description := 'MEP parm name used to look inside the table. If empty, then the node  \
                             name is used instead.';
r.auto_save := F ;
r.auto_save::description := 'if T, then any updates to a funklet are saved into the MEP table  \
                             automatically (for example, after each solve iteration). Default  \
                             behaviour is to only save when specified via a request rider (e.g., \
                             at the end of a solve).';
_meqdefrec_map.MeqParm := r;
#
# ---------- class MeqConstant
# generated from /home/oms/LOFAR/Timba/MeqNodes/src/Constant.h
#
r := _meqdefrec_map.MeqNode;
r::description := 'Represents a constant node. A MeqConstant cannot have any children.';
r.value := 0.0  ;
r.value::description := 'value of constant - double or complex double scalar or array (if array \
                         is used, a tensor will be returned)';
r.vells := F  ;
r.vells::description := 'variable constant (ugly hack) - expected double or complex double array. \
                         Subsequent request cells must have the same shape.';
r.integrated := F  ;
r.integrated::description := 'if true, constant represents an integration -- result value will be  \
                              multiplied by cell size';
_meqdefrec_map.MeqConstant := r;
#
# ---------- class MeqPaster
# generated from /home/oms/LOFAR/Timba/MeqNodes/src/Paster.h
#
r := _meqdefrec_map.MeqNode;
r::description := 'A MeqPaster \"pastes\" the result of its second child (Result2) at the  \
                   selected position in the result of the first child (Result1).';
r.index := [];
r.index::description := 'Index (1-based) of position(s) to paste at. If more than one index is \
                         supplied, it is interpreted according to the \'multi\' field below. Note \
                         that the semantics of the selection match those of the MeqSelector node.';
r.multi := F;
r.multi::description := 'If false (default): a multiple-element index is treated as a tensor index  \
                           that selects a single element or a slice. Result1 must  be a tensor  \
                           of the same rank as there are elements in \'index\'. A \'-1\' at \
                           any position in \'index\' indicates a slice along the corresponding axis. \
                           Result2 must have the same dimensions/rank as the selected slice. \
                         If true: a multiple-element index is treated as a set of  scalar indices. \
                           Result2 must have the same number of vellsets as there are elements in \
                           \'index\', and they are pasted at the indicated positions.';
_meqdefrec_map.MeqPaster := r;
#
# ---------- class MeqMergeFlags
# generated from /home/oms/LOFAR/Timba/MeqNodes/src/MergeFlags.h
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
# ---------- class MeqZeroFlagger
# generated from /home/oms/LOFAR/Timba/MeqNodes/src/ZeroFlagger.h
#
r := _meqdefrec_map.MeqNode;
r::description := 'Sets flags in a VellSet based on a comparison of the main value with 0.';
r.oper := hiid('ne');
r.oper::description := 'logical operator to use (HIID or string). One of: EQ NE GE LE GT LT, \
                        for == != >= <= < >. ';
r.flag_bit := 1;
r.flag_bit::description := 'this value is ORed with the flags at all points where the  \
                            main value OPER 0 is true.';
r.force_output := F;
r.force_output::description := 'normally, if nothing at all is flagged, no dataflags at all are generated. \
                                Set this to true to generate a null flags entry.';
_meqdefrec_map.MeqZeroFlagger := r;
