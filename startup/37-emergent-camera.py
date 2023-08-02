print(f"Loading {__file__}")


emergent_pv_prefix = "XF:28IDD-EM1{EVT-Cam:1}"


try:
    emergent_hdf5 = XPDAreaDetector_hdf5_mdk(
        emergent_pv_prefix,
        name="emergent",
        read_attrs=["hdf5", "stats1.total"],
    )

    emergent_hdf5.stage_sigs.update(
        [
            (emergent_hdf5.cam.trigger_mode, "Internal"),
            (emergent_hdf5.cam.image_mode, "Multiple"),
            (emergent_hdf5.cam.data_type, "UInt16"),
            (emergent_hdf5.cam.color_mode, "Mono"),
        ]
    )

    emergent_hdf5.proc.data_type_out.put("UInt16")

    emergent_hdf5.hdf5.read_path_template = (
        f"/nsls2/data/xpd-new/legacy/raw/xpdd/{emergent_hdf5.name}_data/%Y/%m/%d/"
    )
    emergent_hdf5.hdf5.write_path_template = (
        f"J:\\{emergent_hdf5.name}_data\\%Y\\%m\\%d\\"
    )

    emergent_hdf5.cam.bin_x.kind = "config"
    emergent_hdf5.cam.bin_y.kind = "config"
    emergent_hdf5.stats1.kind = "hinted"
    emergent_hdf5.stats1.total.kind = "hinted"
    emergent_hdf5.cam.ensure_nonblocking()

    warmup_det(emergent_hdf5)


except Exception as exc:
    print(exc)
    print("\n Unable to initiate Emergent camera (hdf). Something is wrong... ")
    pass


try:
    emergent_tiff = XPDAreaDetector_tiff_mdk(
        emergent_pv_prefix,
        name="emergent",
        read_attrs=["tiff", "stats1.total"],
        plugin_name="tiff",
    )

    emergent_tiff.stage_sigs.update(
        [
            (emergent_tiff.cam.trigger_mode, "Internal"),
            (emergent_tiff.cam.image_mode, 2),
            (emergent_tiff.cam.data_type, "UInt16"),
            (emergent_tiff.cam.color_mode, "Mono"),
        ]
    )

    emergent_tiff.proc.data_type_out.put("UInt16")

    emergent_tiff.tiff.read_path_template = (
        f"/nsls2/data/xpd-new/legacy/raw/xpdd/{emergent_tiff.name}_data/%Y/%m/%d/"
    )
    emergent_tiff.tiff.write_path_template = (
        f"J:\\{emergent_tiff.name}_data\\%Y\\%m\\%d\\"
    )

    emergent_tiff.cam.bin_x.kind = "config"
    emergent_tiff.cam.bin_y.kind = "config"
    emergent_tiff.stats1.kind = "hinted"
    emergent_tiff.stats1.total.kind = "hinted"
    emergent_tiff.cam.ensure_nonblocking()


except Exception as exc:
    print(exc)
    print("\n Unable to initiate Emergent camera (tiff). Something is wrong... ")
    pass
