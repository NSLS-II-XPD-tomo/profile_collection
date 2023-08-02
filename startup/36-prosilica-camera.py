print(f"Loading {__file__}")


prosilica_pv_prefix = "XF:28IDD-BI{Det-Sample:1}"


class XPDAreaDetector_hdf5_mdk_rgb(SingleTrigger, XPDAreaDetector_hdf5):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.cam.stage_sigs["image_mode"] = "Single"

    def make_data_key(self):
        source = "PV:{}".format(self.prefix)
        # This shape is expected to match arr.shape for the array.
        shape = (
            self.number_of_sets.get(),
            self.cam.array_size.array_size_y.get(),
            self.cam.array_size.array_size_x.get(),
            3,
        )
        return dict(shape=shape, source=source, dtype="array", external="FILESTORE:")

    pass


class XPDAreaDetector_tiff_mdk_rgb(ContinuousAcquisitionTrigger, XPDAreaDetector_tiff):
    def make_data_key(self):
        source = "PV:{}".format(self.prefix)
        # This shape is expected to match arr.shape for the array.
        shape = (
            self.number_of_sets.get(),
            self.cam.array_size.array_size_y.get(),
            self.cam.array_size.array_size_x.get(),
            3,
        )
        return dict(shape=shape, source=source, dtype="array", external="FILESTORE:")

    pass


try:
    prosilica_hdf5 = XPDAreaDetector_hdf5_mdk_rgb(
        prosilica_pv_prefix,
        name="prosilica",
        read_attrs=["hdf5", "stats1.total"],
    )

    prosilica_hdf5.stage_sigs.update(
        [
            (prosilica_hdf5.cam.trigger_mode, "Free Run"),
            (prosilica_hdf5.cam.image_mode, "Multiple"),
            (prosilica_hdf5.cam.data_type, "UInt8"),
            (prosilica_hdf5.cam.color_mode, "RGB1"),
        ]
    )

    prosilica_hdf5.proc.data_type_out.put("UInt8")

    prosilica_hdf5.hdf5.read_path_template = (
        f"/nsls2/data/xpd-new/legacy/raw/xpdd/{prosilica_hdf5.name}_data/%Y/%m/%d/"
    )
    prosilica_hdf5.hdf5.write_path_template = (
        f"/nsls2/data/xpd-new/legacy/raw/xpdd/{prosilica_hdf5.name}_data/%Y/%m/%d/"
    )

    prosilica_hdf5.cam.bin_x.kind = "config"
    prosilica_hdf5.cam.bin_y.kind = "config"
    prosilica_hdf5.stats1.kind = "hinted"
    prosilica_hdf5.stats1.total.kind = "hinted"
    prosilica_hdf5.cam.ensure_nonblocking()

    warmup_det(prosilica_hdf5)


except Exception as exc:
    print(exc)
    print("\n Unable to initiate Prosilica camera (hdf). Something is wrong... ")
    pass


try:
    prosilica_tiff = XPDAreaDetector_tiff_mdk_rgb(
        prosilica_pv_prefix,
        name="prosilica",
        read_attrs=["tiff", "stats1.total"],
        plugin_name="tiff",
    )

    prosilica_tiff.stage_sigs.update(
        [
            (prosilica_tiff.cam.trigger_mode, "Free Run"),
            (prosilica_tiff.cam.image_mode, 2),
            (prosilica_tiff.cam.data_type, "UInt8"),
            (prosilica_tiff.cam.color_mode, "Mono"),
        ]
    )

    prosilica_tiff.proc.data_type_out.put("UInt8")

    prosilica_tiff.tiff.read_path_template = (
        f"/nsls2/data/xpd-new/legacy/raw/xpdd/{prosilica_tiff.name}_data/%Y/%m/%d/"
    )
    prosilica_tiff.tiff.write_path_template = (
        f"/nsls2/data/xpd-new/legacy/raw/xpdd/{prosilica_tiff.name}_data/%Y/%m/%d/"
    )

    prosilica_tiff.cam.bin_x.kind = "config"
    prosilica_tiff.cam.bin_y.kind = "config"
    prosilica_tiff.stats1.kind = "hinted"
    prosilica_tiff.stats1.total.kind = "hinted"
    prosilica_tiff.cam.ensure_nonblocking()


except Exception as exc:
    print(exc)
    print("\n Unable to initiate Prosilica camera (tiff). Something is wrong... ")
    pass
