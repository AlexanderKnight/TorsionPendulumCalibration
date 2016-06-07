import sys
sys.path.append("./PowerSupplyControl/")
import powersupply
import numpy as np
import time



# these two are for the horizontal field adustment 
xCoil = powersupply.PowerSupply('/dev/tty.usbserial-FTBZ1G1B')
yCoil = powersupply.PowerSupply('/dev/tty.usbserial-FTBYZZIN')

# this one stays locked at a value to keep the laser centered on the sensor
zCoil = powersupply.PowerSupply('/dev/tty.usbserial-FTFBPHDT') # assign the correct port the the z powersupply

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
zCoil.current(471)

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