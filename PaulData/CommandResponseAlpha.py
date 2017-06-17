# -*- coding: utf-8 -*-
"""
Created on Thu Mar 30 12:32:51 2017

@author: Paul Nakroshis

Switch the data taking code to use command-response mode on LabJack T7-Pro


"""
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
run = '2017-Mar-31-run-06'   # data file base name
pendulum = 'Large Copper Ring (37g)'
micrometer = 'not recorded'      # torsional micrometer setting
runFile = run + '-Data.txt'
columnHeadings = ' Time (S)   sumSignal  LR_Signal  TB_Signal'
###
###
###    Length of run in Minutes:

t_minutes = 6.0

###
###
tmax = t_minutes*60     # run time
Ix = 0.0
Iy = 0.0
Iz = 0.0

# Open first found LabJack
handle = ljm.open(ljm.constants.dtANY, ljm.constants.ctANY, "ANY")
#handle = ljm.openS("ANY", "ANY", "ANY")

info = ljm.getHandleInfo(handle)
print("Opened a LabJack with Device type: %i, Connection type: %i,\n" \
    "Serial number: %i, IP address: %s, Port: %i,\nMax bytes per MB: %i" % \
    (info[0], info[1], info[2], ljm.numberToIP(info[3]), info[4], info[5]))

# Setup Analog input channel names:

lr_V, tb_V, sum_V = "AIN0", "AIN1", "AIN2"

# Setup Analog input channel ranges:
# (options: 0 = +/- 10V,  1 = +/- 1V,  0.1 = +/- 0.1V, 0.01 = +/- 0.01V)
ljm.eWriteName(handle, "AIN0_RANGE", 1)  # set to +/- 1 Volt
ljm.eWriteName(handle, "AIN1_RANGE", 1)
ljm.eWriteName(handle, "AIN2_RANGE", 1)

# Setup Analog input channel sampling resolution
ljm.eWriteName(handle, "AIN0_RESOLUTION_INDEX", 8)
ljm.eWriteName(handle, "AIN1_RESOLUTION_INDEX", 8)
ljm.eWriteName(handle, "AIN2_RESOLUTION_INDEX", 8)


# Here is the chart for resolution when set to +/- 10 V:
# Resolution	Effective	   Effective	  AIN Sample
# Index	      Resolution	 Resolution	   Time
#             [bits]	     [µV]	        [ms/sample]
#  1	         16.0	       316	        0.04
#  2	         16.5	       223	        0.04
#  3	         17.0	       158	        0.06
#  4	         17.5	       112	        0.09
#  5	         17.9	        85	        0.16
#  6	         18.3	        64	        0.29
#  7	         18.8	        45	        0.56
#  8	         19.1	        37	        1.09
#  9	         19.6	        26	        3.50
# 10	         20.5	        14	        13.4
# 11	         21.4	         7.5	      66.2
# 12	         21.8	         5.7	      159.0

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

while t <= tmax:
    t1 = time.time()-t0

    lr_V_sample =  ljm.eReadName(handle, lr_V)
    tb_V_sample =  ljm.eReadName(handle, tb_V)
    sum_V_sample =  ljm.eReadName(handle, sum_V)

    t2 = time.time() - t0
    t = 0.5*(t1+t2)
    LR_Signal = np.append(LR_Signal, lr_V_sample)
    TB_Signal = np.append(TB_Signal, tb_V_sample)
    sumSignal = np.append(sumSignal, sum_V_sample)

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
plt.tight_layout(pad=0.1)
plt.savefig(run + 'Summary'+ '.pdf', dpi=300, orientation='landscape', format='pdf', transparent=False, bbox_inches=None, pad_inches=0.05)
plt.show()
