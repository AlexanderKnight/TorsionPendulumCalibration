import sys
sys.path.append("./PowerSupplyControl/")
import powersupply
import numpy as np
import time
#import uncertinties


# these two are for the horizontal field adustment 
xCoil = powersupply.PowerSupply('/dev/tty.usbserial-FTBZ1G1B')
yCoil = powersupply.PowerSupply('/dev/tty.usbserial-FTBYZZIN')

# this one stays locked at a value to keep the laser centered on the sensor
zCoil = powersupply.PowerSupply('/dev/tty.usbserial-FTFBPHDT') # assign the correct port the the z powersupply

# Coil gain calibration values:
# X coil = 42.24 +- 0.08 uT/A
# Y coil = 45.99 +- 0.09 uT/A
# Z coil = 132.16 +- 0.08 uT/A

xCoilGain = 42.24e-6 # T/A
yCoilGain = 45.99e-6 # T/A
zCoilGain = 132.16e-6 # T/A

# Aproximate Earth field components:
# x offset = 9.58 mT
# y offset = 17.0 mT
# z offset = -48.9 mT


# put the pendulum in it's starting position
def set_angle(angle):
    
    angleRad = np.radians(angle) # ((np.pi)/(180))*angle
    
    currentAmplitude = 400
    currentOffset = 401
    
    xCurrent = currentOffset + (currentAmplitude * np.sin(angleRad))
    yCurrent = currentOffset + (currentAmplitude * np.cos(angleRad))

    xCoil.current(xCurrent)
    yCoil.current(yCurrent)

    return

###################################################

startAngle = 50.00
stopAngle = 50.05
steps = 200



# open the ports! 
xCoil.openPort()
yCoil.openPort()
zCoil.openPort()


# set the z coil to be at it's nominal value:
zCoil.current(471.0)

# reset the cois to zero position
set_angle(startAngle)
print('sleeping for 3 seconds')
time.sleep(3)

# make the penduleum go in a circle (wind it up).

# circle one way
angles = np.linspace(startAngle,stopAngle,steps)
print('starting circle')
for i in angles:
    set_angle(i)
    print(i)
    
    
# wait a bit
print('waiting')
time.sleep(6)

# circle is the other way
print('other circle')
angles = np.linspace(stopAngle,startAngle,steps)

for i in angles:
    set_angle(i)
    
# close the ports    
xCoil.closePort()
yCoil.closePort()
zCoil.closePort()

print('done! and HI')

#def sweep(rads/second)