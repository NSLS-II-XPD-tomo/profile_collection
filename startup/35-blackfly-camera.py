print(f"Loading {__file__}")


blackfly_pv_prefix = "XF:28IDD-BI{Det-BlackFly}"


try:
    blackfly_hdf5 = XPDAreaDetector_hdf5_mdk(
        blackfly_pv_prefix,
        name="blackfly",
        read_attrs=["hdf5", "stats1.total"],
    )

    blackfly_hdf5.stage_sigs.update(
        [
            (blackfly_hdf5.cam.trigger_mode, "Off"),
            (blackfly_hdf5.cam.image_mode, "Multiple"),
            (blackfly_hdf5.cam.data_type, "UInt16"),
            (blackfly_hdf5.cam.color_mode, "Mono"),
        ]
    )

    blackfly_hdf5.proc.data_type_out.put("UInt16")

    blackfly_hdf5.hdf5.read_path_template = (
        f"/nsls2/data/xpd-new/legacy/raw/xpdd/{blackfly_hdf5.name}_data/%Y/%m/%d/"
    )
    blackfly_hdf5.hdf5.write_path_template = (
        f"/nsls2/data/xpd-new/legacy/raw/xpdd/{blackfly_hdf5.name}_data/%Y/%m/%d/"
    )

    blackfly_hdf5.cam.bin_x.kind = "config"
    blackfly_hdf5.cam.bin_y.kind = "config"
    blackfly_hdf5.stats1.kind = "hinted"
    blackfly_hdf5.stats1.total.kind = "hinted"
    blackfly_hdf5.cam.ensure_nonblocking()

    warmup_det(blackfly_hdf5)


except Exception as exc:
    print(exc)
    print("\n Unable to initiate Blackfly camera (hdf). Something is wrong... ")
    pass


try:
    blackfly_tiff = XPDAreaDetector_tiff_mdk(
        blackfly_pv_prefix,
        name="blackfly",
        read_attrs=["tiff", "stats1.total"],
        plugin_name="tiff",
    )

    blackfly_tiff.stage_sigs.update(
        [
            (blackfly_tiff.cam.trigger_mode, "Off"),
            (blackfly_tiff.cam.image_mode, 2),
            (blackfly_tiff.cam.data_type, "UInt16"),
            (blackfly_tiff.cam.color_mode, "Mono"),
        ]
    )

    blackfly_tiff.proc.data_type_out.put("UInt16")

    blackfly_tiff.tiff.read_path_template = (
        f"/nsls2/data/xpd-new/legacy/raw/xpdd/{blackfly_tiff.name}_data/%Y/%m/%d/"
    )
    blackfly_tiff.tiff.write_path_template = (
        f"/nsls2/data/xpd-new/legacy/raw/xpdd/{blackfly_tiff.name}_data/%Y/%m/%d/"
    )

    blackfly_tiff.cam.bin_x.kind = "config"
    blackfly_tiff.cam.bin_y.kind = "config"
    blackfly_tiff.stats1.kind = "hinted"
    blackfly_tiff.stats1.total.kind = "hinted"
    blackfly_tiff.cam.ensure_nonblocking()


except Exception as exc:
    print(exc)
    print("\n Unable to initiate Blackfly camera (tiff). Something is wrong... ")
    pass
