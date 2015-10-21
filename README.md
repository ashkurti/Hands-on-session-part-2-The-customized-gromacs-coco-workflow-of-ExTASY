# README #

### What is this repository for? ###

This repository, stores the input files necessary to execute the gromacs/coco workflow for a penta-alanine example in a High Performance Computing (HPC) environment such as STAMPEDE (XSEDE, US supercomputing resources) or ARCHER (UK supercomputing resources).

The resource configuration file stampede.rcfg and archer.rcfg should be modified by the user, with their credentials on the username UNAME and allocation (project to be charged for the computations on the HPC resource).

In addition the users would ideally use their own simulation files, for computation contexts similar to this one and complete the information on their file names in a workload configuration file such as gmxcoco.wcfg.

A- In this case, we will perform a set of Molecular Dynamics (MD) simulations (the user decides the size of the set throught the num_CUs parameter of the gmxcoco.wcfg configuration file) with gromacs, starting from an initial structure ./inp_files/helix.gro with simulation parameters and topology described at respectively ./inp_files/grompp-verlet.mdp and ./inp_files/topol.top

B- Afterwards, we will analyse all coordinate trajectories produced from the set of MD simulations by means of the CoCo method through the [pyCoCo](https://bitbucket.org/extasy-project/coco/overview) tool, and produce new simulation starting points (in terms of .gro structures) by means of the same technique.

C- We will then perform a set of minimisation procedures using position restraints and the simulation parameters described at ./inp_files/grompp_after_coco-em1.mdp, ./inp_files/grompp_after_coco-em2.mdp
Afterwards, we will proceed with a standard set of MD simulation runs using the same simulation parameters as described at step A.

D- We will analyse all coordinate trajectories produced from the set of MD simulations of step C by means of the CoCo method as described for step B.

Steps from A to D make 2 iterations in our workflow:

* Iteration 1 - Step A & Step B
* Iteration 2 - Step C & Step D

All iterations from the 2nd onwards would include one C-like step and one D-like step for example:

* Iteration 3 - Step C & Step D
* Iteration 4 - Step C & Step D

### How do I get the workflow to run? ###

To run this workflow in their own systems the users should do the following:
```
#!python

wget https://bitbucket.org/extasy-project/extasy_gmxcoco/get/ext_gmxcoco-0.5.tar.gz
mkdir -p extasy_gmxcoco ; tar -xvf ext_gmxcoco-0.5.tar.gz -C extasy_gmxcoco
cd extasy_gmxcoco
virtualenv $HOME/ExTASY_0.2
source $HOME/ExTASY_0.2/bin/activate.cs
```
If in a C shell:
```
#!python

setenv ENMD_INSTALL_VERSION "master"
```
or if in a bash shell:
```
#!python

export ENMD_INSTALL_VERSION="master"
```
Afterwards continue with:
```
#!python
pip install --upgrade git+https://github.com/radical-cybertools/radical.ensemblemd.git@$ENMD_INSTALL_VERSION#egg=radical.ensemblemd
```
if in a C shell:

```
#!python

setenv RADICAL_ENMD_VERBOSE REPORT

```
or if in a bash shell:
```
#!python

export RADICAL_ENMD_VERBOSE=REPORT

```
and at last, after completing stampede.rcfg and gmxcoco.wcfg appropriately:
```
#!python

python extasy_gmxcoco.py --RPconfig stampede.rcfg --Kconfig gmxcoco.wcfg | & tee extasy.log

```

If everything is successful, with the current configuration the user should notice the generation of an output folder in his/her current directory with the following contents:
```
#!python

ls -l output/*
-rw------- 1 uname pa  491 Oct 20 12:05 output/coco-iter0.log
-rw------- 1 uname pa  538 Oct 20 12:16 output/coco-iter1.log

output/iter0:
total 3424
-rw------- 1 uname pa 1752276 Oct 20 12:05 md-0_0_whole.xtc
-rw------- 1 uname pa 1751064 Oct 20 12:05 md-0_1_whole.xtc

output/iter1:
total 3424
-rw------- 1 uname pa 1751604 Oct 20 12:15 md-1_0_whole.xtc
-rw------- 1 uname pa 1751592 Oct 20 12:15 md-1_1_whole.xtc
```

### Who do I talk to? ###

* ardita.shkurti@nottingham.ac.uk (for the development of the standalone simulation workflow, development of the kernels to implement this workflow in an extasy context, input/output results expected at each step)
* charles.laughton@nottingham.ac.uk (for the input/output results expected at each step of the workflow and the simulation trajectories analysis technique used)
* vb224@scarletmail.rutgers.edu (for doubts on the interaction of the kernels with the underlying cyber tools - such as radical pilot, saga-python and radical-utils of the RADICAL team at Rutgers)
* shantenu.jha@rutgers.edu (for the cyber tools - such as radical pilot, saga-python and radical-utils of the RADICAL team at Rutgers)
* cclementi@gmail.com, jchen978@gmail.com, Eugen.Hruska@rice.edu (for the gromacs input files - \*mdp, \*gro, \*top)