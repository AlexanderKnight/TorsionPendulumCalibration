# import all the files that have data containers
import sys
sys.path.append("./../PowerSupplyControl/")
sys.path.append("./../CoilControl/")
import powersupply
import coil


def pid(kp, ki, kd, duration):
