print(f"Loading {__file__}")


try:
    # Emergent camera configurations:
    emergent_pv_prefix = "XF:28IDD-EM1{EVT-Cam:1}"
    emergent_c = XPDContinuous(
        emergent_pv_prefix,
        name="emergent",
        read_attrs=["hdf5", "stats1.total"],
        plugin_name="hdf5",
    )

    emergent_c.stage_sigs.update(
        [
            (emergent_c.cam.trigger_mode, "Internal"),
            (emergent_c.cam.data_type, "UInt16"),
            (emergent_c.cam.color_mode, "Mono"),
            (emergent_c.cam.acquire, 1),
        ]
    )

    emergent_c.proc.data_type_out.put("Float32")

    emergent_c.hdf5.read_path_template = (
        f"/nsls2/data/xpd-new/legacy/raw/xpdd/{emergent_c.name}_data/%Y/%m/%d/"
    )
    emergent_c.hdf5.write_path_template = f"J:\\{emergent_c.name}_data\\%Y\\%m\\%d\\"

    emergent_c.cam.bin_x.kind = "config"
    emergent_c.cam.bin_y.kind = "config"
    emergent_c.stats1.kind = "hinted"
    emergent_c.stats1.total.kind = "hinted"
    emergent_c.cam.ensure_nonblocking()

    warmup_det(emergent_c)

except Exception as exc:
    print(exc)
    print("\n Unable to initiate Emergent camera. Something is wrong... ")
    pass
