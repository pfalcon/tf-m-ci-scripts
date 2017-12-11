#-------------------------------------------------------------------------------
# Copyright (c) 2017-2019, Arm Limited and Contributors. All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause
#
#-------------------------------------------------------------------------------

##
##@file
##@brief Shell documentation examples
##


##@var string example_variable
##@brief Example variable
##
##This is an example to show ho to document variables.
##
#This is needed for doxygen for now.
#!string example_variable;


##@fn example_function(path build_base_dir, string build_config_name)
##@brief En example function.
##@param[in] build_base_dir
##@param[in] build_config_name
##@returns N/A
##
##This function was only made to show how-to document a function.
##
##Usage:
##  command | result
##  --------|-------
##  example_function "test_build_st32" "somestring" | Do whatever is done.
##
#This is needed for doxygen for now.
#!void example_function(path build_base_dir, string build_config_name){};
#

