
import xyzFieldControl as xyz
import numpy as np
import time as time
import math as math


# should these be stacks?
# or if we made them dques then we could pass them to the labjack

'''

setpoint = opticalZero

position = ljm.eRead('AIN0')

offset = position - setpoint

area = timestep * offset

slope = (lastOffset - offset) / timestep

if sumSignal == True:
	#run the pid loop


'''
#previous position
#global tempPos
tempPos = 0.0


def pid(setpoint, position):
	'''

	'''
	kP = 0.3
	kD = 0.0
	kI = 0.0
	global tempPos # load in the global variable.

	#print(tempPos)
	lastOffset = tempPos - setpoint # slightly problematic because this should be last setpoint, but we dont really change the setpoint.

	offset = position - setpoint

	area = 1 * offset

	derivative = (offset - lastOffset)


	tempPos = position # load up the prevous position for the next call.

	output = kP*offset + kD*derivative + kI * area

	#print(output)
	return output # value to write to the coils (should be a field value perpendictular to the optical zero)

# open the all ports and get the labjack handle
handle = xyz.openPorts()

#lock in the z because we know what it is (don't change it)
zCurrent = (xyz.zCoil.largeCoilCurrent)

# this is the rough angle of the optical zero
# which we use as our coordinate referance.
opticalZeroRotation = math.pi/4 # radians

setpoint = 0
lastSum = 0
lastLeft = 0
# make some dque objects for leftMinusRight and sumSignal?
nominalFieldOffset = 41.5e-6
outputYField = nominalFieldOffset


try:
	while True:
		# querry the labjack
		t1 = time.time()
		sumSignal, leftMinusRight = xyz.ljm.eReadNames(handle, 2, ['AIN0', 'AIN1'])
		# run the control loop
		output = pid(setpoint, leftMinusRight)
		outputYField += output*1e-6

		print('output = %s' % output)
		# set the field
		xyz.fine_field_cart(xyz.xCoil.coilField, outputYField, xyz.zCoil.largeCoilField, handle)

		# save the (now) old leftMinusRight value for the next loop
		lastLeft = leftMinusRight
		dt = time.time() - t1 # keep track of the timestep for consistancy sake.
		print('time step = %s' % dt)
		if sumSignal < 3:
			raise exception('sum signal LOW!')

except Exception as e:
    # helpful to close the ports on except when debugging the code!
    xyz.closePorts(handle)
    print('closed all the ports')
    print(e) # print the exception
    raise

# work in the optical zero space so we are always adusting perpenductular to the optical zero.

# each limit will need to be an equation for a line and the max and min values will need to be changesd based on the lineear range of that line.
