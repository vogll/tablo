# -*- coding: utf-8 -*-
#
#SS32017C138047036015010
#
# obracene poradi znaku
# C = clear - nezobrazi nic
#SS SSMMHHDDHH111222333444S
#
#SS sekundy v obracenem poradi
#MM minuty v obracenem poradi.
#111 trest levy horni (domaci) MSS prvni znak na displeji neni
#222 trest pravy horni (hoste) MSS
#333 trest levy dolni (domaci) MSS
#444 trest pravy dolni (hoste) MSS
#S sirena  0 = stop 1 = start


from Tkinter import *
import time, serial, logging.config

# tlacitko skore
# ma dva Buttony (up, down)
# je svazano s master aplikaci

class SerialPort():

    ser = 0

    def __init__(self):

	#initialization and open the port
        #possible timeout values:
	#    1. None: wait forever, block call
	#    2. 0: non-blocking mode, return immediately
	#    3. x, x is bigger than 0, float allowed, timeout block call

	self.ser = serial.Serial()
#	self.ser.port = "/dev/ttyUSB0"
	self.ser.port = "/dev/ttyUSB0"
	self.ser.baudrate = 2400
	self.ser.bytesize = serial.EIGHTBITS 	# number of bits per bytes
	self.ser.parity = serial.PARITY_NONE 	# set parity check: no parity
	self.ser.stopbits = serial.STOPBITS_ONE 	# number of stop bits
	#self.ser.timeout = None          		# block read
	self.ser.timeout = 1            		# non-block read
	#self.ser.timeout = 2              		# timeout block read
	self.ser.xonxoff = False     		# disable software flow control
	self.ser.rtscts = False     			# disable hardware (RTS/CTS) flow control
	self.ser.dsrdtr = False       		# disable hardware (DSR/DTR) flow control
	self.ser.writeTimeout = 2     		# timeout for write

	try: 
	    self.ser.open()
	except Exception, e:
	    myLogger.error("error open serial port: " + str(e))
	    exit()


    def send(self,data):

	if self.ser.isOpen():
	    try:
		self.ser.flushInput()		# flush input buffer, discarding all its contents
		self.ser.flushOutput()		# flush output buffer, aborting current output 
                				# and discard all that is in buffer
		#write data
		self.ser.write(data)
		myLogger.debug("write data: " + data)
		time.sleep(0.5)  		# give the serial port sometime to receive the data
		numOfLines = 0
#		while True:
#    		    response = self.ser.readline()
#    		    myLogger.debug("read data: " + response)
#    		    numOfLines = numOfLines + 1
#    		    if (numOfLines >= 5):
#        	        break
#		self.ser.close()
	    except Exception, e1:
		myLogger.error("error communicating...: " + str(e1))

	else:
	    myLogger.error("cannot open serial port ")


class SkoreButton(Button):

    skore = 0			# stav ukazatel na promennou stav v master
    master = 0			# nadrazeny widget (hlavni okno)
    skore_text = 0		# ukazatel na Label - text skore

    def __init__(self,r,c,master_app,skore_t,skore_h):

	self.skore=skore_h
	self.master=master_app
	self.skore_text = skore_t
	self.image_up=PhotoImage(file="up.png")
	self.image_down=PhotoImage(file="down.png")
	self.master.bsAup = Button(root, image=self.image_up, width="20", height="10",command=self.pridej_skore)
	self.master.bsAup.grid(row=r, column=c,sticky='N')
	self.master.bsAup = Button(root, image=self.image_down, width="20", height="10",command=self.uber_skore)
	self.master.bsAup.grid(row=r, column=c,sticky='S')

    def pridej_skore(self):
	self.skore = self.skore + 1
	c = '{:02d}'.format(self.skore)
	self.skore_text.config(text=c)

    def uber_skore(self):
	if self.skore > 0:
		self.skore = self.skore - 1 	
		c = str('{:02d}'.format(self.skore))
		self.skore_text.config(text=c)


class App:

    skoreA = 0
    skoreB = 0

    cas = ''		# posledni cas - skutecne hodiny - pouze sekundy

#    def __exit__(self, exc_type, exc_value, traceback):
#	logging.shutdown()

    def __init__(self, master,cas_hra=[0,0]):

#	myLogger.info(msg)
#	myLogger.warn(msg)
#	myLogger.error(msg)
#	myLogger.critical(msg)

	self.ser = SerialPort()

	self.cas_hra = cas_hra		# cas v sekundach od zacatku hry
	self.cas_stop = 1		# 1=hodiny stoji

	self.trest = [10,0,0,1,0,0,0,2] # s,m s,m s,m s,m

        self.button = Button(root, text="START", fg="red", command=self.zastav_hodiny)
        self.button.grid(row=10, column=4)
	
	self.e_skoreA = Label(root,font=('arial',30, 'bold'),text="00",bg='white')
	self.e_skoreA.grid(row=4,column=2)
	# tlacitko pridani skore tym A ButtonStavAup
        self.bsAup = SkoreButton(4,1,self,self.e_skoreA,self.skoreA)

	self.e_skoreB = Label(root,font=('arial',30, 'bold'),text="00",bg='white')
	self.e_skoreB.grid(row=4,column=6)
	# tlacitko pridani skore tym B ButtonStavAup
        self.bsBup = SkoreButton(4,5,self,self.e_skoreB,self.skoreB)


#	self.e_skoreB = Entry(root,font=('arial',30, 'bold'),textvariable=self.skoreB,width="2",justify="center")
#	self.e_skoreB.grid(row=4,column=6)
	
	self.clock = Label(root, font=('arial',30, 'bold'), bg='green')
	self.clock.grid(row=6,column=4)

	self.trestA1 = Label(root, font=('times', 20, 'bold'), bg='green')
	self.trestA1.grid(row=8,column=2)
	self.trestA2 = Label(root, font=('times', 20, 'bold'), bg='green')
	self.trestA2.grid(row=9,column=2)
	#self.trestA2.pack(fill=BOTH, expand=1)
	self.trestB1 = Label(root, font=('times', 20, 'bold'), bg='green')
	self.trestB1.grid(row=8,column=5)
	#self.trestB1.pack(fill=BOTH, expand=1)
	self.trestB2 = Label(root, font=('times', 20, 'bold'), bg='green')
	self.trestB2.grid(row=9,column=5)
	#self.trestB2.pack(fill=BOTH, expand=1)

	self.trestA1.config(text=self.formatuj_cas(self.trest[0],self.trest[1]))
	self.trestA2.config(text=self.formatuj_cas(self.trest[2],self.trest[3]))
	self.trestB1.config(text=self.formatuj_cas(self.trest[4],self.trest[5]))
	self.trestB2.config(text=self.formatuj_cas(self.trest[6],self.trest[7]))
	
    	self.clock.config(text=self.formatuj_cas(self.cas_hra[0],self.cas_hra[1]))


    def formatuj_cas(self,s,m):
	c = '{:02d}'.format(m)+':'+'{:02d}'.format(s)
	return c

    def formatuj_cas_tablo(self,s,m):
	cm = '{:02d}'.format(m)
	cs = '{:02d}'.format(s)
	c = cs[1]+cs[0]+cm[1]+cm[0]
	return c


    # posle data na tablo
    def send_s(self):
	pass


    def tick(self):

        # get the current local time from the PC
        time2 = time.strftime('%S')
	
        # if time string has changed, update it
	if self.cas_stop != 1:
    	    if time2 != self.cas:
        	self.cas = time2
		if self.cas_hra[0] == 59:
			self.cas_hra[0] = 0
			if self.cas_hra[1] == 99:
			    self.cas_hra[1] = 0
			else:
			    self.cas_hra[1] = self.cas_hra[1] + 1
			
		else:
			self.cas_hra[0] = self.cas_hra[0] + 1
		time4 = self.formatuj_cas(self.cas_hra[0],self.cas_hra[1])
		self.clock.config(text=time4)
		i = 7
		while i > 0:
			if (self.trest[i]+self.trest[i-1])>0:
				if self.trest[i-1] > 0:
					self.trest[i-1] = self.trest[i-1] - 1
				else:
					self.trest[i-1] = 59
				if self.trest[i] > 0:
					self.trest[i] = self.trest[i] - 1
			i = i - 2  

    		self.trestA1.config(text=self.formatuj_cas(self.trest[0],self.trest[1]))
    		self.trestA2.config(text=self.formatuj_cas(self.trest[2],self.trest[3]))
    		self.trestB1.config(text=self.formatuj_cas(self.trest[4],self.trest[5]))
    		self.trestB2.config(text=self.formatuj_cas(self.trest[6],self.trest[7]))
#SS32017C138047036015010
#
# obracene poradi znaku
# C = clear - nezobrazi nic
#SS SSMMHHDDHH111222333444S
#
#SS sekundy v obracenem poradi
#MM minuty v obracenem poradi.
#111 trest levy horni (domaci) MSS prvni znak na displeji neni
#222 trest pravy horni (hoste) MSS
#333 trest levy dolni (domaci) MSS
#444 trest pravy dolni (hoste) MSS
#S sirena  0 = stop 1 = start
		cas = self.formatuj_cas_tablo(self.cas_hra[0],self.cas_hra[1])
		stavA = '0C'
		stavB = '0C'
		trestA1 = '000'
		trestA2 = '000'
		trestB1 = '000'
		trestB2 = '000'

		s = 'SS'+ cas + stavA + stavB + trestA1 + trestB1 + trestA2 + trestB2 + '0' 
		myLogger.debug('cas '+ s)
		self.ser.send(s)


	# posle aktualni stav na TABLO
	

        # calls itself every 200 milliseconds
        # to update the time display as needed
        # could use >200 ms, but display gets jerky
        self.clock.after(200, self.tick)

    def zastav_hodiny(self):
	# rozbehnuti
	if self.cas_stop != 0:
	    self.cas_stop = 0
    	    self.button.config(text="STOP")
	    # musim pockat na celou vterinu, jinak prvni vterina bude kratsi
    	    t = time.strftime('%S')
	    while t == time.strftime('%S'):
		pass
	# zastaveni
	else:
    	    self.cas_stop = 1
    	    self.button.config(text="START")
    

if __name__=="__main__":

    root = Tk()
    logging.config.fileConfig('log.ini')
    myLogger = logging.getLogger()
    myLogger.info('Start aplikace TABLO')
    app = App(root)
    app.tick()
    root.mainloop()
    logging.shutdown()

