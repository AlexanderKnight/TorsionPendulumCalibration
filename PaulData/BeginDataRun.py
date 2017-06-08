import u6
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
runParams = {
    'runName':'2014-04-11-run-00',
    'pendulum':'Glass Disk & Alum Loop',
    'micrometer':'6.77 mm',
    'runFile':'2014-04-11-run-00-Data.txt',
    'tmax':180.0,
    'res':8,
    'settling':5}
run = '2014-04-11-run-00'   # data file base name
pendulum = 'Glass Disc & Al Loop'
micrometer = '6.77 mm'      # torsional micrometer setting
runFile = run + '-Data.txt'
columnHeadings = ' Time (S)   sumSignal  LR_Signal  TB_Signal'
tmax = 180.0     # run time
res = 8         # resolution: 0=default, 1-8 high speed ADC; 9-12 high res ADC
setFactor = 5   # settling factor: 0 = auto, 1=20 us, 2=50 us, 3=100 us
                # 4=200 us, 5=500 us, 6=1 ms, 7=2 ms, 8=5ms, 9=10 ms
        # Anecdotally:
        # hand picking a settling factor seems to result in more
        # uniform sampling rates.
###
"""
G = x1 (+/-10V)

Single Channel	8 Channels

Res bits	ms	    ms

1	16.1	0.65	1.4
2	16.4	0.65	1.5
3	16.9	0.65	1.6
4	17.5	0.65	2.0
5	17.9	0.68	2.6
6	18.4	0.85	4.0
7	18.8	1.2	    6.6
8	19.0	1.8	    12
9	19.7	4.1	    30
10	20.6	14	    110
11	21.3	68	    530
12	22.0	161	    1280
"""

###################################
###  open LabJack and apply proper calibrations:
##
d = u6.U6()
d.configU6()
d.getCalibrationData()
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
hdrText += 'resolution = ' + str(res) + '\n'
hdrText += 'settling time = ' + str(setFactor) + '\n'


print "starting run!", start

while t <= tmax:
    t1 = time.time()-t0
    chan0 =  d.getAIN(0, resolutionIndex=res, settlingFactor=setFactor)
    chan1 =  d.getAIN(1, resolutionIndex=res, settlingFactor=setFactor)
    chan2 =  d.getAIN(2, resolutionIndex=res, settlingFactor=setFactor)
    t2 = time.time() - t0
    t = 0.5*(t1+t2)
    sumSignal = np.append(sumSignal,chan0)
    LR_Signal = np.append(LR_Signal, chan1)
    TB_Signal = np.append(TB_Signal, chan2)
    dataTime = np.append(dataTime, t)

stop = datetime.now()
d.close()
stopTime = ' run end = ' +  str(stop) + '\n'
runTime = (stop-start).seconds + float((stop-start).microseconds)/1.0e6
print "The experiment took %s seconds." % runTime
hdrText +=  stopTime
hdrText += columnHeadings + '\n'

np.savetxt(runFile,np.c_[dataTime,sumSignal, LR_Signal,TB_Signal],\
fmt='%10.6f', delimiter = '\t', header = hdrText)
print 'Data file ' + runFile + ' written to disc \n'
print hdrText + '\n'


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
print type(dt)
print dt.mean()
plt.ylabel('Sampling Time Histogram')
plt.hist(dt,bins=100)

plt.subplot(616)
plt.plot(dataTime[0:n-2],dt)
plt.ylabel('Sampling Time Intervals')
plt.tight_layout()
plt.savefig(run + 'Summary'+ '.pdf', dpi=300, orientation='landscape', format='pdf', transparent=False, bbox_inches=None, pad_inches=0.1)
plt.show()
