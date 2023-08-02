print(f"Loading {__file__}")


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

        # if image_mode_ != 2:
        #     yield from bps.abs_set(det.cam.image_mode, 2, wait=True)
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

        # if image_mode_ != 2:
        #     yield from bps.abs_set(det.cam.image_mode, 2, wait=True)
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
