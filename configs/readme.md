## This folder should be used to export JSON configuration for ci scripts

Configuration classes can be called to export their supported configuration map
to JSON files. Those files can be used to directly control the CI through the
corresponding text fields.

Reference configuration files can be created when calling a _config module
with --export command, followed by an optional target directory

`python xxx_config.py --export (out_dir)`

If out_dir is not defined configuration will be exported in current working
directory.

At release date the system will generate two configuration files for building
and testing AN521 reference platform

~~~~~
python lava_helper/lava_helper_configs.py --export ./configs
python build_helper/build_helper_configs.py --export ./configs
~~~~~

*Copyright (c) 2018-2019, Arm Limited. All rights reserved.*
