
import xyzFieldControl as xyz
import numpy as np
import time as time
import matplotlib.pyplot as plt

Bx = np.linspace()
By = np.linspace()
backwardsBy = By[::-1]

minSumSignal = 3.0 # analog voltage goes between 0 and 6 volts roughly
sumSignal = np.array([0.0,0.0])
# open the all ports and get the labjack handle
handle - xyz.openPorts()

#lock in the z because we know what it is (don't change it)
zCurrent = (xyz.zCoil.largeCoilCurrent)
# xyz.zCoil.supply.current(439.5)

try:
    for i, xField in enumerate(Bx):
        if i % 2:
            for j, yField in enumerate(By):
                xyz.fine_field_cart(xField, yField, xyz.zCoil.largeCoilField, handle)
                #time.sleep(0.1)
                result = float(xyz.ljm.eReadName(handle,'AIN0'))
                if result > minSumSignal:
                    sumSignal = np.vstack((sumSignal, np.array([xField, yField])))
        else:
            for j, yField in enumerate(backwardsBy):
                xyz.fine_field_cart(xField, yField, xyz.zCoil.largeCoilField, handle)
                #time.sleep(0.1)
                result = float(xyz.ljm.eReadName(handle,'AIN0'))
                if result > minSumSignal:
                    sumSignal = np.vstack((sumSignal, np.array([xField, yField])))

    '''
    # try something a bit more simple
    xyz.field_cart(xyz.xCoil.appliedMaxField, xyz.yCoil.appliedMaxField, xyz.zCoil.largeCoilField)
    '''
    pass
except Exception as e:
    # helpful to close the ports on except when debugging the code!
    xyz.closePorts(handle)
    print('closed all the ports')
    print(e) # print the exception
    raise

# generate timestamp
timeStamp = time.strftime('%m_%d_%y_%H_%M_%S')

# convert sumSignal into numpy array
print(sumSignal)

xarray = sumSignal[:,0]
yarray = sumSignal[:,1]
print(xarray, yarray)

plt.plot(xarray, yarray, 'o')
np.savetxt(timeStamp+'quadtrantSearchData.txt', sumSignal)
plt.savefig(timeStamp + 'quadrantSearch.png')
plt.show()
