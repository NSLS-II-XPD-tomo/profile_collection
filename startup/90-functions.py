print(f'Loading {__file__}')


def configure_area_det(det,acq_time,acq_period=None,exposure=None,num_exposures=1):
    
    if det.name == 'prosilica':
        acq_time = min(acq_time,25)
    
    if det.cam.acquire.get() == 0:
        yield from bps.abs_set(det.cam.acquire, 1, wait=True)

    if det.name == 'dexela': 
        yield from bps.abs_set(det.cam.acquire_time, max(acq_time,0.1), wait=True)
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
