# This file is generated automatically -- do not edit
# Original file name: /home/oms/LOFAR/Timba/MeqServer/src/defrecs_MeqServer.g
# Generated on Mon Mar 21 16:12:24 CET 2005

# Defines the default init records ("defrecs") for all the nodes in a 
# given package. This file is meant to be included inside a function that 
# fills out the defrecs.
# 
#
# ---------- class MeqSink
# generated from /home/oms/LOFAR/Timba/MeqServer/src/Sink.h
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
r.output_col::description := 'tile column to write results to: DATA, PREDICT or RESIDUALS. \
                              If empty, then no output is generated.';
r.corr_index := [];
r.corr_index::description := 'Defines mappings from result planes to correlations. If empty, then \
                              a default one-to-one mapping is used. Otherwise, should contain one \
                              correlation index (1-based) per each result plane.';
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
# generated from /home/oms/LOFAR/Timba/MeqServer/src/Spigot.h
#
r := _meqdefrec_map.MeqNode;
r::description := 'A MeqSpigot is attached to a VisAgent data source, and represents \
                   one interferometer. For every matching VisCube::VTile at the input of the  \
                   source, it caches the visibility data. If a matching request is then \
                   received, it returns that data as the result (with one plane per \
                   correlation.) A MeqSpigot usually works in concert with a MeqSink, \
                   in that a sink is placed at the base of the tree, and generates  \
                   results matching the input data.  \
                   A MeqSpigot can have no children.';
r.station_1_index := 0;
r.station_1_index::description := 'Index (1-based) of first station comprising the interferometer';
r.station_2_index := 0;
r.station_2_index::description := 'Index (1-based) of second station comprising the interferometer';
r.input_col := 'DATA';
r.input_col::description := 'tile column to get result from: DATA, PREDICT or RESIDUALS. ';
r.flag_mask := -1;
r.flag_mask::description := 'Flags bitmask. This is AND-ed with the FLAGS column of the tile to  \
                             generate output VellSet flags. Use -1 for a full mask. If both  \
                             flag_mask and row_flag_mask are 0, no output flags will be generated.';
r.row_flag_mask := -1;
r.row_flag_mask::description := 'Row flags bitmask. This is AND-ed with the ROWFLAG column of the tile  \
                                 and added to the output VellSet flags. Use -1 for a full mask. If both \
                                 flag_mask and row_flag_mask are 0, no output flags will be generated.';
r.flag_bit := 1;
r.flag_bit::description := 'Vells flag bit. If non-0, overrides flag behaviour as follows: \
                            the FLAGS and ROWFLAG columns tile of the tile are AND-ed with flag_mask \
                            and row_flag_mask, respecitively, and the output is flagged with \
                            flag_bit wherever the result of this operation is not 0.';
_meqdefrec_map.MeqSpigot := r;
