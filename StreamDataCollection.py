# dataframes

import pandas as pd
import xyzFieldControl as xyz
from labjack import ljm
import time
import sys
from datetime import datetime
import numpy as np

# dataframe packing function
def package_my_data_into_a_dataframe_yay(data):
    """Takes a five column dataset in numpy
    array form and packaages it into a dataFrame"""
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


def kickUpAndWait(xKick, yKick, zKick, waitTime):
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

    # kick the y field:
    xyz.field_cart(xField+xKick, yField+yKick, zField+zKick)

    # wait for waitTime
    time.sleep(waitTime)

    return(xField, yField, zField)

def kickDown(xField, yField, zField):

    xyz.field_cart(xField, yField, zField)
    return



def StreamCollection(time= 60, scanrate=1000, bKick=True):
    #blahx;aksdjf;lak
    #time = max_requests/scanRate in seconds

    MAX_REQUESTS = int(time*scanRate)

    #MAX_REQUESTS = max_requests # The number of eStreamRead calls that will be performed.
    FIRST_AIN_CHANNEL = 0 #AIN0
    NUMBER_OF_AINS = 3 # AIN0: L-R, AIN1: Sum, AIN2: T-B

    rawData = []

    # open the all ports and get the labjack handle
    handle = xyz.openPorts()

    info = ljm.getHandleInfo(handle)
    print("Opened a LabJack with Device type: %i, Connection type: %i,\n" \
        "Serial number: %i, IP address: %s, Port: %i,\nMax bytes per MB: %i" % \
        (info[0], info[1], info[2], ljm.numberToIP(info[3]), info[4], info[5]))


    # Stream Configuration
    aScanListNames = ["AIN%i"%i for i in range(FIRST_AIN_CHANNEL, FIRST_AIN_CHANNEL+NUMBER_OF_AINS)] #Scan list names
    print("\nScan List = " + " ".join(aScanListNames))
    numAddresses = len(aScanListNames)
    aScanList = ljm.namesToAddresses(numAddresses, aScanListNames)[0]
    scanRate = scanrate
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

        eventNumber = 0 # keeps track of the event we make a new one each time the user resets the pendulum and hits enter
        input('start?')
        while True:

            if bKick:
                # kick the pendulum to drive it so we can take period data.
                print('Kicking')
                xr,yr,zr = kickUpAndWait(0, 4.5e-6, 0, 10) # kick the field and save the current values.
                #xr,yr,zr = kickUpAndWait(0, 2e-6, 0, 10) # seems like we maight want a bit less kick

            # Configure and start stream
            scanRate = ljm.eStreamStart(handle, scansPerRead, numAddresses, aScanList, scanRate)
            print("\nStream started with a scan rate of %0.0f Hz." % scanRate)

            print("\nPerforming %i stream reads." % MAX_REQUESTS)

            kickDown(xr,yr,zr) # put the currents back to where they were
            print('Done Kicking!')

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
            print(np.shape(rawDataWithFieldValues))

            # and add it to our master data array
            if eventNumber != 0:
                #print(np.shape(allTheData))
                #print('--------')
                #print(np.shape(rawDataWithFieldValues))
                allTheData = np.vstack((allTheData, rawDataWithFieldValues))
                #print(np.shape(allTheData))
            else:
                allTheData = rawDataWithFieldValues

            print(allTheData)
            print(np.shape(allTheData))

            input("finished with eventNumber %s. Press enter to start a new data run." % eventNumber)
            eventNumber += 1 # increment the event number

    except ljm.LJMError:
        ljme = sys.exc_info()[1]
        print(ljme)
        #xyz.closePorts(handle)

    except KeyboardInterrupt: # usefull to have a KeyboardInterrupt when your're debugging

        # save the data to a DataFrame
        print("saving dataFrame")
        dataFrame = package_my_data_into_a_dataframe_yay(allTheData)
        #dataFrame.to_csv("./data/frequencyVsField/testData.csv")

        # generate timestamp
        timeStamp1 = time.strftime('%y-%m-%d~%H-%M-%S')
        dataFrame.to_csv("./data/frequencyVsField/freqVsField%s.csv" % timeStamp1)

        xyz.closePorts(handle)

    except Exception as e:
        # helpful to close the ports on except when debugging the code.
        # it prevents the devices from thinking they are still conected and refusing the new connecton
        # on the next open ports call.


        print("saving dataFrame")
        dataFrame = package_my_data_into_a_dataframe_yay(allTheData)
        #dataFrame.to_csv("./data/frequencyVsField/testData.csv")

        # generate timestamp
        timeStamp1 = time.strftime('%y-%m-%d~%H-%M-%S')
        dataFrame.to_csv("./data/frequencyVsField/freqVsField%s.csv" % timeStamp1)

        xyz.closePorts(handle)
        print('closed all the ports\n')

        print(e) # print the exception
        raise
