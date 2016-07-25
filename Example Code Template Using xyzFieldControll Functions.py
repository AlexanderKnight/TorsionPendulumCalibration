



import xyzFieldControl as xyz


# open the all ports and get the labjack handle
handle = xyz.openPorts()

try:
    # run your code here!
    while True:
        print("hi")


except KeyboardInterrupt:
	print('\n')
	xyz.closePorts(handle)
	print('closed all the ports')

except Exception as e:
	# helpful to close the ports on except when debugging the code.
    # it prevents the devices from thinking they are still conected and refusing the new connecton
    # on the next open ports call.
	xyz.closePorts(handle)
	print('closed all the ports')
	print(e) # print the exception
