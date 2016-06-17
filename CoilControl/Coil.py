
class Coil:
    '''
    parent class for a coil that is attached to a BK powersupply
    '''
    def __init__(self, powersupplyAddress, largeFieldGain):
        # assign the correct port address to a powersupply objectsupply
        self.supply = powersupply.PowerSupply(powersupplyAdress)

        # calibration dependant data:
        self.largeFieldGain = LargeFieldGain
        # power supply current command limits
        self.maxPowerSupplyCurrent = 0.9999 # A
        self.minPowerSupplyCurrent = 0.0010 # A

        # Maximum and minimum possible field that can be produced by the coil.
        self.appliedMaxField = fieldGain.n * maxPowerSupplyCurrent
        self.appliedMinField = fieldGain.n * minPowerSupplyCurrent

        # innitalize field value containers
        self.CoilField = 0.0

        return(self)

    def setLargeCoilField(self, fieldValue):
        '''
        sets the powersupies to the current required for the specified field
        '''
        # calculate the current from the field value
        current = fieldValue / self.largeFieldGain
        self.supply.current(current) # make sure the current is in milliamps
        # update the stored value of the

        return

class CoilWithCorrection(Coil):
    '''
    coil with additional correction coil controlled by the labjack
    '''
    def __init__(self, powersupplyAddress, largeFieldGain, labjackHandle, dacName, smallFieldGain):
        Coil.__init__(self, powersupplyAddress, largeFieldGain)

        self.dacName = dacName # the DAC to which the adustment coil is conndected
        self.smallFieldGain = smallFieldGain
        self.voltageGain = 250 # opAmp current source gain in (V/A)

        # use this value to measure the smallest deveation avalable from the
        # large powersupplies
        self.minPowerSupplyCurrentStep = 0.0001 # Amps
        # and the field?


        return(self)


class ClassName(object):
    """docstring for """
    def __init__(self, arg):
        super(, self).__init__()
        self.arg = arg
