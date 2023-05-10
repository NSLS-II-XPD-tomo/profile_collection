print(f"Loading {__file__}")


try:
    # AlliedVision camera configurations:
    alliedvision_pv_prefix = "XF:28ID2-ES:2{Det:AV1}"
    alliedvision_c = XPDContinuous(
        alliedvision_pv_prefix,
        name="alliedvision",
        read_attrs=["hdf5", "stats1.total"],
        plugin_name="hdf5",
    )

    alliedvision_c.stage_sigs.update(
        [
            (alliedvision_c.cam.trigger_mode, "Off"),
            (alliedvision_c.cam.data_type, "UInt16"),
            (alliedvision_c.cam.color_mode, "Mono"),
        ]
    )

    alliedvision_c.proc.data_type_out.put("Float32")

    alliedvision_c.hdf5.read_path_template = (
        f"/nsls2/data/xpd-new/legacy/raw/xpdd/{alliedvision_c.name}_data/%Y/%m/%d/"
    )
    alliedvision_c.hdf5.write_path_template = (
        f"/nsls2/data/xpd-new/legacy/raw/xpdd/{alliedvision_c.name}_data/%Y/%m/%d/"
    )

    alliedvision_c.cam.bin_x.kind = "config"
    alliedvision_c.cam.bin_y.kind = "config"
    alliedvision_c.stats1.kind = "hinted"
    alliedvision_c.stats1.total.kind = "hinted"
    alliedvision_c.cam.ensure_nonblocking()
except Exception as exc:
    print(exc)
    print("\n Unable to initiate Allied Vision camera. Something is wrong... ")
    pass
