print(f"Loading {__file__}")


# Smartpod for hexapods
sSmartPodUnit = EpicsSignal("XF:28IDD-ES:2{SPod:1}Unit-SP", name="sSmartPodUnit")
sSmartPodTrasZ = EpicsSignal("XF:28IDD-ES:2{SPod:1-Ax:1}Pos-SP", name="sSmartPodTrasZ")
sSmartPodTrasX = EpicsSignal("XF:28IDD-ES:2{SPod:1-Ax:2}Pos-SP", name="sSmartPodTrasX")
sSmartPodTrasY = EpicsSignal("XF:28IDD-ES:2{SPod:1-Ax:3}Pos-SP", name="sSmartPodTrasY")
sSmartPodRotZ = EpicsSignal("XF:28IDD-ES:2{SPod:1-Ax:1}Rot-SP", name="sSmartPodRotZ")
sSmartPodRotX = EpicsSignal("XF:28IDD-ES:2{SPod:1-Ax:2}Rot-SP", name="sSmartPodRotX")
sSmartPodRotY = EpicsSignal("XF:28IDD-ES:2{SPod:1-Ax:3}Rot-SP", name="sSmartPodRotY")
sSmartPodSync = EpicsSignal("XF:28IDD-ES:2{SPod:1}Sync-Cmd", name="sSmartPodSync")
sSmartPodMove = EpicsSignal("XF:28IDD-ES:2{SPod:1}Move-Cmd", name="sSmartPodMove")


# Filters
class FilterBank(ophyd.Device):
    flt1 = ophyd.Component(EpicsSignal, "1-Cmd", string=True)
    flt2 = ophyd.Component(EpicsSignal, "2-Cmd", string=True)
    flt3 = ophyd.Component(EpicsSignal, "3-Cmd", string=True)
    flt4 = ophyd.Component(EpicsSignal, "4-Cmd", string=True)


Filters = FilterBank("XF:28IDC-OP:1{Fltr}Cmd:Opn", name="fb")  # fb.flt1.set('In')

# APC SWITCHED RACK PDUs
pdu1 = EpicsSignal("XF:28IDD-CT{PDU:1}Sw:1-Sel", name="pdu1")
pdu2 = EpicsSignal("XF:28IDD-CT{PDU:1}Sw:2-Sel", name="pdu2")
pdu3 = EpicsSignal("XF:28IDD-CT{PDU:1}Sw:3-Sel", name="pdu3")
pdu4 = EpicsSignal("XF:28IDD-CT{PDU:1}Sw:4-Sel", name="pdu4")


ring_current = EpicsSignalRO("SR:OPS-BI{DCCT:1}I:Real-I", name="ring_current")
