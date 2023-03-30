print(f"Loading {__file__}")


class XPDProsilica(XPDDetector):
    image = Component(ImagePlugin, "image1:")
    _default_configuration_attrs = XPDDetector._default_configuration_attrs + (
        "images_per_set",
        "number_of_sets",
        "pixel_size",
    )
    tiff = Component(
        XPDTIFFPlugin,
        "TIFF1:",
        write_path_template="/a/b/c/",
        read_path_template="/a/b/c",
        cam_name="cam",
        proc_name="proc",
        read_attrs=[],
    )

    proc = Component(ProcessPlugin, "Proc1:")

    # These attributes together replace `num_images`. They control
    # summing images before they are stored by the detector (a.k.a. "tiff
    # squashing").
    images_per_set = Component(Signal, value=1, add_prefix=())
    number_of_sets = Component(Signal, value=1, add_prefix=())

    pixel_size = Component(Signal, value=0.0055, kind="config")
    detector_type = Component(Signal, value="Prosilica GT2300C", kind="config")

    stats1 = Component(StatsPluginV33, "Stats1:", kind="hinted")
    stats2 = Component(StatsPluginV33, "Stats2:")
    stats3 = Component(StatsPluginV33, "Stats3:")
    stats4 = Component(StatsPluginV33, "Stats4:")

    roi1 = Component(ROIPlugin, "ROI1:")
    roi2 = Component(ROIPlugin, "ROI2:")
    roi3 = Component(ROIPlugin, "ROI3:")
    roi4 = Component(ROIPlugin, "ROI4:")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stage_sigs.update([(self.cam.trigger_mode, "Free Run")])
        self.proc.stage_sigs.update([(self.proc.filter_type, "RecursiveAve")])


class ProsilicaContinuous(ContinuousAcquisitionTrigger, XPDProsilica):
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
    # Prosilica camera configurations:
    prosilica_pv_prefix = "XF:28IDD-BI{Det-Sample:1}"
    prosilica_c = ProsilicaContinuous(
        prosilica_pv_prefix,
        name="prosilica",
        read_attrs=["tiff", "stats1.total"],
        plugin_name="tiff",
    )

    prosilica_c.tiff.read_path_template = (
        f"/nsls2/data/xpd-new/legacy/raw/xpdd/{prosilica_c.name}_data/%Y/%m/%d/"
    )
    prosilica_c.tiff.write_path_template = (
        f"/nsls2/data/xpd-new/legacy/raw/xpdd/{prosilica_c.name}_data/%Y/%m/%d/"
    )
    prosilica_c.cam.bin_x.kind = "config"
    prosilica_c.cam.bin_y.kind = "config"
    prosilica_c.detector_type.kind = "config"
    prosilica_c.stats1.kind = "hinted"
    prosilica_c.stats1.total.kind = "hinted"
    prosilica_c.cam.ensure_nonblocking()
except Exception as exc:
    print(exc)
    print("\n Unable to initiate prosilica camera. Something is wrong... ")
    pass
