eclair_tfm_set_toolchain_path() {
    path_cmd=$(python3 tf-m-ci-scripts/configs.py -b -g all $CONFIG_NAME | head -n1)
    eval $path_cmd
}
