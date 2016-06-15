import sys
sys.path.append("./PowerSupplyControl/")
import powersupply
import numpy as np
import time
import uncertainties as u
from labjack import ljm # import labjack library



class Coil:
'''
powersupplyAddress --> a string with the device port address corisponding to the supply
labjackHandle --> the handle of the labjack to which the adustment coils are attached
fieldGain --> teslas per amp ratio of the coil connected to the powersupply
aFieldGain --> the teslas per amp ratio of the adustment coils connected to the DAC
of the labjack.
'''
    def __init__(self, powersupplyAddress, labjackHandle, dacName, largeFieldGain, smallFieldGain):

        # assign the correct port address to a powersupply objectsupply
        self.supply = powersupply.PowerSupply(powersupplyAdress)

        self.dacName = dacName
        # preliminary calibration data:
        self.largeFieldGain = LargeFieldGain
        self.smallFieldGain = smallFieldGain
        self.voltageGain = 250 # voltage gain (V/A)

        # power supply current command limits
        self.maxPowerSupplyCurrent = 0.9999 # A
        self.minPowerSupplyCurrent = 0.0010 # A
        self.minPowerSupplyCurrentStep = 0.0001 # A

        #Maximum possible field to be produced by coil
        self.appliedMaxField = fieldGain.n * maxPowerSupplyCurrent

        #minimum possible field to be produced by coil
        self.appliedMinField = fieldGain.n * minPowerSupplyCurrent

        self.fieldValue = 0 # keeps the last field value the coil was set to
        self.setLargeCoilField = 0 # lets the coil keep track of what it was last set to
        self.setSmallCoilField = 0


        return(self)

    def setLargeCoilField(self, fieldValue):
        '''
        sets the powersupies to the current required for the specified field
        '''
        current = fieldValue / self.largeFieldGain
        self.supply.current(current)

        return

    def setSmallCoilField(self, fieldValue):
        '''
        sets the DAC on the labjack to the voltage requitred for the specified field
        '''
        current = fieldValue / self.smallFieldGain
        voltage = current * self.voltageGain
        return(voltage)

    def setField(self, fieldValue):

        minimumLargeCoilFieldStep = self.minPowerSupplyCurrentStep * self.LargeFieldGain

        dacFieldRange = 1.5 * minimumLargeCoilFieldStep
        if fieldValue - self.smallFieldValue# if the diference last field and field value is smaller than dacFieldRange
            self.smallFieldValue = fieldValue % minimumLargeCoilFieldStep
            self.setSmallCoilField(smallFieldValue)

        # the 0.5 is to fix a rounding error in the powersupply code.
        fieldOffset = minimumLargeCoilFieldStep * 3.5 # gives the DAC some room to play
        self.largeFieldValue = fieldValue - fieldOffset
        self.setLargeCoilField(self.largeFieldValue)

        self.smallFieldValue = fieldValue % minimumLargeCoilFieldStep
        self.setSmallCoilField(self.smallFieldValue)
        self.fieldValue = fieldValue
        return
