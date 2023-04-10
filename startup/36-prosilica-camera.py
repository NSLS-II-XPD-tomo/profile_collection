print(f"Loading {__file__}")


try:

    class XPDContinuous_rgb(ContinuousAcquisitionTrigger, XPDAreaDetector):
        def make_data_key(self):
            source = "PV:{}".format(self.prefix)
            # This shape is expected to match arr.shape for the array.
            shape = (
                self.number_of_sets.get(),
                self.cam.array_size.array_size_y.get(),
                self.cam.array_size.array_size_x.get(),
                3,
            )
            return dict(
                shape=shape, source=source, dtype="array", external="FILESTORE:"
            )

        pass

    # Prosilica camera configurations:
    prosilica_pv_prefix = "XF:28IDD-BI{Det-Sample:1}"
    prosilica_c = XPDContinuous_rgb(
        prosilica_pv_prefix,
        name="prosilica",
        read_attrs=["tiff", "stats1.total"],
        plugin_name="tiff",
    )

    prosilica_c.stage_sigs.update([(prosilica_c.cam.trigger_mode, "Free Run")])

    prosilica_c.tiff.read_path_template = (
        f"/nsls2/data/xpd-new/legacy/raw/xpdd/{prosilica_c.name}_data/%Y/%m/%d/"
    )
    prosilica_c.tiff.write_path_template = (
        f"/nsls2/data/xpd-new/legacy/raw/xpdd/{prosilica_c.name}_data/%Y/%m/%d/"
    )

    prosilica_c.cam.bin_x.kind = "config"
    prosilica_c.cam.bin_y.kind = "config"
    prosilica_c.stats1.kind = "hinted"
    prosilica_c.stats1.total.kind = "hinted"
    prosilica_c.cam.ensure_nonblocking()
except Exception as exc:
    print(exc)
    print("\n Unable to initiate prosilica camera. Something is wrong... ")
    pass
