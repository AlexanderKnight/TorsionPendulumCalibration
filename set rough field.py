import xyzFieldControl as xyz
import numpy as np
import time as time

# open the all ports and get the labjack handle
handle = xyz.openPorts()

#lock in the z because we know what it is (don't change it)
zCurrent = (xyz.zCoil.largeCoilCurrent)
# xyz.zCoil.supply.current(439.5)
xField = 0
yField = 0
zField = 0

try:

    while True:
        xInField = float('0'+input('xField in micro Tesla -->'))*1e-6
        yInField = float('0'+input('yField in micro Tesla -->'))*1e-6
        #zInField = float('0'+input('zField in micro Tesla -->'))*1e-6

        if xInField != 0:
            xField = xInField
        if yInField != 0:
            yField = yInField
        zField = xyz.zCoil.getLargeCoilField() # keep the z at whatever it's set to

        print('setting field to:\n(xField, yField, zField)\n(%f, %f, %f)' % ((xField * 1e6), (yField * 1e6), (zField * 1e6)))
        xyz.fine_field_cart(xField, yField, zField, handle)


except Exception as e:
    # helpful to close the ports on except when debugging the code!
    xyz.closePorts(handle)
    print('closed all the ports')
    print(e) # print the exception
    raise
