import sys
sys.path.append("./../PowerSupplyControl/")
import powersupply

class Coil:
    '''
    parent class for a coil that is attached to a BK powersupply
    '''
    def __init__(self, powersupplyAddress, largeCoilFieldGain):
        # assign the correct port address to a powersupply objectsupply
        self.supply = powersupply.PowerSupply(powersupplyAddress)

        # calibration dependant data:
        self.largeCoilFieldGain = largeCoilFieldGain
        # power supply current command limits
        self.maxPowerSupplyCurrent = 0.9999 # A
        self.minPowerSupplyCurrent = 0.0010 # A

        # Maximum and minimum possible field that can be produced by the coil.
        self.appliedMaxField = self.largeCoilFieldGain.n * self.maxPowerSupplyCurrent
        self.appliedMinField = self.largeCoilFieldGain.n * self.minPowerSupplyCurrent

        # innitalize field value containers
        self.coilField = 0.0 # total field
        self.largeCoilCurrent = 0.0
        
        return

    def setLargeCoilField(self, fieldValue):
        '''
        Calculates the current required for the specified field.
        '''
        # calculate the current from the field value
        current = fieldValue / self.largeCoilFieldGain
        self.largeCoilCurrent = ('%5.1f' % current) # format the current the same way powersupply does
        # with the formatted current we can recalculate the largeCoilField
        self.largeCoilField = self.largeCoilCurrent * self.largeCoilfieldGain

        self.supply.current(self.largeCoilCurrent) # make sure the current is in milliamps
        # update the stored value of the

        return

class CoilWithCorrection(Coil):
    '''
    coil with additional correction coil controlled by the labjack
    '''
    def __init__(self, powersupplyAddress, largeCoilFieldGain, dacName, smallCoilFieldGain):

        Coil.__init__(self, powersupplyAddress, largeCoilFieldGain)

        self.dacName = dacName # the DAC to which the adustment coil is conndected
        self.smallCoilFieldGain = smallCoilFieldGain # T/A
        self.voltageGain = 250 # opAmp current source gain in (V/A)
        self.dacVoltage = 0.0 # store the voltage to write to the DAC

        # use this value to measure the smallest deveation avalable from the
        # large powersupplies
        self.minPowerSupplyCurrentStep = 0.0001 # Amps
        # and the field now gets divided into two coils
        self.largeCoilField = 0.0 # portion of the total field controlled by the large coils
        self.smallCoilField = 0.0 # portion of the total field for the small coils

        return

    def setSmallCoilField(self, fieldValue):
        '''
        sets the adustmetn coils to the specified value.
        the adustment coils only work in one direction and add to the field
        of the large coils.
        due to the constraints of the labjack serial link, this function
        only sets the local variable 'smallCoilVoltage' which can later
        be passed to the labjack with the other DAC setting to minimize comunication time
        '''
        self.smallFieldValue = fieldValue # update the field container
        current = fieldValue / self.smallCoilFieldGain # calculate the current from the field gain
        self.dacVoltage = current * self.voltageGain # V = I*R

    def setField(self, fieldValue):
        '''
        set both the small and large coils.
        use the large coils to get in range of the desired value,
        and the small ones to precisely set the field.
        '''
        # calculate the smallest field that the large coil can produce
        minimumLargeCoilFieldStep = self.minPowerSupplyCurrentStep * self.largeCoilFieldGain
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
        # powersupply.PowerSupply.current() function round up or down with format %5.1f

        # set the large coils only if we are out of range of the dacs
        maximumChangeInField = largeCoilFieldOffset + smallCoilFieldRange
        minimumChangeInField = largeCoilFieldOffset - smallCoilFieldRange

        self.smallFieldValue = (fieldValue - self.largeCoilField)

        if self.smallFieldValue > maximumChangeInField or self.smallFieldValue < minimumChangeInField:
            # renormalize!
            # set the large coil to the field value minus the field that we will add with the adustment coils
            self.setLargeCoilField(fieldValue - largeCoilFieldOffset)

        # for the small coil, we need to first provide the field offset
        # setLargeCoilField recalculates the true field contribution
        # of the large coil so we can simply subtract that from our desired field value,
        # and set the small coil field.
        self.setSmallCoilField(fieldValue - self.largeCoilField)
        # We do NOT want to run the labjack code here because its better to give
        # it both coil values at once in the xyzFieldControl module.

        self.coilField = fieldValue # update the total coil field for the next call

        return
