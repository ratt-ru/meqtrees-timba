//#  MeqVocabulary.h: provide some standard field names
//#
//#  Copyright (C) 2002-2003
//#  ASTRON (Netherlands Foundation for Research in Astronomy)
//#  P.O.Box 2, 7990 AA Dwingeloo, The Netherlands, seg@astron.nl
//#
//#  This program is free software; you can redistribute it and/or modify
//#  it under the terms of the GNU General Public License as published by
//#  the Free Software Foundation; either version 2 of the License, or
//#  (at your option) any later version.
//#
//#  This program is distributed in the hope that it will be useful,
//#  but WITHOUT ANY WARRANTY; without even the implied warranty of
//#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//#  GNU General Public License for more details.
//#
//#  You should have received a copy of the GNU General Public License
//#  along with this program; if not, write to the Free Software
//#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
//#
//#  $Id$

#ifndef MEQ_VOCABULARY_H
#define MEQ_VOCABULARY_H

#include <MEQ/AID-Meq.h>


#pragma aidgroup Meq
#pragma aid Node Class Name State Child Children Request Result VellSet 
#pragma aid Rider Command Id Group Add Update Value Values Solve Solver
#pragma aid Dependency Resolution Depend Mask Resample Integrated
#pragma aid Cells Domain Freq Time Calc Deriv Vells VellSets Flags Weights
#pragma aid Shape Grid Cell Size Segments Start End Steps Axis Axes Offset
#pragma aid NodeIndex Table Name Default Index Num Cache Code 
#pragma aid Parm Spid Coeff Perturbed Perturbations Names Pert Relative Mask
#pragma aid Cell Results Fail Origin Line Message Contagious  Normalized
#pragma aid Solvable Config Groups All By List Polc Polcs Scale Matrix
#pragma aid DbId Grow Inf Weight Epsilon UseSVD Set Auto Save Clear Invert
#pragma aid Metrics Rank Fit Errors CoVar Flag Bit Mu StdDev Chi Iter Last Update


namespace Meq
{
  const HIID 
      
    FRequestId       = AidRequest|AidId,
    FCells           = AidCells,
    FCalcDeriv       = AidCalc|AidDeriv,
    FClearSolver     = AidClear|AidSolver,
    FRider           = AidRider,
    FNodeName        = AidNode|AidName,
    FNodeState       = AidNode|AidState,
    FClass           = AidClass,
    FClassName       = AidClass|AidName,
    FVellSets        = AidVellSets,
    FResult          = AidResult,
    FRequest         = AidRequest,
    FState           = AidState,
    
    // Node staterec
    FChildren           = AidChildren,
    FChildrenNames      = AidChildren|AidName,
    FName               = AidName,
    FNodeIndex          = AidNodeIndex,
    FNodeGroups         = AidNode|AidGroups,
//    FDependMask         = AidDepend|AidMask,
    FAutoResample       = AidAuto|AidResample, 
    
    // Request rider fields (for commands)
//    FAll                = AidAll,
    FCommandAll         = AidCommand|AidAll,
    FCommandByNodeIndex = AidCommand|AidBy|AidNodeIndex,
    FCommandByList      = AidCommand|AidBy|AidList,
    
    FCacheResult     = AidCache|AidResult,
    FCacheResultCode = AidCache|AidResult|AidCode,
    
    // Domain fields
    FFreq            = AidFreq,
    FTime            = AidTime,
    
    // Cells fields
    FDomain          = AidDomain,
    FGrid            = AidGrid,
    FCellSize        = AidCell|AidSize,
    FSegments        = AidSegments,
    FStartIndex      = AidStart|AidIndex,
    FEndIndex        = AidEnd|AidIndex,
    
    // Parm staterec fields
    FDefault         = AidDefault,
    FTableName       = AidTable|AidName,
    FParmName        = AidParm|AidName,
    FAutoSave        = AidAuto|AidSave,
    FDomainId        = AidDomain|AidId,
    FSolveDomainId   = AidSolve|AidDomain|AidId,
    
    
    // FDomain      defined previously
    FSolveDomain     = AidSolve|AidDomain,
    FPolcs           = AidPolcs,
    FSolvePolcs      = AidSolve|AidPolcs,
    
    // Parm rider commands
    FUpdateValues    = AidUpdate|AidValues,
    FSavePolcs       = AidSave|AidPolcs,
    FClearPolcs      = AidClear|AidPolcs,
    
    // Parm/Polc fields
    FCoeff           = AidCoeff,
    FAxisIndex       = AidAxis|AidIndex,
    FOffset          = AidOffset,
    FScale           = AidScale,
    FPerturbation    = AidPert,
    FWeight          = AidWeight,
    FPertRelative    = AidPert|AidRelative,
    FGrowDomain      = AidGrow|AidDomain,
    FInfDomain       = AidInf|AidDomain,
    FDbId            = AidDbId|AidIndex,
    
    // VellSet fields
    FShape           = AidShape,
    FIntegrated      = AidIntegrated, 
    FValue           = AidValue,
    FFlags           = AidFlags,
    FWeights         = AidWeights,
    FSpids           = AidSpid|AidIndex,
    FPerturbedValues = AidPerturbed|AidValue,
    FPerturbations   = AidPerturbations,

    // Fail fields
    FFail            = AidFail,
    FOrigin          = AidOrigin,
    FOriginLine      = AidOrigin|AidLine,
    FMessage         = AidMessage,

    // Solver staterec fields
    FSolvable        = AidSolvable,
    FParmGroup       = AidParm|AidGroup,
    // Solver staterec fields and commands
    FEpsilon         = AidEpsilon,
    FUseSVD          = AidUseSVD,
    FClearMatrix     = AidClear|AidMatrix,
    FInvertMatrix    = AidInvert|AidMatrix,
    FNumIter         = AidNum|AidIter,
    // FSavePolcs already defined above
    FLastUpdate      = AidLast|AidUpdate,

    FSolveDependMask   = AidSolve|AidDepend|AidMask,
    FDomainDependMask  = AidDomain|AidDepend|AidMask,
    FSolveSymDeps      = AidSolve|AidSymdeps,
    FDomainSymDeps     = AidDomain|AidSymdeps,

    
    // Flag handling fields
    FFlagMask        = AidFlag|AidMask,
    FFlagBit         = AidFlag|AidBit,

    // Solver result rider
    FMetrics         = AidMetrics,
    FRank            = AidRank,
    FFit             = AidFit,
    FErrors          = AidErrors,
    FCoVar           = AidCoVar,
    FFlag            = AidFlag,
    FMu              = AidMu,
    FStdDev          = AidStdDev,
    FChi             = AidChi,

    FResolutionDependMask = AidResolution|AidDepend|AidMask,
    
    FContagiousFail  = AidContagious|AidFail,
    
    FIndex           = AidIndex;
    

};

#endif
