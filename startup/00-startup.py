print(f'Loading {__file__}')

import nslsii

# See docstring for nslsii.configure_base() for more details
nslsii.configure_base(get_ipython().user_ns,'xpdd', pbar=False, bec=True,
                      magics=True, mpl=True, epics_context=False, configure_logging=False)

RE.md['facility'] = 'NSLS-II'
RE.md['group'] = 'XPD'
RE.md['beamline_id'] = '28-ID-D'

import ophyd
from ophyd import EpicsMotor
from ophyd import EpicsSignal
from ophyd import EpicsSignalRO 

EpicsSignal.set_defaults(timeout=10, connection_timeout=10)


from databroker import catalog
raw = catalog['xpdd']


# general imports -------------

import numpy as np
import xarray as xr

import os
import shutil
import glob
import datetime

import copy 
from copy import deepcopy

import time
from time import gmtime, localtime, strftime

import matplotlib
import matplotlib.pyplot as plt
plt.rcParams.update({'figure.max_open_warning': 0})
