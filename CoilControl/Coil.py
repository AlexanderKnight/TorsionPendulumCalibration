
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
        self.coilField = 0.0 # total field

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
        # and the field now gets divided into two coils
        self.largeCoilField = 0.0 # portion of the total field controlled by the large coils
        self.smallCoilField = 0.0 # portion of the total field for the small coils

        return(self)


    def setField(self, fieldValue):

        # calculate the smallest field that the large coil can produce
        minimumLargeCoilFieldStep = self.minPowerSupplyCurrentStep * self.LargeFieldGain
        # total range of the small coil.
        # |--|--|--|--|--|--|--|--| the small ticks are the minimumLargeCoilFieldStep
        #    |--|--|**|--|--|       this is the range of the dac after voltage clamping band
        #  pick the ** for the middle of our field.
        # usable +- range of the small coil (total range is 3 steps)
        #    |--{--|**|--}--|       Curly braces are the trigger points where we want to renormalize
        smallCoilFieldRange = 1.5 * minimumLargeCoilFieldStep
        # |  |--|--|**|--|--|       Distance from the left side is 3.5 smallest divisions
        largeCoilFieldOffset = minimumLargeCoilFieldStep * 3.5
        # the extra .5 above is to hack the rounding in the current function :P
        smallCoilFieldOffse = minimumLargeCoilFieldStep * 3.0
        # with this in mind let's split the field btween the large and small coils
        # the large coil is easy we just subtract the field offset and let the
        # powersupply.PowerSupply.current() function round up or down with format
        self.largeCoilField = (fieldValue - largeCoilFieldOffset)
        # for the small coil, we need to first provide the field offset but also
        # calculate the remaining field (with mod) to get a precise measurement
        smallCoilFieldRemainder = (fieldValue % minimumLargeCoilFieldStep)
        # add the offset with the remainder to get the small field value.
        self.smallCoilField = smallCoilFieldOffset + smallCoilFieldRemainder
        self.setLargeCoilField(fieldValue - largeCoilFieldOffset)
