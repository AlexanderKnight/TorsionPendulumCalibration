
import xyzFieldControl as xyz
import numpy as np
import time as time

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

def pid(setpoint, position, lastPosition, timeStep):
    '''

    '''
    kP = 0.01
    kD = 0.01
    kI = 0.01

    lastOffset = lastPosition - LastSetpoint

    offset = position - setpoint

    area = timeStep * offset

    derivative = (offset - lastOffset)

    output = kP*offset + kD*derivative + kI*area
	print(output)
    return output # value to write to the coils (should be a field value perpendictular to the optical zero)

# open the all ports and get the labjack handle
handle = xyz.openPorts()

#lock in the z because we know what it is (don't change it)
zCurrent = (xyz.zCoil.largeCoilCurrent)

opticalZeroRotation = math.pi/4 # radians

setpoint = 0

try:
	while True:
		output = pid(setpoint, )






# work in the optical zero space so we are always adusting perpenductular to the optical zero.

# each limit will need to be an equation for a line and the max and min values will need to be changesd based on the lineear range of that line.
