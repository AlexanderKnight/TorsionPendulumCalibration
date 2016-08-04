import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from time import sleep

def periodCalc (data, sumCrop=4.5, swingCrop=None, viewGraph=True):
    '''
    This function takes a pandas dataframe of signal data and calculates the
    period from the zero crossings, by event numbers.

    input: dataframe with columns=['eventNumber', 'sumSignal',
                                    'leftMinusRight', 'topMinusBotom',
                                    'xField', 'yField', 'timeStamp']
    output: dataframe with columns=['eventNumber', 'avgPeriod',
                                    'xField', 'yField', 'netField']

    Variables
    ------------
    sumCrop(float): value for which all data be ignored if sumSignal is lower than it

    swingCrop(float/None): a +/- value to stop counting when the signal dampens out, checks
                backwards, until swingCrop or (-swingCrop) is met by
                leftMinusRight, and then crops off all data after that index.
                May not work if the data wanders high or low after good crossings.

    viewGraph(bool): allows the user to see a graph of the leftMinusRight and sumSignal
                data, and then prompts for a last index value for analysis.
                Allows for wandering data, as people tend to be better at picking
                out bad wandering signals than computers.
    '''
    eventNumbers = data.eventNumber.unique() # checks for unique event numbers

    #set up for a couple of checks in the loop
    first=True

    for j,l in enumerate(eventNumbers): #goes through data by event number

        print('%s of %s'%(int(l), len(eventNumbers)))#prints which event number

        selectedData = data.loc[data.eventNumber == l] #only checks event number data
        selectedData = selectedData.reset_index()

        #crops end where data is no longer swinging consistantly
        if swingCrop != None:
            for i in reversed(selectedData.leftMinusRight.index):
                if selectedData.leftMinusRight[i] >= swingCrop \
                or selectedData.leftMinusRight[i] <= -1*swingCrop:
                    CropIndex = i
                    break

        #shows users the data, and asks for index to crop after
        if viewGraph:
            repeat = True
            while repeat:
                x = selectedData.index
                y = selectedData.leftMinusRight
                z = selectedData.sumSignal
                plt.figure(figsize=(15,12))
                plt.plot(x,y, 'o')
                plt.plot(x,z, 'o')
                plt.xlabel('Index')
                plt.ylabel('Sum Signal and L-R Signal')
                plt.show()
                try:
                    CropIndex = 1000*int(input('Please enter the end index value \
                                for analysis in thousands, \n e.g. 13 for index \
                                13,000 (0 for all): '))
                    repeat = False
                if CropIndex == 0:
                    CropIndex = max(selectedData.index)+1
                    repeat = False

        #crops index
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

        #adds column to data of crossing value
        selectedData['crossings'] = pd.Series(crossings, index=selectedData.index)

        #crops data to only include crossings and high sum signal
        newdata = selectedData.loc[selectedData['sumSignal'] >= sumCrop]
        newdata = newdata.loc[newdata['crossings'] == True]


        #resets index
        newdata = newdata.reset_index()

        #gets periods of crossings
        periods = []
        for i in range(2, len(newdata.index)):
            periods.append(newdata.timeStamp[i]-newdata.timeStamp[i-2])

        #gets average period
        avgPeriod = np.mean(periods)
        stdPeriods = np.std(periods)
        numPeriods = len(periods)

        #if first time through loop (usually eventNumber = 0), sets up return
        #database
        if first:

            d = {'eventNumber':l, 'avgPeriod':avgPeriod,
                'periodSTD': stdPeriods, 'numPeriods': numPeriods,
                'xField':newdata.xField.mean(), 'yField':newdata.yField.mean(),
                'netField':np.sqrt(newdata.xField.mean()**2+newdata.yField.mean()**2)}
            periodList = pd.DataFrame(d, index=[0])

            first=False

        #adds to set up database from above
        else:

            tempdf = pd.DataFrame({'eventNumber':l, 'avgPeriod':avgPeriod,
                                'periodSTD':stdPeriods, 'numPeriods':numPeriods,
                                'xField':newdata.xField.mean(),
                                'yField':newdata.yField.mean(),
                                'netField':np.sqrt(newdata.xField.mean()**2+newdata.yField.mean()**2)}
                                , index=[0])
            periodList= pd.concat([periodList,tempdf], ignore_index=True)


    return periodList
