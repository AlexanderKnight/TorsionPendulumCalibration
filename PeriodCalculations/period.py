import numpy as np
import pandas as pd

def periodCalc (data, sumCrop=1.0):

    crossingsIndex=[]
    for i in range(1,len(data.index)):
        if ((data.LR[i]>0.0 and data.LR[i-1]<0.0)
        or (data.LR[i]<0.0 and data.LR[i-1]>0.0)):
            crossingsIndex.append(i)
            crossingsIndex.append(i-1)

    for i in crossingsIndex:
        data.crossings[i] = True

    newdata = data[data.sumSignal >= sumCrop]
    newdata = newdata.reset_index()
    periods = []
    for i in range(2, len(newdata.index)):
        periods.append(newdata.time[i]-newdata.time[i-2])

    return periods
