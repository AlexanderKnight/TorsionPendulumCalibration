import numpy as np
import matplotlib.pyplot as plt


data = np.loadtxt('/home/pauln/Dropbox/DocumentsF/' +
'_Research/LabjackDevelopment/2014-02-24_Data/2014_02_24-run01Data.txt',
 skiprows=1)
dt = []
times = data[:, 0]
n = len(times) - 1
dt[0:n] = times[1:n] - times[0:n - 1]
deltaT = np.mean(dt)
print deltaT

tbSignal = data[:, 3]

tb = tbSignal[0:len(times)]
timeSlice = times[0:len(times)]

plt.subplot(211)
plt.plot(timeSlice, tb)
plt.subplot(212)
rawPSD = plt.psd(tb, NFFT=511, Fs=1.0 / deltaT)

plt.show()