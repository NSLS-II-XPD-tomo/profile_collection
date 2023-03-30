print(f"Loading {__file__}")


class XPDBlackfly(XPDDetector):
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

    pixel_size = Component(Signal, value=0.00345, kind="config")
    detector_type = Component(Signal, value="Blackfly S", kind="config")

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
        self.stage_sigs.update([(self.cam.acquire, 1)])
        self.stage_sigs.update([(self.cam.trigger_mode, "Off")])
        self.proc.stage_sigs.update([(self.proc.filter_type, "RecursiveAve")])


class BlackflyContinuous(ContinuousAcquisitionTrigger, XPDBlackfly):
    def make_data_key(self):
        source = "PV:{}".format(self.prefix)
        # This shape is expected to match arr.shape for the array.
        shape = (
            self.number_of_sets.get(),
            self.cam.array_size.array_size_y.get(),
            self.cam.array_size.array_size_x.get(),
        )
        return dict(shape=shape, source=source, dtype="array", external="FILESTORE:")

    pass


try:
    # Blackfly camera configurations:
    blackfly_pv_prefix = "XF:28IDD-BI{Det-BlackFly}"
    blackfly_c = BlackflyContinuous(
        blackfly_pv_prefix,
        name="blackfly",
        read_attrs=["tiff", "stats1.total"],
        plugin_name="tiff",
    )

    blackfly_c.tiff.read_path_template = (
        f"/nsls2/data/xpd-new/legacy/raw/xpdd/{blackfly_c.name}_data/%Y/%m/%d/"
    )
    blackfly_c.tiff.write_path_template = (
        f"/nsls2/data/xpd-new/legacy/raw/xpdd/{blackfly_c.name}_data/%Y/%m/%d/"
    )
    blackfly_c.cam.bin_x.kind = "config"
    blackfly_c.cam.bin_y.kind = "config"
    blackfly_c.detector_type.kind = "config"
    blackfly_c.stats1.kind = "hinted"
    blackfly_c.stats1.total.kind = "hinted"
    blackfly_c.cam.ensure_nonblocking()
except Exception as exc:
    print(exc)
    print("\n Unable to initiate blackfly camera. Something is wrong... ")
    pass
