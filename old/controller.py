__version__ = "4.2.0"

#TO DO
# - Add File Drop: https://www.blog.pythonlibrary.org/2012/06/20/wxpython-introduction-to-drag-and-drop/
# - Add Wrap Sizer: https://www.blog.pythonlibrary.org/2014/01/22/wxpython-wrap-widgets-with-wrapsizer/
# - Look through these demos for more things: https://github.com/wxWidgets/Phoenix/tree/master/demo
# - Look through the menu examples: https://www.programcreek.com/python/example/44403/wx.EVT_FIND

# - Add handler indexing
#		~ See Operation Table on: https://docs.python.org/3/library/stdtypes.html#typeiter

#IMPORT CONTROLS
##Here the user can turn on and off specific parts of the module, 
##which will reduce the overall size of a generated .exe.
##To do so, comment out the block of import statements
##WARNING: If you turn off a feature, make sure you dont try to use it.

#Import standard elements to interact with the computer
# import os
import sys
import time
import copy
# import ctypes
import string
# import builtins
import inspect
import warnings
# import functools


#Import wxPython elements to create GUI
import wx
import wx.adv
import wx.grid
import wx.lib.masked
# import wx.lib.newevent
import wx.lib.splitter
import wx.lib.agw.floatspin
import wx.lib.mixins.listctrl
import wx.lib.agw.fourwaysplitter

#Import matplotlib elements to add plots to the GUI
# import matplotlib
# matplotlib.use('WXAgg')
# matplotlib.get_py2exe_datafiles()
# import matplotlib.pyplot as plt
# from matplotlib.backends.backend_wxagg import FigureCanvas


#Import py2exe elements for creating a .exe of the GUI
# import sys; sys.argv.append('py2exe')
# from distutils.core import setup
# import py2exe


#Import cryptodome to encrypt and decrypt files
# import Cryptodome.Random
# import Cryptodome.Cipher.AES
# import Cryptodome.PublicKey.RSA
# import Cryptodome.Cipher.PKCS1_OAEP


#Import communication elements for talking to other devices such as printers, the internet, a raspberry pi, etc.
import socket
import serial
import serial.tools.list_ports

#Import barcode software for drawing and decoding barcodes
# import elaphe


#Import multi-threading to run functions as background processes
import queue
import threading
import subprocess


#Import needed support modules
import re
# import atexit
# import netaddr
# import PIL.Image


#Import user-defined modules
# from .ExcelManipulator_6 import Excel #Used to make wxGrid objects interactable with excel


#Database Interaction
# from .DatabaseAPI_12 import Database


#Required Modules
##py -m pip install
	# wxPython
	# openpyxl
	# numpy
	# matplotlib
	# py2exe
	# pillow
	# pycryptodomex
	# atexit
	# netaddr
	# elaphe
	# python3-ghostscript "https://pypi.python.org/pypi/python3-ghostscript/0.5.0#downloads"
	# sqlite3

##User Created
	#ExcelManipulator

##Module Patches (Replace the following files with these from my computer)
	#C:\Python34\Lib\site-packages\wx\lib\masked\maskededit.py

##Module dependancies (Install the following .exe files)
	#"Ghostscript AGPL Release" on "https://ghostscript.com/download/gsdnld.html"
		#Make sure you install the 32 bit version if you are using 32 bit python
		#Add the .dll location to your PATH enviroment variable. Mine was at "C:\Program Files (x86)\gs\gs9.20\bin"

#_________________________________________________________________________#
#                                                                         #
#            !!!    Do not change code below this point    !!!            #
#_________________________________________________________________________#
#                                                                         #

#Global Variables
# idGen = 2000 #Used to generate individual identifyers
# idCatalogue = {} #Used to keep track of important IDs
valueQueue = {} #Used to keep track of values the user wants to have
dragDropDestination = None #Used to help a source know if a destination is itself
nestingCatalogue = {} #Used to keep track of what is nested in what

#Controllers
def build(*args, **kwargs):
	"""Starts the GUI making process."""

	return Controller(*args, **kwargs)

#Iterators
class Iterator(object):
	"""Used by handle objects to iterate over their nested objects."""

	def __init__(self, data):
		self.data = data

	def __iter__(self):
		return self

	def __next__(self):
		if not self.data:
			raise StopIteration
		return self.data.pop()

#Background Processes
class ThreadQueue():
	"""Used by passFunction() to move functions from one thread to another.
	Special thanks to Claudiu for the base code on https://stackoverflow.com/questions/18989446/execute-python-function-in-main-thread-from-call-in-dummy-thread
	"""
	def __init__(self):
		"""Internal variables."""
	
		self.callback_queue = queue.Queue()

	def from_dummy_thread(self, myFunction, myFunctionArgs = None, myFunctionKwargs = None):
		"""A function from a MyThread to be called in the main thread."""

		self.callback_queue.put([myFunction, myFunctionArgs, myFunctionKwargs])

	def from_main_thread(self, blocking = True):
		"""An non-critical function from the sub-thread will run in the main thread.

		blocking (bool) - If True: This is a non-critical function
		"""

		def setupFunction(self, myFunctionList, myFunctionArgsList, myFunctionKwargsList):
			#Skip empty functions
			if (myFunctionList != None):
				myFunctionList, myFunctionArgsList, myFunctionKwargsList = Utilities.formatFunctionInputList(self, myFunctionList, myFunctionArgsList, myFunctionKwargsList)
				
				#Run each function
				for i, myFunction in enumerate(myFunctionList):
					#Skip empty functions
					if (myFunction != None):
						myFunctionEvaluated, myFunctionArgs, myFunctionKwargs = Utilities.formatFunctionInput(self, i, myFunctionList, myFunctionArgsList, myFunctionKwargsList)
						runFunction(self, myFunctionEvaluated, myFunctionArgs, myFunctionKwargs)

		def runFunction(self, myFunction, myFunctionArgs, myFunctionKwargs):
			"""Runs a function."""

			#Has both args and kwargs
			if ((myFunctionKwargs != None) and (myFunctionArgs != None)):
				myFunction(*myFunctionArgs, **myFunctionKwargs)

			#Has args, but not kwargs
			elif (myFunctionArgs != None):
				myFunction(*myFunctionArgs)

			#Has kwargs, but not args
			elif (myFunctionKwargs != None):
				myFunction(**myFunctionKwargs)

			#Has neither args nor kwargs
			else:
				myFunction()

		if (blocking):
			myFunction, myFunctionArgs, myFunctionKwargs = self.callback_queue.get() #blocks until an item is available
			setupFunction(self, myFunction, myFunctionArgs, myFunctionKwargs)
			
			runFunction(self, myFunction, myFunctionArgs, myFunctionKwargs)

		else:		
			while True:
				try:
					myFunction, myFunctionArgs, myFunctionKwargs = self.callback_queue.get(False) #doesn't block
				
				except queue.Empty: #raised when queue is empty
					print("--- Thread Queue Empty ---")
					break

				setupFunction(self, myFunction, myFunctionArgs, myFunctionKwargs)

class MyThread(threading.Thread):
	"""Used to run functions in the background.
	More information on threads can be found at: https://docs.python.org/3.4/library/threading.html
	_________________________________________________________________________

	CREATE AND RUN A NEW THREAD
	#Create new threads
	thread1 = myThread(1, "Thread-1", 1)
	thread2 = myThread(2, "Thread-2", 2)

	#Start new threads
	thread1.start()
	thread2.start()
	_________________________________________________________________________

	RUNNING A FUNCTION ON A THREAD
	After the thread has been created and started, you can run functions on it like you do on the main thread.
	The following code shows how to run functions on the new thread:

	runFunction(longFunction, [1, 2], {label: "Lorem"}, self, False)
	_________________________________________________________________________

	If you exit the main thread, the other threads will still run.

	EXAMPLE CREATING A THREAD THAT EXITS WHEN THE MAIN THREAD EXITS
	If you want the created thread to exit when the main thread exits, make it a daemon thread.
		thread1 = myThread(1, "Thread-1", 1, daemon = True)

	You can also make it a daemon using the function:
		thread1.setDaemon(True)
	_________________________________________________________________________

	CLOSING A THREAD
	If any thread is open, the program will not end. To close a thread use return on the function that is running in the thread.
	The thread will then close itself automatically.
	"""

	def __init__(self, threadID = None, name = None, counter = None, daemon = None):
		"""Setup the thread.

		threadID (int) -
		name (str)     - The thread name. By default, a unique name is constructed of the form "Thread-N" where N is a small decimal number.
		counter (int)  - 
		daemon (bool)  - Sets whether the thread is daemonic. If None (the default), the daemonic property is inherited from the current thread.
		
		Example Input: MyThread()
		Example Input: MyThread(1, "Thread-1", 1)
		Example Input: MyThread(daemon = True)
		"""

		#Initialize the thread
		threading.Thread.__init__(self, name = name, daemon = daemon)
		# self.setDaemon(daemon)

		#Setup thread properties
		if (threadID != None):
			self.threadID = threadID

		self.stopEvent = threading.Event() #Used to stop the thread

		#Initialize internal variables
		self.shown = None
		self.window = None
		self.myFunction = None
		self.myFunctionArgs = None
		self.myFunctionKwargs = None

	def runFunction(self, myFunction, myFunctionArgs, myFunctionKwargs, window, shown):
		"""Sets the function to run in the thread object.

		myFunction (str)        - What function will be ran. Can a function object
		myFunctionArgs (list)   - The arguments for 'myFunction'
		myFunctionKwargs (dict) - The keyword arguments for 'myFunction'
		window (wxFrame)        - The window that called this function
		shown (bool)            - If True: The function will only run if the window is being shown. It will wait for the window to first be shown to run.
								  If False: The function will run regardless of whether the window is being shown or not
								  #### THIS IS NOT WORKING YET ####

		Example Input: runFunction(longFunction, [1, 2], {label: "Lorem"}, 5, False)
		"""

		#Record given values
		self.shown = shown
		self.window = window
		self.myFunction = myFunction
		self.myFunctionArgs = myFunctionArgs
		self.myFunctionKwargs = myFunctionKwargs
		self.start()

	def run(self):
		"""Runs the thread and then closes it."""

		if (self.shown):
			#Wait until the window is shown to start
			while True:
				#Check if the thread should still run
				if (self.stopEvent.is_set()):
					return

				#Check if the window is shown yet
				if (self.window.showWindowCheck()):
					break

				#Reduce lag
				time.sleep(0.01)

		#Has both args and kwargs
		if ((self.myFunctionKwargs != None) and (self.myFunctionArgs != None)):
			self.myFunction(*self.myFunctionArgs, **self.myFunctionKwargs)

		#Has args, but not kwargs
		elif (self.myFunctionArgs != None):
			self.myFunction(*self.myFunctionArgs)

		#Has kwargs, but not args
		elif (self.myFunctionKwargs != None):
			self.myFunction(**self.myFunctionKwargs)

		#Has neither args nor kwargs
		else:
			self.myFunction()

	def stop(self):
		"""Stops the running thread."""

		self.stopEvent.set()

#Global Inheritance Classes
class Utilities():
	"""Contains common functions needed for various other functions.
	This is here for convenience in programming.
	"""

	def __init__(self):
		"""Defines the internal variables needed to run.

		Example Input: Meant to be inherited by Controller().
		"""

		self.keyOptions = {
			"0": 48, "1": 49, "2": 50, "3": 51, "4": 52, "5": 53, "6": 54,  "7": 55, "8": 56, "9": 57,
			"numpad+0": 324, "numpad+1": 325, "numpad+2": 326, "numpad+3": 327, "numpad+4": 328, 
			"numpad+5": 329, "numpad+6": 330, "numpad+7": 331, "numpad+8": 332, "numpad+9": 333, 

			#For some reason lower case letters are being read as upper case. To Do: Investigate why and fix it
			# "A": 65, "B": 66, "C": 67, "D": 68, "E": 69, "F": 70, "G": 71, "H": 72, "I": 73, "J": 74,
			# "K": 75, "L": 76, "M": 77, "N": 78, "O": 79, "P": 80, "Q": 81, "R": 82, "S": 83, "T": 84,
			# "U": 85, "V": 86, "W": 87, "X": 88, "Y": 89, "Z": 90,

			"a": 65, "b": 66, "c": 67, "d": 68, "e": 69, "f": 70, "g": 71, "h": 72, "i": 73, "j": 74,
			"k": 75, "l": 76, "m": 77, "n": 78, "o": 79, "p": 80, "q": 81, "r": 82, "s": 83, "t": 84,
			"u": 85, "v": 86, "w": 87, "x": 88, "y": 89, "z": 90,

			# "a": 97, "b": 98, "c": 99, "d": 100, "e": 101, "f": 102, "g": 103,  "h": 104, "i": 105,
			# "j": 106, "k": 107, "l": 108, "m": 109, "n": 110, "o": 111, "p": 112,  "q": 113,
			# "r": 114, "s": 115, "t": 116, "u": 117, "v": 118, "w": 119, "x": 120, "y": 121, "z": 122,
			
			"ctrl+a": 1, "ctrl+b": 2, "ctrl+c": 3, "ctrl+d": 4, "ctrl+e": 5, "ctrl+f": 6, "ctrl+g": 7,
			"ctrl+h": 8, "ctrl+i": 9, "ctrl+j": 10, "ctrl+k": 11, "ctrl+l": 12, "ctrl+m": 13, "ctrl+n": 14, 
			"ctrl+o": 15, "ctrl+p": 16, "ctrl+q": 17, "ctrl+r": 18, "ctrl+s": 19, "ctrl+t": 20,
			"ctrl+u": 21, "ctrl+v": 22, "ctrl+w": 23, "ctrl+x": 24, "ctrl+y": 25, "ctrl+z": 26,

			"!": 33, "\"": 34, "#": 35, "$": 36, "%": 37, "&": 38, "'": 39, "(": 40, ")": 41, 
			"*": 42, "+": 43, ",": 44, "-": 45, ".": 46, "/": 47, ":": 58, ";": 59, "<": 60, 
			"=": 61, ">": 62, "?": 63, "@": 64, "[": 91, "\\": 92, "]": 93, "^": 94, "_": 95, 
			"`": 96, "{": 123, "|": 124, "}": 125, "~": 126,

			"start": 300, "buttonL": 301, "buttonR": 302, "cancel": 303, "buttonM": 304, 
			"left": 314, "up": 315, "right": 316, "down": 317, "windows+left": 393, "windows+right": 394,
			"numpad+left": 376, "numpad+up": 377, "numpad+right": 378, "numpad+down": 379, 

			"none":  0, "null": 0, "backspace": 8, "tab": 9, "tab_hor": 9, "tab_vert": 11, "enter": 13, 
			"return": 13, "\n": 13, "esc": 27, "escape": 27, "space": 32, " ": 32,  "del": 127, 
			"delete": 127, "clear": 305, "shift": 306, "alt": 307, "control": 308, "ctrl": 308, 
			"crtlRaw": 308, "menu": 309, "pause": 310, "capital": 311, "end": 312, "home": 313, 
			"select": 318, "print": 319, "execute": 320, "snapshot": 321, "insert": 322, "help": 323,
			"multiply": 334, "add": 335, "separate": 336, "subtract": 337, "decimal": 338, "divide": 339,
			"numlock": 364, "scroll": 365, "pageup": 366, "pagedown": 367,
			
			"f1": 340, "f2": 341, "f3": 342, "f4": 343, "f5": 344, "f6": 345, "f7": 346, "f8": 347, "f9": 348,
			"f10": 349, "f11": 350, "f12": 351, "f13": 352, "f14": 353, "f15": 354, "f16": 355, "f17": 356,
			"f18": 357, "f19": 358, "f20": 359, "f21": 360, "f22": 361, "f23": 362, "f24": 363,
			"numpad+f1": 371, "numpad+f2": 372,  "numpad+f3": 373, "numpad+f4": 374, 

			"numpad+enter": 370, "numpad+equal": 386, "numpad+=": 386, "numpad+multiply": 387, 
			"numpad+*": 387, "numpad+add": 388, "numpad++": 388, "numpad+subtract": 390, "numpad+-": 390,
			"numpad+decimal": 391, "numpad+divide": 392, "numpad+/": 392, "numpad+\\": 392,

			"numpad+space": 368, "numpad+ ": 368, "numpad+tab": 369, "numpad+end": 382, "numpad+begin": 383, 
			"numpad+insert": 384, "numpad+delete": 385, "numpad+home": 375, "numpad+separate": 389,
			"numpad+pageup": 380, "numpad+pagedown": 381, "windows+menu": 395, "command": 308, "cmd": 308,

			"special+1": 193, "special+2": 194, "special+3": 195, "special+4": 196, "special+5": 197,
			"special+6": 198, "special+7": 199, "special+8": 200, "special+9": 201, "special+10": 202,
			"special+11": 203, "special+12": 204, "special+13": 205, "special+14": 206, "special+15": 207,
			"special+16": 208, "special+17": 209, "special+18": 210, "special+19": 211, "special+20": 212}

	#Binding Functions
	def formatFunctionInputList(self, myFunctionList, myFunctionArgsList, myFunctionKwargsList):
		"""Formats the args and kwargs for various internal functions."""

		#Ensure that multiple function capability is given
		##Functions
		if (myFunctionList != None):
			#Compensate for the user not making it a list
			if (type(myFunctionList) != list):
				if (type(myFunctionList) == tuple):
					myFunctionList = list(myFunctionList)
				else:
					myFunctionList = [myFunctionList]

			#Fix list order so it is more intuitive
			if (len(myFunctionList) > 1):
				myFunctionList.reverse()

		##args
		if (myFunctionArgsList != None):
			#Compensate for the user not making it a list
			if (type(myFunctionArgsList) != list):
				if (type(myFunctionArgsList) == tuple):
					myFunctionArgsList = list(myFunctionArgsList)
				else:
					myFunctionArgsList = [myFunctionArgsList]

			#Fix list order so it is more intuitive
			if (len(myFunctionList) > 1):
				myFunctionArgsList.reverse()

			if (len(myFunctionList) == 1):
				myFunctionArgsList = [myFunctionArgsList]

		##kwargs
		if (myFunctionKwargsList != None):
			#Compensate for the user not making it a list
			if (type(myFunctionKwargsList) != list):
				if (type(myFunctionKwargsList) == tuple):
					myFunctionKwargsList = list(myFunctionKwargsList)
				else:
					myFunctionKwargsList = [myFunctionKwargsList]

			#Fix list order so it is more intuitive
			if (len(myFunctionList) > 1):
				myFunctionKwargsList.reverse()

		return myFunctionList, myFunctionArgsList, myFunctionKwargsList

	def formatFunctionInput(self, i, myFunctionList, myFunctionArgsList, myFunctionKwargsList):
		"""Formats the args and kwargs for various internal functions."""

		myFunction = myFunctionList[i]

		#Skip empty functions
		if (myFunction != None):
			#Use the correct args and kwargs
			if (myFunctionArgsList != None):
				myFunctionArgs = myFunctionArgsList[i]
			else:
				myFunctionArgs = myFunctionArgsList

			if (myFunctionKwargsList != None):
				myFunctionKwargs = myFunctionKwargsList[i]
				
			else:
				myFunctionKwargs = myFunctionKwargsList

			#Check for User-defined function
			if (type(myFunction) != str):
				#The address is already given
				myFunctionEvaluated = myFunction
			else:
				#Get the address of myFunction
				myFunctionEvaluated = eval(myFunction)

			#Ensure the *args and **kwargs are formatted correctly 
			if (myFunctionArgs != None):
				#Check for single argument cases
				if ((type(myFunctionArgs) != list)):
					#The user passed one argument that was not a list
					myFunctionArgs = [myFunctionArgs]
				# else:
				# 	if (len(myFunctionArgs) == 1):
				# 		#The user passed one argument that is a list
				# 		myFunctionArgs = [myFunctionArgs]

			#Check for user error
			if ((type(myFunctionKwargs) != dict) and (myFunctionKwargs != None)):
				errorMessage = "myFunctionKwargs must be a dictionary for function {}".format(myFunctionEvaluated.__repr__())
				raise ValueError(errorMessage)

		return myFunctionEvaluated, myFunctionArgs, myFunctionKwargs

	def betterBind(self, eventType, thing, myFunctionList, myFunctionArgsList = None, myFunctionKwargsList = None, mode = 1):
		"""Binds wxObjects in a better way.
		Inspired by: "Florian Bosch" on http://stackoverflow.com/questions/173687/is-it-possible-to-pass-arguments-into-event-bindings
		Special thanks for help on mult-functions to "Mike Driscoll" on http://stackoverflow.com/questions/11621833/how-to-bind-2-functions-to-a-single-event

		eventType (CommandEvent) - The wxPython event to be bound
		thing (wxObject)         - What is being bound to
		myFunctionList (str)     - The function that will be ran when the event occurs
		myFunctionArgs (list)    - Any input arguments for myFunction. A list of multiple functions can be given
		myFunctionKwargs (dict)  - Any input keyword arguments for myFunction. A dictionary of variables for each function can be given as a list. The index of the variables must be the same as the index for the functions 
		mode (int)               - Dictates how things are bound. Used for special cases
		_________________________________________________________________________

		MULTIPLE FUNCTION ORDER
		The functions are ran in the order given; from left to right.

		MULTIPLE FUNCTION FAILURE
		Make it a habbit to end all bound functions with 'event.Skip()'. 
		If the bound function does not end with 'event.Skip()', then it will overwrite a previously bound function.
		This will result in the new function being ran in place of both functions.
		_________________________________________________________________________

		Example Input: betterBind(wx.EVT_BUTTON, menuItem, "self.onExit", "Extra Information")
		Example Input: betterBind(wx.EVT_BUTTON, menuItem, ["self.toggleObjectWithLabel", "self.onQueueValue", ], [["myCheckBox", True], None])
		"""

		#Create the sub-function that does the binding
		def bind(self, eventType, thing, myFunctionEvaluated, myFunctionArgs, myFunctionKwargs, mode):
			"""This sub-function is needed to make the multiple functions work properly."""

			#Get the class type in order to bind the object to the correct thing
			thingClass = thing.GetClassName()

			##Determine how to bind the object
			if (thingClass == "wxWindow"):
				if (mode == 2):
					bindObject = thing
				else:
					bindObject = self.parent.thing

			elif (thingClass == "wxMenuItem"):
				bindObject = self.thing
			else:
				bindObject = thing

			#Typical binding mode
			if (mode == 1):
				#Has both args and kwargs
				if ((myFunctionKwargs != None) and (myFunctionArgs != None)):
					bindObject.Bind(eventType, lambda event: myFunctionEvaluated(event, *myFunctionArgs, **myFunctionKwargs), thing)

				#Has args, but not kwargs
				elif (myFunctionArgs != None):
					bindObject.Bind(eventType, lambda event: myFunctionEvaluated(event, *myFunctionArgs), thing)

				#Has kwargs, but not args
				elif (myFunctionKwargs != None):
					bindObject.Bind(eventType, lambda event: myFunctionEvaluated(event, **myFunctionKwargs), thing)

				#Has neither args nor kwargs
				else:
					bindObject.Bind(eventType, lambda event: myFunctionEvaluated(event), thing)

			#Binding mode for window key bindings
			elif (mode == 2):
				#Has both args and kwargs
				if ((myFunctionKwargs != None) and (myFunctionArgs != None)):
					bindObject.Bind(eventType, lambda event: myFunctionEvaluated(event, *myFunctionArgs, **myFunctionKwargs))

				#Has args, but not kwargs
				elif (myFunctionArgs != None):
					bindObject.Bind(eventType, lambda event: myFunctionEvaluated(event, *myFunctionArgs))

				#Has kwargs, but not args
				elif (myFunctionKwargs != None):
					bindObject.Bind(eventType, lambda event: myFunctionEvaluated(event, **myFunctionKwargs))

				#Has neither args nor kwargs
				else:
					bindObject.Bind(eventType, lambda event: myFunctionEvaluated(event))

			else:
				errorMessage = "Unknown mode {} for betterBind()".format(mode)
				raise TypeError(errorMessage)

		#Skip empty functions
		if (myFunctionList != None):
			myFunctionList, myFunctionArgsList, myFunctionKwargsList = self.formatFunctionInputList(myFunctionList, myFunctionArgsList, myFunctionKwargsList)
			#Run each function
			for i, myFunction in enumerate(myFunctionList):
				#Skip empty functions
				if (myFunction != None):
					myFunctionEvaluated, myFunctionArgs, myFunctionKwargs = self.formatFunctionInput(i, myFunctionList, myFunctionArgsList, myFunctionKwargsList)
					bind(self, eventType, thing, myFunctionEvaluated, myFunctionArgs, myFunctionKwargs, mode)

	def keyBind(self, key, thing, myFunctionList, myFunctionArgsList = None, myFunctionKwargsList = None, includeEvent = True,
		keyUp = True, numpad = False, ctrl = False, alt = False, shift = False, event = None):
		"""Binds wxObjects to key events.
		Speed efficency help from Aya on http://stackoverflow.com/questions/17166074/most-efficient-way-of-making-an-if-elif-elif-else-statement-when-the-else-is-don

		key (str)              - The keyboard key to bind the function(s) to
		thing (wxObject)       - What is being bound to
		myFunctionList (str)   - The function that will be ran when the event occurs
		myFunctionArgs (any)   - Any input arguments for myFunction. A list of multiple functions can be given
		myFunctionKwargs (any) - Any input keyword arguments for myFunction. A list of variables for each function can be given. The index of the variables must be the same as the index for the functions
		includeEvent (bool)    - If True: The event variable will be passed to the function, like a normal event function would get

		keyUp (bool)  - If True: The function will run when the key is released
						If False: The function will run when the key is pressed
		numpad (bool) - If True: The key is located on the numpad
		ctrl (bool)   - If True: The control key is pressed
		alt (bool)    - If True: The control key is pressed
		shift (bool)  - If True: The shift key is pressed

		event (wxCommandEvent) - If not None: This will be the bound event instead of the ones provided below

		Example Input: keyBind("enter", inputBox, "self.onExit", "Extra Information")
		Example Input: keyBind("enter", inputBox, "self.onExit", "Extra Information", ctrl = True)
		Example Input: keyBind("enter", inputBox, ["self.toggleObjectWithLabel", "self.onQueueValue", ], [["myInputBox", True], None])
		"""

		#Check for key modifiers
		keyCheck = re.split("\$@\$", key)
		if (keyCheck != None):
			if (len(keyCheck) != 1):
				#Correctly format the key
				for i, item in enumerate(keyCheck):
					#Mind the capital letter keys
					if (len(key) != 1):
						keyCheck[i] = item.lower()

				#Toggle modifiers
				if ("noctrl") in keyCheck:
					ctrl = False
				elif ("ctrl") in keyCheck:
					ctrl = True

				if ("noalt") in keyCheck:
					alt = False
				elif ("alt") in keyCheck:
					alt = True

				if ("noshift") in keyCheck:
					shift = False
				elif ("shift") in keyCheck:
					shift = True

				if ("nonumpad") in keyCheck:
					numpad = False
				elif ("numpad") in keyCheck:
					numpad = True

				if ("nokeyup") in keyCheck:
					keyUp = False
				elif ("keyup") in keyCheck:
					keyUp = True

				#Remove modifier strings from key
				key = keyCheck[0]

		#Mind the capital letter keys
		if (len(key) != 1):
			#Correctly format the key
			key = key.lower()

		if (numpad):
			if ("numpad" not in key):
				key = "numpad+" + key
		# elif (ctrl):
		#   if ("ctrl" not in key):
		#       key = "ctrl+" + key

		#Error Check
		if (key not in self.keyOptions):
			print("ERROR:", key, "is not a known key binding")
			return None

		#Get the corresponding key address
		value = self.keyOptions[key]

		#Determine at what time to run the function
		if (event == None):
			if (keyUp):
				event = wx.EVT_KEY_UP
			else:
				event = wx.EVT_KEY_DOWN

		#Bind the event
		self.betterBind(event, thing, self.onKeyPress, [value, myFunctionList, myFunctionArgsList, myFunctionKwargsList, ctrl, alt, shift, includeEvent], mode = 2)

		return value #Used for finished()

	def onKeyPress(self, event, *args, **kwargs):
		"""Runs a function on a specific key press.
		Inorder to bind multiple keys to the same object, the keys must be passed in as a list.

		Keep in mind that this function runs every time any key is pressed.
		The function associated with that key will only run if the current.
		key is the same as the associated key.
		"""

		#Create the sub-function that does the binding
		def runFunction(event, myFunctionEvaluated, myFunctionArgs, myFunctionKwargs, includeEvent):
			"""This sub-function is needed to make the multiple functions work properly.

			Keep in mind that 'event' is passed on as well. This is so that the key press 
			events can function the same way as other triggered events.
			"""

			#Ensure the *args and **kwargs are formatted correctly 
			if ((type(myFunctionArgs) != list) and (myFunctionArgs != None)):
				myFunctionArgs = [myFunctionArgs]

			if ((type(myFunctionKwargs) != list) and (myFunctionKwargs != None)):
				myFunctionKwargs = [myFunctionKwargs]

			#Has both args and kwargs
			if ((myFunctionKwargs != None) and (myFunctionArgs != None)):
				if (includeEvent):
					myFunctionEvaluated(event, *myFunctionArgs, **myFunctionKwargs)
				else:
					myFunctionEvaluated(*myFunctionArgs, **myFunctionKwargs)

			#Has args, but not kwargs
			elif (myFunctionArgs != None):
				if (includeEvent):
					myFunctionEvaluated(event, *myFunctionArgs)
				else:
					myFunctionEvaluated(*myFunctionArgs)

			#Has kwargs, but not args
			elif (myFunctionKwargs != None):
				if (includeEvent):
					myFunctionEvaluated(event, **myFunctionKwargs)
				else:
					myFunctionEvaluated(**myFunctionKwargs)

			#Has neither args nor kwargs
			else:
				if (includeEvent):
					myFunctionEvaluated(event)
				else:
					myFunctionEvaluated()

		#Unpack Values
		keyList = args[0]

		#Format keyList correctly
		if (type(keyList) == tuple):
			keyList = list(keyList)
		elif (type(keyList) != list):
			keyList = [keyList]

		#Read current keyboard state
		keyCode = event.GetKeyCode()

		#Determine if the function should be run
		if (keyCode not in keyList):
			return
		else:
			#Unpack Values
			myFunctionList       = args[1]
			myFunctionArgsList   = args[2]
			myFunctionKwargsList = args[3]
			ctrl  = args[4]
			alt   = args[5]
			shift = args[6]
			includeEvent = args[7]

			#Check for multi-key conditions
			controlDown = event.CmdDown()
			altDown = event.AltDown()
			shiftDown = event.ShiftDown()

			#Check modifiers
			if (ctrl):
				if (not controlDown):
					event.Skip()
					return
			if (not ctrl):
				if (controlDown):
					event.Skip()
					return

			if (alt):
				if (not altDown):
					event.Skip()
					return
			if (not alt):
				if (altDown):
					event.Skip()
					return

			if (shift):
				if (not shiftDown):
					event.Skip()
					return
			if (not shift):
				if (shiftDown):
					event.Skip()
					return

			#Skip empty functions
			if (myFunctionList != None):
				#Ensure that multiple function capability is given
				if ((type(myFunctionList) != list) and (myFunctionList != None)):
					if (type(myFunctionList) == tuple):
						myFunctionList = list(myFunctionList)
					else:
						myFunctionList = [myFunctionList]

				#args
				if ((type(myFunctionArgsList) != list) and (myFunctionArgsList != None)):
					if (type(myFunctionArgsList) == tuple):
						myFunctionArgsList = list(myFunctionArgsList)
					else:
						myFunctionArgsList = [myFunctionArgsList]

					#Compensate for the user not making lists in lists for single functions or multiple functions
					if (len(myFunctionList) == 1):
						#Compensate for the user not making lists in lists for single functions or multiple functions
						if (len(myFunctionArgsList) != 1):
							myFunctionArgsList = [myFunctionArgsList]
				
				if ((len(myFunctionList) == 1) and (myFunctionArgsList != None)):
					#Compensate for the user not making lists in lists for single functions or multiple functions
					if (len(myFunctionArgsList) != 1):
						myFunctionArgsList = [myFunctionArgsList]

				#kwargs
				if ((type(myFunctionKwargsList) != list) and (myFunctionKwargsList != None)):
					if (type(myFunctionKwargsList) == tuple):
						myFunctionKwargsList = list(myFunctionKwargsList)
					else:
						myFunctionKwargsList = [myFunctionKwargsList]

					if (len(myFunctionList) == 1):
						#Compensate for the user not making lists in lists for single functions or multiple functions
						if (len(myFunctionKwargsList) != 1):
							myFunctionKwargsList = [myFunctionKwargsList]
				
				if ((len(myFunctionList) == 1) and (myFunctionKwargsList != None)):
					#Compensate for the user not making lists in lists for single functions or multiple functions
					if (len(myFunctionKwargsList) != 1):
						myFunctionKwargsList = [myFunctionKwargsList]

				#Fix list order so it is more intuitive
				if (myFunctionList != None):
					myFunctionList.reverse()

				if (myFunctionArgsList != None):
					myFunctionArgsList.reverse()

				if (myFunctionKwargsList != None):
					myFunctionKwargsList.reverse()
				
				#Run each function
				for i, myFunction in enumerate(myFunctionList):
					#Skip empty functions
					if (myFunction != None):
						#Use the correct args and kwargs
						if (myFunctionArgsList != None):
							myFunctionArgs = myFunctionArgsList[i]
						else:
							myFunctionArgs = myFunctionArgsList

						if (myFunctionKwargsList != None):
							myFunctionKwargs = myFunctionKwargsList[i]
						else:
							myFunctionKwargs = myFunctionKwargsList

						#Check for User-defined function
						if (type(myFunction) != str):
							#The address is already given
							myFunctionEvaluated = myFunction
						else:
							#Get the address of myFunction
							myFunctionEvaluated = eval(myFunction)

						runFunction(event, myFunctionEvaluated, myFunctionArgs, myFunctionKwargs, includeEvent)

		event.Skip()

	#Background Processes
	def passFunction(self, myFunction, myFunctionArgs = None, myFunctionKwargs = None, thread = None):
		"""Passes a function from one thread to another. Used to pass the function
		If a thread object is not given it will pass from the current thread to the main thread.
		"""

		#Get current thread
		myThread = threading.current_thread()
		mainThread = threading.main_thread()

		#How this function will be passed
		if (thread != None):
			pass

		else:
			if (myThread != mainThread):
				self.threadQueue.from_dummy_thread(myFunction, myFunctionArgs, myFunctionKwargs)

			else:
				print("ERROR: Cannot pass from the main thread to the main thread")

	def recieveFunction(self):
		"""Passes a function from one thread to another. Used to recieve the function.
		If a thread object is not given it will pass from the current thread to the main thread.
		"""

		self.threadQueue.from_main_thread()

	def onBackgroundRun(self, event, myFunctionList, myFunctionArgsList = None, myFunctionKwargsList = None, shown = False):
		"""Here so the function backgroundRun can be triggered from a bound event."""

		#Run the function correctly
		self.backgroundRun(myFunctionList, myFunctionArgsList, myFunctionKwargsList, shown)

		event.Skip()

	def backgroundRun(self, myFunctionList, myFunctionArgsList = None, myFunctionKwargsList = None, shown = False, makeThread = True):
		"""Runs a function in the background in a way that it does not lock up the GUI.
		Meant for functions that take a long time to run.
		If makeThread is true, the new thread object will be returned to the user.

		myFunctionList (str)   - The function that will be ran when the event occurs
		myFunctionArgs (any)   - Any input arguments for myFunction. A list of multiple functions can be given
		myFunctionKwargs (any) - Any input keyword arguments for myFunction. A list of variables for each function can be given. The index of the variables must be the same as the index for the functions
		shown (bool)           - If True: The function will only run if the window is being shown. If the window is not shown, it will terminate the function. It will wait for the window to first be shown to run
								 If False: The function will run regardless of whether the window is being shown or not
		makeThread (bool)      - If True: A new thread will be created to run the function
								 If False: The function will only run while the GUI is idle. Note: This can cause lag. Use this for operations that must be in the main thread.

		Example Input: backgroundRun(self.startupFunction)
		Example Input: backgroundRun(self.startupFunction, shown = True)
		"""

		#Skip empty functions
		if (myFunctionList != None):
			myFunctionList, myFunctionArgsList, myFunctionKwargsList = self.formatFunctionInputList(myFunctionList, myFunctionArgsList, myFunctionKwargsList)

			#Run each function
			for i, myFunction in enumerate(myFunctionList):

				#Skip empty functions
				if (myFunction != None):
					myFunctionEvaluated, myFunctionArgs, myFunctionKwargs = self.formatFunctionInput(i, myFunctionList, myFunctionArgsList, myFunctionKwargsList)

					#Determine how to run the function
					if (makeThread):
						#Create parallel thread
						thread = MyThread(daemon = True)
						thread.runFunction(myFunctionEvaluated, myFunctionArgs, myFunctionKwargs, self, shown)
						return thread
					else:
						#Add to the idling queue
						if (self.idleQueue != None):
							self.idleQueue.append([myFunctionEvaluated, myFunctionArgs, myFunctionKwargs, shown])
						else:
							print("ERROR: The window", self, "was given it's own idle function by the user")
				else:
					print("ERROR: function", i, "in myFunctionList == None for backgroundRun()")
		else:
			print("ERROR: myFunctionList == None for backgroundRun()")

		return None

	def autoRun(self, delay, myFunctionList, myFunctionArgsList = None, myFunctionKwargsList = None, after = False):
		"""Automatically runs the provided function.

		delay (int)           - How many milliseconds to wait before the function is executed
		myFunctionList (list) - What function will be ran. Can be a string or function object
		after (bool)          - If True: The function will run after the function that called this function instead of after a timer ends

		Example Input: autoRun(0, self.startupFunction)
		Example Input: autoRun(5000, myFrame.switchWindow, [0, 1])
		"""

		#Create the sub-function that runs the function
		def runFunction(after, myFunctionEvaluated, myFunctionArgs, myFunctionKwargs):
			"""This sub-function is needed to make the multiple functions work properly."""

			#Has both args and kwargs
			if ((myFunctionKwargs != None) and (myFunctionArgs != None)):
				if (after):
					wx.CallAfter(myFunctionEvaluated, *myFunctionArgs, **myFunctionKwargs)
				else:
					wx.CallLater(delay, myFunctionEvaluated, *myFunctionArgs, **myFunctionKwargs)

			#Has args, but not kwargs
			elif (myFunctionArgs != None):
				if (after):
					wx.CallAfter(myFunctionEvaluated, *myFunctionArgs)
				else:
					wx.CallLater(delay, myFunctionEvaluated, *myFunctionArgs)

			#Has kwargs, but not args
			elif (myFunctionKwargs != None):
				if (after):
					wx.CallAfter(myFunctionEvaluated, **myFunctionKwargs)
				else:
					wx.CallLater(delay, myFunctionEvaluated, **myFunctionKwargs)

			#Has neither args nor kwargs
			else:
				if (after):
					wx.CallAfter(myFunctionEvaluated)
				else:
					wx.CallLater(delay, myFunctionEvaluated)

		#Skip empty functions
		if (myFunctionList != None):
			myFunctionList, myFunctionArgsList, myFunctionKwargsList = self.formatFunctionInputList(myFunctionList, myFunctionArgsList, myFunctionKwargsList)
			
			#Run each function
			for i, myFunction in enumerate(myFunctionList):
				#Skip empty functions
				if (myFunction != None):
					myFunctionEvaluated, myFunctionArgs, myFunctionKwargs = self.formatFunctionInput(i, myFunctionList, myFunctionArgsList, myFunctionKwargsList)
					runFunction(after, myFunctionEvaluated, myFunctionArgs, myFunctionKwargs)
		else:
			print("ERROR: myFunctionList == None for autoRun()")

	#Nesting Catalogue
	def getAddressValue(self, address):
		"""Returns the value of a given address for a dictionary of dictionaries.
		Special thanks to DomTomCat for how to get a value from a dictionary of dictionaries of n depth on https://stackoverflow.com/questions/14692690/access-nested-dictionary-items-via-a-list-of-keys
		
		address (list) - The path of keys to follow on the catalogue

		Example Input: getAddressValue(self.nestingAddress)
		Example Input: getAddressValue(self.nestingAddress + [self.(id)])
		"""
		global nestingCatalogue

		if ((not isinstance(address, list)) and (not isinstance(address, tuple))):
			address = [address]

		#Search through catalogue
		catalogue = nestingCatalogue
		for key in address: 
			catalogue = catalogue[key]

		return catalogue

	def setAddressValue(self, address, value):
		"""Returns the value of a given address for a dictionary of dictionaries.
		Special thanks to eafit for how to set a value of a dictionary of dictionaries of n depth on https://stackoverflow.com/questions/14692690/access-nested-dictionary-items-via-a-list-of-keys
		"""
		global nestingCatalogue

		if ((not isinstance(address, list)) and (not isinstance(address, tuple))):
			address = [address]

		catalogue = nestingCatalogue
		for key in address[:-1]:
			catalogue = catalogue.setdefault(key, {})
		catalogue[address[-1]] = value

	def getNested(self, include = [], exclude = [], includeUnnamed = True):
		"""Returns a list of handles of the immediate nested objects.

		include (list)        - Determiens what is returned
			- If None: Will return items regardless of type
			- If not None: Will return only the items requested
		exclude (list)        - Determiens what is not returned
			- If None: Will not exclude items from the return list
			- If not None: Will exclude any type of item in the list given from the return list
		includeUnnamed (bool) - Determiens if nested items without a label will also be returned
			- If True: Both labled and unlabled items will be returned
			- If False: Only labled items will be returned

		Example Input: getAddressValue()
		Example Input: getAddressValue(include = handle_Sizer)
		Example Input: getAddressValue(includeUnnamed = False)
		"""

		#Ensure correct format
		if (include == None):
			include = []
		elif ((not isinstance(include, list)) and (not isinstance(include, tuple))):
			include = [include]

		if (exclude == None):
			exclude = []
		elif ((not isinstance(exclude, list)) and (not isinstance(exclude, tuple))):
			exclude = [exclude]


		catalogue = self.getAddressValue(self.nestingAddress + [id(self)])

		nestedList = []
		for key, value in catalogue.items():
			if (key == None):
				continue

			if (len(include) != 0):
				for item in include:
					if (isinstance(value[None], item)):
						break
				else:
					continue

			if (len(exclude) != 0):
				for item in exclude:
					if (not isinstance(value[None], item)):
						break
				else:
					continue

			nestedList.append(value[None])

		if (includeUnnamed):
			for item in self.unnamedList:
				if (not item in include):
					continue

				if (item in exclude):
					continue

				nestedList.append(item)

		return nestedList

	def removeHandle(self, handle_remove, handle_source = None):
		"""Removes a handle from the nested containers in 'self'.
		The handle will not appear in self[:] after this.

		handle_source (object) - What to remove from
		handle_remove (object) - What to remove

		Example Input: removeHandle(myPopupMenu)
		Example Input: removeHandle(myPopupMenu, self.myWindow)
		"""

		if (handle_source == None):
			handle_source = self

		#Remove popup menu from nested catalogue
		for label, handle in {key: value for key, value in handle_source.labelCatalogue.items()}.items():
			if (handle == handle_remove):
				del handle_source.labelCatalogue[label]
				
				for i, item in enumerate(handle_source.labelCatalogueOrder):
					if (item == label):
						handle_source.labelCatalogueOrder.pop(i)
						break
				else:
					warnings.warn("Could not find {} in labelCatalogueOrder for {}".format(label, handle_source.__repr__()), Warning, stacklevel = 2)
				break
		else:
			for i, handle in enumerate(handle_source.unnamedList):
				if (handle == handle_remove):
					handle_source.unnamedList.pop(i)
					break
			else:
				warnings.warn(" Could not find {} in labelCatalogue or unnamedList for {}".format(handle_remove.__repr__(), handle_source.__repr__()), Warning, stacklevel = 2)

	#Settings
	def getItemMod(self, flags = None, stretchable = True, border = 5):
		"""Returns modable item attributes, stretchability, and border.

		flags (list) - Which flag to add to the sizer
			How the sizer item is aligned in its cell.
			"ac" (str) - Align the item to the center
			"av" (str) - Align the item to the vertical center only
			"ah" (str) - Align the item to the horizontal center only
			"at" (str) - Align the item to the top
			"ab" (str) - Align the item to the bottom
			"al" (str) - Align the item to the left
			"ar" (str) - Align the item to the right

			Which side(s) the border width applies to.
			"ba" (str) - Border the item on all sides
			"bt" (str) - Border the item to the top
			"bb" (str) - Border the item to the bottom
			"bl" (str) - Border the item to the left
			"br" (str) - Border the item to the right

			Whether the sizer item will expand or change shape.
			"ex" (str) - Item expands to fill as much space as it can
			"ea" (str) - Item expands, but maintain aspect ratio
			"fx" (str) - Item will not change size when the window is resized
			"fh" (str) - Item will still take up space, even if hidden

			These are some common combinations of flags.
			"c1" (str) - "ac", "ba", and "ex"
			"c2" (str) - "ba" and "ex"
			"c3" (str) - "ba" and "ea"
			"c4" (str) - "al", "bl", "br"

		stretchable (bool) - Whether or not the item will grow and shrink with respect to a parent sizer
		border (int)       - The width of the item's border

		Example Input: getItemMod("ac")
		Example Input: getItemMod("ac", border = 10)
		Example Input: getItemMod("c1")
		"""

		#Determine the flag types
		fixedFlags = ""
		if (flags != None):
			#Ensure that 'flags' is a list
			if (type(flags) != list):
				flags = [flags]

			#Evaluate each flag
			for flag in flags:
				flag = flag.lower()
				##Typical combinations
				if (flag[0] == "c"):
					#Align to center, Border all sides, expand to fill space
					if (flag[1] == "1"):
						if (fixedFlags != ""):
							fixedFlags += "|"
						fixedFlags += "wx.ALIGN_CENTER|wx.ALL|wx.EXPAND"

					#Border all sides, expand to fill space
					elif (flag[1] == "2"):
						if (fixedFlags != ""):
							fixedFlags += "|"
						fixedFlags += "wx.ALL|wx.EXPAND"

					#Border all sides, expand to fill space while maintaining aspect ratio
					elif (flag[1] == "3"):
						if (fixedFlags != ""):
							fixedFlags += "|"
						fixedFlags += "wx.ALL|wx.SHAPED"

					#Align to left, Border left and right side
					elif (flag[1] == "4"):
						if (fixedFlags != ""):
							fixedFlags += "|"
						fixedFlags += "wx.ALIGN_LEFT|wx.LEFT|wx.RIGHT"

					#Unknown Action
					else:
						errorMessage = "Unknown combination flag {}".format(flag)
						raise ValueError(errorMessage)

				##Align the Item
				elif (flag[0] == "a"):
					#Center 
					if (flag[1] == "c"):
						if (fixedFlags != ""):
							fixedFlags += "|"
						fixedFlags += "wx.ALIGN_CENTER"

					#Center Vertical
					elif (flag[1] == "v"):
						if (fixedFlags != ""):
							fixedFlags += "|"
						fixedFlags += "wx.ALIGN_CENTER_VERTICAL"

					#Center Horizontal
					elif (flag[1] == "h"):
						fixedFlags += "wx.ALIGN_CENTER_HORIZONTAL"
						
					#Top
					elif (flag[1] == "t"):
						if (fixedFlags != ""):
							fixedFlags += "|"
						fixedFlags += "wx.ALIGN_TOP"
						
					#Bottom
					elif (flag[1] == "b"):
						if (fixedFlags != ""):
							fixedFlags += "|"
						fixedFlags += "wx.ALIGN_BOTTOM"
						
					#Left
					elif (flag[1] == "l"):
						if (fixedFlags != ""):
							fixedFlags += "|"
						fixedFlags += "wx.ALIGN_LEFT"
						
					#Right
					elif (flag[1] == "r"):
						if (fixedFlags != ""):
							fixedFlags += "|"
						fixedFlags += "wx.ALIGN_RIGHT"

					#Unknown Action
					else:
						errorMessage = "Unknown alignment flag {}".format(flag)
						raise ValueError(errorMessage)

				##Border the Item
				elif (flag[0] == "b"):
					#All
					if (flag[1] == "a"):
						if (fixedFlags != ""):
							fixedFlags += "|"
						fixedFlags += "wx.ALL"
						
					#Top
					elif (flag[1] == "t"):
						if (fixedFlags != ""):
							fixedFlags += "|"
						fixedFlags += "wx.TOP"
						
					#Bottom
					elif (flag[1] == "b"):
						if (fixedFlags != ""):
							fixedFlags += "|"
						fixedFlags += "wx.BOTTOM"
						
					#Left
					elif (flag[1] == "l"):
						if (fixedFlags != ""):
							fixedFlags += "|"
						fixedFlags += "wx.LEFT"
						
					#Right
					elif (flag[1] == "r"):
						if (fixedFlags != ""):
							fixedFlags += "|"
						fixedFlags += "wx.RIGHT"

					#Unknown Action
					else:
						errorMessage = "Unknown border flag {}".format(flag)
						raise ValueError(errorMessage)

				##Expand the Item
				elif (flag[0] == "e"):
					#Expand
					if (flag[1] == "x"):
						if (fixedFlags != ""):
							fixedFlags += "|"
						fixedFlags += "wx.EXPAND"
						
					#Expand with Aspect Ratio
					elif (flag[1] == "a"):
						if (fixedFlags != ""):
							fixedFlags += "|"
						fixedFlags += "wx.SHAPED"

					#Unknown Action
					else:
						errorMessage = "Unknown expand flag {}".format(flag)
						raise ValueError(errorMessage)

				##Fixture the Item
				elif (flag[0] == "f"):
					#Fixed Size
					if (flag[1] == "x"):
						fixedFlags += "wx.FIXED_MINSIZE"
						
					#Fixed Space when hidden
					elif (flag[1] == "h"):
						fixedFlags += "wx.RESERVE_SPACE_EVEN_IF_HIDDEN"

					#Unknown Action
					else:
						errorMessage = "Unknown fixture flag {}".format(flag)
						raise ValueError(errorMessage)

				##Unknown Action
				else:
					errorMessage = "Unknown flag {}".format(flag)
					raise ValueError(errorMessage)
		else:
			fixedFlags = "0"

		#Determine stretchability
		if (stretchable):
			position = 1
		else:
			position = 0

		return fixedFlags, position, border

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
		if ((imagePath != None) and (imagePath != "")):
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
						errorMessage = "The icon {} cannot be found".format(imagePath)
						raise KeyError(errorMessage)
				else:
					try:
						image = wx.Bitmap(imagePath)
					except:
						image = wx.Image(imagePath, wx.BITMAP_TYPE_BMP).ConvertToBitmap()
		else:
			image = wx.NullBitmap

		return image

	#Converters
	def convertImageToBitmap(self, imgImage):
		"""Converts a wxImage image (wxPython) to a wxBitmap image (wxPython).
		Adapted from: https://wiki.wxpython.org/WorkingWithImages

		imgImage (object) - The wxBitmap image to convert

		Example Input: convertImageToBitmap(image)
		"""

		bmpImage = imgImage.ConvertToBitmap()
		return bmpImage

	def convertBitmapToImage(self, bmpImage):
		"""Converts a wxBitmap image (wxPython) to a wxImage image (wxPython).
		Adapted from: https://wiki.wxpython.org/WorkingWithImages

		bmpImage (object) - The wxBitmap image to convert

		Example Input: convertBitmapToImage(image)
		"""

		#Determine if a static bitmap was given
		classType = bmpImage.GetClassName()
		if (classType == "wxStaticBitmap"):
			bmpImage = bmpImage.GetBitmap()

		imgImage = bmpImage.ConvertToImage()
		return imgImage

	def convertImageToPil(self, imgImage):
		"""Converts a wxImage image (wxPython) to a PIL image (pillow).
		Adapted from: https://wiki.wxpython.org/WorkingWithImages

		imgImage (object) - The wxImage image to convert

		Example Input: convertImageToPil(image)
		"""

		pilImage = PIL.Image.new("RGB", (imgImage.GetWidth(), imgImage.GetHeight()))
		pilImage.fromstring(imgImage.GetData())
		return pilImage

	def convertBitmapToPil(self, bmpImage):
		"""Converts a wxBitmap image (wxPython) to a PIL image (pillow).
		Adapted from: https://wiki.wxpython.org/WorkingWithImages

		bmpImage (object) - The wxBitmap image to convert

		Example Input: convertBitmapToPil(image)
		"""

		imgImage = self.convertBitmapToImage(bmpImage)
		pilImage = self.convertImageToPil(imgImage)
		return pilImage

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

	#Etc
	def getArguments(self, argument_catalogue, desiredArgs):
		"""Returns a list of the values for the desired arguments from a dictionary.

		argument_catalogue (dict) - All locals() of the function
		desiredArgs (str)   - Determines what is returned. Can be a list of values

		Example Input: getArguments(argument_catalogue, desiredArgs = "handler")
		Example Input: getArguments(argument_catalogue, desiredArgs = ["handler", "flex", "flags"])
		"""

		#Ensure correct format
		if ((not isinstance(desiredArgs, list)) and (not isinstance(desiredArgs, tuple))):
			desiredArgs = [desiredArgs]

		argList = []
		for arg in desiredArgs:
			if (arg not in argument_catalogue):
				errorMessage = "Must provide the argument {} to {}".format(arg, self.__repr__())
				raise KeyError(errorMessage)

			argList.append(argument_catalogue[arg])

		#Ensure correct format
		if (len(argList) == 1):
			argList = argList[0]

		return argList

	def arrangeArguments(self, function, argList = [], kwargDict = {}, desiredArgs = None, notFound = {}):
		"""Returns a dictionary of the args and kwargs for a function.

		function (function) - The function to inspect
		argList (list)      - The *args of 'function'
		kwargDict (dict)    - The **kwargs of 'function'
		desiredArgs (str)   - Determines what is returned to the user. Can be a list of strings
			- If None: A dictionary of all args and kwargs will be returned
			- If not None: A dictionary of the provided args and kwargs will be returned if they exist
		notFound (dict)     - Allows the user to define what an argument should be if it is not in the function's argument list. {kwarg (str): default (any)}

		Example Input: arrangeArguments(myFunction, args, kwargs)
		Example Input: arrangeArguments(myFunction, args, kwargs, desiredArgs = "handler")
		Example Input: arrangeArguments(myFunction, args, kwargs, desiredArgs = "handler")
		Example Input: arrangeArguments(myFunction, args, kwargs, desiredArgs = ["handler", "flex", "flags"])
		Example Input: arrangeArguments(myFunction, args, kwargs, desiredArgs = ["handler", "flex", "flags"], notFound = {"flex": 0, "flags" = "c1"})
		"""

		#Ensure correct format
		if (desiredArgs != None):
			if ((not isinstance(desiredArgs, list)) and (not isinstance(desiredArgs, tuple))):
				desiredArgs = [desiredArgs]

		arguments = {}
		arg_indexList = []
		containsSelf = False
		for i, item in enumerate(inspect.signature(function).parameters.values()):
			#Skip inherited parameter 'self'
			if (item.name == "self"):
				containsSelf = True
				continue

			#Collect desired arguments
			if ((desiredArgs == None) or (item.name in desiredArgs)):
				if (i <= len(argList)):
					#Account for kwarg being passed in as an arg
					arguments[item.name] = argList[i - 1 * containsSelf]
				else:
					#Place defaults from function in catalogue
					arguments[item.name] = item.default

			#Track arg index positions
			if (item.default == item.empty):
				arg_indexList.append(item.name)

		#Account for returning all arguments
		if (desiredArgs == None):
			desiredArgs = [item.name for item in inspect.signature(function).parameters.values()]

		for item in desiredArgs:
			#Place kwargs in catalogue
			if (item in kwargDict):
				arguments[item] = kwargDict[item]

			#Account for requested arguments that were not found
			elif (item not in arguments):
				if (item in notFound):
					arguments[item] = notFound[item]

			elif (item in arg_indexList):
				i = arg_indexList.index(item)
				arguments[item] = argList[i]

		return arguments

	def checkHandleType(self, typeNeeded, function):
		#Ensure correct format
		if ((not isinstance(typeNeeded, list)) and (not isinstance(typeNeeded, tuple))):
			typeNeeded = [typeNeeded]

		#Error check
		if (self.type.lower() not in [str(item).lower() for item in typeNeeded]):
			errorMessage = "Cannot use type {} with the function {}".format(self.type, function.__name__)
			raise TypeError(errorMessage)

	def getArgument_event(self, arguments, args, kwargs):
		"""Returns the event for a function where the event could be in a given argument, args, or kwargs

		arguments (list) - What is not an arg or kwargs as an item in a list
		args (list)      - *args
		kwargs (dict)    - **kwargs

		Example Input: getArgument_event(label, args, kwargs)
		Example Input: getArgument_event([label, event], args, kwargs)
		"""
		#Ensure correct format
		if ((not isinstance(arguments, list)) and (not isinstance(arguments, tuple))):
			arguments = [arguments]

		#Search for event
		if ("event" in kwargs):
			event = kwargs["event"]
		else:
			for item in arguments:
				if (isinstance(item, wx.CommandEvent)):
					event = item
					break
			else:
				for item in args:
					if (isinstance(item, wx.CommandEvent)):
						event = item
						break
				else:
					event = None

		return event

	def getObjectWithEvent(self, event):
		"""Gets the object that triggered an event.

		event (CommandEvent) - The wxPython event that was triggered

		Example Input: getObjectWithEvent(event)
		"""

		thing = event.GetEventObject()

		return thing

	def getObjectParent(self, thing):
		"""Gets the parent of an object.

		thing (wxObject) - The object to find the parent of

		Example Input: getObjectParent(self)
		Example Input: getObjectParent(thing)
		"""

		#Check for special circumstances
		thingClass = thing.GetClassName()

		if ((thingClass == "wxMenu") or (thingClass == "wxMenuItem")):
			parent = self
		else:
			parent = thing.GetParent()

		#Check for notebook
		thingClass = parent.GetClassName()
		if (thingClass == "wxNotebook"):
			if (parent.GetParent() != None):
				parent = parent.GetParent()

				if (parent.GetParent() != None):
					parent = parent.GetParent()

		return parent

	def getScreenSize(self):
		"""Returns the screen resolution."""

		size = wx.GetDisplaySize()

		return size

	def getDpmm(self, mm = True):
		"""Convenience function."""

		dpmm = self.getDpi(mm)

		return dpmm

	def getDpi(self, mm = False):
		"""Returns the screen dpi to the user IF they have made the GUI dpi aware.

		mm (bool) - If True: Returns the dpi in dpmm instead

		Example Input: getDpi()
		Example Input: getDpi(mm = True)
		"""

		if (self.dpiAware):
			screen = wx.ScreenDC()
			dpi = screen.GetPPI()

			if (mm):
				dpi = dpi * 25.4

			return dpi
		else:
			return None

	def setDpiAware(self, awareness = True):
		"""Makes the program aware of the screen's true resolution.
		### To do: Allow the user to set the app dpi unaware ###

		awareness (bool) - If True: the program will be dpi aware
						   If False: the program will not be dpi aware

		Example Input: setDpiAware()
		Example Input: setDpiAware(False)
		"""

		self.dpiAware = awareness

		if (awareness):
			screen = wx.ScreenDC()
			# screen.GetSize()
			screen.GetPPI() #Doing this causes it to be dpi aware

	def getStringPixels(self, line):
		"""Returns the length of a string in pixels.

		line (str) - The string to measure

		Example Input: getStringPixels("Lorem Ipsum")
		"""

		#Get the current font
		font = self.GetFont()
		dc = wx.WindowDC(self)
		dc.SetFont(font)

		#Get font pixel size
		size = dc.GetTextExtent(line)
		del dc

		return size

	def getWindow(self, windowLabel = None):
		window = self.get(windowLabel, typeList = [handle_Window])
		return window

	def getTable(self, tableLabel = None):
		table = self.get(tableLabel, typeList = [handle_WidgetTable])
		return table

	def getCanvas(self, canvasLabel = None):
		canvas = self.get(canvasLabel, typeList = [handle_WidgetCanvas])
		return canvas

	def getSizer(self, sizerLabel = None):
		sizer = self.get(sizerLabel, typeList = [handle_Sizer])
		return sizer

	def getPopupMenu(self, popupMenuLabel = None):
		popupMenu = self.get(popupMenuLabel, typeList = [handle_MenuPopup])
		return popupMenu

class CommonEventFunctions():
	"""Contains common functions used for events bound to wxObjects.
	This is here for convenience in programming.
	_________________________________________________________________________

	HOW TO CREATE YOUR OWN FUNCTION
	These functions are a function within a function.
	This is so that *args and **kwargs can be passed to the function,
	and it is still able to be bound to a wxObject.

	The 'myFunction' must be a string if it is a non-user defined function. User-defined functions should not be a string.
	Function inputs are passed to the GUI object creator as kwargs. 
	The kwarg for the creator has the same name as the variable used to pass in the respective function;
	The args for the respective function have the phrase 'Args' after that variable name (example: myFunctionArgs);
	The kwargs for the respective function have the phrase 'Kwargs' after that variable name (example: myFunctionKwargs);
	Here are some example 'myFunction' variables that can be used when creating a new wxObject.
		myFunction = "onExit"
		myFunction = "onDebugShowFile", myFunctionArgs = "openFile"
		myFunction = myOwnUserDefinedFunction

	Here is a template for writing a function. Be sure to include the event argument!
	The args and kwargs are optional for if inputs are required.
	Replace things that are in ALL CAPS.
		def FUNCTIONNAME_nested(event, *args, *kwargs)
			INSERT DOCSTRING AND CODE HERE
	_________________________________________________________________________
	"""

	def __init__(self):     
		"""Defines the internal variables needed to run.

		Example Input: Meant to be inherited by GUI().
		"""

		pass

	#Windows
	# def onHide(self, event):
	# 	"""Hides the window. Default of a hide (h) menu item."""

	# 	self.Hide()
	# 	#There is no event.Skip() because if not, then the window will destroy itself

	# def onQuit(self, event):
	# 	"""Closes the window. Default of a close (c) menu item."""

	# 	self.Destroy()
	# 	event.Skip()

	def onExit(self, event):
		"""Closes all windows. Default of a quit (q) or exit (e) menu item."""

		# #Make sure sub threads are closed
		# if (threading.active_count() > 1):
		# 	for thread in threading.enumerate():
		# 		#Close the threads that are not the main thread
		# 		if (thread != threading.main_thread()):
		# 			thread.stop()

		#Exit the main thread
		sys.exit()
		event.Skip()

	def onMinimize(self, event):
		"""Minimizes the window. Default of a minimize (mi) menu item."""

		self.Iconize()
		event.Skip()

	def onMaximize(self, event):
		"""Maximizes the window. Default of a maximize (ma) menu item."""

		self.Maximize()
		event.Skip()

	#Etc
	def onDoNothing(self, event):
		"""Does nothing."""

		print("onDoNothing()")
		pass
		
		#There is no event.Skip() here to prevent the event from propigating forward

	def onIdle(self, event):
		"""Runs functions only while the GUI is idle. It will pause running the functions if the GUI becomes active.
		WARNING: This is not working yet.
		"""

		print("onIdle()")
		pass

#handles
class handle_Base(Utilities, CommonEventFunctions):
	"""The base handler for all GUI handlers.
	Meant to be inherited.
	"""

	def __init__(self):
		"""Initializes defaults."""

		#Initialize Inherited Classes
		Utilities.__init__(self)
		CommonEventFunctions.__init__(self)

		#Defaults
		self.type = None
		self.thing = None
		self.label = None
		self.parent = None
		self.nested = False
		self.nestingAddress = None
		self.allowBuildErrors = None

	def __repr__(self):
		representation = "{}(id = {})".format(type(self).__name__, id(self))
		return representation

	def __str__(self):
		"""Gives diagnostic information on the Widget when it is printed out."""

		output = "{}()\n-- id: {}\n".format(type(self).__name__, id(self))
		if (self.parent != None):
			output += "-- parent id: {}\n".format(id(self.parent))
		if (self.nestingAddress != None):
			output += "-- nesting address: {}\n".format(self.nestingAddress)
		if (self.label != None):
			output += "-- label: {}\n".format(self.label)
		if (self.type != None):
			output += "-- type: {}\n".format(self.type)
		if (self.thing != None):
			output += "-- wxObject: {}\n".format(type(self.thing).__name__)
		if (self.nested):
			output += "-- nested: True\n"
		return output

	def __enter__(self):
		"""Allows the user to use a with statement to build the GUI."""

		return self

	def __exit__(self, exc_type, exc_value, traceback):
		"""Allows the user to use a with statement to build the GUI."""

		#Error handling
		if (traceback != None):
			print(exc_type, exc_value)

			if (self.allowBuildErrors == None):
				return False
			elif (not self.allowBuildErrors):
				return True

	def getLabel(self, event = None):
		"""Returns the label for this object."""

		return self.label

class handle_Container_Base(handle_Base):
	"""The base handler for all GUI handlers.
	Meant to be inherited.
	"""

	def __init__(self):
		"""Initializes defaults."""

		#Initialize Inherited Classes
		handle_Base.__init__(self)

		#Defaults
		self.unnamedList = []
		self.labelCatalogue = {}
		self.labelCatalogueOrder = []

	def __add__(self, other):
		"""If two sizers are added together, then they are nested."""

		self.nest(other)

	def __len__(self):
		"""Returns the number of immediate nested elements.
		Does not include elements that those nested elements may have nested.
		"""

		catalogue = self.getAddressValue(self.nestingAddress + [id(self)])
		return len(catalogue) - 1

	def __iter__(self):
		"""Returns an iterator object that provides the nested objects."""
		
		nestedList = self.getNested()
		return Iterator(nestedList)

	def __getitem__(self, key):
		"""Allows the user to index the handle to get nested elements with labels."""

		return self.get(key)

	def __setitem__(self, key, value):
		"""Allows the user to index the handle to get nested elements with labels."""

		self.labelCatalogue[key] = value

	def __delitem__(self, key):
		"""Allows the user to index the handle to get nested elements with labels."""

		del self.labelCatalogue[key]

	def get(self, itemLabel = None, includeUnnamed = True, checkNested = True, typeList = None):
		"""Searches the label catalogue for the requested object.

		itemLabel (any) - What the object is labled as in the catalogue
			- If slice: objects will be returned from between the given spots 
			- If wxEvent: Will get the object that triggered the event
			- If None: Will return all that would be in an unbound slice

		Example Input: get()
		Example Input: get(0)
		Example Input: get(1.1)
		Example Input: get("text")
		Example Input: get(slice(None, None, None))
		Example Input: get(slice(2, "text", None))
		Example Input: get(event)
		"""

		def nestCheck(itemList, itemLabel):
			"""Makes sure everything is nested."""

			answer = None
			for item in itemList:
				#Skip Widgets
				if (not isinstance(item, handle_Widget_Base)):
					if (itemLabel == item.label):
						return item
					else:
						answer = nestCheck(item[:], itemLabel)
						if (answer != None):
							return answer
				else:
					if (isinstance(itemLabel, wx.Event)):
						if (itemLabel.GetEventObject() == item.thing):
							return item
					else:
						if (itemLabel == item.label):
							return item
			return answer

		def checkType(handleList):
			"""Makes sure only the instance typoes teh user wants are in the return list."""
			nonlocal typeList

			if ((handleList != None) and (typeList != None)):
				answer = []
				if ((not isinstance(handleList, list)) and (not isinstance(handleList, tuple))):
					handleList = [handleList]

				for item in handleList:
					if (isinstance(item, typeList)):
						answer.append(item)

				if (isinstance(answer, list) or isinstance(answer, tuple)):
					if (len(answer) == 0):
						answer = None
			else:
				answer = handleList
			return answer

		#Ensure correct format
		if (typeList != None):
			if ((not isinstance(typeList, list)) and (not isinstance(typeList, tuple))):
				typeList = (typeList)
			if (len(typeList) == 0):
				typeList = None
			elif (len(typeList) == 1):
				typeList = typeList[0]

		#Account for retrieving all nested
		if (itemLabel == None):
			itemLabel = slice(None, None, None)

		#Account for passing in a wxEvent
		if (isinstance(itemLabel, wx.Event)):
			answer = None
			for item in self[:]:
				if (itemLabel.GetEventObject() == item.thing):
					answer = item
					break
			else:
				if (checkNested):
					answer = nestCheck(self[:], itemLabel)
				else:
					answer = None

		#Account for indexing
		elif (isinstance(itemLabel, slice)):
			if (itemLabel.step != None):
				raise FutureWarning("Add slice steps to get() for indexing {}".format(self.__repr__()))
			
			elif ((itemLabel.start != None) and (itemLabel.start not in self.labelCatalogue)):
				errorMessage = "There is no item labled {} in the label catalogue for {}".format(itemLabel.start, self.__repr__())
				raise KeyError(errorMessage)
			
			elif ((itemLabel.stop != None) and (itemLabel.stop not in self.labelCatalogue)):
				errorMessage = "There is no item labled {} in the label catalogue for {}".format(itemLabel.stop, self.__repr__())
				raise KeyError(errorMessage)

			handleList = []
			begin = False
			for item in self.labelCatalogueOrder:
				#Allow for slicing with non-integers
				if ((not begin) and ((itemLabel.start == None) or (self.labelCatalogue[item].label == itemLabel.start))):
					begin = True
				elif ((itemLabel.stop != None) and (self.labelCatalogue[item].label == itemLabel.stop)):
					break

				#Slice catalogue via creation date
				if (begin):
					handleList.append(self.labelCatalogue[item])

			if (includeUnnamed):
				for item in self.unnamedList:
					handleList.append(item)

			answer = checkType(handleList)
			return handleList

		elif (itemLabel not in self.labelCatalogue):
			if (checkNested):
				answer = nestCheck(self[:], itemLabel)
				answer = checkType(answer)
			else:
				answer = None
		else:
			answer = checkType(self.labelCatalogue[itemLabel])
		
		if (answer != None):
			if (isinstance(answer, list) or isinstance(answer, tuple)):
				if (len(answer) == 1):
					answer = answer[0]

			return answer

		if (isinstance(itemLabel, wx.Event)):
			errorMessage = "There is no item associated with the event {} in the label catalogue for {}".format(itemLabel, self.__repr__())
		elif (typeList != None):
			if (isinstance(answer, list) or isinstance(answer, tuple)):
				errorMessage = "There is no item labled {} in the label catalogue for {} that is a {}".format(itemLabel, self.__repr__(), [item.__name__ for item in typeList])
			else:
				errorMessage = "There is no item labled {} in the label catalogue for {} that is a {}".format(itemLabel, self.__repr__(), typeList.__name__)
		else:
			errorMessage = "There is no item labled {} in the label catalogue for {}".format(itemLabel, self.__repr__())
		raise KeyError(errorMessage)

	def preBuild(self, argument_catalogue):
		"""Runs before this object is built."""

		#Unpack arguments
		label = argument_catalogue["label"]
		parent = argument_catalogue["parent"]
		buildSelf = argument_catalogue["self"]

		#Store data
		self.label = label

		#Add object to internal catalogue
		if (label != None):
			if (label in buildSelf.labelCatalogue):
				warnings.warn("Overwriting label association for {} in ".format(label), Warning, stacklevel = 2)

			buildSelf.labelCatalogue[self.label] = self
			buildSelf.labelCatalogueOrder.append(self.label)
		else:
			buildSelf.unnamedList.append(self)

		#Determine parent
		if (parent != None):
			self.parent = parent
		else:
			if (not isinstance(buildSelf, Controller)):
				if (buildSelf.parent != None):
					self.parent = buildSelf.parent
				else:
					if (buildSelf.mainPanel != None):
						self.parent = buildSelf.mainPanel
					else:
						self.parent = buildSelf

		#Determine Nesting Address
		self.nestingAddress = buildSelf.nestingAddress + [id(buildSelf)]
		buildSelf.setAddressValue(self.nestingAddress + [id(self)], {None: self})

		#Remember build error policy
		if (not isinstance(buildSelf, Controller)):
			buildSelf.allowBuildErrors = nestingCatalogue[buildSelf.nestingAddress[0]][None].allowBuildErrors
			self.allowBuildErrors = buildSelf.allowBuildErrors

	def postBuild(self, argument_catalogue):
		"""Runs after this object is built."""
		
		pass

	def overloadHelp(self, myFunction, label, kwargs):
		"""Helps the overloaded functions to stay small.

		Example Input: overloadHelp("toggleEnable")
		"""

		#Account for all nested
		if (label == None):
			for handle in self[:]:
				function = eval("handle.{}".format(myFunction))
				function(**kwargs)
		else:
			#Account for multiple objects
			if ((not isinstance(label, list)) and (not isinstance(label, tuple))):
				labelList = [label]
			else:
				labelList = label

			for label in labelList:
				handle = self.get(label, checkNested = True)
				function = eval("handle.{}".format(myFunction))
				function(**kwargs)

	#Change State
	##Enable / Disable
	def onToggleEnable(self, event, *args, **kwargs):
		"""A wx.CommandEvent version of toggleEnable."""

		self.toggleEnable(*args, event = event, **kwargs)
		event.Skip()

	def toggleEnable(self, label = None, **kwargs):
		"""Overload for toggleEnable in handle_Widget_Base."""

		self.overloadHelp("toggleEnable", label, kwargs)

	def onSetEnable(self, event, *args, **kwargs):
		"""A wx.CommandEvent version of setEnable."""

		self.setEnable(*args, event = event, **kwargs)
		event.Skip()

	def setEnable(self, label = None, **kwargs):
		"""Overload for setEnable in handle_Widget_Base."""

		self.overloadHelp("setEnable", label, kwargs)

	def onSetDisable(self, event, *args, **kwargs):
		"""A wx.CommandEvent version of setDisable."""

		self.setDisable(*args, event = event, **kwargs)
		event.Skip()

	def setDisable(self, label = None, **kwargs):
		"""Overload for setDisable in handle_Widget_Base."""

		self.overloadHelp("setDisable", label, kwargs)

	def onEnable(self, event, *args, **kwargs):
		"""A wx.CommandEvent version of enable."""

		self.enable(*args, event = event, **kwargs)
		event.Skip()

	def enable(self, label = None, **kwargs):
		"""Overload for enable in handle_Widget_Base."""

		self.overloadHelp("enable", label, kwargs)

	def onDisable(self, event, *args, **kwargs):
		"""A wx.CommandEvent version of disable."""

		self.disable(*args, event = event, **kwargs)
		event.Skip()

	def disable(self, label = None, **kwargs):
		"""Overload for disable in handle_Widget_Base."""

		self.overloadHelp("disable", label, kwargs)

	def onCheckEnabled(self, event, *args, **kwargs):
		"""A wx.CommandEvent version of checkEnabled."""

		self.checkEnabled(*args, event = event, **kwargs)
		event.Skip()

	def checkEnabled(self, label = None, **kwargs):
		"""Overload for checkEnabled in handle_Widget_Base."""

		self.overloadHelp("checkEnabled", label, kwargs)

	def onCheckDisabled(self, event, *args, **kwargs):
		"""A wx.CommandEvent version of checkDisabled."""

		self.checkDisabled(*args, event = event, **kwargs)
		event.Skip()

	def checkDisabled(self, label = None, **kwargs):
		"""Overload for checkDisabled in handle_Widget_Base."""

		self.overloadHelp("checkDisabled", label, kwargs)

	##Show / Hide
	def onToggleShow(self, event, *args, **kwargs):
		"""A wx.CommandEvent version of toggleShow."""

		self.toggleShow(*args, event = event, **kwargs)
		event.Skip()

	def toggleShow(self, label = None, **kwargs):
		"""Overload for toggleShow in handle_Widget_Base."""

		self.overloadHelp("toggleShow", label, kwargs)

	def onSetShow(self, event, *args, **kwargs):
		"""A wx.CommandEvent version of setShow."""

		self.setShow(*args, event = event, **kwargs)
		event.Skip()

	def setShow(self, label = None, **kwargs):
		"""Overload for setShow in handle_Widget_Base."""

		self.overloadHelp("setShow", label, kwargs)

	def onSetHide(self, event, *args, **kwargs):
		"""A wx.CommandEvent version of setHide."""

		self.setHide(*args, event = event, **kwargs)
		event.Skip()

	def setHide(self, label = None, **kwargs):
		"""Overload for setHide in handle_Widget_Base."""

		self.overloadHelp("setHide", label, kwargs)

	def onShow(self, event, *args, **kwargs):
		"""A wx.CommandEvent version of show."""

		self.show(*args, event = event, **kwargs)
		event.Skip()

	def show(self, label = None, **kwargs):
		"""Overload for show in handle_Widget_Base."""

		self.overloadHelp("show", label, kwargs)

	def onHide(self, event, *args, **kwargs):
		"""A wx.CommandEvent version of hide."""

		self.hide(*args, event = event, **kwargs)
		event.Skip()

	def hide(self, label = None, **kwargs):
		"""Overload for hide in handle_Widget_Base."""

		self.overloadHelp("hide", label, kwargs)

	def oncheckShown(self, event, *args, **kwargs):
		"""A wx.CommandEvent version of checkShown."""

		self.checkShown(*args, event = event, **kwargs)
		event.Skip()

	def checkShown(self, label = None, **kwargs):
		"""Overload for checkShown in handle_Widget_Base."""

		self.overloadHelp("checkShown", label, kwargs)

	def onCheckHidden(self, event, *args, **kwargs):
		"""A wx.CommandEvent version of checkHidden."""

		self.checkHidden(*args, event = event, **kwargs)
		event.Skip()

	def checkHidden(self, label = None, **kwargs):
		"""Overload for checkHidden in handle_Widget_Base."""

		self.overloadHelp("checkHidden", label, kwargs)

	##Modified
	def onModify(self, event, *args, **kwargs):
		"""A wx.CommandEvent version of modify."""

		self.modify(*args, event = event, **kwargs)
		event.Skip()

	def modify(self, label = None, **kwargs):
		"""Overload for modify in handle_Widget_Base."""

		self.overloadHelp("modify", label, kwargs)

	def onSetModified(self, event, *args, **kwargs):
		"""A wx.CommandEvent version of setModified."""

		self.setModified(*args, event = event, **kwargs)
		event.Skip()

	def setModified(self, label = None, **kwargs):
		"""Overload for setModified in handle_Widget_Base."""

		self.overloadHelp("setModified", label, kwargs)

	def onCheckModified(self, event, *args, **kwargs):
		"""A wx.CommandEvent version of checkModified."""

		self.checkModified(*args, event = event, **kwargs)
		event.Skip()

	def checkModified(self, label = None, **kwargs):
		"""Overload for checkModified in handle_Widget_Base."""

		self.overloadHelp("checkModified", label, kwargs)

	def onReadOnly(self, event, *args, **kwargs):
		"""A wx.CommandEvent version of readOnly."""

		self.readOnly(*args, event = event, **kwargs)
		event.Skip()

	def readOnly(self, label = None, **kwargs):
		"""Overload for readOnly in handle_Widget_Base."""

		self.overloadHelp("readOnly", label, kwargs)

	def onSetReadOnly(self, event, *args, **kwargs):
		"""A wx.CommandEvent version of setReadOnly."""

		self.setReadOnly(*args, event = event, **kwargs)
		event.Skip()

	def setReadOnly(self, label = None, **kwargs):
		"""Overload for setReadOnly in handle_Widget_Base."""

		self.overloadHelp("setReadOnly", label, kwargs)

class handle_Widget_Base(handle_Base):
	"""A handle for working with a wxWidget."""

	def __init__(self):
		"""Initializes defaults."""

		#Initialize inherited classes
		handle_Base.__init__(self)

	def __len__(self):
		"""Returns what the contextual length is for the object associated with this handle."""

		if (self.type == "ProgressBar"):
			value = self.thing.GetRange()

		else:
			warnings.warn("Add {} to __len__() for {}".format(self.type, self.__repr__()), Warning, stacklevel = 2)
			value = 0

		return value

	def __str__(self):
		"""Gives diagnostic information on the Widget when it is printed out."""

		output = handle_Base.__str__(self)
		
		if (self.nestingAddress != None):
			sizer = self.getAddressValue(self.nestingAddress)[None]
			output += "-- sizer id: {}\n".format(id(sizer))
		return output

	def preBuild(self, argument_catalogue):
		"""Runs before this object is built."""

		#Unpack arguments
		label, parent, buildSelf = self.getArguments(argument_catalogue, ["label", "parent", "self"])

		#Store data
		self.label = label
		self.sizer = buildSelf

		#Add object to internal catalogue
		if (label != None):
			if (label in buildSelf.labelCatalogue):
				warnings.warn("Overwriting label association for {} in ".format(label), Warning, stacklevel = 2)

			buildSelf.labelCatalogue[self.label] = self
			buildSelf.labelCatalogueOrder.append(self.label)
		else:
			buildSelf.unnamedList.append(self)

		#Determine parent
		if (parent != None):
			self.parent = parent
		else:
			if (not isinstance(buildSelf, Controller)):
				if (isinstance(buildSelf, handle_Menu)):
					self.parent = buildSelf
				else:
					if (buildSelf.parent != None):
						self.parent = buildSelf.parent
					else:
						if (buildSelf.mainPanel != None):
							self.parent = buildSelf.mainPanel
						else:
							self.parent = buildSelf

		#Determine Nesting Address
		self.nestingAddress = buildSelf.nestingAddress + [id(buildSelf)]
		buildSelf.setAddressValue(self.nestingAddress + [id(self)], {None: self})

		#Remember build error policy
		if (not isinstance(buildSelf, Controller)):
			buildSelf.allowBuildErrors = nestingCatalogue[buildSelf.nestingAddress[0]][None].allowBuildErrors
			self.allowBuildErrors = buildSelf.allowBuildErrors

	def postBuild(self, argument_catalogue):
		"""Runs after this object is built."""
		
		#Unpack arguments
		selected, hidden, flags, flex = self.getArguments(argument_catalogue, ["selected", "hidden", "flags", "flex"])

		#Determine if it is selected by default
		if (selected):
			self.thing.SetDefault()

		#Determine visibility
		if (hidden):
			if (isinstance(self, handle_Sizer)):
				self.addFinalFunction(self.thing.ShowItems, False)
			else:
				self.thing.Hide()
		
		#Add it to the sizer
		self.sizer.nest(self, flex = flex, flags = flags)

	#Getters
	def getValue(self, event = None):
		"""Returns what the contextual value is for the object associated with this handle."""

		if (self.type == "ProgressBar"):
			value = self.thing.GetValue() #(int) - Where the progress bar currently is

		else:
			warnings.warn("Add {} to getValue() for {}".format(self.type, self.__repr__()), Warning, stacklevel = 2)
			value = None

		return value

	def getIndex(self, event = None):
		"""Returns what the contextual index is for the object associated with this handle."""

		if (False):
			pass
		else:
			warnings.warn("Add {} to getIndex() for {}".format(self.type, self.__repr__()), Warning, stacklevel = 2)
			value = None

		return value

	def getAll(self, event = None):
		"""Returns all the contextual values for the object associated with this handle."""

		if (self.type == "ProgressBar"):
			value = self.thing.GetRange()

		else:
			warnings.warn("Add {} to getAll() for {}".format(self.type, self.__repr__()), Warning, stacklevel = 2)
			value = None

		return value

	#Setters
	def setReadOnly(self, state = True, event = None):
		"""Sets the contextual readOnly for the object associated with this handle to what the user supplies."""

		if (self.type == "Line"):
			pass
			
		else:
			warnings.warn("Add {} to setReadOnly() for {}".format(self.type, self.__repr__()), Warning, stacklevel = 2)

	#Change State
	##Enable / Disable
	def toggleEnable(self):
		"""Disables an item if it is enabled.
		Otherwise, it enables the item.

		Example Input: toggleEnable()
		"""
		
		#Make sure the object is disabled
		if (not self.thing.IsEnabled()):
			self.enable()
		else:
			self.disable()

	def setEnable(self, state = True):
		"""Enables or disables an item based on the given input.

		state (bool) - If it is enabled or not

		Example Input: setEnable()
		Example Input: setEnable(False)
		"""
		
		self.thing.Enable(state)

	def setDisable(self, state = True):
		"""Enables or disables an item based on the given input.

		state (bool) - If it is disabled or not

		Example Input: setDisable()
		Example Input: setDisable(False)
		"""
		
		self.setEnable(not state)

	def enable(self):
		"""Enables an item if it is disabled.
		Otherwise, it leaves it enabled.

		Example Input: enable()
		"""
		
		self.setEnable(True)

	def disable(self):
		"""Disables an item if it is enabled.
		Otherwise, it leaves it disabled.

		Example Input: disable()
		"""
		
		self.setEnable(False)

	def checkEnabled(self):
		"""Checks if an item is enabled.

		Example Input: checkEnabled()
		"""

		state = self.thing.IsEnabled()
		return state

	def checkDisabled(self):
		"""Checks if an item is disabled.

		Example Input: checkDisabled()
		"""

		state = not self.checkEnabled()
		return state

	##Show / Hide
	def toggleShow(self):
		"""Hides an item if it is shown.
		Otherwise, it shows the item.

		Example Input: toggleShow()
		"""

		#Make sure the object is disabled
		if (not self.thing.IsShown()):
			self.show()
		else:
			self.hide()

	def setShow(self, state = True):
		"""Shows or hides an item based on the given input.

		state (bool) - If it is shown or not

		Example Input: setShow()
		Example Input: setShow(False)
		"""

		self.thing.Show(state)

	def setHide(self, state = True):
		"""Shows or hides an item based on the given input.

		state (bool) - If it is hidden or not

		Example Input: setHide()
		Example Input: setHide(False)
		"""
		
		self.setShow(not state)

	def show(self, event = None):
		"""Shows an item if it is hidden.
		Otherwise, it leaves it shown.

		Example Input: show()
		"""
		
		self.setShow(True)

	def hide(self, event = None):
		"""Hides an item if it is shown.
		Otherwise, it leaves it hidden.

		Example Input: hide()
		"""
		
		self.setShow(False)

	def checkShown(self):
		"""Checks if an item is shown.

		Example Input: checkShown()
		"""

		state = self.thing.IsShown()
		return state

	def checkHidden(self):
		"""Checks if an item is hidden.

		Example Input: checkHidden()
		"""

		state = not self.checkShown()
		return state

	##Modified
	def modify(self):
		"""Marks an object as having been modified."""

		self.setModified(True)

	def setModified(self, state = True):
		"""Resets wether or not an object has been modified to True or False.

		state (bool) - If the object should be marked as modified or not

		Example Input: setModified(thing, False)
		"""

		#Set Modification
		self.thing.SetModified(state)

	def checkModified(self, resetOnCheck = True):
		"""Checks if an item has been modified by the user sense it was first created.

		resetOnCheck (bool) - If True: Will reset the modified value after checking it

		Example Input: checkModified()
		Example Input: checkModified(resetOnCheck = False)
		"""

		#Make sure the object is enabled
		state = self.thing.IsModified()

		if (resetOnCheck):
			self.setModified(False)

		return state

	#Change Settings
	def addToolTip(self, text = "", maxWidth = None, 
		delayAppear = None, delayDisappear = None, delayReappear = None,

		label = None, myId = -1, identity = None):
		"""Adds a small text box that will appear when the mouse hovers over a wxObject.

		triggerObjectLabel (str) - The id catalogue number for the object that triggers the tool tip
		text (str)               - What the text box will say
		label (str)            - What this is called in the idCatalogue
		maxWidth (int)           - How long the text box will be until it wraps the text to a new line.
								   If None: The wrap width will be automatically calculated
								   If -1: The text will not wrap
		
		delayAppear (int)    - Sets a delay in milliseconds for the tool tip to appear. If None, there will be no delay
		delayDisappear (int) - Sets a delay in milliseconds for the tool tip to disappear. If None, there will be no delay
		delayReappear (int)  - Sets a delay in milliseconds for the tool tip to appear again. If None, there will be no delay

		Example Input: addToolTip("Shows what will be sent to the printer.")
		"""

		if (text == None):
			text = ""
		else:
			if (not isinstance(text, str)):
				text = "{}".format(text)

		#Add the tool tip
		toolTip = wx.ToolTip(text)

		#Apply properties
		if (delayAppear != None):
			toolTip.SetDelay(delayAppear)

		if (delayDisappear != None):
			toolTip.SetAutoPop(delayDisappear)

		if (delayReappear != None):
			toolTip.SetReshow(delayReappear)

		if (maxWidth != None):
			toolTip.SetMaxWidth(maxWidth)

		#Attach the tool tip to the wxObject
		self.thing.SetToolTip(toolTip)

		#Catalogue tool tip
		if (label != None):
			self.catalogueToolTip(label, toolTip)

class handle_WidgetText(handle_Widget_Base):
	"""A handle for working with text widgets."""

	def __init__(self):
		"""Initializes defaults."""

		#Initialize inherited classes
		handle_Widget_Base.__init__(self)

	def __len__(self):
		"""Returns what the contextual length is for the object associated with this handle."""

		if (self.type == "Text"):
			value = len(self.getValue()) #(int) - How long the text is

		elif (self.type == "Hyperlink"):
			value = len(self.getValue()) #(int) - How long the url link is

		else:
			warnings.warn("Add {} to __len__() for {}".format(self.type, self.__repr__()), Warning, stacklevel = 2)
			value = 0

		return value

	#Getters
	def getValue(self, event = None):
		"""Returns what the contextual value is for the object associated with this handle."""

		if (self.type == "Text"):
			value = self.thing.GetLabel() #(str) - What the text says

		elif (self.type == "Hyperlink"):
			value = self.thing.GetURL() #(str) - What the link is

		else:
			warnings.warn("Add {} to getValue() for {}".format(self.type, self.__repr__()), Warning, stacklevel = 2)
			value = None

		return value

	#Setters
	def setValue(self, newValue, event = None):
		"""Sets the contextual value for the object associated with this handle to what the user supplies."""

		if (self.type == "Text"):
			if (not isinstance(newValue, str)):
				newValue = "{}".format(newValue)

			self.thing.SetLabel(newValue) #(str) - What the static text will now say

		elif (self.type == "Hyperlink"):
			if (not isinstance(newValue, str)):
				newValue = "{}".format(newValue)

			self.thing.SetURL(newValue) #(str) - What the hyperlink will now connect to

		else:
			warnings.warn("Add {} to setValue() for {}".format(self.type, self.__repr__()), Warning, stacklevel = 2)

	def setReadOnly(self, state = True):
		"""Sets the contextual readOnly for the object associated with this handle to what the user supplies."""

		if (self.type == "Text"):
			pass
			
		else:
			warnings.warn("Add {} to setReadOnly() for {}".format(self.type, self.__repr__()), Warning, stacklevel = 2)

	#Change Settings
	def wrapText(self, wrap = 1):
		"""Wraps the text to a specific point.

		wrap (int)      - How many pixels wide the line will be before it wraps. If negative: no wrapping is done

		Example Text: wrapText(250)
		"""

		if (wrap != None):
			self.thing.Wrap(wrap)

	#Create sub objects
	def makeFont(self, size = None, bold = False, italic = False, color = None, family = None):
		"""Returns a wxFont object.

		size (int)    - The font size of the text  
		bold (bool)   - Determines the boldness of the text
			- If True: The font will be bold
			- If False: The font will be normal
			- If None: The font will be light
		italic (bool) - Determines the italic state of the text
			- If True: The font will be italicized
			- If False: The font will not be italicized
			- If None: The font will be slanted
		color (str)   - The color of the text. Can be an RGB tuple (r, g, b) or hex value
			- If None: Will use black
		family (str)  - What font family it is.
			~ "times new roman"

		Example Input: makeFont()
		Example Input: makeFont(size = 72, bold = True, color = "red")
		"""

		#Configure the font object
		if (italic != None):
			if (italic):
				italic = wx.ITALIC
			else:
				italic = wx.NORMAL
		else:
			italic = wx.SLANT

		if (bold != None):
			if (bold):
				bold = wx.BOLD
			else:
				bold = wx.NORMAL
		else:
			bold = wx.LIGHT

		if (family == "TimesNewRoman"):
			family = wx.ROMAN
		else:
			family = wx.DEFAULT

		if (size == None):
			size = wx.DEFAULT

		font = wx.Font(size, family, italic, bold)

		return font

class handle_WidgetList(handle_Widget_Base):
	"""A handle for working with list widgets."""

	def __init__(self):
		"""Initializes defaults."""

		#Initialize inherited classes
		handle_Widget_Base.__init__(self)

		#Internal Variables
		self.myDropTarget = None
		self.dragable = False

		self.preDragFunction = None
		self.preDragFunctionArgs = None
		self.preDragFunctionKwargs = None

		self.postDragFunction = None
		self.postDragFunctionArgs = None
		self.postDragFunctionKwargs = None

	def __len__(self, returnRows = True):
		"""Returns what the contextual length is for the object associated with this handle.

		returnRows(bool) - Determines what is returned for 2D objects
			- If True: Returns how many rows the object has
			- If False: Returns how many columns the object has
		"""

		if (self.type == "ListDrop"):
			value = self.thing.GetCount() #(int) - How many items are in the drop list

		elif (self.type == "ListFull"):
			if (returnRows):
				value = self.thing.GetItemCount()
			else:
				value = self.thing.GetColumnCount()

		else:
			warnings.warn("Add {} to __len__() for {}".format(self.type, self.__repr__()), Warning, stacklevel = 2)
			value = 0

		return value

	#Getters
	def getValue(self, event = None):
		"""Returns what the contextual value is for the object associated with this handle."""

		if (self.type == "ListDrop"):
			index = self.thing.GetSelection()
			value = self.thing.GetString(index) #(str) - What is selected in the drop list

		elif (self.type == "ListFull"):
			value = []
			columnCount = self.thing.GetColumnCount()

			row = -1
			while True:
				row = self.thing.GetNextSelected(row)
				if row == -1:
					break
				else:
					subValue = []
					for column in range(columnCount):
						subValue.append(thing.GetItem(row, column).GetText()) #(list) - What is selected in the first column of the row selected in the full list as strings
					value.append(subValue)

		else:
			warnings.warn("Add {} to getValue() for {}".format(self.type, self.__repr__()), Warning, stacklevel = 2)
			value = None

		return value

	def getIndex(self, event = None):
		"""Returns what the contextual index is for the object associated with this handle."""

		if (self.type == "ListDrop"):
			value = self.thing.GetSelection() #(int) - The index number of what is selected in the drop list	

		elif (self.type == "ListFull"):
			value = []
			columnCount = self.thing.GetColumnCount()

			row = -1
			while True:
				row = self.thing.GetNextSelected(row)
				if row == -1:
					break
				else:
					subValue = []
					for column in range(columnCount):
							subValue.append(row) #(list) - The index number of the row of what is selected in the full list as integers
					value.append(subValue)

		else:
			warnings.warn("Add {} to getIndex() for {}".format(self.type, self.__repr__()), Warning, stacklevel = 2)
			value = None

		return value

	def getAll(self, event = None):
		"""Returns all the contextual values for the object associated with this handle."""

		if (self.type == "ListDrop"):
			value = []
			n = self.thing.GetCount()
			for i in range(n):
				value.append(self.thing.GetString(i)) #(list) - What is in the drop list as strings

		elif (self.type == "ListFull"):
			value = []
			rowCount = self.thing.GetItemCount()
			columnCount = self.thing.GetColumnCount()

			n = self.thing.GetItemCount()
			for row in range(rowCount):
				subValue = []
				for column in range(columnCount):
					subValue.append(self.thing.GetItem(row, column).GetText()) #(list) - What is in the full list as strings
				value.append(subValue)
	
		else:
			warnings.warn("Add {} to getAll() for {}".format(self.type, self.__repr__()), Warning, stacklevel = 2)
			value = None

		return value

	#Setters
	def setValue(self, newValue, filterNone = True, event = None):
		"""Sets the contextual value for the object associated with this handle to what the user supplies."""

		if (self.type == "ListDrop"):
			if (filterNone):
				if (None in newValue):
					newValue[:] = [value for value in newValue if value is not None] #Filter out None
				else:
					newValue[:] = [value if (value != None) else "" for value in newValue] #Replace None with blank space

			self.thing.SetItems(newValue) #(list) - What the choice options will now be now

		elif (self.type == "ListFull"):
			columnCount = self.thing.GetColumnCount()
			### TO DO: Fix this mess ###
			
			# if (columnCount != 0):
			# 	columns = columnCount
			# else:
			# 	#Error Check
			# 	if (columns == 1):
			# 		if ((isinstance(choices, list) or isinstance(choices, tuple)) and (len(choices) != 0)):
			# 			if ((not isinstance(choices[0], list)) and (not isinstance(choices[0], tuple))):
			# 				choices = [choices]

			# 	if (filterNone):
			# 		if (None in choices):
			# 			choices = [value for value in choices if value is not None] #Filter out None
			# 		else:
			# 			choices[:] = [value if (value != None) else "" for value in choices] #Replace None with blank space

			# #Preserve column names
			# if (columnNames != None):
			# 	if (columnNames == {}):
			# 		for i in range(self.thing.GetColumnCount()):
			# 			columnNames[i] = self.thing.GetColumn(i)

			# #Clear list
			# self.thing.ClearAll()

			# #Add items
			# if (self.thing.InReportView()):
			# 	#Error check
			# 	if (columnNames == None):
			# 		columnNames = {}

			# 	#Create columns
			# 	for i in range(columns):
			# 		if (i in columnNames):
			# 			name = columnNames[i]
			# 		else:
			# 			name = ""

			# 		self.thing.InsertColumn(i, name)

			# 	#Remember the column names
			# 	self.thing.columnNames = columnNames

			# 	#Add items
			# 	if (type(choices) != dict):
			# 		itemDict = {}
			# 		for row, column in enumerate(choices):
			# 			if (row not in itemDict):
			# 				itemDict[row] = []

			# 			itemDict[row].extend(column)
			# 	else:
			# 		itemDict = choices

			# 	#Make sure there are enough rows
			# 	itemCount = self.thing.GetItemCount()
			# 	rowCount = len(list(itemDict.keys()))

			# 	if (itemCount < rowCount):
			# 		for i in range(rowCount - itemCount):
			# 			self.thing.InsertItem(i + 1 + itemCount, "")

			# 	for row, column in itemDict.items():
			# 		# if (type(column) == str):
			# 		# 	#Get the column number
			# 		# 	index = [key for key, value in columnNames.items() if value == column]

			# 		# 	#Account for no column found
			# 		# 	if (len(index) == 0):
			# 		# 		print("ERROR: There is no column", column, "for the list", label, "in the column names", columnNames, "\nAdding value to the first column instead")
			# 		# 		column = 0
			# 		# 	else:
			# 		# 		#Choose the first instance of it
			# 		# 		column = index[0]

			# 		#Add contents
			# 		for i, text in enumerate(column):
			# 			#Error check
			# 			if (type(text) != str):
			# 				text = str(text)

			# 			self.thing.SetItem(row, i, text)

			# else:
			# 	#Add items
			# 	choices.reverse()
			# 	for text in choices:
			# 		#Error check
			# 		if (type(text) != str):
			# 			text = str(text)

			# 		self.thing.InsertItem(0, text)

		else:
			warnings.warn("Add {} to setValue() for {}".format(self.type, self.__repr__()), Warning, stacklevel = 2)

	def setSelection(self, newValue, event = None):
		"""Sets the contextual value for the object associated with this handle to what the user supplies."""

		if (self.type == "ListDrop"):
			if (isinstance(newValue, str)):
				newValue = self.thing.FindString(newValue)

			if (newValue == None):
				errorMessage = "Invalid drop list selection in setSelection() for {}".format(self.__repr__())
				raise ValueError(errorMessage)
				
			self.thing.SetSelection(newValue) #(int) - What the choice options will now be

		else:
			warnings.warn("Add {} to setSelection() for {}".format(self.type, self.__repr__()), Warning, stacklevel = 2)

	#Change Settings
	def setFunction_click(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type == "ListDrop"):
			self.betterBind(wx.EVT_CHOICE, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)

		elif (self.type == "ListFull"):
			self.betterBind(wx.EVT_LIST_ITEM_SELECTED, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		else:
			warnings.warn("Add {} to setFunction_click() for {}".format(self.type, self.__repr__()), Warning, stacklevel = 2)
			
	def setFunction_preEdit(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type == "ListFull"):
			self.betterBind(wx.EVT_LIST_BEGIN_LABEL_EDIT, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		else:
			warnings.warn("Add {} to EVT_LIST_BEGIN_LABEL_EDIT() for {}".format(self.type, self.__repr__()), Warning, stacklevel = 2)
			
	def setFunction_postEdit(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type == "ListFull"):
			self.betterBind(wx.EVT_LIST_END_LABEL_EDIT, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		else:
			warnings.warn("Add {} to setFunction_postEdit() for {}".format(self.type, self.__repr__()), Warning, stacklevel = 2)

	def setFunction_preDrag(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type == "ListFull"):
			if (not self.dragable):
				warnings.warn("'drag' was not enabled for {} upon creation".format(self.__repr__()), Warning, stacklevel = 2)
			else:
				self.preDragFunction = myFunction
				self.preDragFunctionArgs = myFunctionArgs
				self.preDragFunctionKwargs = myFunctionKwargs
		else:
			warnings.warn("Add {} to setFunction_preDrag() for {}".format(self.type, self.__repr__()), Warning, stacklevel = 2)
			
	def setFunction_postDrag(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type == "ListFull"):
			if (not self.dragable):
				warnings.warn("'drag' was not enabled for {} upon creation".format(self.__repr__()), Warning, stacklevel = 2)
			else:
				self.postDragFunction = myFunction
				self.postDragFunctionArgs = myFunctionArgs
				self.postDragFunctionKwargs = myFunctionKwargs
		else:
			warnings.warn("Add {} to setFunction_postDrag() for {}".format(self.type, self.__repr__()), Warning, stacklevel = 2)
			
	def setFunction_preDrop(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type == "ListFull"):
			if (self.myDropTarget == None):
				warnings.warn("'drop' was not enabled for {} upon creation".format(self.__repr__()), Warning, stacklevel = 2)
			else:
				self.myDropTarget.preDropFunction = myFunction
				self.myDropTarget.preDropFunctionArgs = myFunctionArgs
				self.myDropTarget.preDropFunctionKwargs = myFunctionKwargs
		else:
			warnings.warn("Add {} to setFunction_preDrop() for {}".format(self.type, self.__repr__()), Warning, stacklevel = 2)
			
	def setFunction_postDrop(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type == "ListFull"):
			if (self.myDropTarget == None):
				warnings.warn("'drop' was not enabled for {} upon creation".format(self.__repr__()), Warning, stacklevel = 2)
			else:
				self.myDropTarget.postDropFunction = myFunction
				self.myDropTarget.postDropFunctionArgs = myFunctionArgs
				self.myDropTarget.postDropFunctionKwargs = myFunctionKwargs
		else:
			warnings.warn("Add {} to setFunction_postDrop() for {}".format(self.type, self.__repr__()), Warning, stacklevel = 2)
			
	def setFunction_dragOver(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type == "ListFull"):
			if (self.myDropTarget == None):
				warnings.warn("'drop' was not enabled for {} upon creation".format(self.__repr__()), Warning, stacklevel = 2)
			else:
				self.myDropTarget.dragOverFunction = myFunction
				self.myDropTarget.dragOverFunctionArgs = myFunctionArgs
				self.myDropTarget.dragOverFunctionKwargs = myFunctionKwargs
		else:
			warnings.warn("Add {} to setFunction_dragOver() for {}".format(self.type, self.__repr__()), Warning, stacklevel = 2)

	def setReadOnly(self, state = True):
		"""Sets the contextual readOnly for the object associated with this handle to what the user supplies."""

		if (self.type == "ListDrop"):
			pass

		else:
			warnings.warn("Add {} to setReadOnly() for {}".format(self.type, self.__repr__()), Warning, stacklevel = 2)

	#Event functions
	def onDragList_beginDragAway(self, event, label = None,
		deleteOnDrop = True, overrideCopy = False, allowExternalAppDelete = True):
		"""Used to begin dragging an item away from a list.
		Modified code from: https://www.tutorialspoint.com/wxpython/wxpython_drag_and_drop.htm
		"""
		global dragDropDestination

		#Create the sub-function that runs the function
		def runFunction(myFunctionList, myFunctionArgsList, myFunctionKwargsList):
			"""This sub-function is needed to make the multiple functions work properly."""

			#Skip empty functions
			if (myFunctionList != None):
				myFunctionList, myFunctionArgsList, myFunctionKwargsList = self.formatFunctionInputList(myFunctionList, myFunctionArgsList, myFunctionKwargsList)
				
				#Run each function
				for i, myFunction in enumerate(myFunctionList):
					#Skip empty functions
					if (myFunction != None):
						myFunctionEvaluated, myFunctionArgs, myFunctionKwargs = self.formatFunctionInput(i, myFunctionList, myFunctionArgsList, myFunctionKwargsList)

						#Has both args and kwargs
						if ((myFunctionKwargs != None) and (myFunctionArgs != None)):
							myFunctionEvaluated(*myFunctionArgs, **myFunctionKwargs)

						#Has args, but not kwargs
						elif (myFunctionArgs != None):
							myFunctionEvaluated(*myFunctionArgs)

						#Has kwargs, but not args
						elif (myFunctionKwargs != None):
							myFunctionEvaluated(**myFunctionKwargs)

						#Has neither args nor kwargs
						else:
							myFunctionEvaluated()

		preDragFunction = copy.deepcopy(self.preDragFunction)
		preDragFunctionArgs = copy.deepcopy(self.preDragFunctionArgs)
		preDragFunctionKwargs = copy.deepcopy(self.preDragFunctionKwargs)

		postDragFunction = copy.deepcopy(self.postDragFunction)
		postDragFunctionArgs = copy.deepcopy(self.postDragFunctionArgs)
		postDragFunctionKwargs = copy.deepcopy(self.postDragFunctionKwargs)

		#Determine if a specific id should be set
		if (label != None):
			myId = self.newId(label)
			
		else:
			myId = self.newId()

		#Get Values
		index = event.GetIndex()
		originList = event.GetEventObject()
		textToDrag = originList.GetItemText(index)

		#Create drag objects
		textToDrag_object = wx.TextDataObject(textToDrag)
		originList_object = wx.DropSource(originList)

		#Catalogue dragObject
		self.addToId(textToDrag, label)

		#Run pre-functions
		runFunction(preDragFunction, preDragFunctionArgs, preDragFunctionKwargs)

		#Begin dragging item
		originList_object.SetData(textToDrag_object)
		dragResult = originList_object.DoDragDrop(True)

		#Remove the dragged item from the list
		if (deleteOnDrop):
			#Make sure the text sucessfully went somewhere
			if ((dragResult != wx.DragNone) and (dragResult != wx.DragError) and (dragResult != wx.DragCancel)):
				if ((dragResult != wx.DragCopy) or ((dragResult == wx.DragCopy) and (overrideCopy))):
					#Account for dropping it into a different application
					if (dragDropDestination != None):
						#Account for dropping it into the same thing it was dragged from
						if (originList == dragDropDestination[0]):
							if (dragDropDestination[1] < index):
								index += 1

						#Remove the object
						originList.DeleteItem(index)

					else:
						if (allowExternalAppDelete):
							#Remove the object
							originList.DeleteItem(index)
					

		#Remove dragObject from catalogue
		self.removeFromId(label)
		dragDropDestination = None

		#Run post-functions
		runFunction(postDragFunction, postDragFunctionArgs, postDragFunctionKwargs)

		event.Skip()

	# def onEditList_checkReadOnly(self, event, editable):
	# 	"""Used to make sure the user is allowed to edit the current item.
	# 	Special thanks to ErwinP for how to edit certain columns on https://stackoverflow.com/questions/12806542/wx-listctrl-with-texteditmixin-disable-editing-of-selected-cells
	# 	"""

	# 	#Get the current selection's column
	# 	thing = self.getObjectWithEvent(event)
	# 	column = self.thing.GetFocusedItem()

	# 	if (column not in editable):
	# 		event.Veto()
	# 	else:
	# 		if (not editable[column]):
	# 			event.Veto()
	# 		else:

	# 	event.Skip()

	class ListFull_Editable(wx.ListCtrl, wx.lib.mixins.listctrl.TextEditMixin):
		"""Allows a list control to have editable text."""

		def __init__(self, parent, myId = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.DefaultSize, style = "0"):
			"""Creates the editable list object"""

			#Load in modules
			wx.ListCtrl.__init__(self, parent, id = myId, pos = pos, size = size, style = eval(style))
			wx.lib.mixins.listctrl.TextEditMixin.__init__(self)

			#Fix class type
			self.__name__ = "wxListCtrl"

			#Internal variables
			self.editable = {}

		def OpenEditor(self, column, row):
			"""Overriden to make only some cells editable."""

			#Check for non-editable column
			if (type(self.editable) != dict):
				#All is editable
				if (not self.editable):
					return

			elif (column in self.editable):
				#Specific columns are editable
				if (not self.editable[column]):
					return

			else:
				#None is editable
				return

			#Run Function Normally
			event = wx.ListEvent(wx.wxEVT_COMMAND_LIST_BEGIN_LABEL_EDIT, self.GetId())
			event.SetEventObject(self) #Added this so the event has an associated object
			event.Index = row
			event.Column = column
			item = self.GetItem(row, column)
			event.Item.SetId(item.GetId())
			event.Item.SetColumn(item.GetColumn())
			event.Item.SetData(item.GetData())
			event.Item.SetText(item.GetText())
			ret = self.GetEventHandler().ProcessEvent(event)
			if ret and not event.IsAllowed():
				return   

			if self.GetColumn(column).Align != self.col_style:
				self.make_editor(self.GetColumn(column).Align)

			x0 = self.col_locs[column]
			x1 = self.col_locs[column+1] - x0

			scrolloffset = self.GetScrollPos(wx.HORIZONTAL)

			if x0+x1-scrolloffset > self.GetSize()[0]:
				if wx.Platform == "__WXMSW__":
					offset = x0+x1-self.GetSize()[0]-scrolloffset
					addoffset = self.GetSize()[0]/4
					if addoffset + scrolloffset < self.GetSize()[0]:
						offset += addoffset

					self.ScrollList(offset, 0)
					scrolloffset = self.GetScrollPos(wx.HORIZONTAL)
				else:
					self.editor.SetValue(self.GetItem(row, column).GetText())
					self.curRow = row
					self.curCol = column
					self.CloseEditor()
					return

			y0 = self.GetItemRect(row)[1]

			editor = self.editor
			editor.SetSize(x0-scrolloffset,y0, x1,-1)

			editor.SetValue(self.GetItem(row, column).GetText())
			editor.Show()
			editor.Raise()
			editor.SetSelection(-1,-1)
			editor.SetFocus()

			self.curRow = row
			self.curCol = column

		def CloseEditor(self, event = None):
			"""Overriden to fix deprication warnings."""

			if (not self.editor.IsShown()):
				return

			text = self.editor.GetValue()
			self.editor.Hide()
			self.SetFocus()

			event = wx.ListEvent(wx.wxEVT_COMMAND_LIST_END_LABEL_EDIT, self.GetId())
			event.SetEventObject(self) #Added this so the event has an associated object
			event.Index = self.curRow
			event.Column = self.curCol
			item = self.GetItem(self.curRow, self.curCol)
			item.SetText(text)
			event.SetItem(item)
			ret = self.GetEventHandler().ProcessEvent(event)

			if (not ret or event.IsAllowed()):
				if (self.IsVirtual()):
					self.SetVirtualData(self.curRow, self.curCol, text)
				else:
					self.SetItem(self.curRow, self.curCol, text) #Changed SetStringItem to SetItem
			self.RefreshItem(self.curRow)

	class DragTextDropTarget(wx.TextDropTarget):
		"""Used to set an object as a drop destination for text being dragged by the mouse.
		More info at: https://wxpython.org/Phoenix/docs/html/wx.DropTarget.html
		"""

		def __init__(self, parent, insertMode = 0,
			preDropFunction = None, preDropFunctionArgs = None, preDropFunctionKwargs = None, 
			postDropFunction = None, postDropFunctionArgs = None, postDropFunctionKwargs = None, 
			dragOverFunction = None, dragOverFunctionArgs = None, dragOverFunctionKwargs = None):
			"""Defines the internal variables needed to run.

			parent (wxObject) - The wx widget that will be recieve the dropped text.
			insertMode (int)  - Used to customize how the dropped text is added to the parent
			
			preDropFunction (str)       - The function that is ran when the user tries to drop something from the list; before it begins to drop
			preDropFunctionArgs (any)   - The arguments for 'preDropFunction'
			preDropFunctionKwargs (any) - The keyword arguments for 'preDropFunction'function
			
			postDropFunction (str)       - The function that is ran when the user tries to drop something from the list; after it drops
			postDropFunctionArgs (any)   - The arguments for 'postDropFunction'
			postDropFunctionKwargs (any) - The keyword arguments for 'postDropFunction'function
			
			dragOverFunction (str)       - The function that is ran when the user drags something over this object
			dragOverFunctionArgs (any)   - The arguments for 'dragOverFunction'
			dragOverFunctionKwargs (any) - The keyword arguments for 'dragOverFunction'function

			Example Input: DragTextDropTarget(thing)
			Example Input: DragTextDropTarget(thing, -1)
			"""

			wx.TextDropTarget.__init__(self)

			#Internal Variables
			self.parent = parent
			self.classType = self.parent.GetClassName()
			self.insertMode = insertMode

			self.preDropFunction = preDropFunction
			self.preDropFunctionArgs = preDropFunctionArgs
			self.preDropFunctionKwargs = preDropFunctionKwargs

			self.postDropFunction = postDropFunction
			self.postDropFunctionArgs = postDropFunctionArgs
			self.postDropFunctionKwargs = postDropFunctionKwargs

			self.dragOverFunction = dragOverFunction
			self.dragOverFunctionArgs = dragOverFunctionArgs
			self.dragOverFunctionKwargs = dragOverFunctionKwargs

		def runFunction(self, myFunctionList, myFunctionArgsList, myFunctionKwargsList):
			"""This function is needed to make the multiple functions work properly."""

			#Skip empty functions
			if (myFunctionList != None):
				myFunctionList, myFunctionArgsList, myFunctionKwargsList = Utilities.formatFunctionInputList(self, myFunctionList, myFunctionArgsList, myFunctionKwargsList)
				
				#Run each function
				for i, myFunction in enumerate(myFunctionList):
					#Skip empty functions
					if (myFunction != None):
						myFunctionEvaluated, myFunctionArgs, myFunctionKwargs = Utilities.formatFunctionInput(self, i, myFunctionList, myFunctionArgsList, myFunctionKwargsList)

						#Has both args and kwargs
						if ((myFunctionKwargs != None) and (myFunctionArgs != None)):
							myFunctionEvaluated(*myFunctionArgs, **myFunctionKwargs)

						#Has args, but not kwargs
						elif (myFunctionArgs != None):
							myFunctionEvaluated(*myFunctionArgs)

						#Has kwargs, but not args
						elif (myFunctionKwargs != None):
							myFunctionEvaluated(**myFunctionKwargs)

						#Has neither args nor kwargs
						else:
							myFunctionEvaluated()

		def OnDragOver(self, x, y, d):
			"""Overriden function. Needed to make this work."""
			
			self.runFunction(self.dragOverFunction, self.dragOverFunctionArgs, self.dragOverFunctionKwargs)

			return wx.DragCopy
			
		def OnDropText(self, x, y, data):
			"""Overriden function. Needed to make this work."""

			global dragDropDestination

			#Run pre-functions
			self.runFunction(self.preDropFunction, self.preDropFunctionArgs, self.preDropFunctionKwargs)

			#Determine how to handle recieving the text
			if (self.classType == "wxListCtrl"):
				itemCount = self.parent.GetItemCount()

				#Configure drop point
				if (self.insertMode != None):
					if (self.insertMode < 0):
						#Add from the end of the list
						index = itemCount + self.insertMode + 1
					else:
						#Add from the beginning of the list
						index = self.insertMode
				else:
					columnFound = None

					#Look at the position of each item in the list
					for i in range(itemCount):
						item_x, item_y, item_width, item_height = self.parent.GetItemRect(i)

						#Make sure it is looking at the correct column
						if (x - item_x - item_width < 0):
							#Account for dropping it at the bottom of a multi-column
							if (columnFound != None):
								if (columnFound != item_x):
									index = i
									break
							else:
								columnFound = item_x

							#Configure drop tollerance
							dropPositionTollerance = item_height / 2
							if (dropPositionTollerance < 0):
								dropPositionTollerance = 0

							#Determine where it should go based on mouse position
							if (item_y < y - dropPositionTollerance):
								continue
							else:
								index = i
								break

					else:
						index = itemCount

				dragDropDestination = [self.parent, index]

				#Add text to list
				self.parent.InsertItem(index, data) #Add the item to the top of the list

			else:
				print("Add", classType, "to OnDropText()")

			#Run post functions
			self.runFunction(self.postDropFunction, self.postDropFunctionArgs, self.postDropFunctionKwargs)

			return True

class handle_WidgetInput(handle_Widget_Base):
	"""A handle for working with input widgets."""

	def __init__(self):
		"""Initializes defaults."""

		#Initialize inherited classes
		handle_Widget_Base.__init__(self)

	def __len__(self, returnMax = True):
		"""Returns what the contextual length is for the object associated with this handle.

		returnMax(bool) - Determines what is returned for 2D objects
			- If True: Returns the max of the object range
			- If False: Returns the min of the object range
		"""

		if (self.type == "InputBox"):
			value = len(self.getValue())

		elif (self.type == "InputSpinner"):
			if (returnMax):
				value = self.thing.GetMax()
			else:
				value = self.thing.GetMin()

		elif (self.type == "Slider"):
			if (returnMax):
				value = self.thing.GetMax()
			else:
				value = self.thing.GetMin()

		elif (self.type == "InputSearch"):
			value = len(self.getValue())

		else:
			warnings.warn("Add {} to __len__() for {}".format(self.type, self.__repr__()), Warning, stacklevel = 2)
			value = 0

		return value

	#Getters
	def getValue(self, event = None):
		"""Returns what the contextual value is for the object associated with this handle."""

		if (self.type == "InputBox"):
			value = self.thing.GetValue() #(str) - What the text currently says

		elif (self.type == "InputSpinner"):
			value = self.thing.GetValue() #(str) - What is in the spin box

		elif (self.type == "Slider"):
			value = self.thing.GetValue() #(str) - What is in the spin box

		elif (self.type == "InputSearch"):
			value = self.thing.GetValue() #(str) - What is in the search box

		else:
			warnings.warn("Add {} to getValue() for {}".format(self.type, self.__repr__()), Warning, stacklevel = 2)
			value = None

		return value

	#Setters
	def setValue(self, newValue, event = None):
		"""Sets the contextual value for the object associated with this handle to what the user supplies."""

		if (self.type == "InputBox"):
			if (newValue == None):
				newValue = "" #Filter None as blank text
			self.thing.SetValue(newValue) #(str) - What will be shown in the text box

		elif (self.type == "InputSpinner"):
			self.thing.SetValue(newValue) #(int / float) - What will be shown in the input box

		elif (self.type == "Slider"):
			self.thing.SetValue(newValue) #(int / float) - Where the slider position will be

		elif (self.type == "InputSearch"):
			if (newValue == None):
				newValue = "" #Filter None as blank text
			self.thing.SetValue(newValue) #(str) - What will be shown in the search box

		else:
			warnings.warn("Add {} to setValue() for {}".format(self.type, self.__repr__()), Warning, stacklevel = 2)

	#Change Settings
	def setFunction_click(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type == "InputBox"):
			self.betterBind(wx.EVT_TEXT, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)

		elif (self.type == "InputSpinner"):
			self.betterBind(wx.EVT_SPINCTRL, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)	
		else:
			warnings.warn("Add {} to setFunction_click() for {}".format(self.type, self.__repr__()), Warning, stacklevel = 2)

	def setFunction_enter(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type == "InputBox"):
			self.keyBind("enter", self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		else:
			warnings.warn("Add {} to setFunction_enter() for {}".format(self.type, self.__repr__()), Warning, stacklevel = 2)

	def setFunction_preEdit(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type == "InputBox"):
			self.betterBind(wx.EVT_SET_FOCUS, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		else:
			warnings.warn("Add {} to setFunction_preEdit() for {}".format(self.type, self.__repr__()), Warning, stacklevel = 2)

	def setFunction_postEdit(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type == "InputBox"):
			self.betterBind(wx.EVT_KILL_FOCUS, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		else:
			warnings.warn("Add {} to setFunction_postEdit() for {}".format(self.type, self.__repr__()), Warning, stacklevel = 2)

	def setMin(self, newValue):
		"""Sets the contextual minimum for the object associated with this handle to what the user supplies."""

		if (self.type == "InputSpinner"):
			self.thing.SetMin(newValue) #(int / float) - What the min value will be for the the input box

		elif (self.type == "Slider"):
			self.thing.SetMin(newValue) #(int / float) - What the min slider position will be

		else:
			warnings.warn("Add {} to setMin() for {}".format(self.type, self.__repr__()), Warning, stacklevel = 2)

	def setMax(self, newValue):
		"""Sets the contextual maximum for the object associated with this handle to what the user supplies."""

		if (self.type == "InputSpinner"):
			self.thing.SetMax(newValue) #(int / float) - What the max value will be for the the input box

		elif (self.type == "Slider"):
			self.thing.SetMax(newValue) #(int / float) - What the max slider position will be

		else:
			warnings.warn("Add {} to setMax() for {}".format(self.type, self.__repr__()), Warning, stacklevel = 2)

	def setReadOnly(self, state = True):
		"""Sets the contextual readOnly for the object associated with this handle to what the user supplies."""

		if (self.type == "InputBox"):
			self.thing.SetEditable(not state)

		elif (self.type == "InputSpinner"):
			self.thing.Enable(not state)

		else:
			warnings.warn("Add {} to setReadOnly() for {}".format(self.type, self.__repr__()), Warning, stacklevel = 2)

class handle_WidgetButton(handle_Widget_Base):
	"""A handle for working with button widgets."""

	def __init__(self):
		"""Initializes defaults."""

		#Initialize inherited classes
		handle_Widget_Base.__init__(self)

	def __len__(self):
		"""Returns what the contextual length is for the object associated with this handle."""

		if (self.type == "ButtonCheck"):
			value = len(self.thing.GetLabel()) #(int) - The length of the text by the check box

		elif (self.type == "ButtonRadio"):
			value = len(self.thing.GetLabel()) #(int) - The length of the text by the radio button

		elif (self.type == "ButtonToggle"):
			value = len(self.thing.GetLabel()) #(int) - The length of the text in the toggle button

		elif (self.type == "ButtonRadioBox"):
			value = self.thing.GetCount() #(int) - How many items are in the check list

		elif (self.type == "CheckList"):
			value = self.thing.GetCount() #(int) - How many items are in the check list

		elif (self.type == "Button"):
			value = len(self.getValue()) #(int) - The length of the text in the button

		elif (self.type == "ButtonImage"):
			value = len(self.getValue()) #(int) - The length of the text in the image button

		else:
			warnings.warn("Add {} to __len__() for {}".format(self.type, self.__repr__()), Warning, stacklevel = 2)
			value = 0

		return value

	#Getters
	def getValue(self, event = None):
		"""Returns what the contextual value is for the object associated with this handle."""

		if (self.type == "ButtonCheck"):
			value = self.thing.GetValue() #(bool) - True: Checked; False: Un-Checked

		elif (self.type == "ButtonRadio"):
			value = self.thing.GetValue() #(bool) - True: Selected; False: Un-Selected

		elif (self.type == "ButtonToggle"):
			value = self.thing.GetValue() #(bool) - True: Selected; False: Un-Selected

		elif (self.type == "ButtonRadioBox"):
			index = self.thing.GetSelection()
			if (index != -1):
				value = self.thing.GetString(index) #(str) - What the selected item's text says
			else:
				value = None

		elif (self.type == "CheckList"):
			value = self.thing.GetCheckedStrings() #(list) - What is selected in the check list as strings

		elif (self.type == "Button"):
			value = self.thing.GetLabel() #(str) - What the button says

		elif (self.type == "ButtonImage"):
			value = self.thing.GetLabel() #(str) - What the button says

		else:
			warnings.warn("Add {} to getValue() for {}".format(self.type, self.__repr__()), Warning, stacklevel = 2)
			value = None

		return value

	def getIndex(self, event = None):
		"""Returns what the contextual index is for the object associated with this handle."""

		if (self.type == "ButtonRadioBox"):
			value = self.thing.GetSelection() #(int) - Which button is selected by index

		if (self.type == "CheckList"):
			value = self.thing.GetCheckedItems() #(list) - Which checkboxes are selected as integers

		else:
			warnings.warn("Add {} to getIndex() for {}".format(self.type, self.__repr__()), Warning, stacklevel = 2)
			value = None

		return value

	def getAll(self, event = None):
		"""Returns all the contextual values for the object associated with this handle."""

		if (self.type == "ButtonRadioBox"):
			value = []
			n = self.thing.GetCount()
			for i in range(n):
				value.append(thing.GetString(i)) #(list) - What is in the radio box as strings

		elif (self.type == "CheckList"):
			value = []
			n = self.thing.GetCount()
			for i in range(n):
				value.append(thing.GetString(i)) #(list) - What is in the full list as strings

		else:
			warnings.warn("Add {} to getAll() for {}".format(self.type, self.__repr__()), Warning, stacklevel = 2)
			value = None

		return value

	#Setters
	def setValue(self, newValue, event = None):
		"""Sets the contextual value for the object associated with this handle to what the user supplies."""

		if (self.type == "ButtonCheck"):
			self.thing.SetValue(bool(newValue)) #(bool) - True: checked; False: un-checked

		elif (self.type == "ButtonRadio"):
			self.thing.SetValue(bool(newValue)) #(bool) - True: selected; False: un-selected

		elif (self.type == "ButtonToggle"):
			self.thing.SetValue(bool(newValue)) #(bool) - True: selected; False: un-selected

		elif (self.type == "ButtonRadioBox"):
			if (isinstance(newValue, str)):
				if (not newValue.isdigit()):
					newValue = self.thing.FindString(newValue)

			if (newValue == None):
				errorMessage = "Invalid radio button selection in setValue() for {}".format(self.__repr__())
				raise ValueError(errorMessage)

			self.thing.SetSelection(int(newValue)) #(int / str) - Which radio button to select

		elif (self.type == "CheckList"):
			if (not isinstance(newValue, dict)):
				errorMessage = "Must give a dictionary of {which item (int): state (bool)}"# or {item label (str): state (bool)}"
				raise ValueError(errorMessage)

			for index, state in newValue.items():
				if (isinstance(index, str)):
					state = self.thing.FindString(index)
				
				self.thing.Check(index, state) #(bool) - True: selected; False: un-selected
		
		elif (self.type == "Button"):
			self.thing.SetLabel(newValue) #(str) - What the button will say on it

		elif (self.type == "ButtonImage"):
			self.thing.SetLabel(newValue) #(str) - What the button will say on it

		else:
			warnings.warn("Add {} to setValue() for {}".format(self.type, self.__repr__()), Warning, stacklevel = 2)

	#Change Settings
	def setFunction_click(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		"""Changes the function that runs when a menu item is selected."""
		
		if (self.type == "ButtonCheck"):
			self.betterBind(wx.EVT_CHECKBOX, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		
		elif (self.type == "ButtonRadio"):
			self.betterBind(wx.EVT_RADIOBUTTON, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)

		elif (self.type == "ButtonRadioBox"):
			self.betterBind(wx.EVT_RADIOBOX, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		
		elif (self.type == "Button"):
			self.betterBind(wx.EVT_BUTTON, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		else:
			warnings.warn("Add {} to setFunction_click() for {}".format(self.type, self.__repr__()), Warning, stacklevel = 2)

	def setReadOnly(self, state = True, event = None):
		"""Sets the contextual readOnly for the object associated with this handle to what the user supplies."""

		if (self.type == "ButtonCheck"):
			self.thing.SetReadOnly(state)

		else:
			warnings.warn("Add {} to setReadOnly() for {}".format(self.type, self.__repr__()), Warning, stacklevel = 2)

class handle_WidgetPicker(handle_Widget_Base):
	"""A handle for working with picker widgets."""

	def __init__(self):
		"""Initializes defaults."""

		#Initialize inherited classes
		handle_Widget_Base.__init__(self)

	def __len__(self):
		"""Returns what the contextual length is for the object associated with this handle."""

		if (self.type == "PickerFile"):
			value = len(self.getValue()) #(int) - How long the file path selected is

		elif (self.type == "PickerFileWindow"):
			value = len(self.getValue()) #(int) - How long the file path selected is

		else:
			warnings.warn("Add {} to __len__() for {}".format(self.type, self.__repr__()), Warning, stacklevel = 2)
			value = 0

		return value

	#Getters
	def getValue(self, event = None):
		"""Returns what the contextual value is for the object associated with this handle."""

		if (self.type == "PickerFile"):
			value = self.thing.GetPath() #(str) - What is in the attached file picker

		elif (self.type == "PickerFileWindow"):
			value = self.thing.GetPath() #(str) - What is in the attached file picker
		
		elif (self.type == "PickerDate"):
			value = self.thing.GetValue() #(str) - What date is selected in the date picker
			if (value != None):
				value = str(value.GetMonth()) + "/"+ str(value.GetDay()) + "/" + str(value.GetYear())

		elif (self.type == "PickerDateWindow"):
			value = self.thing.GetDate() #(str) - What date is selected in the date picker
			if (value != None):
				value = str(value.GetMonth()) + "/"+ str(value.GetDay()) + "/" + str(value.GetYear())

		elif (self.type == "PickerTime"):
			value = self.thing.GetTime() #(str) - What date is selected in the date picker
			if (value != None):
				value = str(value[0]) + ":"+ str(value[1]) + ":" + str(value[2])

		elif (self.type == "PickerColor"):
			value = self.thing.GetColour()

		elif (self.type == "PickerFont"):
			value = self.thing.GetSelectedFont()

		else:
			warnings.warn("Add {} to getValue() for {}".format(self.type, self.__repr__()), Warning, stacklevel = 2)
			value = None

		return value

	#Setters
	def setValue(self, newValue, event = None):
		"""Sets the contextual value for the object associated with this handle to what the user supplies."""

		if ((self.type == "PickerFile") or (self.type == "PickerFileWindow")):
			self.thing.SetPath(newValue) #(str) - What will be shown in the input box
		
		elif ((self.type == "PickerDate") or (self.type == "PickerDateWindow")):
			#Format value
			try:
				if (newValue != None):
					month, day, year = re.split("[\\\\/]", newValue) #Format: mm/dd/yyyy
					month, day, year = int(month), int(day), int(year)
					newValue = wx.DateTime(day, month, year)
				else:
					newValue = wx.DateTime().SetToCurrent()
			except:
				errorMessage = "Calandar dates must be formatted 'mm/dd/yy' for setValue() for {}".format(self.__repr__())
				raise SyntaxError(errorMessage)

			self.thing.SetValue(newValue) #(str) - What date will be selected as 'mm/dd/yyyy'

		elif (self.type == "PickerTime"):
			#Format value
			try:
				if (newValue != None):
					time = re.split(":", newValue) #Format: hour:minute:second
			
					if (len(time) == 2):
						hour, minute = time
						second = "0"

					elif (len(time) == 3):
						hour, minute, second = time

					else:
						errorMessage = "Time must be formatted 'hh:mm:ss' or 'hh:mm' for setValue() for {}".format(self.__repr__())
						raise SyntaxError(errorMessage)

				else:
					newValue = wx.DateTime().SetToCurrent()
					hour, minute, second = newValue.GetHour(), newValue.GetMinute(), newValue.GetSecond()

				hour, minute, second = int(hour), int(minute), int(second)
			except:
				errorMessage = "Time must be formatted 'hh:mm:ss' or 'hh:mm' for setValue() for {}".format(self.__repr__())
				raise SyntaxError(errorMessage)

			self.thing.SetTime(hour, minute, second) #(str) - What time will be selected as 'hour:minute:second'

		else:
			warnings.warn("Add {} to setValue() for {}".format(self.type, self.__repr__()), Warning, stacklevel = 2)


	#Change Settings
	def setFunction_click(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		"""Changes the function that runs when a menu item is selected."""
		
		if (self.type == "PickerFile"):
			if (self.thing.GetClassName() == "wxDirPickerCtrl"):
				self.betterBind(wx.EVT_DIRPICKER_CHANGED, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
			else:
				self.betterBind(wx.EVT_FILEPICKER_CHANGED, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		else:
			warnings.warn("Add {} to setFunction_click() for {}".format(self.type, self.__repr__()), Warning, stacklevel = 2)

class handle_WidgetImage(handle_Widget_Base):
	"""A handle for working with image widgets."""

	def __init__(self):
		"""Initializes defaults."""

		#Initialize inherited classes
		handle_Widget_Base.__init__(self)

	def __len__(self, returnRows = True):
		"""Returns what the contextual length is for the object associated with this handle.

		returnRows(bool) - Determines what is returned for 2D objects
			- If True: Returns how many rows the object has
			- If False: Returns how many columns the object has
		"""

		if (self.type == "Image"):
			image = self.getValue()
			if (returnRows):
				value = image.GetWidth()
			else:
				value = image.GetHeight()

		else:
			warnings.warn("Add {} to __len__() for {}".format(self.type, self.__repr__()), Warning, stacklevel = 2)
			value = 0

		return value

	#Getters
	def getValue(self, event = None):
		"""Returns what the contextual value is for the object associated with this handle."""

		if (self.type == "Image"):
			value = self.thing.GetBitmap() #(bitmap) - The image that is currently being shown

		else:
			warnings.warn("Add {} to getValue() for {}".format(self.type, self.__repr__()), Warning, stacklevel = 2)
			value = None

		return value

	#Setters
	def setValue(self, newValue, event = None):
		"""Sets the contextual value for the object associated with this handle to what the user supplies."""

		if (self.type == "Image"):
			image = self.getImage(newValue)
			self.thing.SetBitmap(image) #(wxBitmap) - What the image will be now

		else:
			warnings.warn("Add {} to setValue() for {}".format(self.type, self.__repr__()), Warning, stacklevel = 2)

class handle_Menu(handle_Container_Base):
	"""A handle for working with menus."""

	def __init__(self):
		"""Initializes defaults."""

		#Initialize inherited classes
		handle_Container_Base.__init__(self)

	def preBuild(self, argument_catalogue):
		"""Runs after this object is built."""

		handle_Container_Base.preBuild(self, argument_catalogue)
		
		#Unpack arguments
		buildSelf = self.getArguments(argument_catalogue, "self")
		detachable, text = self.getArguments(argument_catalogue, ["detachable", "text"])

		#Make sure there is a menu bar
		if ((not isinstance(buildSelf, handle_Menu)) and (not isinstance(buildSelf, handle_MenuPopup))):
			menuList = buildSelf.getNested(include = handle_Menu)
			if (len(menuList) <= 1):
				buildSelf.addMenuBar()

		#Create menu
		if (detachable):
			self.thing = wx.Menu(wx.MENU_TEAROFF)
		else:
			self.thing = wx.Menu()

		self.text = text

	def postBuild(self, argument_catalogue):
		"""Runs after this object is built."""

		handle_Container_Base.postBuild(self, argument_catalogue)
		
		#Unpack arguments
		buildSelf = argument_catalogue["self"]

		if (isinstance(buildSelf, handle_Window)):
			#Main Menu
			self.myWindow = buildSelf
			buildSelf.menuBar.Append(self.thing, self.text)

		elif (isinstance(buildSelf, handle_MenuPopup)):
			#Popup Menu
			self.myWindow = buildSelf.myWindow

		else:
			#Sub Menu
			self.myWindow = buildSelf.myWindow
			buildSelf.thing.Append(wx.ID_ANY, self.text, self.thing)

		self.nested = True

	def getValue(self, event = None):
		"""Returns what the contextual value is for the object associated with this handle."""

		if (self.type == "Menu"):
			if (event == None):
				errorMessage = "Pass the event parameter to getValue() when working with menu items"
				raise SyntaxError(errorMessage)
			
			index = event.GetId()
			value = self.thing.GetLabel(index)

		else:
			warnings.warn("Add {} to getValue() for {}".format(self.type, self.__repr__()), Warning, stacklevel = 2)
			value = None

		return value

	def addMenuItem(self, text = "", icon = None, internal = False, special = None, check = None, default = False, toolTip = "",

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, 

		label = None, hidden = False, enabled = True, parent = None, handle = None):
		"""Adds a menu item to a specific pre-existing menu.
		Note: More special IDs for future implementation can be found at: https://wiki.wxpython.org/SpecialIDs

		HOW TO GROUP RADIO BUTTONS
		The radio buttons will group with any radio buttons immediately before and after themselves.
		This means, that inorder to create two separate radio groups, you need to add a non-radio button item between them.
		This could be a normal item, a check box, or a separator.

		which (int)     - The label for the menu to add this to. Can be a string
		text (str)      - The label for the menu item. This is what is shown to the user
		icon (str)      - The file path to the icon for the menu item
			If None: No icon will be shown
		internal (bool) - If True: The icon provided is an internal icon, not an external file

		label (str) - What this is called in the idCatalogue
		special (str) - Declares if the item has a special pre-defined functionality. Overrides 'label'. Only the first letter matters
			"new"    - ?
			"open"   - ?
			"save"   - ?
			"hide"   - The current window is hidden
			"close"  - The current window is closed
			"quit"   - The program ends
			"exit"   - Does the same as 'quit'. This is here for convenience
			"status" - ?
			"tool"   - ?
			"undo"   - ?
			"redo"   - ?
		
		myFunction (str)       - The function that is ran when the item is clicked
		myFunctionArgs (any)   - The arguments for 'myFunction'
		myFunctionKwargs (any) - The keyword arguments for 'myFunction'function

		check (bool) - Determines the type of menu item it is
			~If None:  Normal menu item
			~If True:  Check box menu item
			~If False: Radio Button menu item

		default (bool) - Determines if the checkbox/radio button is intially checked/pressed
		enabled (bool) - If True: The user can interact with this
		toolTip (str)  - What the status bar will say if this is moused over

		Example Input: addMenuItem(0, "Lorem")
		Example Input: addMenuItem(0, icon = 'exit.bmp')
		Example Input: addMenuItem(2, "Print Preview", myFunction = [self.onPrintLabelsPreview, "self.onShowPopupWindow"], myFunctionArgs = [None, 0], label = "printPreview")
		"""

		handle = handle_MenuItem()
		handle.type = "MenuItem"
		
		# parent = self
		handle.preBuild(locals())

		#Determine if the id is special
		if (special != None):
			special = special.lower()
			if (special[0] == "n"):
				myId = wx.ID_NEW
			elif (special[0] == "o"):
				myId = wx.ID_OPEN
			elif (special[0] == "s"):
				myId = wx.ID_SAVE
			elif (special[0] == "c"):
				myId = wx.ID_EXIT
			elif (special[0] == "q" or special[0] == "e"):
				myId = wx.ID_CLOSE
			elif (special[0] == "u"):
				myId = wx.ID_UNDO
			elif (special[0] == "r"):
				myId = wx.ID_REDO
			else:
				myId = wx.ID_ANY
		else:
			myId = wx.ID_ANY

		#Create Menu Item
		if (check == None):
			handle.thing = wx.MenuItem(self.thing, myId, text)

			#Determine icon
			if (icon != None):
				image = self.getImage(icon, internal)
				image = self.convertBitmapToImage(image)
				image = image.Scale(16, 16, wx.IMAGE_QUALITY_HIGH)
				image = self.convertImageToBitmap(image)
				handle.thing.SetBitmap(image)
		else:
			if (check):
				handle.thing = wx.MenuItem(self.thing, myId, text, kind = wx.ITEM_CHECK)
			else:
				handle.thing = wx.MenuItem(self.thing, myId, text, kind = wx.ITEM_RADIO)

		#Add Menu Item
		self.thing.Append(handle.thing)
		handle.nested = True

		#Determine initial value
		if (check != None):
			if (default):
				handle.thing.Check(True)

		#Determine how to do the bound function
		if (myFunction == None):
			if (special != None):
				if (special[0] == "q" or special[0] == "e"):
					self.betterBind(wx.EVT_MENU, handle.thing, "self.onExit")
				elif (special[0] == "c"):
					self.betterBind(wx.EVT_MENU, handle.thing, "self.onQuit")
				elif (special[0] == "h"):
					self.betterBind(wx.EVT_MENU, handle.thing, "self.onHide")
				elif (special[0] == "s"):
					self.betterBind(wx.EVT_MENU, handle.thing, "self.onToggleStatusBar")
				elif (special[0] == "t"):
					self.betterBind(wx.EVT_MENU, handle.thing, "self.onToggleToolBar")
				else:
					errorMessage = "Unknown special function {} for {}".format(special, self.__repr__())
					raise KeyError(errorMessage)
		else:
			self.betterBind(wx.EVT_MENU, handle.thing, myFunction, myFunctionArgs, myFunctionKwargs)

		#Add help
		if (toolTip != None):
			#Ensure correct formatting
			if (not isinstance(toolTip, str)):
				toolTip = "{}".format(toolTip)

			#Do not add empty tool tips
			if (len(toolTip) != 0):
				handle.thing.SetHelp(toolTip)

		#Determine visibility
		if (hidden):
			if (isinstance(buildSelf, handle_Sizer)):
				buildSelf.addFinalFunction(buildSelf.thing.ShowItems, False)
			else:
				self.thing.Hide()

		handle.postBuild(locals())

		return handle

	def addMenuSeparator(self, 
		label = None, hidden = False, parent = None, handle = None):
		"""Adds a line to a specific pre-existing menu to separate menu items.

		Example Input: addMenuSeparator()
		"""

		handle = handle_MenuItem()
		handle.preBuild(locals())

		handle.thing = wx.MenuItem(self.thing, kind = wx.ITEM_SEPARATOR)
		self.thing.Append(handle.thing)
		handle.nested = True

		handle.postBuild(locals())

		return handle

	def addMenuSub(self, text = "", 
		label = None, hidden = False, parent = None, handle = None):
		"""Adds a sub menu to a specific pre-existing menu.
		To adding items to a sub menu is the same as for menus.

		text (str)  - The text for the menu item. This is what is shown to the user
		label (int) - The label for this menu

		Example Input: addMenuSub()
		Example Input: addMenuSub(text = "I&mport")
		"""

		handle = handle_Menu()
		detachable = False

		handle.preBuild(locals())
		handle.postBuild(locals())

		return handle

class handle_MenuItem(handle_Widget_Base):
	"""A handle for working with menu widgets."""

	def __init__(self):
		"""Initializes defaults."""

		#Initialize inherited classes
		handle_Widget_Base.__init__(self)

	def __len__(self):
		"""Returns what the contextual length is for the object associated with this handle."""

		if (self.type == "MenuItem"):
			value = len(self.thing.GetLabel()) #(int) - How long the text inside the menu item is

		else:
			warnings.warn("Add {} to __len__() for {}".format(self.type, self.__repr__()), Warning, stacklevel = 2)
			value = 0

		return value

	def postBuild(self, argument_catalogue):
		pass

	def getValue(self, event = None):
		"""Returns what the contextual value is for the object associated with this handle."""

		if (self.type == "MenuItem"):
			if (self.thing.IsCheckable()):
				value = self.thing.IsChecked() #(bool) - True: Selected; False: Un-Selected
			else:
				value = self.thing.GetText() #(str) - What the selected item says

		else:
			warnings.warn("Add {} to getValue() for {}".format(self.type, self.__repr__()), Warning, stacklevel = 2)
			value = None

		return value

	def getIndex(self, event = None):
		"""Returns what the contextual index is for the object associated with this handle."""

		if (self.type == "MenuItem"):
			if (event != None):
				value = event.GetId()
			else:
				errorMessage = "Pass the event parameter to getIndex() when working with menu items"
				raise SyntaxError(errorMessage)

		else:
			warnings.warn("Add {} to getIndex() for {}".format(self.type, self.__repr__()), Warning, stacklevel = 2)
			value = None

		return value

	#Change Settings
	def addToolTip(self, text = ""):
		"""Adds a small text box that will appear when the mouse hovers over a wxObject.
		For a wxMenuItem, the text will appear in the status bar.

		text (str)     - What the text box will say

		Example Input: addToolTip("Shows what will be sent to the printer")
		"""

		if (self.parent.myWindow.statusBar == None):
			warnings.warn("No status bar found for. Tool tips for menu items are displayed on a status bar".format(self.parent.myWindow.__repr__()), Warning, stacklevel = 2)

		if (text != None):
			#Ensure correct formatting
			if (not isinstance(text, str)):
				text = "{}".format(text)

			#Do not add empty tool tips
			if (len(text) != 0):
				self.thing.SetHelp(text)

	#Setters
	def setValue(self, newValue, event = None):
		"""Sets the contextual value for the object associated with this handle to what the user supplies."""

		if (self.type == "menuItem"):
			if ((self.thing.GetKind() == wx.ITEM_CHECK) or (self.thing.GetKind() == wx.ITEM_RADIO)):
				self.thing.Check(newValue) #(bool) - True: selected; False: un-selected
			else:
				errorMessage = "Only a menu 'Check Box' or 'Radio Button' can be set to a different value for setValue() for {}".format(self.__repr__())
				raise SyntaxError(errorMessage)

		else:
			warnings.warn("Add {} to setValue() for {}".format(self.type, self.__repr__()), Warning, stacklevel = 2)

	def setFunction_click(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		"""Changes the function that runs when a menu item is selected."""

		self.parent.betterBind(wx.EVT_MENU, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)

class handle_MenuPopup(handle_Container_Base):
	"""A handle for working with popup menus."""

	def __init__(self):
		"""Initializes defaults."""

		#Initialize inherited classes
		handle_Container_Base.__init__(self)

		#Internal variables
		self.contents = [] #Contains all menu item handles for this popup menu
		self.popupMenu = None

	def postBuild(self, argument_catalogue):
		"""Runs after this object is built."""

		handle_Container_Base.postBuild(self, argument_catalogue)

		#Unpack arguments
		buildSelf = argument_catalogue["self"]
		rightClick = argument_catalogue["rightClick"]

		preFunction = argument_catalogue["preFunction"]
		preFunctionArgs = argument_catalogue["preFunctionArgs"]
		preFunctionKwargs = argument_catalogue["preFunctionKwargs"]

		postFunction = argument_catalogue["postFunction"]
		postFunctionArgs = argument_catalogue["postFunctionArgs"]
		postFunctionKwargs = argument_catalogue["postFunctionKwargs"]

		#Bind functions
		if (rightClick != None):
			if (rightClick):
				self.betterBind(wx.EVT_RIGHT_DOWN, self.parent.thing, self.onTriggerPopupMenu, [[preFunction, preFunctionArgs, preFunctionKwargs], [postFunction, postFunctionArgs, postFunctionKwargs]])
			else:
				self.betterBind(wx.EVT_LEFT_DOWN, self.parent.thing, self.onTriggerPopupMenu, [[preFunction, preFunctionArgs, preFunctionKwargs], [postFunction, postFunctionArgs, postFunctionKwargs]])

		#Remember window handle
		if (isinstance(buildSelf, handle_Window)):
			#Main Menu
			self.myWindow = buildSelf
		else:
			#Sub Menu
			self.myWindow = buildSelf.myWindow

		self.nested = True #This is not nested. It is called by handle_MenuPopup.onTriggerPopupMenu() or handle_Window.onShow()

	def getValue(self, event = None):
		"""Returns what the contextual value is for the object associated with this handle."""

		print("@2", event)

		if (self.popupMenu != None):
			value = self.popupMenu.myMenu.getValue(event = event)
		else:
			warnings.warn("Popup Menu not shown for getValue() in {}".format(self.__repr__()), Warning, stacklevel = 2)
			value = None

		return value

	def getIndex(self, event = None):
		"""Returns what the contextual index is for the object associated with this handle."""

		if (self.popupMenu != None):
			value = self.popupMenu.myMenu.getIndex(event = event)
		else:
			warnings.warn("Popup Menu not shown for getIndex() in {}".format(self.__repr__()), Warning, stacklevel = 2)
			value = None

	#Setters
	def setValue(self, newValue, event = None):
		"""Sets the contextual value for the object associated with this handle to what the user supplies."""

		self.popupMenu.setValue(event = event)

	#Change Settings
	def show(self, event = None):
		"""Triggers the popup menu."""

		self.onTriggerPopupMenu(event)

	def clearPopupMenu(self):
		"""Clears the popup menu of all items.

		Example Input: clearPopupMenu()
		"""

		self.contents = []

	#Add Content
	def addMenuItem(self, text = "", icon = None, internal = False, special = None, 
		check = None, default = False, toolTip = "", 

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, 

		label = None, hidden = False, enabled = True, parent = None, handle = None):
		"""Adds an item to a catalogued popup menu.

		text (str)           - The label of the item. This is what is shown to the user
			- If None: The item will be an item separator instead of a selectable object
		label (str)        - The label for the popup menu item. Can be an integer
			- If None: Will not be labeled, which means it cannot be modified later
		enable (bool)        - If the row is clickable
		hidden (bool)        - If the row is hidden

		icon_filePath (str)  - The file path to the icon for the menu item
			- If None: No icon will be used
		icon_internal (bool) - If the icon provided is an internal icon, not an external file
		check_enable (bool)  - Determines if the row has a check box or radio button
			- If None:  Normal menu item
			- If True:  Check box menu item
			- If False: Radio Button menu item
		check_default (bool) - If this check box is checked already

		overwrite (bool)    - Determines how existing items with the same 'label' are handled
			- If True: It will overwrite existing menu items
			- If False: It will do nothing
			- If None: It will increment the label by 1 until it is unique.
				- If 'label' is a string: It will be in the form "_x", where 'x' is the incremented value
				- If 'label' is an int or float: It will be in the form 'x' as an int or float, where 'x' is the incremented value
		printWarnings(bool) - If warning messages should be printed
		printErrors (bool)  - If error messages should be printed

		myFunction (function) the function to run when pressed
		myFunctionArgs (list) args for 'myFunction'
		myFunctionKwargs (dict) kwargs for 'myFunction'
		special (str)   - Declares if the item has a special pre-defined functionality
			"new", "open", "save", "quit" or "exit", "status", "tool". Only the first letter matters
			- If 'myFunction' is defined, 'myFunction' will be ran before the special functionality happens

		Example Input: addItem(text = "Minimize", "myFunction" = "self.onMinimize")
		Example Input: addItem(text = "Hide", "myFunction" = myFrame.onHideWindow, myFunctionArgs = 0)
		Example Input: addItem(text = "Show Sdvanced Settings", label = "advancedSettings", myFunction = self.onShowAdvancedSettings, check = True)
		"""

		#Create the menu item
		handle = handle_MenuPopupItem()
		handle.type = "MenuPopupItem"
		handle.build(locals())

		self.contents.append(handle)
		handle.nested = True
		handle.myMenu = self

		return handle

	def addMenuSeparator(self, *args, **kwargs):
		"""Adds an separator line to the popup menu
		This must be done before it gets triggered.

		label (str)        - The label for the popup menu item. Can be an integer
			- If None: Will not be labeled, which means it cannot be modified later
		hidden (bool)        - If the row is hidden

		addPopupMenuSeparator()
		addPopupMenuSeparator(label = "menuSeparator", hidden = True)
		"""

		handle = self.addMenuItem(None, *args, **kwargs)
		return handle

	def addMenuSub(self, text = None, label = None, 
		parent = None, hidden = False, enabled = False, handle = None):
		"""Adds a sub menu to a specific pre-existing menu.
		To adding items to a sub menu is the same as for menus.

		text (str)  - The text for the menu item. This is what is shown to the user
		label (int) - The label for this menu

		Example Input: addMenuSub()
		Example Input: addMenuSub(text = "I&mport")
		"""
		
		#Setup
		rightClick = None
		preFunction = None
		preFunctionArgs = None
		preFunctionKwargs = None
		postFunction = None
		postFunctionArgs = None
		postFunctionKwargs = None

		#Build sub menu
		handle = handle_MenuPopup()
		handle.preBuild(locals())
		handle.postBuild(locals())

		#Remember sub menu details
		handle.text = text
		handle.label = label
		handle.hidden = hidden
		handle.enabled = enabled

		#Nest handle
		self.contents.append(handle)
		handle.nested = True
		handle.myMenu = self

		return handle

	def onTriggerPopupMenu(self, event, preFunction = [None, None, None], postFunction = [None, None, None]):
		"""The event that right-clicking triggers to pull up the popup menu."""

		#Account for grid events
		classType = event.GetClassName()
		if (classType == "wxGridEvent"):
			#Account for grid offset
			parent = event.GetEventObject()
			position = event.GetPosition() + parent.GetPosition()

			#Account for splitters and nested panels
			grandParent = parent.GetParent()
			while ((parent != grandParent) and (grandParent != None)):
				parent = grandParent
				grandParent = parent.GetParent()

				#Ignore root window position
				if (grandParent != None):
					position += parent.GetPosition()
		else:
			#Get position on screen
			position = event.GetPosition()

		#Skip empty popup lists
		if (len(self.contents) < 1):
			warnings.warn("Popup Menu {} for {} has no contents".format(self.__repr__(), self.myWindow.__repr__()), Warning, stacklevel = 2)
		else:
			#Create temporary popup menu
			self.popupMenu = self.MyPopupMenu(self, preFunction, postFunction)
			self.myWindow.thing.PopupMenu(self.popupMenu.thing, position)

			#Destroy the popup menu in memory
			for item in self[:]:
				if (isinstance(item, (handle_MenuPopupItem, handle_MenuPopupSubMenu, handle_Menu, handle_MenuItem))):
					self.removeHandle(item)
			self.popupMenu.thing.Destroy()
			self.popupMenu = None
			self.thing = None

		event.Skip()

	class MyPopupMenu():
		"""Creates a pop up menu.
		Because of the way that the popup menu is created, the items within must be
		determineed before the initial creation.

		Note: The runFunction is NOT an event function. It is a normal function.

		In order to allow for customization, the user creates a dictionary of
		{labels: functions}. This dictionary is then used to populate the menu.
		"""

		def __init__(self, parent, popupMenuLabel, preFunction = [None, None, None], postFunction = [None, None, None], idCatalogueLabel = None):
			"""Defines the internal variables needed to run.

			Example Input: MyPopupMenu(self)
			"""

			#Internal Variables
			self.parent = parent

			#Configure menu
			self.myMenu = self.addMenu()
			self.thing = self.myMenu.thing
			self.parent.thing = self.myMenu.thing

			#Run pre function(s)
			if (preFunction[0] != None):
				runFunctionList, runFunctionArgsList, runFunctionKwargsList = self.formatFunctionInputList(preFunction[0], preFunction[1], preFunction[2])
				#Run each function
				for i, runFunction in enumerate(runFunctionList):
					#Skip empty functions
					if (runFunction != None):
						runFunctionEvaluated, runFunctionArgs, runFunctionKwargs = self.formatFunctionInput(i, runFunctionList, runFunctionArgsList, runFunctionKwargsList)
						
						#Has both args and kwargs
						if ((runFunctionKwargs != None) and (runFunctionArgs != None)):
							runFunctionEvaluated(*runFunctionArgs, **runFunctionKwargs)

						#Has args, but not kwargs
						elif (runFunctionArgs != None):
							runFunctionEvaluated(*runFunctionArgs)

						#Has kwargs, but not args
						elif (runFunctionKwargs != None):
							runFunctionEvaluated(**runFunctionKwargs)

						#Has neither args nor kwargs
						else:
							runFunctionEvaluated()

			#Create Menu
			self.populateMenu(self.myMenu, self.parent.contents)

			#Run post function(s)
			if (postFunction[0] != None):
				runFunctionList, runFunctionArgsList, runFunctionKwargsList = self.parent.formatFunctionInputList(postFunction[0], postFunction[1], postFunction[2])
				#Run each function
				for i, runFunction in enumerate(runFunctionList):
					#Skip empty functions
					if (runFunction != None):
						runFunctionEvaluated, runFunctionArgs, runFunctionKwargs = self.parent.formatFunctionInput(i, runFunctionList, runFunctionArgsList, runFunctionKwargsList)
						
						#Has both args and kwargs
						if ((runFunctionKwargs != None) and (runFunctionArgs != None)):
							runFunctionEvaluated(*runFunctionArgs, **runFunctionKwargs)

						#Has args, but not kwargs
						elif (runFunctionArgs != None):
							runFunctionEvaluated(*runFunctionArgs)

						#Has kwargs, but not args
						elif (runFunctionKwargs != None):
							runFunctionEvaluated(**runFunctionKwargs)

						#Has neither args nor kwargs
						else:
							runFunctionEvaluated()

		def addMenu(self, label = None, text = " ", detachable = False,
			parent = None, hidden = False, enabled = False, handle = None):
			"""Adds a menu to a pre-existing menubar.
			This is a collapsable array of menu items.

			text (str)        - What the menu is called
				If you add a '&', a keyboard shortcut will be made for the letter after it
			label (str)     - What this is called in the idCatalogue
			detachable (bool) - If True: The menu can be undocked

			Example Input: addMenu(0, "&File")
			Example Input: addMenu("first", "&File")
			"""

			handle = handle_Menu()
			handle.type = "Menu"
			kwargs = locals()
			kwargs["self"] = self.parent

			handle.preBuild(kwargs)
			handle.postBuild(kwargs)
			return handle

		def populateMenu(self, menu, contents):
			"""Uses a dictionary to populate the menu with items and bound events."""

			#Create the menu
			if (len(contents) != 0):
				for i, handle in enumerate(contents):
					if (isinstance(handle, handle_MenuPopup)):
						subMenu = menu.addMenuSub(text = handle.text, label = handle.label, hidden = handle.hidden)
						self.populateMenu(subMenu, handle.contents)

					elif (handle.text != None):
						menu.addMenuItem(text = handle.text, icon = handle.icon, internal = handle.internal, special = None, check = handle.check, default = handle.default,
							myFunction = handle.myFunction, myFunctionArgs = handle.myFunctionArgs, myFunctionKwargs = handle.myFunctionKwargs, 
							label = handle.label, hidden = handle.hidden, enabled = handle.enabled)
					else:
						menu.addMenuSeparator(label = handle.label, hidden = handle.hidden)

class handle_MenuPopupItem(handle_Widget_Base):
	"""A handle for working with menu widgets."""

	def __init__(self):
		"""Initializes defaults."""

		#Initialize inherited classes
		handle_Widget_Base.__init__(self)

		#Defaults
		self.myMenu = None
		self.text = None
		self.icon = None
		self.internal = None
		self.myFunction = None
		self.myFunctionArgs = None
		self.myFunctionKwargs = None
		self.check = None
		self.default = None
		self.enabled = None
		self.hidden = None

	def build(self, argument_catalogue):
		self.preBuild(argument_catalogue)

		text = self.getArguments(argument_catalogue, "text")

		#Check for separator
		if (text != None):
			enabled, hidden = self.getArguments(argument_catalogue, ["enabled", "hidden"])

			myFunction, myFunctionArgs, myFunctionKwargs, = self.getArguments(argument_catalogue, ["myFunction", "myFunctionArgs", "myFunctionKwargs"])
			icon, internal = self.getArguments(argument_catalogue, ["icon", "internal"])
			check, default, = self.getArguments(argument_catalogue, ["check", "default"])

			#Prepare menu item
			if (myFunction == None):
				special = self.getArguments(argument_catalogue, "special")
				if (special != None):
					#Ensure correct format
					if ((special != None) and (not isinstance(special, str))):
						errorMessage = "'special' should be a string for addMenuItem() for {}".format(buildSelf.__repr__())
						raise ValueError(errorMessage)

					special = special.lower()
					if (special[0:2] == "mi"):
						myFunction = [myFunction, "self.onMinimize"]
						myFunctionArgs = [myFunctionArgs, None]
						myFunctionKwargs = [myFunctionKwargs, None]
					
					elif (special[0:2] == "ma"):
						myFunction = [myFunction, "self.onMaximize"]
						myFunctionArgs = [myFunctionArgs, None]
						myFunctionKwargs = [myFunctionKwargs, None]

			#Create menu item
			self.myFunction = myFunction
			self.myFunctionArgs = myFunctionArgs
			self.myFunctionKwargs = myFunctionKwargs

			self.icon = icon
			self.internal = internal
			self.check = check
			self.default = default

			#Create menu item
			self.text = text
			self.enabled = enabled
			self.hidden = hidden

class handle_MenuPopupSubMenu(handle_MenuPopup):
	"""A handle for working with menu widgets."""

	def __init__(self):
		"""Initializes defaults."""

		#Initialize inherited classes
		handle_MenuPopup.__init__(self)

		#Defaults
		self.myMenu = None
		self.text = None
		self.enabled = None
		self.hidden = None

class handle_WidgetCanvas(handle_Widget_Base):
	"""A handle for working with canvas widgets."""

	def __init__(self):
		"""Initializes defaults."""

		#Initialize inherited classes
		handle_Widget_Base.__init__(self)

		#Defaults
		self.paint_count = 0
		self.drawQueue = [] #What will be drawn on the window. Items are drawn from left to right in their list order. [function, args, kwargs]

	def readBuildInstructions_panel(self, parent, instructions):
		"""Interprets instructions given by the user for what panel to make and how to make it."""

		if (not isinstance(instructions, dict)):
			errorMessage = "panel must be a dictionary for {}".format(self.__repr__())
			raise ValueError(errorMessage)

		#Overwrite default with user given data
		kwargs = {item.name: item.default for item in inspect.signature(handle_Window.addPanel).parameters.values()}
		for key, value in instructions.items():
			kwargs[key] = value

		#Create Handler
		panel = handle_Panel()

		#Finish building panel
		kwargs["self"] = parent
		panel.build(kwargs)

		return panel

	def onPaint(self, event):
		"""Needed so that the GUI can draw on the panel."""

		#All that is needed here is to draw the buffer to screen
		dc = wx.BufferedPaintDC(self.thing, self._Buffer)

		event.Skip()

	def onSize(self, event):
		"""Needed so that the GUI can draw on the panel."""
		
		#Make sure the buffer is always the same size as the Window
		Size  = self.parent.parent.thing.ClientSize
		self._Buffer = wx.Bitmap(*Size)
		self.update()

		if (event != None):
			event.Skip()

	def save(self, fileName, fileType = wx.BITMAP_TYPE_PNG):
		"""Save the contents of the buffer to the specified file.

		Example Input: save("example.png")
		"""

		self._Buffer.SaveFile(fileName, fileType)

	def update(self):
		"""This is called if the drawing needs to change.

		Example Input: update()
		"""

		#Create dc
		dc = wx.MemoryDC()
		dc.SelectObject(self._Buffer)

		#Draw on canvas
		self.draw(dc)

		#Update canvas
		del dc #Get rid of the MemoryDC before Update() is called.
		self.parent.thing.Refresh()
		self.parent.thing.Update()

	def queue(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		"""Queues a drawing function for the canvas.

		Example Input: queue(drawRectangle, [5, 5, 25, 25])
		"""

		#Do not queue empty functions
		if (myFunction != None):
			self.drawQueue.append([myFunction, myFunctionArgs, myFunctionKwargs])

	def new(self):
		"""Empties the draw queue and clears the canvas.

		Example Input: new()
		"""

		#Clear queue
		self.drawQueue = []

		#Create dc
		dc = wx.MemoryDC()
		dc.SelectObject(self._Buffer)
		
		#Clear canvas
		brush = wx.Brush("White")
		dc.SetBackground(brush)
		dc.Clear()

		#Update canvas
		del dc #Get rid of the MemoryDC before Update() is called.
		self.parent.thing.Refresh()
		self.parent.thing.Update()

	def draw(self, dc):
		"""Draws the queued shapes.

		Example Input: draw(dc)
		"""

		#Clear canvas
		brush = wx.Brush("White")
		dc.SetBackground(brush)
		dc.Clear()

		#Draw items in queue
		for item in self.drawQueue:
			#Unpack variables
			myFunction = eval(item[0])
			myFunctionArgs = item[1]
			myFunctionKwargs = item[2]

			#Ensure args and kwargs are formatted correctly
			myFunction, myFunctionArgs, myFunctionKwargs = self.parent.formatFunctionInput(0, [myFunction], [myFunctionArgs], [myFunctionKwargs])

			if (type(myFunctionArgs) == tuple):
				myFunctionArgs = list(myFunctionArgs)
			elif (type(myFunctionArgs) != list):
				myFunctionArgs = [myFunctionArgs]

			#Run function
			##Has args and kwargs
			if ((myFunctionArgs != None) and (myFunctionKwargs != None)):
				myFunction(*myFunctionArgs, **myFunctionKwargs)

			##Has only args
			elif (myFunctionArgs != None):
				myFunction(*myFunctionArgs)

			##Has only kwargs
			elif (myFunctionArgs != None):
				myFunction(**myFunctionKwargs)

	#Drawing Functions
	def getPen(self, color, width = 1):
		"""Returns a pen or list of pens to the user.
		Pens are used to draw shape outlines.

		color (tuple) - (R, G, B) as integers
					  - If a list of tuples is given: A brush for each color will be created
		width (int)   - How thick the pen will be

		Example Input: getPen((255, 0, 0))
		Example Input: getPen((255, 0, 0), 3)
		Example Input: getPen([(255, 0, 0), (0, 255, 0)])
		"""

		#Account for brush lists
		multiple = False
		if ((type(color[0]) == tuple) or (type(color[0]) == list)):
			multiple = True

		#Create a brush list
		if (multiple):
			penList = []
			for i, item in enumerate(color):
				#Determine color
				if (multiple):
					color = wx.Colour(color[0], color[1], color[2])
				else:
					color = wx.Colour(color[i][0], color[i][1], color[i][2])

				pen = wx.Pen(color, int(width))
				penList.append(pen)
			pen = penList

		#Create a single pen
		else:
			color = wx.Colour(color[0], color[1], color[2])
			pen = wx.Pen(color, int(width))

		return pen

	def getBrush(self, color, style = "solid", image = None, internal = False):
		"""Returns a pen or list of pens to the user.
		Brushes are used to fill shapes

		color (tuple)  - (R, G, B) as integers
						 If None: The fill will be transparent (no fill)
					   - If a list of tuples is given: A brush for each color will be created
		style (str)    - If not None: The fill style
					   - If a list is given: A brush for each style will be created
		image (str)    - If 'style' has "image" in it: This is the image that is used for the bitmap. Can be a PIL image
		internal (str) - If True and 'style' has "image" in it: 'image' is an iternal image

		Example Input: getBrush((255, 0, 0))
		Example Input: getBrush([(255, 0, 0), (0, 255, 0)])
		Example Input: getBrush((255, 0, 0), style = "hatchCross)
		Example Input: getBrush([(255, 0, 0), (0, 255, 0)], ["hatchCross", "solid"])
		Example Input: getBrush(None)
		Example Input: getBrush([(255, 0, 0), None])
		"""

		#Account for void color
		if (color == None):
			color = wx.Colour(0, 0, 0)
			style, image = self.getBrushStyle("transparent", None)
			brush = wx.Brush(color, style)

		else:
			#Account for brush lists
			multiple = [False, False]
			if ((type(color) == tuple) or (type(color) == list)):
				if ((type(color[0]) == tuple) or (type(color[0]) == list)):
					multiple[0] = True

			if ((type(style) == tuple) or (type(style) == list)):
				multiple[1] = True

			#Create a brush list
			if (multiple[0] or multiple[1]):
				brushList = []
				for i, item in enumerate(color):
					#Determine color
					if (multiple[0]):
						#Account for void color
						if (color[i] != None):
							color = wx.Colour(color[i][0], color[i][1], color[i][2])
						else:
							color = wx.Colour(0, 0, 0)
					else:
						#Account for void color
						if (color != None):
							color = wx.Colour(color[0], color[1], color[2])
						else:
							color = wx.Colour(0, 0, 0)

					#Determine style
					if (multiple[1]):
						#Account for void color
						if (color[i] != None):
							style, image = self.getBrushStyle(style[i], image)
						else:
							style, image = self.getBrushStyle("transparent", None)
					else:
						#Account for void color
						if (color != None):
							style, image = self.getBrushStyle(style, image)
						else:
							style, image = self.getBrushStyle("transparent", None)

					#Create bruh
					brush = wx.Brush(color, style)

					#Bind image if an image style was used
					if (image != None):
						brush.SetStipple(image)

					#Remember the brush
					brushList.append(brush)
				brush = brushList

			#Create a single brush
			else:
				#Account for void color
				if (color != None):
					#Create brush
					color = wx.Colour(color[0], color[1], color[2])
					style, image = self.getBrushStyle(style, image)
				else:
					color = wx.Colour(0, 0, 0)
					style, image = self.getBrushStyle("transparent", None)
				brush = wx.Brush(color, style)

				#Bind image if an image style was used
				if (image != None):
					brush.SetStipple(image)

		return brush

	def getBrushStyle(self, style, image = None, internal = False):
		"""Returns a brush style to the user.

		style (str) - What style the shape fill will be. Only some of the letters are needed. The styles are:
			'solid'       - Solid. Needed: "s"
			'transparent' - Transparent (no fill). Needed: "t"

			'image'                - Uses a bitmap as a stipple. Needed: "i"
			'imageMask'            - Uses a bitmap as a stipple; a mask is used for masking areas in the stipple bitmap. Needed: "im"
			'imageMaskTransparent' - Uses a bitmap as a stipple; a mask is used for blitting monochrome using text foreground and background colors. Needed: "it"

			'hatchHorizontal'   - Horizontal hatch. Needed: "hh"
			'hatchVertical'     - Vertical hatch. Needed: "hv"
			'hatchCross'        - Cross hatch. Needed: "h"
			'hatchDiagForward'  - Forward diagonal hatch. Needed: "hdf" or "hfd"
			'hatchDiagBackward' - Backward diagonal hatch. Needed: "hdb" or "hbd"
			'hatchDiagCross'    - Cross-diagonal hatch. Needed: "hd"

		image (str)    - If 'style' has "image" in it: This is the image that is used for the bitmap. Can be a PIL image
		internal (str) - If True and 'style' has "image" in it: 'image' is an iternal image

		Example Input: getBrushStyle("solid")
		Example Input: getBrushStyle("image", image)
		Example Input: getBrushStyle("image", "example.bmp")
		Example Input: getBrushStyle("image", "error", True)
		"""

		#Ensure lower case
		if (style != None):
			style = style.lower()

		#Normal
		if (style == None):
			style = wx.BRUSHSTYLE_SOLID
			image = None

		elif (style[0] == "s"):
			style = wx.BRUSHSTYLE_SOLID
			image = None

		elif (style[0] == "t"):
			style = wx.BRUSHSTYLE_TRANSPARENT
			image = None

		#Bitmap
		elif (style[0] == "i"):
			#Make sure an image was given
			if (image != None):
				#Ensure correct image format
				image = self.getImage(imagePath, internal)

				#Determine style
				if ("t" in style):
					style = wx.BRUSHSTYLE_STIPPLE_MASK_OPAQUE

				elif ("m" in style):
					style = wx.BRUSHSTYLE_STIPPLE_MASK

				else:
					style = wx.BRUSHSTYLE_STIPPLE
			else:
				print("ERROR: Must supply an image path in getBrushStyle() to use the style", style)
				style = wx.BRUSHSTYLE_TRANSPARENT

		#Hatch
		elif (style[0] == "h"):
			#Diagonal
			if ("d" in style):
				if ("f" in style):
					style = wx.BRUSHSTYLE_FDIAGONAL_HATCH

				elif ('b' in style):
					style = wx.BRUSHSTYLE_BDIAGONAL_HATCH

				else:
					style = wx.BRUSHSTYLE_CROSSDIAG_HATCH
			else:
				if ("h" in style[1:]):
					style = wx.BRUSHSTYLE_HORIZONTAL_HATCH

				elif ('v' in style):
					style = wx.BRUSHSTYLE_VERTICAL_HATCH

				else:
					style = wx.BRUSHSTYLE_CROSS_HATCH
			image = None

		else:
			print("ERROR: Unknown style", style, "in getBrushStyle()")
			style = wx.BRUSHSTYLE_TRANSPARENT
			image = None

		return style, image

	def setThickness(self, thickness):
		"""Sets the pen thickness."""

		thicknesses = [1, 2, 3, 4, 6, 8, 12, 16, 24, 32, 48, 64, 72, 96, 128]
		# self.currentThickness = self.thicknesses[0] 

	def setFill(self, fill):
		"""Sets the brush style."""

		#https://wxpython.org/Phoenix/docs/html/wx.BrushStyle.enumeration.html#wx-brushstyle
		pass

	def setColor(self, color):
		"""Sets the brush and pen color."""

		colours = ["Black", "Yellow", "Red", "Green", "Blue", 
				   "Purple", "Brown", "Aquamarine", "Forest Green", 
				   "Light Blue", "Goldenrod", "Cyan", "Orange", 
				   "Navy", "Dark Grey", "Light Grey", "White"]

		# self.SetBackgroundColour('WHITE')
		# self.currentColour = self.colours[0]

	def drawUpdate(self):
		"""Updates the canvas."""

		self.update()

	def drawNew(self):
		"""Clears the canvas."""

		self.new()

	def drawSave(self, imagePath = "savedImage"):
		"""Saves the canvas to an external folder."""

		self.save(imagePath)

	def drawZoom(self, x, y = None):
		"""Zooms the image in or out.

		x (int) - The x-axis scaling factor
				  If None: The scale will be set to 1:1
		y (int) - The y-axis scaling factor
				  If None: Will be the same as x

		Example Input: drawZoom(0, 2)
		Example Input: drawZoom(0, 2.5, 3)
		Example Input: drawZoom(0, None)
		"""

		#Scale the canvas
		if (x != None):
			if (y != None):
				self.thing.SetUserScale(x, y)
			else:
				self.thing.SetUserScale(x, x)

		else:
			self.thing.SetUserScale(1, 1)

	def drawSetOrigin(self, x, y = None):
		"""Changes the origin of the canvas after scaling has been applied.

		x (int) - The x-axis origin point using the current origin's coordinates
		y (int) - The y-axis origin point using the current origin's coordinates
				  If None: Will be the same as x

		Example Input: drawZoom(0, 2)
		Example Input: drawZoom(0, 2.5, 3)
		"""

		#Skip empty origins
		if (x != None):
			#Move the origin
			if (y != None):
				self.thing.SetDeviceOrigin(x, y)
			else:
				self.thing.SetDeviceOrigin(x, x)
			
	def drawImage(self, imagePath, x, y, internal = True, alpha = False):
		"""Draws an image on the canvas.
		

		imagePath (str) - The pathway to the image
		x (int)         - The x-coordinate of the image on the canvas
		y (int)         - The y-coordinate of the image on the canvas

		Example Input: drawImage(0, "python.jpg", 10, 10)
		"""

		#Skip blank images
		if (imagePath != None):
			#Get correct image
			image = self.getImage(imagePath, internal, alpha = alpha)

			#Draw the image
			self.queue("dc.DrawBitmap", [image, x, y, alpha])

	def drawText(self, text, x, y, size = 12, angle = None, color = (0, 0, 0), bold = False):
		"""Draws text on the canvas.
		### To Do: Add font family, italix, and bold args ###

		text (str)    - The text that will be drawn on the canvas
					  - If a list of lists is given: Is a list containing text to draw
						Note: This is the fastest way to draw many non-rotated lines
		
		x (int)       - The x-coordinate of the text on the canvas
					  - If a list of lists is given and 'text' is a list: Is a list containing the x-coordinates of the text correcponding to that index
		
		y (int)       - The y-coordinate of the text on the canvas
					  - If a list of lists is given and 'text' is a list: Is a list containing the y-coordinates of the text correcponding to that index
		
		size (int)    - The size of the text in word editor format
					  - If a list of lists is given and 'text' is a list: Is a list containing the sizes of the text correcponding to that index
					  Note: You do not get the speed bonus for non-rotated lines if you make this a list
		
		angle (int)   - If not None: The angle in degrees that the text will be rotated. Positive values rotate it counter-clockwise
					  - If a list of lists is given and 'text' is a list: Is a list containing angles of rotation for the text correcponding to that index
		
		color (tuple) - (R, G, B) as integers
					  - If a list of tuples is given and 'text' is a list: Each color will be used for each text in the list 'x' correcponding to that index

		Example Input: drawText("Lorem Ipsum", 5, 5)
		Example Input: drawText("Lorem Ipsum", 5, 5, 10)
		Example Input: drawText("Lorem Ipsum", 5, 5, 10, 45)
		Example Input: drawText("Lorem Ipsum", 5, 5, color = (255, 0, 0))
		Example Input: drawText(["Lorem Ipsum", "Dolor Sit"], 5, 5, color = (255, 0, 0)) #Will draw both on top of each other
		Example Input: drawText(["Lorem Ipsum", "Dolor Sit"], 5, [5, 10]) #Will draw both in a straight line
		Example Input: drawText(["Lorem Ipsum", "Dolor Sit"], 5, [5, 10], color = [(255, 0, 0), (0, 255, 0)]) #Will color both differently
		Example Input: drawText(["Lorem Ipsum", "Dolor Sit"], 5, [5, 10], 18) #Will size both the same
		Example Input: drawText(["Lorem Ipsum", "Dolor Sit"], 5, [5, 10], [12, 18]) #Will size both differently
		Example Input: drawText(["Lorem Ipsum", "Dolor Sit"], 5, [5, 10], angle = 45) #Will rotate both to the same angle
		Example Input: drawText(["Lorem Ipsum", "Dolor Sit"], 5, [5, 10], angle = [45, -45]) #Will rotate both to different angles
		Example Input: drawText(["Lorem Ipsum", "Dolor Sit"], 5, [5, 10], angle = [45, 0]) #Will rotate only one
		Example Input: drawText(["Lorem Ipsum", "Dolor Sit"], [5, 10], [5, 10], [12, 18], [45, 0], [(255, 0, 0), (0, 255, 0)])
		"""

		#Determine text color
		pen = self.getPen(color)

		#Configure text
		if (angle != None):
			if ((type(text) == list) or (type(text) == tuple)):
				for i, item in enumerate(text):
					#Determine font size
					if ((type(size) != list) and (type(size) != tuple)):
						fontSize = size
					else:
						fontSize = size[i]

					#Determine font family
					fontFamily = wx.ROMAN

					#Determine font italicization
					fontItalic = wx.ITALIC

					#Determine font boldness
					if (bold):
						fontBold = wx.BOLD
					else:
						fontBold = wx.NORMAL

					#Define font
					font = wx.Font(fontSize, fontFamily, fontItalic, fontBold)
					self.queue("dc.SetFont", font)

					#Determine x-coordinate
					if ((type(x) != list) and (type(x) != tuple)):
						textX = x
					else:
						textX = x[i]

					#Determine y-coordinate
					if ((type(y) != list) and (type(y) != tuple)):
						textY = y
					else:
						textY = y[i]

					#Determine angle
					if ((type(angle) != list) and (type(angle) != tuple)):
						textAngle = angle
					else:
						textAngle = angle[i]

					if (type(pen) != list):
						self.queue("dc.SetPen", pen)
					else:
						self.queue("dc.SetPen", pen[i])

					#Draw text
					self.queue("dc.DrawRotatedText", [item, textX, textY, textAngle])
			else:
				self.queue("dc.SetPen", pen)
				self.queue("dc.DrawRotatedText", [text, x, y, angle])
		
		else:
			if ((type(text) == list) or (type(text) == tuple)):
				#Determine if fonts are different or not
				### To Do: When other font things are implemented, account for them in this if statement as well
				if ((type(size) != list) or (type(size) != tuple)):
					for i, item in enumerate(text):
						#Determine font size
						if ((type(size) != list) and (type(size) != tuple)):
							fontSize = size
						else:
							fontSize = size[i]

						#Determine font family
						fontFamily = wx.ROMAN

						#Determine font italicization
						fontItalic = wx.ITALIC

						#Determine font boldness
						fontBold = wx.NORMAL

						#Define font
						font = wx.Font(fontSize, fontFamily, fontItalic, fontBold)
						self.queue("dc.SetFont", font)

						#Determine x-coordinates and y-coordinates
						if ((type(x) != list) and (type(x) != tuple)):
							textX = x
						else:
							textX = x[i]

						#Determine y-coordinate
						if ((type(y) != list) and (type(y) != tuple)):
							textY = y
						else:
							textY = y[i]

						if (type(pen) != list):
							pen = [pen for i in range(len(text))]
						else:
							self.queue("dc.SetPen", pen[i])

						#Draw text
						self.queue("dc.DrawText", [item, textX, textY])

				else:
					#Determine font family
					fontFamily = wx.ROMAN

					#Determine font italicization
					fontItalic = wx.ITALIC

					#Determine font boldness
					fontBold = wx.NORMAL

					#Define font
					font = wx.Font(size, fontFamily, fontItalic, fontBold)
					self.queue("dc.SetFont", font)

					#Ensure x-coordinates and y-coordinates are lists
					if ((type(x) != list) and (type(x) != tuple)):
						x = [x for i in range(len(text))]

					if ((type(y) != list) and (type(y) != tuple)):
						y = [y for i in range(len(text))]

					#Leaf x-coordinates and y-coordinates
					coordinates = [(x[i], y[i]) for i in range(len(text))]

					#Draw text
					self.queue("dc.DrawTextList", [item, coordinates, pen])
			else:
				#Determine font family
				fontFamily = wx.ROMAN

				#Determine font italicization
				fontItalic = wx.NORMAL

				#Determine font boldness
				fontBold = wx.NORMAL

				#Define font
				font = wx.Font(size, fontFamily, fontItalic, fontBold)
				self.queue("dc.SetFont", font)

				self.queue("dc.SetPen", pen)
				self.queue("dc.DrawText", [text, x, y])

	def drawPoint(self, x, y, color = (0, 0, 0)):
		"""Draws a single pixel on the canvas.

		x (int) - The x-coordinate of the point
				- If a list is given: Is a list containing (x, y) for each point to draw. 'y' will be ignored
				  Note: This is the fastest way to draw many points

		y (int) - The y-coordinate of the point
		color (tuple) - (R, G, B) as integers
					  - If a list of tuples is given and 'x' is a list: Each color will be used for each point in the list 'x' correcponding to that index

		Example Input: drawPoint(5, 5)
		Example Input: drawPoint(5, 5, (255, 0, 0))
		Example Input: drawPoint([(5, 5), (7, 7)], color = (255, 0, 0))
		Example Input: drawPoint([(5, 5), (7, 7)], color = [(255, 0, 0), (0, 255, 0)])
		"""

		#Determine point color
		pen = self.getPen(color)

		#Draw the point
		if ((type(x) == list) or (type(x) == tuple)):
			self.queue("dc.DrawPointList", [x, pen])
		else:
			self.queue("dc.SetPen", pen)
			self.queue("dc.DrawPoint", [x, y])

	def drawLine(self, x1, y1, x2, y2, width = 1, color = (0, 0, 0)):
		"""Draws a line on the canvas.

		x1 (int)      - The x-coordinate of endpoint 1
					  - If a list is given: Is a list containing (x1, y1, x2, y2) or [(x1, y1), (x2, y2)] for each line to draw. 'y1', 'x2', and 'y2' will be ignored
						Note: This is the fastest way to draw many lines

		y1 (int)      - The y-coordinate of endpoint 1
		x2 (int)      - The x-coordinate of endpoint 2
		y2 (int)      - The y-coordinate of endpoint 2
		width (int)   - How thick the line is
		color (tuple) - (R, G, B) as integers
					  - If a list of tuples is given and 'x1' is a list: Each color will be used for each line in the list 'x1' correcponding to that index

		Example Input: drawLine(5, 5, 10, 10)
		Example Input: drawLine(5, 5, 10, 10, (255, 0, 0))
		Example Input: drawLine([(5, 5, 10, 10), (7, 7, 12, 12)], color = (255, 0, 0))
		Example Input: drawLine([(5, 5, 10, 10), (7, 7, 12, 12)], color = [(255, 0, 0), (0, 255, 0)])
		Example Input: drawLine([[(5, 5), (10, 10)], [(7, 7), (12, 12)], color = (255, 0, 0))
		"""

		#Determine line color
		pen = self.getPen(color, width)

		#Draw the line
		if ((type(x1) == list) or (type(x1) == tuple)):
			#Determine input type
			if ((type(x1[0]) == list) or (type(x1[0]) == tuple)):
				#Type [(x1, y1), (x2, y2)]
				lines = [(item[0][0], item[0][1], item[1][0], item[1][1]) for item in x] #Leaf coordinates correctly
			else:
				#Type (x1, y1, x2, y2)
				lines = x1

			#Draw lines
			self.queue("dc.DrawLineList", [lines, pen])
		else:
			self.queue("dc.SetPen", pen)
			self.queue("dc.DrawLine", [x1, y1, x2, y2])

	def drawSpline(self, points, color = (0, 0, 0)):
		"""Draws a spline on the canvas.

		points (list) - The vertices of the spline as tuples
					  - If a list of lists is given: Is a list containing the points for each spline to draw
						Note: This provides no speed benifit

		color (tuple) - (R, G, B) as integers
					  - If a list of tuples is given and 'points' is a list: Each color will be used for each spline in the list 'points' correcponding to that index

		Example Input: drawSpline([(5, 5), (10, 10), (15, 15)])
		Example Input: drawSpline([[(5, 5), (10, 10), (15, 15)], [(7, 7), (12, 12), (13, 13)], color = (255, 0, 0))
		Example Input: drawSpline([[(5, 5), (10, 10), (15, 15)], [(7, 7), (12, 12), (13, 13)], color = [(255, 0, 0), (0, 255, 0)])
		"""

		#Determine spline color
		pen = self.getPen(color)

		#Draw the spline
		if ((type(points) == list) or (type(points) == tuple)):
			for item in points:
				#Configure points
				spline = [element for sublist in item for element in sublist]

				#Draw spline
				self.queue("dc.DrawSpline", spline)
		else:
			self.queue("dc.SetPen", pen)
			self.queue("dc.DrawSpline", points)

	def drawArc(self, x, y, width, height = None, start = 0, end = 180, outline = (0, 0, 0), fill = None, style = None):
		"""Draws an arced line on the canvas.
		The arc is drawn counter-clockwise from (x1, y1) to (x3, y3).

		x (int)       - The x-coordinate of the top-left corner of a rectangle that contains the arc
					  - If a list is given: Is a list containing (x, y) for each arc to draw. 'y' will be ignored
						Note: This provides no speed benifit

		y (int)       - The y-coordinate of the top-left corner of a rectangle that contains the arc
		width (int)   - The width of the rectangle that contains the arc
					  - If a list is given and 'x' is a list: Is a list containing the width for each arc to draw. Each width will be used for each arc in the list 'x' correcponding to that index
		
		height (int)  - The height of the rectangle that contains the arc. If None: It will be a square
					  - If a list is given and 'x' is a list: Is a list containing the height for each arc to draw. Each height will be used for each arc in the list 'x' correcponding to that index
					  
		start (float) - The angle in degrees where the arc will start.
					  - If a list is given and 'x' is a list: Is a list containing the starting angle for each arc to draw. Each angle will be used for each arc in the list 'x' correcponding to that index
		
		end (float)   - The angle in degrees where the arc will end.
					  - If a list is given and 'x' is a list: Is a list containing the ending angle for each arc to draw. Each angle will be used for each arc in the list 'x' correcponding to that index
		
		outline (tuple) - The outline in (R, G, B) as integers
					  - If a list of tuples is given and 'x' is a list: Each color will be used to outline each arc in the list 'x' correcponding to that index
		
		fill (tuple)  - The fill in (R, G, B) as integers
						If None: The fill will be transparent (no fill)
					  - If a list of tuples is given and 'x' is a list: Each color will be used to fill each arc  in the list 'x' correcponding to that index

		style (str)   - How the arc will be filled in
						If None: It will default to solid
					  - If a list of tuples is given and 'x' is a list: Each color will be used to fill style each arc in the list 'x' correcponding to that index

		Example Input: drawArc(5, 5, 10)
		Example Input: drawArc(5, 5, 10, start = 90, end = 180)
		Example Input: drawArc(5, 5, 10, 5, outline = (255, 0, 0))
		Example Input: drawArc(5, 5, 10, 5, outline = (255, 0, 0), fill = (0, 255, 0))
		Example Input: drawArc([(5, 5), (7, 7)], 10, start = 90, end = 180)
		Example Input: drawArc([(5, 5), (7, 7)], 10, start = [45, 225], end = [90, 270])
		Example Input: drawArc([(5, 5), (7, 7)], 10, outline = (255, 0, 0))
		Example Input: drawArc([(5, 5), (7, 7)], 10, outline = [(255, 0, 0), (0, 255, 0)])
		Example Input: drawArc([(5, 5), (7, 7)], [7, 10], outline = (255, 0, 0))
		Example Input: drawArc([(5, 5), (7, 7)], [7, 10], [5, 10], outline = (255, 0, 0))
		Example Input: drawArc([(5, 5), (7, 7)], 10, outline = [(255, 0, 0), (0, 255, 0)], fill = [(0, 255, 0), (255, 0, 0)], style = "solid")
		Example Input: drawArc([(5, 5), (7, 7)], 10, outline = [(255, 0, 0), (0, 255, 0)], fill = [(0, 255, 0), (255, 0, 0)], style = ["solid", "hatchCross"])
		"""

		#Determine arc color
		pen = self.getPen(outline)
		brush = self.getBrush(fill, style)

		#Draw the arc
		if ((type(x) == list) or (type(x) == tuple)):
			for i, item in enumerate(x):
				#Setup colors
				if ((type(pen) != list) and (type(pen) != tuple)):
					self.queue("dc.SetPen", pen)
				else:
					self.queue("dc.SetPen", pen[i])

				if (type(brush) != list):
					self.queue("dc.SetBrush", brush)
				else:
					self.queue("dc.SetBrush", brush[i])

				#Determine height and width
				if (height != None):
					if ((type(height) != list) and (type(height) != tuple)):
						arcHeight = height
					else:
						arcHeight = height[i]
				else:
					arcHeight = width

				if ((type(width) != list) and (type(width) != tuple)):
					arcWidth = width
				else:
					arcWidth = width[i]

				#Determine angles
				if ((type(start) != list) and (type(start) != tuple)):
					arcStart = start
				else:
					arcStart = start[i]

				if ((type(end) != list) and (type(end) != tuple)):
					arcEnd = end
				else:
					arcEnd = end[i]

				#Draw the arc
				self.queue("dc.DrawEllipticArc", [item[0], item[1], arcWidth, arcHeight, arcStart, arcEnd])
		else:
			if (height == None):
				height = width

			self.queue("dc.SetPen", pen)
			self.queue("dc.SetBrush", brush)
			self.queue("dc.DrawEllipticArc", [x, y, width, height, start, end])

	def drawCheckMark(self, x, y, width, height = None, color = (0, 0, 0)):
		"""Draws a check mark on the canvas.

		x (int)       - The x-coordinate of the top-left corner of a rectangle that contains the check mark
					  - If a list is given: Is a list containing (x, y) for each point to draw. 'y' will be ignored
						Note: This provides no speed benifit

		y (int)       - The y-coordinate of the top-left corner of a rectangle that contains the check mark
		width (int)   - The width of the rectangle that contains the check mark
					  - If a list is given and 'x' is a list: Is a list containing the width for each arc to draw. Each width will be used for each check mark in the list 'x' correcponding to that index

		height (int)  - The height of the rectangle that contains the check mark. If None: It will be a square
					  - If a list is given and 'x' is a list: Is a list containing the width for each arc to draw. Each width will be used for each check mark in the list 'x' correcponding to that index

		color (tuple) - (R, G, B) as integers

		Example Input: drawCheckMark(5, 5, 10)
		Example Input: drawCheckMark(5, 5, 10, 5, (255, 0, 0))
		Example Input: drawCheckMark([(5, 5), (10, 10)], 10)
		Example Input: drawCheckMark([(5, 5), (10, 10)], [10, 5])
		Example Input: drawCheckMark([(5, 5), (10, 10)], 10, color = [(255, 0, 0), (0, 255, 0)])
		"""

		#Determine check mark color
		pen = self.getPen(color)

		#Draw the line
		if ((type(x) == list) or (type(x) == tuple)):
			for i, item in enumerate(x):
				#Setup color
				if ((type(pen) != list) and (type(pen) != tuple)):
					self.queue("dc.SetPen", pen)
				else:
					self.queue("dc.SetPen", pen[i])

				#Determine height and width
				if (height != None):
					if ((type(height) != list) and (type(height) != tuple)):
						checkMarkHeight = height
					else:
						checkMarkHeight = height[i]
				else:
					checkMarkHeight = width

				if ((type(width) != list) and (type(width) != tuple)):
					checkMarkWidth = width
				else:
					checkMarkWidth = width[i]

				#Draw the check mark
				self.queue("dc.DrawCheckMark", [item[0], item[1], checkMarkWidth, checkMarkHeight])
		else:
			#Draw the line
			if (height == None):
				height = width

			self.queue("dc.SetPen", pen)
			self.queue("dc.DrawCheckMark", [x, y, width, height])

	def drawRectangle(self, x, y, width, height = None, radius = None, outline = (0, 0, 0), outlineWidth = 1, fill = None, style = None):
		"""Draws a rectangle on the canvas.

		x (int)       - The x-coordinate for the top-left corner of the rectangle
					  - If a list is given: Is a list containing (x, y) for each rectangle to draw. 'y' will be ignored
						Note: This is the fastest way to draw many non-rounded rectangles

		y (int)       - The y-coordinate for the top-left corner of the rectangle
		width (int)   - The width of the rectangle
					  - If a list is given and 'x' is a list: Is a list containing the width for each rectangle to draw. Each width will be used for each check mark in the list 'x' correcponding to that index

		height (int)  - The height of the rectangle. If None: It will be a square
					  - If a list is given and 'x' is a list: Is a list containing the width for each rectangle to draw. Each width will be used for each check mark in the list 'x' correcponding to that index

		radius (int)  - The radius of the rounded corners. If None: There will be no radius
					  - If a list is given and 'x' is a list: Is a list containing the width for each rectangle to draw. Each width will be used for each check mark in the list 'x' correcponding to that index
		
		outline (tuple) - The outline in (R, G, B) as integers
					  - If a list of tuples is given and 'x' is a list: Each color will be used to outline each rectangle in the list 'x' correcponding to that index
		
		outline Width (int) - The width of the outline
					  - If a list of tuples is given and 'x' is a list: Each color will be used to outline each rectangle in the list 'x' correcponding to that index
		
		fill (tuple)  - The fill in (R, G, B) as integers
						If None: The fill will be transparent (no fill)
					  - If a list of tuples is given and 'x' is a list: Each color will be used to fill each rectangle  in the list 'x' correcponding to that index

		style (str)   - How the rectangle will be filled in
						If None: It will default to solid
					  - If a list of tuples is given and 'x' is a list: Each color will be used to fill style each rectangle in the list 'x' correcponding to that index

		Example Input: drawRectangle(5, 5, 25)
		Example Input: drawRectangle(5, 5, 25, 40)
		Example Input: drawRectangle(5, 5, 25, outline = (255, 0, 0))
		Example Input: drawRectangle(5, 5, 10, 5, outline = (255, 0, 0), fill = (0, 255, 0))
		Example Input: drawRectangle([(5, 5), (7, 7)], 10, outline = (255, 0, 0))
		Example Input: drawRectangle([(5, 5), (7, 7)], 10, outline = [(255, 0, 0), (0, 255, 0)])
		Example Input: drawRectangle([(5, 5), (7, 7)], [7, 10], outline = (255, 0, 0), outlineWidth = 4)
		Example Input: drawRectangle([(5, 5), (7, 7)], [7, 10], [5, 10], outline = (255, 0, 0))
		Example Input: drawRectangle([(5, 5), (7, 7)], 10, outline = [(255, 0, 0), (0, 255, 0)], fill = [(0, 255, 0), (255, 0, 0)], style = "solid")
		Example Input: drawRectangle([(5, 5), (7, 7)], 10, outline = [(255, 0, 0), (0, 255, 0)], fill = [(0, 255, 0), (255, 0, 0)], style = ["solid", "hatchCross"])
		"""

		#Determine rectangle color
		pen = self.getPen(outline, outlineWidth)
		brush = self.getBrush(fill, style)

		#Draw the rectangle
		if ((type(x) == list) or (type(x) == tuple)):
			if (radius != None):
				#Create rounded rectangles
				for i, item in enumerate(x):
					#Setup colors
					if ((type(pen) != list) and (type(pen) != tuple)):
						self.queue("dc.SetPen", pen)
					else:
						self.queue("dc.SetPen", pen[i])

					if (type(brush) != list):
						self.queue("dc.SetBrush", brush)
					else:
						self.queue("dc.SetBrush", brush[i])

					#Determine height and width
					if (height != None):
						if ((type(height) != list) and (type(height) != tuple)):
							arcHeight = height
						else:
							arcHeight = height[i]
					else:
						arcHeight = width

					if ((type(width) != list) and (type(width) != tuple)):
						arcWidth = width
					else:
						arcWidth = width[i]

					#Draw the rectangle
					self.queue("dc.DrawRoundedRectangle", [item[0], item[1], width, height, radius])

			else:
				#Create non-rounded rectangle
				#Determine height and width
				if ((type(width) != list) and (type(width) != tuple)):
					width = [width for item in x]

				if (height != None):
					if ((type(height) != list) and (type(height) != tuple)):
						height = [height for item in x]
				else:
					height = [width[i] for i in range(len(x))]

				#Configure correct arg format
				rectangles = [(item[0][0], item[0][1], width[i], height[i]) for i, item in enumerate(x)] #Leaf coordinates correctly

				#Draw Rectangle
				self.queue("dc.DrawRectangleList", [rectangles, pen, brush])
		else:

			#Draw the rectangle
			if (height == None):
				height = width

			self.queue("dc.SetPen", pen)
			self.queue("dc.SetBrush", brush)

			if (radius != None):
				self.queue("dc.DrawRoundedRectangle", [x, y, width, height, radius])
			else:
				self.queue("dc.DrawRectangle", [x, y, width, height])

	def drawPolygon(self, points, outline = (0, 0, 0), outlineWidth = 1, fill = None, style = None, algorithm = 0):
		"""Draws a polygon on the canvas.

		points (list) - The vertices of the polygon as tuples
					  - If a list of lists is given: Is a list containing the points for each polygon to draw
						Note: This is the fastest way to draw many polygons

		outline (tuple) - The outline in (R, G, B) as integers
					  - If a list of tuples is given and 'x' is a list: Each color will be used to outline each circle in the list 'x' correcponding to that index
		
		outline Width (int) - The width of the outline
					  - If a list of tuples is given and 'x' is a list: Each color will be used to outline each rectangle in the list 'x' correcponding to that index
		
		fill (tuple)  - The fill in (R, G, B) as integers
						If None: The fill will be transparent (no fill)
					  - If a list of tuples is given and 'x' is a list: Each color will be used to fill each circle  in the list 'x' correcponding to that index

		style (str)   - How the circle will be filled in
						If None: It will default to solid
					  - If a list of tuples is given and 'x' is a list: Each color will be used to fill style each circle in the list 'x' correcponding to that index
		
		algorithm (int) - Which algorithm will connect the polygon points which are:
			0 - Odd Even Rule
			1 - Winding Rule

		Example Input: drawPolygon([(5, 5), (7, 5), (5, 7)])
		Example Input: drawPolygon([(5, 5), (7, 5), (5, 7)], outline = (255, 0, 0), fill = (0, 255, 0), outlineWidth = 4)
		Example Input: drawPolygon([[(5, 5), (7, 5), (5, 7)], [(8, 8), (10, 8), (8, 10)]])
		Example Input: drawPolygon([[(5, 5), (7, 5), (5, 7)], [(8, 8), (10, 8), (8, 10)]], outline = [(255, 0, 0), (0, 255, 0)], fill = [(0, 255, 0), (255, 0, 0)], style = "hatchCross")
		Example Input: drawPolygon([[(5, 5), (7, 5), (5, 7)], [(8, 8), (10, 8), (8, 10)]], outline = [(255, 0, 0), (0, 255, 0)], fill = [(0, 255, 0), (255, 0, 0)], style = ["solid", "hatchCross"])
		"""

		#Determine point color
		pen = self.getPen(outline, outlineWidth)
		brush = self.getBrush(fill, style)

		#Draw the polygon
		if (type(points) == list):
			self.queue("dc.DrawPolygonList", [points, pen, brush])
		else:
			self.queue("dc.SetPen", pen)
			self.queue("dc.SetBrush", brush)
			self.queue("dc.DrawPolygon", [points, 0, 0, style])

	def drawCircle(self, x, y, radius, outline = (0, 0, 0), outlineWidth = 1, fill = None, style = None):
		"""Draws a circle on the canvas.

		x (int)       - The x-coordinate of the circle on the canvas
					  - If a list is given: Is a list containing (x, y) for each point to draw. 'y' will be ignored
						Note: This provides no speed benifit

		y (int)       - The y-coordinate of the circle on the canvas
		radius (int)  - The radius of the circle
					  - If a list is given and 'x' is a list: Is a list containing the radii of the circles to draw. Each width will be used for each check mark in the list 'x' correcponding to that index
		
		outline (tuple) - The outline in (R, G, B) as integers
					  - If a list of tuples is given and 'x' is a list: Each color will be used to outline each circle in the list 'x' correcponding to that index
		
		outline Width (int) - The width of the outline
					  - If a list of tuples is given and 'x' is a list: Each color will be used to outline each rectangle in the list 'x' correcponding to that index
		
		fill (tuple)  - The fill in (R, G, B) as integers
						If None: The fill will be transparent (no fill)
					  - If a list of tuples is given and 'x' is a list: Each color will be used to fill each circle  in the list 'x' correcponding to that index

		style (str)   - How the circle will be filled in
						If None: It will default to solid
					  - If a list of tuples is given and 'x' is a list: Each color will be used to fill style each circle in the list 'x' correcponding to that index

		Example Input: drawCircle(5, 5, 10)
		Example Input: drawCircle(5, 5, 10, (255, 0, 0))
		Example Input: drawCircle(5, 5, 10, outline = (255, 0, 0), fill = (0, 255, 0))
		Example Input: drawCircle([(5, 5), (7, 7)], 10, outline = (255, 0, 0), outlineWidth = 4)
		Example Input: drawCircle([(5, 5), (7, 7)], 10, outline = [(255, 0, 0), (0, 255, 0)])
		Example Input: drawCircle([(5, 5), (7, 7)], [7, 10], outline = (255, 0, 0))
		Example Input: drawCircle([(5, 5), (7, 7)], 10, outline = [(255, 0, 0), (0, 255, 0)], fill = [(0, 255, 0), (255, 0, 0)], style = "solid")
		Example Input: drawCircle([(5, 5), (7, 7)], 10, outline = [(255, 0, 0), (0, 255, 0)], fill = [(0, 255, 0), (255, 0, 0)], style = ["solid", "hatchCross"])
		"""

		#Determine circle color
		pen = self.getPen(outline, outlineWidth)
		brush = self.getBrush(fill, style)

		#Draw the circle
		if ((type(x) == list) or (type(x) == tuple)):
			for i, item in enumerate(x):
				#Setup colors
				if ((type(pen) != list) and (type(pen) != tuple)):
					self.queue("dc.SetPen", pen)
				else:
					self.queue("dc.SetPen", pen[i])

				if (type(brush) != list):
					self.queue("dc.SetBrush", brush)
				else:
					self.queue("dc.SetBrush", brush[i])

				#Determine radius
				if ((type(radius) != list) and (type(radius) != tuple)):
					circleRadius = radius
				else:
					circleRadius = radius[i]

				#Draw the circle
				self.queue("dc.DrawCircle", [item[0], item[1], circleRadius])

		else:
			#Draw the circle
			self.queue("dc.SetPen", pen)
			self.queue("dc.SetBrush", brush)
			self.queue("dc.DrawCircle", [x, y, radius])

	def drawEllipse(self, x, y, width, height = None, outline = (0, 0, 0), outlineWidth = 1, fill = None, style = None):
		"""Draws a ellipse on the canvas.

		x (int)       - The x-coordinate for the top-left corner of the ellipse
					  - If a list is given: Is a list containing (x, y) for each ellipse to draw. 'y' will be ignored
						Note: This is the fastest way to draw many ellipses

		y (int)       - The y-coordinate for the top-left corner of the ellipse
		width (int)   - The width of the ellipse
					  - If a list is given and 'x' is a list: Is a list containing the width for each ellipse to draw. Each width will be used for each check mark in the list 'x' correcponding to that index

		height (int)  - The height of the ellipse. If None: It will be a square
					  - If a list is given and 'x' is a list: Is a list containing the width for each ellipse to draw. Each width will be used for each check mark in the list 'x' correcponding to that index

		outline (tuple) - The outline in (R, G, B) as integers
					  - If a list of tuples is given and 'x' is a list: Each color will be used to outline each ellipse in the list 'x' correcponding to that index
		
		outline Width (int) - The width of the outline
					  - If a list of tuples is given and 'x' is a list: Each color will be used to outline each rectangle in the list 'x' correcponding to that index
		
		fill (tuple)  - The fill in (R, G, B) as integers
						If None: The fill will be transparent (no fill)
					  - If a list of tuples is given and 'x' is a list: Each color will be used to fill each ellipse  in the list 'x' correcponding to that index

		style (str)   - How the ellipse will be filled in
						If None: It will default to solid
					  - If a list of tuples is given and 'x' is a list: Each color will be used to fill style each ellipse in the list 'x' correcponding to that index

		Example Input: drawEllipse(5, 5, 25)
		Example Input: drawEllipse(5, 5, 25, 40)
		Example Input: drawEllipse(5, 5, 25, outline = (255, 0, 0))
		Example Input: drawEllipse(5, 5, 10, 5, outline = (255, 0, 0), fill = (0, 255, 0))
		Example Input: drawEllipse([(5, 5), (7, 7)], 10, outline = (255, 0, 0))
		Example Input: drawEllipse([(5, 5), (7, 7)], 10, outline = [(255, 0, 0), (0, 255, 0)])
		Example Input: drawEllipse([(5, 5), (7, 7)], [7, 10], outline = (255, 0, 0), outlineWidth = 4)
		Example Input: drawEllipse([(5, 5), (7, 7)], [7, 10], [5, 10], outline = (255, 0, 0))
		Example Input: drawEllipse([(5, 5), (7, 7)], 10, outline = [(255, 0, 0), (0, 255, 0)], fill = [(0, 255, 0), (255, 0, 0)], style = "solid")
		Example Input: drawEllipse([(5, 5), (7, 7)], 10, outline = [(255, 0, 0), (0, 255, 0)], fill = [(0, 255, 0), (255, 0, 0)], style = ["solid", "hatchCross"])
		"""

		#Determine ellipse color
		pen = self.getPen(outline, outlineWidth)
		brush = self.getBrush(fill, style)

		#Draw the ellipse
		if ((type(x) == list) or (type(x) == tuple)):
			#Determine height and width
			if ((type(width) != list) and (type(width) != tuple)):
				width = [width for item in x]

			if (height != None):
				if ((type(height) != list) and (type(height) != tuple)):
					height = [height for item in x]
			else:
				height = [width[i] for i in range(len(x))]

			#Configure correct arg format
			ellipses = [(item[0][0], item[0][1], width[i], height[i]) for i, item in enumerate(x)] #Leaf coordinates correctly

			#Draw ellipse
			self.queue("dc.DrawEllipseList", [ellipses, pen, brush])
		else:

			#Draw the ellipse
			if (height == None):
				height = width

			self.queue("dc.SetPen", pen)
			self.queue("dc.SetBrush", brush)

			self.queue("dc.DrawEllipse", [x, y, width, height])

class handle_WidgetTable(handle_Widget_Base):
	"""A handle for working with table widgets."""

	def __init__(self):
		"""Initializes defaults."""

		#Initialize inherited classes
		handle_Widget_Base.__init__(self)

	def __len__(self):
		"""Returns what the contextual length is for the object associated with this handle.

		returnRows(bool) - Determines what is returned for 2D objects
			- If True: Returns how many rows the object has
			- If False: Returns how many columns the object has
		"""

		if (self.type == "Table"):
			if (returnRows):
				value = self.thing.GetNumberRows()
			else:
				value = self.thing.GetNumberCols()

		else:
			warnings.warn("Add {} to __len__() for {}".format(self.type, self.__repr__()), Warning, stacklevel = 2)
			value = 0

		return value

	#Change Settings

	def setFunction_preEdit(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		self.betterBind(wx.grid.EVT_GRID_CELL_CHANGING, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)

	def setFunction_postEdit(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		self.thing.EnableEditing(True)
		self.betterBind(wx.grid.EVT_GRID_CELL_CHANGED, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)

	def setFunction_drag(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		self.betterBind(wx.grid.EVT_GRID_COL_SIZE, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		self.betterBind(wx.grid.EVT_GRID_ROW_SIZE, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)

	def setFunction_selectMany(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		self.betterBind(wx.grid.EVT_GRID_RANGE_SELECT, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)

	def setFunction_selectSingle(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		self.betterBind(wx.grid.EVT_GRID_SELECT_CELL, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)

	def setFunction_rightClickCell(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		self.betterBind(wx.grid.EVT_GRID_CELL_RIGHT_CLICK, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)

	def setFunction_rightClickLabel(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		self.betterBind(wx.grid.EVT_GRID_LABEL_RIGHT_CLICK, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)

	#Interact with table
	def appendRow(self, numberOf = 1, updateLabels = True):
		"""Adds one or more new rows to the bottom of the grid.
		The top-left corner is row (0, 0) not (1, 1).

		numberOf (int)      - How many rows to add
		updateLabels (bool) - If True: The row labels will update

		Example Input: appendRow(0)
		Example Input: appendRow(0, 5)
		"""

		self.thing.AppendRows(numberOf, updateLabels)

	def appendColumn(self, numberOf = 1, updateLabels = True):
		"""Adds one or more new columns to the right of the grid.
		The top-left corner is row (0, 0) not (1, 1).

		numberOf (int)      - How many columns to add
		updateLabels (bool) - If True: The row labels will update

		Example Input: appendColumn(0)
		Example Input: appendColumn(0, 5)
		"""

		self.thing.AppendCols(numberOf, updateLabels)

	def enableTableEditing(self, row = -1, column = -1, state = True):
		"""Allows the user to edit the table.

		row (int)         - Which row this applies to
		column (int)      - Which column this applies to
			If both 'row' and 'column' are -1, the whole table will diabled
			If both 'row' and 'column' are given, that one cell will be disabled
			If 'row' is given and 'column is -1', that one row will be disabled
			If 'row' is -1 and 'column' is given, that one column will be disabled


		Example Input: enableTableEditing(0)
		Example Input: enableTableEditing(0, row = 0)
		Example Input: enableTableEditing(0, column = 0)
		Example Input: enableTableEditing(0, row = 0, column = 0)
		"""

		#Account for multiple rows and columns
		if ((type(row) != list) and (type(row) != tuple)):
			rowList = [row]
		else:
			rowList = row

		if ((type(column) != list) and (type(column) != tuple)):
			columnList = [column]
		else:
			columnList = column

		for column in columnList:
			for row in rowList:
				#Determine if only 1 cell will be changed
				if ((row != -1) and (column != -1)):
					self.readOnlyCatalogue[row][column] = not state

				elif ((row == -1) and (column == -1)):
					for i in range(self.thing.GetNumberRows()):
						for j in range(self.thing.GetNumberCols()):
							self.readOnlyCatalogue[i][j] = not state

				elif (row != -1):
					for j in range(self.thing.GetNumberCols()):
						self.readOnlyCatalogue[row][j] = not state

				elif (column != -1):
					for i in range(self.thing.GetNumberRows()):
						self.readOnlyCatalogue[i][column] = not state

	def disableTableEditing(self, row = -1, column = -1, state = False):
		"""Allows the user to edit the table.

		row (int)         - Which row this applies to
		column (int)      - Which column this applies to
			If both 'row' and 'column' are -1, the whole table will diabled
			If both 'row' and 'column' are given, that one cell will be disabled
			If 'row' is given and 'column is -1', that one row will be disabled
			If 'row' is -1 and 'column' is given, that one column will be disabled

		Example Input: disableTableEditing(0)
		Example Input: disableTableEditing(0, row = 0)
		Example Input: disableTableEditing(0, column = 0)
		Example Input: disableTableEditing(0, row = 0, column = 0)
		"""

		self.enableTableEditing(row = row, column = column,  state = not state)

	def getTableReadOnly(self, row, column):
		"""Moves the table highlight cursor to the given cell coordinates
		The top-left corner is row (0, 0) not (1, 1).

		row (int)         - The index of the row
		column (int)      - The index of the column

		Example Input: getTableReadOnly(1, 1, 0)
		"""

		readOnly = self.readOnlyCatalogue[row][column]
		return readOnly

	def getTableCurrentCellReadOnly(self):
		"""Moves the table highlight cursor to the given cell coordinates
		The top-left corner is row (0, 0) not (1, 1).

		Example Input: getTableCurrentCellReadOnly()
		"""

		selection = self.getTableCurrentCell()

		#Default to the top left cell if a range is selected
		row, column = selection[0]

		readOnly = self.getTableReadOnly(row, column)
		return readOnly

	def clearTable(self):
		"""Clears all cells in the table

		Example Input: clearTable()
		"""
		
		self.thing.ClearGrid()

	def setTableCursor(self, row, column):
		"""Moves the table highlight cursor to the given cell coordinates
		The top-left corner is row (0, 0) not (1, 1).

		row (int)         - The index of the row
		column (int)      - The index of the column

		Example Input: setTableCursor(1, 2)
		"""

		#Set the cell value
		self.thing.GoToCell(row, column)

	def setTableCell(self, row, column, value, noneReplace = True):
		"""Writes something to a cell.
		The top-left corner is row (0, 0) not (1, 1).

		row (int)         - The index of the row
		column (int)      - The index of the column
		value (any)       - What will be written to the cell.
		value (array)     - What will be written in the group of cells with the row and column being the top-left coordinates. Can be a 2D list
		noneReplace (bool) - Determines what happens if the user gives a value of None for 'value'.
			- If True: Will replace the cell with ""
			- If False: Will not replace the cell

		Example Input: setTableCell(1, 2, 42)
		Example Input: setTableCell(1, 2, 3.14)
		Example Input: setTableCell(1, 2, "Lorem Ipsum")
		"""

		#Account for None
		if (value == None):
			if (noneReplace):
				value = ""
			else:
				return

		#Ensure correct format
		if (type(value) != str):
			value = str(value)

		#Set the cell value
		self.thing.SetCellValue(row, column, value)

	def setTableCellList(self, row, column, listContents, noneReplace = True):
		"""Makes a cell a dropdown list.
		The top-left corner is row (0, 0) not (1, 1).

		row (int)          - The index of the row
		column (int)       - The index of the column
		listContents (any) - What will be written to the cell.
		noneReplace (bool) - Determines what happens if the user gives a value of None for 'listContents'.
			- If True: Will replace the cell with ""
			- If False: Will not replace the cell

		Example Input: setTableCell(1, 2, [1, 2, 3], 0)
		"""

		#Account for None
		if (listContents == None):
			if (noneReplace):
				listContents = ""
			else:
				return

		#Ensure correct format
		if ((type(listContents) != list) and (type(listContents) != tuple)):
			listContents = [listContents]

		#Set the cell listContents
		editor = wx.grid.GridCellChoiceEditor(listContents)
		self.thing.SetCellValue(row, column, editor)

	def getTableCellValue(self, row, column):
		"""Reads something in a cell.
		The top-left corner is row (0, 0) not (1, 1).

		row (int)         - The index of the row
			- If None: Will return the all values of the column if 'column' is not None
		column (int)      - The index of the column
			- If None: Will return the all values of the row if 'row' is not None

		Example Input: getTableCellValue(1, 2)
		"""

		#Error Checking
		if ((row == None) and (column == None)):
			value = []
			for i in range(self.thing.GetNumberRows()):
				for j in range(self.thing.GetNumberCols()):
					#Get the cell value
					value.append(self.thing.GetCellValue(i, j))
			return None

		#Account for entire row or column request
		if ((row != None) and (column != None)):
			#Get the cell value
			value = self.thing.GetCellValue(row, column)

		elif (row == None):
			value = []
			for i in range(self.thing.GetNumberRows()):
				#Get the cell value
				value.append(self.thing.GetCellValue(i, column))

		else:
			value = []
			for i in range(self.thing.GetNumberCols()):
				#Get the cell value
				value.append(self.thing.GetCellValue(row, i))

		return value

	def getTableCurrentCell(self, event = None):
		"""Returns the row and column of the currently selected cell.
		The top-left corner is row (0, 0) not (1, 1).
		Modified code from http://ginstrom.com/scribbles/2008/09/07/getting-the-selected-cells-from-a-wxpython-grid/

		### TO DO: Make this work with events on all three levels ###

		rangeOn (bool)    - Determines what is returned when the user has a range of cells selected
			- If True: Returns [[(row 1, col 1), (row 1, col 2)], [(row 2, col 1), (row 2, col 2)]]
			- If False: Returns (row, col) of which cell in the range is currently active

		Example Input: getTableCurrentCellValue()
		"""

		#Check for multiple cells that were drag selected
		top_left_list = self.thing.GetSelectionBlockTopLeft()
		if (top_left_list):
			bottom_right_list = self.thing.GetSelectionBlockBottomRight()

			currentCell = []
			for top_left, bottom_right in zip(top_left_list, bottom_right_list):

				rows_start = top_left[0]
				rows_end = bottom_right[0]

				cols_start = top_left[1]
				cols_end = bottom_right[1]

				rows = range(rows_start, rows_end + 1)
				cols = range(cols_start, cols_end + 1)

				currentCell.extend([(row, col) for row in rows for col in cols])
		else:
			#Check for multiple cells were click-selected
			selection = self.thing.GetSelectedCells()

			if not selection:
				#Only a single cell was selected
				if (event != None):
					row = event.GetRow()
					column = event.GetCol()
				else:
					row = self.thing.GetGridCursorRow()
					column = self.thing.GetGridCursorCol()
				
				currentCell = [(row, column)]
			else:
				currentCell = selection

		return currentCell

	def getTableCurrentCellValue(self):
		"""Reads something from rhe currently selected cell.
		The top-left corner is row (0, 0) not (1, 1).

		Example Input: getTableCurrentCellValue()
		"""

		#Get the selected cell's coordinates
		selection = self.getTableCurrentCell()

		#Default to the top left cell if a range is selected
		row, column = selection[0]

		#Get the currently selected cell's value
		value = self.getTableCellValue(row, column)

		return value

	def getTableEventCell(self, event):
		"""Returns the row and column of the previously selected cell.
		The top-left corner is row (0, 0) not (1, 1).

		Example Input: getTableEventCellValue(event)
		"""

		row = event.GetRow()
		column = event.GetCol()

		return (row, column)

	def getTableEventCellValue(self, event):
		"""Reads something from the previously selected cell.
		The top-left corner is row (0, 0) not (1, 1).

		Example Input: getTableEventCellValue(event)
		"""

		#Get the selected cell's coordinates
		row, column = self.getTableEventCell(event)

		#Get the currently selected cell's value
		value = self.thing.GetCellValue(row, column)

		return value

	def setTableRowLabel(self, row, rowLabel):
		"""Changes a row's label.
		The top-left corner is row (0, 0) not (1, 1).

		row (int)         - The index of the row
		rowLabel (str)    - The new label for the row

		Example Input: setTableRowLabel(1, "Row 1")
		"""

		#Ensure correct data type
		if (type(rowLabel) != str):
			rowLabel = str(rowLabel)

		

		#Set the cell value
		self.thing.SetRowLabelValue(row, rowLabel)

	def setTableColumnLabel(self, column = 0, text = ""):
		"""Changes a cell's column label.
		The top-left corner is row (0, 0) not (1, 1).

		column (int)      - The index of the row
		columnLabel (str) - The new label for the row

		Example Input: setTableColumnLabel(1, "Column 2")
		"""

		#Ensure correct data type
		if (not isinstance(text, str)):
			text = "{}".format(text)

		#Set the cell value
		self.thing.SetColLabelValue(column, text)

	def getTableColumnLabel(self, column):
		"""Returns a cell's column label
		The top-left corner is row (0, 0) not (1, 1).

		column (int)      - The index of the row

		Example Input: setTableColumnLabel(1)
		"""

		#Ensure correct data type
		if (not isinstance(columnLabel, str)):
			columnLabel = "{}".format(columnLabel)

		#Set the cell value
		columnLabel = self.thing.GetColLabelValue(column)
		return columnLabel

	def setTableCellFormat(self, row, column, format):
		"""Changes the format of the text in a cell.
		The top-left corner is row (0, 0) not (1, 1).

		row (int)    - The index of the row
		column (int) - The index of the column
		format (str) - The format for the cell
			~ "float" - floating point

		Example Input: setTableCellFormat(1, 2, "float")
		"""

		#Set the cell format
		if (format == "float"):
			self.thing.SetCellFormatFloat(row, column, width, percision)

	def setTableCellColor(self, row, column, color):
		"""Changes the color of the background of a cell.
		The top-left corner is row (0, 0) not (1, 1).
		If both 'row' and 'column' are None, the entire table will be colored
		Special thanks to  for how to apply changes to the table on https://stackoverflow.com/questions/14148132/wxpython-updating-grid-cell-background-colour

		row (int)     - The index of the row
			- If None: Will color all cells of the column if 'column' is not None
		column (int)  - The index of the column
			- If None: Will color all cells of the column if 'column' is not None
		color (tuple) - What color to use. (R, G, B). Can be a string for standard colors
			- If None: Use thw wxPython background color

		Example Input: setTableCellColor(1, 2, (255, 0, 0))
		Example Input: setTableCellColor(1, 2, "red")
		"""

		if ((not isinstance(color, list)) and (not isinstance(color, tuple))):
			#Determine color (r, g, b)
			if (color == None):
				color = self.thing.GetDefaultCellBackgroundColour()

			elif (color == "grey"):
				color = (210, 210, 210)

			else:
				print("Add the color", color, "to setTableCellColor")
				return None

		#Convert color to wxColor
		color = wx.Colour(color[0], color[1], color[2])

		if ((row == None) and (column == None)):
			for i in range(self.thing.GetNumberRows()):
				for j in range(self.thing.GetNumberCols()):
					#Color the cell
					self.thing.SetCellBackgroundColour(i, j, color)

		elif ((row != None) and (column != None)):
			#Color the cell
			self.thing.SetCellBackgroundColour(row, column, color)

		elif (row == None):
			for i in range(self.thing.GetNumberRows()):
				#Color the cell
				self.thing.SetCellBackgroundColour(i, column, color)

		else:
			for i in range(self.thing.GetNumberCols()):
				#Color the cell
				self.thing.SetCellBackgroundColour(row, i, color)

		self.thing.ForceRefresh()

	def getTableCellColor(self, row, column):
		"""Returns the color of the background of a cell.
		The top-left corner is row (0, 0) not (1, 1).

		row (int)     - The index of the row
			- If None: Will color all cells of the column if 'column' is not None
		column (int)  - The index of the column
			- If None: Will color all cells of the column if 'column' is not None

		Example Input: getTableCellColor(1, 2)
		"""

		color = self.thing.GetCellBackgroundColour(row, column)
		return color

	def setTableCellFont(self, row, column, font, italic = False, bold = False):
		"""Changes the color of the text in a cell.
		The top-left corner is row (0, 0) not (1, 1).

		row (int)     - The index of the row
		column (int)  - The index of the column
		font(any)     - What font the text will be in the cell. Can be a:
								(A) string with the english word for the color
								(B) wxFont object
		italic (bool) - If True: the font will be italicized
		bold (bool)   - If True: the font will be bold

		Example Input: setTableTextColor(1, 2, "TimesNewRoman")
		Example Input: setTableTextColor(1, 2, wx.ROMAN)
		"""

		#Configure the font object
		if (italic):
			italic = wx.ITALIC
		else:
			italic = wx.NORMAL

		if (bold):
			bold = wx.BOLD
		else:
			bold = wx.NORMAL

		if (font == "TimesNewRoman"):
			font = wx.Font(wx.ROMAN, italic, bold)

		self.thing.SetCellFont(row, column, font)

	######################## FIX THIS #######################
	def setTableMods(self, row, column, font, italic = False, bold = False):
		"""Modifies the alignemt of a cell
		The top-left corner is row (0, 0) not (1, 1).

		row (int)         - The index of the row
		column (int)      - The index of the column
		font(any)         - What font the text will be in the cell. Can be a:
								(A) string with the english word for the color
								(B) wxFont object
		italic (bool)     - If True: the font will be italicized
		bold (bool)       - If True: the font will be bold

		Example Input: setTableTextColor(1, 2, "TimesNewRoman")
		Example Input: setTableTextColor(1, 2, wx.ROMAN)
		"""

		#Configure the font object
		if (italic):
			italic = wx.ITALIC
		else:
			italic = wx.NORMAL

		if (bold):
			bold = wx.BOLD
		else:
			bold = wx.NORMAL

		if (font == "TimesNewRoman"):
			font = wx.Font(wx.ROMAN, italic, bold)

		self.thing.SetCellFont(row, column, font)

		fixedFlags, position, border = self.getItemMod(flags)
	#########################################################

	def hideTableRow(self, row):
		"""Hides a row in a grid.
		The top-left corner is row (0, 0) not (1, 1).

		row (int)         - The index of the row

		Example Input: hideTableRow(1)
		"""

		self.thing.SetRowLabelSize(0) # hide the rows

	def hideTableColumn(self, column):
		"""Hides a column in a grid.
		The top-left corner is column (0, 0) not (1, 1).

		column (int)         - The index of the column

		Example Input: hideTableColumn(1)
		"""

		self.thing.SetColLabelSize(0) # hide the columns

	def setTableTextColor(self, row, column, color):
		"""Changes the color of the text in a cell.
		The top-left corner is row (0, 0) not (1, 1).

		row (int)         - The index of the row
		column (int)      - The index of the column
		color(any)        - What color the text will be in the cell. Can be a:
								(A) string with the english word for the color
								(B) wxColor object
								(C) list with the rgb color code; [red, green, blue]
								(D) string with the hex color code (remember to include the #)

		Example Input: setTableTextColor(1, 2, "red")
		Example Input: setTableTextColor(1, 2, wx.RED)
		Example Input: setTableTextColor(1, 2, [255, 0, 0])
		Example Input: setTableTextColor(1, 2, "#FF0000")
		"""

		#Set the text color
		self.thing.SetCellTextColour(row, column, color)

	def setTableBackgroundColor(self, row, column, color):
		"""Changes the color of the text in a cell.
		The top-left corner is row (0, 0) not (1, 1).

		row (int)    - The index of the row
		column (int) - The index of the column
		color(any)   - What color the text will be in the cell. Can be a:
								(A) string with the english word for the color
								(B) wxColor object
								(C) list with the rgb color code; [red, green, blue]
								(D) string with the hex color code (remember to include the #)

		Example Input: setTableBackgroundColor(1, 2, "red")
		Example Input: setTableBackgroundColor(1, 2, wx.RED)
		Example Input: setTableBackgroundColor(1, 2, [255, 0, 0])
		Example Input: setTableBackgroundColor(1, 2, "#FF0000")
		"""

		#Set the text color
		self.thing.SetCellBackgroundColour(row, column, color)

	def autoTableSize(self, autoRow = True, autoColumn = True, setAsMinimum = False):
		"""Sizes the rows and columns to fit all of their contents.
		What is autosizing can be toggled on and off.

		autoRow (bool)      - If True: Rows will be resized
		autoColumn (bool)   - If True: Columns will be resized
		setAsMinimum (bool) - If True: The calculated sizes will be set as the minimums
							  Note: In order to set for only rows, call this function once for all but rows with this toggled off, and then a second time for the rest.

		Example Input: autoTableSize()
		Example Input: autoTableSize(autoColumn = False)
		Example Input: autoTableSize(autoRow = False, setAsMinimum = False)
		"""

		#Size Gid
		if (autoRow):
			self.thing.AutoSizeRows(setAsMinimum)

		if (autoColumn):
			self.thing.AutoSizeColumns(setAsMinimum)

	def autoTableSizeRow(self, row, setAsMinimum = False):
		"""Sizes the a single row to fit its contents.
		What is autosizing can be toggled on and off.

		row (int)           - The row that will be autosized
		setAsMinimum (bool) - If True: The calculated sizes will be set as the minimums
							  
		Example Input: autoTableSizeRow(3)
		Example Input: autoTableSizeRow(4, setAsMinimum = False)
		"""

		#Size Row
		self.thing.AutoSizeRow(row, setAsMinimum)

	def autoTableSizeColumn(self, column, setAsMinimum = False):
		"""Sizes the a single column to fit its contents.
		What is autosizing can be toggled on and off.

		column (int)        - The column that will be autosized
		setAsMinimum (bool) - If True: The calculated sizes will be set as the minimums
							  
		Example Input: autoTableSizeColumn(3)
		Example Input: autoTableSizeColumn(4, setAsMinimum = False)
		"""

		#Size Row
		self.thing.AutoSizeColumn(column, setAsMinimum)

	def autoTableSizeRowLabel(self, row, setAsMinimum = False):
		"""Sizes the a single row to fit the height of the row label.

		row (int)           - The row that will be autosized
										  
		Example Input: autoSizeRowLabel(3)
		"""

		#Size Row
		self.thing.AutoSizeRowLabelSize(row)

	def autoTableSizeColumnLabel(self, column):
		"""Sizes the a single column to fit the width of the column label.

		column (int) - The column that will be autosized
							 
		Example Input: autoTableSizeColumnLabel(3)
		"""

		#Size Row
		self.thing.AutoSizeColumnLabelSize(column)

	def setTableRowSize(self, row, size):
		"""Changes the height of a row.

		row (int) - The index of the row
		size (int) - The new height of the row in pixels

		Example Input: setTableRowSize(3, 15)
		"""

		#Set the text color
		self.thing.SetRowSize(row, size)

	def setTableColumnSize(self, column, size):
		"""Changes the width of a column.

		column (int) - The index of the column
		size (int) - The new height of the column in pixels

		Example Input: setTableColumnSize(3, 15)
		"""

		#Set the text color
		self.thing.SetColSize(column, size)

	def setTableRowSizeDefaults(self):
		"""Restores the default heights to all rows.

		Example Input: setTableRowSizeDefaults()
		"""

		#Set the text color
		self.thing.SetRowSizes(wx.grid.GridSizesInfo)

	def setTableColumnSizeDefaults(self):
		"""Restores the default widths to all columns.

		Example Input: setTableColumnSizeDefaults()
		"""

		#Set the text color
		self.thing.SetColSizes(wx.grid.GridSizesInfo)

	#Getters
	def getValue(self, event = None):
		"""Returns what the contextual value is for the object associated with this handle."""

		if (self.type == "Table"):
			value = []
			content = self.thing.GetSelectedCells()
			if (len(content) != 0):
				for row, column in content:
					value.append(self.thing.GetCellValue(row, column)) #(list) - What is in the selected cells

		else:
			warnings.warn("Add {} to getValue() for {}".format(self.type, self.__repr__()), Warning, stacklevel = 2)
			value = None

		return value

	def getIndex(self, event = None):
		"""Returns what the contextual index is for the object associated with this handle."""

		if (self.type == ""):
			pass

		else:
			warnings.warn("Add {} to getIndex() for {}".format(self.type, self.__repr__()), Warning, stacklevel = 2)
			value = None

		return value

	def getAll(self):
		"""Returns all the contextual values for the object associated with this handle."""

		if (self.type == "Table"):
			value = []
			for i in range(self.thing.GetNumberRows()):
				row = []
				for j in range(self.thing.GetNumberCols()):
					row.append(self.thing.GetCellValue(i, j)) #(list) - What is in each cell
				value.append(row)

		else:
			warnings.warn("Add {} to getAll() for {}".format(self.type, self.__repr__()), Warning, stacklevel = 2)
			value = None

		return value

	def onTableCheckCell(self, event, *args, **kwargs):
		"""Returns information about a specific cell on a table."""

		print("Cell Row:     ", event.GetRow())
		print("Cell Column:  ", event.GetCol())
		print("Cell Position:", event.GetPosition())

		event.Skip()

	def onTableDisplayToolTip(self, event, *args, **kwargs):
		"""Displays a tool tip when the mouse moves over the cell."""

		#Get the wxObject
		thing = self.getObjectWithEvent(event)

		#Check where the mouse is
		x, y = wx.grid.CalcUnscrolledPosition(event.GetX(), event.GetY())
		coordinates = wx.grid.XYToCell(x, y)
		currentRow = coordinates[0]
		currentColumn = coordinates[1]

		#Display the tool tip
		for item in args:
			#Unpack Input Variables
			row = item[0] #(int)     - The row of the cell. If None: It will respond to all rows in the given column
			column = item[1] #(int)  - The column of the cell. If None: It will respond to all columns in the given row
			message = item[2] #(str) - What the tool tip message will say

			#Determine if the tool tip should be shown
			if ((row != None) and (column != None)):
				if ((currentRow == row) and (currentColumn == column)):
					thing.SetToolTipString(message)
				else:
					thing.SetToolTipString("")
			elif (row != None):
				if (currentRow == row):
					thing.SetToolTipString(message)
				else:
					thing.SetToolTipString("")
			elif (column != None):
				if (currentColumn == column):
					thing.SetToolTipString(message)
				else:
					thing.SetToolTipString("")
			else:
				thing.SetToolTipString("")

		event.Skip()

	def onTableArrowKeyMove(self, event):
		"""Traverses the cells in the table using the arrow keys."""

		#Get the key that was pressed
		keyCode = event.GetKeyCode()

		#Determine which key was pressed
		if (keyCode == wx.WXK_UP):
			table = self.thing
			table.MoveCursorUp(True)

		elif (keyCode == wx.WXK_DOWN):
			table = self.thing
			table.MoveCursorDown(True)

		elif (keyCode == wx.WXK_LEFT):
			table = self.thing
			table.MoveCursorLeft(True)

		elif (keyCode == wx.WXK_RIGHT):
			table = self.thing
			table.MoveCursorRight(True)

		event.Skip()

	def onTableEditOnEnter(self, event):
		"""Allows the user to enter 'edit cell mode' by pressing enter.
		Special thaks to Fenikso for how to start the editor on https://stackoverflow.com/questions/7976717/enter-key-behavior-in-wx-grid
		"""

		#Get the key that was pressed
		keyCode = event.GetKeyCode()

		#Do not let the key event propigate if it is an enter key
		if ((keyCode != wx.WXK_RETURN) and (keyCode != wx.WXK_NUMPAD_ENTER)):
			event.Skip()
		else:
			### THIS PART IS NOT WORKING YET ###
			### The cursor navigates down after pressing enter in the edior box 
			#Get the table

			# Start the editor
			self.thing.EnableCellEditControl()

			#There is no event.Skip() here to keep the cursor from moving down

	def onTableEditOnClick(self, event, edit):
		"""Allows the user to enter 'edit cell mode' on a single click instead of a double click
		This is currently not working

		tableNumber (int) - What the table is called in the table catalogue
		edit (bool)       - If True: The user will enter 'edit cell mode' on a single click instead of a double click
							If False: The user will enter 'edit cell mode' on a double click instead of a single click

		Example Input: onTableEditOnClick(0, True)
		"""

		### NOT WORKING YET ###
		if (edit):
			#Move editor
			selection = self.getTableCurrentCell()

			#Default to the top left cell if a range is selected
			row, column = selection[0]

			# wx.grid.GridCellEditor(row, column, table)

		event.Skip()

	####################################################################################################
	class TableCellEditor(wx.grid.GridCellEditor):
		"""Used to modify the grid cell editor's behavior.
		Modified code from: https://github.com/wxWidgets/wxPython/blob/master/demo/GridCustEditor.py
		"""

		def __init__(self, parent, downOnEnter = True, debugging = False):
			"""Defines internal variables and arranges how the editor will behave.

			downOnEnter (bool) - Determines what happens to the cursor after the user presses enter
				- If True: The cursor will move down one cell
				- If False: The cursor will not move
			debugging (bool)   - Determines if debug information should be displayed or not
				- If True: Debug information will be printed to the command window

			Example Input: TableCellEditor()
			Example Input: TableCellEditor(debugging = True)
			Example Input: TableCellEditor(downOnEnter = False)
			"""

			#Load in default behavior
			wx.grid.GridCellEditor.__init__(self)

			#Internal variables

			self.parent = parent
			self.downOnEnter = downOnEnter
			self.debugging = debugging
			# self.debugging = True

			#Write debug information
			if (self.debugging):
				print("TableCellEditor.__init__(self = {}, downOnEnter = {}, debugging = {})".format(self, downOnEnter, debugging))

		def Create(self, parent, myId, event):
			"""Called to create the control, which must derive from wx.Control.
			*Must Override*.
			"""

			#Write debug information
			if (self.debugging):
				print("TableCellEditor.Create(self = {}, parent = {}, myId = {}, event = {})".format(self, parent, myId, event))

			#Prepare text control
			styles = ""

			#Check how the enter key is processed
			if (self.downOnEnter):
				style += "|wx.TE_PROCESS_ENTER"

			#Check readOnly
			if (self.parent.getTableCurrentCellReadOnly()):
				styles += "|wx.TE_READONLY"

			#Strip of extra divider
			if (styles != ""):
				if (styles[0] == "|"):
					styles = styles[1:]
			else:
				styles = "wx.DEFAULT"

			#Create text control
			self.myTextControl = wx.TextCtrl(parent, myId, "", style = eval(styles))
			self.myTextControl.SetInsertionPoint(0)
			self.SetControl(self.myTextControl)

			#Handle events
			if (event):
				self.myTextControl.PushEventHandler(event)

		def SetSize(self, rect):
			"""Called to position/size the edit control within the cell rectangle.
			If you don't fill the cell (the rect) then be sure to override
			PaintBackground and do something meaningful there.
			"""

			#Write debug information
			if (self.debugging):
				print("TableCellEditor.SetSize(self = {}, rect = {})".format(self, rect))

			self.myTextControl.SetSize(rect.x, rect.y, rect.width+2, rect.height+2,
								   wx.SIZE_ALLOW_MINUS_ONE)

		def Show(self, show, attr):
			"""Show or hide the edit control. You can use the attr (if not None)
			to set colours or fonts for the control.
			"""

			#Write debug information
			if (self.debugging):
				print("TableCellEditor.Show(self = {}, show = {}, attr = {})".format(self, show, attr))

			wx.grid.GridCellEditor.Show(self, show, attr)

		def PaintBackground(self, rect, attr):
			"""Draws the part of the cell not occupied by the edit control. The
			base  class version just fills it with background colour from the
			attribute. In this class the edit control fills the whole cell so
			don't do anything at all in order to reduce flicker.
			"""

			#Write debug information
			if (self.debugging):
				print("TableCellEditor.PaintBackground(self = {}, rect = {}, attr = {})".format(self, rect, attr))

			self.log.write("TableCellEditor: PaintBackground\n")

		def BeginEdit(self, row, column, grid):
			"""Fetch the value from the table and prepare the edit control
			to begin editing. Set the focus to the edit control.
			*Must Override*
			"""

			#Write debug information
			if (self.debugging):
				print("TableCellEditor.BeginEdit(self = {}, row = {}, column = {}, grid = {})".format(self, row, column, grid))

			self.startValue = grid.GetTable().GetValue(row, column)
			self.myTextControl.SetValue(self.startValue)
			self.myTextControl.SetInsertionPointEnd()
			self.myTextControl.SetFocus()

			self.myTextControl.SetSelection(0, self.myTextControl.GetLastPosition())

		def EndEdit(self, row, column, grid, oldValue):
			"""End editing the cell. This function must check if the current
			value of the editing control is valid and different from thde
			original value (available as oldValue in its string form.)  If
			it has not changed then simply return None, otherwise return
			the value in its string form.
			*Must Override*
			"""

			#Write debug information
			if (self.debugging):
				print("TableCellEditor.EndEdit(self = {}, row = {}, column = {}, grid = {}, oldValue = {})".format(self, row, column, grid, oldValue))

			#Check for read only condition
			if (self.parent.readOnlyCatalogue[row][column]):
				return None

			newValue = self.myTextControl.GetValue()
			if newValue != oldValue:   #self.startValue:
				return newValue
			else:
				return None
			
		def ApplyEdit(self, row, column, grid):
			"""This function should save the value of the control into the
			grid or grid table. It is called only after EndEdit() returns
			a non-None value.
			*Must Override*
			"""

			#Write debug information
			if (self.debugging):
				print("TableCellEditor.ApplyEdit(self = {}, row = {}, column = {}, grid = {})".format(self, row, column, grid))

			value = self.myTextControl.GetValue()
			table = grid.GetTable()
			table.SetValue(row, column, value) # update the table

			self.startValue = ''
			self.myTextControl.SetValue('')

			#Move cursor down
			if (self.downOnEnter):
				table.MoveCursorDown(True)

		def Reset(self):
			"""Reset the value in the control back to its starting value.
			*Must Override*
			"""

			#Write debug information
			if (self.debugging):
				print("TableCellEditor.Reset(self = {})".format(self))

			self.myTextControl.SetValue(self.startValue)
			self.myTextControl.SetInsertionPointEnd()

		def IsAcceptedKey(self, event):
			"""Return True to allow the given key to start editing: the base class
			version only checks that the event has no modifiers. F2 is special
			and will always start the editor.
			"""

			#Write debug information
			if (self.debugging):
				print("TableCellEditor.IsAcceptedKey(self = {}, event = {})".format(self, event))

			## We can ask the base class to do it
			#return super(TableCellEditor, self).IsAcceptedKey(event)

			# or do it ourselves
			return (not (event.ControlDown() or event.AltDown()) and
					event.GetKeyCode() != wx.WXK_SHIFT)

		def StartingKey(self, event):
			"""If the editor is enabled by pressing keys on the grid, this will be
			called to let the editor do something about that first key if desired.
			"""

			#Write debug information
			if (self.debugging):
				print("TableCellEditor.StartingKey(self = {}, event = {})".format(self, event))

			key = event.GetKeyCode()
			char = None
			if key in [ wx.WXK_NUMPAD0, wx.WXK_NUMPAD1, wx.WXK_NUMPAD2, wx.WXK_NUMPAD3, 
						wx.WXK_NUMPAD4, wx.WXK_NUMPAD5, wx.WXK_NUMPAD6, wx.WXK_NUMPAD7, 
						wx.WXK_NUMPAD8, wx.WXK_NUMPAD9
						]:

				char = char = chr(ord('0') + key - wx.WXK_NUMPAD0)

			elif key < 256 and key >= 0 and chr(key) in string.printable:
				char = chr(key)

			if char is not None:
				# For this example, replace the text. Normally we would append it.
				self.myTextControl.AppendText(char)
				# self.myTextControl.SetValue(char)
				self.myTextControl.SetInsertionPointEnd()
			
			event.Skip()

		def StartingClick(self):
			"""If the editor is enabled by clicking on the cell, this method will be
			called to allow the editor to simulate the click on the control if
			needed.
			"""

			#Write debug information
			if (self.debugging):
				print("TableCellEditor.StartingClick(self = {})".format(self))

			pass

		def Destroy(self):
			"""Final Cleanup"""

			#Write debug information
			if (self.debugging):
				print("TableCellEditor.Destroy(self = {})".format(self))

			wx.grid.GridCellEditor.Destroy(self)

		def Clone(self):
			"""Create a new object which is the copy of this one
			*Must Override*
			"""

			#Write debug information
			if (self.debugging):
				print("TableCellEditor.Clone(self = {})".format(self))

			return TableCellEditor(downOnEnter = self.downOnEnter, debugging = self.debugging)
	####################################################################################################

class handle_Sizer(handle_Container_Base):
	"""A handle for working with a wxSizer."""

	def __init__(self):
		"""Initializes defaults."""

		#Initialize inherited classes
		handle_Container_Base.__init__(self)

		#Defaults
		self.myWindow = None
		self.text = None

	def __str__(self):
		"""Gives diagnostic information on the Sizer when it is printed out."""

		output = handle_Container_Base.__str__(self)
		
		if (self.myWindow != None):
			output += "-- window id: {}\n".format(id(self.myWindow))
		return output

	def __enter__(self):
		"""Allows the user to use a with statement to build the GUI."""

		#Error handling
		if (self in self.myWindow.sizersIterating):
			errorMessage = "Only use {} in a while loop once".format(self.__repr__())
			raise SyntaxError(errorMessage)

		#Allow nested while loops to nest their objects
		self.myWindow.sizersIterating[self] = [True, len(self.myWindow.sizersIterating)]

		handle = handle_Container_Base.__enter__(self)

		return handle

	def __exit__(self, exc_type, exc_value, traceback):
		"""Allows the user to use a with statement to build the GUI."""
		
		#Allow nested while loops to nest their objects
		self.myWindow.sizersIterating[self][0] = False

		state = handle_Container_Base.__exit__(self, exc_type, exc_value, traceback)
		if (state != None):
			return state

		#Check for auto-nesting conditions
		myOrder = self.myWindow.sizersIterating[self][1]
		leftOpen = {value[1]: key for key, value in self.myWindow.sizersIterating.items() if (value[0])}

		if (myOrder - 1 in leftOpen):
			if (not self.nested):
				leftOpen[myOrder - 1].nest(self)

	def build(self, argument_catalogue):
		if (self.type == None):
			errorMessage = "Must define sizer type before building"
			raise SyntaxError(errorMessage)

		sizerType = self.type.lower()
		if (sizerType not in ["grid", "flex", "bag", "box", "text", "wrap"]):
			errorMessage = "There is no 'type' {}. The value should be be 'Grid', 'Flex', 'Bag', 'Box', 'Text', or 'Wrap'".format(self.type)
			raise KeyError(errorMessage)

		#Get Default build arguments
		if (sizerType == "grid"):
			sizerFunction = handle_Window.addSizerGrid
		elif (sizerType == "flex"):
			sizerFunction = handle_Window.addSizerGridFlex
		elif (sizerType == "bag"):
			sizerFunction = handle_Window.addSizerGridBag
		elif (sizerType == "box"):
			sizerFunction = handle_Window.addSizerBox
		elif (sizerType == "text"):
			sizerFunction = handle_Window.addSizerText
		else:
			sizerFunction = handle_Window.addSizerWrap
		for item in inspect.signature(sizerFunction).parameters.values():
			if (item.name not in argument_catalogue):
				argument_catalogue[item.name] = item.default

		#Pre Build
		handle_Container_Base.preBuild(self, argument_catalogue)

		#Unpack arguments
		buildSelf, text = self.getArguments(argument_catalogue, ["self", "text"])

		#Set values
		if (isinstance(buildSelf, handle_Window)):
			self.myWindow = buildSelf
		else:
			self.myWindow = buildSelf.myWindow

		#Nest first sizer
		if (isinstance(buildSelf, handle_Window)):
			sizerList = buildSelf.getNested(include = handle_Sizer)
			if (len(sizerList) <= 1):
				#The first sizer added to a window is automatically nested
				self.nested = True
		
		#Create Sizer
		if (sizerType == "grid"):
			rows, columns, rowGap, colGap = self.getArguments(argument_catalogue, ["rows", "columns", "rowGap", "colGap"])
			self.thing = wx.GridSizer(rows, columns, rowGap, colGap)

		else:
			#Determine direction
			vertical = self.getArguments(argument_catalogue, "vertical")
			if (vertical == None):
				direction = wx.BOTH
			elif (vertical):
				direction = wx.VERTICAL
			else:
				direction = wx.HORIZONTAL

			if (sizerType == "box"):
				self.thing = wx.BoxSizer(direction)

			elif (sizerType == "text"):
				self.thing = wx.StaticBoxSizer(wx.StaticBox(self.parent.thing, wx.ID_ANY, text), direction)

			elif (sizerType == "wrap"):
				extendLast = self.getArguments(argument_catalogue, "extendLast")
				if (extendLast):
					flags = "wx.EXTEND_LAST_ON_EACH_LINE"
				else:
					flags = "wx.WRAPSIZER_DEFAULT_FLAGS"

				self.thing = wx.WrapSizer(direction, eval(flags))

			else:
				rows, columns, rowGap, colGap = self.getArguments(argument_catalogue, ["rows", "columns", "rowGap", "colGap"])
				if (sizerType == "flex"):
					self.thing = wx.FlexGridSizer(rows, columns, rowGap, colGap)

				elif (sizerType == "bag"):
					self.thing = wx.GridBagSizer(rows, columns, rowGap, colGap)

					emptySpace = self.getArguments(argument_catalogue, "emptySpace")
					if (emptySpace != None):
						self.thing.SetEmptyCellSize(emptySpace)

				else:
					errorMessage = "Unknown sizer type {} for {}".format(self.type, self.__repr__())
					raise KeyError(errorMessage)

				flexGrid = self.getArguments(argument_catalogue, "flexGrid")
				if (flexGrid):
					self.thing.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)
				else:
					self.thing.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_NONE)
				
				self.thing.SetFlexibleDirection(direction)

		#Update catalogue
		for key, value in locals().items():
			if (key != "self"):
				argument_catalogue[key] = value
		
		#Post Build
		handle_Container_Base.postBuild(self, argument_catalogue)

		#Unpack arguments
		hidden = self.getArguments(argument_catalogue, "hidden")

		#Determine visibility
		if (hidden):
			if (isinstance(self, handle_Sizer)):
				self.addFinalFunction(self.thing.ShowItems, False)
			else:
				self.thing.Hide()

		#Account for nesting in a text sizer
		if (sizerType != "text"):
			if (text != None):
				subHandle = handle_Sizer()
				subHandle.type = "text"

				argument_catalogue = self.arrangeArguments(handle_Window.addSizerText)
				argument_catalogue["self"] = self
				argument_catalogue["text"] = text
				subHandle.build(argument_catalogue)

				self.text = subHandle
				self.text.nest(self)

	#Change Settings
	def growFlexColumn(self, column, proportion = 0):
		"""Allows the column to grow as much as it can.

		column (int)      - The column that will expand
		proportion (int)  - How this column will grow compared to other growable columns
							If all are zero, they will grow equally

		Example Input: growFlexColumn(0)
		"""

		self.checkHandleType("Flex", self.growFlexColumn)

		#Check growability
		if (self.thing.IsColGrowable(column)):
			#The column must be growable. To change the proportion, it's growability must first be removed
			self.thing.RemoveGrowableCol(column)

		#Add attribute
		self.thing.AddGrowableCol(column, proportion)

	def growFlexRow(self, row, proportion = 0):
		"""Allows the row to grow as much as it can.

		row (int)      - The row that will expand
		proportion (int)  - How this row will grow compared to other growable rows
							If all are zero, they will grow equally

		Example Input: growFlexRow(1)
		"""

		self.checkHandleType("Flex", self.growFlexRow)

		#Check growability
		if (self.thing.IsRowGrowable(row)):
			#The row must be growable. To change the proportion, it's growability must first be removed
			self.thing.RemoveGrowableRow(row)

		#Add attribute
		self.thing.AddGrowableRow(row, proportion)

	def growFlexColumnAll(self, proportion = 0):
		"""Allows all the columns to grow as much as they can.

		column (int)      - The column that will expand
		proportion (int)  - How this column will grow compared to other growable columns
							If all are zero, they will grow equally

		Example Input: growFlexColumnAll()
		"""

		self.checkHandleType("Flex", self.growFlexColumnAll)
	
		for column in range(self.thing.GetCols()):
			self.growFlexColumn(column, proportion = proportion)

	def growFlexRowAll(self, proportion = 0):
		"""Allows all the rows to grow as much as they can.

		row (int)      - The row that will expand
		proportion (int)  - How this row will grow compared to other growable rows
							If all are zero, they will grow equally

		Example Input: growFlexRowAll()
		"""

		self.checkHandleType("Flex", self.growFlexRowAll)
		
		for row in range(self.thing.GetRows()):
			self.growFlexRow(row, proportion = proportion)
	
	#Etc
	def nest(self, handle = None, flex = 0, flags = "c1"):
		"""Nests an object inside of this Sizer.

		handle (handle) - What to place in this object
			- Widgets should be passed in as a dictionary

		Example Input: nest(text)
		"""

		#Account for automatic text sizer nesting
		if (isinstance(handle, handle_Sizer)):
			if (isinstance(self, handle_Sizer)):
				sizerType = self.type.lower()
			else:
				sizerType = handle.type.lower()

			if (sizerType != "text"):
				if (handle.text != None):
					handle = handle.text

		#Do not nest already nested objects
		if (handle.nested):
			errorMessage = "Cannot nest objects twice"
			raise SyntaxError(errorMessage)

		#Configure Flags
		flags, position, border = self.getItemMod(flags)

		#Perform Nesting
		if (isinstance(handle, handle_Widget_Base)):
			#Nesting a widget
			self.thing.Add(handle.thing, int(flex), eval(flags), border)
		
		elif (isinstance(handle, handle_NotebookPage)):
			self.thing.Add(handle.mySizer.thing, int(flex), eval(flags), border)
		
		elif (isinstance(handle, handle_Sizer)):
			self.thing.Add(handle.thing, int(flex), eval(flags), border)
		
		elif (isinstance(handle, handle_Splitter)):
			self.thing.Add(handle.thing, int(flex), eval(flags), border)

		elif (isinstance(handle, handle_Notebook)):
			self.thing.Add(handle.thing, int(flex), eval(flags), border)

		else:
			warnings.warn("Add {} to nest() for {}".format(handle.__class__, self.__repr__()), Warning, stacklevel = 2)
			return

		
		handle.nested = True
		handle.nestingAddress = self.nestingAddress + [id(self)]
		self.setAddressValue(handle.nestingAddress + [id(handle)], {None: handle})

	def addFinalFunction(self, *args, **kwargs):
		"""Overload for addFinalFunction in handle_Window()."""

		self.myWindow.addFinalFunction(*args, **kwargs)

	def addKeyPress(self, *args, **kwargs):
		"""Overload for addKeyPress in handle_Window()."""

		self.myWindow.addKeyPress(*args, **kwargs)

	#Add Widgets
	def addText(self, text = "", wrap = None, ellipsize = False, alignment = None,
		size = None, bold = False, italic = False, color = None, family = None, 

		label = None, hidden = False, enabled = True, selected = False, 
		flex = 0, flags = "c1", parent = None, handle = None):
		"""Adds text to the grid.
		If you want to update this text, you will need to run the function setObjectValue() or setObjectValueWithLabel().
		If you provide a variable to this function and that variable changes- the text on the GUI will not update.
		It must be told to do so explicitly by using one of the functions mentioned above.
		Note: If you change the text, any word wrap will be removed. To wrap it again, call the function textWrap().

		text (str)    - The text that will be added to the next cell on the grid.
		flags (list)    - A list of strings for which flag to add to the sizer. Can be just a string if only 1 flag is given
		label (any)   - What this is catalogued as
		selected (bool) - If True: This is the default thing selected
		hidden (bool)   - If True: The widget is hidden from the user, but it is still created
		wrap (int)      - How many pixels wide the line will be before it wraps. If negative: no wrapping is done
		flex (int)      - Only for Box Sizers:
			~ If 0: The cell will not grow or shrink; acts like a Flex Grid cell
			~ If not 0: The cell will grow and shrink to match the cells that have the same number
		
		ellipsize (bool) - Determines what happens if the text exceeds the alloted space
			- If True: Will cut the text with a '...' at the end
			- If False: Will adjust the alloted space to fit the text
			- If None: Will adjust the alloted space to fit the text
			- If 0: Will cut the text with a '...' at the beginning
			- If 1: Will cut the text with a '...' in the middle
			- If 2: Will cut the text with a '...' at the end
		alignment (int) - Determines how the text is aligned in its alloted space
			- If True: Will align text to the left
			- If False: Will align text to the center
			- If None: Will align text to the center
			- If 0: Will align text to the left
			- If 1: Will align text to the center
			- If 2: Will align text to the right

		size (int)    - The font size of the text  
		bold (bool)   - If True: the font will be bold
		italic (bool) - If True: the font will be italicized
		color (str)   - The color of the text. Can be an RGB tuple (r, g, b) or hex value
		family (str)  - What font family it is.
			~ "times new roman"         

		Example Input: addText()
		Example Input: addText(text = "Lorem Ipsum")
		Example Input: addText(text = "Change Me", label = "changableText")
		Example Input: addText(text = "Part Type", flags = "c2")
		Example Input: addText(text = "Part Type", flags = ["at", "c2"])
		Example Input: addText(text = "This line will wrap", wrap = 10)
		Example Input: addText(text = "BIG TEXT", bold = True, size = 72, color = "red")
		Example Input: addText(text = "Really long text", ellipsize = True)
		Example Input: addText(text = "Really long text", ellipsize = 0)
		Example Input: addText(text = "Really long text", ellipsize = 1)
		"""

		handle = handle_WidgetText()
		handle.preBuild(locals())

		handle.type = "Text"

		#Ensure correct format
		if (not isinstance(text, str)):
			text = "{}".format(text)

		#Apply Settings
		if (alignment != None):
			if (isinstance(alignment, bool)):
				if (alignment):
					style = "wx.ALIGN_LEFT"
				else:
					style = "wx.ALIGN_CENTRE"
			elif (alignment == 0):
				style = "wx.ALIGN_LEFT"
			elif (alignment == 1):
				style = "wx.ALIGN_RIGHT"
			else:
				style = "wx.ALIGN_CENTRE"
		else:
			style = "wx.ALIGN_CENTRE"

		if (ellipsize != None):
			if (isinstance(ellipsize, bool)):
				if (ellipsize):
					style += "|wx.ST_ELLIPSIZE_END"
			elif (ellipsize == 0):
				style += "|wx.ST_ELLIPSIZE_START"
			elif (ellipsize == 1):
				style += "|wx.ST_ELLIPSIZE_MIDDLE"
			else:
				style += "|wx.ST_ELLIPSIZE_END"

		#Create the thing to put in the grid
		handle.thing = wx.StaticText(handle.parent.thing, label = text, style = eval(style))

		# font = self.makeFont(size = size, bold = bold, italic = italic, color = color, family = family)
		# handle.thing.SetFont(font)

		# if (wrap != None):
		# 	if (wrap > 0):
		# 		handle.wrapText(wrap)

		handle.postBuild(locals())

		return handle

	def addHyperlink(self, text = "", myWebsite = "",

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, 

		label = None, hidden = False, enabled = True, selected = False, 
		flex = 0, flags = "c1", parent = None, handle = None):
		"""Adds a hyperlink text to the next cell on the grid.

		text (str)            - What text is shown
		myWebsite (str)         - The address of the website to open
		myFunction (str)        - What function will be ran when the link is clicked
		flags (list)            - A list of strings for which flag to add to the sizer
		label (any)           - What this is catalogued as
		myFunctionArgs (any)    - The arguments for 'myFunction'
		myFunctionKwargs (any)  - The keyword arguments for 'myFunction'function

		Example Input: addHyperlink("wxFB Website", "http://www.wxformbuilder.org", "siteVisited")
		"""

		handle = handle_WidgetText()
		handle.preBuild(locals())

		handle.type = "Hyperlink"

		#Apply settings
		# wx.adv.HL_ALIGN_LEFT: Align the text to the left.
		# wx.adv.HL_ALIGN_RIGHT: Align the text to the right. This style is not supported under Windows XP but is supported under all the other Windows versions.
		# wx.adv.HL_ALIGN_CENTRE: Center the text (horizontally). This style is not supported by the native MSW implementation used under Windows XP and later.
		# wx.adv.HL_CONTEXTMENU: Pop up a context menu when the hyperlink is right-clicked. The context menu contains a “Copy URL” menu item which is automatically handled by the hyperlink and which just copies in the clipboard the URL (not the label) of the control.
		# wx.adv.HL_DEFAULT_STYLE: The default style for wx.adv.HyperlinkCtrl: BORDER_NONE|wxHL_CONTEXTMENU|wxHL_ALIGN_CENTRE.
		styles = "wx.adv.HL_DEFAULT_STYLE"


		#Create the thing to put in the grid
		handle.thing = wx.adv.HyperlinkCtrl(handle.parent.thing, label = text, url = myWebsite, style = eval(styles))

		#Apply colors
		# SetHoverColour
		# SetNormalColour
		# SetVisitedColour

		#Bind the function(s)
		self.betterBind(wx.adv.EVT_HYPERLINK, handle.thing, myFunction, myFunctionArgs, myFunctionKwargs)

		handle.postBuild(locals())

		return handle

	def addEmpty(self, 

		label = None, hidden = False, enabled = True, selected = False, 
		flex = 0, flags = ["ex", "ba"], parent = None, handle = None):
		"""Adds an empty space to the next cell on the grid.

		label (any)     - What this is catalogued as
		selected (bool)   - If True: This is the default thing selected
		hidden (bool)     - If True: The widget is hidden from the user, but it is still created

		Example Input: addEmpty()
		Example Input: addEmpty(label = "spacer")
		"""

		handle = handle_WidgetText()
		handle.preBuild(locals())

		handle.type = "Empty"

		#Create the thing to put in the grid
		handle.thing = wx.StaticText(handle.parent.thing, label = wx.EmptyString)
		handle.wrapText(-1)

		handle.postBuild(locals())

		return handle

	def addLine(self, vertical = False,

		label = None, hidden = False, enabled = True, selected = False, 
		flex = 0, flags = ["ex", "ba"], parent = None, handle = None):
		"""Adds a simple line to the window.
		It can be horizontal or vertical.

		vertical (bool)   - Whether the line is vertical or horizontal
		flags (list)      - A list of strings for which flag to add to the sizer
		label (any)     - What this is catalogued as
		hidden (bool)     - If True: The widget is hidden from the user, but it is still created

		Example Input: addLine()
		Example Input: addLine(vertical = True)
		"""

		handle = handle_Widget_Base()
		handle.preBuild(locals())

		handle.type = "Line"
		
		#Apply settings
		if (vertical):
			direction = wx.LI_VERTICAL
		else:
			direction = wx.LI_HORIZONTAL

		#Create the thing to put in the grid
		handle.thing = wx.StaticLine(handle.parent.thing, style = direction)

		handle.postBuild(locals())

		return handle

	def addListDrop(self, choices = [], default = None, alphabetic = False,

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, 

		label = None, hidden = False, enabled = True, selected = False, 
		flex = 0, flags = "c1", parent = None, handle = None):
		"""Adds a dropdown list with choices to the next cell on the grid.

		choices (list)          - A list of the choices as strings
		myFunction (str)        - The function that is ran when the user chooses something from the list. If a list is given, each function will be bound.
		flags (list)            - A list of strings for which flag to add to the sizer
		label (any)           - What this is catalogued as
		myFunctionArgs (any)    - The arguments for 'myFunction'
		myFunctionKwargs (any)  - The keyword arguments for 'myFunction'function
		default (int)           - Which item in the droplist is selected
			- If a string is given, it will select the first item in the list that matches that string. If noting matches, it will default to the first element
		enabled (bool)          - If True: The user can interact with this
		alphabetic (bool)      - Determines if the list is automatically sorted alphabetically
			- If True: The list is sorted alphabetically
			- If False: The list is presented in the order given

		Example Input: addListDrop(choices = ["Lorem", "Ipsum", "Dolor"])
		Example Input: addListDrop(choices = ["Lorem", "Ipsum", "Dolor"], label = "chosen")
		Example Input: addListDrop(choices = ["Lorem", "Ipsum", "Dolor"], alphabetic = True)
		"""

		handle = handle_WidgetList()
		handle.preBuild(locals())

		handle.type = "ListDrop"

		#Ensure that the choices given are a list or tuple
		if ((type(choices) != list) and (type(choices) != tuple)):
			choices = list(choices)

		#Ensure that the choices are all strings
		choices = [str(item) for item in choices]

		#Apply Settings
		if (alphabetic):
			style = wx.CB_SORT
		else:
			style = 0

		#Create the thing to put in the grid
		handle.thing = wx.Choice(handle.parent.thing, choices = choices, style = style)
		
		#Set default position
		if (type(default) == str):
			if (default in choices):
				default = choices.index(default)

		if (default == None):
			default = 0

		handle.thing.SetSelection(default)

		#Bind the function(s)
		self.betterBind(wx.EVT_CHOICE, handle.thing, myFunction, myFunctionArgs, myFunctionKwargs)

		handle.postBuild(locals())

		return handle


	def addListFull(self, choices = [], default = False, singleSelect = False, editable = False,

		report = False, columns = 1, columnNames = {},
		drag = False, dragDelete = False, dragCopyOverride = False, 
		allowExternalAppDelete = True, dragLabel = None, drop = False, dropIndex = 0,

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, 
		preEditFunction = None, preEditFunctionArgs = None, preEditFunctionKwargs = None, 
		postEditFunction = None, postEditFunctionArgs = None, postEditFunctionKwargs = None, 
		preDragFunction = None, preDragFunctionArgs = None, preDragFunctionKwargs = None, 
		postDragFunction = None, postDragFunctionArgs = None, postDragFunctionKwargs = None, 
		preDropFunction = None, preDropFunctionArgs = None, preDropFunctionKwargs = None, 
		postDropFunction = None, postDropFunctionArgs = None, postDropFunctionKwargs = None, 
		dragOverFunction = None, dragOverFunctionArgs = None, dragOverFunctionKwargs = None, 

		label = None, hidden = False, enabled = True, selected = False, 
		flex = 0, flags = "c1", parent = None, handle = None):
		"""Adds a full list with choices to the next cell on the grid.
		https://wxpython.org/Phoenix/docs/html/wx.ListCtrl.html

		choices (list - A list of the choices as strings
			- If 'report' is True: Can be given as either [[row 1 column 1, row 2 column 1], [row 1 column 2, row 2 column 2]] or {column name 1: [row 1, row 2], column name 2: [row 1, row 2]}
				- If an integer is given instead of a string for the column name, it will use that as the column index
				- If more than one column have the same header, it will be added to the left most one
		label (any) - What this is catalogued as
		flags (list)  - A list of strings for which flag to add to the sizer

		default (bool)      - If True: This is the default thing selected
		enabled (bool)      - If True: The user can interact with this
		singleSelect (bool) - Determines how many things the user can select
			- If True: The user can only select one thing
			- If False: The user can select multiple things using the shift key
		editable (bool)     - Determines if the user can edit the first item in the list
			- If True: The user can edit all items in the list

		report (bool)      - Determines how the list is set up
			- If True: The list will be arranged in a grid
			- If False: Rows and columns will be dynamically calculated
		columns (int)      - How many columns the report will have
		columnNames (dict) - What the column headers will say. If not given, the column will be blank. {row index: name}
		
		drag (bool)       - If True: The user can drag text away from this list
		dragDelete (bool) - If True: Text dragged away from this list will be deleted after dropping
		dragLabel (bool)  - What the text dragging object being dropped into this list is called in the idCatalogue
		drop (bool)       - If True: Text dropped on this list will be inserted
		dropIndex (int)   - Where to insert the text dropped into this list. Works like a python list index
		
		dragCopyOverride (bool)       - If False: Holding [ctrl] will copy the text, not delete it
		allowExternalAppDelete (bool) - If False: The text will not be deleted if it is dragged into an external application 
		
		myFunction (str)       - The function that is ran when the user chooses something from the list
		myFunctionArgs (any)   - The arguments for 'myFunction'
		myFunctionKwargs (any) - The keyword arguments for 'myFunction'function
		
		preEditFunction (str)       - The function that is ran when the user edits something from the list
		preEditFunctionArgs (any)   - The arguments for 'preEditFunction'
		preEditFunctionKwargs (any) - The keyword arguments for 'preEditFunction'function
		
		postEditFunction (str)       - The function that is ran when the user edits something from the list
		postEditFunctionArgs (any)   - The arguments for 'postEditFunction'
		postEditFunctionKwargs (any) - The keyword arguments for 'postEditFunction'function
		
		preDragFunction (str)       - The function that is ran when the user tries to drag something from the list; before it begins to drag
		preDragFunctionArgs (any)   - The arguments for 'preDragFunction'
		preDragFunctionKwargs (any) - The keyword arguments for 'preDragFunction'function
		
		postDragFunction (str)       - The function that is ran when the user tries to drag something from the list; after it begins to drag
		postDragFunctionArgs (any)   - The arguments for 'postDragFunction'
		postDragFunctionKwargs (any) - The keyword arguments for 'postDragFunction'function
		
		preDropFunction (str)       - The function that is ran when the user tries to drop something from the list; before it begins to drop
		preDropFunctionArgs (any)   - The arguments for 'preDropFunction'
		preDropFunctionKwargs (any) - The keyword arguments for 'preDropFunction'function
		
		postDropFunction (str)       - The function that is ran when the user tries to drop something from the list; after it drops
		postDropFunctionArgs (any)   - The arguments for 'postDropFunction'
		postDropFunctionKwargs (any) - The keyword arguments for 'postDropFunction'function
		
		dragOverFunction (str)       - The function that is ran when the user drags something over this object
		dragOverFunctionArgs (any)   - The arguments for 'dragOverFunction'
		dragOverFunctionKwargs (any) - The keyword arguments for 'dragOverFunction'function
		

		Example Input: addListFull(["Lorem", "Ipsum", "Dolor"], 0)
		Example Input: addListFull(["Lorem", "Ipsum", "Dolor"], 0, myFunction = self.onChosen)

		Example Input: addListFull(["Lorem", "Ipsum", "Dolor"], 0, report = True)
		Example Input: addListFull([["Lorem", "Ipsum"], ["Dolor"]], 0, report = True, columns = 2)
		Example Input: addListFull([["Lorem", "Ipsum"], ["Dolor"]], 0, report = True, columns = 2, columnNames = {0: "Sit", 1: "Amet"})
		Example Input: addListFull({"Sit": ["Lorem", "Ipsum"], "Amet": ["Dolor"]], 0, report = True, columns = 2, columnNames = {0: "Sit", 1: "Amet"})
		Example Input: addListFull({"Sit": ["Lorem", "Ipsum"], 1: ["Dolor"]], 0, report = True, columns = 2, columnNames = {0: "Sit"})

		Example Input: addListFull([["Lorem", "Ipsum"], ["Dolor"]], 0, report = True, columns = 2, columnNames = {0: "Sit", 1: "Amet"}, editable = True)

		Example Input: addListFull(["Lorem", "Ipsum", "Dolor"], 0, drag = True)
		Example Input: addListFull(["Lorem", "Ipsum", "Dolor"], 0, drag = True, dragDelete = True)
		Example Input: addListFull(["Lorem", "Ipsum", "Dolor"], 0, drag = True, dragDelete = True, allowExternalAppDelete = False)

		Example Input: addListFull(["Lorem", "Ipsum", "Dolor"], 0, drop = True)
		Example Input: addListFull(["Lorem", "Ipsum", "Dolor"], 0, drop = True, drag = True)

		Example Input: addListFull(["Lorem", "Ipsum", "Dolor"], 0, drop = True, dropIndex = 2)
		Example Input: addListFull(["Lorem", "Ipsum", "Dolor"], 0, drop = True, dropIndex = -1)
		Example Input: addListFull(["Lorem", "Ipsum", "Dolor"], 0, drop = True, dropIndex = -2)

		Example Input: addListFull(["Lorem", "Ipsum", "Dolor"], 0, drop = True, dropLabel = "text", preDropFunction = self.checkText)
		"""

		handle = handle_WidgetList()
		handle.preBuild(locals())

		handle.type = "ListFull"

		#Determine style
		if (report):
			styleList = "wx.LC_REPORT"
		else:
			styleList = "wx.LC_LIST" #Auto calculate columns and rows

		if (singleSelect):
			styleList += "|wx.LC_SINGLE_SEL" #Default: Can select multiple with shift

		#Determine if it is editable or not
		mixin_editable = False
		if (type(editable) != dict):
			if (editable):
				mixin_editable = True
				styleList += "|wx.LC_EDIT_LABELS" #Editable

		elif (len(editable) != 0):
			mixin_editable = True
			styleList += "|wx.LC_EDIT_LABELS" #Editable

		#Create the thing to put in the grid
		if (mixin_editable):
			handle.thing = handle.ListFull_Editable(handle.parent.thing, style = styleList)
			handle.thing.editable = editable
		else:
			handle.thing = wx.ListCtrl(handle.parent.thing, style = eval(styleList))

		#Error Check
		if (columns == 1):
			if ((type(choices) == list) or (type(choices) == tuple)):
				if (len(choices) != 0):
					if ((type(choices[0]) != list) and ((type(choices[0]) != tuple))):
						choices = [choices]

		#Add Items
		handle.setValue(choices)#, columns = columns, columnNames = columnNames)

		#Determine if it's contents are dragable
		if (drag):
			handle.dragable = True
			self.betterBind(wx.EVT_LIST_BEGIN_DRAG, handle.thing, handle.onDragList_beginDragAway, None, 
				{"label": dragLabel, "deleteOnDrop": dragDelete, "overrideCopy": dragCopyOverride, "allowExternalAppDelete": allowExternalAppDelete})
			
			handle.preDragFunction = preDragFunction
			handle.preDragFunctionArgs = preDragFunctionArgs
			handle.preDragFunctionKwargs = preDragFunctionKwargs

			handle.postDragFunction = postDragFunction
			handle.postDragFunctionArgs = postDragFunctionArgs
			handle.postDragFunctionKwargs = postDragFunctionKwargs

		#Determine if it accepts dropped items
		if (drop):
			handle.myDropTarget = handle.DragTextDropTarget(handle.thing, dropIndex,
				preDropFunction = preDropFunction, preDropFunctionArgs = preDropFunctionArgs, preDropFunctionKwargs = preDropFunctionKwargs, 
				postDropFunction = postDropFunction, postDropFunctionArgs = postDropFunctionArgs, postDropFunctionKwargs = postDropFunctionKwargs,
				dragOverFunction = dragOverFunction, dragOverFunctionArgs = dragOverFunctionArgs, dragOverFunctionKwargs = postDropFunctionKwargs)
			handle.thing.SetDropTarget(handle.myDropTarget)

		#Bind the function(s)
		# self.betterBind(wx.EVT_LISTBOX, handle.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		if (myFunction != None):
			self.betterBind(wx.EVT_LIST_ITEM_SELECTED, handle.thing, myFunction, myFunctionArgs, myFunctionKwargs)

		if (preEditFunction):
			self.betterBind(wx.EVT_LIST_BEGIN_LABEL_EDIT, handle.thing, preEditFunction, preEditFunctionArgs, preEditFunctionKwargs)
		if (postEditFunction):
			self.betterBind(wx.EVT_LIST_END_LABEL_EDIT, handle.thing, postEditFunction, postEditFunctionArgs, postEditFunctionKwargs)

		handle.postBuild(locals())

		return handle

	def addSlider(self, myMin = 0, myMax = 100, myInitial = 0, vertical = False,

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None,

		label = None, hidden = False, enabled = True, selected = False, 
		flex = 0, flags = "c1", parent = None, handle = None):
		"""Adds a slider bar to the next cell on the grid.

		myMin (int)             - The minimum value of the slider bar
		myMax (int)             - The maximum value of the slider bar
		myInitial (int)         - The initial value of the slider bar's position
		myFunction (str)        - The function that is ran when the user enters text and presses enter
		flags (list)            - A list of strings for which flag to add to the sizer
		label (any)           - What this is catalogued as
		myFunctionArgs (any)    - The arguments for 'myFunction'
		myFunctionKwargs (any)  - The keyword arguments for 'myFunction'function

		Example Input: addSlider(0, 100, 50, "initialTemperature")
		"""

		handle = handle_WidgetInput()
		handle.preBuild(locals())

		handle.type = "Slider"

		#Apply settings
		if (vertical):
			styles = "wx.SL_HORIZONTAL"
		else:
			styles = "wx.SL_VERTICAL"

		# wx.SL_MIN_MAX_LABELS: Displays minimum, maximum labels (new since wxWidgets 2.9.1).
		# wx.SL_VALUE_LABEL: Displays value label (new since wxWidgets 2.9.1).
		# wx.SL_LABELS: Displays minimum, maximum and value labels (same as wx.SL_VALUE_LABEL and wx.SL_MIN_MAX_LABELS together).
		
		# wx.SL_LEFT: Displays ticks on the left and forces the slider to be vertical.
		# wx.SL_RIGHT: Displays ticks on the right and forces the slider to be vertical.
		# wx.SL_TOP: Displays ticks on the top.
		# wx.SL_BOTTOM: Displays ticks on the bottom (this is the default).

		# wx.SL_SELRANGE: Allows the user to select a range on the slider. Windows only.
		# wx.SL_INVERSE: Inverses the minimum and maximum endpoints on the slider. Not compatible with wx.SL_SELRANGE.

		#Create the thing to put in the grid
		handle.thing = wx.Slider(handle.parent.thing, value = myInitial, minValue = myMin, maxValue = myMax, style = eval(styles))

		#Bind the function(s)
		if (myFunction != None):
			self.betterBind(wx.EVT_SCROLL_CHANGED, handle.thing, myFunction, myFunctionArgs, myFunctionKwargs)

		# EVT_SCROLL_TOP
		# EVT_SCROLL_BOTTOM
		# EVT_SCROLL_LINEUP
		# EVT_SCROLL_LINEDOWN
		# EVT_SCROLL_PAGEUP
		# EVT_SCROLL_PAGEDOWN
		# EVT_SCROLL_THUMBTRACK
		# EVT_SCROLL_THUMBRELEASE

		handle.postBuild(locals())

		return handle
	
	def addInputBox(self, text = None, maxLength = None, 
		password = False, alpha = False, readOnly = False, tab = True, wrap = None, ipAddress = False,
		
		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, 
		enterFunction = None, enterFunctionArgs = None, enterFunctionKwargs = None, 
		postEditFunction = None, postEditFunctionArgs = None, postEditFunctionKwargs = None,  
		preEditFunction = None, preEditFunctionArgs = None, preEditFunctionKwargs = None,  

		label = None, hidden = False, enabled = True, selected = False, 
		flex = 0, flags = "c1", parent = None, handle = None):
		"""Adds an input box to the next cell on the grid.

		myFunction (str)       - The function that is ran when the user enters text
		flags (list)           - A list of strings for which flag to add to the sizer
		label (any)          - What this is catalogued as
		myFunctionArgs (any)   - The arguments for 'myFunction'
		myFunctionKwargs (any) - The keyword arguments for 'myFunction'
		text (str)             - What is initially in the box
		maxLength (int)        - If not None: The maximum length of text that can be added
		
		selected (bool)  - If True: This is the default thing selected
		enabled (bool)   - If True: The user can interact with this
		hidden (bool)    - If True: The widget is hidden from the user, but it is still created
		password (bool)  - If True: The text within is shown as dots
		alpha (bool)     - If True: The items will be sorted alphabetically
		readOnly (bool)  - If True: The user cannot change the text
		tab (bool)       - If True: The 'Tab' key will move the focus to the next widget
		wrap (int)       - How many pixels wide the line will be before it wraps. 
		  If None: no wrapping is done
		  If positive: Will not break words
		  If negative: Will break words
		ipAddress (bool) - If True: The input will accept and understand the semantics of an ip address

		enterFunction (str)       - The function that is ran when the user presses enter while in the input box
		enterFunctionArgs (any)   - The arguments for 'enterFunction'
		enterFunctionKwargs (any) - the keyword arguments for 'enterFunction'

		postEditFunction (str)       - The function that is ran after the user clicks out (or tabs out, moves out, etc.) of the input box
		postEditFunctionArgs (any)   - The arguments for 'postEditFunction'
		postEditFunctionKwargs (any) - the keyword arguments for 'postEditFunction'

		preEditFunction (str)       - The function that is ran after the user clicks into (or tabs into, moves into, etc.) the input box
		preEditFunctionArgs (any)   - The arguments for 'preEditFunction'
		preEditFunctionKwargs (any) - the keyword arguments for 'preEditFunction'


		Example Input: addInputBox("initialTemperature", 0)
		Example Input: addInputBox("connect", 0, text = "127.0.0.0", ipAddress = True)
		"""

		handle = handle_WidgetInput()
		handle.preBuild(locals())

		handle.type = "InputBox"

		#Prepare style attributes
		styles = ""
		if (password):
			styles += "|wx.TE_PASSWORD"

		if (alpha):
			styles += "|wx.CB_SORT"

		if (readOnly):
			styles += "|wx.TE_READONLY"

		if (tab):
			#Interpret 'Tab' as 4 spaces
			styles += "|wx.TE_PROCESS_TAB"

		if (wrap != None):
			if (wrap > 0):
				styles += "|wx.TE_MULTILINE|wx.TE_WORDWRAP"
			else:
				styles += "|wx.TE_CHARWRAP|wx.TE_MULTILINE"

		# if (enterFunction != None):
			#Interpret 'Enter' as \n
		#   styles += "|wx.TE_PROCESS_ENTER"

		#styles = "|wx.EXPAND"

		#Strip of extra divider
		if (styles != ""):
			if (styles[0] == "|"):
				styles = styles[1:]
		else:
			styles = "wx.DEFAULT"

		#Account for empty text
		if (text == None):
			text = wx.EmptyString

		#Create the thing to put in the grid
		if (ipAddress):
			handle.thing = wx.lib.masked.ipaddrctrl.IpAddrCtrl(handle.parent.thing, wx.ID_ANY, style = eval(styles))

			if (text != wx.EmptyString):
				handle.thing.SetValue(text)
		else:
			handle.thing = wx.TextCtrl(handle.parent.thing, value = text, style = eval(styles))

			#Set maximum length
			if (maxLength != None):
				handle.thing.SetMaxLength(maxLength)

		#flags += "|wx.RESERVE_SPACE_EVEN_IF_HIDDEN"

		#Bind the function(s)
		#self.betterBind(wx.EVT_CHAR, handle.thing, enterFunction, enterFunctionArgs, enterFunctionKwargs)
		#self.betterBind(wx.EVT_KEY_UP, handle.thing, self.testFunction, myFunctionArgs, myFunctionKwargs)
		if (enterFunction != None):
			self.keyBind("enter", handle.thing, enterFunction, enterFunctionArgs, enterFunctionKwargs)
		
		self.betterBind(wx.EVT_TEXT, handle.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		
		if (postEditFunction != None):
			self.betterBind(wx.EVT_KILL_FOCUS, handle.thing, postEditFunction, postEditFunctionArgs, postEditFunctionKwargs)
		
		if (preEditFunction != None):
			self.betterBind(wx.EVT_SET_FOCUS, handle.thing, preEditFunction, preEditFunctionArgs, preEditFunctionKwargs)

		handle.postBuild(locals())

		return handle
	
	def addInputSearch(self, text = None, 

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, 
		searchFunction = None, searchFunctionArgs = None, searchFunctionKwargs = None, 
		cancelFunction = None, cancelFunctionArgs = None, cancelFunctionKwargs = None, 

		label = None, hidden = False, enabled = True, selected = False, 
		flex = 0, flags = "c1", parent = None, handle = None):
		"""Adds an input box to the next cell on the grid.

		myFunction (str)       - The function that is ran when the user enters text and presses enter
		flags (list)           - A list of strings for which flag to add to the sizer
		label (any)          - What this is catalogued as
		myFunctionArgs (any)   - The arguments for 'myFunction'
		myFunctionKwargs (any) - The keyword arguments for 'myFunction'function
		text (str)             - What is initially in the box
		
		searchFunction (str)       - If provided, this is what will be ran when the search button to the left is pressed
		searchFunctionArgs (any)   - The arguments for 'searchFunction'
		searchFunctionKwargs (any) - The keyword arguments for 'searchFunction'function
		cancelFunction (str)       - If provided, this is what will be ran when the cancel button to the right is pressed
		cancelFunctionArgs (any)   - The arguments for 'cancelFunction'
		cancelFunctionKwargs (any) - The keyword arguments for 'cancelFunction'function
		
		selected (bool)         - If True: This is the default thing selected
		enabled (bool)          - If True: The user can interact with this

		Example Input: addInputSearch("initialTemperature")
		"""

		handle = handle_WidgetInput()
		handle.preBuild(locals())

		handle.type = "InputSearch"

		#Create the thing to put in the grid
		handle.thing = wx.SearchCtrl(handle.parent.thing, value = wx.EmptyString, style = 0)

		#Determine if additional features are enabled
		if (searchFunction != None):
			handle.thing.ShowSearchButton(True)
		if (cancelFunction != None):
			handle.thing.ShowCancelButton(True)

		#Bind the function(s)
		if (searchFunction != None):
			self.betterBind(wx.EVT_SEARCHCTRL_SEARCH_BTN, handle.thing, searchFunction, searchFunctionArgs, searchFunctionKwargs)
		if (cancelFunction != None):
			self.betterBind(wx.EVT_SEARCHCTRL_CANCEL_BTN, handle.thing, cancelFunction, cancelFunctionArgs, cancelFunctionKwargs)
		self.betterBind(wx.EVT_TEXT_ENTER, handle.thing, myFunction, myFunctionArgs, myFunctionKwargs)

		handle.postBuild(locals())

		return handle
	
	def addInputSpinner(self, myMin = 0, myMax = 100, myInitial = 0, size = wx.DefaultSize, maxSize = None, minSize = None,
		increment = None, digits = None, useFloat = False, readOnly = False,

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, 
		changeTextFunction = True, changeTextFunctionArgs = None, changeTextFunctionKwargs = None,

		label = None, hidden = False, enabled = True, selected = False, 
		flex = 0, flags = "c1", parent = None, handle = None):
		"""Adds a spin control to the next cell on the grid. This is an input box for numbers.

		myMin (int)       - The minimum value of the input spinner
		myMax (int)       - The maximum value of the input spinner
		myInitial (int)   - The initial value of the input spinner's position
		myFunction (str)  - The function that is ran when the user scrolls through the numbers
		flags (list)      - A list of strings for which flag to add to the sizer
		label (any)     - What this is catalogued as

		maxSize (tuple)   - If not None: The maximum size that the input spinner can be in pixels in the form (x, y) as integers
		minSize (tuple)   - If not None: The minimum size that the input spinner can be in pixels in the form (x, y) as integers
		increment (float) - If not None: Will increment by this value
		digits (float)    - If not None: Will show this many digits past the decimal point. Only applies if 'useFloat' is True

		useFloat (bool) - If True: Will increment decimal numbers instead of integers
		readOnly (bool) - If True: The user will not be able to change the value
		
		myFunctionArgs (any)           - The arguments for 'myFunction'
		myFunctionKwargs (any)         - The keyword arguments for 'myFunction'function
		changeTextFunction (str)       - The function that is ran when the user changes the text in the box directly. If True: Will be the same as myFunction
		changeTextFunctionArgs (any)   - The arguments for 'changeTextFunction'
		changeTextFunctionKwargs (any) - The key word arguments for 'changeTextFunction'
		

		Example Input: addInputSpinner(0, 100, 50, "initialTemperature")
		Example Input: addInputSpinner(0, 100, 50, "initialTemperature", maxSize = (100, 100))
		"""

		handle = handle_WidgetInput()
		handle.preBuild(locals())

		handle.type = "InputSpinner"

		# wx.SP_ARROW_KEYS: The user can use arrow keys to change the value.
		# wx.SP_WRAP: The value wraps at the minimum and maximum.
		styles = "wx.SP_ARROW_KEYS|wx.SP_WRAP"

		#Create the thing to put in the grid
		if (useFloat):
			style = "wx.lib.agw.floatspin.FS_LEFT"
			if (readOnly):
				style += "|wx.lib.agw.floatspin.FS_READONLY"

			if (increment == None):
				increment = 0.1

			if (digits == None):
				digits = 1

			handle.thing = wx.lib.agw.floatspin.FloatSpin(handle.parent.thing, wx.ID_ANY, wx.DefaultPosition, size, wx.SP_ARROW_KEYS|wx.SP_WRAP, myInitial, myMin, myMax, increment, digits, eval(style))
		else:
			if (increment != None):
				style = "wx.lib.agw.floatspin.FS_LEFT"
				handle.thing = wx.lib.agw.floatspin.FloatSpin(handle.parent.thing, wx.ID_ANY, wx.DefaultPosition, size, wx.SP_ARROW_KEYS|wx.SP_WRAP, myInitial, myMin, myMax, increment, -1, eval(style))
				handle.thing.SetDigits(0)
			else:
				handle.thing = wx.SpinCtrl(handle.parent.thing, value = wx.EmptyString, size = size, style = eval(styles), min = myMin, max = myMax, initial = myInitial)

			if (readOnly):
				handle.thing.SetReadOnly()

		#Determine size constraints
		if (maxSize != None):
			handle.thing.SetMaxSize(maxSize)

		if (minSize != None):
			handle.thing.SetMinSize(minSize)

		# print(label, handle.thing.GetBestSize())
		# handle.thing.SetMinSize(handle.thing.GetBestSize())
		# handle.thing.SetMaxSize(handle.thing.GetBestSize())

		#Bind the function(s)
		self.betterBind(wx.EVT_SPINCTRL, handle.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		if (changeTextFunction != None):
			if (type(changeTextFunction) == bool):
				if (changeTextFunction == True):
					self.betterBind(wx.EVT_TEXT, handle.thing, myFunction, myFunctionArgs, myFunctionKwargs)
			else:
				self.betterBind(wx.EVT_TEXT, handle.thing, changeTextFunction, changeTextFunctionArgs, changeTextFunctionKwargs)

		handle.postBuild(locals())

		return handle
	
	def addButton(self, text = "", valueLabel = None,

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None,

		label = None, hidden = False, enabled = True, selected = False, 
		flex = 0, flags = "c1", parent = None, handle = None):
		"""Adds a button to the next cell on the grid.

		text (str)            - What will be written on the button
		flags (list)            - A list of strings for which flag to add to the sizer
		myFunction (str)        - What function will be ran when the button is pressed
		label (any)           - What this is catalogued as
		valueLabel (str)        - If not None: Which label to get a value from. Ie: TextCtrl, FilePickerCtrl, etc.
		myFunctionArgs (any)    - The arguments for 'myFunction'
		myFunctionKwargs (any)  - The keyword arguments for 'myFunction'function
		default (bool)          - If True: This is the default thing selected
		enabled (bool)          - If True: The user can interact with this
		hidden (bool)           - If True: The widget is hidden from the user, but it is still created

		Example Input: addButton("Go!", "computeFinArray", 0)
		"""

		handle = handle_WidgetButton()
		handle.preBuild(locals())

		handle.type = "Button"

		#Create the thing to put in the grid
		handle.thing = wx.Button(handle.parent.thing, label = text, style = 0)

		#Bind the function(s)
		self.betterBind(wx.EVT_BUTTON, handle.thing, myFunction, myFunctionArgs, myFunctionKwargs)

		handle.postBuild(locals())

		return handle
	
	def addButtonToggle(self, text = "", 

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, 

		label = None, hidden = False, enabled = True, selected = False, 
		flex = 0, flags = "c1", parent = None, handle = None):
		"""Adds a toggle button to the next cell on the grid.

		text (str)             - What will be written on the button
		myFunction (str)        - What function will be ran when the button is pressed
		flags (list)            - A list of strings for which flag to add to the sizer
		label (any)           - What this is catalogued as
		myFunctionArgs (any)    - The arguments for 'myFunction'
		myFunctionKwargs (any)  - The keyword arguments for 'myFunction'function
		default (bool)          - If True: This is the default thing selected
		enabled (bool)          - If True: The user can interact with this

		Example Input: addButtonToggle("Go!", "computeFinArray")
		"""

		handle = handle_WidgetButton()
		handle.preBuild(locals())

		handle.type = "ButtonToggle"
	
		#Create the thing to put in the grid
		handle.thing = wx.ToggleButton(handle.parent.thing, label = text, style = 0)
		handle.thing.SetValue(True) 

		#Bind the function(s)
		self.betterBind(wx.EVT_TOGGLEBUTTON, handle.thing, myFunction, myFunctionArgs, myFunctionKwargs)

		handle.postBuild(locals())

		return handle
	
	def addButtonCheck(self, text = "", 

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, default = False,

		label = None, hidden = False, enabled = True, selected = False, 
		flex = 0, flags = "c1", parent = None, handle = None):
		"""Adds a check box to the next cell on the grid.
		Event fires every time the check box is clicked

		text (str)            - What will be written to the right of the button
		myFunction (str)        - What function will be ran when the button is pressed
		flags (list)            - A list of strings for which flag to add to the sizer
		label (any)           - What this is catalogued as
		myFunctionArgs (any)    - The arguments for 'myFunction'
		myFunctionKwargs (any)  - The keyword arguments for 'myFunction'function
		selected (bool)          - If True: This is the default thing selected
		enabled (bool)          - If True: The user can interact with this
		hidden (bool)           - If True: The widget is hidden from the user, but it is still created

		Example Input: addButtonCheck("compute?", "computeFinArray", 0)
		"""

		handle = handle_WidgetButton()
		handle.preBuild(locals())

		handle.type = "ButtonCheck"

		#Create the thing to put in the grid
		handle.thing = wx.CheckBox(handle.parent.thing, label = text, style = 0)

		#Determine if it is on by default
		handle.thing.SetValue(default)

		#Bind the function(s)
		self.betterBind(wx.EVT_CHECKBOX, handle.thing, myFunction, myFunctionArgs, myFunctionKwargs)

		handle.postBuild(locals())

		return handle
	
	def addCheckList(self, choices = [], multiple = True, sort = False,

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, 

		label = None, hidden = False, enabled = True, selected = False, 
		flex = 0, flags = "c1", parent = None, handle = None):
		"""Adds a checklist to the next cell on the grid.

		choices (list)          - A list of strings that are the choices for the check boxes
		myFunction (str)        - What function will be ran when the date is changed
		flags (list)            - A list of strings for which flag to add to the sizer
		label (any)           - What this is catalogued as
		myFunctionArgs (any)    - The arguments for 'myFunction'
		myFunctionKwargs (any)  - The keyword arguments for 'myFunction'function
		multiple (bool)         - True if the user can check off multiple check boxes
		sort (bool)             - True if the checklist will be sorted alphabetically or numerically

		Example Input: addCheckList(["Milk", "Eggs", "Bread"], 0, sort = True)
		"""

		handle = handle_WidgetButton()
		handle.preBuild(locals())

		handle.type = "CheckList"

		#Ensure that the choices given are a list or tuple
		if ((not isinstance(choices, list)) and (not isinstance(choices, tuple))):
			choices = list(choices)

		#Ensure that the choices are all strings
		choices = [str(item) for item in choices]

		#Apply settings
		styles = "wx.LB_NEEDED_SB"

		if (multiple):
			styles += "|wx.LB_MULTIPLE"
		
		if (sort):
			styles += "|wx.LB_SORT"
	
		#Create the thing to put in the grid
		handle.thing = wx.CheckListBox(handle.parent.thing, choices = choices, style = eval(styles))

		#Bind the function(s)
		self.betterBind(wx.EVT_CHECKLISTBOX, handle.thing, myFunction, myFunctionArgs, myFunctionKwargs)

		handle.postBuild(locals())

		return handle
	
	def addButtonRadio(self, text = "", groupStart = False, default = False,

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, 

		label = None, hidden = False, enabled = True, selected = False, 
		flex = 0, flags = "c1", parent = None, handle = None):
		"""Adds a radio button to the next cell on the grid. If default, it will disable the other
		radio buttons of the same group.

		text (str)            - What will be written to the right of the button
		myFunction (str)        - What function will be ran when the button is pressed
		flags (list)            - A list of strings for which flag to add to the sizer
		label (int)           - What this is catalogued as
		myFunctionArgs (any)    - The arguments for 'myFunction'
		myFunctionKwargs (any)  - The keyword arguments for 'myFunction'function
		selected (bool)          - If True: This is the default thing selected
		enabled (bool)          - If True: The user can interact with this
		groupStart (bool)       - True if this is the start of a new radio button group.

		Example Input: addButtonRadio("compute?", "computeFinArray", 0, groupStart = True)
		"""

		handle = handle_WidgetButton()
		handle.preBuild(locals())

		handle.type = "ButtonRadio"

		#determine if this is the start of a new radio button group
		if (groupStart):
			group = wx.RB_GROUP
		else:
			group = 0
	
		#Create the thing to put in the grid
		handle.thing = wx.RadioButton(handle.parent.thing,label = text, style = group)

		#Determine if it is turned on by default
		handle.thing.SetValue(default)

		#Bind the function(s)
		self.betterBind(wx.EVT_RADIOBUTTON, handle.thing, myFunction, myFunctionArgs, myFunctionKwargs)

		handle.postBuild(locals())

		return handle
	
	def addButtonRadioBox(self, choices = [], title = "", vertical = False, default = 0, 

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, 

		label = None, hidden = False, enabled = True, selected = False, 
		flex = 0, flags = "c1", parent = None, handle = None):
		"""Adds a box filled with grouped radio buttons to the next cell on the grid.
		Because these buttons are grouped, only one can be selected

		choices (list)           - What will be written to the right of the button. ["Button 1", "Button 2", "Button 3"]
		myFunction (int)        - What function will be ran when the button is pressed
		title (str)             - What will be written above the box
		flags (list)            - A list of strings for which flag to add to the sizer
		label (int)           - What this is catalogued as
		myFunctionArgs (any)    - The arguments for 'myFunction'
		myFunctionKwargs (any)  - The keyword arguments for 'myFunction'function
		horizontal (bool)       - If True: The box will be oriented horizontally
								  If False: The box will be oriented vertically
		default (int)           - Which of the radio buttons will be selected by default
		enabled (bool)          - If True: The user can interact with this

		Example Input: addButtonRadioBox(["Button 1", "Button 2", "Button 3"], "self.onQueueValue", 0)
		"""

		handle = handle_WidgetButton()
		handle.preBuild(locals())

		handle.type = "ButtonRadioBox"

		#Ensure that the choices given are a list or tuple
		if ((not isinstance(choices, list)) and (not isinstance(choices, tuple))):
			choices = list(choices)

		#Ensure that the choices are all strings
		choices = [str(item) for item in choices]

		#Determine orientation
		if (vertical):
			direction = wx.RA_SPECIFY_COLS
		else:
			direction = wx.RA_SPECIFY_ROWS

		#Create the thing to put in the grid
		handle.thing = wx.RadioBox(handle.parent.thing, label = title, choices = choices, majorDimension = 1, style = direction)

		#Set default position
		if (len(choices) != 0):
			if (type(default) == str):
				if (default in choices):
					default = choices.index(default)

			if (default == None):
				default = 0

			handle.thing.SetSelection(default)

		#Bind the function(s)
		self.betterBind(wx.EVT_RADIOBOX, handle.thing, myFunction, myFunctionArgs, myFunctionKwargs)

		handle.postBuild(locals())

		return handle
	
	def addButtonImage(self, idlePath = "", disabledPath = "", selectedPath = "", focusPath = "", hoverPath = "",

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, 

		label = None, hidden = False, enabled = True, selected = False, 
		flex = 0, flags = "c1", parent = None, handle = None):
		"""Adds a button to the next cell on the grid. You design what the button looks like yourself.

		idlePath (str)          - Where the image of the button idling is on the computer
		disabledPath (str)      - Where the image of the button disabled is on the computer
		selectedPath (str)      - Where the image of the button selected is on the computer
		focusPath (str)         - Where the image of the button focused is on the computer
		hoverPath (str)         - Where the image of the button hovered is on the computer
		myFunction (str)        - What function will be ran when the button is pressed
		flags (list)            - A list of strings for which flag to add to the sizer
		label (any)           - What this is catalogued as
		myFunctionArgs (any)    - The arguments for 'myFunction'
		myFunctionKwargs (any)  - The keyword arguments for 'myFunction'function
		default (bool)          - If True: This is the default thing selected
		enabled (bool)          - If True: The user can interact with this

		Example Input: addButtonImage("1.bmp", "2.bmp", "3.bmp", "4.bmp", "5.bmp", "computeFinArray")
		"""

		def imageCheck(imagePath):
			"""Determines what image to use."""
			nonlocal self

			if ((imagePath != "") and (imagePath != None)):
				if (not os.path.exists(imagePath)):
					return self.getImage("error", internal = True)
				return self.getImage(imagePath)
			else:
				return None

		handle = handle_WidgetButton()
		handle.preBuild(locals())

		handle.type = "ButtonImage"

		# wx.BU_LEFT: Left-justifies the bitmap label.
		# wx.BU_TOP: Aligns the bitmap label to the top of the button.
		# wx.BU_RIGHT: Right-justifies the bitmap label.
		# wx.BU_BOTTOM: Aligns the bitmap label to the bottom of the button.

		#Error Check
		image = imageCheck(idlePath)
		if (image == None):
			image = self.getImage(None)

		#Create the thing to put in the grid
		handle.thing = wx.BitmapButton(handle.parent.thing, bitmap = image, style = wx.BU_AUTODRAW)
	
		image = imageCheck(disabledPath)
		if (image != None):
			handle.thing.SetBitmapDisabled(image)

		image = imageCheck(selectedPath)
		if (image != None):
			handle.thing.SetBitmapSelected(image)

		image = imageCheck(focusPath)
		if (image != None):
			handle.thing.SetBitmapFocus(image)

		image = imageCheck(hoverPath)
		if (image != None):
			handle.thing.SetBitmapHover(image)

		#Bind the function(s)
		self.betterBind(wx.EVT_BUTTON, handle.thing, myFunction, myFunctionArgs, myFunctionKwargs)

		handle.postBuild(locals())

		return handle
	
	def addImage(self, imagePath = "", internal = False, size = wx.DefaultSize,

		label = None, hidden = False, enabled = True, selected = False, 
		flex = 0, flags = "c1", parent = None, handle = None):
		"""Adds an embeded image to the next cell on the grid.

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
				"plus"        - A blue '+'
				"minus"       - A blue '-'
				"close"       - A black 'X'
				"quit"        - A door opening to the left with a green arrow coming out of it to the right
				"find"        - A magnifying glass
				"findReplace" - "find" with a double sided arrow in the bottom left corner pointing left and right
				"first"       - A green arrow pointing left with a green vertical line
				"last"        - A green arrow pointing right with a green vertical line
				"diskHard"    - ?
				"diskFloppy"  - ?
				"diskCd"      - ?
				"book"        - A blue book with white pages
				"addBookmark" - A green banner with a '+' by it
				"delBookmark" - A red banner with a '-' by it
				"sidePanel"   - A grey box with lines in with a white box to the left with arrows pointing left and right
				"viewReport"  - A white box with lines in it with a grey box with lines in it on top
				"viewList"    - A white box with squiggles in it with a grey box with dots in it to the left
			
		flags (list)            - A list of strings for which flag to add to the sizer
		label (any)           - What this is catalogued as
		internal (bool)         - If True: The 'filePath' provided will represent an internal image

		Example Input: addImage("1.bmp", 0)
		Example Input: addImage(image, 0)
		Example Input: addImage("error", 0, internal = True)
		Example Input: addImage(image, 0, size = (32, 32))
		"""

		handle = handle_WidgetImage()
		handle.preBuild(locals())

		handle.type = "Image"

		#Get correct image
		image = self.getImage(imagePath, internal)
	
		#Create the thing to put in the grid
		handle.thing = wx.StaticBitmap(handle.parent.thing, bitmap = image, size = size, style = 0)

		handle.postBuild(locals())

		return handle
	
	def addProgressBar(self, myInitial = 0, myMax = 100, vertical = False,

		label = None, hidden = False, enabled = True, selected = False, 
		flex = 0, flags = "c1", parent = None, handle = None):
		"""Adds progress bar to the next cell on the grid.

		myInitial (int)         - The value that the progress bar starts at
		myMax (int)             - The value that the progress bar is full at
		flags (list)            - A list of strings for which flag to add to the sizer
		label (any)           - What this is catalogued as

		Example Input: addProgressBar(0, 100)
		"""

		handle = handle_Widget_Base()
		handle.preBuild(locals())

		handle.type = "ProgressBar"

		if (vertical):
			styles = wx.GA_VERTICAL
		else:
			styles = wx.GA_HORIZONTAL
	
		#Create the thing to put in the grid
		handle.thing = wx.Gauge(handle.parent.thing, range = myMax, style = styles)

		#Set Initial Conditions
		handle.thing.SetValue(myInitial)

		handle.postBuild(locals())

		return handle
	
	def addPickerColor(self, addInputBox = False, colorText = False, initial = None,

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, 

		label = None, hidden = False, enabled = True, selected = False, 
		flex = 0, flags = "c1", parent = None, handle = None):
		"""Adds a color picker to the next cell on the grid.
		It can display the name or RGB of the color as well.

		myFunction (str)        - What function will be ran when the color is chosen
		flags (list)            - A list of strings for which flag to add to the sizer
		label (any)           - What this is catalogued as
		myFunctionArgs (any)    - The arguments for 'myFunction'
		myFunctionKwargs (any)  - The keyword arguments for 'myFunction'function

		Example Input: addPickerColor(label = "changeColor")
		"""

		handle = handle_WidgetPicker()
		handle.preBuild(locals())

		handle.type = "PickerColor"

		styles = ""

		#Add settings
		if (addInputBox):
			styles += "|wx.CLRP_USE_TEXTCTRL"
		
		if (colorText):
			styles += "|wx.CLRP_SHOW_LABEL"

		if (len(styles) == 0):
			styles = "0"
		else:
			styles = styles[1:] #Remove leading line

		if (initial == None):
			initial = wx.BLACK
		else:
			initial = wx.BLACK
	
		#Create the thing to put in the grid
		handle.thing = wx.ColourPickerCtrl(handle.parent.thing, colour = initial, style = eval(styles))

		#Bind the function(s)
		self.betterBind(wx.EVT_COLOURPICKER_CHANGED, handle.thing, myFunction, myFunctionArgs, myFunctionKwargs)

		handle.postBuild(locals())

		return handle
	
	def addPickerFont(self, maxSize = 72, fontText = False, addInputBox = False,

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, 

		label = None, hidden = False, enabled = True, selected = False, 
		flex = 0, flags = "c1", parent = None, handle = None):
		"""Adds a color picker to the next cell on the grid.
		It can display the name or RGB of the color as well.

		maxSize (int)           - The maximum font size that can be chosen
		myFunction (str)        - What function will be ran when the color is chosen
		flags (list)            - A list of strings for which flag to add to the sizer
		label (any)           - What this is catalogued as
		myFunctionArgs (any)    - The arguments for 'myFunction'
		myFunctionKwargs (any)  - The keyword arguments for 'myFunction'function
		fontText (str)          - True if it should show the name of the font picked

		Example Input: addPickerFont(32, "changeFont")
		"""

		handle = handle_WidgetPicker()
		handle.preBuild(locals())

		handle.type = "PickerFont"

		#Add settings
		styles = ""
		if (addInputBox):
			styles += "|wx.FNTP_USE_TEXTCTRL"
		
		if (fontText):
			styles += "|wx.FNTP_FONTDESC_AS_LABEL"
			#FNTP_USEFONT_FOR_LABEL

		if (len(styles) != 0):
			styles = styles[1:] #Remove leading line
		else:
			styles = "0"

		# font = handle.makeFont()
		font = wx.NullFont
	
		#Create the thing to put in the grid
		handle.thing = wx.FontPickerCtrl(handle.parent.thing, font = font, style = eval(styles))
		
		handle.thing.SetMaxPointSize(maxSize) 

		#Bind the function(s)
		self.betterBind(wx.EVT_FONTPICKER_CHANGED, handle.thing, myFunction, myFunctionArgs, myFunctionKwargs)

		handle.postBuild(locals())

		return handle
	
	def addPickerFile(self, text = "Select a File", default = "", initialDir = "*.*", 
		directoryOnly = False, changeCurrentDirectory = False, fileMustExist = False, openFile = False, 
		saveConfirmation = False, saveFile = False, smallButton = False, addInputBox = False, 

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None,

		label = None, hidden = False, enabled = True, selected = False, 
		flex = 0, flags = "c1", parent = None, handle = None):
		"""Adds a file picker to the next cell on the grid.

		flags (list)      - A list of strings for which flag to add to the sizer
		label (any)     - What this is catalogued as
		text (str)        - What is shown on the top of the popout window
		default (str)     - What the default value will be for the input box

		initialDir (str)              - Which directory it will start at. By default this is the directory that the program is in
		directoryOnly (bool)          - If True: Only the directory will be shown; no files will be shown
		changeCurrentDirectory (bool) - If True: Changes the current working directory on each user file selection change
		fileMustExist (bool)          - If True: When a file is opened, it must exist
		openFile (bool)               - If True: The file picker is configured to open a file
		saveConfirmation (bool)       - If True: When a file is saved over an existing file, it makes sure you want to do that
		saveFile (bool)               - If True: The file picker is configured to save a file
		smallButton (bool)            - If True: The file picker button will be small
		addInputBox (bool)            - If True: The file picker will have an input box that updates with the chosen directory. A chosen directory can be pasted/typed into this box as well
		hidden (bool)                 - If True: The widget is hidden from the user, but it is still created

		myFunction (str)       - What function will be ran when the file is chosen
		myFunctionArgs (any)   - The arguments for 'myFunction'
		myFunctionKwargs (any) - The keyword arguments for 'myFunction'function
		

		Example Input: addPickerFile(0, myFunction = self.openFile, addInputBox = True)
		Example Input: addPickerFile(0, saveFile = True, myFunction = self.saveFile, saveConfirmation = True, directoryOnly = True)
		"""

		handle = handle_WidgetPicker()
		handle.preBuild(locals())

		handle.type = "PickerFile"

		#Picker configurations
		config = ""

		if (directoryOnly):
			##Determine which configurations to add
			if (changeCurrentDirectory):
				config += "wx.DIRP_CHANGE_DIR|"
			if (fileMustExist):
				config += "wx.DIRP_DIR_MUST_EXIST|"
			if (smallButton):
				config += "wx.DIRP_SMALL|"
			if (addInputBox):
				config += "wx.DIRP_USE_TEXTCTRL|"
		else:
			##Make sure conflicting configurations are not given
			if ((openFile or fileMustExist) and (saveFile or saveConfirmation)):
				errorMessage = "Open config and save config cannot be added to the same file picker"
				raise SyntaxError(errorMessage)

			if (changeCurrentDirectory and ((openFile or fileMustExist or saveFile or saveConfirmation))):
				errorMessage = "Open config and save config cannot be used in combination with a directory change"
				raise SyntaxError(errorMessage)

			##Determine which configurations to add
			if (changeCurrentDirectory):
				config += "wx.FLP_CHANGE_DIR|"
			if (fileMustExist):
				config += "wx.FLP_FILE_MUST_EXIST|"
			if (openFile):
				config += "wx.FLP_OPEN|"
			if (saveConfirmation):
				config += "wx.FLP_OVERWRITE_PROMPT|"
			if (saveFile):
				config += "wx.FLP_SAVE|"
			if (smallButton):
				config += "wx.FLP_SMALL|"
			if (addInputBox):
				config += "wx.FLP_USE_TEXTCTRL|"

		if (config != ""):
			config = config[:-1]
		else:
			config = "0"
	
		#Create the thing to put in the grid
		if (directoryOnly):
			handle.thing = wx.DirPickerCtrl(handle.parent.thing, path = default, message = text, style = eval(config))
		else:
			handle.thing = wx.FilePickerCtrl(handle.parent.thing, path = default, message = text, wildcard = initialDir, style = eval(config))

		#Set Initial directory
		handle.thing.SetInitialDirectory(initialDir)

		#Bind the function(s)
		if (directoryOnly):
			self.betterBind(wx.EVT_DIRPICKER_CHANGED, handle.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		else:
			self.betterBind(wx.EVT_FILEPICKER_CHANGED, handle.thing, myFunction, myFunctionArgs, myFunctionKwargs)

		handle.postBuild(locals())

		return handle
	
	def addPickerFileWindow(self, initialDir = "*.*", 
		directoryOnly = True, selectMultiple = False, showHidden = True,

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, 
		editLabelFunction = None, editLabelFunctionArgs = None, editLabelFunctionKwargs = None, 
		rightClickFunction = None, rightClickFunctionArgs = None, rightClickFunctionKwargs = None, 

		label = None, hidden = False, enabled = True, selected = False, 
		flex = 0, flags = "c1", parent = None, handle = None):
		"""Adds a file picker window to the next cell on the grid.

		myFunction (str)               - What function will be ran when the file is chosen
		flags (list)                   - A list of strings for which flag to add to the sizer
		label (any)                  - What this is catalogued as
		myFunctionArgs (any)           - The arguments for 'myFunction'
		myFunctionKwargs (any)         - The keyword arguments for 'myFunction'function
		initialDir (str)               - Which directory it will start at. By default this is the directory that the program is in.
		editLabelFunction (str)        - What function will be ran when a label is edited
		editLabelFunctionArgs (any)    - The arguments for 'myFunction'
		editLabelFunctionKwargs (any)  - The keyword arguments for 'myFunction'function
		rightClickFunction (str)       - What function will be ran when an item is right clicked
		rightClickFunctionArgs (any)   - The arguments for 'myFunction'
		rightClickFunctionKwargs (any) - The keyword arguments for 'myFunction'function
		directoryOnly (bool)           - If True: Only the directory will be shown; no files will be shown
		selectMultiple (bool)          - If True: It is possible to select multiple files by using the [ctrl] key while clicking

		Example Input: addPickerFileWindow("changeDirectory")
		"""

		handle = handle_WidgetPicker()
		handle.preBuild(locals())

		handle.type = "PickerFileWindow"

		#Apply settings
		styles = "wx.DIRCTRL_3D_INTERNAL|wx.SUNKEN_BORDER"

		if (directoryOnly):
			styles += "|wx.DIRCTRL_DIR_ONLY"

		if (editLabelFunction != None):
			styles += "|wx.DIRCTRL_EDIT_LABELS"

		if (selectMultiple):
			styles += "|wx.DIRCTRL_MULTIPLE"

		# wx.DIRCTRL_SELECT_FIRST: When setting the default path, select the first file in the directory.
		# wx.DIRCTRL_SHOW_FILTERS: Show the drop-down filter list.

		# A filter string, using the same syntax as that for wx.FileDialog. This may be empty if filters are not being used. Example: "All files (*.*)|*.*|JPEG files (*.jpg)|*.jpg"
		filterList = wx.EmptyString
	
		#Create the thing to put in the grid
		handle.thing = wx.GenericDirCtrl(handle.parent.thing, dir = initialDir, style = eval(styles), filter = filterList)

		#Determine if it is hidden
		if (showHidden):
			handle.thing.ShowHidden(True)
		else:
			handle.thing.ShowHidden(False)

		#Bind the function(s)
		if (editLabelFunction != None):
			self.betterBind(wx.EVT_TREE_END_LABEL_EDIT, handle.thing, editLabelFunction, editLabelFunctionArgs, editLabelFunctionKwargs)
		if (rightClickFunction != None):
			self.betterBind(wx.EVT_TREE_ITEM_RIGHT_CLICK, handle.thing, rightClickFunction, rightClickFunctionArgs, rightClickFunctionKwargs)
		self.betterBind(wx.EVT_TREE_SEL_CHANGED, handle.thing, myFunction, myFunctionArgs, myFunctionKwargs)

		handle.postBuild(locals())

		return handle
	
	def addPickerTime(self, time = None,

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, 

		label = None, hidden = False, enabled = True, selected = False, 
		flex = 0, flags = "c1", parent = None, handle = None):
		"""Adds a time picker to the next cell on the grid.
		The input time is in military time.

		myFunction (str)        - What function will be ran when the time is changed
		time (str)              - What the currently selected time is as 'hh:mm:ss'
								  If None: The current time will be used
		flags (list)            - A list of strings for which flag to add to the sizer
		label (any)           - What this is catalogued as
		myFunctionArgs (any)    - The arguments for 'myFunction'
		myFunctionKwargs (any)  - The keyword arguments for 'myFunction'function
		hidden (bool)           - If True: The widget is hidden from the user, but it is still created

		Example Input: addPickerTime(0)
		Example Input: addPickerTime(0, "17:30")
		Example Input: addPickerTime(0, "12:30:20")
		"""

		handle = handle_WidgetPicker()
		handle.preBuild(locals())

		handle.type = "PickerTime"

		#Set the currently selected time
		if (time != None):
			try:
				time = re.split(":", newValue) #Format: hour:minute:second
				
				if (len(time) == 2):
					hour, minute = time
					second = "0"

				elif (len(time) == 3):
					hour, minute, second = time

				else:
					raise SyntaxError


				hour, minute, second = int(hour), int(minute), int(second)
				time = wx.DateTime(1, 1, 2000, hour, minute, second)
			except:
				errorMessage = "Time must be formatted 'hh:mm:ss' or 'hh:mm'"
				raise SyntaxError(errorMessage)
		else:
			time = wx.DateTime().SetToCurrent()

		#Create the thing to put in the grid
		handle.thing = wx.adv.TimePickerCtrl(handle.parent.thing, dt = time)

		#Bind the function(s)
		self.betterBind(wx.adv.EVT_TIME_CHANGED, handle.thing, myFunction, myFunctionArgs, myFunctionKwargs)

		handle.postBuild(locals())

		return handle
	
	def addPickerDate(self, date = None, dropDown = False, 

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, 

		label = None, hidden = False, enabled = True, selected = False, 
		flex = 0, flags = "c1", parent = None, handle = None):
		"""Adds a date picker to the next cell on the grid.

		myFunction (str)        - What function will be ran when the date is changed
		date (str)              - What the currently selected date is
								  If None: The current date will be used
		flags (list)            - A list of strings for which flag to add to the sizer
		label (any)           - What this is catalogued as
		myFunctionArgs (any)    - The arguments for 'myFunction'
		myFunctionKwargs (any)  - The keyword arguments for 'myFunction'function
		dropDown (bool)         - True if a calandar dropdown should be displayed instead of just the arrows
		hidden (bool)           - If True: The widget is hidden from the user, but it is still created

		Example Input: addPickerDate(0)
		Example Input: addPickerDate(0, "10/16/2000")
		Example Input: addPickerDate(0, dropDown = True)
		"""

		handle = handle_WidgetPicker()
		handle.preBuild(locals())

		handle.type = "PickerDate"

		#Set the currently selected date
		if (date != None):
			try:
				month, day, year = re.split("[\\\\/]", newValue) #Format: mm/dd/yyyy
				month, day, year = int(month), int(day), int(year)
				date = wx.DateTime(day, month, year)
			except:
				errorMessage = "Calandar dates must be formatted 'mm/dd/yy'"
				raise SyntaxError(errorMessage)
		else:
			date = wx.DateTime().SetToCurrent()

		#Apply Settings
		# wx.adv.DP_SPIN: Creates a control without a month calendar drop down but with spin-control-like arrows to change individual date components. This style is not supported by the generic version.
		# wx.adv.DP_DROPDOWN: Creates a control with a month calendar drop-down part from which the user can select a date. This style is not supported in OSX/Cocoa native version.
		# wx.adv.DP_DEFAULT: Creates a control with the style that is best supported for the current platform (currently wx.adv.DP_SPIN under Windows and OSX/Cocoa and wx.adv.DP_DROPDOWN elsewhere).
		# wx.adv.DP_ALLOWNONE: With this style, the control allows the user to not enter any valid date at all. Without it - the default - the control always has some valid date. This style is not supported in OSX/Cocoa native version.
		# wx.adv.DP_SHOWCENTURY: Forces display of the century in the default date format. Without this style the century could be displayed, or not, depending on the default date representation in the system. This style is not supported in OSX/Cocoa native version currently.

		if (dropDown):
			styles = wx.adv.DP_DROPDOWN
		else:
			styles = wx.adv.DP_SPIN

		#Create the thing to put in the grid
		handle.thing = wx.adv.DatePickerCtrl(handle.parent.thing, dt = date, style = styles)

		#Bind the function(s)
		self.betterBind(wx.adv.EVT_DATE_CHANGED, handle.thing, myFunction, myFunctionArgs, myFunctionKwargs)

		handle.postBuild(locals())

		return handle
	
	def addPickerDateWindow(self, date = None, showHolidays = False, showOther = False,
		
		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, 
		dayFunction = None, dayFunctionArgs = None, dayFunctionKwargs = None, 
		monthFunction = None, monthFunctionArgs = None, monthFunctionKwargs = None, 
		yearFunction = None, yearFunctionArgs = None, yearFunctionArgsKwargs = None, 

		label = None, hidden = False, enabled = True, selected = False, 
		flex = 0, flags = "c1", parent = None, handle = None):
		"""Adds a date picker to the next cell on the grid.

		myFunction (str)          - What function will be ran when the date is changed
		date (str)                - What the currently selected date is
									If None: The current date will be used
		flags (list)              - A list of strings for which flag to add to the sizer
		label (any)             - What this is catalogued as
		myFunctionArgs (any)      - The arguments for 'myFunction'
		myFunctionKwargs (any)    - The keyword arguments for 'myFunction'function
		showHoliday (bool)        - True if the holidays, weekends, and sunday will be bolded
		showOther (bool)          - True if the surrounding week's days will be shown
		hidden (bool)             - If True: The widget is hidden from the user, but it is still created

		dayFunction (str)         - What function will be ran when day is changed
		dayFunctionArgs (any)     - The arguments for 'dayFunction'
		dayFunctionKwargs (any)   - The keyword arguments for 'dayFunction'function

		monthFunction (str)       - What function will be ran when month is changed
		monthFunctionArgs (any)   - The arguments for 'monthFunction'
		monthFunctionKwargs (any) - The keyword arguments for 'monthFunction'function

		yearFunction (str)        - What function will be ran when year is changed
		yearFunctionArgs (any)    - The arguments for 'yearFunction'
		yearFunctionKwargs (any)  - The keyword arguments for 'yearFunction'function


		Example Input: addPickerDateWindow(0)
		"""

		handle = handle_WidgetPicker()
		handle.preBuild(locals())

		handle.type = "PickerDateWindow"

		#Set the currently selected date
		if (date != None):
			try:
				month, day, year = re.split("[\\\\/]", newValue) #Format: mm/dd/yyyy
				date = wx.DateTime(day, month, year)
			except:
				errorMessage = "Calandar dates must be formatted 'mm/dd/yy'"
				raise SyntaxError(errorMessage)
		else:
			date = wx.DateTime().SetToCurrent()

		#Apply settings
		styles = ""

		# wx.adv.CAL_SUNDAY_FIRST: Show Sunday as the first day in the week (not in wxGTK)
		# wx.adv.CAL_MONDAY_FIRST: Show Monday as the first day in the week (not in wxGTK)
		# wx.adv.CAL_NO_YEAR_CHANGE: Disable the year changing (deprecated, only generic)
		# wx.adv.CAL_NO_MONTH_CHANGE: Disable the month (and, implicitly, the year) changing
		# wx.adv.CAL_SEQUENTIAL_MONTH_SELECTION: Use alternative, more compact, style for the month and year selection controls. (only generic)
		# wx.adv.CAL_SHOW_WEEK_NUMBERS: Show week numbers on the left side of the calendar. (not in generic)

		if (showHolidays):
			styles += "|wx.adv.CAL_SHOW_HOLIDAYS"
		
		if (showOther):
			styles += "|wx.adv.CAL_SHOW_SURROUNDING_WEEKS"

		if (len(styles) != 0):
			styles = styles[1:] #Remove leading line
		else:
			styles = "0"
	
		#Create the thing to put in the grid
		handle.thing = wx.adv.CalendarCtrl(handle.parent.thing, date = date, style = eval(styles))

		#Bind the function(s)
		self.betterBind(wx.adv.EVT_CALENDAR_SEL_CHANGED, handle.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		if (dayFunction != None):
			self.betterBind(wx.adv.EVT_CALENDAR_DAY, handle.thing, dayFunction, dayFunctionArgs, dayFunctionKwargs)
		if (monthFunction != None):
			self.betterBind(wx.adv.EVT_CALENDAR_MONTH, handle.thing, monthFunction, monthFunctionArgs, monthFunctionKwargs)
		if (yearFunction != None):
			self.betterBind(wx.adv.EVT_CALENDAR_YEAR, handle.thing, yearFunction, yearFunctionArgs, yearFunctionKwargs)

		handle.postBuild(locals())

		return handle

	def addCanvas(self, size = wx.DefaultSize, position = wx.DefaultPosition, 
		panel = {},

		initFunction = None, initFunctionArgs = None, initFunctionKwargs = None,

		label = None, hidden = False, enabled = True, selected = False, 
		flex = 0, flags = "c1", parent = None, handle = None):
		"""Creates a blank canvas window.

		size (int tuple)  - The size of the canvas. (length, width)
		label (str)     - What this is called in the idCatalogue
		border (str)      - What style the border has. "simple", "raised", "sunken" or "none". Only the first two letters are necissary
		
		tabTraversal (bool)   - If True: Pressing [tab] will move the cursor to the next widget
		useDefaultSize (bool) - If True: The xSize and ySize will be overridden to fit as much of the widgets as it can. Will lock the canvas size from re-sizing

		initFunction (str)       - The function that is ran when the canvas first appears
		initFunctionArgs (any)   - The arguments for 'initFunction'
		initFunctionKwargs (any) - The keyword arguments for 'initFunction'function

		Example Input: addCanvas()
		"""

		handle = handle_WidgetCanvas()
		handle.preBuild(locals())

		handle.type = "Canvas"
		
		#Create the thing
		panel["parent"] = self.parent
		handle.myPanel = handle.readBuildInstructions_panel(self, panel)
		handle.myPanel.nested = True
		handle.thing = handle.myPanel.thing

		#onSize called to make sure the buffer is initialized.
		#This might result in onSize getting called twice on some platforms at initialization, but little harm done.
		handle.onSize(None)

		#Bind Functions
		if (initFunction != None):
			self.betterBind(wx.EVT_INIT_DIALOG, handle.thing, initFunction, initFunctionArgs, initFunctionKwargs)

		#Enable painting
		self.betterBind(wx.EVT_PAINT, handle.thing, handle.onPaint)
		self.betterBind(wx.EVT_SIZE, handle.thing, handle.onSize)

		handle.postBuild(locals())

		return handle

	def addTable(self, rows = 1, columns = 1,
		contents = None, gridLabels = [[],[]], toolTips = None, 
		rowSize = None, columnSize = None, rowLabelSize = None, columnLabelSize = None, rowSizeMinimum = None, columnSizeMinimum = None,

		showGrid = True, dragableRows = False, dragableColumns = False, arrowKeyExitEdit = False, enterKeyExitEdit = False, editOnEnter = False, 
		readOnly = False, readOnlyDefault = False, default = (0, 0),

		preEditFunction = None, preEditFunctionArgs = None, preEditFunctionKwargs = None, 
		postEditFunction = None, postEditFunctionArgs = None, postEditFunctionKwargs = None, 
		dragFunction = None, dragFunctionArgs = None, dragFunctionKwargs = None, 
		selectManyFunction = None, selectManyFunctionArgs = None, selectManyFunctionKwargs = None, 
		selectSingleFunction = None, selectSingleFunctionArgs = None, selectSingleFunctionKwargs = None, 
		rightClickCellFunction = None, rightClickCellFunctionArgs = None, rightClickCellFunctionKwargs = None, 
		rightClickLabelFunction = None, rightClickLabelFunctionArgs = None, rightClickLabelFunctionKwargs = None,

		label = None, hidden = False, enabled = True, selected = False, 
		flex = 0, flags = "c1", parent = None, handle = None):

		"""Adds a table to the next cell on the grid. 
		If enabled, it can be edited; the column &  sizerNumber, size can be changed.
		To get a cell value, use: myGridId.GetCellValue(row, column).
		For a deep tutorial: http://www.blog.pythonlibrary.org/2010/03/18/wxpython-an-introduction-to-grids/

		rows (int)       - The number of rows the table has
		columns (int)    - The number of columns the table has
		sizerNumber (int) - The number of the sizer that this will be added to
		tableNumber (int) - The table catalogue number for this new table
		flags (list)      - A list of strings for which flag to add to the sizer
		contents (list)   - Either a 2D list [[row], [column]] or a numpy array that contains the contents of each cell. If None, they will be blank.
		gridLabels (str)  - The labels for the [[rows], [columns]]. If not enough are provided, the resst will be capital letters.
		toolTips (list)   - The coordinates and message for all the tool tips. [[row, column, message], [row, column, message], ...]
		label (str)     - What this is called in the idCatalogue
		
		rowSize (str)           - The height of the rows. 'None' will make it the default size
		columnSize (str)        - The width of the columns. 'None' will make it the default size
		rowLabelSize (int)      - The width of the row labels. 'None' will make it the default size
		columnLabelSize (int)   - The height of the column labels. 'None' will make it the default size
		rowSizeMinimum (str)    - The minimum height for the rows. 'None' will make it the default size
		columnSizeMinimum (str) - The minimum width for the columns. 'None' will make it the default size
		
		showGrid (bool)         - If True: the grid lines will be visible
		dragableRows (bool)     - If True: The user can drag the row lines of the cells
		dragableColumns (bool)  - If True: The user can drag the column lines of the cells
		editOnEnter (bool)      - Determiens the default behavior for the enter key
			- If True: The user will begin editing the cell when enter is pressed
			- If False: The cursor will move down to the next row
		arrowKeyExitEdit (bool) - If True: The user will stop editing and navigate the grid if they use the arrow keys while editing instead of navigating the editor box
		enterKeyExitEdit (bool) - If True: If the user presses enter while editing a cell, the cursor will move down
		readOnly (bool)         - Determines the editability of the table
			- If True: The user will not be able to edit the cells. If an edit function is provided, this cell will be ignored
			- If False: The user will be able to edit all cells.
			- A dictionary can be given to single out specific cells, rows, or columns
				~ {row number (int): {column number (int): readOnly for the cell (bool)}}
				~ {row number (int): readOnly for the whole row (bool)}
				~ {None: column number (int): readOnly for the whole column (bool)}
		readOnlyDefault (bool)  - What readOnly value to give a cell if the user does not provide one
		default (tuple)         - Which cell the table starts out with selected. (row, column)

		preEditFunction (str)               - The function that is ran when the user edits a cell. If None: the user cannot edit cells. Accessed cells are before the edit
		preEditFunctionArgs (any)           - The arguments for 'preEditFunction'
		preEditFunctionKwargs (any)         - The keyword arguments for 'preEditFunction'
		postEditFunction (str)              - The function that is ran when the user edits a cell. If None: the user cannot edit cells. Accessed cells are after the edit
		postEditFunctionArgs (any)          - The arguments for 'postEditFunction'
		postEditFunctionKwargs (any)        - The keyword arguments for 'postEditFunction'
		
		dragFunction (str)                  - The function that is ran when the user drags a row or column. If None: the user cannot drag rows or columns
		dragFunctionArgs (any)              - The arguments for 'dragFunction'
		dragFunctionKwargs (any)            - The keyword arguments for 'dragFunction'
		selectManyFunction (str)            - The function that is ran when the user selects a group of continuous cells
		selectManyFunctionArgs (any)        - The arguments for 'selectManyFunction'
		selectManyFunctionKwargs (any)      - The keyword arguments for 'selectManyFunction'
		selectSingleFunction (str)          - The function that is ran when the user selects a single cell
		selectSingleFunctionArgs (any)      - The arguments for 'selectSingleFunction'
		selectSingleFunctionKwargs (any)    - The keyword arguments for 'selectSingleFunction'
		
		rightClickCellFunction (str)        - What function will be ran when a cell is right clicked
		rightClickCellFunctionArgs (any)    - The arguments for 'rightClickCellFunction'
		rightClickCellFunctionKwargs (any)  - The keyword arguments for 'rightClickCellFunction'function
		rightClickLabelFunction (str)       - What function will be ran when a column or row label is right clicked
		rightClickLabelFunctionArgs (any)   - The arguments for 'rightClickLabelFunction'
		rightClickLabelFunctionKwargs (any) - The keyword arguments for 'rightClickLabelFunction'function

		wizardFrameNumber (int) - The number of the wizard page. If None, it assumes either a frame or a panel

		Example Input: addTable()
		Example Input: addTable(3, 4, 0, 0, contents = [[1, 2, 3], [a, b, c], [4, 5, 6], [d, e, f]])
		Example Input: addTable(3, 4, 0, 0, contents = myArray)

		Example Input: addTable(3, 4, 0, 0, readOnly = True)
		Example Input: addTable(3, 4, 0, 0, readOnly = {1: True})
		Example Input: addTable(3, 4, 0, 0, readOnly = {1: {1: True, 3: True}})
		Example Input: addTable(3, 4, 0, 0, readOnly = {None: {1: True})
		"""

		handle = handle_WidgetTable()
		handle.preBuild(locals())
		
		#Create the thing to put in the grid
		handle.thing = wx.grid.Grid(handle.parent.thing, style = wx.WANTS_CHARS)
		handle.thing.SetDefaultCellAlignment(wx.ALIGN_LEFT, wx.ALIGN_TOP)
		handle.thing.CreateGrid(rows, columns)

		#Grid Enabling
		if (readOnly != None):
			if (readOnly):
				handle.thing.EnableCellEditControl(False)
		if ((preEditFunction != None) or (postEditFunction != None)):
			handle.thing.EnableEditing(True)

		if (showGrid):
			handle.thing.EnableGridLines(True)

		##Grid Dragables
		if (dragableColumns):
			handle.thing.EnableDragColSize(True)
		else:
			handle.thing.EnableDragColMove(False)  

		if (dragableColumns or dragableRows):
			handle.thing.EnableDragGridSize(True)
		handle.thing.SetMargins(0, 0)

		if (dragableRows):
			handle.thing.EnableDragRowSize(True)
		else:
			handle.thing.EnableDragRowSize(True)
		
		##Row and Column Sizes
		if (rowSize != None):
			for i in range(nRows):
				handle.thing.SetRowSize(i, rowSize)

		if (columnSize != None):
			for i in range(nColumns):
				handle.thing.SetColSize(i, columnSize)         

		if (rowLabelSize != None):
			handle.thing.SetRowLabelSize(rowLabelSize)

		if (columnLabelSize != None):
			handle.thing.SetColLabelSize(columnLabelSize)

		##Minimum Sizes
		if (rowSizeMinimum != None):
			handle.thing.SetRowMinimalAcceptableWidth(rowSizeMinimum)
		
		if (columnSizeMinimum != None):
			handle.thing.SetColMinimalAcceptableWidth(columnSizeMinimum)

		##Grid Alignments
		handle.thing.SetColLabelAlignment(wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
		handle.thing.SetRowLabelAlignment(wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)

		##Grid Values
		for i in range(len(gridLabels[1])):
			handle.thing.SetColLabelValue(i, str(colLabels[i]))

		for i in range(len(gridLabels[0])):
			handle.thing.SetRowLabelValue(i, str(colLabels[i]))

		##Populate Given Cells
		if (contents != None):
			for row in range(len(contents)):
				for column in range(len(contents[0])):
					handle.thing.SetCellValue(row, column, contents[row][column])

		##Set Editability for Cells
		handle.readOnlyCatalogue = {}
		for row in range(handle.thing.GetNumberRows()):
			for column in range(handle.thing.GetNumberCols()):
				if (readOnly != None):
					if (row not in handle.readOnlyCatalogue):
						handle.readOnlyCatalogue[row] = {}
					if (column not in handle.readOnlyCatalogue[row]):
						handle.readOnlyCatalogue[row][column] = {}

					if (type(readOnly) == bool):
						handle.readOnlyCatalogue[row][column] = readOnly
					else:
						if (row in readOnly):
							#Account for whole row set
							if (type(readOnly[row]) == bool):
								handle.readOnlyCatalogue[row][column] = readOnly[row]
							else:
								if (column in readOnly[row]):
									handle.readOnlyCatalogue[row][column] = readOnly[row][column]
								else:
									handle.readOnlyCatalogue[row][column] = readOnlyDefault

						elif (None in readOnly):
							#Account for whole column set
							if (column in readOnly[None]):
								handle.readOnlyCatalogue[row][column] = readOnly[None][column]
							else:
								handle.readOnlyCatalogue[row][column] = readOnlyDefault
						else:
							handle.readOnlyCatalogue[row][column] = readOnlyDefault
				else:
					handle.readOnlyCatalogue[row][column] = readOnlyDefault

		##Default Cell Selection
		if ((default != None) and (default != (0, 0))):
			handle.thing.GoToCell(default[0], default[1])

		##Cell Editor
		editor = handle.TableCellEditor(handle, downOnEnter = enterKeyExitEdit)
		handle.thing.SetDefaultEditor(editor)

		#Bind the function(s)
		if (preEditFunction != None):
			self.betterBind(wx.grid.EVT_GRID_CELL_CHANGING, handle.thing, preEditFunction, preEditFunctionArgs, preEditFunctionKwargs)
		if (postEditFunction != None):
			self.betterBind(wx.grid.EVT_GRID_CELL_CHANGED, handle.thing, postEditFunction, postEditFunctionArgs, postEditFunctionKwargs)
		
		if (dragFunction != None):      
			self.betterBind(wx.grid.EVT_GRID_COL_SIZE, handle.thing, dragFunction, dragFunctionArgs, dragFunctionKwargs)
			self.betterBind(wx.grid.EVT_GRID_ROW_SIZE, handle.thing, dragFunction, dragFunctionArgs, dragFunctionKwargs)
		if (selectManyFunction != None):
			self.betterBind(wx.grid.EVT_GRID_RANGE_SELECT, handle.thing, selectManyFunction, selectManyFunctionArgs, selectManyFunctionKwargs)
		if (selectSingleFunction != None):
			self.betterBind(wx.grid.EVT_GRID_SELECT_CELL, handle.thing, selectSingleFunction, selectSingleFunctionArgs, selectSingleFunctionKwargs)
		
		if (rightClickCellFunction != None):
			self.betterBind(wx.grid.EVT_GRID_CELL_RIGHT_CLICK, handle.thing, rightClickCellFunction, rightClickCellFunctionArgs, rightClickCellFunctionKwargs)
		if (rightClickLabelFunction != None):
			self.betterBind(wx.grid.EVT_GRID_CELL_RIGHT_CLICK, handle.thing, rightClickLabelFunction, rightClickLabelFunctionArgs, rightClickLabelFunctionKwargs)

		if (toolTips != None):
			self.betterBind(wx.EVT_MOTION, handle.thing, handle.onTableDisplayToolTip, toolTips)
		if (arrowKeyExitEdit):
			self.betterBind(wx.EVT_KEY_DOWN, handle.thing, handle.onTableArrowKeyMove, mode = 2)
		if (editOnEnter):
			self.betterBind(wx.EVT_KEY_DOWN, handle.thing.GetGridWindow(), handle.onTableEditOnEnter, mode = 2)

		handle.postBuild(locals())

		return handle

	#Splitters
	def addSplitterDouble(self, sizer_0 = {}, sizer_1 = {}, panel_0 = {}, panel_1 = {},

		dividerSize = 1, dividerPosition = None, dividerGravity = 0.5, 
		vertical = True, minimumSize = 20, 
		
		initFunction = None, initFunctionArgs = None, initFunctionKwargs = None, 

		label = None, hidden = False, enabled = True, selected = False, 
		flex = 0, flags = "c1", parent = None, handle = None):
		"""Creates two blank panels in next to each other. 
		The border between double panels is dragable.

		leftSize (int)         - The size of the left panel. (length, width)
		rightSize (int)        - The size of the right panel. (length, width)
									~ If True: 'leftPanel' is the top panel; 'rightPanel' is the bottom panel
									~ If False: 'leftPanel' is the left panel; 'rightPanel' is the right panel
		border (str)           - What style the border has. "simple", "raised", "sunken" or "none". Only the first two letters are necissary
		dividerSize (int)      - How many pixels thick the dividing line is. Not available yet
		dividerPosition (int)  - How many pixels to the right the dividing line starts after the 'minimumSize' location
									~ If None: The line will start at the 'minimumSize' value
		dividerGravity (int)   - From 0.0 to 1.1, how much the left (or top) panel grows with respect to the right (or bottom) panel upon resizing
		vertical (bool)        - Determines the direction that the frames are split
		minimumSize (int)      - How many pixels the smaller pane must have between its far edge and the splitter.
		useDefaultSize (bool) - If True: The xSize and ySize will be overridden to fit as much of the widgets as it can. Will lock the panel size from re-sizing
		
		initFunction (str)       - The function that is ran when the panel first appears
		initFunctionArgs (any)   - The arguments for 'initFunction'
		initFunctionKwargs (any) - The keyword arguments for 'initFunction'function

		label (any)   - What this is catalogued as

		Example Input: addSplitterDouble()
		Example Input: addSplitterDouble(horizontal = False)
		Example Input: addSplitterDouble(minimumSize = 100)
		"""

		handle = handle_Splitter()
		handle.preBuild(locals())

		handle.type = "Double"

		#Create the panel splitter
		handle.thing = wx.SplitterWindow(handle.parent.thing, style = wx.SP_LIVE_UPDATE)

		#Add panels and sizers to splitter
		for i in range(2):
			#Compile instructions
			if ("panel_{}".format(i) in locals()):
				panelInstructions = locals()[("panel_{}".format(i))]
			else:
				panelInstructions = {}

			if ("sizer_{}".format(i) in locals()):
				sizerInstructions = locals()[("sizer_{}".format(i))]
			else:
				sizerInstructions = {}

			panelInstructions["parent"] = handle
			panel = handle.readBuildInstructions_panel(self, i, panelInstructions)
			handle.panelList.append(panel)
			handle.panelList[i].nested = True

			sizerInstructions["parent"] = handle.panelList[i]
			sizer = handle.readBuildInstructions_sizer(self, i, sizerInstructions)
			handle.sizerList.append(sizer)
			handle.panelList[i].nest(sizer)

		#Apply Properties
		##Direction
		if (vertical):
			handle.thing.SplitVertically(handle.panelList[0].thing, handle.panelList[1].thing)
		else:
			handle.thing.SplitHorizontally(handle.panelList[0].thing, handle.panelList[1].thing)

		##Minimum panel size
		handle.thing.SetMinimumPaneSize(minimumSize)

		##Divider position from the right
		if (dividerPosition != None):
			handle.thing.SetSashPosition(dividerPosition)
		
		##Left panel growth ratio
		handle.thing.SetSashGravity(dividerGravity)

		##Dividing line size
		handle.thing.SetSashSize(dividerSize)

		#Bind Functions
		if (initFunction != None):
			self.betterBind(wx.EVT_INIT_DIALOG, handle.thing, initFunction, initFunctionArgs, initFunctionKwargs)

		handle.postBuild(locals())

		return handle.getSizers()

	def addSplitterQuad(self, sizer_0 = {}, sizer_1 = {}, sizer_2 = {}, sizer_3 = {},

		initFunction = None, initFunctionArgs = None, initFunctionKwargs = None,

		label = None, handle = None):
		"""Creates four blank panels next to each other like a grid.
		The borders between quad panels are dragable. The itersection point is also dragable.
		The panel order is top left, top right, bottom left, bottom right.
		
		border (str)          - What style the border has. "simple", "raised", "sunken" or "none". Only the first two letters are necissary
		useDefaultSize (bool) - If True: The xSize and ySize will be overridden to fit as much of the widgets as it can. Will lock the panel size from re-sizing
		label (str)          - What this is called in the idCatalogue
		
		initFunction (str)       - The function that is ran when the panel first appears
		initFunctionArgs (any)   - The arguments for 'initFunction'
		initFunctionKwargs (any) - The keyword arguments for 'initFunction'function
		tabTraversal (bool)      - If True: Hitting the Tab key will move the selected widget to the next one

		Example Input: addSplitterQuad()
		"""

		handle = handle_Splitter()
		handle.preBuild(locals())

		handle.type = "Quad"

		#Add panels and sizers to splitter
		for i in range(4):
			#Add panels to the splitter
			handle.panelList.append(self.myWindow.addPanel(parent = handle, border = "raised"))
			handle.thing.AppendWindow(handle.panelList[i].thing)
			handle.panelList[i].nested = True

			#Add sizers to the panel
			if ("sizer_{}".format(i) in locals()):
				sizerInstructions = locals()[("sizer_{}".format(i))]
			else:
				sizerInstructions = {}
			sizer = handle.readBuildInstructions(self, i, sizerInstructions)

			handle.sizerList.append(sizer)
			handle.panelList[i].nest(sizer)

		#Create the panel splitter
		handle.thing = wx.lib.agw.fourwaysplitter.FourWaySplitter(handle.parent.thing, agwStyle = wx.SP_LIVE_UPDATE)

		#Bind Functions
		if (initFunction != None):
			self.betterBind(wx.EVT_INIT_DIALOG, handle.thing, initFunction, initFunctionArgs, initFunctionKwargs)

		handle.postBuild(locals())

		return handle.getSizers()

	def addSplitterPoly(self, panelNumbers, sizers = {},
		dividerSize = 1, dividerPosition = None, dividerGravity = 0.5, vertical = False, minimumSize = 20, 

		initFunction = None, initFunctionArgs = None, initFunctionKwargs = None,

		label = None, handle = None):
		"""Creates any number of panels side by side of each other.
		The borders between poly panels are dragable.

		panelNumbers (list)   - How many panels to set side by side. [1, 2, 3, 4, ..., n]
		splitterNumber (int)  - The index number of the splitter
		horizontal (bool)     - Determines the that direction the frames are split
									~ If True: 'leftPanel' is the top panel; 'rightPanel' is the bottom panel
									~ If False: 'leftPanel' is the left panel; 'rightPanel' is the right panel
		border (str)          - What style the border has. "simple", "raised", "sunken" or "none". Only the first two letters are necissary
		dividerSize (int)     - How many pixels thick the dividing line is. Not available yet
		dividerPosition (int) - How many pixels to the right the dividing line starts after the 'minimumSize' location
									~ If None: The line will start at the 'minimumSize' value
		dividerGravity (int)  - From 0.0 to 1.1, how much the left (or top) panel grows with respect to the right (or bottom) panel upon resizing
		tabTraversal (bool)   - If True: Pressing [tab] will move the cursor to the next widget
		horizontal (bool)     - Determines the that direction the frames are split
		minimumSize (int)     - How many pixels the smaller pane must have between its far edge and the splitter.
		useDefaultSize (bool) - If True: The xSize and ySize will be overridden to fit as much of the widgets as it can. Will lock the panel size from re-sizing
		label (str)          - What this is called in the idCatalogue
		
		initFunction (str)       - The function that is ran when the panel first appears
		initFunctionArgs (any)   - The arguments for 'initFunction'
		initFunctionKwargs (any) - The keyword arguments for 'initFunction'function
		tabTraversal (bool)      - If True: Hitting the Tab key will move the selected widget to the next one

		Example Input: addSplitterQuad([0, 1, 2, 3], 0)
		Example Input: addSplitterQuad([0, 1, 2, 3], 0, panelSizes = [(200, 300), (300, 300), (100, 300)])
		Example Input: addSplitterQuad([0, 1, 2, 3], 0, horizontal = False)
		Example Input: addSplitterQuad([0, 1, 2, 3], 0, minimumSize = 100)
		"""

		handle = handle_Splitter()
		handle.preBuild(locals())

		handle.type = "Poly"

		#Add panels and sizers to splitter
		for i in range(panelNumbers):
			#Add panels to the splitter
			handle.panelList.append(self.myWindow.addPanel(parent = handle, border = "raised"))
			handle.thing.AppendWindow(handle.panelList[i].thing)
			handle.panelList[i].nested = True

			#Add sizers to the panel
			if (i in sizers):
				sizerInstructions = sizers[i]
			else:
				sizerInstructions = {}
			sizer = handle.readBuildInstructions(self, i, sizerInstructions)

			handle.sizerList.append(sizer)
			handle.panelList[i].nest(sizer)

		#Create the panel splitter
		handle.thing = wx.lib.splitter.MultiSplitterWindow(handle.parent.thing, style = wx.SP_LIVE_UPDATE)

		#Apply Properties
		##Minimum panel size
		handle.thing.SetMinimumPaneSize(minimumSize)

		##Stack Direction
		if (vertical):
			handle.thing.SetOrientation(wx.VERTICAL)
		else:
			handle.thing.SetOrientation(wx.HORIZONTAL)

		#Bind Functions
		if (initFunction != None):
			self.betterBind(wx.EVT_INIT_DIALOG, handle.thing, initFunction, initFunctionArgs, initFunctionKwargs)

		handle.postBuild(locals())

		return handle.getSizers()

	#Notebooks
	def addNotebook(self, label = None, flags = None, tabSide = "top", flex = 0,
		fixedWidth = False, multiLine = True, padding = None, reduceFlicker = True,

		initFunction = None, initFunctionArgs = None, initFunctionKwargs = None,
		pageChangeFunction = None, pageChangeFunctionArgs = None, pageChangeFunctionKwargs = None,
		pageChangingFunction = None, pageChangingFunctionArgs = None, pageChangingFunctionKwargs = None,

		handle = None, parent = None):
		"""Creates a blank notebook.

		label (str)        - What this is called in the idCatalogue
		flags (list)         - A list of strings for which flag to add to the sizer

		tabSide (str)     - Determines which side of the panel the tabs apear on. Only the first letter is needed
			- "top": Tabs will be placed on the top (north) side of the panel
			- "bottom": Tabs will be placed on the bottom (south) side of the panel
			- "left": Tabs will be placed on the left (west) side of the panel
			- "right": Tabs will be placed on the right (east) side of the panel
		fixedWidth (bool) - Determines how tab width is determined (windows only)
			- If True: All tabs will be the same width
			- If False: Tab width will be 
		multiLine (bool) - Determines if there can be several rows of tabs
			- If True: There can be multiple rows
			- If False: There cannot be multiple rows
		padding (tuple) - Determines if there is empty space around all of the tab's icon and text in the form (left and right, top and bottom)
			- If None or -1: There is no empty spage
			- If not None or -1: This is how many pixels of empty space there will be

		initFunction (str)       - The function that is ran when the panel first appears
		initFunctionArgs (any)   - The arguments for 'initFunction'
		initFunctionKwargs (any) - The keyword arguments for 'initFunction'function

		Example Input: makeNotebook()
		Example Input: makeNotebook("myNotebook")
		Example Input: makeNotebook(padding = (5, 5))
		Example Input: makeNotebook(padding = (5, None))
		"""

		handle = handle_Notebook()
		handle.preBuild(locals())

		#Configure Flags            
		flags, x, border = self.getItemMod(flags)

		if (tabSide == None):
			tabSide = "top"
		else:
			if (not isinstance(tabSide, str)):
				errorMessage = "'tabSide' must be a string. Please choose 'top', 'bottom', 'left', or 'right'"
				raise ValueError(errorMessage)
			if (tabSide not in ["top", "bottom", "left", "right"]):
				errorMessage = "'tabSide' must be 'top', 'bottom', 'left', or 'right'"
				raise KeyError(errorMessage)

		if (tabSide[0] == "t"):
			flags += "|wx.NB_TOP"
		elif (tabSide[0] == "b"):
			flags += "|wx.NB_BOTTOM"
		elif (tabSide[0] == "l"):
			flags += "|wx.NB_LEFT"
		else:
			flags += "|wx.NB_RIGHT"

		if (reduceFlicker):
			flags += "|wx.CLIP_CHILDREN|wx.NB_NOPAGETHEME"
		if (fixedWidth):
			flags += "|wx.NB_FIXEDWIDTH"

		#Create notebook object
		handle.thing = wx.Notebook(handle.parent.thing, style = eval(flags))

		#Bind Functions
		if (initFunction != None):
			self.betterBind(wx.EVT_INIT_DIALOG, handle.thing, initFunction, initFunctionArgs, initFunctionKwargs)
		if (pageChangeFunction != None):
			self.betterBind(wx.EVT_NOTEBOOK_PAGE_CHANGED, handle.thing, pageChangeFunction, pageChangeFunctionArgs, pageChangeFunctionKwargs)
		if (pageChangingFunction != None):
			self.betterBind(wx.EVT_NOTEBOOK_PAGE_CHANGING, handle.thing, pageChangingFunction, pageChangingFunctionArgs, pageChangingFunctionKwargs)

		#Determine if there is padding on the tabs
		if ((padding != None) and (padding != -1)):
			#Ensure correct format
			if ((padding[0] != None) and (padding[0] != -1)):
				width = padding[0]
			else:
				width = 0

			if ((padding[1] != None) and (padding[1] != -1)):
				width = padding[1]
			else:
				height = 0

			#Apply padding
			size = wx.Size(width, height)
			handle.thing.SetPadding(size)

		#Set values
		if (isinstance(self, handle_Window)):
			handle.myWindow = self
		else:
			handle.myWindow = self.myWindow

		handle.postBuild(locals())

		self.nest(handle)

		return handle

	#Sizers
	def addSizerBox(self, *args, **kwargs):
		"""Overload for addSizerBox in handle_Window().
		Adds the created sizer to this sizer.
		"""

		handle = handle_Sizer()
		handle.type = "Box"

		argument_catalogue = self.arrangeArguments(handle_Window.addSizerBox, args, kwargs)
		argument_catalogue["self"] = self
		# argument_catalogue["parent"] = self.parent

		handle.build(argument_catalogue)
		self.nest(handle)

		return handle

	def addSizerText(self, *args, **kwargs):
		"""Overload for addSizerText in handle_Window().
		Adds the created sizer to this sizer.
		"""

		handle = handle_Sizer()
		handle.type = "Text"

		argument_catalogue = self.arrangeArguments(handle_Window.addSizerText, args, kwargs)
		argument_catalogue["self"] = self
		# argument_catalogue["parent"] = self.parent

		handle.build(argument_catalogue)
		self.nest(handle)

		return handle

	def addSizerGrid(self, *args, **kwargs):
		"""Overload for addSizerGrid in handle_Window().
		Adds the created sizer to this sizer.
		"""

		handle = handle_Sizer()
		handle.type = "Grid"

		argument_catalogue = self.arrangeArguments(handle_Window.addSizerGrid, args, kwargs)
		argument_catalogue["self"] = self
		# argument_catalogue["parent"] = self.parent

		handle.build(argument_catalogue)
		self.nest(handle)

		return handle

	def addSizerGridFlex(self, *args, **kwargs):
		"""Overload for addSizerGridFlex in handle_Window().
		Adds the created sizer to this sizer.
		"""

		handle = handle_Sizer()
		handle.type = "Flex"

		argument_catalogue = self.arrangeArguments(handle_Window.addSizerGridFlex, args, kwargs)
		argument_catalogue["self"] = self
		# argument_catalogue["parent"] = self.parent

		handle.build(argument_catalogue)
		self.nest(handle)

		return handle

	def addSizerGridBag(self, *args, **kwargs):
		"""Overload for addSizerGridBag in handle_Window().
		Adds the created sizer to this sizer.
		"""

		handle = handle_Sizer()
		handle.type = "Bag"

		argument_catalogue = self.arrangeArguments(handle_Window.addSizerGridBag, args, kwargs)
		argument_catalogue["self"] = self
		# argument_catalogue["parent"] = self.parent

		handle.build(argument_catalogue)
		self.nest(handle)

		return handle

	def addSizerWrap(self, *args, **kwargs):
		"""Overload for addSizerWrap in handle_Window().
		Adds the created sizer to this sizer.
		"""

		handle = handle_Sizer()
		handle.type = "Wrap"

		argument_catalogue = self.arrangeArguments(handle_Window.addSizerWrap, args, kwargs)
		argument_catalogue["self"] = self
		# argument_catalogue["parent"] = self.parent

		handle.build(argument_catalogue)
		self.nest(handle)

		return handle

class handle_Window(handle_Container_Base):
	"""A handle for working with a wxWindow."""

	def __init__(self):
		"""Initializes defaults."""

		#Initialize inherited classes
		handle_Container_Base.__init__(self)

		#Defaults
		self.mainPanel = None
		self.thing = None
		self.visible = False
		self.complexity_total = 0
		self.complexity_max = 20

		self.statusBarOn = True
		self.toolBarOn = True
		self.autoSize = True
		self.menuBar = None
		self.statusBar = None

		self.finalFunctionList = []
		self.sizersIterating = {} #Keeps track of which sizers have been used in a while loop, as well as if they are still in the while loop {sizer (handle): [currently in a while loop (bool), order entered (int)]}
		self.keyPressQueue = {} #A dictionary that contains all of all the key events that need to be bound to this window


	def __str__(self):
		"""Gives diagnostic information on the Window when it is printed out."""

		output = handle_Container_Base.__str__(self)
		
		if (self.mainPanel != None):
			output += "-- main panel id: {}\n".format(id(self.mainPanel))
		return output

	def build(self, argument_catalogue):
		#Fill in default values
		for item in inspect.signature(Controller.addWindow).parameters.values():
			if (item.name not in argument_catalogue):
				argument_catalogue[item.name] = item.default

		#Prebuild
		handle_Container_Base.preBuild(self, argument_catalogue)

		#Nesting windows does not mean anything
		self.nested = True #Turns off warning

		#Determine window style
		tabTraversal, stayOnTop, floatOnParent, resize, topBar, minimize, maximize, close, title = self.getArguments(argument_catalogue, ["tabTraversal", "stayOnTop", "floatOnParent", "resize", "topBar", "minimize", "maximize", "close", "title"])
		flags = "wx.CLIP_CHILDREN|wx.SYSTEM_MENU"
		if (tabTraversal):
			flags += "|wx.TAB_TRAVERSAL"

		if (stayOnTop):
			flags += "|wx.STAY_ON_TOP"

		if (floatOnParent):
			flags += "|wx.FRAME_FLOAT_ON_PARENT"

		if (resize):
			flags += "|wx.RESIZE_BORDER"

		if (topBar != None):
			if (topBar):
				flags += "|wx.MINIMIZE_BOX|wx.MAXIMIZE_BOX|wx.CLOSE_BOX"
		else:
			if (minimize):
				flags += "|wx.MINIMIZE_BOX"

			if (maximize):
				flags += "|wx.MAXIMIZE_BOX"

			if (close):
				flags += "|wx.CLOSE_BOX"

		if (title != None):
			flags += "|wx.CAPTION"
		else:
			title = ""

		#Make the frame
		size, position = self.getArguments(argument_catalogue, ["size", "position"])
		self.thing = wx.Frame(None, title = title, size = size, pos = position, style = eval(flags))
		
		#Add Properties
		icon, internal = self.getArguments(argument_catalogue, ["icon", "internal"])
		if (icon != None):
			self.setIcon(icon, internal)

		#Bind functions
		delFunction, delFunctionArgs, delFunctionKwargs = self.getArguments(argument_catalogue, ["delFunction", "delFunctionArgs", "delFunctionKwargs"])
		initFunction, initFunctionArgs, initFunctionKwargs = self.getArguments(argument_catalogue, ["initFunction", "initFunctionArgs", "initFunctionKwargs"])
		idleFunction, idleFunctionArgs, idleFunctionKwargs = self.getArguments(argument_catalogue, ["idleFunction", "idleFunctionArgs", "idleFunctionKwargs"])
		controller = self.getAddressValue(self.nestingAddress[0])[None]
		
		if (initFunction != None):
			self.betterBind(wx.EVT_ACTIVATE, self.thing, initFunction, initFunctionArgs, initFunctionKwargs)

		if (delFunction != None):
			self.betterBind(wx.EVT_CLOSE, self.thing, delFunction, delFunctionArgs, delFunctionKwargs)
		else:
			endProgram = self.getArguments(argument_catalogue, ["endProgram"])
			if (endProgram != None):
				if (endProgram):
					delFunction = controller.onExit
				else:
					delFunction = controller.onQuit
			else:
				delFunction = controller.onHide

			self.betterBind(wx.EVT_CLOSE, self.thing, delFunction)

		if (idleFunction != None):
			self.idleQueue = None
			self.betterBind(wx.EVT_IDLE, self.thing, idleFunction, idleFunctionArgs, idleFunctionKwargs)
		else:
			self.betterBind(wx.EVT_IDLE, self.thing, controller.onIdle)

		#Post build
		handle_Container_Base.postBuild(self, argument_catalogue)

		#Unpack arguments
		panel = argument_catalogue["panel"]

		#Make the main panel
		if (panel):
			self.mainPanel = self.addPanel()#"-1", parent = handle, size = (10, 10), tabTraversal = tabTraversal, useDefaultSize = False)

	def getValue(self, label, *args, **kwargs):
		"""Overload for getValue for handle_Widget_Base."""

		handle = self.get(label, *args, **kwargs)
		event = self.getArgument_event(label, args, kwargs)
		value = handle.getValue(event = event)
		return value

	def getIndex(self, label, *args, **kwargs):
		"""Overload for getIndex for handle_Widget_Base."""

		handle = self.get(label, *args, **kwargs)
		event = self.getArgument_event(label, args, kwargs)
		value = handle.getIndex(event = event)
		return value

	def getAll(self, label, *args, **kwargs):
		"""Overload for getAll for handle_Widget_Base."""

		handle = self.get(label, *args, **kwargs)
		event = self.getArgument_event(label, args, kwargs)
		value = handle.getAll(event = event)
		return value

	def getLabel(self, label, *args, **kwargs):
		"""Overload for getLabel for handle_Widget_Base."""

		handle = self.get(label, *args, **kwargs)
		event = self.getArgument_event(label, args, kwargs)
		value = handle.getLabel(event = event)
		return value

	def setValue(self, label, newValue, *args, **kwargs):
		"""Overload for setValue for handle_Widget_Base."""

		handle = self.get(label, *args, **kwargs)
		event = self.getArgument_event(label, args, kwargs)
		value = handle.setValue(newValue, event = event)
		return value

	def setSelection(self, label, newValue, *args, **kwargs):
		"""Overload for setSelection for handle_Widget_Base."""

		handle = self.get(label, *args, **kwargs)
		event = self.getArgument_event(label, args, kwargs)
		value = handle.setSelection(newValue, event = event)
		return value

	#Change Settings
	def setWindowSize(self, x, y):
		"""Re-defines the size of the window.

		x (int)     - The width of the window
		y (int)     - The height of the window

		Example Input: setWindowSize(350, 250)
		"""

		#Change the frame size
		self.autoSize = False
		self.thing.SetSize((x, y))

	def setMinimumFrameSize(self, size = (100, 100)):
		"""Sets the minimum window size for the user
		Note: the program can still explicity change the size to be smaller by using setWindowSize().

		size (int tuple) - The size of the window. (length, width)

		Example Input: setMinimumFrameSize()
		Example Input: setMinimumFrameSize((200, 100))
		"""

		#Set the size property
		self.thing.SetMinSize(size)

	def setMaximumFrameSize(self, size = (900, 700)):
		"""Sets the maximum window size for the user
		Note: the program can still explicity change the size to be smaller by using setWindowSize().

		size (int tuple) - The size of the window. (length, width)

		Example Input: setMaximumFrameSize()
		Example Input: setMaximumFrameSize((700, 300))
		"""

		#Set the size property
		self.thing.SetMaxSize(size)

	def setAutoWindowSize(self, minimum = None):
		"""Re-defines the size of the window.

		minimum (bool) - Whether the window will be sized to the minimum best size or the maximum 
			- If None: The auto size will not be set as a minimum or maximum.

		Example Input: setAutoWindowSize()
		Example Input: setAutoWindowSize(True)
		Example Input: setAutoWindowSize(False)
		"""

		#Determine best size
		size = self.thing.GetBestSize()

		#Set the size
		if (minimum != None):
			if (minimum):
				self.thing.SetMinSize(size)
			else:
				self.thing.SetMaxSize(size)

	def setWindowTitle(self, title):
		"""Re-defines the title of the window.

		title (str) - What the new title is

		Example Input: setWindowTitle(0, "test")
		"""

		#Set the title
		self.thing.SetTitle(title)

	def centerWindow(self):
		"""Centers the window on the screen.

		Example Input: centerWindow()
		"""

		self.thing.Center()

	#Visibility
	def showWindow(self):
		"""Shows a specific window to the user.
		If the window is already shown, it will bring it to the front

		Example Input: showWindow()
		"""

		self.thing.Show()

		if (not self.visible):
			self.visible = True
		else:
			if (self.thing.IsIconized()):
				self.thing.Iconize(False)
			else:
				self.thing.Raise()

	def showWindowCheck(self, notShown = False):
		"""Checks if a window is currently being shown to the user.

		notShown (bool) - If True: checks if the window is NOT shown instead

		Example Input: showWindowCheck()
		"""

		if (notShown):
			if (self.visible):
				return False
			return True
		else:
			if (self.visible):
				return True
			return False

	def onShowWindow(self, event, *args, **kwargs):
		"""Event function for showWindow()"""

		self.showWindow(*args, **kwargs)
		event.Skip()

	def hideWindow(self):
		"""Hides the window from view, but does not close it.
		Note: This window continues to run and take up memmory. Local variables are still active.

		Example Input: hideWindow()
		"""

		if (self.visible):
			self.thing.Hide()
			self.visible = False
		else:
			warnings.warn("Window {} is already hidden".format(self.label), Warning, stacklevel = 2)

	def onHideWindow(self, event, *args, **kwargs):
		"""Event function for hideWindow()"""
		
		self.hideWindow(*args, **kwargs)
		event.Skip()

	#Panels
	def addPanel(self, label = None, size = wx.DefaultSize, border = wx.NO_BORDER, position = wx.DefaultPosition, parent = None,
		tabTraversal = True, useDefaultSize = False, autoSize = True, flags = "c1", 

		initFunction = None, initFunctionArgs = None, initFunctionKwargs = None,

		handle = None):
		"""Creates a blank panel window.

		label (any)     - What this is catalogued as
		size (int tuple)  - The size of the panel. (length, width)
		border (str)      - What style the border has. "simple", "raised", "sunken" or "none". Only the first two letters are necissary
		parent (wxObject) - If None: The parent will be 'self'.
		
		tabTraversal (bool)   - If True: Pressing [tab] will move the cursor to the next widget
		useDefaultSize (bool) - If True: The xSize and ySize will be overridden to fit as much of the widgets as it can. Will lock the panel size from re-sizing

		initFunction (str)       - The function that is ran when the panel first appears
		initFunctionArgs (any)   - The arguments for 'initFunction'
		initFunctionKwargs (any) - The keyword arguments for 'initFunction'function

		Example Input: addPanel(0)
		Example Input: addPanel(0, size = (200, 300))
		Example Input: addPanel(0, border = "raised")
		Example Input: addPanel(0, useDefaultSize = True)
		Example Input: addPanel(0, tabTraversal = False)
		"""

		handle = handle_Panel()
		handle.build(locals())

		return handle

	#Sizers
	def getSizer(self, sizerLabel = None, returnAny = False):
		"""Returns a sizer when given the sizer's label.

		sizerLabel (int)  - The label of the sizer. 
			-If None: The whole sizer list is returned
		returnAny (bool)   - If True: Any sizer will be returned.

		Example Input: getSizer()
		Example Input: getSizer(0)
		Example Input: getSizer(returnAny = False)
		"""

		sizerList = self.getNested(include = handle_Sizer)

		#Account for no sizers available
		if (len(sizerList) == 0):
			errorMessage = "{} has no sizers".format(self.__repr__())
			raise ValueError(errorMessage)

		#Account for random sizer request
		if (returnAny):
			return sizerList[0]

		#Account for whole list request
		elif (sizerLabel == None):
			return sizerList

		#Search for requested sizer
		for sizer in sizerList:
			if (sizerLabel == sizer.label):
				return sizer

		#No sizer found
		errorMessage = "{} has no sizer '{}'".format(self.__repr__(), sizerLabel)
		raise ValueError(errorMessage)

	def addSizerGrid(self, rows = 1, columns = 1, rowGap = 0, colGap = 0, 
		minWidth = -1, minHeight = -1, label = None, text = None,

		parent = None, hidden = False, handle = None):
		"""Creates a grid sizer to the specified size.

		label (any)     - What this is catalogued as
		rows (int)        - The number of rows that the grid has
		columns (int)     - The number of columns that the grid has
		hidden (bool)     - If True: All items in the sizer are hidden from the user, but they are still created
		rowGap (int)      - Empty space between each row
		colGap (int)      - Empty space between each column
		minWidth (int)    - The minimum width of a box. -1 means automatic
		minHeight (int)   - The minimum height of a box. -1 means automatic

		Example Input: addSizerGrid()
		Example Input: addSizerGrid(0)
		Example Input: addSizerGrid(rows = 4, columns = 3)
		Example Input: addSizerGrid(0, rows = 4, columns = 3)
		"""

		handle = handle_Sizer()
		handle.type = "Grid"

		kwargs = locals()
		# kwargs["parent"] = self.parent

		handle.build(kwargs)
		return handle

	def addSizerGridFlex(self, rows = 1, columns = 1, rowGap = 0, colGap = 0, 
		minWidth = -1, minHeight = -1, flexGrid = True, label = None, text = None,

		parent = None, hidden = False, vertical = None, handle = None):
		"""Creates a flex grid sizer.
		############## NEEDS TO BE FIXED #################

		label (any)     - What this is catalogued as
		rows (int)        - The number of rows that the grid has
		columns (int)     - The number of columns that the grid has
		rowGap (int)      - Empty space between each row
		colGap (int)      - Empty space between each column
		hidden (bool)     - If True: All items in the sizer are hidden from the user, but they are still created
		minWidth (int)    - The minimum width of a box. -1 means automatic
		minHeight (int)   - The minimum height of a box. -1 means automatic
		flexGrid (bool)   - True if the grid will be flexable. If False, this is like a normal grid sizer.
		vertical (bool)   - Determines what direction cells are flexibally (unequally) sized
			- If True: Rows are sized
			- If False: Columns are sized
			- If None: Both are sized

		Example Input: addSizerGridFlex()
		Example Input: addSizerGridFlex(0)
		Example Input: addSizerGridFlex(rows = 4, columns = 3)
		Example Input: addSizerGridFlex(0, rows = 4, columns = 3)
		"""

		handle = handle_Sizer()
		handle.type = "Flex"

		kwargs = locals()
		# kwargs["parent"] = self.parent

		handle.build(kwargs)
		return handle

	def addSizerGridBag(self, rows = 1, columns = 1, rowGap = 0, colGap = 0, minWidth = -1, minHeight = -1, 
		emptySpace = None, flexGrid = True, label = None, text = None,

		parent = None, hidden = False, vertical = None, handle = None):
		"""Creates a bag grid sizer.

		label (any)      - What this is catalogued as
		rows (int)         - The number of rows that the grid has
		columns (int)      - The number of columns that the grid has
		rowGap (int)       - Empty space between each row
		colGap (int)       - Empty space between each column
		minWidth (int)     - The minimum width of a box. -1 means automatic
		minHeight (int)    - The minimum height of a box. -1 means automatic
		hidden (bool)      - If True: All items in the sizer are hidden from the user, but they are still created
		emptySpace (tuple) - The space taken up by cells that are empty or hidden; (row width, column width)
		flexGrid (bool)    - True if the grid will be flexable. If False, this is like a normal grid sizer.
		vertical (bool)    - Determines what direction cells are flexibally (unequally) sized
			- If True: Rows are sized
			- If False: Columns are sized
			- If None: Both are sized

		Example Input: addSizerGridBag()
		Example Input: addSizerGridBag(0)
		Example Input: addSizerGridBag(0, rows = 4, columns = 3)
		Example Input: addSizerGridBag(0, rows = 4, columns = 3, emptySpace = (0, 0))
		"""

		handle = handle_Sizer()
		handle.type = "Bag"

		kwargs = locals()
		# kwargs["parent"] = self.parent

		handle.build(kwargs)
		return handle

	def addSizerBox(self, minWidth = -1, minHeight = -1, label = None, text = None,
		parent = None, hidden = False, vertical = True, handle = None):
		"""Creates a box sizer.

		label (any)     - What this is catalogued as
		minWidth (int)    - The minimum width of a box. -1 means automatic
		minHeight (int)   - The minimum height of a box. -1 means automatic
		horizontal (bool) - True to align items horizontally. False to align items vertically
		hidden (bool)     - If True: All items in the sizer are hidden from the user, but they are still created

		Example Input: addSizerBox()
		Example Input: addSizerBox(0)
		Example Input: addSizerBox(vertical = False)
		Example Input: addSizerBox(0, vertical = False)
		"""

		handle = handle_Sizer()
		handle.type = "Box"

		kwargs = locals()
		# kwargs["parent"] = self.parent

		handle.build(kwargs)
		return handle

	def addSizerText(self, text = "", minWidth = -1, minHeight = -1, label = None, 

		parent = None, hidden = False, vertical = True, handle = None):
		"""Creates a static box sizer.
		This is a sizer surrounded by a box with a title, much like a wxRadioBox.

		label (any)     - What this is catalogued as
		text (str)      - The text that appears above the static box
		minWidth (int)    - The minimum width of a box. -1 means automatic
		minHeight (int)   - The minimum height of a box. -1 means automatic
		horizontal (bool) - True to align items horizontally. False to align items vertically
		hidden (bool)     - If True: All items in the sizer are hidden from the user, but they are still created

		Example Input: addSizerText()
		Example Input: addSizerText(0)
		Example Input: addSizerText(text = "Lorem")
		Example Input: addSizerText(0, text = "Lorem")
		"""

		handle = handle_Sizer()
		handle.type = "Text"

		kwargs = locals()
		# kwargs["parent"] = self.parent

		handle.build(kwargs)
		return handle

	def addSizerWrap(self, minWidth = -1, minHeight = -1, label = None, 
		extendLast = False, text = None,

		parent = None, hidden = False, vertical = True, handle = None):
		"""Creates a wrap sizer.
		The widgets will arrange themselves into rows and columns on their own, starting in the top-left corner.

		label (any)     - What this is catalogued as
		text (str)      - The text that appears above the static box
		minWidth (int)    - The minimum width of a box. -1 means automatic
		minHeight (int)   - The minimum height of a box. -1 means automatic
		horizontal (bool) - Determines the primary direction to fill widgets in
			- If True: Align items horizontally first
			- If False: Align items vertically first
		hidden (bool)     - If True: All items in the sizer are hidden from the user, but they are still created
		extendLast (bool) - If True: The last widget will extend to fill empty space

		Example Input: addSizerWrap()
		Example Input: addSizerWrap(0)
		"""

		handle = handle_Sizer()
		handle.type = "Wrap"

		kwargs = locals()
		# kwargs["parent"] = self.parent

		handle.build(kwargs)
		return handle

	#Menus
	def getMenu(self, menuLabel = None):
		"""Returns a menu when given the menu's label.

		menuLabel (int)  - The label of the menu. 
			-If None: The whole menu list is returned

		Example Input: getMenu()
		Example Input: getMenu(0)
		"""

		menuList = self.getNested(include = handle_Menu)

		#Account for no menus available
		if (len(menuList) == 0):
			errorMessage = "{} has no menus".format(self.__repr__())
			raise ValueError(errorMessage)

		#Account for whole list request
		if (menuLabel == None):
			return menuList

		#Search for requested menu
		for menu in menuList:
			if (menuLabel == menu.label):
				return menu

		#No menu found
		errorMessage = "{} has no menu '{}'".format(self.__repr__(), menuLabel)
		raise ValueError(errorMessage)

	def addMenuBar(self):
		"""Adds a menu bar to the top of the window.
		Menus with menu items can be added to this.

		Example Input: addMenuBar()
		"""

		self.menuBar = wx.MenuBar()
		self.thing.SetMenuBar(self.menuBar)

	def addMenu(self, label = None, text = " ", detachable = False,

		parent = None, hidden = False, enabled = False, handle = None):
		"""Adds a menu to a pre-existing menubar.
		This is a collapsable array of menu items.

		text (str)        - What the menu is called
			If you add a '&', a keyboard shortcut will be made for the letter after it
		label (str)     - What this is called in the idCatalogue
		detachable (bool) - If True: The menu can be undocked

		Example Input: addMenu(0, "&File")
		Example Input: addMenu("first", "&File")
		"""

		handle = handle_Menu()
		handle.type = "Menu"
		handle.preBuild(locals())
		handle.postBuild(locals())

		return handle

	def addPopupMenu(self, label = None, rightClick = True, 

		preFunction = None, preFunctionArgs = None, preFunctionKwargs = None, 
		postFunction = None, postFunctionArgs = None, postFunctionKwargs = None,

		parent = None, hidden = False, enabled = False, handle = None):
		"""Enables a popup menu.

		label (str) - A unique name for this popupMenu. Used to interact with it later.

		preFunction (str)       - The function that is ran after the popup menu appears
		preFunctionArgs (any)   - The arguments for 'preFunction'
		preFunctionKwargs (any) - The keyword arguments for 'preFunction'function

		postFunction (str)       - The function that is ran after the popup menu appears
		postFunctionArgs (any)   - The arguments for 'postFunction'
		postFunctionKwargs (any) - The keyword arguments for 'postFunction'function

		rightClick - Whether right clicking (True) or left clicking (False) will bring it up.
			- If None: Will not respond to a right click. Assumes you will trigger the popup menu some other way.

		Example Input: addPopupMenu()
		Example Input: addPopupMenu(0)
		Example Input: addPopupMenu("main")
		Example Input: addPopupMenu(0, rightClick = False)
		Example Input: addPopupMenu(0, rightClick = None)
		Example Input: addPopupMenu(0, myFrame.onHideWindow, 0)
		"""

		handle = handle_MenuPopup()
		handle.type = "MenuPopup"
		handle.preBuild(locals())
		handle.postBuild(locals())
		return handle

	#Status Bars
	def addStatusBar(self):
		"""Adds a status bar to the bottom of the window."""

		self.statusBar = self.thing.CreateStatusBar()

	def setStatusText(self, message):
		"""Sets the text shown in the status bar.

		message (str) - What the status bar will say.

		Example Input: setStatusText("Ready")
		"""

		self.statusBar.SetStatusText(message)

	#Etc
	def setIcon(self, icon, internal = False):
		"""Sets the icon for the .exe file.

		icon (str) - The file path to the icon for the menu item
			If None: No icon will be shown
		internal (bool) - If True: The icon provided is an internal icon, not an external file

		Example Input: setIcon("resources/cte_icon.ico")
		Example Input: setIcon("lightBulb", True)
		"""

		#Get the image
		image = self.getImage(icon, internal)
		image = self.convertBitmapToImage(image)
		image = image.Scale(16, 16, wx.IMAGE_QUALITY_HIGH)
		image = self.convertImageToBitmap(image)

		#Create the icon
		myIcon = wx.Icon(image)
		self.thing.SetIcon(myIcon)

	def closeWindow(self):
		"""Closes the window. This frees up the memmory. Local variables will be lost.

		Example Input: closeWindow()
		"""

		self.thing.Destroy()

		if (self.visible):
			self.visible = False
		else:
			errorMessage = "Window {} is already closed.".format(self.label)
			raise ValueError(errorMessage)

	def onCloseWindow(self, event, *args, **kwargs):
		"""Event function for closeWindow()."""
		
		self.closeWindow(*args, **kwargs)
		event.Skip()

	def typicalWindowSetup(self, skipMenu = False, skipStatus = False, skipPopup = False, skipMenuExit = False):
		"""Adds the things a window typically needs. Uses sizer "-1".
			- Menu Bar with exit button
			- Status Bar
			- Popup Menu
			- Border

		which (int)       - The index number of the window. Can be the title of the window
		skipMenu (bool)   - If True: No top bar menu will be added
		skipStatus (bool) - If True: No status bar will be added
		skipPopup (bool)  - If True: No popup menu will be added

		Example Input: typicalWindowSetup()
		"""

		pass

		# #Add Menu Bar
		# if (not skipMenu):
		# 	self.addMenuBar()
		# 	if (not skipMenuExit):
		# 		self.addMenu(0, "&File")
		# 		self.addMenuItem(0, "&Exit", myFunction = "self.onExit", icon = "quit", internal = True, toolTip = "Closes this program", label = "Frame{}_typicalWindowSetup_fileExit".format(self.windowLabel))

		# #Add Status Bar
		# if (not skipStatus):
		# 	self.addStatusBar()
		# 	self.setStatusText("Ready")

		# #Add Popup Menu
		# if (not skipPopup):
		# 	self.createPopupMenu("-1")
		# 	self.addPopupMenuItem("-1", "&Minimize", "self.onMinimize")
		# 	self.addPopupMenuItem("-1", "Maximize", "self.onMaximize")
		# 	self.addPopupMenuItem("-1", "Close", "self.onExit")

	def updateWindow(self, autoSize = None):
		"""Refreshes what the window looks like when things on the top-level sizer are changed.

		autoSize (bool) - Determines how the autosizing behavior is applied
			- If True: The window size will be changed to fit the sizers within
			- If False: The window size will be what was defined when it was initially created
			- If None: The internal autosize state will be used

		Example Input: updateWindow()
		Example Input: updateWindow(autoSize = False)
		"""

		catalogue = self.getAddressValue(self.nestingAddress + [id(self)])

		#Skip empty windows
		if (len(catalogue) > 1):
			#Refresh the window
			if (autoSize == None):
				autoSize = self.autoSize

			#Get random sizer
			# sizerList = [key for key, value in catalogue.items() if (key != None)]
			# sizer = catalogue[sizerList[0]][None]

			sizer = self.getSizer(returnAny = True)

			if (self.mainPanel != None):
				# self.thing.SetSizerAndFit(sizer.thing)
				self.mainPanel.thing.SetSizerAndFit(sizer.thing)

			else:
				self.thing.SetSizerAndFit(sizer.thing)

			#Auto-size the window
			if (autoSize):
				##Toggle the window size before setting to best size
				bestSize = self.thing.GetBestSize()
				modifiedSize = (bestSize[0] + 1, bestSize[1] + 1)
				self.thing.SetSize(modifiedSize)
				self.thing.SetSize(bestSize)

			else:
				#Fix Panel Patch
				currentSize = self.thing.GetSize()
				modifiedSize = (currentSize[0] + 1, currentSize[1] + 1)
				self.thing.SetSize(modifiedSize)
				self.thing.SetSize(currentSize)

	def nest(self, inside, outside):
		"""Nests an object in another object.

		inside (handle) - What is being nested
		outside (handle) - What is being nested in

		Example Input: nest(mySizer_2, mySizer_1)
		"""

		outside.nest(inside)

	def nestSizerInSizer(self, insideNumber, outsideNumber, *args, **kwargs):
		"""Allows you to use labels for nesting a sizer in a sizer"""

		inside = self.getSizer(insideNumber)
		outside = self.getSizer(outsideNumber)
		self.nest(inside, outside, *args, **kwargs)

	def addFinalFunction(self, myFunctionList, myFunctionArgsList = None, myFunctionKwargsList = None):
		"""Adds a function to the queue that will run after building, but before launching, the app."""

		self.finalFunctionList.append([myFunctionList, myFunctionArgsList, myFunctionKwargsList])

	def addKeyPress(self, key, myFunctionList, myFunctionArgsList = None, myFunctionKwargsList = None, 
		keyUp = True, numpad = False, ctrl = False, alt = False, shift = False):
		"""Adds a single key press event to the frame.

		key (str)              - The keyboard key to bind the function(s) to
		myFunctionList (str)   - The function that will be ran when the event occurs
		myFunctionArgs (any)   - Any input arguments for myFunction. A list of multiple functions can be given
		myFunctionKwargs (any) - Any input keyword arguments for myFunction. A list of variables for each function can be given. The index of the variables must be the same as the index for the functions
		
		keyUp (bool)  - If True: The function will run when the key is released
						If False: The function will run when the key is pressed
		numpad (bool) - If True: The key is located on the numpad
		ctrl (bool)   - If True: The control key is pressed
		alt (bool)    - If True: The control key is pressed
		shift (bool)  - If True: The shift key is pressed

		Example Input: addKeyPress("s", self.onSave, ctrl = True)
		Example Input: addKeyPress("x", "self.onExit", ctrl = True, alt = True)
		"""

		#Get the correct object to bind to
		if (self.mainPanel != None):
			thing = self.mainPanel
		else:
			thing = self

		#Take care of the modifier keys
		if (ctrl):
			key += "$@$ctrl"

		if (alt):
			key += "$@$alt"

		if (shift):
			key += "$@$shift"

		if (numpad):
			key += "$@$numpad"

		if (not keyUp):
			key += "$@$noKeyUp"

		#Queue up the key event
		##This is needed so that future key events do not over-write current key events
		if (thing not in self.keyPressQueue):
			self.keyPressQueue[thing] = {key: [myFunctionList, myFunctionArgsList, myFunctionKwargsList]}
		else:
			if (key not in self.keyPressQueue[thing]):
				self.keyPressQueue[thing][key] = [myFunctionList, myFunctionArgsList, myFunctionKwargsList]
			else:
				self.keyPressQueue[thing][key].append([myFunctionList, myFunctionArgsList, myFunctionKwargsList])

	#Overloads
	def addMenuItem(self, menuLabel, *args, **kwargs):
		"""Overload for addMenuItem in handle_Menu()."""

		myMenu = self.getMenu(menuLabel)
		myMenu.addMenuItem(*args, **kwargs)

	def addMenuSeparator(self, menuLabel, *args, **kwargs):
		"""Overload for addMenuSeparator in handle_Menu()."""

		myMenu = self.getMenu(menuLabel)
		myMenu.addMenuSeparator(*args, **kwargs)

	def addMenuSub(self, menuLabel, *args, **kwargs):
		"""Overload for addMenuSub in handle_Menu()."""

		myMenu = self.getMenu(menuLabel)
		myMenu.addMenuSub(*args, **kwargs)

	def growFlexColumn(self, sizerLabel, *args, **kwargs):
		"""Overload for growFlexColumn in handle_Sizer()."""

		mySizer = self.getSizer(sizerLabel)
		mySizer.growFlexColumn(*args, **kwargs)

	def growFlexRow(self, sizerLabel, *args, **kwargs):
		"""Overload for growFlexRow in handle_Sizer()."""

		mySizer = self.getSizer(sizerLabel)
		mySizer.growFlexRow(*args, **kwargs)

	def growFlexColumnAll(self, sizerLabel, *args, **kwargs):
		"""Overload for growFlexColumnAll in handle_Sizer()."""

		mySizer = self.getSizer(sizerLabel)
		mySizer.growFlexColumnAll(*args, **kwargs)

	def growFlexRowAll(self, sizerLabel, *args, **kwargs):
		"""Overload for growFlexRowAll in handle_Sizer()."""

		mySizer = self.getSizer(sizerLabel)
		mySizer.growFlexRowAll(*args, **kwargs)

	def addText(self, sizerLabel, *args, **kwargs):
		"""Overload for addText in handle_Sizer()."""

		mySizer = self.getSizer(sizerLabel)
		handle = mySizer.addText(*args, **kwargs)

		return handle

	def addHyperlink(self, sizerLabel, *args, **kwargs):
		"""Overload for addHyperlink in handle_Sizer()."""

		mySizer = self.getSizer(sizerLabel)
		handle = mySizer.addHyperlink(*args, **kwargs)

		return handle

	def addEmpty(self, sizerLabel, *args, **kwargs):
		"""Overload for addEmpty in handle_Sizer()."""

		mySizer = self.getSizer(sizerLabel)
		handle = mySizer.addEmpty(*args, **kwargs)

		return handle

	def addLine(self, sizerLabel, *args, **kwargs):
		"""Overload for addLine in handle_Sizer()."""

		mySizer = self.getSizer(sizerLabel)
		handle = mySizer.addLine(*args, **kwargs)

		return handle

	def addListDrop(self, sizerLabel, *args, **kwargs):
		"""Overload for addListDrop in handle_Sizer()."""

		mySizer = self.getSizer(sizerLabel)
		handle = mySizer.addListDrop(*args, **kwargs)

		return handle

	def addListFull(self, sizerLabel, *args, **kwargs):
		"""Overload for addListFull in handle_Sizer()."""

		mySizer = self.getSizer(sizerLabel)
		handle = mySizer.addListFull(*args, **kwargs)

		return handle

	def addSlider(self, sizerLabel, *args, **kwargs):
		"""Overload for addSlider in handle_Sizer()."""

		mySizer = self.getSizer(sizerLabel)
		handle = mySizer.addSlider(*args, **kwargs)

		return handle

	def addInputBox(self, sizerLabel, *args, **kwargs):
		"""Overload for addInputBox in handle_Sizer()."""

		mySizer = self.getSizer(sizerLabel)
		handle = mySizer.addInputBox(*args, **kwargs)

		return handle

	def addInputSearch(self, sizerLabel, *args, **kwargs):
		"""Overload for addInputSearch in handle_Sizer()."""

		mySizer = self.getSizer(sizerLabel)
		handle = mySizer.addInputSearch(*args, **kwargs)

		return handle

	def addInputSpinner(self, sizerLabel, *args, **kwargs):
		"""Overload for addInputSpinner in handle_Sizer()."""

		mySizer = self.getSizer(sizerLabel)
		handle = mySizer.addInputSpinner(*args, **kwargs)

		return handle

	def addButton(self, sizerLabel, *args, **kwargs):
		"""Overload for addButton in handle_Sizer()."""

		mySizer = self.getSizer(sizerLabel)
		handle = mySizer.addButton(*args, **kwargs)

		return handle

	def addButtonToggle(self, sizerLabel, *args, **kwargs):
		"""Overload for addButtonToggle in handle_Sizer()."""

		mySizer = self.getSizer(sizerLabel)
		handle = mySizer.addButtonToggle(*args, **kwargs)

		return handle

	def addButtonCheck(self, sizerLabel, *args, **kwargs):
		"""Overload for addButtonCheck in handle_Sizer()."""

		mySizer = self.getSizer(sizerLabel)
		handle = mySizer.addButtonCheck(*args, **kwargs)

		return handle

	def addCheckList(self, sizerLabel, *args, **kwargs):
		"""Overload for addCheckList in handle_Sizer()."""

		mySizer = self.getSizer(sizerLabel)
		handle = mySizer.addCheckList(*args, **kwargs)

		return handle

	def addButtonRadio(self, sizerLabel, *args, **kwargs):
		"""Overload for addButtonRadio in handle_Sizer()."""

		mySizer = self.getSizer(sizerLabel)
		handle = mySizer.addButtonRadio(*args, **kwargs)

		return handle

	def addButtonRadioBox(self, sizerLabel, *args, **kwargs):
		"""Overload for addButtonRadioBox in handle_Sizer()."""

		mySizer = self.getSizer(sizerLabel)
		handle = mySizer.addButtonRadioBox(*args, **kwargs)

		return handle

	def addButtonImage(self, sizerLabel, *args, **kwargs):
		"""Overload for addButtonImage in handle_Sizer()."""

		mySizer = self.getSizer(sizerLabel)
		handle = mySizer.addButtonImage(*args, **kwargs)

		return handle

	def addImage(self, sizerLabel, *args, **kwargs):
		"""Overload for addImage in handle_Sizer()."""

		mySizer = self.getSizer(sizerLabel)
		handle = mySizer.addImage(*args, **kwargs)

		return handle

	def addProgressBar(self, sizerLabel, *args, **kwargs):
		"""Overload for addProgressBar in handle_Sizer()."""

		mySizer = self.getSizer(sizerLabel)
		handle = mySizer.addProgressBar(*args, **kwargs)

		return handle

	def addPickerColor(self, sizerLabel, *args, **kwargs):
		"""Overload for addPickerColor in handle_Sizer()."""

		mySizer = self.getSizer(sizerLabel)
		handle = mySizer.addPickerColor(*args, **kwargs)

		return handle

	def addPickerFont(self, sizerLabel, *args, **kwargs):
		"""Overload for addPickerFont in handle_Sizer()."""

		mySizer = self.getSizer(sizerLabel)
		handle = mySizer.addPickerFont(*args, **kwargs)

		return handle

	def addPickerFile(self, sizerLabel, *args, **kwargs):
		"""Overload for addPickerFile in handle_Sizer()."""

		mySizer = self.getSizer(sizerLabel)
		handle = mySizer.addPickerFile(*args, **kwargs)

		return handle

	def addPickerFileWindow(self, sizerLabel, *args, **kwargs):
		"""Overload for addPickerFileWindow in handle_Sizer()."""

		mySizer = self.getSizer(sizerLabel)
		handle = mySizer.addPickerFileWindow(*args, **kwargs)

		return handle

	def addPickerTime(self, sizerLabel, *args, **kwargs):
		"""Overload for addPickerTime in handle_Sizer()."""

		mySizer = self.getSizer(sizerLabel)
		handle = mySizer.addPickerTime(*args, **kwargs)

		return handle

	def addPickerDate(self, sizerLabel, *args, **kwargs):
		"""Overload for addPickerDate in handle_Sizer()."""

		mySizer = self.getSizer(sizerLabel)
		handle = mySizer.addPickerDate(*args, **kwargs)

		return handle

	def addPickerDateWindow(self, sizerLabel, *args, **kwargs):
		"""Overload for addPickerDateWindow in handle_Sizer()."""

		mySizer = self.getSizer(sizerLabel)
		handle = mySizer.addPickerDateWindow(*args, **kwargs)

		return handle

	def addCanvas(self, sizerLabel, *args, **kwargs):
		"""Overload for addCanvas in handle_Sizer()."""

		mySizer = self.getSizer(sizerLabel)
		handle = mySizer.addCanvas(*args, **kwargs)

		return handle

	def appendRow(self, tableLabel, *args, **kwargs):
		"""Overload for appendRow in handle_WidgetTable()."""

		myTable = self.getTable(tableLabel)
		myTable.appendRow(*args, **kwargs)

	def appendColumn(self, tableLabel, *args, **kwargs):
		"""Overload for appendColumn in handle_WidgetTable()."""

		myTable = self.getTable(tableLabel)
		myTable.appendColumn(*args, **kwargs)

	def enableTableEditing(self, tableLabel, *args, **kwargs):
		"""Overload for enableTableEditing in handle_WidgetTable()."""

		myTable = self.getTable(tableLabel)
		myTable.enableTableEditing(*args, **kwargs)

	def disableTableEditing(self, tableLabel, *args, **kwargs):
		"""Overload for disableTableEditing in handle_WidgetTable()."""

		myTable = self.getTable(tableLabel)
		myTable.disableTableEditing(*args, **kwargs)

	def getTableReadOnly(self, tableLabel, *args, **kwargs):
		"""Overload for getTableReadOnly in handle_WidgetTable()."""

		myTable = self.getTable(tableLabel)
		answer = myTable.getTableReadOnly(*args, **kwargs)

		return answer

	def getTableCurrentCellReadOnly(selftableLabel, *args, **kwargs):
		"""Overload for getTableCurrentCellReadOnly in handle_WidgetTable()."""

		myTable = self.getTable(tableLabel)
		answer = myTable.getTableCurrentCellReadOnly(*args, **kwargs)

		return answer

	def clearTable(self, tableLabel, *args, **kwargs):
		"""Overload for clearTable in handle_WidgetTable()."""

		myTable = self.getTable(tableLabel)
		myTable.clearTable(*args, **kwargs)

	def setTableCursor(self, tableLabel, *args, **kwargs):
		"""Overload for setTableCursor in handle_WidgetTable()."""

		myTable = self.getTable(tableLabel)
		myTable.setTableCursor(*args, **kwargs)

	def setTableCell(self, tableLabel, *args, **kwargs):
		"""Overload for setTableCell in handle_WidgetTable()."""

		myTable = self.getTable(tableLabel)
		myTable.setTableCell(*args, **kwargs)

	def setTableCellList(self, tableLabel, *args, **kwargs):
		"""Overload for setTableCellList in handle_WidgetTable()."""

		myTable = self.getTable(tableLabel)
		myTable.setTableCellList(*args, **kwargs)

	def getTableCellValue(self, tableLabel, *args, **kwargs):
		"""Overload for getTableCellValue in handle_WidgetTable()."""

		myTable = self.getTable(tableLabel)
		answer = myTable.getTableCellValue(*args, **kwargs)

		return answer

	def getTableCurrentCell(self, tableLabel, *args, **kwargs):
		"""Overload for getTableCurrentCell in handle_WidgetTable()."""

		myTable = self.getTable(tableLabel)
		answer = myTable.getTableCurrentCell(*args, **kwargs)

		return answer

	def getTableCurrentCellValue(self, tableLabel, *args, **kwargs):
		"""Overload for getTableCurrentCellValue in handle_WidgetTable()."""

		myTable = self.getTable(tableLabel)
		answer = myTable.getTableCurrentCellValue(*args, **kwargs)

		return answer

	def getTableEventCell(self, tableLabel, *args, **kwargs):
		"""Overload for getTableEventCell in handle_WidgetTable()."""

		myTable = self.getTable(tableLabel)
		answer = myTable.getTableEventCell(*args, **kwargs)

		return answer

	def getTableEventCellValue(self, tableLabel, event, *args, **kwargs):
		"""Overload for getTableEventCellValue in handle_WidgetTable()."""

		myTable = self.getTable(tableLabel)
		answer = myTable.getTableEventCellValue(*args, **kwargs)

		return answer

	def setTableRowLabel(self, tableLabel, *args, **kwargs):
		"""Overload for setTableRowLabel in handle_WidgetTable()."""

		myTable = self.getTable(tableLabel)
		myTable.setTableRowLabel(*args, **kwargs)

	def setTableColumnLabel(self, tableLabel, *args, **kwargs):
		"""Overload for setTableColumnLabel in handle_WidgetTable()."""

		myTable = self.getTable(tableLabel)
		myTable.setTableColumnLabel(*args, **kwargs)

	def getTableColumnLabel(self, tableLabel, *args, **kwargs):
		"""Overload for getTableColumnLabel in handle_WidgetTable()."""

		myTable = self.getTable(tableLabel)
		answer = myTable.getTableColumnLabel(*args, **kwargs)

		return answer

	def setTableCellFormat(self, tableLabel, *args, **kwargs):
		"""Overload for setTableCellFormat in handle_WidgetTable()."""

		myTable = self.getTable(tableLabel)
		myTable.setTableCellFormat(*args, **kwargs)

	def setTableCellColor(self, tableLabel, *args, **kwargs):
		"""Overload for setTableCellColor in handle_WidgetTable()."""

		myTable = self.getTable(tableLabel)
		myTable.setTableCellColor(*args, **kwargs)

	def getTableCellColor(self, tableLabel, *args, **kwargs):
		"""Overload for getTableCellColor in handle_WidgetTable()."""

		myTable = self.getTable(tableLabel)
		answer = myTable.getTableCellColor(*args, **kwargs)

		return answer

	def setTableCellFont(self, tableLabel, *args, **kwargs):
		"""Overload for setTableCellFont in handle_WidgetTable()."""

		myTable = self.getTable(tableLabel)
		myTable.setTableCellFont(*args, **kwargs)

	def setTableMods(self, tableLabel, *args, **kwargs):
		"""Overload for setTableMods in handle_WidgetTable()."""

		myTable = self.getTable(tableLabel)
		myTable.setTableMods(*args, **kwargs)

	def hideTableRow(self, tableLabel, *args, **kwargs):
		"""Overload for hideTableRow in handle_WidgetTable()."""

		myTable = self.getTable(tableLabel)
		myTable.hideTableRow(*args, **kwargs)

	def hideTableColumn(self, tableLabel, *args, **kwargs):
		"""Overload for hideTableColumn in handle_WidgetTable()."""

		myTable = self.getTable(tableLabel)
		myTable.hideTableColumn(*args, **kwargs)

	def setTableTextColor(self, tableLabel, *args, **kwargs):
		"""Overload for setTableTextColor in handle_WidgetTable()."""

		myTable = self.getTable(tableLabel)
		myTable.setTableTextColor(*args, **kwargs)

	def setTableBackgroundColor(self, tableLabel, *args, **kwargs):
		"""Overload for setTableBackgroundColor in handle_WidgetTable()."""

		myTable = self.getTable(tableLabel)
		myTable.setTableBackgroundColor(*args, **kwargs)

	def autoTableSize(self, tableLabel, *args, **kwargs):
		"""Overload for autoTableSize in handle_WidgetTable()."""

		myTable = self.getTable(tableLabel)
		myTable.autoTableSize(*args, **kwargs)

	def autoTableSizeRow(self, tableLabel, *args, **kwargs):
		"""Overload for autoTableSizeRow in handle_WidgetTable()."""

		myTable = self.getTable(tableLabel)
		myTable.autoTableSizeRow(*args, **kwargs)

	def autoTableSizeColumn(self, tableLabel, *args, **kwargs):
		"""Overload for autoTableSizeColumn in handle_WidgetTable()."""

		myTable = self.getTable(tableLabel)
		myTable.autoTableSizeColumn(*args, **kwargs)

	def autoTableSizeRowLabel(self, tableLabel, *args, **kwargs):
		"""Overload for autoTableSizeRowLabel in handle_WidgetTable()."""

		myTable = self.getTable(tableLabel)
		myTable.autoTableSizeRowLabel(*args, **kwargs)

	def autoTableSizeColumnLabel(self, tableLabel, *args, **kwargs):
		"""Overload for autoTableSizeColumnLabel in handle_WidgetTable()."""

		myTable = self.getTable(tableLabel)
		myTable.autoTableSizeColumnLabel(*args, **kwargs)

	def setTableRowSize(self, tableLabel, *args, **kwargs):
		"""Overload for setTableRowSize in handle_WidgetTable()."""

		myTable = self.getTable(tableLabel)
		myTable.setTableRowSize(*args, **kwargs)

	def setTableColumnSize(self, tableLabel, *args, **kwargs):
		"""Overload for setTableColumnSize in handle_WidgetTable()."""

		myTable = self.getTable(tableLabel)
		myTable.setTableColumnSize(*args, **kwargs)

	def setTableRowSizeDefaults(self, tableLabel, *args, **kwargs):
		"""Overload for setTableRowSizeDefaults in handle_WidgetTable()."""

		myTable = self.getTable(tableLabel)
		myTable.setTableRowSizeDefaults(*args, **kwargs)

	def setTableColumnSizeDefaults(self, tableLabel, *args, **kwargs):
		"""Overload for setTableColumnSizeDefaults in handle_WidgetTable()."""

		myTable = self.getTable(tableLabel)
		myTable.setTableColumnSizeDefaults(*args, **kwargs)

	def setThickness(self, canvasLabel, *args, **kwargs):
		"""Overload for setThickness in handle_WidgetCanvas()."""

		myCanvas = self.getCanvas(canvasLabel)
		myCanvas.setThickness(*args, **kwargs)

	def setFill(self, canvasLabel, *args, **kwargs):
		"""Overload for setFill in handle_WidgetCanvas()."""

		myCanvas = self.getCanvas(canvasLabel)
		myCanvas.setFill(*args, **kwargs)

	def setColor(self, canvasLabel, *args, **kwargs):
		"""Overload for setColor in handle_WidgetCanvas()."""

		myCanvas = self.getCanvas(canvasLabel)
		myCanvas.setColor(*args, **kwargs)

	def drawUpdate(self, canvasLabel, *args, **kwargs):
		"""Overload for drawUpdate in handle_WidgetCanvas()."""

		myCanvas = self.getCanvas(canvasLabel)
		myCanvas.drawUpdate(*args, **kwargs)

	def drawNew(self, canvasLabel, *args, **kwargs):
		"""Overload for drawNew in handle_WidgetCanvas()."""

		myCanvas = self.getCanvas(canvasLabel)
		myCanvas.drawNew(*args, **kwargs)

	def drawSave(self, canvasLabel, *args, **kwargs):
		"""Overload for drawSave in handle_WidgetCanvas()."""

		myCanvas = self.getCanvas(canvasLabel)
		myCanvas.drawSave(*args, **kwargs)

	def drawZoom(self, canvasLabel, *args, **kwargs):
		"""Overload for drawZoom in handle_WidgetCanvas()."""

		myCanvas = self.getCanvas(canvasLabel)
		myCanvas.drawZoom(*args, **kwargs)

	def drawSetOrigin(self, canvasLabel, *args, **kwargs):
		"""Overload for drawSetOrigin in handle_WidgetCanvas()."""

		myCanvas = self.getCanvas(canvasLabel)
		myCanvas.drawSetOrigin(*args, **kwargs)
			
	def drawImage(self, canvasLabel, *args, **kwargs):
		"""Overload for drawImage in handle_WidgetCanvas()."""

		myCanvas = self.getCanvas(canvasLabel)
		myCanvas.drawImage(*args, **kwargs)

	def drawText(self, canvasLabel, *args, **kwargs):
		"""Overload for drawText in handle_WidgetCanvas()."""

		myCanvas = self.getCanvas(canvasLabel)
		myCanvas.drawText(*args, **kwargs)

	def drawPoint(self, canvasLabel, *args, **kwargs):
		"""Overload for drawPoint in handle_WidgetCanvas()."""

		myCanvas = self.getCanvas(canvasLabel)
		myCanvas.drawPoint(*args, **kwargs)

	def drawLine(self, canvasLabel, *args, **kwargs):
		"""Overload for drawLine in handle_WidgetCanvas()."""

		myCanvas = self.getCanvas(canvasLabel)
		myCanvas.drawLine(*args, **kwargs)

	def drawSpline(self, canvasLabel, *args, **kwargs):
		"""Overload for drawSpline in handle_WidgetCanvas()."""

		myCanvas = self.getCanvas(canvasLabel)
		myCanvas.drawSpline(*args, **kwargs)

	def drawArc(self, canvasLabel, *args, **kwargs):
		"""Overload for drawArc in handle_WidgetCanvas()."""

		myCanvas = self.getCanvas(canvasLabel)
		myCanvas.drawArc(*args, **kwargs)

	def drawCheckMark(self, canvasLabel, *args, **kwargs):
		"""Overload for drawCheckMark in handle_WidgetCanvas()."""

		myCanvas = self.getCanvas(canvasLabel)
		myCanvas.drawCheckMark(*args, **kwargs)

	def drawRectangle(self, canvasLabel, *args, **kwargs):
		"""Overload for drawRectangle in handle_WidgetCanvas()."""

		myCanvas = self.getCanvas(canvasLabel)
		myCanvas.drawRectangle(*args, **kwargs)

	def drawPolygon(self, canvasLabel, *args, **kwargs):
		"""Overload for drawPolygon in handle_WidgetCanvas()."""

		myCanvas = self.getCanvas(canvasLabel)
		myCanvas.drawPolygon(*args, **kwargs)

	def drawCircle(self, canvasLabel, *args, **kwargs):
		"""Overload for drawCircle in handle_WidgetCanvas()."""

		myCanvas = self.getCanvas(canvasLabel)
		myCanvas.drawCircle(*args, **kwargs)

	def drawEllipse(self, canvasLabel, *args, **kwargs):
		"""Overload for drawEllipse in handle_WidgetCanvas()."""

		myCanvas = self.getCanvas(canvasLabel)
		myCanvas.drawEllipse(*args, **kwargs)

class handle_Panel(handle_Container_Base):
	"""A handle for working with a wxPanel."""

	def __init__(self):
		"""Initializes defaults."""

		#Initialize inherited classes
		handle_Container_Base.__init__(self)

	def __str__(self):
		"""Gives diagnostic information on the Panel when it is printed out."""

		output = handle_Container_Base.__str__(self)
		return output

	def build(self, argument_catalogue):
		#Fill in default values
		for item in inspect.signature(handle_Window.addPanel).parameters.values():
			if (item.name not in argument_catalogue):
				argument_catalogue[item.name] = item.default

		#Prebuild
		handle_Container_Base.preBuild(self, argument_catalogue)

		#Unpack arguments
		buildSelf = self.getArguments(argument_catalogue, "self")

		#Error Check
		if (self.parent.thing == None):
			errorMessage = "The object {} must be fully created for {}".format(self.parent.__repr__(), self.__repr__())
			raise RuntimeError(errorMessage)

		#Add first panel
		if (isinstance(buildSelf, handle_Window)):
			panelList = buildSelf.getNested(include = handle_Panel)
			if (len(panelList) <= 1):
				#The first panel added to a window is automatically nested
				self.nested = True

		#Determine border
		border = self.getArguments(argument_catalogue, "border")
		if (type(border) == str):

			#Ensure correct caseing
			border = border.lower()

			if (border[0:2] == "si"):
				border = "wx.SIMPLE_BORDER"

			elif (border[0] == "r"):
				border = "wx.RAISED_BORDER"

			elif (border[0:2] == "su"):
				border = "wx.SUNKEN_BORDER"

			elif (border[0] == "n"):
				border = "wx.NO_BORDER"

			else:
				errorMessage = "border {} does not exist".format(border)
				raise NameError(errorMessage)
		else:
			border = "wx.NO_BORDER"

		#Get Attributes
		flags = self.getArguments(argument_catalogue, "flags")
		flags = self.getItemMod(flags, False, None)[0]

		tabTraversal = self.getArguments(argument_catalogue, "tabTraversal")
		if (tabTraversal):
			flags += "|wx.TAB_TRAVERSAL"

		#Create the panel
		self.thing = wx.Panel(self.parent.thing, style = eval(border + "|" + flags))

		autoSize = self.getArguments(argument_catalogue, "autoSize")
		self.autoSize = autoSize

		#Bind Functions
		initFunction = self.getArguments(argument_catalogue, "initFunction")
		if (initFunction != None):
			self.betterBind(wx.EVT_INIT_DIALOG, self.thing, initFunction, initFunctionArgs, initFunctionKwargs)

		#Update catalogue
		for key, value in locals().items():
			if (key != "self"):
				argument_catalogue[key] = value

		#Postbuild
		handle_Container_Base.postBuild(self, argument_catalogue)

	#Etc
	def nest(self, handle = None):
		"""Nests an object inside of this Panel.

		handle (handle) - What to place in this object
			- Widgets should be passed in as a dictionary

		Example Input: nest(text)
		"""

		#Do not nest already nested objects
		if (isinstance(handle, dict)):
			if ("nested" in handle):
				nested = handle["nested"]
			else:
				nested = False
		else:
			nested = handle.nested

		if (nested):
			errorMessage = "Cannot nest objects twice"
			raise SyntaxError(errorMessage)

		#Perform Nesting
		if (isinstance(handle, handle_Sizer)):
			self.thing.SetSizer(handle.thing)

		else:
			warnings.warn("Add {} to nest() for {}".format(handle.__class__, self.__repr__()), Warning, stacklevel = 2)
			return

		handle.nested = True
		handle.nestingAddress = self.nestingAddress + [id(self)]
		self.setAddressValue(handle.nestingAddress + [id(handle)], {None: handle})

class handle_Splitter(handle_Container_Base):
	"""A handle for working with a wxSplitter."""

	def __init__(self):
		"""Initializes defaults."""

		#Initialize inherited classes
		handle_Container_Base.__init__(self)

		self.sizerList = []
		self.panelList = []

	def __str__(self):
		"""Gives diagnostic information on the Splitter when it is printed out."""

		output = handle_Container_Base.__str__(self)
		return output

	def postBuild(self, argument_catalogue):
		"""Runs before this object is built."""

		handle_Container_Base.postBuild(self, argument_catalogue)

		#Unpack arguments
		buildSelf = argument_catalogue["self"]

		#Nest splitter
		buildSelf.nest(self)

	def getSizers(self):
		"""Returns the internal sizer list."""

		return self.sizerList

	def readBuildInstructions_sizer(self, parent, i, instructions):
		"""Interprets instructions given by the user for what sizer to make and how to make it."""

		if (not isinstance(instructions, dict)):
			errorMessage = "sizer_{} must be a dictionary for {}".format(i, self.__repr__())
			raise ValueError(errorMessage)

		if (len(instructions) == 1):
			instructions["type"] = "Box"
		else:
			if ("type" not in instructions):
				errorMessage = "Must supply which sizer type to make. The key should be 'type'. The value should be 'Grid', 'Flex', 'Bag', 'Box', 'Text', or 'Wrap'"
				raise ValueError(errorMessage)

		sizerType = instructions["type"].lower()
		if (sizerType not in ["grid", "flex", "bag", "box", "text", "wrap"]):
			errorMessage = "There is no 'type' {}. The value should be be 'Grid', 'Flex', 'Bag', 'Box', 'Text', or 'Wrap'".format(instructions["type"])
			raise KeyError(errorMessage)

		#Get Default build arguments
		if (sizerType == "grid"):
			sizerFunction = handle_Window.addSizerGrid
		elif (sizerType == "flex"):
			sizerFunction = handle_Window.addSizerGridFlex
		elif (sizerType == "bag"):
			sizerFunction = handle_Window.addSizerGridBag
		elif (sizerType == "box"):
			sizerFunction = handle_Window.addSizerBox
		elif (sizerType == "text"):
			sizerFunction = handle_Window.addSizerText
		else:
			sizerFunction = handle_Window.addSizerWrap
		kwargs = {item.name: item.default for item in inspect.signature(sizerFunction).parameters.values()}

		#Create Handler
		sizer = handle_Sizer()
		sizer.type = instructions["type"]
		del instructions["type"]

		#Overwrite default with user given data
		for key, value in instructions.items():
			kwargs[key] = value

		#Finish building sizer
		kwargs["self"] = parent
		sizer.build(kwargs)

		return sizer

	def readBuildInstructions_panel(self, parent, i, instructions):
		"""Interprets instructions given by the user for what panel to make and how to make it."""

		if (not isinstance(instructions, dict)):
			errorMessage = "panel_{} must be a dictionary for {}".format(i, self.__repr__())
			raise ValueError(errorMessage)

		#Overwrite default with user given data
		kwargs = {item.name: item.default for item in inspect.signature(handle_Window.addPanel).parameters.values()}
		for key, value in instructions.items():
			kwargs[key] = value

		#Create Handler
		panel = handle_Panel()

		#Finish building panel
		kwargs["self"] = parent
		panel.build(kwargs)

		return panel

class handle_Notebook(handle_Container_Base):
	"""A handle for working with a wxNotebook."""

	def __init__(self):
		"""Initializes defaults."""

		#Initialize inherited classes
		handle_Container_Base.__init__(self)

		#Internal Variables
		self.notebookImageList = wx.ImageList(16, 16) #A wxImageList containing all tab images associated with this notebook

	def __str__(self):
		"""Gives diagnostic information on the Notebook when it is printed out."""

		output = handle_Container_Base.__str__(self)
		return output

	def addPage(self, text = None, label = None, parent = None, panel = {}, sizer = {},
		insert = None, default = False, icon_path = None, icon_internal = False):
		"""Adds a gage to the notebook.
		Lists can be given to add multiple pages. They are added in order from left to right.
		If only a 'pageLabel' is a list, they will all have the same 'text'.
		If 'pageLabel' and 'text' are a list of different lengths, it will not add any of them.

		text (str)          - What the page's tab will say
			- If None: The tab will be blank
		label (str)       - What this is called in the idCatalogue
		
		insert (int)   - Determines where the new page will be added
			- If None or -1: The page will be added to the end
			- If not None or -1: This is the page index to place this page in 
		default (bool)  - Determines if the new page should be automatically selected

		icon_path (str)      - Determiens if there should be an icon to the left of the text
		icon_internal (bool) - Determiens if 'image_path' refers to an internal image

		Example Input: addPage()
		Example Input: addPage("page_1")
		Example Input: addPage(0, "Lorem")
		Example Input: addPage([0, 1], "Lorem")
		Example Input: addPage([0, 1], ["Lorem", "Ipsum"])
		Example Input: addPage(0, "Lorem", insert = 2)
		Example Input: addPage(0, "Lorem", default = True)
		"""

		#Error Check
		if ((isinstance(label, list) or isinstance(label, tuple)) and (isinstance(text, list) or isinstance(text, tuple))):
			if (len(label) != len(text)):
				errorMessage = "'label' and 'text' must be the same length for {}".format(self.__repr__())
				raise ValueError(errorMessage)

		#Account for multiple objects
		if ((not isinstance(label, list)) and (not isinstance(label, tuple))):
			labelList = [label]
		else:
			labelList = label

		if ((not isinstance(text, list)) and (not isinstance(text, tuple))):
			textList = [text]
		else:
			textList = text

		if (len(labelList) == 0):
			return None

		#Add pages
		handleList = []
		for i, label in enumerate(labelList):
			#Format text
			if (len(textList) != 1):
				text = textList[i]
			else:
				text = textList[0]

			#Get the object
			handle = handle_NotebookPage()
			handleList.append(handle)
			kwargs = locals()
			kwargs["parent"] = self
			handle.preBuild(kwargs)
			handle.build(kwargs)
			handle.postBuild(kwargs)

			#Determine if there is an icon on the tab
			if (handle.icon != None):
				#Add this icon to the notebook's image catalogue
				handle.iconIndex = self.thing.notebookImageList.Add(handle.icon)
				self.thing.AssignImageList(self.thing.notebookImageList)

			#Create the tab
			if ((insert != None) and (insert != -1)):
				if (handle.iconIndex != None):
					self.thing.InsertPage(insert, handle.myPanel.thing, handle.text, default, handle.iconIndex)
				else:
					self.thing.InsertPage(insert, handle.myPanel.thing, handle.text, default)

			else:
				if (handle.iconIndex != None):
					self.thing.AddPage(handle.myPanel.thing, handle.text, default, handle.iconIndex)
				else:
					self.thing.AddPage(handle.myPanel.thing, handle.text, default)

			#Record nesting
			handle.nested = True
			handle.myPanel.nested = True

		if (len(handleList) > 1):
			return handleList
		else:
			return handleList[0]

	def changePage(self, pageLabel, triggerEvent = True):
		"""Changes the page selection on the notebook from the current page to the given page.

		pageLabel (str)     - The catalogue label for the panel to add to the notebook
		triggerEvent (bool) - Determiens if a page change and page changing event is triggered
			- If True: The page change events are triggered
			- If False: the page change events are not triggered

		Example Input: notebookChangePage(1)
		Example Input: notebookChangePage(1, False)
		"""

		#Determine page number
		pageNumber = self.notebookGetPageIndex(notebookLabel, pageLabel)

		#Change the page
		if (triggerEvent):
			notebook.SetSelection(pageNumber)
		else:
			notebook.ChangeSelection(pageNumber)

	def removePage(self, pageLabel):
		"""Removes the given page from the notebook.

		pageLabel (str)     - The catalogue label for the panel to add to the notebook

		Example Input: notebookRemovePage(1)
		"""

		#Determine page number
		pageNumber = self.notebookGetPageIndex(notebookLabel, pageLabel)

		#Remove the page from the notebook
		notebook.RemovePage(pageNumber)

		#Remove the page from the catalogue
		del notebook.notebookPageDict[pageLabel]

	def removeAll(self):
		"""Removes all pages from the notebook.

		Example Input: notebookRemovePage()
		"""

		#Remove all pages from the notebook
		notebook.DeleteAllPages()

		#Remove all pages from the catalogue
		notebook.notebookPageDict = {}

	def nextPage(self):
		"""Selects the next page in the notebook.

		Example Input: notebookNextPage()
		"""

		#Change the page
		notebook.AdvanceSelection()

	def backPage(self):
		"""Selects the previous page in the notebook.

		Example Input: notebookBackPage()
		"""

		#Change the page
		notebook.AdvanceSelection(False)

	##Getters
	def getCurrentPage(self, index = False):
		"""Returns the currently selected page from the given notebook

		index (bool)        - Determines in what form the page is returned.
			- If True: Returns the page's index number
			- If False: Returns the page's catalogue label
			- If None: Returns the wxPanel object associated with the page

		Example Input: notebookGetCurrentPage()
		Example Input: notebookGetCurrentPage(True)
		"""

		#Determine current page
		currentPage = notebook.GetSelection()

		if (currentPage != wx.NOT_FOUND):
			if (not index):
				currentPage = self.notebookGetPageLabel(notebookLabel, currentPage)
		else:
			currentPage = None

		return currentPage

	def getPageIndex(self, pageLabel):
		"""Returns the page index for a page with the given label in the given notebook.

		pageLabel (str)     - The catalogue label for the panel to add to the notebook

		Example Input: notebookGetPageIndex(0)
		"""

		#Determine page number
		pageNumber = notebook.notebookPageDict[pageLabel]["index"]

		return pageNumber

	def getPageText(self, pageIndex):
		"""Returns the first page index for a page with the given label in the given notebook.

		pageLabel (str)     - The catalogue label for the panel to add to the notebook

		Example Input: notebookGetPageLabel(1)
		"""

		#Determine page number
		pageNumber = self.notebookGetPageIndex(notebookLabel, pageLabel)

		#Get the tab's text
		text = notebook.GetPageText(pageNumber)

		return text

	def getTabCount(self):
		"""Returns how many tabs the notebook currently has.

		Example Input: notebookGetTabCount()
		"""

		#Determine the number of tabs
		tabCount = notebook.GetPageCount()

		return tabCount

	def getTabRowCount(self):
		"""Returns how many rows of tabs the notebook currently has.

		Example Input: notebookGetTabRowCount()
		"""

		#Determine the number of tabs
		count = notebook.GetRowCount()

		return count

	##Setters
	def setPageText(self, pageLabel, text = ""):
		"""Changes the given notebook page's tab text.

		pageLabel (str)     - The catalogue label for the panel to add to the notebook
		text (str)          - What the page's tab will now say

		Example Input: notebookSetPageText(0, "Ipsum")
		"""

		#Determine page number
		pageNumber = self.notebookGetPageIndex(notebookLabel, pageLabel)

		#Change page text
		notebook.SetPageText(pageNumber, text)

class handle_NotebookPage(handle_Sizer):#, handle_Container_Base):
	"""A handle for working with a wxNotebook."""

	def __init__(self):
		"""Initializes defaults."""

		#Initialize inherited classes
		# handle_Container_Base.__init__(self)
		handle_Sizer.__init__(self)

		self.thing = None
		self.myPanel = None
		self.mySizer = None
		self.text = None
		self.icon = None
		self.iconIndex = None

	def __str__(self):
		"""Gives diagnostic information on the Notebook when it is printed out."""

		output = handle_Container_Base.__str__(self)
		return output

	def __enter__(self):
		"""Allows the user to use a with statement to build the GUI."""

		handle = self.mySizer.__enter__()

		return handle

	def __exit__(self, exc_type, exc_value, traceback):
		"""Allows the user to use a with statement to build the GUI."""
		
		state = self.mySizer.__exit__(exc_type, exc_value, traceback)
		return state

	def __iter__(self):
		"""Returns an iterator object that provides the nested objects."""
		
		iterator = self.mySizer.__iter__()
		return iterator

	def __getitem__(self, key):
		"""Allows the user to index the handle to get nested elements with labels."""

		return self.mySizer.__getitem__(key)

	def __setitem__(self, key, value):
		"""Allows the user to index the handle to get nested elements with labels."""

		self.mySizer.__setitem__(key, value)

	def __delitem__(self, key):
		"""Allows the user to index the handle to get nested elements with labels."""

		self.mySizer.__delitem__(key)

	def build(self, argument_catalogue):
		"""Adds a gage to the notebook.
		Lists can be given to add multiple pages. They are added in order from left to right.
		If only a 'pageLabel' is a list, they will all have the same 'text'.
		If 'pageLabel' and 'text' are a list of different lengths, it will not add any of them.

		pageLabel (str)     - The catalogue label for the panel to add to the notebook
		text (str)          - What the page's tab will say
			- If None: The tab will be blank
		label (str)       - What this is called in the idCatalogue

		icon_path (str)      - Determiens if there should be an icon to the left of the text
		icon_internal (bool) - Determiens if 'image_path' refers to an internal image

		Example Input: build(0)
		Example Input: build("page_1")
		Example Input: build(0, "Lorem")
		Example Input: build([0, 1], "Lorem")
		Example Input: build([0, 1], ["Lorem", "Ipsum"])
		Example Input: build(0, "Lorem", insert = 2)
		Example Input: build(0, "Lorem", select = True)
		"""

		text, panel, sizer, icon_path, icon_internal = self.getArguments(argument_catalogue, ["text", "panel", "sizer", "icon_path", "icon_internal"])

		self.myWindow = self.parent.myWindow

		#Setup Panel
		panel["parent"] = self.parent
		self.myPanel = self.readBuildInstructions_panel(self, panel)

		#Setup Sizer
		sizer["parent"] = self.myPanel
		self.mySizer = self.readBuildInstructions_sizer(self, sizer)

		self.myPanel.nest(self.mySizer)

		#Format text
		if (text == None):
			self.text = ""
		else:
			if (not isinstance(text, str)):
				self.text = "{}".format(text)
			else:
				self.text = text

		#Format Icon
		if (icon_path != None):
			self.icon = self.getImage(icon_path, icon_internal)
		else:
			self.icon = None
			self.iconIndex = None

	def getSizer(self):
		return self.mySizer

	def remove(self):
		"""Removes the given page from the notebook.

		Example Input: notebookRemovePage()
		"""

		#Determine page number
		pageNumber = self.notebookGetPageIndex(notebookLabel, pageLabel)

		#Remove the page from the notebook
		notebook.RemovePage(self.pageNumber)

		#Remove the page from the catalogue
		del notebook.notebookPageDict[pageLabel]

	def getIndex(self, event = None):
		"""Returns the page index for a page with the given label in the given notebook.

		Example Input: notebookGetPageIndex()
		"""

		#Determine page number
		pageNumber = notebook.notebookPageDict[pageLabel]["index"]

		return pageNumber

	def getValue(self, event = None):
		"""Returns the first page index for a page with the given label in the given notebook.

		Example Input: notebookGetPageLabel()
		"""

		#Determine page number
		pageNumber = self.notebookGetPageIndex(notebookLabel, pageLabel)

		#Get the tab's text
		text = notebook.GetPageText(pageNumber)

		return text

	##Setters
	def setValue(self, text = "", event = None):
		"""Changes the given notebook page's tab text.

		text (str)          - What the page's tab will now say

		Example Input: notebookSetPageText("Ipsum")
		"""

		#Determine page number
		pageNumber = self.notebookGetPageIndex(notebookLabel, pageLabel)

		#Change page text
		notebook.SetPageText(pageNumber, text)

	#Etc
	def readBuildInstructions_sizer(self, parent, instructions):
		"""Interprets instructions given by the user for what sizer to make and how to make it."""

		if (not isinstance(instructions, dict)):
			errorMessage = "sizer must be a dictionary for {}".format(self.__repr__())
			raise ValueError(errorMessage)

		if (len(instructions) == 1):
			instructions["type"] = "Box"
		else:
			if ("type" not in instructions):
				errorMessage = "Must supply which sizer type to make. The key should be 'type'. The value should be 'Grid', 'Flex', 'Bag', 'Box', 'Text', or 'Wrap'"
				raise ValueError(errorMessage)

		sizerType = instructions["type"].lower()
		if (sizerType not in ["grid", "flex", "bag", "box", "text", "wrap"]):
			errorMessage = "There is no 'type' {}. The value should be be 'Grid', 'Flex', 'Bag', 'Box', 'Text', or 'Wrap'".format(instructions["type"])
			raise KeyError(errorMessage)

		#Get Default build arguments
		if (sizerType == "grid"):
			sizerFunction = handle_Window.addSizerGrid
		elif (sizerType == "flex"):
			sizerFunction = handle_Window.addSizerGridFlex
		elif (sizerType == "bag"):
			sizerFunction = handle_Window.addSizerGridBag
		elif (sizerType == "box"):
			sizerFunction = handle_Window.addSizerBox
		elif (sizerType == "text"):
			sizerFunction = handle_Window.addSizerText
		else:
			sizerFunction = handle_Window.addSizerWrap
		kwargs = {item.name: item.default for item in inspect.signature(sizerFunction).parameters.values()}

		#Create Handler
		sizer = handle_Sizer()
		sizer.type = instructions["type"]
		del instructions["type"]

		#Overwrite default with user given data
		for key, value in instructions.items():
			kwargs[key] = value

		#Finish building sizer
		kwargs["self"] = parent
		sizer.build(kwargs)

		return sizer

	def readBuildInstructions_panel(self, parent, instructions):
		"""Interprets instructions given by the user for what panel to make and how to make it."""

		if (not isinstance(instructions, dict)):
			errorMessage = "panel must be a dictionary for {}".format(self.__repr__())
			raise ValueError(errorMessage)

		#Overwrite default with user given data
		kwargs = {item.name: item.default for item in inspect.signature(handle_Window.addPanel).parameters.values()}
		for key, value in instructions.items():
			kwargs[key] = value

		#Create Handler
		panel = handle_Panel()

		#Finish building panel
		kwargs["self"] = parent
		panel.build(kwargs)

		return panel

#Classes
class MyApp(wx.App):
	"""Needed to make the GUI work."""

	def __init__(self, redirect=False, filename=None, useBestVisual=False, clearSigInt=True, parent = None):
		"""Needed to make the GUI work."""

		self.parent = parent
		wx.App.__init__(self, redirect=redirect, filename = filename, useBestVisual = useBestVisual, clearSigInt = clearSigInt)

	def OnInit(self):
		"""Needed to make the GUI work.
		Single instance code modified from: https://wxpython.org/Phoenix/docs/html/wx.SingleInstanceChecker.html
		"""

		#Account for multiple instances of the same app
		if (self.parent != None):
			if (self.parent.oneInstance):
				#Ensure only one instance per user runs
				self.parent.oneInstance_name = "SingleApp-{}".format(wx.GetUserId())
				self.parent.oneInstance_instance = wx.SingleInstanceChecker(self.parent.oneInstance_name)

				if self.parent.oneInstance_instance.IsAnotherRunning():
					wx.MessageBox("Cannot run multiple instances of this program", "Runtime Error")
					return False

		#Allow the app to progress
		return True

class Communication():
	"""Helps the GUI to communicate with other devices.

	CURRENTLY SUPPORTED METHODS
		- COM Port
		- Ethernet & Wi-fi
		- Barcode

	UPCOMING SUPPORTED METHODS
		- Raspberry Pi GPIO
		- QR Code

	Example Input: Meant to be inherited by GUI()
	"""

	def __init__(self):
		"""Initialized internal variables."""

		self.comDict    = {} #A dictionary that contains all of the created COM ports
		self.socketDict = {} #A dictionary that contains all of the created socket connections

	#Barcodes
	def getBarcodeTypes(self):
		"""Convenience Function"""

		return self.Barcodes.getTypes(self)

	def createBarcode(self, codeType, text, fileName = None, saveFormat = None, dpi = 300):
		"""Convenience Function"""

		return self.Barcodes.create(self, codeType, text, fileName = fileName, saveFormat = saveFormat, dpi = dpi)

	def readBarcode(self):
		"""Convenience Function"""

		return Barcodes.read(self)

	#COM port
	def getComPorts(self):
		"""Returns a list of available ports.
		Code from Matt Williams on http://stackoverflow.com/questions/1205383/listing-serial-com-ports-on-windows.

		Example Input: getAllComPorts()
		"""

		ports = [item.device for item in serial.tools.list_ports.comports()]

		return ports

	def makeComPort(self, which):
		"""Creates a new COM Port object.

		Example Input: makeComPort(0)
		"""

		#Create COM object
		comPort = self.ComPort()

		#Catalogue the COM port
		self.comDict[which] = comPort

		return comPort

	def getComPort(self, which):
		"""Returns the requested COM object.

		Example Input: getComPort(0)
		"""

		if (which in self.comDict):
			return self.comDict[which]
		else:
			print("ERROR: There is no COM port object {}".format(which))
			return None

	#Ethernet
	def makeSocket(self, which):
		"""Creates a new Ethernet object.

		Example Input: makeSocket(0)
		"""

		#Create Ethernet object
		mySocket = self.Ethernet(self)

		#Catalogue the COM port
		self.socketDict[which] = mySocket

		return mySocket

	def getSocket(self, which):
		"""Returns the requested Ethernet object.

		Example Input: getComPort(0)
		"""

		if (which in self.socketDict):
			return self.socketDict[which]
		else:
			print("ERROR: There is no Ethernet object {}".format(which))
			return None

	class Ethernet():
		"""A controller for a single ethernet socket.

		Note: If you create a socket in a background function, 
		do not try to read or write to your GUI until you create and open the socket.
		If you do not, the GUI will freeze up.
		"""

		def __init__(self, parent):
			"""Defines the internal variables needed to run."""

			#Create internal variables
			self.parent = parent #The GUI object

			#Background thread variables
			self.dataBlock   = [] #Used to recieve data from the socket
			self.ipScanBlock = [] #Used to store active ip addresses from an ip scan
			self.clientDict  = {} #Used to keep track of all client connections [connection object, client dataBlock, stop recieve flag, recieved all flag]

			self.recieveStop = False #Used to stop the recieving function early
			self.ipScanStop  = False #Used to stop the ip scanning function early

			#Create the socket
			self.mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		def open(self, address, port = 9100, error = False, pingCheck = False):
			"""Opens the socket connection.

			address (str) - The ip address/website you are connecting to
			port (int)    - The socket port that is being used
			error (bool)  - Determines what happens if an error occurs
				If True: If there is an error, returns an error indicator. Otherwise, returns a 0
				If False: Raises an error exception
			pingCheck (bool) - Determines if it will ping an ip address before connecting to it to confirm it exists

			Example Input: open("www.example.com")
			"""

			#Account for the socket having been closed
			if (self.mySocket == None):
				self.mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

			#Remove any white space
			address = re.sub(" ", "", address)

			#Make sure it exists
			if (pingCheck):
				addressExists = self.ping(address)

				if (not addressExists):
					print("Cannot ping address {}".format(address))
					return False

			#Connect to the socket
			if (error):
				error = self.mySocket.connect_ex((address, port))
				return error
			else:
				self.mySocket.connect((address, port))

			#Finish
			if (pingCheck):
				return True

		def close(self, now = False):
			"""Closes the socket connection.

			now (bool) - Determines how the socket is closed
				If True: Releases the resource associated with a connection 
					and closes the connection immediately
				 If False: Releases the resource associated with a connection 
					but does not necessarily close the connection immediately
				 If None: Closes the socket without closing the underlying file descriptor

			Example Input: close()
			Example Input: close(True)
			Example Input: close(None)
			"""

			if (now != None):
				if (now):
					self.restrict()

				self.mySocket.close()
			else:
				self.mySocket.detach()

			self.mySocket = None

		def send(self, data):
			"""Sends data across the socket connection.

			data (str) - What will be sent

			Example Input: send("lorem")
			Example Input: send(1234)
			"""

			#Account for numbers, lists, etc.
			if ((type(data) != str) and (type(data) != bytes)):
				data = str(data)

			#Make sure that the data is a byte string
			if (type(data) != bytes):
				data = data.encode() #The .encode() is needed for python 3.4, but not for python 2.7

			#Send the data
			self.mySocket.sendall(data)
			# self.mySocket.send(data)

		def startRecieve(self, bufferSize = 256):
			"""Retrieves data from the socket connection.
			Because this can take some time, it saves the list of ip addresses as an internal variable.
			Special thanks to A. Polino and david.gaarenstroom on http://code.activestate.com/recipes/577514-chek-if-a-number-is-a-power-of-two/

			bufferSize (int) - The size of the recieveing buffer. Should be a power of 2

			Example Input: startRecieve()
			Example Input: startRecieve(512)
			Example Input: startRecieve(4096)
			"""

			def runFunction(self, bufferSize):
				"""Needed to listen on a separate thread so the GUI is not tied up."""

				#Listen
				while True:
					#Check for stop command
					if (self.recieveStop):
						self.recieveStop = False
						break

					#Retrieve the block of data
					data = self.mySocket.recv(bufferSize).decode() #The .decode is needed for python 3.4, but not for python 2.7

					#Check for end of data stream
					if (len(data) < 1):
						#Stop listening
						break

					#Save the data
					self.dataBlock.append(data)

				#Mark end of message
				self.dataBlock.append(None)

			#Checks buffer size
			if (not (((bufferSize & (bufferSize - 1)) == 0) and (bufferSize > 0))):
				print("ERROR: Buffer size must be a power of 2, not {}".format(bufferSize))
				return None

			#Listen for data on a separate thread
			self.dataBlock = []
			self.parent.backgroundRun(runFunction, [self, bufferSize])

		def checkRecieve(self):
			"""Checks what the recieveing data looks like.
			Each read portion is an element in a list.
			Returns the current block of data and whether it is finished listening or not.

			Example Input: checkRecieve()
			"""

			#The entire message has been read once the last element is None.
			finished = False
			if (len(self.dataBlock) != 0):
				if (self.dataBlock[-1] == None):
					finished = True
					self.dataBlock.pop(-1) #Remove the None from the end so the user does not get confused

			return self.dataBlock, finished

		def stopRecieve(self):
			"""Stops listening for data from the socket.
			Note: The data is still in the buffer. You can resume listening by starting startRecieve() again.
			To flush it, close the socket and then open it again.

			Example Input: stopRecieve()
			"""

			self.recieveStop = True

		#Server Side
		def startServer(self, port = 10000, clients = 1):
			"""Starts a server that connects to clients.
			Modified code from Doug Hellmann on: https://pymotw.com/2/socket/tcp.html

			port (int)    - The port number to listen on
			clients (int) - The number of clients to listen for

			Example Input: startServer()
			Example Input: startServer(80)
			Example Input: startServer(clients = 5)
			"""

			def runFunction(self, port, clients):
				"""Needed to listen on a separate thread so the GUI is not tied up."""

				#Bind the socket to the port
				serverIp = ('', port)
				self.mySocket.bind(serverIp)

				#Listen for incoming connections
				self.mySocket.listen(clients)
				count = clients #How many clients still need to connect
				while True:
					# Wait for a connection
					try:
						connection, clientIp = self.mySocket.accept()
					except:
						count = self.closeClient(clientIp[0], count)

						#Check for all clients having connected and left
						if (count <= 0):
							break

					#Catalogue client
					if (clientIp not in self.clientDict):
						self.clientDict[clientIp] = [connection, "", False, False]

			#Listen for data on a separate thread
			self.parent.backgroundRun(runFunction, [self, port, clients])

		def clientSend(self, clientIp, data):
			"""Sends data across the socket connection to a client.

			clientIp (str) - The IP address of the client
			data (str)     - What will be sent

			Example Input: clientSend("169.254.231.0", "lorem")
			Example Input: clientSend("169.254.231.0", 1234)
			"""

			#Account for numbers, lists, etc.
			if ((type(data) != str) and (type(data) != bytes)):
				data = str(data)

			#Make sure that the data is a byte string
			if (type(data) != bytes):
				data = data.encode() #The .encode() is needed for python 3.4, but not for python 2.7

			#Send the data
			client = self.clientDict[clientIp][0]
			client.sendall(data)

		def clientStartRecieve(self, clientIp, bufferSize = 256):
			"""Retrieves data from the socket connection.
			Because this can take some time, it saves the list of ip addresses as an internal variable.
			Special thanks to A. Polino and david.gaarenstroom on http://code.activestate.com/recipes/577514-chek-if-a-number-is-a-power-of-two/

			clientIp (str)   - The IP address of the client
			bufferSize (int) - The size of the recieveing buffer. Should be a power of 2

			Example Input: clientStartRecieve("169.254.231.0")
			Example Input: clientStartRecieve("169.254.231.0", 512)
			"""

			def runFunction(self, clientIp, bufferSize):
				"""Needed to listen on a separate thread so the GUI is not tied up."""

				#Reset client dataBlock
				self.clientDict[clientIp][1] = ""

				#Listen
				client = self.clientDict[clientIp][0]
				while True:
					#Check for stop command
					if (self.clientDict[clientIp][2]):
						self.clientDict[clientIp][2] = False
						break

					#Retrieve the block of data
					data = client.recv(bufferSize).decode() #The .decode is needed for python 3.4, but not for python 2.7

					#Save the data
					self.clientDict[clientIp][1] += data

					#Check for end of data stream
					if (len(data) < bufferSize):
						#Stop listening
						break

				#Mark end of message
				self.clientDict[clientIp][3] = True

			#Checks buffer size
			if (not (((bufferSize & (bufferSize - 1)) == 0) and (bufferSize > 0))):
				print("ERROR: Buffer size must be a power of 2, not {}".format(bufferSize))
				return None

			#Listen for data on a separate thread
			self.dataBlock = []
			self.parent.backgroundRun(runFunction, [self, clientIp, bufferSize])

		def clientCheckRecieve(self, clientIp):
			"""Checks what the recieveing data looks like.
			Each read portion is an element in a list.
			Returns the current block of data and whether it is finished listening or not.

			clientIp (str)   - The IP address of the client

			Example Input: clientCheckRecieve("169.254.231.0")
			"""

			#The entire message has been read once the self.clientDict[clientIp][3] is True
			finished = False
			if (len(self.clientDict[clientIp][1]) != 0):
				#Check for end of message
				if (self.clientDict[clientIp][3]):
					finished = True

			return self.clientDict[clientIp][1], finished

		def clientStopRecieve(self, clientIp):
			"""Stops listening for data from the client.
			Note: The data is still in the buffer. You can resume listening by starting clientStartRecieve() again.
			To flush it, close the client and then open it again.

			clientIp (str)   - The IP address of the client

			Example Input: clientStopRecieve("169.254.231.0")
			"""

			self.clientDict[clientIp][2] = True

		def getClients(self):
			"""Returns a list of all current client IP addresses.

			Example Input: getClients()
			"""

			clients = list(self.clientDict.keys())
			return clients

		def closeClient(self, clientIp, clientsLeft = None):
			"""Cleans up the connection with a server client.

			clientIp (str)    - The IP number of the client.
			clientsLeft (int) - How many clients still need to connect

			Example Input: closeClient("169.254.231.0")
			"""

			if (clientIp not in self.clientDict):
				print("ERROR: There is no client {} for this server".format(clientIp))

			else:
				client = self.clientDict[clientIp][0]
				client.close()
				del(self.clientDict[clientIp])

			if (clientsLeft != None):
				return clientsLeft - 1

		def restrict(self, how = "rw"):
			"""Restricts the data flow between the ends of the socket.

			how (str) - What will be shut down
				"r"  - Will not allow data to be recieved
				"w"  - Will not allow data to be sent
				"rw" - Will not allow data to be recieved or sent
				"b"  - Will block the data

			Example Input: restrict()
			Example Input: restrict("r")
			"""

			if (how == "rw"):
				self.mySocket.shutdown(socket.SHUT_RDWR)

			elif (how == "r"):
				self.mySocket.shutdown(socket.SHUT_RD)

			elif (how == "w"):
				self.mySocket.shutdown(socket.SHUT_WR)

			elif (how == "b"):
				self.mySocket.setblocking(False)

			else:
				print("ERROR: Unknown restiction flag", how)

		def unrestrict(self, how = "rw"):
			"""Un-Restricts the data flow between the ends of the socket.

			how (str) - What will be shut down
				"r"  - Will allow data to be recieved
				"w"  - Will allow data to be sent
				"rw" - Will allow data to be recieved and sent
				"b"  - Will not block the data. Note: Sets the timeout to None

			Example Input: unrestrict()
			Example Input: unrestrict("r")
			"""

			if (how == "rw"):
				# self.mySocket.shutdown(socket.SHUT_RDWR)
				pass

			elif (how == "r"):
				# self.mySocket.shutdown(socket.SHUT_RD)
				pass

			elif (how == "w"):
				# self.mySocket.shutdown(socket.SHUT_WR)
				pass

			elif (how == "b"):
				self.mySocket.setblocking(True)

			else:
				print("ERROR: Unknown unrestiction flag", how)

		def getTimeout(self):
			"""Gets the tiemout for the socket.
			By default, the timeout is None.

			Example Input: setTimeout()
			"""

			timeout = self.mySocket.gettimeout()
			return timeout

		def setTimeout(self, timeout):
			"""Sets the tiemout for the socket.
			By default, the timeout is None.

			timeout (int) - How many seconds until timeout
				If None: There is no timeout

			Example Input: setTimeout(60)
			"""

			#Ensure that there is no negative value
			if (timeout != None):
				if (timeout < 0):
					print("ERROR: Timeout cannot be negative")
					return

			self.mySocket.settimeout(timeout)

		def getAddress(self, mine = False):
			"""Returns either the socket address or the remote address.

			mine (bool) - Determines which address is returned
				If True: Returns the socket's address
				If False: Returns the remote address

			Example Input: getAddress()
			"""

			if (mine):
				address = self.mySocket.getsockname()
			else:
				address = self.mySocket.getpeername()

			return address

		def ping(self, address):
			"""Returns True if the given ip address is online. Otherwise, it returns False.
			Code modified from http://www.opentechguides.com/how-to/article/python/57/python-ping-subnet.html

			address (str) - The ip address to ping

			Example Input: ping("169.254.231.0")
			"""

			#Configure subprocess to hide the console window
			info = subprocess.STARTUPINFO()
			info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
			info.wShowWindow = subprocess.SW_HIDE

			#Ping the address
			output = subprocess.Popen(['ping', '-n', '1', '-w', '500', address], stdout=subprocess.PIPE, startupinfo=info).communicate()[0]
			output = output.decode("utf-8")

			#Interpret Ping Results
			if ("Destination host unreachable" in output):
				return False #Offline

			elif ("Request timed out" in output):
				return False #Offline

			else:
				return True #Online

		def startScanIpRange(self, start, end):
			"""Scans a range of ip addresses in the given range for online ones.
			Because this can take some time, it saves the list of ip addresses as an internal variable.
			Special thanks to lovetocode on http://stackoverflow.com/questions/4525492/python-list-of-addressable-ip-addresses

			start (str) - The ip address to start at
			end (str)  - The ip address to stop after

			Example Input: startScanIpRange("169.254.231.0", "169.254.231.24")
			"""

			def runFunction(self, start, end):
				"""Needed to scan on a separate thread so the GUI is not tied up."""

				#Strip out empty spaces
				start = re.sub(" ", "", start)
				end = re.sub(" ", "", end)

				#Get ip scan range
				networkAddressSet = list(netaddr.IPRange(start, end))

				#For each IP address in the subnet, run the ping command with the subprocess.popen interface
				for i in range(len(networkAddressSet)):
					if (self.ipScanStop):
						self.ipScanStop = False
						break

					address = str(networkAddressSet[i])
					online = self.ping(address)

					#Determine if the address is desired by the user
					if (online):
						self.ipScanBlock.append(address)

				#Mark end of message
				self.ipScanBlock.append(None)

			#Listen for data on a separate thread
			self.ipScanBlock = []
			self.parent.backgroundRun(runFunction, [self, start, end])

		def checkScanIpRange(self):
			"""Checks for found active ip addresses from the scan.
			Each read portion is an element in a list.
			Returns the current block of data and whether it is finished listening or not.

			Example Input: checkScanIpRange()
			"""

			#The entire message has been read once the last element is None.
			finished = False
			if (len(self.ipScanBlock) != 0):
				if (self.ipScanBlock[-1] == None):
					finished = True
					self.ipScanBlock.pop(-1) #Remove the None from the end so the user does not get confused

			return self.ipScanBlock, finished

		def stopScanIpRange(self):
			"""Stops listening for data from the socket.
			Note: The data is still in the buffer. You can resume listening by starting startRecieve() again.
			To flush it, close the socket and then open it again.

			Example Input: stopScanIpRange()
			"""

			self.ipScanStop = True

	class ComPort():
		"""A controller for a single COM port."""

		def __init__(self):
			"""Defines the internal variables needed to run."""

			#Create needed objects
			self.serialPort = serial.Serial()

			#These are the defaults for serial.Serial.__init__()
			self.comPort         = None                #The device name
			self.comBaudRate     = 9600                #Rate at which information is transferred
			self.comByteSize     = serial.EIGHTBITS    #Number of bits per bytes
			self.comParity       = serial.PARITY_NONE  #For error detection
			self.comStopBits     = serial.STOPBITS_ONE #Signals message end
			self.comTimeoutRead  = None                #Read timeout. Makes the listener wait
			self.comTimeoutWrite = None                #Write timeout. Makes the speaker wait
			self.comFlowControl  = False               #Software flow control
			self.comRtsCts       = False               #Hardware (RTS/CTS) flow control
			self.comDsrDtr       = False               #Hardware (DSR/DTR) flow control
			self.comMessage      = None                #What is sent to the listener

		#Getters
		def getComPort(self):
			"""Returns the port.

			Example Input: getComPort()
			"""

			return self.comPort

		def getComBaudRate(self):
			"""Returns the baud rate.

			Example Input: getComBaudRate()
			"""

			return self.comBaudRate

		def getComDataBits(self):
			"""Overridden function for getComByteSize().

			Example Input: getComDataBits()
			"""

			value = self.getComByteSize()
			return value

		def getComByteSize(self):
			"""Returns the byte size.

			Example Input: getComByteSize()
			"""

			#Format the byte size
			if (self.comByteSize == serial.FIVEBITS):
				return 5

			elif (self.comByteSize == serial.SIXBITS):
				return 6

			elif (self.comByteSize == serial.SEVENBITS):
				return 7

			elif (self.comByteSize == serial.EIGHTBITS):
				return 8

			else:
				return self.comByteSize

		def getComParity(self):
			"""Returns the parity.

			Example Input: getComParity()
			"""

			if (self.comParity == serial.PARITY_NONE):
				return None

			elif (self.comParity == serial.PARITY_ODD):
				return "odd"
			
			elif (self.comParity == serial.PARITY_EVEN):
				return "even"
			
			elif (self.comParity == serial.PARITY_MARK):
				return "mark"
			
			elif (self.comParity == serial.PARITY_SPACE):
				return "space"

			else:
				return self.comParity

		def getComStopBits(self):
			"""Returns the stop bits.

			Example Input: getComStopBits()
			"""

			if (self.comStopBits == serial.STOPBITS_ONE):
				return 1

			elif (self.comStopBits == serial.STOPBITS_TWO):
				return 2

			elif (self.comStopBits == serial.STOPBITS_ONE_POINT_FIVE):
				return 1.5

			else:
				return self.comStopBits

		def getComTimeoutRead(self):
			"""Returns the read timeout.

			Example Input: getComTimeoutRead()
			"""

			return self.comTimeoutRead

		def getComTimeoutWrite(self):
			"""Returns the write timeout.

			Example Input: getComTimeoutWrite()
			"""

			return self.comTimeoutWrite

		def getComFlow(self):
			"""Returns the software flow control.

			Example Input: getComFlow()
			"""

			return self.comFlowControl

		def getComFlowS(self):
			"""Returns the hardware flow control.

			Example Input: getComFlowS(True)
			"""

			return self.comRtsCts

		def getComFlowR(self):
			"""Returns the hardware flow control.

			Example Input: getComFlowR()
			"""

			return self.comDsrDtr

		def getComMessage(self):
			"""Returns the message that will be sent.

			Example Input: getComMessage()
			"""

			return self.comMessage

		#Setters
		def setComPort(self, value):
			"""Changes the port.

			value (str) - The new port

			Example Input: setComPort("COM1")
			"""

			self.comPort = value

		def setComBaudRate(self, value):
			"""Changes the baud rate.

			value (int) - The new baud rate

			Example Input: setComBaudRate(9600)
			"""

			self.comBaudRate = value

		def setComDataBits(self, value):
			"""Overridden function for setComByteSize().

			value (int) - The new byte size. Can be 5, 6, 7, or 8

			Example Input: setComDataBits(8)
			"""

			self.setComByteSize(value)

		def setComByteSize(self, value):
			"""Changes the byte size.

			value (int) - The new byte size. Can be 5, 6, 7, or 8

			Example Input: setComByteSize(8)
			"""

			#Ensure that value is an integer
			if (type(value) != int):
				value = int(value)

			#Format the byte size
			if (value == 5):
				self.comByteSize = serial.FIVEBITS

			elif (value == 6):
				self.comByteSize = serial.SIXBITS

			elif (value == 7):
				self.comByteSize = serial.SEVENBITS

			elif (value == 8):
				self.comByteSize = serial.EIGHTBITS

		def setComParity(self, value):
			"""Changes the parity.

			value (str) - The new parity. Can be None, "odd", "even", "mark", or "space". Only the first letter is needed

			Example Input: setComParity("odd")
			"""

			if (value != None):
				#Ensure correct format
				if (type(value) == str):
					value = value.lower()

					if (value[0] == "n"):
						self.comParity = serial.PARITY_NONE
					
					elif (value[0] == "o"):
						self.comParity = serial.PARITY_ODD
					
					elif (value[0] == "e"):
						self.comParity = serial.PARITY_EVEN
					
					elif (value[0] == "m"):
						self.comParity = serial.PARITY_MARK
					
					elif (value[0] == "s"):
						self.comParity = serial.PARITY_SPACE

					else:
						print("ERROR: There is no parity", value)
						return False

				else:
					print("ERROR: There is no parity", value)
					return False

			else:
				self.comParity = serial.PARITY_NONE

			return True

		def setComStopBits(self, value):
			"""Changes the stop bits.

			value (int) - The new stop bits

			Example Input: setComStopBits(1)
			Example Input: setComStopBits(1.5)
			Example Input: setComStopBits(2)
			"""

			#Ensure that value is an integer or float
			if ((type(value) != int) and (type(value) != float)):
				value = int(value)

			#Format the stop bits
			if (value == 1):
				self.comStopBits = serial.STOPBITS_ONE

			elif (value == 2):
				self.comStopBits = serial.STOPBITS_TWO

			elif (value == 1.5):
				self.comStopBits = serial.STOPBITS_ONE_POINT_FIVE

			else:
				print("ERROR: There is no stop bit", value)

		def setComTimeoutRead(self, value):
			"""Changes the read timeout.

			value (int) - The new read timeout
						  None: Wait forever
						  0: Do not wait
						  Any positive int or float: How many seconds to wait

			Example Input: setComTimeoutRead(None)
			Example Input: setComTimeoutRead(1)
			Example Input: setComTimeoutRead(2)
			"""

			self.comTimeoutRead = value

		def setComTimeoutWrite(self, value):
			"""Changes the write timeout.

			value (int) - The new write timeout
						  None: Wait forever
						  0: Do not wait
						  Any positive int or float: How many seconds to wait

			Example Input: setComTimeoutWrite(None)
			Example Input: setComTimeoutWrite(1)
			Example Input: setComTimeoutWrite(2)
			"""

			self.comTimeoutWrite = value

		def setComFlow(self, value):
			"""Changes the software flow control.

			value (bool) - If True: Enables software flow control

			Example Input: setComFlow(True)
			"""

			self.comFlowControl = value

		def setComFlowS(self, value):
			"""Changes the hardware flow control.

			value (bool) - If True: Enables RTS/CTS flow control

			Example Input: setComFlowS(True)
			"""

			self.comRtsCts = value

		def setComFlowR(self, value):
			"""Changes the hardware flow control.

			value (bool) - If True: Enables DSR/DTR flow control

			Example Input: setComFlowR(True)
			"""

			self.comDsrDtr = value

		def setComMessage(self, value):
			"""Changes the message that will be sent.

			value (str) - The new message

			Example Input: setComMessage("Lorem ipsum")
			"""

			self.comMessage = value

		def openComPort(self, port = None):
			"""Gets the COM port that the zebra printer is plugged into and opens it.
			Returns True if the port sucessfully opened.
			Returns False if the port failed to open.

			### Untested ###
			port (str) - If Provided, opens this port instead of the port in memory

			Example Input: openComPort()
			Example Input: openComPort("COM2")
			"""

			#Configure port options
			if (port != None):
				self.serialPort.port     = port
			else:
				self.serialPort.port     = self.comPort
			self.serialPort.baudrate     = self.comBaudRate
			self.serialPort.bytesize     = self.comByteSize
			self.serialPort.parity       = self.comParity
			self.serialPort.stopbits     = self.comStopBits
			self.serialPort.timeout      = self.comTimeoutRead
			self.serialPort.writeTimeout = self.comTimeoutWrite
			self.serialPort.xonxoff      = self.comFlowControl
			self.serialPort.rtscts       = self.comRtsCts
			self.serialPort.dsrdtr       = self.comDsrDtr

			#Open the port
			try:
				self.serialPort.open()
			except:
				print("ERROR: Cannot find serial port", self.serialPort.port)
				return False

			#Check port status
			if self.serialPort.isOpen():
				print("Serial port", self.serialPort.port, "sucessfully opened")
				return True
			else:
				print("ERROR: Cannot open serial port", self.serialPort.port)
				return False

		def isOpen(self):
			"""Checks whether the COM port is open or not."""

			return self.serialPort.isOpen()

		def emptyComPort(self):
			"""Empties the buffer data in the given COM port."""

			self.serialPort.flushInput() #flush input buffer, discarding all its contents
			self.serialPort.flushOutput()#flush output buffer, aborting current output and discard all that is in buffer

		def closeComPort(self, port = None):
			"""Closes the current COM Port.

			### Not Yet Implemented ###
			port (str) - If Provided, closes this port instead of the port in memory

			Example Input: closeComPort()
			"""

			self.serialPort.close()

		def comWrite(self, message = None):
			"""Sends a message to the COM device.

			message (str) - The message that will be sent to the listener
							If None: The internally stored message will be used.

			Example Input: comWrite()
			Example Input: comWrite("Lorem ipsum")
			"""

			if (message == None):
				message = self.comMessage

			if (message != None):
				if self.serialPort.isOpen():
					#Ensure the buffer is empty
					self.serialPort.flushInput() #flush input buffer, discarding all its contents
					self.serialPort.flushOutput()#flush output buffer, aborting current output and discard all that is in buffer

					if (type(message) == str):
						#Convert the string to bytes
						unicodeString = message
						unicodeString = unicodeString.encode("utf-8")
					else:
						#The user gave a unicode string already
						unicodeString = message

					#write data
					self.serialPort.write(unicodeString)
					print("Wrote:", message)
				else:
					print("ERROR: Serial port has not been opened yet. Make sure that ports are available and then launch this application again.")
			else:
				print("ERROR: No message to send.")

	class Barcodes():
		"""Allows the user to create and read barcodes."""

		def __init__(self):
			"""Initializes internal variables."""

			pass

		def getTypes(self, grouped = 0):
			"""Returns the possible barcode types to the user as a list.

			grouping (int) - Configures how the barcode types will be returned
				0: No grouping will be done
				1: The same barcodes with different names will be grouped as sub-lists
				2: The same barcodes with different names will be grouped as a single string
				3: Barcodes of similar names will be grouped as sub-lists (Some are duplicated)
				4: A dictionary where the key is the readable name for it, and the value is the correct arg 'codeType' for create()

			Example Input: getTypes()
			Example Input: getTypes(1)
			Example Input: getTypes(2)
			"""

			if (grouped == 0):
				typeList = ["EAN-13", "EAN", "UCC-13", "JAN", "JAN-13", "EAN-13+2", "EAN-13+5", "EAN-99", "EAN-8", "UCC-8", "JAN-8", "EAN-8+2", "EAN-8+5", "EAN-Velocity", 
					"UPC-A", "UPC", "UCC-12", "UPC-A+2", "UPC-A+5", "UPC-E", "UPC-E0", "UPC-E1", "UPC-E+2", "UPC-E+5", "ISBN", "ISBN-13", "ISBN-10", "Bookland EAN-13", 
					"ISMN", "ISSN", "EAN-5", "EAN-2", "GS1 DataBar Omnidirectional", "RSS-14", "GS1 DataBar Stacked", "RSS-14 Stacked", 
					"GS1 DataBar Stacked Omnidirectional", "RSS-14 Stacked Omnidirectional", "GS1 DataBar Truncated", "RSS-14 Truncated", 
					"GS1 DataBar Limited", "RSS Limited", "GS1 DataBar Expanded", "RSS Expanded", "GS1 DataBar Expanded Stacked", "RSS Expanded Stacked", 
					"GS1-128", "UCC/EAN-128", "EAN-128", "UCC-128", "SSCC-18", "EAN-18", "NVE", "EAN-14", "UCC-14", "ITF-14", "UPC SCS", "QR Code", 
					"Micro QR Code", "GS1 QR Code", "Data Matrix", "Data Matrix ECC 200", "Data Matrix Rectangular Extension", "GS1 DataMatrix", 
					"Aztec Code", "Compact Aztec Code", "Aztec Runes", "PDF417", "Compact PDF417", "Truncated PDF417", "MicroPDF417", "Han Xin Code", "Chinese Sensible", 
					"MaxiCode", "UPS Code", "Code 6", "Codablock F", "Code 16K", "USS-16K", "Code 49", "USS-49", "Code 1", "Code 1S", "USPS POSTNET", 
					"USPS PLANET", "USPS Intelligent Mail", "USPS OneCode", "USPS FIM", "Royal Mail", "RM4SCC", "CBC", "Royal TNT Post", "KIX", "Japan Post", 
					"Australia Post", "Deutsche Post Identcode", "DHL Identcode", "Deutsche Post Leitcode", "DHL Leitcode", "Pharmacode", "Pharmaceutical Binary Code", 
					"Two-track Pharmacode", "Two-track Pharmaceutical Binary Code", "Code 32", "Italian-Pharmacode", "IMH", "PZN", "Pharmazentralnummer", "PZN-8", "PZN-7", 
					"Code 39", "Code 3 of 9", "LOGMARS", "Alpha39", "USD-3", "USD-2", "USS-39", "Code 39 Extended", "Code 39 Full ASCII", "Code 93", "USD-7", "USS-93", 
					"Code 93 Extended", "Code 93 Full ASCII", "Code 128", "Code 128A", "Code 128B", "Code 128C", "USD-6", "USS-128", "Code 25", "Code 2 of 5", "Industrial 2 of 5", 
					"IATA-2 of 5", "Datalogic 2 of 5", "Matrix 2 of 5", "COOP 2 of 5", "Interleaved 2 of 5", "ITF", "Code 2 of 5 Interleaved", "USD-1", "USS-Interleaved 2 of 5", 
					"Code 11", "USD-8", "Codabar", "Rationalized Codabar", "Ames Code", "NW-7", "USD-4", "USS-Codabar", "Monarch", "Code 2 of 7", "Plessey", "Anker Code", 
					"MSI Plessey", "MSI", "MSI Modified Plessey", "Telepen", "Telepen Alpha", "Telepen Full ASCII", "Telepen Numeric", "Channel Code", 
					"PosiCode", "PosiCode A", "PosiCode B", "BC412", "BC412 SEMI", "BC412 IBM", "GS1 Composite Symbols", "EAN-13 Composite", "EAN-8 Composite", "UPC-A Composite", 
					"UPC-E Composite", "GS1 DataBar Omnidirectional Composite", "GS1 DataBar Stacked Composite", "GS1 DataBar Stacked Omni Composite", 
					"GS1 DataBar Truncated Composite", "GS1 DataBar Limited Composite", "GS1 DataBar Expanded Composite", "GS1 DataBar Expanded Stacked Composite", "GS1-128 Composite", 
					"HIBC barcodes", "HIBC Code 39", "HIBC Code 128", "HIBC Data Matrix", "HIBC PDF417", "HIBC MicroPDF417", "HIBC QR Code", "HIBC Codablock F"]

			elif (grouped == 1):
				typeList = [["EAN-13", "EAN", "UCC-13", "JAN", "JAN-13", "EAN-13+2", "EAN-13+5", "EAN-99"], ["EAN-8", "UCC-8", "JAN-8", "EAN-8+2", "EAN-8+5", "EAN-Velocity"], 
					["UPC-A", "UPC", "UCC-12", "UPC-A+2", "UPC-A+5"], ["UPC-E", "UPC-E0", "UPC-E1", "UPC-E+2", "UPC-E+5"], ["ISBN", "ISBN-13", "ISBN-10", "Bookland EAN-13"], 
					["ISMN"], ["ISSN"], ["EAN-5"], ["EAN-2"], ["GS1 DataBar Omnidirectional", "RSS-14"], ["GS1 DataBar Stacked", "RSS-14 Stacked"], 
					["GS1 DataBar Stacked Omnidirectional", "RSS-14 Stacked Omnidirectional"], ["GS1 DataBar Truncated", "RSS-14 Truncated"], 
					["GS1 DataBar Limited", "RSS Limited"], ["GS1 DataBar Expanded", "RSS Expanded"], ["GS1 DataBar Expanded Stacked", "RSS Expanded Stacked"], 
					["GS1-128", "UCC/EAN-128", "EAN-128", "UCC-128"], ["SSCC-18", "EAN-18", "NVE"], ["EAN-14", "UCC-14"], ["ITF-14", "UPC SCS"], ["QR Code"], 
					["Micro QR Code"], ["GS1 QR Code"], ["Data Matrix", "Data Matrix ECC 200", "Data Matrix Rectangular Extension"], ["GS1 DataMatrix"], 
					["Aztec Code", "Compact Aztec Code"], ["Aztec Runes"], ["PDF417"], ["Compact PDF417", "Truncated PDF417"], ["MicroPDF417"], ["Han Xin Code", "Chinese Sensible"], 
					["MaxiCode", "UPS Code", "Code 6"], ["Codablock F"], ["Code 16K", "USS-16K"], ["Code 49", "USS-49"], ["Code 1", "Code 1S"], ["USPS POSTNET"], 
					["USPS PLANET"], ["USPS Intelligent Mail", "USPS OneCode"], ["USPS FIM"], ["Royal Mail", "RM4SCC", "CBC"], ["Royal TNT Post", "KIX"], ["Japan Post"], 
					["Australia Post"], ["Deutsche Post Identcode", "DHL Identcode"], ["Deutsche Post Leitcode", "DHL Leitcode"], ["Pharmacode", "Pharmaceutical Binary Code"], 
					["Two-track Pharmacode", "Two-track Pharmaceutical Binary Code"], ["Code 32", "Italian-Pharmacode", "IMH"], ["PZN", "Pharmazentralnummer", "PZN-8", "PZN-7"], 
					["Code 39", "Code 3 of 9", "LOGMARS", "Alpha39", "USD-3", "USD-2", "USS-39"], ["Code 39 Extended", "Code 39 Full ASCII"], ["Code 93", "USD-7", "USS-93"], 
					["Code 93 Extended", "Code 93 Full ASCII"], ["Code 128", "Code 128A", "Code 128B", "Code 128C", "USD-6", "USS-128"], ["Code 25", "Code 2 of 5", "Industrial 2 of 5"], 
					["IATA-2 of 5"], ["Datalogic 2 of 5"], ["Matrix 2 of 5"], ["COOP 2 of 5"], ["Interleaved 2 of 5", "ITF", "Code 2 of 5 Interleaved", "USD-1", "USS-Interleaved 2 of 5"], 
					["Code 11", "USD-8"], ["Codabar", "Rationalized Codabar", "Ames Code", "NW-7", "USD-4", "USS-Codabar", "Monarch", "Code 2 of 7"], ["Plessey", "Anker Code"], 
					["MSI Plessey", "MSI", "MSI Modified Plessey"], ["Telepen", "Telepen Alpha", "Telepen Full ASCII"], ["Telepen Numeric"], ["Channel Code"], 
					["PosiCode", "PosiCode A", "PosiCode B"], ["BC412", "BC412 SEMI", "BC412 IBM"], ["GS1 Composite Symbols", "EAN-13 Composite", "EAN-8 Composite", "UPC-A Composite", 
					"UPC-E Composite", "GS1 DataBar Omnidirectional Composite", "GS1 DataBar Stacked Composite", "GS1 DataBar Stacked Omni Composite", 
					"GS1 DataBar Truncated Composite", "GS1 DataBar Limited Composite", "GS1 DataBar Expanded Composite", "GS1 DataBar Expanded Stacked Composite", "GS1-128 Composite"], 
					["HIBC barcodes", "HIBC Code 39", "HIBC Code 128", "HIBC Data Matrix", "HIBC PDF417", "HIBC MicroPDF417", "HIBC QR Code", "HIBC Codablock F"]]

			elif (grouped == 2):
				typeList = ["EAN-13 (EAN, UCC-13, JAN, JAN-13, EAN-13+2, EAN-13+5, EAN-99)", "EAN-8 (UCC-8, JAN-8, EAN-8+2, EAN-8+5, EAN-Velocity)", 
					"UPC-A (UPC, UCC-12, UPC-A+2, UPC-A+5)", "UPC-E (UPC-E0, UPC-E1, UPC-E+2, UPC-E+5)", "ISBN (ISBN-13, ISBN-10, Bookland EAN-13)", 
					"ISMN, ISSN, EAN-5 & EAN-2 (EAN/UPC add-ons)", "GS1 DataBar Omnidirectional (RSS-14)", "GS1 DataBar Stacked (RSS-14 Stacked)", 
					"GS1 DataBar Stacked Omnidirectional (RSS-14 Stacked Omnidirectional)", "GS1 DataBar Truncated (RSS-14 Truncated)", 
					"GS1 DataBar Limited (RSS Limited)", "GS1 DataBar Expanded (RSS Expanded)", "GS1 DataBar Expanded Stacked (RSS Expanded Stacked)", 
					"GS1-128 (UCC/EAN-128, EAN-128, UCC-128)", "SSCC-18 (EAN-18, NVE)", "EAN-14 (UCC-14)", "ITF-14 (UPC SCS)", "QR Code (Quick Response Code)", 
					"Micro QR Code", "GS1 QR Code", "Data Matrix (Data Matrix ECC 200, Data Matrix Rectangular Extension)", "GS1 DataMatrix", 
					"Aztec Code (Compact Aztec Code)", "Aztec Runes", "PDF417", "Compact PDF417 (Truncated PDF417)", "MicroPDF417", "Han Xin Code (Chinese Sensible)", 
					"MaxiCode (UPS Code, Code 6)", "Codablock F", "Code 16K (USS-16K)", "Code 49 (USS-49)", "Code 1 (Code 1S)", "USPS POSTNET", 
					"USPS PLANET", "USPS Intelligent Mail (USPS OneCode)", "USPS FIM", "Royal Mail (RM4SCC, CBC)", "Royal TNT Post (KIX)", "Japan Post", 
					"Australia Post", "Deutsche Post Identcode (DHL Identcode)", "Deutsche Post Leitcode (DHL Leitcode)", "Pharmacode (Pharmaceutical Binary Code)", 
					"Two-track Pharmacode (Two-track Pharmaceutical Binary Code)", "Code 32 (Italian-Pharmacode, IMH)", "PZN (Pharmazentralnummer, PZN-8, PZN-7)", 
					"Code 39 (Code 3 of 9, LOGMARS, Alpha39, USD-3, USD-2, USS-39)", "Code 39 Extended (Code 39 Full ASCII)", "Code 93 (USD-7, USS-93)", 
					"Code 93 Extended (Code 93 Full ASCII)", "Code 128 (Code 128A, Code 128B, Code 128C, USD-6, USS-128)","Code 25 (Code 2 of 5, Industrial 2 of 5)", 
					"IATA-2 of 5", "Datalogic 2 of 5", "Matrix 2 of 5", "COOP 2 of 5", "Interleaved 2 of 5 (ITF, Code 2 of 5 Interleaved, USD-1, USS-Interleaved 2 of 5)", 
					"Code 11 (USD-8)", "Codabar (Rationalized Codabar, Ames Code, NW-7, USD-4, USS-Codabar, Monarch, Code 2 of 7)", "Plessey (Anker Code)", 
					"MSI Plessey (MSI, MSI Modified Plessey)", "Telepen (Telepen Alpha, Telepen Full ASCII)", "Telepen Numeric", "Channel Code", 
					"PosiCode (PosiCode A, PosiCode B)", "BC412 (BC412 SEMI, BC412 IBM)", ("GS1 Composite Symbols (EAN-13 Composite, EAN-8 Composite, UPC-A Composite, " 
					"UPC-E Composite, GS1 DataBar Omnidirectional Composite, GS1 DataBar Stacked Composite, GS1 DataBar Stacked Omni Composite, " 
					"GS1 DataBar Truncated Composite, GS1 DataBar Limited Composite, GS1 DataBar Expanded Composite, GS1 DataBar Expanded Stacked Composite, GS1-128 Composite)"), 
					"HIBC barcodes (HIBC Code 39, HIBC Code 128, HIBC Data Matrix, HIBC PDF417, HIBC MicroPDF417, HIBC QR Code, HIBC Codablock F)"]

			elif (grouped == 3):
				typeList = [["EAN-13", "EAN", "EAN-13+2", "EAN-13+5", "EAN-99", "EAN-8", "EAN-8+2", "EAN-8+5", "Bookland EAN-13", "EAN-Velocity", "EAN-5", "EAN-2", "UCC/EAN-128", 
					"EAN-128", "EAN-18", "EAN-14", "EAN-13 Composite", "EAN-8 Composite"], ["UCC-13", "UCC-8", "UCC-12", "UCC/EAN-128", "UCC-128", "UCC-14"], ["JAN", "JAN-13", "JAN-8"], 
					["UPC-A", "UPC", "UPC-A+2", "UPC-A+5", "UPC-E", "UPC-E0", "UPC-E1", "UPC-E+2", "UPC-E+5", "UPC SCS", "UPC-E Composite", "UPC-A Composite"], ["ISBN", "ISBN-13", "ISBN-10"], 
					["ISMN"], ["ISSN"], ["GS1 DataBar Omnidirectional", "GS1 DataBar Stacked", "GS1 DataBar Stacked Omnidirectional", "GS1 DataBar Truncated", "GS1 DataBar Limited", 
					"GS1 DataBar Expanded", "GS1 DataBar Expanded Stacked", "GS1-128", "GS1 QR Code", "GS1 DataMatrix", "GS1 Composite Symbols", "GS1 DataBar Omnidirectional Composite", 
					"GS1 DataBar Stacked Composite", "GS1 DataBar Stacked Omni Composite", "GS1 DataBar Truncated Composite", "GS1 DataBar Limited Composite", "GS1 DataBar Expanded Composite", 
					"GS1 DataBar Expanded Stacked Composite", "GS1-128 Composite"], ["RSS-14", "RSS-14 Stacked", "RSS-14 Stacked Omnidirectional", "RSS-14 Truncated", "RSS Limited", 
					"RSS Expanded", "RSS Expanded Stacked"], ["SSCC-18"], ["NVE"], ["ITF-14", "ITF"], ["QR Code", "Micro QR Code", "GS1 QR Code", "HIBC QR Code"], ["Data Matrix", "Data Matrix ECC 200", 
					"Data Matrix Rectangular Extension", "HIBC Data Matrix"], ["Aztec Code", "Compact Aztec Code", "Aztec Runes"], ["PDF417", "Compact PDF417", "Truncated PDF417", "MicroPDF417", 
					"HIBC PDF417", "HIBC MicroPDF417", ], ["Han Xin Code", "Chinese Sensible"], ["MaxiCode"], ["UPS Code", "USPS POSTNET", "USPS PLANET", "USPS Intelligent Mail", "USPS OneCode", 
					"USPS FIM", "Royal Mail", "RM4SCC", "CBC", "Royal TNT Post", "KIX", "Japan Post", "Australia Post", "Deutsche Post Identcode", "DHL Identcode", "Deutsche Post Leitcode", "DHL Leitcode"], 
					["Code 6", "Code 16K", "Code 49", "Code 1", "Code 1S", "Code 32", "Code 39", "Code 39 Extended", "Code 39 Full ASCII", "Code 93", "Code 93 Extended", 
					"Code 93 Full ASCII", "Code 128", "Code 128A", "Code 128B", "Code 128C", "Code 25", "Code 11", "HIBC Code 39", "HIBC Code 128"], ["Code 3 of 9", "Code 2 of 5", 
					"Industrial 2 of 5", "IATA-2 of 5", "Datalogic 2 of 5", "Matrix 2 of 5", "COOP 2 of 5", "Interleaved 2 of 5", "Code 2 of 5 Interleaved", "USS-Interleaved 2 of 5", "Code 2 of 7"],
					["Codablock F", "HIBC Codablock F"], ["Codabar", "Rationalized Codabar", "USS-Codabar"], ["USS-Interleaved 2 of 5", "USS-Codabar", "USS-16K", "USS-49", "USS-39", "USS-93", "USS-128"], 
					["Pharmacode", "Pharmaceutical Binary Code", "Two-track Pharmacode", "Two-track Pharmaceutical Binary Code", "Italian-Pharmacode", "IMH", "PZN", 
					"Pharmazentralnummer", "PZN-8", "PZN-7"], ["PZN", "PZN-8", "PZN-7"], ["LOGMARS"], ["Alpha39"], ["USD-3", "USD-2", "USD-7", "USD-6", "USD-1", "USD-8", "USD-4"], 
					["Ames Code"], ["NW-7"], ["Monarch"], ["Plessey", "MSI Plessey", "MSI Modified Plessey"], ["Anker Code"], ["MSI", "MSI Plessey", "MSI Modified Plessey"], ["Telepen", 
					"Telepen Alpha", "Telepen Full ASCII", "Telepen Numeric"], ["Channel Code"], ["PosiCode", "PosiCode A", "PosiCode B"], ["BC412", "BC412 SEMI", "BC412 IBM"], 					
					["HIBC barcodes", "HIBC Code 39", "HIBC Code 128", "HIBC Data Matrix", "HIBC PDF417", "HIBC MicroPDF417", "HIBC QR Code", "HIBC Codablock F"], ["EAN-13 Composite", "EAN-8 Composite", 
					"UPC-E Composite", "UPC-A Composite", "GS1 Composite Symbols", "GS1 DataBar Omnidirectional Composite", "GS1 DataBar Stacked Composite", "GS1 DataBar Stacked Omni Composite", 
					"GS1 DataBar Truncated Composite", "GS1 DataBar Limited Composite", "GS1 DataBar Expanded Composite", "GS1 DataBar Expanded Stacked Composite", "GS1-128 Composite"],
					["GS1 DataBar Truncated", "GS1 DataBar Truncated Composite", "RSS-14 Truncated", "Truncated PDF417", "GS1 DataBar Truncated Composite"], ["GS1 DataBar Expanded", 
					"GS1 DataBar Expanded Stacked", "GS1 DataBar Expanded Composite", "GS1 DataBar Expanded Stacked Composite", "RSS Expanded", "RSS Expanded Stacked", "GS1 DataBar Expanded Composite", 
					"GS1 DataBar Expanded Stacked Composite"], ["GS1 DataBar Stacked", "GS1 DataBar Stacked Omnidirectional", "GS1 DataBar Stacked Composite", "GS1 DataBar Stacked Omni Composite", 
					"GS1 DataBar Expanded Stacked Composite", "RSS-14 Stacked", "RSS-14 Stacked Omnidirectional", "RSS Expanded Stacked"], ["GS1 DataBar Omnidirectional", "GS1 DataBar Stacked Omnidirectional", 
					"GS1 DataBar Omnidirectional Composite", "GS1 DataBar Stacked Omni Composite", "GS1 DataBar Omnidirectional Composite", "RSS-14 Stacked Omnidirectional"]]

			elif (grouped == 4):
				typeList = {"EAN-13": "ean13", "EAN": "ean13", "UCC-13": "ean13", "JAN": "ean13", "JAN-13": "ean13", "EAN-13+2": "ean13", "EAN-13+5": "ean13", "EAN-99": "ean13",
					"EAN-8": "ean8", "UCC-8": "ean8", "JAN-8": "ean8", "EAN-8+2": "ean8", "EAN-8+5": "ean8", "EAN-Velocity": "ean8",
					"UPC-A": "upca", "UPC": "upca", "UCC-12": "upca", "UPC-A+2": "upca", "UPC-A+5": "upca",
					"UPC-E": "upce", "UPC-E0": "upce", "UPC-E1": "upce", "UPC-E+2": "upce", "UPC-E+5": "upce",
					"ISBN": "isbn", "ISBN-13": "isbn", "ISBN-10": "isbn", "Bookland EAN-13": "isbn",
					"ISMN": "ismn",
					"ISSN": "issn",
					"EAN-5": "ean5",
					"EAN-2": "ean2",
					"GS1 DataBar Omnidirectional": "databaromni", "RSS-14": "databaromni",
					"GS1 DataBar Stacked": "databarstacked", "RSS-14 Stacked": "databarstacked",
					"GS1 DataBar Stacked Omnidirectional": "databarstackedomni", "RSS-14 Stacked Omnidirectional": "databarstackedomni",
					"GS1 DataBar Truncated": "databartruncated", "RSS-14 Truncated": "databartruncated",
					"GS1 DataBar Limited": "databarlimited", "RSS Limited": "databarlimited",
					"GS1 DataBar Expanded": "databarexpanded", "RSS Expanded": "databarexpanded",
					"GS1 DataBar Expanded Stacked": "databarexpandedstacked", "RSS Expanded Stacked": "databarexpandedstacked",
					"GS1-128": "gs1-128", "UCC/EAN-128": "gs1-128", "EAN-128": "gs1-128", "UCC-128": "gs1-128",
					"SSCC-18": "sscc18", "EAN-18": "sscc18", "NVE": "sscc18",
					"EAN-14": "ean14", "UCC-14": "ean14",
					"ITF-14": "itf14", "UPC SCS": "itf14",
					"QR Code": "qrcode",
					"Micro QR Code": "microqrcode",
					"GS1 QR Code": "gs1qrcode",
					"Data Matrix": "datamatrix", "Data Matrix ECC 200": "datamatrix", "Data Matrix Rectangular Extension": "datamatrix",
					"GS1 DataMatrix": "gs1datamatrix",
					"Aztec Code": "azteccode", "Compact Aztec Code": "azteccode",
					"Aztec Runes": "aztecrune",
					"PDF417": "pdf417",
					"Compact PDF417": "pdf417compact", "Truncated PDF417": "pdf417compact",
					"MicroPDF417": "micropdf417",
					"Han Xin Code": "hanxin", "Chinese Sensible": "hanxin",
					"MaxiCode": "maxicode", "UPS Code": "maxicode", "Code 6": "maxicode",
					"Codablock F": "codablockf",
					"Code 16K": "code16k", "USS-16K": "code16k",
					"Code 49": "code49", "USS-49": "code49",
					"Code 1": "codeone", "Code 1S": "codeone",
					"USPS POSTNET": "postnet",
					"USPS PLANET": "planet",
					"USPS Intelligent Mail": "onecode", "USPS OneCode": "onecode",
					"USPS FIM": "symbol",
					"Royal Mail": "royalmail", "RM4SCC": "royalmail", "CBC": "royalmail",
					"Royal TNT Post": "kix", "KIX": "kix",
					"Japan Post": "japanpost",
					"Australia Post": "auspost",
					"Deutsche Post Identcode": "identcode", "DHL Identcode": "identcode",
					"Deutsche Post Leitcode": "leitcode", "DHL Leitcode": "leitcode",
					"Pharmacode": "pharmacode", "Pharmaceutical Binary Code": "pharmacode",
					"Two-track Pharmacode": "pharmacode2", "Two-track Pharmaceutical Binary Code": "pharmacode2",
					"Code 32": "code32", "Italian-Pharmacode": "code32", "IMH": "code32",
					"PZN": "pzn", "Pharmazentralnummer": "pzn", "PZN-8": "pzn", "PZN-7": "pzn",
					"Code 39": "code39", "Code 3 of 9": "code39", "LOGMARS": "code39", "Alpha39": "code39", "USD-3": "code39", "USD-2": "code39", "USS-39": "code39",
					"Code 39 Extended": "code39ext", "Code 39 Full ASCII": "code39ext",
					"Code 93": "code93", "USD-7": "code93", "USS-93": "code93",
					"Code 93 Extended": "code93ext", "Code 93 Full ASCII": "code93ext",
					"Code 128": "code128", "Code 128A": "code128", "Code 128B": "code128", "Code 128C": "code128", "USD-6": "code128", "USS-128": "code128",
					"Code 25": "code2of5", "Code 2 of 5": "code2of5", "Industrial 2 of 5": "code2of5",
					"IATA-2 of 5": "iata2of5",
					"Datalogic 2 of 5": None,
					"Matrix 2 of 5": None,
					"COOP 2 of 5": None,
					"Interleaved 2 of 5": "interleaved2of5", "ITF": "interleaved2of5", "Code 2 of 5 Interleaved": "interleaved2of5", "USD-1": "interleaved2of5", "USS-Interleaved 2 of 5": "interleaved2of5",
					"Code 11": "code11", "USD-8": "code11",
					"Codabar": "rationalizedCodabar", "Rationalized Codabar": "rationalizedCodabar", "Ames Code": "rationalizedCodabar", "NW-7": "rationalizedCodabar", "USD-4": "rationalizedCodabar", "USS-Codabar": "rationalizedCodabar", "Monarch": "rationalizedCodabar", "Code 2 of 7": "rationalizedCodabar",
					"Plessey": "plessey", "Anker Code": "plessey",
					"MSI Plessey": "msi", "MSI": "msi", "MSI Modified Plessey": "msi",
					"Telepen": "telepen", "Telepen Alpha": "telepen", "Telepen Full ASCII": "telepen",
					"Telepen Numeric": "telepennumeric",
					"Channel Code": "channelcode",
					"PosiCode": "posicode", "PosiCode A": "posicode", "PosiCode B": "posicode",
					"BC412": "bc412", "BC412 SEMI": "bc412", "BC412 IBM": "bc412",
					"GS1 Composite Symbols": "ean13composite", "EAN-13 Composite": "ean13composite", "EAN-8 Composite": "ean13composite", "UPC-A Composite": "ean13composite", "UPC-E Composite": "ean13composite", "GS1 DataBar Omnidirectional Composite": "ean13composite", "GS1 DataBar Stacked Composite": "ean13composite", "GS1 DataBar Stacked Omni Composite": "ean13composite", "GS1 DataBar Truncated Composite": "ean13composite", "GS1 DataBar Limited Composite": "ean13composite", "GS1 DataBar Expanded Composite": "ean13composite", "GS1 DataBar Expanded Stacked Composite": "ean13composite", "GS1-128 Composite": "ean13composite",
					"HIBC barcodes": "hibccode39", "HIBC Code 39": "hibccode39", "HIBC Code 128": "hibccode39", "HIBC Data Matrix": "hibccode39", "HIBC PDF417": "hibccode39", "HIBC MicroPDF417": "hibccode39", "HIBC QR Code": "hibccode39", "HIBC Codablock F": "hibccode39"}
			# qrcode
			# code128
			# pdf417
			# royalmail
			# datamatrix
			# code11
			# code25
			# code39
			# code93
			# japanpost
			# azteccode
			# auspost
			# interleaved2of5
			# raw
			# kix
			# postnet
			# pharmacode
			# plessey
			# symbol
			# onecode
			# maxicode
			# msi
			# rss14
			# rationalizedCodabar

			return typeList

		def create(self, codeType, text, fileName = None, saveFormat = None, dpi = 300):
			"""Returns a PIL image of the barcode for the user or saves it somewhere as an image.

			codeType (str)   - What type of barcode will be made
			text (str)       - What the barcode will say
			fileName (str)   - If not None: Where an image of the barcode will be saved
			saveFormat (str) - What image format to save it as (All PIL formats are valid)
				If None: The image will be saved as a png
			dpi (int)        - How many dots per inch to draw the label at

			Example Input: create("code128", 1234567890)
			Example Input: create("code128", 1234567890, "barcode", "bmp")
			"""

			#Configure settings
			myWriter = {}
			if (saveFormat != None):
				myWriter["format"] = saveFormat

			if (dpi != 300):
				myWriter["dpi"] = dpi

			#Create barcode
			myBarcode = elaphe.barcode(codeType, text, options=dict(version=9, eclevel='M'), margin=10, data_mode='8bits')










			myBarcode = barcode.get(codeType, text, writer = barcode.writer.ImageWriter())

			#Save or return the barcode
			if (fileName != None):
				myBarcode.save(fileName, myWriter)
			else:
				image = myBarcode.render(myWriter)
				return image

		### To do ###
		def read(self):
			"""Reads a barcode."""

			pass

class Security():
	"""Allows the GUI to encrypt and decrypt files.
	Adapted from: http://www.blog.pythonlibrary.org/2016/05/18/python-3-an-intro-to-encryption/
	"""

	def __init__(self):
		"""Initializes defaults and internal variables."""

		#Defaults
		self.password = "Admin"

		#Internal Variables
		self.missingPublicKey  = True
		self.missingPrivateKey = True

	def setPassword(self, password):
		"""Changes the encryption password.

		password (str) - What the encryption password is

		Example Input: setPassword("Lorem")
		"""

		self.password = password

	def generateKeys(self, privateDir = "", publicDir = "", privateName = "privateKey", publicName = "publicKey", autoLoad = True):
		"""Creates a private and public key.

		privateDir (str)  - The save directory for the private key
		publicDir (str)   - The save directory for the public key
		privateName (str) - The name of the private key file
		publicName (str)  - The name of the public key file
		autoLoad (bool)   - Automatically loads the generated keys into memory

		Example Input: generateKeys()
		Example Input: generateKeys(autoLoad = False)
		"""

		#Create the key
		key = Cryptodome.PublicKey.RSA.generate(2048)
		encryptedKey = key.exportKey(passphrase = self.password, pkcs=8, protection = "scryptAndAES128-CBC")

		#Save the key
		with open(privateDir + privateName + ".pem", 'wb') as fileHandle:
				fileHandle.write(encryptedKey)

		with open(publicDir + publicName + ".pem", 'wb') as fileHandle:
				fileHandle.write(key.publickey().exportKey())

		#Load the key
		if (autoLoad):
			self.loadKeys(privateDir, publicDir, privateName, publicName)

	def loadKeys(self, privateDir = "", publicDir = "", privateName = "privateKey", publicName = "publicKey"):
		"""Creates a private and public key.

		privateDir (str)  - The save directory for the private key
		publicDir (str)   - The save directory for the public key
		privateName (str) - The name of the private key file
		publicName (str)  - The name of the public key file

		Example Input: loadKeys()
		"""

		self.loadPrivateKey(privateDir, privateName)
		self.loadPublicKey(publicDir, publicName)

	def loadPrivateKey(self, directory = "", name = "privateKey"):
		"""Loads the private key into memory.

		directory (str) - The save directory for the private key
		name (str)      - The name of the private key file

		Example Input: loadPrivateKey()
		"""

		self.privateKey = Cryptodome.PublicKey.RSA.import_key(
			open(directory + name + ".pem").read(), passphrase = self.password)

		self.missingPrivateKey = False

	def loadPublicKey(self, directory = "", name = "publicKey"):
		"""Loads the public key into memory.

		directory (str) - The save directory for the public key
		name (str)      - The name of the public key file

		Example Input: loadPublicKey()
		"""

		self.publicKey = Cryptodome.PublicKey.RSA.import_key(
			open(directory + name + ".pem").read())

		self.missingPublicKey = False

	def encryptData(self, data, directory = "", name = "encryptedData", extension = "db"):
		"""Encrypts a string of data to a new file.
		If a file by the same name already exists, it replaces the file.

		data (str)      - The string to encrypt and store
		directory (str) - The save directory for the encrypted data
		name (str)      - The name of the encrypted data
		extension (str) - The file extension for the encrypted data

		Example Input: encryptData("Lorem Ipsum")
		Example Input: encryptData("Lorem Ipsum", extension = "txt")
		"""

		#Check for keys
		if (self.missingPublicKey or self.missingPrivateKey):
			print("ERROR: Cannot encrypt data without keys. Use 'loadKeys()' or 'loadPublicKey() and loadPrivateKey()'.")
			return None

		#Format the output path
		outputName = directory + name + "." + extension

		#Format the data
		data = data.encode("utf-8")

		#Create the file
		with open(outputName, "wb") as outputFile:
			sessionKey = Cryptodome.Random.get_random_bytes(16)

			#Write the session key
			cipherRSA = Cryptodome.Cipher.PKCS1_OAEP.new(self.publicKey)
			outputFile.write(cipherRSA.encrypt(sessionKey))

			#Write the data
			cipherAES = Cryptodome.Cipher.AES.new(sessionKey, Cryptodome.Cipher.AES.MODE_EAX)
			ciphertext, tag = cipherAES.encrypt_and_digest(data)

			outputFile.write(cipherAES.nonce)
			outputFile.write(tag)
			outputFile.write(ciphertext)

	def decryptData(self, directory = "", name = "encryptedData", extension = "db"):
		"""Decrypts an encrypted file into a string of data

		directory (str) - The save directory for the encrypted data
		name (str)      - The name of the encrypted data
		extension (str) - The file extension for the encrypted data

		Example Input: encryptData()
		Example Input: encryptData(extension = "txt")
		"""

		#Check for keys
		if (self.missingPublicKey or self.missingPrivateKey):
			print("ERROR: Cannot encrypt data without keys. Use 'loadKeys()' or 'loadPublicKey() and loadPrivateKey()'.")
			return None

		#Format the output path
		inputName = directory + name + "." + extension

		#Create the file
		with open(inputName, "rb") as inputFile:
			endSessionKey, nonce, tag, ciphertext = [ inputFile.read(x) 
			for x in (self.privateKey.size_in_bytes(), 16, 16, -1) ]

			cipherRSA = Cryptodome.Cipher.PKCS1_OAEP.new(self.privateKey)
			sessionKey = cipherRSA.decrypt(endSessionKey)

			cipherAES = Cryptodome.Cipher.AES.new(sessionKey, Cryptodome.Cipher.AES.MODE_EAX, nonce)
			data = cipherAES.decrypt_and_verify(ciphertext, tag)                

		#Format the output data
		data = data.decode("utf-8")
		return data

class Controller(Utilities, CommonEventFunctions, Communication, Security):
	"""This module will help to create a simple GUI using wxPython without 
	having to learn how to use the complicated program.
	"""

	def __init__(self, debugging = False, best = False, oneInstance = False, allowBuildErrors = None, checkComplexity = True):
		"""Defines the internal variables needed to run.

		debugging (bool) - Determiens if debugging information is given to the user
			- If True: The cmd window will appear and show debugging information. Also closes with [ctrl]+[c]
			- If False: No cmd or logfile will be used.
			- If string: The pathway to a log file that will record debugging information

		best (bool) - Determiens how much work is put into visuals (NOT WORKING YET)
			- If True: The app will try to use the best visual system if more than one is available

		oneInstance (bool) - Determines if the user can run more than one instance at a time of this gui or not
			- If True: Only one instance can be ran at a time
			- If True: Multiple instances can be ran at the same time

		allowBuildErrors (bool) - Determines if, when using a with statement, errors created during build-time are acceptable
			- If True: Build-time errors will not prevent the GUI from finishing the build process
			- If False: Build-time errors will end the with statement, and the program will continue past it
			- If None: Build-time errors will end the program

		Example Input: Controller()
		Example Input: Controller(debugging = True)
		Example Input: Controller(debugging = "log.txt")  
		Example Input: Controller(oneInstance = True)
		"""
		super(Controller, self).__init__()

		#Initialize Inherited classes
		Utilities.__init__(self)
		CommonEventFunctions.__init__(self)
		Communication.__init__(self)
		Security.__init__(self)

		#Setup Internal Variables
		self.labelCatalogue = {} #A dictionary that contains all the windows made for the gui. {windowLabel: myFrame}
		self.labelCatalogueOrder = [] #A list of what order things were added to the label catalogue. [windowLabel 1, windowLabel 2]
		self.unnamedList = [] #A list of the windows created without labels
		self.oneInstance = oneInstance #Allows the user to run only one instance of this gui at a time
		self.allowBuildErrors = allowBuildErrors
		self.nestingAddress = []
		self.nested = True #Removes any warnings that may come up
		self.checkComplexity = checkComplexity

		#Record Address
		self.setAddressValue([id(self)], {None: self})

		#Create the wx app object
		self.app = MyApp(parent = self)

	def __str__(self):
		"""Gives diagnostic information on the GUI when it is printed out."""
		global nestingCatalogue

		output = "Controller()\n-- id: {}\n".format(id(self))
		# windowsList = [item for item in self.labelCatalogue.values() if isinstance(item, handle_Window)]
		windowsList = self.getNested(handle_Window)
		if (len(windowsList) + len(self.unnamedList) != 0):
			output += "-- windows: {}\n".format(len(windowsList) + len(self.unnamedList))
		if (len(nestingCatalogue) != 0):
			output += "-- nesting catalogue: {}\n".format(nestingCatalogue)

		return output

	def __repr__(self):
		representation = "Controller(id = {})".format(id(self))
		return representation

	def __enter__(self):
		"""Allows the user to use a with statement to build the GUI."""

		return self

	def __exit__(self, exc_type, exc_value, traceback):
		"""Allows the user to use a with statement to build the GUI."""

		#Error handling
		if (traceback != None):
			print(exc_type, exc_value)

			if (self.allowBuildErrors == None):
				return False
			elif (not self.allowBuildErrors):
				return True

		self.finish()

	def __len__(self):
		"""Returns the number of immediate nested elements.
		Does not include elements that those nested elements may have nested.
		"""

		catalogue = self.getAddressValue(self.nestingAddress + [id(self)])
		return len(catalogue) - 1

	def __iter__(self):
		"""Returns an iterator object that provides the nested objects."""
		
		nestedList = self.getNested()
		return Iterator(nestedList)

	def __getitem__(self, key):
		"""Allows the user to index the handle to get nested elements with labels."""

		return self.get(key)

	def __setitem__(self, key, value):
		"""Allows the user to index the handle to get nested elements with labels."""

		self.labelCatalogue[key] = value

	def __delitem__(self, key):
		"""Allows the user to index the handle to get nested elements with labels."""

		del self.labelCatalogue[key]

	def get(self, itemLabel, includeUnnamed = True, checkNested = True, typeList = None):
		"""Searches the label catalogue for the requested object.

		itemLabel (any) - What the object is labled as in the catalogue
			- If slice: objects will be returned from between the given spots 

		Example Input: get(0)
		Example Input: get(1.1)
		Example Input: get("text")

		Example Input: get(slice(None, None, None))
		Example Input: get(slice(2, "text", None))

		Example Input: get("text", checkNested = True)
		Example Input: get("text", includeUnnamed = False)
		Example Input: get("text", typeList = [handle_WidgetTable])
		"""

		def nestCheck(itemList, itemLabel):
			"""Makes sure everything is nested."""

			answer = None
			for item in itemList:
				#Skip Widgets
				if (not isinstance(item, handle_Widget_Base)):
					checkSubThings(item)

					answer = nestCheck(item[:], itemLabel)
					if (answer != None):
						return answer
				else:
					if (itemLabel == item.label):
						return item
			return answer

		def checkType(handleList):
			"""Makes sure only the instance typoes teh user wants are in the return list."""
			nonlocal typeList

			answer = []
			if (typeList != None):
				if ((not isinstance(typeList, list)), (not isinstance(typeList, tuple))):
					typeList = [typeList]
				if (len(typeList) != 0):
					for item in handleList:
						if (isinstance(item, typeList)):
							answer.append(item)
				else:
					answer = handleList
			else:
				answer = handleList

			return answer

		#Account for indexing
		if (isinstance(itemLabel, slice)):
			if (itemLabel.step != None):
				raise FutureWarning("Add slice steps to get() for indexing {}".format(self.__repr__()))
			
			elif ((itemLabel.start != None) and (itemLabel.start not in self.labelCatalogue)):
				errorMessage = "There is no item labled {} in the label catalogue for {}".format(itemLabel.start, self.__repr__())
				raise KeyError(errorMessage)
			
			elif ((itemLabel.stop != None) and (itemLabel.stop not in self.labelCatalogue)):
				errorMessage = "There is no item labled {} in the label catalogue for {}".format(itemLabel.stop, self.__repr__())
				raise KeyError(errorMessage)

			handleList = []
			begin = False
			for item in self.labelCatalogueOrder:
				#Allow for slicing with non-integers
				if ((not begin) and ((itemLabel.start == None) or (self.labelCatalogue[item].label == itemLabel.start))):
					begin = True
				elif ((itemLabel.stop != None) and (self.labelCatalogue[item].label == itemLabel.stop)):
					break

				#Slice catalogue via creation date
				if (begin):
					handleList.append(self.labelCatalogue[item])

			if (includeUnnamed):
				for item in self.unnamedList:
					handleList.append(item)

			handleList = checkType(handleList)

			return handleList

		elif (itemLabel not in self.labelCatalogue):
			if (checkNested):
				answer = nestCheck(self[:], itemLabel)
				answer = checkType(answer)
				if (answer != None):
					return answer

			errorMessage = "There is no item labled {} in the label catalogue for {}".format(itemLabel, self.__repr__())
			raise KeyError(errorMessage)

		else:
			return self.labelCatalogue[itemLabel]
	
	#Main Objects
	def addWindow(self, label = None, title = "", size = wx.DefaultSize, position = wx.DefaultPosition, panel = True, autoSize = True,
		tabTraversal = True, stayOnTop = False, floatOnParent = False, endProgram = True,
		resize = True, minimize = True, maximize = True, close = True, icon = None, internal = False, topBar = True,

		initFunction = None, initFunctionArgs = None, initFunctionKwargs = None, 
		delFunction = None, delFunctionArgs = None, delFunctionKwargs = None, 
		idleFunction = None, idleFunctionArgs = None, idleFunctionKwargs = None, 

		parent = None, handle = None):
		"""Creates a new window.
		Returns the index number of the created window.

		label (any) - What this is catalogued as
		title (str)   - The text that appears on top of the window
		xSize (int)   - The width of the window
		ySize (int)   - The height of the window
		
		initFunction (str)       - The function that is ran when the panel first appears
		initFunctionArgs (any)   - The arguments for 'initFunction'
		initFunctionKwargs (any) - The keyword arguments for 'initFunction'function

		delFunction (str)       - The function that is ran when the user tries to close the panel. Can be used to interrup closing
		delFunctionArgs (any)   - The arguments for 'delFunction'
		delFunctionKwargs (any) - The keyword arguments for 'delFunction'function

		idleFunction (str)       - The function that is ran when the window is idle
		idleFunctionArgs (any)   - The arguments for 'idleFunction'
		idleFunctionKwargs (any) - The keyword arguments for 'idleFunction'function
		
		tabTraversal (bool) - If True: Hitting the Tab key will move the selected widget to the next one
		topBar (bool)       - An override for 'minimize', 'maximize', and 'close'.
			- If None: Will not override 'minimize', 'maximize', and 'close'.
			- If True: The top of the window will have a minimize, maximize, and close button.
			- If False: The top of the window will not have a minimize, maximize, and close button.
		panel (bool)        - If True: All content within the window will be nested inside a main panel
		autoSize (bool)     - If True: The window will determine the best size for itself
		icon (str)          - The file path to the icon for the window
			If None: No icon will be shown
		internal (bool)     - If True: The icon provided is an internal icon, not an external file
		
		Example Input: addWindow()
		Example Input: addWindow(0)
		Example Input: addWindow(0, title = "Example")
		"""

		handle = handle_Window()
		handle.build(locals())

		return handle

	#Logistic Functions
	def finish(self):
		"""Run this when the GUI is finished."""
		global nestingCatalogue

		def nestCheck(catalogue):
			"""Makes sure everything is nested."""

			# valueList = [item for item in catalogue.values() if isinstance(item, dict)]
			
			for item in catalogue.values():
				#Skip Widgets
				if (not isinstance(item, handle_Widget_Base)):
					if (isinstance(item, dict)):
						nestCheck(item)
					else:
						if (not item.nested):
							warnings.warn("{} not nested".format(item.__repr__()), Warning, stacklevel = 2)

		#Make sure all things are nested
		nestCheck(nestingCatalogue)
		
		#Take care of last minute things
		# windowsList = [item for item in self.labelCatalogue.values() if isinstance(item, handle_Window)]
		windowsList = self.getNested(include = handle_Window)
		for myFrame in windowsList + self.unnamedList:
			if (self.checkComplexity):
				#Make sure GUI is not too complex
				if (myFrame.complexity_total > myFrame.complexity_max):
					errorMessage = "{} is too complex; {}/{}".format(myFrame.__repr__(), myFrame.complexity_total, myFrame.complexity_max)
					raise RuntimeError(errorMessage)

			#Check for any window key bindings that need to happen
			if (len(myFrame.keyPressQueue) > 0):
				#Bind each key event to the window
				acceleratorTableQueue = []
				### To Do: This does not currently work with more than 1 key. Find out what is wrong. ###
				for handle, queue in myFrame.keyPressQueue.items():
					for key, contents in queue.items():

						#Bind the keys to the window
						### This is likely the issue. The event seems to be 'overwritten' by the next key ###
						myId = handle.thing.GetId()
						# myFrame.Bind(wx.EVT_MENU, contents[0], id=myId)
						# myFrame.Bind(type, lambda event: handler(event, *args, **kwargs), instance)
						# print(contents[0])
						# myFrame.Bind(wx.EVT_MENU, lambda event: contents[0](event), id=eventId)
						# myFrame.Bind(wx.EVT_MENU, lambda event: contents[0](event), id = myId)
						myFrame.betterBind(wx.EVT_MENU, myFrame.thing, contents[0], contents[1], contents[2], mode = 2)
						# asciiValue = myFrame.keyBind(key, thing, contents[0], myFunctionArgsList = contents[1], myFunctionKwargsList = contents[2], event = wx.EVT_MENU, myId = myId)

						#Add to accelerator Table
						acceleratorTableQueue.append((wx.ACCEL_CTRL, 83, myId))

				acceleratorTable = wx.AcceleratorTable(acceleratorTableQueue)
				myFrame.thing.SetAcceleratorTable(acceleratorTable)

			#Run any final functions
			for item in myFrame.finalFunctionList:
				myFunctionList, myFunctionArgsList, myFunctionKwargsList = item

				if (item[0] != None):
					myFunctionList, myFunctionArgsList, myFunctionKwargsList = self.formatFunctionInputList(item[0], item[1], item[2])
					
					#Run each function
					for i, myFunction in enumerate(myFunctionList):
						#Skip empty functions
						if (myFunction != None):
							myFunctionEvaluated, myFunctionArgs, myFunctionKwargs = self.formatFunctionInput(i, myFunctionList, myFunctionArgsList, myFunctionKwargsList)
							
							#Has both args and kwargs
							if ((myFunctionKwargs != None) and (myFunctionArgs != None)):
								myFunctionEvaluated(*myFunctionArgs, **myFunctionKwargs)

							#Has args, but not kwargs
							elif (myFunctionArgs != None):
								myFunctionEvaluated(*myFunctionArgs)

							#Has kwargs, but not args
							elif (myFunctionKwargs != None):
								myFunctionEvaluated(**myFunctionKwargs)

							#Has neither args nor kwargs
							else:
								myFunctionEvaluated()

			#Make sure that the window is up to date
			myFrame.updateWindow()

		#Start the GUI
		self.app.MainLoop()

	def exit(self):
		"""Close the GUI and clean up allocated resources.

		Example Input: exit()
		"""

		self.onExit(None)

	#Logistic
	def switchWindow(self, whichFrom, whichTo, hideFrom = True):
		"""Switches to another window.

		whichFrom (int) - The index number of the current window
		whichTo (int)   - The index number of the next window
		autoSize (bool) - If True: the window size will be changed to fit the sizers within
						  If False: the window size will be what was defined when it was initially created
						  If None: the internal autosize state will be used
		hideFrom (bool) - Whether to hide the current window or close it

		Example Input: switchWindow(0, 1)
		Example Input: switchWindow(0, 1, hideFrom = False)
		"""

		frameFrom = self.getWindow(whichFrom)
		frameTo = self.getWindow(whichTo)

		#Show next window
		frameTo.showWindow()

		#Hide or close current window
		if (hideFrom):
			frameFrom.hideWindow()
		# else:
		# 	frameFrom.closeWindow()

	def onSwitchWindow(self, event, *args, **kwargs):
		"""Event function for switchWindow()."""

		self.switchWindow(*args, **kwargs)			
		event.Skip()

	#Etc
	def enableToolTips(self, enabled = True):
		"""Globally enables tool tips

		enabled (bool) - If tool tips should be enabled

		Example Input: enableToolTips()
		Example Input: enableToolTips(enabled = False)
		"""

		wx.ToolTip.Enable(enabled)

	def disableToolTips(self, disabled = True):
		"""Globally disables tool tips

		disabled (bool) - If tool tips should be disabled

		Example Input: disableToolTips()
		Example Input: disableToolTips(disabled = False)
		"""

		self.enableToolTips(not disabled)

	def toggleToolTips(self, enabled = None):
		"""Globally enables tool tips if they are disabled, and disables them if they are enabled.

		enabled (bool) - If tool tips should be enabled

		Example Input: enableToolTips()
		Example Input: enableToolTips(enabled = True)
		Example Input: enableToolTips(enabled = False)
		"""

		if (enabled != None):
			self.enableToolTips(enabled)
		else:
			if (wx.ToolTip.IsEnabled()):
				self.enableToolTips(False)
			else:
				self.enableToolTips(True)

	def centerWindowAll(self, *args, **kwargs):
		"""Centers all the windows on the screen.

		Example Input: centerWindowAll()
		"""

		for window in self.getWindow():
			window.centerWindow(*args, **kwargs)

	def logPrint(self):
		"""Logs print statements and errors in a text file.
		Acts as a middle man between the user and the intended function.

		Example Input: logPrint()
		"""

		def newStdout_write(*args, fileName = "cmd_log.log", timestamp = True, **kwargs):
			"""Overrides the print function to also log the information printed.

			fileName (str)   - The filename for the log
			timestamp (bool) - Determines if the timestamp is added to the log
			"""
			nonlocal self

			#Write the information to a file
			with open(fileName, "a") as fileHandle:

				if (timestamp):
					content = "{} --- ".format(time.strftime("%Y/%m/%d %H:%M:%S", time.localtime()))
				else:
					content = ""

				content += " " .join([str(item) for item in args])
				fileHandle.write(content)
				fileHandle.write("\n")

			#Run the normal print function
			return self.old_stdout(*args)

		def newStderr_write(*args, fileName = "error_log.log", timestamp = True, **kwargs):
			"""Overrides the stderr function to also log the error information.

			fileName (str)   - The filename for the log
			timestamp (bool) - Determines if the timestamp is added to the log
			"""
			nonlocal self

			#Write the information to a file
			with open(fileName, "a") as fileHandle:

				if (timestamp):
					content = "{} --- ".format(time.strftime("%Y/%m/%d %H:%M:%S", time.localtime()))
				else:
					content = ""

				content += " " .join([str(item) for item in args])
				fileHandle.write(content)
				fileHandle.write("\n")

			#Run the normal stderr function
			return self.old_stderr(*args)

		#Handle print
		self.old_stdout = sys.stdout.write
		sys.stdout.write = newStdout_write

		#Handle errors
		self.old_stderr = sys.stderr.write
		sys.stderr.write = newStderr_write

	#Overloads - handle_Window
	def setWindowSize(self, windowLabel, *args, **kwargs):
		"""Overload for setWindowSize in handle_Window()."""

		myFrame = self.getWindow(windowLabel)
		myFrame.setWindowSize(*args, **kwargs)

	def setMinimumFrameSize(self, windowLabel, *args, **kwargs):
		"""Overload for setMinimumFrameSize in handle_Window()."""

		myFrame = self.getWindow(windowLabel)
		myFrame.setMinimumFrameSize(*args, **kwargs)

	def setMaximumFrameSize(self, windowLabel, *args, **kwargs):
		"""Overload for setMaximumFrameSize in handle_Window()."""

		myFrame = self.getWindow(windowLabel)
		myFrame.setMaximumFrameSize(*args, **kwargs)

	def setAutoWindowSize(self, windowLabel, *args, **kwargs):
		"""Overload for setAutoWindowSize in handle_Window()."""

		myFrame = self.getWindow(windowLabel)
		myFrame.setAutoWindowSize(*args, **kwargs)

	def setWindowTitle(self, windowLabel, title, *args, **kwargs):
		"""Overload for setWindowTitle in handle_Window()."""

		myFrame = self.getWindow(windowLabel)
		myFrame.setWindowTitle(*args, **kwargs)

	def centerWindow(self, windowLabel, *args, **kwargs):
		"""Overload for centerWindow in handle_Window()."""

		myFrame = self.getWindow(windowLabel)
		myFrame.centerWindow(*args, **kwargs)

	def showWindow(self, windowLabel, *args, **kwargs):
		"""Overload for showWindow in handle_Window()."""

		myFrame = self.getWindow(windowLabel)
		myFrame.showWindow(*args, **kwargs)

	def onShowWindow(self, event, windowLabel, *args, **kwargs):
		"""Overload for onShowWindow in handle_Window()."""

		myFrame = self.getWindow(windowLabel)
		myFrame.onShowWindow(event, *args, **kwargs)

	def showWindowCheck(self, windowLabel, *args, **kwargs):
		"""Overload for showWindowCheck in handle_Window()."""

		myFrame = self.getWindow(windowLabel)
		shown = myFrame.showWindowCheck(*args, **kwargs)
		return shown

	def hideWindow(self, windowLabel, *args, **kwargs):
		"""Overload for hideWindow in handle_Window()."""

		myFrame = self.getWindow(windowLabel)
		myFrame.hideWindow(*args, **kwargs)

	def onHideWindow(self, event, windowLabel, *args, **kwargs):
		"""Overload for onHideWindow in handle_Window()."""

		myFrame = self.getWindow(windowLabel)
		myFrame.onHideWindow(event, *args, **kwargs)

	def typicalWindowSetup(self, windowLabel, *args, **kwargs):
		"""Overload for typicalWindowSetup in handle_Window()."""

		myFrame = self.getWindow(windowLabel)
		myFrame.typicalWindowSetup(*args, **kwargs)
		
	def closeWindow(self, windowLabel, *args, **kwargs):
		"""Overload for closeWindow in handle_Window()."""

		myFrame = self.getWindow(windowLabel)
		myFrame.closeWindow(*args, **kwargs)

	def onCloseWindow(self, event, windowLabel, *args, **kwargs):
		"""Overload for onCloseWindow in handle_Window()."""

		myFrame = self.getWindow(windowLabel)
		myFrame.onCloseWindow(event, *args, **kwargs)

	def addSizerBox(self, windowLabel, *args, **kwargs):
		"""Overload for addSizerBox in handle_Window()."""

		myFrame = self.getWindow(windowLabel)
		handle = myFrame.addSizerBox(*args, **kwargs)

		return handle

	def addSizerText(self, windowLabel, *args, **kwargs):
		"""Overload for addSizerText in handle_Window()."""

		myFrame = self.getWindow(windowLabel)
		handle = myFrame.addSizerText(*args, **kwargs)

		return handle

	def addSizerGrid(self, windowLabel, *args, **kwargs):
		"""Overload for addSizerGrid in handle_Window()."""

		myFrame = self.getWindow(windowLabel)
		handle = myFrame.addSizerGrid(*args, **kwargs)

		return handle

	def addSizerGridFlex(self, windowLabel, *args, **kwargs):
		"""Overload for addSizerGridFlex in handle_Window()."""

		myFrame = self.getWindow(windowLabel)
		handle = myFrame.addSizerGridFlex(*args, **kwargs)

		return handle

	def addSizerGridBag(self, windowLabel, *args, **kwargs):
		"""Overload for addSizerGridBag in handle_Window()."""

		myFrame = self.getWindow(windowLabel)
		handle = myFrame.addSizerGridBag(*args, **kwargs)

		return handle

	def addSizerWrap(self, windowLabel, *args, **kwargs):
		"""Overload for addSizerWrap in handle_Window()."""

		myFrame = self.getWindow(windowLabel)
		handle = myFrame.addSizerWrap(*args, **kwargs)

		return handle

	def nestSizerInSizer(self, windowLabel, *args, **kwargs):
		"""Overload for growFlexColumn in handle_Window()."""

		myFrame = self.getWindow(windowLabel)
		myFrame.nestSizerInSizer(*args, **kwargs)

	def growFlexColumn(self, windowLabel, *args, **kwargs):
		"""Overload for growFlexColumn in handle_Window()."""

		myFrame = self.getWindow(windowLabel)
		myFrame.growFlexColumn(*args, **kwargs)

	def growFlexRow(self, windowLabel, *args, **kwargs):
		"""Overload for growFlexRow in handle_Window()."""

		myFrame = self.getWindow(windowLabel)
		myFrame.growFlexRow(*args, **kwargs)

	def growFlexColumnAll(self, windowLabel, *args, **kwargs):
		"""Overload for growFlexColumnAll in handle_Window()."""

		myFrame = self.getWindow(windowLabel)
		myFrame.growFlexColumnAll(*args, **kwargs)

	def growFlexRowAll(self, windowLabel, *args, **kwargs):
		"""Overload for growFlexRowAll in handle_Window()."""

		myFrame = self.getWindow(windowLabel)
		myFrame.growFlexRowAll(*args, **kwargs)

	def addText(self, windowLabel, *args, **kwargs):
		"""Overload for addText in handle_Window()."""

		myFrame = self.getWindow(windowLabel)
		handle = myFrame.addText(*args, **kwargs)

		return handle

	def addHyperlink(self, windowLabel, *args, **kwargs):
		"""Overload for addHyperlink in handle_Window()."""

		myFrame = self.getWindow(windowLabel)
		handle = myFrame.addHyperlink(*args, **kwargs)

		return handle

	def addEmpty(self, windowLabel, *args, **kwargs):
		"""Overload for addEmpty in handle_Window()."""

		myFrame = self.getWindow(windowLabel)
		handle = myFrame.addEmpty(*args, **kwargs)

		return handle

	def addLine(self, windowLabel, *args, **kwargs):
		"""Overload for addLine in handle_Window()."""

		myFrame = self.getWindow(windowLabel)
		handle = myFrame.addLine(*args, **kwargs)

		return handle

	def addListDrop(self, windowLabel, *args, **kwargs):
		"""Overload for addListDrop in handle_Window()."""

		myFrame = self.getWindow(windowLabel)
		handle = myFrame.addListDrop(*args, **kwargs)

		return handle

	def addListFull(self, windowLabel, *args, **kwargs):
		"""Overload for addListFull in handle_Window()."""

		myFrame = self.getWindow(windowLabel)
		handle = myFrame.addListFull(*args, **kwargs)

		return handle

	def addSlider(self, windowLabel, *args, **kwargs):
		"""Overload for addSlider in handle_Window()."""

		myFrame = self.getWindow(windowLabel)
		handle = myFrame.addSlider(*args, **kwargs)

		return handle

	def addInputBox(self, windowLabel, *args, **kwargs):
		"""Overload for addInputBox in handle_Window()."""

		myFrame = self.getWindow(windowLabel)
		handle = myFrame.addInputBox(*args, **kwargs)

		return handle

	def addInputSearch(self, windowLabel, *args, **kwargs):
		"""Overload for addInputSearch in handle_Window()."""

		myFrame = self.getWindow(windowLabel)
		handle = myFrame.addInputSearch(*args, **kwargs)

		return handle

	def addInputSpinner(self, windowLabel, *args, **kwargs):
		"""Overload for addInputSpinner in handle_Window()."""

		myFrame = self.getWindow(windowLabel)
		handle = myFrame.addInputSpinner(*args, **kwargs)

		return handle

	def addButton(self, windowLabel, *args, **kwargs):
		"""Overload for addButton in handle_Window()."""

		myFrame = self.getWindow(windowLabel)
		handle = myFrame.addButton(*args, **kwargs)

		return handle

	def addButtonToggle(self, windowLabel, *args, **kwargs):
		"""Overload for addButtonToggle in handle_Window()."""

		myFrame = self.getWindow(windowLabel)
		handle = myFrame.addButtonToggle(*args, **kwargs)

		return handle

	def addButtonCheck(self, windowLabel, *args, **kwargs):
		"""Overload for addButtonCheck in handle_Window()."""

		myFrame = self.getWindow(windowLabel)
		handle = myFrame.addButtonCheck(*args, **kwargs)

		return handle

	def addCheckList(self, windowLabel, *args, **kwargs):
		"""Overload for addCheckList in handle_Window()."""

		myFrame = self.getWindow(windowLabel)
		handle = myFrame.addCheckList(*args, **kwargs)

		return handle

	def addButtonRadio(self, windowLabel, *args, **kwargs):
		"""Overload for addButtonRadio in handle_Window()."""

		myFrame = self.getWindow(windowLabel)
		handle = myFrame.addButtonRadio(*args, **kwargs)

		return handle

	def addButtonRadioBox(self, windowLabel, *args, **kwargs):
		"""Overload for addButtonRadioBox in handle_Window()."""

		myFrame = self.getWindow(windowLabel)
		handle = myFrame.addButtonRadioBox(*args, **kwargs)

		return handle

	def addButtonImage(self, windowLabel, *args, **kwargs):
		"""Overload for addButtonImage in handle_Window()."""

		myFrame = self.getWindow(windowLabel)
		handle = myFrame.addButtonImage(*args, **kwargs)

		return handle

	def addImage(self, windowLabel, *args, **kwargs):
		"""Overload for addImage in handle_Window()."""

		myFrame = self.getWindow(windowLabel)
		handle = myFrame.addImage(*args, **kwargs)

		return handle

	def addProgressBar(self, windowLabel, *args, **kwargs):
		"""Overload for addProgressBar in handle_Window()."""

		myFrame = self.getWindow(windowLabel)
		handle = myFrame.addProgressBar(*args, **kwargs)

		return handle

	def addPickerColor(self, windowLabel, *args, **kwargs):
		"""Overload for addPickerColor in handle_Window()."""

		myFrame = self.getWindow(windowLabel)
		handle = myFrame.addPickerColor(*args, **kwargs)

		return handle

	def addPickerFont(self, windowLabel, *args, **kwargs):
		"""Overload for addPickerFont in handle_Window()."""

		myFrame = self.getWindow(windowLabel)
		handle = myFrame.addPickerFont(*args, **kwargs)

		return handle

	def addPickerFile(self, windowLabel, *args, **kwargs):
		"""Overload for addPickerFile in handle_Window()."""

		myFrame = self.getWindow(windowLabel)
		handle = myFrame.addPickerFile(*args, **kwargs)

		return handle

	def addPickerFileWindow(self, windowLabel, *args, **kwargs):
		"""Overload for addPickerFileWindow in handle_Window()."""

		myFrame = self.getWindow(windowLabel)
		handle = myFrame.addPickerFileWindow(*args, **kwargs)

		return handle

	def addPickerTime(self, windowLabel, *args, **kwargs):
		"""Overload for addPickerTime in handle_Window()."""

		myFrame = self.getWindow(windowLabel)
		handle = myFrame.addPickerTime(*args, **kwargs)

		return handle

	def addPickerDate(self, windowLabel, *args, **kwargs):
		"""Overload for addPickerDate in handle_Window()."""

		myFrame = self.getWindow(windowLabel)
		handle = myFrame.addPickerDate(*args, **kwargs)

		return handle

	def addPickerDateWindow(self, windowLabel, *args, **kwargs):
		"""Overload for addPickerDateWindow in handle_Window()."""

		myFrame = self.getWindow(windowLabel)
		handle = myFrame.addPickerDateWindow(*args, **kwargs)

		return handle

def main_1():
	"""The program controller. """

	gui = build()
	myFrame = gui.addWindow(title = "created")#, panel = None)
	mySizer_1 = myFrame.addSizerGrid(rows = 3, columns = 2)
	mySizer_1.addText("Lorem")
	mySizer_1.addText("Ipsum")
	mySizer_1.addText("Dolor")
	mySizer_1.addText("Sit")

	mySizer_2 = myFrame.addSizerGrid(rows = 3, columns = 2)
	mySizer_2.addText("Amet")
	mySizer_1.nest(mySizer_2) #Nest sizers with handler function

	myFrame.showWindow()

	print(gui)
	print("GUI Finished")
	gui.finish()

def main_2():
	"""The program controller. """

	gui = build()
	myFrame = gui.addWindow(0, title = "created")#, panel = None)
	mySizer_1 = myFrame.addSizerGrid(0, rows = 3, columns = 2)
	mySizer_1.addText("Lorem")
	mySizer_1.addText("Ipsum")
	mySizer_1.addText("Dolor")
	mySizer_1.addText("Sit")

	mySizer_2 = myFrame.addSizerGrid(1, rows = 3, columns = 2)
	myWidget = mySizer_2.addText("Amet")
	mySizer_1 + mySizer_2 #Nest sizers with handler addition

	print(len(gui))
	print(len(myFrame))
	print(len(mySizer_1))
	print(len(myWidget))

	gui.showWindow(0)

	print(gui)
	print("GUI Finished")
	gui.finish()

def main_3():
	"""The program controller. """

	gui = build()
	myFrame = gui.addWindow(0, title = "created")#, panel = None)
	mySizer_1 = myFrame.addSizerGrid(0, rows = 3, columns = 2)
	mySizer_1.addText("Lorem")
	mySizer_1.addText("Ipsum")
	mySizer_1.addText("Dolor")
	mySizer_1.addText("Sit")

	mySizer_2 = mySizer_1.addSizerGrid(1, rows = 3, columns = 2) #Nest sizers here
	myWidget = mySizer_2.addText("Amet")

	for item in myFrame:
		print("@1", item)

	for item in mySizer_1:
		print("@2", item)

	for item in myWidget:
		print("@3", item)

	for item in gui:
		print("@4", item)

	gui.showWindow(0)

	print(gui)
	print("GUI Finished")
	gui.finish()

def main_4():
	"""The program controller. """

	gui = build()
	myFrame = gui.addWindow(0, title = "created")#, panel = None)
	myFrame.addSizerGrid(0, rows = 3, columns = 2)
	myFrame.addText(0, "Lorem")
	myFrame.addText(0, "Ipsum")
	myFrame.addText(0, "Dolor")
	myFrame.addText(0, "Sit")

	mySizer = myFrame.addSizerGrid(1, rows = 3, columns = 2)
	myWidget = myFrame.addText(1, label = "text", text = "Amet")
	myFrame.nestSizerInSizer(1, 0) #Nest sizers with labels

	print("@1", myWidget in myFrame)
	print("@2", mySizer in myFrame)
	print("@3", mySizer not in myFrame)

	print("@4", myFrame[0])
	try: 
		myFrame[2]
		print("@5 Wrong index did NOT work")
	except: 
		print("@5 Wrong index worked too")

	print("@6", myFrame[:])
	print("@7", myFrame[:1])
	print("@8", mySizer[:])
	print("@9", mySizer["text":])
	try:
		myFrame[:2]
		print("@10 Wrong index slice did NOT work")
	except: 
		print("@10 Wrong index slice worked too")

	gui.showWindow(0)

	print(gui)
	print("GUI Finished")
	gui.finish()

def main_5():
	"""The program controller. """

	gui = build()
	myFrame = gui.addWindow(0, title = "created")#, panel = None)
	mySizer_1 = myFrame.addSizerGrid(0, rows = 3, columns = 2)
	myFrame.addText(0, "Lorem")
	myFrame.addText(0, "Ipsum")
	myFrame.addText(0, "Dolor")
	myFrame.addText(0, "Sit")

	mySizer_2 = myFrame.addSizerGrid(1, rows = 3, columns = 2)
	myFrame.addText(1, "Amet")
	myFrame.nest(mySizer_2, mySizer_1) #Nest sizers with two handles and a function

	gui.showWindow(0)

	print(gui)
	print("GUI Finished")
	gui.finish()

def main_6():
	"""The program controller. """

	with build() as gui:
		with gui.addWindow(0, title = "created") as myFrame:
			with myFrame.addSizerGrid(0, rows = 3, columns = 2) as mySizer_1:
				mySizer_1.addText("Lorem")
				mySizer_1.addText("Ipsum")
				mySizer_1.addText("Dolor")
				mySizer_1.addText("Sit")
				with mySizer_1.addSizerGrid(1, rows = 3, columns = 2) as mySizer_2: #Nest sizers here
					mySizer_2.addText("Amet")

		gui.showWindow(0)

		print(gui)
		print("GUI Finished")

def main_7():
	"""The program controller. """

	with build() as gui:
		with gui.addWindow(title = "created") as myFrame:
			with myFrame.addSizerGrid(0, rows = 3, columns = 2) as mySizer_1:
				mySizer_1.addText("Lorem")
				mySizer_1.addText("Ipsum")
				mySizer_1.addText("Dolor")
				mySizer_1.addText("Sit")
				with myFrame.addSizerGrid(1, rows = 3, columns = 2) as mySizer_2: #Nest sizers automatically
					mySizer_2.addText("Amet")

			myFrame.showWindow()

		print(gui)
		print("GUI Finished")

def main_8():
	"""The program controller. """

	gui = build()
	gui.addWindow(0, title = "created")#, panel = None)
	gui.addSizerGrid(0, 0, rows = 3, columns = 2)
	gui.addText(0, 0, "Lorem")
	gui.addText(0, 0, "Ipsum")
	gui.addText(0, 0, "Dolor")
	gui.addText(0, 0, "Sit")

	gui.addSizerGrid(0, 1, rows = 3, columns = 2)
	gui.addText(0, 1, "Amet")
	gui.nestSizerInSizer(0, 1, 0) #Nest sizers with two handles and a function

	gui.showWindow(0)

	print(gui)
	print("GUI Finished")
	gui.finish()

def main_9():
	"""The program controller. """

	with build() as gui:
		with gui.addWindow(title = "created") as myFrame:
			with myFrame.addSizerGrid(rows = 12, columns = 3, label = "mySizer") as mySizer:
				mySizer.addText(text = "Lorem", label = "myText")
				mySizer.addEmpty(label = "myEmpty")
				mySizer.addLine(label = "myLine")
				mySizer.addListDrop(choices = [1, 2, 3], label = "myListDrop")
				mySizer.addListFull(choices = [1, 2, 3], label = "myListFull")
				mySizer.addSlider(label = "mySlider")
				mySizer.addInputBox(label = "myInputBox")
				mySizer.addInputSearch(label = "myInputSearch")
				mySizer.addInputSpinner(label = "myInputSpinner")
				mySizer.addButton(label = "myButton")
				mySizer.addButtonToggle(label = "myButtonToggle")
				mySizer.addButtonCheck(label = "myButtonCheck")
				mySizer.addButtonRadio(label = "myButtonRadio")
				mySizer.addButtonRadioBox(label = "myButtonRadioBox")
				mySizer.addButtonImage(label = "myButtonImage")
				mySizer.addImage(label = "myImage")
				mySizer.addProgressBar(myInitial = 50, label = "myProgressBar")
				mySizer.addPickerColor(label = "myPickerColor")
				mySizer.addPickerFont(label = "myPickerFont")
				mySizer.addPickerFile(label = "myPickerFile")
				mySizer.addPickerFileWindow(label = "myPickerFileWindow")
				mySizer.addPickerTime(label = "myPickerTime")
				mySizer.addPickerDate(label = "myPickerDate")
				mySizer.addPickerDateWindow(label = "myPickerDateWindow")
				mySizer.addHyperlink(text = "Dolor", label = "myHyperlink")
				mySizer.addCheckList(choices = [1, 2, 3], label = "myCheckList")
			myFrame.showWindow()

			print("@1 Values")
			for item in myFrame["mySizer"]:
				if item.label not in ["myEmpty", "myLine"]:
					print("--", item.label, item.getValue())

			print("@2 Lengths")
			for item in myFrame["mySizer"]:
				if item.label not in ["myEmpty", "myLine", "myPickerColor", "myPickerFont", "myPickerTime", "myPickerDate", "myPickerDateWindow"]:
					print("--", item.label, len(item))

		print(gui)
		print("GUI Finished")

def main_10():
	"""The program controller. """

	gui = build()
	myFrame = gui.addWindow(title = "created")#, panel = None)
	mySizer_1 = myFrame.addSizerGridFlex(rows = 3, columns = 1)
	mySizer_1.growFlexColumnAll()
	mySizer_1.growFlexRow(1)
	mySizer_1.addText("Lorem")

	mySplitter_1 = mySizer_1.addSplitterDouble(minimumSize = 600)
	mySizer_2, mySizer_3 = mySplitter_1.getSizers()
	mySizer_2.addText("Ipsum")
	mySizer_3.addText("Dolor")

	mySplitter_2a = mySizer_2.addSplitterDouble(minimumSize = 100)
	mySizer_4a, mySizer_5a = mySplitter_2a.getSizers()
	mySizer_4a.addText("Sit")
	mySizer_5a.addText("Amet")

	mySplitter_2ab = mySizer_3.addSplitterDouble(minimumSize = 100)
	mySizer_4ab, mySizer_5ab = mySplitter_2ab.getSizers()
	mySizer_4ab.addText("Sit")
	mySizer_5ab.addText("Amet")

	mySplitter_2b = mySizer_3.addSplitterDouble(minimumSize = 100)
	mySizer_4b, mySizer_5b = mySplitter_2b.getSizers()
	mySizer_4b.addText("Sit")
	mySizer_5b.addText("Amet")

	myFrame.showWindow()
	print("GUI Finished")
	gui.finish()

def main_11():
	"""The program controller. """

	gui = build(checkComplexity = False)
	# myFrame = gui.addWindow(title = "created")#, panel = None)
	myFrame = gui.addWindow(0, title = "created")#, panel = None)
	mySizer_0 = myFrame.addSizerGridFlex(rows = 6, columns = 1)
	mySizer_0.growFlexColumnAll()
	mySizer_0.growFlexRow(1)
	mySizer_0.addText("Lorem")

	mySplitter_1 = mySizer_0.addSplitterQuad()
	mySizer_1a, mySizer_1b, mySizer_1c, mySizer_1d = mySplitter_1.getSizers()
	mySizer_1a.addText("1")
	mySizer_1b.addText("2")
	mySizer_1c.addText("3")
	mySizer_1d.addText("4")

	# mySplitter_4a = mySizer_0.addSplitterPoly(3)
	# mySizer_10a, mySizer_11a, mySizer_12a = mySplitter_4a.getSizers()
	# mySizer_10a.addText("a")
	# mySizer_11a.addText("b")
	# mySizer_12a.addText("c")

	mySplitter_3 = mySizer_0.addSplitterDouble(minimumSize = 100)
	mySizer_3a, mySizer_3b = mySplitter_3.getSizers()
	mySizer_3a.addText("Ipsum")
	mySizer_3b.addText("Dolor")

	myFrame.showWindow()
	print("GUI Finished")
	gui.finish()

def main_12():
	"""The program controller. """

	gui = build(checkComplexity = False)
	myFrame = gui.addWindow(title = "created")#, panel = None)
	mySizer_0 = myFrame.addSizerGridFlex(rows = 6, columns = 1)
	mySizer_0.growFlexColumnAll()
	mySizer_0.growFlexRow(1)
	mySizer_0.addText("Lorem")

	mySizer_2, mySizer_3 = mySizer_0.addSplitterDouble(minimumSize = 600)
	# mySizer_2, mySizer_3 = mySplitter_1.getSizers()
	mySizer_2.addText("Ipsum")
	mySizer_3.addText("Dolor")

	mySizer_4a, mySizer_5 = mySizer_0.addSplitterDouble(minimumSize = 100, sizer_0 = {"type": "Grid", "rows": 3, "columns": 4}, panel_0 = {"border": "raised"}, panel_1 = {"border": "raised"})
	# mySizer_4a, mySizer_5 = mySplitter_2.getSizers()
	# mySizer_4a = mySizer_4.addSizerGrid(rows = 3, columns = 4)
	mySizer_4a.addText("Sit")
	mySizer_4a.addText("Sit")
	mySizer_4a.addText("Sit")
	mySizer_4a.addText("Sit")
	mySizer_4a.addText("Sit")
	mySizer_4a.addText("Sit")
	mySizer_4a.addText("Sit")
	mySizer_4a.addText("Sit")
	mySizer_4a.addText("Sit")
	mySizer_4a.addText("Sit")
	mySizer_4a.addText("Sit")
	mySizer_5.addText("Amet")
	mySizer_5.addText("Amet")

	myFrame.showWindow()
	print("GUI Finished")
	gui.finish()

def main_13():
	"""The program controller. """

	gui = build(checkComplexity = False)
	myFrame = gui.addWindow(title = "created")#, panel = None)
	mySizer_0 = myFrame.addSizerGridFlex(rows = 6, columns = 6)
	mySizer_0.growFlexColumnAll()
	mySizer_0.growFlexRow(1)

	mySizer_0.addTable(rows = 4, columns = 3)

	myMenu = myFrame.addMenu(text = "File")
	myMenu.addMenuItem("Save")
	myMenu.addMenuSeparator()

	mySubMenu = myMenu.addMenuSub("Sub Menu")
	mySubMenu.addMenuItem("1")
	mySubMenu.addMenuItem("2")

	mySubSubMenu = mySubMenu.addMenuSub("Sub Sub Menu")
	mySubSubMenu.addMenuItem("3")
	mySubSubMenu.addMenuSeparator()
	mySubSubMenu.addMenuItem("4")

	myFrame.showWindow()
	print("GUI Finished")
	gui.finish()

def main_14():
	"""The program controller. """

	gui = build()
	myFrame = gui.addWindow(title = "created")#, panel = None)
	mySizer_1 = myFrame.addSizerGridFlex(rows = 100, columns = 1)
	mySizer_1.growFlexColumnAll()
	mySizer_1.growFlexRow(1)
	mySizer_1.addText("Lorem")

	with mySizer_1.addSizerBox() as mySizer:
		mySizer.addText("Ipsum")

	mySizer_1.addSplitterDouble(minimumSize = 200, sizer_1 = {"type": "grid", "rows": 3, "columns": 2}, panel_0 = {"border": "raised"}, panel_1 = {"border": "raised"})
	mySizer_1.addSplitterDouble(minimumSize = 200, sizer_1 = {"type": "grid", "rows": 3, "columns": 2}, panel_0 = {"border": "raised"}, panel_1 = {"border": "raised"})
	mySizer_1.addSplitterDouble(minimumSize = 200, sizer_1 = {"type": "grid", "rows": 3, "columns": 2}, panel_0 = {"border": "raised"}, panel_1 = {"border": "raised"})
	mySizer_1.addSplitterDouble(minimumSize = 200, sizer_1 = {"type": "grid", "rows": 3, "columns": 2}, panel_0 = {"border": "raised"}, panel_1 = {"border": "raised"})
	mySizer_1.addSplitterDouble(minimumSize = 200, sizer_1 = {"type": "grid", "rows": 3, "columns": 2}, panel_0 = {"border": "raised"}, panel_1 = {"border": "raised"})


	myFrame.showWindow()
	print("GUI Finished")
	gui.finish()

def main_15():
	"""The program controller. """

	gui = build()
	myFrame = gui.addWindow(title = "created")#, panel = None)
	mySizer_1 = myFrame.addSizerGridFlex(rows = 100, columns = 1)
	mySizer_1.growFlexColumnAll()
	mySizer_1.growFlexRow(1)
	mySizer_1.addText("Lorem")

	with mySizer_1.addSizerBox(text = "Consectetur") as mySizer:
		with mySizer.addNotebook() as myNotebook:
			with myNotebook.addPage() as myPage:
				myPage.addText("Ipsum 1")
				myPage.addText("Ipsum 2")
		with mySizer.addNotebook() as myNotebook:
			with myNotebook.addPage() as myPage:
				myPage.addText("Dolor 1")
				myPage.addText("Dolor 2")
			with myNotebook.addPage() as myPage:
				myPage.addText("Amet 1")
				myPage.addText("Amet 2")
		with mySizer.addNotebook() as myNotebook:
			with myNotebook.addPage() as myPage:
				myPage.addText("Sit 1")
				myPage.addText("Sit 2")

	myFrame.showWindow()
	print("GUI Finished")
	gui.finish()

def main_16():
	"""The program controller. """

	gui = build()
	myFrame = gui.addWindow(title = "created")#, panel = None)
	mySizer_1 = myFrame.addSizerGridFlex(rows = 100, columns = 1)
	mySizer_1.growFlexColumnAll()
	mySizer_1.growFlexRow(1)
	mySizer_1.addText("Lorem")

	with myFrame.addPopupMenu() as myPopupMenu:
		myPopupMenu.addMenuItem("Save")
		myPopupMenu.addMenuSeparator()
		myPopupMenu.addMenuItem("Load")

		with myPopupMenu.addMenuSub("Sub Menu") as mySubMenu:
			mySubMenu.addMenuItem("1")
			mySubMenu.addMenuItem("2")

			with mySubMenu.addMenuSub("Sub Sub Menu") as mySubSubMenu:
				mySubSubMenu.addMenuItem("3")
				mySubSubMenu.addMenuSeparator()
				mySubSubMenu.addMenuItem("4")

	myFrame.showWindow()
	print("GUI Finished")
	gui.finish()

def main_17():
	"""The program controller. """

	gui = build()
	myFrame = gui.addWindow(title = "created")#, panel = None)
	mySizer_1 = myFrame.addSizerGridFlex(rows = 100, columns = 1)
	mySizer_1.growFlexColumnAll()
	mySizer_1.growFlexRow(1)
	mySizer_1.addText("Lorem")

	mySizer_2, mySizer_3 = mySizer_1.addSplitterDouble(minimumSize = 10)

	with mySizer_2.addTable(rows = 4, columns = 3) as myTable:
		myTable.setFunction_rightClickCell(myFunction = myFrame.onShow, myFunctionArgs = "popupMenu")

	with myFrame.addPopupMenu(label = "popupMenu") as myPopupMenu:
		myPopupMenu.addMenuItem("Save", label = "save")
		myPopupMenu.addMenuSeparator(label = "separator")
		myPopupMenu.addMenuItem("Load", label = "load")

		# with myPopupMenu.addMenuSub("Sub Menu") as mySubMenu:
		# 	mySubMenu.addMenuItem("1")
		# 	mySubMenu.addMenuItem("2")

		# 	with mySubMenu.addMenuSub("Sub Sub Menu") as mySubSubMenu:
		# 		mySubSubMenu.addMenuItem("3")
		# 		mySubSubMenu.addMenuSeparator()
		# 		mySubSubMenu.addMenuItem("4")

	myFrame.showWindow()
	print("GUI Finished")
	gui.finish()

if __name__ == '__main__':
	main_17()
