import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sympy import symbols
from sympy.plotting import textplot
from time import sleep


def periodCalc (data, swingCrop=None, viewGraph=True,
                minPeriod=0.1, saveData=False, saveName=None):
    '''
    This function takes a pandas dataframe of period data
    ( or csv file as a string)
    and calculates the period from the zero crossings, by event numbers.

    input: dataframe with columns=['eventNumber', 'sumSignal',
                                    'leftMinusRight', 'topMinusBotom',
                                    'xField', 'yField', 'timestamp']
    output: dataframe with columns=['eventNumber', 'avgPeriod',
                                    'xField', 'yField']

    Variables=

    sumCrop: value for which all data be ignored if sumSignal is lower than it

    swingCrop: a +/- value to stop counting when the signal dampens out, checks
                backwards, until swingCrop or (-swingCrop) is met by
                leftMinusRight, and then crops off all data after that index.
                May not work if the data wanders high or low after good crossings.

    viewGraph: allows the user to see a graph of the leftMinusRight and sumSignal
                data, and then prompts for a last index value for analysis.
                Allows for wandering data, as people tend to be better at picking
                out bad wandering signals than computers.
    '''

    # if given a csv file name, gets dataframe
    if isinstance(data, str):
        data = pd.read_csv(data)

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
                print('You will be shown a graph of the Sum and Left-Right \
                      signal. Please note the the last index that should \
                      be counted, and the minimum Sum signal that should be \
                      included. You will need to input these after the graph\
                      is shown and closed')
                input("Press Enter to show plot...")
                #CropIndex = 0
                x = selectedData.timestamp
                y = selectedData.leftMinusRight
                z = selectedData.sumSignal
                plt.figure(figsize=(15,12))
                plt.plot(x,y, 'o')
                plt.plot(x,z, 'o')
                plt.xlabel('Index')
                plt.ylabel('Sum Signal and L-R Signal')
                plt.show()
                #textplot(x,y,0,max(x))
                #textplot(x,z,0,max(x))

                try:
                    CropIndex = 1000*int(input('Please enter the end index value \
                                for analysis in thousands, \n e.g. 13 for index \
                                13,000 (0 for all): '))
                    sumCrop = float(input('Lowest sum signal to count: '))
                    repeat = False
                except:
                    pass

                if CropIndex == 0:
                    CropIndex = max(selectedData.index)+1
                    repeat = False
        else:
            CropIndex = max(selectedData.index)+1
            sumCrop = -99999

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
        tempPeriods = []
        periods = []

        for i in range(2, len(newdata.index)):
            tempPeriods.append(newdata.timestamp[i]-newdata.timestamp[i-2])

        for period in tempPeriods:
            if period > minPeriod:
                periods.append(period)

        #gets average period
        avgPeriod = np.mean(periods)
        stdPeriods = np.std(periods)
        numPeriods = len(periods)
        print(periods)

        #if first time through loop (usually eventNumber = 0), sets up return
        #database
        if first:

            d = {'eventNumber':l, 'avgPeriod':avgPeriod,
                'periodSTD': stdPeriods, 'numPeriods': numPeriods,
                'xField':newdata.xField.mean(), 'yField':newdata.yField.mean(),
                 'periods':periods}
            #periodList = pd.DataFrame(d, index=[0])
            periodList = pd.DataFrame(d)
            first=False

        #adds to set up database from above
        else:

            tempdf = pd.DataFrame({'eventNumber':l, 'avgPeriod':avgPeriod,
                                'periodSTD':stdPeriods, 'numPeriods':numPeriods,
                                'xField':newdata.xField.mean(),
                                'yField':newdata.yField.mean(),
                                   'periods':periods})
            periodList= pd.concat([periodList,tempdf], ignore_index=True)

    if saveData:
        if saveName == None:
            saveName = str(input('Please give a name for the period data to \
                                 be saved out as. No spaces in name'))
        periodList.to_csv(saveName+'.csv')


    return periodList
