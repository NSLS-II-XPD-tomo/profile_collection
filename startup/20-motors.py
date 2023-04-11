print(f"Loading {__file__}")

## Huber Stack
mTopX = EpicsMotor("XF:28IDD-ES:2{Stg:Stack-Ax:Xfine}Mtr", name="mTopX")
mTopY = EpicsMotor("XF:28IDD-ES:2{Stg:Stack-Ax:Yfine}Mtr", name="mTopY")
mTopZ = EpicsMotor("XF:28IDD-ES:2{Stg:Stack-Ax:Z}Mtr", name="mTopZ")
mPhi = EpicsMotor("XF:28IDD-ES:2{Stg:Stack-Ax:Phi}Mtr", name="mPhi")
mRoll = EpicsMotor("XF:28IDD-ES:2{Stg:Stack-Ax:Roll}Mtr", name="mRoll")
mPitch = EpicsMotor("XF:28IDD-ES:2{Stg:Stack-Ax:Pitch}Mtr", name="mPitch")
mBaseY = EpicsMotor("XF:28IDD-ES:2{Stg:Stack-Ax:Y}Mtr", name="mBaseY")
mBaseX = EpicsMotor("XF:28IDD-ES:2{Stg:Stack-Ax:Xbase}Mtr", name="mBaseX")

# Dexela detector rotation
mDexelaPhi = EpicsMotor("XF:28IDD-ES:2{Stg:Stack-Ax:Htth}Mtr", name="mDexelaPhi")

# Questar lens X-rail
mQuestarX = EpicsMotor("XF:28IDD-ES:2{Cam:Mnt-Ax:X}Mtr", name="mQuestarX")

# Beamstops
mBeamStopY = EpicsMotor("XF:28IDD-ES:2{BS-Ax:X}Mtr", name="mBeamStopY")

# D-hutch slits
mSlitsYGap = EpicsMotor("XF:28IDD-ES:2{Slt-Ax:YGap}Mtr", name="mSlitsYGap")
mSlitsYCtr = EpicsMotor("XF:28IDD-ES:2{Slt-Ax:YCtr}Mtr", name="mSlitsYGap")
mSlitsXGap = EpicsMotor("XF:28IDD-ES:2{Slt-Ax:XGap}Mtr", name="mSlitsXGap")
mSlitsXCtr = EpicsMotor("XF:28IDD-ES:2{Slt-Ax:XCtr}Mtr", name="mSlitsXGap")
mSlitsTop = EpicsMotor("XF:28IDD-ES:2{Slt-Ax:T}Mtr", name="mSlitsTop")
mSlitsBottom = EpicsMotor("XF:28IDD-ES:2{Slt-Ax:B}Mtr", name="mSlitsBottom")
mSlitsOutboard = EpicsMotor("XF:28IDD-ES:2{Slt-Ax:O}Mtr", name="mSlitsOutboard")
mSlitsInboard = EpicsMotor("XF:28IDD-ES:2{Slt-Ax:I}Mtr", name="mSlitsInboard")

# Hexapods Z-rail
mHexapodsZ = EpicsMotor("XF:28IDD-ES:2{Det:Dexela-Ax:Z}Mtr", name="mHexapodsZ")

# Sigray lens
mSigrayX = EpicsMotor("XF:28IDD-ES:2{Stg:Sigray-Ax:X}Mtr", name="mSigrayX")
mSigrayY = EpicsMotor("XF:28IDD-ES:2{Stg:Sigray-Ax:Y}Mtr", name="mSigrayY")
mSigrayZ = EpicsMotor("XF:28IDD-ES:2{Stg:Sigray-Ax:Z}Mtr", name="mSigrayZ")
mSigrayPitch = EpicsMotor("XF:28IDD-ES:2{Stg:Sigray-Ax:Pitch}Mtr", name="mSigrayPitch")
mSigrayYaw = EpicsMotor("XF:28IDD-ES:2{Stg:Sigray-Ax:Yaw}Mtr", name="mSigrayYaw")

# Encoders
ePhi = EpicsMotor("XF:28IDD-ES:2{Stg:Stack-Ax:PhiEnc}Mtr", name="Phi encoder")

# Fast shutter
FastShutter = EpicsMotor("XF:28IDC-ES:1{Sh2:Exp-Ax:5}Mtr", name="shctl1")
