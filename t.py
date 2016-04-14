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


from tkinter import *
import time, serial, logging, logging.config

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
        #self.ser.port = "/dev/ttyUSB0"
        self.ser.port = "/dev/ttyUSB0"
        self.ser.baudrate = 2400
        self.ser.bytesize = serial.EIGHTBITS     # number of bits per bytes
        self.ser.parity = serial.PARITY_NONE     # set parity check: no parity
        self.ser.stopbits = serial.STOPBITS_ONE     # number of stop bits
        #self.ser.timeout = None                  # block read
        self.ser.timeout = 1                    # non-block read
        #self.ser.timeout = 2                      # timeout block read
        self.ser.xonxoff = False             # disable software flow control
        self.ser.rtscts = False                 # disable hardware (RTS/CTS) flow control
        self.ser.dsrdtr = False               # disable hardware (DSR/DTR) flow control
        self.ser.writeTimeout = 2             # timeout for write

        try:
            self.ser.open()
        except:
            myLogger.error("error open serial port: " + str(e))
        #    exit()


    def send(self,data):

        myLogger.debug("try write data: " + data)

        if self.ser.isOpen():
            try:
                #self.ser.flushInput()        # flush input buffer, discarding all its contents
                #self.ser.flushOutput()        # flush output buffer, aborting current output
                                            # and discard all that is in buffer
                #write data
                if(type(data) == type('String')):
                    data = bytearray(data,'ascii')
                self.ser.write(data)
                myLogger.debug("write data: " + data)
                #time.sleep(0.5)          # give the serial port sometime to receive the data
                numOfLines = 0
        #        while True:
        #                response = self.ser.readline()
        #                myLogger.debug("read data: " + response)
        #                numOfLines = numOfLines + 1
        #                if (numOfLines >= 5):
        #                    break
        #        self.ser.close()
            except:
                myLogger.error("error communicating...: ")

        else:
            myLogger.error("cannot open serial port ")

class SkoreButton(Button):

    skore = 0             # skore
    master = 0            # nadrazeny widget (hlavni okno)
    skore_text = 0        # ukazatel na Label - text skore
    bsup = 0
    bsdown = 0

    def __init__(self,r,c,master_app,skore_t,skore_h):

        self.skore=skore_h
        self.master=master_app
        self.skore_text = skore_t
        self.image_up=PhotoImage(file="up.png")
        self.image_down=PhotoImage(file="down.png")
        self.bsup = Button(root, image=self.image_up, width="20", height="10",command=self.pridej_skore)
        self.bsup.grid(row=r, column=c,sticky='NE')
        self.bsdown = Button(root, image=self.image_down, width="20", height="10",command=self.uber_skore)
        self.bsdown.grid(row=r, column=c,sticky='SE')

    def pridej_skore(self):
        self.skore = self.skore + 1
        c = '{:02d}'.format(self.skore)
        self.skore_text.config(text=c)

    def uber_skore(self):
        if self.skore > 0:
            self.skore = self.skore - 1
            c = str('{:02d}'.format(self.skore))
            self.skore_text.config(text=c)

class TrestButton(Button):

    trest = 0
    master = 0
    cass = 0
    casm = 0
    up = 0
    down = 0
    trest_text = 0

    def __init__(self,master,r,c,trest_t):

        self.master = master
        self.trest_text = trest_t
        self.image_up=PhotoImage(file="up.png")
        self.image_down=PhotoImage(file="down.png")
        self.up = Button(root, image=self.image_up, width="20", height="10",command=self.pridej_trest)
        self.up.grid(row=r, column=c,sticky='N')
        self.down = Button(root, image=self.image_down, width="20", height="10",command=self.uber_trest)
        self.down.grid(row=r, column=c,sticky='S')

    def pridej_trest(self):
        if self.master.cas_stop == 1:
            self.casm = self.casm + 2
            c = self.master.formatuj_cas(self.cass,self.casm)
            self.trest_text.config(text=c)

    def uber_trest(self):
        if self.master.cas_stop == 1:
            self.casm = self.casm - 2
            if self.casm < 0:
                self.casm = 0
            if self.cass > 0:
                self.cass = 0
            c = self.master.formatuj_cas(self.cass, self.casm)
            self.trest_text.config(text=c)


class App:

    noSerial = 1    # 1 = neni pripojen seriovy port = debug neposilej data na tablo

    cas_stop = 1
    cas = ''        # posledni cas - skutecne hodiny - pouze sekundy
    cas_hra_default = [20,0]
    cas_hra = [0,0]    

    tablo_start = 'SS000C0C0CCCCCCCCCCCCC0'    # defaultni retezec
    tablo_8 = 'SS888888888888888888880'        # test segmentu
    tablo = ''            # retezec ktery se posle na tablo
    
    sirena = 0
    zvuk = 0    # pomocna promenna dekrementuje se s kadym tickem (200ms), pokud je pustena sirena
    bsA = 0     # buton stav A
    bsB = 0     # button stav B

#    def __exit__(self, exc_type, exc_value, traceback):
#    logging.shutdown()

    def __init__(self, master,cas_hra=[0,0]):

#        if self.noSerial == 0:
        self.ser = SerialPort()

        self.tablo = self.tablo_start
        self.cas_hra = cas_hra        # cas v sekundach od zacatku hry
        self.cas_stop = 1        # 1=hodiny stoji

        self.button = Button(root, text="START", fg="red", command=self.zastav_hodiny)
        self.button.grid(row=10, column=5)

        self.e_skoreA = Label(root,font=('arial',50, 'bold'),text="00",bg='white')
        self.e_skoreA.grid(row=4,column=2, sticky='W')

        # tlacitko pridani skore tym A ButtonStavAup
        self.bsA = SkoreButton(4,1,self,self.e_skoreA,0)

        self.e_skoreB = Label(root,font=('arial',50, 'bold'),text="00",bg='white')
        self.e_skoreB.grid(row=4,column=7, sticky='W')
        # tlacitko pridani skore tym B ButtonStavAup
        self.bsB = SkoreButton(4,6,self,self.e_skoreB,0)

        self.clock = Label(root, font=('arial',40, 'bold'), bg='green')
        self.clock.grid(row=6,column=5)

        self.trestA1 = Label(root, font=('times', 20, 'bold'), bg='green')
        self.trestA1.grid(row=8,column=2)
        self.btA1 = TrestButton(self,8,1,self.trestA1)
        self.trestA2 = Label(root, font=('times', 20, 'bold'), bg='green')
        self.trestA2.grid(row=9,column=2)
        self.btA2 = TrestButton(self,9, 1,self.trestA2)
        #self.trestA2.pack(fill=BOTH, expand=1)
        self.trestB1 = Label(root, font=('times', 20, 'bold'), bg='green')
        self.trestB1.grid(row=8,column=7)
        self.btB1 = TrestButton(self,8, 6,self.trestB1)
        #self.trestB1.pack(fill=BOTH, expand=1)
        self.trestB2 = Label(root, font=('times', 20, 'bold'), bg='green')
        self.trestB2.grid(row=9,column=7)
        self.btB2 = TrestButton(self,9, 6,self.trestB2)
        #self.trestB2.pack(fill=BOTH, expand=1)

        self.trestA1.config(text=self.formatuj_cas(self.btA1.cass,self.btA1.casm))
        self.trestA2.config(text=self.formatuj_cas(self.btA2.cass,self.btA2.casm))
        self.trestB1.config(text=self.formatuj_cas(self.btB1.cass,self.btB1.casm))
        self.trestB2.config(text=self.formatuj_cas(self.btB2.cass,self.btB2.casm))
    
        self.clock.config(text=self.formatuj_cas(self.cas_hra[0],self.cas_hra[1]))


    # vrati cas ve tvaru string MM:SS
    def formatuj_cas(self,s,m):
        c = '{:02d}'.format(m)+':'+'{:02d}'.format(s)
        return c

    # vrati cas ve tvaru string S1S@M!M@ pro zaslani na tablo
    def formatuj_cas_tablo(self,s,m):
        cm = '{:02d}'.format(m)
        cs = '{:02d}'.format(s)
        c = cs[1]+cs[0]+cm[1]+cm[0]
        return c

    def formatuj_trest_tablo(self,s,m):
        cm = format(m)
        cs = '{:02d}'.format(s)
        c = cs[1]+cs[0]+cm[0]
        return c


    def formatuj_stav_tablo(self):
        d = '{:02d}'.format(self.bsA.skore)
        h = '{:02d}'.format(self.bsB.skore)
        return d[1]+d[0]+h[1]+h[0]

    # dekrementuje cas trestu, inkrementuje cas hry
    def uprav_cas(self,curcas):
        myLogger.debug('Upava casu : cas '+curcas) 
        self.cas = curcas
        if self.cas_hra[0] == 59:
            self.cas_hra[0] = 0
            if self.cas_hra[1] == 99:
                self.cas_hra[1] = 0
            else:
                self.cas_hra[1] = self.cas_hra[1] + 1

        else:
            self.cas_hra[0] = self.cas_hra[0] + 1

        if self.btA1.cass + self.btA1.casm > 0:
            if self.btA1.cass > 0:
                self.btA1.cass = self.btA1.cass - 1
            else:
                self.btA1.cass = 59
                if self.btA1.casm > 0:
                    self.btA1.casm = self.btA1.casm - 1

        if self.btA2.cass + self.btA2.casm > 0:
            if self.btA2.cass > 0:
                self.btA2.cass = self.btA2.cass - 1
            else:
                self.btA2.cass = 59
                if self.btA2.casm > 0:
                    self.btA2.casm = self.btA2.casm - 1

        if self.btB1.cass + self.btB1.casm > 0:
            if self.btB1.cass > 0:
                self.btB1.cass = self.btB1.cass - 1
            else:
                self.btB1.cass = 59
                if self.btB1.casm > 0:
                    self.btB1.casm = self.btB1.casm - 1

        if self.btB2.cass + self.btB2.casm > 0:
            if self.btB2.cass > 0:
                self.btB2.cass = self.btB2.cass - 1
            else:
                self.btB2.cass = 59
                if self.btB2.casm > 0:
                    self.btB2.casm = self.btB2.casm - 1
        if self.sirena == 1:
            if self.zvuk == 0:
                 self.sirena = 0

        if self.zvuk > 0:
            self.zvuk = self.zvuk - 1        

        if self.cas_hra[0] == 10:
            if self.sirena == 0:
                self.zvuk = 5
                self.sirena = 1


    # posle data na tablo
    def send_s(self):
        pass


    def tick(self):
        # get the current local time from the PC
        time2 = time.strftime('%S')
        if self.cas_stop != 1:
                # if time string has changed, update it
                if time2 != self.cas:
                    self.uprav_cas(time2)    # snizi cas o 1 sekundu
                    time4 = self.formatuj_cas(self.cas_hra[0],self.cas_hra[1])
                    self.clock.config(text=time4)

                    self.trestA1.config(text=self.formatuj_cas(self.btA1.cass,self.btA1.casm))
                    self.trestA2.config(text=self.formatuj_cas(self.btA2.cass,self.btA2.casm))
                    self.trestB1.config(text=self.formatuj_cas(self.btB1.cass,self.btB1.casm))
                    self.trestB2.config(text=self.formatuj_cas(self.btB2.cass,self.btB2.casm))

        tout = 'SS' + self.formatuj_cas_tablo(self.cas_hra[0],self.cas_hra[1]) + self.formatuj_stav_tablo() + \
                self.formatuj_trest_tablo(self.btA1.cass,self.btA1.casm) + \
                self.formatuj_trest_tablo(self.btA2.cass, self.btA2.casm) +\
                self.formatuj_trest_tablo(self.btB1.cass,self.btB1.casm) + \
                self.formatuj_trest_tablo(self.btB2.cass, self.btB2.casm) + str(self.sirena)
        self.tablo = tout
        myLogger.debug('data na tablo : ' + self.tablo)
        if self.noSerial == 0: 
                self.ser.send(self.tablo)

        # calls itself every 200 milliseconds
        # to update the time display as needed
        # could use >200 ms, but display gets jerky
        self.clock.after(200, self.tick)


    def zastav_hodiny(self):
        # rozbehnuti/
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
    myLogger = logging.getLogger('root')
    myLogger.info('Start aplikace TABLO')
    app = App(root)
    app.tick()
    root.mainloop()
    logging.shutdown()

