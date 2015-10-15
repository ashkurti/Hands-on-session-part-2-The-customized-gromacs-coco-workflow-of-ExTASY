#!/usr/bin/env python

"""A kernel that creates a new ASCII file with a given size and name.
"""

__author__    = "ExTASY project <ardita.shkurti@nottingham.ac.uk>"
__copyright__ = "Copyright 2015, http://www.extasy-project.org/"
__license__   = "MIT"

from copy import deepcopy

from radical.ensemblemd.exceptions import ArgumentError
from radical.ensemblemd.exceptions import NoKernelConfigurationError
from radical.ensemblemd.engine import get_engine
from radical.ensemblemd.kernel_plugins.kernel_base import KernelBase

# ------------------------------------------------------------------------------
#
_KERNEL_INFO = {
    "name":         "md.mdrun",
    "description":  "Molecular dynamics with the gromacs software package. http://www.gromacs.org/",
    "arguments":   {"--deffnm=":
                        {
                            "mandatory": True,
                            "description": "Input parameter filename"
                        }
                    },
    "machine_configs":
    {
        "*": {
            "environment"   : {"FOO": "bar"},
            "pre_exec"      : [],
            "executable"    : "mdrun",
            "uses_mpi"      : True
        },

        "xsede.stampede":
        {
            "environment" : {},
            "pre_exec" : ["module load intel/15.0.2","module load boost","module load gromacs","module load python"],
            "executable" : ["mdrun"],
            "uses_mpi"   : True
        },

        "epsrc.archer":
        {
            "environment" : {},
            "pre_exec" : ["module load packages-archer","module load gromacs/5.0.0","module load python-compute/2.7.6"],
            "executable" : ["mdrun"],
            "uses_mpi"   : True
        },
        "futuregrid.india":
        {
            "environment" : {},
            "pre_exec" : ["module load openmpi","module load python","export PATH=$PATH:/N/u/vivek91/modules/gromacs-5/bin"],
            "executable" : ["mdrun"],
            "uses_mpi"   : True
        },
        "lsu.supermic":
        {
            "environment" : {},
            "pre_exec" : ["module load openmpi","module load python","export PATH=$PATH:/N/u/vivek91/modules/gromacs-5/bin"],
            "executable" : ["mdrun"],
            "uses_mpi"   : True
        }
    }
}


# ------------------------------------------------------------------------------
#
class mdrun_Kernel(KernelBase):

    # --------------------------------------------------------------------------
    #
    def __init__(self):
        """Le constructor.
        """
        super(Kernel, self).__init__(_KERNEL_INFO)

    # --------------------------------------------------------------------------
    #
    @staticmethod
    def get_name():
        return _KERNEL_INFO["name"]

    # --------------------------------------------------------------------------
    #
    def _bind_to_resource(self, resource_key):
        """(PRIVATE) Implements parent class method.
        """
        if resource_key not in _KERNEL_INFO["machine_configs"]:
            if "*" in _KERNEL_INFO["machine_configs"]:
                # Fall-back to generic resource key
                resource_key = "*"
            else:
                raise NoKernelConfigurationError(kernel_name=_KERNEL_INFO["name"], resource_key=resource_key)

        cfg = _KERNEL_INFO["machine_configs"][resource_key]

        arguments = ['--deffnm','{0}'.format(self.get_arg("--deffnm="))]

        self._executable  = cfg["executable"]
        self._arguments   = arguments
        self._environment = cfg["environment"]
        self._uses_mpi    = cfg["uses_mpi"]
        self._pre_exec    = cfg["pre_exec"]
        self._post_exec   = None
