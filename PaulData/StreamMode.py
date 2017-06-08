# -*- coding: utf-8 -*-
"""
Created on Mon Feb 10 15:03:20 2014

@author: paulnakroshis
"""

# streamU3.py
# Peter N. Saeta, 2011 July 2
# Using the LabJack U3, sample four voltages at a fixed sampling rate
# and log the results to a text file. This file can then be used by
# Igor to manage further analysis

import u6
from time import sleep
from math import *

# Prepare the u3 interface for streaming

d = u6.U6()		# initialize the interface; assumes a single U3 is plugged in to a USB port
d.configU6()	# set default configuration
#d.configIO( FIOAnalog = 1 )		# ask for analog inputs

# The following requests 4 analog input channels to be streamed,
# with the positive terminals being 0-3 and the negative terminals
# all set to 31. The sampling frequency is 5000 samples (of each channel)
# per second. The Resolution parameter sets the effective quality of the
# samples. See http://labjack.com/support/u3/users-guide/3.2
d.streamConfig( NumChannels = 4,
	PChannels = [ 0, 1, 2, 3 ],
	NChannels = [ 31, 31, 31, 31 ],
	Resolution = 3,
	SampleFrequency = 5000 )

d.packetsPerRequest = 100     # you can adjust this value to get more or less data

# Try to measure a data set.
def measure():
	try:
		d.streamStart()

		for r in d.streamData():
			if r is not None:
				if r['errors'] or r['numPackets'] != d.packetsPerRequest or r['missed']:
					print "error"
				break
	finally:
		d.streamStop()
	return r

# Write a set of data to a file "myGloriousData.txt"
def writeData( r ):
	f = open( 'myGloriousData.txt', 'w' )
	ch0 = r['AIN0']
	ch1 = r['AIN1']
	ch2 = r['AIN2']
	ch3 = r['AIN3']
	for i in range(0, len(ch0)-1):
		f.write( '{0:.6f}\t{1:.6f}\t{2:.6f}\t{3:.6f}\n'.format(ch0[i],ch1[i],ch2[i],ch3[i]) )
	f.close()

for i in range(1,10):
	writeData( measure() )
	sleep(1)		# sleep for 1 second