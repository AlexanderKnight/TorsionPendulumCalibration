import sys
sys.path.append("./PowerSupplyControl/")
import powersupply
import numpy as np
import time
import uncertinties as u
# import labjack library
from labjack import ljm
import matplotlib.pyplot as plt

# analog input to read from the labjack
analogInputName = 'AIN0'

# assign the correct port address to each supply
xCoil = powersupply.PowerSupply('/dev/tty.usbserial-FTBZ1G1B')
yCoil = powersupply.PowerSupply('/dev/tty.usbserial-FTBYZZIN')
zCoil = powersupply.PowerSupply('/dev/tty.usbserial-FTFBPHDT')

# preliminary calibration data:
xFieldGain = u.ufloat(42.24e-6, 0.08e-6) # T/A
yFieldGain = u.ufloat(45.99e-6, 0.09e-6) # T/A
zFieldGain = u.ufloat(132.16e-6, 0.08e-6) # T/A

maxPowerSupplyCurrent = 999.9 #mA
minPowerSupplyCurrent = 0.1 #mA

xFieldOffset = 13.883e-6 # T
yFieldOffset = 13.883e-6 # T
zFieldOffset = 48.9e-6 # T

#Maximum possible field to be produced by coils
xAppliedMaxField = xFieldGain * maxPowerSupplyCurrent*1e-3
yAppliedMaxField = yFieldGain * maxPowerSupplyCurrent*1e-3
zAppliedMaxField = zFieldGain * maxPowerSupplyCurrent*1e-3

#minimum possible field to be produced by coils
xAppliedMinField = xFieldGain * minPowerSupplyCurrent*1e-3
yAppliedMinField = yFieldGain * minPowerSupplyCurrent*1e-3
zAppliedMinField = zFieldGain * minPowerSupplyCurrent*1e-3

#torsionalZero = 
#torsionConstant = 


def field_polar(fieldMagnitude, fieldDirection):
    '''
    sets the field in the coils using the calibration data with polar coridinates as inputs
    does not allow the field to be greater than the smallest field offset.
    '''    
    angleRad = np.radians(fieldDirection) # ((np.pi)/(180))*angle
    
    # convert to cartesian 
    xField = xFieldOffset + (fieldMagnitude * np.sin(angleRad))
    yField = yFieldOffset + (fieldMagnitude * np.cos(angleRad))
    
    # devide the field-component by the axis gain to get the desired current for each coil
    xCurrent = xField / xFieldGain
    yCurrent = yField / yFieldGain
    
    xCoil.current(xCurrent.n) # set to the nominal value of the current
    yCoil.current(yCurrent.n) # with the .n (from the uncertinties package)
    
    return

def field_cart(xField, yField):
    '''
    sets the field in the coils using the calibration data with cartesian coordinates as input
    '''
    
    # devide the field-component by the axis gain to get the desired current for each coil
    xCurrent = xField / xFieldGain
    yCurrent = yField / yFieldGain
    
    xCoil.current(xCurrent.n) # set to the nominal value of the current
    yCoil.current(yCurrent.n) # with the .n (from the uncertinties package)
    
    return
    
    
# open the powersupply ports
xCoil.openPort()
yCoil.openPort()
zCoil.openPort()

#open the labjack
handle = ljm.open(ljm.constants.dtANY, ljm.constants.ctANY, "ANY")

# check labjack connection
info = ljm.getHandleInfo(handle)
print("Opened a LabJack with Device type: %i, Connection type: %i,\n" \
    "Serial number: %i, IP address: %s, Port: %i,\nMax bytes per MB: %i" % \
    (info[0], info[1], info[2], ljm.numberToIP(info[3]), info[4], info[5]))

##############
Bx = np.linspace(xAppliedMinField, xAppliedMaxField, 200)
By = np.linspace(yAppliedMinField, xAppliedMaxField, 200)
Bz = np.linspace(56.0, 62.0, 200)

minSumSignal = 3.0

sumSignal = []

for i in range(len(bx)):
    if i % 2:
        for y in By:
            field_cart(Bx[i],y)
            time.sleep(0.1)
            result = float(ljm.eReadName(handle,analogInputName))
            if result > minSumSignal:
                sumSignal.append([Bx[i],y])
    else:
        
        for y in By:
            field_cart(Bx[-(i+1)],y)
            time.sleep(0.1)
            result = float(ljm.eReadName(handle,analogInputName))
            if result > minSumSignal:
                sumSignal.append([Bx[-(i+1)],y])

for i in range(len(sumSignal)):
    plt.scatter(sumSignal[i][0],sumSignal[i][1])
plt.show()
##############    
    
# close the labjack connection    
ljm.close(handle)   

# close the powersupply conections
xCoil.closePort()
yCoil.closePort()
zCoil.closePort()