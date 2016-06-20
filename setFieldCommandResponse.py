import xyzFieldControl as xyz
import numpy as np
import time as time

# open the all ports and get the labjack handle
handle = xyz.openPorts()

#lock in the z because we know what it is (don't change it)
zCurrent = (xyz.zCoil.largeCoilCurrent)
# xyz.zCoil.supply.current(439.5)
yField = 42.5e-6

try:

    while True:
        yField += float(input('offset yField by (nano Tesla) -->'))*1e-9 #
        print('yField = %f (micro Tesla)' % (yField * 1e6))
        xyz.fine_field_cart(xyz.xCoil.appliedMaxField, yField, xyz.zCoil.largeCoilField, handle)
    '''
    # try something a bit more simple
    xyz.field_cart(xyz.xCoil.appliedMaxField, xyz.yCoil.appliedMaxField, xyz.zCoil.largeCoilField)
    '''
    pass
except Exception as e:
    # helpful to close the ports on except when debugging the code!
    xyz.closePorts(handle)
    print('closed all the ports')
    print(e) # print the exception
    raise
