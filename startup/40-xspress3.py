print(f'Loading {__file__}')

import os
from ophyd import Component
from ophyd.areadetector import Xspress3Detector, ProcessPlugin
from nslsii.areadetector.xspress3 import (
    Xspress3Trigger,
    Xspress3HDF5Plugin,
    build_xspress3_class,
)
from ophyd.status import SubscriptionStatus


class XPDDXspress3Trigger(Xspress3Trigger):
    def new_acquire_status(self):
        device_status = super().new_acquire_status()

        def hdf5plugin_done_callback(old_value, value, **kwargs):
            print(f"old_value = {old_value}\nnew_value = {value}")
            print(f"kwargs = {kwargs}")
            expected_frames = int(self.cam.num_images.get() / self.proc_plugin.num_filter.get())
            if old_value != value and value == expected_frames:
                return True
            else:
                return False

        hdf5plugin_status = SubscriptionStatus(self.hdf5plugin.array_counter,
                                               hdf5plugin_done_callback,
                                               run=False)

        return device_status & hdf5plugin_status

    def trigger(self):
        self.hdf5plugin.array_counter.put(0)
        st = super().trigger()
        return st



xs3_pv_prefix = "XF:28ID2-ES{Xsp:1}:"
xs3_root_path = "/nsls2/data/xpd-new/legacy/raw/xpdd/xspress3_data/"
xs3_data_dir = os.path.join(xs3_root_path, "%Y/%m/%d")

xspress3_class = build_xspress3_class(
        channel_numbers=(1,),
        mcaroi_numbers=(1,),
        image_data_key="data",
        xspress3_parent_classes=(Xspress3Detector, XPDDXspress3Trigger),
        extra_class_members={
            "hdf5plugin": Component(
                Xspress3HDF5Plugin,
                name="h5p",
                prefix=f"{xs3_pv_prefix}HDF1:",
                root_path=xs3_root_path,
                path_template=xs3_data_dir,
                resource_kwargs={},
            ),
            "proc_plugin": Component(ProcessPlugin, 'Proc1:')
        },
    )

xs3 = xspress3_class(prefix=xs3_pv_prefix, name="xs3")

# Hints for live plots/table.
# Hint: check the status of the fields with `xs3.summary()`. The hinted
# components should be marked with '*'. Example:
#
# In [1]: xs3.summary()
# data keys (* hints)
# -------------------
#  xs3_channel01_data
# *xs3_channel01_mcaroi01_total_rbv
#
# read attrs
# ----------
# channel01            GeneratedXspress3Channel('xs3_channel01')
# channel01.sca        Sca                 ('xs3_channel01_sca')
# channel01.mca        Mca                 ('xs3_channel01_mca')
# ...

xs3.channel01.kind = "normal"
xs3.channel01.data.kind = "normal"
xs3.channel01.mcaroi01.kind = 'hinted'
xs3.channel01.mcaroi01.total_rbv.kind = 'hinted'
