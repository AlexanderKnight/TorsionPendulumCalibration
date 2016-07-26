# dataframes

import pandas as pd
import xyzFieldControl as xyz
from labjack import ljm
import time
import sys
from datetime import datetime
import numpy as np

MAX_REQUESTS = 50 # The number of eStreamRead calls that will be performed.
FIRST_AIN_CHANNEL = 0 #AIN0
NUMBER_OF_AINS = 3 # AIN0: L-R, AIN1: Sum, AIN2: T-B

rawData = [0,0,0]

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


    while True:
        # Configure and start stream
        scanRate = ljm.eStreamStart(handle, scansPerRead, numAddresses, aScanList, scanRate)
        print("\nStream started with a scan rate of %0.0f Hz." % scanRate)

        print("\nPerforming %i stream reads." % MAX_REQUESTS)
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
            rawData = np.vstack((rawData, newDataChunk)) # append the data to the data List
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

        input("press enter to start a new scan")

except ljm.LJMError:
    ljme = sys.exc_info()[1]
    print(ljme)
    #xyz.closePorts(handle)

except KeyboardInterrupt: # usefull to have a KeyboardInterrupt when your're debugging
    #xyz.closePorts(handle)
    # save the data to a DataFrame
    print(rawData)

except Exception as e:
    # helpful to close the ports on except when debugging the code.
    # it prevents the devices from thinking they are still conected and refusing the new connecton
    # on the next open ports call.
    xyz.closePorts(handle)
    print('closed all the ports\n')
    print(e) # print the exception
    raise

xyz.closePorts(handle)
print('closed all the ports\n')


def package_my_data_into_a_dataframe_yay(data): # feel more than free to change the name of this function
    """Takes a three column dataset in numpy array form and packaages it into a dataFrame"""
    dataFrame = pd.DataFrame({'leftMinusRight': data[:,0], 'Sum': data[:,1], 'TopMinusBottom': data[:,2]})
    return dataFrame

print("saving dataFrame")
dataFrame = package_my_data_into_a_dataframe_yay(rawData)
dataFrame.to_csv("./data/freequencyVsField/testData.csv")


#data = pd.DataFrame({'Time': [0,1,2,3,4,5], 'Sum':[5,5,5,5,0,3]}, index = [0,1,3,4,6,7]) #

#print(data)
#data.to_csv("./data/freequencyVsField/test.csv")
