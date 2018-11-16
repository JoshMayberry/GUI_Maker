__version__ = "2.0.0"

import os
import sys
import time
import threading

import operator
import functools
import contextlib

import wx
import Utilities as MyUtilities
# import pubsub.pub
from forks.pypubsub.src.pubsub import pub as pubsub_pub #Use my own fork

_splashThread = None

@contextlib.contextmanager
def makeSplash_cm(*args, **kwargs):
	"""A context manager version of makeSplash().
	Yields a handle that can be used to set up the splash screen.
	On exit, the splash screen will be shown.

	Example Use:
		with makeSplash_cm() as mySplash:
			mySplash.setTimeout(1500)
			mySplash.setImage("resources/splashScreen.bmp")
	"""
	global _splashThread

	_splashThread = SplashThread(*args, **kwargs)

	yield _splashThread

	_splashThread.start()

def makeSplash(*args, waitDelay = 100, **kwargs):
	"""Creates a splash screen, then shows it."""

	with makeSplash_cm(*args, **kwargs):
		pass

	#Wait for splash screen to appear
	while ((_splashThread.splashHandle is None) or (not _splashThread.splashHandle.IsShown())):
		time.sleep(waitDelay / 1000)

	return _splashThread

def hideSplash(*args, myApp = None, **kwargs):
	"""Hides the splash screen created by makeSplash()."""
	global _splashThread

	_splashThread.hide(*args, **kwargs)

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

		pubsub_pub.subscribe(self.setStatus, 'status')

	def setStatus(self, value):
		self.status = value

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

		self.bitmap = MyUtilities.wxPython._getImage(filePath, mask = mask, maskColor = maskColor, **imageKwargs,
			returnForNone = lambda: MyUtilities.wxPython._getImage("error", internal = True, scale = (300, 300)))

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

		pubsub_pub.subscribe(self.setProgress, 'progress')
		pubsub_pub.subscribe(self.setProgressMax, 'progressMax')

	def setProgress(self, value):
		self.progress = value

	def setProgressMax(self, value):
		self.progressMax = value

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

class SplashThread(threading.Thread):
	def __init__(self, image = None, *, threadName = "Splash", **splashKwargs):
		"""A thread used to show a splash screen on.

		Example Input: SplashThread()
		Example Input: SplashThread(name = None)
		"""

		threading.Thread.__init__(self, name = threadName, daemon = True)

		self.image = image
		self.splashHandle = None
		self.splashKwargs = splashKwargs

	def run(self):
		"""Runs the thread and then closes it."""

		self.app = wx.App(False)

		self.splashHandle = SplashScreen(image = self.image, **self.splashKwargs)
		self.splashHandle.Show()

		wx.DisableAsserts() #Allows a thread that is not this thread to exit the program (https://stackoverflow.com/questions/49304429/wxpython-main-thread-other-than-0-leads-to-wxwidgets-debug-alert-on-exit/49305518#49305518)

		self.app.MainLoop()

	def hide(self, *, waitForClose = False, waitDelay = 100):
		"""Hides the splash screen.

		TO DO: This currently takes a long time (sometimes) to close the app in this thread.
			Find out why and fix it.

		waitForClose (bool) - Determines if the program should wait for the splash screen to hide before continuing
		waitDelay (int) - How long to wait between checks for if the splash screen has closed yet

		Example Input: hide()
		Example Input: hide(waitForClose = True)
		Example Input: hide(waitForClose = True, waitDelay = 10)
		"""

		if (self.splashHandle is None):
			print("Splash screen is already hidden")
			return

		self.splashHandle.Hide()
		self.splashHandle.Close()
		self.splashHandle = None

		# if (not waitForClose):
		# 	return

		# while self.is_alive():
		# 	print("@hide")
		# 	time.sleep(waitDelay / 1000)

	@MyUtilities.common.makeProperty()
	class progressMax():
		def getter(self):
			return self.splashHandle.thing_progressBar.progressMax

		def setter(self, value):
			self.splashHandle.thing_progressBar.progressMax = value


	@MyUtilities.common.makeProperty()
	class progress():
		def getter(self):
			return self.splashHandle.thing_progressBar.progress

		def setter(self, value):
			self.splashHandle.thing_progressBar.progress = value


	@MyUtilities.common.makeProperty()
	class status():
		def getter(self):
			return self.splashHandle.thing_text.status

		def setter(self, value):
			pubsub_pub.sendMessage("status", value = value)

if __name__ == '__main__':
	#Create Splash Screen
	splash = makeSplash(image = "examples/resources/splashScreen.bmp", image_maskColor = (0, 177, 64))
	# splash = makeSplash(image = "H:/Python/Material_Tracker/resources/splashScreen.png")

	splash.progressMax = 20
	
	#Simulate long tasks
	for i in range(8):
		time.sleep(0.25)
		splash.progress = i

	splash.status = "Creating Window"

	#Create main app
	app = wx.App(False)
	frame = wx.Frame(None, wx.ID_ANY, "Lorem Ipsum")

	time.sleep(2)

	#Simulate more long tasks
	for i in range(20):
		splash.status = f"Doing thing {i + 1}"

		time.sleep(0.25)
		splash.progress += 1

	#Show main app now
	frame.Show()
	hideSplash(myApp = app)
