import numpy as np
import scipy as sp

def periodCalc (file, sumCrop=1.0):

    data = np.genfromtxt(file, delimiter=',')
    time = data[:,0]
    sumSignal = data[:,1]
    leftRightSignal = data[:,2]

    crossings = []
    rising = False
    for i,e in enumerate(time):

        if sumsig >= sumCrop
        and ((leftRightSignal[i]>0.0
        and leftRightSignal[i-1]<0.0)
        or (leftRightSignal[i]<0.0
        and leftRightSignal[i-1]>0.0)):
            if abs(leftRightSignal[i])<abs(leftRightSignal[i-1]):
                crossings.append(time[i])
            else:
                crossings.append(time[i-1])
    periods = []
    for i,e in enumerate(crossings):
        periods.append(crossings[i+2]-e)

    return periods
