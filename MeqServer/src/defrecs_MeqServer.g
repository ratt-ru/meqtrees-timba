# This file is generated automatically -- do not edit
# Original file name: /home/oms/alt/LOFAR/Timba/MeqServer/src/defrecs_MeqServer.g
# Generated on Mon Jan  2 18:18:05 CET 2006

# Defines the default init records ("defrecs") for all the nodes in a 
# given package. This file is meant to be included inside a function that 
# fills out the defrecs.
# 
#
# ---------- class MeqSink
# generated from /home/oms/alt/LOFAR/Timba/MeqServer/src/Sink.h
#
r := _meqdefrec_map.MeqNode;
r::description := 'A MeqSink is attached to a VisAgent data source. A MeqSink represents \
                   one interferometer. For every matching VisCube::VTile at the input of the  \
                   source, it generates a MeqRequest corresponding to the domain/cells  \
                   of the tile, and optionally stores the result back in the tile. \
                   A MeqSink must have exactly one child. The child may return a  \
                   multi-plane result.';
r.station_1_index := 0;
r.station_1_index::description := 'Index (1-based) of first station comprising the interferometer';
r.station_2_index := 0;
r.station_2_index::description := 'Index (1-based) of second station comprising the interferometer';
r.output_col := '';
r.output_col::description := 'tile column to write results to: DATA, PREDICT or RESIDUALS for  \
                              correlation data, but other columns may be used too, \
                              If empty, then no output is generated.';
r.corr_index := [];
r.corr_index::description := 'Defines mappings from result vellsets to correlations. If empty, then \
                              a default one-to-one mapping is used, and an error will be thrown if \
                              sizes mismatch. Otherwise, should contain one correlation index (1-based)  \
                              per each vellset (0 to ignore that vellset). Note that tensor  \
                              results are decomposed in row-major order, [[1,2],[3,4]].';
r.flag_mask := 0;
r.flag_mask::description := 'If non-0, then any data flags in the result are ANDed with this mask \
                             and written to the FLAGS column of the output tile. If 0, then no \
                             tile flags are generated. Use -1 for a full flag mask.';
r.flag_bit := ;
r.flag_bit::description := 'Output flag bit. If non-0, overrides flag behaviour as follows: \
                            the dataflags are AND-ed with flag_mask, and the output is flagged with \
                            flag_bit wherever the result of this operation is not 0.';
_meqdefrec_map.MeqSink := r;
#
# ---------- class MeqSpigot
# generated from /home/oms/alt/LOFAR/Timba/MeqServer/src/Spigot.h
#
r := _meqdefrec_map.MeqNode;
r::description := 'A MeqSpigot is attached to a VisAgent data source, and represents \
                   one interferometer. For every matching VisCube::VTile at the input of the  \
                   source, it caches the visibility data. If a matching request is then \
                   received, it returns that data as the result (with one plane per \
                   correlation.) A MeqSpigot usually works in concert with a MeqSink, \
                   in that a sink is placed at the base of the tree, and generates  \
                   results matching the input data.  \
                   A MeqSpigot can have no children. \
                   field input_col \"DATA\" \
                   Gives the tile column from which data is to be read. Note that any double \
                   or fcomplex tile column can be used (i.e. WEIGHT and SIGMA and such, not \
                   just DATA, PREDICT and RESIDUALS, which contain correlations).  \
                   1D columns produce a time-variable vells in the result, matrix columns  \
                   produce a time-freq variable vells in the result, and cubic columns can  \
                   produce a tensor result with multiple vells.  \
                   In the latter case, the dims and corr_index fields come into play, \
                   telling the spigot how to decompose the \"correlation\" axis into a tensor, \
                   as well as the flag_mask and row_flag_mask fields, to set flags. In the \
                   case of 1D or 2D columns, flags are ignored (NB: in the future, we may \
                   support row flags for these columns).';
r.dims := [2,2];
r.dims::description := 'For 3D tile columns only. \
                        Tensor dimensions of result. Set to [1] for a scalar result,  \
                        [n] for a vector result, etc. Default is [2,2] (a canonical coherency \
                        matrix).';
r.corr_index := [1,2,3,4];
r.corr_index::description := 'For 3D tile columns only. \
                              A vector of four indices telling how to map output vellsets to \
                              the correlation axis in the tile column. A tensor result is \
                              composed in row-major order, e.g. a 2x2 matrix is composed as  \
                              [[C1,C2],[C3,C4]], where Ci is the correlation column given by corr_index[i]. \
                              For example, the canonical form of a coherency matrix is [[xx,xy],[yx,yy]].  \
                              Therefore, if the correlation axis of the tile is ordered as XX XY YX YY,  \
                              then corr_index should be set to [1,2,3,4]. If the correlation axis \
                              contains XX YY only, corr_index should be set to [1,0,0,2].';
r.station_1_index := 0;
r.station_1_index::description := 'Index (1-based) of first station comprising the interferometer';
r.station_2_index := 0;
r.station_2_index::description := 'Index (1-based) of second station comprising the interferometer';
r.flag_mask_ := -1;
r.flag_mask_::description := 'For 3D tile columns only. \
                              Flags bitmask. This is AND-ed with the FLAGS column of the tile to  \
                              generate output VellSet flags. Use -1 for a full mask. If both  \
                              flag_mask_ and row_flag_mask_ are 0, no output flags will be generated.';
r.row_flag_mask_ := -1;
r.row_flag_mask_::description := 'For 3D tile columns only. \
                                  Row flags bitmask. This is AND-ed with the ROWFLAG column of the tile  \
                                  and added to the output VellSet flags. Use -1 for a full mask. If both \
                                  flag_mask_ and row_flag_mask_ are 0, no output flags will be generated.';
r.flag_bit_ := 1;
r.flag_bit_::description := 'For 3D tile columns only. \
                             Vells flag bit. If non-0, overrides flag behaviour as follows: \
                             the FLAGS and ROWFLAG columns tile of the tile are AND-ed with flag_mask_ \
                             and row_flag_mask_, respecitively, and the output is flagged with \
                             flag_bit_ wherever the result of this operation is not 0.';
_meqdefrec_map.MeqSpigot := r;
