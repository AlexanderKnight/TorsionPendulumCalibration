
import time as time

class PIDControl():
    def __init__(self, kP, kI, kD):
        self.P = kP
        self.I = kI
        self.D = kD

        # the state of the loop
        self.setpoint = 0
        self.position = 0
        self.offset = 0
        self.timestamp = 0
        # the previous state of the loop
        self.lastSetpoint = 0
        self.lastPosition = 0
        self.lastOffset = 0
        self.lastTimestamp = 0

        self.output = 0

    def runloop(self, setpoint, position):
        # update the last position etc with the old data
        self.lastSetpoint = self.setpoint
        self.lastPosition = self.position
        self.lastOffset = self.offset

        # update the gains with the passed in values.
        self.setpoint = setpoint
        self.position = position
        self.offset = setpoint - position # swap these to make the output have the correct sign

        # calculate the time step since last loop
        self.timestamp = time.time()
        dt = self.lastTimestamp - self.timestamp
        self.lastTimestamp = self.timestamp # store the timestamp for use next round

        # claculate the pid gains
        proportional = self.P * self.offset
        integral += self.I * (dt*self.offset)
        derivative = self.D * ((self.offset - self.lastOffset)/(dt))

        # calculate the output from the pid gains
        self.output = proportional + integral + derivative

        return(self.output)
