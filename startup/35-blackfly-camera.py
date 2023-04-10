print(f"Loading {__file__}")


try:
    # Blackfly camera configurations:
    blackfly_pv_prefix = "XF:28IDD-BI{Det-BlackFly}"
    blackfly_c = XPDContinuous(
        blackfly_pv_prefix,
        name="blackfly",
        read_attrs=["tiff", "stats1.total"],
        plugin_name="tiff",
    )

    blackfly_c.stage_sigs.update([(blackfly_c.cam.trigger_mode, "Off")])

    blackfly_c.tiff.read_path_template = (
        f"/nsls2/data/xpd-new/legacy/raw/xpdd/{blackfly_c.name}_data/%Y/%m/%d/"
    )
    blackfly_c.tiff.write_path_template = (
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
