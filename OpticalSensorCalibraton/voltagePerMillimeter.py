"""
In this file we want to generate a text file that will let us calibrate the optical sensor and determine its angular resolution.
we are going to be reading from the z-axis sensor (top-bottom) and cranking the optical stage
through the full range of the quadrent sensor.

we can read the sensor signal automaticly with the labjack, but we need to ask the user
for the stage position. we can ease the process by asking the user to set the stage to a value and then taking a reading,
but we wnat to keep it simple.
"""

# imports
import time as time
import numpy as np
import sys
sys.path.append("./../Python_LJM 3") # use the local copy of the ljm library
from labjack import ljm # local labjack module


# Open first found LabJack
handle = ljm.open(ljm.constants.dtANY, ljm.constants.ctANY, "ANY")

try:
    # print LabJack config info
    info = ljm.getHandleInfo(handle)
    print("Opened a LabJack with Device type: %i, Connection type: %i,\n" \
        "Serial number: %i, IP address: %s, Port: %i,\nMax bytes per MB: %i" % \
        (info[0], info[1], info[2], ljm.numberToIP(info[3]), info[4], info[5]))

    # configure the LabJack
    # Setup and call eWriteNames to configure the AIN on the LabJack.
    numFrames = 3
    names = ["AIN0_NEGATIVE_CH", "AIN0_RANGE", "AIN0_RESOLUTION_INDEX"]
    aValues = [199, 0, 9]
    ljm.eWriteNames(handle, numFrames, names, aValues)

    # print the configureaton.
    print("\nSet configuration:")
    for i in range(numFrames):
        print("    %s : %f" % (names[i], aValues[i]))


    # make a file so we can store the data:
    # create a timestamp so we can have a uneque file name each time.
    timeStamp = time.strftime('%m_%d_%y_%H_%M_%S')
    f = open("voltsPerMillimeter"+timeStamp+".txt", "w") # open a new text file in write mode


    # ask the user to decide where the experement will start. we will be sweeping up in value so start low
    STARTING_STAGE_POSITION = float(input('What is the low starting position of the optical stage in mm? \n -->'))

    END_STAGE_POSITION = float(input('set the END_STAGE_POSITION in mm \n -->'))

    NUMBER_OF_DATA_POINTS = float(input('How manny data points? \n -->')) + 1

    stagePositions = np.linspace(STARTING_STAGE_POSITION, END_STAGE_POSITION, NUMBER_OF_DATA_POINTS)
    print(stagePositions)




    name = "AIN0" # analog channel to read on the LabJack

    for i, stagePos in enumerate(stagePositions):
        # verify that the stage is set to the starting value:
        input('Please set the stage to %s mm.' % stagePos)
        # read the value of the LabJack
        result = ljm.eReadName(handle, name)

        # save the data to the text file.
        f.write("%s, %s\n" % (stagePos, result))


    ljm.close(handle)
    f.close()

except Exception as e:
    ljm.close(handle)
    f.close()
    raise
