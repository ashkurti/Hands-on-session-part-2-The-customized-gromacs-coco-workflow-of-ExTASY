#!/usr/bin/env python

import os.path
import sys

import math as m
import numpy as n
import matplotlib.mlab as mlab
from pylab import figure, show, text, close, savefig

from MDPlus.analysis.pca.pczfile import Pczfile

# some global variables that keep track of where we are:
i      = 0
j      = 1
option = 1
c      = 0
resol  = 1
subset = 0

if len(sys.argv) < 2 or sys.argv[1] == '-h' or sys.argv[1] == '--help':
    print 'usage: pyPczplot pczfile'
    exit(1)

testfile = sys.argv[1]
pcz = Pczfile(testfile)

i1 = [(0)]
i2 = [(pcz.nframes)]
subid = [str(0)]
nsub = 1

evals=pcz.evals()
prange = n.zeros((pcz.nvecs,2))
for k in range(pcz.nvecs):
    proj = pcz.proj(k)
    prange[k,0]=proj.min()
    prange[k,1]=proj.max()
 
proj1=pcz.proj(i)[i1[subset]:i2[subset]]
proj2=pcz.proj(j)[i1[subset]:i2[subset]]
range=[prange[j,:],prange[i,:]]
nb=15+5*resol

fig = figure()
ax = fig.add_subplot(111) 
H, xedges, yedges = n.histogram2d(proj2, proj1, bins=(nb,nb), range=range)
extent = [yedges[0], yedges[-1], xedges[0], xedges[-1]]
ax.set_title(os.path.basename(pcz.filename)+'\n'+
             'Proj '+str(i)+' vs. '+str(j))
ax.set_xlabel('Proj '+str(i))
ax.set_ylabel('Proj '+str(j))
if c==1:
    ax.imshow(H, extent=extent, interpolation='nearest',origin='lower')
else:
    ax.contour(H, 10, extent=extent, origin='lower')
ax.set_aspect('auto')
fig.canvas.draw()

savefig('PC0_PC1.png', bbox_inches='tight')

