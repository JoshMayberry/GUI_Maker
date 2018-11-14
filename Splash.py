__version__ = "1.0.0"

import os
import sys
import operator
import functools
import subprocess

import wx
import wx.lib.agw.advancedsplash

import Utilities.debugging

#Use: https://stackoverflow.com/questions/24247772/wxpython-custom-splashscreen-with-progress-gauge

class SplashScreen():
	"""Shows a splash screen before running your code.
	This shows the user things are happening while your program loads.
	Modified code from: https://wiki.wxpython.org/SplashScreen%20While%20Loading
	_________________________________________________________________________

	EAMPLE USAGE
	from modules.GUI_Maker.Splash import SplashScreen
	splashScreen = SplashScreen()
	splashScreen.setTimeout(1500)
	imagePath = "resources/valeoSplashScreen.bmp"
	splashScreen.setImage(imagePath)
	splashScreen.finish()
	"""

	def __init__(self, parent = None, exeOnly = True):
		"""Defines internal variables and defaults.

		exeOnly (bool) - Determiens what types of applications will launch the splash screen
			- If True: Only a .exe will show the splash screen
			- If False: Both a .exe and a .py will show the splash screen
			- If None: Any file type will show the splash screen

		Example Input: SplashScreen()
		Example Input: SplashScreen(myFrame)
		"""

		#Default Variables for both apps
		self.showSplash = True
		self.splashApp = False

		#Account for main app
		if (len(sys.argv) == 1):
			#Account for splash screen not showing for development stages
			if (not sys.argv[0].endswith(".exe")):
				if(exeOnly != None):
					if (exeOnly):
						return None
					else:
						if (not sys.argv[0].endswith(".py")):
							return None

			#Internal Variables
			self.App = wx.App() #This must run before the wxArtProvider
			self.parent = parent
			self.fileName = sys.argv[0]
			self.splashApp = True #Only runs splash screen functions for the splash app, not the main app

			#Default Variables for splash screen only
			self.image = Utilities.debugging.getImage("error", internal = True)
			self.timeout = 5000 #ms
			self.centerScreen = True
			self.shadow = None

	def setImage(self, imagePath, internal = False, alpha = False):
		"""Changes the splash screen image.

		imagePath (str) - Where the image is on the computer. Can be a PIL image. If None, it will be a blank image
		internal (bool) - If True: 'imagePath' is the name of an icon as a string.
		alpha (bool)    - If True: The image will preserve any alpha chanels

		Example Input: setImage("example.bmp", 0)
		Example Input: setImage("error", 0, internal = True)
		Example Input: setImage("example.bmp", 0, alpha = True)
		"""

		if (len(sys.argv) == 1):
			if (self.splashApp):
				self.image = Utilities.debugging.getImage(imagePath, internal = internal, alpha = alpha)

	def setTimeout(self, timeout):
		"""Changes the duration of the splash screen.

		timeout (int) - How long to show the splash screen in milliseconds
			- If None: The splash screen will disappear after clicking on it

		Example Input: setTimeout(9000)
		Example Input: setTimeout(None)
		"""

		if (len(sys.argv) == 1):
			if (self.splashApp):
				self.timeout = timeout

	def disableSplashScreen(self, disable = True):
		"""Disables the splash screen.

		disable (bool) - Determines if the splash screen is shown or not.
			- If True: The splash screen will not appear
			- If False: The splash screen will appear

		Example: disableSplashScreen()
		Example: disableSplashScreen(False)
		"""

		if (len(sys.argv) == 1):
			if (self.splashApp):
				self.showSplash = not disable

	def enableSplashScreen(self, enable = True):
		"""Enables the splash screen.

		enable (bool) - Determines if the splash screen is shown or not.
			- If True: The splash screen will appear
			- If False: The splash screen will not appear

		Example: enableSplashScreen()
		Example: enableSplashScreen(False)
		"""

		if (len(sys.argv) == 1):
			if (self.splashApp):
				self.showSplash = enable

	def toggleSplashScreen(self):
		"""Enables the splash screen if it is disabled and disables it if it is enabled.

		Example: toggleSplashScreen()
		"""

		if (len(sys.argv) == 1):
			if (self.splashApp):
				self.showSplash = not self.showSplash

	def setCenter(self, centerScreen = True):
		"""Changes where the splash screen appears.

		centerScreen (bool) - Determines if the splash screen is cenetred and if so on what
			- If True: It will be cenetred on the screen
			- If False: It will be centered on the parent
			- If None: It will not be centered

		Example Input: setCenter()
		Example Input: setCenter(False)
		Example Input: setCenter(None)
		"""

		if (len(sys.argv) == 1):
			if (self.splashApp):
				self.centerScreen = centerScreen

	def setShadow(self, shadow = (0, 0, 0)):
		"""If the image has no transparency, this casts a shadow of one color.

		shadow (tuple) - The shadow color as (r, g, b)
			- If None: No shadow will appear

		Example Input: setShadow()
		Example Input: setShadow((255, 255, 255))
		Example Input: setShadow(None)
		"""

		if (len(sys.argv) == 1):
			if (self.splashApp):

				#Ensure correct format
				if ((type(shadow) == tuple) or (type(shadow) == list)):
					shadow = wx.Colour(shadow[0], shadow[1], shadow[2])

				self.shadow = shadow

	def finish(self):
		"""Run this when you are finished building the splash screen.

		Example Input: finish()
		"""

		#Launch the splash screen and the main program as two separate applications
		if (self.showSplash and len(sys.argv) == 1):
			if (self.splashApp):
				#Build splash screen
				if (self.timeout != None):
					flags = [wx.lib.agw.advancedsplash.AS_TIMEOUT]
				else:
					flags = [wx.lib.agw.advancedsplash.AS_NOTIMEOUT]

				if (self.centerScreen != None):
					if (self.centerScreen):
						flags.append(wx.lib.agw.advancedsplash.AS_CENTER_ON_SCREEN)
					else:
						flags.append(wx.lib.agw.advancedsplash.AS_CENTER_ON_PARENT)
				else:
					flags.append(wx.lib.agw.advancedsplash.AS_NO_CENTER)

				if (self.shadow != None):
					flags.append(wx.lib.agw.advancedsplash.AS_SHADOW_BITMAP)
				else:
					self.shadow = wx.NullColour

				myFrame = wx.lib.agw.advancedsplash.AdvancedSplash(self.parent, bitmap = self.image, timeout = self.timeout, agwStyle = functools.reduce(operator.ior, flags or (0,)), shadowcolour = self.shadow)

				#Launch program again as a separate application
				if (self.fileName.endswith(".py")):
					command = ["py", os.path.basename(self.fileName), "NO_SPLASH"]
				else:
					command = [os.path.basename(self.fileName), "NO_SPLASH"]
				subprocess.Popen(command)

				#Run the splash screen
				self.App.MainLoop()
				sys.exit()

if __name__ == "__main__":
	print("Building Splash Screen...")
	splashScreen = SplashScreen()
	print("Finishing Splash Screen...")
	splashScreen.finish()

	print("Simulating Imports...")
	import time
	time.sleep(1.3) # Simulate 1.3s of time spent importing libraries and source files

	class MyApp(wx.App):
		def OnInit(self):
			print("Simulating Building GUI...")
			time.sleep(6) # Simulate 6s of time spent initializing wx components
			print("GUI Finished")

			#Ensure only one instance runs
			self.name = "SingleApp-%s" % wx.GetUserId()
			self.instance = wx.SingleInstanceChecker(self.name)

			if self.instance.IsAnotherRunning():
				wx.MessageBox("Cannot run multiple instances of this program", "Runtime Error")
				return False

			#Create App
			self.Frame = wx.Frame(None, -1, "Application Frame")
			self.Frame.Show()
			return True

	App = MyApp(0)
	App.MainLoop()