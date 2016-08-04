#! /etc/bin/python3
# script to auto calibrate the magnetic torsion pendulum to get the magnetic
    #moment and torsion constant

import xyzFieldControl as xyzFieldControl
import sys
sys.path.append('./PeriodCalculation')
import period
import time

handle = xyz.openPorts()
Bz = xyz.zCoil.coilField
BxRange = np.linspace(xyz.xCoil.appliedMinField, xyz.xCoil.appliedMaxField, 20)
eventNumber = 0
xyz.fine_field_cart(xyz.xCoil.appliedMaxField, xyz.yCoil.appliedMaxField,
                    Bz, handle)
try:
    for x in reverse(BxRange):
        By = xyz.yCoil.coilField
        xyz.fine_field_cart(x, By, Bz, handle)
        xyz.beamSearch(searchAxis='y', minSumSignal=4.95)
        xyz.pidLoop(function='dampen')
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
    calibrationRun = xyz.package_my_data_into_a_dataframe_yay(allTheData)

    timeStamp1 = time.strftime('%y-%m-%d~%H-%M-%S')
    calibrationRun.to_csv("./data/calibration/calibration%s.csv" % timeStamp1)

    periodInfo = period.periodCalc(calibrationRun)
    periodInfo.to_csv('data/calibration/periodInfo%s.csv' % timeStamp1)
