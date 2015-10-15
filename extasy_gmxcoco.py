#!/usr/bin/env python

__author__        = "The ExTASY project <ardita.shkurti@nottingham.ac.uk>"
__copyright__     = "Copyright 2015, http://www.extasy-project.org/"
__license__       = "MIT"
__use_case_name__ = "'Gromacs + CoCo' simulation-analysis proof-of-concept (ExTASY)."


from radical.ensemblemd import Kernel
from radical.ensemblemd import EnsemblemdError
from radical.ensemblemd import SimulationAnalysisLoop
from radical.ensemblemd import SingleClusterEnvironment

from radical.ensemblemd.engine import get_engine

import imp
import argparse
import sys
import os

from grompp import grompp_Kernel
get_engine().add_kernel_plugin(grompp_Kernel)

from mdrun import mdrun_Kernel
get_engine().add_kernel_plugin(mdrun_Kernel)

from trjconv import trjconv_Kernel
get_engine().add_kernel_plugin(trjconv_Kernel)

# ------------------------------------------------------------------------------
#

class Extasy_CocoGromacs_Static(SimulationAnalysisLoop):            

    def __init__(self, maxiterations, simulation_instances, analysis_instances):
        SimulationAnalysisLoop.__init__(self, maxiterations, simulation_instances, analysis_instances)

    def pre_loop(self):
        '''
        function : transfers input files, intermediate executables

        pre_coam_loop :-                                         

                Purpose : Transfers files that will be used for this workflow
                in the remote machine. This is a kernel that can be used from
                all workflows for transfering data files.
		

                Arguments : None
        '''
        k = Kernel(name="md.pre_coam_loop")                      
        k.upload_input_data = [Kconfig.initial_crd_file,
                               Kconfig.md_input_file,   
                               Kconfig.top_file,
                               Kconfig.itp_file,                    
                               Kconfig.restr_file,                  
                               Kconfig.eminrestr_md,                
                               Kconfig.eeqrestr_md]                 
                               
        return k


    def simulation_step(self, iteration, instance):
        '''
        function : if iteration = 1, use coordinates file from pre_loop, else use coordinates output file from analysis generated
        in the previous iteration. 
        - Preprocess the simulation parameters, coordinates structure and topology file to generate the 
        portable binary run - .tpr - file to be used by the simulation run;
        - Run the simulations;
        - Apply gromacs to the trajectory and coordinate files to adjust the jumps of the molecular system
        in the periodic boundary conditions simulation box.

        md.grompp: -
        
                Purpose : Run gromacs preprocessing to obtain a portable binary run file (.tpr) that unifies information
                from the simulation parameters, topology file and the initial coordinates file.
                
                Arguments : --mdp  = simulation parameters file - input
                            --gro  = single coordinates file - input
                            --top  = topology filename - input
                            --ref  = single coordinates file to be used as a reference for position restraints - input
                            --tpr  = portable binary run file - output
        md.mdrun :-

                Purpose : Run gromacs on each of the coordinate files .gro that were given in input to the previous 
                grompp kernel, using as input the .tpr file generated by the previous grompp kernel.
                Among others generates a .xtc file in each instance, all of which will be used for further analysis.

                Arguments : --deffnm = basename that will be used for all generated files in output but also to determine
                the .tpr file in input.
        '''
        
        kernel_list = []
        
        if((iteration-1)!=0):

            k1_prep_min_kernel = Kernel(name="md.grompp")
            k1_prep_min_kernel.link_input_data = ['$PRE_LOOP/{0}'.format(os.path.basename(Kconfig.eminrestr_md)),
                                                  '$PRE_LOOP/{0}'.format(os.path.basename(Kconfig.top_file)),
                                                  '$PRE_LOOP/{0}'.format(os.path.basename(Kconfig.restr_file))]			
            k1_prep_min_kernel.link_input_data = k1_prep_min_kernel.link_input_data + ['$PREV_ANALYSIS_INSTANCE_{2}/coco_out{0}_{1}.gro > coco_out{0}_{1}.gro'.format(iteration-2,instance-1,instance)]
            k1_prep_min_kernel.arguments = ["--mdp={0}".format(os.path.basename(Kconfig.eminrestr_md)),
                                            "--gro=coco_out{0}_{1}.gro".format(iteration-2,instance-1),
                                            "--top={0}".format(os.path.basename(Kconfig.top_file)),
                                            "--ref={0}".format(os.path.basename(Kconfig.restr_file)),
                                            "--tpr=min-%d_%d.tpr"%(iteration-1,instance-1)]
            k1_prep_min_kernel.copy_output_data = ['min-{0}_{1}.tpr > $PRE_LOOP/min-{0}_{1}.tpr'.format(iteration-1,instance-1)]    
            kernel_list.append(k1_prep_min_kernel)
            
            k2_min_kernel = Kernel(name="md.mdrun")
            k2_min_kernel.link_input_data = ['$PRE_LOOP/min-{0}_{1}.tpr > min-{0}_{1}.tpr'.format(iteration-1,instance-1)]
            k2_min_kernel.arguments = ["--deffnm=min-%d_%d"%(iteration-1,instance-1)]
            k2_min_kernel.copy_output_data = ['min-{0}_{1}.gro > $PRE_LOOP/min-{0}_{1}.gro'.format(iteration-1,instance-1)]
            kernel_list.append(k2_min_kernel)
            
            k3_prep_eq_kernel = Kernel(name="md.grompp")
            k3_prep_eq_kernel.link_input_data = ['$PRE_LOOP/{0}'.format(os.path.basename(Kconfig.eeqrestr_md)),
                                                 '$PRE_LOOP/{0}'.format(os.path.basename(Kconfig.top_file)),
                                                 '$PRE_LOOP/{0}'.format(os.path.basename(Kconfig.restr_file))]
            k3_prep_eq_kernel.link_input_data = k3_prep_eq_kernel.link_input_data + ['$PRE_LOOP/min-{0}_{1}.gro > min-{0}_{1}.gro'.format(iteration-1,instance-1)]
            k3_prep_eq_kernel.arguments = ["--mdp={0}".format(os.path.basename(Kconfig.eeqrestr_md)),
                                           "--gro=min-%d_%d.gro"%(iteration-1,instance-1),
                                           "--top={0}".format(os.path.basename(Kconfig.top_file)),
                                           "--ref={0}".format(os.path.basename(Kconfig.restr_file)),
                                           "--tpr=eq-%d_%d.tpr"%(iteration-1,instance-1)]
            k3_prep_eq_kernel.copy_output_data = ['eq-{0}_{1}.tpr > $PRE_LOOP/eq-{0}_{1}.tpr'.format(iteration-1,instance-1)]
            kernel_list.append(k3_prep_eq_kernel)

            k4_eq_kernel = Kernel(name="md.mdrun")
            k4_eq_kernel.link_input_data = ['$PRE_LOOP/eq-{0}_{1}.tpr > eq-{0}_{1}.tpr'.format(iteration-1,instance-1)]
            k4_eq_kernel.arguments = ["--deffnm=eq-%d_%d"%(iteration-1,instance-1)]
            k4_eq_kernel.copy_output_data = ['eq-{0}_{1}.gro > $PRE_LOOP/eq-{0}_{1}.gro'.format(iteration-1,instance-1)]
            kernel_list.append(k4_min_kernel)
			
        k5_prep_sim_kernel = Kernel(name="md.grompp")
        k5_prep_sim_kernel.link_input_data = ['$PRE_LOOP/{0}'.format(os.path.basename(Kconfig.md_input_file)),
                                             '$PRE_LOOP/{0}'.format(os.path.basename(Kconfig.top_file))]
        if((iteration-1)==0):
            k5_prep_sim_kernel.link_input_data =  k5_prep_sim_kernel.link_input_data + ['$PRE_LOOP/{0}'.format(os.path.basename(Kconfig.initial_crd_file))]
            k5_prep_sim_kernel.arguments = ["--mdp={0}".format(os.path.basename(Kconfig.md_input_file)),
                                           "--gro={0}".format(os.path.basename(Kconfig.initial_crd_file)),
                                           "--top={0}".format(os.path.basename(Kconfig.top_file)),
                                           "--tpr=md-%d_%d.tpr"%(iteration-1,instance-1)]  
        else:
            k5_prep_sim_kernel.link_input_data =  k5_prep_sim_kernel.link_input_data + ['$PRE_LOOP/eq-{0}_{1}.gro > eq-{0}_{1}.gro'.format(iteration-1,instance-1)]
            k5_prep_sim_kernel.arguments = ["--mdp={0}".format(os.path.basename(Kconfig.md_input_file)),
                                           "--gro=eq-%d_%d.gro"%(iteration-1,instance-1),
                                           "--top={0}".format(os.path.basename(Kconfig.top_file)),
                                           "--tpr=md-%d_%d.tpr"%(iteration-1,instance-1)]             
        k5_prep_sim_kernel.copy_output_data = ['md-{0}_{1}.tpr > $PRE_LOOP/md-{0}_{1}.tpr'.format(iteration-1,instance-1)]        
        kernel_list.append(k5_prep_sim_kernel)
        
        k6_sim_kernel = Kernel(name="md.mdrun")
        k6_sim_kernel.link_input_data = ['$PRE_LOOP/md-{0}_{1}.tpr > md-{0}_{1}.tpr'.format(iteration-1,instance-1)]
        k6_sim_kernel.arguments = ["--deffnm=md-%d_%d"%(iteration-1,instance-1)]
        k6_sim_kernel.copy_output_data = ["md-{0}_{1}.gro > $PRE_LOOP/md-{0}_{1}.gro".format(iteration-1,instance-1)]
        kernel_list.append(k6_sim_kernel)

        k7_sim_kernel = Kernel(name="md.trjconv")
        k7_sim_kernel.link_input_data = ["$PRE_LOOP/md-{0}_{1}.gro > md-{0}_{1}.gro".format(iteration-1,instance-1)]
        k7_sim_kernel.arguments = [    "--echo1=System",
                                                             "--f1=md-{0}_{1}.gro".format(iteration-1,instance-1),
                                                             "--s1=md-{0}_{1}.tpr".format(iteration-1,instance-1),
                                                             "--o1=md-{0}_{1}_whole.gro".format(iteration-1,instance-1),
                                                             "--pbc1=whole",
                                                             "--echo2=System",
                                                             "--f2=md-{0}_{1}.xtc".format(iteration-1,instance-1),
                                                             "--s2=md-{0}_{1}.tpr".format(iteration-1,instance-1),
                                                             "--o2=md-{0}_{1}_whole.xtc".format(iteration-1,instance-1),
                                                             "--pbc2=whole"

                            ]
        k7_sim_kernel.copy_output_data = ["md-%d_%d.xtc > $PRE_LOOP/md-%d_%d.xtc"%(iteration-1,instance-1)]
        
        if(iteration%Kconfig.nsave==0):
            k7_sim_kernel.download_output_data = ["md-{0}_{1}.xtc > output/iter{0}/md-{0}_{1}.xtc".format(iteration-1,instance-1)]	
        
        kernel_list.append(k7_sim_kernel)              
        
        return kernel_list
        

    def analysis_step(self, iteration, instance):
        '''
        function : Perform CoCo Analysis on the output of the simulation from the current iteration. Using the .xtc
         files generated in all instances, generate .gro files (as many as the num_CUs) to be used in the next simulations. 
        

        coco :-

                Purpose : Runs CoCo analysis on a set of MD trajectory files in this case xtc files and generates several coordinates file to be

                Arguments : --grid           = Number of points along each dimension of the CoCo histogram
                            --dims           = The number of projections to consider from the input pcz file
                            --frontpoints    = Number of CUs
                            --topfile        = Topology filename
                            --mdfile         = MD Input filename
                            --output         = Output filename
                            --cycle          = Current iteration number
                            --atom_selection = Selection of the biological part of the system we want to consider for analysis
        '''

        k1_ana_kernel = Kernel(name="md.coco")

        k1_ana_kernel.link_input_data = ['$PRE_LOOP/{0}'.format(os.path.basename(Kconfig.top_file))]
        for iter in range(1,iteration+1):
            for i in range(1,Kconfig.num_CUs+1):        
                k1_ana_kernel.link_input_data = k3_ana_kernel.link_input_data + ['$SIMULATION_ITERATION_{0}_INSTANCE_{1}/md-{2}_{3}.xtc > md-{2}_{3}.xtc'.format(iter,i,iter-1,i-1)]
        
        k1_ana_kernel.cores = 1
        k1_ana_kernel.uses_mpi = False
        
        outbase, ext = os.path(Kconfig.output)
        if ext == '':
			ext = '.pdb'
                
        k1_ana_kernel.arguments = ["--grid={0}".format(Kconfig.grid),
                                   "--dims={0}".format(Kconfig.dims),
                                   "--frontpoints={0}".format(Kconfig.num_CUs),
                                   "--topfile={0}".format(os.path.basename(Kconfig.top_file)),
                                   "--mdfile=*.xtc",
                                   "--output={0}{1}{2}".format(outbase,iteration-1,ext),
                                   "--atom_selection={0}".format(Kconfig.sel)]

        k1_ana_kernel.copy_output_data = []
        for i in range(0,Kconfig.num_CUs):
            k1_ana_kernel.copy_output_data = k1_ana_kernel.copy_output_data + ["{0}{1}{2}{3} > $PRE_LOOP/{0}{1}{2}{3}".format(outbase,iteration-1,i,ext)]

        k1_ana_kernel.download_output_data = ["coco.log > output/coco-iter{0}.log".format(iteration-1)]	
        
        return k1_ana_kernel
        
    def post_loop(self):
        pass

# ------------------------------------------------------------------------------
#
if __name__ == "__main__":

    try:
        parser = argparse.ArgumentParser()
        parser.add_argument('--RPconfig', help='link to Radical Pilot related configurations file')
        parser.add_argument('--Kconfig', help='link to Kernel configurations file')

        args = parser.parse_args()

        if args.RPconfig is None:
            parser.error('Please enter a RP configuration file')
            sys.exit(1)
        if args.Kconfig is None:
            parser.error('Please enter a Kernel configuration file')
            sys.exit(0)

        RPconfig = imp.load_source('RPconfig', args.RPconfig)
        Kconfig = imp.load_source('Kconfig', args.Kconfig)

        # Create a new static execution context with one resource and a fixed
        # number of cores and runtime.

        cluster = SingleClusterEnvironment(
            resource=RPconfig.REMOTE_HOST,
            cores=RPconfig.PILOTSIZE,
            walltime=RPconfig.WALLTIME,
            username = RPconfig.UNAME, #username
            project = RPconfig.ALLOCATION, #project
            queue = RPconfig.QUEUE,
            database_url = RPconfig.DBURL
        )

        cluster.allocate()

        coco_gromacs_static = Extasy_CocoGromacs_Static(maxiterations=Kconfig.num_iterations, simulation_instances=Kconfig.num_CUs, analysis_instances=1)
        cluster.run(coco_gromacs_static)

        cluster.deallocate()

    except EnsemblemdError, er:

        print "The gromacs-coco ExTASY workflow not completed correctly due to an Ensemble MD Toolkit Error: {0}".format(str(er))
        raise # Just raise the execption again to get the backtrace
