__copyright__ = """
/*
 * Copyright (c) 2018-2019, Arm Limited. All rights reserved.
 *
 * SPDX-License-Identifier: BSD-3-Clause
 *
 */
 """

__all__ = ["config_templates",
           "fastmodel_config_map",
           "fastmodel_wrapper",
           "fastmodel_wrapper_config"]

from .fastmodel_wrapper_config import config_variant, fpv_wrapper_config
from .fastmodel_wrapper import FastmodelWrapper
from .fastmodel_config_map import FastmodelConfigMap

from .config_templates import template_default_config, \
    template_regression_config, template_coreipc_config, \
    template_coreipctfmlevel2_config
