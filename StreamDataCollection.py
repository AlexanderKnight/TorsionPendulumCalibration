# dataframes

import pandas as pd
import xyzFieldControl as xyz
from labjack import ljm
import time
import sys
from datetime import datetime

MAX_REQUESTS = 50 # The number of eStreamRead calls that will be performed.
FIRST_AIN_CHANNEL = 0 #AIN0
NUMBER_OF_AINS = 3 # AIN0: L-R, AIN1: Sum, AIN2: T-B

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
    # all labjack code in this try/except you could put all your code here!
    while True:
        print("hi")
except KeyboardInterrupt: # usefull to have a KeyboardInterrupt when your're debugging
    xyz.closePorts(handle)

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




#data = pd.DataFrame({'Time': [0,1,2,3,4,5], 'Sum':[5,5,5,5,0,3]}, index = [0,1,3,4,6,7]) #

#print(data)
#data.to_csv("./data/freequencyVsField/test.csv")
