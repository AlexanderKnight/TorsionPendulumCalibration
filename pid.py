
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

def pid(setpoint, position, handle):
	'''

	'''
	kP = 0.01
	kD = 0.009
	kI = 0.55
	global prePos
	global integral
	global t0
	global initialOutput

	# calculate dt and save t0 for the next call.
	t1 = time.time()
	dt = t1 - t0
	t0 = t1

	offset = position - setpoint
	preOffset = prePos - setpoint

	integral += (offset * dt)

	derivative = (offset - preOffset) / dt

	prePos = position # save the position for the next call.

	output = ((kP * offset) + (kI * integral) + (kD * derivative)) * -1e-7 + initialOutput

	# now set the field with the output
	#print('output = %14.11f\toffset = %14.11f\tdt = %14.11f\tintegral = %14.11f' % (output, offset, position, dt, integral))
	print('offset = %14.11f\tintegral = %14.11f\tderivative = %14.11f\tdt = %14.11f' % (offset, integral, derivative, dt))
	xyz.fine_field_cart(xyz.xCoil.appliedMaxField, output, xyz.zCoil.largeCoilField, handle)


# open the all ports and get the labjack handle
handle = xyz.openPorts()

# configure the analog register
# Setup and call eWriteNames to configure the AIN on the LabJack.
numFrames = 3
names = ["AIN0_NEGATIVE_CH", "AIN0_RANGE", "AIN0_RESOLUTION_INDEX"]
aValues = [199, 0, 10]
xyz.ljm.eWriteNames(handle, numFrames, names, aValues)

#lock in the z because we know what it is (don't change it)
zCurrent = (xyz.zCoil.largeCoilCurrent)

# global variables to be used by the pid loop
prePos = 0.0 #previous position
integral = 0.0
t0 = time.time()

setpoint = 0.0

initialOutput = xyz.yCoil.coilField



try:
	while True:
		# take the optical sensor readings from the labjack
		sumSignal, leftMinusRight = xyz.ljm.eReadNames(handle, 2, ['AIN0', 'AIN1'])
		if sumSignal > 3.0: # if we have a sum signal
			pid(setpoint, leftMinusRight, handle) # run the pid loop
		else:
			print('sumSignal = %s' % sumSignal)
			xyz.yCoil.supply.current(.9110)
			input('Off sensor! (press enter when on sensor)')
			initialOutput = xyz.yCoil.coilField

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

# work in the optical zero space so we are always adusting perpenductular to the optical zero.

# each limit will need to be an equation for a line and the max and min values will need to be changesd based on the lineear range of that line.
