import sys
sys.path.append("./PowerSupplyControl/")
import powersupply
import numpy as np
import time
import uncertainties as u

# assign the correct port address to each supply
xCoil = powersupply.PowerSupply('/dev/tty.usbserial-FTBZ1G1B')
yCoil = powersupply.PowerSupply('/dev/tty.usbserial-FTBYZZIN')
zCoil = powersupply.PowerSupply('/dev/tty.usbserial-FTFBPHDT')

# preliminary calibration data:
xFieldGain = u.ufloat(42.24e-6, 0.08e-6) # T/A
yFieldGain = u.ufloat(45.99e-6, 0.09e-6) # T/A
zFieldGain = u.ufloat(132.16e-6, 0.08e-6) # T/A

xFieldOffset = 13.883e-6 # T
yFieldOffset = 13.883e-6 # T
zFieldOffset = 48.9e-6 # T

def field_cart(xField, yField):
    
    # devide the field-component by the axis gain to get the desired current for each coil
    xCurrent = xField / xFieldGain
    yCurrent = yField / yFieldGain
    
    xCoil.current(xCurrent.n) # set to the nominal value of the current
    yCoil.current(yCurrent.n) # with the .n (from the uncertinties package)



