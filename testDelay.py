
import xyzFieldControl as xyz
import numpy as np
import time as time
import math as math


# open the all ports and get the labjack handle
handle = xyz.openPorts()

# configure the analog register
# Setup and call eWriteNames to configure the AIN on the LabJack.
numFrames = 3
names = ["AIN0_NEGATIVE_CH", "AIN0_RANGE", "AIN0_RESOLUTION_INDEX"]
aValues = [199, 0, 10] # setup the analog register values for the labjack
xyz.ljm.eWriteNames(handle, numFrames, names, aValues)


# open ports
handle = xyz.openPorts()

try:
    while True:
        input('setLow')
        xyz.fine_field_cart(10e-6, 10e-6, handle)
        input('setHigh')
        xyz.fine_field_cart(20e-6, 20e-6, handle)

except KeyboardInterrupt:
	time.sleep(.5)
	print('\n')
	xyz.closePorts(handle)
	print('closed all the ports')
	#print('Keyboard Interrupt') # print the exception
	#raise
except Exception as e:
	# helpful to close the ports on except when debugging the code!
	time.sleep(.5)
	xyz.closePorts(handle)
	print('closed all the ports')
	print(e) # print the exception
	raise
