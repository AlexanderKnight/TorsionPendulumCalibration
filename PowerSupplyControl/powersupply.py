import time
import serial
import re

class PowerSupply():

    def __init__(self, portAddress):
        
        self.portAddress = portAddress # the string that tells the self.serial library to open the correct port
        self.portOpen = False
        

    def openPort(self):
    
        # open the self.serial port with the settings for the bk-supplies
        self.ser = serial.Serial(port= self.portAddress,
                                 baudrate= 9600,
                                 parity= serial.PARITY_NONE,
                                 stopbits= serial.STOPBITS_ONE,
                                 bytesize= serial.EIGHTBITS)
        
        self.ser.isOpen()
        self.portOpen = True
        return

    def closePort(self):

        self.ser.close()
        self.portOpen = False
        return
        
    def writeToPort(self, bytearrayCommandToWrite):
        # first write the command to the port 
        self.ser.write(bytearrayCommandToWrite + b'\r') # add the return char to the command bytearray
        
        # now wait for the powersupply to respond
        time.sleep(0.05) #time.sleep(.05) # make this longer if you're getting errors
        
        # read the return message 
        out = bytearray() # empty bytearray to fill from the input buffer
        
        while self.ser.inWaiting() > 0: # while we have bytes wating in the buffer to read
            # detect the stop bit from the powersupply which happens to be: '\x11'. The start bit is: '\x13'.
            bufferByte = self.ser.read() # pull a byte off the input buffer
            # messages always start with '\x13' so we can wait for that char and parse out the message
            if bufferByte == (b'\x13'): # if we are at the begining of a message, 
                bufferByte = self.ser.read() # read past the start bit
                while bufferByte != (b'\x11') and bufferByte != (b'\r'): # while we are inside the message
                    out += bufferByte
                    bufferByte = self.ser.read() # read the next byte
                self.ser.reset_input_buffer() # clean out the input buffer after reading the message
        
        # check to see if we have any bytes in the byte array
        # if we don't, then that means that we just set the current and the powersupply is 
        # just telling us that it's finished setting the current with the return bytes
        if len(out) == 0:
            return(out)
        
        out = out.decode("utf-8") # switch from type bytearray to string
        
        # now we want to format the output to be a float if we have a number.
        temp = re.search(r'\d+\.\d', out) # look for a number in out
        if bool(temp): # if we find a numbers in the string, 
            out = float(temp.group()) # put them together and cast them as a float.
            return(out) # returns a float (current value or voltage value)
        else: 
            return(out) # returns a string (error message or text reply to command)
        
    def parseErrorMessages(self, message):
        '''
        Check the input message for any of the predefined error messages from the powersupply 
        and raise an exception if an error is found.
        '''
        if message == 'Syntax Error':
            #print('Syntax Error. Command not a number or value too high for the power supply')
            raise Exception('Syntax Error. Command not a number or value too high for the power supply')
        elif message == 'Out Of Range':
            #print('Input number out of range! (Likly too small. Minimum is 0.01V or 0.1mA)')
            raise Exception('Input number out of range! (Likly too small. Minimum is 0.01V or 0.1mA)')
        else:
            #print('strange message receved: %s' % message)
            raise Exception('strange message receved: %s' % message)
            
    def checkMode(self):
        '''
        Test to see if the supply is in constant current mode or constant voltage mode
        returns a string 'CV' if constant voltage and 'CC' if the mode is constant current. 
        '''
        out = self.writeToPort(bytearray('STAT?', 'utf-8'))
        if out == 'CV' or out == 'CC': # if we get expected values for the mode
            return out # return them!
        else:
            self.parseErrorMessages(out) # check the errors 
            raise Exception('enable the exceptions in the parseErrorMessages functon!')

    def voltage(self, setVoltage = 'None'):
        '''
        If no arguments are passed, this function queries the voltage and returns it.
        otherwise it will try to set the voltage of the powersupply and return a None type. 
        '''
        
        #if(self.checkMode() != 'CV'): # check the mode of the powersupply
        #     raise Exception('Incorrect mode! Supply is in constant current mode.')

        initialPortOpen = self.portOpen # handles the port state so we can leave it open if it is already open.
        if initialPortOpen == False: # if the port is closed,
            self.openPort()        # open it!

        if setVoltage != 'None': # if we pass a value other than none, try to set the voltage
            voltage=str('%05.2f' % setVoltage) # formats the voltage to have 5 chars and 2 digits before and after the decimal
            out = self.writeToPort(bytearray('VOLT ' + voltage, 'utf-8')) #format and write to the port
            if len(out) != 0: # if we get anything back
                self.parseErrorMessages(out) # analize errors
                raise Exception('enable the exceptions in the parseErrorMessages functon!')
                
        else: # querry the voltage from the powersupply.
            out = self.writeToPort(bytearray('VOLT?', 'utf-8')) # write command to query current powersupply voltage
            if type(out) != float: # did we get a number?
                elf.parseErrorMessages(out) # analize errors
                raise Exception('enable the exceptions in the parseErrorMessages functon!')
                
        if initialPortOpen == False and self.portOpen == True: # leave the port how we found it. 
            self.closePort() # if it was open before the call, keep it open. Else close it.
            
        # return the voltage (None if setting, float in volts if getting)
        return(out)
        
    def current(self, setCurrent = 'None'):
        '''
        If no arguments are passed this function queries the current and returns it.
        otherwise it will try to set the current of the powersupply and return a None type.
        This is very similar to the voltage() function but has slightly differet formatting. 
        
        The current is set in milliamps with one digit of precision after the decimal
        (minimum precision = 0.1 mA). 
        
        The returned current float is also in milliamps.
        '''
        
        #if(self.checkMode() != 'CC'): # make sure the supply is in constant current mode. 
        #    raise Exception('Incorrect mode! Supply is in constant voltage mode.')

        initialPortState = self.portOpen # handles the port state so we can leave it open if it is open 
        if initialPortState == False:
            self.openPort()
        
        if setCurrent != 'None': # if we pass a value other than none, try to set the current    
            current=str('%05.1f' % setCurrent) # sets the setCurrent to have 5 chars and 3 digits before and 1 digit after the decimal
            out = self.writeToPort(bytearray('CURR ' + current, 'utf-8')) #format and write to the port
            if len(out) != 0: # if we get anything back
                self.parseErrorMessages(out) # analize errors
                raise Exception('enable the exceptions in the parseErrorMessages functon!')
            
        else: # get the current current from the powersupply
            out = self.writeToPort(bytearray('CURR?', 'utf-8'))
            if type(out) != float:
                elf.parseErrorMessages(out) # analize errors
                raise Exception('enable the exceptions in the parseErrorMessages functon!')
            
        if initialPortState == False and self.portOpen == True:
            self.closePort()
            
        # return the current (type is None if setting the current and float in milliamps if getting the voltage)
        return(out)
        
