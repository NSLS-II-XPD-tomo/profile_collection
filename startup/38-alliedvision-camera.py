print(f"Loading {__file__}")


alliedvision_pv_prefix = "XF:28ID2-ES:2{Det:AV1}"


try:
    alliedvision_hdf5 = XPDAreaDetector_hdf5_mdk(
        alliedvision_pv_prefix,
        name="alliedvision",
        read_attrs=["hdf5", "stats1.total"],
    )

    alliedvision_hdf5.stage_sigs.update(
        [
            # (alliedvision_hdf5.cam.trigger_mode, "Internal"),
            (alliedvision_hdf5.cam.image_mode, "Multiple"),
            (alliedvision_hdf5.cam.data_type, "UInt8"),
            (alliedvision_hdf5.cam.color_mode, "Mono"),
        ]
    )

    alliedvision_hdf5.proc.data_type_out.put("UInt16")

    alliedvision_hdf5.hdf5.read_path_template = (
        f"/nsls2/data/xpd-new/legacy/raw/xpdd/{alliedvision_hdf5.name}_data/%Y/%m/%d/"
    )
    alliedvision_hdf5.hdf5.write_path_template = (
        f"J:\\{alliedvision_hdf5.name}_data\\%Y\\%m\\%d\\"
    )

    alliedvision_hdf5.cam.bin_x.kind = "config"
    alliedvision_hdf5.cam.bin_y.kind = "config"
    alliedvision_hdf5.stats1.kind = "hinted"
    alliedvision_hdf5.stats1.total.kind = "hinted"
    alliedvision_hdf5.cam.ensure_nonblocking()

    warmup_det(alliedvision_hdf5)


except Exception as exc:
    print(exc)
    print("\n Unable to initiate Alliedvision camera (hdf). Something is wrong... ")
    pass


try:
    alliedvision_tiff = XPDAreaDetector_tiff_mdk(
        alliedvision_pv_prefix,
        name="alliedvision",
        read_attrs=["tiff", "stats1.total"],
        plugin_name="tiff",
    )

    alliedvision_tiff.stage_sigs.update(
        [
            # (alliedvision_tiff.cam.trigger_mode, "Internal"),
            (alliedvision_tiff.cam.image_mode, 2),
            (alliedvision_tiff.cam.data_type, "UInt8"),
            (alliedvision_tiff.cam.color_mode, "Mono"),
        ]
    )

    alliedvision_tiff.proc.data_type_out.put("UInt16")

    alliedvision_tiff.tiff.read_path_template = (
        f"/nsls2/data/xpd-new/legacy/raw/xpdd/{alliedvision_tiff.name}_data/%Y/%m/%d/"
    )
    alliedvision_tiff.tiff.write_path_template = (
        f"J:\\{alliedvision_tiff.name}_data\\%Y\\%m\\%d\\"
    )

    alliedvision_tiff.cam.bin_x.kind = "config"
    alliedvision_tiff.cam.bin_y.kind = "config"
    alliedvision_tiff.stats1.kind = "hinted"
    alliedvision_tiff.stats1.total.kind = "hinted"
    alliedvision_tiff.cam.ensure_nonblocking()


except Exception as exc:
    print(exc)
    print("\n Unable to initiate Alliedvision camera (tiff). Something is wrong... ")
    pass
