__author__ = 'ashkurti'
"""
This will carry out the fix of the jumps from the simulation box of the periodic boundary conditions
"""
import os
import sys
from extasy import script

if __name__ == '__main__':
    print 'fixing the jumps within the central simulation box due to pbc...'
    base = sys.argv[1]
    nreps = int(sys.argv[2])
    cycle = int(sys.argv[3])
    dict = {}
    dict['cycle'] = cycle
    for rep in range(nreps):
        tl = script.Script()
        tl.append('source leaprc.ff99SB')
        tl.append('x = loadpdb %s%s%s.pdb'%(base,cycle,rep))
        tl.append('saveamberparm x delete.me min%s%s.crd'%(cycle,rep))
        tl.append('quit')
        tl.run('tleap -f {}')
