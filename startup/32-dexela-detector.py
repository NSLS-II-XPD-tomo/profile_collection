print(f"Loading {__file__}")


dexela_pv_prefix = "XF:28IDD-ES:2{Det:DEX}"


try:
    dexela_hdf5 = XPDAreaDetector_hdf5(
        dexela_pv_prefix,
        name="dexela",
        read_attrs=["hdf5", "stats1.total"],
    )

    dexela_hdf5.stage_sigs.update(
        [
            (dexela_hdf5.cam.trigger_mode, "Int. Fixed Rate"),
            (dexela_hdf5.cam.image_mode, "Multiple"),
            (dexela_hdf5.cam.data_type, "UInt16"),
            (dexela_hdf5.cam.color_mode, "Mono"),
        ]
    )

    dexela_hdf5.proc.data_type_out.put("UInt16")

    dexela_hdf5.hdf5.read_path_template = (
        f"/nsls2/data/xpd-new/legacy/raw/xpdd/{dexela_hdf5.name}_data/%Y/%m/%d/"
    )
    dexela_hdf5.hdf5.write_path_template = f"J:\\{dexela_hdf5.name}_data\\%Y\\%m\\%d\\"

    dexela_hdf5.cam.bin_x.kind = "config"
    dexela_hdf5.cam.bin_y.kind = "config"
    dexela_hdf5.stats1.kind = "hinted"
    dexela_hdf5.stats1.total.kind = "hinted"
    dexela_hdf5.cam.ensure_nonblocking()

    warmup_det(dexela_hdf5)


except Exception as exc:
    print(exc)
    print("\n Unable to initiate Dexela detector (hdf). Something is wrong... ")
    pass


try:
    dexela_tiff = XPDAreaDetector_tiff(
        dexela_pv_prefix,
        name="dexela",
        read_attrs=["tiff", "stats1.total"],
        plugin_name="tiff",
    )

    dexela_tiff.stage_sigs.update(
        [
            (dexela_tiff.cam.trigger_mode, "Int. Fixed Rate"),
            (dexela_tiff.cam.image_mode, "Multiple"),
            (dexela_tiff.cam.data_type, "UInt16"),
            (dexela_tiff.cam.color_mode, "Mono"),
        ]
    )

    dexela_tiff.proc.data_type_out.put("UInt16")

    dexela_tiff.tiff.read_path_template = (
        f"/nsls2/data/xpd-new/legacy/raw/xpdd/{dexela_tiff.name}_data/%Y/%m/%d/"
    )
    dexela_tiff.tiff.write_path_template = f"J:\\{dexela_tiff.name}_data\\%Y\\%m\\%d\\"

    dexela_tiff.cam.bin_x.kind = "config"
    dexela_tiff.cam.bin_y.kind = "config"
    dexela_tiff.stats1.kind = "hinted"
    dexela_tiff.stats1.total.kind = "hinted"
    dexela_tiff.cam.ensure_nonblocking()


except Exception as exc:
    print(exc)
    print("\n Unable to initiate Dexela detector (tiff). Something is wrong... ")
    pass
