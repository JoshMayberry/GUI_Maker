__version__ = "4.3.0"

#TO DO
# - Add File Drop: https://www.blog.pythonlibrary.org/2012/06/20/wxpython-introduction-to-drag-and-drop/
# - Add Wrap Sizer: https://www.blog.pythonlibrary.org/2014/01/22/wxpython-wrap-widgets-with-wrapsizer/
# - Look through these demos for more things: https://github.com/wxWidgets/Phoenix/tree/master/demo
# - Look through the menu examples: https://www.programcreek.com/python/example/44403/wx.EVT_FIND

# - Add handler indexing
#       ~ See Operation Table on: https://docs.python.org/3/library/stdtypes.html#typeiter

#IMPORT CONTROLS
##Here the user can turn on and off specific parts of the module, 
##which will reduce the overall size of a generated .exe.
##To do so, comment out the block of import statements
##WARNING: If you turn off a feature, make sure you dont try to use it.

#Import standard elements to interact with the computer
import os
import ast
import sys
import time
import math
import copy
import ctypes
import string
# import builtins

import typing #NoReturn, Union
import inspect
import warnings
import traceback
import functools


#Import wxPython elements to create GUI
import wx
import wx.adv
import wx.grid
import wx.lib.masked
import wx.lib.buttons
import wx.lib.dialogs
import wx.lib.agw.aui
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
import select
import socket
import serial
import netaddr
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
# import PIL.Image


#Import user-defined modules
# from .ExcelManipulator_6 import Excel #Used to make wxGrid objects interactable with excel


#Database Interaction
# from .DatabaseAPI_12 import Database


#Required Modules
##py -m pip install
	# wxPython
	# cx_Freeze
	# pyserial
	# netaddr

#Maybe Required Modules?
	# openpyxl
	# numpy
	# matplotlib
	# pillow
	# pycryptodomex
	# atexit
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

#User Access Variables
ethernetError = socket.error

#Controllers
def build(*args, **kwargs):
	"""Starts the GUI making process."""

	return Controller(*args, **kwargs)

#Iterators
class Iterator(object):
	"""Used by handle objects to iterate over their nested objects."""

	def __init__(self, data, filterNone = False):
		if (not isinstance(data, (list, dict))):
			data = data[:]

		self.data = data
		if (isinstance(self.data, dict)):
			self.order = list(self.data.keys())

			if (filterNone):
				self.order = [key for key in self.data.keys() if key != None]
			else:
				self.order = [key if key != None else "" for key in self.data.keys()]

			self.order.sort()

			self.order = [key if key != "" else None for key in self.order]

	def __iter__(self):
		return self

	def __next__(self):
		if (not isinstance(self.data, dict)):
			if not self.data:
				raise StopIteration

			return self.data.pop()
		else:
			if not self.order:
				raise StopIteration

			key = self.order.pop()
			return self.data[key]

#Event System
class Event(object):
	"""Used to create simple events.
	Modified code from spassig on https://stackoverflow.com/questions/1092531/event-system-in-python
	_________________________________________________________________________

	Example Use:
		class MyBroadcaster()
			def __init__():
				self.onChange = Event()

		theBroadcaster = MyBroadcaster()

		#Add listener to the event
		theBroadcaster.onChange += myFunction

		#Remove listener from the event
		theBroadcaster.onChange -= myFunction

		#Fire event
		theBroadcaster.onChange.fire()
	_________________________________________________________________________
	"""

	def __init__(self):
		self.__handlers = [] #(function, args, kwargs)

	def __iadd__(self, myFunction):
		answer = self.add(myFunction, myFunctionArgs = None, myFunctionKwargs = None)
		return answer

	def __isub__(self, myFunction):
		answer = self.sub(myFunction, myFunctionArgs = None, myFunctionKwargs = None)
		return answer

	def add(self, myFunction, myFunctionArgs = None, myFunctionKwargs = None):
		self.__handlers.append((myFunction, myFunctionArgs, myFunctionKwargs))
		return self

	def sub(self, myFunction, myFunctionArgs = None, myFunctionKwargs = None):
		self.__handlers.remove((myFunction, myFunctionArgs, myFunctionKwargs))
		return self

	def fire(self, *args, **kwargs):
		def setupFunction(myFunctionList, myFunctionArgsList, myFunctionKwargsList):
			"""Sets up a function to run."""
			nonlocal self, args, kwargs

			#Skip empty functions
			if (myFunctionList != None):
				myFunctionList, myFunctionArgsList, myFunctionKwargsList = Utilities.formatFunctionInputList(None, myFunctionList, myFunctionArgsList, myFunctionKwargsList)
				
				#Run each function
				for i, myFunction in enumerate(myFunctionList):
					#Skip empty functions
					if (myFunction != None):
						myFunctionEvaluated, myFunctionArgs, myFunctionKwargs = Utilities.formatFunctionInput(None, i, myFunctionList, myFunctionArgsList, myFunctionKwargsList)

						#Combine with args and kwargs provided by fire()
						if (myFunctionArgs != None):
							myFunctionArgsCombined = myFunctionArgs + [item for item in args]
						else:
							myFunctionArgsCombined = args

						if (myFunctionKwargs != None):
							myFunctionKwargsCombined = {**myFunctionKwargs, **kwargs}
						else:
							myFunctionKwargsCombined = {**kwargs}

						#Run function
						runFunction(myFunctionEvaluated, myFunctionArgsCombined, myFunctionKwargsCombined)

		def runFunction(myFunction, myFunctionArgs, myFunctionKwargs):
			"""Runs a function."""
			nonlocal self

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

		#########################################################

		for myFunction, myFunctionArgs, myFunctionKwargs in self.__handlers:
			setupFunction(myFunction, myFunctionArgs, myFunctionKwargs)

#Decorators
def wrap_showError(makeDialog = True, fileName = "error_log.log"):
	def decorator(function):
		@functools.wraps(function)
		def wrapper(*args, **kwargs):
			"""Shows an error that happens to the user.

			Example Usage: @GUI_Maker.wrap_showError()
			"""

			try:
				answer = function(*args, **kwargs)
			except SystemExit:
				sys.exit()
			except:
				answer = None

				#Get the error text
				error = traceback.format_exc()

				#Show Error on CMD
				print(error)

				#Log the error
				try:
					Utilities.logPrint(None, text = error, fileName = fileName)
				except:
					traceback.print_exc()

				#Display Error on GUI
				if (makeDialog):
					try:
						myDialog = handle_Window.makeDialogMessage(None, text = error, icon = "error", addOk = True)
						myDialog.show()
					except:
						traceback.print_exc()

			return answer
		return wrapper
	return decorator

def wrap_eventInit(eventName = "event"):
	def decorator(function):
		@functools.wraps(function)
		def wrapper(self, *args, **kwargs):
			"""Adds a function to the event handler for this object.

			Example Usage: @GUI_Maker.wrap_eventInit(eventName = "_event")
			"""

			#Ensure that an event object exists
			if (not hasattr(self, eventName)):
				setattr(self, eventName, Event())

			answer = function(self, *args, **kwargs)

			return answer
		return wrapper
	return decorator

def wrap_eventAdd(myFunction, eventName = "event"):
	def decorator(function):
		@functools.wraps(function)
		def wrapper(self, *args, **kwargs):
			"""Adds a function to the event handler for this object.

			Example Usage: @GUI_Maker.wrap_eventAdd(myFunction, eventName = "_event")
			"""

			#Ensure that an event object exists
			if (not hasattr(self, eventName)):
				setattr(self, eventName, Event())

			#Add function to event object
			event = getattr(self, eventName)
			event.add(myFunction)

			answer = function(self, *args, **kwargs)

			return answer
		return wrapper
	return decorator

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

	def from_main_thread(self, blocking = True, printEmpty = False):
		"""An non-critical function from the sub-thread will run in the main thread.

		blocking (bool) - If True: This is a non-critical function
		"""

		def setupFunction(myFunctionList, myFunctionArgsList, myFunctionKwargsList):
			nonlocal self

			#Skip empty functions
			if (myFunctionList != None):
				myFunctionList, myFunctionArgsList, myFunctionKwargsList = Utilities.formatFunctionInputList(self, myFunctionList, myFunctionArgsList, myFunctionKwargsList)
				
				#Run each function
				answerList = []
				for i, myFunction in enumerate(myFunctionList):
					#Skip empty functions
					if (myFunction != None):
						myFunctionEvaluated, myFunctionArgs, myFunctionKwargs = Utilities.formatFunctionInput(self, i, myFunctionList, myFunctionArgsList, myFunctionKwargsList)
						answer = runFunction(myFunctionEvaluated, myFunctionArgs, myFunctionKwargs)
						answerList.append(answer)

				#Account for just one function
				if (len(answerList) == 1):
					answerList = answerList[0]
			return answerList

		def runFunction(myFunction, myFunctionArgs, myFunctionKwargs):
			"""Runs a function."""
			nonlocal self

			#Has both args and kwargs
			if ((myFunctionKwargs != None) and (myFunctionArgs != None)):
				answer = myFunction(*myFunctionArgs, **myFunctionKwargs)

			#Has args, but not kwargs
			elif (myFunctionArgs != None):
				answer = myFunction(*myFunctionArgs)

			#Has kwargs, but not args
			elif (myFunctionKwargs != None):
				answer = myFunction(**myFunctionKwargs)

			#Has neither args nor kwargs
			else:
				answer = myFunction()

			return answer

		if (blocking):
			myFunction, myFunctionArgs, myFunctionKwargs = self.callback_queue.get() #blocks until an item is available
			answer = setupFunction(myFunction, myFunctionArgs, myFunctionKwargs)
			
		else:       
			while True:
				try:
					myFunction, myFunctionArgs, myFunctionKwargs = self.callback_queue.get(False) #doesn't block
				
				except queue.Empty: #raised when queue is empty
					if (printEmpty):
						print("--- Thread Queue Empty ---")
					answer = None
					break

				answer = setupFunction(myFunction, myFunctionArgs, myFunctionKwargs)

		return answer

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
			"scroll": 365, "pageup": 366, "pagedown": 367, 
			"cl": 311, "capslock": 311, "nl": 364, "numlock": 364, "sl": 365, "scrolllock": 365,
			
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
				if (isinstance(itemLabel, wx.Event)):
					if (itemLabel.GetEventObject() == item.thing):
						return item
				else:
					if (itemLabel == item.label):
						return item
				
				answer = nestCheck(item[:], itemLabel)
				if (answer != None):
					return answer
			return answer

		def checkType(handleList):
			"""Makes sure only the instance types the user wants are in the return list."""
			nonlocal typeList

			if ((handleList != None) and (typeList != None)):
				answer = []
				if (not isinstance(handleList, (list, tuple, range))):
					handleList = [handleList]

				for item in handleList:
					if (isinstance(item, typeList)):
						answer.append(item)

				if (isinstance(answer, (list, tuple, range))):
					if (len(answer) == 0):
						answer = None
			else:
				answer = handleList
			return answer

		#Ensure correct format
		if (typeList != None):
			if (not isinstance(typeList, (list, tuple, range))):
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
			if ((not isinstance(self, Controller)) and (itemLabel.GetEventObject() == self.thing)):
				answer = self
			else:
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
				raise FutureWarning(f"Add slice steps to get() for indexing {self.__repr__()}")
			
			elif ((itemLabel.start != None) and (itemLabel.start not in self.labelCatalogue)):
				errorMessage = f"There is no item labled {itemLabel.start} in the label catalogue for {self.__repr__()}"
				raise KeyError(errorMessage)
			
			elif ((itemLabel.stop != None) and (itemLabel.stop not in self.labelCatalogue)):
				errorMessage = f"There is no item labled {itemLabel.stop} in the label catalogue for {self.__repr__()}"
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
			if (isinstance(answer, (list, tuple, range))):
				if (len(answer) == 1):
					answer = answer[0]

			return answer

		if (isinstance(itemLabel, wx.Event)):
			errorMessage = f"There is no item associated with the event {itemLabel} in the label catalogue for {self.__repr__()}"
		elif (typeList != None):
			if (isinstance(answer, (list, tuple, range))):
				errorMessage = f"There is no item labled {itemLabel} in the label catalogue for {self.__repr__()} that is a {[item.__name__ for item in typeList]}"
			else:
				errorMessage = f"There is no item labled {itemLabel} in the label catalogue for {self.__repr__()} that is a {typeList.__name__}"
		else:
			errorMessage = f"There is no item labled {itemLabel} in the label catalogue for {self.__repr__()}"
		raise KeyError(errorMessage)

	def runMyFunction(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		"""Runs a function."""

		def runFunction(myFunctionEvaluated, myFunctionArgs, myFunctionKwargs):
			"""This sub-function is needed to make the multiple functions work properly."""

			#Ensure the *args and **kwargs are formatted correctly 
			if ((type(myFunctionArgs) != list) and (myFunctionArgs != None)):
				myFunctionArgs = [myFunctionArgs]

			if ((type(myFunctionKwargs) != list) and (myFunctionKwargs != None)):
				myFunctionKwargs = [myFunctionKwargs]

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

		#Skip empty functions
		if (myFunction != None):
			myFunctionList, myFunctionArgsList, myFunctionKwargsList = self.formatFunctionInputList(myFunction, myFunctionArgs, myFunctionKwargs)
			#Run each function
			for i, myFunction in enumerate(myFunctionList):
				#Skip empty functions
				if (myFunction != None):
					myFunctionEvaluated, myFunctionArgs, myFunctionKwargs = self.formatFunctionInput(i, myFunctionList, myFunctionArgsList, myFunctionKwargsList)
					runFunction(myFunctionEvaluated, myFunctionArgs, myFunctionKwargs)

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
				#   if (len(myFunctionArgs) == 1):
				#       #The user passed one argument that is a list
				#       myFunctionArgs = [myFunctionArgs]

			#Check for user error
			if ((type(myFunctionKwargs) != dict) and (myFunctionKwargs != None)):
				errorMessage = f"myFunctionKwargs must be a dictionary for function {myFunctionEvaluated.__repr__()}"
				raise ValueError(errorMessage)

		return myFunctionEvaluated, myFunctionArgs, myFunctionKwargs

	def betterBind(self, eventType, thing, myFunctionList, myFunctionArgsList = None, myFunctionKwargsList = None, mode = 1, rebind = False):
		"""Binds wxObjects in a better way.
		Inspired by: "Florian Bosch" on http://stackoverflow.com/questions/173687/is-it-possible-to-pass-arguments-into-event-bindings
		Special thanks for help on mult-functions to "Mike Driscoll" on http://stackoverflow.com/questions/11621833/how-to-bind-2-functions-to-a-single-event

		eventType (CommandEvent) - The wxPython event to be bound
		thing (wxObject)         - What is being bound to
		myFunctionList (str)     - The function that will be ran when the event occurs
		myFunctionArgs (list)    - Any input arguments for myFunction. A list of multiple functions can be given
		myFunctionKwargs (dict)  - Any input keyword arguments for myFunction. A dictionary of variables for each function can be given as a list. The index of the variables must be the same as the index for the functions 
		mode (int)               - Dictates how things are bound. Used for special cases
		rebind (bool)            - Will unbind the provided function (if it was already bound) from the 'thing' and then rebind it. Only works for non-argument functions
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
		def bind(myFunctionEvaluated, myFunctionArgs, myFunctionKwargs):
			"""This sub-function is needed to make the multiple functions work properly."""
			nonlocal self, eventType, thing, mode, rebind

			#Get the class type in order to bind the object to the correct thing
			thingClass = thing.GetClassName()

			##Determine how to bind the object
			if (thingClass == "wxWindow"):
				if (mode == 2):
					bindObject = thing
				else:
					bindObject = self.parent.thing

			elif (thingClass in ["wxMenuItem", "wxToolBarToolBase"]):
				bindObject = self.thing
			else:
				bindObject = thing

			#Account for rebinding
			if (rebind):
				unbound = bindObject.Unbind(eventType, handler = myFunctionEvaluated, source = thing)
				if (not unbound):
					#If the lambda style function was used, this will not work
					warnings.warn(f"Unbinding function {myFunctionEvaluated} for {self.__repr__()} failed", Warning, stacklevel = 3)

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
					bindObject.Bind(eventType, myFunctionEvaluated, thing)

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
					bindObject.Bind(eventType, myFunctionEvaluated)

			else:
				errorMessage = f"Unknown mode {mode} for betterBind()"
				raise TypeError(errorMessage)

		#Skip empty functions
		if (myFunctionList != None):
			myFunctionList, myFunctionArgsList, myFunctionKwargsList = self.formatFunctionInputList(myFunctionList, myFunctionArgsList, myFunctionKwargsList)
			#Run each function
			for i, myFunction in enumerate(myFunctionList):
				#Skip empty functions
				if (myFunction != None):
					myFunctionEvaluated, myFunctionArgs, myFunctionKwargs = self.formatFunctionInput(i, myFunctionList, myFunctionArgsList, myFunctionKwargsList)
					bind(myFunctionEvaluated, myFunctionArgs, myFunctionKwargs)

	def keyBind(self, key, myFunction, myFunctionArgs = None, myFunctionKwargs = None, includeEvent = True,
		keyUp = True, numpad = False, ctrl = False, alt = False, shift = False, event = None, thing = None):
		"""Binds wxObjects to key events.
		Speed efficency help from Aya on http://stackoverflow.com/questions/17166074/most-efficient-way-of-making-an-if-elif-elif-else-statement-when-the-else-is-don

		key (str)              - The keyboard key to bind the function(s) to
		thing (wxObject)       - What is being bound to
			- If None: Will bind to self.thing
		myFunction (str)   - The function that will be ran when the event occurs
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

		Example Input: keyBind("enter", "self.onExit", "Extra Information")
		Example Input: keyBind("enter", "self.onExit", "Extra Information", thing = myInputBox.thing)
		Example Input: keyBind("enter", "self.onExit", "Extra Information", ctrl = True)
		Example Input: keyBind("enter", ["self.toggleObjectWithLabel", "self.onQueueValue", ], [["myInputBox", True], None])
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
				key = f"numpad+{key}"
		# elif (ctrl):
		#   if ("ctrl" not in key):
		#       key = f"ctrl+{key}"

		#Error Check
		if (key not in self.keyOptions):
			warnings.warn(f"{key} is not a known key binding", Warning, stacklevel = 2)
			return None

		#Get the corresponding key address
		value = self.keyOptions[key]

		#Determine at what time to run the function
		if (event == None):
			if (keyUp):
				event = wx.EVT_KEY_UP
			else:
				event = wx.EVT_KEY_DOWN

		if (thing == None):
			thing = self.thing

		#Bind the event
		self.betterBind(event, thing, self.onKeyPress, [value, myFunction, myFunctionArgs, myFunctionKwargs, ctrl, alt, shift, includeEvent], mode = 2)

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

	def getKeyState(self, key, event = None):
		"""Returns the state of the requested key.
		Returns True if the key is currently pressed, and false if it is not.
		For Locks, returns True if the key is locked on, and false if it is not.
		Special thanks to Abhijit for how to check keyboard lock states on https://stackoverflow.com/questions/21160100/python-3-x-getting-the-state-of-caps-lock-num-lock-scroll-lock-on-windows

		key (str) - What key to check
			"CL" - Caps Lock
			"NL" - Num Lock
			"SL" - Scroll Lock

		Example Input: getKeyState("k")
		Example Input: getKeyState("cl")
		"""

		#Error Check
		if (not isinstance(key, str)):
			key = str(key)

		#Determine key
		state = None
		if (key == "cl"):
			if ((event != None) and (event.GetKeyCode() != self.keyOptions["cl"])):
				return

			hllDll = ctypes.WinDLL ("User32.dll")
			VK_CAPITAL = 0x14
			state = hllDll.GetKeyState(VK_CAPITAL)

			if ((state == 1) or (state == 65409)):
				state = True
			else:
				state = False
	
		return state

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
				self.controller.threadQueue.from_dummy_thread(myFunction, myFunctionArgs, myFunctionKwargs)

			else:
				warnings.warn(f"Cannot pass from the main thread to the main thread for {self.__repr__()}", Warning, stacklevel = 2)

	def recieveFunction(self, blocking = True, printEmpty = False):
		"""Passes a function from one thread to another. Used to recieve the function.
		If a thread object is not given it will pass from the current thread to the main thread.
		"""

		self.controller.threadQueue.from_main_thread(blocking = blocking, printEmpty = printEmpty)

	def onBackgroundRun(self, event, myFunctionList, myFunctionArgsList = None, myFunctionKwargsList = None, shown = False, makeThread = True):
		"""Here so the function backgroundRun can be triggered from a bound event."""

		#Run the function correctly
		self.backgroundRun(myFunctionList, myFunctionArgsList, myFunctionKwargsList, shown, makeThread)

		event.Skip()

	def backgroundRun(self, myFunction, myFunctionArgs = None, myFunctionKwargs = None, shown = False, makeThread = True):
		"""Runs a function in the background in a way that it does not lock up the GUI.
		Meant for functions that take a long time to run.
		If makeThread is true, the new thread object will be returned to the user.

		myFunction (str)       - The function that will be ran when the event occurs
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
		if (myFunction != None):
			myFunctionList, myFunctionArgsList, myFunctionKwargsList = self.formatFunctionInputList(myFunction, myFunctionArgs, myFunctionKwargs)

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
							warnings.warn(f"The window {self} was given it's own idle function by the user for {self.__repr__()}", Warning, stacklevel = 2)
				else:
					warnings.warn(f"function {i} in myFunctionList == None for backgroundRun() for {self.__repr__()}", Warning, stacklevel = 2)
		else:
			warnings.warn(f"myFunction == None for backgroundRun() for {self.__repr__()}", Warning, stacklevel = 2)

		return None

	def autoRun(self, delay, myFunction, myFunctionArgs = None, myFunctionKwargs = None, after = False):
		"""Automatically runs the provided function.

		delay (int)       - How many milliseconds to wait before the function is executed
		myFunction (list) - What function will be ran. Can be a string or function object
		after (bool)      - If True: The function will run after the function that called this function instead of after a timer ends

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
		if (myFunction != None):
			myFunctionList, myFunctionArgsList, myFunctionKwargsList = self.formatFunctionInputList(myFunction, myFunctionArgs, myFunctionKwargs)
			
			#Run each function
			for i, myFunction in enumerate(myFunctionList):
				#Skip empty functions
				if (myFunction != None):
					myFunctionEvaluated, myFunctionArgs, myFunctionKwargs = self.formatFunctionInput(i, myFunctionList, myFunctionArgsList, myFunctionKwargsList)
					runFunction(after, myFunctionEvaluated, myFunctionArgs, myFunctionKwargs)
		else:
			warnings.warn(f"myFunctionList == None for autoRun() in {self.__repr__()}", Warning, stacklevel = 2)

	#Nesting Catalogue
	def getAddressValue(self, address):
		"""Returns the value of a given address for a dictionary of dictionaries.
		Special thanks to DomTomCat for how to get a value from a dictionary of dictionaries of n depth on https://stackoverflow.com/questions/14692690/access-nested-dictionary-items-via-a-list-of-keys
		
		address (list) - The path of keys to follow on the catalogue

		Example Input: getAddressValue(self.nestingAddress)
		Example Input: getAddressValue(self.nestingAddress + [self.(id)])
		"""
		global nestingCatalogue

		if (not isinstance(address, (list, tuple, range))):
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

		if (not isinstance(address, (list, tuple, range))):
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
		elif (not isinstance(include, (list, tuple, range))):
			include = [include]

		if (exclude == None):
			exclude = []
		elif (not isinstance(exclude, (list, tuple, range))):
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
					warnings.warn(f"Could not find {label} in labelCatalogueOrder for {handle_source.__repr__()}", Warning, stacklevel = 2)
				break
		else:
			for i, handle in enumerate(handle_source.unnamedList):
				if (handle == handle_remove):
					handle_source.unnamedList.pop(i)
					break
			else:
				warnings.warn(f"Could not find {handle_remove.__repr__()} in labelCatalogue or unnamedList for {handle_source.__repr__()}", Warning, stacklevel = 2)

	def finalNest(self, handle):
		"""The final step in the nesting process."""

		handle.nested = True
		handle.nestingAddress = self.nestingAddress + [id(self)]
		self.setAddressValue(handle.nestingAddress + [id(handle)], {None: handle})

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
						errorMessage = f"Unknown combination flag {flag}"
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
						errorMessage = f"Unknown alignment flag {flag}"
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
						errorMessage = f"Unknown border flag {flag}"
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
						errorMessage = f"Unknown expand flag {flag}"
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
						errorMessage = f"Unknown fixture flag {flag}"
						raise ValueError(errorMessage)

				##Unknown Action
				else:
					errorMessage = f"Unknown flag {flag}"
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
						
					elif (imagePath == "folderNew"):
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
						errorMessage = f"The icon {imagePath} cannot be found"
						raise KeyError(errorMessage)
				else:
					try:
						image = wx.Bitmap(imagePath)
					except:
						image = wx.Image(imagePath, wx.BITMAP_TYPE_BMP).ConvertToBitmap()
		else:
			image = wx.NullBitmap

		return image

	def getColor(self, color):
		"""Returns a wxColor object.

		color (str) - What color to return
			- If tuple: Will interperet as (Red, Green, Blue). Values can be integers from 0 to 255 or floats from 0.0 to 1.0

		Example Input: getColor("white")
		Example Input: getColor((255, 255, 0))
		Example Input: getColor((0.5, 0.5, 0.5))
		Example Input: getColor((255, 0.5, 0))
		"""

		if (color == None):
			thing = wx.NullColour
		else:
			if (isinstance(color, str)):
				if (color[0].lower() == "w"):
					color = (255, 255, 255)
				elif (color[:3].lower() == "bla"):
					color = (0, 0, 0)
				if (color[0].lower() == "r"):
					color = (255, 0, 0)
				if (color[0].lower() == "g"):
					color = (0, 255, 0)
				if (color[:3].lower() == "blu"):
					color = (0, 0, 255)
				else:
					warnings.warn(f"Unknown color {color} given to getColor in {self.__repr__()}", Warning, stacklevel = 2)
					return
			elif (not isinstance(color, (list, tuple, range))):
					warnings.warn(f"'color' must be a tuple or string, not a {type(color)}, for getColor in {self.__repr__()}", Warning, stacklevel = 2)
					return
			elif (len(color) != 3):
					warnings.warn(f"'color' must have a length of three, not {len(color)}, for getColor in {self.__repr__()}", Warning, stacklevel = 2)
					return

			color = list(color)
			for i, item in enumerate(color):
				if (isinstance(item, float)):
					color[i] = math.ceil(item * 255)

			thing = wx.Colour(color[0], color[1], color[2])
		return thing

	def getFont(self, size = None, bold = False, italic = False, color = None, family = None):
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

		Example Input: getFont()
		Example Input: getFont(size = 72, bold = True, color = "red")
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
	def logPrint(self, *args, fileName = "cmd_log.log", timestamp = True, **kwargs):
		"""Overrides the print function to also log the information printed.

		fileName (str)   - The filename for the log
		timestamp (bool) - Determines if the timestamp is added to the log
		"""

		#Write the information to a file
		with open(fileName, "a") as fileHandle:

			if (timestamp):
				content = f"{time.strftime('%Y/%m/%d %H:%M:%S', time.localtime())} --- "
			else:
				content = ""

			content += " " .join([str(item) for item in args])
			fileHandle.write(content)
			fileHandle.write("\n")

	def logError(self, *args, fileName = "error_log.log", timestamp = True, **kwargs):
		"""Overrides the stderr function to also log the error information.

		fileName (str)   - The filename for the log
		timestamp (bool) - Determines if the timestamp is added to the log
		"""

		self.logPrint(*args, fileName = fileName, timestamp = timestamp, **kwargs)

	def getArguments(self, argument_catalogue, desiredArgs):
		"""Returns a list of the values for the desired arguments from a dictionary.

		argument_catalogue (dict) - All locals() of the function
		desiredArgs (str)   - Determines what is returned. Can be a list of values

		Example Input: getArguments(argument_catalogue, desiredArgs = "handler")
		Example Input: getArguments(argument_catalogue, desiredArgs = ["handler", "flex", "flags"])
		"""

		#Ensure correct format
		if (not isinstance(desiredArgs, (list, tuple, range))):
			desiredArgs = [desiredArgs]

		argList = []
		for arg in desiredArgs:
			if (arg not in argument_catalogue):
				errorMessage = f"Must provide the argument {arg} to {self.__repr__()}"
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
			if (not isinstance(desiredArgs, (list, tuple, range))):
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
		if (not isinstance(typeNeeded, (list, tuple, range))):
			typeNeeded = [typeNeeded]

		#Error check
		if (self.type.lower() not in [str(item).lower() for item in typeNeeded]):
			errorMessage = f"Cannot use type {self.type} with the function {function.__name__}"
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
		if (not isinstance(arguments, (list, tuple, range))):
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
		font = self.getFont()
		dc = wx.WindowDC(self)
		dc.SetFont(font)

		#Get font pixel size
		size = dc.GetTextExtent(line)
		del dc

		return size

	def getWindow(self, label = None):
		if (isinstance(label, handle_Window)):
			return label

		window = self.get(label, typeList = [handle_Window])
		return window

	def getTable(self, label = None):
		table = self.get(label, typeList = [handle_WidgetTable])
		return table

	def getCanvas(self, label = None):
		canvas = self.get(label, typeList = [handle_WidgetCanvas])
		return canvas

	def getSizer(self, label = None):
		sizer = self.get(label, typeList = [handle_Sizer])
		return sizer

	def getWidget(self, label = None):
		widget = self.get(label, typeList = [handle_Widget_Base])
		return widget

	def getPopupMenu(self, label = None):
		popupMenu = self.get(label, typeList = [handle_MenuPopup])
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
	#   """Hides the window. Default of a hide (h) menu item."""

	#   self.Hide()
	#   #There is no event.Skip() because if not, then the window will destroy itself

	# def onQuit(self, event):
	#   """Closes the window. Default of a close (c) menu item."""

	#   self.Destroy()
	#   event.Skip()

	def onExit(self, event):
		"""Closes all windows. Default of a quit (q) or exit (e) menu item."""

		# #Make sure sub threads are closed
		# if (threading.active_count() > 1):
		#   for thread in threading.enumerate():
		#       #Close the threads that are not the main thread
		#       if (thread != threading.main_thread()):
		#           thread.stop()

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

		self.unnamedList = []
		self.labelCatalogue = {}
		self.labelCatalogueOrder = []

	def __repr__(self):
		representation = f"{type(self).__name__}(id = {id(self)}"

		if (hasattr(self, "label")):
			representation += f", label = {self.label})"
		else:
			representation += ")"

		return representation

	def __str__(self):
		"""Gives diagnostic information on the Widget when it is printed out."""

		output = f"{type(self).__name__}()\n-- id: {id(self)}\n"
		if (self.parent != None):
			output += f"-- parent id: {id(self.parent)}\n"
		if (self.nestingAddress != None):
			output += f"-- nesting address: {self.nestingAddress}\n"
		if (self.label != None):
			output += f"-- label: {self.label}\n"
		if (self.type != None):
			output += f"-- type: {self.type}\n"
		if (self.thing != None):
			output += f"-- wxObject: {type(self.thing).__name__}\n"
		if (self.nested):
			output += "-- nested: True\n"
		if ((self.unnamedList != None) and (len(self.unnamedList) != 0)):
			output += f"-- unnamed items: {len(self.unnamedList)}\n"
		if ((self.labelCatalogue != None) and (len(self.labelCatalogue) != 0)):
			output += f"-- labeled items: {len(self.labelCatalogue)}\n"
		return output

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

	def __contains__(self, key):
		"""Allows the user to use get() when using 'in'."""

		if (key in self[:]):
			return True
		elif (key in [item.label for item in self[:]]):
			return True
		return False

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

	def preBuild(self, argument_catalogue):
		"""Runs before this object is built."""

		buildSelf = argument_catalogue["self"]
		
		#Determine mySizer
		if (hasattr(self, "mySizer") and (self.mySizer != None)):
			warnings.warn(f"{self.__repr__()} already has the sizer {self.mySizer.__repr__()} as 'mySizer' in finalNest() for {buildSelf.__repr__()}\nOverwriting 'mySizer'", Warning, stacklevel = 2)
			
		if (isinstance(buildSelf, handle_Sizer)):
			self.mySizer = buildSelf
		elif (isinstance(buildSelf, (handle_Window, Controller, handle_MenuPopup))):
			self.mySizer = None
		elif (isinstance(buildSelf, handle_Menu) and (buildSelf.type.lower() != "toolbar")):
			self.mySizer = None
		else:
			self.mySizer = buildSelf.mySizer
		
		#Determine native window
		if (isinstance(buildSelf, handle_Window)):
			self.myWindow = buildSelf
		elif (isinstance(buildSelf, Controller)):
			self.myWindow = None
		else:
			self.myWindow = buildSelf.myWindow

	def postBuild(self, argument_catalogue):
		"""Runs after this object is built."""
		
		#Unpack arguments
		buildSelf = argument_catalogue["self"]
		hidden, enabled = self.getArguments(argument_catalogue, ["hidden", "enabled"])

		#Determine visibility
		if (isinstance(self, handle_Window) and (not hidden)):
			self.showWindow()
		elif (hidden):
			if (isinstance(self, handle_Sizer)):
				self.addFinalFunction(self.thing.ShowItems, False)
			else:
				self.thing.Hide()

		#Determine disability
		if (isinstance(self, handle_Window) and (not enabled)):
			pass
		elif (not enabled):
			if (isinstance(self, handle_Sizer)):
				self.addFinalFunction(self.setEnable, False)
			else:
				self.setEnable(False)

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

	def __add__(self, other):
		"""If two sizers are added together, then they are nested."""

		self.nest(other)

	def preBuild(self, argument_catalogue):
		"""Runs before this object is built."""

		handle_Base.preBuild(self, argument_catalogue)

		#Unpack arguments
		label = argument_catalogue["label"]
		parent = argument_catalogue["parent"]
		buildSelf = argument_catalogue["self"]

		#Error Checking
		if (buildSelf.nestingAddress == None):
			errorMessage = f"{buildSelf.__repr__()} is not nested, and so it cannot nest things in preBuild() for {self.__repr__()}"
			raise ValueError(errorMessage)

		#Store data
		self.label = label

		#Add object to internal catalogue
		if (label != None):
			if (label in buildSelf.labelCatalogue):
				warnings.warn(f"Overwriting label association for {label} in {buildSelf.__repr__()}", Warning, stacklevel = 2)

			buildSelf.labelCatalogue[self.label] = self
			buildSelf.labelCatalogueOrder.append(self.label)
		else:
			buildSelf.unnamedList.append(self)

		if (parent != None):
			self.parent = parent
		else:
			if (not isinstance(buildSelf, Controller)):
				if (buildSelf.parent != None):
					self.parent = buildSelf
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
			if (buildSelf.nestingAddress[0] not in nestingCatalogue):
				warnings.warn(f"{buildSelf.nestingAddress[0]} not in nestingCatalogue", Warning, stacklevel = 2)
				return

			if (None not in nestingCatalogue[buildSelf.nestingAddress[0]]):
				warnings.warn(f"None not in nestingCatalogue for {buildSelf.nestingAddress[0]}", Warning, stacklevel = 2)
				return

			buildSelf.allowBuildErrors = nestingCatalogue[buildSelf.nestingAddress[0]][None].allowBuildErrors
			self.allowBuildErrors = buildSelf.allowBuildErrors

	def postBuild(self, argument_catalogue):
		"""Runs after this object is built."""
		
		handle_Base.postBuild(self, argument_catalogue)

	def overloadHelp(self, myFunction, label, kwargs, window = False):
		"""Helps the overloaded functions to stay small.

		Example Input: overloadHelp("toggleEnable")
		"""

		#Account for all nested
		if (label == None):
			if (window):
				function = getattr(handle_Widget_Base, myFunction)
				answer = function(self, **kwargs)
				return answer
			else:
				answerList = []
				for handle in self:
					function = getattr(handle, myFunction)
					answer = function(**kwargs)

					if (not isinstance(answer, list)):
						answer = [answer]

					answerList.extend(answer)

				return answerList
		else:
			#Account for multiple objects
			if (not isinstance(label, (list, tuple, range))):
				labelList = [label]
			else:
				labelList = label

			answerList = []
			for label in labelList:
				handle = self.get(label, checkNested = True)

				function = getattr(handle, myFunction)
				answer = function(**kwargs)

				if (not isinstance(answer, list)):
					answer = [answer]

				answerList.extend(answer)

			return answerList

	#Change State
	##Enable / Disable
	def onToggleEnable(self, event, *args, **kwargs):
		"""A wx.CommandEvent version of toggleEnable."""

		self.toggleEnable(*args, event = event, **kwargs)
		event.Skip()

	def toggleEnable(self, label = None, window = False, **kwargs):
		"""Overload for toggleEnable in handle_Widget_Base."""

		self.overloadHelp("toggleEnable", label, kwargs, window = window)

	def onSetEnable(self, event, *args, **kwargs):
		"""A wx.CommandEvent version of setEnable."""

		self.setEnable(*args, event = event, **kwargs)
		event.Skip()

	def setEnable(self, label = None, window = False, **kwargs):
		"""Overload for setEnable in handle_Widget_Base."""

		self.overloadHelp("setEnable", label, kwargs, window = window)

	def onSetDisable(self, event, *args, **kwargs):
		"""A wx.CommandEvent version of setDisable."""

		self.setDisable(*args, event = event, **kwargs)
		event.Skip()

	def setDisable(self, label = None, window = False, **kwargs):
		"""Overload for setDisable in handle_Widget_Base."""

		self.overloadHelp("setDisable", label, kwargs, window = window)

	def onEnable(self, event, *args, **kwargs):
		"""A wx.CommandEvent version of enable."""

		self.enable(*args, event = event, **kwargs)
		event.Skip()

	def enable(self, label = None, window = False, **kwargs):
		"""Overload for enable in handle_Widget_Base."""

		self.overloadHelp("enable", label, kwargs, window = window)

	def onDisable(self, event, *args, **kwargs):
		"""A wx.CommandEvent version of disable."""

		self.disable(*args, event = event, **kwargs)
		event.Skip()

	def disable(self, label = None, window = False, **kwargs):
		"""Overload for disable in handle_Widget_Base."""

		self.overloadHelp("disable", label, kwargs, window = window)

	def checkEnabled(self, label = None, window = False, **kwargs):
		"""Overload for checkEnabled in handle_Widget_Base."""

		answer = self.overloadHelp("checkEnabled", label, kwargs, window = window)
		return answer

	def checkDisabled(self, label = None, window = False, **kwargs):
		"""Overload for checkDisabled in handle_Widget_Base."""

		answer = self.overloadHelp("checkDisabled", label, kwargs, window = window)
		return answer

	##Show / Hide
	def onToggleShow(self, event, *args, **kwargs):
		"""A wx.CommandEvent version of toggleShow."""

		self.toggleShow(*args, event = event, **kwargs)
		event.Skip()

	def toggleShow(self, label = None, window = False, **kwargs):
		"""Overload for toggleShow in handle_Widget_Base."""

		self.overloadHelp("toggleShow", label, kwargs, window = window)

	def onSetShow(self, event, *args, **kwargs):
		"""A wx.CommandEvent version of setShow."""

		self.setShow(*args, event = event, **kwargs)
		event.Skip()

	def setShow(self, label = None, window = False, **kwargs):
		"""Overload for setShow in handle_Widget_Base."""

		self.overloadHelp("setShow", label, kwargs, window = window)

	def onSetHide(self, event, *args, **kwargs):
		"""A wx.CommandEvent version of setHide."""

		self.setHide(*args, event = event, **kwargs)
		event.Skip()

	def setHide(self, label = None, window = False, **kwargs):
		"""Overload for setHide in handle_Widget_Base."""

		self.overloadHelp("setHide", label, kwargs, window = window)

	def onShow(self, event, *args, **kwargs):
		"""A wx.CommandEvent version of show."""

		self.show(*args, event = event, **kwargs)
		event.Skip()

	def show(self, label = None, window = False, **kwargs):
		"""Overload for show in handle_Widget_Base."""

		self.overloadHelp("show", label, kwargs, window = window)

	def onHide(self, event, *args, **kwargs):
		"""A wx.CommandEvent version of hide."""

		self.hide(*args, event = event, **kwargs)
		event.Skip()

	def hide(self, label = None, window = False, **kwargs):
		"""Overload for hide in handle_Widget_Base."""

		self.overloadHelp("hide", label, kwargs, window = window)

	def checkShown(self, label = None, window = False, **kwargs):
		"""Overload for checkShown in handle_Widget_Base."""

		answer = self.overloadHelp("checkShown", label, kwargs, window = window)
		return answer

	def checkHidden(self, label = None, window = False, **kwargs):
		"""Overload for checkHidden in handle_Widget_Base."""

		answer = self.overloadHelp("checkHidden", label, kwargs, window = window)
		return answer

	##Modified
	def onModify(self, event, *args, **kwargs):
		"""A wx.CommandEvent version of modify."""

		self.modify(*args, event = event, **kwargs)
		event.Skip()

	def modify(self, label = None, window = False, **kwargs):
		"""Overload for modify in handle_Widget_Base."""

		self.overloadHelp("modify", label, kwargs, window = window)

	def onSetModified(self, event, *args, **kwargs):
		"""A wx.CommandEvent version of setModified."""

		self.setModified(*args, event = event, **kwargs)
		event.Skip()

	def setModified(self, label = None, window = False, **kwargs):
		"""Overload for setModified in handle_Widget_Base."""

		self.overloadHelp("setModified", label, kwargs, window = window)

	def checkModified(self, label = None, window = False, **kwargs):
		"""Overload for checkModified in handle_Widget_Base."""

		answer = self.overloadHelp("checkModified", label, kwargs, window = window)
		return answer

	##Read Only
	def onReadOnly(self, event, *args, **kwargs):
		"""A wx.CommandEvent version of readOnly."""

		self.readOnly(*args, event = event, **kwargs)
		event.Skip()

	def readOnly(self, label = None, window = False, **kwargs):
		"""Overload for readOnly in handle_Widget_Base."""

		self.overloadHelp("readOnly", label, kwargs, window = window)

	def onSetReadOnly(self, event, *args, **kwargs):
		"""A wx.CommandEvent version of setReadOnly."""

		self.setReadOnly(*args, event = event, **kwargs)
		event.Skip()

	def setReadOnly(self, label = None, window = False, **kwargs):
		"""Overload for setReadOnly in handle_Widget_Base."""

		self.overloadHelp("setReadOnly", label, kwargs, window = window)

	def checkReadOnly(self, label = None, window = False, **kwargs):
		"""Overload for checkReadOnly in handle_Widget_Base."""

		answer = self.overloadHelp("checkReadOnly", label, kwargs, window = window)
		return answer

	#Tool Tips
	def setToolTipAppearDelay(self, *args, label = None, window = False, **kwargs):
		"""Override function for setToolTipAppearDelay for handle_Widget_Base."""

		self.overloadHelp("setToolTipAppearDelay", label, kwargs, window = window)

	def setToolTipDisappearDelay(self, *args, label = None, window = False, **kwargs):
		"""Override function for setToolTipDisappearDelay for handle_Widget_Base."""

		self.overloadHelp("setToolTipDisappearDelay", label, kwargs, window = window)

	def setToolTipReappearDelay(self, *args, label = None, window = False, **kwargs):
		"""Override function for setToolTipReappearDelay for handle_Widget_Base."""

		self.overloadHelp("setToolTipReappearDelay", label, kwargs, window = window)

	#Etc
	def readBuildInstructions_sizer(self, parent, i, instructions):
		"""Interprets instructions given by the user for what sizer to make and how to make it."""

		if (not isinstance(instructions, dict)):
			errorMessage = f"sizer_{i} must be a dictionary for {self.__repr__()}"
			raise ValueError(errorMessage)

		if (len(instructions) == 0):
			instructions["parent"] = parent

		if (len(instructions) == 1):
			instructions["type"] = "Box"
		else:
			if ("type" not in instructions):
				errorMessage = "Must supply which sizer type to make. The key should be 'type'. The value should be 'Grid', 'Flex', 'Bag', 'Box', 'Text', or 'Wrap'"
				raise ValueError(errorMessage)

		sizerType = instructions["type"].lower()
		if (sizerType not in ["grid", "flex", "bag", "box", "text", "wrap"]):
			errorMessage = f"There is no 'type' {instructions['type']}. The value should be be 'Grid', 'Flex', 'Bag', 'Box', 'Text', or 'Wrap'"
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
		sizer.index = i
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
			errorMessage = f"panel_{i} must be a dictionary for {self.__repr__()}"
			raise ValueError(errorMessage)

		#Overwrite default with user given data
		kwargs = {item.name: item.default for item in inspect.signature(handle_Window.addPanel).parameters.values()}
		for key, value in instructions.items():
			kwargs[key] = value

		#Create Handler
		panel = handle_Panel()
		panel.index = i

		#Finish building panel
		kwargs["self"] = parent
		panel.build(kwargs)

		return panel

class handle_Widget_Base(handle_Base):
	"""A handle for working with a wxWidget."""

	def __init__(self):
		"""Initializes defaults."""

		#Initialize inherited classes
		handle_Base.__init__(self)

	def __len__(self):
		"""Returns what the contextual length is for the object associated with this handle."""

		if (self.type.lower() == "progressbar"):
			value = self.thing.GetRange()

		else:
			warnings.warn(f"Add {self.type} to __len__() for {self.__repr__()}", Warning, stacklevel = 2)
			value = 0

		return value

	def __str__(self):
		"""Gives diagnostic information on the Widget when it is printed out."""

		output = handle_Base.__str__(self)
		
		if ((self.nestingAddress != None) and (hasattr(self, "mySizer") and (self.mySizer != None))):
			# sizer = self.getAddressValue(self.nestingAddress)[None]
			output += f"-- sizer id: {id(self.mySizer)}\n"
		return output

	def preBuild(self, argument_catalogue):
		"""Runs before this object is built."""

		handle_Base.preBuild(self, argument_catalogue)
		
		#Unpack arguments
		label, parent, buildSelf = self.getArguments(argument_catalogue, ["label", "parent", "self"])

		#Store data
		self.label = label

		#Add object to internal catalogue
		if (label != None):
			if (label in buildSelf.labelCatalogue):
				warnings.warn(f"Overwriting label association for {label} in {buildSelf.__repr__()}", Warning, stacklevel = 2)

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
			if (buildSelf.nestingAddress[0] not in nestingCatalogue):
				warnings.warn(f"{buildSelf.nestingAddress[0]} not in nestingCatalogue", Warning, stacklevel = 2)
				return

			if (None not in nestingCatalogue[buildSelf.nestingAddress[0]]):
				warnings.warn(f"None not in nestingCatalogue for {buildSelf.nestingAddress[0]}", Warning, stacklevel = 2)
				return

			buildSelf.allowBuildErrors = nestingCatalogue[buildSelf.nestingAddress[0]][None].allowBuildErrors
			self.allowBuildErrors = buildSelf.allowBuildErrors

	def postBuild(self, argument_catalogue):
		"""Runs after this object is built."""
		
		handle_Base.postBuild(self, argument_catalogue)
		
		#Unpack arguments
		selected, flags, flex, mySizer = self.getArguments(argument_catalogue, ["selected", "flags", "flex", "mySizer"])

		#Determine if it is selected by default
		if (selected):
			self.thing.SetDefault()
		
		#Add it to the sizer
		if (mySizer == None):
			mySizer = self.mySizer
		mySizer.nest(self, flex = flex, flags = flags)

	def build(self, argument_catalogue):
		"""Determiens which build system to use for this handle."""

		def build_line():
			"""Builds a wx line object."""
			nonlocal self, argument_catalogue

			vertical = self.getArguments(argument_catalogue, "vertical")

			#Apply settings
			if (vertical):
				direction = wx.LI_VERTICAL
			else:
				direction = wx.LI_HORIZONTAL

			#Create the thing to put in the grid
			self.thing = wx.StaticLine(self.parent.thing, style = direction)

		def build_progressBar():
			"""Builds a wx line object."""
			nonlocal self, argument_catalogue

			vertical, myMax, myInitial = self.getArguments(argument_catalogue, ["vertical", "myMax", "myInitial"])
			if (vertical):
				styles = wx.GA_VERTICAL
			else:
				styles = wx.GA_HORIZONTAL
		
			#Create the thing to put in the grid
			self.thing = wx.Gauge(self.parent.thing, range = myMax, style = styles)

			#Set Initial Conditions
			self.thing.SetValue(myInitial)
		
		#########################################################

		self.preBuild(argument_catalogue)

		if (self.type.lower() == "line"):
			build_line()
		elif (self.type.lower() == "progressbar"):
			build_progressBar()
		else:
			warnings.warn(f"Add {self.type} to build() for {self.__repr__()}", Warning, stacklevel = 2)

		self.postBuild(argument_catalogue)

	#Getters
	def getValue(self, event = None):
		"""Returns what the contextual value is for the object associated with this handle."""

		if (self.type.lower() == "progressbar"):
			value = self.thing.GetValue() #(int) - Where the progress bar currently is

		else:
			warnings.warn(f"Add {self.type} to getValue() for {self.__repr__()}", Warning, stacklevel = 2)
			value = None

		return value

	def getIndex(self, event = None):
		"""Returns what the contextual index is for the object associated with this handle."""

		if (False):
			pass
		else:
			warnings.warn(f"Add {self.type} to getIndex() for {self.__repr__()}", Warning, stacklevel = 2)
			value = None

		return value

	def getAll(self, event = None):
		"""Returns all the contextual values for the object associated with this handle."""

		if (self.type.lower() == "progressbar"):
			value = self.thing.GetRange()

		else:
			warnings.warn(f"Add {self.type} to getAll() for {self.__repr__()}", Warning, stacklevel = 2)
			value = None

		return value

	#Setters
	def setValue(self, newValue, event = None):
		"""Returns what the contextual value is for the object associated with this handle."""

		warnings.warn(f"Add {self.type} to setValue() for {self.__repr__()}", Warning, stacklevel = 2)

	def setSelection(self, newValue, event = None):
		"""Returns what the contextual value is for the object associated with this handle."""

		warnings.warn(f"Add {self.type} to setValue() for {self.__repr__()}", Warning, stacklevel = 2)

	def setReadOnly(self, state = True, event = None):
		"""Sets the contextual readOnly for the object associated with this handle to what the user supplies."""

		if (self.type.lower() == "line"):
			pass
			
		else:
			warnings.warn(f"Add {self.type} to setReadOnly() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_rightClick(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		self.betterBind(wx.EVT_RIGHT_DOWN, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)

	def addPopupMenu(self, label = None, rightClick = True, 

		preFunction = None, preFunctionArgs = None, preFunctionKwargs = None, 
		postFunction = None, postFunctionArgs = None, postFunctionKwargs = None,

		parent = None, hidden = False, enabled = True, handle = None):
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
		Example Input: addPopupMenu(0, preFunction = myFrame.onHideWindow, preFunctionArgs = 0)
		"""

		handle = handle_MenuPopup()
		handle.type = "MenuPopup_widget"
		parent = self
		text = None
		handle.build(locals())
		self.finalNest(handle)
		return handle

	#Change State
	##Enable / Disable
	def toggleEnable(self, event = None):
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
				text = f"{text}"

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
			if (label in self.myWindow.toolTipCatalogue):
				warnings.warn(f"Overwriting tool tip for {label} in {self.myWindow.__repr__()}", Warning, stacklevel = 2)

			self.myWindow.toolTipCatalogue[label] = toolTip

	def setToolTipAppearDelay(self, delay = 0, label = None):
		"""Changes the appear delay for the tool tip.

		delay (int) - How long to set the delay for
		label (str) - What tool tip to modify this for
			- If None: Will apply to all tool tips for this window created up to this point (not future ones)

		Example Input: setToolTipAppearDelay()
		Example Input: setToolTipAppearDelay(500)
		Example Input: setToolTipAppearDelay(500, "passwordInput")
		"""

		if (isinstance(self, handle_Window)):
			window = self
		elif (isinstance(self, handle_Panel)):
			window = self.parent
		else:
			window = self.myWindow

		if (label != None):
			if (label not in window.toolTipCatalogue):
				warnings.warn(f"There is no tool tip {label} for {window.__repr__()}", Warning, stacklevel = 2)
				return

			toolTip = window.toolTipCatalogue[label]
			toolTip.SetDelay(delay)
		else:
			for label, toolTip in window.toolTipCatalogue:
				toolTip.SetDelay(delay)

	def setToolTipDisappearDelay(self, delay = 0, label = None):
		"""Changes the appear delay for the tool tip.

		delay (int) - How long to set the delay for
		label (str) - What tool tip to modify this for
			- If None: Will apply to all tool tips created up to this point (not future ones)

		Example Input: setToolTipDisappearDelay()
		Example Input: setToolTipDisappearDelay(500)
		Example Input: setToolTipDisappearDelay(500, "passwordInput")
		"""

		if (isinstance(self, handle_Window)):
			window = self
		elif (isinstance(self, handle_Panel)):
			window = self.parent
		else:
			window = self.myWindow

		if (label != None):
			if (label not in window.toolTipCatalogue):
				warnings.warn(f"There is no tool tip {label} for {window.__repr__()}", Warning, stacklevel = 2)
				return

			toolTip = window.toolTipCatalogue[label]
			toolTip.SetAutoPop(delay)
		else:
			for label, toolTip in window.toolTipCatalogue:
				toolTip.SetAutoPop(delay)

	def setToolTipReappearDelay(self, delay = 0, label = None):
		"""Changes the appear delay for the tool tip.

		delay (int) - How long to set the delay for
		label (str) - What tool tip to modify this for
			- If None: Will apply to all tool tips created up to this point (not future ones)

		Example Input: setToolTipReappearDelay()
		Example Input: setToolTipReappearDelay(500)
		Example Input: setToolTipReappearDelay(500, "passwordInput")
		"""

		if (isinstance(self, handle_Window)):
			window = self
		elif (isinstance(self, handle_Panel)):
			window = self.parent
		else:
			window = self.myWindow

		if (label != None):
			if (label not in window.toolTipCatalogue):
				warnings.warn(f"There is no tool tip {label} for {window.__repr__()}", Warning, stacklevel = 2)
				return

			toolTip = window.toolTipCatalogue[label]
			toolTip.SetReshow(delay)
		else:
			for label, toolTip in window.toolTipCatalogue:
				toolTip.SetReshow(delay)

class handle_WidgetText(handle_Widget_Base):
	"""A handle for working with text widgets."""

	def __init__(self):
		"""Initializes defaults."""

		#Initialize inherited classes
		handle_Widget_Base.__init__(self)

	def __len__(self):
		"""Returns what the contextual length is for the object associated with this handle."""

		if (self.type.lower() == "text"):
			value = len(self.getValue()) #(int) - How long the text is

		elif (self.type.lower() == "hyperlink"):
			value = len(self.getValue()) #(int) - How long the url link is

		else:
			warnings.warn(f"Add {self.type} to __len__() for {self.__repr__()}", Warning, stacklevel = 2)
			value = 0

		return value

	def build(self, argument_catalogue):
		"""Determiens which build system to use for this handle."""

		def build_text():
			"""Builds a wx text object."""
			nonlocal self, argument_catalogue

			text, alignment, ellipsize = self.getArguments(argument_catalogue, ["text", "alignment", "ellipsize"])

			#Ensure correct format
			if (not isinstance(text, str)):
				text = f"{text}"
			if (not isinstance(argument_catalogue["flags"], (list, tuple, range))):
				argument_catalogue["flags"] = [argument_catalogue["flags"]]

			#Apply Settings
			if (alignment != None):
				if (isinstance(alignment, bool)):
					if (alignment):
						style = "wx.ALIGN_LEFT"
						argument_catalogue["flags"].append("al")
					else:
						style = "wx.ALIGN_CENTRE"
						argument_catalogue["flags"].append("ac")
				elif (alignment == 0):
					style = "wx.ALIGN_LEFT"
					argument_catalogue["flags"].append("al")
				elif (alignment == 1):
					style = "wx.ALIGN_RIGHT"
					argument_catalogue["flags"].append("ar")
				else:
					style = "wx.ALIGN_CENTRE"
					argument_catalogue["flags"].append("ac")
			else:
				style = "wx.ALIGN_CENTRE"
				argument_catalogue["flags"].append("ac")
			
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
			self.thing = wx.StaticText(self.parent.thing, label = text, style = eval(style))

			# font = self.getFont(size = size, bold = bold, italic = italic, color = color, family = family)
			# self.thing.SetFont(font)

			# if (wrap != None):
			#   if (wrap > 0):
			#       self.wrapText(wrap)

		def build_hyperlink():
			"""Builds a wx hyperlink object."""
			nonlocal self, argument_catalogue

			text, myWebsite = self.getArguments(argument_catalogue, ["text", "myWebsite"])

			#Apply settings
			# wx.adv.HL_ALIGN_LEFT: Align the text to the left.
			# wx.adv.HL_ALIGN_RIGHT: Align the text to the right. This style is not supported under Windows XP but is supported under all the other Windows versions.
			# wx.adv.HL_ALIGN_CENTRE: Center the text (horizontally). This style is not supported by the native MSW implementation used under Windows XP and later.
			# wx.adv.HL_CONTEXTMENU: Pop up a context menu when the hyperlink is right-clicked. The context menu contains a “Copy URL” menu item which is automatically handled by the hyperlink and which just copies in the clipboard the URL (not the label) of the control.
			# wx.adv.HL_DEFAULT_STYLE: The default style for wx.adv.HyperlinkCtrl: BORDER_NONE|wxHL_CONTEXTMENU|wxHL_ALIGN_CENTRE.
			styles = "wx.adv.HL_DEFAULT_STYLE"


			#Create the thing to put in the grid
			self.thing = wx.adv.HyperlinkCtrl(self.parent.thing, label = text, url = myWebsite, style = eval(styles))

			#Apply colors
			# SetHoverColour
			# SetNormalColour
			# SetVisitedColour

			#Bind the function(s)
			myFunction, myFunctionArgs, myFunctionKwargs = self.getArguments(argument_catalogue, ["myFunction", "myFunctionArgs", "myFunctionKwargs"])
			self.setFunction_click(myFunction, myFunctionArgs, myFunctionKwargs)

		def build_empty():
			"""Builds a blank wx text object."""
			nonlocal self

			#Create the thing to put in the grid
			self.thing = wx.StaticText(self.parent.thing, label = wx.EmptyString)
			self.wrapText(-1)
		
		#########################################################

		self.preBuild(argument_catalogue)

		if (self.type.lower() == "text"):
			build_text()
		elif (self.type.lower() == "hyperlink"):
			build_hyperlink()
		elif (self.type.lower() == "empty"):
			build_empty()
		else:
			warnings.warn(f"Add {self.type} to build() for {self.__repr__()}", Warning, stacklevel = 2)

		self.postBuild(argument_catalogue)

	#Getters
	def getValue(self, event = None):
		"""Returns what the contextual value is for the object associated with this handle."""

		if (self.type.lower() == "text"):
			value = self.thing.GetLabel() #(str) - What the text says

		elif (self.type.lower() == "hyperlink"):
			value = self.thing.GetURL() #(str) - What the link is

		else:
			warnings.warn(f"Add {self.type} to getValue() for {self.__repr__()}", Warning, stacklevel = 2)
			value = None

		return value

	#Setters
	def setValue(self, newValue, event = None):
		"""Sets the contextual value for the object associated with this handle to what the user supplies."""

		if (self.type.lower() == "text"):
			if (not isinstance(newValue, str)):
				newValue = f"{newValue}"

			self.thing.SetLabel(newValue) #(str) - What the static text will now say

		elif (self.type.lower() == "hyperlink"):
			if (not isinstance(newValue, str)):
				newValue = f"{newValue}"

			self.thing.SetURL(newValue) #(str) - What the hyperlink will now connect to

		else:
			warnings.warn(f"Add {self.type} to setValue() for {self.__repr__()}", Warning, stacklevel = 2)

	def setReadOnly(self, state = True):
		"""Sets the contextual readOnly for the object associated with this handle to what the user supplies."""

		if (self.type.lower() == "text"):
			pass
			
		else:
			warnings.warn(f"Add {self.type} to setReadOnly() for {self.__repr__()}", Warning, stacklevel = 2)

	#Change Settings
	def wrapText(self, wrap = 1):
		"""Wraps the text to a specific point.

		wrap (int)      - How many pixels wide the line will be before it wraps. If negative: no wrapping is done

		Example Text: wrapText(250)
		"""

		if (wrap != None):
			self.thing.Wrap(wrap)

	def setFunction_click(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type.lower() == "hyperlink"):
			self.betterBind(wx.adv.EVT_HYPERLINK, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		else:
			warnings.warn(f"Add {self.type} to setFunction_click() for {self.__repr__()}", Warning, stacklevel = 2)

class handle_WidgetList(handle_Widget_Base):
	"""A handle for working with list widgets."""

	def __init__(self):
		"""Initializes defaults."""

		#Initialize inherited classes
		handle_Widget_Base.__init__(self)

		#Internal Variables
		self.myDropTarget = None
		self.dragable = False

		self.columnNames = None
		self.columns = None

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

		if (self.type.lower() == "listdrop"):
			value = self.thing.GetCount() #(int) - How many items are in the drop list

		elif (self.type.lower() == "listfull"):
			if (returnRows):
				value = self.thing.GetItemCount()
			else:
				# value = self.thing.GetColumnCount()
				value = self.columns

		else:
			warnings.warn(f"Add {self.type} to __len__() for {self.__repr__()}", Warning, stacklevel = 2)
			value = 0

		return value

	def build(self, argument_catalogue):
		"""Determiens which build system to use for this handle."""

		def build_listDrop():
			"""Builds a wx choice object."""
			nonlocal self, argument_catalogue

			choices, alphabetic, default = self.getArguments(argument_catalogue, ["choices", "alphabetic", "default"])

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
			self.thing = wx.Choice(self.parent.thing, choices = choices, style = style)
			
			#Set default position
			if (type(default) == str):
				if (default in choices):
					default = choices.index(default)
				else:
					warnings.warn(f"the default was not in the provided list of choices for a {self.type} in {self.__repr__()}", Warning, stacklevel = 4)
					default = None

			if (default == None):
				default = 0

			self.thing.SetSelection(default)

			#Bind the function(s)
			myFunction, myFunctionArgs, myFunctionKwargs = self.getArguments(argument_catalogue, ["myFunction", "myFunctionArgs", "myFunctionKwargs"])
			self.setFunction_click(myFunction, myFunctionArgs, myFunctionKwargs)

		def build_listFull():
			"""Builds a wx choice object."""
			nonlocal self, argument_catalogue

			report, singleSelect, editable = self.getArguments(argument_catalogue, ["report", "singleSelect", "editable"])
			columns, drag, drop, choices = self.getArguments(argument_catalogue, ["columns", "drag", "drop", "choices"])
			columnNames, columnWidth = self.getArguments(argument_catalogue, ["columnNames", "columnWidth"])
			border, rowLines, columnLines, boldHeader = self.getArguments(argument_catalogue, ["border", "rowLines", "columnLines", "boldHeader"])

			#Determine style
			if (report):
				styleList = "wx.LC_REPORT"
			else:
				styleList = "wx.LC_LIST" #Auto calculate columns and rows

			if (border):
				styleList += "|wx.BORDER_SUNKEN"
			if (rowLines):
				styleList += "|wx.LC_HRULES"
			if (columnLines):
				styleList += "|wx.LC_VRULES"

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
				self.thing = self.ListFull_Editable(self.parent.thing, style = styleList)
				self.thing.editable = editable
			else:
				self.thing = wx.ListCtrl(self.parent.thing, style = eval(styleList))

			#Remember key variables
			self.columns = columns
			self.columnNames = columnNames
			self.columnWidth = columnWidth
			self.boldHeader = boldHeader

			#Add Items
			self.setValue(choices)

			#Determine if it's contents are dragable
			if (drag):
				dragLabel, dragDelete, dragCopyOverride, allowExternalAppDelete = self.getArguments(argument_catalogue, ["dragLabel", "dragDelete", "dragCopyOverride", "allowExternalAppDelete"])
				preDragFunction, preDragFunctionArgs, preDragFunctionKwargs = self.getArguments(argument_catalogue, ["preDragFunction", "preDragFunctionArgs", "preDragFunctionKwargs"])
				postDragFunction, postDragFunctionArgs, postDragFunctionKwargs = self.getArguments(argument_catalogue, ["postDragFunction", "postDragFunctionArgs", "postDragFunctionKwargs"])
				
				self.dragable = True
				self.betterBind(wx.EVT_LIST_BEGIN_DRAG, self.thing, self.onDragList_beginDragAway, None, 
					{"label": dragLabel, "deleteOnDrop": dragDelete, "overrideCopy": dragCopyOverride, "allowExternalAppDelete": allowExternalAppDelete})
				
				self.preDragFunction = preDragFunction
				self.preDragFunctionArgs = preDragFunctionArgs
				self.preDragFunctionKwargs = preDragFunctionKwargs

				self.postDragFunction = postDragFunction
				self.postDragFunctionArgs = postDragFunctionArgs
				self.postDragFunctionKwargs = postDragFunctionKwargs

			#Determine if it accepts dropped items
			if (drop):
				dropIndex = self.getArguments(argument_catalogue, ["dropIndex"])
				preDropFunction, preDropFunctionArgs, preDropFunctionKwargs = self.getArguments(argument_catalogue, ["preDropFunction", "preDropFunctionArgs", "preDropFunctionKwargs"])
				postDropFunction, postDropFunctionArgs, postDropFunctionKwargs = self.getArguments(argument_catalogue, ["postDropFunction", "postDropFunctionArgs", "postDropFunctionKwargs"])
				dragOverFunction, dragOverFunctionArgs, postDropFunctionKwargs = self.getArguments(argument_catalogue, ["dragOverFunction", "dragOverFunctionArgs", "postDropFunctionKwargs"])
				
				self.myDropTarget = self.DragTextDropTarget(self.thing, dropIndex,
					preDropFunction = preDropFunction, preDropFunctionArgs = preDropFunctionArgs, preDropFunctionKwargs = preDropFunctionKwargs, 
					postDropFunction = postDropFunction, postDropFunctionArgs = postDropFunctionArgs, postDropFunctionKwargs = postDropFunctionKwargs,
					dragOverFunction = dragOverFunction, dragOverFunctionArgs = dragOverFunctionArgs, dragOverFunctionKwargs = postDropFunctionKwargs)
				self.thing.SetDropTarget(self.myDropTarget)

			#Bind the function(s)
			myFunction, preEditFunction, postEditFunction = self.getArguments(argument_catalogue, ["myFunction", "preEditFunction", "postEditFunction"])
			
			# self.betterBind(wx.EVT_LISTBOX, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
			if (myFunction != None):
				myFunctionArgs, myFunctionKwargs = self.getArguments(argument_catalogue, ["myFunctionArgs", "myFunctionKwargs"])
				self.setFunction_click(myFunction, myFunctionArgs, myFunctionKwargs)

			if (preEditFunction):
				preEditFunctionArgs, preEditFunctionKwargs = self.getArguments(argument_catalogue, ["preEditFunctionArgs", "preEditFunctionKwargs"])
				self.setFunction_preEdit(preEditFunction, preEditFunctionArgs, preEditFunctionKwargs)

			if (postEditFunction):
				postEditFunctionArgs, postEditFunctionKwargs = self.getArguments(argument_catalogue, ["postEditFunctionArgs", "postEditFunctionKwargs"])
				self.setFunction_postEdit(postEditFunction, postEditFunctionArgs, postEditFunctionKwargs)

		def build_listTree():
			"""Builds a wx choice object."""
			nonlocal self, argument_catalogue

			
			choices, drag, drop = self.getArguments(argument_catalogue, ["choices", "drag", "drop"])
			addButton, editable, rowHighlight, root = self.getArguments(argument_catalogue, ["addButton", "editable", "rowHighlight", "root"])
			rowLines, rootLines, variableHeight, selectMultiple = self.getArguments(argument_catalogue, ["rowLines", "rootLines", "variableHeight", "selectMultiple"])

			#Apply Settings
			if (addButton == None):
				style = "wx.TR_NO_BUTTONS"
			else:
				if (addButton):
					style = "wx.TR_HAS_BUTTONS"
				else:
					style = "wx.TR_TWIST_BUTTONS"

			if (editable):
				style += "|wx.TR_EDIT_LABELS"

			if (rowHighlight):
				style += "|wx.TR_FULL_ROW_HIGHLIGHT"

			if (root == None):
				style += "|wx.TR_HIDE_ROOT"

			if (rowLines or rootLines):
				if (rowLines):
					style += "|wx.TR_ROW_LINES"

				if (rootLines and (root != None)):
					style += "|wx.TR_LINES_AT_ROOT"
			else:
				style += "|wx.TR_NO_LINES"

			if (variableHeight):
				style += "|wx.TR_HAS_VARIABLE_ROW_HEIGHT"

			if (selectMultiple):
				style += "|wx.TR_MULTIPLE"
			else:
				style += "|wx.TR_SINGLE"

			#Create the thing to put in the grid
			self.thing = wx.TreeCtrl(self.parent.thing, style = eval(style))
			
			self.setValue({root: choices})

			preRightDragFunction, postRightDragFunction = self.getArguments(argument_catalogue, ["preRightDragFunction", "postRightDragFunction"])
			preDropFunction, postDropFunction, dragOverFunction = self.getArguments(argument_catalogue, ["preDropFunction", "postDropFunction", "dragOverFunction"])

			# #Determine if it's contents are dragable
			# if (drag):
			#   dragLabel, dragDelete, dragCopyOverride, allowExternalAppDelete = self.getArguments(argument_catalogue, ["dragLabel", "dragDelete", "dragCopyOverride", "allowExternalAppDelete"])
			#   preDragFunction, preDragFunctionArgs, preDragFunctionKwargs = self.getArguments(argument_catalogue, ["preDragFunction", "preDragFunctionArgs", "preDragFunctionKwargs"])
			#   postDragFunction, postDragFunctionArgs, postDragFunctionKwargs = self.getArguments(argument_catalogue, ["postDragFunction", "postDragFunctionArgs", "postDragFunctionKwargs"])
				
			#   self.dragable = True
			#   self.betterBind(wx.EVT_TREE_BEGIN_DRAG, self.thing, self.onDragList_beginDragAway, None, 
			#       {"label": dragLabel, "deleteOnDrop": dragDelete, "overrideCopy": dragCopyOverride, "allowExternalAppDelete": allowExternalAppDelete})
				
			#   self.preDragFunction = preDragFunction
			#   self.preDragFunctionArgs = preDragFunctionArgs
			#   self.preDragFunctionKwargs = preDragFunctionKwargs

			#   self.postDragFunction = postDragFunction
			#   self.postDragFunctionArgs = postDragFunctionArgs
			#   self.postDragFunctionKwargs = postDragFunctionKwargs

			# #Determine if it accepts dropped items
			# if (drop):
			#   dropIndex = self.getArguments(argument_catalogue, ["dropIndex"])
			#   preDropFunction, preDropFunctionArgs, preDropFunctionKwargs = self.getArguments(argument_catalogue, ["preDropFunction", "preDropFunctionArgs", "preDropFunctionKwargs"])
			#   postDropFunction, postDropFunctionArgs, postDropFunctionKwargs = self.getArguments(argument_catalogue, ["postDropFunction", "postDropFunctionArgs", "postDropFunctionKwargs"])
			#   dragOverFunction, dragOverFunctionArgs, postDropFunctionKwargs = self.getArguments(argument_catalogue, ["dragOverFunction", "dragOverFunctionArgs", "postDropFunctionKwargs"])
				
			#   self.myDropTarget = self.DragTextDropTarget(self.thing, dropIndex,
			#       preDropFunction = preDropFunction, preDropFunctionArgs = preDropFunctionArgs, preDropFunctionKwargs = preDropFunctionKwargs, 
			#       postDropFunction = postDropFunction, postDropFunctionArgs = postDropFunctionArgs, postDropFunctionKwargs = postDropFunctionKwargs,
			#       dragOverFunction = dragOverFunction, dragOverFunctionArgs = dragOverFunctionArgs, dragOverFunctionKwargs = postDropFunctionKwargs)
			#   self.thing.SetDropTarget(self.myDropTarget)

			#Bind the function(s)
			myFunction, preEditFunction, postEditFunction = self.getArguments(argument_catalogue, ["myFunction", "preEditFunction", "postEditFunction"])
			preCollapseFunction, preExpandFunction = self.getArguments(argument_catalogue, ["preCollapseFunction", "preExpandFunction"])
			postCollapseFunction, postExpandFunction = self.getArguments(argument_catalogue, ["postCollapseFunction", "postExpandFunction"])
			rightClickFunction, middleClickFunction, doubleClickFunction = self.getArguments(argument_catalogue, ["rightClickFunction", "middleClickFunction", "doubleClickFunction"])
			keyDownFunction, toolTipFunction, itemMenuFunction = self.getArguments(argument_catalogue, ["keyDownFunction", "toolTipFunction", "itemMenuFunction"])

			if (myFunction != None):
				myFunctionArgs, myFunctionKwargs = self.getArguments(argument_catalogue, ["myFunctionArgs", "myFunctionKwargs"])
				self.setFunction_postClick(myFunction, myFunctionArgs, myFunctionKwargs)

			if (preEditFunction != None):
				preEditFunctionArgs, preEditFunctionKwargs = self.getArguments(argument_catalogue, ["preEditFunctionArgs", "preEditFunctionKwargs"])
				self.setFunction_preEdit(preEditFunction, preEditFunctionArgs, preEditFunctionKwargs)

			if (postEditFunction != None):
				postEditFunctionArgs, postEditFunctionKwargs = self.getArguments(argument_catalogue, ["postEditFunctionArgs", "postEditFunctionKwargs"])
				self.setFunction_postEdit(postEditFunction, postEditFunctionArgs, postEditFunctionKwargs)

			if (preCollapseFunction != None):
				preCollapseFunctionArgs, preCollapseFunctionKwargs = self.getArguments(argument_catalogue, ["preCollapseFunctionArgs", "preCollapseFunctionKwargs"])
				self.setFunction_collapse(preCollapseFunction, preCollapseFunctionArgs, preCollapseFunctionKwargs)

			if (postCollapseFunction != None):
				postCollapseFunctionArgs, postCollapseFunctionKwargs = self.getArguments(argument_catalogue, ["postCollapseFunctionArgs", "postCollapseFunctionKwargs"])
				self.setFunction_collapse(postCollapseFunction, postCollapseFunctionArgs, postCollapseFunctionKwargs)

			if (preExpandFunction != None):
				preExpandFunctionArgs, preExpandFunctionKwargs = self.getArguments(argument_catalogue, ["preExpandFunctionArgs", "preExpandFunctionKwargs"])
				self.setFunction_expand(preExpandFunction, preExpandFunctionArgs, preExpandFunctionKwargs)

			if (postExpandFunction != None):
				postExpandFunctionArgs, postExpandFunctionKwargs = self.getArguments(argument_catalogue, ["postExpandFunctionArgs", "postExpandFunctionKwargs"])
				self.setFunction_expand(postExpandFunction, postExpandFunctionArgs, postExpandFunctionKwargs)

			if (rightClickFunction != None):
				rightClickFunctionArgs, rightClickFunctionKwargs = self.getArguments(argument_catalogue, ["rightClickFunctionArgs", "rightClickFunctionKwargs"])
				self.setFunction_rightClick(rightClickFunction, rightClickFunctionArgs, rightClickFunctionKwargs)

			if (middleClickFunction != None):
				middleClickFunctionArgs, middleClickFunctionKwargs = self.getArguments(argument_catalogue, ["middleClickFunctionArgs", "middleClickFunctionKwargs"])
				self.setFunction_middleClick(middleClickFunction, middleClickFunctionArgs, middleClickFunctionKwargs)
			
			if (doubleClickFunction != None):
				doubleClickFunctionArgs, doubleClickFunctionKwargs = self.getArguments(argument_catalogue, ["doubleClickFunctionArgs", "doubleClickFunctionKwargs"])
				self.setFunction_doubleClick(doubleClickFunction, doubleClickFunctionArgs, doubleClickFunctionKwargs)

			if (keyDownFunction != None):
				keyDownFunctionArgs, keyDownFunctionKwargs = self.getArguments(argument_catalogue, ["keyDownFunctionArgs", "keyDownFunctionKwargs"])
				self.setFunction_keyDown(keyDownFunction, keyDownFunctionArgs, keyDownFunctionKwargs)

			if (toolTipFunction != None):
				toolTipFunctionArgs, toolTipFunctionKwargs = self.getArguments(argument_catalogue, ["toolTipFunctionArgs", "toolTipFunctionKwargs"])
				self.setFunction_toolTip(toolTipFunction, toolTipFunctionArgs, toolTipFunctionKwargs)
			
			if (itemMenuFunction != None):
				itemMenuFunctionArgs, itemMenuFunctionKwargs = self.getArguments(argument_catalogue, ["itemMenuFunctionArgs", "itemMenuFunctionKwargs"])
				self.setFunction_itemMenu(itemMenuFunction, itemMenuFunctionArgs, itemMenuFunctionKwargs)

		#########################################################

		self.preBuild(argument_catalogue)

		if (self.type.lower() == "listdrop"):
			build_listDrop()
		elif (self.type.lower() == "listfull"):
			build_listFull()
		elif (self.type.lower() == "listtree"):
			build_listTree()
		else:
			warnings.warn(f"Add {self.type} to build() for {self.__repr__()}", Warning, stacklevel = 2)

		self.postBuild(argument_catalogue)

	#Getters
	def getValue(self, event = None):
		"""Returns what the contextual value is for the object associated with this handle."""

		if (self.type.lower() == "listdrop"):
			index = self.thing.GetSelection()
			value = self.thing.GetString(index) #(str) - What is selected in the drop list

		elif (self.type.lower() == "listfull"):
			value = []
			# columnCount = self.thing.GetColumnCount()
			columnCount = self.columns

			row = -1
			while True:
				row = self.thing.GetNextSelected(row)
				if row == -1:
					break
				else:
					subValue = []
					for column in range(columnCount):
						#If the event is a postEdit event, then the value is not applied until after the event is over and not vetoed. (See: http://wxpython-users.1045709.n5.nabble.com/wx-ListCtrl-Problem-editing-td2342724.html)
						if ((event != None) and (event.GetClassName() == "wxListEvent") and (column == event.GetColumn())):
							item = event.GetText()
						else:
							item = self.thing.GetItem(row, column).GetText()
						subValue.append(item) #(list) - What is selected in the first column of the row selected in the full list as strings
					value.append(subValue)

		else:
			warnings.warn(f"Add {self.type} to getValue() for {self.__repr__()}", Warning, stacklevel = 2)
			value = None

		return value

	def getIndex(self, event = None):
		"""Returns what the contextual index is for the object associated with this handle."""

		if (self.type.lower() == "listdrop"):
			value = self.thing.GetSelection() #(int) - The index number of what is selected in the drop list    

		elif (self.type.lower() == "listfull"):
			value = []
			# columnCount = self.thing.GetColumnCount()
			columnCount = self.columns

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
			warnings.warn(f"Add {self.type} to getIndex() for {self.__repr__()}", Warning, stacklevel = 2)
			value = None

		return value

	def getAll(self, event = None):
		"""Returns all the contextual values for the object associated with this handle."""

		if (self.type.lower() == "listdrop"):
			value = []
			n = self.thing.GetCount()
			for i in range(n):
				value.append(self.thing.GetString(i)) #(list) - What is in the drop list as strings

		elif (self.type.lower() == "listfull"):
			value = []
			rowCount = self.thing.GetItemCount()
			# columnCount = self.thing.GetColumnCount()
			columnCount = self.columns

			n = self.thing.GetItemCount()
			for row in range(rowCount):
				subValue = []
				for column in range(columnCount):
					subValue.append(self.thing.GetItem(row, column).GetText()) #(list) - What is in the full list as strings
				value.append(subValue)
	
		else:
			warnings.warn(f"Add {self.type} to getAll() for {self.__repr__()}", Warning, stacklevel = 2)
			value = None

		return value

	#Setters
	def setValue(self, newValue, columns = None, columnNames = None, columnWidth = None, filterNone = False, boldHeader = None, event = None):
		"""Sets the contextual value for the object associated with this handle to what the user supplies."""

		if (self.type.lower() == "listdrop"):
			if (filterNone != None):
				if (filterNone):
					if (None in newValue):
						newValue[:] = [value for value in newValue if value is not None] #Filter out None
				else:
					newValue[:] = [value if (value != None) else "" for value in newValue] #Replace None with blank space

			self.thing.SetItems(newValue) #(list) - What the choice options will now be now

		elif (self.type.lower() == "listfull"):
			# columnCount = self.thing.GetColumnCount()
			columnCount = self.columns
			
			#Account for redefining columns
			if (columns == None):
				columns = self.columns
			else:
				self.columns = columns

			#Account for redefining column names
			if (columnNames == None):
				columnNames = self.columnNames
			else:
				for key, value in columnNames.items():
					self.columnNames[key] = value

			#Account for redefining column widths
			if (columnWidth == None):
				columnWidth = self.columnWidth
			else:
				for key, value in columnWidth.items():
					self.columnWidth[key] = value
			
			#Account for redefining column style
			if (boldHeader == None):
				boldHeader = self.boldHeader
			else:
				self.boldHeader = boldHeader

			#Error Check
			if (not isinstance(newValue, (list, tuple, range, dict))):
				newValue = [newValue]

			if (columns != 1):
				if ((isinstance(newValue, (list, tuple, range))) and (len(newValue) != 0)):
					if (not isinstance(newValue[0], (list, tuple, range))):
						newValue = [newValue]

			if (filterNone != None):
				if (filterNone):
					if (None in newValue):
						newValue[:] = [value for value in newValue if value is not None] #Filter out None
				else:
					newValue[:] = [value if (value != None) else "" for value in newValue] #Replace None with blank space

			#Clear list
			self.thing.ClearAll()

			#Add items
			if (self.thing.InReportView()):
				#Create columns
				for i in range(columns):
					if (i in columnNames):
						name = columnNames[i]
					else:
						name = ""

					if (i in columnWidth):
						self.thing.InsertColumn(i, name, width = columnWidth[i])
					else:
						self.thing.InsertColumn(i, name)

					#Style column
					if (boldHeader):
						item = wx.ListItem()
						font = wx.Font(self.thing.GetClassDefaultAttributes().font)
						font.MakeBold()
						item.SetFont(font)
						self.thing.SetColumn(i, item)

				#Add items
				if (not isinstance(newValue, dict)):
					itemDict = {}
					for row, column in enumerate(newValue):
						if (row not in itemDict):
							itemDict[row] = []

						itemDict[row].extend(column)
				else:
					itemDict = newValue

				#Make sure there are enough rows
				itemCount = self.thing.GetItemCount()
				rowCount = len(list(itemDict.keys()))

				if (itemCount < rowCount):
					for i in range(rowCount - itemCount):
						self.thing.InsertItem(i + 1 + itemCount, "")

				for row, column in itemDict.items():
					if (isinstance(column, str)):
						#Get the column number
						index = [key for key, value in columnNames.items() if value == column]

						#Account for no column found
						if (len(index) == 0):
							warnings.warn(f"There is no column {column} for the list {label} in the column names {columnNames}\nAdding value to the first column instead", Warning, stacklevel = 2)
							column = 0
						else:
							#Choose the first instance of it
							column = index[0]

					#Add contents
					for i, text in enumerate(column):
						#Error check
						if (not isinstance(text, str)):
							text = str(text)

						self.thing.SetItem(row, i, text)

			else:
				#Add items
				newValue.reverse()
				for text in newValue:
					#Error check
					if (not isinstance(text, str)):
						text = str(text)

					self.thing.InsertItem(0, text)

		elif (self.type.lower() == "listtree"):
			if (not isinstance(newValue, dict)):
				errorMessage = f"'newValue' must be a dict, not a {type(newValue)} in setValue() for {self.__repr__()}"
				raise KeyError(errorMessage)

			if (len(newValue) != 1):
				errorMessage = f"There must be only one root for 'newValue' not {len(newValue)} in setValue() for {self.__repr__()}"
				raise ValueError(errorMessage)

			rootThing = self.thing.AddRoot(str(list(newValue.keys())[0]))
			self.thing.SetItemData(rootThing, ("key", "value"))

			for root, branches in newValue.items():
				self.appendValue(branches, rootThing)

		else:
			warnings.warn(f"Add {self.type} to setValue() for {self.__repr__()}", Warning, stacklevel = 2)

	def setSelection(self, newValue, event = None):
		"""Sets the contextual value for the object associated with this handle to what the user supplies."""

		if (self.type.lower() == "listdrop"):
			if (newValue != None):
				if (isinstance(newValue, str)):
					newValue = self.thing.FindString(newValue)

				if (newValue == None):
					errorMessage = f"Invalid drop list selection in setSelection() for {self.__repr__()}"
					raise ValueError(errorMessage)
			else:
				newValue = 0
				
			self.thing.SetSelection(newValue) #(int) - What the choice options will now be

		elif (self.type.lower() == "listfull"):
			if (newValue != None):
				if (isinstance(newValue, str)):
					newValue = self.thing.FindItem(-1, newValue)

				if (newValue == None):
					errorMessage = f"Invalid drop list selection in setSelection() for {self.__repr__()}"
					raise ValueError(errorMessage)
			else:
				newValue = 0
				
			self.thing.Select(newValue) #(int) - What the choice options will now be


		else:
			warnings.warn(f"Add {self.type} to setSelection() for {self.__repr__()}", Warning, stacklevel = 2)

	def appendValue(self, newValue, where = -1):
		"""Appends the given value to the current contextual value for this handle."""

		if (self.type.lower() == "listtree"):
			if (not isinstance(where, wx.TreeCtrl)):
				#Find the root
				pass

			#Account for multiple items on the same level
			if (isinstance(newValue, (list, tuple, range))):
				for item in newValue:
					self.appendValue(item, where)
			else:
				#Account for new branches
				if (isinstance(newValue, dict)):
					for key, value in newValue.items():
						if (key != None):
							branch = self.thing.AppendItem(where, str(key))

						if (value != None):
							self.appendValue(value, branch)
				else:
					if (newValue != None):
						branch = self.thing.AppendItem(where, str(newValue))
		else:
			warnings.warn(f"Add {self.type} to setSelection() for {self.__repr__()}", Warning, stacklevel = 2)

	#Change Settings
	def setFunction_preClick(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type.lower() == "listtree"):
			self.betterBind(wx.EVT_TREE_SEL_CHANGING, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		else:
			warnings.warn(f"Add {self.type} to setFunction_click() for {self.__repr__()}", Warning, stacklevel = 2)
			
	def setFunction_postClick(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type.lower() == "listdrop"):
			self.betterBind(wx.EVT_CHOICE, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		elif (self.type.lower() == "listfull"):
			self.betterBind(wx.EVT_LIST_ITEM_SELECTED, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		elif (self.type.lower() == "listtree"):
			self.betterBind(wx.EVT_TREE_SEL_CHANGED, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		else:
			warnings.warn(f"Add {self.type} to setFunction_click() for {self.__repr__()}", Warning, stacklevel = 2)
			
	def setFunction_click(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		self.setFunction_postClick(myFunction = myFunction, myFunctionArgs = myFunctionArgs, myFunctionKwargs = myFunctionKwargs)

	def setFunction_preEdit(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type.lower() == "listfull"):
			self.betterBind(wx.EVT_LIST_BEGIN_LABEL_EDIT, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		elif (self.type.lower() == "listtree"):
			self.betterBind(wx.EVT_TREE_BEGIN_LABEL_EDIT, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		else:
			warnings.warn(f"Add {self.type} to EVT_LIST_BEGIN_LABEL_EDIT() for {self.__repr__()}", Warning, stacklevel = 2)
			
	def setFunction_postEdit(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type.lower() == "listfull"):
			self.betterBind(wx.EVT_LIST_END_LABEL_EDIT, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		elif (self.type.lower() == "listtree"):
			self.betterBind(wx.EVT_TREE_END_LABEL_EDIT, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		else:
			warnings.warn(f"Add {self.type} to setFunction_postEdit() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_preDrag(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type.lower() == "listfull"):
			if (not self.dragable):
				warnings.warn(f"'drag' was not enabled for {self.__repr__()} upon creation", Warning, stacklevel = 2)
			else:
				self.preDragFunction = myFunction
				self.preDragFunctionArgs = myFunctionArgs
				self.preDragFunctionKwargs = myFunctionKwargs
		else:
			warnings.warn(f"Add {self.type} to setFunction_preDrag() for {self.__repr__()}", Warning, stacklevel = 2)
			
	def setFunction_postDrag(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type.lower() == "listfull"):
			if (not self.dragable):
				warnings.warn(f"'drag' was not enabled for {self.__repr__()} upon creation", Warning, stacklevel = 2)
			else:
				self.postDragFunction = myFunction
				self.postDragFunctionArgs = myFunctionArgs
				self.postDragFunctionKwargs = myFunctionKwargs
		else:
			warnings.warn(f"Add {self.type} to setFunction_postDrag() for {self.__repr__()}", Warning, stacklevel = 2)
			
	def setFunction_preDrop(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type.lower() == "listfull"):
			if (self.myDropTarget == None):
				warnings.warn(f"'drop' was not enabled for {self.__repr__()} upon creation", Warning, stacklevel = 2)
			else:
				self.myDropTarget.preDropFunction = myFunction
				self.myDropTarget.preDropFunctionArgs = myFunctionArgs
				self.myDropTarget.preDropFunctionKwargs = myFunctionKwargs
		else:
			warnings.warn(f"Add {self.type} to setFunction_preDrop() for {self.__repr__()}", Warning, stacklevel = 2)
			
	def setFunction_postDrop(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type.lower() == "listfull"):
			if (self.myDropTarget == None):
				warnings.warn(f"'drop' was not enabled for {self.__repr__()} upon creation", Warning, stacklevel = 2)
			else:
				self.myDropTarget.postDropFunction = myFunction
				self.myDropTarget.postDropFunctionArgs = myFunctionArgs
				self.myDropTarget.postDropFunctionKwargs = myFunctionKwargs
		else:
			warnings.warn(f"Add {self.type} to setFunction_postDrop() for {self.__repr__()}", Warning, stacklevel = 2)
			
	def setFunction_dragOver(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type.lower() == "listfull"):
			if (self.myDropTarget == None):
				warnings.warn(f"'drop' was not enabled for {self.__repr__()} upon creation", Warning, stacklevel = 2)
			else:
				self.myDropTarget.dragOverFunction = myFunction
				self.myDropTarget.dragOverFunctionArgs = myFunctionArgs
				self.myDropTarget.dragOverFunctionKwargs = myFunctionKwargs
		else:
			warnings.warn(f"Add {self.type} to setFunction_dragOver() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_preCollapse(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type.lower() == "listtree"):
			self.betterBind(wx.EVT_TREE_ITEM_COLLAPSING, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		else:
			warnings.warn(f"Add {self.type} to setFunction_preCollapse() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_postCollapse(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type.lower() == "listtree"):
			self.betterBind(wx.EVT_TREE_ITEM_COLLAPSED, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		else:
			warnings.warn(f"Add {self.type} to setFunction_postCollapse() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_preExpand(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type.lower() == "listtree"):
			self.betterBind(wx.EVT_TREE_ITEM_EXPANDING, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		else:
			warnings.warn(f"Add {self.type} to setFunction_preExpand() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_postExpand(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type.lower() == "listtree"):
			self.betterBind(wx.EVT_TREE_ITEM_EXPANDED, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		else:
			warnings.warn(f"Add {self.type} to setFunction_postExpand() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_rightClick(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type.lower() == "listtree"):
			self.betterBind(wx.EVT_TREE_ITEM_RIGHT_CLICK, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		elif (self.type.lower() == "listfull"):
			self.betterBind(wx.EVT_RIGHT_DOWN, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		else:
			warnings.warn(f"Add {self.type} to setFunction_rightClick() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_middleClick(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type.lower() == "listtree"):
			self.betterBind(wx.EVT_TREE_ITEM_MIDDLE_CLICK, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		else:
			warnings.warn(f"Add {self.type} to setFunction_middleClick() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_doubleClick(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type.lower() == "listtree"):
			self.betterBind(wx.EVT_TREE_ITEM_ACTIVATED, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		else:
			warnings.warn(f"Add {self.type} to setFunction_middleClick() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_keyDown(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type.lower() == "listtree"):
			self.betterBind(wx.EVT_TREE_KEY_DOWN, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		else:
			warnings.warn(f"Add {self.type} to setFunction_keyDown() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_toolTip(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type.lower() == "listtree"):
			self.betterBind(wx.EVT_TREE_ITEM_GETTOOLTIP, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		else:
			warnings.warn(f"Add {self.type} to setFunction_toolTip() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_itemMenu(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type.lower() == "listtree"):
			self.betterBind(wx.EVT_TREE_ITEM_MENU, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		else:
			warnings.warn(f"Add {self.type} to setFunction_toolTip() for {self.__repr__()}", Warning, stacklevel = 2)

	def setReadOnly(self, state = True):
		"""Sets the contextual readOnly for the object associated with this handle to what the user supplies."""

		if (self.type.lower() == "listdrop"):
			self.setDisable(state)
		else:
			warnings.warn(f"Add {self.type} to setReadOnly() for {self.__repr__()}", Warning, stacklevel = 2)

	def setRowColor(self, row = None, color = "white"):
		"""Sets the contextual row color for the object associated with this handle to what the user supplies.

		row (int)   - Which row to change the color of
			- If list: Will change the color of all rows in the list
			- If None: Will change the color of all rows
			- If slice: Will change the color of all rows in the slice
		color (str) - What color to make the rows
			- If tuple: Will interperet as (Red, Green, Blue). Values can be integers from 0 to 255 or floats from 0.0 to 1.0

		Example Input: setRowColor(0, color = "grey")
		Example Input: setRowColor(0, color = (255, 0, 0))
		Example Input: setRowColor(0, color = (0.5, 0.5, 0.5))
		Example Input: setRowColor(slice(None, None, None))
		Example Input: setRowColor(slice(1, 3, None))
		Example Input: setRowColor(slice(None, None, 2))
		"""

		if (self.type.lower() == "listfull"):
			colorHandle = self.getColor(color)
			rowCount = self.thing.GetItemCount()

			if (row == None):
				rowList = range(rowCount)

			elif (isinstance(row, slice)):				
				if (row.start != None):
					if (row.start > rowCount):
						errorMessage = f"{row.start} is less than {rowCount}; not enough rows for start in setRowColor for {self.__repr__()}"
						raise KeyError(errorMessage)
					start = row.start
				else:
					start = 0
				
				if (row.stop != None):
					if (row.stop > rowCount):
						errorMessage = f"{row.stop} is less than {rowCount}; not enough rows for stop in setRowColor for {self.__repr__()}"
						raise KeyError(errorMessage)
					stop = row.stop
				else:
					stop = rowCount

				if (row.step != None):
					step = row.step
				else:
					step = 1

				rowList = range(start, stop, step)

			else:
				rowList = [row]

			for i in rowList:
				self.thing.SetItemBackgroundColour(i, colorHandle)
			
		else:
			warnings.warn(f"Add {self.type} to setRowColor() for {self.__repr__()}", Warning, stacklevel = 2)



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

		preDragFunction = self.preDragFunction
		preDragFunctionArgs = self.preDragFunctionArgs
		preDragFunctionKwargs = self.preDragFunctionKwargs

		postDragFunction = self.postDragFunction
		postDragFunctionArgs = self.postDragFunctionArgs
		postDragFunctionKwargs = self.postDragFunctionKwargs

		#Get Values
		index = event.GetIndex()
		originList = event.GetEventObject()
		textToDrag = originList.GetItemText(index)

		#Create drag objects
		textToDrag_object = wx.TextDataObject(textToDrag)
		originList_object = wx.DropSource(originList)

		#Catalogue dragObject
		self.parent[label] = textToDrag

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
		del self.parent[label]
		dragDropDestination = None

		#Run post-functions
		runFunction(postDragFunction, postDragFunctionArgs, postDragFunctionKwargs)

		event.Skip()

	# def onEditList_checkReadOnly(self, event, editable):
	#   """Used to make sure the user is allowed to edit the current item.
	#   Special thanks to ErwinP for how to edit certain columns on https://stackoverflow.com/questions/12806542/wx-listctrl-with-texteditmixin-disable-editing-of-selected-cells
	#   """

	#   #Get the current selection's column
	#   thing = self.getObjectWithEvent(event)
	#   column = self.thing.GetFocusedItem()

	#   if (column not in editable):
	#       event.Veto()
	#   else:
	#       if (not editable[column]):
	#           event.Veto()
	#       else:

	#   event.Skip()

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

		#Defaults
		self.exclude = None
		self.previousValue = None

	def __len__(self, returnMax = True):
		"""Returns what the contextual length is for the object associated with this handle.

		returnMax(bool) - Determines what is returned for 2D objects
			- If True: Returns the max of the object range
			- If False: Returns the min of the object range
		"""

		if (self.type.lower() == "inputbox"):
			value = len(self.getValue())

		elif (self.type.lower() == "inputspinner"):
			if (returnMax):
				value = self.thing.GetMax()
			else:
				value = self.thing.GetMin()

		elif (self.type.lower() == "slider"):
			if (returnMax):
				value = self.thing.GetMax()
			else:
				value = self.thing.GetMin()

		elif (self.type.lower() == "inputsearch"):
			value = len(self.getValue())

		else:
			warnings.warn(f"Add {self.type} to __len__() for {self.__repr__()}", Warning, stacklevel = 2)
			value = 0

		return value

	def build(self, argument_catalogue):
		"""Determiens which build system to use for this handle."""

		def build_slider():
			"""Builds a wx slider object."""
			nonlocal self, argument_catalogue

			vertical = self.getArguments(argument_catalogue, "vertical")
			myInitial, myMin, myMax = self.getArguments(argument_catalogue, ["myInitial", "myMin", "myMax"])

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
			self.thing = wx.Slider(self.parent.thing, value = myInitial, minValue = myMin, maxValue = myMax, style = eval(styles))

			#Bind the function(s)
			myFunction = self.getArguments(argument_catalogue, "myFunction")
			if (myFunction != None):
				myFunctionArgs, myFunctionKwargs = self.getArguments(argument_catalogue, ["myFunctionArgs", "myFunctionKwargs"])
				self.setFunction_postEdit(myFunction, myFunctionArgs, myFunctionKwargs)

			# EVT_SCROLL_TOP
			# EVT_SCROLL_BOTTOM
			# EVT_SCROLL_LINEUP
			# EVT_SCROLL_LINEDOWN
			# EVT_SCROLL_PAGEUP
			# EVT_SCROLL_PAGEDOWN
			# EVT_SCROLL_THUMBTRACK
			# EVT_SCROLL_THUMBRELEASE

		def build_inputBox():
			"""Builds a wx text control or ip address control object."""
			nonlocal self, argument_catalogue

			password, alpha, readOnly, tab, wrap = self.getArguments(argument_catalogue, ["password", "alpha", "readOnly", "tab", "wrap"])
			text, ipAddress, maxLength = self.getArguments(argument_catalogue, ["text", "ipAddress", "maxLength"])

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
				self.thing = wx.lib.masked.ipaddrctrl.IpAddrCtrl(self.parent.thing, wx.ID_ANY, style = eval(styles))

				if (text != wx.EmptyString):
					self.thing.SetValue(text)
			else:
				self.thing = wx.TextCtrl(self.parent.thing, value = text, style = eval(styles))

				#Set maximum length
				if (maxLength != None):
					self.thing.SetMaxLength(maxLength)

			#flags += "|wx.RESERVE_SPACE_EVEN_IF_HIDDEN"

			#Bind the function(s)
			myFunction, enterFunction, postEditFunction, preEditFunction = self.getArguments(argument_catalogue, ["myFunction", "enterFunction", "postEditFunction", "preEditFunction"])
			
			#self.betterBind(wx.EVT_CHAR, self.thing, enterFunction, enterFunctionArgs, enterFunctionKwargs)
			#self.betterBind(wx.EVT_KEY_UP, self.thing, self.testFunction, myFunctionArgs, myFunctionKwargs)
			if (myFunction != None):
				myFunctionArgs, myFunctionKwargs = self.getArguments(argument_catalogue, ["myFunctionArgs", "myFunctionKwargs"])
				self.setFunction_click(myFunction, myFunctionArgs, myFunctionKwargs)

			if (enterFunction != None):
				enterFunctionArgs, enterFunctionKwargs = self.getArguments(argument_catalogue, ["enterFunctionArgs", "enterFunctionKwargs"])
				self.setFunction_enter(enterFunction, enterFunctionArgs, enterFunctionKwargs)
			
			if (postEditFunction != None):
				postEditFunctionArgs, postEditFunctionKwargs = self.getArguments(argument_catalogue, ["postEditFunctionArgs", "postEditFunctionKwargs"])
				self.setFunction_postEdit(postEditFunction, postEditFunctionArgs, postEditFunctionKwargs)
			
			if (preEditFunction != None):
				preEditFunctionArgs, preEditFunctionKwargs = self.getArguments(argument_catalogue, ["preEditFunctionArgs", "preEditFunctionKwargs"])
				self.setFunction_preEdit(preEditFunction, preEditFunctionArgs, preEditFunctionKwargs)

		def build_inputSearch():
			"""Builds a wx search control object."""
			nonlocal self, argument_catalogue

			myFunction, searchFunction, cancelFunction = self.getArguments(argument_catalogue, ["myFunction", "searchFunction", "cancelFunction"])

			#Create the thing to put in the grid
			self.thing = wx.SearchCtrl(self.parent.thing, value = wx.EmptyString, style = 0)

			#Determine if additional features are enabled
			if (searchFunction != None):
				self.thing.ShowSearchButton(True)
			if (cancelFunction != None):
				self.thing.ShowCancelButton(True)

			#Bind the function(s)
			if (myFunction != None):
				myFunctionArgs, myFunctionKwargs = self.getArguments(argument_catalogue, ["myFunctionArgs", "myFunctionKwargs"])
				self.setFunction_postEdit(myFunction, myFunctionArgs, myFunctionKwargs)

			if (searchFunction != None):
				searchFunctionArgs, searchFunctionKwargs = self.getArguments(argument_catalogue, ["searchFunctionArgs", "searchFunctionKwargs"])
				self.setFunction_search(searchFunction, searchFunctionArgs, searchFunctionKwargs)
			
			if (cancelFunction != None):
				cancelFunctionArgs, cancelFunctionKwargs = self.getArguments(argument_catalogue, ["cancelFunctionArgs", "cancelFunctionKwargs"])
				self.setFunction_cancel(cancelFunction, cancelFunctionArgs, cancelFunctionKwargs)

		def build_inputSpinner():
			"""Builds a wx search control object."""
			nonlocal self, argument_catalogue

			useFloat, readOnly, increment, digits, size = self.getArguments(argument_catalogue, ["useFloat", "readOnly", "increment", "digits", "size"])
			myInitial, myMin, myMax, maxSize, minSize, exclude = self.getArguments(argument_catalogue, ["myInitial", "myMin", "myMax", "maxSize", "minSize", "exclude"])

			#Remember values
			self.exclude = exclude

			#wx.SP_ARROW_KEYS: The user can use arrow keys to change the value.
			#wx.SP_WRAP: The value wraps at the minimum and maximum.
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

				self.thing = wx.lib.agw.floatspin.FloatSpin(self.parent.thing, wx.ID_ANY, wx.DefaultPosition, size, wx.SP_ARROW_KEYS|wx.SP_WRAP, myInitial, myMin, myMax, increment, digits, eval(style))
			else:
				if (increment != None):
					style = "wx.lib.agw.floatspin.FS_LEFT"
					self.thing = wx.lib.agw.floatspin.FloatSpin(self.parent.thing, wx.ID_ANY, wx.DefaultPosition, size, wx.SP_ARROW_KEYS|wx.SP_WRAP, myInitial, myMin, myMax, increment, -1, eval(style))
					self.thing.SetDigits(0)
				else:
					self.thing = wx.SpinCtrl(self.parent.thing, value = wx.EmptyString, size = size, style = eval(styles), min = myMin, max = myMax, initial = myInitial)

				if (readOnly):
					self.thing.SetReadOnly()

			#Determine size constraints
			if (maxSize != None):
				self.thing.SetMaxSize(maxSize)

			if (minSize != None):
				self.thing.SetMinSize(minSize)

			# print(label, self.thing.GetBestSize())
			# self.thing.SetMinSize(self.thing.GetBestSize())
			# self.thing.SetMaxSize(self.thing.GetBestSize())

			#Remember values
			self.previousValue = self.thing.GetValue()

			#Bind the function(s)
			myFunction, changeTextFunction = self.getArguments(argument_catalogue, ["myFunction", "changeTextFunction"])

			if (myFunction != None):
				myFunctionArgs, myFunctionKwargs = self.getArguments(argument_catalogue, ["myFunctionArgs", "myFunctionKwargs"])
				self.betterBind(wx.EVT_SPINCTRL, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
	
			if (changeTextFunction != None):
				if (isinstance(changeTextFunction, bool)):
					if (changeTextFunction and (myFunction != None)):
						self.betterBind(wx.EVT_TEXT, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
				else:
					changeTextFunctionArgs, changeTextFunctionKwargs = self.getArguments(argument_catalogue, ["changeTextFunctionArgs", "changeTextFunctionKwargs"])
					self.betterBind(wx.EVT_TEXT, self.thing, changeTextFunction, changeTextFunctionArgs, changeTextFunctionKwargs)

			if (not ((self.exclude == None) or (isinstance(self.exclude, (list, tuple, range)) and (len(self.exclude) == 0)))):
				self.betterBind(wx.EVT_KILL_FOCUS, self.thing, self.onCheckValue_exclude)
		
		#########################################################

		self.preBuild(argument_catalogue)

		if (self.type.lower() == "inputbox"):
			build_inputBox()
		elif (self.type.lower() == "inputspinner"):
			build_inputSpinner()
		elif (self.type.lower() == "slider"):
			build_slider()
		elif (self.type.lower() == "inputsearch"):
			build_inputSearch()
		else:
			warnings.warn(f"Add {self.type} to build() for {self.__repr__()}", Warning, stacklevel = 2)

		self.postBuild(argument_catalogue)

	#Getters
	def getValue(self, event = None):
		"""Returns what the contextual value is for the object associated with this handle."""

		if (self.type.lower() == "inputbox"):
			value = self.thing.GetValue() #(str) - What the text currently says

		elif (self.type.lower() == "inputspinner"):
			value = self.thing.GetValue() #(str) - What is in the spin box

		elif (self.type.lower() == "slider"):
			value = self.thing.GetValue() #(str) - What is in the spin box

		elif (self.type.lower() == "inputsearch"):
			value = self.thing.GetValue() #(str) - What is in the search box

		else:
			warnings.warn(f"Add {self.type} to getValue() for {self.__repr__()}", Warning, stacklevel = 2)
			value = None

		return value

	#Setters
	def setValue(self, newValue, event = None):
		"""Sets the contextual value for the object associated with this handle to what the user supplies."""

		if (self.type.lower() == "inputbox"):
			if (newValue == None):
				newValue = "" #Filter None as blank text
			self.thing.SetValue(newValue) #(str) - What will be shown in the text box

		elif (self.type.lower() == "inputspinner"):
			self.thing.SetValue(newValue) #(int / float) - What will be shown in the input box

		elif (self.type.lower() == "slider"):
			self.thing.SetValue(newValue) #(int / float) - Where the slider position will be

		elif (self.type.lower() == "inputsearch"):
			if (newValue == None):
				newValue = "" #Filter None as blank text
			self.thing.SetValue(newValue) #(str) - What will be shown in the search box

		else:
			warnings.warn(f"Add {self.type} to setValue() for {self.__repr__()}", Warning, stacklevel = 2)

	#Change Settings
	def setFunction_click(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type.lower() == "inputbox"):
			self.betterBind(wx.EVT_TEXT, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)

		elif (self.type.lower() == "inputspinner"):
			self.betterBind(wx.EVT_SPINCTRL, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		else:
			warnings.warn(f"Add {self.type} to setFunction_click() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_enter(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type.lower() == "inputbox"):
			self.keyBind("enter", myFunction, myFunctionArgs, myFunctionKwargs)
		else:
			warnings.warn(f"Add {self.type} to setFunction_enter() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_preEdit(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type.lower() == "inputbox"):
			self.betterBind(wx.EVT_SET_FOCUS, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		else:
			warnings.warn(f"Add {self.type} to setFunction_preEdit() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_postEdit(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type.lower() == "inputbox"):
			self.betterBind(wx.EVT_KILL_FOCUS, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)

		elif (self.type.lower() == "inputspinner"):
			self.betterBind(wx.EVT_KILL_FOCUS, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)

			if (not ((self.exclude == None) or (isinstance(self.exclude, (list, tuple, range)) and (len(self.exclude) == 0)))):
				self.betterBind(wx.EVT_KILL_FOCUS, self.thing, self.onCheckValue_exclude, rebind = True)

		elif (self.type.lower() == "inputsearch"):
			self.betterBind(wx.EVT_TEXT_ENTER, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)

		elif (self.type.lower() == "slider"):
			self.betterBind(wx.EVT_SCROLL_CHANGED, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		else:
			warnings.warn(f"Add {self.type} to setFunction_postEdit() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_search(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type.lower() == "inputsearch"):
			self.betterBind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		else:
			warnings.warn(f"Add {self.type} to setFunction_preEdit() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_cancel(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type.lower() == "inputsearch"):
			self.betterBind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		else:
			warnings.warn(f"Add {self.type} to setFunction_preEdit() for {self.__repr__()}", Warning, stacklevel = 2)

	def setMin(self, newValue):
		"""Sets the contextual minimum for the object associated with this handle to what the user supplies."""

		if (self.type.lower() == "inputspinner"):
			self.thing.SetMin(newValue) #(int / float) - What the min value will be for the the input box

		elif (self.type.lower() == "slider"):
			self.thing.SetMin(newValue) #(int / float) - What the min slider position will be

		else:
			warnings.warn(f"Add {self.type} to setMin() for {self.__repr__()}", Warning, stacklevel = 2)

	def setMax(self, newValue):
		"""Sets the contextual maximum for the object associated with this handle to what the user supplies."""

		if (self.type.lower() == "inputspinner"):
			self.thing.SetMax(newValue) #(int / float) - What the max value will be for the the input box

		elif (self.type.lower() == "slider"):
			self.thing.SetMax(newValue) #(int / float) - What the max slider position will be

		else:
			warnings.warn(f"Add {self.type} to setMax() for {self.__repr__()}", Warning, stacklevel = 2)

	def setReadOnly(self, state = True):
		"""Sets the contextual readOnly for the object associated with this handle to what the user supplies."""

		if (self.type.lower() == "inputbox"):
			self.thing.SetEditable(not state)

		elif (self.type.lower() == "inputspinner"):
			self.thing.Enable(not state)

		else:
			warnings.warn(f"Add {self.type} to setReadOnly() for {self.__repr__()}", Warning, stacklevel = 2)

	def onCheckValue_exclude(self, event):
		"""Checks the current value to make sure it is valid."""

		if (self.type.lower() == "inputspinner"):
			if (self.exclude != None):
				#Error Check
				if (not isinstance(self.exclude, (list, tuple, range))):
					warnings.warn(f"'exclude' must be a list or tuple for {self.__repr__()}", Warning, stacklevel = 2)
					event.Skip()
					return

				#Setup
				value = self.getValue()
				if (value > self.previousValue):
					increment = 1
				else:
					increment = -1

				#Get Valid Entry
				if (value in self.exclude):
					while value in self.exclude:
						value += increment
					self.setValue(value)

				#Remember current value
				self.previousValue = value
		else:
			warnings.warn(f"Add {self.type} to onCheckValue_exclude() for {self.__repr__()}", Warning, stacklevel = 2)

		event.Skip()

class handle_WidgetButton(handle_Widget_Base):
	"""A handle for working with button widgets."""

	def __init__(self):
		"""Initializes defaults."""

		#Initialize inherited classes
		handle_Widget_Base.__init__(self)

	def __len__(self):
		"""Returns what the contextual length is for the object associated with this handle."""

		if (self.type.lower() == "buttoncheck"):
			value = len(self.thing.GetLabel()) #(int) - The length of the text by the check box

		elif (self.type.lower() == "buttonradio"):
			value = len(self.thing.GetLabel()) #(int) - The length of the text by the radio button

		elif (self.type.lower() == "buttontoggle"):
			value = len(self.thing.GetLabel()) #(int) - The length of the text in the toggle button

		elif (self.type.lower() == "buttonradiobox"):
			value = self.thing.GetCount() #(int) - How many items are in the check list

		elif (self.type.lower() == "checklist"):
			value = self.thing.GetCount() #(int) - How many items are in the check list

		elif (self.type.lower() == "button"):
			value = len(self.getValue()) #(int) - The length of the text in the button

		elif (self.type.lower() == "buttonimage"):
			value = len(self.getValue()) #(int) - The length of the text in the image button

		else:
			warnings.warn(f"Add {self.type} to __len__() for {self.__repr__()}", Warning, stacklevel = 2)
			value = 0

		return value

	def build(self, argument_catalogue):
		"""Determiens which build system to use for this handle."""

		def build_button():
			"""Builds a wx button object."""
			nonlocal self, argument_catalogue

			text, myFunction = self.getArguments(argument_catalogue, ["text", "myFunction"])

			#Create the thing to put in the grid
			self.thing = wx.Button(self.parent.thing, label = text, style = 0)

			#Bind the function(s)
			if (myFunction != None):
				myFunctionArgs, myFunctionKwargs = self.getArguments(argument_catalogue, ["myFunctionArgs", "myFunctionKwargs"])
				self.setFunction_click(myFunction, myFunctionArgs, myFunctionKwargs)

		def build_buttonToggle():
			"""Builds a wx toggle button object."""
			nonlocal self, argument_catalogue

			text, myFunction = self.getArguments(argument_catalogue, ["text", "myFunction"])

			#Create the thing to put in the grid
			self.thing = wx.ToggleButton(self.parent.thing, label = text, style = 0)
			self.thing.SetValue(True) 

			#Bind the function(s)
			if (myFunction != None):
				myFunctionArgs, myFunctionKwargs = self.getArguments(argument_catalogue, ["myFunctionArgs", "myFunctionKwargs"])
				self.setFunction_click(myFunction, myFunctionArgs, myFunctionKwargs)

		def build_buttonCheck():
			"""Builds a wx check box object."""
			nonlocal self, argument_catalogue

			text, default, myFunction = self.getArguments(argument_catalogue, ["text", "default", "myFunction"])

			#Create the thing to put in the grid
			self.thing = wx.CheckBox(self.parent.thing, label = text, style = 0)

			#Determine if it is on by default
			self.thing.SetValue(default)

			#Bind the function(s)
			if (myFunction != None):
				myFunctionArgs, myFunctionKwargs = self.getArguments(argument_catalogue, ["myFunctionArgs", "myFunctionKwargs"])
				self.setFunction_click(myFunction, myFunctionArgs, myFunctionKwargs)

		def build_checkList():
			"""Builds a wx check list box object."""
			nonlocal self, argument_catalogue

			choices, multiple, sort, myFunction = self.getArguments(argument_catalogue, ["choices", "multiple", "sort", "myFunction"])

			#Ensure that the choices given are a list or tuple
			if (not isinstance(choices, (list, tuple, range))):
				choices = [choices]

			#Ensure that the choices are all strings
			choices = [str(item) for item in choices]

			#Apply settings
			styles = "wx.LB_NEEDED_SB"

			if (multiple):
				styles += "|wx.LB_MULTIPLE"
			
			if (sort):
				styles += "|wx.LB_SORT"
		
			#Create the thing to put in the grid
			self.thing = wx.CheckListBox(self.parent.thing, choices = choices, style = eval(styles))

			#Bind the function(s)
			if (myFunction != None):
				myFunctionArgs, myFunctionKwargs = self.getArguments(argument_catalogue, ["myFunctionArgs", "myFunctionKwargs"])
				self.setFunction_click(myFunction, myFunctionArgs, myFunctionKwargs)

		def build_buttonRadio():
			"""Builds a wx radio button object."""
			nonlocal self, argument_catalogue

			groupStart, text, default, myFunction = self.getArguments(argument_catalogue, ["groupStart", "text", "default", "myFunction"])

			#Determine if this is the start of a new radio button group
			if (groupStart):
				group = wx.RB_GROUP
			else:
				group = 0
		
			#Create the thing to put in the grid
			self.thing = wx.RadioButton(self.parent.thing, label = text, style = group)

			#Determine if it is turned on by default
			self.thing.SetValue(default)

			#Bind the function(s)
			if (myFunction != None):
				myFunctionArgs, myFunctionKwargs = self.getArguments(argument_catalogue, ["myFunctionArgs", "myFunctionKwargs"])
				self.setFunction_click(myFunction, myFunctionArgs, myFunctionKwargs)

		def build_buttonRadioBox():
			"""Builds a wx radio box object."""
			nonlocal self, argument_catalogue

			choices, vertical, title, default, maximum, myFunction = self.getArguments(argument_catalogue, ["choices", "vertical", "title", "default", "maximum", "myFunction"])

			#Ensure that the choices given are a list or tuple
			if (not isinstance(choices, (list, tuple, range))):
				choices = [choices]

			#Ensure that the choices are all strings
			choices = [str(item) for item in choices]

			#Determine orientation
			if (vertical):
				direction = wx.RA_SPECIFY_COLS
			else:
				direction = wx.RA_SPECIFY_ROWS

			if (maximum < 0):
				maximum = 0


			#Create the thing to put in the grid
			self.thing = wx.RadioBox(self.parent.thing, label = title, choices = choices, majorDimension = maximum, style = direction)

			#Set default position
			if (len(choices) != 0):
				if (type(default) == str):
					if (default in choices):
						default = choices.index(default)

				if (default == None):
					default = 0

				self.thing.SetSelection(default)

			#Bind the function(s)
			if (myFunction != None):
				myFunctionArgs, myFunctionKwargs = self.getArguments(argument_catalogue, ["myFunctionArgs", "myFunctionKwargs"])
				self.setFunction_click(myFunction, myFunctionArgs, myFunctionKwargs)

		def build_buttonImage():
			"""Builds a wx bitmap button object."""
			nonlocal self, argument_catalogue

			def imageCheck(imagePath):
				"""Determines what image to use."""
				nonlocal self

				if ((imagePath != "") and (imagePath != None)):
					if (not os.path.exists(imagePath)):
						return self.getImage("error", internal = True)
					return self.getImage(imagePath)
				else:
					return None

			#########################################################

			idlePath, disabledPath, selectedPath, text = self.getArguments(argument_catalogue, ["idlePath", "disabledPath", "selectedPath", "text"])
			focusPath, hoverPath, toggle, myFunction = self.getArguments(argument_catalogue, ["focusPath", "hoverPath", "toggle", "myFunction"])

			# wx.BU_LEFT: Left-justifies the bitmap label.
			# wx.BU_TOP: Aligns the bitmap label to the top of the button.
			# wx.BU_RIGHT: Right-justifies the bitmap label.
			# wx.BU_BOTTOM: Aligns the bitmap label to the bottom of the button.

			#Error Check
			image = imageCheck(idlePath)
			if (image == None):
				image = self.getImage(None)

			#Remember values
			self.toggle = toggle

			#Create the thing to put in the grid
			if (text != None):
				if (toggle):
					self.thing = wx.lib.buttons.GenBitmapTextToggleButton(self.parent.thing, bitmap = image, label = text, style = wx.BU_AUTODRAW)
				else:
					self.thing = wx.lib.buttons.GenBitmapTextButton(self.parent.thing, bitmap = image, label = text, style = wx.BU_AUTODRAW)
			else:
				if (toggle):
					self.thing = wx.lib.buttons.GenBitmapToggleButton(self.parent.thing, bitmap = image, style = wx.BU_AUTODRAW)
				else:
					# self.thing = wx.BitmapToggleButton(self.parent.thing, bitmap = image)
					self.thing = wx.lib.buttons.GenBitmapButton(self.parent.thing, bitmap = image, style = wx.BU_AUTODRAW)
		
			#Apply extra images
			image = imageCheck(disabledPath)
			if (image != None):
				self.thing.SetBitmapDisabled(image)

			image = imageCheck(selectedPath)
			if (image != None):
				self.thing.SetBitmapSelected(image)

			image = imageCheck(focusPath)
			if (image != None):
				self.thing.SetBitmapFocus(image)

			image = imageCheck(hoverPath)
			if (image != None):
				self.thing.SetBitmapHover(image)

			#Bind the function(s)
			if (myFunction != None):
				myFunctionArgs, myFunctionKwargs = self.getArguments(argument_catalogue, ["myFunctionArgs", "myFunctionKwargs"])
				self.setFunction_click(myFunction, myFunctionArgs, myFunctionKwargs)
		
		#########################################################

		self.preBuild(argument_catalogue)

		
		if (self.type.lower() == "button"):
			build_button()
		elif (self.type.lower() == "buttoncheck"):
			build_buttonCheck()
		elif (self.type.lower() == "buttonradio"):
			build_buttonRadio()
		elif (self.type.lower() == "buttontoggle"):
			build_buttonToggle()
		elif (self.type.lower() == "buttonradiobox"):
			build_buttonRadioBox()
		elif (self.type.lower() == "checklist"):
			build_checkList()
		elif (self.type.lower() == "buttonimage"):
			build_buttonImage()
		elif (self.type.lower() == "buttonhelp"):
			build_buttonImage()
		else:
			warnings.warn(f"Add {self.type} to build() for {self.__repr__()}", Warning, stacklevel = 2)

		self.postBuild(argument_catalogue)

	#Getters
	def getValue(self, event = None):
		"""Returns what the contextual value is for the object associated with this handle."""

		if (self.type.lower() == "buttoncheck"):
			value = self.thing.GetValue() #(bool) - True: Checked; False: Un-Checked

		elif (self.type.lower() == "buttonradio"):
			value = self.thing.GetValue() #(bool) - True: Selected; False: Un-Selected

		elif (self.type.lower() == "buttontoggle"):
			value = self.thing.GetValue() #(bool) - True: Selected; False: Un-Selected

		elif (self.type.lower() == "buttonradiobox"):
			index = self.thing.GetSelection()
			if (index != -1):
				value = self.thing.GetString(index) #(str) - What the selected item's text says
			else:
				value = None

		elif (self.type.lower() == "checklist"):
			value = self.thing.GetCheckedStrings() #(list) - What is selected in the check list as strings

		elif (self.type.lower() == "button"):
			value = self.thing.GetLabel() #(str) - What the button says

		elif ((self.type.lower() == "buttonimage") and (self.toggle)):
			value = self.thing.GetToggle() #(bool) - True: Selected; False: Un-Selected

		else:
			warnings.warn(f"Add {self.type} to getValue() for {self.__repr__()}", Warning, stacklevel = 2)
			value = None

		return value

	def getIndex(self, event = None):
		"""Returns what the contextual index is for the object associated with this handle."""

		if (self.type.lower() == "buttonradiobox"):
			value = self.thing.GetSelection() #(int) - Which button is selected by index

		elif (self.type.lower() == "checklist"):
			value = self.thing.GetCheckedItems() #(list) - Which checkboxes are selected as integers

		else:
			warnings.warn(f"Add {self.type} to getIndex() for {self.__repr__()}", Warning, stacklevel = 2)
			value = None

		return value

	def getAll(self, event = None):
		"""Returns all the contextual values for the object associated with this handle."""

		if (self.type.lower() == "buttonradiobox"):
			value = []
			n = self.thing.GetCount()
			for i in range(n):
				value.append(thing.GetString(i)) #(list) - What is in the radio box as strings

		elif (self.type.lower() == "checklist"):
			value = []
			n = self.thing.GetCount()
			for i in range(n):
				value.append(thing.GetString(i)) #(list) - What is in the full list as strings

		else:
			warnings.warn(f"Add {self.type} to getAll() for {self.__repr__()}", Warning, stacklevel = 2)
			value = None

		return value

	#Setters
	def setValue(self, newValue, event = None):
		"""Sets the contextual value for the object associated with this handle to what the user supplies."""

		if (self.type.lower() == "buttoncheck"):
			self.thing.SetValue(bool(newValue)) #(bool) - True: checked; False: un-checked

		elif (self.type.lower() == "buttonradio"):
			self.thing.SetValue(bool(newValue)) #(bool) - True: selected; False: un-selected

		elif (self.type.lower() == "buttontoggle"):
			self.thing.SetValue(bool(newValue)) #(bool) - True: selected; False: un-selected

		elif (self.type.lower() == "buttonradiobox"):
			if (isinstance(newValue, str)):
				# if (not newValue.isdigit()):
				newValue = self.thing.FindString(newValue)

			if (newValue == None):
				errorMessage = f"Invalid radio button selection in setValue() for {self.__repr__()}"
				raise ValueError(errorMessage)

			self.thing.SetSelection(int(newValue)) #(int / str) - Which radio button to select

		elif (self.type.lower() == "checklist"):
			if (not isinstance(newValue, dict)):
				errorMessage = "Must give a dictionary of {which item (int): state (bool)}"# or {item label (str): state (bool)}"
				raise ValueError(errorMessage)

			for index, state in newValue.items():
				if (isinstance(index, str)):
					state = self.thing.FindString(index)
				
				self.thing.Check(index, state) #(bool) - True: selected; False: un-selected
		
		elif (self.type.lower() == "button"):
			self.thing.SetLabel(newValue) #(str) - What the button will say on it

		elif ((self.type.lower() == "buttonimage") and (self.toggle)):
			self.thing.SetToggle(bool(newValue)) #(bool) - True: selected; False: un-selected

		else:
			warnings.warn(f"Add {self.type} to setValue() for {self.__repr__()}", Warning, stacklevel = 2)

	def setSelection(self, newValue, event = None):
		"""Sets the contextual value for the object associated with this handle to what the user supplies."""

		if (self.type.lower() == "buttonradiobox"):
			if (newValue == None):
				newValue = 0
			self.setValue(newValue, event)
		else:
			warnings.warn(f"Add {self.type} to setSelection() for {self.__repr__()}", Warning, stacklevel = 2)

	#Change Settings
	def setFunction_click(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		"""Changes the function that runs when the widget is clicked."""
		
		if (self.type.lower() == "buttoncheck"):
			self.betterBind(wx.EVT_CHECKBOX, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		
		elif (self.type.lower() == "buttonradio"):
			self.betterBind(wx.EVT_RADIOBUTTON, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)

		elif (self.type.lower() == "buttonradiobox"):
			self.betterBind(wx.EVT_RADIOBOX, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		
		elif (self.type.lower() == "button"):
			self.betterBind(wx.EVT_BUTTON, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		
		elif (self.type.lower() == "buttonimage"):
			self.betterBind(wx.EVT_BUTTON, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		
		elif (self.type.lower() == "buttontoggle"):
			self.betterBind(wx.EVT_TOGGLEBUTTON, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		
		elif (self.type.lower() == "checklist"):
			self.betterBind(wx.EVT_CHECKLISTBOX, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)

		else:
			warnings.warn(f"Add {self.type} to setFunction_click() for {self.__repr__()}", Warning, stacklevel = 2)

	def setReadOnly(self, state = True, event = None):
		"""Sets the contextual readOnly for the object associated with this handle to what the user supplies."""

		if (self.type.lower() == "buttoncheck"):
			self.thing.SetReadOnly(state)

		else:
			warnings.warn(f"Add {self.type} to setReadOnly() for {self.__repr__()}", Warning, stacklevel = 2)

class handle_WidgetPicker(handle_Widget_Base):
	"""A handle for working with picker widgets."""

	def __init__(self):
		"""Initializes defaults."""

		#Initialize inherited classes
		handle_Widget_Base.__init__(self)

	def __len__(self):
		"""Returns what the contextual length is for the object associated with this handle."""

		if (self.type.lower() == "pickerfile"):
			value = len(self.getValue()) #(int) - How long the file path selected is

		elif (self.type.lower() == "pickerfilewindow"):
			value = len(self.getValue()) #(int) - How long the file path selected is

		else:
			warnings.warn(f"Add {self.type} to __len__() for {self.__repr__()}", Warning, stacklevel = 2)
			value = 0

		return value

	def build(self, argument_catalogue):
		"""Determiens which build system to use for this handle."""

		def build_pickerFile():
			"""Builds a wx file picker control or directory picker control object."""
			nonlocal self, argument_catalogue

			default, text, initialDir, myFunction = self.getArguments(argument_catalogue, ["default", "text", "initialDir", "myFunction"])
			directoryOnly, openFile, saveFile, saveConfirmation = self.getArguments(argument_catalogue, ["directoryOnly", "openFile", "saveFile", "saveConfirmation"])
			changeCurrentDirectory, fileMustExist, smallButton, addInputBox = self.getArguments(argument_catalogue, ["changeCurrentDirectory", "fileMustExist", "smallButton", "addInputBox"])

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
				self.thing = wx.DirPickerCtrl(self.parent.thing, path = default, message = text, style = eval(config))
			else:
				self.thing = wx.FilePickerCtrl(self.parent.thing, path = default, message = text, wildcard = initialDir, style = eval(config))

			#Set Initial directory
			self.thing.SetInitialDirectory(initialDir)

			#Bind the function(s)
			if (myFunction != None):
				myFunctionArgs, myFunctionKwargs = self.getArguments(argument_catalogue, ["myFunctionArgs", "myFunctionKwargs"])
				self.setFunction_click(myFunction, myFunctionArgs, myFunctionKwargs)

		def build_pickerFileWindow():
			"""Builds a wx generic directory control object."""
			nonlocal self, argument_catalogue

			myFunction, editLabelFunction, rightClickFunction = self.getArguments(argument_catalogue, ["myFunction", "editLabelFunction", "rightClickFunction"])
			directoryOnly, selectMultiple, initialDir, showHidden = self.getArguments(argument_catalogue, ["directoryOnly", "selectMultiple", "initialDir", "showHidden"])

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
			self.thing = wx.GenericDirCtrl(self.parent.thing, dir = initialDir, style = eval(styles), filter = filterList)

			#Determine if it is hidden
			if (showHidden):
				self.thing.ShowHidden(True)
			else:
				self.thing.ShowHidden(False)

			#Bind the function(s)
			if (myFunction != None):
				myFunctionArgs, myFunctionKwargs = self.getArguments(argument_catalogue, ["myFunctionArgs", "myFunctionKwargs"])
				self.setFunction_click(myFunction, myFunctionArgs, myFunctionKwargs)

			if (editLabelFunction != None):
				editLabelFunctionArgs, editLabelFunctionKwargs = self.getArguments(argument_catalogue, ["editLabelFunctionArgs", "editLabelFunctionKwargs"])
				self.setFunction_editLabel(myFunction, myFunctionArgs, myFunctionKwargs)

			if (rightClickFunction != None):
				rightClickFunctionArgs, rightClickFunctionKwargs = self.getArguments(argument_catalogue, ["rightClickFunctionArgs", "rightClickFunctionKwargs"])
				self.setFunction_rightClick(myFunction, myFunctionArgs, myFunctionKwargs)

		def build_pickerDate():
			"""Builds a wx  object."""
			nonlocal self, argument_catalogue

			date, dropDown, myFunction = self.getArguments(argument_catalogue, ["date", "dropDown", "myFunction"])

			#Set the currently selected date
			if (date != None):
				try:
					month, day, year = re.split("[\\\\/]", date) #Format: mm/dd/yyyy
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
			self.thing = wx.adv.DatePickerCtrl(self.parent.thing, dt = date, style = styles)

			#Bind the function(s)
			if (myFunction != None):
				myFunctionArgs, myFunctionKwargs = self.getArguments(argument_catalogue, ["myFunctionArgs", "myFunctionKwargs"])
				self.setFunction_click(myFunction, myFunctionArgs, myFunctionKwargs)

		def build_pickerDateWindow():
			"""Builds a wx  object."""
			nonlocal self, argument_catalogue

			date, showHolidays, showOther = self.getArguments(argument_catalogue, ["date", "showHolidays", "showOther"])
			myFunction, dayFunction, monthFunction, yearFunction = self.getArguments(argument_catalogue, ["myFunction", "dayFunction", "monthFunction", "yearFunction"])

			#Set the currently selected date
			if (date != None):
				try:
					month, day, year = re.split("[\\\\/]", date) #Format: mm/dd/yyyy
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
			self.thing = wx.adv.CalendarCtrl(self.parent.thing, date = date, style = eval(styles))

			#Bind the function(s)
			if (myFunction != None):
				myFunctionArgs, myFunctionKwargs = self.getArguments(argument_catalogue, ["myFunctionArgs", "myFunctionKwargs"])
				self.setFunction_click(myFunction, myFunctionArgs, myFunctionKwargs)

			if (dayFunction != None):
				dayFunctionArgs, dayFunctionKwargs = self.getArguments(argument_catalogue, ["dayFunctionArgs", "dayFunctionKwargs"])
				self.setFunction_editDay(myFunction, myFunctionArgs, myFunctionKwargs)

			if (monthFunction != None):
				monthFunctionArgs, monthFunctionKwargs = self.getArguments(argument_catalogue, ["monthFunctionArgs", "monthFunctionKwargs"])
				self.setFunction_editMonth(myFunction, myFunctionArgs, myFunctionKwargs)

			if (yearFunction != None):
				yearFunctionArgs, yearFunctionKwargs = self.getArguments(argument_catalogue, ["yearFunctionArgs", "yearFunctionKwargs"])
				self.setFunction_editYear(myFunction, myFunctionArgs, myFunctionKwargs)

		def build_pickerTime():
			"""Builds a wx time picker control object."""
			nonlocal self, argument_catalogue

			time, myFunction = self.getArguments(argument_catalogue, ["time", "myFunction"])

			#Set the currently selected time
			if (time != None):
				try:
					time = re.split(":", time) #Format: hour:minute:second
					
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
			self.thing = wx.adv.TimePickerCtrl(self.parent.thing, dt = time)

			#Bind the function(s)
			if (myFunction != None):
				myFunctionArgs, myFunctionKwargs = self.getArguments(argument_catalogue, ["myFunctionArgs", "myFunctionKwargs"])
				self.setFunction_click(myFunction, myFunctionArgs, myFunctionKwargs)

		def build_pickerColor():
			"""Builds a wx color picker control object."""
			nonlocal self, argument_catalogue

			addInputBox, colorText, initial, myFunction = self.getArguments(argument_catalogue, ["addInputBox", "colorText", "initial", "myFunction"])

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
			self.thing = wx.ColourPickerCtrl(self.parent.thing, colour = initial, style = eval(styles))

			#Bind the function(s)
			if (myFunction != None):
				myFunctionArgs, myFunctionKwargs = self.getArguments(argument_catalogue, ["myFunctionArgs", "myFunctionKwargs"])
				self.setFunction_click(myFunction, myFunctionArgs, myFunctionKwargs)

		def build_pickerFont():
			"""Builds a wx font picker control object."""
			nonlocal self, argument_catalogue

			addInputBox, fontText, maxSize, myFunction = self.getArguments(argument_catalogue, ["addInputBox", "fontText", "maxSize", "myFunction"])

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

			# font = self.getFont()
			font = wx.NullFont
		
			#Create the thing to put in the grid
			self.thing = wx.FontPickerCtrl(self.parent.thing, font = font, style = eval(styles))
			
			self.thing.SetMaxPointSize(maxSize) 

			#Bind the function(s)
			if (myFunction != None):
				myFunctionArgs, myFunctionKwargs = self.getArguments(argument_catalogue, ["myFunctionArgs", "myFunctionKwargs"])
				self.setFunction_click(myFunction, myFunctionArgs, myFunctionKwargs)
		
		#########################################################

		self.preBuild(argument_catalogue)

		if (self.type.lower() == "pickerfile"):
			build_pickerFile()
		elif (self.type.lower() == "pickerfilewindow"):
			build_pickerFileWindow()
		elif (self.type.lower() == "pickerdate"):
			build_pickerDate()
		elif (self.type.lower() == "pickerdatewindow"):
			build_pickerDateWindow()
		elif (self.type.lower() == "pickertime"):
			build_pickerTime()
		elif (self.type.lower() == "pickercolor"):
			build_pickerColor()
		elif (self.type.lower() == "pickerfont"):
			build_pickerFont()
		else:
			warnings.warn(f"Add {self.type} to build() for {self.__repr__()}", Warning, stacklevel = 2)

		self.postBuild(argument_catalogue)

	#Getters
	def getValue(self, event = None):
		"""Returns what the contextual value is for the object associated with this handle."""

		if (self.type.lower() == "pickerfile"):
			value = self.thing.GetPath() #(str) - What is in the attached file picker

		elif (self.type.lower() == "pickerfilewindow"):
			value = self.thing.GetPath() #(str) - What is in the attached file picker
		
		elif (self.type.lower() == "pickerdate"):
			value = self.thing.GetValue() #(str) - What date is selected in the date picker
			if (value != None):
				value = f"{value.GetMonth()}/{value.GetDay()}/{value.GetYear()}"

		elif (self.type.lower() == "pickerdatewindow"):
			value = self.thing.GetDate() #(str) - What date is selected in the date picker
			if (value != None):
				value = f"{value.GetMonth()}/{value.GetDay()}/{value.GetYear()}"

		elif (self.type.lower() == "pickertime"):
			value = self.thing.GetTime() #(str) - What date is selected in the date picker
			if (value != None):
				value = f"{value[0]}:{value[1]}:{value[2]}"

		elif (self.type.lower() == "pickercolor"):
			value = self.thing.GetColour()

		elif (self.type.lower() == "pickerfont"):
			value = self.thing.GetSelectedFont()

		else:
			warnings.warn(f"Add {self.type} to getValue() for {self.__repr__()}", Warning, stacklevel = 2)
			value = None

		return value

	#Setters
	def setValue(self, newValue, event = None):
		"""Sets the contextual value for the object associated with this handle to what the user supplies."""

		if ((self.type.lower() == "pickerfile") or (self.type.lower() == "pickerfilewindow")):
			self.thing.SetPath(newValue) #(str) - What will be shown in the input box
		
		elif ((self.type.lower() == "pickerdate") or (self.type.lower() == "pickerdatewindow")):
			#Format value
			try:
				if (newValue != None):
					month, day, year = re.split("[\\\\/]", newValue) #Format: mm/dd/yyyy
					month, day, year = int(month), int(day), int(year)
					newValue = wx.DateTime(day, month, year)
				else:
					newValue = wx.DateTime().SetToCurrent()
			except:
				errorMessage = f"Calandar dates must be formatted 'mm/dd/yy' for setValue() for {self.__repr__()}"
				raise SyntaxError(errorMessage)

			self.thing.SetValue(newValue) #(str) - What date will be selected as 'mm/dd/yyyy'

		elif (self.type.lower() == "pickertime"):
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
						errorMessage = f"Time must be formatted 'hh:mm:ss' or 'hh:mm' for setValue() for {self.__repr__()}"
						raise SyntaxError(errorMessage)

				else:
					newValue = wx.DateTime().SetToCurrent()
					hour, minute, second = newValue.GetHour(), newValue.GetMinute(), newValue.GetSecond()

				hour, minute, second = int(hour), int(minute), int(second)
			except:
				errorMessage = f"Time must be formatted 'hh:mm:ss' or 'hh:mm' for setValue() for {self.__repr__()}"
				raise SyntaxError(errorMessage)

			self.thing.SetTime(hour, minute, second) #(str) - What time will be selected as 'hour:minute:second'

		else:
			warnings.warn(f"Add {self.type} to setValue() for {self.__repr__()}", Warning, stacklevel = 2)


	#Change Settings
	def setFunction_click(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		"""Changes the function that runs when the widget is changed/clicked on."""
		
		if (self.type.lower() == "pickerfile"):
			if (self.thing.GetClassName() == "wxDirPickerCtrl"):
				self.betterBind(wx.EVT_DIRPICKER_CHANGED, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
			else:
				self.betterBind(wx.EVT_FILEPICKER_CHANGED, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		elif (self.type.lower() == "pickerfilewindow"):
			self.betterBind(wx.EVT_TREE_SEL_CHANGED, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		elif (self.type.lower() == "pickertime"):
			self.betterBind(wx.adv.EVT_TIME_CHANGED, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		elif (self.type.lower() == "pickerdate"):
			self.betterBind(wx.adv.EVT_DATE_CHANGED, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		elif (self.type.lower() == "pickerdatewindow"):
			self.betterBind(wx.adv.EVT_CALENDAR_SEL_CHANGED, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		elif (self.type.lower() == "pickercolor"):
			self.betterBind(wx.EVT_COLOURPICKER_CHANGED, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		elif (self.type.lower() == "pickerfont"):
			self.betterBind(wx.EVT_FONTPICKER_CHANGED, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		else:
			warnings.warn(f"Add {self.type} to setFunction_click() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_editLabel(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		"""Changes the function that runs when a label is modified."""
		
		if (self.type.lower() == "pickerfilewindow"):
			self.betterBind(wx.EVT_TREE_END_LABEL_EDIT, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		else:
			warnings.warn(f"Add {self.type} to setFunction_editLabel() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_rightClick(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		"""Changes the function that runs when the right mouse button is clicked in the widget."""
		
		if (self.type.lower() == "pickerfilewindow"):
			self.betterBind(wx.EVT_TREE_ITEM_RIGHT_CLICK, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		else:
			warnings.warn(f"Add {self.type} to setFunction_rightClick() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_editDay(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		"""Changes the function that runs when the day is modified."""
		
		if (self.type.lower() == "pickerdatewindow"):
			self.betterBind(wx.adv.EVT_CALENDAR_DAY, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		else:
			warnings.warn(f"Add {self.type} to setFunction_editDay() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_editMonth(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		"""Changes the function that runs when the month is modified."""
		
		if (self.type.lower() == "pickerdatewindow"):
			self.betterBind(wx.adv.EVT_CALENDAR_MONTH, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		else:
			warnings.warn(f"Add {self.type} to setFunction_editMonth() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_editYear(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		"""Changes the function that runs when the year is modified."""
		
		if (self.type.lower() == "pickerdatewindow"):
			self.betterBind(wx.adv.EVT_CALENDAR_YEAR, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		else:
			warnings.warn(f"Add {self.type} to setFunction_editYear() for {self.__repr__()}", Warning, stacklevel = 2)

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

		if (self.type.lower() == "image"):
			image = self.getValue()
			if (returnRows):
				value = image.GetWidth()
			else:
				value = image.GetHeight()

		else:
			warnings.warn(f"Add {self.type} to __len__() for {self.__repr__()}", Warning, stacklevel = 2)
			value = 0

		return value

	def build(self, argument_catalogue):
		"""Determiens which build system to use for this handle."""

		def build_image():
			"""Builds a wx static bitmap object."""
			nonlocal self, argument_catalogue

			imagePath, internal, size = self.getArguments(argument_catalogue, ["imagePath", "internal", "size"])

			#Get correct image
			image = self.getImage(imagePath, internal)
		
			#Create the thing to put in the grid
			self.thing = wx.StaticBitmap(self.parent.thing, bitmap = image, size = size, style = 0)
		
		#########################################################

		self.preBuild(argument_catalogue)

		if (self.type.lower() == "image"):
			build_image()
		else:
			warnings.warn(f"Add {self.type} to build() for {self.__repr__()}", Warning, stacklevel = 2)

		self.postBuild(argument_catalogue)

	#Getters
	def getValue(self, event = None):
		"""Returns what the contextual value is for the object associated with this handle."""

		if (self.type.lower() == "image"):
			value = self.thing.GetBitmap() #(bitmap) - The image that is currently being shown

		else:
			warnings.warn(f"Add {self.type} to getValue() for {self.__repr__()}", Warning, stacklevel = 2)
			value = None

		return value

	#Setters
	def setValue(self, newValue, event = None):
		"""Sets the contextual value for the object associated with this handle to what the user supplies."""

		if (self.type.lower() == "image"):
			image = self.getImage(newValue)
			self.thing.SetBitmap(image) #(wxBitmap) - What the image will be now

		else:
			warnings.warn(f"Add {self.type} to setValue() for {self.__repr__()}", Warning, stacklevel = 2)

class handle_Menu(handle_Container_Base):
	"""A handle for working with menus."""

	def __init__(self):
		"""Initializes defaults."""

		#Initialize inherited classes
		handle_Container_Base.__init__(self)

	# def preBuild(self, argument_catalogue):
	# 	"""Runs after this object is built."""

	# 	handle_Container_Base.preBuild(self, argument_catalogue)

	# def postBuild(self, argument_catalogue):
	# 	"""Runs after this object is built."""

	# 	handle_Container_Base.postBuild(self, argument_catalogue)
		
	# 	#Unpack arguments
	# 	buildSelf = argument_catalogue["self"]
	# 	buildSelf.finalNest(self)

	def build(self, argument_catalogue):
		"""Determiens which build system to use for this handle."""

		def build_menu():
			"""Builds a wx menu control object."""
			nonlocal self, argument_catalogue
		
			#Unpack arguments
			buildSelf = self.getArguments(argument_catalogue, "self")
			detachable, text = self.getArguments(argument_catalogue, ["detachable", "text"])

			#Make sure there is a menu bar
			if ((not isinstance(buildSelf, handle_Menu)) and (not isinstance(buildSelf, handle_MenuPopup)) and (self.type.lower() == "menu")):
				menuList = buildSelf.getNested(include = handle_Menu)
				if (len(menuList) <= 1):
					buildSelf.addMenuBar()

			#Create menu
			if (detachable):
				self.thing = wx.Menu(wx.MENU_TEAROFF)
			else:
				self.thing = wx.Menu()

			self.text = text

			#Finish
			if (isinstance(buildSelf, handle_Window)):
				#Main Menu
				# self.myWindow = buildSelf
				buildSelf.menuBar.Append(self.thing, self.text)

			elif (isinstance(buildSelf, handle_MenuPopup)):
				#Popup Menu
				pass
				# self.myWindow = buildSelf.myWindow

			else:
				#Sub Menu
				# self.myWindow = buildSelf.myWindow
				buildSelf.thing.Append(wx.ID_ANY, self.text, self.thing)

		def build_toolbar():
			"""Builds a wx toolbar control object."""
			nonlocal self, argument_catalogue

			vertical, detachable, flat, align, top = self.getArguments(argument_catalogue, ["vertical", "detachable", "flat", "align", "top"])
			showIcon, showDivider, showToolTip, showText = self.getArguments(argument_catalogue, ["showIcon", "showDivider", "showToolTip", "showText"])
			flags, flex, vertical_text, myFunction = self.getArguments(argument_catalogue, ["flags", "flex", "vertical_text", "myFunction"])

			if (vertical):
				style = "wx.TB_VERTICAL"
			else:
				style = "wx.TB_HORIZONTAL"

			if (detachable):
				style += "|wx.TB_DOCKABLE"

			if (flat):
				style += "|wx.TB_FLAT"
			if (not align):
				style += "|wx.TB_NOALIGN"
			if (top == None):
				style += "|wx.TB_RIGHT"
			elif (not top):
				style += "|wx.TB_BOTTOM"

			if (not showIcon):
				style += "wx.TB_NOICONS"
			if (not showDivider):
				style += "wx.TB_NODIVIDER"
			if (not showToolTip):
				style += "wx.TB_NO_TOOLTIPS"
			if (showText):
				style += "|wx.TB_TEXT"
				if (vertical_text):
					style += "wx.TB_HORZ_LAYOUT"
			
			self.thing = wx.ToolBar(self.parent.thing, style = eval(style))
			self.thing.Realize()

			self.mySizer.nest(self, flex = flex, flags = flags)

			#Bind the function(s)
			if (myFunction != None):
				myFunctionArgs, myFunctionKwargs = self.getArguments(argument_catalogue, ["myFunctionArgs", "myFunctionKwargs"])
				self.setFunction_click(myFunction, myFunctionArgs, myFunctionKwargs)
		
		#########################################################

		self.preBuild(argument_catalogue)

		if (self.type.lower() == "menu"):
			build_menu()
		elif (self.type.lower() == "toolbar"):
			build_toolbar()
		else:
			warnings.warn(f"Add {self.type} to build() for {self.__repr__()}", Warning, stacklevel = 2)

		self.postBuild(argument_catalogue)

	def nest(self, handle, *args, **kwargs):
		"""Nests wx controls in a toolbar."""

		#Do not nest already nested objects
		if (handle.nested):
			errorMessage = "Cannot nest objects twice"
			raise SyntaxError(errorMessage)

		self.finalNest(handle)

	#Getters
	def getValue(self, event = None):
		"""Returns what the contextual value is for the object associated with this handle."""

		if (self.type.lower() == "menu"):
			#Get menu item
			if (event == None):
				errorMessage = "Pass the event parameter to getValue() when working with menu items"
				raise SyntaxError(errorMessage)
			
			index = event.GetId()
			item = self.thing.FindItemById(index)

			#Act on menu item
			if (item.IsCheckable()):
				value = item.IsChecked() #(bool) - True: Selected; False: Un-Selected
			else:
				value = item.GetLabel() #(str) - What the selected item says

		else:
			warnings.warn(f"Add {self.type} to getValue() for {self.__repr__()}", Warning, stacklevel = 2)
			value = None

		return value

	#Setters
	def setValue(self, newValue, event = None):
		"""Sets the contextual value for the object associated with this handle to what the user supplies."""

		if (self.type.lower() == "menu"):
			#Get menu item
			if (event == None):
				errorMessage = "Pass the event parameter to getValue() when working with menu items"
				raise SyntaxError(errorMessage)
			
			index = event.GetId()
			item = self.thing.FindItemById(index)

			#Act on menu item
			if ((item.GetKind() == wx.ITEM_CHECK) or (item.GetKind() == wx.ITEM_RADIO)):
				item.Check(newValue) #(bool) - True: selected; False: un-selected
			else:
				errorMessage = f"Only a menu 'Check Box' or 'Radio Button' can be set to a different value for setValue() for {self.__repr__()}"
				raise SyntaxError(errorMessage)

		else:
			warnings.warn(f"Add {self.type} to setValue() for {self.__repr__()}", Warning, stacklevel = 2)

	#Change Settings
	def setFunction_click(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		"""Changes the function that runs when the widget is changed/clicked on."""
		
		if (self.type.lower() == "toolbar"):
			self.betterBind(wx.EVT_TOOL_RCLICKED, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		else:
			warnings.warn(f"Add {self.type} to setFunction_click() for {self.__repr__()}", Warning, stacklevel = 2)

	def addItem(self, text = "", icon = None, internal = False, disabled_icon = None, disabled_internal = None,
		special = None, check = None, default = False, toolTip = "", stretchable = None,

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, 

		label = None, hidden = False, enabled = True, parent = None, handle = None, flex = 0, flags = "c1"):
		"""Adds a menu item to a specific pre-existing menu.
		Note: More special IDs for future implementation can be found at: https://wiki.wxpython.org/SpecialIDs

		HOW TO GROUP RADIO BUTTONS
		The radio buttons will group with any radio buttons immediately before and after themselves.
		This means, that inorder to create two separate radio groups, you need to add a non-radio button item between them.
		This could be a normal item, a check box, or a separator.

		which (int)     - The label for the menu to add this to. Can be a string
		text (str)      - The label for the menu item. This is what is shown to the user

		icon (str)              - The file path to the icon for the menu item
			- If None: No icon will be shown
		internal (bool)         - If True: The icon provided is an internal icon, not an external file
		disabled_icon (str)     - The file path to the icon for the menu item while it is disabled
			- If None: Will use a darker version of 'icon'
		disabled_internal (bool) - If the icon in 'disabled' provided is an internal icon, not an external file
			- If None: Will use the value given for 'internal'

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

		Example Input: addItem("Lorem")
		Example Input: addItem(icon = 'exit.bmp')
		Example Input: addItem("Print Preview", myFunction = [self.onPrintLabelsPreview, "self.onShowPopupWindow"], myFunctionArgs = [None, 0], label = "printPreview")
		Example Input: addItem(label = "scanner", check = True, default = True, icon = "resources/scanner_enabled.ico", disabled_icon = "resources/scanner_disabled.ico")
		"""

		handle = handle_MenuItem()
		handle.type = "MenuItem"
		selected = False
		mySizer = self
		handle.build(locals())
		self.finalNest(handle)

		return handle

	def addSeparator(self, *args, **kwargs):
		"""Adds a line to a specific pre-existing menu to separate menu items.

		Example Input: addSeparator()
		"""

		handle = self.addItem(*args, text = None, stretchable = False, **kwargs)

		return handle

	def addStretchableSpace(self, *args, **kwargs):
		"""Adds a line to a specific pre-existing menu to separate menu items.

		Example Input: addSeparator()
		"""

		if (self.type.lower() == "toolbar"):
			handle = self.addItem(*args, text = None, stretchable = True, **kwargs)
		else:
			warnings.warn(f"Add {self.type} to addStretchableSpace() for {self.__repr__()}", Warning, stacklevel = 2)
			handle = None

		return handle

	def addSub(self, text = "", flex = 0, flags = "c1", 
		label = None, hidden = False, parent = None, handle = None):
		"""Adds a sub menu to a specific pre-existing menu.
		To adding items to a sub menu is the same as for menus.

		text (str)  - The text for the menu item. This is what is shown to the user
		label (int) - The label for this menu

		Example Input: addSub()
		Example Input: addSub(text = "I&mport")
		"""

		handle = handle_Menu()
		detachable = False
		selected = False
		mySizer = self
		handle.build(locals())

		return handle

	def addText(self, *args, **kwargs):
		"""Adds a text widget to the tool bar."""

		if (self.type.lower() == "toolbar"):
			subHandle = handle_Sizer.addText(self, *args, mySizer = self, **kwargs)
			handle = self.thing.AddControl(subHandle.thing)
			self.thing.Realize()
		else:
			warnings.warn(f"Add {self.type} to addText() for {self.__repr__()}", Warning, stacklevel = 2)
			handle = None

		return handle

	def addHyperlink(self, *args, **kwargs):
		"""Adds a hyperlink widget to the tool bar."""

		if (self.type.lower() == "toolbar"):
			subHandle = handle_Sizer.addHyperlink(self, *args, mySizer = self, **kwargs)
			handle = self.thing.AddControl(subHandle.thing)
			self.thing.Realize()
		else:
			warnings.warn(f"Add {self.type} to addHyperlink() for {self.__repr__()}", Warning, stacklevel = 2)
			handle = None

		return handle

	def addLine(self, *args, **kwargs):
		"""Adds a line widget to the tool bar."""

		if (self.type.lower() == "toolbar"):
			subHandle = handle_Sizer.addLine(self, *args, mySizer = self, **kwargs)
			handle = self.thing.AddControl(subHandle.thing)
			self.thing.Realize()
		else:
			warnings.warn(f"Add {self.type} to addLine() for {self.__repr__()}", Warning, stacklevel = 2)
			handle = None

		return handle

	def addListDrop(self, *args, **kwargs):
		"""Adds a drop list widget to the tool bar."""

		if (self.type.lower() == "toolbar"):
			subHandle = handle_Sizer.addListDrop(self, *args, mySizer = self, **kwargs)
			handle = self.thing.AddControl(subHandle.thing)
			self.thing.Realize()
		else:
			warnings.warn(f"Add {self.type} to addListDrop() for {self.__repr__()}", Warning, stacklevel = 2)
			handle = None

		return handle

	def addListFull(self, *args, **kwargs):
		"""Adds a full list widget to the tool bar."""

		if (self.type.lower() == "toolbar"):
			subHandle = handle_Sizer.addListFull(self, *args, mySizer = self, **kwargs)
			handle = self.thing.AddControl(subHandle.thing)
			self.thing.Realize()
		else:
			warnings.warn(f"Add {self.type} to addListFull() for {self.__repr__()}", Warning, stacklevel = 2)
			handle = None

		return handle

	def addInputSlider(self, *args, **kwargs):
		"""Adds an input slider widget to the tool bar."""

		if (self.type.lower() == "toolbar"):
			subHandle = handle_Sizer.addInputSlider(self, *args, mySizer = self, **kwargs)
			handle = self.thing.AddControl(subHandle.thing)
			self.thing.Realize()
		else:
			warnings.warn(f"Add {self.type} to addInputSlider() for {self.__repr__()}", Warning, stacklevel = 2)
			handle = None

		return handle

	def addInputBox(self, *args, **kwargs):
		"""Adds an input box widget to the tool bar."""

		if (self.type.lower() == "toolbar"):
			subHandle = handle_Sizer.addInputBox(self, *args, mySizer = self, **kwargs)
			handle = self.thing.AddControl(subHandle.thing)
			self.thing.Realize()
		else:
			warnings.warn(f"Add {self.type} to addInputBox() for {self.__repr__()}", Warning, stacklevel = 2)
			handle = None

		return handle

	def addInputSearch(self, *args, **kwargs):
		"""Adds a search box widget to the tool bar."""

		if (self.type.lower() == "toolbar"):
			subHandle = handle_Sizer.addInputSearch(self, *args, mySizer = self, **kwargs)
			handle = self.thing.AddControl(subHandle.thing)
			self.thing.Realize()
		else:
			warnings.warn(f"Add {self.type} to addInputSearch() for {self.__repr__()}", Warning, stacklevel = 2)
			handle = None

		return handle

	def addInputSpinner(self, *args, **kwargs):
		"""Adds an input spinner widget to the tool bar."""

		if (self.type.lower() == "toolbar"):
			subHandle = handle_Sizer.addInputSpinner(self, *args, mySizer = self, **kwargs)
			handle = self.thing.AddControl(subHandle.thing)
			self.thing.Realize()
		else:
			warnings.warn(f"Add {self.type} to addInputSpinner() for {self.__repr__()}", Warning, stacklevel = 2)
			handle = None

		return handle

	def addButton(self, *args, **kwargs):
		"""Adds a button widget to the tool bar."""

		if (self.type.lower() == "toolbar"):
			subHandle = handle_Sizer.addButton(self, *args, mySizer = self, **kwargs)
			handle = self.thing.AddControl(subHandle.thing)
			self.thing.Realize()
		else:
			warnings.warn(f"Add {self.type} to addButton() for {self.__repr__()}", Warning, stacklevel = 2)
			handle = None

		return handle

	def addButtonToggle(self, *args, **kwargs):
		"""Adds a toggle button widget to the tool bar."""

		if (self.type.lower() == "toolbar"):
			subHandle = handle_Sizer.addButtonToggle(self, *args, mySizer = self, **kwargs)
			handle = self.thing.AddControl(subHandle.thing)
			self.thing.Realize()
		else:
			warnings.warn(f"Add {self.type} to addButtonToggle() for {self.__repr__()}", Warning, stacklevel = 2)
			handle = None

		return handle

	def addButtonCheck(self, *args, **kwargs):
		"""Adds a check button widget to the tool bar."""

		if (self.type.lower() == "toolbar"):
			subHandle = handle_Sizer.addButtonCheck(self, *args, mySizer = self, **kwargs)
			handle = self.thing.AddControl(subHandle.thing)
			self.thing.Realize()
		else:
			warnings.warn(f"Add {self.type} to addButtonCheck() for {self.__repr__()}", Warning, stacklevel = 2)
			handle = None

		return handle

	def addButtonCheckList(self, *args, **kwargs):
		"""Adds a check list widget to the tool bar."""

		if (self.type.lower() == "toolbar"):
			subHandle = handle_Sizer.addButtonCheckList(self, *args, mySizer = self, **kwargs)
			handle = self.thing.AddControl(subHandle.thing)
			self.thing.Realize()
		else:
			warnings.warn(f"Add {self.type} to addButtonCheckList() for {self.__repr__()}", Warning, stacklevel = 2)
			handle = None

		return handle

	def addButtonRadio(self, *args, **kwargs):
		"""Adds a radio button widget to the tool bar."""

		if (self.type.lower() == "toolbar"):
			subHandle = handle_Sizer.addButtonRadio(self, *args, mySizer = self, **kwargs)
			handle = self.thing.AddControl(subHandle.thing)
			self.thing.Realize()
		else:
			warnings.warn(f"Add {self.type} to addButtonRadio() for {self.__repr__()}", Warning, stacklevel = 2)
			handle = None

		return handle

	def addButtonRadioBox(self, *args, **kwargs):
		"""Adds a radio button box widget to the tool bar."""

		if (self.type.lower() == "toolbar"):
			subHandle = handle_Sizer.addButtonRadioBox(self, *args, mySizer = self, **kwargs)
			handle = self.thing.AddControl(subHandle.thing)
			self.thing.Realize()
		else:
			warnings.warn(f"Add {self.type} to addButtonRadioBox() for {self.__repr__()}", Warning, stacklevel = 2)
			handle = None

		return handle

	def addButtonImage(self, *args, **kwargs):
		"""Adds an image button widget to the tool bar."""

		if (self.type.lower() == "toolbar"):
			subHandle = handle_Sizer.addButtonImage(self, *args, mySizer = self, **kwargs)
			handle = self.thing.AddControl(subHandle.thing)
			self.thing.Realize()
		else:
			warnings.warn(f"Add {self.type} to addButtonImage() for {self.__repr__()}", Warning, stacklevel = 2)
			handle = None

		return handle

	def addImage(self, *args, **kwargs):
		"""Adds an image widget to the tool bar."""

		if (self.type.lower() == "toolbar"):
			subHandle = handle_Sizer.addImage(self, *args, mySizer = self, **kwargs)
			handle = self.thing.AddControl(subHandle.thing)
			self.thing.Realize()
		else:
			warnings.warn(f"Add {self.type} to addImage() for {self.__repr__()}", Warning, stacklevel = 2)
			handle = None

		return handle

	def addProgressBar(self, *args, **kwargs):
		"""Adds a progress bar widget to the tool bar."""

		if (self.type.lower() == "toolbar"):
			subHandle = handle_Sizer.addProgressBar(self, *args, mySizer = self, **kwargs)
			handle = self.thing.AddControl(subHandle.thing)
			self.thing.Realize()
		else:
			warnings.warn(f"Add {self.type} to addProgressBar() for {self.__repr__()}", Warning, stacklevel = 2)
			handle = None

		return handle

	def addPickerColor(self, *args, **kwargs):
		"""Adds a color picker widget to the tool bar."""

		if (self.type.lower() == "toolbar"):
			subHandle = handle_Sizer.addPickerColor(self, *args, mySizer = self, **kwargs)
			handle = self.thing.AddControl(subHandle.thing)
			self.thing.Realize()
		else:
			warnings.warn(f"Add {self.type} to addPickerColor() for {self.__repr__()}", Warning, stacklevel = 2)
			handle = None

		return handle

	def addPickerFont(self, *args, **kwargs):
		"""Adds a font picker widget to the tool bar."""

		if (self.type.lower() == "toolbar"):
			subHandle = handle_Sizer.addPickerFont(self, *args, mySizer = self, **kwargs)
			handle = self.thing.AddControl(subHandle.thing)
			self.thing.Realize()
		else:
			warnings.warn(f"Add {self.type} to addPickerFont() for {self.__repr__()}", Warning, stacklevel = 2)
			handle = None

		return handle

	def addPickerFile(self, *args, **kwargs):
		"""Adds a file picker widget to the tool bar."""

		if (self.type.lower() == "toolbar"):
			subHandle = handle_Sizer.addPickerFile(self, *args, mySizer = self, **kwargs)
			handle = self.thing.AddControl(subHandle.thing)
			self.thing.Realize()
		else:
			warnings.warn(f"Add {self.type} to addPickerFile() for {self.__repr__()}", Warning, stacklevel = 2)
			handle = None

		return handle

	def addPickerFileWindow(self, *args, **kwargs):
		"""Adds a file window picker widget to the tool bar."""

		if (self.type.lower() == "toolbar"):
			subHandle = handle_Sizer.addPickerFileWindow(self, *args, mySizer = self, **kwargs)
			handle = self.thing.AddControl(subHandle.thing)
			self.thing.Realize()
		else:
			warnings.warn(f"Add {self.type} to addPickerFileWindow() for {self.__repr__()}", Warning, stacklevel = 2)
			handle = None

		return handle

	def addPickerTime(self, *args, **kwargs):
		"""Adds a time picker widget to the tool bar."""

		if (self.type.lower() == "toolbar"):
			subHandle = handle_Sizer.addPickerTime(self, *args, mySizer = self, **kwargs)
			handle = self.thing.AddControl(subHandle.thing)
			self.thing.Realize()
		else:
			warnings.warn(f"Add {self.type} to addPickerTime() for {self.__repr__()}", Warning, stacklevel = 2)
			handle = None

		return handle

	def addPickerDate(self, *args, **kwargs):
		"""Adds a date picker widget to the tool bar."""

		if (self.type.lower() == "toolbar"):
			subHandle = handle_Sizer.addPickerDate(self, *args, mySizer = self, **kwargs)
			handle = self.thing.AddControl(subHandle.thing)
			self.thing.Realize()
		else:
			warnings.warn(f"Add {self.type} to addPickerDate() for {self.__repr__()}", Warning, stacklevel = 2)
			handle = None

		return handle

	def addPickerDateWindow(self, *args, **kwargs):
		"""Adds a text date window picker to the tool bar."""

		if (self.type.lower() == "toolbar"):
			subHandle = handle_Sizer.addPickerDateWindow(self, *args, mySizer = self, **kwargs)
			handle = self.thing.AddControl(subHandle.thing)
			self.thing.Realize()
		else:
			warnings.warn(f"Add {self.type} to addPickerDateWindow() for {self.__repr__()}", Warning, stacklevel = 2)
			handle = None

		return handle

	def addCanvas(self, *args, **kwargs):
		"""Adds a canvas widget to the tool bar."""

		if (self.type.lower() == "toolbar"):
			subHandle = handle_Sizer.addCanvas(self, *args, mySizer = self, **kwargs)
			handle = self.thing.AddControl(subHandle.thing)
			self.thing.Realize()
		else:
			warnings.warn(f"Add {self.type} to addCanvas() for {self.__repr__()}", Warning, stacklevel = 2)
			handle = None

		return handle

class handle_MenuItem(handle_Widget_Base):
	"""A handle for working with menu widgets."""

	def __init__(self):
		"""Initializes defaults."""

		#Initialize inherited classes
		handle_Widget_Base.__init__(self)

	def __len__(self):
		"""Returns what the contextual length is for the object associated with this handle."""

		if (self.type.lower() == "menuitem"):
			value = len(self.thing.GetLabel()) #(int) - How long the text inside the menu item is

		else:
			warnings.warn(f"Add {self.type} to __len__() for {self.__repr__()}", Warning, stacklevel = 2)
			value = 0

		return value

	# def postBuild(self, argument_catalogue):
	# 	buildSelf = self.getArguments(argument_catalogue, "self")

	# 	handle_Widget_Base.postBuild(self, argument_catalogue)

	# 	# #Determine native window
	# 	# if (isinstance(buildSelf, handle_Window)):
	# 	# 	self.myWindow = buildSelf
	# 	# else:
	# 	# 	self.myWindow = buildSelf.myWindow

	def build(self, argument_catalogue):
		"""Determiens which build system to use for this handle."""

		def build_menuItem():
			"""Builds a wx menu item control object."""
			nonlocal self, argument_catalogue
		
			#Unpack arguments
			buildSelf, text, hidden = self.getArguments(argument_catalogue, ["self", "text", "hidden"])

			#Account for separators
			if (text == None):
				self.thing = wx.MenuItem(self.parent.thing, kind = wx.ITEM_SEPARATOR)
			else:
				special, check, default = self.getArguments(argument_catalogue, ["special", "check", "default"])
				myFunction, toolTip = self.getArguments(argument_catalogue, ["myFunction", "toolTip"])
				
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
					self.thing = wx.MenuItem(self.parent.thing, myId, text)

					#Determine icon
					icon, internal = self.getArguments(argument_catalogue, ["icon", "internal"])
					if (icon != None):
						image = self.getImage(icon, internal)
						image = self.convertBitmapToImage(image)
						image = image.Scale(16, 16, wx.IMAGE_QUALITY_HIGH)
						image = self.convertImageToBitmap(image)
						self.thing.SetBitmap(image)
				else:
					if (check):
						self.thing = wx.MenuItem(self.parent.thing, myId, text, kind = wx.ITEM_CHECK)
					else:
						self.thing = wx.MenuItem(self.parent.thing, myId, text, kind = wx.ITEM_RADIO)

				#Determine initial value
				if (check != None):
					if (default):
						self.thing.Check(True)

				#Determine how to do the bound function
				if (myFunction == None):
					if (special != None):
						if (special[0] == "q" or special[0] == "e"):
							buildSelf.betterBind(wx.EVT_MENU, self.thing, "self.onExit")
						elif (special[0] == "c"):
							buildSelf.betterBind(wx.EVT_MENU, self.thing, "self.onQuit")
						elif (special[0] == "h"):
							buildSelf.betterBind(wx.EVT_MENU, self.thing, "self.onHide")
						elif (special[0] == "s"):
							buildSelf.betterBind(wx.EVT_MENU, self.thing, "self.onToggleStatusBar")
						elif (special[0] == "t"):
							buildSelf.betterBind(wx.EVT_MENU, self.thing, "self.onToggleToolBar")
						else:
							errorMessage = f"Unknown special function {special} for {self.__repr__()}"
							raise KeyError(errorMessage)
				else:
					myFunctionArgs, myFunctionKwargs = self.getArguments(argument_catalogue, ["myFunctionArgs", "myFunctionKwargs"])
					buildSelf.betterBind(wx.EVT_MENU, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)

				#Add help
				if (toolTip != None):
					#Ensure correct formatting
					if (not isinstance(toolTip, str)):
						toolTip = f"{toolTip}"

					#Do not add empty tool tips
					if (len(toolTip) != 0):
						self.thing.SetHelp(toolTip)

			#Determine visibility
			if (hidden):
				if (isinstance(buildSelf, handle_Sizer)):
					buildSelf.addFinalFunction(buildSelf.thing.ShowItems, False)
				else:
					self.thing.Hide()

			#Add Menu Item
			self.parent.thing.Append(self.thing)

		def build_toolbarItem():
			"""Builds a wx tool control object."""
			nonlocal self, argument_catalogue

			text = self.getArguments(argument_catalogue, ["text"])
			if (text == None):
				stretchable = self.getArguments(argument_catalogue, ["stretchable"])
				if (stretchable):
					self.thing = self.parent.AddStretchableSpace()
				else:
					self.thing = self.parent.AddSeparator()
			else:
				icon, internal, toolTip = self.getArguments(argument_catalogue, ["icon", "internal", "toolTip"])
				disabled_icon, disabled_internal = self.getArguments(argument_catalogue, ["disabled_icon", "disabled_internal"])
				check, default, myFunction, special = self.getArguments(argument_catalogue, ["check", "default", "myFunction", "special"])
				
				#Get Images
				if (icon == None):
					warnings.warn(f"No icon provided for {self.__repr__()}", Warning, stacklevel = 2)
					icon = "error"
					internal = True
				image = self.getImage(icon, internal)

				if (disabled_icon == None):
					imageDisabled = wx.NullBitmap
				else:
					if (disabled_internal == None):
						disabled_internal = internal
					imageDisabled = self.getImage(disabled_icon, disabled_internal)

				#Configure Settings
				if (toolTip == None):
					toolTip = ""
				elif (not isinstance(toolTip, str)):
					toolTip = f"{toolTip}"

				if (check == None):
					kind = "wx.ITEM_NORMAL"
				else:
					if (check):
						kind = "wx.ITEM_CHECK"
					else:
						kind = "wx.ITEM_RADIO"

				self.thing = self.parent.thing.AddTool(wx.ID_ANY, text, image, imageDisabled, kind = eval(kind), shortHelp = toolTip, longHelp = toolTip)

				if (default):
					self.thing.SetToggle(True)#Determine how to do the bound function
				
				if (myFunction == None):
					if (special != None):
						if (special[0] == "q" or special[0] == "e"):
							self.parent.betterBind(wx.EVT_TOOL, self.thing, "self.onExit")
						elif (special[0] == "c"):
							self.parent.betterBind(wx.EVT_TOOL, self.thing, "self.onQuit")
						elif (special[0] == "h"):
							self.parent.betterBind(wx.EVT_TOOL, self.thing, "self.onHide")
						elif (special[0] == "s"):
							self.parent.betterBind(wx.EVT_TOOL, self.thing, "self.onToggleStatusBar")
						elif (special[0] == "t"):
							self.parent.betterBind(wx.EVT_TOOL, self.thing, "self.onToggleToolBar")
						else:
							errorMessage = f"Unknown special function {special} for {self.__repr__()}"
							raise KeyError(errorMessage)
				else:
					myFunctionArgs, myFunctionKwargs = self.getArguments(argument_catalogue, ["myFunctionArgs", "myFunctionKwargs"])
					self.parent.betterBind(wx.EVT_TOOL, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)

			self.parent.thing.Realize()
		
		#########################################################

		self.preBuild(argument_catalogue)

		if (self.parent.type.lower() == "menu"):
			build_menuItem()
		elif (self.parent.type.lower() == "toolbar"):
			build_toolbarItem()
		else:
			warnings.warn(f"Add {self.type} to build() for {self.__repr__()}", Warning, stacklevel = 2)

		self.postBuild(argument_catalogue)

	def getValue(self, event = None):
		"""Returns what the contextual value is for the object associated with this handle."""

		if (self.type.lower() == "menuitem"):
			if (self.thing.IsCheckable()):
				value = self.thing.IsChecked() #(bool) - True: Selected; False: Un-Selected
			else:
				value = self.thing.GetText() #(str) - What the selected item says

		else:
			warnings.warn(f"Add {self.type} to getValue() for {self.__repr__()}", Warning, stacklevel = 2)
			value = None

		return value

	def getIndex(self, event = None):
		"""Returns what the contextual index is for the object associated with this handle."""

		if (self.type.lower() == "menuitem"):
			if (event != None):
				value = event.GetId()
			else:
				errorMessage = "Pass the event parameter to getIndex() when working with menu items"
				raise SyntaxError(errorMessage)

		else:
			warnings.warn(f"Add {self.type} to getIndex() for {self.__repr__()}", Warning, stacklevel = 2)
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
			warnings.warn(f"No status bar found for. Tool tips for menu items are displayed on a status bar for {self.parent.myWindow.__repr__()}", Warning, stacklevel = 2)

		if (text != None):
			#Ensure correct formatting
			if (not isinstance(text, str)):
				text = f"{text}"

			#Do not add empty tool tips
			if (len(text) != 0):
				self.thing.SetHelp(text)

	#Setters
	def setValue(self, newValue, event = None):
		"""Sets the contextual value for the object associated with this handle to what the user supplies."""

		if (self.type.lower() == "menuitem"):
			if ((self.thing.GetKind() == wx.ITEM_CHECK) or (self.thing.GetKind() == wx.ITEM_RADIO)):
				self.thing.Check(newValue) #(bool) - True: selected; False: un-selected
			else:
				errorMessage = f"Only a menu 'Check Box' or 'Radio Button' can be set to a different value for setValue() for {self.__repr__()}"
				raise SyntaxError(errorMessage)

		else:
			warnings.warn(f"Add {self.type} to setValue() for {self.__repr__()}", Warning, stacklevel = 2)

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

	def __len__(self):
		"""Returns what the contextual length is for the object associated with this handle."""

		return len(self.contents)

	def postBuild(self, argument_catalogue):
		"""Runs after this object is built."""

		handle_Container_Base.postBuild(self, argument_catalogue)

		# #Remember window handle
		# buildSelf = self.getArguments(argument_catalogue, ["self"])
		# if (isinstance(buildSelf, handle_Window)):
		# 	#Main Menu
		# 	self.myWindow = buildSelf
		# else:
		# 	#Sub Menu
		# 	self.myWindow = buildSelf.myWindow

	def build(self, argument_catalogue):
		"""Determiens which build system to use for this handle."""

		def build_menuPopup():
			"""Builds a wx menu control object."""
			nonlocal self, argument_catalogue
		
			#Unpack arguments
			buildSelf, text, label, hidden, enabled, rightClick = self.getArguments(argument_catalogue, ["self", "text", "label", "hidden", "enabled", "rightClick"])

			#Remember sub menu details
			self.text = text
			self.label = label
			self.hidden = hidden
			self.enabled = enabled

			#Bind functions
			if (rightClick != None):
				preFunction, preFunctionArgs, preFunctionKwargs = argument_catalogue["preFunction", "preFunctionArgs", "preFunctionKwargs"]
				postFunction, postFunctionArgs, postFunctionKwargs = argument_catalogue["postFunction", "postFunctionArgs", "postFunctionKwargs"]

				if (rightClick):
					self.betterBind(wx.EVT_RIGHT_DOWN, self.parent.thing, self.onTriggerPopupMenu, [[preFunction, preFunctionArgs, preFunctionKwargs], [postFunction, postFunctionArgs, postFunctionKwargs]])
				else:
					self.betterBind(wx.EVT_LEFT_DOWN, self.parent.thing, self.onTriggerPopupMenu, [[preFunction, preFunctionArgs, preFunctionKwargs], [postFunction, postFunctionArgs, postFunctionKwargs]])

		
		#########################################################

		self.preBuild(argument_catalogue)

		if (self.type.lower() == "menupopup"):
			build_menuPopup()
		elif (self.type.lower() == "menupopup_widget"):
			build_menuPopup()
		else:
			warnings.warn(f"Add {self.type} to build() for {self.__repr__()}", Warning, stacklevel = 2)

		self.postBuild(argument_catalogue)

	def getValue(self, event = None):
		"""Returns what the contextual value is for the object associated with this handle."""

		if (self.popupMenu != None):
			value = self.popupMenu.myMenu.getValue(event = event)
		else:
			warnings.warn(f"Popup Menu not shown for getValue() in {self.__repr__()}", Warning, stacklevel = 2)
			value = None

		return value

	def getIndex(self, event = None):
		"""Returns what the contextual index is for the object associated with this handle."""

		if (self.popupMenu != None):
			value = self.popupMenu.myMenu.getIndex(event = event)
		else:
			warnings.warn(f"Popup Menu not shown for getIndex() in {self.__repr__()}", Warning, stacklevel = 2)
			value = None

	#Setters
	def setValue(self, newValue, event = None):
		"""Sets the contextual value for the object associated with this handle to what the user supplies."""

		self.popupMenu.setValue(event = event)

	#Change Settings
	def show(self, event):
		"""Triggers the popup menu."""

		self.onTriggerPopupMenu(event)

	def clearPopupMenu(self):
		"""Clears the popup menu of all items.

		Example Input: clearPopupMenu()
		"""

		self.contents = []

	#Add Content
	def addItem(self, text = "", icon = None, internal = False, special = None, 
		check = None, default = False, toolTip = "",

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, 

		label = None, hidden = False, enabled = True, parent = None, handle = None):
		"""Adds an item to a catalogued popup menu.

		text (str)           - The label of the item. This is what is shown to the user
			- If None: The item will be an item separator instead of a selectable object
		label (str)          - The label for the popup menu item. Can be an integer
			- If None: Will not be labeled, which means it cannot be modified later
		enable (bool)        - If the row is clickable
		hidden (bool)        - If the row is hidden

		icon (str)              - The file path to the icon for the menu item
			- If None: No icon will be used
		internal (bool)         - If the icon provided is an internal icon, not an external file
		
		check_enable (bool)  - Determines if the row has a check box or radio button
			- If None:  Normal menu item
			- If True:  Check box menu item
			- If False: Radio Button menu item
		check_default (bool) - If this check box is checked already

		myFunction (function)   - the function to run when pressed
		myFunctionArgs (list)   - args for 'myFunction'
		myFunctionKwargs (dict) - kwargs for 'myFunction'
		special (str)           - Declares if the item has a special pre-defined functionality
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
		self.finalNest(handle)
		handle.myMenu = self

		return handle

	def addSeparator(self, *args, **kwargs):
		"""Adds an separator line to the popup menu
		This must be done before it gets triggered.

		label (str)        - The label for the popup menu item. Can be an integer
			- If None: Will not be labeled, which means it cannot be modified later
		hidden (bool)        - If the row is hidden

		addPopupMenuSeparator()
		addPopupMenuSeparator(label = "menuSeparator", hidden = True)
		"""

		handle = self.addItem(None, *args, **kwargs)
		return handle

	def addSub(self, text = None, label = None, 
		parent = None, hidden = False, enabled = True, handle = None):
		"""Adds a sub menu to a specific pre-existing menu.
		To adding items to a sub menu is the same as for menus.

		text (str)  - The text for the menu item. This is what is shown to the user
		label (int) - The label for this menu

		Example Input: addSub()
		Example Input: addSub(text = "I&mport")
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
		handle.type = "MenuPopup"
		handle.build(locals())

		#Nest handle
		self.contents.append(handle)
		self.finalNest(handle)
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
			warnings.warn(f"Popup Menu {self.__repr__()} for {self.myWindow.__repr__()} has no contents", Warning, stacklevel = 2)
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
				runFunctionList, runFunctionArgsList, runFunctionKwargsList = self.parent.formatFunctionInputList(preFunction[0], preFunction[1], preFunction[2])
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
			parent = None, hidden = False, enabled = True, handle = None):
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

			handle.build(kwargs)
			self.parent.finalNest(handle)
			return handle

		def populateMenu(self, menu, contents):
			"""Uses a dictionary to populate the menu with items and bound events."""

			#Create the menu
			if (len(contents) != 0):
				for i, handle in enumerate(contents):
					if (isinstance(handle, handle_MenuPopup)):
						subMenu = menu.addSub(text = handle.text, label = handle.label, hidden = handle.hidden)
						self.populateMenu(subMenu, handle.contents)

					elif (handle.text != None):
						menu.addItem(text = handle.text, icon = handle.icon, internal = handle.internal, special = None, check = handle.check, default = handle.default,
							myFunction = handle.myFunction, myFunctionArgs = handle.myFunctionArgs, myFunctionKwargs = handle.myFunctionKwargs, 
							label = handle.label, hidden = handle.hidden, enabled = handle.enabled)
					else:
						menu.addSeparator(label = handle.label, hidden = handle.hidden)

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
						errorMessage = f"'special' should be a string for addItem() for {buildSelf.__repr__()}"
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

	def build(self, argument_catalogue):
		"""Determiens which build system to use for this handle."""

		def build_canvas():
			"""Builds a wx panel object and makes it a canvas for painting."""
			nonlocal self, argument_catalogue

			panel, initFunction, buildSelf = self.getArguments(argument_catalogue, ["panel", "initFunction", "self"])

			#Create the thing
			panel["parent"] = buildSelf.parent
			self.myPanel = self.readBuildInstructions_panel(buildSelf, panel)
			self.finalNest(self.myPanel)
			self.thing = self.myPanel.thing

			#onSize called to make sure the buffer is initialized.
			#This might result in onSize getting called twice on some platforms at initialization, but little harm done.
			self.onSize(None)

			#Bind Functions
			if (initFunction != None):
				initFunctionArgs, initFunctionKwargs = self.getArguments(argument_catalogue, ["initFunctionArgs", "initFunctionKwargs"])
				self.setFunction_init(initFunction, initFunctionArgs, initFunctionKwargs)

			#Enable painting
			self.betterBind(wx.EVT_PAINT, self.thing, self.onPaint)
			self.betterBind(wx.EVT_SIZE, self.thing, self.onSize)
		
		#########################################################

		self.preBuild(argument_catalogue)

		if (self.type.lower() == "canvas"):
			build_canvas()
		else:
			warnings.warn(f"Add {self.type} to build() for {self.__repr__()}", Warning, stacklevel = 2)

		self.postBuild(argument_catalogue)

	def setFunction_init(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		"""Changes the function that runs when the object is first created."""

		if (self.type.lower() == "canvas"):
			self.parent.betterBind(wx.EVT_INIT_DIALOG, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		else:
			warnings.warn(f"Add {self.type} to setFunction_init() for {self.__repr__()}", Warning, stacklevel = 2)

	def readBuildInstructions_panel(self, parent, instructions):
		"""Interprets instructions given by the user for what panel to make and how to make it."""

		if (not isinstance(instructions, dict)):
			errorMessage = f"panel must be a dictionary for {self.__repr__()}"
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
				warnings.warn(f"Must supply an image path in getBrushStyle() to use the style for {self.__repr__()}", Warning, stacklevel = 2)
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
			warnings.warn(f"Unknown style {style} in getBrushStyle() for {self.__repr__()}", Warning, stacklevel = 2)
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

	def drawArc(self, x, y, width, height = None, start = 0, end = 180, 
		outline = (0, 0, 0), fill = None, style = None):
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

	def drawRectangle(self, x, y, width, height = None, radius = None, 
		outline = (0, 0, 0), outlineWidth = 1, fill = None, style = None):
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

	def drawPolygon(self, points, outline = (0, 0, 0), outlineWidth = 1, 
		fill = None, style = None, algorithm = 0):
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

		self.previousCell = (-1, -1)
		self.readOnlyCatalogue = {}
		self.cellTypeCatalogue = {}

	def __len__(self):
		"""Returns what the contextual length is for the object associated with this handle.

		returnRows(bool) - Determines what is returned for 2D objects
			- If True: Returns how many rows the object has
			- If False: Returns how many columns the object has
		"""

		if (self.type.lower() == "table"):
			if (returnRows):
				value = self.thing.GetNumberRows()
			else:
				value = self.thing.GetNumberCols()

		else:
			warnings.warn(f"Add {self.type} to __len__() for {self.__repr__()}", Warning, stacklevel = 2)
			value = 0

		return value

	def build(self, argument_catalogue):
		"""Determiens which build system to use for this handle."""

		def build_table():
			"""Builds a wx grid object."""
			nonlocal self, argument_catalogue

			rows, columns, readOnly = self.getArguments(argument_catalogue, ["rows", "columns", "readOnly" ])
			showGrid, dragableColumns, dragableRows = self.getArguments(argument_catalogue, ["showGrid", "dragableColumns", "dragableRows"])
			rowSize, columnSize, autoSizeRow, autoSizeColumn = self.getArguments(argument_catalogue, ["rowSize", "columnSize", "autoSizeRow", "autoSizeColumn"])

			rowLabelSize, columnLabelSize = self.getArguments(argument_catalogue, ["rowLabelSize", "columnLabelSize"])
			rowSizeMinimum, columnSizeMinimum, rowSizeMaximum, columnSizeMaximum = self.getArguments(argument_catalogue, ["rowSizeMinimum", "columnSizeMinimum", "rowSizeMaximum", "columnSizeMaximum"])
			gridLabels, contents, default, enterKeyExitEdit = self.getArguments(argument_catalogue, ["gridLabels", "contents", "default", "enterKeyExitEdit"])
			toolTips, arrowKeyExitEdit, editOnEnter = self.getArguments(argument_catalogue, ["toolTips", "arrowKeyExitEdit", "editOnEnter"])

			preEditFunction, postEditFunction = self.getArguments(argument_catalogue, ["preEditFunction", "postEditFunction"])
			dragFunction, selectManyFunction, selectSingleFunction = self.getArguments(argument_catalogue, ["dragFunction", "selectManyFunction", "selectSingleFunction"])
			rightClickCellFunction, rightClickLabelFunction = self.getArguments(argument_catalogue, ["rightClickCellFunction", "rightClickLabelFunction"])

			readOnlyDefault, cellType, cellTypeDefault = self.getArguments(argument_catalogue, ["readOnlyDefault", "cellType", "cellTypeDefault"])
			
			#Remember Values
			self.rowSizeMaximum = rowSizeMaximum
			self.columnSizeMaximum = columnSizeMaximum

			#Create the thing to put in the grid
			self.thing = self.Table(self, self.parent.thing, style = wx.WANTS_CHARS)
			self.thing.SetDefaultCellAlignment(wx.ALIGN_LEFT, wx.ALIGN_TOP)
			self.thing.CreateGrid(rows, columns)

			#Grid Enabling
			if (readOnly != None):
				if (readOnly):
					self.thing.EnableCellEditControl(False)
			if ((preEditFunction != None) or (postEditFunction != None)):
				self.thing.EnableEditing(True)

			if (showGrid):
				self.thing.EnableGridLines(True)

			##Grid Dragables
			if (dragableColumns):
				self.thing.EnableDragColSize(True)
			else:
				self.thing.EnableDragColMove(False)  

			if (dragableColumns or dragableRows):
				self.thing.EnableDragGridSize(True)
			self.thing.SetMargins(0, 0)

			if (dragableRows):
				self.thing.EnableDragRowSize(True)
			else:
				self.thing.EnableDragRowSize(True)
			
			##Row and Column Sizes
			self.setRowSize(rowSize, autoSizeRow)
			self.setColumnSize(columnSize, autoSizeColumn)

			if (columnSize != None):
				if (isinstance(columnSize, dict)):
					for column, value in columnSize.items():
						self.thing.SetColSize(column, value)
				else:
					for i in range(nColumns):
						self.thing.SetColSize(i, columnSize)         

			if (rowLabelSize != None):
				self.thing.SetRowLabelSize(rowLabelSize)

			if (columnLabelSize != None):
				self.thing.SetColLabelSize(columnLabelSize)

			##Minimum Sizes
			if (rowSizeMinimum != None):
				self.thing.SetRowMinimalAcceptableHeight(rowSizeMinimum)
			
			if (columnSizeMinimum != None):
				self.thing.SetColMinimalAcceptableWidth(columnSizeMinimum)

			##Grid Alignments
			self.thing.SetColLabelAlignment(wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
			self.thing.SetRowLabelAlignment(wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)

			##Grid Values
			for i in range(len(gridLabels[1])):
				self.thing.SetColLabelValue(i, str(colLabels[i]))

			for i in range(len(gridLabels[0])):
				self.thing.SetRowLabelValue(i, str(colLabels[i]))

			##Populate Given Cells
			if (contents != None):
				for row in range(len(contents)):
					for column in range(len(contents[0])):
						self.thing.SetCellValue(row, column, contents[row][column])

			##Set Editability for Cells
			self.readOnlyCatalogue = {}
			self.readOnlyDefault = readOnlyDefault
			self.disableTableEditing(readOnly)
			for row in range(self.thing.GetNumberRows()):
				for column in range(self.thing.GetNumberCols()):
					if (row not in self.readOnlyCatalogue):
						self.readOnlyCatalogue[row] = {}
					if (column not in self.readOnlyCatalogue[row]):
						self.readOnlyCatalogue[row][column] = {}
					
					if (readOnly != None):
						if (isinstance(readOnly, bool)):
							self.readOnlyCatalogue[row][column] = readOnly
						else:
							if (row in readOnly):
								#Account for whole row set
								if (isinstance(readOnly[row], bool)):
									self.readOnlyCatalogue[row][column] = readOnly[row]
								else:
									if (column in readOnly[row]):
										self.readOnlyCatalogue[row][column] = readOnly[row][column]
									else:
										self.readOnlyCatalogue[row][column] = readOnlyDefault

							elif (None in readOnly):
								#Account for whole column set
								if (column in readOnly[None]):
									self.readOnlyCatalogue[row][column] = readOnly[None][column]
								else:
									self.readOnlyCatalogue[row][column] = readOnlyDefault
							else:
								self.readOnlyCatalogue[row][column] = readOnlyDefault
					else:
						self.readOnlyCatalogue[row][column] = readOnlyDefault

			##Set Cell Type for Cells
			self.cellTypeCatalogue = {}
			self.enterKeyExitEdit = enterKeyExitEdit
			self.cellTypeDefault = cellTypeDefault
			self.setTableCellType()

			for row in range(self.thing.GetNumberRows()):
				for column in range(self.thing.GetNumberCols()):
					self.setTableCellType(cellType, row, column)

			##Default Cell Selection
			if ((default != None) and (default != (0, 0))):
				self.thing.GoToCell(default[0], default[1])

			#Bind the function(s)
			if (preEditFunction != None):
				preEditFunctionArgs, preEditFunctionKwargs = self.getArguments(argument_catalogue, ["preEditFunctionArgs", "preEditFunctionKwargs"])
				self.setFunction_preEdit(preEditFunction, preEditFunctionArgs, preEditFunctionKwargs)

			if (postEditFunction != None):
				postEditFunctionArgs, postEditFunctionKwargs = self.getArguments(argument_catalogue, ["postEditFunctionArgs", "postEditFunctionKwargs"])
				self.setFunction_postEdit(postEditFunction, postEditFunctionArgs, postEditFunctionKwargs)
			
			if (dragFunction != None):      
				dragFunctionArgs, dragFunctionKwargs = self.getArguments(argument_catalogue, ["dragFunctionArgs", "dragFunctionKwargs"])
				self.setFunction_drag(dragFunction, dragFunctionArgs, dragFunctionKwargs)

			if (selectManyFunction != None):
				selectManyFunctionArgs, selectManyFunctionKwargs = self.getArguments(argument_catalogue, ["selectManyFunctionArgs", "selectManyFunctionKwargs"])
				self.setFunction_selectMany([self.setTablePreviousCell, selectManyFunction], [None, selectManyFunctionArgs], [None, selectManyFunctionKwargs])
			else:
				self.setFunction_selectMany(self.setTablePreviousCell)

			if (selectSingleFunction != None):
				selectSingleFunctionArgs, selectSingleFunctionKwargs = self.getArguments(argument_catalogue, ["selectSingleFunctionArgs", "selectSingleFunctionKwargs"])
				self.setFunction_selectSingle([self.setTablePreviousCell, selectSingleFunction], [None, selectSingleFunctionArgs], [None, selectSingleFunctionKwargs])
			else:
				self.setFunction_selectSingle(self.setTablePreviousCell)
			
			if (rightClickCellFunction != None):
				rightClickCellFunctionArgs, rightClickCellFunctionKwargs = self.getArguments(argument_catalogue, ["rightClickCellFunctionArgs", "rightClickCellFunctionKwargs"])
				self.setFunction_rightClickCell(rightClickCellFunction, rightClickCellFunctionArgs, rightClickCellFunctionKwargs)

			if (rightClickLabelFunction != None):
				rightClickLabelFunctionArgs, rightClickLabelFunctionKwargs = self.getArguments(argument_catalogue, ["rightClickLabelFunctionArgs", "rightClickLabelFunctionKwargs"])
				self.setFunction_rightClickLabel(rightClickLabelFunction, rightClickLabelFunctionArgs, rightClickLabelFunctionKwargs)

			if (toolTips != None):
				self.betterBind(wx.EVT_MOTION, self.thing, self.onTableDisplayToolTip, toolTips)

			if (arrowKeyExitEdit):
				self.betterBind(wx.EVT_KEY_DOWN, self.thing, self.onTableArrowKeyMove, mode = 2)

			if (editOnEnter):
				self.betterBind(wx.EVT_KEY_DOWN, self.thing.GetGridWindow(), self.onTableEditOnEnter, mode = 2)

			self.betterBind(wx.EVT_SIZE, self.thing, self.onTableAutoSize, mode = 2)
		
		#########################################################

		self.preBuild(argument_catalogue)

		if (self.type.lower() == "table"):
			build_table()
		else:
			warnings.warn(f"Add {self.type} to build() for {self.__repr__()}", Warning, stacklevel = 2)

		self.postBuild(argument_catalogue)


	#Getters
	def getValue(self, row = None, column = None, event = None):
		"""Returns what the contextual value is for the object associated with this handle."""

		if (self.type.lower() == "table"):
			if ((row == None) or (column == None)):
				value = []
				selection = self.getTableCurrentCell(event = event)
				for _row, _column in selection:
					value.append(self.getTableCellValue(_row, _column)) #(list) - What is in the selected cells
			else:
				value = self.getTableCellValue(row, column) #(str) - What is in the requested cell
		else:
			warnings.warn(f"Add {self.type} to getValue() for {self.__repr__()}", Warning, stacklevel = 2)
			value = None

		return value

	def getAll(self):
		"""Returns all the contextual values for the object associated with this handle."""

		if (self.type.lower() == "table"):
			value = []
			for _row in range(self.thing.GetNumberRows()):
				row = []
				for _column in range(self.thing.GetNumberCols()):
					row.append(self.getTableCellValue(_row, _column)) #(list) - What is in each cell
				value.append(row)

		else:
			warnings.warn(f"Add {self.type} to getAll() for {self.__repr__()}", Warning, stacklevel = 2)
			value = None

		return value

	#Change Settings
	def setFunction_click(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		self.setFunction_selectSingle(myFunction = myFunction, myFunctionArgs = myFunctionArgs, myFunctionKwargs = myFunctionKwargs)

	def setFunction_rightClick(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		self.setFunction_rightClickCell(myFunction = myFunction, myFunctionArgs = myFunctionArgs, myFunctionKwargs = myFunctionKwargs)

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
	def setColumnNumber(self, number):
		"""Changes the number of columns in the table.
		Modified Code from: https://www.pythonstudio.us/wxpython/how-do-i-add-and-delete-rows-columns-and-cells.html

		number (int) - How many columns to make the table have

		Example Input: setColumnNumber(10)
		"""

		current = self.thing.GetNumberCols()
		if (number != current):
			if (number > current):
				self.thing.AppendCols(number - current)
				self.disableTableEditing(column = range(current - 1, number))
			else:
				self.thing.DeleteCols(number, current - number)

			self.thing.ForceRefresh()
			self.onTableAutoSize()

	def setRowNumber(self, number):
		"""Changes the number of rows in the table.
		Modified Code from: https://www.pythonstudio.us/wxpython/how-do-i-add-and-delete-rows-rows-and-cells.html

		number (int) - How many rows to make the table have

		Example Input: setRowNumber(10)
		"""

		current = self.thing.GetNumberRows()
		if (number != current):
			if (number > current):
				self.thing.AppendRows(number - current)
				self.disableTableEditing(row = range(current - 1, number))
			else:
				self.thing.DeleteRows(number, current - number)

			self.thing.ForceRefresh()
			self.onTableAutoSize()

	def setRowSize(self, size = -1, autoSize = -1):
		"""Changes the size of a row.

		size (str) - The height of the rows
			- If None: Will make it the default size
			- If dict: {row (int): size (int)}. Use None to define the default size
			- If -1: Will use the size in memory
		autoSize (bool) - Determines the size of the rows based on the sizer element. 'size' will override this
			- If None: Will remove autoSize behavior
			- If dict: {row (int): autoSize (int)}. Use None to define the default state
			- If -1: Will use the autoSize in memory

		Example Input: setRowSize(size = 20)
		Example Input: setRowSize(autoSize = None)
		Example Input: setRowSize(size = {0: 50, None: 20})
		Example Input: setRowSize(size = {0: 50}, autoSize = True)
		Example Input: setRowSize(size = {0: 50, None: 20}, autoSize = {1: True})
		"""

		#Setup
		if (size == -1):
			size = self.rowSize
		if (autoSize == -1):
			autoSize = self.autoSizeRow

		default = self.thing.GetDefaultRowSize()
		if (size == None):
			size = default

		if (not isinstance(size, dict)):
			size = {None: size}
		elif (None not in size):
			size[None] = default

		if (not isinstance(autoSize, dict)):
			autoSize = {None: autoSize}
		elif (None not in autoSize):
			autoSize[None] = False

		#Account for exceeding the maximum
		if (not isinstance(self.rowSizeMaximum, dict)):
			self.rowSizeMaximum = {None: self.rowSizeMaximum}
		elif (None not in self.rowSizeMaximum):
			self.rowSizeMaximum[None] = None

		for row, value in size.items():
			if ((row in self.rowSizeMaximum) and (self.rowSizeMaximum[row]) != None):
				if (value > self.rowSizeMaximum[row]):
					size[row] = self.rowSizeMaximum[row]

		#Modify Size
		for row in range(self.thing.GetNumberRows()):
			self.thing.SetRowSize(row, size[None])

		for row, value in size.items():
			if (row != None):
				if (value == None):
					value = default
				self.thing.SetRowSize(row, value)

		#Remember Values
		self.rowSize = size
		self.autoSizeRow = autoSize

	def setColumnSize(self, size = -1, autoSize = -1):
		"""Changes the size of a column.

		size (str) - The height of the columns
			- If None: Will make it the default size
			- If dict: {column (int): size (int)}. Use None to define the default size
			- If -1: Will use the size in memory
		autoSize (bool) - Determines the size of the columns based on the sizer element. 'size' will override this
			- If None: Will remove autoSize behavior
			- If dict: {column (int): autoSize (int)}. Use None to define the default state
			- If -1: Will use the autoSize in memory

		Example Input: setColumnSize(size = 20)
		Example Input: setColumnSize(autoSize = None)
		Example Input: setColumnSize(size = {0: 50, None: 20})
		Example Input: setColumnSize(size = {0: 50}, autoSize = True)
		Example Input: setColumnSize(size = {0: 50, None: 20}, autoSize = {1: True})
		"""

		#Setup
		if (size == -1):
			size = self.columnSize
		if (autoSize == -1):
			autoSize = self.autoSizeColumn

		default = self.thing.GetDefaultColSize()
		if (size == None):
			size = default

		if (not isinstance(size, dict)):
			size = {None: size}
		elif (None not in size):
			size[None] = default

		if (not isinstance(autoSize, dict)):
			autoSize = {None: autoSize}
		elif (None not in autoSize):
			autoSize[None] = False

		#Account for exceeding the maximum
		if (not isinstance(self.columnSizeMaximum, dict)):
			self.columnSizeMaximum = {None: self.columnSizeMaximum}
		elif (None not in self.columnSizeMaximum):
			self.columnSizeMaximum[None] = None

		for column, value in size.items():
			if ((column in self.columnSizeMaximum) and (self.columnSizeMaximum[column]) != None):
				if (value > self.columnSizeMaximum[column]):
					size[column] = self.columnSizeMaximum[column]

		#Modify Size
		for column in range(self.thing.GetNumberCols()):
			self.thing.SetColSize(column, size[None])

		for column, value in size.items():
			if (column != None):
				if (value == None):
					value = default
				self.thing.SetColSize(column, value)

		#Remember Values
		self.columnSize = size
		self.autoSizeColumn = autoSize

	def setTablePreviousCell(self, row = None, column = None, event = None):
		"""Sets the internal previous cell to the specified value.
		If 'row' and 'column' are None, it will take the current cell.

		Example Input: setTablePreviousCell()
		Example Input: setTablePreviousCell(1, 2)
		"""

		if ((row != None) and (column != None)):
			self.previousCell = (row, column)
		else:
			self.previousCell = self.getTableCurrentCell(event = event)[0]

	def getTablePreviousCell(self):
		"""Returns the previous cell coordinates.

		Example Input: getTablePreviousCell()
		"""

		return self.previousCell

	def getTablePreviousCellValue(self):
		"""Returns the value at the previous cell coordinates.

		Example Input: getTablePreviousCellValue()
		"""

		row, column = self.previousCell
		value = self.getTableCellValue(row, column)
		return value

	def appendRow(self, numberOf = 1, updateLabels = True):
		"""Adds one or more new rows to the bottom of the grid.
		The top-left corner is cell (0, 0) not (1, 1).

		numberOf (int)      - How many rows to add
		updateLabels (bool) - If True: The row labels will update

		Example Input: appendRow(0)
		Example Input: appendRow(0, 5)
		"""

		self.thing.AppendRows(numberOf, updateLabels)

	def appendColumn(self, numberOf = 1, updateLabels = True):
		"""Adds one or more new columns to the right of the grid.
		The top-left corner is cell (0, 0) not (1, 1).

		numberOf (int)      - How many columns to add
		updateLabels (bool) - If True: The row labels will update

		Example Input: appendColumn(0)
		Example Input: appendColumn(0, 5)
		"""

		self.thing.AppendCols(numberOf, updateLabels)

	def enableTableEditing(self, state = True, row = None, column = None):
		"""Allows the user to edit the table.

		row (int)    - Which row this applies to
		column (int) - Which column this applies to
			- If both 'row' and 'column' are None, the whole table will enabled
			- If both 'row' and 'column' are given, that one cell will be enabled
			- If 'row' is given and 'column' is None', that one row will be enabled
			- If 'row' is None and 'column' is given, that one column will be enabled
		state (bool) - Determines the editability of the table
			- If True: The user will be able to edit all cells.
			- If False: The user will not be able to edit the cells. If an edit function is provided, this cell will be ignored
			- If None: Will use the default
			- A dictionary can be given to single out specific cells, rows, or columns
				~ {row number (int): {column number (int): editability for the cell (bool)}}
				~ {row number (int): editability for the whole row (bool)}
				~ {None: {column number (int): editability for the whole column (bool)}}

		Example Input: enableTableEditing(0)
		Example Input: enableTableEditing(0, row = 0)
		Example Input: enableTableEditing(0, column = 0)
		Example Input: enableTableEditing(0, row = 0, column = 0)
		"""

		if (state == None):
			newState = state
		elif (isinstance(state, bool)):
			newState = not state
		elif (isinstance(state, dict)):
			newState = {}
			for key, value in state.items():
				if (not isinstance(value, dict)):
					if (state == None):
						newState[key] = value
					else:
						newState[key] = not value
				else:
					if (key not in newState):
						newState[key] = {}
					for subKey, subValue in value.items():
						if (not isinstance(subValue, dict)):
							if (subValue == None):
								newState[key][subKey] = subValue
							else:
								newState[key][subKey] = not subValue
		else:
			errorMessage = f"'state' must be a bool or a dict, not {type(state)} for enableTableEditing() in {self.__repr__()}"
			raise KeyError(errorMessage)

		self.disableTableEditing(row = row, column = column,  state = newState)

	def disableTableEditing(self, state = False, row = None, column = None):
		"""Allows the user to edit the table.

		row (int)    - Which row this applies to
		column (int) - Which column this applies to
			If both 'row' and 'column' are None, the whole table will disabled
			If both 'row' and 'column' are given, that one cell will be disabled
			If 'row' is given and 'column' is None, that one row will be disabled
			If 'row' is None and 'column' is given, that one column will be disabled
		state (bool) - Determines the editability of the table
			- If True: The user will not be able to edit the cells. If an edit function is provided, this cell will be ignored
			- If False: The user will be able to edit all cells.
			- If None: Will use the default
			- A dictionary can be given to single out specific cells, rows, or columns
				~ {row number (int): {column number (int): editability for the cell (bool)}}
				~ {row number (int): editability for the whole row (bool)}
				~ {None: {column number (int): editability for the whole column (bool)}}

		Example Input: disableTableEditing(0)
		Example Input: disableTableEditing(0, row = 0)
		Example Input: disableTableEditing(0, column = 0)
		Example Input: disableTableEditing(0, row = 0, column = 0)
		"""

		def modifyReadonly(state, row = None, column = None):
			"""Modifies the readOnly catalogue

			state (str)  - Determines the editability of the table
			row (int)    - Which row to add this to
				- If None: Will apply to all rows
			column (int) - Which column to add this to
				- If None: Will apply to all columns

			Example Input: modifyReadonly(state[_row][_column], _row, _column)
			"""
			nonlocal self

			#Determine affected cells
			rowList = range(self.thing.GetNumberRows()) if (row == None) else [row]
			columnList = range(self.thing.GetNumberCols()) if (column == None) else [column]

			#Apply readOnly
			for _row in rowList:
				if (_row not in self.readOnlyCatalogue):
					self.readOnlyCatalogue[_row] = {}
				for _column in columnList:
					self.readOnlyCatalogue[_row][_column] = state
			
		#########################################################	

		if (state == None):
			state = self.readOnlyDefault

		if (row == None):
			row = range(self.thing.GetNumberRows())
		elif (not isinstance(row, (list, tuple, range))):
			row = [row]
		
		if (column == None):
			column = range(self.thing.GetNumberCols())
		elif (not isinstance(column, (list, tuple, range))):
			column = [column]
		
		for _row in row:
			for _column in column:
				if (not isinstance(state, dict)):
					modifyReadonly(state, _row, _column)
				else:
					if (_row in state):
						if (isinstance(state[_row], str)):
							#Define for whole row
							modifyReadonly(state[_row], _row, _column)
						else:
							if (_column in state[_row]):
								#Define for individual cell or whole column if _row is None
								modifyReadonly(state[_row][_column], _row, _column)

	def getTableReadOnly(self, row, column):
		"""Returns if the given cell is readOnly or not.
		The top-left corner is cell (0, 0) not (1, 1).

		row (int)         - The index of the row
		column (int)      - The index of the column

		Example Input: getTableReadOnly(1, 1)
		"""

		readOnly = self.readOnlyCatalogue[row][column]
		return readOnly

	def getTableCurrentCellReadOnly(self, event = None):
		"""Returns if the current cell is readOnly or not.
		The top-left corner is cell (0, 0) not (1, 1).

		Example Input: getTableCurrentCellReadOnly()
		"""

		selection = self.getTableCurrentCell(event = event)

		#Default to the top left cell if a range is selected
		row, column = selection[0]

		readOnly = self.getTableReadOnly(row, column)
		return readOnly

	def getTableCellType(self, row, column):
		"""Returns the widget type of the given cell.
		The top-left corner is cell (0, 0) not (1, 1).

		row (int)         - The index of the row
		column (int)      - The index of the column

		Example Input: getTableCellType(1, 1)
		"""

		cellType = self.cellTypeCatalogue[row][column]
		return cellType

	def getTableCurrentCellType(self, event = None):
		"""Returns the widget type of the current cell.
		The top-left corner is cell (0, 0) not (1, 1).

		Example Input: getTableCurrentCellType()
		"""

		selection = self.getTableCurrentCell(event = event)

		#Default to the top left cell if a range is selected
		row, column = selection[0]

		readOnly = self.getTableCellType(row, column)
		return readOnly

	def setTableCellType(self, cellType = None, row = None, column = None):
		"""Changes the cell types for the table.

		cellType (dict) - Determines the widget type used for a specific cell in the table
			~ {row number (int): {column number (int): cell type for the cell (str)}}
			~ {row number (int): cell type for the whole row (str)}
			~ {None: {column number (int): cell type for the whole column (str)}}
			- Can be a string that applies to the given row and column
			- Possible Inputs: "inputBox", "dropList"
			- If None: will apply the default cell type
		row (int) - Which row to apply this cell type to. Can be a list. Must be in the dict for 'cellType' or 'cellType' must be a string
		column (int) - Which column to apply this cell type to. Can be a list. Must be in the dict for 'cellType' or 'cellType' must be a string

		Example Input: setTableCellType()
		Example Input: setTableCellType("dropList")
		Example Input: setTableCellType("dropList", column = 1)
		Example Input: setTableCellType({None: {1: "dropList"}})
		Example Input: setTableCellType("dropList", row = [1, 2, 5])
		"""

		def addEditor(cellType, row = None, column = None):
			"""Adds the requested editor to the provided cell.
			Creates the requested editor if it does not exist.
			Special thanks to RobinD42 for how to fix an error when closing the window on https://github.com/wxWidgets/Phoenix/issues/627

			cellType (str) - What type of editor to add
			row (int)      - Which row to add this to
				- If None: Will apply to all rows
			column (int)   - Which column to add this to
				- If None: Will apply to all columns

			Example Input: addEditor(cellType[_row][_column], _row, _column)
			"""
			nonlocal self

			#Create editor if needed
			if (str(cellType) not in self.cellTypeCatalogue):
				self.cellTypeCatalogue[str(cellType)] = self.TableCellEditor(self, downOnEnter = self.enterKeyExitEdit, cellType = cellType)

			#Determine affected cells
			if ((row == None) and (column == None)):
				self.thing.SetDefaultEditor(self.cellTypeCatalogue[str(cellType)])

			rowList = range(self.thing.GetNumberRows()) if (row == None) else [row]
			columnList = range(self.thing.GetNumberCols()) if (column == None) else [column]

			#Assign editor to grid
			for _row in rowList:
				for _column in columnList:
					self.thing.SetCellEditor(_row, _column, self.cellTypeCatalogue[str(cellType)])

			#Increment the reference variable for managing clones
			self.cellTypeCatalogue[str(cellType)].IncRef()
			
		#########################################################	

		if (cellType == None):
			cellType = self.cellTypeDefault
		if (not isinstance(row, (list, tuple, range))):
			row = [row]
		if (not isinstance(column, (list, tuple, range))):
			column = [column]
		
		for _row in row:
			for _column in column:
				if (not isinstance(cellType, dict)):
					addEditor(cellType, _row, _column)
				else:
					if (_row in cellType):
						if (isinstance(cellType[_row], str)):
							#Define for whole row
							addEditor(cellType[_row], _row, _column)
						else:
							if (_column in cellType[_row]):
								#Define for individual cell or whole column if _row is None
								addEditor(cellType[_row][_column], _row, _column)

	def clearTable(self):
		"""Clears all cells in the table

		Example Input: clearTable()
		"""
		
		self.thing.ClearGrid()

	def setTableCursor(self, row, column):
		"""Moves the table highlight cursor to the given cell coordinates
		The top-left corner is cell (0, 0) not (1, 1).

		row (int)         - The index of the row
		column (int)      - The index of the column

		Example Input: setTableCursor(1, 2)
		"""

		#Set the cell value
		self.thing.GoToCell(row, column)
		self.thing.SetGridCursor(row, column)

	def setTableCell(self, row, column, value, noneReplace = True):
		"""Writes something to a cell.
		The top-left corner is cell (0, 0) not (1, 1).

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
		The top-left corner is cell (0, 0) not (1, 1).

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
		The top-left corner is cell (0, 0) not (1, 1).

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
		The top-left corner is cell (0, 0) not (1, 1).
		Modified code from http://ginstrom.com/scribbles/2008/09/07/getting-the-selected-cells-from-a-wxpython-grid/

		### TO DO: Make this work with events on all three levels ###

		rangeOn (bool)    - Determines what is returned when the user has a range of cells selected
			- If True: Returns [[(row 1, col 1), (row 1, col 2)], [(row 2, col 1), (row 2, col 2)]]
			- If False: Returns (row, col) of which cell in the range is currently active

		Example Input: getTableCurrentCell()
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
				if (isinstance(event, wx.grid.GridEvent)):
					row = event.GetRow()
					column = event.GetCol()
				else:
					row = self.thing.GetGridCursorRow()
					column = self.thing.GetGridCursorCol()
				
				currentCell = [(row, column)]
			else:
				currentCell = selection

		return currentCell

	def getTableCurrentCellValue(self, event = None):
		"""Reads something from rhe currently selected cell.
		The top-left corner is cell (0, 0) not (1, 1).

		Example Input: getTableCurrentCellValue()
		"""

		#Get the selected cell's coordinates
		selection = self.getTableCurrentCell(event = event)

		#Default to the top left cell if a range is selected
		row, column = selection[0]

		#Get the currently selected cell's value
		value = self.getTableCellValue(row, column)

		return value

	def getTableEventCell(self, event):
		"""Returns the row and column of the previously selected cell.
		The top-left corner is cell (0, 0) not (1, 1).

		Example Input: getTableEventCellValue(event)
		"""

		row = event.GetRow()
		column = event.GetCol()

		return (row, column)

	def getTableEventCellValue(self, event):
		"""Reads something from the previously selected cell.
		The top-left corner is cell (0, 0) not (1, 1).

		Example Input: getTableEventCellValue(event)
		"""

		#Get the selected cell's coordinates
		row, column = self.getTableEventCell(event)

		#Get the currently selected cell's value
		value = self.thing.GetCellValue(row, column)

		return value

	def setTableRowLabel(self, row = None, text = ""):
		"""Changes a row's label.
		The top-left corner is cell (0, 0) not (1, 1).

		row (int)  - The index of the row. Can be a list of rows
			- If None: Will apply label to all rows
		text (str) - The new label for the row
			- If dict: {row (int): label (str)}

		Example Input: setTableRowLabel()
		Example Input: setTableRowLabel(0, "Row 1")
		"""

		if (row == None):
			row = range(self.thing.GetNumberRows())
		elif (not isinstance(row, (list, tuple, range))):
			row = [row]

		if (isinstance(text, dict)):
			for key, value in text.items():
				if (not isinstance(value, str)):
					text[key] = f"{value}"
		elif (not isinstance(text, str)):
			text = f"{text}"

		for _row in row:
			if (isinstance(text, dict)):
				if (_row in text):
					self.thing.SetRowLabelValue(_row, text[_row])
			else:
				self.thing.SetRowLabelValue(_row, text)

	def setTableColumnLabel(self, column = None, text = ""):
		"""Changes a cell's column label.
		The top-left corner is cell (0, 0) not (1, 1).

		column (int)  - The index of the column. Can be a list of columns
			- If None: Will apply label to all columns
		text (str) - The new label for the column
			- If dict: {column (int): label (str)}

		Example Input: setTableColumnLabel()
		Example Input: setTableColumnLabel(1, "Column 2")
		"""

		if (column == None):
			column = range(self.thing.GetNumberCols())
		elif (not isinstance(column, (list, tuple, range))):
			column = [column]

		if (isinstance(text, dict)):
			for key, value in text.items():
				if (not isinstance(value, str)):
					text[key] = f"{value}"
		elif (not isinstance(text, str)):
			text = f"{text}"

		for _column in column:
			if (isinstance(text, dict)):
				if (_column in text):
					self.thing.SetColLabelValue(_column, text[_column])
			else:
				self.thing.SetColLabelValue(_column, text)

	def getTableRowLabel(self, row):
		"""Returns a cell's row label
		The top-left corner is cell (0, 0) not (1, 1).

		row (int) - The index of the row. Can be a list of rows
			- If None: Will return the labels of all rows

		Example Input: getTableRowLabel()
		Example Input: getTableRowLabel(1)
		"""

		if (row == None):
			row = range(self.thing.GetNumberRows())
		elif (not isinstance(row, (list, tuple, range))):
			row = [row]

		value = []
		for _row in row:
			text = self.thing.GetRowLabelValue(_row)
			value.append(text)
		
		return value

	def getTableColumnLabel(self, column = None):
		"""Returns a cell's column label
		The top-left corner is cell (0, 0) not (1, 1).

		column (int) - The index of the column. Can be a list of columns
			- If None: Will return the labels of all columns

		Example Input: getTableColumnLabel()
		Example Input: getTableColumnLabel(1)
		Example Input: getTableColumnLabel([1, 3, 4])
		Example Input: getTableColumnLabel(range(5))
		"""

		if (column == None):
			column = range(self.thing.GetNumberCols())
		elif (not isinstance(column, (list, tuple, range))):
			column = [column]

		value = []
		for _column in column:
			text = self.thing.GetColLabelValue(_column)
			value.append(text)
		
		return value

	def setTableCellFormat(self, row, column, format):
		"""Changes the format of the text in a cell.
		The top-left corner is cell (0, 0) not (1, 1).

		row (int)    - The index of the row
		column (int) - The index of the column
		format (str) - The format for the cell
			~ "float" - floating point

		Example Input: setTableCellFormat(1, 2, "float")
		"""

		#Set the cell format
		if (format == "float"):
			self.thing.SetCellFormatFloat(row, column, width, percision)

	def setTableCellColor(self, row = None, column = None, color = None):
		"""Changes the color of the background of a cell.
		The top-left corner is cell (0, 0) not (1, 1).
		If both 'row' and 'column' are None, the entire table will be colored
		Special thanks to  for how to apply changes to the table on https://stackoverflow.com/questions/14148132/wxpython-updating-grid-cell-background-colour

		row (int)     - The index of the row
			- If None: Will color all cells of the column if 'column' is not None
		column (int)  - The index of the column
			- If None: Will color all cells of the column if 'column' is not None
		color (tuple) - What color to use. (R, G, B). Can be a string for standard colors
			- If None: Use thw wxPython background color

		Example Input: setTableCellColor()
		Example Input: setTableCellColor(1, 2, (255, 0, 0))
		Example Input: setTableCellColor(1, 2, "red")
		"""

		color = self.getColor(color)

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
		The top-left corner is cell (0, 0) not (1, 1).

		row (int)     - The index of the row
			- If None: Will color all cells of the column if 'column' is not None
		column (int)  - The index of the column
			- If None: Will color all cells of the column if 'column' is not None

		Example Input: getTableCellColor(1, 2)
		"""

		color = self.thing.GetCellBackgroundColour(row, column)
		return color

	def setTableCellFont(self, row, column, font, 
		italic = False, bold = False):
		"""Changes the color of the text in a cell.
		The top-left corner is cell (0, 0) not (1, 1).

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
		The top-left corner is cell (0, 0) not (1, 1).

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
		The top-left corner is cell (0, 0) not (1, 1).

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
		The top-left corner is cell (0, 0) not (1, 1).

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
		The top-left corner is cell (0, 0) not (1, 1).

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
			selection = self.getTableCurrentCell(event)

			#Default to the top left cell if a range is selected
			row, column = selection[0]

			# wx.grid.GridCellEditor(row, column, table)

		event.Skip()

	def onTableAutoSize(self, event = None, distributeRemainer = True, distributeAttempts = 5):
		"""Allows the table to automatically change the size of the columns to fit in the sizer element"""

		def find(autoSize, size, row = True):
			"""Finds the rows or columns.

			Example Input: find(self.autoSizeRow, self.rowSize, row = True)
			Example Input: find(self.autoSizeColumn, self.columnSize, row = False)
			"""
			nonlocal self, nRows, nColumns

			if (autoSize[None] != None):
				itemList = [item for item, state in autoSize.items() if ((item != None) and (state != False) and (item not in size))]
				if (autoSize[None]):
					if (row):
						n = nRows
					else:
						n = nColumns
					itemList.extend([item for item in range(n) if ((item not in itemList) and (item not in size) and (item not in autoSize))])
			else:
				itemList = []

			return itemList

		def calculate(autoSize, itemList, row = True):
			"""Calculates the new size for the row or column.

			Example Input: calculate(self.rowSizeMaximum, rowList, row = True)
			Example Input: calculate(self.columnSizeMaximum, columnList, row = False)
			"""
			nonlocal self, totalSize, distributeRemainer, distributeAttempts, nRows, nColumns

			def checkMaximum():
				"""Checks if the decided value exceeds the maximum for that item.

				Example Input: checkMaximum(autoSize, itemList)
				"""
				nonlocal self, totalSize, autoSize, itemList, row, itemSize, distributeRemainer, n

				#Account for exceeding maximum
				tooLong = {}
				if (autoSize != None):
					for i, item in enumerate(itemList):
						if (item in itemSize):
							value = itemSize[item]
						else:
							value = itemSize[None]

						if ((item in autoSize) and (autoSize[item] < value)):
							tooLong[item] = value - autoSize[item]
						elif ((autoSize[None] != None) and (autoSize[None] < value)):
							tooLong[item] = value - autoSize[None]

					notIncluded = [item for item in range(n) if ((item != None) and (item not in tooLong))]
					if ((not distributeRemainer) or (len(notIncluded) == 0)):
						for item, value in tooLong.items():
							itemSize[item] = itemSize[None] - value
						tooLong = {}
					else:
						for item, value in tooLong.items():
							newValue = math.floor(value / (len(notIncluded) + 1))

							for subItem in notIncluded:
								if (subItem in itemSize):
									itemSize[subItem] += newValue
								else:
									itemSize[subItem] = itemSize[None] + newValue

							if (item in itemSize):
								itemSize[item] -= value
							else:
								itemSize[item] = itemSize[None] - value
				return tooLong

			if (row):
				n = nRows
			else:
				n = nColumns

			itemSize = {None: math.floor(totalSize[int(row)] / (len(itemList) + 1))}

			#Account for not converging upon a solution
			for tries in range(distributeAttempts):
				tooLong = checkMaximum()
				if (len(tooLong) == 0):
					break
			else:
				warnings.warn(f"Could not find a solution in onTableAutoSize.calculate(row = {row}) for {self.__repr__()}", Warning, stacklevel = 2)
				distributeRemainer = False
				checkMaximum()

			return itemSize

		def apply(itemList, itemSize, row = True):
			"""Applies the size change.

			Example Input: apply(rowList, rowSize, row = True)
			Example Input: apply(columnList, columnSize, row = False)
			"""
			nonlocal self

			if (row):
				myFunction = self.thing.SetRowSize
			else:
				myFunction = self.thing.SetColSize

			for item in itemList:
				if (item in itemSize):
					myFunction(item, itemSize[item])
				else:
					myFunction(item, itemSize[None])

		#Enable Disableing
		if ((self.autoSizeRow[None] != None) or (self.autoSizeColumn[None] != None)):
			nRows = self.thing.GetNumberRows()
			nColumns = self.thing.GetNumberCols()

			rowList = find(self.autoSizeRow, self.rowSize, row = True)
			columnList = find(self.autoSizeColumn, self.columnSize, row = False)

			totalSize = self.mySizerItem.GetSize()
			rowSize = calculate(self.rowSizeMaximum, rowList, row = True)
			columnSize = calculate(self.columnSizeMaximum, columnList, row = False)

			apply(rowList, rowSize, row = True)
			apply(columnList, columnSize, row = False)

		if (event != None):
			event.Skip()

	####################################################################################################
	class Table(wx.grid.Grid):
		"""Enables a copy and paste behavior for the table.
		Modified code from ROB on https://stackoverflow.com/questions/28509629/work-with-ctrl-c-and-ctrl-v-to-copy-and-paste-into-a-wx-grid-in-wxpython?answertab=votes#tab-top
		"""
		def __init__(self, parent, panel, style):
			wx.grid.Grid.__init__(self, panel, style = style)
			self.parent = parent
			self.Bind(wx.EVT_KEY_DOWN, self.OnKey)
			self.data4undo = [0, 0, '']

		def OnKey(self, event):
			#If Ctrl+C is pressed...
			if event.ControlDown() and event.GetKeyCode() == 67:
				self.copy()

			#If Ctrl+V is pressed...
			if event.ControlDown() and event.GetKeyCode() == 86:
				self.paste('clip')

			#If Ctrl+Z is pressed...
			if event.ControlDown() and event.GetKeyCode() == 90:
				if self.data4undo[2] != '':
					self.paste('undo')

			#If del is pressed...
			if event.GetKeyCode() == 127:
				# Call delete method
				self.delete()

			#Skip other Key events
			if event.GetKeyCode():
				event.Skip()
				return

		def copy(self):
			#Get number of rows and columns
			topleft = self.GetSelectionBlockTopLeft()
			if list(topleft) == []:
				topleft = []
			else:
				topleft = list(topleft[0])
			
			bottomright = self.GetSelectionBlockBottomRight()
			if list(bottomright) == []:
				bottomright = []
			else:
				bottomright = list(bottomright[0])

			if list(self.GetSelectionBlockTopLeft()) == []:
				rows = 1
				cols = 1
				iscell = True
			else:
				rows = bottomright[0] - topleft[0] + 1
				cols = bottomright[1] - topleft[1] + 1
				iscell = False

			#Data variable contain text that must be set in the clipboard
			data = ''
			#For each cell in selected range append the cell value in the data variable
			#Tabs '    ' for cols and '\r' for rows
			for r in range(rows):
				for c in range(cols):
					if iscell:
						data += str(self.GetCellValue(self.GetGridCursorRow() + r, self.GetGridCursorCol() + c))
					else:
						data += str(self.GetCellValue(topleft[0] + r, topleft[1] + c))
					if c < cols - 1:
						data += '    '
				data += '\n'

			#Create text data object
			clipboard = wx.TextDataObject()

			#Set data object value
			clipboard.SetText(data)

			#Put the data in the clipboard
			if wx.TheClipboard.Open():
				wx.TheClipboard.SetData(clipboard)
				wx.TheClipboard.Close()
			else:
				wx.MessageBox("Can't open the clipboard", "Error")

		def paste(self, stage):
			topleft = list(self.GetSelectionBlockTopLeft())
			if stage == 'clip':
				clipboard = wx.TextDataObject()

				if wx.TheClipboard.Open():
					wx.TheClipboard.GetData(clipboard)
					wx.TheClipboard.Close()
				else:
					wx.MessageBox("Can't open the clipboard", "Error")
				data = clipboard.GetText()

				if topleft == []:
					rowstart = self.GetGridCursorRow()
					colstart = self.GetGridCursorCol()
				else:
					rowstart = topleft[0][0]
					colstart = topleft[0][1]

			elif stage == 'undo':
				data = self.data4undo[2]
				rowstart = self.data4undo[0]
				colstart = self.data4undo[1]
			else:
				wx.MessageBox(f"Paste method {stage} does not exist", "Error")
			text4undo = ''

			#Convert text in a array of lines
			for y, r in enumerate(data.splitlines()):
				#Convert c in a array of text separated by tab
				for x, c in enumerate(r.split('    ')):
					if y + rowstart < self.NumberRows and x + colstart < self.NumberCols :
						text4undo += str(self.GetCellValue(rowstart + y, colstart + x)) + '    '
						
						if (not self.parent.getTableReadOnly(rowstart + y, colstart + x)):
							self.setValue(rowstart + y, colstart + x, c)
				text4undo = text4undo[:-1] + '\n'

			if stage == 'clip':
				self.data4undo = [rowstart, colstart, text4undo]
			else:
				self.data4undo = [0, 0, '']

		def delete(self):
			#Number of rows and cols
			topleft = list(self.GetSelectionBlockTopLeft())
			bottomright = list(self.GetSelectionBlockBottomRight())
			if topleft == []:
				rows = 1
				cols = 1
			else:
				rows = bottomright[0][0] - topleft[0][0] + 1
				cols = bottomright[0][1] - topleft[0][1] + 1

			#Clear cells contents
			for r in range(rows):
				for c in range(cols):
					if topleft == []:
						if (not self.parent.getTableReadOnly(self.GetGridCursorRow() + r, self.GetGridCursorCol() + c)):
							self.setValue(self.GetGridCursorRow() + r, self.GetGridCursorCol() + c, '')
					else:
						if (not self.parent.getTableReadOnly(topleft[0][0] + r, topleft[0][1] + c)):
							self.setValue(topleft[0][0] + r, topleft[0][1] + c, '')

		def setValue(self, row, column, value, triggerEvents = True):
			"""Triggers an event when the data is changed."""

			if (triggerEvents):
				event = wx.grid.GridEvent(self.GetId(), wx.grid.EVT_GRID_CELL_CHANGING.typeId, self, row = row, col = column, sel = True, kbd = wx.KeyboardState(controlDown = True))
				# wx.PostEvent(self.GetEventHandler(), event)
				self.GetEventHandler().ProcessEvent(event)

			self.SetCellValue(row, column, value)

			if (triggerEvents):
				event = wx.grid.GridEvent(self.GetId(), wx.grid.EVT_GRID_CELL_CHANGED.typeId, self, row = row, col = column, sel = True, kbd = wx.KeyboardState(controlDown = True))
				# wx.PostEvent(self.GetEventHandler(), event)
				self.GetEventHandler().ProcessEvent(event)

	####################################################################################################        
	class TableCellEditor(wx.grid.GridCellEditor):
		"""Used to modify the grid cell editor's behavior.
		Modified code from: https://github.com/wxWidgets/wxPython/blob/master/demo/GridCustEditor.py
		Cell Type 'droplist' code from: https://wiki.wxpython.org/wxGridCellChoiceEditor2
		"""

		def __init__(self, parent, downOnEnter = True, debugging = False, cellType = None):
			"""Defines internal variables and arranges how the editor will behave.

			downOnEnter (bool) - Determines what happens to the cursor after the user presses enter
				- If True: The cursor will move down one cell
				- If False: The cursor will not move
			debugging (bool)   - Determines if debug information should be displayed or not
				- If True: Debug information will be printed to the command window
			cellType - Which widget type to use for the controller
				- If None: Will use 'inputBox'

			Example Input: TableCellEditor()
			Example Input: TableCellEditor(debugging = True)
			Example Input: TableCellEditor(downOnEnter = False)
			"""

			#Load in default behavior
			super(handle_WidgetTable.TableCellEditor, self).__init__()
			# wx.grid.GridCellEditor.__init__(self)

			#Internal variables
			self.parent = parent
			self.downOnEnter = downOnEnter
			self.debugging = debugging
			self.patching = False
			# self.debugging = True

			if (cellType == None):
				self.cellType = "inputbox"
			else:
				if (isinstance(cellType, (list, tuple))):
					self.cellType = cellType[0]
					self.cellTypeValue = cellType[1]
				else:
					self.cellType = cellType
					self.cellTypeValue = None

			#Write debug information
			if (self.debugging):
				print(f"TableCellEditor.__init__(downOnEnter = {downOnEnter}, debugging = {debugging}, cellType = {cellType})")

			# # event = wx.CommandEvent(wx.grid.EVT_GRID_CELL_CHANGING.typeId, self.parent.thing.GetId())
			# event = wx.grid.GridEvent(self.parent.thing.GetId(), wx.grid.EVT_GRID_CELL_CHANGING.typeId, self.parent.thing, row = 2, col = 3)
			# # event = wx.grid.GridEvent()#wx.ID_ANY, wx.grid.EVT_GRID_CELL_CHANGING.typeId, self.parent.thing.GetId())
			# # event.SetEventType(wx.grid.EVT_GRID_CELL_CHANGING.typeId)
			# # event.SetEventObject(self.parent.thing)

			# print(event.GetRow())

			# wx.PostEvent(self.parent.thing.GetEventHandler(), event)

		def Create(self, parent, myId, event):
			"""Called to create the control, which must derive from wx.Control.
			*Must Override*.
			"""

			#Write debug information
			if (self.debugging):
				print(f"TableCellEditor.Create(parent = {parent}, myId = {myId}, event = {event})")

			#Prepare widget control
			styles = ""

			#Account for special styles
			if (self.cellType.lower() == "droplist"):
				#Ensure that the choices given are a list or tuple
				if (not isinstance(self.cellTypeValue, (list, tuple, range))):
					self.cellTypeValue = [self.cellTypeValue]

				#Ensure that the choices are all strings
				self.cellTypeValue = [str(item) for item in self.cellTypeValue]

				self.myCellControl = wx.Choice(parent, myId, (100, 50), choices = self.cellTypeValue)

				#Check readOnly
				if (self.parent.getTableCurrentCellReadOnly(event = event)):
					self.myCellControl.Enable(False)

			#Use a text box
			else:
				#Check how the enter key is processed
				if (self.downOnEnter):
					style += "|wx.TE_PROCESS_ENTER"

				#Check readOnly
				if (self.parent.getTableCurrentCellReadOnly(event = event)):
					styles += "|wx.TE_READONLY"

				#Strip of extra divider
				if (styles != ""):
					if (styles[0] == "|"):
						styles = styles[1:]
				else:
					styles = "wx.DEFAULT"

				#Create text control
				self.myCellControl = wx.TextCtrl(parent, myId, "", style = eval(styles))
				self.myCellControl.SetInsertionPoint(0)
			
			self.SetControl(self.myCellControl)

			#Handle events
			if (event):
				self.myCellControl.PushEventHandler(event)

		def SetSize(self, rect):
			"""Called to position/size the edit control within the cell rectangle.
			If you don't fill the cell (the rect) then be sure to override
			PaintBackground and do something meaningful there.
			"""

			#Write debug information
			if (self.debugging):
				print(f"TableCellEditor.SetSize(rect = {rect})")

			self.myCellControl.SetSize(rect.x, rect.y, rect.width + 2, rect.height + 2, wx.SIZE_ALLOW_MINUS_ONE)

		def Show(self, show, attr):
			"""Show or hide the edit control. You can use the attr (if not None)
			to set colours or fonts for the control.
			"""

			#Check for patching in process
			if (self.patching):
				return

			#Write debug information
			if (self.debugging):
				print(f"TableCellEditor.Show(show = {show}, attr = {attr})")

			super(handle_WidgetTable.TableCellEditor, self).Show(show, attr)

		def PaintBackground(self, rect, attr):
			"""Draws the part of the cell not occupied by the edit control. The
			base  class version just fills it with background colour from the
			attribute. In this class the edit control fills the whole cell so
			don't do anything at all in order to reduce flicker.
			"""

			#Write debug information
			if (self.debugging):
				print(f"TableCellEditor.PaintBackground(rect = {rect}, attr = {attr})")

		def BeginEdit(self, row, column, grid):
			"""Fetch the value from the table and prepare the edit control
			to begin editing. Set the focus to the edit control.
			*Must Override*
			"""

			#Write debug information
			if (self.debugging):
				print(f"TableCellEditor.BeginEdit(row = {row}, column = {column}, grid = {grid})")

			self.startValue = grid.GetTable().GetValue(row, column)

			#Account for special styles
			if (self.cellType.lower() == "droplist"):
				self.myCellControl.SetStringSelection(self.startValue)
				self.myCellControl.SetFocus()
			else:
				self.myCellControl.SetValue(self.startValue)
				self.myCellControl.SetInsertionPointEnd()
				self.myCellControl.SetFocus()

				self.myCellControl.SetSelection(0, self.myCellControl.GetLastPosition())

			# #Handle Events
			# event = wx.CommandEvent()
			# event.SetEventType(wx.grid.EVT_GRID_CELL_CHANGING.typeId)
			# wx.PostEvent(grid, event)
		
		def EndEdit(self, row, column, grid, oldValue):
			"""End editing the cell. This function must check if the current
			value of the editing control is valid and different from thde
			original value (available as oldValue in its string form.)  If
			it has not changed then simply return None, otherwise return
			the value in its string form.
			*Must Override*

			If you return a non-none, things will enter an infinite loop, because it triggers the
			event wx.grid.EVT_GRID_CELL_CHANGED, which causes this function to run again.
			"""

			#Check for patching in process
			if (self.patching):
				return

			#Write debug information
			if (self.debugging):
				print(f"TableCellEditor.EndEdit(row = {row}, column = {column}, grid = {grid}, oldValue = {oldValue})")

			#Check for read only condition
			if (self.parent.readOnlyCatalogue[row][column]):
				return

			if (self.cellType.lower() == "droplist"):
				newValue = self.myCellControl.GetStringSelection()
			else:
				newValue = self.myCellControl.GetValue()
			
			#Compare Value
			if (newValue != oldValue):
				#Fix loop problem
				self.patching = True

				event = wx.grid.GridEvent(grid.GetId(), wx.grid.EVT_GRID_CELL_CHANGING.typeId, grid, row = row, col = column)
				self.parent.thing.GetEventHandler().ProcessEvent(event)

				self.ApplyEdit(row, column, grid)

				event = wx.grid.GridEvent(grid.GetId(), wx.grid.EVT_GRID_CELL_CHANGED.typeId, grid, row = row, col = column)
				self.parent.thing.GetEventHandler().ProcessEvent(event)

				self.patching = False
				return
				# return newValue
			else:
				# if (self.cellType.lower() == "droplist"):
				#   self.myCellControl.SetStringSelection(self.cellTypeValue[0])
				# else:
				#   self.startValue = ''
				#   self.myCellControl.SetValue('')
				return
			
		def ApplyEdit(self, row, column, grid):
			"""This function should save the value of the control into the
			grid or grid table. It is called only after EndEdit() returns
			a non-None value.
			*Must Override*
			"""

			#Write debug information
			if (self.debugging):
				print(f"TableCellEditor.ApplyEdit(row = {row}, column = {column}, grid = {grid})")

			table = grid.GetTable()

			if (self.cellType.lower() == "droplist"):
				value = self.myCellControl.GetStringSelection()
				self.startValue = self.cellTypeValue[0]
				self.myCellControl.SetStringSelection(self.cellTypeValue[0])
			else:
				value = self.myCellControl.GetValue()
				self.startValue = ''
				self.myCellControl.SetValue('')

			grid.SetCellValue(row, column, value) # update the table
			# table.SetValue(row, column, value) # update the table

			#Move cursor down
			if (self.downOnEnter):
				table.MoveCursorDown(True)

			# #Handle Events
			# event = wx.CommandEvent()
			# event.SetEventType(wx.grid.EVT_GRID_CELL_CHANGED.typeId)
			# event = wx.grid.EVT_GRID_CELL_CHANGED
			# wx.PostEvent(grid, event)

		def Reset(self):
			"""Reset the value in the control back to its starting value.
			*Must Override*
			"""

			#Write debug information
			if (self.debugging):
				print("TableCellEditor.Reset()")

			if (self.cellType.lower() == "droplist"):
				self.myCellControl.SetStringSelection(self.startValue)
			else:
				self.myCellControl.SetValue(self.startValue)
				self.myCellControl.SetInsertionPointEnd()

		def IsAcceptedKey(self, event):
			"""Return True to allow the given key to start editing: the base class
			version only checks that the event has no modifiers. F2 is special
			and will always start the editor.
			"""

			#Write debug information
			if (self.debugging):
				print(f"TableCellEditor.IsAcceptedKey(event = {event})")

			## We can ask the base class to do it
			#return super(handle_WidgetTable.TableCellEditor, self).IsAcceptedKey(event)

			# or do it ourselves
			return (not (event.ControlDown() or event.AltDown()) and
					event.GetKeyCode() != wx.WXK_SHIFT)

		def StartingKey(self, event):
			"""If the editor is enabled by pressing keys on the grid, this will be
			called to let the editor do something about that first key if desired.
			"""

			#Write debug information
			if (self.debugging):
				print(f"TableCellEditor.StartingKey(event = {event})")

			# if (not self.editing):
				# self.editing = True
			if True:
			# if False:
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
					if (self.cellType.lower() == "droplist"):
						if (char in self.cellTypeValue):
							self.myCellControl.SetStringSelection(char)
						else:
							self.myCellControl.SetStringSelection(self.cellTypeValue[0])
					else:
						# For this example, replace the text. Normally we would append it.
						self.myCellControl.AppendText(char)
						# self.myCellControl.SetValue(char)
						self.myCellControl.SetInsertionPointEnd()
			
			event.Skip()

		def StartingClick(self):
			"""If the editor is enabled by clicking on the cell, this method will be
			called to allow the editor to simulate the click on the control if
			needed.
			"""

			#Write debug information
			if (self.debugging):
				print("TableCellEditor.StartingClick()")

			pass

		def Destroy(self):
			"""Final Cleanup"""

			#Write debug information
			if (self.debugging):
				print("TableCellEditor.Destroy()")

			return super(handle_WidgetTable.TableCellEditor, self).Destroy()

		def Clone(self):
			"""Create a new object which is the copy of this one
			*Must Override*
			"""

			#Write debug information
			if (self.debugging):
				print("TableCellEditor.Clone()")

			return TableCellEditor(downOnEnter = self.downOnEnter, debugging = self.debugging)

		def GetControl(self):
			"""Returns the wx control used"""

			#Write debug information
			if (self.debugging):
				print("TableCellEditor.GetControl()")

			return super(handle_WidgetTable.TableCellEditor, self).GetControl()

		def GetValue(self):
			"""Returns the current value in the wx control used"""

			#Write debug information
			if (self.debugging):
				print("TableCellEditor.GetValue()")

			return super(handle_WidgetTable.TableCellEditor, self).GetValue()

		def HandleReturn(self, event):
			"""Helps the enter key use."""

			#Write debug information
			if (self.debugging):
				print(f"TableCellEditor.HandleReturn({event})")

			return super(handle_WidgetTable.TableCellEditor, self).HandleReturn(event)

		def IsCreated(self):
			"""Returns True if the edit control has been created."""

			#Write debug information
			if (self.debugging):
				print("TableCellEditor.IsCreated()")

			return super(handle_WidgetTable.TableCellEditor, self).IsCreated()

		def SetControl(self, control):
			"""Set the wx control that will be used by this cell editor for editing the value."""

			#Write debug information
			if (self.debugging):
				print(f"TableCellEditor.SetControl({control})")

			return super(handle_WidgetTable.TableCellEditor, self).SetControl(control)

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
		self.rows = None
		self.columns = None

	def __str__(self):
		"""Gives diagnostic information on the Sizer when it is printed out."""

		output = handle_Container_Base.__str__(self)
		
		if (self.myWindow != None):
			output += f"-- Window id: {id(self.myWindow)}\n"
		if (self.rows != None):
			output += f"-- Rows: {self.rows}\n"
		if (self.columns != None):
			output += f"-- Columns: {self.columns}\n"
		return output

	def __enter__(self):
		"""Allows the user to use a with statement to build the GUI."""

		#Error handling
		if (self not in self.myWindow.sizersIterating):
			#Allow nested while loops to nest their objects
			self.myWindow.sizersIterating[self] = [True, len(self.myWindow.sizersIterating)]

		handle = handle_Container_Base.__enter__(self)

		return handle

	def __exit__(self, exc_type, exc_value, traceback):
		"""Allows the user to use a with statement to build the GUI."""
		
		#Allow nested while loops to nest their objects
		building = False
		if (self.myWindow.sizersIterating[self][0]):
			building = True
			self.myWindow.sizersIterating[self][0] = False

		state = handle_Container_Base.__exit__(self, exc_type, exc_value, traceback)
		if (state != None):
			return state

		if (building):
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
			errorMessage = f"There is no 'type' {self.type}. The value should be be 'Grid', 'Flex', 'Bag', 'Box', 'Text', or 'Wrap'"
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
				buildSelf.finalNest(self)
		
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
					errorMessage = f"Unknown sizer type {self.type} for {self.__repr__()}"
					raise KeyError(errorMessage)

				flexGrid = self.getArguments(argument_catalogue, "flexGrid")
				if (flexGrid):
					self.thing.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)
				else:
					self.thing.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_NONE)
				
				self.thing.SetFlexibleDirection(direction)

		#Remember variables
		if (sizerType not in ["box", "text", "wrap"]):
			self.rows = rows
			self.columns = columns

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

		self.finalNest(handle)

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

		elif (isinstance(handle, handle_Menu) and (handle.type.lower() == "toolbar")):
			self.thing.Add(handle.thing, int(flex), eval(flags), border)

		elif (isinstance(handle, handle_AuiManager)):
			# self.thing.Add(handle.mySizer.thing, int(flex), eval(flags), border)
			pass

		else:
			warnings.warn(f"Add {handle.__class__} to nest() for {self.__repr__()}", Warning, stacklevel = 2)
			return

		#Remember Values
		if (isinstance(self, handle_Sizer) and (not isinstance(handle, handle_Sizer))):
			for item in self.thing.GetChildren():
				if (item.GetWindow() == handle.thing):
					handle.mySizerItem = item
					break
			else:
				warnings.warn(f"Could not find sizer item for {handle.__repr__()} in nest() for {self.__repr__()}", Warning, stacklevel = 2)

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
		flex = 0, flags = "c1", parent = None, handle = None, mySizer = None):
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
			- If 1: Will align text to the right
			- If 2: Will align text to the center

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
		handle.type = "Text"
		handle.build(locals())
		
		return handle

	def addHyperlink(self, text = "", myWebsite = "",

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, 

		label = None, hidden = False, enabled = True, selected = False, 
		flex = 0, flags = "c1", parent = None, handle = None, mySizer = None):
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
		handle.type = "Hyperlink"
		handle.build(locals())

		return handle

	def addEmpty(self, 

		label = None, hidden = False, enabled = True, selected = False, 
		flex = 0, flags = ["ex", "ba"], parent = None, handle = None, mySizer = None):
		"""Adds an empty space to the next cell on the grid.

		label (any)     - What this is catalogued as
		selected (bool)   - If True: This is the default thing selected
		hidden (bool)     - If True: The widget is hidden from the user, but it is still created

		Example Input: addEmpty()
		Example Input: addEmpty(label = "spacer")
		"""

		handle = handle_WidgetText()
		handle.type = "Empty"
		handle.build(locals())

		return handle

	def addLine(self, vertical = False,

		label = None, hidden = False, enabled = True, selected = False, 
		flex = 0, flags = ["ex", "ba"], parent = None, handle = None, mySizer = None):
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
		handle.type = "Line"
		handle.build(locals())

		return handle

	def addListDrop(self, choices = [], default = None, alphabetic = False,

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, 

		label = None, hidden = False, enabled = True, selected = False, 
		flex = 0, flags = "c1", parent = None, handle = None, mySizer = None):
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
		handle.type = "ListDrop"
		handle.build(locals())

		return handle

	def addListFull(self, choices = [], default = False, singleSelect = False, editable = False,

		report = False, columns = 1, columnNames = {}, columnWidth = {},
		border = True, rowLines = True, columnLines = True, boldHeader = True,
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
		flex = 0, flags = "c1", parent = None, handle = None, mySizer = None):
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
		

		Example Input: addListFull(["Lorem", "Ipsum", "Dolor"])
		Example Input: addListFull(["Lorem", "Ipsum", "Dolor"], myFunction = self.onChosen)

		Example Input: addListFull(["Lorem", "Ipsum", "Dolor"], report = True)
		Example Input: addListFull([["Lorem", "Ipsum"], ["Dolor"]], report = True, columns = 2)
		Example Input: addListFull([["Lorem", "Ipsum"], ["Dolor"]], report = True, columns = 2, columnNames = {0: "Sit", 1: "Amet"})
		Example Input: addListFull({"Sit": ["Lorem", "Ipsum"], "Amet": ["Dolor"]], report = True, columns = 2, columnNames = {0: "Sit", 1: "Amet"})
		Example Input: addListFull({"Sit": ["Lorem", "Ipsum"], 1: ["Dolor"]], report = True, columns = 2, columnNames = {0: "Sit"})

		Example Input: addListFull([["Lorem", "Ipsum"], ["Dolor"]], report = True, columns = 2, columnNames = {0: "Sit", 1: "Amet"}, editable = True)

		Example Input: addListFull(["Lorem", "Ipsum", "Dolor"], drag = True)
		Example Input: addListFull(["Lorem", "Ipsum", "Dolor"], drag = True, dragDelete = True)
		Example Input: addListFull(["Lorem", "Ipsum", "Dolor"], drag = True, dragDelete = True, allowExternalAppDelete = False)

		Example Input: addListFull(["Lorem", "Ipsum", "Dolor"], drop = True)
		Example Input: addListFull(["Lorem", "Ipsum", "Dolor"], drop = True, drag = True)

		Example Input: addListFull(["Lorem", "Ipsum", "Dolor"], drop = True, dropIndex = 2)
		Example Input: addListFull(["Lorem", "Ipsum", "Dolor"], drop = True, dropIndex = -1)
		Example Input: addListFull(["Lorem", "Ipsum", "Dolor"], drop = True, dropIndex = -2)

		Example Input: addListFull(["Lorem", "Ipsum", "Dolor"], drop = True, dropLabel = "text", preDropFunction = self.checkText)
		"""

		handle = handle_WidgetList()
		handle.type = "ListFull"
		handle.build(locals())

		return handle

	def addListTree(self, choices = [], default = None, root = None,
		addButton = True, editable = False, rowHighlight = True, drag = False, drop = False,
		rowLines = True, rootLines = True, variableHeight = True, selectMultiple = False,

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, 
		preEditFunction = None, preEditFunctionArgs = None, preEditFunctionKwargs = None,
		postEditFunction = None, postEditFunctionArgs = None, postEditFunctionKwargs = None,

		preRightDragFunction = None, preRightDragFunctionArgs = None, preRightDragFunctionKwargs = None, 
		postRightDragFunction = None, postRightDragFunctionArgs = None, postRightDragFunctionKwargs = None, 
		preDropFunction = None, preDropFunctionArgs = None, preDropFunctionKwargs = None, 
		postDropFunction = None, postDropFunctionArgs = None, postDropFunctionKwargs = None, 
		dragOverFunction = None, dragOverFunctionArgs = None, dragOverFunctionKwargs = None, 

		preCollapseFunction = None, preCollapseFunctionArgs = None, preCollapseFunctionKwargs = None, 
		postCollapseFunction = None, postCollapseFunctionArgs = None, postCollapseFunctionKwargs = None, 
		preExpandFunction = None, preExpandFunctionArgs = None, preExpandFunctionKwargs = None, 
		postExpandFunction = None, postExpandFunctionArgs = None, postExpandFunctionKwargs = None, 

		rightClickFunction = None, rightClickFunctionArgs = None, rightClickFunctionKwargs = None, 
		middleClickFunction = None, middleClickFunctionArgs = None, middleClickFunctionKwargs = None, 
		doubleClickFunction = None, doubleClickFunctionArgs = None, doubleClickFunctionKwargs = None, 
		
		keyDownFunction = None, keyDownFunctionArgs = None, keyDownFunctionKwargs = None, 
		toolTipFunction = None, toolTipFunctionArgs = None, toolTipFunctionKwargs = None, 
		itemMenuFunction = None, itemMenuFunctionArgs = None, itemMenuFunctionKwargs = None, 

		label = None, hidden = False, enabled = True, selected = False, 
		flex = 0, flags = "c1", parent = None, handle = None, mySizer = None):
		"""Adds a tree list to the next cell on the grid.

		choices (list)          - A list of the choices as strings
		flags (list)            - A list of strings for which flag to add to the sizer
		label (any)           - What this is catalogued as
		default (int)           - Which item in the droplist is selected
			- If a string is given, it will select the first item in the list that matches that string. If noting matches, it will default to the first element
		enabled (bool)          - If True: The user can interact with this

		myFunction (str)        - The function that is ran when the user chooses something from the list. If a list is given, each function will be bound.
		myFunctionArgs (any)    - The arguments for 'myFunction'
		myFunctionKwargs (any)  - The keyword arguments for 'myFunction'function
		
		preEditFunction (str)       - The function that is ran when the user edits something from the list
		preEditFunctionArgs (any)   - The arguments for 'preEditFunction'
		preEditFunctionKwargs (any) - The keyword arguments for 'preEditFunction'function
		
		postEditFunction (str)       - The function that is ran when the user edits something from the list
		postEditFunctionArgs (any)   - The arguments for 'postEditFunction'
		postEditFunctionKwargs (any) - The keyword arguments for 'postEditFunction'function
		
		preRightDragFunction (str)       - The function that is ran when the user tries to right-click drag something from the list; before it begins to drag
		preRightDragFunctionArgs (any)   - The arguments for 'preRightDragFunction'
		preRightDragFunctionKwargs (any) - The keyword arguments for 'preRightDragFunction' function
		
		postRightDragFunction (str)       - The function that is ran when the user tries to right-click drag something from the list; after it begins to drag
		postRightDragFunctionArgs (any)   - The arguments for 'postRightDragFunction'
		postRightDragFunctionKwargs (any) - The keyword arguments for 'postRightDragFunction' function
		
		preDropFunction (str)       - The function that is ran when the user tries to drop something from the list; before it begins to drop
		preDropFunctionArgs (any)   - The arguments for 'preDropFunction'
		preDropFunctionKwargs (any) - The keyword arguments for 'preDropFunction'function
		
		postDropFunction (str)       - The function that is ran when the user tries to drop something from the list; after it drops
		postDropFunctionArgs (any)   - The arguments for 'postDropFunction'
		postDropFunctionKwargs (any) - The keyword arguments for 'postDropFunction'function
		
		dragOverFunction (str)       - The function that is ran when the user drags something over this object
		dragOverFunctionArgs (any)   - The arguments for 'dragOverFunction'
		dragOverFunctionKwargs (any) - The keyword arguments for 'dragOverFunction'function
		
		itemCollapseFunction (str)       - The function that is ran when the user collapses an item
		itemCollapseFunctionArgs (any)   - The arguments for 'itemCollapseFunction'
		itemCollapseFunctionKwargs (any) - The keyword arguments for 'itemCollapseFunction' function
		
		itemExpandFunction (str)       - The function that is ran when the user expands an item
		itemExpandFunctionArgs (any)   - The arguments for 'itemExpandFunction'
		itemExpandFunctionKwargs (any) - The keyword arguments for 'itemExpandFunction'function

		itemRightClickFunction (str)       - The function that is ran when the user right clicks on an item
		itemRightClickFunctionArgs (any)   - The arguments for 'itemRightClickFunction'
		itemRightClickFunctionKwargs (any) - The keyword arguments for 'itemRightClickFunction' function

		itemMiddleClickFunction (str)       - The function that is ran when the user expands an item
		itemMiddleClickFunctionArgs (any)   - The arguments for 'itemMiddleClickFunction'
		itemMiddleClickFunctionKwargs (any) - The keyword arguments for 'itemMiddleClickFunction'function

		keyDownFunction (str)       - The function that is ran when the user uses the arrow keys to select an item
		keyDownFunctionArgs (any)   - The arguments for 'keyDownFunction'
		keyDownFunctionKwargs (any) - The keyword arguments for 'keyDownFunction'function

		toolTipFunction (str)       - The function that is ran when the user requests a tool tip
		toolTipFunctionArgs (any)   - The arguments for 'toolTipFunction'
		toolTipFunctionKwargs (any) - The keyword arguments for 'toolTipFunction'function

		Example Input: addListTree(choices = {"Lorem": [{"Ipsum": "Dolor"}, "Sit"], "Amet": None})
		Example Input: addListTree(choices = {"Lorem": [{"Ipsum": "Dolor"}, "Sit"], "Amet": None}, label = "chosen")
		"""

		handle = handle_WidgetList()
		handle.type = "ListTree"
		handle.build(locals())

		return handle

	def addInputSlider(self, myMin = 0, myMax = 100, myInitial = 0, vertical = False,

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None,

		label = None, hidden = False, enabled = True, selected = False, 
		flex = 0, flags = "c1", parent = None, handle = None, mySizer = None):
		"""Adds a slider bar to the next cell on the grid.

		myMin (int)             - The minimum value of the slider bar
		myMax (int)             - The maximum value of the slider bar
		myInitial (int)         - The initial value of the slider bar's position
		myFunction (str)        - The function that is ran when the user enters text and presses enter
		flags (list)            - A list of strings for which flag to add to the sizer
		label (any)           - What this is catalogued as
		myFunctionArgs (any)    - The arguments for 'myFunction'
		myFunctionKwargs (any)  - The keyword arguments for 'myFunction'function

		Example Input: addInputSlider(0, 100, 50, "initialTemperature")
		"""

		handle = handle_WidgetInput()
		handle.type = "Slider"
		handle.build(locals())

		return handle
	
	def addInputBox(self, text = None, maxLength = None, 
		password = False, alpha = False, readOnly = False, tab = True, wrap = None, ipAddress = False,
		
		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, 
		enterFunction = None, enterFunctionArgs = None, enterFunctionKwargs = None, 
		postEditFunction = None, postEditFunctionArgs = None, postEditFunctionKwargs = None,  
		preEditFunction = None, preEditFunctionArgs = None, preEditFunctionKwargs = None,  

		label = None, hidden = False, enabled = True, selected = False, 
		flex = 0, flags = "c1", parent = None, handle = None, mySizer = None):
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
		handle.type = "InputBox"
		handle.build(locals())

		return handle
	
	def addInputSearch(self, text = None, 

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, 
		searchFunction = None, searchFunctionArgs = None, searchFunctionKwargs = None, 
		cancelFunction = None, cancelFunctionArgs = None, cancelFunctionKwargs = None, 

		label = None, hidden = False, enabled = True, selected = False, 
		flex = 0, flags = "c1", parent = None, handle = None, mySizer = None):
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
		handle.type = "InputSearch"
		handle.build(locals())

		return handle
	
	def addInputSpinner(self, myMin = 0, myMax = 100, myInitial = 0, size = wx.DefaultSize, maxSize = None, minSize = None,
		increment = None, digits = None, useFloat = False, readOnly = False, exclude = [],

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, 
		changeTextFunction = True, changeTextFunctionArgs = None, changeTextFunctionKwargs = None,

		label = None, hidden = False, enabled = True, selected = False, 
		flex = 0, flags = "c1", parent = None, handle = None, mySizer = None):
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
		exclude (list)  - A list of integers/floats to exclude from the spinner
		
		myFunctionArgs (any)           - The arguments for 'myFunction'
		myFunctionKwargs (any)         - The keyword arguments for 'myFunction'function
		changeTextFunction (str)       - The function that is ran when the user changes the text in the box directly. If True: Will be the same as myFunction
		changeTextFunctionArgs (any)   - The arguments for 'changeTextFunction'
		changeTextFunctionKwargs (any) - The key word arguments for 'changeTextFunction'
		

		Example Input: addInputSpinner(0, 100, 50, "initialTemperature")
		Example Input: addInputSpinner(0, 100, 50, "initialTemperature", maxSize = (100, 100))
		Example Input: addInputSpinner(0, 100, 50, "initialTemperature", exclude = [1,2,3])
		"""

		handle = handle_WidgetInput()
		handle.type = "InputSpinner"
		handle.build(locals())

		return handle
	
	def addButton(self, text = "", valueLabel = None,

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None,

		label = None, hidden = False, enabled = True, selected = False, 
		flex = 0, flags = "c1", parent = None, handle = None, mySizer = None):
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
		handle.type = "Button"
		handle.build(locals())

		return handle
	
	def addButtonToggle(self, text = "", 

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, 

		label = None, hidden = False, enabled = True, selected = False, 
		flex = 0, flags = "c1", parent = None, handle = None, mySizer = None):
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
		handle.type = "ButtonToggle"
		handle.build(locals())

		return handle
	
	def addButtonCheck(self, text = "", default = False,

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, 

		label = None, hidden = False, enabled = True, selected = False, 
		flex = 0, flags = "c1", parent = None, handle = None, mySizer = None):
		"""Adds a check box to the next cell on the grid.
		Event fires every time the check box is clicked

		text (str)             - What will be written to the right of the button
		myFunction (str)       - What function will be ran when the button is pressed
		flags (list)           - A list of strings for which flag to add to the sizer
		label (any)            - What this is catalogued as
		myFunctionArgs (any)   - The arguments for 'myFunction'
		myFunctionKwargs (any) - The keyword arguments for 'myFunction'function
		selected (bool)        - If True: This is the default thing selected
		enabled (bool)         - If True: The user can interact with this
		hidden (bool)          - If True: The widget is hidden from the user, but it is still created

		Example Input: addButtonCheck("compute?", "computeFinArray", 0)
		"""

		handle = handle_WidgetButton()
		handle.type = "ButtonCheck"
		handle.build(locals())

		return handle
	
	def addButtonCheckList(self, choices = [], multiple = True, sort = False,

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, 

		label = None, hidden = False, enabled = True, selected = False, 
		flex = 0, flags = "c1", parent = None, handle = None, mySizer = None):
		"""Adds a checklist to the next cell on the grid.

		choices (list)          - A list of strings that are the choices for the check boxes
		myFunction (str)        - What function will be ran when the date is changed
		flags (list)            - A list of strings for which flag to add to the sizer
		label (any)           - What this is catalogued as
		myFunctionArgs (any)    - The arguments for 'myFunction'
		myFunctionKwargs (any)  - The keyword arguments for 'myFunction'function
		multiple (bool)         - True if the user can check off multiple check boxes
		sort (bool)             - True if the checklist will be sorted alphabetically or numerically

		Example Input: addButtonCheckList(["Milk", "Eggs", "Bread"], 0, sort = True)
		"""

		handle = handle_WidgetButton()
		handle.type = "CheckList"
		handle.build(locals())

		return handle
	
	def addButtonRadio(self, text = "", groupStart = False, default = False,

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, 

		label = None, hidden = False, enabled = True, selected = False, 
		flex = 0, flags = "c1", parent = None, handle = None, mySizer = None):
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
		handle.type = "ButtonRadio"
		handle.build(locals())

		return handle
	
	def addButtonRadioBox(self, choices = [], title = "", vertical = False, default = 0, maximum = 1,

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, 

		label = None, hidden = False, enabled = True, selected = False, 
		flex = 0, flags = "c1", parent = None, handle = None, mySizer = None):
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
		maximum (int)           - The maximum number of rows or columns (defined by 'vertical') the box can have

		Example Input: addButtonRadioBox(["Button 1", "Button 2", "Button 3"], "self.onQueueValue", 0)
		"""

		handle = handle_WidgetButton()
		handle.type = "ButtonRadioBox"
		handle.build(locals())

		return handle
	
	def addButtonHelp(self, 

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None,

		label = None, hidden = False, enabled = True, selected = False, 
		flex = 0, flags = "c1", parent = None, handle = None, mySizer = None):
		"""Adds a context help button to the next cell on the grid.

		flags (list)            - A list of strings for which flag to add to the sizer
		myFunction (str)        - What function will be ran when the button is pressed
		label (any)           - What this is catalogued as
		myFunctionArgs (any)    - The arguments for 'myFunction'
		myFunctionKwargs (any)  - The keyword arguments for 'myFunction'function
		default (bool)          - If True: This is the default thing selected
		enabled (bool)          - If True: The user can interact with this
		hidden (bool)           - If True: The widget is hidden from the user, but it is still created

		Example Input: addButtonHelp(label = "myHelpButton")
		"""

		handle = handle_WidgetButton()
		handle.type = "ButtonHelp"
		handle.build(locals())

		return handle
	
	def addButtonImage(self, idlePath = "", disabledPath = "", selectedPath = "", 
		focusPath = "", hoverPath = "", text = None,

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, 

		label = None, hidden = False, enabled = True, selected = False, toggle = False, default = False,
		flex = 0, flags = "c1", parent = None, handle = None, mySizer = None):
		"""Adds a button to the next cell on the grid. You design what the button looks like yourself.

		idlePath (str)         - Where the image of the button idling is on the computer
		disabledPath (str)     - Where the image of the button disabled is on the computer
		selectedPath (str)     - Where the image of the button selected is on the computer
		focusPath (str)        - Where the image of the button focused is on the computer
		hoverPath (str)        - Where the image of the button hovered is on the computer
		myFunction (str)       - What function will be ran when the button is pressed
		flags (list)           - A list of strings for which flag to add to the sizer
		label (any)            - What this is catalogued as
		myFunctionArgs (any)   - The arguments for 'myFunction'
		myFunctionKwargs (any) - The keyword arguments for 'myFunction'function
		default (bool)         - If True: This is the default thing selected
		enabled (bool)         - If True: The user can interact with this

		Example Input: addButtonImage("1.bmp", "2.bmp", "3.bmp", "4.bmp", "5.bmp", "computeFinArray")
		"""

		handle = handle_WidgetButton()
		handle.type = "ButtonImage"
		handle.build(locals())

		return handle
	
	def addImage(self, imagePath = "", internal = False, size = wx.DefaultSize,

		label = None, hidden = False, enabled = True, selected = False, 
		flex = 0, flags = "c1", parent = None, handle = None, mySizer = None):
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
		handle.type = "Image"
		handle.build(locals())

		return handle
	
	def addProgressBar(self, myInitial = 0, myMax = 100, vertical = False,

		label = None, hidden = False, enabled = True, selected = False, 
		flex = 0, flags = "c1", parent = None, handle = None, mySizer = None):
		"""Adds progress bar to the next cell on the grid.

		myInitial (int)         - The value that the progress bar starts at
		myMax (int)             - The value that the progress bar is full at
		flags (list)            - A list of strings for which flag to add to the sizer
		label (any)           - What this is catalogued as

		Example Input: addProgressBar(0, 100)
		"""

		handle = handle_Widget_Base()
		handle.type = "ProgressBar"
		handle.build(locals())

		return handle

	def addToolBar(self, showText = False, showIcon = True, showDivider = True,
		detachable = False, flat = False, vertical = False, align = True,
		vertical_text = False, showToolTip = True, top = True,

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None,

		label = None, hidden = False, enabled = True, selected = False, 
		flex = 0, flags = "c1", parent = None, handle = None, mySizer = None):
		"""Adds a tool bar to the next cell on the grid.
		Menu items can be added to this.

		label (str)     - What this is called in the idCatalogue
		detachable (bool) - If True: The menu can be undocked

		Example Input: addToolBar()
		Example Input: addToolBar(label = "first")
		"""

		handle = handle_Menu()
		handle.type = "ToolBar"
		handle.build(locals())

		return handle
	
	def addPickerColor(self, initial = None, addInputBox = False, colorText = False,

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, 

		label = None, hidden = False, enabled = True, selected = False, 
		flex = 0, flags = "c1", parent = None, handle = None, mySizer = None):
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
		handle.type = "PickerColor"
		handle.build(locals())

		return handle
	
	def addPickerFont(self, maxSize = 72, addInputBox = False, fontText = False,

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, 

		label = None, hidden = False, enabled = True, selected = False, 
		flex = 0, flags = "c1", parent = None, handle = None, mySizer = None):
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
		handle.type = "PickerFont"
		handle.build(locals())

		return handle
	
	def addPickerFile(self, text = "Select a File", default = "", initialDir = "*.*", 
		directoryOnly = False, changeCurrentDirectory = False, fileMustExist = False, openFile = False, 
		saveConfirmation = False, saveFile = False, smallButton = False, addInputBox = False, 

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None,

		label = None, hidden = False, enabled = True, selected = False, 
		flex = 0, flags = "c1", parent = None, handle = None, mySizer = None):
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
		

		Example Input: addPickerFile(myFunction = self.openFile, addInputBox = True)
		Example Input: addPickerFile(saveFile = True, myFunction = self.saveFile, saveConfirmation = True, directoryOnly = True)
		"""

		handle = handle_WidgetPicker()
		handle.type = "PickerFile"
		handle.build(locals())

		return handle
	
	def addPickerFileWindow(self, initialDir = "*.*", 
		directoryOnly = True, selectMultiple = False, showHidden = True,

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, 
		editLabelFunction = None, editLabelFunctionArgs = None, editLabelFunctionKwargs = None, 
		rightClickFunction = None, rightClickFunctionArgs = None, rightClickFunctionKwargs = None, 

		label = None, hidden = False, enabled = True, selected = False, 
		flex = 0, flags = "c1", parent = None, handle = None, mySizer = None):
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
		handle.type = "PickerFileWindow"
		handle.build(locals())

		return handle
	
	def addPickerTime(self, time = None,

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, 

		label = None, hidden = False, enabled = True, selected = False, 
		flex = 0, flags = "c1", parent = None, handle = None, mySizer = None):
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

		Example Input: addPickerTime()
		Example Input: addPickerTime("17:30")
		Example Input: addPickerTime("12:30:20")
		"""

		handle = handle_WidgetPicker()
		handle.type = "PickerTime"
		handle.build(locals())

		return handle
	
	def addPickerDate(self, date = None, dropDown = False, 

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, 

		label = None, hidden = False, enabled = True, selected = False, 
		flex = 0, flags = "c1", parent = None, handle = None, mySizer = None):
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

		Example Input: addPickerDate()
		Example Input: addPickerDate("10/16/2000")
		Example Input: addPickerDate(dropDown = True)
		"""

		handle = handle_WidgetPicker()
		handle.type = "PickerDate"
		handle.build(locals())

		return handle
	
	def addPickerDateWindow(self, date = None, showHolidays = False, showOther = False,
		
		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, 
		dayFunction = None, dayFunctionArgs = None, dayFunctionKwargs = None, 
		monthFunction = None, monthFunctionArgs = None, monthFunctionKwargs = None, 
		yearFunction = None, yearFunctionArgs = None, yearFunctionArgsKwargs = None, 

		label = None, hidden = False, enabled = True, selected = False, 
		flex = 0, flags = "c1", parent = None, handle = None, mySizer = None):
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


		Example Input: addPickerDateWindow()
		"""

		handle = handle_WidgetPicker()
		handle.type = "PickerDateWindow"
		handle.build(locals())

		return handle

	def addCanvas(self, size = wx.DefaultSize, position = wx.DefaultPosition, 
		panel = {},

		initFunction = None, initFunctionArgs = None, initFunctionKwargs = None,

		label = None, hidden = False, enabled = True, selected = False, 
		flex = 0, flags = "c1", parent = None, handle = None, mySizer = None):
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
		handle.type = "Canvas"
		handle.build(locals())

		return handle

	def addTable(self, rows = 1, columns = 1,
		contents = None, gridLabels = [[],[]], toolTips = None, autoSizeRow = False, autoSizeColumn = False,
		rowSize = None, columnSize = None, rowLabelSize = None, columnLabelSize = None, 
		rowSizeMinimum = None, columnSizeMinimum = None, rowSizeMaximum = None, columnSizeMaximum = None,

		showGrid = True, dragableRows = False, dragableColumns = False, arrowKeyExitEdit = False, enterKeyExitEdit = False, editOnEnter = False, 
		readOnly = False, readOnlyDefault = False, default = (0, 0), cellType = None, cellTypeDefault = "inputbox",

		preEditFunction = None, preEditFunctionArgs = None, preEditFunctionKwargs = None, 
		postEditFunction = None, postEditFunctionArgs = None, postEditFunctionKwargs = None, 
		dragFunction = None, dragFunctionArgs = None, dragFunctionKwargs = None, 
		selectManyFunction = None, selectManyFunctionArgs = None, selectManyFunctionKwargs = None, 
		selectSingleFunction = None, selectSingleFunctionArgs = None, selectSingleFunctionKwargs = None, 
		rightClickCellFunction = None, rightClickCellFunctionArgs = None, rightClickCellFunctionKwargs = None, 
		rightClickLabelFunction = None, rightClickLabelFunctionArgs = None, rightClickLabelFunctionKwargs = None,

		label = None, hidden = False, enabled = True, selected = False, 
		flex = 0, flags = "c1", parent = None, handle = None, mySizer = None):

		"""Adds a table to the next cell on the grid. 
		If enabled, it can be edited; the column &  sizerNumber, size can be changed.
		To get a cell value, use: myGridId.GetCellValue(row, column).
		For a deep tutorial: http://www.blog.pythonlibrary.org/2010/03/18/wxpython-an-introduction-to-grids/

		rows (int)        - The number of rows the table has
		columns (int)     - The number of columns the table has
		sizerNumber (int) - The number of the sizer that this will be added to
		tableNumber (int) - The table catalogue number for this new table
		flags (list)      - A list of strings for which flag to add to the sizer
		contents (list)   - Either a 2D list [[row], [column]] or a numpy array that contains the contents of each cell. If None, they will be blank.
		gridLabels (str)  - The labels for the [[rows], [columns]]. If not enough are provided, the resst will be capital letters.
		toolTips (list)   - The coordinates and message for all the tool tips. [[row, column, message], [row, column, message], ...]
		label (str)       - What this is called in the idCatalogue
		
		rowSize (str)           - The height of the rows
			- If None: Will make it the default size
			- If dict: {row (int): size (int)}. Use None to define the default size
		columnSize (str)        - The width of the columns
			- If None: Will make it the default size
			- If dict: {column (int): size (int)}. Use None to define the default size
		rowLabelSize (int)      - The width of the row labels
			- If None: Will make it the default size
		columnLabelSize (int)   - The height of the column labels
			- If None: Will make it the default size

		rowSizeMinimum (str)    - The minimum height for the rows
			- If None: Will not restrict minimum row size
		columnSizeMinimum (str) - The minimum width for the columns
			- If None: Will not restrict minimum column size
		rowSizeMaximum (str)    - The maximum height for the rows. Does not apply to the user, only when the program is setting the size
			- If None: Will not restrict maximum row size
		columnSizeMaximum (str) - The maximum width for the columns. Does not apply to the user, only when the program is setting the size
			- If None: Will not restrict maximum column size

		autoSizeRow (bool)      - Determines the size of the rows based on the sizer element. 'rowSize' will override this
			- If dict: {row (int): autoSize (int)}. Use None to define the default state
		autoSizeColumn (bool)   - Determines the size of the columns based on the sizer element. 'columnSize' will override this
			- If dict: {column (int): autoSize (int)}. Use None to define the default state
		
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
				~ {None: {column number (int): readOnly for the whole column (bool)}}
		readOnlyDefault (bool)  - What readOnly value to give a cell if the user does not provide one
		default (tuple)         - Which cell the table starts out with selected. (row, column)
		cellType (dict)         - Determines the widget type used for a specific cell in the table
				~ {row number (int): {column number (int): cell type for the cell (str)}}
				~ {row number (int): cell type for the whole row (str)}
				~ {None: {column number (int): cell type for the whole column (str)}}
		cellTypeDefault (str)   - What the cells default to as a widget
			- Possible Inputs: "inputbox", "droplist"

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
		Example Input: addTable(rows = 3, columns = 4)
		Example Input: addTable(rows = 3, columns = 4, contents = [[1, 2, 3], [a, b, c], [4, 5, 6], [d, e, f]])
		Example Input: addTable(rows = 3, columns = 4, contents = myArray)

		Example Input: addTable(rows = 3, columns = 4, readOnly = True)
		Example Input: addTable(rows = 3, columns = 4, readOnly = {1: True})
		Example Input: addTable(rows = 3, columns = 4, readOnly = {1: {1: True, 3: True}})
		Example Input: addTable(rows = 3, columns = 4, readOnly = {None: {1: True})

		Example Input: addTable(rows = 3, columns = 4, cellType = {1: "droplist"})
		Example Input: addTable(rows = 3, columns = 4, cellType = {1: {1: "droplist", 3: "droplist"}})
		Example Input: addTable(rows = 3, columns = 4, cellType = {None: {1: "droplist"}})

		Example Input: addTable(rows = 3, columns = 4, columnSize = 20)
		Example Input: addTable(rows = 3, columns = 4, columnSize = {0: 50, None: 20})
		Example Input: addTable(rows = 3, columns = 4, columnSize = {0: 50}, autoSizeColumn = True)
		Example Input: addTable(rows = 3, columns = 4, columnSize = {0: 50, None: 20}, autoSizeColumn = {1: True})
		"""

		handle = handle_WidgetTable()
		handle.type = "Table"
		handle.build(locals())

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
		handle.type = "Double"
		handle.build(locals())

		return handle.getSizers()

	def addSplitterQuad(self, sizer_0 = {}, sizer_1 = {}, sizer_2 = {}, sizer_3 = {},

		initFunction = None, initFunctionArgs = None, initFunctionKwargs = None,

		label = None, hidden = False, enabled = True, handle = None):
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
		handle.type = "Quad"
		handle.build(locals())

		return handle.getSizers()

	def addSplitterPoly(self, panelNumbers, sizers = {},
		dividerSize = 1, dividerPosition = None, dividerGravity = 0.5, vertical = False, minimumSize = 20, 

		initFunction = None, initFunctionArgs = None, initFunctionKwargs = None,

		label = None, hidden = False, enabled = True, handle = None):
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
		handle.type = "Poly"
		handle.build(locals())

		return handle.getSizers()

	#Notebooks
	def addNotebook(self, label = None, flags = None, tabSide = "top", flex = 0, 
		fixedWidth = False, multiLine = False, padding = None, reduceFlicker = True,

		initFunction = None, initFunctionArgs = None, initFunctionKwargs = None,
		postPageChangeFunction = None, postPageChangeFunctionArgs = None, postPageChangeFunctionKwargs = None,
		prePageChangeFunction = None, prePageChangeFunctionArgs = None, prePageChangeFunctionKwargs = None,

		hidden = False, enabled = True, handle = None, parent = None):
		"""Creates a blank notebook.

		label (str)        - What this is called in the idCatalogue
		flags (list)       - A list of strings for which flag to add to the sizer

		tabSide (str)     - Determines which side of the panel the tabs apear on. Only the first letter is needed
			- "top": Tabs will be placed on the top (north) side of the panel
			- "bottom": Tabs will be placed on the bottom (south) side of the panel
			- "left": Tabs will be placed on the left (west) side of the panel
			- "right": Tabs will be placed on the right (east) side of the panel
		fixedWidth (bool) - Determines how tab width is determined (windows only)
			- If True: All tabs will be the same width
			- If False: Tab width will be differnet from eachother
		multiLine (bool) - Determines if there can be several rows of tabs
			- If True: There can be multiple rows
			- If False: There cannot be multiple rows
		padding (tuple) - Determines if there is empty space around all of the tab's icon and text in the form (left and right, top and bottom)
			- If None or -1: There is no empty spage
			- If not None or -1: This is how many pixels of empty space there will be

		initFunction (str)       - The function that is ran when the panel first appears
		initFunctionArgs (any)   - The arguments for 'initFunction'
		initFunctionKwargs (any) - The keyword arguments for 'initFunction'function

		Example Input: addNotebook()
		Example Input: addNotebook("myNotebook")
		Example Input: addNotebook(padding = (5, 5))
		Example Input: addNotebook(padding = (5, None))
		"""

		handle = handle_Notebook()
		handle.type = "Notebook"
		handle.build(locals())

		self.nest(handle)

		return handle

	def addNotebookAui(self, label = None, flags = None, flex = 0, 

		tabSide = "top", tabSplit = True, tabMove = True, tabBump = False, 
		tabSmart = True, tabOrderAccess = False, tabFloat = False, 
		addScrollButton = False, addListDrop = None, addCloseButton = None, 
		closeOnLeft = False, middleClickClose = False, fixedWidth = False, drawFocus = True, 

		initFunction = None, initFunctionArgs = None, initFunctionKwargs = None,
		postPageChangeFunction = None, postPageChangeFunctionArgs = None, postPageChangeFunctionKwargs = None,
		prePageChangeFunction = None, prePageChangeFunctionArgs = None, prePageChangeFunctionKwargs = None,

		handle = None, parent = None):
		"""Creates a blank notebook with dockable pages.

		label (str)        - What this is called in the idCatalogue
		flags (list)       - A list of strings for which flag to add to the sizer

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

		Example Input: addNotebookAui()
		Example Input: addNotebookAui("myNotebook")
		"""

		handle = handle_Notebook()
		handle.type = "AuiNotebook"
		handle.build(locals())

		self.nest(handle)

		return handle

	# def addAui(self, label = None, flags = None, flex = 0, 

	#   reduceFlicker = True, 

	#   initFunction = None, initFunctionArgs = None, initFunctionKwargs = None,
	#   postPageChangeFunction = None, postPageChangeFunctionArgs = None, postPageChangeFunctionKwargs = None,
	#   prePageChangeFunction = None, prePageChangeFunctionArgs = None, prePageChangeFunctionKwargs = None,

	#   handle = None, parent = None):
	#   """Creates a container for dockable panels.

	#   label (str)        - What this is called in the idCatalogue
	#   flags (list)       - A list of strings for which flag to add to the sizer

	#   tabSide (str)     - Determines which side of the panel the tabs apear on. Only the first letter is needed
	#       - "top": Tabs will be placed on the top (north) side of the panel
	#       - "bottom": Tabs will be placed on the bottom (south) side of the panel
	#       - "left": Tabs will be placed on the left (west) side of the panel
	#       - "right": Tabs will be placed on the right (east) side of the panel
	#   fixedWidth (bool) - Determines how tab width is determined (windows only)
	#       - If True: All tabs will be the same width
	#       - If False: Tab width will be 

	#   initFunction (str)       - The function that is ran when the panel first appears
	#   initFunctionArgs (any)   - The arguments for 'initFunction'
	#   initFunctionKwargs (any) - The keyword arguments for 'initFunction'function

	#   Example Input: addAui()
	#   Example Input: addAui("myAui")
	#   Example Input: addAui(padding = (5, 5))
	#   Example Input: addAui(padding = (5, None))
	#   """

	#   handle = handle_AuiManager(self, self.myWindow)
	#   handle.build(locals())

	#   self.nest(handle)

	#   return handle

	#Sizers
	def addSizerBox(self, *args, **kwargs):
		"""Overload for addSizerBox in handle_Window().
		Adds the created sizer to this sizer.
		"""

		handle = handle_Sizer()
		handle.type = "Box"

		argument_catalogue = self.arrangeArguments(handle_Window.addSizerBox, args, kwargs)
		argument_catalogue["self"] = self

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

		handle.build(argument_catalogue)
		self.nest(handle)

		return handle

class handle_Dialog(handle_Base):
	"""A handle for working with a wxDialog widget.

	Use: https://www.blog.pythonlibrary.org/2010/06/26/the-dialogs-of-wxpython-part-1-of-2/
	https://www.blog.pythonlibrary.org/2010/07/10/the-dialogs-of-wxpython-part-2-of-2/
	"""

	def __init__(self):
		"""Initializes defaults."""

		#Initialize inherited classes
		handle_Base.__init__(self)

		#Defaults
		self.answer = None
		self.data = None
		self.subType = ""

	def __enter__(self):
		"""Allows the user to use a with statement to build the GUI."""

		handle = handle_Base.__enter__(self)

		self.show()

		return handle

	def __exit__(self, exc_type, exc_value, traceback):
		"""Allows the user to use a with statement to build the GUI."""

		state = handle_Base.__exit__(self, exc_type, exc_value, traceback)

		if (self.type.lower() == "busy"):
			self.hide()

		return state

	def build(self, argument_catalogue):
		"""Determiens which build system to use for this handle."""

		def build_message():
			"""Builds a wx message dialog object."""
			nonlocal self, argument_catalogue

			#Gather variables
			text, title = self.getArguments(argument_catalogue, ["text", "title"])
			stayOnTop, default, icon = self.getArguments(argument_catalogue, ["stayOnTop", "default", "icon"])
			addYes, addOk, addCancel, addHelp = self.getArguments(argument_catalogue, ["addYes", "addOk", "addCancel", "addHelp"])

			#Error Checking
			if (addCancel and not (addYes or addOk)):
				errorMessage = f"'Cancel' must be acompanied with either a [Yes]/[No] and/or [Ok] for {self.__repr__()}"
				raise ValueError(errorMessage)

			#Prepare styles
			style = "wx.CENTRE"

			if (stayOnTop):
				style += "|wx.STAY_ON_TOP"

			##Buttons
			if (addYes):
				style += "|wx.YES_NO"
			if (addOk):
				style += "|wx.OK"
			if (addCancel):
				style += "|wx.CANCEL"
			if (addHelp):
				style += "|wx.HELP"

			##Defaults
			if (addYes):
				if (default):
					style += "|wx.YES_DEFAULT"
				else:
					style += "|wx.NO_DEFAULT"

			elif (addOk):
				if (default):
					style += "|wx.OK_DEFAULT"
				else:
					if (addCancel):
						style += "|wx.CANCEL_DEFAULT"

			##Icons
			if (icon != None):
				if (icon[0].lower() == "h"):
					style += "|wx.ICON_HAND"
					
				elif (icon[0].lower() == "q"):
					style += "|wx.ICON_QUESTION"
					
				elif (icon[0].lower() == "i"):
					style += "|wx.ICON_INFORMATION"
					
				elif (icon[0].lower() == "a"):
					style += "|wx.ICON_AUTH_NEEDED"
					
				elif (icon[0].lower() == "e"):
					if (len(icon) == 1): 
						style += "|wx.ICON_ERROR"

					elif (icon[1].lower() == "r"):
						style += "|wx.ICON_ERROR"

					else:
						style += "|wx.ICON_EXCLAMATION"
				else:
					errorMessage = f"Unknown Icon type '{icon}' for {self.__repr__()}"
					raise KeyError(errorMessage)
			else:
				style += "|wx.ICON_NONE"

			#Create object
			self.thing = wx.MessageDialog(parent = None, message = text, caption = title, style = eval(style))

		def build_scroll():
			"""Builds a wx scroll dialog object."""
			nonlocal self, argument_catalogue

			text, title = self.getArguments(argument_catalogue, ["text", "title"])
			self.thing = wx.lib.dialogs.ScrolledMessageDialog(None, text, title)

		def build_busyInfo():
			"""Builds a wx busy info dialog object."""
			nonlocal self, argument_catalogue

			self.thing = self.getArguments(argument_catalogue, ["text"])

		def build_color():
			"""Builds a wx color dialog object."""
			nonlocal self, argument_catalogue

			simple = self.getArguments(argument_catalogue, ["simple"])

			if (simple != None):
				self.subType = "simple"
				self.thing = wx.ColourDialog(self)
				self.thing.GetColourData().SetChooseFull(not simple)
			else:
				self.thing = wx.lib.agw.cubecolourdialog.CubeColourDialog(self)

		def build_choice():
			"""Builds a wx choice dialog object."""
			nonlocal self, argument_catalogue

			choices, title, text, default, single = self.getArguments(argument_catalogue, ["choices", "title", "text", "default", "single"])

			self.choices = choices
			
			if (single):
				self.subType = "single"
				self.thing = wx.SingleChoiceDialog(None, title, text, choices, wx.CHOICEDLG_STYLE)
			else:
				self.thing = wx.MultiChoiceDialog(None, text, title, choices, wx.CHOICEDLG_STYLE)

			if (default != None):
				if (single):
					self.thing.SetSelection(default)
				else:
					self.thing.SetSelections(default)
		
		#########################################################

		if (self.type.lower() == "message"):
			build_message()
		elif (self.type.lower() == "process"):
			build_process()
		elif (self.type.lower() == "scroll"):
			build_scroll()
		elif (self.type.lower() == "inputBox"):
			build_inputBox()
		elif (self.type.lower() == "busy"):
			build_busyInfo()
		elif (self.type.lower() == "color"):
			build_color()
		elif (self.type.lower() == "file"):
			build_file()
		elif (self.type.lower() == "directory"):
			build_directory()
		elif (self.type.lower() == "open"):
			build_open()
		elif (self.type.lower() == "save"):
			build_save()
		elif (self.type.lower() == "font"):
			build_font()
		elif (self.type.lower() == "image"):
			build_image()
		elif (self.type.lower() == "list"):
			build_list()
		elif (self.type.lower() == "choice"):
			build_choice()
		elif (self.type.lower() == "printSetup"):
			build_pageSetup()
		elif (self.type.lower() == "print"):
			build_print()
		else:
			warnings.warn(f"Add {self.type} to build() for {self.__repr__()}", Warning, stacklevel = 2)

	def show(self):
		"""Shows the dialog box for this handle."""

		#Error Check
		if (self.thing == None):
			warnings.warn(f"The {self.type} dialogue box {self.__repr__()} has already been shown", Warning, stacklevel = 2)
			return

		myThread = threading.current_thread()
		if (myThread != threading.main_thread()):
			warnings.warn(f"The {self.type} dialogue box {self.__repr__()} must be shown in the main thread, not a background thread", Warning, stacklevel = 2)
			return

		#Show dialogue
		if (self.type.lower() == "message"):
			self.answer = self.thing.ShowModal()

			self.thing.Destroy()
			self.thing = None

		elif (self.type.lower() == "choice"):
			self.answer = self.thing.ShowModal()

			if (self.subType.lower() == "single"):
				self.data = self.thing.GetSelection()
			else:
				self.data = self.thing.GetSelections()

			self.thing.Destroy()
			self.thing = None

		elif (self.type.lower() == "scroll"):
			self.answer = self.thing.ShowModal()

			self.thing.Destroy()
			self.thing = None

		elif (self.type.lower() == "busyinfo"):
			self.thing = wx.BusyInfo(self.thing)

		elif (self.type.lower() == "color"):
			self.answer = self.thing.ShowModal()
			self.data = self.thing.GetColourData()

			self.thing.Destroy()
			self.thing = None

		else:
			warnings.warn(f"Add {self.type} to show() for {self.__repr__()}", Warning, stacklevel = 2)

	def hide(self):
		"""Hides the dialog box for this handle."""

		if (self.type.lower() == "busyinfo"):
			del self.thing
			self.thing = None
		else:
			warnings.warn(f"Add {self.type} to hide() for {self.__repr__()}", Warning, stacklevel = 2)

	#Getters
	def getValue(self, event = None):
		"""Returns what the contextual value is for the object associated with this handle."""

		if (self.type.lower() == "choice"):
			if (self.subType.lower() == "single"):
				value = self.choices[self.data]
			else:
				value = [self.choices[i] for i in self.data]

		elif (self.type.lower() == "color"):
			color = self.data.GetColour().Get()
			value = (color.Red(), color.Green(), color.Blue(), color.Alpha())

		else:
			warnings.warn(f"Add {self.type} to getValue() for {self.__repr__()}", Warning, stacklevel = 2)
			value = None

		return value

	def getIndex(self, event = None):
		"""Returns what the contextual value is for the object associated with this handle."""

		if (self.type.lower() == "choice"):
			value = self.data

		else:
			warnings.warn(f"Add {self.type} to getValue() for {self.__repr__()}", Warning, stacklevel = 2)
			value = None

		return value

	def isOk(self):
		"""Returns if the closed dialog box answer was 'ok'."""

		if (self.answer == wx.ID_OK):
			return True
		return False

	def isCancel(self):
		"""Returns if the closed dialog box answer was 'cancel'."""

		if (self.answer == wx.ID_CANCEL):
			return True
		return False

	def isYes(self):
		"""Returns if the closed dialog box answer was 'yes'."""

		if (self.answer == wx.ID_YES):
			return True
		return False

	def isNo(self):
		"""Returns if the closed dialog box answer was 'no'."""

		if (self.answer == wx.ID_NO):
			return True
		return False

class handle_Window(handle_Container_Base):
	"""A handle for working with a wxWindow."""

	def __init__(self, controller):
		"""Initializes defaults."""

		#Initialize inherited classes
		handle_Container_Base.__init__(self)

		#Defaults
		self.mainPanel = None
		self.thing = None
		self.visible = False
		self.complexity_total = 0
		self.complexity_max = 20
		self.controller = controller

		self.statusBarOn = True
		self.toolBarOn = True
		self.autoSize = True
		self.menuBar = None
		self.statusBar = None
		self.auiManager = None

		self.refreshFunction = None
		self.refreshFunctionArgs = None
		self.refreshFunctionKwargs = None

		self.finalFunctionList = []
		self.sizersIterating = {} #Keeps track of which sizers have been used in a while loop, as well as if they are still in the while loop {sizer (handle): [currently in a while loop (bool), order entered (int)]}
		self.keyPressQueue = {} #A dictionary that contains all of the key events that need to be bound to this window
		self.toolTipCatalogue = {} #A dictionary that contains all of the tool tips for this window

	def __str__(self):
		"""Gives diagnostic information on the Window when it is printed out."""

		output = handle_Container_Base.__str__(self)
		
		if (self.mainPanel != None):
			output += f"-- main panel id: {id(self.mainPanel)}\n"
		return output

	def build(self, argument_catalogue):
		#Fill in default values
		for item in inspect.signature(Controller.addWindow).parameters.values():
			if (item.name not in argument_catalogue):
				argument_catalogue[item.name] = item.default

		#Prebuild
		handle_Container_Base.preBuild(self, argument_catalogue)

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

	def getSelection(self, label, *args, **kwargs):
		"""Overload for getSelection for handle_Widget_Base."""

		handle = self.get(label, *args, **kwargs)
		event = self.getArgument_event(label, args, kwargs)
		value = handle.getSelection(event = event)
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
		handle.setValue(newValue, event = event)

	def setSelection(self, label, newValue, *args, **kwargs):
		"""Overload for setSelection for handle_Widget_Base."""

		handle = self.get(label, *args, **kwargs)
		event = self.getArgument_event(label, args, kwargs)
		handle.setSelection(newValue, event = event)

	#Event Functions
	def setFunction_size(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		self.betterBind(wx.EVT_SIZE, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)

	def setFunction_position(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		self.betterBind(wx.EVT_MOVE, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)

	#Change Settings
	def setWindowSize(self, x, y = None):
		"""Re-defines the size of the window.

		x (int)     - The width of the window
		y (int)     - The height of the window

		Example Input: setWindowSize(350, 250)
		Example Input: setWindowSize((350, 250))
		"""

		if (isinstance(x, str)):
			if (x.lower() == "default"):
				self.thing.SetSize(wx.DefaultSize)
				return
			else:
				x = ast.literal_eval(x)

		if (y == None):
			y = x[1]
			x = x[0]

		#Change the frame size
		self.autoSize = False
		self.thing.SetSize((x, y))

	def getWindowSize(self):
		"""Returns the size of the window

		Example Input: getWindowSize()
		"""

		size = self.thing.GetSize()
		return size

	def setWindowPosition(self, x, y = None):
		"""Re-defines the position of the window.

		x (int)     - The width of the window
		y (int)     - The height of the window

		Example Input: setWindowPosition(350, 250)
		Example Input: setWindowPosition((350, 250))
		"""

		if (isinstance(x, str)):
			if (x.lower() == "center"):
				self.centerWindow()
				return
			elif (x.lower() == "default"):
				self.thing.SetPosition(wx.DefaultPosition)
				return
			else:
				x = ast.literal_eval(x)

		if (y == None):
			y = x[1]
			x = x[0]

		#Change the frame size
		self.thing.SetPosition((x, y))

	def getWindowPosition(self):
		"""Returns the position of the window

		Example Input: getWindowPosition()
		"""

		position = self.thing.GetPosition()
		return position

	def setMinimumFrameSize(self, x = (100, 100), y = None):
		"""Sets the minimum window size for the user
		Note: the program can still explicity change the size to be smaller by using setWindowSize().

		size (int tuple) - The size of the window. (length, width)

		Example Input: setMinimumFrameSize()
		Example Input: setMinimumFrameSize(200, 100)
		Example Input: setMinimumFrameSize((200, 100))
		"""

		if (y == None):
			y = x[1]
			x = x[0]

		#Set the size property
		self.thing.SetMinSize((x, y))

	def setMaximumFrameSize(self, x = (900, 700), y = None):
		"""Sets the maximum window size for the user
		Note: the program can still explicity change the size to be smaller by using setWindowSize().

		size (int tuple) - The size of the window. (length, width)

		Example Input: setMaximumFrameSize()
		Example Input: setMaximumFrameSize(700, 300)
		Example Input: setMaximumFrameSize((700, 300))
		"""

		if (y == None):
			y = x[1]
			x = x[0]

		#Set the size property
		self.thing.SetMaxSize((x, y))

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

	def centerWindow(self, offset = None):
		"""Centers the window on the screen.

		Example Input: centerWindow()
		Example Input: centerWindow(offset = (0, -100))
		"""

		if (offset == None):
			offset = (0, 0)

		screenSize = self.getScreenSize()
		windowSize = self.thing.GetSize()

		size_x = math.floor(screenSize[0] / 2 - windowSize[0] / 2 + offset[0])
		size_y = math.floor(screenSize[1] / 2 - windowSize[1] / 2 + offset[1])

		self.thing.SetPosition((size_x, size_y))

	#Visibility
	def showWindow(self, asDialog = False):
		"""Shows a specific window to the user.
		If the window is already shown, it will bring it to the front

		Example Input: showWindow()
		Example Input: showWindow(asDialog = True)
		"""

		self.thing.Show()

		if (asDialog):
			self.controller.windowDisabler = [self.thing, wx.WindowDisabler(self.thing)]

		if (not self.visible):
			self.visible = True
		else:
			if (self.thing.IsIconized()):
				self.thing.Iconize(False)
			else:
				self.thing.Raise()

	def showWindowCheck(self, notShown = False, onScreen = False):
		"""Checks if a window is currently being shown to the user.

		notShown (bool) - If True: Checks if the window is NOT shown instead
		onScreen (bool) - If True: Checks if the window is visible on the computer monitor (not dragged off to the side)

		Example Input: showWindowCheck()
		"""

		if (onScreen):
			screenSize = self.getScreenSize()
			position = self.thing.GetPosition()

			flag = (position[0] < screenSize[0]) and (position[1] < screenSize[1])
		else:
			flag = self.visible

		if (notShown):
			flag = not flag

		return flag

	def onShowWindow(self, event, *args, **kwargs):
		"""Event function for showWindow()"""

		self.showWindow(*args, **kwargs)
		event.Skip()

	def hideWindow(self):
		"""Hides the window from view, but does not close it.
		Note: This window continues to run and take up memmory. Local variables are still active.

		Example Input: hideWindow()
		"""

		if (self.controller.windowDisabler != None):
			if (self.controller.windowDisabler[0] == self.thing):
				# del self.controller.windowDisabler[1]
				self.controller.windowDisabler = None

		if (self.visible):
			self.thing.Hide()
			self.visible = False
		else:
			warnings.warn(f"Window {self.label} is already hidden", Warning, stacklevel = 2)

	def onHideWindow(self, event, *args, **kwargs):
		"""Event function for hideWindow()"""
		
		self.hideWindow(*args, **kwargs)
		event.Skip()

	def onSwitchWindow(self, event, *args, **kwargs):
		"""Event function for switchWindow()"""
		
		self.switchWindow(*args, **kwargs)
		event.Skip()

	def switchWindow(self, whichTo, hideFrom = True):
		"""Overload for Controller.switchWindow()."""

		self.controller.switchWindow(self, whichTo, hideFrom = hideFrom)

	#Panels
	def addPanel(self, label = None, size = wx.DefaultSize, border = wx.NO_BORDER, position = wx.DefaultPosition, parent = None,
		tabTraversal = True, useDefaultSize = False, autoSize = True, flags = "c1", 

		initFunction = None, initFunctionArgs = None, initFunctionKwargs = None,

		handle = None, hidden = False, enabled = True):
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
			warnings.warn(f"{self.__repr__()} has no sizers", Warning, stacklevel = 2)
			return

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
		warnings.warn(f"{self.__repr__()} has no sizer '{sizerLabel}'", Warning, stacklevel = 2)
		return

	def addSizerGrid(self, rows = 1, columns = 1, text = None, label = None,
		rowGap = 0, colGap = 0, minWidth = -1, minHeight = -1,

		parent = None, hidden = False, enabled = True, handle = None):
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

	def addSizerGridFlex(self, rows = 1, columns = 1, text = None, label = None, 
		rowGap = 0, colGap = 0, minWidth = -1, minHeight = -1, flexGrid = True,

		parent = None, hidden = False, enabled = True, vertical = None, handle = None):
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

	def addSizerGridBag(self, rows = 1, columns = 1, text = None, label = None, 
		rowGap = 0, colGap = 0, minWidth = -1, minHeight = -1, 
		emptySpace = None, flexGrid = True,

		parent = None, hidden = False, enabled = True, vertical = None, handle = None):
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

	def addSizerBox(self, text = None, label = None, minWidth = -1, minHeight = -1,

		parent = None, hidden = False, enabled = True, vertical = True, handle = None):
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

	def addSizerText(self, text = "", label = None, minWidth = -1, minHeight = -1, 

		parent = None, hidden = False, enabled = True, vertical = True, handle = None):
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

	def addSizerWrap(self, text = None, label = None, minWidth = -1, minHeight = -1, 
		extendLast = False,

		parent = None, hidden = False, enabled = True, vertical = True, handle = None):
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
			errorMessage = f"{self.__repr__()} has no menus"
			raise ValueError(errorMessage)

		#Account for whole list request
		if (menuLabel == None):
			return menuList

		#Search for requested menu
		for menu in menuList:
			if (menuLabel == menu.label):
				return menu

		#No menu found
		errorMessage = f"{self.__repr__()} has no menu '{menuLabel}'"
		raise ValueError(errorMessage)

	def addMenuBar(self):
		"""Adds a menu bar to the top of the window.
		Menus with menu items can be added to this.

		Example Input: addMenuBar()
		"""

		self.menuBar = wx.MenuBar()
		self.thing.SetMenuBar(self.menuBar)

	def addMenu(self, text = " ", label = None, detachable = False,

		parent = None, hidden = False, enabled = True, handle = None):
		"""Adds a menu to a pre-existing menubar.
		This is a collapsable array of menu items.

		text (str)        - What the menu is called
			If you add a '&', a keyboard shortcut will be made for the letter after it
		label (str)     - What this is called in the idCatalogue
		detachable (bool) - If True: The menu can be undocked

		Example Input: addMenu("&File", 0)
		Example Input: addMenu("&File", "first")
		"""

		handle = handle_Menu()
		handle.type = "Menu"
		handle.build(locals())
		self.finalNest(handle)

		return handle

	def addPopupMenu(self, label = None, rightClick = True, 

		preFunction = None, preFunctionArgs = None, preFunctionKwargs = None, 
		postFunction = None, postFunctionArgs = None, postFunctionKwargs = None,

		parent = None, hidden = False, enabled = True, handle = None):
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
		Example Input: addPopupMenu(0, preFunction = myFrame.onHideWindow, preFunctionArgs = 0)
		"""

		handle = handle_MenuPopup()
		text = None
		handle.type = "MenuPopup"
		handle.build(locals())
		self.finalNest(handle)
		return handle

	#Status Bars
	def addStatusBar(self):
		"""Adds a status bar to the bottom of the window."""

		self.statusBar = self.thing.CreateStatusBar()
		self.setDefaultStatusText()

	def setStatusText(self, message = None, autoAdd = False):
		"""Sets the text shown in the status bar.

		message (str)  - What the status bar will say
			- If dict: {What to say (str): How long to wait in ms before moving on to the next message (int). Use None for ending}
			- If None: Will use the defaultr status message
		autoAdd (bool) - If there is no status bar, add one

		Example Input: setStatusText()
		Example Input: setStatusText("Ready")
		Example Input: setStatusText({"Ready": 1000, "Set": 1000, "Go!": None, "This will not appear": 1000)
		"""

		def timerMessage():
			"""The thread function that runs for the timer status message."""
			nonlocal self, message

			for text, delay in message.items():
				if (text == None):
					text = self.statusTextDefault
				self.statusBar.SetStatusText(text)

				if (delay == None):
					break
				time.sleep(delay / 1000)

		#Error Checking
		if (self.statusBar == None):
			if (autoAdd):
				self.addStatusBar()
			else:
				warnings.warn(f"There is no status bar for {self.__repr__()}", Warning, stacklevel = 2)
				return

		if (isinstance(message, dict)):
			self.backgroundRun(timerMessage)
		else:
			if (message == None):
				message = self.statusTextDefault
			self.statusBar.SetStatusText(message)

	def setDefaultStatusText(self, message = " "):
		"""Sets the default status message for the status bar.

		message (str)  - What the status bar will say on default

		Example Input: setDefaultStatusText("Ready")
		"""

		if (message == None):
			message = " "
		self.statusTextDefault = message

	#Dialog Boxes
	def makeDialogMessage(self, text = "", title = "", stayOnTop = False, icon = None, 
		addYes = False, addOk = False, addCancel = False, addHelp = False, default = False):
		"""Pauses the running code and shows a dialog box to get input from the user or display a message.
		_________________________________________________________________________

		Example Use:
			with myFrame.makeDialogMessage(text = "Lorem Ipsum", addOk = True) as myDialog:
				if (myDialog.isOk()):
					print("You selected ok")
		_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

		Example Use:
			myDialog = myFrame.makeDialogMessage(text = "Lorem Ipsum", addOk = True)
			myDialog.show()
			if (myDialog.isOk()):
				print("You selected ok")
		_________________________________________________________________________

		Example Input: makeDialogMessage("Lorem Ipsum")
		Example Input: makeDialogMessage("Lorem Ipsum", addYes = True)
		Example Input: makeDialogMessage("Lorem Ipsum", addOk = True, addCancel = True)
		"""

		handle = handle_Dialog()
		handle.type = "message"
		handle.build(locals())
		return handle

	def makeDialogError(self, *args, **kwargs):
		"""Overload for makeDialogMessage() to look like an error message automatically.
		_________________________________________________________________________

		Example Use:
			with myFrame.makeDialogError(text = traceback.print_exc()):
				pass
		_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

		Example Use:
			myDialog = myFrame.makeDialogError(text = traceback.print_exc())
			myDialog.show()
		_________________________________________________________________________

		Example Input: makeDialogError()
		Example Input: makeDialogError(text = "Lorem Ipsum")
		Example Input: makeDialogError(text = traceback.print_exc())
		"""

		kwargs["icon"] = "error"
		kwargs["addOk"] = True

		handle = self.makeDialogMessage(*args, **kwargs)
		return handle

	def makeDialogScroll(self, text = "", title = ""):
		"""Pauses the running code and shows a dialog box that scrolls.
		_________________________________________________________________________

		Example Use:
			with myFrame.makeDialogScroll(text = "Lorem Ipsum") as myDialog:
				if (myDialog.isOk()):
					print("You selected ok")
		_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

		Example Use:
			myDialog = myFrame.makeDialogScroll(text = "Lorem Ipsum")
			myDialog.show()
			if (myDialog.isOk()):
				print("You selected ok")
		_________________________________________________________________________

		Example Input: makeDialogScroll()
		Example Input: makeDialogScroll(text = "Lorem Ipsum")
		"""

		handle = handle_Dialog()
		handle.type = "scroll"
		handle.build(locals())
		return handle

	def makeDialogBusy(self, text = ""):
		"""Does not pause the running code, but instead ignores user inputs by 
		locking the GUI until the code tells the dialog box to go away. 
		This is done by eitehr exiting a while loop or using the hide() function. 

		To protect the GUI better, implement: https://wxpython.org/Phoenix/docs/html/wx.WindowDisabler.html
		_________________________________________________________________________

		Example Use:
			with myFrame.makeDialog(text = "Hold on...") as myDialog:
				for i in range(100):
					time.sleep(1)
		_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

		Example Use:
			myDialog = myFrame.makeDialog(text = "Hold on...")
			myDialog.show()
			for i in range(100):
				time.sleep(1)
			myDialog.hide()
		_________________________________________________________________________

		Example Input: makeDialogBusy()
		Example Input: makeDialogBusy(text = "Calculating...")
		"""

		handle = handle_Dialog()
		handle.type = "busy"
		handle.build(locals())
		return handle

	def makeDialogColor(self, simple = True):
		"""Pauses the running code and shows a dialog box to get input from the user about color.

		simple (bool) - Determines the amount of complexity the color picker window will have.
			- If True: Only shows a few color choices
			- If False: Shows color choices and a color picker field
			- If None: Shows as much detail as possible for selecting color
		_________________________________________________________________________

		Example Use:
			with myFrame.makeDialogColor() as myDialog:
				color = myDialog.getValue()
		_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

		Example Use:
			myDialog = myFrame.makeDialogColor()
			myDialog.show()
			color = myDialog.getValue()
		_________________________________________________________________________

		Example Input: makeDialogColor()
		Example Input: makeDialogColor(simple = False)
		Example Input: makeDialogColor(simple = None)
		"""

		handle = handle_Dialog()
		handle.type = "color"
		handle.build(locals())
		return handle

	def makeDialogChoice(self, choices = [], text = "", title = "", single = True, default = None):
		"""Pauses the running code and shows a dialog box that scrolls.

		choices (list) - What can be chosen from
		default (int) - The index of what to select by default
			- If None: Will not set the default
			- If 'single' is False: Provide a list of what indexes to set by default
		_________________________________________________________________________

		Example Use:
			with myFrame.makeDialogChoice(["Lorem", "Ipsum"]) as myDialog:
				choices = myDialog.getValue()
		_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

		Example Use:
			myDialog = myFrame.makeDialogChoice(["Lorem", "Ipsum"])
			choices = myDialog.getValue()
		_________________________________________________________________________

		Example Input: makeDialogChoice()
		Example Input: makeDialogChoice(["Lorem", "Ipsum"])
		Example Input: makeDialogChoice(["Lorem", "Ipsum"], default = 1)
		Example Input: makeDialogChoice(["Lorem", "Ipsum"], single = False, default = [0, 1])
		"""

		handle = handle_Dialog()
		handle.type = "choice"
		handle.build(locals())
		return handle

	def addAui(self, label = None, flags = None, flex = 0, 

		reduceFlicker = True, 

		initFunction = None, initFunctionArgs = None, initFunctionKwargs = None,
		postPageChangeFunction = None, postPageChangeFunctionArgs = None, postPageChangeFunctionKwargs = None,
		prePageChangeFunction = None, prePageChangeFunctionArgs = None, prePageChangeFunctionKwargs = None,

		handle = None, parent = None):
		"""Creates a container for dockable panels.

		label (str)        - What this is called in the idCatalogue
		flags (list)       - A list of strings for which flag to add to the sizer

		tabSide (str)     - Determines which side of the panel the tabs apear on. Only the first letter is needed
			- "top": Tabs will be placed on the top (north) side of the panel
			- "bottom": Tabs will be placed on the bottom (south) side of the panel
			- "left": Tabs will be placed on the left (west) side of the panel
			- "right": Tabs will be placed on the right (east) side of the panel
		fixedWidth (bool) - Determines how tab width is determined (windows only)
			- If True: All tabs will be the same width
			- If False: Tab width will be 

		initFunction (str)       - The function that is ran when the panel first appears
		initFunctionArgs (any)   - The arguments for 'initFunction'
		initFunctionKwargs (any) - The keyword arguments for 'initFunction'function

		Example Input: addAui()
		Example Input: addAui("myAui")
		Example Input: addAui(padding = (5, 5))
		Example Input: addAui(padding = (5, None))
		"""

		if (isinstance(self, handle_Window)):
			window = self
		else:
			self.myWindow

		handle = handle_AuiManager(self, window)
		handle.build(locals())

		#Nest handle
		self.finalNest(handle)

		return handle

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
			errorMessage = f"Window {self.label} is already closed."
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
		#   self.addMenuBar()
		#   if (not skipMenuExit):
		#       self.addMenu(0, "&File")
		#       self.addItem(0, "&Exit", myFunction = "self.onExit", icon = "quit", internal = True, toolTip = "Closes this program", label = f"Frame{self.windowLabel}_typicalWindowSetup_fileExit")

		# #Add Status Bar
		# if (not skipStatus):
		#   self.addStatusBar()
		#   self.setStatusText("Ready")

		# #Add Popup Menu
		# if (not skipPopup):
		#   self.createPopupMenu("-1")
		#   self.addPopupMenuItem("-1", "&Minimize", "self.onMinimize")
		#   self.addPopupMenuItem("-1", "Maximize", "self.onMaximize")
		#   self.addPopupMenuItem("-1", "Close", "self.onExit")

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
			sizer = self.getSizer(returnAny = True)

			if (sizer == None):
				#Empty Window
				return

			if (self.mainPanel != None):
				if (autoSize):
					self.mainPanel.thing.SetSizerAndFit(sizer.thing)
				else:
					self.mainPanel.thing.SetSizer(sizer.thing)

			else:
				if (autoSize):
					self.thing.SetSizerAndFit(sizer.thing)
				else:
					self.thing.SetSizer(sizer.thing)

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

	def setRefresh(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		"""Sets the functions to call for refresh()."""

		self.refreshFunction = myFunction
		self.refreshFunctionArgs = myFunctionArgs
		self.refreshFunctionKwargs = myFunctionKwargs

	def refresh(self):
		"""Runs the user defined refresh function.
		This function is intended to make sure all widget values are up to date.

		Example Input: refresh()
		"""

		if (self.refreshFunction == None):
			warnings.warn(f"The refresh function for {self.__repr__()} has not been set yet\nUse setRefresh() during window creation first to set the refresh function", Warning, stacklevel = 2)
			return

		self.runMyFunction(self.refreshFunction, self.refreshFunctionArgs, self.refreshFunctionKwargs)

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

	def addFinalFunction(self, myFunction, myFunctionArgs = None, myFunctionKwargs = None):
		"""Adds a function to the queue that will run after building, but before launching, the app."""

		self.finalFunctionList.append([myFunction, myFunctionArgs, myFunctionKwargs])

	def addKeyPress(self, key, myFunction, myFunctionArgs = None, myFunctionKwargs = None, 
		keyUp = True, numpad = False, ctrl = False, alt = False, shift = False):
		"""Adds a single key press event to the frame.

		key (str)              - The keyboard key to bind the function(s) to
		myFunction (str)   - The function that will be ran when the event occurs
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
			self.keyPressQueue[thing] = {key: [myFunction, myFunctionArgs, myFunctionKwargs]}
		else:
			if (key not in self.keyPressQueue[thing]):
				self.keyPressQueue[thing][key] = [myFunction, myFunctionArgs, myFunctionKwargs]
			else:
				self.keyPressQueue[thing][key].append([myFunction, myFunctionArgs, myFunctionKwargs])

	#Overloads
	def addItem(self, menuLabel, *args, **kwargs):
		"""Overload for addItem in handle_Menu()."""

		myMenu = self.getMenu(menuLabel)
		myMenu.addItem(*args, **kwargs)

	def addSeparator(self, menuLabel, *args, **kwargs):
		"""Overload for addSeparator in handle_Menu()."""

		myMenu = self.getMenu(menuLabel)
		myMenu.addSeparator(*args, **kwargs)

	def addSub(self, menuLabel, *args, **kwargs):
		"""Overload for addSub in handle_Menu()."""

		myMenu = self.getMenu(menuLabel)
		myMenu.addSub(*args, **kwargs)

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

	def addInputSlider(self, sizerLabel, *args, **kwargs):
		"""Overload for addInputSlider in handle_Sizer()."""

		mySizer = self.getSizer(sizerLabel)
		handle = mySizer.addInputSlider(*args, **kwargs)

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

	def addButtonCheckList(self, sizerLabel, *args, **kwargs):
		"""Overload for addButtonCheckList in handle_Sizer()."""

		mySizer = self.getSizer(sizerLabel)
		handle = mySizer.addButtonCheckList(*args, **kwargs)

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

	def getTableCurrentCellReadOnly(self, tableLabel, *args, **kwargs):
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

	def setFunction_click(self, widgetLabel, *args, **kwargs):
		"""Overload for setFunction_click in handle_Widget_Base()."""

		myWidget = self.getWidget(widgetLabel)
		myWidget.setFunction_click(*args, **kwargs)

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
			errorMessage = f"The object {self.parent.__repr__()} must be fully created for {self.__repr__()}"
			raise RuntimeError(errorMessage)

		#Add first panel
		if (isinstance(buildSelf, handle_Window)):
			panelList = buildSelf.getNested(include = handle_Panel)
			if (len(panelList) <= 1):
				#The first panel added to a window is automatically nested
				buildSelf.finalNest(self)

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
				errorMessage = f"border {border} does not exist"
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
		self.thing = wx.Panel(self.parent.thing, style = eval(f"{border}|{flags}"))

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
			warnings.warn(f"Add {handle.__class__} to nest() for {self.__repr__()}", Warning, stacklevel = 2)
			return

		self.finalNest(handle)

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

	def build(self, argument_catalogue):
		"""Determiens which build system to use for this handle."""

		def build_double():
			"""Builds a wx  object."""
			nonlocal self, argument_catalogue

			vertical, minimumSize, dividerPosition, buildSelf = self.getArguments(argument_catalogue, ["vertical", "minimumSize", "dividerPosition", "self"])
			dividerGravity, dividerSize, initFunction = self.getArguments(argument_catalogue, ["dividerGravity", "dividerSize", "initFunction"])

			#Create the panel splitter
			self.thing = wx.SplitterWindow(self.parent.thing, style = wx.SP_LIVE_UPDATE)
			self.myWindow = buildSelf.myWindow

			#Add panels and sizers to splitter
			for i in range(2):
				#Compile instructions
				if (f"panel_{i}" in argument_catalogue):
					panelInstructions = argument_catalogue[(f"panel_{i}")]
				else:
					panelInstructions = {}

				if (f"sizer_{i}" in argument_catalogue):
					sizerInstructions = argument_catalogue[(f"sizer_{i}")]
				else:
					sizerInstructions = {}

				panelInstructions["parent"] = self
				panel = self.readBuildInstructions_panel(buildSelf, i, panelInstructions)
				self.panelList.append(panel)
				self.finalNest(self.panelList[i])

				sizerInstructions["parent"] = self.panelList[i]
				sizer = self.readBuildInstructions_sizer(buildSelf, i, sizerInstructions)
				self.sizerList.append(sizer)
				self.panelList[i].nest(sizer)

			#Apply Properties
			##Direction
			if (vertical):
				self.thing.SplitVertically(self.panelList[0].thing, self.panelList[1].thing)
			else:
				self.thing.SplitHorizontally(self.panelList[0].thing, self.panelList[1].thing)

			##Minimum panel size
			self.thing.SetMinimumPaneSize(minimumSize)

			##Divider position from the right
			if (dividerPosition != None):
				self.thing.SetSashPosition(dividerPosition)

			##Left panel growth ratio
			self.thing.SetSashGravity(dividerGravity)

			##Dividing line size
			self.thing.SetSashSize(dividerSize)

			#Bind Functions
			if (initFunction != None):
				initFunctionArgs, initFunctionKwargs = self.getArguments(argument_catalogue, ["initFunctionArgs", "initFunctionKwargs"])
				self.setFunction_init(initFunction, initFunctionArgs, initFunctionKwargs)

		def build_quad():
			"""Builds a wx  object."""
			nonlocal self, argument_catalogue

			buildSelf = self.getArguments(argument_catalogue, "self")
			self.myWindow = buildSelf.myWindow

			#Add panels and sizers to splitter
			for i in range(4):
				#Add panels to the splitter
				self.panelList.append(self.myWindow.addPanel(parent = self, border = "raised"))
				self.thing.AppendWindow(self.panelList[i].thing)
				self.finalNest(self.panelList[i])

				#Add sizers to the panel
				if (f"sizer_{i}" in argument_catalogue):
					sizerInstructions = argument_catalogue[(f"sizer_{i}")]
				else:
					sizerInstructions = {}
				sizer = self.readBuildInstructions(buildSelf, i, sizerInstructions)

				self.sizerList.append(sizer)
				self.panelList[i].nest(sizer)

			#Create the panel splitter
			self.thing = wx.lib.agw.fourwaysplitter.FourWaySplitter(self.parent.thing, agwStyle = wx.SP_LIVE_UPDATE)

			#Bind Functions
			if (initFunction != None):
				initFunctionArgs, initFunctionKwargs = self.getArguments(argument_catalogue, ["initFunctionArgs", "initFunctionKwargs"])
				self.setFunction_init(initFunction, initFunctionArgs, initFunctionKwargs)

		def build_poly():
			"""Builds a wx  object."""
			nonlocal self, argument_catalogue

			minimumSize, vertical, buildSelf = self.getArguments(argument_catalogue, ["minimumSize", "vertical", "self"])
			self.myWindow = buildSelf.myWindow

			#Add panels and sizers to splitter
			for i in range(panelNumbers):
				#Add panels to the splitter
				self.panelList.append(self.myWindow.addPanel(parent = self, border = "raised"))
				self.thing.AppendWindow(self.panelList[i].thing)
				self.finalNest(self.panelList[i])

				#Add sizers to the panel
				if (i in sizers):
					sizerInstructions = sizers[i]
				else:
					sizerInstructions = {}
				sizer = self.readBuildInstructions(buildSelf, i, sizerInstructions)

				self.sizerList.append(sizer)
				self.panelList[i].nest(sizer)

			#Create the panel splitter
			self.thing = wx.lib.splitter.MultiSplitterWindow(self.parent.thing, style = wx.SP_LIVE_UPDATE)

			#Apply Properties
			##Minimum panel size
			self.thing.SetMinimumPaneSize(minimumSize)

			##Stack Direction
			if (vertical):
				self.thing.SetOrientation(wx.VERTICAL)
			else:
				self.thing.SetOrientation(wx.HORIZONTAL)

			#Bind Functions
			if (initFunction != None):
				initFunctionArgs, initFunctionKwargs = self.getArguments(argument_catalogue, ["initFunctionArgs", "initFunctionKwargs"])
				self.setFunction_init(initFunction, initFunctionArgs, initFunctionKwargs)

			
		#########################################################

		self.preBuild(argument_catalogue)

		if (self.type.lower() == "double"):
			build_double()
		elif (self.type.lower() == "quad"):
			build_quad()
		elif (self.type.lower() == "poly"):
			build_poly()
		else:
			warnings.warn(f"Add {self.type} to build() for {self.__repr__()}", Warning, stacklevel = 2)

		self.postBuild(argument_catalogue)

	def setFunction_init(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		"""Changes the function that runs when the object is first created."""

		if (self.type.lower() == "double"):
			self.parent.betterBind(wx.EVT_INIT_DIALOG, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		elif (self.type.lower() == "quad"):
			self.parent.betterBind(wx.EVT_INIT_DIALOG, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		elif (self.type.lower() == "poly"):
			self.parent.betterBind(wx.EVT_INIT_DIALOG, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		else:
			warnings.warn(f"Add {self.type} to setFunction_init() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_preMoveSash(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		"""Changes the function that runs when the object is first created."""

		if (self.type.lower() == "double"):
			self.parent.betterBind(wx.EVT_SPLITTER_SASH_POS_CHANGING, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		else:
			warnings.warn(f"Add {self.type} to setFunction_preMoveSash() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_postMoveSash(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		"""Changes the function that runs when the object is first created."""

		if (self.type.lower() == "double"):
			self.parent.betterBind(wx.EVT_SPLITTER_SASH_POS_CHANGED, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		else:
			warnings.warn(f"Add {self.type} to setFunction_preMoveSash() for {self.__repr__()}", Warning, stacklevel = 2)

	def getSizers(self):
		"""Returns the internal sizer list."""

		return self.sizerList

	def getSashPosition(self):
		"""Returns the current sash position."""
		
		if (self.type.lower() == "double"):
			value = self.thing.GetSashPosition()
		else:
			warnings.warn(f"Add {self.type} to getSashPosition() for {self.__repr__()}", Warning, stacklevel = 2)
			value = None

		return value

	def setSashPosition(self, newValue):
		"""Changes the position of the sash marker."""
		
		if (self.type.lower() == "double"):
			if (isinstance(newValue, str)):
				newValue = ast.literal_eval(newValue)

			if (newValue != None):
				self.thing.SetSashPosition(newValue)
		else:
			warnings.warn(f"Add {self.type} to setSashPosition() for {self.__repr__()}", Warning, stacklevel = 2)

	# def readBuildInstructions_sizer(self, parent, i, instructions):
	#   """Interprets instructions given by the user for what sizer to make and how to make it."""

	#   if (not isinstance(instructions, dict)):
	#       errorMessage = f"sizer_{i} must be a dictionary for {self.__repr__()}"
	#       raise ValueError(errorMessage)

	#   if (len(instructions) == 1):
	#       instructions["type"] = "Box"
	#   else:
	#       if ("type" not in instructions):
	#           errorMessage = "Must supply which sizer type to make. The key should be 'type'. The value should be 'Grid', 'Flex', 'Bag', 'Box', 'Text', or 'Wrap'"
	#           raise ValueError(errorMessage)

	#   sizerType = instructions["type"].lower()
	#   if (sizerType not in ["grid", "flex", "bag", "box", "text", "wrap"]):
	#       errorMessage = f"There is no 'type' {instructions['type']}. The value should be be 'Grid', 'Flex', 'Bag', 'Box', 'Text', or 'Wrap'"
	#       raise KeyError(errorMessage)

	#   #Get Default build arguments
	#   if (sizerType == "grid"):
	#       sizerFunction = handle_Window.addSizerGrid
	#   elif (sizerType == "flex"):
	#       sizerFunction = handle_Window.addSizerGridFlex
	#   elif (sizerType == "bag"):
	#       sizerFunction = handle_Window.addSizerGridBag
	#   elif (sizerType == "box"):
	#       sizerFunction = handle_Window.addSizerBox
	#   elif (sizerType == "text"):
	#       sizerFunction = handle_Window.addSizerText
	#   else:
	#       sizerFunction = handle_Window.addSizerWrap
	#   kwargs = {item.name: item.default for item in inspect.signature(sizerFunction).parameters.values()}

	#   #Create Handler
	#   sizer = handle_Sizer()
	#   sizer.type = instructions["type"]
	#   del instructions["type"]

	#   #Overwrite default with user given data
	#   for key, value in instructions.items():
	#       kwargs[key] = value

	#   #Finish building sizer
	#   kwargs["self"] = parent
	#   sizer.build(kwargs)

	#   return sizer

	# def readBuildInstructions_panel(self, parent, i, instructions):
	#   """Interprets instructions given by the user for what panel to make and how to make it."""

	#   if (not isinstance(instructions, dict)):
	#       errorMessage = f"panel_{i} must be a dictionary for {self.__repr__()}"
	#       raise ValueError(errorMessage)

	#   #Overwrite default with user given data
	#   kwargs = {item.name: item.default for item in inspect.signature(handle_Window.addPanel).parameters.values()}
	#   for key, value in instructions.items():
	#       kwargs[key] = value

	#   #Create Handler
	#   panel = handle_Panel()

	#   #Finish building panel
	#   kwargs["self"] = parent
	#   panel.build(kwargs)

	#   return panel

class handle_AuiManager(handle_Container_Base):
	"""The manager for dockable windows.
	Modified code from: https://www.blog.pythonlibrary.org/2009/12/09/the-%E2%80%9Cbook%E2%80%9D-controls-of-wxpython-part-2-of-2/
	"""

	def __init__(self, parent, myWindow):
		"""Initialize Defaults"""

		#Initialize inherited classes
		handle_Container_Base.__init__(self)

		#Internal Variables
		self.parent = parent
		self.myWindow = myWindow
		self.mySizer = None

	def build(self, argument_catalogue):
		"""Builds a wx AuiManager object"""

		reduceFlicker = self.getArguments(argument_catalogue, ["reduceFlicker"])

		#Expand using: https://wxpython.org/Phoenix/docs/html/wx.aui.AuiManager.html

		style = "wx.lib.agw.aui.AUI_MGR_DEFAULT" #See: https://wxpython.org/Phoenix/docs/html/wx.aui.AuiManagerOption.enumeration.html#wx-aui-auimanageroption

		if (reduceFlicker):
			style += "|wx.lib.agw.aui.AUI_MGR_LIVE_RESIZE"

		self.thing = wx.lib.agw.aui.AuiManager(self.myWindow.thing, eval(style))
		self.thing.SetManagedWindow(self.myWindow.thing)

		# self.mySizer = self.readBuildInstructions_sizer(self.myWindow, 0, {})
		# self.parent.nest(self.mySizer)

	def addPane(self, text = "", default = "top", 
		label = None, panel = {}, sizer = {}, handle = None, 
		dockTop = True, dockBottom = True, dockLeft = True, dockRight = True,
		showTitle = True, showBorder = False, showGripper = True,
		addCloseButton = False, addMaximizeButton = False, addMinimizeButton = False,
		floatable = False, resizable = True, movable = True,
		minimumSize = None, maximumSize = None, bestSize = None, fixedSize = False):
		"""Adds a wx object to the aui manager."""

		paneInfo = wx.lib.agw.aui.AuiPaneInfo()

		#Default Position
		if (default != None):
			if (default[0].lower() == "c"):
				paneInfo.CenterPane()
			elif (default[0].lower() == "t"):
				paneInfo.Top()
			elif (default[0].lower() == "b"):
				paneInfo.Bottom()
			elif (default[0].lower() == "l"):
				paneInfo.Left()
			else:
				paneInfo.Right()
		else:
			paneInfo.Top()

		#Appearance
		paneInfo.Caption(text)
		paneInfo.PaneBorder(showBorder)
		paneInfo.CaptionVisible(showTitle)
		paneInfo.Gripper(showGripper)

		#Dockability
		paneInfo.TopDockable(dockTop)
		paneInfo.BottomDockable(dockBottom)
		paneInfo.LeftDockable(dockLeft)
		paneInfo.RightDockable(dockRight)

		#Attributes
		paneInfo.CloseButton(addCloseButton)
		paneInfo.MinimizeButton(addMinimizeButton)
		paneInfo.MaximizeButton(addMaximizeButton)
		paneInfo.Resizable(resizable)
		paneInfo.Movable(movable)

		if (minimumSize != None):
			paneInfo.MinSize(minimumSize)
		if (maximumSize != None):
			paneInfo.MaxSize(maximumSize)
		if (bestSize != None):
			paneInfo.BestSize(bestSize)

		if (fixedSize):
			paneInfo.Fixed()

		if (floatable):
			paneInfo.Float()
			paneInfo.PinButton(True)

		if (label != None):
			paneInfo.Name(str(label))

		#Account for overriding the handle with your own widget or panel
		if (handle == None):
			#Get the object
			handle = handle_NotebookPage()
			handle.type = "auiPage"
			kwargs = locals()

			kwargs["parent"] = self.myWindow
			kwargs["myManager"] = self

			handle.preBuild(kwargs)
			handle.build(kwargs)
			handle.postBuild(kwargs)

		#Add Pane
		self.thing.AddPane(handle.myPanel.thing, paneInfo) 
		self.thing.Update()

		#Record nesting
		self.finalNest(handle)

		return handle

	def nest(self, handle, *args, **kwargs):
		print(f"@1 nesting {type(handle)} in {self.__repr__()}")

		self.finalNest(handle)

	def setFunction_click(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		"""Changes the function that runs when the object is activated."""

		self.parent.betterBind(wx.EVT_AUI_PANE_ACTIVATED, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)

	def setFunction_tabClick(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		"""Changes the function that runs when the object is activated."""

		self.parent.betterBind(wx.EVT_AUI_PANE_BUTTON, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)

	def setFunction_maximize(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		"""Changes the function that runs when the object is activated."""

		self.parent.betterBind(wx.EVT_AUI_PANE_MAXIMIZE, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)

	def setFunction_minimize(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		"""Changes the function that runs when the object is activated."""

		self.parent.betterBind(wx.EVT_AUI_PANE_MINIMIZE, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)

	def setFunction_restore(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		"""Changes the function that runs when the object is activated."""

		self.parent.betterBind(wx.EVT_AUI_PANE_RESTORE, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)

	#Getters
	def getSetup(self):
		"""Returns a string that describes the current setup for the window panes.

		Example Imput: getSetup()
		"""

		return self.thing.SavePerspective()

	def getPaneInfo(self, label):
		"""Returns the pane info object for the reqested pane object.
		Note: Objects must have been given a label upon creation to be retrieved.

		label (str) - What the object was called upon creation

		Example Input: getPaneInfo("settings")
		"""

		return self.thing.GetPane(label)

	#Setters
	def setSetup(self, config, renderChanges = True):
		"""Uses a string that describes the current setup for the window panes
		to configure the positions, etc. of the panes.

		Example Imput: setSetup(config)
		"""

		self.thing.LoadPerspective(config, update = renderChanges)

	def setDockConstraint(self, width = 0.25, height = 0.25):
		"""Changes the size of the available space to drop a pane that is being dragged.

		width (float)  - Percentage of available width to use
		height (float) - Percentage of available height to use

		Example Input: setDockConstraint()
		Example Input: setDockConstraint(height = 1)
		Example Input: setDockConstraint(0.75, 0.75)
		"""

		self.thing.SetDockSizeConstraint(width, height)

	def setTitle(self, label, text = ""):
		"""Changes the title of the requested pane.

		Example Input: setTitle()
		"""

		paneInfo = self.getPaneInfo(label)
		paneInfo.Caption(text)
		self.thing.Update()

	#Change Attributes
	def dockCenter(self, label):
		"""Docks the page on the center area.

		Example Input: dockCenter()
		"""

		paneInfo = self.getPaneInfo(label)
		paneInfo.CenterPane()
		self.thing.Update()

	def dockTop(self, label):
		"""Docks the page on the top area.

		Example Input: dockTop()
		"""

		paneInfo = self.getPaneInfo(label)
		paneInfo.Top()
		self.thing.Update()

	def dockBottom(self, label):
		"""Docks the page on the bottom area.

		Example Input: dockBottom()
		"""

		paneInfo = self.getPaneInfo(label)
		paneInfo.Bottom()
		self.thing.Update()

	def dockLeft(self, label):
		"""Docks the page on the left area.

		Example Input: dockLeft()
		"""

		paneInfo = self.getPaneInfo(label)
		paneInfo.Left()
		self.thing.Update()

	def dockRight(self, label):
		"""Docks the page on the right area.

		Example Input: dockRight()
		"""

		paneInfo = self.getPaneInfo(label)
		paneInfo.Right()
		self.thing.Update()

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

	def build(self, argument_catalogue):
		"""Determiens which build system to use for this handle."""

		def build_notebook():
			"""Builds a wx notebook object."""
			nonlocal self, argument_catalogue

			flags, tabSide, reduceFlicker, fixedWidth, padding, buildSelf = self.getArguments(argument_catalogue, ["flags", "tabSide", "reduceFlicker", "fixedWidth", "padding", "self"])
			initFunction, postPageChangeFunction, prePageChangeFunction, multiLine = self.getArguments(argument_catalogue, ["initFunction", "postPageChangeFunction", "prePageChangeFunction", "multiLine"])

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
			if (multiLine):
				flags += "|wx.NB_MULTILINE"

			#Create notebook object
			self.thing = wx.Notebook(self.parent.thing, style = eval(flags))

			#Bind Functions
			if (initFunction != None):
				initFunctionArgs, initFunctionKwargs = self.getArguments(argument_catalogue, ["initFunctionArgs", "initFunctionKwargs"])
				self.setFunction_init(initFunction, initFunctionArgs, initFunctionKwargs)
			
			if (prePageChangeFunction != None):
				prePageChangeFunctionArgs, prePageChangeFunctionKwargs = self.getArguments(argument_catalogue, ["prePageChangeFunctionArgs", "prePageChangeFunctionKwargs"])
				self.setFunction_prePageChange(initFunction, initFunctionArgs, initFunctionKwargs)

			if (postPageChangeFunction != None):
				postPageChangeFunctionArgs, postPageChangeFunctionKwargs = self.getArguments(argument_catalogue, ["postPageChangeFunctionArgs", "postPageChangeFunctionKwargs"])
				self.setFunction_postPageChange(initFunction, initFunctionArgs, initFunctionKwargs)

			#Determine if there is padding on the tabs
			if ((padding != None) and (padding != -1)):
				#Ensure correct format
				if ((padding[0] != None) and (padding[0] != -1)):
					width = padding[0]
				else:
					width = 0

				if ((padding[1] != None) and (padding[1] != -1)):
					height = padding[1]
				else:
					height = 0

				#Apply padding
				size = wx.Size(width, height)
				self.thing.SetPadding(size)

			#Set values
			if (isinstance(self, handle_Window)):
				self.myWindow = buildSelf
			else:
				self.myWindow = buildSelf.myWindow

		def build_auiNotebook():
			"""Builds a wx auiNotebook object."""
			nonlocal self, argument_catalogue

			flags, buildSelf = self.getArguments(argument_catalogue, ["flags", "self"])
			initFunction, postPageChangeFunction, prePageChangeFunction = self.getArguments(argument_catalogue, ["initFunction", "postPageChangeFunction", "prePageChangeFunction"])

			tabSide, tabSplit, tabMove, tabBump = self.getArguments(argument_catalogue, ["tabSide", "tabSplit", "tabMove", "tabBump"])
			tabSmart, tabOrderAccess, tabFloat = self.getArguments(argument_catalogue, ["tabSmart", "tabOrderAccess", "tabFloat"])
			addScrollButton, addListDrop, addCloseButton = self.getArguments(argument_catalogue, ["addScrollButton", "addListDrop", "addCloseButton"])
			closeOnLeft, middleClickClose = self.getArguments(argument_catalogue, ["closeOnLeft", "middleClickClose"])
			fixedWidth, drawFocus = self.getArguments(argument_catalogue, ["fixedWidth", "drawFocus"])

			#Create Styles
			if (tabSide != None):
				if (tabSide[0] == "t"):
					styles = "wx.lib.agw.aui.AUI_NB_TOP"
				elif (tabSide[0] == "b"):
					styles = "wx.lib.agw.aui.AUI_NB_BOTTOM"
				elif (tabSide[0] == "l"):
					styles = "wx.lib.agw.aui.AUI_NB_LEFT"
				else:
					styles = "wx.lib.agw.aui.AUI_NB_RIGHT"
			else:
				styles = "wx.lib.agw.aui.AUI_NB_TOP"

			if (tabSplit):
				styles += "|wx.lib.agw.aui.AUI_NB_TAB_SPLIT"

			if (tabMove):
				styles += "|wx.lib.agw.aui.AUI_NB_TAB_MOVE"

			if (tabBump):
				styles += "|wx.lib.agw.aui.AUI_NB_TAB_EXTERNAL_MOVE"

			if (tabSmart):
				# styles += "|wx.lib.agw.aui.AUI_NB_HIDE_ON_SINGLE_TAB"
				styles += "|wx.lib.agw.aui.AUI_NB_SMART_TABS"
				styles += "|wx.lib.agw.aui.AUI_NB_DRAW_DND_TAB"

			if (tabOrderAccess):
				styles += "|wx.lib.agw.aui.AUI_NB_ORDER_BY_ACCESS"

			if (tabFloat):
				styles += "|wx.lib.agw.aui.AUI_NB_TAB_FLOAT"

			if (fixedWidth):
				styles += "|wx.lib.agw.aui.AUI_NB_TAB_FIXED_WIDTH"

			if (addScrollButton):
				styles += "|wx.lib.agw.aui.AUI_NB_SCROLL_BUTTONS"

			if (addListDrop != None):
				if (addListDrop):
					styles += "|wx.lib.agw.aui.AUI_NB_WINDOWLIST_BUTTON"
				else:
					styles += "|wx.lib.agw.aui.AUI_NB_USE_IMAGES_DROPDOWN"

			if (addCloseButton != None):
				if (addCloseButton):
					styles += "|wx.lib.agw.aui.AUI_NB_CLOSE_ON_ALL_TABS"
				else:
					styles += "|wx.lib.agw.aui.AUI_NB_CLOSE_ON_ACTIVE_TAB"

				if (closeOnLeft):
					styles += "|wx.lib.agw.aui.AUI_NB_CLOSE_ON_TAB_LEFT"

			if (middleClickClose):
				styles += "|wx.lib.agw.aui.AUI_NB_MIDDLE_CLICK_CLOSE"

			if (not drawFocus):
				styles += "|wx.lib.agw.aui.AUI_NB_NO_TAB_FOCUS"

			self.thing = wx.lib.agw.aui.auibook.AuiNotebook(self.parent.thing, agwStyle = eval(styles))

			#Set values
			if (isinstance(self, handle_Window)):
				self.myWindow = buildSelf
			else:
				self.myWindow = buildSelf.myWindow

			#Link to window's aui manager
			if (self.myWindow.auiManager == None):
				self.myWindow.auiManager = handle_AuiManager(self, self.myWindow)#, reduceFlicker = reduceFlicker)
				self.build(locals())

			self.myWindow.auiManager.addPane(self)
		
		#########################################################

		self.preBuild(argument_catalogue)

		if (self.type.lower() == "notebook"):
			build_notebook()
		elif (self.type.lower() == "auinotebook"):
			build_auiNotebook()
		else:
			warnings.warn(f"Add {self.type} to build() for {self.__repr__()}", Warning, stacklevel = 2)

		self.postBuild(argument_catalogue)

	def setSelection(self, newValue, event = None):
		"""Sets the contextual value for the object associated with this handle to what the user supplies."""

		if (self.type.lower() == "notebook"):
			self.changePage(newValue)
		else:
			warnings.warn(f"Add {self.type} to setSelection() for {self.__repr__()}", Warning, stacklevel = 2)

	def getValue(self, event = None):
		"""Gets the contextual value for the object associated with this handle to what the user supplies."""

		if (self.type.lower() == "notebook"):
			index = self.getCurrentPage(index = True)
			return self.getPageText(index)
		else:
			warnings.warn(f"Add {self.type} to setSelection() for {self.__repr__()}", Warning, stacklevel = 2)

	#Change Settings
	def setFunction_init(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		"""Changes the function that runs when the object is first created."""

		if (self.type.lower() == "notebook"):
			self.parent.betterBind(wx.EVT_INIT_DIALOG, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		else:
			warnings.warn(f"Add {self.type} to setFunction_init() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_prePageChange(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		"""Changes the function that runs when the page begins to change."""

		if (self.type.lower() == "notebook"):
			self.parent.betterBind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		else:
			warnings.warn(f"Add {self.type} to setFunction_prePageChange() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_postPageChange(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		"""Changes the function that runs when the page has finished changing."""

		if (self.type.lower() == "notebook"):
			self.parent.betterBind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		else:
			warnings.warn(f"Add {self.type} to setFunction_postPageChange() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_rightClick(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type.lower() == "notebook"):
			self.betterBind(wx.EVT_RIGHT_DOWN, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
			for handle in self[:]:
				handle.setFunction_rightClick(myFunction = myFunction, myFunctionArgs = myFunctionArgs, myFunctionKwargs = myFunctionKwargs)
		else:
			warnings.warn(f"Add {self.type} to setFunction_rightClick() for {self.__repr__()}", Warning, stacklevel = 2)

	def addPage(self, text = None, panel = {}, sizer = {},
		insert = None, default = False, icon_path = None, icon_internal = False,

		label = None, hidden = False, enabled = True, parent = None):
		"""Adds a gage to the notebook.
		Lists can be given to add multiple pages. They are added in order from left to right.
		If only a 'pageLabel' is a list, they will all have the same 'text'.
		If 'pageLabel' and 'text' are a list of different lengths, it will not add any of them.

		text (str)  - What the page's tab will say
			- If None: The tab will be blank
		label (str) - What this is called in the idCatalogue
		
		insert (int)   - Determines where the new page will be added
			- If None or -1: The page will be added to the end
			- If not None or -1: This is the page index to place this page in 
		default (bool) - Determines if the new page should be automatically selected

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
		if (isinstance(label, (list, tuple, range)) and isinstance(text, (list, tuple, range))):
			if (len(label) != len(text)):
				errorMessage = f"'label' and 'text' must be the same length for {self.__repr__()}"
				raise ValueError(errorMessage)

		#Account for multiple objects
		if (not isinstance(label, (list, tuple, range))):
			labelList = [label]
		else:
			labelList = label

		if (not isinstance(text, (list, tuple, range))):
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
			handle.type = "notebookPage"
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
			self.finalNest(handle)

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
		pageNumber = self.getPageIndex(pageLabel)

		#Change the page
		if (triggerEvent):
			self.thing.SetSelection(pageNumber)
		else:
			self.thing.ChangeSelection(pageNumber)

	def removePage(self, pageLabel):
		"""Removes the given page from the notebook.

		pageLabel (str) - The catalogue label for the panel to add to the notebook

		Example Input: notebookRemovePage(1)
		"""

		#Determine page number
		pageNumber = self.getPageIndex(pageLabel)

		#Remove the page from the notebook
		self.thing.RemovePage(pageNumber)

		#Remove the page from the catalogue
		del self[pageLabel]

	def removeAll(self):
		"""Removes all pages from the notebook.

		Example Input: notebookRemovePage()
		"""

		#Remove all pages from the notebook
		self.thing.DeleteAllPages()

		for item in self:
			del item

	def nextPage(self):
		"""Selects the next page in the notebook.

		Example Input: notebookNextPage()
		"""

		#Change the page
		self.thing.AdvanceSelection()

	def backPage(self):
		"""Selects the previous page in the notebook.

		Example Input: notebookBackPage()
		"""

		#Change the page
		self.thing.AdvanceSelection(False)

	##Getters
	def getCurrentPage(self, index = None):
		"""Returns the currently selected page from the given notebook

		index (bool) - Determines in what form the page is returned.
			- If True: Returns the page's index number
			- If False: Returns the page's catalogue label
			- If None: Returns the handle object for the page

		Example Input: notebookGetCurrentPage()
		Example Input: notebookGetCurrentPage(True)
		"""

		#Determine current page
		currentPage = self.thing.GetSelection()

		if (currentPage == wx.NOT_FOUND):
			return

		#Return the correct type
		if (index):
			return currentPage

		for item in self:
			if (item.index == currentPage):
				if (index == None):
					return item
				else:
					return item.label

		errorMessage = f"Unknown Error in getCurrentPage() for {self.__repr__()}"
		raise ValueError(errorMessage)

	def getPageIndex(self, pageLabel):
		"""Returns the page index for a page with the given label in the given notebook.

		pageLabel (str) - The catalogue label for the panel to add to the notebook

		Example Input: getPageIndex(0)
		"""

		#Determine page number
		for item in self:
			if (item.label == pageLabel):
				return item.index

		errorMessage = f"There is no page labled {pageLabel} in {self.__repr__()}"
		raise KeyError(errorMessage)

	def getPageText(self, pageIndex = None):
		"""Returns the first page index for a page with the given label in the given notebook.

		pageLabel (str) - The catalogue label for the panel to add to the notebook
			- If None: Uses the current page

		Example Input: getPageText()
		Example Input: getPageText(1)
		"""

		#Determine page number
		if (pageIndex == None):
			pageIndex = self.getCurrentPage(index = True)
		elif (not isinstance(pageIndex, int)):
			pageIndex = self.getPageIndex(pageIndex)

		#Get the tab's text
		text = self.thing.GetPageText(pageIndex)

		return text

	def getTabCount(self):
		"""Returns how many tabs the notebook currently has.

		Example Input: notebookGetTabCount()
		"""

		#Determine the number of tabs
		tabCount = self.thing.GetPageCount()

		return tabCount

	def getTabRowCount(self):
		"""Returns how many rows of tabs the notebook currently has.

		Example Input: notebookGetTabRowCount()
		"""

		#Determine the number of tabs
		count = self.thing.GetRowCount()

		return count

	##Setters
	def setPageText(self, pageLabel, text = ""):
		"""Changes the given notebook page's tab text.

		pageLabel (str) - The catalogue label for the panel to add to the notebook
		text (str)      - What the page's tab will now say

		Example Input: notebookSetPageText(0, "Ipsum")
		"""

		#Determine page number
		pageNumber = self.getPageIndex(pageLabel)

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
		self.myManager = None
		self.text = None
		self.icon = None
		self.iconIndex = None
		self.index = None
		self.type = None

	def __str__(self):
		"""Gives diagnostic information on the Notebook when it is printed out."""

		output = handle_Container_Base.__str__(self)

		if (self.index != None):
			output += f"-- index: {self.index}\n"
		if (self.text != None):
			output += f"-- text: {self.text}\n"
		if (self.icon != None):
			output += f"-- icon: {self.icon}\n"

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

		text, panel, sizer = self.getArguments(argument_catalogue, ["text", "panel", "sizer"])

		if (isinstance(self.parent, handle_Window)):
			self.myWindow = self.parent
		else:
			self.myWindow = self.parent.myWindow
		self.index = len(self.parent) - 1

		#Setup Panel
		panel["parent"] = self.parent
		self.myPanel = self.readBuildInstructions_panel(self, 0, panel)

		#Setup Sizer
		sizer["parent"] = self.myPanel
		self.mySizer = self.readBuildInstructions_sizer(self, 0, sizer)

		self.myPanel.nest(self.mySizer)

		self.finalNest(self.myPanel)

		#Format text
		if (text == None):
			self.text = ""
		else:
			if (not isinstance(text, str)):
				self.text = f"{text}"
			else:
				self.text = text

		#Format Icon
		if (self.type.lower() == "notebookpage"):
			icon_path, icon_internal = self.getArguments(argument_catalogue, ["icon_path", "icon_internal"])
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

		if (self.type.lower() == "notebookpage"):
			#Determine page number
			pageNumber = self.getPageIndex(pageLabel)

			#Remove the page from the notebook
			notebook.RemovePage(self.pageNumber)

			#Remove the page from the catalogue
			del notebook.notebookPageDict[pageLabel]
		else:
			warnings.warn(f"Add {self.type} to remove() for {self.__repr__()}", Warning, stacklevel = 2)

	def getIndex(self, event = None):
		"""Returns the page index for a page with the given label in the given notebook.

		Example Input: getIndex()
		"""

		if (self.type.lower() == "notebookpage"):
			#Determine page number
			pageNumber = notebook.notebookPageDict[pageLabel]["index"]
		else:
			warnings.warn(f"Add {self.type} to getIndex() for {self.__repr__()}", Warning, stacklevel = 2)
			pageNumber = None

		return pageNumber

	def getValue(self, event = None):
		"""Returns the first page index for a page with the given label in the given notebook.

		Example Input: getValue()
		"""

		if (self.type.lower() == "notebookpage"):
			text = self.getPageText()
		else:
			warnings.warn(f"Add {self.type} to getValue() for {self.__repr__()}", Warning, stacklevel = 2)
			text = None

		return text

	def getPageText(self):
		"""Returns the page text.

		Example Input: getPageText()
		"""

		return self.text

	def getPageIndex(self):
		"""Returns the page text.

		Example Input: getPageIndex()
		"""

		return self.index

	##Setters
	def setValue(self, newValue = "", event = None):
		"""Changes the given notebook page's tab text.

		newValue (str) - What the page's tab will now say

		Example Input: notebookSetPageText("Ipsum")
		"""

		if (self.type.lower() == "notebookpage"):
			#Determine page number
			pageNumber = self.getPageIndex(pageLabel)

			#Change page text
			notebook.SetPageText(pageNumber, newValue)

		elif (self.type.lower() == "auipage"):
			if (self.label == None):
				warnings.warn(f"A label is needed for {self.__repr__()} to change the caption", Warning, stacklevel = 2)

			self.myManager.setTitle(self.label, newValue)
		else:
			warnings.warn(f"Add {self.type} to setValue() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_rightClick(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type.lower() == "notebookpage"):
			self.betterBind(wx.EVT_RIGHT_DOWN, self.myPanel.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		else:
			warnings.warn(f"Add {self.type} to setFunction_rightClick() for {self.__repr__()}", Warning, stacklevel = 2)

	#Etc
	def dockCenter(self, *args, **kwargs):
		"""Overload for dockCenter() in handle_AuiManager."""

		if (self.type.lower() == "auipage"):
			if (self.label == None):
				warnings.warn(f"A label is needed for {self.__repr__()} to programatically dock it", Warning, stacklevel = 2)

			self.myManager.dockCenter(self.label, *args, **kwargs)

		else:
			warnings.warn(f"Add {self.type} to setValue() for {self.__repr__()}", Warning, stacklevel = 2)

	def dockTop(self, *args, **kwargs):
		"""Overload for dockTop() in handle_AuiManager."""

		if (self.type.lower() == "auipage"):
			if (self.label == None):
				warnings.warn(f"A label is needed for {self.__repr__()} to programatically dock it", Warning, stacklevel = 2)

			self.myManager.dockTop(self.label, *args, **kwargs)

		else:
			warnings.warn(f"Add {self.type} to setValue() for {self.__repr__()}", Warning, stacklevel = 2)

	def dockBottom(self, *args, **kwargs):
		"""Overload for dockBottom() in handle_AuiManager."""

		if (self.type.lower() == "auipage"):
			if (self.label == None):
				warnings.warn(f"A label is needed for {self.__repr__()} to programatically dock it", Warning, stacklevel = 2)

			self.myManager.dockBottom(self.label, *args, **kwargs)

		else:
			warnings.warn(f"Add {self.type} to setValue() for {self.__repr__()}", Warning, stacklevel = 2)

	def dockLeft(self, *args, **kwargs):
		"""Overload for dockLeft() in handle_AuiManager."""

		if (self.type.lower() == "auipage"):
			if (self.label == None):
				warnings.warn(f"A label is needed for {self.__repr__()} to programatically dock it", Warning, stacklevel = 2)

			self.myManager.dockLeft(self.label, *args, **kwargs)

		else:
			warnings.warn(f"Add {self.type} to setValue() for {self.__repr__()}", Warning, stacklevel = 2)

	def dockRight(self, *args, **kwargs):
		"""Overload for dockRight() in handle_AuiManager."""

		if (self.type.lower() == "auipage"):
			if (self.label == None):
				warnings.warn(f"A label is needed for {self.__repr__()} to programatically dock it", Warning, stacklevel = 2)

			self.myManager.dockRight(self.label, *args, **kwargs)

		else:
			warnings.warn(f"Add {self.type} to setValue() for {self.__repr__()}", Warning, stacklevel = 2)

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
				self.parent.oneInstance_name = f"SingleApp-{wx.GetUserId()}"
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
	def getComPortList(self):
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
			warnings.warn(f"There is no COM port object {which}", Warning, stacklevel = 2)
			return None

	#Ethernet
	def makeSocket(self, which):
		"""Creates a new Ethernet object.

		Example Input: makeSocket(0)
		"""

		#Create Ethernet object
		mySocket = self.Ethernet(self)

		if (which in self.socketDict):
			warnings.warn(f"Overwriting Socket {which}", Warning, stacklevel = 2)

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
			warnings.warn(f"There is no Ethernet object {which}", Warning, stacklevel = 2)
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
			self.clientDict  = {} #Used to keep track of all client connections {"mySocket": connection object (socket), "data": client dataBlock (str), "stop": stop flag (bool), "listening": currently listening flag, "finished": recieved all flag}

			self.recieveStop = False #Used to stop the recieving function early
			self.ipScanStop  = False #Used to stop the ip scanning function early
			self.recieveListening = False #Used to chek if the recieve function has started listening or if it has finished listeing

			#Create the socket
			self.mySocket = None
			self.stream = None
			self.address = None
			self.port = None

		def open(self, address, port = 9100, error = False, pingCheck = False, 
			timeout = -1, stream = True):
			"""Opens the socket connection.

			address (str) - The ip address/website you are connecting to
			port (int)    - The socket port that is being used
			error (bool)  - Determines what happens if an error occurs
				If True: If there is an error, returns an error indicator. Otherwise, returns a 0
				If False: Raises an error exception
			pingCheck (bool) - Determines if it will ping an ip address before connecting to it to confirm it exists

			Example Input: open("www.example.com")
			"""

			if (self.mySocket != None):
				warnings.warn(f"Socket already opened", Warning, stacklevel = 2)

			#Account for the socket having been closed
			# if (self.mySocket == None):
			if (stream):
				self.mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				self.stream = "SOCK_STREAM"
			else:
				self.mySocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
				self.stream = "SOCK_DGRAM"

			if (timeout != -1):
				self.setTimeout(timeout)

			#Remove any white space
			address = re.sub("\s", "", address)

			#Make sure it exists
			if (pingCheck):
				addressExists = self.ping(address)

				if (not addressExists):
					print(f"Cannot ping address {address}")
					self.mySocket = None
					return False

			#Remember Values
			self.address = address
			self.port = port

			#Connect to the socket
			if (stream):
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

			if (self.mySocket == None):
				warnings.warn(f"Socket already closed", Warning, stacklevel = 2)
				return

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
			if (self.stream == "SOCK_DGRAM"):
				self.mySocket.sendto(data, (self.address, self.port))
			else:
				self.mySocket.sendall(data)
				# self.mySocket.send(data)

		def startRecieve(self, bufferSize = 256, scanDelay = 500):
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

				self.recieveListening = True

				#Listen
				while True:
					#Check for stop command
					if (self.recieveStop or (self.mySocket == None)):# or ((len(self.dataBlock) > 0) and (self.dataBlock[-1] == None))):
						self.recieveStop = False
						break

					#Check for data to recieve
					self.mySocket.setblocking(0)
					ready = select.select([self.mySocket], [], [], 0.5)
					if (not ready[0]):
						#Stop listening
						break

					#Retrieve the block of data
					data = self.mySocket.recv(bufferSize).decode() #The .decode is needed for python 3.4, but not for python 2.7
					# data, address = self.mySocket.recvfrom(bufferSize)#.decode() #The .decode is needed for python 3.4, but not for python 2.7

					#Check for end of data stream
					if (len(data) < 1):
						#Stop listening
						break

					#Save the data
					self.dataBlock.append(data)

					time.sleep(scanDelay / 1000)

				#Mark end of message
				self.dataBlock.append(None)
				self.recieveListening = False

			#Checks buffer size
			if (not (((bufferSize & (bufferSize - 1)) == 0) and (bufferSize > 0))):
				warnings.warn(f"Buffer size must be a power of 2, not {bufferSize}", Warning, stacklevel = 2)
				return None

			if (self.recieveListening):
				warnings.warn(f"Already listening to socket", Warning, stacklevel = 2)
				return None

			if ((len(self.dataBlock) > 0) and (self.dataBlock[-1] == None)):
				warnings.warn(f"Use checkRecieve() to take out data", Warning, stacklevel = 2)
				return None

			#Listen for data on a separate thread
			self.dataBlock = []
			self.parent.backgroundRun(runFunction, [self, bufferSize])

		def checkRecieve(self, removeNone = True):
			"""Checks what the recieveing data looks like.
			Each read portion is an element in a list.
			Returns the current block of data and whether it is finished listening or not.

			Example Input: checkRecieve()
			"""

			if (self.recieveStop):
				print("WARNING: Recieveing has stopped")
				return [], False

			if (not self.recieveListening):
				if (len(self.dataBlock) > 0):
					if (self.dataBlock[-1] != None):
						self.startRecieve()
				else:
					self.startRecieve()

			#The entire message has been read once the last element is None.
			finished = False
			compareBlock = self.dataBlock[:] #Account for changing mid-analysis
			self.dataBlock = []
			if (len(compareBlock) != 0):
				if (compareBlock[-1] == None):
					finished = True

					if (removeNone):
						compareBlock.pop(-1) #Remove the None from the end so the user does not get confused

			data = compareBlock[:]

			return data, finished

		def stopRecieve(self):
			"""Stops listening for data from the socket.
			Note: The data is still in the buffer. You can resume listening by starting startRecieve() again.
			To flush it, close the socket and then open it again.

			Example Input: stopRecieve()
			"""

			self.recieveStop = True

		#Server Side
		def startServer(self, address = None, port = 10000, clients = 1, scanDelay = 500):
			"""Starts a server that connects to clients.
			Modified code from Doug Hellmann on: https://pymotw.com/2/socket/tcp.html

			port (int)      - The port number to listen on
			clients (int)   - The number of clients to listen for
			scanDelay (int) - How long in milliseconds between scans for clients

			Example Input: startServer()
			Example Input: startServer(port = 80)
			Example Input: startServer(clients = 5)
			"""

			def runFunction():
				"""Needed to listen on a separate thread so the GUI is not tied up."""
				nonlocal self, address, port, clients, scanDelay

				#Bind the socket to the port
				if (address == None):
					address = '0.0.0.0'

				#Remove any white space
				address = re.sub("\s", "", address)

				serverIp = (socket.gethostbyname(address), port)
				self.address = address
				self.port = port

				self.mySocket.bind(serverIp)

				#Listen for incoming connections
				self.mySocket.listen(clients)
				count = clients #How many clients still need to connect
				clientIp = None
				while True:
					# Wait for a connection
					try:
						connection, clientIp = self.mySocket.accept()
					except:
						traceback.print_exc()
						if (clientIp != None):
							count = self.closeClient(clientIp[0], count)
						else:
							break

						#Check for all clients having connected and left
						if (count <= 0):
							break

					if (clientIp != None):
						#Catalogue client
						if (clientIp not in self.clientDict):
							self.clientDict[clientIp] = {"mySocket": connection, "data": "", "stop": False, "listening": False, "finished": False}
						else:
							warnings.warn(f"Client {clientIp} recieved again", Warning, stacklevel = 2)

					time.sleep(scanDelay / 1000)

			#Error Checking
			self.mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

			#Listen for data on a separate thread
			self.parent.backgroundRun(runFunction)

		def clientSend(self, clientIp, data, logoff = False):
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
			client = self.clientDict[clientIp]["mySocket"]
			client.sendall(data)

			# if (logoff):
			# 	client.shutdown(socket.SHUT_WR)

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
				self.clientDict[clientIp]["data"] = ""
				self.clientDict[clientIp]["finished"] = False
				self.clientDict[clientIp]["listening"] = True

				#Listen
				client = self.clientDict[clientIp]["mySocket"]
				while True:
					#Check for stop command
					if (self.clientDict[clientIp]["stop"]):
						self.clientDict[clientIp]["stop"] = False
						break

					#Retrieve the block of data
					data = client.recv(bufferSize).decode() #The .decode is needed for python 3.4, but not for python 2.7

					#Save the data
					self.clientDict[clientIp]["data"] += data

					#Check for end of data stream
					if (len(data) < bufferSize):
						#Stop listening
						break

				#Mark end of message
				self.clientDict[clientIp]["finished"] = True
				self.clientDict[clientIp]["listening"] = False

			#Checks buffer size
			if (not (((bufferSize & (bufferSize - 1)) == 0) and (bufferSize > 0))):
				warnings.warn(f"Buffer size must be a power of 2, not {bufferSize}", Warning, stacklevel = 2)
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

			if (self.clientDict[clientIp]["stop"]):
				print("WARNING: Recieveing has stopped")
				return [], False

			if (not self.clientDict[clientIp]["listening"]):
				if (len(self.clientDict[clientIp]["data"]) > 0):
					if (self.clientDict[clientIp]["finished"] != True):
						self.clientStartRecieve(clientIp)
				else:
					self.clientStartRecieve(clientIp)

			#Account for changing mid-analysis
			finished = self.clientDict[clientIp]["finished"]
			data = self.clientDict[clientIp]["data"][:]
			self.clientDict[clientIp]["data"] = ""

			# if (len(compareBlock) == 0):
			# 	finished = False

			return data, finished

		def clientStopRecieve(self, clientIp):
			"""Stops listening for data from the client.
			Note: The data is still in the buffer. You can resume listening by starting clientStartRecieve() again.
			To flush it, close the client and then open it again.

			clientIp (str)   - The IP address of the client

			Example Input: clientStopRecieve("169.254.231.0")
			"""

			self.clientDict[clientIp]["stop"] = True

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
				warnings.warn(f"There is no client {clientIp} for this server", Warning, stacklevel = 2)
			else:
				client = self.clientDict[clientIp]["mySocket"]
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
				warnings.warn(f"Unknown restiction flag {how}", Warning, stacklevel = 2)

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
				warnings.warn(f"Unknown unrestiction flag {how}", Warning, stacklevel = 2)

		def getTimeout(self):
			"""Gets the tiemout for the socket.
			By default, the timeout is None.

			Example Input: getTimeout()
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
					warnings.warn(f"Timeout cannot be negative for setTimeout() in {self.__repr__()}", Warning, stacklevel = 2)
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

			#Remove Whitespace
			address = re.sub("\s", "", address)

			#Ping the address
			output = subprocess.Popen(['ping', '-n', '1', '-w', '500', address], stdout=subprocess.PIPE, startupinfo=info).communicate()[0]
			output = output.decode("utf-8")

			#Interpret Ping Results
			if ("Destination host unreachable" in output):
				return False #Offline

			elif ("Request timed out" in output):
				return False #Offline

			elif ("could not find host" in output):
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

				#Remove Whitespace
				start = re.sub("\s", "", start)
				end = re.sub("\s", "", end)

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

		def isOpen(self, address = None):
			"""Returns if a socket is already open."""

			# error = self.mySocket.connect_ex((address, port))
			# if (error == 0):
			#   self.mySocket.shutdown(2)
			#   return True
			# return False

			if (self.mySocket == None):
				return True
			return False

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
						warnings.warn(f"There is no parity {value}", Warning, stacklevel = 2)
						return False

				else:
					warnings.warn(f"There is no parity {value}", Warning, stacklevel = 2)
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
				warnings.warn(f"There is no stop bit {value} for {self.__repr__()}", Warning, stacklevel = 2)

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
				warnings.warn(f"Cannot find serial port {self.serialPort.port} for {self.__repr__()}", Warning, stacklevel = 2)
				return False

			#Check port status
			if self.serialPort.isOpen():
				# print(f"Serial port {self.serialPort.port} sucessfully opened")
				return True
			else:
				warnings.warn(f"Cannot open serial port {self.serialPort.port} for {self.__repr__()}", Warning, stacklevel = 2)
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
					warnings.warn(f"Serial port has not been opened yet for {self.__repr__()}\n Make sure that ports are available and then launch this application again", Warning, stacklevel = 2)
			else:
				warnings.warn(f"No message to send for comWrite() in {self.__repr__()}", Warning, stacklevel = 2)

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
			warnings.warn(f"Cannot encrypt data without keys for {self.__repr__()}\n Use 'loadKeys()' or 'loadPublicKey() and loadPrivateKey()' first", Warning, stacklevel = 2)
			return None

		#Format the output path
		outputName = f"{directory}{name}.{extension}"

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
			warnings.warn(f"Cannot decrypt data without keys for {self.__repr__()}\n Use 'loadKeys()' or 'loadPublicKey() and loadPrivateKey()' first", Warning, stacklevel = 2)
			return None

		#Format the output path
		inputName = f"{directory}{name}.{extension}"

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
		self.windowDisabler = None

		self.loggingPrint = False
		self.old_stdout = sys.stdout.write
		self.old_stderr = sys.stderr.write

		#Record Address
		self.setAddressValue([id(self)], {None: self})

		#Used to pass functions from threads
		self.threadQueue = ThreadQueue()

		#Create the wx app object
		self.app = MyApp(parent = self)

	def __str__(self):
		"""Gives diagnostic information on the GUI when it is printed out."""
		global nestingCatalogue

		output = f"Controller()\n-- id: {id(self)}\n"
		# windowsList = [item for item in self.labelCatalogue.values() if isinstance(item, handle_Window)]
		windowsList = self.getNested(handle_Window)
		if (len(windowsList) + len(self.unnamedList) != 0):
			output += f"-- windows: {len(windowsList) + len(self.unnamedList)}\n"
		if (len(nestingCatalogue) != 0):
			output += f"-- nesting catalogue: {nestingCatalogue}\n"

		return output

	def __repr__(self):
		representation = f"Controller(id = {id(self)}"

		if (hasattr(self, "label")):
			representation += f", label = {self.label})"
		else:
			representation += ")"

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

		#Check nested windows first
		windowList = Utilities.get(self, None, typeList = [handle_Window])
		for window in windowList:
			try:
				handle = window.get(itemLabel = itemLabel, includeUnnamed = includeUnnamed, checkNested = checkNested, typeList = typeList)
				return handle
			except:
				pass

		#It is not a window item, so check inside of self
		handle = Utilities.get(self, itemLabel = itemLabel, includeUnnamed = includeUnnamed, checkNested = checkNested, typeList = typeList)
		return handle

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
		handle.setValue(newValue, event = event)

	def setSelection(self, label, newValue, *args, **kwargs):
		"""Overload for setSelection for handle_Widget_Base."""

		handle = self.get(label, *args, **kwargs)
		event = self.getArgument_event(label, args, kwargs)
		handle.setSelection(newValue, event = event)
	
	#Main Objects
	def addWindow(self, label = None, title = "", size = wx.DefaultSize, position = wx.DefaultPosition, panel = True, autoSize = True,
		tabTraversal = True, stayOnTop = False, floatOnParent = False, endProgram = True,
		resize = True, minimize = True, maximize = True, close = True, icon = None, internal = False, topBar = True,

		initFunction = None, initFunctionArgs = None, initFunctionKwargs = None, 
		delFunction = None, delFunctionArgs = None, delFunctionKwargs = None, 
		idleFunction = None, idleFunctionArgs = None, idleFunctionKwargs = None, 

		parent = None, handle = None, hidden = True, enabled = True):
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

		handle = handle_Window(self)
		handle.type = "Frame"
		handle.build(locals())
		self.finalNest(handle)

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
							warnings.warn(f"{item.__repr__()} not nested", Warning, stacklevel = 2)

		#Make sure all things are nested
		nestCheck(nestingCatalogue)
		
		#Take care of last minute things
		# windowsList = [item for item in self.labelCatalogue.values() if isinstance(item, handle_Window)]
		windowsList = self.getNested(include = handle_Window)
		for myFrame in windowsList + self.unnamedList:
			if (self.checkComplexity):
				#Make sure GUI is not too complex
				if (myFrame.complexity_total > myFrame.complexity_max):
					errorMessage = f"{myFrame.__repr__()} is too complex; {myFrame.complexity_total}/{myFrame.complexity_max}"
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
		#   frameFrom.closeWindow()

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

	def setToolTipAppearDelay(self, *args, **kwargs):
		"""Override function for setToolTipAppearDelay for handle_Window."""

		for window in self.getWindow():
			window.setToolTipAppearDelay(*args, **kwargs)

	def setToolTipDisappearDelay(self, *args, **kwargs):
		"""Override function for setToolTipDisappearDelay for handle_Window."""

		for window in self.getWindow():
			window.setToolTipDisappearDelay(*args, **kwargs)

	def setToolTipReappearDelay(self, *args, **kwargs):
		"""Override function for setToolTipReappearDelay for handle_Window."""

		for window in self.getWindow():
			window.setToolTipReappearDelay(*args, **kwargs)

	def centerWindowAll(self, *args, **kwargs):
		"""Centers all the windows on the screen.

		Example Input: centerWindowAll()
		"""

		for window in self.getWindow():
			window.centerWindow(*args, **kwargs)

	def logCMD(self):
		"""Logs print statements and errors in a text file.
		Acts as a middle man between the user and the intended function.

		Example Input: logCMD()
		"""

		def new_stdout(*args, fileName = "cmd_log.log", timestamp = True, **kwargs):
			"""Overrides the print function to also log the information printed.

			fileName (str)   - The filename for the log
			timestamp (bool) - Determines if the timestamp is added to the log
			"""
			nonlocal self

			self.logPrint(args, fileName = fileName, timestamp = timestamp, **kwargs)

			#Run the normal print function
			return self.old_stdout(*args)

		def new_stderr(*args, fileName = "error_log.log", timestamp = True, **kwargs):
			"""Overrides the stderr function to also log the error information.

			fileName (str)   - The filename for the log
			timestamp (bool) - Determines if the timestamp is added to the log
			"""
			nonlocal self

			self.logError(args, fileName = fileName, timestamp = timestamp, **kwargs)

			#Run the normal stderr function
			return self.old_stderr(*args)

		if (not self.loggingPrint):
			self.loggingPrint = True

			sys.stdout.write = new_stdout
			sys.stderr.write = new_stderr
		else:
			warnings.warn(f"Already logging cmd outputs for {item.__repr__()}", Warning, stacklevel = 2)

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

	def addInputSlider(self, windowLabel, *args, **kwargs):
		"""Overload for addInputSlider in handle_Window()."""

		myFrame = self.getWindow(windowLabel)
		handle = myFrame.addInputSlider(*args, **kwargs)

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

	def addButtonCheckList(self, windowLabel, *args, **kwargs):
		"""Overload for addButtonCheckList in handle_Window()."""

		myFrame = self.getWindow(windowLabel)
		handle = myFrame.addButtonCheckList(*args, **kwargs)

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

#User Things
class User_Utilities():
	def __init__(self, catalogue_variable = None, label_variable = None):
		if ((catalogue_variable != None) and (not isinstance(catalogue_variable, (str, Controller)))):
			errorMessage = f"'catalogue_variable' must be a str, not a {type(catalogue_variable)}"
			raise ValueError(errorMessage)
		if ((label_variable != None) and (not isinstance(label_variable, str))):
			errorMessage = f"'label_variable' must be a str, not a {type(label_variable)}"
			raise ValueError(errorMessage)

		self._catalogue_variable = catalogue_variable
		self._label_variable = label_variable

	def __repr__(self):
		representation = f"{type(self).__name__}(id = {id(self)})"
		return representation

	def __str__(self):
		output = f"{type(self).__name__}()\n-- id: {id(self)}\n"
		if (hasattr(self, "parent") and (self.parent != None)):
			output += f"-- Parent: {self.parent.__repr__()}\n"
		if (hasattr(self, "root") and (self.root != None)):
			output += f"-- Root: {self.root.__repr__()}\n"
		return output

	def __len__(self):
		if (hasattr(self, "_catalogue_variable") and (self._catalogue_variable != None)):
			if (isinstance(self._catalogue_variable, Controller)):
				return self._catalogue_variable.__len__()
		return len(self[:])

	def __contains__(self, key):
		if (hasattr(self, "_catalogue_variable") and (self._catalogue_variable != None)):
			if (isinstance(self._catalogue_variable, Controller)):
				return self._catalogue_variable.__contains__(key)

		if (key in self[:]):
			return True
		else:
			if (hasattr(self, "_catalogue_variable") and (self._label_variable != None)):
				for item in self[:]:
					if (hasattr(item, self._label_variable)):
						if (key == getattr(item, self._label_variable)):
							return True
		return False

	def __iter__(self):
		if (hasattr(self, "_catalogue_variable") and (self._catalogue_variable != None)):
			if (isinstance(self._catalogue_variable, Controller)):
				return self._catalogue_variable.__iter__()

		dataCatalogue = self._getDataCatalogue()
		return Iterator(dataCatalogue)

	def __getitem__(self, key):
		if (hasattr(self, "_catalogue_variable") and (self._catalogue_variable != None)):
			if (isinstance(self._catalogue_variable, Controller)):
				return self._catalogue_variable.__getitem__(key)
			
		dataCatalogue = self._getDataCatalogue()
		return self._get(dataCatalogue, key)

	def __setitem__(self, key, value):
		if (hasattr(self, "_catalogue_variable") and (self._catalogue_variable != None)):
			if (isinstance(self._catalogue_variable, Controller)):
				return self._catalogue_variable.__setitem__(key, value)
		
		dataCatalogue = self._getDataCatalogue()
		dataCatalogue[key] = value

	def __delitem__(self, key):
		if (hasattr(self, "_catalogue_variable") and (self._catalogue_variable != None)):
			if (isinstance(self._catalogue_variable, Controller)):
				return self._catalogue_variable.__delitem__(key)
		
		dataCatalogue = self._getDataCatalogue()
		del dataCatalogue[key]

	def __enter__(self):
		if (hasattr(self, "_catalogue_variable") and (self._catalogue_variable != None)):
			if (isinstance(self._catalogue_variable, Controller)):
				return self._catalogue_variable.__enter__()
			
		return self

	def __exit__(self, exc_type, exc_value, traceback):
		if (hasattr(self, "_catalogue_variable") and (self._catalogue_variable != None)):
			if (isinstance(self._catalogue_variable, Controller)):
				return self._catalogue_variable.__exit__(exc_type, exc_value, traceback)
			
		if (traceback != None):
			print(exc_type, exc_value)
			return False

	def _getDataCatalogue(self):
		"""Returns the data catalogue used to select items from this thing."""

		if (hasattr(self, "_catalogue_variable") and (self._catalogue_variable != None)):
			if (isinstance(self._catalogue_variable, str)):
				if (not hasattr(self, self._catalogue_variable)):
					warnings.warn(f"There is no variable {self._catalogue_variable} in {self.__repr__()} to use for the data catalogue", Warning, stacklevel = 2)
					dataCatalogue = {}
				else:
					dataCatalogue = getattr(self, self._catalogue_variable)
			else:
				if (isinstance(self._catalogue_variable, Controller)):
					dataCatalogue = self._catalogue_variable.labelCatalogue
				else:
					dataCatalogue = self._catalogue_variable
		else:
			dataCatalogue = {}

		return dataCatalogue

	def _get(self, itemCatalogue, itemLabel = None):
		"""Searches the label catalogue for the requested object.

		itemLabel (any) - What the object is labled as in the catalogue
			- If slice: objects will be returned from between the given spots 
			- If None: Will return all that would be in an unbound slice

		Example Input: _get(self.rowCatalogue)
		Example Input: _get(self.rowCatalogue, 0)
		Example Input: _get(self.rowCatalogue, slice(None, None, None))
		Example Input: _get(self.rowCatalogue, slice(2, 7, None))
		"""

		#Account for retrieving all nested
		if (itemLabel == None):
			itemLabel = slice(None, None, None)

		#Account for indexing
		if (isinstance(itemLabel, slice)):
			if (itemLabel.step != None):
				raise FutureWarning(f"Add slice steps to _get() for indexing {self.__repr__()}")
			
			elif ((itemLabel.start != None) and (itemLabel.start not in itemCatalogue)):
				errorMessage = f"There is no item labled {itemLabel.start} in the row catalogue for {self.__repr__()}"
				raise KeyError(errorMessage)
			
			elif ((itemLabel.stop != None) and (itemLabel.stop not in itemCatalogue)):
				errorMessage = f"There is no item labled {itemLabel.stop} in the row catalogue for {self.__repr__()}"
				raise KeyError(errorMessage)

			handleList = []
			begin = False
			for item in sorted(itemCatalogue.keys()):
				#Allow for slicing with non-integers
				if ((not begin) and ((itemLabel.start == None) or (itemCatalogue[item].label == itemLabel.start))):
					begin = True
				elif ((itemLabel.stop != None) and (itemCatalogue[item].label == itemLabel.stop)):
					break

				#Slice catalogue via creation date
				if (begin):
					handleList.append(itemCatalogue[item])
			return handleList

		elif (itemLabel not in itemCatalogue):
			answer = None
		else:
			answer = itemCatalogue[itemLabel]

		if (answer != None):
			if (isinstance(answer, (list, tuple, range))):
				if (len(answer) == 1):
					answer = answer[0]
			return answer

		errorMessage = f"There is no item labled {itemLabel} in the data catalogue for {self.__repr__()}"
		raise KeyError(errorMessage)

	def getValue(self, variable, order = True, exclude = []):
		"""Returns a list of all values for the requested variable.
		Special thank to Andrew Dalke for how to sort objects by attributes on https://wiki.python.org/moin/HowTo/Sorting#Key_Functions

		variable (str) - what variable to retrieve from all rows
		order (str) - By what variable to order the items
			- If variable does not exist: Will place the item at the end of the list with sort() amongst themselves
			- If True: Will use the python list function sort()
			- If False: Will not sort returned items
			- If None: Will not sort returned items

		Example Input: getValue("naed")
		Example Input: getValue(self.easyPrint_selectBy)
		Example Input: getValue("naed", "defaultOrder")
		"""

		if (not isinstance(exclude, (list, tuple, range))):
			exclude = [exclude]

		if ((order != None) and (not isinstance(order, bool))):
			data = [getattr(item, variable) for item in self.getOrder(order) if (item not in exclude)]
		else:
			data = [getattr(item, variable) for item in self if (item not in exclude)]

			if ((order != None) and (isinstance(order, bool)) and order):
				data.sort()

		return data

	def getOrder(self, variable, includeMissing = True, reverse = False, exclude = []):
		"""Returns a list of children in order according to the variable given.

		variable (str) - what variable to use for sorting
		includeMissing (bool) - Determiens what to do with children who do not have the requested variable

		Example Input: getOrder("order")
		"""

		if (not isinstance(exclude, (list, tuple, range))):
			exclude = [exclude]

		handleList = sorted([item for item in self if (hasattr(item, variable) and (item not in exclude))], key = lambda item: getattr(item, variable), reverse = reverse)

		if (includeMissing):
			handleList.extend([item for item in self if (not hasattr(item, variable) and (item not in exclude))])

		return handleList

	def getHandle(self, where, exclude = []):
		"""Returns a list of children whose variables are equal to what is given.

		where (dict) - {variable (str): value (any)}

		Example Input: getHandle({"order": 4})
		"""

		if (not isinstance(exclude, (list, tuple, range))):
			exclude = [exclude]

		handleList = []
		for handle in self[:]:
			if (handle not in exclude):
				for variable, value in where.items():
					if (hasattr(handle, variable) and (getattr(handle, variable) == value)):
						continue
					break
				else:
					handleList.append(handle)
		return handleList

	def getUnique(self, base = "{}", increment = 1, start = 1, exclude = []):
		"""Returns a unique name with the given criteria.

		Example Input: getUnique()
		Example Input: getUnique("Format_{}")
		Example Input: getUnique(exclude = [item.database_id for item in self.parent])
		"""

		if (not isinstance(exclude, (list, tuple, range))):
			exclude = [exclude]

		while True:
			ending = start + increment - 1
			if ((base.format(ending) in self) or (base.format(ending) in exclude) or (ending in exclude) or (str(ending) in [str(item) for item in exclude])):
				increment += 1
			else:
				break
		return base.format(ending)