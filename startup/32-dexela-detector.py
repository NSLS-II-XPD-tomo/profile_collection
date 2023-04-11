print(f"Loading {__file__}")


try:
    # Dexela camera configurations:
    dexela_pv_prefix = "XF:28IDD-ES:2{Det:DEX}"
    dexela_c = XPDContinuous(
        dexela_pv_prefix,
        name="dexela",
        read_attrs=["tiff", "stats1.total"],
        plugin_name="tiff",
    )

    dexela_c.stage_sigs.update([(dexela_c.cam.trigger_mode, "Int. Software")])

    dexela_c.tiff.read_path_template = (
        f"/nsls2/data/xpd-new/legacy/raw/xpdd/{dexela_c.name}_data/%Y/%m/%d/"
    )
    dexela_c.tiff.write_path_template = f"J:\\{dexela_c.name}_data\\%Y\\%m\\%d\\"

    dexela_c.cam.bin_x.kind = "config"
    dexela_c.cam.bin_y.kind = "config"
    dexela_c.stats1.kind = "hinted"
    dexela_c.stats1.total.kind = "hinted"
    dexela_c.cam.ensure_nonblocking()
except Exception as exc:
    print(exc)
    print("\n Unable to initiate Dexela detector. Something is wrong... ")
    pass
