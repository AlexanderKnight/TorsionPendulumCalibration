import threading
import time
import numpy as np
import pandas as pd

import uncertainties as u
import math
# now import the modules that are part of the repo
import sys
sys.path.append("./Python_LJM 3/") # check that this works properly
from labjack import ljm # import labjack library
sys.path.append("./PowerSupplyControl/")
import powersupply
sys.path.append("./CoilControl/")
import coil

# calibration predifines
xFieldGain = u.ufloat(42.24e-6, 0.08e-6) # T/A
yFieldGain = u.ufloat(45.99e-6, 0.09e-6) # T/A
zFieldGain = u.ufloat(132.16e-6, 0.08e-6) # T/A

# field to current gain for the adustment coils which is
# extrapolated from the large coil calibration.
xAFieldGain = xFieldGain / 25 # T/A
yAFieldgain = yFieldGain / 20 # T/A

# insanteate the coil objects.
xCoil = coil.CoilWithCorrection('/dev/tty.usbserial-FTBZ1G1B', xFieldGain,
                                'DAC0', xAFieldGain)

yCoil = coil.CoilWithCorrection('/dev/tty.usbserial-FTBYZZIN', yFieldGain,
                                'DAC1', yAFieldgain)

zCoil = coil.Coil('/dev/tty.usbserial-FTFBPHDT', zFieldGain)


def openPorts():
    """Open all the ports including the labjack and the powersupplies"""
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
    """close all the ports including the labjack and the powersupplies"""
    # pass in the labjack handle so we don't have to open it on import
    xCoil.supply.closePort()
    yCoil.supply.closePort()
    #zCoil.supply.closePort()
    print('closed all three powersupplies')

    ljm.close(handle)
    print('closed labjack')
    return

# define field setting functions

# old non-threading field function.
'''
def fine_field_cart(xField, yField, zField, handle):
    """
    Set powersupplies to the proper current for each coil
    and set the DACs to the correct voltage with the labjack.
    """
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
'''

def fine_field_cart(xField, yField, zField, handle):
    """
    Set powersupplies to the proper current for each coil
    and set the DACs to the correct voltage with the labjack.
    """
    t0 = time.time()
    # create the thread objects to handle the serial wait times
    xThread = threading.Thread(target= xCoil.setField, args= [xField])
    yThread = threading.Thread(target= yCoil.setField, args= [yField])
    zThread = threading.Thread(target= zCoil.setLargeCoilField, args= [zField])

    # start the threads()
    xThread.start()
    yThread.start()
    zThread.start()

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
    zThread.join()

    t1 = time.time()
    #print('total time between = %s' % (t1-t0))
    #print('total time between = {0}'.format(t1-t0)) #

    return

def field_cart(xField, yField, zField):
    """
    Corsely set the coils using the large powersupplies only.
    (avoid using the adustment coils)
    """
    xCoil.setLargeCoilField(xField)
    yCoil.setLargeCoilField(yField)
    zCoil.setLargeCoilField(zField)
    return

# rotate the coridinate system to allow us to input field values perpendicular
# to the optical zero.


def fine_field_cart_rotation(xField, yField, zField, phi, handle):
    """
    Rotate a the cordinate system about the z axis
    so we can allign our control components to be perpendicular
    and parallel to the optical zero.
    """
    # do a rotation about the z axis.
    xFieldPrime = xField * math.cos(phi) + yField * math.sin(phi)
    yFieldPrime = yField * math.cos(phi) - xField * math.sin(phi)

    fine_field_cart(xFieldPrime, yFieldPrime, zField, handle)

    return

'''def pid_duration(kP, kI, kD, durationInSeconds, labjackHandle):
    startTime = time.time() # time stamp to start the clock
    # load in the field values for the coils
    xField = self.'''


def find_nearest(array, value):
    '''Finds the index of the element in an array that is closest to a value
    '''
    idx = (np.abs(array-value)).argmin()
    return idx


def beamSearch(searchAxis, handle, minSumSignal=4.5, steps=5000):
    '''
    This function takes a value in x or y axis and adjusts the other until a
    high sum signal is reached, then returns the values at which optical zeroi
    is seen.
    '''

    analogInputName = 'AIN1' #L-R signal

    ##############
    #steps = 1000
    #Bx = np.linspace(xAppliedMinField, xAppliedMaxField, 40)
    #By = np.linspace(yAppliedMinField, yAppliedMaxField, 1000)
    #Bz = np.linspace(56.0, 62.0, 200)

    if searchAxis == 'x':

        Bx = np.linspace(xCoil.appliedMinField, xCoil.appliedMaxField, steps)
        By = yCoil.getLargeCoilField()
        Bz = zCoil.getLargeCoilField()

        BxInit = xCoil.getLargeCoilField()
        BxInitIndex = find_nearest(Bx, BxInit)

        for x in Bx[BxInitIndex::-1]:
            fine_field_cart(x, By, Bz, handle)
            resultSum = float(ljm.eReadName(handle,analogInputName))
            resultLR = float(ljm.eReadName(handle, 'AIN0'))
            time.sleep(0.1)
            if resultSum > minSumSignal and (-2.0 < resultLR < 2.0):
                return [x, By, Bz]

        for x in Bx:
            fine_field_cart(x,By, Bz, handle)
            #time.sleep(0.1)
            resultSum = float(ljm.eReadName(handle,analogInputName))
            resultLR = float(ljm.eReadName(handle, 'AIN0'))
            time.sleep(0.1)
            if resultSum > minSumSignal and (-2.0 < resultLR < 2.0):
                return [x, By, Bz]



    elif searchAxis == 'y':
        Bx = xCoil.getLargeCoilField()
        By = np.linspace(yCoil.appliedMinField, yCoil.appliedMaxField, steps)
        Bz = zCoil.getLargeCoilField()

        ByInit = yCoil.getLargeCoilField()
        ByInitIndex = find_nearest(By, ByInit)

        for y in By[ByInitIndex::-1]:
            fine_field_cart(Bx, y, Bz, handle)
            resultSum = float(ljm.eReadName(handle,analogInputName))
            resultLR = float(ljm.eReadName(handle, 'AIN0'))
            #time.sleep(0.1)
            if resultSum > minSumSignal:
                time.sleep(10)
                if resultLR > 1:
                    Bysmall = np.linspace(yCoil.coilField-3e-6, yCoil.coilField, 10000)
                    print(Bysmall)
                    for ys in Bysmall[::-1]:

                        fine_field_cart(Bx, ys, Bz, handle)
                        resultSumSmall = float(ljm.eReadName(handle, analogInputName))
                        resultLRSmall = float(ljm.eReadName(handle, 'AIN0'))
                        if resultSumSmall >4.9 and (-0.5 < resultLRSmall < 0.5):
                            print('Finished Beam Search with Bx = {0}, By = {1}, and Bz = {2}'.format(Bx, ys, Bz))
                            return [Bx, ys, Bz]
                elif resultLR < -1.0:

                    Bysmall = np.linspace(yCoil.coilField, yCoil.coilField+3e-6, 10000)
                    print(Bysmall)
                    for ys in Bysmall:
                        fine_field_cart(Bx, ys, Bz, handle)
                        resultSumSmall = float(ljm.eReadName(handle, analogInputName))
                        resultLRSmall = float(ljm.eReadName(handle, 'AIN0'))
                        if resultSumSmall >4.9 and (-0.5 < resultLRSmall < 0.5):
                            print('Finished Beam Search with Bx = {0}, By = {1}, and Bz = {2}'.format(Bx, ys, Bz))
                            return [Bx, ys, Bz]


        for y in By:
            fine_field_cart(Bx,y, Bz, handle)
            #time.sleep(0.1)
            resultSum = float(ljm.eReadName(handle,analogInputName))
            resultLR = float(ljm.eReadName(handle, 'AIN0'))
            #time.sleep(0.1)
            if resultSum > minSumSignal:
                time.sleep(10)
                if resultLR > 4.5:
                    Bysmall = np.linspace(yCoil.coilField-3e-6, yCoil.coilField, 10000)
                    for ys in Bysmall[::-1]:
                        fine_field_cart(Bx, ys, Bz, handle)
                        resultSumSmall = float(ljm.eReadName(handle, analogInputName))
                        resultLRSmall = float(ljm.eReadName(handle, 'AIN0'))
                        if resultSumSmall >4.9 and (-0.5 < resultLRSmall < 0.5):
                            print('Finished Beam Search with Bx = {0}, By = {1}, and Bz = {2}'.format(Bx, ys, Bz))
                            return [Bx, ys, Bz]
                elif resultLR < -4.5:
                    Bysmall = np.linspace(yCoil.coilField, yCoil.coilField+3e-6, 10000)
                    for ys in Bysmall:
                        fine_field_cart(Bx, ys, Bz, handle)
                        resultSumSmall = float(ljm.eReadName(handle, analogInputName))
                        resultLRSmall = float(ljm.eReadName(handle, 'AIN0'))
                        if resultSumSmall >4.9 and (-0.5 < resultLRSmall < 0.5):
                            print('Finished Beam Search with Bx = {0}, By = {1}, and Bz = {2}'.format(Bx, ys, Bz))
                            return [Bx, ys, Bz]


    else:
        Bx = xCoil.getLargeCoilField()
        By = yCoil.getLargeCoilField()
        Bz = np.linspace(zCoil.appliedMinField, zCoil.appliedMaxField, steps)

        BzInit = zCoil.getLargeCoilField()
        BzInitIndex = find_nearest(Bz, BzInit)

        for z in Bz[BzInitIndex::-1]:
            fine_field_cart(Bx, By, z, handle)
            resultSum = float(ljm.eReadName(handle,analogInputName))
            resultLR = float(ljm.eReadName(handle, 'AIN0'))
            time.sleep(0.1)
            if resultSum > minSumSignal and (-2.0 < resultLR < 2.0):
                return [Bx, By, z]

        for z in Bz:
            fine_field_cart(Bx,By, z, handle)
            #time.sleep(0.1)
            resultSum = float(ljm.eReadName(handle,analogInputName))
            resultLR = float(ljm.eReadName(handle, 'AIN0'))
            time.sleep(0.1)
            if resultSum > minSumSignal and (-2.0 < resultLR < 2.0):
                return [Bx, By, z]




def pid(setpoint, position, handle, prePos, integral, initialOutput, t0):
    """
    hello this is a doc string
    """

    '''kP = 0.004
    kD = 0.02
    kI = 0.005
    '''

    kP = 0.01
    kD = 0.05
    kI = 0.4


    #kP = 0.019
    #kD = 0.007
    #kI = 0.4


    # calculate dt and save t0 for the next call.
    t1 = time.time()
    dt = t1 - t0
    t0 = t1

    offset = position - setpoint

    preOffset = prePos - setpoint

    # only set the integral if it is not saturated
    satVal = 2
    # the three conditions are: (in range), (too low but step will bring us closer), ( too high but step will bring us closer)
    if (integral < satVal or integral > -1 * satVal) or (integral < -1 * satVal and offset > 0) or (integral > satVal and offset <= 0):
        integral += (offset * dt)
    #integral += (offset*dt)

    derivative = (offset - preOffset) / dt

    prePos = position # save the position for the next call.

    output = ((kP * offset) + (kI * integral) + (kD * derivative)) * -1e-7 + initialOutput

    # now set the field with the output
    #print('output = %14.11f\toffset = %14.11f\tdt = %14.11f\tintegral = %14.11f' % (output, offset, position, dt, integral))
    print('offset = %14.11f\tintegral = %14.11f\tderivative = %14.11f\tdt = %14.11f'
	 		% (offset, integral, derivative, dt))
    fine_field_cart(xCoil.coilField, output, zCoil.coilField, handle)

    return (offset, integral, derivative, prePos)


def pidLoop(handle, controlAxis='y', fieldVals = None, function='dampen', timeLimit = None,
			dampenLimits = [0.1, 0.1, 5], sumSignalLimit = 3.0):

    # configure the analog register
    # Setup and call eWriteNames to configure the AIN on the LabJack.
    numFrames = 3
    names = ["AIN0_NEGATIVE_CH", "AIN0_RANGE", "AIN0_RESOLUTION_INDEX"]
    aValues = [199, 0, 10] # setup the analog register values for the labjack
    ljm.eWriteNames(handle, numFrames, names, aValues)

    # global variables to be used by the pid loop
    prePos = 0.0 #previous position
    integral = 0.0
    derivative = 0.0
    t0 = time.time()

    setpoint = 0.0
    if fieldVals == None:
        if controlAxis == 'y':
            initialOutput = yCoil.coilField


    counterIndex = 0
    try:
        while True:
	        # take the optical sensor readings from the labjack
            leftMinusRight, sumSignal = ljm.eReadNames(handle, 2, ['AIN0', 'AIN1'])

            if sumSignal > sumSignalLimit: #  if we have a sum signal
                if counterIndex == 0:
                    prePos = leftMinusRight

                offset, integral, derivative, prePos = pid(setpoint, leftMinusRight,handle, prePos, integral,initialOutput, t0) # run the pid loop
                print('offset: {0}, integral: {1}, derivative: {2}, prePos: {3} \n'.format(offset, integral, derivative, prePos))
                if (function == 'dampen') and (abs(offset) <= dampenLimits[0]) and (abs(derivative) <= dampenLimits[1]) and (abs(integral) <=dampenLimits[2]):
                    return


                elif function == 'timed' and time.time() - t0 >= timeLimit:
                    return

            else:
                print('sumSignal = %s' % sumSignal)

                input('Off sensor! (press enter when on sensor)')
                #dt = .001
                #integral = 0
                #derivative = 0
                #pid(setpoint, leftMinusRight, handle)
                #dt = .001
                #integral = 0
                #derivative = 0
                #pid(setpoint, leftMinusRight, handle)
            counterIndex += 1

    except KeyboardInterrupt:
    	time.sleep(.5)
    	print('\n')

        #closePorts(handle)
    	#print('closed all the ports')
    	#print('Keyboard Interrupt') # print the exception
    	#raise
    except Exception as e:
    	# helpful to close the ports on except when debugging the code!
    	time.sleep(.5)
    	#closePorts(handle)
    	#print('closed all the ports')
    	print(e) # print the exception
    	raise

	# work in the optical zero space so we are always adusting perpenductular to the optical zero.

	# each limit will need to be an equation for a line and the max and min values will need to be changesd based on the lineear range of that line.

def kick(xKick, yKick, zKick, waitTime):

    """
    kick the y supply by 100 milliamps for 3 seconds then
    reset the values to their old settings.
    takes: values in field to kick by, and time to wait before
    setting the field back to normal.
    """
    # update the field values
    xField = xyz.xCoil.getLargeCoilField()
    yField = xyz.yCoil.getLargeCoilField()
    zField = xyz.zCoil.getLargeCoilField()

    try:
        # kick the y field:
        xyz.field_cart(xField+xKick, yField+yKick, zField+zKick)

    except:
        xyz.field_cart(xField-xKick, yField-yKick, zField-zKick)
    # wait for waitTime
    time.sleep(waitTime)

    #return field to original values
    xyz.field_cart(xField, yField, zField)

    return



def kickTracking(handle, eventNumber, allTheData=None):
    MAX_REQUESTS = 60 # The number of eStreamRead calls that will be performed.
    FIRST_AIN_CHANNEL = 0 #AIN0
    NUMBER_OF_AINS = 3 # AIN0: L-R, AIN1: Sum, AIN2: T-B

    rawData = []


    info = ljm.getHandleInfo(handle)
    print("Opened a LabJack with Device type: %i, Connection type: %i,\n" \
        "Serial number: %i, IP address: %s, Port: %i,\nMax bytes per MB: %i" % \
        (info[0], info[1], info[2], ljm.numberToIP(info[3]), info[4], info[5]))


    # Stream Configuration
    aScanListNames = ["AIN%i"%i for i in range(FIRST_AIN_CHANNEL, FIRST_AIN_CHANNEL+NUMBER_OF_AINS)] #Scan list names
    print("\nScan List = " + " ".join(aScanListNames))
    numAddresses = len(aScanListNames)
    aScanList = ljm.namesToAddresses(numAddresses, aScanListNames)[0]
    scanRate = 1000
    scansPerRead = int(scanRate/2)

    try:
        # Configure the analog inputs' negative channel, range, settling time and
        # resolution.
        # Note when streaming, negative channels and ranges can be configured for
        # individual analog inputs, but the stream has only one settling time and
        # resolution.
        aNames = ["AIN_ALL_NEGATIVE_CH", "AIN_ALL_RANGE", "STREAM_SETTLING_US",
                  "STREAM_RESOLUTION_INDEX"]
        aValues = [ljm.constants.GND, 10.0, 0, 0] #single-ended, +/-10V, 0 (default),
                                                  #0 (default)
        ljm.eWriteNames(handle, len(aNames), aNames, aValues)


        # kick the pendulum to drive it so we can take period data.
        print('Kicking')
        kickThreadObj = threading.Thread(target=kick, args=(0, 4.5e-6, 0, 10))
        kickThreadObj.start()
        #kick(0, 4.5e-6, 0, 10) # kick the field and save the current values.

        # Configure and start stream
        scanRate = ljm.eStreamStart(handle, scansPerRead, numAddresses, aScanList, scanRate)
        print("\nStream started with a scan rate of %0.0f Hz." % scanRate)

        print("\nPerforming %i stream reads." % MAX_REQUESTS)


        # then do the stream.
        start = datetime.now()
        totScans = 0
        totSkip = 0 # Total skipped samples

        i = 1 # counter for number of stream requests

        while i <= MAX_REQUESTS:
            ret = ljm.eStreamRead(handle)

            data = ret[0]
            scans = len(data)/numAddresses
            totScans += scans

            # Count the skipped samples which are indicated by -9999 values. Missed
            # samples occur after a device's stream buffer overflows and are
            # reported after auto-recover mode ends.
            curSkip = data.count(-9999.0)
            totSkip += curSkip

            print("\neStreamRead %i" % i)
            ainStr = ""
            for j in range(0, numAddresses):
                ainStr += "%s = %0.5f " % (aScanListNames[j], data[j])
            print("  1st scan out of %i: %s" % (scans, ainStr))
            print("  Scans Skipped = %0.0f, Scan Backlogs: Device = %i, LJM = " \
                  "%i" % (curSkip/numAddresses, ret[1], ret[2]))

            newDataChunk = np.reshape(data, (-1,NUMBER_OF_AINS)) # reshape the data to have each row be a different reading

            if i != 1: # if we are not on the first run.
                rawData = np.vstack((rawData, newDataChunk))
            else:
                rawData = newDataChunk # this should only run on the first time.
                #print('FIRST RUN THROUGH')

            #print(rawData,'\n')

            i += 1

        end = datetime.now()

        print("\nTotal scans = %i" % (totScans))
        tt = (end-start).seconds + float((end-start).microseconds)/1000000
        print("Time taken = %f seconds" % (tt))
        print("LJM Scan Rate = %f scans/second" % (scanRate))
        print("Timed Scan Rate = %f scans/second" % (totScans/tt))
        print("Timed Sample Rate = %f samples/second" % (totScans*numAddresses/tt))
        print("Skipped scans = %0.0f" % (totSkip/numAddresses))

        print("\nStop Stream")
        ljm.eStreamStop(handle)

        print('current querry!')
        # update the powersupply field readings so we can reference them later
        xyz.xCoil.getLargeCoilField()
        xyz.yCoil.getLargeCoilField()
        print('done with current querry!')

        # format data to include field values
        rawDataWithFieldValues = []
        for j, row in enumerate(rawData): # setp throuh and append the field values to each datapoint
            rowWithFieldValues = np.append(row, np.array([xyz.xCoil.largeCoilField, xyz.yCoil.largeCoilField, eventNumber])) # for now we aren't using the adustment coils
            if j > 0: # not on the first loop
                rawDataWithFieldValues = np.vstack((rawDataWithFieldValues, rowWithFieldValues))
            else:
                rawDataWithFieldValues = rowWithFieldValues

        # and add it to our master data array
        if eventNumber != 0:
            #print(np.shape(allTheData))
            #print('--------')
            #print(np.shape(rawDataWithFieldValues))
            allTheData = np.vstack((allTheData, rawDataWithFieldValues))
            #print(np.shape(allTheData))
        else:
            allTheData = rawDataWithFieldValues



        return (rawDataWithFieldValues, allTheData)

    except ljm.LJMError:
        ljme = sys.exc_info()[1]
        print(ljme)
        #xyz.closePorts(handle)

    except KeyboardInterrupt: # usefull to have a KeyboardInterrupt when your're debugging
        closePorts(handle)
        # save the data to a DataFrame
        print("saving dataFrame")
        dataFrame = package_my_data_into_a_dataframe_yay(allTheData)
        #dataFrame.to_csv("./data/frequencyVsField/testData.csv")

        # generate timestamp
        timeStamp1 = time.strftime('%y-%m-%d~%H-%M-%S')
        dataFrame.to_csv("./data/frequencyVsField/freqVsField%s.csv" % timeStamp1)


    except Exception as e:
        # helpful to close the ports on except when debugging the code.
        # it prevents the devices from thinking they are still conected and refusing the new connecton
        # on the next open ports call.
        closePorts(handle)
        print('closed all the ports\n')

        print("saving dataFrame")
        dataFrame = package_my_data_into_a_dataframe_yay(allTheData)
        #dataFrame.to_csv("./data/frequencyVsField/testData.csv")

        # generate timestamp
        timeStamp1 = time.strftime('%y-%m-%d~%H-%M-%S')
        dataFrame.to_csv("./data/frequencyVsField/freqVsField%s.csv" % timeStamp1)


        print(e) # print the exception
        raise



def package_my_data_into_a_dataframe_yay(data): # feel more than free to change the name of this function
    """Takes a five column dataset in numpy array form and packaages it into a dataFrame"""
    dataFrame = pd.DataFrame({'leftMinusRight': data[:,0],
                              'sumSignal': data[:,1],
                              'topMinusBottom': data[:,2],
                              'xField': data[:,3],
                              'yField': data[:,4],
                              'eventNumber': data[:,5]})


    # append a time column that is calculated from the scan rate

    # length
    length = len(dataFrame.index)
    time = []
    for i in range(length):
        timestamp = i * (1.0/scanRate)
        time.append(timestamp)

    dataFrame['timeStamp'] = time

    return dataFrame
