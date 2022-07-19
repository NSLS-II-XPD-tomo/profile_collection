print(f'Loading {__file__}')


def configure_area_det(det,acq_time,acq_period=None,exposure=None,num_exposures=1):
    
    if det.name == 'prosilica':
        acq_time = min(acq_time,25)
    
    if det.cam.acquire.get() == 0:
        yield from bps.abs_set(det.cam.acquire, 1, wait=True)

    if det.name == 'dexela': 
        yield from bps.abs_set(det.cam.acquire_time, max(acq_time,0.0625), wait=True)
        acq_time_rbv = det.cam.acquire_time.get()  
    else:
        yield from bps.abs_set(det.cam.acquire_time, acq_time, wait=True)
        acq_time_rbv = det.cam.acquire_time.get()        
        
    if det.name == 'dexela': 
        yield from bps.abs_set(det.cam.acquire_period, acq_time_rbv+0.005, wait=True)
        acq_period_rbv = det.cam.acquire_period.get()
    else:
        if acq_period is None:
            
            if det.name == 'blackfly':
                yield from bps.abs_set(det.cam.acquire_period, 0.1, wait=False)
            else:
                yield from bps.abs_set(det.cam.acquire_period, acq_time_rbv, wait=True)
            acq_period_rbv = det.cam.acquire_period.get()
        else:
            if det.name == 'blackfly':
                yield from bps.abs_set(det.cam.acquire_period, min(1,acq_period), wait=False)
            else:
                yield from bps.abs_set(det.cam.acquire_period, acq_period, wait=True)
            acq_period_rbv = det.cam.acquire_period.get()
                  
    if exposure is None:
        exposure = acq_time_rbv*10

    num_frames = np.ceil(exposure / acq_time_rbv)
    
    yield from bps.abs_set(det.images_per_set, num_frames, wait=True)
    
    yield from bps.abs_set(det.number_of_sets, num_exposures, wait=True) 
    
    if det.name == 'emergent': 
        print(">>>%s is configured as:\n acq_time = %.3fmsec;  acq_period = %.3fmsec; exposure = %.3fmsec \
    (num frames = %.2f); num_exposures = %d"%(det.name,acq_time_rbv,acq_period_rbv,exposure,num_frames,num_exposures))
    
    else:
        print(">>>%s is configured as:\n acq_time = %.3fsec;  acq_period = %.3fsec; exposure = %.3fsec \
    (num frames = %.2f); num_exposures = %d"%(det.name,acq_time_rbv,acq_period_rbv,exposure,num_frames,num_exposures))
    
    return 















"""
Simulatanous rocking multiple motors while detector is collecting
"""

import asyncio
import itertools

from ophyd import Signal
from bluesky import Msg
from bluesky.utils import ts_msg_hook

import bluesky.plan_stubs as bps
import bluesky.preprocessors as bpp

def multi_rock_per_shot(dets):
    def build_future(status):
        p_event = asyncio.Event(**RE._loop_for_kwargs)
        loop = asyncio.get_running_loop()

        def done_callback(status=None):
            task = loop.call_soon_threadsafe(p_event.set)

        status.add_callback(done_callback)

        return asyncio.ensure_future(p_event.wait())

    ### SET THIS TO YOUR REAL HARDWARE
    # x =
    # y =
    # th = 
    
    status_objects = {}
    future_factories = {}

    theta_gen = itertools.cycle([55, 65])
    x_gen = itertools.cycle([44, 46])
    yield Msg('checkpoint')
    th_satus = yield from bps.abs_set(th, next(theta_gen))
    th_future = build_future(th_satus)
    for d in dets:
        yield from bps.trigger(d, group='detectors')
    for y_target in np.linspace(-1, 1, 5):
        y_status = yield from bps.abs_set(y, y_target)
        y_future = build_future(y_status)

        while True:
            yield Msg(
                "wait_for",
                None,
                [lambda: y_future, lambda: th_future],
                return_when="FIRST_COMPLETED",
            )
            if th_satus.done:
                th_satus = yield from bps.abs_set(th, next(theta_gen))
                th_future = build_future(th_satus)
            if y_status.done:
                break

        x_target = next(x_gen)
        x_status = yield from bps.abs_set(x, x_target)
        x_future = build_future(x_status)

        while True:
            yield Msg(
                "wait_for",
                None,
                [lambda: x_future, lambda: th_future],
                return_when="FIRST_COMPLETED",
            )
            if th_satus.done:
                th_satus = yield from bps.abs_set(th, next(theta_gen))
                th_future = build_future(th_satus)
            if x_status.done:
                break
        yield from bps.wait(group='detectors')

    # create the event!
    yield from bps.create('primary')
    ret = {}  # collect and return readings to give plan access to them
    for d in dets:
        reading = (yield from bps.read(d))
        if reading is not None:
            ret.update(reading)
    yield from bps.save()                       
    return ret

"""
xpd_configuration['area_det']=pe2c
glbl['frame_acq_time']=0.2
glbl['dk_window']=3000
RE(_configure_area_det(120))
#x = diff_x
#y = diff_y
#th = th
%time uid = RE(count([pe2c],per_shot=multi_rock_per_shot))[0]
"""









