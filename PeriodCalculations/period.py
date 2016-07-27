import numpy as np
import pandas as pd

def periodCalc (data, sumCrop=4.5, swingCrop=3.0):

    eventNumbers = data.eventNumber.unique() # checks for unique event numbers

    periodList=[] #creates an array that will be appended to
    for l in eventnumbers: #goes through data by event number
        selectedData = data[data.eventNumber == l] #only checks event number data

        #crops end where data is bad
        for i in reversed(selectedData.leftMinusRight):
            if selectedData.leftMinusRight[i] >= swingCrop
            or selectedData.leftMinusRight[i] <= -1*swingCrop:
                swingCropIndex = i
                break
        selectedData = slectedData[selectedData.index <= swingCropIndex]

        crossingsIndex=[]
        #checks to see if the sign from one element to the next changes, and then
        #appends the value of the two that is closest to zero
        for i in range(1,len(selectedData.index)):
            if ((selectedData.leftMinusRight[i]>0.0 and selectedData.leftMinusRight[i-1]<0.0)
            or (selectedData.leftMinusRight[i]<0.0 and selectedData.leftMinusRight[i-1]>0.0)):
                if abs(selectedData.leftMinusRight[i]) < abs(selectedData.leftMinusRight[i-1]):
                    crossingsIndex.append(i)
                else:
                    crossingsIndex.append(i-1)

        #creates a boolean array to append to data DataFrame to show crossings
        crossings = np.zeros(len(selectedData.index))
        for i in crossingsIndex:
            crossings[i] = True
        data.crossings = crossings
        #crops data to only include crossings and high sum signal
        newdata = selectedData[selectedData.sumSignal >= sumCrop and selectedData.crossings]

        #resets index
        newdata = newdata.reset_index()
        periods = []
        for i in range(2, len(newdata.index)):
            periods.append(newdata.timeStamp[i]-newdata.timeStamp[i-2])

        avgPeriod = np.mean(periods)
        periodList.append([l, avgPeriod, data.xField.mean(), data.yField.mean()])
    return periodList
