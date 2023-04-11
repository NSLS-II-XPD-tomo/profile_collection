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
    StatsPlugin,
    ProcessPlugin,
    ROIPlugin,
    CamBase,
)

from ophyd.areadetector.filestore_mixins import (
    FileStoreTIFFIterativeWrite,
    FileStoreHDF5IterativeWrite,
    FileStoreTIFFSquashing,
    FileStoreIterativeWrite,
    FileStoreTIFF,
    FileStoreBase,
)


from ophyd import Component

from ophyd import Signal, EpicsSignal, EpicsSignalRO
from nslsii.ad33 import SingleTriggerV33, StatsPluginV33
from ophyd.areadetector import EpicsSignalWithRBV as SignalWithRBV

from ophyd.device import BlueskyInterface
from ophyd.device import DeviceStatus


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


class XPDTIFFPlugin(TIFFPlugin, FileStoreTIFFSquashing, FileStoreIterativeWrite):
    pass


class XPDAreaDetector(AreaDetector):
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
        self.stage_sigs.update([(self.cam.trigger_mode, "Int. Software")])
        self.proc.stage_sigs.update([(self.proc.filter_type, "RecursiveAve")])


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


class XPDContinuous(ContinuousAcquisitionTrigger, XPDAreaDetector):
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
