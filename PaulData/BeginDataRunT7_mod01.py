from labjack import ljm
import time
#import struct
import matplotlib.pyplot as plt
import numpy as np
#
# make sure that the next line is the last module imported or you
# may get a bizzarre error (see http://trac-hacks.org/ticket/8235)
from datetime import datetime

#### initialize arrays:
####
sumSignal = np.array([])
LR_Signal = np.array([])
TB_Signal = np.array([])
dataTime = np.array([])

#### SET THESE RUN PARAMETERS BEFORE STARTING RUN;
#### The parameters are stored as a python dictionary:
####
run = '2017-Mar-28-run-01'   # data file base name
pendulum = 'Large Copper Ring (37g)'
micrometer = 'not recorded'      # torsional micrometer setting
runFile = run + '-Data.txt'
columnHeadings = ' Time (S)   sumSignal  LR_Signal  TB_Signal'
tmax = 60.0     # run time
Ix = 421.1
Iy = 384.2
Iz = 463.0

# Open first found LabJack
handle = ljm.open(ljm.constants.dtANY, ljm.constants.ctANY, "ANY")
#handle = ljm.openS("ANY", "ANY", "ANY")

info = ljm.getHandleInfo(handle)
print("Opened a LabJack with Device type: %i, Connection type: %i,\n" \
    "Serial number: %i, IP address: %s, Port: %i,\nMax bytes per MB: %i" % \
    (info[0], info[1], info[2], ljm.numberToIP(info[3]), info[4], info[5]))
###
#### initialize time to zero; grab current time and date:
###
t = 0.0
start = datetime.now()
t0 = time.time()
startTime = str(start)  # for writing to header
###
######   create string with all relevant run info;
######   this string gets written as the file header.
######
hdrText ='run          :' + run + '\n'
hdrText += ' Pendulum = ' + pendulum + '\n'
hdrText += ' micrometer = ' + micrometer + '\n'
hdrText += ' run length = ' + str(tmax) + 'sec\n'
hdrText += ' run start = ' + startTime + '\n'
hdrText += 'Ix, Iy, Iz = ' + str(Ix) + ', ' + str(Iy) + ', ' + str(Iz) + '\n'


print( "starting run!", start)
 # Setup Analog input channel names:
AIN0, AIN1, AIN2 = "AIN0", "AIN1", "AIN2"

while t <= tmax:
    t1 = time.time()-t0
    
    chan0 =  ljm.eReadName(handle, AIN0)
    chan1 =  ljm.eReadName(handle, AIN1)
    chan2 =  ljm.eReadName(handle, AIN2)
    
    t2 = time.time() - t0
    t = 0.5*(t1+t2)
    LR_Signal = np.append(LR_Signal, chan0)
    TB_Signal = np.append(TB_Signal, chan1)
    sumSignal = np.append(sumSignal,chan2)
    
    dataTime = np.append(dataTime, t)

stop = datetime.now()
ljm.close(handle)
stopTime = ' run end = ' +  str(stop) + '\n'
runTime = (stop-start).seconds + float((stop-start).microseconds)/1.0e6
print ("The experiment took %s seconds." % runTime)
hdrText +=  stopTime
hdrText += columnHeadings + '\n'

np.savetxt(runFile,np.c_[dataTime,sumSignal, LR_Signal,TB_Signal],\
fmt='%10.6f', delimiter = '\t', header = hdrText)
print ('Data file ' + runFile + ' written to disc \n')
print (hdrText + '\n')


plt.figure(figsize=(12,14))

plt.subplot(611)
plt.axis('off')
plt.xlim(0,1)
plt.ylim(0,1)
plt.title('Run Summary: Run = ' + run, fontsize=20)
plt.text(0.05, -0.3, hdrText)

plt.subplot(612)
plt.plot(dataTime, sumSignal)
plt.ylabel('sum Signal')
plt.xlim(0,tmax)
plt.title(run + 'micrometer = ' + micrometer, fontsize=16)

plt.subplot(613)
plt.plot(dataTime, LR_Signal)
plt.ylabel('Left - Right')
plt.xlim(0,tmax)

plt.subplot(614)
plt.plot(dataTime, TB_Signal)
plt.ylabel('Top-Bottom')
plt.xlabel('time (s)')
plt.xlim(0,tmax)

plt.subplot(615)
n = len(dataTime)
dt = dataTime[1:n-1] - dataTime[0:n-2]
print(type(dt))
print(dt.mean())
plt.ylabel('Sampling Time Histogram')
plt.hist(dt,bins=100)

plt.subplot(616)
plt.plot(dataTime[0:n-2],dt)
plt.ylabel('Sampling Time Intervals')
plt.tight_layout()
plt.savefig(run + 'Summary'+ '.pdf', dpi=300, orientation='landscape', format='pdf', transparent=False, bbox_inches=None, pad_inches=0.1)
plt.show()
