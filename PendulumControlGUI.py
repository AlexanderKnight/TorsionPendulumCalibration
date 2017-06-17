import tkinter as tk
import xyzFieldControl as xyz

class Application(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self,master)
        self.grid()
        self.createWidgets()

    def createWidgets(self):
        #Creates magnetic field axis for the x,y, and z axes
        self.XAxisLabel = tk.Label(self, text='X-Axis')
        self.XAxisLabel.grid(row=0)
        self.XAxisValue = tk.DoubleVar()
        self.XAxisValue.set(10.0)
        self.XAxisValueEntry = tk.Entry(self, bd=5, textvariable=self.XAxisValue)
        self.XAxisValueEntry.grid(row=0, column=1)
        self.xValue = self.XAxisValue.get()

        #Sets up y axis entry field
        self.yAxisLabel = tk.Label(self, text='Y-Axis')
        self.yAxisLabel.grid(row=1)
        self.yAxisValue = tk.DoubleVar()
        self.yAxisValue.set(10.0)
        self.yAxisValueEntry = tk.Entry(self, bd=5, textvariable=self.yAxisValue)
        self.yAxisValueEntry.grid(row=1, column=1)
        self.yValue = self.yAxisValue.get()

        #Sets up z axis entry field
        self.zAxisLabel = tk.Label(self, text='Z-Axis')
        self.zAxisLabel.grid(row=2)
        self.zAxisValue = tk.DoubleVar()
        self.zAxisValue.set(10.0)
        self.zAxisValueEntry = tk.Entry(self, bd=5, textvariable=self.zAxisValue)
        self.zAxisValueEntry.grid(row=2, column=1)
        self.zValue = self.zAxisValue.get()

        #Sets up button to take values from axis fields to be magnetic values
        self.setField = tk.Button(self, command=self.SetBField)
        self.setField['text']='Set Magnetic Field'
        self.setField.grid(row=0,column=2)

        #Sets up button to take values from axis fields to be current values
        self.setCurrent = tk.Button(self, command=self.SetCurrent)
        self.setCurrent['text']='Set Current'
        self.setCurrent.grid(row=1,column=2)


        #Sets up quit button
        self.QUIT = tk.Button(self,text='QUIT', fg='red', command=root.destroy)
        self.QUIT.grid(row=99,column=1)

        # open the powersupplies and the labjack and save the handle
        try:
            self.handle = xyz.openPorts()
        except Exception as e:
            raise e

    #sets power supplies to generate field
    def SetBField(self):
        try:
            xyz.fine_field_cart(self.xValue, self.yValue, self.zValue, self.handle)
            print("Magnetic Field Set")
        except Error as err:
            xyz.closePorts(self.handle) # close the ports before raising the error.
            raise err
        #try:
        #    self.xValue = self.XAxisValue.get()
        #    print(self.xValue)
        #except:
        #    print("Not a number")


    def SetCurrent(self):
        pass


root=tk.Tk()
root.wm_title('Magnetic Torsion Pendulum Control')
app = Application(master=root)
app.mainloop()
