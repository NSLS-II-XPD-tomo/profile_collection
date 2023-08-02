print(f"Loading {__file__}")


# Some of the code below is from
# https://github.com/NSLS-II-HXN/hxntools/blob/master/hxntools/detectors
# and
# https://github.com/NSLS-II-XPD/profile_collection

import ophyd
from ophyd.areadetector import (
    AreaDetector,
    ImagePlugin,
    TIFFPlugin,
    HDF5Plugin,
    StatsPlugin,
    ProcessPlugin,
    ROIPlugin,
    CamBase,
)
from ophyd.areadetector.plugins import HDF5Plugin_V33

from ophyd.areadetector.filestore_mixins import (
    FileStoreTIFFIterativeWrite,
    FileStoreHDF5IterativeWrite,
    FileStoreTIFFSquashing,
    FileStoreIterativeWrite,
    FileStoreTIFF,
    FileStoreBase,
    FileStorePluginBase,
)


from ophyd import Component

from ophyd import Signal, EpicsSignal, EpicsSignalRO
from nslsii.ad33 import SingleTriggerV33, StatsPluginV33
from ophyd.areadetector import EpicsSignalWithRBV as SignalWithRBV


from ophyd.device import BlueskyInterface
from ophyd.device import DeviceStatus


from ophyd.areadetector.trigger_mixins import SingleTrigger


from collections import OrderedDict


class XPDCamBase(CamBase):
    wait_for_plugins = Component(
        EpicsSignal, "WaitForPlugins", string=True, kind="config"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stage_sigs["wait_for_plugins"] = "Yes"

    def ensure_nonblocking(self):
        self.stage_sigs["wait_for_plugins"] = "Yes"
        for c in self.parent.component_names:
            cpt = getattr(self.parent, c)
            if cpt is self:
                continue
            if hasattr(cpt, "ensure_nonblocking"):
                #                 print(f'cpt: {cpt.name}')
                cpt.ensure_nonblocking()


# TIFF stuff
class XPDTIFFPlugin(TIFFPlugin, FileStoreTIFFSquashing, FileStoreIterativeWrite):
    pass


class XPDAreaDetector_tiff(AreaDetector):
    cam = Component(
        XPDCamBase,
        "cam1:",
        read_attrs=[],
        configuration_attrs=[
            "image_mode",
            "trigger_mode",
            "acquire_time",
            "acquire_period",
        ],
    )

    image = Component(ImagePlugin, "image1:")

    tiff = Component(
        XPDTIFFPlugin,
        "TIFF1:",
        write_path_template="/a/b/c/",
        read_path_template="/a/b/c",
        cam_name="cam",
        proc_name="proc",
        read_attrs=[],
        root="/nsls2/data/xpd-new/legacy/raw/xpdd",
    )

    proc = Component(ProcessPlugin, "Proc1:")

    # These attributes together replace `num_images`. They control
    # summing images before they are stored by the detector (a.k.a. "tiff
    # squashing").
    images_per_set = Component(Signal, value=1, add_prefix=())
    number_of_sets = Component(Signal, value=1, add_prefix=())

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
        self.proc.stage_sigs.update(
            [
                (self.proc.filter_type, "RecursiveAve"),
                (self.proc.data_type_out, "UInt16"),
            ]
        )


class ContinuousAcquisitionTrigger(BlueskyInterface):
    """
    This trigger mixin class records images when it is triggered.

    It expects the detector to *already* be acquiring, continously.
    """

    def __init__(self, *args, plugin_name=None, image_name=None, **kwargs):
        if plugin_name is None:
            raise ValueError("plugin name is a required keyword argument")
        super().__init__(*args, **kwargs)
        self._plugin = getattr(self, plugin_name)
        if image_name is None:
            image_name = "_".join([self.name, "image"])
        self._plugin.stage_sigs[self._plugin.auto_save] = "No"

        # self.cam.stage_sigs[self.cam.image_mode] = 'Continuous'
        # MT: For Emergent to work
        self.cam.stage_sigs["image_mode"] = "Continuous"
        self.cam.stage_sigs["acquire"] = 1

        self._plugin.stage_sigs[self._plugin.file_write_mode] = "Capture"
        self._image_name = image_name
        self._status = None
        self._num_captured_signal = self._plugin.num_captured
        self._num_captured_signal.subscribe(self._num_captured_changed)
        self._save_started = False

    def stage(self):
        if self.cam.acquire.get() != 1:
            raise RuntimeError(
                "The ContinuousAcuqisitionTrigger expects "
                "the detector to already be acquiring."
            )
        return super().stage()

    def trigger(self):
        "Trigger one acquisition."
        if not self._staged:
            raise RuntimeError(
                "This detector is not ready to trigger."
                "Call the stage() method before triggering."
            )
        self._save_started = False
        self._status = DeviceStatus(self)
        self._desired_number_of_sets = self.number_of_sets.get()
        self._plugin.num_capture.put(self._desired_number_of_sets)
        self.generate_datum(self._image_name, ttime.time())
        # reset the proc buffer, this needs to be generalized
        self.proc.reset_filter.put(1)
        self._plugin.capture.put(1)  # Now the TIFF plugin is capturing.
        return self._status

    def _num_captured_changed(self, value=None, old_value=None, **kwargs):
        "This is called when the 'acquire' signal changes."
        if self._status is None:
            return
        if value == self._desired_number_of_sets:
            # This is run on a thread, so exceptions might pass silently.
            # Print and reraise so they are at least noticed.
            try:
                self.tiff.write_file.put(1)
            except Exception as e:
                print(e)
                raise
            self._save_started = True
        if value == 0 and self._save_started:
            self._status._finished()
            self._status = None
            self._save_started = False


class XPDAreaDetector_tiff(ContinuousAcquisitionTrigger, XPDAreaDetector_tiff):
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


# HDF5 stuff
class FileStoreHDF5Squashing(FileStorePluginBase):
    r"""Write out 'squashed' HDF5

    .. note::

       See :class:`FileStoreBase` for the rest of the required parametrs

    This mixin will also configure the ``cam`` and ``proc`` plugins
    on the parent.

    This is useful to work around the dynamic range of detectors
    and minimizing disk spaced used by synthetically increasing
    the exposure time of the saved images.

    Parameters
    ----------
    images_per_set_name, number_of_sets_name : str, optional
        The names of the signals on the parent to get the
        images_pre_set and number_of_sets from.

        The total number of frames extracted from the camera will be
        :math:`number\_of\_sets * images\_per\_set` and result in
        ``number_of_sets`` frames in the HDF5 file each of which is the average of
        ``images_per_set`` frames from the detector.

        Defaults to ``'images_per_set'`` and ``'number_of_sets'``

    cam_name : str, optional
        The name of the :class:`~ophyd.areadetector.cam.CamBase`
        instance on the parent.

        Defaults to ``'cam'``

    proc_name : str, optional
        The name of the
        :class:`~ophyd.areadetector.plugins.ProcessPlugin` instance on
        the parent.

        Defaults to ``'proc1'``

    Notes
    -----

    This class in cooperative and expected to particpate in multiple
    inheritance, all ``*args`` and extra ``**kwargs`` are passed up the
    MRO chain.

    """

    def __init__(
        self,
        *args,
        images_per_set_name="images_per_set",
        number_of_sets_name="number_of_sets",
        cam_name="cam",
        proc_name="proc1",
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.filestore_spec = "AD_HDF5"  # spec name stored in resource doc
        self._ips_name = images_per_set_name
        self._num_sets_name = number_of_sets_name
        self._cam_name = cam_name
        self._proc_name = proc_name
        cam = getattr(self.parent, self._cam_name)
        proc = getattr(self.parent, self._proc_name)
        self.stage_sigs.update(
            [
                ("file_template", "%s%s_%6.6d.h5"),
                ("file_write_mode", "Stream"),
                ("capture", 1),
                (proc.nd_array_port, cam.port_name.get()),
                (proc.reset_filter, 1),
                (proc.enable_filter, 1),
                (proc.filter_type, "RecursiveAve"),
                (proc.auto_reset_filter, 1),
                (proc.filter_callbacks, 1),
                ("nd_array_port", proc.port_name.get()),
            ]
        )

    def get_frames_per_point(self):
        return getattr(self.parent, self._num_sets_name).get()

    def stage(self):
        # print(f"Before staging: {self._fn = }\n{self._fp = }")

        cam = getattr(self.parent, self._cam_name)
        proc = getattr(self.parent, self._proc_name)
        images_per_set = getattr(self.parent, self._ips_name).get()
        num_sets = getattr(self.parent, self._num_sets_name).get()

        self.stage_sigs.update(
            [
                (proc.num_filter, images_per_set),
                (cam.num_images, images_per_set * num_sets),
            ]
        )
        super().stage()
        resource_kwargs = {
            "frame_per_point": self.get_frames_per_point(),
        }
        self._generate_resource(resource_kwargs)
        # print(f"After staging: {self._fn = }\n{self._fp = }")


class XPDHDF5Plugin(HDF5Plugin_V33, FileStoreHDF5Squashing, FileStoreIterativeWrite):
    pass


class XPDAreaDetector_hdf5(AreaDetector):
    cam = Component(
        XPDCamBase,
        "cam1:",
        read_attrs=[],
        configuration_attrs=[
            "image_mode",
            "trigger_mode",
            "acquire_time",
            "acquire_period",
        ],
    )

    image = Component(ImagePlugin, "image1:")

    # tiff = Component(
    #     XPDTIFFPlugin,
    #     "TIFF1:",
    #     write_path_template="/a/b/c/",
    #     read_path_template="/a/b/c",
    #     cam_name="cam",
    #     proc_name="proc",
    #     read_attrs=[],
    # )

    hdf5 = Component(
        XPDHDF5Plugin,
        "HDF1:",
        write_path_template="/a/b/c/",
        read_path_template="/a/b/c",
        cam_name="cam",
        proc_name="proc",
        read_attrs=[],
        root="/nsls2/data/xpd-new/legacy/raw/xpdd",
    )

    proc = Component(ProcessPlugin, "Proc1:")

    # These attributes together replace `num_images`. They control
    # summing images before they are stored by the detector (a.k.a. "tiff
    # squashing").
    images_per_set = Component(Signal, value=1, add_prefix=())
    number_of_sets = Component(Signal, value=1, add_prefix=())

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
        self.proc.stage_sigs.update(
            [
                (self.proc.filter_type, "RecursiveAve"),
                (self.proc.data_type_out, "UInt16"),
            ]
        )


class XPDAreaDetector_hdf5(SingleTrigger, XPDAreaDetector_hdf5):
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
        )
        return dict(shape=shape, source=source, dtype="array", external="FILESTORE:")

    pass


def warmup_det(det):
    """
    Adapted from https://github.com/bluesky/ophyd/blob/7612b2c9de9d5bc16cf28eea79ba5c12553f3cc2/ophyd/areadetector/plugins.py#L966
    For hdf5 plugin "priming". ophyd version on;y supports Internal trigger mode.
    """

    if det.name == "dexela":
        warmup_sigs = OrderedDict(
            [
                (det.cam.array_callbacks, 1),
                (det.cam.image_mode, "Single"),
                (det.cam.trigger_mode, "Int. Free Run"),
                (det.cam.acquire_time, 1),
                (det.cam.acquire_period, 1),
                (det.cam.acquire, 1),
            ]
        )
    elif det.name == "prosilica":
        warmup_sigs = OrderedDict(
            [
                (det.cam.array_callbacks, 1),
                (det.cam.image_mode, "Single"),
                (det.cam.trigger_mode, "Free Run"),
                (det.cam.acquire_time, 1),
                (det.cam.acquire_period, 1),
                (det.cam.acquire, 1),
            ]
        )
    elif det.name == "blackfly":
        warmup_sigs = OrderedDict(
            [
                (det.cam.array_callbacks, 1),
                (det.cam.image_mode, "Single"),
                (det.cam.trigger_mode, "Off"),
                (det.cam.acquire_time, 1),
                (det.cam.acquire_period, 1),
                (det.cam.acquire, 1),
            ]
        )
    elif det.name == "emergent":
        warmup_sigs = OrderedDict(
            [
                (det.cam.array_callbacks, 1),
                (det.cam.image_mode, "Single"),
                (det.cam.trigger_mode, "Internal"),
                (det.cam.acquire_time, 1),
                (det.cam.acquire_period, 1),
                (det.cam.acquire, 1),
            ]
        )
    elif det.name == "alliedvision":
        warmup_sigs = OrderedDict(
            [
                (det.cam.array_callbacks, 1),
                (det.cam.image_mode, "Single"),
                # (det.cam.trigger_mode, "Off"),
                (det.cam.acquire_time, 1),
                # (det.cam.acquire_period, 1),
                (det.cam.acquire, 1),
            ]
        )
    elif det.name == "xs3":
        warmup_sigs = OrderedDict(
            [
                (det.cam.array_callbacks, 1),
                (det.cam.image_mode, "Single"),
                (det.cam.trigger_mode, "Internal"),
                (det.cam.acquire_time, 1),
                (det.cam.acquire_period, 1),
                (det.cam.acquire, 1),
            ]
        )

    original_vals = {sig: sig.get() for sig in warmup_sigs}

    for sig, val in warmup_sigs.items():
        ttime.sleep(0.1)
        sig.set(val).wait()

    ttime.sleep(2)

    for sig, val in reversed(list(original_vals.items())):
        ttime.sleep(0.1)
        sig.set(val).wait()


"""
/xx//site-packages/ophyd/areadetector/detectors.py
    def make_data_key(self):
        source = 'PV:{}'.format(self.prefix)
        # This shape is expected to match arr.shape for the array.
        #shape = (self.cam.num_images.get(),
                 #self.cam.array_size.array_size_y.get(),
                 #self.cam.array_size.array_size_x.get())
        #if proc plugin is being used
        shape = (self.number_of_sets.get(),
                 self.cam.array_size.array_size_y.get(),
                 self.cam.array_size.array_size_x.get())
                 
 
# for dtype_str issue==========================================================|
# git clone file:///nsls2/software/etc/tiled/ ~/.config/tiled 
# cd  ~/.config/tiled
# make_links.sh

# add this to xpdd_transforms.py

import copy

def patch_descriptor(doc):

    for cam in ["dexela", "blackfly", "prosilica", "emergent", "alliedvision"]:
        if f"{cam}_image" in doc["data_keys"]:
            doc = copy.deepcopy(doc)
            doc["data_keys"][f"{cam}_image"]["dtype_str"] = "<u2"

    for cam in ["prosilica",]:
        if f"{cam}_image" in doc["data_keys"]:
            doc = copy.deepcopy(doc)
            doc["data_keys"][f"{cam}_image"]["dtype_str"] = "<u1"

    return doc

===============================================================================|
"""
