import serial
from tkinter import *
import tkinter as tk
from tkinter import ttk
import time
from tkinter import messagebox
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
from matplotlib import rc
from IPython.display import HTML
import heartpy as hp

flag = 0
#Application Start
while 1:
    d = []
    flag = 0
    window = Tk()

    window.title("Heart Monitor app")

    window.geometry('500x300')

    ser = serial.Serial()

    labelTop = Label(window , text = "Choose your Com Number: ")
    labelTop.grid(column=0, row=0)

    # Connect and configure Serial after getting COM Port from the combobox 
    def callbackFunc(event):
        global flag
        ser.port = comboExample.get()
        ser.bytesize = serial.EIGHTBITS
        ser.timeout = 1
        ser.parity = serial.PARITY_NONE
        ser.open()
        flag = flag +1
        comboExample.config(state= "disabled")
        print(ser.port)

    comboExample = ttk.Combobox(window, values=["COM5", "COM12", "COM13"])
    comboExample.grid(column=1, row=0)

    comboExample.bind("<<ComboboxSelected>>", callbackFunc)

    labelTop2 = Label(window , text = "Choose your Baudrate: ")
    labelTop2.grid(column=0, row=1)

    # Set Baudrate after getting it from the combobox 
    def callbackFunc2(event):
        global flag
        ser.baudrate = int(combo2.get())
        flag = flag + 1
        combo2.config(state= "disabled")
        print(ser.baudrate)

    combo2 = ttk.Combobox(window, values=["9600", "57600", "115200"])
    combo2.grid(column=1, row=1)

    combo2.bind("<<ComboboxSelected>>", callbackFunc2)
    print(ser.is_open)

    lbl = Label(window, text="Sampling Rate: ")
    lbl.grid(column=0, row=2)

    txt = Entry(window,width=10)
    txt.grid(column=1, row=2)

    #Acquire Sampling rate and transmit it over the serial port with validation that the serial is up and running
    def clicked():
        global flag
        name = txt.get()
        if int(name) < 1000:
            name = 'r0' + name
        else:
            name = 'r' + name
        if flag == 0:
            messagebox.showinfo('Error', 'Please Select a COM Port')
        elif flag == 1:
            messagebox.showinfo('Error', 'Please Select a Baudrate')
        else:
            flag =flag +1
            print(name)
            txt.config(state='disabled')
            ser.write(bytes(name,'utf-8'))

    btn = Button(window, text="Set", command=clicked)
    btn.grid(column=2, row=2)

    #Transmit the start signal after making sure that the Serial attributes and the sampling are configures
    def clicked1():
        global flag
        if flag == 0:
            messagebox.showinfo('Error', 'Please Select a COM Port')
        elif flag == 1:
            messagebox.showinfo('Error', 'Please Select a Baudrate')
        elif flag == 2:
            messagebox.showinfo('Error', 'Please Select a Sampling Rate')
        else:
            ser.write(b's5555')
            window.destroy()

    btn = Button(window, text="Start", command=clicked1)
    btn.grid(column=1, row=3)

    window.mainloop()

    #Start of plotting using Animation
    def init(): 
        line.set_ydata([])
        return line,

    def animate(i, ys):
        # Read ADC Transmitted Values
        out = ser.readline().decode("ascii")
        if out != '':
            out1 = int(out)
            d.append(out1)
        else:
            out1=0    
        # Add y to list
        ys.append(out1)
        # Limit y list to set number of items
        ys = ys[-x_len:]

        # Update line with new Y values
        line.set_ydata(ys)

        return line,

    x_len = 301         # Number of points to display
    y_range = [0, 6000]  # Range of possible Y values to display
    fig = plt.figure()

    ax = fig.add_subplot(1, 1, 1)
    xs = list([0 + (x * (2/300)) for x in range(0, 301)])
    ys = [0] * x_len
    ax.set_ylim(y_range)

    print(ser.is_open)
    # Create a blank line. We will update the line in animate
    line, = ax.plot(xs, ys)

    #Add labels
    plt.title('Heart Beat')
    plt.xlabel('Seconds')
    plt.ylabel('Value')

    animation.FuncAnimation(fig,
        animate,
        init_func=init,
        frames=9002,
        fargs=(ys,),
        interval=6.6667,
        blit=True)
    plt.show()
    ser.close()
    #End of Plotting Using Animation

    #Start of displaying the Heart Rate in bpm
    window1 = Tk()

    window1.title("Heart Monitor app")

    window1.geometry('350x200')

    lbl = Label(window1, text="Show Heart Rate (bpm) ? ")

    lbl.grid(column=0, row=0)

    configfile = Text(window1, wrap=WORD, width=25, height= 5)

    configfile.grid(column= 0, row = 1)

    #Acquire heart rate data using Heartpy and display it
    def clicked1():
        wd, m = hp.process(np.array(d), 150)

        for measure in m.keys():
            #configfile.insert(END, (measure, m[measure]))
            print('%s: %f' %(measure, m[measure]))
        configfile.insert(END, m['bpm'])
        #for measure in m.keys():
            #configfile.insert(END, (measure, m[measure]))
            #print('%s: %f' %(measure, m[measure]))
        

    btn = Button(window1, text="Yes", command=clicked1)

    btn.grid(column=1, row=0)


    #Closes the window
    def clicked2():
        window1.destroy()

    btn1 = Button(window1, text="No", command=clicked2)

    btn1.grid(column=2, row=0)

    window1.mainloop()
