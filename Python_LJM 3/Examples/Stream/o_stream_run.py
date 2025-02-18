"""
Demonstrates setting up stream-in and stream-out together, then reading
stream-in values.

Connect a wire from AIN0 to DAC0 to see the effect of stream-out on
stream-in channel 0.

"""

from labjack import ljm
import time
import sys
from datetime import datetime

MAX_REQUESTS = 20 # The number of eStreamRead calls that will be performed.

# Open first found LabJack
handle = ljm.openS("ANY", "ANY", "ANY")
#handle = ljm.open(ljm.constants.dtANY, ljm.constants.ctANY, "ANY")


info = ljm.getHandleInfo(handle)
print("Opened a LabJack with Device type: %i, Connection type: %i,\n" \
    "Serial number: %i, IP address: %s, Port: %i,\nMax bytes per MB: %i" % \
    (info[0], info[1], info[2], ljm.numberToIP(info[3]), info[4], info[5]))


# Setup Stream Out
OUT_NAMES = ["DAC0"]
NUM_OUT_CHANNELS = len(OUT_NAMES)
outAddress = ljm.nameToAddress(OUT_NAMES[0])[0]

# Allocate memory for the stream-out buffer
ljm.eWriteName(handle, "STREAM_OUT0_TARGET", outAddress)
ljm.eWriteName(handle, "STREAM_OUT0_BUFFER_SIZE", 512)
ljm.eWriteName(handle, "STREAM_OUT0_ENABLE", 1)

# Write values to the stream-out buffer
ljm.eWriteName(handle, "STREAM_OUT0_LOOP_SIZE", 6)
ljm.eWriteName(handle, "STREAM_OUT0_BUFFER_F32", 0.0) # 0.0 V
ljm.eWriteName(handle, "STREAM_OUT0_BUFFER_F32", 1.0) # 1.0 V
ljm.eWriteName(handle, "STREAM_OUT0_BUFFER_F32", 2.0) # 2.0 V
ljm.eWriteName(handle, "STREAM_OUT0_BUFFER_F32", 3.0) # 3.0 V
ljm.eWriteName(handle, "STREAM_OUT0_BUFFER_F32", 4.0) # 4.0 V
ljm.eWriteName(handle, "STREAM_OUT0_BUFFER_F32", 5.0) # 5.0 V

ljm.eWriteName(handle, "STREAM_OUT0_SET_LOOP", 1)

print("STREAM_OUT0_BUFFER_STATUS = %f" % (ljm.eReadName(handle, "STREAM_OUT0_BUFFER_STATUS")))
    

# Stream Configuration
POS_IN_NAMES = ["AIN0", "AIN1"]
NUM_IN_CHANNELS = len(POS_IN_NAMES)

TOTAL_NUM_CHANNELS = NUM_IN_CHANNELS + NUM_OUT_CHANNELS


#Add positive channels to scan list
aScanList = ljm.namesToAddresses(NUM_IN_CHANNELS, POS_IN_NAMES)[0]
scanRate = 2000
scansPerRead = 60

# Add the stream out token 4800 to the end
aScanList.extend([4800])

# Add the scan list outputs to the end of the scan list.
# STREAM_OUT0 = 4800, STREAM_OUT1 = 4801, etc.
aScanList.extend([4800]) # STREAM_OUT0
# If we had more STREAM_OUTs
# aScanList.extend([4801]) # STREAM_OUT1
# aScanList.extend([4802]) # STREAM_OUT2
# etc.
            
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

    # Configure and start stream
    print(aScanList[0:TOTAL_NUM_CHANNELS])
    scanRate = ljm.eStreamStart(handle, scansPerRead, TOTAL_NUM_CHANNELS, aScanList, scanRate)
    print("\nStream started with a scan rate of %0.0f Hz." % scanRate)

    print("\nPerforming %i stream reads." % MAX_REQUESTS)
    start = datetime.now()
    totScans = 0
    totSkip = 0 # Total skipped samples

    i = 1
    while i <= MAX_REQUESTS:
        ret = ljm.eStreamRead(handle)

        # Note that the Python eStreamData will return a data list of size
        # scansPerRead*TOTAL_NUM_CHANNELS, but only the first
        # scansPerRead*NUM_IN_CHANNELS samples in the list are valid. Output
        # channels are not included in the eStreamRead's returned data.
        data = ret[0][0:scansPerRead*NUM_IN_CHANNELS]
        scans = len(data)/NUM_IN_CHANNELS
        totScans += scans
        
        # Count the skipped samples which are indicated by -9999 values. Missed
        # samples occur after a device's stream buffer overflows and are
        # reported after auto-recover mode ends.
        curSkip = data.count(-9999.0)
        totSkip += curSkip
        
        print("\neStreamRead #%i, %i scans" % (i, scans))
        for j in range(0, scansPerRead):
            ainStr = ""
            for k in range(0, NUM_IN_CHANNELS):
                ainStr += "%s: %0.5f, " % (POS_IN_NAMES[k], data[j*NUM_IN_CHANNELS + k])
            print("  %s" % (ainStr))
        print("  Scans Skipped = %0.0f, Scan Backlogs: Device = %i, LJM = " \
              "%i" % (curSkip/NUM_IN_CHANNELS, ret[1], ret[2]))
        i += 1

    end = datetime.now()

    print("\nTotal scans = %i" % (totScans))
    tt = (end-start).seconds + float((end-start).microseconds)/1000000
    print("Time taken = %f seconds" % (tt))
    print("LJM Scan Rate = %f scans/second" % (scanRate))
    print("Timed Scan Rate = %f scans/second" % (totScans/tt))
    print("Timed Sample Rate = %f samples/second" % (totScans*NUM_IN_CHANNELS/tt))
    print("Skipped scans = %0.0f" % (totSkip/NUM_IN_CHANNELS))
except ljm.LJMError:
    ljme = sys.exc_info()[1]
    print(ljme)
except Exception:
    e = sys.exc_info()[1]
    print(e)

print("\nStop Stream")
ljm.eStreamStop(handle)

# Close handle
ljm.close(handle)
