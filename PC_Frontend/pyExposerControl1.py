from Tkinter import *
from tkFileDialog import *
from subprocess import call
from PIL import Image
from PIL import ImageTk
from PIL import ImageFilter
import ImageOps
import serial

WORK_X_SIZE = 2400
WORK_Y_SIZE = 3780

class PcbData:
	def init_widgets(self, parent):				
		i = 0
		label = Label(parent, text = 'rotation')
		label.grid(row=i, column = 0, sticky=W)
		self.rotationSpinbox = Spinbox(parent, value = range(0, 360, 90))
		self.rotationSpinbox.grid(row=i, column = 1, sticky=W)
		i += 1;
		
		label = Label(parent, text = 'upper margin (mm)')
		label.grid(row=i, column = 0, sticky=W)
		self.upperMarginEntry = Entry(parent)
		self.upperMarginEntry.insert(0, '0')
		self.upperMarginEntry.grid(row=i, column = 1, sticky=W)
		i += 1;
		
		label = Label(parent, text = 'right margin (mm)')
		label.grid(row=i, column = 0, sticky=W)
		self.rightMarginEntry = Entry(parent)
		self.rightMarginEntry.insert(0, '0')
		self.rightMarginEntry.grid(row=i, column = 1, sticky=W)
		i += 1;
		
		label = Label(parent, text = 'x copys')
		label.grid(row=i, column = 0, sticky=W)
		self.xCopysSpinbox = Spinbox(parent, value = range(1, 20))
		self.xCopysSpinbox.grid(row=i, column = 1, sticky=W)
		i += 1;
		
		label = Label(parent, text = 'y copys')
		label.grid(row=i, column = 0, sticky=W)
		self.yCopysSpinbox = Spinbox(parent, value = range(1, 20))
		self.yCopysSpinbox.grid(row=i, column = 1, sticky=W)
		i += 1;
		
		label = Label(parent, text = 'x spacing(mm)')
		label.grid(row=i, column = 0, sticky=W)
		self.xSpacingEntry = Entry(parent)
		self.xSpacingEntry.insert(0, '0')
		self.xSpacingEntry.grid(row=i, column = 1, sticky=W)
		i += 1;
		
		label = Label(parent, text = 'y spacing(mm)')
		label.grid(row=i, column = 0, sticky=W)
		self.ySpacingEntry = Entry(parent)
		self.ySpacingEntry.insert(0, '0')
		self.ySpacingEntry.grid(row=i, column = 1, sticky=W)
		i += 1;
		
		
		
		button = Button(parent, text = 'Apply', command = self.generateGrid)
		button.grid(row=i, column = 1)
		i += 1;
		
		
	def  __init__(self, parent, updateThumbnailCallback, updateSizeCallback):
		self.updateThumbnailCallback = updateThumbnailCallback
		self.updateSizeCallback = updateSizeCallback
		self.pcbImage = Image.new('L', (1,1))
		self.init_widgets(parent)
		self.generateGrid()
		
	def generateThumbnail(self):
		size = self.workImage.size
		self.thumb = self.workImage.resize((size[0]/4, size[1]/4))
		#self.thumb = self.workImage.crop((size[0]/2, 0, size[0], size[1]))
		self.thumb = self.thumb.convert('RGB')
		
		photo = ImageTk.PhotoImage(self.thumb)
		self.updateThumbnailCallback(photo)
	
	def thickenLines(self, image):
		#timage = Image.new('L', (image.size[0], image.size[1]), "white")
		
		#timage = image.filter(ImageFilter.Kernel((5,5), (1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1)))
		#timage = image.filter(ImageFilter.BLUR)
		timage = image.filter(ImageFilter.MinFilter(3))
		
		#timage = timage.point(lambda x: 0 if x<180 else 255, '1')
		#timage = image
		
#		y_thicken = 2;
#		x_thicken = 2;
#		print image.size[0]
#		print image.size[1]
#		for y in range(y_thicken, image.size[1] - y_thicken - 1, 1):
#			for x in range(x_thicken, image.size[0] - x_thicken - 1, 1):
#				value = 1;
#				for yy in range(-y_thicken, y_thicken + 1, 1):
#					for xx in range(-x_thicken, x_thicken + 1, 1):
#						if image.getpixel((x+xx, y+yy)) == 0:
#							value = 0
#				if value:
#					timage.putpixel((x,y), 1)
#				else:
#					timage.putpixel((x,y), 0)
		return timage
				
	
	def generateGrid(self):
		print "grid"
		pcbim = self.pcbImage.rotate(int(self.rotationSpinbox.get()))
		pcbim = self.thickenLines(pcbim)
		x_size = pcbim.size[0]
		y_size = pcbim.size[1]
		x_margin = int(float(self.xSpacingEntry.get()) * 23.622)
		y_margin = int(float(self.ySpacingEntry.get()) * 23.622)

		upperMargin = int(float(self.upperMarginEntry.get()) * 23.622) #convert from mm to 600dpi dots
		rightMargin = int(float(self.rightMarginEntry.get()) * 23.622)
		x_copys = int(self.xCopysSpinbox.get())
		y_copys = int(self.yCopysSpinbox.get())
		im = Image.new('L',(WORK_X_SIZE, WORK_Y_SIZE), 0)
		x_work_size = rightMargin + x_size * x_copys + (x_copys-1) * x_margin
		y_work_size = upperMargin + y_size * y_copys + (y_copys-1) * y_margin
		for x in range(x_copys):
			for y in range(y_copys):
				x_pos = WORK_X_SIZE - 1 - rightMargin - (x_size + x_margin) * (x_copys - x) + x_margin
				y_pos = upperMargin + (y_size + y_margin) * y
				im.paste(pcbim, (x_pos, y_pos))
		self.workImage = im
		self.updateSizeCallback((x_work_size, y_work_size))
		self.generateThumbnail()

	def getLine(self, line):
		data = []
		x_size = self.workImage.size[0]
		
		for x in range((x_size - (x_size % 8))-8, -8, -8):
			val = 0
			for b in range(7,-1,-1):
				val <<= 1
				if (self.workImage.getpixel((x + b, line))):
					val |= 0x01
			data.append( val)

		#vorschau
		x_size = self.thumb.size[0]
		if line%4 == 0 :
			for x in range(0, x_size):
				if (self.thumb.getpixel((x, line/4)) != (0,0,0)):
					self.thumb.putpixel((x, line/4), (255,0,0)) 
			
		
		photo = ImageTk.PhotoImage(self.thumb)
		self.updateThumbnailCallback(photo)

		return data

	def open_file(self):
		myPdf = askopenfilename(filetypes=[("pdf files", "*.pdf")], initialdir="d:/work/eagle")
		#print myPdf
		args = "-mono -f 1 -l 1 -r 600 \"" + myPdf + "\" C:/Windows/Temp/"
		#print args
		call("pdftoppm " + args, shell=True)
		image = Image.open("c:/Windows/Temp/-000001.pbm")
		#image.show()
		im = image.convert("L")
		im1 = ImageOps.invert(im)
		
		self.pcbImage = im.crop(im1.getbbox())
		self.generateGrid()

class MachineData:
	def read_config(self):
		f = open("calib.txt")
		self.start_delay = int(f.readline())
		self.delaySettings = []
		for i in range(40):
			self.delaySettings.append(int(f.readline()))
		self.stepperStartPos = int(f.readline())
	def generateTimingData(self):
		self.timingData = [] #new byte[480];
		tbl = self.timingData
		
		pos = 0
		finepos = 0 # pos = finepos / 8
		tbl_cnt = 0
		
		for x in range(40):
		    if ((x & 0x01) == 0):
		        count = 8
		    else:
		        count = 7
		
		    for y in range (count):
		        finepos += self.delaySettings[x]
		        oldpos = pos
		        pos = int(finepos / 8)
		        tbl.append(pos - oldpos)
		
		for i in range (len(tbl), 480):
			tbl.append (0)
	def __init__(self):
		self.read_config()
		self.generateTimingData()
	def translateLine(self, line_600dpi):
		#//array has 480 bytes, each represents 8 pixels, msb left
		#//translates 600dpi lines to 1/16MHz delays between changes
		
		min_delay = 30
		delays = []
		
		delay_akk = 0
		last_change = 0
		
		aktval = False
		
		for x in range(len(line_600dpi)):
			for bit in range(7,-1,-1):
				val = (line_600dpi[x] & (1 << bit)) != 0
				if(val != aktval):
					aktval = val
					delays.append( int(delay_akk / 2) - last_change)
					last_change = int(delay_akk / 2)
				delay_akk += self.timingData[x]
		
		subfromnext = 0
		ret = []
		
		for x in range(len(delays)):
			tmp = delays[x]
			tmp -= subfromnext
			if (tmp < min_delay):
				subfromnext = min_delay - tmp
				tmp = min_delay
			else:
				subfromnext = 0
				
			if (tmp < 256):
				ret.append (tmp)
			else:
				ret.append (0)
				ret.append (tmp % 256)
				ret.append (int(tmp /256))
		
		ret.append (0)# //end mark
		ret.append (0)
		ret.append (0)
		
		
		return ( ret );


class SerialCom():
	def __init__(self):
		self.ser = serial.Serial('COM7', 128000, timeout=1)
	def getStatus(self):
		self.ser.write('S')
		return ord(self.ser.read())
	def write(self, str):
		self.ser.write(str)
	def write16(self, val):
		if(val < 0): val = 65536 + val
		self.ser.write(chr(val % 256))
		self.ser.write(chr(val / 256))
	def data(self, data):
		self.ser.write('d')
		status = ord(self.ser.read())
		d = ''
		for item in data:
			d += chr(item)
		
		self.write16(len(data))
		self.ser.write(d)
		return status
	def stepper(self, val):
		self.ser.write('s')
		self.write16(val)
		
		


class App():
	def create_menu(self):
		menubar = Menu(self.root)
		
		# create a pulldown menu, and add it to the menu bar
		filemenu = Menu(menubar, tearoff=0)
		filemenu.add_command(label="Open", command=self.pcbData.open_file)
		filemenu.add_separator()
		filemenu.add_command(label="Exit", command=self.root.quit)
		menubar.add_cascade(label="File", menu=filemenu)
		
		helpmenu = Menu(menubar, tearoff=0)
		#helpmenu.add_command(label="About", command=hello)
		menubar.add_cascade(label="Help", menu=helpmenu)
		
		# display the menu
		self.root.config(menu=menubar)

	def __init__(self):
		self.root = Tk()
		
		self.serialCom = SerialCom()
		self.machineData = MachineData()
		
		
		self.content = Frame(self.root)
		self.content.grid(column=0, row=0, sticky=(N, S, E, W))
		
		self.pcbSettingsFrame = Frame(self.content)
		self.pcbSettingsFrame.grid(column=0, row=0)
		
		self.controlFrame = Frame(self.content)
		self.controlFrame.grid(column=0, row=1)
		
		
		i = 0
				
		label = Label(self.controlFrame, text="size")
		label.grid(column=0, row=i)
		
		self.sizeText = StringVar()
		self.sizeLabel = Label(self.controlFrame, textvariable=self.sizeText)
		self.sizeLabel.grid(column=1, row=i)
		i += 1
		
		goButton = Button(self.controlFrame, text="Go", command=self.goCommand)
		goButton.grid(column=1, row=i)
		i += 1
		
		stopButton = Button(self.controlFrame, text="Stop", command=self.stopCommand)
		stopButton.grid(column=1, row=i)
		i += 1

		delayLabel = Label(self.controlFrame, text="Delay")
		delayLabel.grid(column=0, row=i)
		self.delayEntry = Entry(self.controlFrame)
		self.delayEntry.insert(0, '120')		
		self.delayEntry.grid(column=1, row=i)
		i += 1
		
		self.pcbData = PcbData(self.pcbSettingsFrame, self.updateThumbnail, self.updateSize)
		
		self.create_menu()
		self.tickAction = 0
		self.currentLine = 0
		self.lastLine = 0
		
		self.root.after(500, self.goTick)

		self.root.mainloop()
		
	def goTick(self):
		status = self.serialCom.getStatus()
		print status
		if (self.tickAction == 0) :
			self.root.after(100, self.goTick)
		elif (self.tickAction == 1) :
			if( status & 0x01): #stepper ready (at ls)
				self.serialCom.stepper(self.machineData.stepperStartPos) #stepper to pcb zero position
				self.tickAction = 2
			self.root.after(100, self.goTick)
		elif (self.tickAction == 2) :
			if( 7 == status): #all is ready
				self.serialCom.write('l1') #laser on
				self.tickAction = 3
			self.root.after(100, self.goTick)
		elif (self.tickAction == 3) :
			if( 7 == (status & 7)):
				data = self.machineData.translateLine(self.pcbData.getLine(self.currentLine))
				self.serialCom.data(data)
				self.serialCom.stepper(-1)
				
				self.currentLine += 1
				if(self.currentLine >= self.lastLine):
					self.tickAction = 4

				self.root.after(int(self.delayEntry.get()), self.goTick)
			else:
				self.serialCom.write('l0') #laser off
				self.tickAction = 2
				self.root.after(100, self.goTick)
		elif (self.tickAction == 4) :
			self.serialCom.write('l0') #laser off
			self.serialCom.write('m0') #polygon motor off
			self.serialCom.stepper(0)  #home stepper
			self.tickAction = 0
			self.root.after(100, self.goTick)

	def goCommand(self):
		self.currentLine = 0
		self.pcbData.generateThumbnail() #remove allready drawn laser lines
		self.serialCom.write('m1') #polygon motor on
		self.serialCom.stepper(0)  #home stepper
		self.tickAction = 1
	
	def stopCommand(self):
		self.serialCom.write('m0l0')
		self.tickAction = 0

	def updateThumbnail(self, photo):
		for w in self.content.grid_slaves(column=1, row=0):
			w.grid_remove()
			w.destroy()
		label = Label(self.content, image=photo)
		label.image = photo # keep a reference!
		label.grid(row=0, column=1,  rowspan=2, sticky=(N, S, E, W))
	def updateSize(self, size):
		#self.sizeText.set( str(size[0] / 23.622) + " x " + str(size[1] / 23.622) + " mm")
		self.sizeText.set( "%1.2f x %1.2f mm" % (size[0] / 23.622 , size[1] / 23.622) )
		#print self.sizeText
		self.lastLine = size[1]
		
app=App()
