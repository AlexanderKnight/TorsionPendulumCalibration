import numpy as np
import pandas as pd


def periodCalc (data, sumCrop=4.5, swingCrop=4.5):

    eventNumbers = data.eventNumber.unique() # checks for unique event numbers
    print(eventNumbers)
    periodList=[] #creates an array that will be appended to
    selectedData = []
    for i in eventNumbers:
        selectedData.append(data.loc[data.eventNumber == i])
    for j,e in enumerate(selectedData): #goes through data by event number
        print(j)
        #selectedData = data[data.eventNumber == l] #only checks event number data

        #crops end where data is bad
        for i in reversed(e.leftMinusRight.index):
            if e.leftMinusRight[i] >= swingCrop \
            or e.leftMinusRight[i] <= -1*swingCrop:
                swingCropIndex = i
                break
        e = e[e.index <= swingCropIndex]

        crossingsIndex=[]
        #checks to see if the sign from one element to the next changes, and then
        #appends the value of the two that is closest to zero
        print(e.leftMinusRight[10])
        for i in range(1,len(e.index)):
            if ((e.leftMinusRight[i]>0.0 and e.leftMinusRight[i-1]<0.0)
            or (e.leftMinusRight[i]<0.0 and e.leftMinusRight[i-1]>0.0)):
                if abs(e.leftMinusRight[i]) < abs(e.leftMinusRight[i-1]):
                    crossingsIndex.append(i)
                else:
                    crossingsIndex.append(i-1)

        #creates a boolean array to append to data DataFrame to show crossings
        crossings = np.zeros(len(e.index))

        for i in crossingsIndex:
            crossings[i] = True
        e.loc['crossings'] = pd.Series(crossings, index=e.index)
        #crops data to only include crossings and high sum signal
        newdata = e.loc[e['sumSignal'] >= sumCrop]
        newdata = newdata.loc[newdata['crossings'] == True]


        #resets index
        newdata = newdata.reset_index()
        periods = []
        for i in range(2, len(newdata.index)):
            periods.append(newdata.timeStamp[i]-newdata.timeStamp[i-2])

        avgPeriod = np.mean(periods)
        periodList.append([j, avgPeriod, data.xField.mean(), data.yField.mean()])
    return periodList

Data = pd.read_csv('freqVsField16-07-29~16-17-18.csv')
print(periodCalc(Data))
