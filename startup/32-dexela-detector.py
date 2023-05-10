print(f"Loading {__file__}")


try:
    # Dexela camera configurations:
    dexela_pv_prefix = "XF:28IDD-ES:2{Det:DEX}"
    dexela_c = XPDContinuous(
        dexela_pv_prefix,
        name="dexela",
        read_attrs=["hdf5", "stats1.total"],
        plugin_name="hdf5",
    )

    dexela_c.stage_sigs.update(
        [
            (dexela_c.cam.trigger_mode, "Int. Software"),
            (dexela_c.cam.data_type, "UInt16"),
            (dexela_c.cam.color_mode, "Mono"),
        ]
    )

    dexela_c.proc.data_type_out.put("Float32")

    dexela_c.hdf5.read_path_template = (
        f"/nsls2/data/xpd-new/legacy/raw/xpdd/{dexela_c.name}_data/%Y/%m/%d/"
    )
    dexela_c.hdf5.write_path_template = f"J:\\{dexela_c.name}_data\\%Y\\%m\\%d\\"

    dexela_c.cam.bin_x.kind = "config"
    dexela_c.cam.bin_y.kind = "config"
    dexela_c.stats1.kind = "hinted"
    dexela_c.stats1.total.kind = "hinted"
    dexela_c.cam.ensure_nonblocking()

except Exception as exc:
    print(exc)
    print("\n Unable to initiate Dexela detector (hdf). Something is wrong... ")
    pass
