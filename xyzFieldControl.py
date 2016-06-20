import uncertainties as u
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
zFieldGain = u.ufloat(132.16e-6, 0.08e-6) # T/A

# field to current gain for the adustment coils (extrapolated from the large coil calibration)
xAFieldGain = xFieldGain / 25 # T/A
yAFieldgain = yFieldGain / 20 # T/A


# insanteate the coil objects.
xCoil = coil.CoilWithCorrection('/dev/tty.usbserial-FTBZ1G1B', xFieldGain,
                                'DAC0', xAFieldGain)

yCoil = coil.CoilWithCorrection('/dev/tty.usbserial-FTBYZZIN', yFieldGain,
                                'DAC1', yAFieldgain)

zCoil = coil.Coil('/dev/tty.usbserial-FTFBPHDT', zFieldGain)


def openPorts():
    # open the powersupply serial ports
    xCoil.supply.openPort()
    yCoil.supply.openPort()
    zCoil.supply.openPort()
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
    zCoil.supply.closePort()
    print('closed all three powersupplies')

    ljm.close(handle)
    print('closed labjack')
    return

# define field setting functions
def fine_field_cart(xField, yField, zField, handle):
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
    return


def field_cart(xField, yField, zField):
    '''
    Corsely set the coils using the powersupplies only!
    '''
    xCoil.setLargeCoilField(xField)
    yCoil.setLargeCoilField(yField)
    zCoil.setLargeCoilField(zField)
    return
