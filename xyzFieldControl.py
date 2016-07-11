import threading


import uncertainties as u
import math
from labjack import ljm # import labjack library
# now import the modules that we wrote
import sys
sys.path.append("./PowerSupplyControl/")
sys.path.append("./CoilControl/")
import powersupply
import coil

# calibration predifines
xFieldGain = u.ufloat(42.24e-6, 0.08e-6) # T/A
yFieldGain = u.ufloat(45.99e-6, 0.09e-6) # T/A
#zFieldGain = u.ufloat(132.16e-6, 0.08e-6) # T/A

# field to current gain for the adustment coils which is
# extrapolated from the large coil calibration.
xAFieldGain = xFieldGain / 25 # T/A
yAFieldgain = yFieldGain / 20 # T/A

# insanteate the coil objects.
xCoil = coil.CoilWithCorrection('/dev/tty.usbserial-FTBZ1G1B', xFieldGain,
                                'DAC0', xAFieldGain)

yCoil = coil.CoilWithCorrection('/dev/tty.usbserial-FTBYZZIN', yFieldGain,
                                'DAC1', yAFieldgain)

#zCoil = coil.Coil('/dev/tty.usbserial-FTFBPHDT', zFieldGain)


def openPorts():
    # open the powersupply serial ports
    xCoil.supply.openPort()
    yCoil.supply.openPort()
    #zCoil.supply.openPort()
    print('opened all three powersupplies')

    # open the labjack serial port
    handle = ljm.open(ljm.constants.dtANY, ljm.constants.ctANY, "ANY")
    # print the labjack info
    info = ljm.getHandleInfo(handle)
    print("Opened a LabJack with Device type: %i, Connection type: %i,\n" \
        "Serial number: %i, IP address: %s, Port: %i,\nMax bytes per MB: %i" % \
        (info[0], info[1], info[2], ljm.numberToIP(info[3]), info[4], info[5]))
    return(handle) # return the handle so e can close it later

def closePorts(handle):
    # pass in the labjack handle so we don't have to open it on import
    xCoil.supply.closePort()
    yCoil.supply.closePort()
    #zCoil.supply.closePort()
    print('closed all three powersupplies')

    ljm.close(handle)
    print('closed labjack')
    return

# define field setting functions
"""def fine_field_cart(xField, yField, zField, handle):
    '''
    Set powersupplies to the proper current for each coil
    and set the DACs to the correct voltage with the labjack.
    '''
    xCoil.setField(xField)
    yCoil.setField(yField)
    zCoil.setLargeCoilField(zField)

    # now adust the adustment coils with the labjack
    # Setup and call eWriteNames to write values to the LabJack.
    numFrames = 2
    names = [xCoil.dacName, yCoil.dacName]
    analogValues = [xCoil.dacVoltage, yCoil.dacVoltage] # [2.5 V, 12345]
    ljm.eWriteNames(handle, numFrames, names, analogValues)
    return"""

def fine_field_cart(xField, yField, handle):
    '''
    Set powersupplies to the proper current for each coil
    and set the DACs to the correct voltage with the labjack.
    '''

    # create the thread objects to handle the serial wait times
    xThread = threading.Thread(target= xCoil.setField, args= [xField])
    yThread = threading.Thread(target= yCoil.setField, args= [yField])
    #zThread = threading.Thread(target= zCoil.setField, args= zField)

    # start the threads()
    yThread.start()
    xThread.start()
    #zThread.start()

    # now adust the adustment coils with the labjack
    # Setup and call eWriteNames to write values to the LabJack.
    numFrames = 2
    names = [xCoil.dacName, yCoil.dacName]
    analogValues = [xCoil.dacVoltage, yCoil.dacVoltage] # [2.5 V, 12345]
    ljm.eWriteNames(handle, numFrames, names, analogValues)

    # wait for the threads to finish before moving on
    # (prevent thread duplication in an additional call)
    xThread.join()
    yThread.join()
    #zThread.join()


    return

def field_cart(xField, yField, zField):
    '''
    Corsely set the coils using the large powersupplies only.
    (avoid using the adustment coils)
    '''
    xCoil.setLargeCoilField(xField)
    yCoil.setLargeCoilField(yField)
    zCoil.setLargeCoilField(zField)
    return

# rotate the coridinate system to allow us to input field values perpendicular
# to the optical zero.


def fine_field_cart_rotation(xField, yField, zField, phi, handle):
    '''
    Rotate a the cordinate system about the z axis
    so we can allign our control components to be perpendicular
    and parallel to the optical zero.
    '''
    # do a rotation about the z axis.
    xFieldPrime = xField * math.cos(phi) + yField * math.sin(phi)
    yFieldPrime = yField * math.cos(phi) - xField * math.sin(phi)

    fine_field_cart(xFieldPrime, yFieldPrime, zField, handle)

    return

"""def pid_duration(kP, kI, kD, durationInSeconds, labjackHandle):
    startTime = time.time() # time stamp to start the clock
    # load in the field values for the coils
    xField = self."""
