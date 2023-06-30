eclair_tfm_set_toolchain_path() {
    path_cmd=$(python3 tf-m-ci-scripts/configs.py -b set_compiler $CONFIG_NAME)
    eval $path_cmd
}
