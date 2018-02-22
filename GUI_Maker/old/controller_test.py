__version__ = "4.1.0"

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
import os
import sys
import time
# import ctypes
# import string
# import builtins
import inspect
import warnings
import functools


#Import wxPython elements to create GUI
import wx
import wx.adv
import wx.grid
# import wx.lib.masked
# import wx.lib.newevent
import wx.lib.splitter
# import wx.lib.agw.floatspin
# import wx.lib.mixins.listctrl
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
# import serial
# import socket


#Import barcode software for drawing and decoding barcodes
# import elaphe


#Import multi-threading to run functions as background processes
# import queue
import threading
# import subprocess


#Import needed support modules
# import re
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
shownWindowsList = [] #Used to keep track of which windows are being shown
dragDropDestination = None #Used to help a source know if a destination is itself
nestingCatalogue = {} #Used to keep track of what is nested in what

#Controllers
def build(*args, **kwargs):
	"""Starts the GUI making process."""

	return Controller(*args, **kwargs)

#Decorators
def wrap_makeWidget(sub = None):
	def decorator(function):
		def wrapper(self, *args, **kwargs):
			"""Makes a widget object"""

			if (sub == None):
				handle = handle_Widget_Base()
			else:
				handle = sub()
			function(self, *args, handle = handle, **kwargs)

			return handle
		return wrapper
	return decorator

def wrap_makeMenu():
	def decorator(function):
		def wrapper(self, *args, **kwargs):
			"""Makes a menu object"""

			if (not isinstance(self, handle_Menu)):
				#Make sure there is a menu bar
				menuList = self.getNested(include = handle_Menu)
				if (len(menuList) == 0):
					self.addMenuBar()

			handle = handle_Menu()
			function(self, *args, handle = handle, **kwargs)

			if (isinstance(self, handle_Window)):
				self.menubar.Append(handle.thing, handle.text)
			else:
				self.thing.Append(wx.ID_ANY, handle.text, handle.thing)
			handle.nested = True

			return handle
		return wrapper
	return decorator

def wrap_makeMenuItem():
	def decorator(function):
		def wrapper(self, *args, **kwargs):
			"""Makes a menu object"""

			handle = handle_MenuItem()
			function(self, *args, handle = handle, **kwargs)

			handle.nested = True

			return handle
		return wrapper
	return decorator

def wrap_makeSizer():
	def decorator(function):
		def wrapper(self, *args, **kwargs):
			"""Makes a sizer object"""

			handle = handle_Sizer()
			handle.myWindow = self

			if (isinstance(self, handle_Window)):
				sizerList = self.getNested(include = handle_Sizer)
				if (len(sizerList) == 0):
					#The first sizer added to a window is automatically nested
					handle.nested = True

			function(self, *args, handle = handle, **kwargs)

			return handle
		return wrapper
	return decorator

def wrap_addPanel():
	def decorator(function):
		def wrapper(self, *args, **kwargs):
			"""Makes a panel object"""

			handle = handle_Panel()

			if (isinstance(self, handle_Window)):
				panelList = self.getNested(include = handle_Panel)
				if (len(panelList) == 0):
					#The first panel added to a window is automatically nested
					handle.nested = True

			function(self, *args, handle = handle, **kwargs)

			return handle
		return wrapper
	return decorator

def wrap_makeWindow():
	def decorator(function):
		def wrapper(self, *args, **kwargs):
			"""Makes a window object"""

			#Unpack arguments
			arguments = self.getArguments(function, args, kwargs, "panel", {"panel": None})
			panel = arguments["panel"]

			handle = handle_Window()
			handle.nested = True
			function(self, *args, handle = handle, **kwargs)

			#Make the main panel
			if (panel):
				handle.mainPanel = handle.addPanel()#"-1", parent = handle, size = (10, 10), tabTraversal = tabTraversal, useDefaultSize = False)

			return handle
		return wrapper
	return decorator

def wrap_makeSplitter():
	def decorator(function):
		def wrapper(self, *args, **kwargs):
			"""Makes a window object"""

			#Check Complexity
			controller = self.getAddressValue([self.nestingAddress[0]])[None]
			if (controller.checkComplexity):
				nestedList = self.getNested(include = handle_Splitter)
				if (len(nestedList) > 0):
					warnings.warn("Adding more than one splitter in {} may make GUI framework too complex".format(self.myWindow.__repr__()), Warning, stacklevel = 2)

			#Create Splitter
			handle = handle_Splitter()
			function(self, *args, handle = handle, **kwargs)

			#Nest splitter
			self.nest(handle)

			return handle
		return wrapper
	return decorator

def wrap_nestingAddress():
	def decorator(function):
		def wrapper(self, *args, **kwargs):
			"""Makes a window object"""

			handle = function(self, *args, **kwargs)

			handle.nestingAddress = self.nestingAddress + [id(self)]
			self.setAddressValue(handle.nestingAddress + [id(handle)], {None: handle})

			if (not isinstance(self, Controller)):
				self.allowBuildErrors = nestingCatalogue[self.nestingAddress[0]][None].allowBuildErrors
				handle.allowBuildErrors = self.allowBuildErrors

			return handle
		return wrapper
	return decorator

def wrap_addLabel():
	def decorator(function):
		def wrapper(self, *args, **kwargs):
			"""Makes objects callable from a label."""

			#Unpack arguments
			arguments = self.getArguments(function, args, kwargs, ["handle", "label"], {"handle": None, "label": None})
			handle = arguments["handle"]
			label = arguments["label"]

			#Store data
			handle.label = label

			#Run function
			handle = function(self, *args, **kwargs)

			#Add object to internal catalogue
			if (label != None):
				if (label in self.labelCatalogue):
					warnings.warn("Overwriting label association for {} in ".format(label), Warning, stacklevel = 2)

				self.labelCatalogue[handle.label] = handle
				self.labelCatalogueOrder.append(handle.label)
			else:
				self.unnamedList.append(handle)

			return handle
		return wrapper
	return decorator

def wrap_setParent():
	def decorator(function):
		def wrapper(self, *args, **kwargs):
			"""Determines where to put the object."""

			#Unpack arguments
			arguments = self.getArguments(function, args, kwargs, ["handle", "parent"], {"handle": None, "parent": None})
			handle = arguments["handle"]
			parent = arguments["parent"]

			#Determine parent
			if (parent != None):
				handle.parent = parent
			else:
				if (not isinstance(self, Controller)):
					if (self.parent != None):
						handle.parent = self.parent
					else:
						if (self.mainPanel != None):
							handle.parent = self.mainPanel
						else:
							handle.parent = self
			
			#Run Function
			handle = function(self, *args, **kwargs)

			return handle
		return wrapper
	return decorator

def wrap_setLocation(default_flags = "c1"):
	def decorator(function):
		def wrapper(self, *args, **kwargs):
			"""Determines where to put the object."""

			#Unpack arguments
			arguments = self.getArguments(function, args, kwargs, ["handle", "flags", "flex"], {"handle": None, "flags": default_flags, "flex": 0})
			handle = arguments["handle"]
			flags = arguments["flags"]
			flex = arguments["flex"]

			#Which sizer is being used?
			handle.sizer = self

			#Run Function
			handle = function(self, *args, **kwargs)

			#Add it to the sizer
			handle.sizer.nest(handle, flex = flex, flags = flags)

			return handle
		return wrapper
	return decorator

def wrap_setSelection():
	def decorator(function):
		def wrapper(self, *args, **kwargs):
			"""Determines if the object is selected by default."""

			#Unpack arguments
			arguments = self.getArguments(function, args, kwargs, ["selected"], {"selected": None})
			selected = arguments["selected"]

			handle = function(self, *args, **kwargs)

			#Determine if it is selected by default
			if (selected):
				handle.thing.SetDefault() 

			return handle
		return wrapper
	return decorator

def wrap_setDirection():
	def decorator(function):
		def wrapper(self, *args, **kwargs):
			"""Controls which direction things go in a sizer."""

			#Unpack arguments
			arguments = self.getArguments(function, args, kwargs, ["handle", "vertical"], {"handle": None, "vertical": None})
			handle = arguments["handle"]
			vertical = arguments["vertical"]

			if (vertical == None):
				handle.direction = wx.BOTH
			elif (vertical):
				handle.direction = wx.VERTICAL
			else:
				handle.direction = wx.HORIZONTAL

			#Run function
			handle = function(self, *args, **kwargs)

			return handle
		return wrapper
	return decorator

def wrap_setState_hidden():
	def decorator(function):
		def wrapper(self, *args, **kwargs):
			"""Determines if the object is hidden."""

			#Unpack arguments
			arguments = self.getArguments(function, args, kwargs, ["hidden"], {"hidden": None})
			hidden = arguments["hidden"]

			handle = function(self, *args, **kwargs)
			
			#Determine visibility
			if (hidden):
				if (isinstance(self, handle_Sizer)):
					self.addFinalFunction(handle.thing.ShowItems, False)
				else:
					handle.thing.Hide()

			return handle
		return wrapper
	return decorator

def wrap_setState_disabled():
	def decorator(function):
		def wrapper(self, *args, **kwargs):
			"""Determines if the object is enabled."""

			#Unpack arguments
			arguments = self.getArguments(function, args, kwargs, ["enabled"], {"enabled": None})
			enabled = arguments["enabled"]

			handle = function(self, *args, **kwargs)
			
			#Determine if it is enabled
			if (not enabled):
				handle.thing.Disable()

			return handle
		return wrapper
	return decorator

def wrap_checkType(typeNeeded = []):
	def decorator(function):
		def wrapper(self, *args, **kwargs):
			"""Makes sure an object is of a specific type"""
			nonlocal typeNeeded

			#Ensure correct format
			if ((not isinstance(typeNeeded, list)) and (not isinstance(typeNeeded, tuple))):
				typeNeeded = [typeNeeded]

			#Error check
			if (self.type not in typeNeeded):
				errorMessage = "Cannot use type {} with the function {}".format(self.type, function.__name__)
				raise TypeError(errorMessage)

			#Run function
			answer = function(self, *args, **kwargs)

			return answer
		return wrapper
	return decorator

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
					bindObject = self

			elif (thingClass == "wxMenuItem"):
				bindObject = self
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

	#Nesting Catalogue
	def getAddressValue(self, address):
		"""Returns the value of a given address for a dictionary of dictionaries.
		Special thanks to DomTomCat for how to get a value from a dictionary of dictionaries of n depth on https://stackoverflow.com/questions/14692690/access-nested-dictionary-items-via-a-list-of-keys
		
		address (list) - The path of keys to follow on the catalogue

		Example Input: getAddressValue(self.nestingAddress)
		Example Input: getAddressValue(self.nestingAddress + [self.(id)])
		"""
		global nestingCatalogue

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

	#Etc
	def getArguments(self, function, argList, kwargDict, desiredArgs = None, notFound = {}):
		"""Returns a dictionary of the args and kwargs for a function.

		function (function) - The function to inspect
		argList (list)      - The *args of 'function'
		kwargDict (dict)    - The **kwargs of 'function'
		desiredArgs (str)   - Determines what is returned to the user. Can be a list of strings
			- If None: A dictionary of all args and kwargs will be returned
			- If not None: A dictionary of the provided args and kwargs will be returned if they exist
		notFound (dict)     - Allows the user to define what an argument should be if it is not in the function's argument list. {kwarg (str): default (any)}

		Example Input: getArguments(myFunction, args, kwargs)
		Example Input: getArguments(myFunction, args, kwargs, desiredArgs = "handler")
		Example Input: getArguments(myFunction, args, kwargs, desiredArgs = "handler")
		Example Input: getArguments(myFunction, args, kwargs, desiredArgs = ["handler", "flex", "flags"])
		Example Input: getArguments(myFunction, args, kwargs, desiredArgs = ["handler", "flex", "flags"], notFound = {"flex": 0, "flags" = "c1"})
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

#handles
class handle_Base(Utilities):
	"""The base handler for all GUI handlers.
	Meant to be inherited.
	"""

	def __init__(self):
		"""Initializes defaults."""

		#Initialize Inherited Classes
		Utilities.__init__(self)

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

	def get(self, itemLabel, includeUnnamed = True):
		"""Searches the label catalogue for the requested object.

		itemLabel (any) - What the object is labled as in the catalogue
			- If slice: objects will be returned from between the given spots 

		Example Input: get(0)
		Example Input: get(1.1)
		Example Input: get("text")
		Example Input: get(slice(None, None, None))
		Example Input: get(slice(2, "text", None))
		"""

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

			return handleList

		elif (itemLabel not in self.labelCatalogue):
			errorMessage = "There is no item labled {} in the label catalogue for {}".format(itemLabel, self.__repr__())
			raise KeyError(errorMessage)

		else:
			return self.labelCatalogue[itemLabel]

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

	#Getters
	def getValue(self):
		"""Returns what the contextual value is for the object associated with this handle."""

		if (self.type == "ProgressBar"):
			value = self.thing.GetValue() #(int) - Where the progress bar currently is

		else:
			warnings.warn("Add {} to getValue() for {}".format(self.type, self.__repr__()), Warning, stacklevel = 2)
			value = None

		return value

	def getIndex(self):
		"""Returns what the contextual index is for the object associated with this handle."""

		if (False):
			pass
		else:
			warnings.warn("Add {} to getIndex() for {}".format(self.type, self.__repr__()), Warning, stacklevel = 2)
			value = None

		return value

	def getAll(self):
		"""Returns all the contextual values for the object associated with this handle."""

		if (self.type == "ProgressBar"):
			value = self.thing.GetRange()

		else:
			warnings.warn("Add {} to getAll() for {}".format(self.type, self.__repr__()), Warning, stacklevel = 2)
			value = None

		return value

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
	def getValue(self):
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
	def setValue(self, newValue):
		"""Sets the contextual value for the object associated with this handle to what the user supplies."""

		if (self.type == "Text"):
			if (not isinstance(newValue, str)):
				newValue = str(newValue)

			self.thing.SetLabel(newValue) #(str) - What the static text will now say

		elif (self.type == "Hyperlink"):
			if (not isinstance(newValue, str)):
				newValue = str(newValue)

			self.thing.SetURL(newValue) #(str) - What the hyperlink will now connect to

		else:
			warnings.warn("Add {} to setValue() for {}".format(self.type, self.__repr__()), Warning, stacklevel = 2)

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
	def getValue(self):
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

	def getIndex(self):
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

	def getAll(self):
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
	def setValue(self, newValue, filterNone = True):
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

	def setSelection(self, newValue):
		"""Sets the contextual value for the object associated with this handle to what the user supplies."""

		if (self.type == "ListDrop"):
			if (isinstance(newValue, str)):
				newValue = thing.FindString(newValue)

			if (newValue == None):
				errorMessage = "Invalid drop list selection in setSelection() for {}".format(self.__repr__())
				raise ValueError(errorMessage)
				
			thing.SetSelection(newValue) #(int) - What the choice options will now be

		else:
			warnings.warn("Add {} to setSelection() for {}".format(self.type, self.__repr__()), Warning, stacklevel = 2)

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
	def getValue(self):
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
	def setValue(self, newValue):
		"""Sets the contextual value for the object associated with this handle to what the user supplies."""

		if (self.type == "InputBox"):
			if (newValue == None):
				newValue = "" #Filter None as blank text
			self.thing.SetValue(newValue) #(str) - What will be shown in the text box

		elif (self.type == "InputSpinner"):
			thing.SetValue(newValue) #(int / float) - What will be shown in the input box

		elif (self.type == "Slider"):
			thing.SetValue(newValue) #(int / float) - Where the slider position will be

		elif (self.type == "InputSearch"):
			if (newValue == None):
				newValue = "" #Filter None as blank text
			self.thing.SetValue(newValue) #(str) - What will be shown in the search box

		else:
			warnings.warn("Add {} to setValue() for {}".format(self.type, self.__repr__()), Warning, stacklevel = 2)

	def setMin(self, newValue):
		"""Sets the contextual minimum for the object associated with this handle to what the user supplies."""

		if (self.type == "InputSpinner"):
			thing.SetMin(newValue) #(int / float) - What the min value will be for the the input box

		elif (self.type == "Slider"):
			thing.SetMin(newValue) #(int / float) - What the min slider position will be

		else:
			warnings.warn("Add {} to setMin() for {}".format(self.type, self.__repr__()), Warning, stacklevel = 2)

	def setMax(self, newValue):
		"""Sets the contextual maximum for the object associated with this handle to what the user supplies."""

		if (self.type == "InputSpinner"):
			thing.SetMax(newValue) #(int / float) - What the max value will be for the the input box

		elif (self.type == "Slider"):
			thing.SetMax(newValue) #(int / float) - What the max slider position will be

		else:
			warnings.warn("Add {} to setMax() for {}".format(self.type, self.__repr__()), Warning, stacklevel = 2)

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
	def getValue(self):
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

	def getIndex(self):
		"""Returns what the contextual index is for the object associated with this handle."""

		if (self.type == "ButtonRadioBox"):
			value = self.thing.GetSelection() #(int) - Which button is selected by index

		if (self.type == "CheckList"):
			value = self.thing.GetCheckedItems() #(list) - Which checkboxes are selected as integers

		else:
			warnings.warn("Add {} to getIndex() for {}".format(self.type, self.__repr__()), Warning, stacklevel = 2)
			value = None

		return value

	def getAll(self):
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
	def setValue(self, newValue):
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
	def getValue(self):
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
	def setValue(self, newValue):
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

			thing.SetTime(hour, minute, second) #(str) - What time will be selected as 'hour:minute:second'

		else:
			warnings.warn("Add {} to setValue() for {}".format(self.type, self.__repr__()), Warning, stacklevel = 2)

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
	def getValue(self):
		"""Returns what the contextual value is for the object associated with this handle."""

		if (self.type == "Image"):
			value = self.thing.GetBitmap() #(bitmap) - The image that is currently being shown

		else:
			warnings.warn("Add {} to getValue() for {}".format(self.type, self.__repr__()), Warning, stacklevel = 2)
			value = None

		return value

	#Setters
	def setValue(self, newValue):
		"""Sets the contextual value for the object associated with this handle to what the user supplies."""

		if (self.type == "Image"):
			image = self.getImage(newValue)
			self.thing.SetBitmap(image) #(wxBitmap) - What the image will be now

		else:
			warnings.warn("Add {} to setValue() for {}".format(self.type, self.__repr__()), Warning, stacklevel = 2)


class handle_MenuItem(handle_Widget_Base):
	"""A handle for working with image widgets."""

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

	#Setters
	def setValue(self, newValue):
		"""Sets the contextual value for the object associated with this handle to what the user supplies."""

		if (classType == "wxMenuItem"):
			if ((thing.GetKind() == wx.ITEM_CHECK) or (thing.GetKind() == wx.ITEM_RADIO)):
				myMenu = thing.GetMenu()
				myId = thing.GetId()
				myMenu.Check(myId, newValue) #(bool) - True: selected; False: un-selected
			else:
				errorMessage = "Only a menu 'Check Box' or 'Radio Button' can be set to a different value for setValue() for {}".format(self.__repr__())
				raise SyntaxError(errorMessage)

		else:
			warnings.warn("Add {} to setValue() for {}".format(self.type, self.__repr__()), Warning, stacklevel = 2)

class handle_Menu(handle_Container_Base):
	"""A handle for working with image widgets."""

	def __init__(self):
		"""Initializes defaults."""

		#Initialize inherited classes
		handle_Container_Base.__init__(self)

	def getValue(self, event = None):
		"""Returns what the contextual value is for the object associated with this handle."""

		if (self.type == ""):
			pass

		else:
			warnings.warn("Add {} to getValue() for {}".format(self.type, self.__repr__()), Warning, stacklevel = 2)
			value = None

		return value

	#Setters
	def setValue(self, newValue):
		"""Sets the contextual value for the object associated with this handle to what the user supplies."""

		if (classType == ""):
			pass

		else:
			warnings.warn("Add {} to setValue() for {}".format(self.type, self.__repr__()), Warning, stacklevel = 2)

	def addMenuItem(self, text = "", icon = None, internal = False, special = None, check = None, default = False, toolTip = "",

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, 

		label = None, hidden = False, enabled = True, handle = None):
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

		myLabel (str) - What this is called in the idCatalogue
		special (str) - Declares if the item has a special pre-defined functionality. Overrides 'myLabel'. Only the first letter matters
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
		Example Input: addMenuItem(2, "Print Preview", myFunction = [self.onPrintLabelsPreview, "self.onShowPopupWindow"], myFunctionArgs = [None, 0], myLabel = "printPreview")
		"""

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

		#Determine initial value
		# if (check != None):
		# 	if (default):
		# 		self.thing.Check(myId, True)

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
				toolTip = str(toolTip)

			#Do not add empty tool tips
			if (len(toolTip) != 0):
				handle.thing.SetHelp(toolTip)

		return handle

	def addMenuSeparator(self, 

		label = None, hidden = False, handle = None):
		"""Adds a line to a specific pre-existing menu to separate menu items.

		Example Input: addMenuSeparator()
		"""

		handle.thing = wx.MenuItem(self.thing, kind = wx.ITEM_SEPARATOR)
		self.thing.Append(handle.thing)

		return handle

	def addMenuSub(self, text = "", 

		label = None, hidden = False, handle = None):
		"""Adds a sub menu to a specific pre-existing menu.
		To adding items to a sub menu is the same as for menus.

		text (str)  - The text for the menu item. This is what is shown to the user
		label (int) - The label for this menu

		Example Input: addMenuSub()
		Example Input: addMenuSub(text = "I&mport")
		"""

		#Create menu
		handle.thing = wx.Menu()
		handle.text = text

		return handle

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

		tableNumber (int) - The table catalogue number for this table
		numberOf (int)      - How many columns to add
		updateLabels (bool) - If True: The row labels will update

		Example Input: appendColumn(0)
		Example Input: appendColumn(0, 5)
		"""

		self.thing.AppendCols(numberOf, updateLabels)

	def enableTableEditing(self, row = -1, column = -1):
		"""Allows the user to edit the table.

		tableNumber (int) - What the table is called in the table catalogue
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
					self.thing.readOnlyCatalogue[row][column] = False

				elif ((row == -1) and (column == -1)):
					for i in range(self.thing.GetNumberRows()):
						for j in range(self.thing.GetNumberCols()):
							self.thing.readOnlyCatalogue[i][j] = False

				elif (row != -1):
					for j in range(self.thing.GetNumberCols()):
						self.thing.readOnlyCatalogue[row][j] = False

				elif (column != -1):
					for i in range(self.thing.GetNumberRows()):
						self.thing.readOnlyCatalogue[i][column] = False

	def disableTableEditing(self, row = -1, column = -1):
		"""Allows the user to edit the table.

		tableNumber (int) - What the table is called in the table catalogue
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
					self.thing.readOnlyCatalogue[row][column] = True

				elif ((row == -1) and (column == -1)):
					for i in range(self.thing.GetNumberRows()):
						for j in range(self.thing.GetNumberCols()):
							self.thing.readOnlyCatalogue[i][j] = True

				elif (row != -1):
					for j in range(self.thing.GetNumberCols()):
						self.thing.readOnlyCatalogue[row][j] = True

				elif (column != -1):
					for i in range(self.thing.GetNumberRows()):
						self.thing.readOnlyCatalogue[i][column] = True

	def getTableReadOnly(self, row, column, tableNumber):
		"""Moves the table highlight cursor to the given cell coordinates
		The top-left corner is row (0, 0) not (1, 1).

		row (int)         - The index of the row
		column (int)      - The index of the column
		tableNumber (int) - What the table is called in the table catalogue

		Example Input: getTableReadOnly(1, 1, 0)
		"""

		thing = self.getTable(tableNumber)
		readOnly = self.thing.readOnlyCatalogue[row][column]
		return readOnly

	def getTableCurrentCellReadOnly(self, tableNumber):
		"""Moves the table highlight cursor to the given cell coordinates
		The top-left corner is row (0, 0) not (1, 1).

		tableNumber (int) - What the table is called in the table catalogue

		Example Input: getTableCurrentCellReadOnly(0)
		"""

		selection = self.getTableCurrentCell(tableNumber)

		#Default to the top left cell if a range is selected
		row, column = selection[0]

		readOnly = self.getTableReadOnly(row, column, tableNumber)
		return readOnly

	def clearTable(self, tableNumber):
		"""Clears all cells in the table

		tableNumber (int) - What the table is called in the table catalogue

		Example Input: clearTable( 0)
		"""
		
		self.thing.ClearGrid()

	def setTableCursor(self, row, column, tableNumber):
		"""Moves the table highlight cursor to the given cell coordinates
		The top-left corner is row (0, 0) not (1, 1).

		row (int)         - The index of the row
		column (int)      - The index of the column
		tableNumber (int) - What the table is called in the table catalogue

		Example Input: setTableCursor(1, 2, 0)
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
		tableNumber (int) - What the table is called in the table catalogue
		noneReplace (bool) - Determines what happens if the user gives a value of None for 'value'.
			- If True: Will replace the cell with ""
			- If False: Will not replace the cell

		Example Input: setTableCell(1, 2, 42, 0)
		Example Input: setTableCell(1, 2, 3.14, 0)
		Example Input: setTableCell(1, 2, "Lorem Ipsum", 0)
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
		tableNumber (int)  - What the table is called in the table catalogue
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

	def getTableCellValue(self, row, column, tableNumber):
		"""Reads something in a cell.
		The top-left corner is row (0, 0) not (1, 1).

		row (int)         - The index of the row
			- If None: Will return the all values of the column if 'column' is not None
		column (int)      - The index of the column
			- If None: Will return the all values of the row if 'row' is not None
		tableNumber (int) - What the table is called in the table catalogue

		Example Input: getTableCellValue(1, 2, 0)
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

	def getTableCell_atMouse(self, tableNumber):
		"""Returns the cell coordinates of where the mouse is."""

		thing = self.getTable(tableNumber)

		row = self.thing.GetGridCursorRow()
		column = self.thing.GetGridCursorCol()

		return (row, column)

	def getTableCurrentCell(self, tableNumber):
		"""Returns the row and column of the currently selected cell.
		The top-left corner is row (0, 0) not (1, 1).
		Modified code from http://ginstrom.com/scribbles/2008/09/07/getting-the-selected-cells-from-a-wxpython-grid/

		tableNumber (int) - What the table is called in the table catalogue
		rangeOn (bool)    - Determines what is returned when the user has a range of cells selected
			- If True: Returns [[(row 1, col 1), (row 1, col 2)], [(row 2, col 1), (row 2, col 2)]]
			- If False: Returns (row, col) of which cell in the range is currently active

		Example Input: getTableCurrentCellValue(0)
		"""

		#Setup
		thing = self.getTable(tableNumber)
		currentCell = []

		#Check for multiple cells that were drag selected
		top_left_list = self.thing.GetSelectionBlockTopLeft()
		if (top_left_list):
			bottom_right_list = self.thing.GetSelectionBlockBottomRight()

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
				row, column = self.tableDict[tableNumber]["currentCell"]
				
				currentCell = [(row, column)]
			else:
				currentCell = selection

		return currentCell

	def getTableCurrentCellValue(self, tableNumber):
		"""Reads something from rhe currently selected cell.
		The top-left corner is row (0, 0) not (1, 1).

		tableNumber (int) - What the table is called in the table catalogue

		Example Input: getTableCurrentCellValue(0)
		"""

		#Get the selected cell's coordinates
		selection = self.getTableCurrentCell(tableNumber)

		#Default to the top left cell if a range is selected
		row, column = selection[0]

		#Get the currently selected cell's value
		value = self.getTableCellValue(row, column, tableNumber)

		return value

	def getTablePreviousCell(self, tableNumber):
		"""Returns the row and column of the previously selected cell.
		The top-left corner is row (0, 0) not (1, 1).

		tableNumber (int) - What the table is called in the table catalogue

		Example Input: getTablePreviousCellValue(0)
		"""

		selection = self.thing.GetSelectedCells()

		#Get the selected cell's coordinates
		if not selection:
			row, column = self.tableDict[tableNumber]["previousCell"]
		else:
			### Not Working Yet
			print("WARNING: Previous selection of ranges is not currently working")
			row = selection[0]
			column = selection[1]

		return (row, column)

	def getTablePreviousCellValue(self, tableNumber):
		"""Reads something from the previously selected cell.
		The top-left corner is row (0, 0) not (1, 1).

		tableNumber (int) - What the table is called in the table catalogue

		Example Input: getTablePreviousCellValue(0)
		"""

		#Get the selected cell's coordinates
		row, column = self.getTablePreviousCell()

		#Get the currently selected cell's value
		value = self.thing.GetCellValue(row, column)

		return value

	def setTableRowLabel(self, row, rowLabel, tableNumber):
		"""Changes a row's tableNumber.
		The top-left corner is row (0, 0) not (1, 1).

		row (int)         - The index of the row
		rowLabel (str)    - The new tableNumber for the row
		tableNumber (int) - What the table is called in the table catalogue

		Example Input: setTableRowLabel(1, "Row 1", 0)
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
		columnLabel (str) - The new tableNumber for the row

		Example Input: setTableColumnLabel(1, "Column 2")
		"""

		#Ensure correct data type
		if (not isinstance(text, str)):
			text = str(text)

		#Set the cell value
		self.thing.SetColLabelValue(column, text)

	def getTableColumnLabel(self, column, tableNumber):
		"""Returns a cell's column label
		The top-left corner is row (0, 0) not (1, 1).

		column (int)      - The index of the row
		tableNumber (int) - What the table is called in the table catalogue

		Example Input: setTableColumnLabel(1, 0)
		"""

		#Ensure correct data type
		if (not isinstance(columnLabel, str)):
			columnLabel = str(columnLabel)

		#Set the cell value
		columnLabel = self.thing.GetColLabelValue(column)
		return columnLabel

	def setTableCellFormat(self, row, column, format, tableNumber):
		"""Changes the format of the text in a cell.
		The top-left corner is row (0, 0) not (1, 1).

		row (int)    - The index of the row
		column (int) - The index of the column
		format (str) - The format for the cell
			~ "float" - floating point
		tableNumber (int) - What the table is called in the table catalogue

		Example Input: setTableCellFormat(1, 2, "float", 0)
		"""

		#Set the cell format
		if (format == "float"):
			self.thing.SetCellFormatFloat(row, column, width, percision)

	def setTableCellColor(self, row, column, color, tableNumber):
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
		tableNumber (int) - What the table is called in the table catalogue

		Example Input: setTableCellColor(1, 2, (255, 0, 0), 0)
		Example Input: setTableCellColor(1, 2, "red", 0)
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

	def getTableCellColor(self, row, column, tableNumber):
		"""Returns the color of the background of a cell.
		The top-left corner is row (0, 0) not (1, 1).

		row (int)     - The index of the row
			- If None: Will color all cells of the column if 'column' is not None
		column (int)  - The index of the column
			- If None: Will color all cells of the column if 'column' is not None
		tableNumber (int) - What the table is called in the table catalogue

		Example Input: getTableCellColor(1, 2, 0)
		"""

		color = self.thing.GetCellBackgroundColour(row, column)
		return color

	def setTableCellFont(self, row, column, font, italic = False, bold = False):
		"""Changes the color of the text in a cell.
		The top-left corner is row (0, 0) not (1, 1).

		row (int)         - The index of the row
		column (int)      - The index of the column
		font(any)         - What font the text will be in the cell. Can be a:
								(A) string with the english word for the color
								(B) wxFont object
		tableNumber (int) - What the table is called in the table catalogue
		italic (bool)     - If True: the font will be italicized
		bold (bool)       - If True: the font will be bold

		Example Input: setTableTextColor(1, 2, "TimesNewRoman", 0)
		Example Input: setTableTextColor(1, 2, wx.ROMAN, 0)
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
		tableNumber (int) - What the table is called in the table catalogue
		italic (bool)     - If True: the font will be italicized
		bold (bool)       - If True: the font will be bold

		Example Input: setTableTextColor(1, 2, "TimesNewRoman", 0)
		Example Input: setTableTextColor(1, 2, wx.ROMAN, 0)
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

	def hideTableRow(self, row, tableNumber):
		"""Hides a row in a grid.
		The top-left corner is row (0, 0) not (1, 1).

		row (int)         - The index of the row
		tableNumber (int) - What the table is called in the table catalogue

		Example Input: hideTableRow(1, 0)
		"""

		self.thing.SetRowLabelSize(0) # hide the rows

	def hideTableColumn(self, column, tableNumber):
		"""Hides a column in a grid.
		The top-left corner is column (0, 0) not (1, 1).

		column (int)         - The index of the column
		tableNumber (int) - What the table is called in the table catalogue

		Example Input: hideTableColumn(1, 0)
		"""

		self.thing.SetColLabelSize(0) # hide the columns

	def setTableTextColor(self, row, column, color, tableNumber):
		"""Changes the color of the text in a cell.
		The top-left corner is row (0, 0) not (1, 1).

		row (int)         - The index of the row
		column (int)      - The index of the column
		color(any)        - What color the text will be in the cell. Can be a:
								(A) string with the english word for the color
								(B) wxColor object
								(C) list with the rgb color code; [red, green, blue]
								(D) string with the hex color code (remember to include the #)
		tableNumber (int) - What the table is called in the table catalogue

		Example Input: setTableTextColor(1, 2, "red", 0)
		Example Input: setTableTextColor(1, 2, wx.RED, 0)
		Example Input: setTableTextColor(1, 2, [255, 0, 0], 0)
		Example Input: setTableTextColor(1, 2, "#FF0000", 0)
		"""

		#Set the text color
		self.thing.SetCellTextColour(row, column, color)

	def setTableBackgroundColor(self, row, column, color, tableNumber):
		"""Changes the color of the text in a cell.
		The top-left corner is row (0, 0) not (1, 1).

		row (int)         - The index of the row
		column (int)      - The index of the column
		color(any)        - What color the text will be in the cell. Can be a:
								(A) string with the english word for the color
								(B) wxColor object
								(C) list with the rgb color code; [red, green, blue]
								(D) string with the hex color code (remember to include the #)
		tableNumber (int) - What the table is called in the table catalogue

		Example Input: setTableBackgroundColor(1, 2, "red", 0)
		Example Input: setTableBackgroundColor(1, 2, wx.RED)
		Example Input: setTableBackgroundColor(1, 2, [255, 0, 0], 0)
		Example Input: setTableBackgroundColor(1, 2, "#FF0000", 0)
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
							  
		Example Input: autoTableSizeRow(3, 0)
		Example Input: autoTableSizeRow(4, 0, setAsMinimum = False)
		"""

		#Size Row
		self.thing.AutoSizeRow(row, setAsMinimum)

	def autoTableSizeColumn(self, column, setAsMinimum = False):
		"""Sizes the a single column to fit its contents.
		What is autosizing can be toggled on and off.

		column (int)        - The column that will be autosized
		setAsMinimum (bool) - If True: The calculated sizes will be set as the minimums
							  
		Example Input: autoTableSizeColumn(3, 0)
		Example Input: autoTableSizeColumn(4, 0, setAsMinimum = False)
		"""

		#Size Row
		self.thing.AutoSizeColumn(column, setAsMinimum)

	def autoTableSizeRowLabel(self, row, setAsMinimum = False):
		"""Sizes the a single row to fit the height of the row label.

		row (int)           - The row that will be autosized
										  
		Example Input: autoSizeRowLabel(3, 0)
		"""

		#Size Row
		self.thing.AutoSizeRowLabelSize(row)

	def autoTableSizeColumnLabel(self, column, tableNumber):
		"""Sizes the a single column to fit the width of the column label.

		column (int) - The column that will be autosized
							 
		Example Input: autoTableSizeColumnLabel(3, 0)
		"""

		#Size Row
		self.thing.AutoSizeColumnLabelSize(column)

	def setTableRowSize(self, row, size, tableNumber):
		"""Changes the height of a row.

		row (int) - The index of the row
		size (int) - The new height of the row in pixels
		tableNumber (int) - What the table is called in the table catalogue

		Example Input: setTableRowSize(3, 15, 0)
		"""

		#Set the text color
		self.thing.SetRowSize(row, size)

	def setTableColumnSize(self, column, size, tableNumber):
		"""Changes the width of a column.

		column (int) - The index of the column
		size (int) - The new height of the column in pixels
		tableNumber (int) - What the table is called in the table catalogue

		Example Input: setTableColumnSize(3, 15, 0)
		"""

		#Set the text color
		self.thing.SetColSize(column, size)

	def setTableRowSizeDefaults(self, tableNumber):
		"""Restores the default heights to all rows.

		tableNumber (int) - What the table is called in the table catalogue

		Example Input: setTableRowSizeDefaults(0)
		"""

		#Set the text color
		self.thing.SetRowSizes(wx.grid.GridSizesInfo)

	def setTableColumnSizeDefaults(self, tableNumber):
		"""Restores the default widths to all columns.

		tableNumber (int) - What the table is called in the table catalogue

		Example Input: setTableColumnSizeDefaults(0)
		"""

		#Set the text color
		self.thing.SetColSizes(wx.grid.GridSizesInfo)

	#Getters
	def getValue(self):
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

	def onSelectCell(self, event):
		"""Queues the row and column for the user."""
		
		#Get the cell coordinates
		row = event.GetRow()
		column = event.GetCol()

		#Determine which table it is
		thing = self.getObjectWithEvent(event)
		which = -1
		for i, table in enumerate(self.tableDict.keys()):
			if (thing == self.tableDict[table]["thing"]):
				which = i
				break
		if (which != -1):
			self.catalogueTableCurrentCellCoordinates(which, row, column)
		else:
			print("ERROR: Table catalogue error for table", thing)

		event.Skip()

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

	def onTableArrowKeyMove(self, event, tableNumber):
		"""Traverses the cells in the table using the arrow keys."""

		#Get the key that was pressed
		keyCode = event.GetKeyCode()

		#Determine which key was pressed
		if (keyCode == wx.WXK_UP):
			table = self.getTable(tableNumber)
			table.MoveCursorUp(True)

		elif (keyCode == wx.WXK_DOWN):
			table = self.getTable(tableNumber)
			table.MoveCursorDown(True)

		elif (keyCode == wx.WXK_LEFT):
			table = self.getTable(tableNumber)
			table.MoveCursorLeft(True)

		elif (keyCode == wx.WXK_RIGHT):
			table = self.getTable(tableNumber)
			table.MoveCursorRight(True)

		event.Skip()

	def onTableEditOnEnter(self, event, tableNumber):
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
			table = self.getTable(tableNumber)

			# Start the editor
			table.EnableCellEditControl()

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
			table = self.getTable(tableNumber)
			selection = self.getTableCurrentCell(tableNumber)

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
			self.parent = parent.thing
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

			super(TableCellEditor, self).Show(show, attr)

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

			#For this example, select the text
			self.myTextControl.SetSelection(0, self.myTextControl.GetLastPosition())

		def EndEdit(self, row, column, grid, oldValue):
			"""End editing the cell. This function must check if the current
			value of the editing control is valid and different from the
			original value (available as oldValue in its string form.)  If
			it has not changed then simply return None, otherwise return
			the value in its string form.
			*Must Override*
			"""

			#Write debug information
			if (self.debugging):
				print("TableCellEditor.EndEdit(self = {}, row = {}, column = {}, grid = {}, oldValue = {})".format(self, row, column, grid, oldValue))

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

			super(TableCellEditor, self).Destroy()

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

	#Change Settings
	def growFlexColumn(self, column, proportion = 0):
		"""Allows the column to grow as much as it can.

		column (int)      - The column that will expand
		proportion (int)  - How this column will grow compared to other growable columns
							If all are zero, they will grow equally

		Example Input: growFlexColumn(0)
		"""

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

		for column in range(self.thing.GetCols()):
			self.growFlexColumn(column, proportion = proportion)

	def growFlexRowAll(self, proportion = 0):
		"""Allows all the rows to grow as much as they can.

		row (int)      - The row that will expand
		proportion (int)  - How this row will grow compared to other growable rows
							If all are zero, they will grow equally

		Example Input: growFlexRowAll()
		"""

		for row in range(self.thing.GetCols()):
			self.growFlexRow(row, proportion = proportion)
	
	#Etc
	def nest(self, handle = None, flex = 0, flags = "c1"):
		"""Nests an object inside of this Sizer.

		handle (handle) - What to place in this object

		Example Input: nest(text)
		"""

		#Do not nest already nested objects
		if (handle.nested):
			errorMessage = "Cannot nest objects twice"
			raise SyntaxError(errorMessage)

		#Configure Flags
		flags, position, border = self.getItemMod(flags)

		#Perform Nesting
		if (isinstance(handle, handle_Widget_Base)):
			self.thing.Add(handle.thing, int(flex), eval(flags), border)
		
		elif (isinstance(handle, handle_Sizer)):
			self.thing.Add(handle.thing, int(flex), eval(flags), border)
		
		elif (isinstance(handle, handle_Splitter)):
			self.thing.Add(handle.thing, int(flex), eval(flags), border)


		
		else:
			print("Add", handle.__class__, "to handle_Sizer.nestObject()")
			return

		handle.nested = True
		handle.nestingAddress = self.nestingAddress + [id(self)]
		self.setAddressValue(handle.nestingAddress + [id(handle)], {None: handle})

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


		##### wrap_makeWidget #####
		handle = handle_WidgetText()
		##### wrap_makeWidget #####

		##### wrap_addLabel 1 of 2 #####
		handle.label = label
		##### wrap_addLabel 1 of 2 #####

		##### wrap_setParent #####
		if (parent != None):
			handle.parent = parent
		else:
			if (not isinstance(self, Controller)):
				if (self.parent != None):
					handle.parent = self.parent
				else:
					if (self.mainPanel != None):
						handle.parent = self.mainPanel
					else:
						handle.parent = self
		##### wrap_setParent #####

		###### wrap_nestingAddress ######
		handle.nestingAddress = self.nestingAddress + [id(self)]
		self.setAddressValue(handle.nestingAddress + [id(handle)], {None: handle})

		if (not isinstance(self, Controller)):
			self.allowBuildErrors = nestingCatalogue[self.nestingAddress[0]][None].allowBuildErrors
			handle.allowBuildErrors = self.allowBuildErrors
		###### wrap_nestingAddress ######

		##### wrap_setLocation 1 of 2 #####
		handle.sizer = self
		##### wrap_setLocation 1 of 2 #####














		handle.type = "Text"

		#Ensure correct format
		if (not isinstance(text, str)):
			text = str(text)

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

		font = handle.makeFont(size = size, bold = bold, italic = italic, color = color, family = family)
		handle.thing.SetFont(font)

		if (wrap != None):
			if (wrap > 0):
				handle.wrapText(wrap)










		##### wrap_setLocation 2 of 2 #####
		#Add it to the sizer
		handle.sizer.nest(handle, flex = flex, flags = flags)
		##### wrap_setLocation 2 of 2 #####

		##### wrap_addLabel 2 of 2 #####
		if (label != None):
			if (label in self.labelCatalogue):
				warnings.warn("Overwriting label association for {} in ".format(label), Warning, stacklevel = 2)

			self.labelCatalogue[handle.label] = handle
			self.labelCatalogueOrder.append(handle.label)
		else:
			self.unnamedList.append(handle)
		##### wrap_addLabel 2 of 2 #####



		return handle
	
	def addHyperlink(self, text = "", myWebsite = "",

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, 

		label = None, hidden = False, enabled = True, selected = False, 
		flex = 0, flags = "c1", handle = None):
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

		handle.type = "Empty"

		#Create the thing to put in the grid
		handle.thing = wx.StaticText(handle.parent.thing, label = wx.EmptyString)
		handle.wrapText(-1)

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

		handle.type = "Line"
		
		#Apply settings
		if (vertical):
			direction = wx.LI_VERTICAL
		else:
			direction = wx.LI_HORIZONTAL

		#Create the thing to put in the grid
		handle.thing = wx.StaticLine(handle.parent.thing, style = direction)

		return handle

	def addListDrop(self, choices = [], default = None, alphabetic = False,

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, 

		label = None, hidden = False, enabled = True, selected = False, 
		flex = 0, flags = "c1", handle = None):
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
		flex = 0, flags = "c1", handle = None):
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
			handle.thing = ListFull_Editable(handle.parent.thing, style = eval(styleList))
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
			self.betterBind(wx.EVT_LIST_BEGIN_DRAG, handle.thing, self.onDragList_beginDragAway, None, 
				{"label": dragLabel, "deleteOnDrop": dragDelete, "overrideCopy": dragCopyOverride, "allowExternalAppDelete": allowExternalAppDelete,
				"preDragFunction": preDragFunction, "preDragFunctionArgs": preDragFunctionArgs, "preDragFunctionKwargs": preDragFunctionKwargs, 
				"postDragFunction": postDragFunction, "postDragFunctionArgs": postDragFunctionArgs, "postDragFunctionKwargs": postDragFunctionKwargs})

		#Determine if it accepts dropped items
		if (drop):
			dropTarget = DragTextDropTarget(handle.thing, dropIndex,
				preDropFunction = preDropFunction, preDropFunctionArgs = preDropFunctionArgs, preDropFunctionKwargs = preDropFunctionKwargs, 
				postDropFunction = postDropFunction, postDropFunctionArgs = postDropFunctionArgs, postDropFunctionKwargs = postDropFunctionKwargs,
				dragOverFunction = dragOverFunction, dragOverFunctionArgs = dragOverFunctionArgs, dragOverFunctionKwargs = postDropFunctionKwargs)
			handle.thing.SetDropTarget(dropTarget)

		#Bind the function(s)
		# self.betterBind(wx.EVT_LISTBOX, handle.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		if (myFunction != None):
			self.betterBind(wx.EVT_LIST_ITEM_SELECTED, handle.thing, myFunction, myFunctionArgs, myFunctionKwargs)

		if (preEditFunction):
			self.betterBind(wx.EVT_LIST_BEGIN_LABEL_EDIT, handle.thing, preEditFunction, preEditFunctionArgs, preEditFunctionKwargs)
		if (postEditFunction):
			self.betterBind(wx.EVT_LIST_END_LABEL_EDIT, handle.thing, postEditFunction, postEditFunctionArgs, postEditFunctionKwargs)

		return handle

	def addSlider(self, myMin = 0, myMax = 100, myInitial = 0, vertical = False,

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None,

		label = None, hidden = False, enabled = True, selected = False, 
		flex = 0, flags = "c1", handle = None):
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

		return handle
	
	def addInputBox(self, text = None, maxLength = None, 
		password = False, alpha = False, readOnly = False, tab = True, wrap = None, ipAddress = False,
		
		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, 
		enterFunction = None, enterFunctionArgs = None, enterFunctionKwargs = None, 
		postEditFunction = None, postEditFunctionArgs = None, postEditFunctionKwargs = None,  
		preEditFunction = None, preEditFunctionArgs = None, preEditFunctionKwargs = None,  

		label = None, hidden = False, enabled = True, selected = False, 
		flex = 0, flags = "c1", handle = None):
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

		return handle
	
	def addInputSearch(self, text = None, 

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, 
		searchFunction = None, searchFunctionArgs = None, searchFunctionKwargs = None, 
		cancelFunction = None, cancelFunctionArgs = None, cancelFunctionKwargs = None, 

		label = None, hidden = False, enabled = True, selected = False, 
		flex = 0, flags = "c1", handle = None):
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

		return handle
	
	def addInputSpinner(self, myMin = 0, myMax = 100, myInitial = 0, size = wx.DefaultSize, maxSize = None, minSize = None,
		increment = None, digits = None, useFloat = False, readOnly = False,

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, 
		changeTextFunction = True, changeTextFunctionArgs = None, changeTextFunctionKwargs = None,

		label = None, hidden = False, enabled = True, selected = False, 
		flex = 0, flags = "c1", handle = None):
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

		return handle
	
	def addButton(self, text = "", valueLabel = None,

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None,

		label = None, hidden = False, enabled = True, selected = False, 
		flex = 0, flags = "c1", handle = None):
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

		handle.type = "Button"

		#Create the thing to put in the grid
		handle.thing = wx.Button(handle.parent.thing, label = text, style = 0)

		#Bind the function(s)
		self.betterBind(wx.EVT_BUTTON, handle.thing, myFunction, myFunctionArgs, myFunctionKwargs)

		return handle
	
	def addButtonToggle(self, text = "", 

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, 

		label = None, hidden = False, enabled = True, selected = False, 
		flex = 0, flags = "c1", handle = None):
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

		handle.type = "ButtonToggle"
	
		#Create the thing to put in the grid
		handle.thing = wx.ToggleButton(handle.parent.thing, label = text, style = 0)
		handle.thing.SetValue(True) 

		#Bind the function(s)
		self.betterBind(wx.EVT_TOGGLEBUTTON, handle.thing, myFunction, myFunctionArgs, myFunctionKwargs)

		return handle
	
	def addButtonCheck(self, text = "", 

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, default = False,

		label = None, hidden = False, enabled = True, selected = False, 
		flex = 0, flags = "c1", handle = None):
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

		handle.type = "ButtonCheck"

		#Create the thing to put in the grid
		handle.thing = wx.CheckBox(handle.parent.thing, label = text, style = 0)

		#Determine if it is on by default
		handle.thing.SetValue(default)

		#Bind the function(s)
		self.betterBind(wx.EVT_CHECKBOX, handle.thing, myFunction, myFunctionArgs, myFunctionKwargs)

		return handle
	
	def addCheckList(self, choices = [], multiple = True, sort = False,

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, 

		label = None, hidden = False, enabled = True, selected = False, 
		flex = 0, flags = "c1", handle = None):
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

		return handle
	
	def addButtonRadio(self, text = "", groupStart = False, default = False,

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, 

		label = None, hidden = False, enabled = True, selected = False, 
		flex = 0, flags = "c1", handle = None):
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

		return handle
	
	def addButtonRadioBox(self, choices = [], title = "", vertical = False, default = 0, 

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, 

		label = None, hidden = False, enabled = True, selected = False, 
		flex = 0, flags = "c1", handle = None):
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

		return handle
	
	def addButtonImage(self, idlePath = "", disabledPath = "", selectedPath = "", focusPath = "", hoverPath = "",

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, 

		label = None, hidden = False, enabled = True, selected = False, 
		flex = 0, flags = "c1", handle = None):
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

		return handle
	
	def addImage(self, imagePath = "", internal = False, size = wx.DefaultSize,

		label = None, hidden = False, enabled = True, selected = False, 
		flex = 0, flags = "c1", handle = None):
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

		handle.type = "Image"

		#Get correct image
		image = self.getImage(imagePath, internal)
	
		#Create the thing to put in the grid
		handle.thing = wx.StaticBitmap(handle.parent.thing, bitmap = image, size = size, style = 0)

		return handle
	
	def addProgressBar(self, myInitial = 0, myMax = 100, vertical = False,

		label = None, hidden = False, enabled = True, selected = False, 
		flex = 0, flags = "c1", handle = None):
		"""Adds progress bar to the next cell on the grid.

		myInitial (int)         - The value that the progress bar starts at
		myMax (int)             - The value that the progress bar is full at
		flags (list)            - A list of strings for which flag to add to the sizer
		label (any)           - What this is catalogued as

		Example Input: addProgressBar(0, 100)
		"""

		handle.type = "ProgressBar"

		if (vertical):
			styles = wx.GA_HORIZONTAL
		else:
			styles = wx.GA_VERTICAL
	
		#Create the thing to put in the grid
		handle.thing = wx.Gauge(handle.parent.thing, range = myMax, style = styles)

		#Set Initial Conditions
		handle.thing.SetValue(myInitial)

		return handle
	
	def addPickerColor(self, addInputBox = False, colorText = False, initial = None,

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, 

		label = None, hidden = False, enabled = True, selected = False, 
		flex = 0, flags = "c1", handle = None):
		"""Adds a color picker to the next cell on the grid.
		It can display the name or RGB of the color as well.

		myFunction (str)        - What function will be ran when the color is chosen
		flags (list)            - A list of strings for which flag to add to the sizer
		label (any)           - What this is catalogued as
		myFunctionArgs (any)    - The arguments for 'myFunction'
		myFunctionKwargs (any)  - The keyword arguments for 'myFunction'function

		Example Input: addPickerColor(label = "changeColor")
		"""

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

		return handle
	
	def addPickerFont(self, maxSize = 72, fontText = False, addInputBox = False,

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, 

		label = None, hidden = False, enabled = True, selected = False, 
		flex = 0, flags = "c1", handle = None):
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

		return handle
	
	def addPickerFile(self, text = "Select a File", default = "", initialDir = "*.*", 
		directoryOnly = False, changeCurrentDirectory = False, fileMustExist = False, openFile = False, 
		saveConfirmation = False, saveFile = False, smallButton = False, addInputBox = False, 

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None,

		label = None, hidden = False, enabled = True, selected = False, 
		flex = 0, flags = "c1", handle = None):
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

		return handle
	
	def addPickerFileWindow(self, initialDir = "*.*", 
		directoryOnly = True, selectMultiple = False, showHidden = True,

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, 
		editLabelFunction = None, editLabelFunctionArgs = None, editLabelFunctionKwargs = None, 
		rightClickFunction = None, rightClickFunctionArgs = None, rightClickFunctionKwargs = None, 

		label = None, hidden = False, enabled = True, selected = False, 
		flex = 0, flags = "c1", handle = None):
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

		return handle
	
	def addPickerTime(self, time = None,

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, 

		label = None, hidden = False, enabled = True, selected = False, 
		flex = 0, flags = "c1", handle = None):
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

		return handle
	
	def addPickerDate(self, date = None, dropDown = False, 

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, 

		label = None, hidden = False, enabled = True, selected = False, 
		flex = 0, flags = "c1", handle = None):
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

		return handle
	
	def addPickerDateWindow(self, date = None, showHolidays = False, showOther = False,
		
		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, 
		dayFunction = None, dayFunctionArgs = None, dayFunctionKwargs = None, 
		monthFunction = None, monthFunctionArgs = None, monthFunctionKwargs = None, 
		yearFunction = None, yearFunctionArgs = None, yearFunctionArgsKwargs = None, 

		label = None, hidden = False, enabled = True, selected = False, 
		flex = 0, flags = "c1", handle = None):
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
		flex = 0, flags = "c1", handle = None):

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
		myLabel (str)     - What this is called in the idCatalogue
		
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
		handle.thing.readOnlyCatalogue = {}
		for row in range(handle.thing.GetNumberRows()):
			for column in range(handle.thing.GetNumberCols()):
				if (readOnly != None):
					if (row not in handle.thing.readOnlyCatalogue):
						handle.thing.readOnlyCatalogue[row] = {}
					if (column not in handle.thing.readOnlyCatalogue[row]):
						handle.thing.readOnlyCatalogue[row][column] = {}

					if (type(readOnly) == bool):
						handle.thing.readOnlyCatalogue[row][column] = readOnly
					else:
						if (row in readOnly):
							#Account for whole row set
							if (type(readOnly[row]) == bool):
								handle.thing.readOnlyCatalogue[row][column] = readOnly[row]
							else:
								if (column in readOnly[row]):
									handle.thing.readOnlyCatalogue[row][column] = readOnly[row][column]
								else:
									handle.thing.readOnlyCatalogue[row][column] = readOnlyDefault

						elif (None in readOnly):
							#Account for whole column set
							if (column in readOnly[None]):
								handle.thing.readOnlyCatalogue[row][column] = readOnly[None][column]
							else:
								handle.thing.readOnlyCatalogue[row][column] = readOnlyDefault
						else:
							handle.thing.readOnlyCatalogue[row][column] = readOnlyDefault
				else:
					handle.thing.readOnlyCatalogue[row][column] = readOnlyDefault

		##Default Cell Selection
		if ((default != None) and (default != (0, 0))):
			handle.thing.GoToCell(default[0], default[1])

		##Cell Editor
		editor = handle.TableCellEditor(self, downOnEnter = enterKeyExitEdit)
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
			self.betterBind(wx.grid.EVT_GRID_SELECT_CELL, handle.thing, [handle.onSelectCell, selectSingleFunction], [None, selectSingleFunctionArgs], [None, selectSingleFunctionKwargs])
		else:
			self.betterBind(wx.grid.EVT_GRID_SELECT_CELL, handle.thing, handle.onSelectCell, selectSingleFunctionArgs, selectSingleFunctionKwargs)
		
		if (rightClickCellFunction != None):
			self.betterBind(wx.grid.EVT_GRID_CELL_RIGHT_CLICK, handle.thing, rightClickCellFunction, rightClickCellFunctionArgs, rightClickCellFunctionKwargs)
		if (rightClickLabelFunction != None):
			self.betterBind(wx.grid.EVT_GRID_CELL_RIGHT_CLICK, handle.thing, rightClickLabelFunction, rightClickLabelFunctionArgs, rightClickLabelFunctionKwargs)

		if (toolTips != None):
			self.betterBind(wx.EVT_MOTION, handle.thing, handle.onTableDisplayToolTip, toolTips)
		if (arrowKeyExitEdit):
			self.betterBind(wx.EVT_KEY_DOWN, handle.thing, handle.onTableArrowKeyMove, mode = 2)
		if (editOnEnter):
			self.betterBind(wx.EVT_KEY_DOWN, handle.thing.GetGridWindow(), handle.onTableEditOnEnter, tableNumber, mode = 2)

		return handle

	#Splitters
	def addSplitterDouble(self, sizer_0 = {}, sizer_1 = {},

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

		handle.type = "Double"

		#Create the panel splitter
		handle.thing = wx.SplitterWindow(handle.parent.thing, style = wx.SP_LIVE_UPDATE)

		#Add panels and sizers to splitter
		for i in range(2):
			#Add panels to the splitter
			handle.panelList.append(self.myWindow.addPanel(parent = handle, border = "raised"))
			handle.panelList[i].nested = True

			#Add sizers to the panel
			if ("sizer_{}".format(i) in locals()):
				sizerInstructions = locals()[("sizer_{}".format(i))]
			else:
				sizerInstructions = {}
			sizer = handle.readBuildInstructions(self, i, sizerInstructions)

			handle.sizerList.append(sizer)
			handle.panelList[i].thing.SetSizer(sizer.thing)
			handle.sizerList[i].nested = True

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

		return handle

	def addSplitterQuad(self, sizer_0 = {}, sizer_1 = {}, sizer_2 = {}, sizer_3 = {},

		initFunction = None, initFunctionArgs = None, initFunctionKwargs = None,

		myLabel = None, handle = None):
		"""Creates four blank panels next to each other like a grid.
		The borders between quad panels are dragable. The itersection point is also dragable.
		The panel order is top left, top right, bottom left, bottom right.
		
		border (str)          - What style the border has. "simple", "raised", "sunken" or "none". Only the first two letters are necissary
		useDefaultSize (bool) - If True: The xSize and ySize will be overridden to fit as much of the widgets as it can. Will lock the panel size from re-sizing
		myLabel (str)          - What this is called in the idCatalogue
		
		initFunction (str)       - The function that is ran when the panel first appears
		initFunctionArgs (any)   - The arguments for 'initFunction'
		initFunctionKwargs (any) - The keyword arguments for 'initFunction'function
		tabTraversal (bool)      - If True: Hitting the Tab key will move the selected widget to the next one

		Example Input: addSplitterQuad()
		"""

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
			handle.panelList[i].thing.SetSizer(sizer.thing)
			handle.sizerList[i].nested = True

		#Create the panel splitter
		handle.thing = wx.lib.agw.fourwaysplitter.FourWaySplitter(handle.parent.thing, agwStyle = wx.SP_LIVE_UPDATE)

		#Bind Functions
		if (initFunction != None):
			self.betterBind(wx.EVT_INIT_DIALOG, handle.thing, initFunction, initFunctionArgs, initFunctionKwargs)

		return handle

	def addSplitterPoly(self, panelNumbers, sizers = {},
		dividerSize = 1, dividerPosition = None, dividerGravity = 0.5, vertical = False, minimumSize = 20, 

		initFunction = None, initFunctionArgs = None, initFunctionKwargs = None,

		myLabel = None, handle = None):
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
		myLabel (str)          - What this is called in the idCatalogue
		
		initFunction (str)       - The function that is ran when the panel first appears
		initFunctionArgs (any)   - The arguments for 'initFunction'
		initFunctionKwargs (any) - The keyword arguments for 'initFunction'function
		tabTraversal (bool)      - If True: Hitting the Tab key will move the selected widget to the next one

		Example Input: addSplitterQuad([0, 1, 2, 3], 0)
		Example Input: addSplitterQuad([0, 1, 2, 3], 0, panelSizes = [(200, 300), (300, 300), (100, 300)])
		Example Input: addSplitterQuad([0, 1, 2, 3], 0, horizontal = False)
		Example Input: addSplitterQuad([0, 1, 2, 3], 0, minimumSize = 100)
		"""

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
			handle.panelList[i].thing.SetSizer(sizer.thing)
			handle.sizerList[i].nested = True

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

		return handle

	#Overloads
	def addSizerBox(self, *args, **kwargs):
		"""Overload for addSizerBox in handle_Window().
		Adds the created sizer to this sizer.
		"""

		myFrame = self.myWindow
		handle = myFrame.addSizerBox(*args, parent = self.parent, **kwargs)
		self.nest(handle)

		return handle

	def addSizerText(self, *args, **kwargs):
		"""Overload for addSizerText in handle_Window().
		Adds the created sizer to this sizer.
		"""

		myFrame = self.myWindow
		handle = myFrame.addSizerText(*args, parent = self.parent, **kwargs)
		self.nest(handle)

		return handle

	def addSizerGrid(self, *args, **kwargs):
		"""Overload for addSizerGrid in handle_Window().
		Adds the created sizer to this sizer.
		"""

		myFrame = self.myWindow
		handle = myFrame.addSizerGrid(*args, parent = self.parent, **kwargs)
		self.nest(handle)

		return handle

	def addSizerGridFlex(self, *args, **kwargs):
		"""Overload for addSizerGridFlex in handle_Window().
		Adds the created sizer to this sizer.
		"""

		myFrame = self.myWindow
		handle = myFrame.addSizerGridFlex(*args, parent = self.parent, **kwargs)
		self.nest(handle)

		return handle

	def addSizerGridBag(self, *args, **kwargs):
		"""Overload for addSizerGridBag in handle_Window().
		Adds the created sizer to this sizer.
		"""

		myFrame = self.myWindow
		handle = myFrame.addSizerGridBag(*args, parent = self.parent, **kwargs)
		self.nest(handle)

		return handle

	def addSizerWrap(self, *args, **kwargs):
		"""Overload for addSizerWrap in handle_Window().
		Adds the created sizer to this sizer.
		"""

		myFrame = self.myWindow
		handle = myFrame.addSizerWrap(*args, parent = self.parent, **kwargs)
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
		self.menubar = None

		self.finalFunctionList = []
		self.sizersIterating = {} #Keeps track of which sizers have been used in a while loop, as well as if they are still in the while loop {sizer (handle): [currently in a while loop (bool), order entered (int)]}

	def __str__(self):
		"""Gives diagnostic information on the Window when it is printed out."""

		output = handle_Container_Base.__str__(self)
		
		if (self.mainPanel != None):
			output += "-- main panel id: {}\n".format(id(self.mainPanel))
		return output

	#Change Settings
	def setWindowSize(self, x, y):
		"""Re-defines the size of the window.

		x (int)     - The width of the window
		y (int)     - The height of the window

		Example Input: setWindowSize(350, 250)
		"""

		#Change the frame size
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

		if (self.visible * notShown):
			return False
		return True

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
			shownWindowsList.remove(self)
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

		##### wrap_makePanel #####
		handle = handle_Panel()

		if (isinstance(self, handle_Window)):
			panelList = self.getNested(include = handle_Panel)
			if (len(panelList) == 0):
				#The first panel added to a window is automatically nested
				handle.nested = True
		##### wrap_makePanel #####

		##### wrap_addLabel 1 of 2 #####
		handle.label = label
		##### wrap_addLabel 1 of 2 #####

		##### wrap_setParent #####
		if (parent != None):
			handle.parent = parent
		else:
			if (not isinstance(self, Controller)):
				if (self.parent != None):
					handle.parent = self.parent
				else:
					if (self.mainPanel != None):
						handle.parent = self.mainPanel
					else:
						handle.parent = self
		##### wrap_setParent #####

		###### wrap_nestingAddress ######
		handle.nestingAddress = self.nestingAddress + [id(self)]
		self.setAddressValue(handle.nestingAddress + [id(handle)], {None: handle})

		if (not isinstance(self, Controller)):
			self.allowBuildErrors = nestingCatalogue[self.nestingAddress[0]][None].allowBuildErrors
			handle.allowBuildErrors = self.allowBuildErrors
		###### wrap_nestingAddress ######













		#Determine border
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

		#Determine size
		if (useDefaultSize):
			size = wx.DefaultSize

		#Get Attributes
		flags = self.getItemMod(flags, False, None)[0]

		if (tabTraversal):
			flags += "|wx.TAB_TRAVERSAL"

		#Create the panel
		handle.thing = wx.Panel(handle.parent.thing, id = wx.ID_ANY, pos = position, size = size, style = eval(border + "|" + flags))

		handle.autoSize = autoSize

		#Bind Functions
		if (initFunction != None):
			self.betterBind(wx.EVT_INIT_DIALOG, handle.thing, initFunction, initFunctionArgs, initFunctionKwargs)




		##### wrap_addLabel 2 of 2 #####
		if (label != None):
			if (label in self.labelCatalogue):
				warnings.warn("Overwriting label association for {} in ".format(label), Warning, stacklevel = 2)

			self.labelCatalogue[handle.label] = handle
			self.labelCatalogueOrder.append(handle.label)
		else:
			self.unnamedList.append(handle)
		##### wrap_addLabel 2 of 2 #####











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

	def addSizerGrid(self, label = None, rows = 1, columns = 1, 
		rowGap = 0, colGap = 0, minWidth = -1, minHeight = -1, 

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

		handle.type = "Grid"

		#Create Sizer
		handle.thing = wx.GridSizer(rows, columns, rowGap, colGap)

		return handle

	def addSizerGridFlex(self, label = None, rows = 1, columns = 1, rowGap = 0, colGap = 0, 
		minWidth = -1, minHeight = -1, flexGrid = True, 

		parent = None, hidden = False, vertical = None, handle = None):
		"""Creates a flex grid sizer.
		############## NEEDS TO BE FIXED #################

		label (any)     - What this is catalogued as
		rows (int)        - The number of rows that the grid has
		columns (int)     - The number of columns that the grid has
		rowGap (int)      - Empyt space between each row
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

		handle.type = "Flex"

		#Create Sizer
		handle.thing = wx.FlexGridSizer(rows, columns, rowGap, colGap)
		handle.thing.SetFlexibleDirection(handle.direction)

		#Determine if flexability specifications
		# if (flexGrid):
		# 	handle.thing.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)
		# else:
		# 	handle.thing.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_NONE)

		return handle

	def addSizerGridBag(self, label = None, rows = 1, columns = 1, rowGap = 0, colGap = 0, minWidth = -1, minHeight = -1, 
		emptySpace = None, flexGrid = True, 

		parent = None, hidden = False, vertical = None, handle = None):
		"""Creates a bag grid sizer.

		label (any)      - What this is catalogued as
		rows (int)         - The number of rows that the grid has
		columns (int)      - The number of columns that the grid has
		rowGap (int)       - Empyt space between each row
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

		handle.type = "Bag"

		#Create Sizer
		handle.thing = wx.GridBagSizer(rows, columns, rowGap, colGap)
		
		handle.thing.SetFlexibleDirection(handle.direction)

		if (flexGrid):
			handle.thing.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)
		else:
			handle.thing.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_NONE)

		if (emptySpace != None):
			handle.thing.SetEmptyCellSize(emptySpace)

		return handle

	def addSizerBox(self, label = None, minWidth = -1, minHeight = -1, 

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

		##### wrap_makeSizer #####
		handle = handle_Sizer()
		handle.myWindow = self

		if (isinstance(self, handle_Window)):
			sizerList = self.getNested(include = handle_Sizer)
			if (len(sizerList) == 0):
				#The first sizer added to a window is automatically nested
				handle.nested = True

		##### wrap_makeSizer #####

		##### wrap_addLabel 1 of 2 #####
		handle.label = label
		##### wrap_addLabel 1 of 2 #####

		##### wrap_setParent #####
		if (parent != None):
			handle.parent = parent
		else:
			if (not isinstance(self, Controller)):
				if (self.parent != None):
					handle.parent = self.parent
				else:
					if (self.mainPanel != None):
						handle.parent = self.mainPanel
					else:
						handle.parent = self
		##### wrap_setParent #####

		###### wrap_nestingAddress ######
		handle.nestingAddress = self.nestingAddress + [id(self)]
		self.setAddressValue(handle.nestingAddress + [id(handle)], {None: handle})

		if (not isinstance(self, Controller)):
			self.allowBuildErrors = nestingCatalogue[self.nestingAddress[0]][None].allowBuildErrors
			handle.allowBuildErrors = self.allowBuildErrors
		###### wrap_nestingAddress ######

		##### wrap_setDirection #####
		if (vertical == None):
			handle.direction = wx.BOTH
		elif (vertical):
			handle.direction = wx.VERTICAL
		else:
			handle.direction = wx.HORIZONTAL
		##### wrap_setDirection #####
















		handle.type = "Box"

		handle.thing = wx.BoxSizer(handle.direction)








		##### wrap_setState_hidden #####
		if (hidden):
			if (isinstance(self, handle_Sizer)):
				self.addFinalFunction(handle.thing.ShowItems, False)
			else:
				handle.thing.Hide()
		##### wrap_setState_hidden #####

		##### wrap_addLabel 2 of 2 #####
		if (label != None):
			if (label in self.labelCatalogue):
				warnings.warn("Overwriting label association for {} in ".format(label), Warning, stacklevel = 2)

			self.labelCatalogue[handle.label] = handle
			self.labelCatalogueOrder.append(handle.label)
		else:
			self.unnamedList.append(handle)
		##### wrap_addLabel 2 of 2 #####





		return handle

	def addSizerText(self, label = None, text = "", minWidth = -1, minHeight = -1, 

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

		handle.type = "Text"

		handle.thing = wx.StaticBoxSizer(wx.StaticBox(handle.parent.thing, wx.ID_ANY, text), handle.direction)

		return handle

	def addSizerWrap(self, label = None, minWidth = -1, minHeight = -1, 
		extendLast = False, 

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

		handle.type = "Wrap"

		#Setup flags
		if (extendLast):
			flags = "wx.EXTEND_LAST_ON_EACH_LINE"
		else:
			flags = "wx.WRAPSIZER_DEFAULT_FLAGS"

		#Create Sizer
		handle.thing = wx.WrapSizer(handle.direction, eval(flags))

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

		self.menubar = wx.MenuBar()
		self.thing.SetMenuBar(self.menubar)

	def addMenu(self, label = None, text = " ", detachable = False,

		parent = None, hidden = False, handle = None):
		"""Adds a menu to a pre-existing menubar.
		This is a collapsable array of menu items.

		text (str)        - What the menu is called
			If you add a '&', a keyboard shortcut will be made for the letter after it
		myLabel (str)     - What this is called in the idCatalogue
		detachable (bool) - If True: The menu can be undocked

		Example Input: addMenu(0, "&File")
		Example Input: addMenu("first", "&File")
		"""

		#Create menu
		if (detachable):
			handle.thing = wx.Menu(wx.MENU_TEAROFF)
		else:
			handle.thing = wx.Menu()

		handle.text = text

		return handle

	#Etc
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

class handle_Splitter(handle_Container_Base):
	"""A handle for working with a wxSplitter."""

	def __init__(self):
		"""Initializes defaults."""

		#Initialize inherited classes
		handle_Container_Base.__init__(self)

		self.complexity = 5
		self.sizerList = []
		self.panelList = []

	def __str__(self):
		"""Gives diagnostic information on the Splitter when it is printed out."""

		output = handle_Container_Base.__str__(self)
		return output

	def getSizers(self):
		"""Returns the internal sizer list."""

		return self.sizerList

	def readBuildInstructions(self, parent, i, instructions):
		"""Interprets instructions given by the user for what sizer to make and how to make it."""

		if (not isinstance(instructions, dict)):
			errorMessage = "sizer_{} must be a dictionary for {}".format(i, self.__repr__())
			raise ValueError(errorMessage)

		if (len(instructions) == 0):
			sizer = parent.myWindow.addSizerBox(parent = self.panelList[i])
		else:
			if ("type" not in instructions):
				errorMessage = "Must supply which sizer type to make. The key should be 'type'. The value should be 'Grid', 'Flex', 'Bag', 'Box', 'Text', or 'Wrap'"
				raise ValueError(errorMessage)

			sizerType = instructions["type"].lower()
			if (sizerType not in ["grid", "flex", "bag", "box", "text", "wrap"]):
				errorMessage = "There is no 'type' {}. The value should be be 'Grid', 'Flex', 'Bag', 'Box', 'Text', or 'Wrap'".format(instructions["type"])
				raise KeyError(errorMessage)

			if (sizerType == "grid"):
				sizerFunction = parent.myWindow.addSizerGrid
			elif (sizerType == "flex"):
				sizerFunction = parent.myWindow.addSizerGridFlex
			elif (sizerType == "bag"):
				sizerFunction = parent.myWindow.addSizerGridBag
			elif (sizerType == "box"):
				sizerFunction = parent.myWindow.addSizerBox
			elif (sizerType == "text"):
				sizerFunction = parent.myWindow.addSizerText
			elif (sizerType == "wrap"):
				sizerFunction = parent.myWindow.addSizerWrap

			del instructions["type"]

			instructions["parent"] = self.panelList[i]

			sizer = sizerFunction(**instructions)

		return sizer

class handle_Notebook(handle_Container_Base):
	"""A handle for working with a wxNotebook."""

	def __init__(self):
		"""Initializes defaults."""

		#Initialize inherited classes
		handle_Container_Base.__init__(self)

	def __str__(self):
		"""Gives diagnostic information on the Notebook when it is printed out."""

		output = handle_Container_Base.__str__(self)
		return output

#Classes
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
	def onHide(self, event):
		"""Hides the window. Default of a hide (h) menu item."""

		self.Hide()
		#There is no event.Skip() because if not, then the window will destroy itself

	def onQuit(self, event):
		"""Closes the window. Default of a close (c) menu item."""

		self.Destroy()
		event.Skip()

	def onExit(self, event):
		"""Closes all windows. Default of a quit (q) or exit (e) menu item."""

		#Make sure sub threads are closed
		if (threading.active_count() > 1):
			for thread in threading.enumerate():
				#Close the threads that are not the main thread
				if (thread != threading.main_thread()):
					thread.stop()

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

class Controller(Utilities, CommonEventFunctions):
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

		#Setup Internal Variables
		self.labelCatalogue = {} #A dictionary that contains all the windows made for the gui. {windowLabel: myFrame}
		self.labelCatalogueOrder = [] #A list of what order things were added to teh label catalogue. [windowLabel 1, windowLabel 2]
		self.unnamedList = [] #A list of the windows created without labels
		self.oneInstance = oneInstance #Allows the user to run only one instance of this gui at a time
		self.allowBuildErrors = allowBuildErrors
		self.nestingAddress = []
		self.nested = True
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
	
	#Main Objects
	def addWindow(self, label = None, title = "", xSize = 500, ySize = 300, panel = True, autoSize = True,
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

		##### wrap_makeWindow 1 of 2 #####
		handle = handle_Window()
		handle.nested = True
		##### wrap_makeWindow 1 of 2 #####

		##### wrap_addLabel 1 of 2 #####
		handle.label = label
		##### wrap_addLabel 1 of 2 #####

		##### wrap_setParent #####
		if (parent != None):
			handle.parent = parent
		else:
			if (not isinstance(self, Controller)):
				if (self.parent != None):
					handle.parent = self.parent
				else:
					if (self.mainPanel != None):
						handle.parent = self.mainPanel
					else:
						handle.parent = self
		##### wrap_setParent #####

		###### wrap_nestingAddress ######
		handle.nestingAddress = self.nestingAddress + [id(self)]
		self.setAddressValue(handle.nestingAddress + [id(handle)], {None: handle})

		if (not isinstance(self, Controller)):
			self.allowBuildErrors = nestingCatalogue[self.nestingAddress[0]][None].allowBuildErrors
			handle.allowBuildErrors = self.allowBuildErrors
		###### wrap_nestingAddress ######











		#Determine window style
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

		handle.autoSize = autoSize

		#Make the frame
		handle.thing = wx.Frame(None, id = wx.ID_ANY, title = title, pos = wx.DefaultPosition, size = (xSize, ySize), style = eval(flags))
		
		#Add Properties
		if (icon != None):
			self.setIcon(icon, internal)

		#Bind functions
		if (initFunction != None):
			self.betterBind(wx.EVT_ACTIVATE, handle.thing, initFunction, initFunctionArgs, initFunctionKwargs)

		if (delFunction != None):
			self.betterBind(wx.EVT_CLOSE, handle.thing, delFunction, delFunctionArgs, delFunctionKwargs)
		else:
			if (endProgram != None):
				if (endProgram):
					delFunction = self.onExit
				else:
					delFunction = self.onQuit
			else:
				delFunction = self.onHide

			self.betterBind(wx.EVT_CLOSE, handle.thing, delFunction)

		if (idleFunction != None):
			self.idleQueue = None
			self.betterBind(wx.EVT_IDLE, handle.thing, idleFunction, idleFunctionArgs, idleFunctionKwargs)
		else:
			self.betterBind(wx.EVT_IDLE, handle.thing, self.onIdle)












		##### wrap_makeWindow 2 of 2 #####
		if (panel):
			handle.mainPanel = handle.addPanel()#"-1", parent = handle, size = (10, 10), tabTraversal = tabTraversal, useDefaultSize = False)
		##### wrap_makeWindow 2 of 2 #####


		##### wrap_addLabel 2 of 2 #####
		if (label != None):
			if (label in self.labelCatalogue):
				warnings.warn("Overwriting label association for {} in ".format(label), Warning, stacklevel = 2)

			self.labelCatalogue[handle.label] = handle
			self.labelCatalogueOrder.append(handle.label)
		else:
			self.unnamedList.append(handle)
		##### wrap_addLabel 2 of 2 #####

		return handle

	#Logistic Functions
	def finish(self):
		"""Run this when the GUI is finished."""
		global nestingCatalogue

		def nestCheck(catalogue):
			"""Makes sure everything is nested."""

			valueList = [item for item in catalogue.values() if isinstance(item, dict)]
			
			for item in catalogue.values():
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

			# #Check for any window key bindings that need to happen
			# if (len(myFrame.keyPressQueue) > 0):
			# 	#Bind each key event to the window
			# 	acceleratorTableQueue = []
			# 	### To Do: This does not currently work with more than 1 key. Find out what is wrong. ###
			# 	for thing, queue in myFrame.keyPressQueue.items():
			# 		for key, contents in queue.items():

			# 			#Bind the keys to the window
			# 			### This is likely the issue. The event seems to be 'overwritten' by the next key ###
			# 			myId = myFrame.newId()
			# 			# myId = self.thing.GetId()
			# 			# myFrame.Bind(wx.EVT_MENU, contents[0], id=myId)
			# 			# myFrame.Bind(type, lambda event: handler(event, *args, **kwargs), instance)
			# 			# print(contents[0])
			# 			# myFrame.Bind(wx.EVT_MENU, lambda event: contents[0](event), id=eventId)
			# 			# myFrame.Bind(wx.EVT_MENU, lambda event: contents[0](event), id = myId)
			# 			myFrame.betterBind(wx.EVT_MENU, myFrame, contents[0], contents[1], contents[2], myId = myId, mode = 2)
			# 			# asciiValue = myFrame.keyBind(key, thing, contents[0], myFunctionArgsList = contents[1], myFunctionKwargsList = contents[2], event = wx.EVT_MENU, myId = myId)

			# 			#Add to accelerator Table
			# 			acceleratorTableQueue.append((wx.ACCEL_CTRL, 83, myId))

			# 	acceleratorTable = wx.AcceleratorTable(acceleratorTableQueue)
			# 	myFrame.SetAcceleratorTable(acceleratorTable)

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

	#Overloads
	def getWindow(self, windowLabel):
		"""Returns a window object when given the corresponding frame number.

		windowLabel (any) - The label for the desired window
			- If None: Returns whole window list

		Example Input: getWindow(0)
		Example Input: getWindow("test")
		"""

		if (windowLabel != None):
			if (windowLabel not in self.labelCatalogue):
				errorMessage = "There is no window labeled {} for {}".format(windowLabel, self.__repr__())
				raise KeyError(errorMessage)

			myFrame = self.labelCatalogue[windowLabel]
		else:
			myFrame = list(self.labelCatalogue.values()) + self.unnamedList

		return myFrame

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
		else:
			frameFrom.closeWindow()

	def onSwitchWindow(self, event, *args, **kwargs):
		"""Event function for switchWindow()."""

		self.switchWindow(*args, **kwargs)			
		event.Skip()

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
		"""Overload for growFlexRowAll in handle_Window()."""

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

def main_14():
	"""The program controller. """

	gui = build()
	myFrame = gui.addWindow(title = "created")#, panel = None)
	mySizer_1 = myFrame.addSizerBox()
	mySizer_1.addText("Lorem")

	with mySizer_1.addSizerBox() as mySizer:
		mySizer.addText("Ipsum")

	with mySizer_1.addSizerBox() as mySizer:
		mySizer.addText("Dolor 1")

	with mySizer_1.addSizerBox() as mySizer:
		mySizer.addText("Dolor 2")

	with mySizer_1.addSizerBox() as mySizer:
		mySizer.addText("Dolor 3")

	with mySizer_1.addSizerBox() as mySizer:
		mySizer.addText("Dolor 4")

	with mySizer_1.addSizerBox() as mySizer:
		mySizer.addText("Dolor 5")

	with mySizer_1.addSizerBox() as mySizer:
		mySizer.addText("Dolor 6")

	with mySizer_1.addSizerBox() as mySizer:
		mySizer.addText("Dolor 7")

	with mySizer_1.addSizerBox() as mySizer:
		mySizer.addText("Sit")

	# with mySizer_1.addSizerBox() as mySizer:
	# 	mySizer.addText("Ipsum")

	# with mySizer_1.addSizerBox() as mySizer:
	# 	mySizer.addText("Ipsum")

	# mySizer_1.addSplitterDouble(minimumSize = 200)
	# mySizer_1.addSplitterDouble(minimumSize = 200)
	# mySizer_1.addSplitterDouble(minimumSize = 200)
	# mySizer_1.addSplitterDouble(minimumSize = 200)
	# mySizer_1.addSplitterDouble(minimumSize = 200)
	# mySizer_1.addSplitterDouble(minimumSize = 200)
	# mySizer_1.addSplitterDouble(minimumSize = 200)

	myFrame.showWindow()
	print("GUI Finished")
	gui.finish()

if __name__ == '__main__':
	main_14()
