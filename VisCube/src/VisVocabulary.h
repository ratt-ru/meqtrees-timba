//  VisVocabulary.h: defines various constants for visibility data
//
//  Copyright (C) 2002
//  ASTRON (Netherlands Foundation for Research in Astronomy)
//  P.O.Box 2, 7990 AA Dwingeloo, The Netherlands, seg@astron.nl
//
//  This program is free software; you can redistribute it and/or modify
//  it under the terms of the GNU General Public License as published by
//  the Free Software Foundation; either version 2 of the License, or
//  (at your option) any later version.
//
//  This program is distributed in the hope that it will be useful,
//  but WITHOUT ANY WARRANTY; without even the implied warranty of
//  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//  GNU General Public License for more details.
//
//  You should have received a copy of the GNU General Public License
//  along with this program; if not, write to the Free Software
//  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
//
//  $Id$
#ifndef VisCube_VisVocabulary_h
#define VisCube_VisVocabulary_h 1
    
#pragma aidgroup VisCube
#pragma aid UVData UVSet Row Raw Sorted Unsorted Time Timeslot Channel Num
#pragma aid Control MS Integrate Flag Exposure Receptor Antenna IFR
#pragma aid SPW Field UVW Data Integrated Point Source Segment Corr Name
#pragma aid Header Footer Patch XX YY XY YX Chunk Indexing Index
#pragma aid Subtable Type Station Mount Pos Offset Dish Diameter
#pragma aid Feed Interval Polarization Response Angle Ref Freq Width
#pragma aid Bandwidth Effective Resolution Total Net Sideband
#pragma aid IF Conv Chain Group Data Desc Polarization Code Poly Delay
#pragma aid Dir Phase Pointing Lines Calibration Group Proper Motion Sigma Weight
#pragma aid Origin Target Tracking Beam Product Meas Centroid
#pragma aid AIPSPP Ignore VDSID Data Type

#include <DMI/HIID.h>
#include <VisCube/AID-VisCube.h>
    
namespace VisVocabulary
{
  static int dummy = aidRegistry_VisCube();
  
  const HIID 
    FVDSID          = AidVDSID,
    
    FDataType       = AidData|AidType,
      
    FUVSetIndex     = AidUVSet|AidIndex,
    FPatchIndex     = AidPatch|AidIndex,
    FSegmentIndex   = AidSegment|AidIndex,
    FFieldIndex     = AidField|AidIndex,
    FFieldName      = AidField|AidName,
    FSourceName     = AidSource|AidName,
    FCorr           = AidCorr,
    FCorrName       = AidCorr|AidName,
    FNumTimeslots   = AidNum|AidTimeslot,
    FNumChannels    = AidNum|AidChannel,
    FNumBaselines   = AidNum|AidIFR,
    FChunkIndexing  = AidChunk|AidIndexing,

    FName           = AidName,
    FRowIndex       = AidRow|AidIndex,
    FRowFlag        = AidRow|AidFlag,
    FTimeSlotIndex  = AidTimeslot|AidIndex,
    FTime           = AidTime,
    FExposure       = AidExposure,
    FInterval       = AidInterval,
    FTimeCentroid   = AidTime|AidCentroid,
    FSigma          = AidSigma,
    FWeight         = AidWeight,
    FReceptorIndex  = AidReceptor|AidIndex,
    FAntennaIndex   = AidAntenna|AidIndex,
    FIFRIndex       = AidIFR|AidIndex,
    FSPWIndex       = AidSPW|AidIndex,
    FUVW            = AidUVW,
    FData           = AidData,
    FDataFlag       = AidData|AidFlag,
    FNumIntTimes    = AidNum|AidIntegrated|AidTimeslot,
    FNumIntPixels   = AidNum|AidIntegrated|AidPoint,
    FRowIndexing    = AidRow|AidIndexing,

    FAipsMSName     = AidAIPSPP|AidMS|AidName,
    
// field names for Antenna subtable
    FAntennaSubtable = AidAntenna|AidSubtable,
    FStationName     = AidStation|AidName,
    FType            = AidType,
    FMount           = AidMount,
    FPosition        = AidPos,
    FOffset          = AidOffset,
    FDishDiameter    = AidDish|AidDiameter,

// field names for Pointing subtable
    FPointingSubtable = AidPointing|AidSubtable,
    // FAntennaIndex, FTime, FName, FInterval already defined
    FNumPoly          = AidNum|AidPoly,
    FTimeOrigin       = AidTime|AidOrigin,
    FDirection        = AidDir,
    FTarget           = AidTarget,
    FTracking         = AidTracking,

// field names for Feed subtable
     FFeedSubtable    = AidFeed|AidSubtable,
     // FAntennaIndex, FTime, FInterval, FPosition, FNumRecptors already defined
     FNumReceptors    = AidNum|AidReceptor,
     FFeedIndex       = AidFeed|AidIndex,
     FBeamIndex       = AidBeam|AidIndex,
     FBeamOffset      = AidBeam|AidOffset,
     FPolznType       = AidPolarization|AidType,
     FPolznResponse   = AidPolarization|AidResponse,
     FReceptorAngle   = AidReceptor|AidAngle,
    
// Field names for Polarization subtable
    FPolarizationSubtable = AidPolarization|AidSubtable,
    FCorrType         = AidCorr|AidType,
    FCorrProduct      = AidCorr|AidProduct,
//      FCorr, FFlagRow - already defined

// Field names for SpectralWindow subtable
    FSPWSubtable     = AidSPW|AidSubtable,
    FRefFreq         = AidRef|AidFreq,
//    FNumChannels already defined
    FChannelFreq     = AidChannel|AidFreq,
    FChannelWidth    = AidChannel|AidWidth,
    FMeasFreqRef     = AidMeas|AidFreq|AidRef,
    FEffectiveBW     = AidEffective|AidBandwidth,
    FResolution      = AidResolution,
    FTotalBW         = AidTotal|AidBandwidth,
    FNetSideband     = AidNet|AidSideband,
    FIFConvChain     = AidIF|AidConv|AidChain,
    FFreqGroup       = AidFreq|AidGroup,
    FFreqGroupName   = AidFreq|AidGroup|AidName,
    
// Field names for SOURCE subtable
    FSourceSubtable   = AidSource|AidSubtable,
    FSourceIndex      = AidSource|AidIndex,
    // FName, FTime, FInterval, FSPWIndex already defined
    FNumLines         = AidNum|AidLines,
    FCalibrationGroup = AidCalibration|AidGroup,
    FCode             = AidCode,
    // FDirection, FPosition already defined
    FProperMotion     = AidProper|AidMotion,

// Field names for Data Description subtable
    FDataDescriptionSubtable = AidData|AidDesc|AidSubtable,
    // FSPWIndex defined above
    FPolarizationIndex = AidPolarization|AidIndex,
    
// Field  names for Field subtable
    FFieldSubtable      = AidField|AidSubtable,
    // FCode, FTime, FNumPoly already defined
    FDelayDirMeas       = AidDelay|AidDir|AidMeas,
    FPhaseDirMeas       = AidPhase|AidDir|AidMeas,
    FRefDirMeas         = AidRef|AidDir|AidMeas,
    // FSourceIndex already defined
    
    // this lets us end the list above with a comma
    __last_field_declaration;

  
  
    typedef int FlagType;
    // flag value for missing data
    const int FlagMissing = 0xFFFFFFFF;


// small function for converting antennas to flat IFR indices    
//    when ant1 < ant2, we always get odd numbers
//    when ant1 >= ant2, we always get even numbers 
// and, ifr(a1,a2)/2 = ifr(a2,a1)/2
    inline int ifrNumber ( int ant1,int ant2 ) 
    {
      return ant1 < ant2
              ? ifrNumber(ant2,ant1) + 1
              : 2*( ant1*(ant1+1)/2 + ant2 );
    }

};

#endif 
