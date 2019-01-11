__version__ = "2.0.0"

import time
import atexit
import multiprocessing

import operator
import functools

import wx
import MyUtilities.common
import MyUtilities.wxPython
import MyUtilities.multiProcess

splashList = set()

def freeze_support():
	multiprocessing.freeze_support()

def makeSplash(*args, **kwargs):
	"""Creates a splash screen, then shows it."""

	return SplashProcess(*args, **kwargs)

@atexit.register
def hideSplash(*args, myApp = None, **kwargs):
	"""Hides the splash screen created by makeSplash()."""
	global splashList

	for splash in tuple(splashList):
		splash.hide(*args, **kwargs)

	if (myApp is not None):
		myApp.MainLoop()

class StatusText(wx.StaticText, MyUtilities.common.EnsureFunctions):
	"""A wxStaticText object used to display the program's status."""

	def __init__(self, parent, *, default = None, font = None, 
		align = "center", pulse = False, style = 0):
		"""
		default (str) - What the status text will say when set to None
		font (wxFont) - What font to use
		align (str) - How to align the text in the sizer #Not implemented yet
		pulse (bool) - Determines if three periods appear cycle from 0 to 3 after the text at a rate of 250ms #Not implemented yet

		Example Input: StatusText(self)
		"""

		self.parent = parent

		self.default = self.ensure_default(default, default = "Loading...")
		self.font = self.ensure_default(font, default = lambda: wx.Font(24, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))

		super().__init__(parent, id = wx.ID_ANY, label = self.default, style = style)

		self.SetFont(self.font)

	@MyUtilities.common.makeProperty()
	class status():
		"""What the status text says."""

		def getter(self):
			return self.GetLabel()

		def setter(self, value):
			"""If None: Will show the default status text.

			Example Use: status = "Lorem Ipsum"
			Example Use: status = None
			"""

			if (value is None):
				self.SetLabel(self.default)
			else:
				self.SetLabel(value)

class SplashImage(wx.StaticBitmap):
	"""A wxStaticBitmap used as the splash screen's image."""

	def __init__(self, parent, *, filePath = None, 
		mask = True, maskColor = "black", style = 0, **imageKwargs):
		"""
		filePath (str) - A path to the image to show
		scale (tuple) - The scale to use for the image
			- If None: Will not scale the image

		mask (str) - A path to the mask to use for the image
			- If None: No mask will be applied
			- If True: Will use 'image' as the mask file

		maskColor (wxColor) - What color to use for the mask

		Example Input: SplashImage(self)
		"""

		self.bitmap = MyUtilities.wxPython.getImage(filePath, mask = mask, maskColor = maskColor, **imageKwargs,
			returnForNone = lambda: MyUtilities.wxPython.getImage("error", internal = True, scale = (300, 300)))

		super().__init__(parent, id = wx.ID_ANY, bitmap = self.bitmap, style = style)

class SplashProgress(wx.Gauge):
	"""A wxGauge used to display the program's progress."""

	def __init__(self, parent, *, initial = 0, maximum = 100, vertical = False, style = 0):
		"""
		initial (int) - Where to start the progress bar at
		maximum (int) - What the maximum progress value is
		vertical (bool) - Determines if the progress bar is displayed vertically or horizontally

		Example Input: SplashProgress(self)
		"""

		super().__init__(parent, id = wx.ID_ANY, range = maximum or 100, style = style | (wx.GA_HORIZONTAL, wx.GA_VERTICAL)[vertical])

		self.progress = initial

	@MyUtilities.common.makeProperty()
	class progressMax():
		"""The maximum position of the progress bar."""

		def getter(self):
			return self.GetRange()

		def setter(self, value):
			self.SetRange(value)

	@MyUtilities.common.makeProperty()
	class progress():
		"""The position of the progress bar."""

		def getter(self):
			return self.GetValue()

		def setter(self, value):
			"""If None: Will make the progress bar pulse.

			Example Use: progress = 10
			Example Use: progress = None
			"""

			if (value is None):
				self.Pulse()
				return

			maximum = self.progressMax
			if (value > maximum):
				value = maximum
			self.SetValue(value)

class SplashScreen(wx.Frame, MyUtilities.wxPython.DrawFunctions):
	"""A wxFrame object that is used as a splash screen.
		Use: wx.lib.agw.advancedsplash.py
	"""

	def __init__(self, image = None, *, image_scale = None, image_mask = True, image_maskColor = "black",
		status_default = None, status_font = None, status_pulse = False, status_align = "center",
		progress_initial = 0, progress_max = None, progress_vertical = False,

		size = None, position = None, resizeable = False, timeout = None):
		"""
		

		timeout (int) - How long to wait before hiding the splash screen
			- If None: Will not auto-hide the splash screen

		size (tuple) - The starting size for the window
			- If None: Will use the image size

		position (tuple) - Where the window should be located
			- If None: Will center on the monitor

		resizeable (bool) - Determines if the window can be resized

		Example Input: SplashScreen()
		Example Input: SplashScreen(size = (400, 400))
		Example Input: SplashScreen("resources/splashScreen.bmp")
		Example Input: SplashScreen("resources/splashScreen.bmp", timeout = 1500)
		"""

		#Create Frame
		style = [wx.FRAME_NO_TASKBAR|wx.FRAME_SHAPED|wx.STAY_ON_TOP]

		if (resizeable):
			style.append(wx.RESIZE_BORDER)
		
		wx.Frame.__init__(self, None, id = wx.ID_ANY, pos = position or wx.DefaultPosition, style = functools.reduce(operator.ior, style or (0,))) 

		#Populate Window
		self.thing_panel = wx.Panel(self, id = wx.ID_ANY)
		
		self.thing_text = StatusText(self.thing_panel, default = status_default, font = status_font, pulse = status_pulse, align = status_align)
		self.thing_image = SplashImage(self.thing_panel, filePath = image, scale = image_scale, mask = image_mask, maskColor = image_maskColor)
		self.thing_progressBar = SplashProgress(self.thing_panel, initial = progress_initial, maximum = progress_max, vertical = progress_vertical)

		mainSizer = wx.FlexGridSizer(3, 1, 0, 0)
		mainSizer.AddGrowableCol(0, 1)
		mainSizer.AddGrowableRow(0, 1)

		mainSizer.Add(self.thing_image, 		0, wx.ALL|wx.EXPAND, 0)
		mainSizer.Add(self.thing_text, 			1, wx.ALL|wx.EXPAND, 0)
		mainSizer.Add(self.thing_progressBar, 	0, wx.ALL|wx.EXPAND, 0)

		self.thing_panel.SetSizer(mainSizer)
		mainSizer.Fit(self)

		#Final Settings
		if (position is None):
			self.CenterOnScreen()

		#Bind events
		self.Bind(wx.EVT_CLOSE, lambda event: self.Destroy())

		if wx.Platform == "__WXGTK__":
			self.Bind(wx.EVT_WINDOW_CREATE, self.SetSplashShape)
		else:
			self.SetSplashShape()

	def SetSplashShape(self, event = None):
		"""Modified code from: wx.lib.agw.advancedsplash.SetSplashShape."""

		region = wx.Region(self.thing_progressBar.GetRect())
		region.Union(self.thing_text.GetRect())
		region.Union(self.thing_image.bitmap)
		region.Offset(1, 1)

		self.SetShape(region)

		if (event is not None):
			event.Skip()

class SplashProcess():
	def __init__(self, image = None, **splashKwargs):
		"""A handle for interacting with the splash screen process

		Example Input: SplashThread()
		Example Input: SplashThread(name = None)
		"""
		global splashList

		splashList.add(self)

		self.image = image
		self.splashKwargs = splashKwargs

		self.processHandle = MyUtilities.multiProcess.Parent(event = 2, queue = True)
		self.processChild = self.processHandle.spawn(myFunction = self.run)
		self.begin()

	def begin(self, waitForStart = True, waitTimeout = None):
		"""Starts the splash screen process.

		waitForStart (bool) - Determines if the program should wait for the splash screen to be created before continuing

		Example Input: begin()
		Example Input: begin(waitForStart = True)
		Example Input: begin(waitForStart = True, waitDelay = 10)
		"""

		self.processChild.start()

		if (waitForStart):
			self.processChild.event[0].wait(timeout = waitTimeout)

	def run(self, child):
		"""The function to run for the splash screen process."""

		self.app = self.MyApp(self)

		child.splashHandle = SplashScreen(image = self.image, **self.splashKwargs)
		child.event[0].set()
		child.splashHandle.Show()

		self.app.MainLoop()

	def hide(self):
		"""Hides the splash screen.

		Example Input: hide()
		"""

		if (not hasattr(self, "processChild")):
			return

		self.processChild.event[1].set()
		self.processChild.join()

		splashList.discard(self)

	def setProgressMax(self, value):
		self.processChild.append(("thing_progressBar", "progressMax", value))

	def setProgress(self, value):
		self.processChild.append(("thing_progressBar", "progress", value))

	def addProgress(self, value):
		self.processChild.append((None, None, value))

	def setStatus(self, value):
		self.processChild.append(("thing_text", "status", value))

	class MyApp(wx.App):
		def __init__(self, parent, redirect = False, filename = None, useBestVisual = False, clearSigInt = True):
			"""Needed to make the GUI work."""

			self.parent = parent
			wx.App.__init__(self, redirect = redirect, filename = filename, useBestVisual = useBestVisual, clearSigInt = clearSigInt)

		def MainLoop(self):
			"""Modified code from: https://github.com/wxWidgets/wxPython/blob/master/samples/mainloop/mainloop.py"""

			# wx.DisableAsserts() #Allows a thread that is not this thread to exit the program (https://stackoverflow.com/questions/49304429/wxpython-main-thread-other-than-0-leads-to-wxwidgets-debug-alert-on-exit/49305518#49305518)

			processChild = self.parent.processChild
			splashQueue = processChild.queue
			if (splashQueue is None):
				return super().MainLoop()

			splashHandle = processChild.splashHandle
			hideEvent = processChild.event[1]

			import queue
			eventLoop = wx.GUIEventLoop()
			wx.EventLoop.SetActive(eventLoop)

			while True:
				#Hide event
				if (hideEvent.is_set()):
					splashHandle.Hide()
					splashHandle.Close()
					break

				#Update GUI
				try:
					thing, variable, value = splashQueue.get_nowait() #doesn't block
					
					if (variable is None):
						splashHandle.thing_progressBar.progress += 1
					else:
						setattr(getattr(splashHandle, thing), variable, value)

				except queue.Empty: #raised when queue is empty
					pass

				#Handle events
				while eventLoop.Pending():
					eventLoop.Dispatch()

				#Process idle events
				time.sleep(0.01)
				eventLoop.ProcessIdle()


if __name__ == '__main__':

	# splash = makeSplash(image = "examples/resources/splashScreen.bmp", image_maskColor = (0, 177, 64))
	splash = makeSplash(image = "H:/Python/Material_Tracker/resources/splashScreen.png", image_maskColor = (63, 63, 63))

	splash.setProgressMax(20)
	
	#Simulate long tasks
	for i in range(8):
		time.sleep(0.25)
		splash.setProgress(i)

	splash.setStatus("Creating Window")

	#Create main app
	app = wx.App(False)
	frame = wx.Frame(None, wx.ID_ANY, "Lorem Ipsum")

	time.sleep(2)

	#Simulate more long tasks
	for i in range(20):
		splash.setStatus(f"Doing thing {i + 1}")

		time.sleep(0.25)
		splash.addProgress(1)


	time.sleep(20)

	#Show main app now
	frame.Show()
	hideSplash(myApp = app)
