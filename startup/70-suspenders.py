print(f'Loading {__file__}')


from bluesky.suspenders import SuspendCeil,SuspendFloor


# quad_em_sus = SuspendCeil(quad_em, 0, resume_thresh=0)
# RE.install_suspender(quad_em_sus)

ring_current_sus = SuspendFloor(ring_current, 360, resume_thresh=395, sleep=60*15)
RE.install_suspender(ring_current_sus)


##RE.clear_suspenders()
