print(f"Loading {__file__}")


try:
    # Blackfly camera configurations:
    blackfly_pv_prefix = "XF:28IDD-BI{Det-BlackFly}"
    blackfly_c = XPDContinuous(
        blackfly_pv_prefix,
        name="blackfly",
        read_attrs=["hdf5", "stats1.total"],
        plugin_name="hdf5",
    )

    blackfly_c.stage_sigs.update(
        [
            (blackfly_c.cam.trigger_mode, "Off"),
            (blackfly_c.cam.data_type, "UInt16"),
            (blackfly_c.cam.color_mode, "Mono"),
        ]
    )

    blackfly_c.proc.data_type_out.put("Float32")

    blackfly_c.hdf5.read_path_template = (
        f"/nsls2/data/xpd-new/legacy/raw/xpdd/{blackfly_c.name}_data/%Y/%m/%d/"
    )
    blackfly_c.hdf5.write_path_template = (
        f"/nsls2/data/xpd-new/legacy/raw/xpdd/{blackfly_c.name}_data/%Y/%m/%d/"
    )

    blackfly_c.cam.bin_x.kind = "config"
    blackfly_c.cam.bin_y.kind = "config"
    blackfly_c.stats1.kind = "hinted"
    blackfly_c.stats1.total.kind = "hinted"
    blackfly_c.cam.ensure_nonblocking()
except Exception as exc:
    print(exc)
    print("\n Unable to initiate blackfly camera. Something is wrong... ")
    pass
