print(f"Loading {__file__}")


# def configure_det(
#     det, acq_time=None, acq_period=None, exposure=None, num_exposures=1, sleep=0.2
# ):
#     if det.cam.acquire.get() == 0:
#         yield from bps.abs_set(det.cam.acquire, 1, wait=True)
#         time.sleep(0.1)

#     if acq_time is None:
#         acq_time = det.cam.acquire_time.get()

#     if exposure is None:
#         exposure = acq_time_rbv * 10

#     if det.name == "xs3":
#         yield from bps.abs_set(det.cam.acquire_time, max(acq_time, 0.001), wait=True)
#         acq_time_rbv = det.cam.acquire_time.get()
#         num_frames = np.ceil(exposure / acq_time_rbv)
#         yield from bps.abs_set(det.cam.num_images, num_frames, wait=True)
#         yield from bps.abs_set(det.proc_plugin.num_filter, num_frames, wait=True)
#         print(
#             ">>>%s is configured as:\n acq_time = %.3fsec; exposure = %.3fsec (num frames = %.2f) "
#             % (det.name, acq_time_rbv, exposure, num_frames)
#         )
#         return

#     if det.name == "dexela":
#         yield from bps.abs_set(det.cam.acquire_time, max(acq_time, 0.0625), wait=True)
#         acq_time_rbv = det.cam.acquire_time.get()
#     else:
#         yield from bps.abs_set(det.cam.acquire_time, acq_time, wait=True)
#         acq_time_rbv = det.cam.acquire_time.get()

#     if det.name == "dexela":
#         yield from bps.abs_set(det.cam.acquire_period, acq_time_rbv + 0.005, wait=True)
#         acq_period_rbv = det.cam.acquire_period.get()
#     else:
#         if acq_period is None:
#             if det.name == "blackfly":
#                 yield from bps.abs_set(det.cam.acquire_period, 0.1, wait=False)
#                 time.sleep(0.2)
#             else:
#                 if det.name == "alliedvision":
#                     pass
#                 elif det.name == "prosilica":
#                     yield from bps.abs_set(
#                         det.cam.acquire_period, max([0.115,acq_time_rbv]), wait=False)
#                 else:
#                     yield from bps.abs_set(
#                         det.cam.acquire_period, acq_time_rbv, wait=False)
#             acq_period_rbv = det.cam.acquire_period.get()
#         else:
#             if det.name == "blackfly":
#                 yield from bps.abs_set(
#                     det.cam.acquire_period, min(1, acq_period), wait=False)
#                 time.sleep(0.2)
#                 acq_period_rbv = det.cam.acquire_period.get()
#             elif det.name == "alliedvision":
#                 acq_period_rbv = det.cam.acquire_period.get()
#             else:
#                 yield from bps.abs_set(det.cam.acquire_period, acq_period, wait=False)
#                 acq_period_rbv = det.cam.acquire_period.get()

#     num_frames = np.ceil(exposure / acq_time_rbv)
#     yield from bps.abs_set(det.images_per_set, num_frames, wait=True)
#     yield from bps.abs_set(det.number_of_sets, num_exposures, wait=True)

#     if det.name == "emergent":
#         print(
#             ">>>%s is configured as:\n acq_time = %.3fmsec;  acq_period = %.3fmsec; exposure = %.3fmsec \
#     (num frames = %.2f); num_exposures = %d"
#             % (
#                 det.name,
#                 acq_time_rbv,
#                 acq_period_rbv,
#                 exposure,
#                 num_frames,
#                 num_exposures,
#             )
#         )
#     else:
#         print(
#             ">>>%s is configured as:\n acq_time = %.3fsec;  acq_period = %.3fsec; exposure = %.3fsec \
#     (num frames = %.2f); num_exposures = %d"
#             % (
#                 det.name,
#                 acq_time_rbv,
#                 acq_period_rbv,
#                 exposure,
#                 num_frames,
#                 num_exposures,
#             )
#         )

#     time.sleep(sleep)

#     return


def configure_det(
    det, acq_time=None, acq_period=None, exposure=None, num_exposures=None, sleep=None
):

    # get current values for acq_time, acq_period, image_mode, trigger_mode and acquire status

    # acq_time
    acq_time_ = det.cam.acquire_time.get()
    # acq_period
    acq_period_ = det.cam.acquire_period.get()
    # image_mode
    image_mode_ = det.cam.image_mode.get()
    # trigger_mode
    trigger_mode_ = det.cam.trigger_mode.get()

    # acquire status
    acquire_ = det.cam.acquire.get()

    if det.name == "prosilica":
        if acq_time != None:
            yield from bps.abs_set(det.cam.acquire_time, max(acq_time, 0.01), wait=True)
        else:
            yield from bps.abs_set(det.cam.acquire_time, acq_time_, wait=True)
        if acq_period != None:
            yield from bps.abs_set(
                det.cam.acquire_period, max(acq_period, 0.15), wait=True
            )
        else:
            yield from bps.abs_set(
                det.cam.acquire_period, max(acq_period_, 0.15), wait=True
            )
        if image_mode_ != 2:
            yield from bps.abs_set(det.cam.image_mode, 2, wait=True)
        if exposure is None:
            exposure = 4 * det.cam.acquire_time.get()
        else:
            exposure = max(0.01, exposure)
        num_frames = np.ceil(exposure / det.cam.acquire_time.get())
        yield from bps.abs_set(det.images_per_set, num_frames, wait=True)
        if num_exposures is None:
            num_exposures = 1
        yield from bps.abs_set(det.number_of_sets, num_exposures, wait=True)
        if acquire_ != 1:
            yield from bps.abs_set(det.cam.acquire, 1, wait=True)

    if det.name == "blackfly":
        if acq_time != None:
            yield from bps.abs_set(
                det.cam.acquire_time, max(acq_time, 0.001), wait=True
            )
        else:
            yield from bps.abs_set(det.cam.acquire_time, acq_time_, wait=True)

        if acq_period != None:
            yield from bps.abs_set(
                det.cam.acquire_period,
                max([det.cam.acquire_time.get(), acq_period, 0.02650]),
                wait=True,
            )
        else:
            yield from bps.abs_set(
                det.cam.acquire_period,
                max([det.cam.acquire_time.get(), 0.02650]),
                wait=True,
            )

        if image_mode_ != 2:
            yield from bps.abs_set(det.cam.image_mode, 2, wait=True)
        if exposure is None:
            exposure = 4 * det.cam.acquire_time.get()
        else:
            exposure = max(0.01, exposure)
        num_frames = np.ceil(exposure / det.cam.acquire_time.get())
        yield from bps.abs_set(det.images_per_set, num_frames, wait=True)
        if num_exposures is None:
            num_exposures = 1
        yield from bps.abs_set(det.number_of_sets, num_exposures, wait=True)
        if acquire_ != 1:
            yield from bps.abs_set(det.cam.acquire, 1, wait=True)

    if det.name == "emergent":
        if acq_time != None:
            yield from bps.abs_set(det.cam.acquire_time, max(acq_time, 1), wait=True)
        else:
            yield from bps.abs_set(det.cam.acquire_time, acq_time_, wait=True)

        if acq_period != None:
            yield from bps.abs_set(
                det.cam.acquire_period,
                max([det.cam.acquire_time.get(), acq_period, 1]),
                wait=True,
            )
        else:
            yield from bps.abs_set(
                det.cam.acquire_period,
                max([det.cam.acquire_time.get(), acq_period_]),
                wait=True,
            )

        if image_mode_ != 2:
            yield from bps.abs_set(det.cam.image_mode, 2, wait=True)
        if exposure is None:
            exposure = 4 * det.cam.acquire_time.get()
        else:
            exposure = max(1, exposure)
        num_frames = np.ceil(exposure / det.cam.acquire_time.get())
        yield from bps.abs_set(det.images_per_set, num_frames, wait=True)
        if num_exposures is None:
            num_exposures = 1
        yield from bps.abs_set(det.number_of_sets, num_exposures, wait=True)
        if acquire_ != 1:
            yield from bps.abs_set(det.cam.acquire, 1, wait=True)

    if det.name == "dexela":
        if acq_time != None:
            yield from bps.abs_set(det.cam.acquire_time, max(acq_time, 0.1), wait=True)
        else:
            yield from bps.abs_set(det.cam.acquire_time, acq_time_, wait=True)

        if acq_period != None:
            yield from bps.abs_set(
                det.cam.acquire_period,
                max([det.cam.acquire_time.get(), acq_period, 0.1]),
                wait=True,
            )
        else:
            yield from bps.abs_set(
                det.cam.acquire_period,
                max([det.cam.acquire_time.get(), 0.1]),
                wait=True,
            )

        if image_mode_ != 2:
            yield from bps.abs_set(det.cam.image_mode, 2, wait=True)
        if exposure is None:
            exposure = 4 * det.cam.acquire_time.get()
        else:
            exposure = max(0.1, exposure)
        num_frames = np.ceil(exposure / det.cam.acquire_time.get())
        yield from bps.abs_set(det.images_per_set, num_frames, wait=True)
        if num_exposures is None:
            num_exposures = 1
        yield from bps.abs_set(det.number_of_sets, num_exposures, wait=True)
        if acquire_ != 1:
            yield from bps.abs_set(det.cam.acquire, 1, wait=True)

    if det.name == "xs3":
        yield from bps.abs_set(det.cam.acquire_time, max(acq_time, 0.001), wait=True)
        acq_time_rbv = det.cam.acquire_time.get()
        num_frames = np.ceil(exposure / acq_time_rbv)
        yield from bps.abs_set(det.cam.num_images, num_frames, wait=True)
        yield from bps.abs_set(det.proc_plugin.num_filter, num_frames, wait=True)
        print(
            ">>>%s is configured as:\n acq_time = %.3fsec; exposure = %.3fsec (num frames = %.2f) "
            % (det.name, acq_time_rbv, exposure, num_frames)
        )
        return

    if det.name == "emergent":
        print(
            ">>>%s is configured as:\n acq_time = %.3fmsec;  acq_period = %.3fmsec; exposure = %.3fmsec \
    (num frames = %.2f); num_exposures = %d"
            % (
                det.name,
                det.cam.acquire_time.get(),
                det.cam.acquire_period.get(),
                exposure,
                num_frames,
                num_exposures,
            )
        )
    else:
        print(
            ">>>%s is configured as:\n acq_time = %.3fsec;  acq_period = %.3fsec; exposure = %.3fsec \
    (num frames = %.2f); num_exposures = %d"
            % (
                det.name,
                det.cam.acquire_time.get(),
                det.cam.acquire_period.get(),
                exposure,
                num_frames,
                num_exposures,
            )
        )


def oscillator(
    motor: ophyd.Device,
    oscillate_center: float,
    oscillate_range: float,
    oscillate_time: float,
):
    """
    Move motor from left to right (oscillate) for oscillate_time seconds.
    oscillate_center: center of motor position.
    oscillate_range: range of oscillation.
    oscillate_time: oscillate time in seconds.
    """

    t0 = time.time()

    while time.time() - t0 < oscillate_time:
        yield from bps.mv(motor, oscillate_center + oscillate_range)
        yield from bps.mv(motor, oscillate_center - oscillate_range)


def read_tiff_as_xarray(
    tiffpath, figsize=(6, 6), robust=True, plot=False, cbar=False, mode=None
):
    """
    Reads a tiff file as xarray
    """

    if mode == "prosilica":
        img = fabio.open(tiffpath).data
    else:
        img = tifffile.imread(tiffpath).astype("float32")

    da = xr.DataArray(
        data=img,
        coords=[np.arange(img.shape[0]), np.arange(img.shape[1])],
        dims=["pixel_y", "pixel_x"],
    )

    if plot:
        fig = plt.figure(figsize=figsize)

        ax = fig.add_subplot(1, 1, 1)

        if not cbar:
            xp = da.plot.imshow(
                ax=ax, robust=robust, yincrease=False, cmap="Greys_r", add_colorbar=cbar
            )
        else:
            xp = da.plot.imshow(
                ax=ax,
                robust=robust,
                yincrease=False,
                cmap="Greys_r",
                cbar_kwargs=dict(
                    orientation="vertical", pad=0.07, shrink=0.4, label="Intensity"
                ),
            )

        xp.axes.set_aspect("equal", "box")

        plt.tight_layout()

    return da
