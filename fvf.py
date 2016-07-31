import sys
sys.path.append("./Python_LJM 3/") # check that this works properly
from labjack import ljm # import labjack library
import xyzFieldControl as xyz
import numpy as np
import time
import matplotlib.pyplot as plt

# open the all ports and get the labjack handle
handle = xyz.openPorts()


steps = 1000
print(xyz.xCoil.appliedMinField, xyz.xCoil.appliedMaxField, xyz.yCoil.appliedMinField, xyz.yCoil.appliedMaxField)
Bx = np.linspace(xyz.xCoil.appliedMaxField, xyz.xCoil.appliedMinField, 7) # start from the high field
By = np.linspace(xyz.yCoil.appliedMinField, xyz.yCoil.appliedMaxField, 20000)
#Bz = np.linspace(56.0, 62.0, 200)



minSumSignal = 3.0

sumSignal = []

# analog input to read from the labjack
analogInputName = 'AIN1'


try:
    for i in range(len(Bx)):
        if i % 2:
            for j in range(len(By)):
                xyz.field_cart(Bx[i],By[j],xyz.zCoil.largeCoilField) #,handle)
                #time.sleep(0.1)
                result = float(ljm.eReadName(handle,analogInputName))
                if result > minSumSignal:
                    sumSignal.append([Bx[i],By[j]])
        else:

            for j in range(len(By)):
                xyz.field_cart(Bx[i],By[-(j+1)],xyz.zCoil.largeCoilField) #, handle)
                #time.sleep(0.1)
                result = float(ljm.eReadName(handle,analogInputName))
                if result > minSumSignal:
                    sumSignal.append([Bx[i],By[-(j+1)]])

except KeyboardInterrupt:
    print('\n')
    xyz.closePorts(handle)
    print('closed all the ports')
    timeStamp = time.strftime('%m_%d_%y_%H_%M_%S')
    np.savetxt(timeStamp+'quadtrantSearchData.txt', sumSignal) # save the data
    raise

except Exception as e:
    # helpful to close the ports on except when debugging the code.
    # it prevents the devices from thinking they are still conected and refusing the new connecton
    # on the next open ports call.
    xyz.closePorts(handle)
    print('closed all the ports')
    print(e) # print the exception
    raise

# plot the data

# generate timestamp
timeStamp = time.strftime('%m_%d_%y_%H_%M_%S')

for i in range(len(sumSignal)):
    plt.scatter(sumSignal[i][0],sumSignal[i][1])
np.savetxt(timeStamp+'quadtrantSearchData.txt', sumSignal)
plt.savefig(timeStamp + 'quadrantSearch.png')
plt.show()
##############
