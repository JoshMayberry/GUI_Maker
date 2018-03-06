__version__ = "1.0.0"

import os
import sys
import subprocess

import wx
import wx.lib.agw.advancedsplash

class Utitlities():
	"""Utility functions for the splash screen."""

	def convertImageToBitmap(self, imgImage):
		"""Converts a wxImage image (wxPython) to a wxBitmap image (wxPython).
		Adapted from: https://wiki.wxpython.org/WorkingWithImages

		imgImage (object) - The wxBitmap image to convert

		Example Input: convertImageToBitmap(image)
		"""

		bmpImage = imgImage.ConvertToBitmap()
		return bmpImage

	def convertPilToImage(self, pilImage, alpha = False):
		"""Converts a PIL image (pillow) to a wxImage image (wxPython).
		Adapted from: https://wiki.wxpython.org/WorkingWithImages

		pilImage (object) - The PIL image to convert
		alpha (bool)      - If True: The image will preserve any alpha chanels

		Example Input: convertPilToImage(image)
		Example Input: convertPilToImage(image, True)
		"""

		imgImage = wx.Image(pilImage.size[0], pilImage.size[1])

		hasAlpha = pilImage.mode[-1] == 'A'
		if (hasAlpha and alpha):
			pilImageCopyRGBA = pilImage.copy()
			pilImageRgbData = pilImageCopyRGBA.convert("RGB").tobytes()
			imgImage.SetData(pilImageRgbData)
			imgImage.SetAlpha(pilImageCopyRGBA.tobytes()[3::4])

		else:
			pilImage = pilImage.convert("RGB").tobytes()
			imgImage.SetData(pilImage)

		return imgImage

	def convertPilToBitmap(self, pilImage, alpha = False):
			"""Converts a PIL image (pillow) to a wxBitmap image (wxPython).
			Adapted from: https://wiki.wxpython.org/WorkingWithImages

			pilImage (object) - The PIL image to convert
			alpha (bool)      - If True: The image will preserve any alpha chanels

			Example Input: convertPilToBitmap(image)
			"""

			imgImage = self.convertPilToImage(pilImage, alpha)
			bmpImage = self.convertImageToBitmap(imgImage)
			return bmpImage

	def getImage(self, imagePath, internal = False, alpha = False):
		"""Returns the image as specified by the user.

		imagePath (str) - Where the image is on the computer. Can be a PIL image. If None, it will be a blank image
			If 'internal' is on, it is the name of an icon as a string. Here is a list of the icon names:
				"error"       - A red circle with an 'x' in it
				"question"    - A white speach bubble with a '?' in it
				"question2"   - A white speach bubble with a '?' in it. Looks different from "question"
				"warning"     - A yellow yield sign with a '!' in it
				"info"        - A white circle with an 'i' in it
				"font"        - A times new roman 'A'
				"arrowLeft"   - A white arrow pointing left
				"arrowRight"  - A white arrow pointing right
				"arrowUp"     - A white arrow pointing up
				"arrowDown"   - A white arrow pointing down
				"arrowCurve"  - A white arrow that moves left and then up
				"home"        - A white house
				"print"       - A printer
				"open"        - "folderOpen" with a green arrow curiving up and then down inside it
				"save"        - A blue floppy disk
				"saveAs"      - "save" with a yellow spark in the top right corner
				"delete"      - "markX" in a different style
				"copy"        - Two "page" stacked on top of each other with a southeast offset
				"cut"         - A pair of open scissors with red handles
				"paste"       - A tan clipboard with a blank small version of "page2" overlapping with an offset to the right
				"undo"        - A blue arrow that goes to the right and turns back to the left
				"redo"        - A blue arrow that goes to the left and turns back to the right
				"lightBulb"   - A yellow light bulb with a '!' in it
				"folder"      - A blue folder
				"folderNew"   - "folder" with a yellow spark in the top right corner
				"folderOpen"  - An opened version of "folder"
				"folderUp"    - "folderOpen" with a green arrow pointing up inside it
				"page"        - A blue page with lines on it
				"page2"       - "page" in a different style
				"pageNew"     - "page" with a green '+' in the top left corner
				"pageGear"    - "page" with a blue gear in the bottom right corner
				"pageTorn"    - A grey square with a white border torn in half lengthwise
				"markCheck"   - A black check mark
				"markX"       - A black 'X'
				"plus"        - ?
				"minus"       - ?
				"close"       - A black 'X'
				"quit"        - A door opening to the left with a green arrow coming out of it to the right
				"find"        - A magnifying glass
				"findReplace" - "find" with a double sided arrow in the bottom left corner pointing left and right
				"first"       - ?
				"last"        - ?
				"diskHard"    - ?
				"diskFloppy"  - ?
				"diskCd"      - ?
				"book"        - A blue book with white pages
				"addBookmark" - A green banner with a '+' by it
				"delBookmark" - A red banner with a '-' by it
				"sidePanel"   - A grey box with lines in with a white box to the left with arrows pointing left and right
				"viewReport"  - A white box with lines in it with a grey box with lines in it on top
				"viewList"    - A white box with squiggles in it with a grey box with dots in it to the left
		internal (bool) - If True: 'imagePath' is the name of an icon as a string.
		alpha (bool)    - If True: The image will preserve any alpha chanels

		Example Input: getImage("example.bmp", 0)
		Example Input: getImage(image, 0)
		Example Input: getImage("error", 0, internal = True)
		Example Input: getImage("example.bmp", 0, alpha = True)
		"""

		#Determine if the image is a blank image
		if (imagePath != None):
			#Determine if the image is a PIL image
			if (type(imagePath) != str):
				image = self.convertPilToBitmap(imagePath, alpha)
			else:
				#Determine if the image is an internal image
				if (internal):
					if (imagePath == "error"):
						image = wx.ArtProvider.GetBitmap(wx.ART_ERROR)
						
					elif (imagePath == "question"):
						image = wx.ArtProvider.GetBitmap(wx.ART_QUESTION)
						
					elif (imagePath == "question2"):
						image = wx.ArtProvider.GetBitmap(wx.ART_HELP)
						
					elif (imagePath == "warning"):
						image = wx.ArtProvider.GetBitmap(wx.ART_WARNING)
						
					elif (imagePath == "info"):
						image = wx.ArtProvider.GetBitmap(wx.ART_INFORMATION)
						
					elif (imagePath == "font"):
						image = wx.ArtProvider.GetBitmap(wx.ART_HELP_SETTINGS)
						
					elif (imagePath == "arrowLeft"):
						image = wx.ArtProvider.GetBitmap(wx.ART_GO_BACK)
						
					elif (imagePath == "arrowRight"):
						image = wx.ArtProvider.GetBitmap(wx.ART_GO_FORWARD)
						
					elif (imagePath == "arrowUp"):
						image = wx.ArtProvider.GetBitmap(wx.ART_GO_UP)
						
					elif (imagePath == "arrowDown" ):
						image = wx.ArtProvider.GetBitmap(wx.ART_GO_DOWN)
						
					elif (imagePath == "arrowCurve"):
						image = wx.ArtProvider.GetBitmap(wx.ART_GO_TO_PARENT)
						
					elif (imagePath == "home"):
						image = wx.ArtProvider.GetBitmap(wx.ART_GO_HOME)
						
					elif (imagePath == "print"):
						image = wx.ArtProvider.GetBitmap(wx.ART_PRINT)
						
					elif (imagePath == "open"):
						image = wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN)
						
					elif (imagePath == "save"):
						image = wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE)
						
					elif (imagePath == "saveAs"):
						image = wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE_AS)
						
					elif (imagePath == "delete"):
						image = wx.ArtProvider.GetBitmap(wx.ART_DELETE)
						
					elif (imagePath == "copy"):
						image = wx.ArtProvider.GetBitmap(wx.ART_COPY)
						
					elif (imagePath == "cut"):
						image = wx.ArtProvider.GetBitmap(wx.ART_CUT)
						
					elif (imagePath == "paste"):
						image = wx.ArtProvider.GetBitmap(wx.ART_PASTE)
						
					elif (imagePath == "undo"):
						image = wx.ArtProvider.GetBitmap(wx.ART_UNDO)
						
					elif (imagePath == "redo"):
						image = wx.ArtProvider.GetBitmap(wx.ART_REDO)
						
					elif (imagePath == "lightBulb"):
						image = wx.ArtProvider.GetBitmap(wx.ART_TIP)
						
					elif (imagePath == "folder"):
						image = wx.ArtProvider.GetBitmap(wx.ART_FOLDER)
						
					elif (imagePath == "newFolder"):
						image = wx.ArtProvider.GetBitmap(wx.ART_NEW_DIR)
						
					elif (imagePath == "folderOpen"):
						image = wx.ArtProvider.GetBitmap(wx.ART_FOLDER_OPEN)
						
					elif (imagePath == "folderUp"):
						image = wx.ArtProvider.GetBitmap(wx.ART_GO_DIR_UP)
						
					elif (imagePath == "page"):
						image = wx.ArtProvider.GetBitmap(wx.ART_NORMAL_FILE)
						
					elif (imagePath == "page2"):
						image = wx.ArtProvider.GetBitmap(wx.ART_HELP_PAGE)
						
					elif (imagePath == "pageNew"):
						image = wx.ArtProvider.GetBitmap(wx.ART_NEW)
						
					elif (imagePath == "pageGear"):
						image = wx.ArtProvider.GetBitmap(wx.ART_EXECUTABLE_FILE)
						
					elif (imagePath == "pageTorn"):
						image = wx.ArtProvider.GetBitmap(wx.ART_MISSING_IMAGE)
						
					elif (imagePath == "markCheck"):
						image = wx.ArtProvider.GetBitmap(wx.ART_TICK_MARK)
						
					elif (imagePath == "markX"):
						image = wx.ArtProvider.GetBitmap(wx.ART_CROSS_MARK)
						
					elif (imagePath == "plus"):
						image = wx.ArtProvider.GetBitmap(wx.ART_PLUS )
						
					elif (imagePath == "minus"):
						image = wx.ArtProvider.GetBitmap(wx.ART_MINUS )
						
					elif (imagePath == "close"):
						image = wx.ArtProvider.GetBitmap(wx.ART_CLOSE)
						
					elif (imagePath == "quit"):
						image = wx.ArtProvider.GetBitmap(wx.ART_QUIT)
						
					elif (imagePath == "find"):
						image = wx.ArtProvider.GetBitmap(wx.ART_FIND)
						
					elif (imagePath == "findReplace"):
						image = wx.ArtProvider.GetBitmap(wx.ART_FIND_AND_REPLACE)
						
					elif (imagePath == "first"):
						image = wx.ArtProvider.GetBitmap(wx.ART_GOTO_FIRST)
						
					elif (imagePath == "last"):
						image = wx.ArtProvider.GetBitmap(wx.ART_GOTO_LAST )
						
					elif (imagePath == "diskHard"):
						image = wx.ArtProvider.GetBitmap(wx.ART_HARDDISK)
						
					elif (imagePath == "diskFloppy"):
						image = wx.ArtProvider.GetBitmap(wx.ART_FLOPPY)
						
					elif (imagePath == "diskCd"):
						image = wx.ArtProvider.GetBitmap(wx.ART_CDROM)
						
					elif (imagePath == "book"):
						image = wx.ArtProvider.GetBitmap(wx.ART_HELP_BOOK)
						
					elif (imagePath == "addBookmark"):
						image = wx.ArtProvider.GetBitmap(wx.ART_ADD_BOOKMARK)
						
					elif (imagePath == "delBookmark"):
						image = wx.ArtProvider.GetBitmap(wx.ART_DEL_BOOKMARK)
						
					elif (imagePath == "sidePanel"):
						image = wx.ArtProvider.GetBitmap(wx.ART_HELP_SIDE_PANEL)
						
					elif (imagePath == "viewReport"):
						image = wx.ArtProvider.GetBitmap(wx.ART_REPORT_VIEW)
						
					elif (imagePath == "viewList"):
						image = wx.ArtProvider.GetBitmap(wx.ART_LIST_VIEW)
						
					else:
						print("ERROR: The icon", imagePath, "cannot be found")
				else:
					try:
						image = wx.Bitmap(imagePath)
					except:
						image = wx.Image(imagePath, wx.BITMAP_TYPE_BMP).ConvertToBitmap()
		else:
			image = wx.NullBitmap

		return image

class SplashScreen(Utitlities):
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
			self.image = self.getImage("error", internal = True)
			self.timeout = 5000 #ms
			self.centerScreen = True
			self.shadow = None

	def setImage(self, imagePath, internal = False, alpha = False):
		"""Changes the splash screen image.

		imagePath (str) - Where the image is on the computer. Can be a PIL image. If None, it will be a blank image
		internal (bool) - If True: 'imagePath' is the name of an icon as a string.
		alpha (bool)    - If True: The image will preserve any alpha chanels

		Example Input: getImage("example.bmp", 0)
		Example Input: getImage("error", 0, internal = True)
		Example Input: getImage("example.bmp", 0, alpha = True)
		"""

		if (len(sys.argv) == 1):
			if (self.splashApp):
				self.image = self.getImage(imagePath, internal = internal, alpha = alpha)

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
					flags = "wx.lib.agw.advancedsplash.AS_TIMEOUT"
				else:
					flags = "wx.lib.agw.advancedsplash.AS_NOTIMEOUT"

				if (self.centerScreen != None):
					if (self.centerScreen):
						flags += "|wx.lib.agw.advancedsplash.AS_CENTER_ON_SCREEN"
					else:
						flags += "|wx.lib.agw.advancedsplash.AS_CENTER_ON_PARENT"
				else:
					flags += "|wx.lib.agw.advancedsplash.AS_NO_CENTER"

				if (self.shadow != None):
					flags += "|wx.lib.agw.advancedsplash.AS_SHADOW_BITMAP"
				else:
					self.shadow = wx.NullColour

				myFrame = wx.lib.agw.advancedsplash.AdvancedSplash(self.parent, bitmap = self.image, timeout = self.timeout, agwStyle = eval(flags), shadowcolour = self.shadow)

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
	splashScreen = SplashScreen()
	splashScreen.finish()

	# Simulate 1.3s of time spent importing libraries and source files
	import time
	time.sleep(1.3)

	class MyApp(wx.App):
		def OnInit(self):
			# Simulate 6s of time spent initializing wx components
			time.sleep(6)

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