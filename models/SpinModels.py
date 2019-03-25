"""
Currently only support spin-half models
Generate Hamiltonians of
	Ising model
	Heiseneberg model
Get SumSx, Sy, Sz (squared)
"""

import sys
sys.path.append("../core")
import numpy as np
import numpy.random
import scipy.linalg as LA
import MPS
import MPO
import copy


PauliSigma = np.array(
	[[[1,0],[0,1]], [[0,1],[1,0]], [[0,-1j], [1j,0]], [[1,0],[0,-1]]])

Up = np.array([1,0])
Dn = np.array([0,1])
Xp = np.array([1/np.sqrt(2),1/np.sqrt(2)])
Xm = np.array([1/np.sqrt(2),-1/np.sqrt(2)])
Yp = np.array([1/np.sqrt(2),1j/np.sqrt(2)])
Ym = np.array([1/np.sqrt(2),-1j/np.sqrt(2)])
Em = np.array([0,0])


class Ising:
	# H = \sum_{i=1}^{L-1} J[i]sigma_i^z sigma_{i+1}^z
	#	+ \sum_{i=1}^{L} (g[i]sigma_i^x + h[i]sigma_{i}^z) + offset
	def __init__(self, L, J, g, h, offset):
		self.L = L
		self.J = J
		self.g = g
		self.h = h
		self.offset = offset
		self.hamil = MPO.MPO(L, 3, 2)
		opL = np.array([[ [1,0,0,0], [0,0,0,J[0]], [offset/L,g[0],0,h[0]] ]])
		opR = np.array([ [[offset/L,g[L-1],0,h[L-1]]], [[0,0,0,1]], [[1,0,0,0]] ])
		self.hamil.ops[0].A = np.einsum('ijk,kml->mlij', opL, PauliSigma)
		self.hamil.ops[L-1].A = np.einsum('ijk,kml->mlij', opR, PauliSigma)
		for i in range(1, L-1):
			opM = np.array([ [ [1,0,0,0], [0,0,0,J[i]], [offset/L,g[i],0,h[i]] ],
							 [ [0,0,0,0], [0,0,0,0], [0,0,0,1] ],
							 [ [0,0,0,0], [0,0,0,0], [1,0,0,0] ] ])
			self.hamil.ops[i].A = np.einsum('ijk,kml->mlij', opM, PauliSigma)

	def getUMPO(self, t, TrotterN, imag = True):
		# Return e^{-Ht} if imag else e^{-iHt}

		return 0


class Heisenberg:
	# H = \sum_{p=x,y,z; i=1}^{L-1} J{p}[i]sigma_i^p sigma_{i+1}^p
	#	+ \sum_{i=1}^{L} (g[i]sigma_i^x + h[i]sigma_{i}^z) + offset
	def __init__(self, L, Jx, Jy, Jz, g, h, offset):
		self.L = L
		self.Jx = Jx
		self.Jy = Jy
		self.Jz = Jz
		self.g = g
		self.h = h
		self.offset = offset
		self.hamil = MPO.MPO(L, 5, 2)
		opL = np.array([[ [1,0,0,0], [0,Jx[0],0,0], [0,0,Jy[0],0], [0,0,0,Jz[0]],
						  [offset/L,g[0],0,h[0]] ]])
		opR = np.array([ [[offset/L,g[L-1],0,h[L-1]]], [[0,1,0,0]], [[0,0,1,0]],
					     [[0,0,0,1]], [[1,0,0,0]] ])
		self.hamil.ops[0].A = np.einsum('ijk,kml->mlij', opL, PauliSigma)
		self.hamil.ops[L-1].A = np.einsum('ijk,kml->mlij', opR, PauliSigma)
		for i in range(1, L-1):
			opM = np.array([ [ [1,0,0,0], [0,Jx[i],0,0], [0,0,Jy[i],0],
							   [0,0,0,Jz[i]], [offset/L,g[i],0,h[i]] ],
							 [ [0,0,0,0], [0,0,0,0], [0,0,0,0], [0,0,0,0], [0,1,0,0] ],
							 [ [0,0,0,0], [0,0,0,0], [0,0,0,0], [0,0,0,0], [0,0,1,0] ],
							 [ [0,0,0,0], [0,0,0,0], [0,0,0,0], [0,0,0,0], [0,0,0,1] ],
							 [ [0,0,0,0], [0,0,0,0], [0,0,0,0], [0,0,0,0], [1,0,0,0] ]
						   ])
			self.hamil.ops[i].A = np.einsum('ijk,kml->mlij', opM, PauliSigma)


def getSumSxMPO(L):
	# Return \sum_{i=1}^L sigma_i^x
	sumSx = MPO.MPO(L, 2, 2)
	opL = np.array([[ [1,0,0,0], [0,1,0,0] ]])
	opR = np.array([ [[0,1,0,0]], [[1,0,0,0]] ])
	sumSx.ops[0].A = np.einsum('ijk,kml->mlij', opL, PauliSigma)
	sumSx.ops[L-1].A = np.einsum('ijk,kml->mlij', opR, PauliSigma)
	for i in range(1, L-1):
		opM = np.array([ [ [1,0,0,0], [0,1,0,0] ],
						 [ [0,0,0,0], [1,0,0,0] ] ])
		sumSx.ops[i].A = np.einsum('ijk,kml->mlij', opM, PauliSigma)
	return sumSx


def getSumSyMPO(L):
	# Return \sum_{i=1}^L sigma_i^y
	sumSy = MPO.MPO(L, 2, 2)
	opL = np.array([[ [1,0,0,0], [0,0,1,0] ]])
	opR = np.array([ [[0,0,1,0]], [[1,0,0,0]] ])
	sumSy.ops[0].A = np.einsum('ijk,kml->mlij', opL, PauliSigma)
	sumSy.ops[L-1].A = np.einsum('ijk,kml->mlij', opR, PauliSigma)
	for i in range(1, L-1):
		opM = np.array([ [ [1,0,0,0], [0,0,1,0] ],
						 [ [0,0,0,0], [1,0,0,0] ] ])
		sumSy.ops[i].A = np.einsum('ijk,kml->mlij', opM, PauliSigma)
	return sumSy


def getSumSzMPO(L):
	# Return \sum_{i=1}^L sigma_i^z
	sumSz = MPO.MPO(L, 2, 2)
	opL = np.array([[ [1,0,0,0], [0,0,0,1] ]])
	opR = np.array([ [[0,0,0,1]], [[1,0,0,0]] ])
	sumSz.ops[0].A = np.einsum('ijk,kml->mlij', opL, PauliSigma)
	sumSz.ops[L-1].A = np.einsum('ijk,kml->mlij', opR, PauliSigma)
	for i in range(1, L-1):
		opM = np.array([ [ [1,0,0,0], [0,0,0,1] ],
						 [ [0,0,0,0], [1,0,0,0] ] ])
		sumSz.ops[i].A = np.einsum('ijk,kml->mlij', opM, PauliSigma)
	return sumSz


def getSumSx2MPO(L):
	# Return (\sum_{i=1}^L sigma_i^x) ^ 2
	sumSx2 = MPO.MPO(L, 2, 2)
	opL = np.array([[ [1,0,0,0], [0,1,0,0], [1,0,0,0] ]])
	opR = np.array([ [[1,0,0,0]], [[0,2,0,0]], [[1,0,0,0]] ])
	sumSx2.ops[0].A = np.einsum('ijk,kml->mlij', opL, PauliSigma)
	sumSx2.ops[L-1].A = np.einsum('ijk,kml->mlij', opR, PauliSigma)
	for i in range(1, L-1):
		opM = np.array([ [ [1,0,0,0], [0,1,0,0], [1,0,0,0] ],
						 [ [0,0,0,0], [1,0,0,0], [0,2,0,0] ],
						 [ [0,0,0,0], [0,0,0,0], [1,0,0,0] ] ])
		sumSx2.ops[i].A = np.einsum('ijk,kml->mlij', opM, PauliSigma)
	return sumSx2


def getSumSy2MPO(L):
	# Return (\sum_{i=1}^L sigma_i^y) ^ 2
	sumSy2 = MPO.MPO(L, 2, 2)
	opL = np.array([[ [1,0,0,0], [0,0,1,0], [1,0,0,0] ]])
	opR = np.array([ [[1,0,0,0]], [[0,0,2,0]], [[1,0,0,0]] ])
	sumSy2.ops[0].A = np.einsum('ijk,kml->mlij', opL, PauliSigma)
	sumSy2.ops[L-1].A = np.einsum('ijk,kml->mlij', opR, PauliSigma)
	for i in range(1, L-1):
		opM = np.array([ [ [1,0,0,0], [0,0,1,0], [1,0,0,0] ],
						 [ [0,0,0,0], [1,0,0,0], [0,0,2,0] ],
						 [ [0,0,0,0], [0,0,0,0], [1,0,0,0] ] ])
		sumSy2.ops[i].A = np.einsum('ijk,kml->mlij', opM, PauliSigma)
	return sumSy2


def getSumSz2MPO(L):
	# Return (\sum_{i=1}^L sigma_i^z) ^ 2
	sumSz2 = MPO.MPO(L, 2, 2)
	opL = np.array([[ [1,0,0,0], [0,0,0,1], [1,0,0,0] ]])
	opR = np.array([ [[1,0,0,0]], [[0,0,0,2]], [[1,0,0,0]] ])
	sumSz2.ops[0].A = np.einsum('ijk,kml->mlij', opL, PauliSigma)
	sumSz2.ops[L-1].A = np.einsum('ijk,kml->mlij', opR, PauliSigma)
	for i in range(1, L-1):
		opM = np.array([ [ [1,0,0,0], [0,0,0,1], [1,0,0,0] ],
						 [ [0,0,0,0], [1,0,0,0], [0,0,0,2] ],
						 [ [0,0,0,0], [0,0,0,0], [1,0,0,0] ] ])
		sumSz2.ops[i].A = np.einsum('ijk,kml->mlij', opM, PauliSigma)
	return sumSz2
