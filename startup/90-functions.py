
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





def md_getter():
    
    import time
    
    md = {}
    
    md['time'] = time.time()
    
    md['md_time'] = time.strftime('%Y/%m/%d - %H:%M:%S')
    
    
    for f in [Filters.flt1,Filters.flt2,Filters.flt3,Filters.flt4]:
        md[f.name] = f.get()    
    
    
    for m in [FastShutter,
              mTopX, 
              mTopY, 
              mTopZ, 
              mPhi,
              ePhi,
              mRoll, 
              mPitch,
              mBaseX,
              mBaseY,
              mDexelaPhi,
              mQuestarX,
              mBeamStopY,
              mHexapodsZ,
              mSlitsYGap,    
              mSlitsYCtr,    
              mSlitsXGap,    
              mSlitsXCtr,    
              mSlitsTop,     
              mSlitsBottom,  
              mSlitsOutboard,
              mSlitsInboard, 
              mSigrayX,    
              mSigrayY,    
              mSigrayZ,    
              mSigrayPitch,
              mSigrayYaw,
             ]:
            md[m.name] = float('%.4f'%m.position)

    sSmartPodUnit.set(0)
    time.sleep(0.2)
    sSmartPodSync.set(1)
    time.sleep(0.2)
    for s in [
             sSmartPodUnit, 
             sSmartPodTrasZ,
             sSmartPodTrasX,
             sSmartPodTrasY,
             sSmartPodRotZ, 
             sSmartPodRotX, 
             sSmartPodRotY, 
             sSmartPodSync, 
             sSmartPodMove, 
             ]:
            md['%s_0'%s.name] = float('%.5f'%s.get())            
            
    sSmartPodUnit.set(1)
    time.sleep(0.2)
    sSmartPodSync.set(1)
    time.sleep(0.2)
    for s in [
             sSmartPodUnit, 
             sSmartPodTrasZ,
             sSmartPodTrasX,
             sSmartPodTrasY,
             sSmartPodRotZ, 
             sSmartPodRotX, 
             sSmartPodRotY, 
             sSmartPodSync, 
             sSmartPodMove, 
             ]:
            md['%s_1'%s.name] = float('%.5f'%s.get())    
    
    for s in [
             pdu1,pdu2,pdu3,pdu4,ring_current 
             ]:
            md[s.name] = float('%.2f'%s.get())  
            
    return md




              
              
              
              
def beam_on(shutter_motor=None,sleep=0.1):
    if shutter_motor is None:
        shutter_motor =  FastShutter
    shutter_motor.move(0,wait=True)
    time.sleep(sleep)

def beam_off(shutter_motor=None,sleep=0.1):
    if shutter_motor is None:
        shutter_motor =  FastShutter
    shutter_motor.move(-47,wait=True)
    time.sleep(sleep)
    
    
        
            
def pud_switcher(ipdu, state='off', verbose=False):
    
    pdus = (pdu1,pdu2,pdu3,pdu4)
    
    if state == 'on' or state == 1:
        current_state = pdus[ipdu].get()
        if current_state == 1:
            if verbose:
                print('it is already on!')
        else:
            pdus[ipdu].set(1)
            time.sleep(0.1)

    if state == 'off' or state == 0:
        current_state = pdus[ipdu].get()
        if current_state == 0:
            if verbose:
                print('it is already off!')
        else:
            pdus[ipdu].set(0)
            time.sleep(0.1)
            
            


        
        
def read_tiff_as_xarray(tiffpath,
                       figsize=(6,6),
                       robust=True,
                       plot=False,
                       cbar=False,
                       mode=None):
    
    """
    Reads a tiff file as xarray
    """

    if mode == 'prosilica':
        img = fabio.open(tiffpath).data
    else:
        img = tifffile.imread(tiffpath).astype('float32')

    da = xr.DataArray(data=img,
                      coords=[np.arange(img.shape[0]),np.arange(img.shape[1])],
                      dims=['pixel_y', 'pixel_x'])

    if plot:

        fig = plt.figure(figsize=figsize)
        
        ax = fig.add_subplot(1,1,1)

        if not cbar:
            xp = da.plot.imshow(ax=ax,robust=robust,
                                yincrease=False,
                                cmap='Greys_r',
                                add_colorbar=cbar)
        else:
            xp = da.plot.imshow(ax=ax,robust=robust,
                                yincrease=False,
                                cmap='Greys_r',
                                cbar_kwargs=dict(orientation='vertical',
                                            pad=0.07, 
                                            shrink=0.4, 
                                            label='Intensity'))            
        
        xp.axes.set_aspect('equal', 'box')
     
        plt.tight_layout()

    
    return da
            

    
def print_det_keys(det_class):
    import pprint
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(det_class.tiff.__dict__)
    
    







    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
def counter_1det(det=None,
                 acq_time=0.1,exposure=1,
                 include_dark=False,
                 include_flat=False,flat_motor=None,flat_motor_move=2.5,
                 ):

    if include_dark:
        beam_off()
        print('\nINFO: Taking dark\n') 
        RE(configure_area_det(det,acq_time=acq_time,exposure=exposure))
        uid_dark = RE(count([det]),md={'task':'count-dark','acq_time':acq_time,'exposure':exposure})[0]
    else:
        uid_dark = 'none'
        
    if include_flat:
        print('\nINFO: Taking flat\n') 
        motor_current = flat_motor.position        
        flat_motor.move(motor_current+flat_motor_move,wait=True)
        print([motor_current,flat_motor.position])
        beam_on()
        RE(configure_area_det(det,acq_time=acq_time,exposure=exposure))
        uid_flat = RE(count([det]),md={'task':'count-flat',
                                       'acq_time':acq_time,
                                       'exposure':exposure,
                                       'flat_motor':flat_motor.name,
                                       'flat_motor_move':flat_motor_move})[0]
        beam_off()
        flat_motor.move(motor_current,wait=True) 
    else:
        uid_flat = 'none'
 
    beam_on()
    RE(configure_area_det(det,acq_time=acq_time,exposure=exposure)) 
    uid_light = RE(count([det]),md={'task':'count-light',
                                    'acq_time':acq_time,
                                    'exposure':exposure})[0]
    beam_off()
        

    return uid_light, uid_flat, uid_dark




def linescanner_1det(
                    det = None,
                    det_acq_time = 4,

                    include_dark = False,
                    det_exposure_dark = 4,    

                    include_flat=False,
                    flat_motor=None,
                    flat_motor_move=2.5,
    
                    det_exposure_linescan = 4,
                    motor = None,
                    motor_start = None,
                    motor_stop  = None,
                    motor_nstep = 11,

                    come_back = True,

                    ):

    if include_dark:
        beam_off()
        print('\n>>>> Taking dark\n') 
        RE(configure_area_det(det,acq_time=det_acq_time,exposure=det_exposure_dark))
        uid_dark = RE(count([det]),md={'task':'dark','acq_time':det_acq_time,'exposure':det_exposure_dark})[0]
    else:
        uid_dark = 'none'
         
    if include_flat:
        print('\nINFO: Taking flat\n') 
        motor_current = flat_motor.position        
        flat_motor.move(motor_current+flat_motor_move,wait=True)
        print([motor_current,flat_motor.position])
        beam_on()
        RE(configure_area_det(det,acq_time=det_acq_time,exposure=det_exposure_dark))
        uid_flat = RE(count([det]),md={'task':'linescan-flat',
                                       'acq_time':det_acq_time,
                                       'exposure':det_exposure_dark,
                                       'flat_motor':flat_motor.name,
                                       'flat_motor_move':flat_motor_move})[0]
        beam_off()
        flat_motor.move(motor_current,wait=True) 
    else:
        uid_flat = 'none'        
        
    motor_current_pos = motor.position
    print('>>> %s @ %.3f'%(motor.name,motor_current_pos))

    RE(configure_area_det(det,acq_time=det_acq_time,exposure=det_exposure_linescan))
    beam_on()
    uid_linescan = RE(scan([det],motor,motor_start,motor_stop,motor_nstep),md={'task':'linescan','acq_time':det_acq_time,'exposure':det_exposure_linescan})[0]
    beam_off()
    
    if come_back:
        print('>>> Moving %s back to %.3f'%(motor.name,motor_current_pos))
        motor.move(motor_current_pos)
         
    return uid_linescan, uid_flat, uid_dark


    
    
    
    
    
    
    
    
    
    
    
    
    
def gridscanner_1det(    
                    det = None,
                    det_acq_time = 2,
                    include_dark = True,
                    det_exposure_dark = 2,
                    det_exposure_gridscan = 2,
    
                    include_flat=False,
                    flat_motor=None,
                    flat_motor_move=None,    

                    #put slowest motor first
                    motor1 = None,
                    motor1_start = None,
                    motor1_stop  = None,
                    motor1_nstep = None,

                    motor2 = None,
                    motor2_start = None,
                    motor2_stop  = None,
                    motor2_nstep = None,

                    snake=True,
                    come_back = True,
    
                    ):





    if include_dark:
        print('\n>>>> Taking dark\n') 
        beam_off()
        RE(configure_area_det(det,acq_time=det_acq_time,exposure=det_exposure_dark))
        uid_dark = RE(count([det]),md={'task':'dark','acq_time':det_acq_time,'exposure':det_exposure_dark})[0]
    else:
        uid_dark = 'none'
         
    if include_flat:
        print('\nINFO: Taking flat\n') 
        motor_current = flat_motor.position        
        flat_motor.move(motor_current+flat_motor_move,wait=True)
        print([motor_current,flat_motor.position])
        beam_on()
        RE(configure_area_det(det,acq_time=det_acq_time,exposure=det_exposure_dark))
        uid_flat = RE(count([det]),md={'task':'linescan-flat',
                                       'acq_time':det_acq_time,
                                       'exposure':det_exposure_dark,
                                       'flat_motor':flat_motor.name,
                                       'flat_motor_move':flat_motor_move})[0]
        beam_off()
        flat_motor.move(motor_current,wait=True) 
    else:
        uid_flat = 'none' 

    motor1_current_pos = motor1.position
    print('>>> %s @ %.3f'%(motor1.name,motor1_current_pos))
    motor2_current_pos = motor2.position
    print('>>> %s @ %.3f'%(motor2.name,motor2_current_pos))


    beam_on()
    RE(configure_area_det(det,acq_time=det_acq_time,exposure=det_exposure_gridscan))

    uid_gridscan = RE(grid_scan([det],
                                motor1,motor1_start,motor1_stop,motor1_nstep,
                                motor2,motor2_start,motor2_stop,motor2_nstep,
                                snake_axes=snake),
                                md={'task':'gridscan','acq_time':det_acq_time,'exposure':det_exposure_gridscan})[0]
    beam_off()


    if come_back:
        print('>>> Moving %s back to %.3f'%(motor1.name,motor1_current_pos))
        motor1.move(motor1_current_pos)
        print('>>> Moving %s back to %.3f'%(motor2.name,motor2_current_pos))
        motor2.move(motor2_current_pos)    
    
    return uid_gridscan, uid_flat, uid_dark    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    




    
    
    
    
    
def ds_maker(js,return_ds=False):
    

################################################################################################################ 
########################################## count_1det ########################################################## 
################################################################################################################    
    if js['task'] == 'count_1det':  

        ds = xr.Dataset()


        if js['uid_dark'] != 'none':
            ds_dark = raw[js['uid_dark']].primary.read()
            hdr_dark = db[js['uid_dark']]
            md_dark = hdr_dark.start['md']
            da_dark = xr.DataArray(data=ds_dark['%s_image'%hdr_dark.start['detectors'][0]].squeeze(('time','dim_0')).values,
                  coords=[ds_dark.dim_1, ds_dark.dim_2],
                  dims=['%s_pixel_y'%(hdr_dark.start['detectors'][0]), '%s_pixel_x'%(hdr_dark.start['detectors'][0])],
                  attrs={'uid':js['uid_dark'],
                         'acq_time':md_dark['acq_time'],
                         'exposure':md_dark['exposure'],
                        }
                 )
            ds['dark'] = da_dark

        if js['uid_flat'] != 'none':
            ds_flat = raw[js['uid_flat']].primary.read()
            hdr_flat = db[js['uid_flat']]
            md_flat = hdr_flat.start['md']
            try:
                da_flat = xr.DataArray(data=ds_flat['%s_image'%hdr_flat.start['detectors'][0]].squeeze(('time','dim_0')).values,
                      coords=[ds_flat.dim_1, ds_flat.dim_2],
                      dims=['%s_pixel_y'%(hdr_flat.start['detectors'][0]), '%s_pixel_x'%(hdr_flat.start['detectors'][0])],
                      attrs={'uid':js['uid_flat'],
                             'acq_time':md_flat['acq_time'],
                             'exposure':md_flat['exposure'],
                             'flat_motor':md_flat['flat_motor'],
                             'flat_motor_move':md_flat['flat_motor_move'],
                            }
                     )
            except:
                print('uid_flat does not contain motor information')
                da_flat = xr.DataArray(data=ds_flat['%s_image'%hdr_flat.start['detectors'][0]].squeeze(('time','dim_0')).values,
                      coords=[ds_flat.dim_1, ds_flat.dim_2],
                      dims=['%s_pixel_y'%(hdr_flat.start['detectors'][0]), '%s_pixel_x'%(hdr_flat.start['detectors'][0])],
                      attrs={'uid':js['uid_flat'],
                             'acq_time':md_flat['acq_time'],
                             'exposure':md_flat['exposure']
                            }
                     )                
            ds['flat'] = da_flat

        ds_light = raw[js['uid_light']].primary.read()
        hdr_light = db[js['uid_light']]
        md_light = hdr_light.start['md']
        da_light = xr.DataArray(data=ds_light['%s_image'%hdr_light.start['detectors'][0]].squeeze(('time','dim_0')).values,
              coords=[ds_light.dim_1, ds_light.dim_2],
              dims=['%s_pixel_y'%(hdr_light.start['detectors'][0]), '%s_pixel_x'%(hdr_light.start['detectors'][0])],
              attrs={'uid':js['uid_light'],
                     'acq_time':md_light['acq_time'],
                     'exposure':md_light['exposure'],
                    }
             )
        ds['light'] = da_light

        z = ds.attrs.copy()
        z.update(md_getter())
        ds.attrs = z        

        comp = dict(zlib=False)
        encoding = {var: comp for var in ds.data_vars}
        ds.to_netcdf(js['nc_path'], encoding=encoding)  
        
        if return_ds:
            print(js['nc_path'])
            return ds
        else:
            return js['nc_path']   
    
    

    
    
    
################################################################################################################ 
########################################## linescan_1det ####################################################### 
################################################################################################################      
    if js['task'] == 'linescan_1det': 
        
        ds = xr.Dataset()


        ds_linescan = raw[js['uid_linescan']].primary.read()
        hdr_linescan = db[js['uid_linescan']]
        md_linescan = hdr_linescan.start['md']
        da_linescan = xr.DataArray(data=ds_linescan['%s_image'%hdr_linescan.start['detectors'][0]].squeeze('dim_0').values,
                  coords=[ds_linescan['%s'%hdr_linescan.start['motors'][0]], ds_linescan.dim_1, ds_linescan.dim_2],
                  dims=['%s'%(hdr_linescan.start['motors'][0]),'%s_pixel_y'%(hdr_linescan.start['detectors'][0]), '%s_pixel_x'%(hdr_linescan.start['detectors'][0])],
                  attrs={'uid':js['uid_linescan'],
                         'acq_time':md_linescan['acq_time'],
                         'exposure':md_linescan['exposure'],
                        }
                 )
        ds['linescan'] = da_linescan

        da_stats1_total = xr.DataArray(data=ds_linescan['%s_stats1_total'%hdr_linescan.start['detectors'][0]].values,
                  coords=[ds_linescan['%s'%hdr_linescan.start['motors'][0]]],
                  dims=[hdr_linescan.start['motors'][0]],
                 )
        ds['stats1_total'] = da_stats1_total

        ds = ds.assign_coords(time = ds_linescan.time)





        if js['uid_dark'] != 'none':
            ds_dark = raw[js['uid_dark']].primary.read()
            hdr_dark = db[js['uid_dark']]
            md_dark = hdr_dark.start['md']
            da_dark = xr.DataArray(data=ds_dark['%s_image'%hdr_dark.start['detectors'][0]].squeeze(('time','dim_0')).values,
                  coords=[ds_dark.dim_1, ds_dark.dim_2],
                  dims=['%s_pixel_y'%(hdr_dark.start['detectors'][0]), '%s_pixel_x'%(hdr_dark.start['detectors'][0])],
                  attrs={'uid':js['uid_dark'],
                         'acq_time':md_dark['acq_time'],
                         'exposure':md_dark['exposure'],
                        }
                 )
            ds['dark'] = da_dark  
            
            
            
            

        if js['uid_flat'] != 'none':
            ds_flat = raw[js['uid_flat']].primary.read()
            hdr_flat = db[js['uid_flat']]
            md_flat = hdr_flat.start['md']
            try:
                da_flat = xr.DataArray(data=ds_flat['%s_image'%hdr_flat.start['detectors'][0]].squeeze(('time','dim_0')).values,
                      coords=[ds_flat.dim_1, ds_flat.dim_2],
                      dims=['%s_pixel_y'%(hdr_flat.start['detectors'][0]), '%s_pixel_x'%(hdr_flat.start['detectors'][0])],
                      attrs={'uid':js['uid_flat'],
                             'acq_time':md_flat['acq_time'],
                             'exposure':md_flat['exposure'],
                             'flat_motor':md_flat['flat_motor'],
                             'flat_motor_move':md_flat['flat_motor_move'],
                            }
                     )
            except:
                print('uid_flat does not contain motor information')
                da_flat = xr.DataArray(data=ds_flat['%s_image'%hdr_flat.start['detectors'][0]].squeeze(('time','dim_0')).values,
                      coords=[ds_flat.dim_1, ds_flat.dim_2],
                      dims=['%s_pixel_y'%(hdr_flat.start['detectors'][0]), '%s_pixel_x'%(hdr_flat.start['detectors'][0])],
                      attrs={'uid':js['uid_flat'],
                             'acq_time':md_flat['acq_time'],
                             'exposure':md_flat['exposure']
                            }
                     )                
            ds['flat'] = da_flat            
            



        z = ds.attrs.copy()
        z.update(md_getter())
        ds.attrs = z        



        comp = dict(zlib=False)
        encoding = {var: comp for var in ds.data_vars}
        ds.to_netcdf(js['nc_path'], encoding=encoding)
    
    
        if return_ds:
            print(js['nc_path'])
            return ds
        else:
            return js['nc_path']      
    
    
    
    
    
    
################################################################################################################ 
########################################## gridscan_1det_2motors ############################################### 
################################################################################################################      

    if js['task'] == 'gridscan_1det_2motors': 

        ds = xr.Dataset()

        ds_gridscan = raw[js['uid_gridscan']].primary.read()
        hdr_gridscan = db[js['uid_gridscan']]
        md_gridscan = hdr_gridscan.start['md']

        if hdr_gridscan['start']['snaking'][1]:

            data_ds = ds_gridscan['%s_image'%hdr_gridscan.start['detectors'][0]].squeeze('dim_0').values
            data = np.zeros(((hdr_gridscan['start']['shape'][0],
                              hdr_gridscan['start']['shape'][1],
                              ds_gridscan.dim_1.shape[0],
                              ds_gridscan.dim_2.shape[0],
                             )))
            c = 0
            s = 0
            for i in range(hdr_gridscan['start']['shape'][0]):        
                if s == 0:
                    for j in range(hdr_gridscan['start']['shape'][1]):
                        data[i,j,:,:] = data_ds[c,:,:]
                        c += 1
                    s = 1
                else:
                    for j in range(hdr_gridscan['start']['shape'][1]):
                        data[i,j-hdr_gridscan['start']['shape'][1]+1,:,:] = data_ds[c,:,:]
                        c += 1
                    s = 0

        else:    
            data_ds = ds_gridscan['%s_image'%hdr_gridscan.start['detectors'][0]].squeeze('dim_0').values

            data = np.zeros(((hdr_gridscan['start']['shape'][0],
                              hdr_gridscan['start']['shape'][1],
                              ds_gridscan.dim_1.shape[0],
                              ds_gridscan.dim_2.shape[0],
                             )))

            c = 0
            for i in range(hdr_gridscan['start']['shape'][0]):
                for j in range(hdr_gridscan['start']['shape'][1]):
                    data[i,j,:,:] = data_ds[c,:,:]
                    c += 1


        da_gridscan = xr.DataArray(data=data,

                  coords=[
                        np.linspace(hdr_gridscan['start']['extents'][0][0],
                                    hdr_gridscan['start']['extents'][0][1],
                                    hdr_gridscan['start']['shape'][0]),
                        np.linspace(hdr_gridscan['start']['extents'][1][0],
                                    hdr_gridscan['start']['extents'][1][1],
                                    hdr_gridscan['start']['shape'][1]),
                          ds_gridscan.dim_1,
                          ds_gridscan.dim_2],

                  dims=[
                      '%s'%hdr_gridscan.start['motors'][0],
                        '%s'%hdr_gridscan.start['motors'][1],
                        '%s_pixel_y'%(hdr_gridscan.start['detectors'][0]),
                        '%s_pixel_x'%(hdr_gridscan.start['detectors'][0])],

                  attrs={'uid':js['uid_gridscan'],
                         'acq_time':md_gridscan['acq_time'],
                         'exposure':md_gridscan['exposure'],
                        }
                 )
        ds['gridscan'] = da_gridscan




    #         da_stats1_total = xr.DataArray(data=ds_linescan['%s_stats1_total'%hdr_linescan.start['detectors'][0]].values,
    #                   coords=[ds_linescan['%s'%hdr_linescan.start['motors'][0]]],
    #                   dims=[hdr_linescan.start['motors'][0]],
    #                  )
    #         ds['stats1_total'] = da_stats1_total

    #         ds = ds.assign_coords(time = ds_linescan.time)





        if js['uid_dark'] != 'none':
            ds_dark = raw[js['uid_dark']].primary.read()
            hdr_dark = db[js['uid_dark']]
            md_dark = hdr_dark.start['md']
            da_dark = xr.DataArray(data=ds_dark['%s_image'%hdr_dark.start['detectors'][0]].squeeze(('time','dim_0')).values,
                  coords=[ds_dark.dim_1, ds_dark.dim_2],
                  dims=['%s_pixel_y'%(hdr_dark.start['detectors'][0]), '%s_pixel_x'%(hdr_dark.start['detectors'][0])],
                  attrs={'uid':js['uid_dark'],
                         'acq_time':md_dark['acq_time'],
                         'exposure':md_dark['exposure'],
                        }
                 )
            ds['dark'] = da_dark  





        if js['uid_flat'] != 'none':
            ds_flat = raw[js['uid_flat']].primary.read()
            hdr_flat = db[js['uid_flat']]
            md_flat = hdr_flat.start['md']
            try:
                da_flat = xr.DataArray(data=ds_flat['%s_image'%hdr_flat.start['detectors'][0]].squeeze(('time','dim_0')).values,
                      coords=[ds_flat.dim_1, ds_flat.dim_2],
                      dims=['%s_pixel_y'%(hdr_flat.start['detectors'][0]), '%s_pixel_x'%(hdr_flat.start['detectors'][0])],
                      attrs={'uid':js['uid_flat'],
                             'acq_time':md_flat['acq_time'],
                             'exposure':md_flat['exposure'],
                             'flat_motor':md_flat['flat_motor'],
                             'flat_motor_move':md_flat['flat_motor_move'],
                            }
                     )
            except:
                print('uid_flat does not contain motor information')
                da_flat = xr.DataArray(data=ds_flat['%s_image'%hdr_flat.start['detectors'][0]].squeeze(('time','dim_0')).values,
                      coords=[ds_flat.dim_1, ds_flat.dim_2],
                      dims=['%s_pixel_y'%(hdr_flat.start['detectors'][0]), '%s_pixel_x'%(hdr_flat.start['detectors'][0])],
                      attrs={'uid':js['uid_flat'],
                             'acq_time':md_flat['acq_time'],
                             'exposure':md_flat['exposure']
                            }
                     )                
            ds['flat'] = da_flat            




        z = ds.attrs.copy()
        z.update(md_getter())
        ds.attrs = z        



        comp = dict(zlib=False)
        encoding = {var: comp for var in ds.data_vars}
        ds.to_netcdf(js['nc_path'], encoding=encoding)


        if return_ds:
            print(js['nc_path'])
            return ds
        else:
            return js['nc_path']   

    
    
    
    
    
    
    
    
    
"""  

LEGACY:   
    
def counter(det, 
            acq_time,
            num_exposure=1,
            expo_dark=0, 
            expo_bright=0, 
            auto_off=True
            ):

    
    ds = xr.Dataset()

    
    if expo_dark>0:

        beam_off()
        RE(configure_area_det(det,acq_time,exposure=expo_dark,num_exposure=num_exposure))
        uid = RE(count([det],num=1))[0]
        
        img = np.array(list(db[-1].data('%s_image'%(det.name))))

        img = img.mean(axis=(0,1))
        if det.name == 'prosilica':
            img = np.mean(img,-1)
        
        da = xr.DataArray(data=img.astype('float32'),
                  coords=[np.arange(img.shape[0]), np.arange(img.shape[1])],
                  dims=['pixel_y', 'pixel_x'],attrs=dict(uid=uid,
                                                         det=det.name,
                                                         acq_time=acq_time,
                                                         exposure=expo_dark)
                              )
        ds['dark'] = da
        


    if expo_bright>0:

        beam_on()
        RE(configure_area_det(det,acq_time,exposure=expo_bright,num_exposure=num_exposure))
        uid = RE(count([det],num=1))[0]
        
        if auto_off:
            beam_off()
        
        img = np.array(list(db[-1].data('%s_image'%(det.name))))

        img = img.mean(axis=(0,1))
        if det.name == 'prosilica':
            img = np.mean(img,-1)

        da = xr.DataArray(data=img.astype('float32'),
                  coords=[np.arange(img.shape[0]), np.arange(img.shape[1])],
                  dims=['pixel_y', 'pixel_x'],attrs=dict(uid=uid,
                                                         det=det.name,
                                                         acq_time=acq_time,
                                                         exposure=expo_bright)
                              )
        ds['bright'] = da



    md={'type': 'count',
        'time': time.time(),   
        'filter1':Filters.flt1.get(),
        'filter2':Filters.flt2.get(),
        'filter3':Filters.flt3.get(),
        'filter4':Filters.flt4.get(), 
        'mBaseX':mBaseX.position,
        'mBaseY':mBaseY.position,
        'mTopX':mTopX.position,
        'mTopY':mTopY.position, 
        'mTopZ':mTopZ.position,
        'mPhi':mPhi.position,  
        'mSlitsTop':mSlitsTop.position,     
        'mSlitsBottom':mSlitsBottom.position,    
        'mSlitsOutboard':mSlitsOutboard.position,   
        'mSlitsInboard':mSlitsInboard.position,     
        'mPitch':mPitch.position,       
        'mRoll':mRoll.position,      
        'mDexelaPhi':mDexelaPhi.position,       
        'mQuestarX':mQuestarX.position,      
        'mSigrayX':mSigrayX.position,    
        'mSigrayY':mSigrayY.position,    
        'mSigrayZ':mSigrayZ.position,    
        'mSigrayPitch':mSigrayPitch.position,   
        'mSigrayYaw':mSigrayYaw.position,     
        'FastShutter':FastShutter.position, 
        'RingCurrent':ring_current.get(),
        'mHexapodsZ':mHexapodsZ.position,
        'ePhi':ePhi.position,
       }

    ds.attrs = md
    
    
    return ds



def scanner(det, 
            motor,
            acq_time,
            num_exposure=1,
            expo_dark=0, 
            expo_bright=0, 
            
            motor_start = -0.1,
            motor_stop =  0.1,
            motor_nstep = 11, 
            
            come_back = False

            ):

    
    ds = xr.Dataset()
    
    motor_initial_pos = motor.position

    
    if expo_dark>0:

        beam_off()
        RE(configure_area_det(det,acq_time,exposure=expo_dark,num_exposure=1))
        uid = RE(count([det],num=1))[0]
        
        img = np.array(list(db[-1].data('%s_image'%(det.name))))
        if det.name == 'prosilica':
            img = np.mean(img,-1)
        img = img.mean(axis=(0,1))

        da = xr.DataArray(data=img.astype('float32'),
                  coords=[np.arange(img.shape[0]), np.arange(img.shape[1])],
                  dims=['pixel_y', 'pixel_x'],attrs=dict(uid=uid,
                                                         det=det.name,
                                                         acq_time=acq_time,
                                                         exposure=expo_dark)
                              )
        ds['dark'] = da
        


    if expo_bright>0:

        beam_on()
        RE(configure_area_det(det,acq_time,exposure=expo_bright,num_exposure=1))
        uid = RE(scan([det],motor,motor_start,motor_stop,motor_nstep))[0]
        beam_off()
        
        imgs = np.array(list(db[-1].data('%s_image'%(det.name))))
        if det.name == 'prosilica':
            imgs = np.mean(imgs,-1)
        imgs = imgs.mean(axis=(1))
        
        motor_pos = np.linspace(motor_start,motor_stop,motor_nstep)

        da = xr.DataArray(data=imgs.astype('float32'),
                  coords=[motor_pos, np.arange(imgs.shape[1]), np.arange(imgs.shape[2])],
                  dims=[motor.name,'pixel_y', 'pixel_x'],attrs=dict(uid=uid,
                                                         det=det.name,
                                                         acq_time=acq_time,
                                                         exposure=expo_bright,
                                                         motor=motor.name,
                                                         motor_start=motor_start,
                                                         motor_stop=motor_stop,
                                                         motor_nstep=motor_nstep,
                                                         motor_initial_pos=motor_initial_pos)
                              )
        ds['scan'] = da
        
        if come_back:
            print('moving back')
            motor.move(motor_initial_pos)



    md={'type': 'scan',
        'time': time.time(),   
        'filter1':Filters.flt1.get(),
        'filter2':Filters.flt2.get(),
        'filter3':Filters.flt3.get(),
        'filter4':Filters.flt4.get(), 
        'mBaseX':mBaseX.position,
        'mBaseY':mBaseY.position,
        'mTopX':mTopX.position,
        'mTopY':mTopY.position, 
        'mTopZ':mTopZ.position,
        'mPhi':mPhi.position,  
        'mSlitsTop':mSlitsTop.position,     
        'mSlitsBottom':mSlitsBottom.position,    
        'mSlitsOutboard':mSlitsOutboard.position,   
        'mSlitsInboard':mSlitsInboard.position,     
        'mPitch':mPitch.position,       
        'mRoll':mRoll.position,      
        'mDexelaPhi':mDexelaPhi.position,       
        'mQuestarX':mQuestarX.position,      
        'mSigrayX':mSigrayX.position,    
        'mSigrayY':mSigrayY.position,    
        'mSigrayZ':mSigrayZ.position,    
        'mSigrayPitch':mSigrayPitch.position,   
        'mSigrayYaw':mSigrayYaw.position,     
        'FastShutter':FastShutter.position, 
        'RingCurrent':ring_current.get(),
        'mHexapodsZ':mHexapodsZ.position,
        'ePhi':ePhi.position,
       }

    ds.attrs = md
    
    
    return ds

    
    
    
    
    

    
    
    
def counter(det,exposure_time=1, take_dark=False, take_bright=True, num_dark = 3, num_bright = 2):

    ds = xr.Dataset()

    
    if take_dark:
        set_detector(det,exposure_time=exposure_time,num_images=num_dark)

#         laser_off()
#         light1_off()
#         light2_off()

        beam_off()
        uid_dark = RE(count([det],num=1))[0]
        
        if det.name == 'prosilica':
            tiffs = get_tiff_list(hdr=db[-1])
            t0 = fabio.open(tiffs[0]).data
            img_dark = np.zeros((len(tiffs),t0.shape[0],t0.shape[1]))
            for e,t in enumerate(tiffs):
                img_dark[e,:,:] = fabio.open(tiffs[e]).data
        else:
            img_dark = np.array(list(db[-1].data('%s_image'%(det.name))))
            

        if len(img_dark.shape) == 4:
            img_dark = img_dark.mean(axis=1)
            img_dark = img_dark.mean(axis=0)
        if len(img_dark.shape) == 3:
            img_dark = img_dark.mean(axis=0)
            
        da_dark = xr.DataArray(data=img_dark.astype('float32'),
                  coords=[np.arange(img_dark.shape[0]), np.arange(img_dark.shape[1])],
                  dims=['pixel_y', 'pixel_x'],attrs=None
                 )
        ds['dark'] = da_dark
        dark_taken = 'true'
        
    else:
        uid_dark = 'none'
        num_dark = 'none'
        dark_taken = 'false'

    
    if take_bright:
        beam_on()
        set_detector(det,exposure_time=exposure_time,num_images=num_bright)
        uid_bright = RE(count([det],num=1))[0]
        beam_off()
        bright_taken = 'true'
    else:
        uid_bright = 'none'
        bright_taken = 'false'
        
        
    if bright_taken == 'true':
        if det.name == 'prosilica':
            tiffs = get_tiff_list(hdr=db[-1])
            t0 = fabio.open(tiffs[0]).data
            img_bright = np.zeros((len(tiffs),t0.shape[0],t0.shape[1]))
            for e,t in enumerate(tiffs):
                img_bright[e,:,:] = fabio.open(tiffs[e]).data
        else:
            img_bright = np.array(list(db[-1].data('%s_image'%(det.name))))

        if len(img_bright.shape) == 4:
            img_bright = img_bright.mean(axis=1)
            img_bright = img_bright.mean(axis=0)
        if len(img_bright.shape) == 3:
            img_bright = img_bright.mean(axis=0)


        da_bright = xr.DataArray(data=img_bright.astype('float32'),
                  coords=[np.arange(img_bright.shape[0]), np.arange(img_bright.shape[1])],
                  dims=['pixel_y', 'pixel_x'],attrs=None
                 )
        ds['bright'] = da_bright
        


    md={'type': 'count',
        'time': time.time(),
        'detector':det.name,
        'exposure_time':exposure_time,
        'dark_taken': dark_taken,
        'bright_taken': bright_taken,
        'uid_dark':uid_dark,
        'num_dark':num_dark, 
        'uid_bright':uid_bright,   
        'num_bright':num_bright,    
        'filter1':Filters.flt1.value,
        'filter2':Filters.flt2.value,
        'filter3':Filters.flt3.value,
        'filter4':Filters.flt4.value, 
        'mXBase':mXBase.position,
        'mYBase':mYBase.position,
        'mStackX':mStackX.position,
        'mStackY':mStackY.position, 
        'mStackZ':mStackZ.position,
        'mPhi':mPhi.position,  
        'mSlitsTop':mSlitsTop.position,     
        'mSlitsBottom':mSlitsBottom.position,    
        'mSlitsOutboard':mSlitsOutboard.position,   
        'mSlitsInboard':mSlitsInboard.position,     
        'mPitch':mPitch.position,       
        'mRoll':mRoll.position,      
        'mDexelaPhi':mDexelaPhi.position,       
        'mQuestarX':mQuestarX.position,      
        'mSigrayX':mSigrayX.position,    
        'mSigrayY':mSigrayY.position,    
        'mSigrayZ':mSigrayZ.position,    
        'mSigrayPitch':mSigrayPitch.position,   
        'mSigrayYaw':mSigrayYaw.position,     
        'FastShutter':FastShutter.position,      
       }

    ds.attrs = md
    
    
    return ds






def scanner(det,
            
            exposure_time=0.5, 
            
            take_dark=False, 
            num_dark = 10, 

            
            motor = mStackX,
            motor_start = -0.1,
            motor_stop =  0.1,
            motor_nstep = 11,


           ):

    ds = xr.Dataset()

    
    if take_dark:
        beam_off()
        set_detector(det,exposure_time=exposure_time,num_images=num_dark)
        uid_dark = RE(count([det],num=1))[0]
        
        if det.name == 'prosilica':
            tiffs = get_tiff_list(hdr=db[-1])
            t0 = fabio.open(tiffs[0]).data
            img_dark = np.zeros((len(tiffs),t0.shape[0],t0.shape[1]))
            for e,t in enumerate(tiffs):
                img_dark[e,:,:] = fabio.open(tiffs[e]).data
        else:
            img_dark = np.array(list(db[-1].data('%s_image'%(det.name))))
            
#         tiff_cleaner(hdr=db[-1])
        if len(img_dark.shape) == 4:
            img_dark = img_dark.mean(axis=0)
            img_dark = img_dark.mean(axis=0)
        elif len(img_dark.shape) == 3:
            img_dark = img_dark.mean(axis=0)
            
        da_dark = xr.DataArray(data=img_dark.astype('float32'),
                  coords=[np.arange(img_dark.shape[0]), np.arange(img_dark.shape[1])],
                  dims=['pixel_y', 'pixel_x'],attrs=None
                 )
        ds['dark'] = da_dark
        dark_taken = 'true'
        
    else:
        uid_dark = 'none'
        num_dark = 'none'
        dark_taken = 'false'

    
    beam_on()
    set_detector(det,exposure_time=exposure_time,num_images=1)
    uid_scan = RE(scan([det],motor,motor_start,motor_stop,motor_nstep))[0]
    beam_off()
    
    if det.name == 'prosilica':
        tiffs = get_tiff_list(hdr=db[-1])
        t0 = fabio.open(tiffs[0]).data
        imgs_scan = np.zeros((len(tiffs),t0.shape[0],t0.shape[1]))
        for e,t in enumerate(tiffs):
            imgs_scan[e,:,:] = fabio.open(tiffs[e]).data
    else:
        imgs_scan = np.array(list(db[-1].data('%s_image'%(det.name))))
        
    print(imgs_scan.shape)
    
    if len(imgs_scan.shape) == 4:
        imgs_scan = imgs_scan.mean(axis=1)
        
    motor_pos = np.linspace(motor_start,motor_stop,motor_nstep)
        
#     tiff_cleaner(hdr=db[-1])
   
    da_scan = xr.DataArray(data=imgs_scan.astype('float32'),
              coords=[motor_pos,np.arange(imgs_scan.shape[1]), np.arange(imgs_scan.shape[2])],
              dims=[motor.name,'pixel_y', 'pixel_x'],attrs=None
             )
    ds['scan'] = da_scan


    md={'type': 'scan',
        'time': time.time(),
        'detector':det.name,
        'exposure_time':exposure_time,
        'dark_taken': dark_taken,
        'uid_dark':uid_dark,
        'num_dark':num_dark, 
        'uid_bright':uid_scan,      
        'filter1':Filters.flt1.value,
        'filter2':Filters.flt2.value,
        'filter3':Filters.flt3.value,
        'filter4':Filters.flt4.value, 
        'mXBase':mXBase.position,
        'mYBase':mYBase.position,
        'mStackX':mStackX.position,
        'mStackY':mStackY.position, 
        'mStackZ':mStackZ.position,
        'mPhi':mPhi.position,  
        'mSlitsTop':mSlitsTop.position,     
        'mSlitsBottom':mSlitsBottom.position,    
        'mSlitsOutboard':mSlitsOutboard.position,   
        'mSlitsInboard':mSlitsInboard.position,     
        'mPitch':mPitch.position,       
        'mRoll':mRoll.position,      
        'mDexelaPhi':mDexelaPhi.position,       
        'mQuestarX':mQuestarX.position,      
        'mSigrayX':mSigrayX.position,    
        'mSigrayY':mSigrayY.position,    
        'mSigrayZ':mSigrayZ.position,    
        'mSigrayPitch':mSigrayPitch.position,   
        'mSigrayYaw':mSigrayYaw.position,     
        'FastShutter':FastShutter.position,      
       }

    ds.attrs = md
    
    
    return ds







    
    
def ds_saver(ds,save_to,save_str='_',zlib=False,dtype='float32'):
    comp = dict(zlib=zlib, dtype=dtype)
    encoding = {var: comp for var in ds.data_vars}
    ds.to_netcdf('%s/%d_%s.nc'%(save_to,ds.attrs['time'],save_str), encoding=encoding)    
    
    
    
    
    
    
    
    
    
    
    
    
    




def set_detector(det,exposure_time=1.0,num_images=1,sleep=0.5):
    if det.name == 'prosilica':
        det.proc.enable_filter.put(0,wait=True)
        det.cam.acquire_time.put(exposure_time)
        det.cam.acquire_period.put(0.5)     
        if num_images > 1:
            print('Multiple mode doesnt work well!!!')
            det.cam.stage_sigs['image_mode'] = 'Multiple'
            det.cam.num_images.put(num_images)
            det.cam.image_mode.put(1)       
        else:
            det.cam.stage_sigs['image_mode'] = 'Single'
            det.cam.num_images.put(1)
            det.cam.image_mode.put(0)
        det.cam.trigger_mode.put(0)
        det.unstage()
        time.sleep(sleep)    
        
    elif det.name == 'blackfly':
        det.proc.enable_filter.put(0,wait=True)
        det.cam.acquire_time.put(exposure_time)    
        det.cam.acquire_period.put(exposure_time)     
        if num_images > 1:
            det.cam.stage_sigs['image_mode'] = 'Multiple'
            det.cam.num_images.put(num_images)
            det.cam.image_mode.put(1)
        else:
            det.cam.stage_sigs['image_mode'] = 'Single'
            det.cam.num_images.put(1)
            det.cam.image_mode.put(0)
        det.cam.trigger_mode.put(0)
        det.unstage()
        time.sleep(sleep)
        
    elif det.name == 'emergent':
        det.proc.enable_filter.put(0,wait=True)
        det.cam.acquire_time.put(exposure_time)
        det.cam.acquire_period.put(exposure_time)             
        if num_images > 1:        
            det.cam.stage_sigs['image_mode'] = 'Multiple'    
            det.cam.stage_sigs['num_images'] = num_images
            det.cam.num_images.put(num_images)  
            det.cam.image_mode.put(1)        
        else:
            det.cam.stage_sigs['image_mode'] = 'Single'
            det.cam.num_images.put(1)
            det.cam.image_mode.put(0)
#         det.cam.trigger_mode.put(0)
        det.unstage()
        time.sleep(sleep)
        
    elif det.name == 'dexela':
        det.proc.enable_filter.put(0,wait=True)
        det.cam.stage_sigs['image_mode'] = 'Multiple'        
        det.cam.stage_sigs['trigger_mode'] = 'Int. Free Run'        
        det.cam.acquire_time.put(exposure_time)
        det.cam.acquire_period.put(exposure_time+0.02)
        if num_images > 1:
            det.cam.stage_sigs['image_mode'] = 'Multiple'
            det.cam.num_images.put(num_images)
            det.cam.image_mode.put(1)
        else:
            det.cam.stage_sigs['image_mode'] = 'Single'
            det.cam.num_images.put(1)
            det.cam.image_mode.put(0)
        det.cam.trigger_mode.put(0)
        det.unstage()
        time.sleep(sleep)



RE(bps.mv(Filters.flt1, 'Out')) 
RE(bps.mv(Filters.flt2, 'Out'))
RE(bps.mv(Filters.flt3, 'Out'))
RE(bps.mv(Filters.flt4, 'In'))
""" 
