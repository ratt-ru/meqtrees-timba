#!/usr/bin/env python

#
#% $Id$ 
#
#
# Copyright (C) 2002-2007
# The MeqTree Foundation & 
# ASTRON (Netherlands Foundation for Research in Astronomy)
# P.O.Box 2, 7990 AA Dwingeloo, The Netherlands
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>,
# or write to the Free Software Foundation, Inc., 
# 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

import biggles
import Numeric
import sys
import math
from string import split, strip

def getdata( filename ):
	text = open(filename, 'r').readlines()
	data = []
	L = len(text)
	i = 0
	while(text[i][0:4] != '++++'):
		i = i+1
		if i >= L:
			print 'bogus input file : ++++ never found'
			return data,0

#	print '%d comments' % i
	
	info = split(strip(text[i+1]))
	if(info[0] != '1'):
		print 'bogus input file'
		return data,0
	
	info = split(strip(text[i+2]))
	icomp = int(info[1])
	ncomp = int(info[2])
	igrid = int(info[3])
	if igrid != 1:
		print 'not a UV grid'
		return data,0
	if icomp != 3:
		print 'not linear polarization'
		return data,0
	
	info = split(strip(text[i+5]))
	nx = int(info[0])
	ny = int(info[1])
	if nx != ny:
		print 'unsupported : nx != ny'
		return data, 0
	
	info = split(strip(text[i+4]))
	scale = (float(info[2])-float(info[0]))/float(nx-1)
	
	for j in range(2*ncomp):
		data.append([])
	
	for j in range(i+6, L):
		comps = split(strip(text[j]))
		for k in range(2*ncomp):
			data[k].append(float(comps[k]))

	return data, (scale*180.0/math.pi)

def func_linewidth( i, n, z0, z_min, z_max ):
	f = float(n-i)/(1.5*float(n))
	r = int(255*f)
	return 0x10101*r
	

def usage( prog ):
	print 'usage : %s <infile> [-{l|L} <d>]' % prog
	return 1

def plot( Z, scale, nx, outfile, levs ):
	X = Numeric.zeros( (nx), Numeric.Float )
	Y = Numeric.zeros( (nx), Numeric.Float )

	min = 1e9

	for i in range(nx):
		for j in range(nx):
			if Z[j][i] < min:
				min = Z[j][i]

	start = -scale*(nx-1.0)/2.0

	for x in range(nx):
		X[x] = start + x*scale
		Y[x] = start + x*scale
	
	P = biggles.FramedPlot()
	cntrs = biggles.Contours(Z, X, Y, levels=levs, linewidth=0.5)
	return cntrs

def totalpower( data, nx, ind ):
	Z = Numeric.zeros( (nx, nx), Numeric.Float )
	C = len(data)
	L = len(data[0])
	m = 0.0
	for y in range(nx):
		if ind < 15:
			for x in range(nx):	
				i = y + nx*x
				s = 0.0;
				for j in range(C):
					s = s + data[j][i]*data[j][i];
				Z[x][y] = s
				if s > m:
					m = s;
		else:
			for x in range(nx):	
				i = y + nx*x
				s = 0.0;
				for j in range(C):
					s = s + data[j][i]*data[j][i];
				Z[y][x] = s
				if s > m:
					m = s;

	Z = Z/m
	
	return Z

def amplitude( data, nx ):
	Z = Numeric.zeros( (nx, nx), Numeric.Float )
	C = len(data)
	L = len(data[0])
	m = 0.0
	for y in range(nx):
		for x in range(nx):	
			i = x + nx*y
			s = 0.0;
			for j in range(C):
				s = s + data[j][i]*data[j][i];
			s = math.sqrt(s)
			Z[y][x] = s
			if s > m:
				m = s;

	Z = Z/m
	
	return Z

def linlevs( spacing ):
	levs = []
	l = 1.0
	while(1):
		l = l - spacing
		if(l <= 0.0):
			break
		levs.append(l);
	return levs

def loglevs( factor ):
	levs = []
	l = 1.0
	for i in range(6):
		l = l*factor
		levs.append(l)
	return levs

def main( argv ):
	P = biggles.FramedArray(5, 5)
	P.aspect_ratio=1
	P.uniform_limits=1
	P.xlabel='[Degrees]'
	P.ylabel='[Degrees]'
	xa = [0,1,2,3,1,2,3,2,3,3,4,4,4,4,4,0,0,0,0,1,1,1,2,2,3]
	ya = [0,0,0,0,1,1,1,2,2,3,0,1,2,3,4,1,2,3,4,2,3,4,3,4,4]
#for i in range(0, 20):
#	for i in range(0, 25):
 	for i in range(5, 25):
		filename = argv[1]+('_%02d.grd' % (i+1))
		data, scale = getdata(filename)

		levs = loglevs(0.5)

		if len(argv) > 2:
			if(argv[2] == '-l'):
				if len(argv) > 3:
					levs = linlevs(float(argv[3]))
			if(argv[2] == '-L'):
				if len(argv) > 3:
					levs = loglevs(float(argv[3]))

		ncomp = len(data)
		if(ncomp <= 0): 
			return 1

		size = len(data[0])

		nx = int(math.sqrt(size))
		if(nx*nx != size):
			print 'data not square:', filename
			return 1

#	print 'nx = %d' % nx
#	print 'scale = %f deg / pix' % scale

		Z = totalpower(data, nx, i);
		cntrs = plot(Z, scale, nx, "beam.eps", levs)
                print 'filename xa ya ',filename, ' ', xa[i], ' ',ya[i]
		P[xa[i],ya[i]].add(cntrs)
	P.show()
	P.save_as_eps('allbeams.ps')

if len(sys.argv) < 2:
	usage(sys.argv[0])
else:
	main(sys.argv)
