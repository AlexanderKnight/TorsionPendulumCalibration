



import xyzFieldControl as xyz


# open the all ports and get the labjack handle
handle = xyz.openPorts()

try:
    # all labjack code in this try/except you could put all your code here!
    while True:
        print("hi")
except KeyboardInterrupt: # usefull to have a KeyboardInterrupt when your're debugging
    xyz.closePorts(handle)
except Exception as e:
	# helpful to close the ports on except when debugging the code.
    # it prevents the devices from thinking they are still conected and refusing the new connecton
    # on the next open ports call.
	xyz.closePorts(handle)
	print('closed all the ports\n')
	print(e) # print the exception
    raise

xyz.closePorts(handle)
print('closed all the ports\n')
