import numpy as np
import time
import uncertainties as u
from labjack import ljm # import labjack library
import matplotlib.pyplot as plt
# now import the modules that we wrote
import sys
sys.path.append("./PowerSupplyControl/")
sys.path.append("./CoilControl/")
import powersupply
import coil

# calibration predifines
xFieldGain = u.ufloat(42.24e-6, 0.08e-6) # T/A
yFieldGain = u.ufloat(45.99e-6, 0.09e-6) # T/A
zFieldGain = u.ufloat(132.16e-6, 0.08e-6) # T/A

# field to current gain for the adustment coils (extrapolated from the large coil calibration)
xAFieldGain = xFieldGain / 25 # T/A
yAFieldgain = yFieldGain / 20 # T/A

# power supply current command limits
maxPowerSupplyCurrent = 0.9999 # A
minPowerSupplyCurrent = 0.0010 # A

# preliminary rough estimate feild values
xFieldOffset = 13.883e-6 # T
yFieldOffset = 13.883e-6 # T
zFieldOffset = 48.9e-6 # T

# insanteate the coil objects.
xCoil = coil.CoilWithCorrection('/dev/tty.usbserial-FTBZ1G1B', xFieldGain, 'DAC0', xAFieldGain)
yCoil = coil.CoilWithCorrection('/dev/tty.usbserial-FTBYZZIN', yFieldGain, 'DAC1', yAFieldgain)
zCoil = coil.Coil('/dev/tty.usbserial-FTFBPHDT', zFieldGain)

# define field setting functions
def fine_field_cart(xField, yField, zField):
    # calculate the currents and voltages for each coil
    xCoil.setField(xField)
    yCoil.setField(yField)
    zCoil.setLargeCoilField(zField)
