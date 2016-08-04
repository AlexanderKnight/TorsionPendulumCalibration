#! /etc/bin/python3
# script to auto calibrate the magnetic torsion pendulum to get the magnetic
    #moment and torsion constant

import xyzFieldControl as xyz
import sys
sys.path.append('./PeriodCalculations/')
import period
import time
import numpy as np


handle = xyz.openPorts()
Bz = xyz.zCoil.coilField
BxRange = np.linspace(xyz.xCoil.appliedMinField, xyz.xCoil.appliedMaxField, 20)
eventNumber = 0
xyz.fine_field_cart(xyz.xCoil.appliedMaxField, 0.82*xyz.yCoil.appliedMaxField,
                    Bz, handle)
allTheData = None
try:
    for x in BxRange[::-1]:
        By = xyz.yCoil.coilField
        xyz.fine_field_cart(x, By, Bz, handle)
        xyz.beamSearch(searchAxis='y', handle = handle, minSumSignal=3.0, steps=5000)
        time.sleep(5)
        xyz.pidLoop(handle, function='dampen')
        if eventNumber == 0:
            currentRun, allTheData = xyz.kickTracking(handle=handle,
                                                    eventNumber = eventNumber)
        else:
            currentRun, allTheData = xyz.kickTracking(handle=handle,
                                                eventNumber = eventNumber,
                                                allTheData = allTheData)
        eventNumber += 1


    time.sleep(0.5)
    xyz.closePorts(handle)

    calibrationRun = xyz.package_my_data_into_a_dataframe_yay(allTheData)
    timeStamp1 = time.strftime('%y-%m-%d~%H-%M-%S')
    calibrationRun.to_csv("./data/calibration/calibration%s.csv" % timeStamp1)

    periodInfo = period.periodCalc(calibrationRun)
    periodInfo.to_csv('data/calibration/periodInfo%s.csv' % timeStamp1)


    plt.figure(figsize=(12,10))
    plt.plot((4*np.pi**2)/(periodInfo.avgPeriod)**2, periodInfo.netField, 'o')
    plt.show()

except:
    time.sleep(0.5)
    xyz.closePorts(handle)
    if allTheData != None:
        calibrationRun = xyz.package_my_data_into_a_dataframe_yay(allTheData)

        timeStamp1 = time.strftime('%y-%m-%d~%H-%M-%S')
        calibrationRun.to_csv("./data/calibration/calibration%s.csv" % timeStamp1)

        periodInfo = period.periodCalc(calibrationRun)
        periodInfo.to_csv('data/calibration/periodInfo%s.csv' % timeStamp1)
    raise
