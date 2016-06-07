import sys
sys.path.append('./PowerSupplyControl/')
import powersupply
import numpy as np
import time



# Setup the powersupply serial ports!

# these two are for the horizontal field adustment 
xCoil = powersupply.PowerSupply('/dev/tty.usbserial-FTBZ1G1B')
yCoil = powersupply.PowerSupply('/dev/tty.usbserial-FTBYZZIN')

# this one stays locked at a value to keep the laser centered on the sensor
zCoil = powersupply.PowerSupply('/dev/tty.usbserial-FTFBPHDT') # assign the correct port the the z powersupply


# aproximate current values for zero field
# x = 420
# y = 354
# z = 465

# maximum is one amp


# x and y field gain

# x gain:  (milliamps per tesla)
# y gain:  (milliamps per tesla)
# z gain: 

# for now we are going to just work in the current space

currentMax = 800 
currentMin = 0



# set the z coil to be at it's nominal value:
zCoil.current(465)



# set the pendulum at a certin angle \theta


def set_angle(angle):
    
    currentAmplitude = 400
    currentOffset = 400
    
    xCoil.current( currentOffset + ((currentAmplitude * np.sin(angle)) ))
    yCoil.current( currentOffset + ((currentAmplitude * np.cos(angle)) ))

# open the ports! 
xCoil.openPort()
yCoil.openPort()



# reset the cois to zero position
set_angle(0)
print('sleeping for 5 seconds')
time.sleep(5)

# make the penduleum go in a circle (wind it up).

angles = np.linspace(0,np.pi*2,2000)

# circle one way

print('starting circle')
for i in angles:
    set_angle(i)

    
    
# wait a bit
print('waiting')
time.sleep(6)

# circle is the other way
print('other circle')
angles = np.linspace(np.pi*2,0,2000)

for i in angles:
    set_angle(i)
    
    
print('done! and HI')

# close the ports!
xCoil.closePort()
yCoil.closePort()

