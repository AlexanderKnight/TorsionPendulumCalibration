import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from time import sleep

def periodCalc (data, sumCrop=4.5, swingCrop=None, viewGraph=True):

    eventNumbers = data.eventNumber.unique() # checks for unique event numbers

    #periodList= pd.DataFrame(columns=['eventNumber', 'avgPeriod', 'xField', 'yField'])#creates an array that will be appended to
    first=True

    for l in eventNumbers: #goes through data by event number
        print('%s of %s'%(int(l), len(eventNumbers)))
        selectedData = data.loc[data.eventNumber == l] #only checks event number data
        selectedData = selectedData.reset_index()
        #crops end where data is bad
        if swingCrop != None:
            for i in reversed(selectedData.leftMinusRight.index):
                if selectedData.leftMinusRight[i] >= swingCrop \
                or selectedData.leftMinusRight[i] <= -1*swingCrop:
                    CropIndex = i
                    break
        if viewGraph:
            x = selectedData.index
            y = selectedData.leftMinusRight
            z = selectedData.sumSignal
            plt.figure(figsize=(15,12))
            plt.plot(x,y, 'o')
            plt.plot(x,z, 'o')
            plt.xlabel('Index')
            plt.ylabel('Sum Signal and L-R Signal')
            plt.show()
            CropIndex = 1000*int(input('Please enter the end index value for analysis in thousands, \n e.g. 13 for index 13,000 (0 for all): '))
            if CropIndex == 0:
                CropIndex = max(selectedData.index)+1
        selectedData = selectedData[selectedData.index <= CropIndex]

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
        selectedData['crossings'] = pd.Series(crossings, index=selectedData.index)
        #crops data to only include crossings and high sum signal
        newdata = selectedData.loc[selectedData['sumSignal'] >= sumCrop]
        newdata = newdata.loc[newdata['crossings'] == True]


        #resets index
        newdata = newdata.reset_index()
        periods = []
        for i in range(2, len(newdata.index)):
            periods.append(newdata.timeStamp[i]-newdata.timeStamp[i-2])

        avgPeriod = np.mean(periods)
        if first:

            d = {'eventNumber':l, 'avgPeriod':avgPeriod, 'xField':newdata.xField.mean(), 'yField':newdata.yField.mean()}
            periodList = pd.DataFrame(d, index=[0])

            first=False
        else:

            tempdf = pd.DataFrame({'eventNumber':l, 'avgPeriod':avgPeriod, 'xField':newdata.xField.mean(), 'yField':newdata.yField.mean()}, index=[0])
            periodList= pd.concat([periodList,tempdf], ignore_index=True)

    return periodList

Data = pd.read_csv('freqVsField16-07-29~16-17-18.csv')
print(periodCalc(Data))
