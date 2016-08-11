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

def set_field(coil, fieldValue, fieldGain):
    """
    Field gain is in T/A so to get Amps we need to devide the field value by the field Gain
    """
    current = (fieldValue/fieldGain)*1e3 # set the current to be in milliamps
    #print(current) 
    coil.current(current)
    return
                                                  
                                                  
# put the pendulum in it's starting position
def set_angle(angle, fieldStrength):
    '''
    takes the desired angle in degrees and the field strength in tesla
    sets the supplies to these values
    
    the maximum field strength is given by the weakest coil.
    in our case, the x coil 42.23 uT at max powersupply current so we shan't set the 
    fieldStrength to be greater than this value. 
    '''
    
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
    # 13.883e-6
    xFieldOffset = 13.883e-6 # T
    yFieldOffset = 13.883e-6 # T
    zFieldOffset = 48.9e-6 # T
    
    angleRad = np.radians(angle) # ((np.pi)/(180))*angle
    
    xField = xFieldOffset + (fieldStrength * np.sin(angleRad))
    yField = yFieldOffset + (fieldStrength * np.cos(angleRad))
    
    
    set_field(xCoil, xField, xCoilGain) # set the x field
    set_field(yCoil, yField, yCoilGain) # set the y field
    
    return 

###################################################

startAngle = 43.39
stopAngle = 43.6
steps = 100
maxField = 13e-6


# open the ports! 
xCoil.openPort()
yCoil.openPort()
zCoil.openPort()


# set the z coil to be at it's nominal value:
#zCoil.current(471.0)

# reset the cois to zero position
set_angle(startAngle, maxField) # maximum field value
print('sleeping for 3 seconds')
time.sleep(3)


zSweep = np.linspace(436.4, 436.8, 5)
for k in zSweep:
    zCoil.current(k)
    print('zcoil current = %s' % k)
    # make the penduleum go in a circle (wind it up).
    # circle one way
    anglesUp = np.linspace(startAngle,stopAngle,steps)
    print('starting circle')
    for i in anglesUp:
        set_angle(i, maxField)
        print(i)
    
    # sweep back to the start point
    set_angle(startAngle, maxField)
    time.sleep(2)
    
    '''
    # wait a bit
    print('waiting')
    time.sleep(2)

    # circle is the other way
    print('other circle')
    anglesDown = np.linspace(stopAngle,startAngle,steps)

    for i in anglesDown:
        set_angle(i, maxField)
        print(i)'''
# close the ports    
xCoil.closePort()
yCoil.closePort()
zCoil.closePort()

print('done! and HI')

#def sweep(rads/second)