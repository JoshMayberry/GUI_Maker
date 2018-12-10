__version__ = "4.3.0"

#TO DO
# - Add File Drop: https://www.blog.pythonlibrary.org/2012/06/20/wxpython-introduction-to-drag-and-drop/
# - Add Wrap Sizer: https://www.blog.pythonlibrary.org/2014/01/22/wxpython-wrap-widgets-with-wrapsizer/
# - Look through these demos for more things: https://github.com/wxWidgets/Phoenix/tree/master/demo
# - Look through the menu examples: https://www.programcreek.com/python/example/44403/wx.EVT_FIND
# - Add https://wxpython.org/Phoenix/docs/html/wx.MDIParentFrame.html; use: https://stackoverflow.com/questions/46999890/display-html-using-a-wxpython-control
# - Add https://wxpython.org/Phoenix/docs/html/wx.ConfigBase.html#wx.ConfigBase
# https://wxpython.org/Phoenix/docs/html/wx.lib.agw.html
# https://wxpython.org/Phoenix/docs/html/wx.html2.WebView.html

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
import enum
import time
import math
import copy
import types
import bisect
import ctypes
import string
import operator
# import builtins

import typing #NoReturn, Union
import inspect
import warnings
import traceback
import functools
import contextlib

import anytree

#Import wxPython elements to create GUI
import wx
import wx.adv
import wx.grid
import wx.html
import wx.lib.masked
import wx.lib.buttons
import wx.lib.dialogs
import wx.lib.agw.aui
import wx.lib.newevent
import wx.lib.wordwrap
import wx.lib.splitter
import wx.lib.agw.flatmenu
import wx.lib.agw.floatspin
import wx.lib.scrolledpanel
import wx.lib.mixins.listctrl
import wx.lib.agw.multidirdialog
import wx.lib.agw.fourwaysplitter
import wx.lib.agw.ultimatelistctrl
import wx.lib.agw.genericmessagedialog
import forks.objectlistview.ObjectListView as ObjectListView #Use my own fork

#Import matplotlib elements to add plots to the GUI
# import matplotlib
# matplotlib.use('WXAgg')
# matplotlib.get_py2exe_datafiles()
# import matplotlib.pyplot as plt
# from matplotlib.backends.backend_wxagg import FigureCanvas


#Import modules needed to print RAW
# import win32print


#Import multi-threading to run functions as background processes
import queue
import threading
import subprocess
# import pubsub.pub
from forks.pypubsub.src.pubsub import pub as pubsub_pub #Use my own fork


#Import needed support modules
import re
import PIL

import Utilities as MyUtilities

if (__name__ == "__main__"):
	import LICENSE_forSections as Legal
	import ExceptionHandling
else:
	from . import LICENSE_forSections as Legal
	from . import ExceptionHandling

#Required Modules
##py -m pip install
	# wxPython
	# pillow
	# pypubsub
	# objectlistview
	# anytree

#Maybe Required Modules?
	# numpy
	# matplotlib

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
topicManager = pubsub_pub.getDefaultTopicMgr()

NULL = object()

#Get all event names
#See: https://www.blog.pythonlibrary.org/2011/07/05/wxpython-get-the-event-name-instead-of-an-integer/
# eventCatalogue = {}
# for module_name, module in tuple(sys.modules.items()):
# 	if (module_name.startswith("wx")):
# 		if (module_name == "wx.core"):
# 			module_name = "wx"
# 		for name in dir(module):
# 			if (name.startswith('EVT_')):
# 				event = getattr(module, name)
# 				if (isinstance(event, wx.PyEventBinder)):
# 					eventCatalogue[event.typeId] = (name, f"{module_name}.{name}", eval(f"{module_name}.{name}"))

#Controllers
def build(*args, **kwargs):
	"""Starts the GUI making process."""
	# global myEventCatalogue, MyEvent
	global Controller

	# #Give custom events an event binder
	# myEventCatalogue.clear()
	# for subclass in MyEvent.__subclasses__():
	# 	subclass.makeBinder()

	return Controller(*args, **kwargs)

#Enumerations
class Types(enum.IntEnum):
	empty = enum.auto()
	line = enum.auto()

	box = enum.auto()
	grid = enum.auto()
	flex = enum.auto()
	wrap = enum.auto()
	bag = enum.auto()

	text = enum.auto()
	html = enum.auto()
	hyperlink = enum.auto()

	drop = enum.auto()
	view = enum.auto()
	tree = enum.auto()

	slider = enum.auto()
	search = enum.auto()
	spinner = enum.auto()
	progressbar = enum.auto()

	button = enum.auto()
	checklist = enum.auto()
	list = enum.auto()
	help = enum.auto()
	check = enum.auto()
	radio = enum.auto()
	image = enum.auto()
	toggle = enum.auto()
	radiobox = enum.auto()

	file = enum.auto()
	filewindow = enum.auto()
	date = enum.auto()
	datewindow = enum.auto()
	time = enum.auto()
	color = enum.auto()
	font = enum.auto()

	menu = enum.auto()
	toolbar = enum.auto()
	flatmenu = enum.auto()

	menuitem = enum.auto()
	toolbaritem = enum.auto()
	flatmenuitem = enum.auto()

	popup = enum.auto()
	popup_widget = enum.auto()

	canvas = enum.auto()
	table = enum.auto()

	busy = enum.auto()
	print = enum.auto()
	choice = enum.auto()
	scroll = enum.auto()
	custom = enum.auto()
	message = enum.auto()
	process = enum.auto()
	printsetup = enum.auto()
	printpreview = enum.auto()

	frame = enum.auto()
	dialog = enum.auto()
	panel = enum.auto()
	wizard = enum.auto()
	wizardpage = enum.auto()
	notebook = enum.auto()
	notebookpage = enum.auto()

	quad = enum.auto()
	poly = enum.auto()
	double = enum.auto()

#Event System
MyEvent = MyUtilities.wxPython.MyEvent

#Decorators
wrap_skipEvent = MyUtilities.wxPython.wrap_skipEvent

#Global Inheritance Classes
class Utilities(MyUtilities.common.CommonFunctions, MyUtilities.common.EnsureFunctions, MyUtilities.wxPython.Converters, MyUtilities.wxPython.CommonFunctions):
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

	def get(self, itemLabel = None, default = NULL, *, includeUnnamed = True, checkNested = True, typeList = None, subTypeList = None, returnExists = False):
		"""Searches the label catalogue for the requested object.

		itemLabel (any) - What the object is labled as in the catalogue
			- If slice: objects will be returned from between the given spots 
			- If wxEvent: Will get the object that triggered the event
			- If None: Will return all that would be in an unbound slice
			- If Types enumeration: Will return an object of that type

		Example Input: get()
		Example Input: get(0)
		Example Input: get(1.1)
		Example Input: get("text")
		Example Input: get(slice(None, None, None))
		Example Input: get(slice(2, "text", None))
		Example Input: get(event)
		Example Input: get(event, returnExists = True)
		Example Input: get(slice(None, None, None), checkNested = False)

		Example Use: GUI_Maker.Types.view in frameSettings.myFrame
		"""

		def nestCheck(itemList, itemLabel, compareType = False):
			"""Makes sure everything is nested."""

			if (isinstance(itemLabel, handle_Base)):
				key = itemLabel.label
			else:
				key = itemLabel

			answer = None
			for item in itemList:
				if (isinstance(key, wx.Event)):
					if (key.GetEventObject() == item.thing):
						return item
				elif (compareType):
					if (key is item.type):
						return item
				else:
					if (key == item.label):
						return item
				
				answer = nestCheck(item[:], key, compareType = compareType)
				if (answer is not None):
					return answer
			return answer

		def checkType(handleList):
			"""Makes sure only the instance types the user wants are in the return list."""
			nonlocal typeList, subTypeList

			if ((handleList is not None) and (typeList is not None)):
				answer = []

				for item in self.ensure_container(handleList):
					for itemType in self.ensure_container(typeList):
						if (isinstance(item, itemType)):
							if ((subTypeList is not None) and (item.type not in subTypeList)):
								continue
							answer.append(item)
							break

				if (isinstance(answer, (list, tuple, range))):
					if (len(answer) == 0):
						answer = None
			else:
				answer = handleList
			return answer

		#####################################################

		#Ensure correct format
		if (subTypeList is not None):
			subTypeList = self.ensure_container(subTypeList) or None

		if (typeList is not None):
			typeList = self.ensure_container(typeList) or None

		#Account for retrieving all nested
		if (itemLabel is None):
			itemLabel = slice(None, None, None)

		#Account for passing in a handle
		if (isinstance(itemLabel, handle_Base)):
			itemLabel = itemLabel.label
			if (itemLabel is None):
				raise NotImplementedError()

		#Account for passing in a wxEvent
		if (isinstance(itemLabel, wx.Event)):
			answer = None
			if ((not isinstance(self, Controller)) and (itemLabel.GetEventObject() == self.thing)):
				answer = self
			else:
				if (itemLabel.GetEventObject() is None):
					if (default is NULL):
						errorMessage = f"There is no object associated with the event {itemLabel}"
						raise SyntaxError(errorMessage)
					answer = None
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
			if (itemLabel.step is not None):
				raise FutureWarning(f"Add slice steps to get() for indexing {self.__repr__()}")
			
			elif ((itemLabel.start is not None) and (itemLabel.start not in self.labelCatalogue)):
				errorMessage = f"There is no item labled {itemLabel.start} in the label catalogue for {self.__repr__()}"
				raise KeyError(errorMessage)
			
			elif ((itemLabel.stop is not None) and (itemLabel.stop not in self.labelCatalogue)):
				errorMessage = f"There is no item labled {itemLabel.stop} in the label catalogue for {self.__repr__()}"
				raise KeyError(errorMessage)

			if (isinstance(itemLabel.start, handle_Base)):
				itemLabel.start = itemLabel.start.label
			if (isinstance(itemLabel.stop, handle_Base)):
				itemLabel.stop = itemLabel.stop.label

			handleList = []
			begin = False
			for item in self.labelCatalogueOrder:
				#Allow for slicing with non-integers
				if ((not begin) and ((itemLabel.start is None) or (self.labelCatalogue[item].label == itemLabel.start))):
					begin = True
				elif ((itemLabel.stop is not None) and (self.labelCatalogue[item].label == itemLabel.stop)):
					break

				#Slice catalogue via creation date
				if (begin):
					handleList.append(self.labelCatalogue[item])

			if (includeUnnamed):
				for item in self.unnamedList:
					handleList.append(item)

			answer = checkType(handleList)
			if (returnExists):
				return answer is not None
			return answer

		#Account for passing in a Types enumeration
		elif (isinstance(itemLabel, Types)):
			answer = nestCheck(self[:], itemLabel, compareType = True)
			answer = checkType(answer)

		elif (itemLabel in self.unnamedList):
			answer = checkType(itemLabel)

		else:
			if (isinstance(itemLabel, handle_Base)):
				key = itemLabel.label
			else:
				key = itemLabel

			if (key is None):
				answer = None
			elif (key in self.labelCatalogue):
				answer = checkType(self.labelCatalogue[key])
			else:
				if (checkNested):
					answer = nestCheck(self[:], key)
					answer = checkType(answer)
				else:
					answer = None

		if (returnExists):
			return answer is not None
		
		if (answer is not None):
			if (isinstance(answer, (list, tuple, range))):
				if (len(answer) == 1):
					answer = answer[0]

			return answer

		elif (default is not NULL):
			return default

		if (isinstance(itemLabel, wx.Event)):
			errorMessage = f"There is no item associated with the event {itemLabel} in the label catalogue for {self.__repr__()}"
		elif (typeList is not None):
			if (isinstance(answer, (list, tuple, range))):
				errorMessage = f"There is no item labled {itemLabel} in the label catalogue for {self.__repr__()} that is a {[item.__name__ for item in typeList]}"
			else:
				errorMessage = f"There is no item labled {itemLabel} in the label catalogue for {self.__repr__()} that is a {typeList.__name__}"
		else:
			errorMessage = f"There is no item labled {itemLabel} in the label catalogue for {self.__repr__()}"
		raise KeyError(errorMessage)

	def runMyFunction(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, event = None, includeEvent = False,
		errorFunction = None, errorFunctionArgs = None, errorFunctionKwargs = None, includeError = True):
		"""Runs a function."""

		answer = None

		try:
			#Skip empty functions
			if (myFunction is not None):
				if (not isinstance(myFunction, (list, tuple))):
					if (isinstance(myFunction, str)):
						myFunction = eval(myFunction, {'__builtins__': None}, {})
					
					if (myFunctionArgs is None):
						myFunctionArgs = []
					elif (not isinstance(myFunctionArgs, (list, tuple))):
						myFunctionArgs = [myFunctionArgs]

					if (myFunctionKwargs is None):
						myFunctionKwargs = {}

					answer = myFunction(*myFunctionArgs, **myFunctionKwargs)

				elif (len(myFunction) != 0):
					myFunctionList, myFunctionArgsList, myFunctionKwargsList = self._formatFunctionInputList(myFunction, myFunctionArgs, myFunctionKwargs)
					#Run each function
					answer = []
					for i, myFunction in enumerate(myFunctionList):
						#Skip empty functions
						if (myFunction is not None):
							myFunctionEvaluated, myFunctionArgs, myFunctionKwargs = self._formatFunctionInput(i, myFunctionList, myFunctionArgsList, myFunctionKwargsList)
							
							if (includeEvent):
								if (myFunctionArgs is None):
									myFunctionArgs = [event]
								else:
									myFunctionArgs = [event] + myFunctionArgs

							answer.append(myFunctionEvaluated(*myFunctionArgs, **myFunctionKwargs))

		except Exception as error:
			if (errorFunction is None):
				raise error
			else:
				if (includeError):
					if (errorFunctionArgs is None):
						errorFunctionArgs = [error]
					else:
						errorFunctionArgs = [error] + errorFunctionArgs
				
				answer = self.runMyFunction(errorFunction, errorFunctionArgs, errorFunctionKwargs, event = event, includeEvent = includeEvent)

		return answer

	def _removeDuplicates(self, sequence, idFunction=None):
		"""Removes duplicates from a list while preserving order.
		Created by Alex Martelli. From https://www.peterbe.com/plog/uniqifiers-benchmark

		Example Input: _removeDuplicates()
		"""

		if idFunction is None:
			def idFunction(x): 
				return x

		seen = {}
		result = []
		for item in sequence:
			marker = idFunction(item)
			if marker in seen: 
				continue
			seen[marker] = 1
			result.append(item)
		return result

	#Binding Functions
	def _formatFunctionInputList(self, myFunctionList, myFunctionArgsList, myFunctionKwargsList):
		"""Formats the args and kwargs for various internal functions."""

		#Ensure that multiple function capability is given
		##Functions
		if (myFunctionList is not None):
			#Compensate for the user not making it a list
			if (not isinstance(myFunctionList, list)):
				if (isinstance(myFunctionList, (tuple, types.GeneratorType))):
					myFunctionList = list(myFunctionList)
				else:
					myFunctionList = [myFunctionList]

			#Fix list order so it is more intuitive
			if (len(myFunctionList) > 1):
				myFunctionList.reverse()

		##args
		if (myFunctionArgsList is not None):
			#Compensate for the user not making it a list
			if (not isinstance(myFunctionArgsList, list)):
				if (isinstance(myFunctionArgsList, (tuple, types.GeneratorType))):
					myFunctionArgsList = list(myFunctionArgsList)
				else:
					myFunctionArgsList = [myFunctionArgsList]

			#Fix list order so it is more intuitive
			if (len(myFunctionList) > 1):
				myFunctionArgsList.reverse()

			if ((len(myFunctionList) == 1) and (myFunctionArgsList[0] is not None)):
				myFunctionArgsList = [myFunctionArgsList]

		##kwargs
		if (myFunctionKwargsList is not None):
			#Compensate for the user not making it a list
			if (not isinstance(myFunctionKwargsList, list)):
				if (isinstance(myFunctionKwargsList, (tuple, types.GeneratorType))):
					myFunctionKwargsList = list(myFunctionKwargsList)
				else:
					myFunctionKwargsList = [myFunctionKwargsList]

			#Fix list order so it is more intuitive
			if (len(myFunctionList) > 1):
				myFunctionKwargsList.reverse()

		return myFunctionList, myFunctionArgsList, myFunctionKwargsList

	def _formatFunctionInput(self, i, myFunctionList, myFunctionArgsList, myFunctionKwargsList):
		"""Formats the args and kwargs for various internal functions."""

		myFunction = myFunctionList[i]

		#Skip empty functions
		if (myFunction is not None):
			#Use the correct args and kwargs
			if (myFunctionArgsList is not None):
				myFunctionArgs = myFunctionArgsList[i]
			else:
				myFunctionArgs = myFunctionArgsList

			if (myFunctionKwargsList is not None):
				myFunctionKwargs = myFunctionKwargsList[i]
				
			else:
				myFunctionKwargs = myFunctionKwargsList

			#Check for User-defined function
			if (not isinstance(myFunction, str)):
				#The address is already given
				myFunctionEvaluated = myFunction
			else:
				#Get the address of myFunction
				myFunctionEvaluated = eval(myFunction, {'__builtins__': None}, {})

			#Ensure the *args and **kwargs are formatted correctly 
			if (myFunctionArgs is not None):
				#Check for single argument cases
				if (not isinstance(myFunctionArgs, list)):
					#The user passed one argument that was not a list
					myFunctionArgs = [myFunctionArgs]
				# else:
				#   if (len(myFunctionArgs) == 1):
				#       #The user passed one argument that is a list
				#       myFunctionArgs = [myFunctionArgs]

			#Check for user error
			if ((not isinstance(myFunctionKwargs, dict)) and (myFunctionKwargs is not None)):
				errorMessage = f"myFunctionKwargs must be a dictionary for function {myFunctionEvaluated.__repr__()}"
				raise ValueError(errorMessage)

		if (myFunctionArgs is None):
			myFunctionArgs = []
		if (myFunctionKwargs is None):
			myFunctionKwargs = {}

		return myFunctionEvaluated, myFunctionArgs, myFunctionKwargs

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
		if (keyCheck is not None):
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
		if (event is None):
			if (keyUp):
				event = wx.EVT_KEY_UP
			else:
				event = wx.EVT_KEY_DOWN

		if (thing is None):
			thing = self.thing

		#Bind the event
		self._betterBind(event, thing, self.onKeyPress, [value, myFunction, myFunctionArgs, myFunctionKwargs, ctrl, alt, shift, includeEvent], mode = 2)

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
			if ((not isinstance(myFunctionArgs, (list, tuple))) and (myFunctionArgs is not None)):
				myFunctionArgs = [myFunctionArgs]

			if ((not isinstance(myFunctionKwargs, (list, tuple))) and (myFunctionKwargs is not None)):
				myFunctionKwargs = [myFunctionKwargs]

			#Has both args and kwargs
			if ((myFunctionKwargs is not None) and (myFunctionArgs is not None)):
				if (includeEvent):
					myFunctionEvaluated(event, *myFunctionArgs, **myFunctionKwargs)
				else:
					myFunctionEvaluated(*myFunctionArgs, **myFunctionKwargs)

			#Has args, but not kwargs
			elif (myFunctionArgs is not None):
				if (includeEvent):
					myFunctionEvaluated(event, *myFunctionArgs)
				else:
					myFunctionEvaluated(*myFunctionArgs)

			#Has kwargs, but not args
			elif (myFunctionKwargs is not None):
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
		if (isinstance(keyList, (tuple, types.GeneratorType))):
			keyList = list(keyList)
		elif (not isinstance(keyList, list)):
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
			if (myFunctionList is not None):
				#Ensure that multiple function capability is given
				if ((not isinstance(myFunctionList, list)) and (myFunctionList is not None)):
					if (isinstance(myFunctionList, (tuple, types.GeneratorType))):
						myFunctionList = list(myFunctionList)
					else:
						myFunctionList = [myFunctionList]

				#args
				if ((not isinstance(myFunctionArgsList, list)) and (myFunctionArgsList is not None)):
					if (isinstance(myFunctionArgsList, (tuple, types.GeneratorType))):
						myFunctionArgsList = list(myFunctionArgsList)
					else:
						myFunctionArgsList = [myFunctionArgsList]

					#Compensate for the user not making lists in lists for single functions or multiple functions
					if (len(myFunctionList) == 1):
						#Compensate for the user not making lists in lists for single functions or multiple functions
						if (len(myFunctionArgsList) != 1):
							myFunctionArgsList = [myFunctionArgsList]
				
				if ((len(myFunctionList) == 1) and (myFunctionArgsList is not None)):
					#Compensate for the user not making lists in lists for single functions or multiple functions
					if (len(myFunctionArgsList) != 1):
						myFunctionArgsList = [myFunctionArgsList]

				#kwargs
				if ((not isinstance(myFunctionKwargsList, list)) and (myFunctionKwargsList is not None)):
					if (isinstance(myFunctionKwargsList, (tuple, types.GeneratorType))):
						myFunctionKwargsList = list(myFunctionKwargsList)
					else:
						myFunctionKwargsList = [myFunctionKwargsList]

					if (len(myFunctionList) == 1):
						#Compensate for the user not making lists in lists for single functions or multiple functions
						if (len(myFunctionKwargsList) != 1):
							myFunctionKwargsList = [myFunctionKwargsList]
				
				if ((len(myFunctionList) == 1) and (myFunctionKwargsList is not None)):
					#Compensate for the user not making lists in lists for single functions or multiple functions
					if (len(myFunctionKwargsList) != 1):
						myFunctionKwargsList = [myFunctionKwargsList]

				#Fix list order so it is more intuitive
				if (myFunctionList is not None):
					myFunctionList.reverse()

				if (myFunctionArgsList is not None):
					myFunctionArgsList.reverse()

				if (myFunctionKwargsList is not None):
					myFunctionKwargsList.reverse()
				
				#Run each function
				for i, myFunction in enumerate(myFunctionList):
					#Skip empty functions
					if (myFunction is not None):
						#Use the correct args and kwargs
						if (myFunctionArgsList is not None):
							myFunctionArgs = myFunctionArgsList[i]
						else:
							myFunctionArgs = myFunctionArgsList

						if (myFunctionKwargsList is not None):
							myFunctionKwargs = myFunctionKwargsList[i]
						else:
							myFunctionKwargs = myFunctionKwargsList

						#Check for User-defined function
						if (not isinstance(myFunction,  str)):
							#The address is already given
							myFunctionEvaluated = myFunction
						else:
							#Get the address of myFunction
							myFunctionEvaluated = eval(myFunction, {'__builtins__': None}, {})

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
			if ((event is not None) and (event.GetKeyCode() != self.keyOptions["cl"])):
				return

			hllDll = ctypes.WinDLL("User32.dll")
			VK_CAPITAL = 0x14
			state = hllDll.GetKeyState(VK_CAPITAL)

			if ((state == 1) or (state == 65409)):
				state = True
			else:
				state = False
	
		return state

	def getMousePosition(self):
		"""Returns the current mouse position relative to the current handle.

		Example Input: getMousePosition()
		"""

		position = self.thing.ScreenToClient(wx.GetMousePosition())

		if (not isinstance(position, (list, tuple))):
			position = position.Get()

		return position

	#Background Processes
	

	#Nesting Catalogue
	def _getAddressValue(self, address):
		"""Returns the value of a given address for a dictionary of dictionaries.
		Special thanks to DomTomCat for how to get a value from a dictionary of dictionaries of n depth on https://stackoverflow.com/questions/14692690/access-nested-dictionary-items-via-a-list-of-keys
		
		address (list) - The path of keys to follow on the catalogue

		Example Input: _getAddressValue(self.nestingAddress)
		Example Input: _getAddressValue(self.nestingAddress + [id(self)])
		"""
		global nestingCatalogue

		if (not isinstance(address, (list, tuple, range))):
			address = [address]

		#Search through catalogue
		catalogue = nestingCatalogue
		for key in address: 
			catalogue = catalogue[key]

		return catalogue

	def _setAddressValue(self, address, value):
		"""Sets the value of a given address for a dictionary of dictionaries.
		Special thanks to eafit for how to set a value of a dictionary of dictionaries of n depth on https://stackoverflow.com/questions/14692690/access-nested-dictionary-items-via-a-list-of-keys
		"""
		global nestingCatalogue

		if (not isinstance(address, (list, tuple, range))):
			address = [address]

		catalogue = nestingCatalogue
		for key in address[:-1]:
			catalogue = catalogue.setdefault(key, {})
		catalogue[address[-1]] = value

	def _removeAddress(self, target):
		"""Removes the target from the nestingCatalogue under self.

		target (handle) - What to remove
			- If label: Will look up the handle in self

		Example Input: _removeAddress(key)
		"""
		global nestingCatalogue

		if (not isinstance(target, (list, tuple, range))):
			target = [target]

		for item in target:
			if (not isinstance(item, handle_Base)):
				item = self[item]
			catalogue = self._getAddressValue(self.nestingAddress + [id(self)])
			del catalogue[id(item)]

			item.nestedParent.nestingOrder.remove(item)

	def _getNested(self, include = [], exclude = [], includeUnnamed = True, useNestingOrder = True):
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
		useNestingOrder (bool) - Determines what order the returned object is in
			- If True: The returned order will be the order they were nested in
			- If False: The returned order will be [items with labels] then [items without labels]

		Example Input: _getNested()
		Example Input: _getNested(include = handle_Sizer)
		Example Input: _getNested(includeUnnamed = False)
		"""

		#Ensure correct format
		if (include is None):
			include = ()
		elif (isinstance(include, (list, range))):
			include = tuple(include)
		elif (not isinstance(include, tuple)):
			include = tuple([include])

		if (exclude is None):
			exclude = ()
		elif (isinstance(exclude, (list, range))):
			exclude = tuple(exclude)
		elif (not isinstance(exclude, tuple)):
			exclude = tuple([exclude])

		if (useNestingOrder):
			nestedList = [item for item in self.nestingOrder if (
				((len(include) == 0) or (isinstance(item, include))) and 
				((len(exclude) == 0) or (not isinstance(item, exclude))))]
		else:
			catalogue = self._getAddressValue(self.nestingAddress + [id(self)])
			nestedList = [value[None] for key, value in self.catalogue if (
				(key is not None) and (None in value) and 
				((len(include) == 0) or (isinstance(value[None], include))) and 
				((len(exclude) == 0) or (not isinstance(value[None], exclude))))]

			if (includeUnnamed):
				nestedList.extend([item for item in self.unnamedList if (
					((len(include) == 0) or (isinstance(item, include))) and 
					((len(exclude) == 0) or (not isinstance(item, exclude))))])

		return nestedList

	def _finalNest(self, handle):
		"""The final step in the nesting process."""

		handle.nested = True
		self.nestingOrder.append(handle)
		handle.nestedParent = self

	#Etc
	def _logPrint(self, *args, fileName = "cmd_log.log", timestamp = True, **kwargs):
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

	def _logError(self, *args, fileName = "error_log.log", timestamp = True, **kwargs):
		"""Overrides the stderr function to also log the error information.

		fileName (str)   - The filename for the log
		timestamp (bool) - Determines if the timestamp is added to the log
		"""

		self._logPrint(*args, fileName = fileName, timestamp = timestamp, **kwargs)

	def _getId(self, argument_catalogue, checkSpecial = False):
		"""Returns the appropriate id to use for the wxObject.

		Example Input: _getId(argument_catalogue)
		"""

		myId = self._getArguments(argument_catalogue, ["myId"])
		if (myId is None):
			if (checkSpecial and ("special" in argument_catalogue)):
				special = self._getArguments(argument_catalogue, ["special"])
				if (special is not None):
					#Use: https://wxpython.org/Phoenix/docs/html/stock_items.html#stock-items
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
			else:
				myId = wx.ID_ANY
		return myId

	def _getArguments(self, argument_catalogue, desiredArgs, checkOverride = True, checkAppend = True):
		"""Returns a list of the values for the desired arguments from a dictionary.

		argument_catalogue (dict) - All locals() of the function
		desiredArgs (str)   - Determines what is returned. Can be a list of values
		addToPrint (bool)   - Determines if the loaded arguments will be displayed when the handle is printed out

		Example Input: _getArguments(argument_catalogue, desiredArgs = "handler")
		Example Input: _getArguments(argument_catalogue, desiredArgs = ["handler", "flex", "flags"])
		"""

		#Ensure correct format
		if (not isinstance(desiredArgs, (list, tuple, range))):
			desiredArgs = [desiredArgs]

		if (self.label is not None):
			if (not checkOverride):
				_checkOverride = {}
			elif ((self.parent is not None) and (self.label in self.parent.attributeOverride)):
				_checkOverride = self.parent.attributeOverride[self.label]
			elif ((self.myWindow is not None) and (self.label in self.myWindow.attributeOverride)):
				_checkOverride = self.myWindow.attributeOverride[self.label]
			else:
				_checkOverride = {}

			if (not checkAppend):
				_checkAppend = {}
			elif ((self.parent is not None) and (self.label in self.parent.attributeAppend)):
				_checkAppend = self.parent.attributeAppend[self.label]
			elif ((self.myWindow is not None) and (self.label in self.myWindow.attributeAppend)):
				_checkAppend = self.myWindow.attributeAppend[self.label]
			else: 
				_checkAppend = {}
		else:
			_checkOverride = {}
			_checkAppend = {}

		argList = []
		for arg in desiredArgs:
			if (arg not in argument_catalogue):
				errorMessage = f"Must provide the argument {arg} to {self.__repr__()}"
				raise KeyError(errorMessage)

			if (arg in _checkOverride):
				value = _checkOverride[arg]
			else:
				value = argument_catalogue[arg]

			if (arg in _checkAppend):
				if (isinstance(value, (tuple, range, types.GeneratorType))):
					value = list(value)
				elif (not isinstance(value, list)):
					value = [value]
				value.extend(_checkAppend[arg])
			argList.append(value)

			if (arg not in ["self", "parent"]):
				self.makeVariables[arg] = value
						
		if (len(argList) == 1):
			argList = argList[0]

		return argList

	def _addAttributeOverride(self, label, variable, value):
		"""Will override 'variable' with 'value' for future children labeled 'label'.

		Example Input: _addAttributeOverride(addApply, "myId", wx.ID_APPLY)
		"""

		if (label not in self.attributeOverride):
			self.attributeOverride[label] = {}
		self.attributeOverride[label][variable] = value

	def _addAttributeAppend(self, label, variable, value):
		"""Will append 'variable' with 'value' for future children labeled 'label'.

		Example Input: _addAttributeAppend(addApply, "myFunction", self.onHideWindow)
		"""

		if (label not in self.attributeAppend):
			self.attributeAppend[label] = {}
		if (variable not in self.attributeAppend[label]):
			self.attributeAppend[label][variable] = []
		self.attributeAppend[label][variable].append(value)

	def _arrangeArguments(self, handle, function, argList = [], kwargDict = {}, exclude = [], copyFrom = None):
		"""Returns a dictionary of the args and kwargs for a function.

		function (function) - The function to inspect
		argList (list)      - The *args of 'function'
		kwargDict (dict)    - The **kwargs of 'function'
		exclude (list)      - What args or kwargs to not include
		copyFrom (handle)   - What to copy values from
			- If None: Does nothing

		Example Input: _arrangeArguments(self, function, args, kwargs)
		Example Input: _arrangeArguments(self.controller, Controller.addWindow, kwargDict = argument_catalogue)
		Example Input: _arrangeArguments(self, function, args, kwargs, copyFrom = handle)
		Example Input: _arrangeArguments(self, function, args, kwargs, exclude = ["self"])
		"""

		if (handle is not None):
			argList = [handle, *argList]
		arguments = inspect.getcallargs(function, *argList, **kwargDict)

		if (copyFrom is not None):
			if (not isinstance(copyFrom, handle_Base)):
				errorMessage = f"'copyFrom' must be a GUI_Maker handle, not {copyFrom.__repr__()} for _arrangeArguments() in {self.__repr__()}"
				raise ValueError(errorMessage)
			arguments = {key: value for key, value in vars(copyFrom).items() if (key in arguments)}

		if (not isinstance(exclude, (list, tuple, range))):
			exclude = exclude
		for item in exclude:
			if (item in arguments):
				del arguments[item]

		return arguments

	def _getArgument_event(self, arguments, args, kwargs):
		"""Returns the event for a function where the event could be in a given argument, args, or kwargs

		arguments (list) - What is not an arg or kwargs as an item in a list
		args (list)      - *args
		kwargs (dict)    - **kwargs

		Example Input: _getArgument_event(label, args, kwargs)
		Example Input: _getArgument_event([label, event], args, kwargs)
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

	def _getObjectWithEvent(self, event):
		"""Gets the object that triggered an event.

		event (CommandEvent) - The wxPython event that was triggered

		Example Input: _getObjectWithEvent(event)
		"""

		thing = event.GetEventObject()

		return thing

	def _getObjectParent(self, thing):
		"""Gets the parent of an object.

		thing (wxObject) - The object to find the parent of

		Example Input: _getObjectParent(self)
		Example Input: _getObjectParent(thing)
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
			if (parent.GetParent() is not None):
				parent = parent.GetParent()

				if (parent.GetParent() is not None):
					parent = parent.GetParent()

		return parent

	def getScreenSize(self, number = None, combine = True):
		"""Returns the screen resolution.
		Special thanks to Frederic Hamidi for how to get the screen size from multple displays on https://stackoverflow.com/questions/10294920/how-to-find-the-screen-size-of-two-monitors-using-wx-displaysize

		number (int) - Which screen to get the size of
			- If list: Which screens to get the size of
			- If None: Gets the size of all screens

		combine (bool) - Determines how the screen sizes are combined
			- If True: A single size is returned
			- If False: Each individual size is returned

		Example Input: getScreenSize()
		Example Input: getScreenSize(1)
		"""

		displays = (wx.Display(i) for i in range(wx.Display.GetCount()))

		geometry = sorted((display.GetGeometry() for display in displays), key = lambda item: item[0]) #Sort displays from left most to right most
		
		if (not combine):
			size = [tuple(rectangle.GetSize()) for rectangle in geometry]
			
			if (number is not None):
				size = size[number]
		else:
			if (isinstance(number, int)):
				geometry = [geometry[number]]
			elif (isinstance(number, (list, tuple, range))):
				geometry = [item for i, item in enumerate(geometry) if (i in number)]

			index = max(range(len(geometry)), key = lambda i: geometry[i][0])
			width = geometry[index][0] + geometry[index][2]
			
			index = max(range(len(geometry)), key = lambda i: geometry[i][1])
			height = geometry[index][1] + geometry[index][3]

			size = (width, height)

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

	def getStringPixels(self, line, multiLine = None, useDC = False):
		"""Returns the length of a string in pixels.

		line (str) - The string to measure
		multiLine (bool) - Determines if "\n" should be taken into account
			- If None: Will determine on its own if it should use multiLine

		Example Input: getStringPixels("Lorem Ipsum")
		Example Input: getStringPixels("Lorem Ipsum\nDolor Sit")
		Example Input: getStringPixels("Lorem Ipsum\nDolor Sit", multiLine = False)
		"""

		if (multiLine is None):
			multiLine = "\n" in line

		if (useDC):
			#Get the current font
			font = self.getFont()
			dc = wx.WindowDC(self)
			dc.SetFont(font)

			#Get font pixel size
			if (multiLine):
				size = dc.GetMultilineTextExtent(line)
			else:
				size = dc.GetTextExtent(line)
			del dc
		else:
			if (multiLine):
				size = self.thing.GetMultilineTextExtent(line)
			else:
				size = self.thing.GetTextExtent(line)

		return size

	def getWindow(self, label = None, frameOnly = True):
		if (isinstance(label, handle_Window)):
			if (frameOnly and (label.type is Types.frame)):
				return label

		if (frameOnly):
			window = self.get(label, typeList = [handle_Window], subTypeList = Types.frame)
		else:
			window = self.get(label, typeList = [handle_Window])

		return window

	def getDialog(self, label = None):
		if ((isinstance(label, handle_Window)) and (label.type is labelTypes.dialog)):
			return label

		window = self.get(label, typeList = [handle_Window], subTypeList = Types.dialog)
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

	#Make Functions
	def makeDummy(self):
		"""Returns an object that will accept all functions but won't do anything.
		Meant to be used to prevent crashes, such as entering a frame that is not made yet.

		Example Input: makeDummy()
		"""

		handle = handle_Dummy()
		return handle

	def _makeText(self, text = "", wrap = None, ellipsize = False, alignment = None,
		size = None, bold = False, italic = False, color = None, family = None, 

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None, tabSkip = False):
		"""Creates a wx text object.
		If you want to update this text, you will need to run the function setObjectValue() or setObjectValueWithLabel().
		If you provide a variable to this function and that variable changes- the text on the GUI will not update.
		It must be told to do so explicitly by using one of the functions mentioned above.
		Note: If you change the text, any word wrap will be removed. To wrap it again, call the function textWrap().

		text (str)    - The text that will be added to the next cell on the grid.
		label (any)   - What this is catalogued as
		selected (bool) - If True: This is the default thing selected
		hidden (bool)   - If True: The widget is hidden from the user, but it is still created
		wrap (int)      - How many pixels wide the line will be before it wraps. If negative: no wrapping is done
		
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

		Example Input: _makeText()
		Example Input: _makeText(text = "Lorem Ipsum")
		Example Input: _makeText(text = "Change Me", label = "changableText")
		Example Input: _makeText(text = "Part Type", flags = "c2")
		Example Input: _makeText(text = "Part Type", flags = ["at", "c2"])
		Example Input: _makeText(text = "This line will wrap", wrap = 10)
		Example Input: _makeText(text = "BIG TEXT", bold = True, size = 72, color = "red")
		Example Input: _makeText(text = "Really long text", ellipsize = True)
		Example Input: _makeText(text = "Really long text", ellipsize = 0)
		Example Input: _makeText(text = "Really long text", ellipsize = 1)
		"""

		handle = handle_WidgetText()
		handle.type = Types.text
		handle._build(locals())

		return handle

	def _makeHyperlink(self, text = "", myWebsite = "",

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, 

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None, tabSkip = False):
		"""Adds a hyperlink text to the next cell on the grid.

		text (str)            - What text is shown
		myWebsite (str)         - The address of the website to open
		myFunction (str)        - What function will be ran when the link is clicked
		flags (list)            - A list of strings for which flag to add to the sizer
		label (any)           - What this is catalogued as
		myFunctionArgs (any)    - The arguments for 'myFunction'
		myFunctionKwargs (any)  - The keyword arguments for 'myFunction'function

		Example Input: _makeHyperlink("wxFB Website", "http://www.wxformbuilder.org", "siteVisited")
		"""

		handle = handle_WidgetText()
		handle.type = Types.hyperlink
		handle._build(locals())

		return handle

	def _makeHtml(self, text = "", can_scroll = True, can_select = True, position = None, size = None,

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, 

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None, tabSkip = False):
		"""Adds a widget that represents html to the next cell on the grid.

		text (str)            - What text is shown
		myFunction (str)        - What function will be ran when the link is clicked
		flags (list)            - A list of strings for which flag to add to the sizer
		label (any)           - What this is catalogued as
		myFunctionArgs (any)    - The arguments for 'myFunction'
		myFunctionKwargs (any)  - The keyword arguments for 'myFunction'function


		Example Input: _makeHtml(text = "<html><body>Lorem Ipsum</body></html>")
		Example Input: _makeHtml(text = "Lorem <b>ipsum</b> <i><u>dolor</u></i> sit <font color='red'>amet</font>.")
		"""

		handle = handle_WidgetText()
		handle.type = Types.html
		handle._build(locals())

		return handle

	def _makeEmpty(self, 

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None, tabSkip = False):
		"""Adds an empty space to the next cell on the grid.

		label (any)     - What this is catalogued as
		selected (bool)   - If True: This is the default thing selected
		hidden (bool)     - If True: The widget is hidden from the user, but it is still created

		Example Input: _makeEmpty()
		Example Input: _makeEmpty(label = "spacer")
		"""

		handle = handle_WidgetText()
		handle.type = Types.empty
		handle._build(locals())

		return handle

	def _makeLine(self, vertical = False,

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None, tabSkip = False):
		"""Adds a simple line to the window.
		It can be horizontal or vertical.

		vertical (bool)   - Whether the line is vertical or horizontal
		flags (list)      - A list of strings for which flag to add to the sizer
		label (any)     - What this is catalogued as
		hidden (bool)     - If True: The widget is hidden from the user, but it is still created

		Example Input: _makeLine()
		Example Input: _makeLine(vertical = True)
		"""

		handle = handle_Widget_Base()
		handle.type = Types.line
		handle._build(locals())

		return handle

	def _makeListDrop(self, choices = [], default = None, alphabetic = False, readOnly = False,
		formatter = None, inputBox = False, autoComplete = False, dropDown = True,

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, 

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None, tabSkip = False):
		"""Adds a dropdown list with choices to the next cell on the grid.

		choices (list)          - A list of the choices as strings
		myFunction (str)        - The function that is ran when the user chooses something from the list. If a list is given, each function will be bound.
		flags (list)            - A list of strings for which flag to add to the sizer
		label (any)           - What this is catalogued as
		myFunctionArgs (any)    - The arguments for 'myFunction'
		myFunctionKwargs (any)  - The keyword arguments for 'myFunction'function
		default (int)           - Which item in the droplist is selected
			- If a string is given, it will select the first item in the list that matches that string. If nothing matches, it will default to the first element
		enabled (bool)          - If True: The user can interact with this
		alphabetic (bool)      - Determines if the list is automatically sorted alphabetically
			- If True: The list is sorted alphabetically
			- If False: The list is presented in the order given

		Example Input: _makeListDrop(choices = ["Lorem", "Ipsum", "Dolor"])
		Example Input: _makeListDrop(choices = ["Lorem", "Ipsum", "Dolor"], label = "chosen")
		Example Input: _makeListDrop(choices = ["Lorem", "Ipsum", "Dolor"], alphabetic = True)
		Example Input: _makeListDrop(choices = [{label: "Lorem", value: 3}, {label: "Ipsum", value: 2}], formatter = lambda catalogue: catalogue["label"])
		"""

		handle = handle_WidgetList()
		handle.type = Types.drop
		handle._build(locals())

		return handle

	def _makeListFull(self, choices = [], default = False, single = False, editable = False,
		editOnClick = True, cellType = None, cellTypeDefault = "text", useWeakRefs = True,  

		sortable = True, sortFunction = None, rowFormatter = None,
		columns = None, columnTitles = {}, columnWidth = {}, columnLabels = {},
		columnImage = {}, columnAlign = {}, columnFormatter = {}, check = None,
		border = True, rowLines = True, columnLines = True, report = True, 
		group = {}, groupFormatter = {}, groupSeparator = True,
		showContextMenu = False, showColumnContextMenu = False, showEmptyGroups = None,
		groupIndent = None, hideFirstIndent = True, copyEntireRow = None, pasteEntireRow = None,

		can_scroll = True, can_expand = True, can_copy = True, can_paste = True, 
		can_selectAll = True, can_edit = True, can_undo = True,
		
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

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None, tabSkip = False):
		"""Adds a full list with choices to the next cell on the grid.
		https://wxpython.org/Phoenix/docs/html/wx.ListCtrl.html

		choices (list) - A list of the choices as strings
			- If list: [[row 1 column 1, row 2 column 1], [row 1 column 2, row 2 column 2]]
			- If dict: {column name 1: [row 1, row 2], column name 2: [row 1, row 2]}
				~ If an integer is given instead of a string for the column name, it will use that as the column index


		default (bool) - If True: This is the default thing selected
		enabled (bool) - If True: The user can interact with this
		single (bool)  - Determines how many things the user can select
			- If True: The user can only select one thing
			- If False: The user can select multiple things using the shift key
		
		editable (bool) - Determines if the user can edit the first item in the list
			- If True: The user can edit all items in the list
			- If False: The user can edit none of the items in the list
			- If dict: {column (int): state (bool)}
		editOnClick (bool) - Determines how many clicks it takes to open the editor
			- If True: one click
			- If False: Depends on engine
				~ engine 0: two clicks to edit, one click to select
				~ engine 1: two clicks to edit
				~ engine 2: two clicks to edit
			- If None: Depends on engine
				~ engine 1: two clicks to edit
				~ engine 1: Pressing F2 edits the primary cell. Tab/Shift-Tab can be used to edit other cells
				~ engine 2: two clicks to edit

		cellType (dict)       - Determines the widget type used for a specific cell in the list
				~ {column number (int): cell type for the cell (str)}
		cellTypeDefault (str) - What the cells default to as a widget
			- Possible Inputs: "text", inputbox", "button", "image"

		report (bool)      - Determines how the list is set up
			- If True: The list will be arranged in a grid
			- If False: Rows and columns will be dynamically calculated
		columns (int)      - How many columns the report will have
		columnTitles (dict) - What the column headers will say. If not given, the column will be blank. {row index (int) or column label (str): name}
		columnLabels (dict) - Used to interact with columns instead of using their column numbers (because tehse might change). {row index (int): column label (str)}
		
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
		

		Example Input: _makeListFull(["Lorem", "Ipsum", "Dolor"])
		Example Input: _makeListFull(["Lorem", "Ipsum", "Dolor"], myFunction = self.onChosen)

		Example Input: _makeListFull(["Lorem", "Ipsum", "Dolor"], report = False)
		Example Input: _makeListFull([["Lorem", "Ipsum"], ["Dolor"]], columns = 2)
		Example Input: _makeListFull([["Lorem", "Ipsum"], ["Dolor"]], columns = 2, columnTitles = {0: "Sit", 1: "Amet"})
		Example Input: _makeListFull({"Sit": ["Lorem", "Ipsum"], "Amet": ["Dolor"]], columns = 2, columnTitles = {0: "Sit", 1: "Amet"})
		Example Input: _makeListFull({"Sit": ["Lorem", "Ipsum"], 1: ["Dolor"]], columns = 2, columnTitles = {0: "Sit"})

		Example Input: _makeListFull([["Lorem", "Ipsum"], ["Dolor"]], columns = 2, columnTitles = {0: "Sit", 1: "Amet"}, editable = True)

		Example Input: _makeListFull(["Lorem", "Ipsum", "Dolor"], drag = True)
		Example Input: _makeListFull(["Lorem", "Ipsum", "Dolor"], drag = True, dragDelete = True)
		Example Input: _makeListFull(["Lorem", "Ipsum", "Dolor"], drag = True, dragDelete = True, allowExternalAppDelete = False)

		Example Input: _makeListFull(["Lorem", "Ipsum", "Dolor"], drop = True)
		Example Input: _makeListFull(["Lorem", "Ipsum", "Dolor"], drop = True, drag = True)

		Example Input: _makeListFull(["Lorem", "Ipsum", "Dolor"], drop = True, dropIndex = 2)
		Example Input: _makeListFull(["Lorem", "Ipsum", "Dolor"], drop = True, dropIndex = -1)
		Example Input: _makeListFull(["Lorem", "Ipsum", "Dolor"], drop = True, dropIndex = -2)

		Example Input: _makeListFull(["Lorem", "Ipsum", "Dolor"], drop = True, dropLabel = "text", preDropFunction = self.checkText)
		"""

		handle = handle_WidgetList()
		handle.type = Types.view
		handle._build(locals())

		return handle

	def _makeListTree(self, choices = [], default = None, root = None,
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

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None, tabSkip = False):
		"""Adds a tree list to the next cell on the grid.

		choices (list)          - A list of the choices as strings
		flags (list)            - A list of strings for which flag to add to the sizer
		label (any)           - What this is catalogued as
		default (int)           - Which item in the droplist is selected
			- If a string is given, it will select the first item in the list that matches that string. If nothing matches, it will default to the first element
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

		Example Input: _makeListTree(choices = {"Lorem": [{"Ipsum": "Dolor"}, "Sit"], "Amet": None})
		Example Input: _makeListTree(choices = {"Lorem": [{"Ipsum": "Dolor"}, "Sit"], "Amet": None}, label = "chosen")
		"""

		handle = handle_WidgetList()
		handle.type = Types.tree
		handle._build(locals())

		return handle

	def _makeInputSlider(self, myMin = 0, myMax = 100, myInitial = 0, vertical = False,

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None,

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None, tabSkip = False):
		"""Adds a slider bar to the next cell on the grid.

		myMin (int)             - The minimum value of the slider bar
		myMax (int)             - The maximum value of the slider bar
		myInitial (int)         - The initial value of the slider bar's position
		myFunction (str)        - The function that is ran when the user enters text and presses enter
		flags (list)            - A list of strings for which flag to add to the sizer
		label (any)           - What this is catalogued as
		myFunctionArgs (any)    - The arguments for 'myFunction'
		myFunctionKwargs (any)  - The keyword arguments for 'myFunction'function

		Example Input: _makeInputSlider(0, 100, 50, "initialTemperature")
		"""

		handle = handle_WidgetInput()
		handle.type = Types.slider
		handle._build(locals())

		return handle
	
	def _makeInputBox(self, text = None, maxLength = None, wrap = None, 
		autoComplete = None, caseSensitive = False, alwaysShow = False, 
		password = False, readOnly = False, tab = False, ipAddress = False, formatter = None, 
		onSelect_hide = False, onSelect_update = False, onKey_update = False, verifier = None, 
		
		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, 
		enterFunction = None, enterFunctionArgs = None, enterFunctionKwargs = None, 
		preEditFunction = None, preEditFunctionArgs = None, preEditFunctionKwargs = None, 
		postEditFunction = None, postEditFunctionArgs = None, postEditFunctionKwargs = None, 

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None, tabSkip = False):
		"""Adds an input box to the next cell on the grid.

		flags (list)    - A list of strings for which flag to add to the sizer
		label (any)     - What this is catalogued as
		text (str)      - What is initially in the box
		maxLength (int) - If not None: The maximum length of text that can be added
		
		selected (bool)  - If True: This is the default thing selected
		enabled (bool)   - If True: The user can interact with this
		hidden (bool)    - If True: The widget is hidden from the user, but it is still created
		password (bool)  - If True: The text within is shown as dots
		readOnly (bool)  - If True: The user cannot change the text
		tab (bool)       - If False: The 'Tab' key will move the focus to the next widget
		wrap (int)       - How many pixels wide the line will be before it wraps. 
		  If None: no wrapping is done
		  If positive: Will not break words
		  If negative: Will break words
		ipAddress (bool) - If True: The input will accept and understand the semantics of an ip address

		myFunction (str)       - The function that is ran when the user enters text
		myFunctionArgs (any)   - The arguments for 'myFunction'
		myFunctionKwargs (any) - The keyword arguments for 'myFunction'

		enterFunction (str)       - The function that is ran when the user presses enter while in the input box
		enterFunctionArgs (any)   - The arguments for 'enterFunction'
		enterFunctionKwargs (any) - the keyword arguments for 'enterFunction'

		postEditFunction (str)       - The function that is ran after the user clicks out (or tabs out, moves out, etc.) of the input box
		postEditFunctionArgs (any)   - The arguments for 'postEditFunction'
		postEditFunctionKwargs (any) - the keyword arguments for 'postEditFunction'

		preEditFunction (str)       - The function that is ran after the user clicks into (or tabs into, moves into, etc.) the input box
		preEditFunctionArgs (any)   - The arguments for 'preEditFunction'
		preEditFunctionKwargs (any) - the keyword arguments for 'preEditFunction'


		Example Input: _makeInputBox("initialTemperature", 0)
		Example Input: _makeInputBox("connect", 0, text = "127.0.0.0", ipAddress = True)
		"""

		handle = handle_WidgetInput()
		handle.type = Types.box
		handle._build(locals())

		return handle
	
	def _makeInputSearch(self, choices = None, text = None, menuLabel = None, 
		searchButton = True, cancelButton = True, hideSelection = True, 
		tab = False, alignment = 0, menuReplaceText = False, autoComplete = True,

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, 
		enterFunction = None, enterFunctionArgs = None, enterFunctionKwargs = None, 
		searchFunction = None, searchFunctionArgs = None, searchFunctionKwargs = None, 
		cancelFunction = None, cancelFunctionArgs = None, cancelFunctionKwargs = None, 
		menuFunction = None, menuFunctionArgs = None, menuFunctionKwargs = None, 

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None, tabSkip = False):
		"""Adds an input box to the next cell on the grid.

		text (str)      - What is initially in the box
		label (any)     - What this is catalogued as
		menuLabel (any) - What the menu associated with this is catalogued as
			- If None: Will not show the menu
			- If handle_Menu: Will use that menu
		searchButton (any) - If the search button should be shown
		cancelButton (any) - If the cancel button should be shown
		menuReplaceText(bool) - If the selection from the menu should replace the text in the input box

		alignment (int) - Determines how the text is aligned in its alloted space
			- If True: Will align text to the left
			- If False: Will align text to the center
			- If None: Will align text to the center
			- If 0: Will align text to the left
			- If 1: Will align text to the right
			- If 2: Will align text to the center

		myFunction (str)       - The function that is ran when the user enters text
		myFunctionArgs (any)   - The arguments for 'myFunction'
		myFunctionKwargs (any) - The keyword arguments for 'myFunction'function

		enterFunction (str)       - The function that is ran when the user presses enter while in the input box
		enterFunctionArgs (any)   - The arguments for 'enterFunction'
		enterFunctionKwargs (any) - the keyword arguments for 'enterFunction'
		
		searchFunction (str)       - If provided, this is what will be ran when the search button to the left is pressed
		searchFunctionArgs (any)   - The arguments for 'searchFunction'
		searchFunctionKwargs (any) - The keyword arguments for 'searchFunction'function
		
		cancelFunction (str)       - If provided, this is what will be ran when the cancel button to the right is pressed
			- If None: Will clear the input box
		cancelFunctionArgs (any)   - The arguments for 'cancelFunction'
		cancelFunctionKwargs (any) - The keyword arguments for 'cancelFunction'function
		
		menuFunction (str)       - If provided, this is what will be ran when the user selects an item from the menu
		menuFunctionArgs (any)   - The arguments for 'menuFunction'
		menuFunctionKwargs (any) - The keyword arguments for 'menuFunction'function
		
		Example Input: _makeInputSearch("initialTemperature")
		Example Input: _makeInputSearch("initialTemperature", "pastSearches")
		Example Input: _makeInputSearch("initialTemperature", "unitList", menuFunction = self.changeUnits)
		"""

		handle = handle_WidgetInput()
		handle.type = Types.search
		handle._build(locals())

		return handle
	
	def _makeInputSpinner(self, myMin = 0, myMax = 100, myInitial = 0, size = wx.DefaultSize, 
		increment = None, digits = None, useFloat = False, useHex = False, readOnly = False, exclude = [],

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, 
		changeTextFunction = True, changeTextFunctionArgs = None, changeTextFunctionKwargs = None,

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None, tabSkip = False):
		"""Adds a spin control to the next cell on the grid. This is an input box for numbers.

		myMin (int)       - The minimum value of the input spinner
		myMax (int)       - The maximum value of the input spinner
		myInitial (int)   - The initial value of the input spinner's position
		myFunction (str)  - The function that is ran when the user scrolls through the numbers
		flags (list)      - A list of strings for which flag to add to the sizer
		label (any)       - What this is catalogued as

		maxSize (tuple)   - If not None: The maximum size that the input spinner can be in pixels in the form (x, y) as integers
		minSize (tuple)   - If not None: The minimum size that the input spinner can be in pixels in the form (x, y) as integers
		increment (float) - If not None: Will increment by this value
		digits (float)    - If not None: Will show this many digits past the decimal point. Only applies if 'useFloat' is True

		useFloat (bool) - If True: Will increment decimal numbers instead of integers
		useHex (bool)   - If True: Will use base 16 numbers instead of base 10 numbers 
		readOnly (bool) - If True: The user will not be able to change the value
		exclude (list)  - A list of integers/floats to exclude from the spinner
		
		myFunctionArgs (any)           - The arguments for 'myFunction'
		myFunctionKwargs (any)         - The keyword arguments for 'myFunction'function
		changeTextFunction (str)       - The function that is ran when the user changes the text in the box directly. If True: Will be the same as myFunction
		changeTextFunctionArgs (any)   - The arguments for 'changeTextFunction'
		changeTextFunctionKwargs (any) - The key word arguments for 'changeTextFunction'
		

		Example Input: _makeInputSpinner(0, 100, 50, "initialTemperature")
		Example Input: _makeInputSpinner(0, 100, 50, "initialTemperature", maxSize = (100, 100))
		Example Input: _makeInputSpinner(0, 100, 50, "initialTemperature", exclude = [1,2,3])
		"""

		handle = handle_WidgetInput()
		handle.type = Types.spinner
		handle._build(locals())

		return handle
	
	def _makeButton(self, text = "", 
		
		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None,
		
		valueLabel = None,
		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None, tabSkip = False):
		"""Adds a button to the next cell on the grid.

		text (str)              - What will be written on the button
		flags (list)            - A list of strings for which flag to add to the sizer
		myFunction (str)        - What function will be ran when the button is pressed
		label (any)             - What this is catalogued as
		valueLabel (str)        - If not None: Which label to get a value from. Ie: TextCtrl, FilePickerCtrl, etc.
		myFunctionArgs (any)    - The arguments for 'myFunction'
		myFunctionKwargs (any)  - The keyword arguments for 'myFunction'function
		default (bool)          - If True: This is the default thing selected
		enabled (bool)          - If True: The user can interact with this
		hidden (bool)           - If True: The widget is hidden from the user, but it is still created

		Example Input: _makeButton("Go!", computeFinArray)
		"""

		handle = handle_WidgetButton()
		handle.type = Types.button
		handle._build(locals())

		return handle
	
	def _makeButtonToggle(self, text = "", 

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, 
		pressed = False,

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None, tabSkip = False):
		"""Adds a toggle button to the next cell on the grid.

		text (str)              - What will be written on the button
		myFunction (str)        - What function will be ran when the button is pressed
		flags (list)            - A list of strings for which flag to add to the sizer
		label (any)             - What this is catalogued as
		myFunctionArgs (any)    - The arguments for 'myFunction'
		myFunctionKwargs (any)  - The keyword arguments for 'myFunction'function
		default (bool)          - If True: This is the default thing selected
		enabled (bool)          - If True: The user can interact with this

		Example Input: _makeButtonToggle("Go!", computeFinArray)
		"""

		handle = handle_WidgetButton()
		handle.type = Types.toggle
		handle._build(locals())

		return handle
	
	def _makeButtonList(self, text = [], 
		
		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None,
		
		valueLabel = None,
		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None, tabSkip = False):
		"""Adds a button to the next cell on the grid.
		Each time this button is pressed, it will change the text to display the next item in the list.
		When it reaches the end of the list, it will start back at the beginning

		text (list)             - [What will be written on the button (str)]
		flags (list)            - A list of strings for which flag to add to the sizer
		myFunction (str)        - What function will be ran when the button is pressed
		label (any)             - What this is catalogued as
		valueLabel (str)        - If not None: Which label to get a value from. Ie: TextCtrl, FilePickerCtrl, etc.
		myFunctionArgs (any)    - The arguments for 'myFunction'
		myFunctionKwargs (any)  - The keyword arguments for 'myFunction'function
		default (bool)          - If True: This is the default thing selected
		enabled (bool)          - If True: The user can interact with this
		hidden (bool)           - If True: The widget is hidden from the user, but it is still created

		Example Input: _makeButton(["Showing All", "Showing One"], label = "lorem")
		"""

		handle = handle_WidgetButton()
		handle.type = Types.list
		handle._build(locals())

		return handle
	
	def _makeButtonCheck(self, text = "", default = False,

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, 

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None, tabSkip = False):
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

		Example Input: _makeButtonCheck("compute?", "computeFinArray", 0)
		"""

		handle = handle_WidgetButton()
		handle.type = Types.check
		handle._build(locals())

		return handle
	
	def _makeButtonCheckList(self, choices = [], multiple = True, sort = False,

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, 

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None, tabSkip = False):
		"""Adds a checklist to the next cell on the grid.

		choices (list)          - A list of strings that are the choices for the check boxes
		myFunction (str)        - What function will be ran when the date is changed
		flags (list)            - A list of strings for which flag to add to the sizer
		label (any)           - What this is catalogued as
		myFunctionArgs (any)    - The arguments for 'myFunction'
		myFunctionKwargs (any)  - The keyword arguments for 'myFunction'function
		multiple (bool)         - True if the user can check off multiple check boxes
		sort (bool)             - True if the checklist will be sorted alphabetically or numerically

		Example Input: _makeButtonCheckList(["Milk", "Eggs", "Bread"], 0, sort = True)
		"""

		handle = handle_WidgetButton()
		handle.type = Types.checklist
		handle._build(locals())

		return handle
	
	def _makeButtonRadio(self, text = "", groupStart = False, default = False,

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, 

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None, tabSkip = False):
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

		Example Input: _makeButtonRadio("compute?", "computeFinArray", 0, groupStart = True)
		"""

		handle = handle_WidgetButton()
		handle.type = Types.radio
		handle._build(locals())

		return handle
	
	def _makeButtonRadioBox(self, choices = [], title = "", vertical = False, default = 0, maximum = 1,

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, 

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None, tabSkip = False):
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

		Example Input: _makeButtonRadioBox(["Button 1", "Button 2", "Button 3"], "self.onQueueValue", 0)
		"""

		handle = handle_WidgetButton()
		handle.type = Types.radiobox
		handle._build(locals())

		return handle
	
	def _makeButtonHelp(self, 

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, 

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None, tabSkip = False):
		"""Adds a context help button to the next cell on the grid.

		flags (list)            - A list of strings for which flag to add to the sizer
		myFunction (str)        - What function will be ran when the button is pressed
		label (any)           - What this is catalogued as
		myFunctionArgs (any)    - The arguments for 'myFunction'
		myFunctionKwargs (any)  - The keyword arguments for 'myFunction'function
		default (bool)          - If True: This is the default thing selected
		enabled (bool)          - If True: The user can interact with this
		hidden (bool)           - If True: The widget is hidden from the user, but it is still created

		Example Input: _makeButtonHelp(label = "myHelpButton")
		"""

		handle = handle_WidgetButton()
		handle.type = Types.help
		handle._build(locals())

		return handle
	
	def _makeButtonImage(self, idlePath = "", disabledPath = "", selectedPath = "", 
		focusPath = "", hoverPath = "", text = None, toggle = False, size = None,
		internal = False, idle_internal = None, disabled_internal = None, 
		selected_internal = None, focus_internal = None, hover_internal = None,

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, 

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None, tabSkip = False):
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

		Example Input: _makeButtonImage("1.bmp", "2.bmp", "3.bmp", "4.bmp", "5.bmp", "computeFinArray")
		"""

		handle = handle_WidgetButton()
		handle.type = Types.image
		handle._build(locals())

		return handle
	
	def _makeImage(self, imagePath = "", internal = False, size = wx.DefaultSize,

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None, tabSkip = False):
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

		Example Input: _makeImage("1.bmp", 0)
		Example Input: _makeImage(image, 0)
		Example Input: _makeImage("error", 0, internal = True)
		Example Input: _makeImage(image, 0, size = (32, 32))
		"""

		handle = handle_WidgetImage()
		handle.type = Types.image
		handle._build(locals())

		return handle
	
	def _makeProgressBar(self, myInitial = 0, myMax = 100, *, vertical = False,

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None, tabSkip = False):
		"""Adds progress bar to the next cell on the grid.

		myInitial (int)         - The value that the progress bar starts at
		myMax (int)             - The value that the progress bar is full at
		flags (list)            - A list of strings for which flag to add to the sizer
		label (any)           - What this is catalogued as

		Example Input: _makeProgressBar(0, 100)
		"""

		handle = handle_Widget_Base()
		handle.type = Types.progressbar
		handle._build(locals())

		return handle

	def _makeToolBar(self, showText = False, showIcon = True, showDivider = False,
		detachable = False, flat = False, vertical = False, align = True,
		vertical_text = False, showToolTip = True, top = True,

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None,

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None, tabSkip = False):
		"""Adds a tool bar to the next cell on the grid.
		Menu items can be added to this.

		label (str)     - What this is called in the idCatalogue
		detachable (bool) - If True: The menu can be undocked

		Example Input: _makeToolBar()
		Example Input: _makeToolBar(label = "first")
		"""

		handle = handle_Menu()
		handle.type = Types.toolbar
		handle._build(locals())

		return handle

	def _makeFlatMenu(self, text = None, *, smallIcons = True, 
		spaceSize = None, canCustomize = False, 

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None,

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None, tabSkip = False):
		"""Adds a tool bar to the next cell on the grid.
		Menu items can be added to this.

		label (str)     - What this is called in the idCatalogue
		detachable (bool) - If True: The menu can be undocked

		Example Input: _makeToolBar()
		Example Input: _makeToolBar(label = "first")
		"""

		handle = handle_Menu()
		handle.type = Types.flatmenu
		handle._build(locals())

		return handle
	
	def _makePickerColor(self, initial = None, *, addInputBox = False, colorText = False,

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, 

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None, tabSkip = False):
		"""Adds a color picker to the next cell on the grid.
		It can display the name or RGB of the color as well.

		myFunction (str)        - What function will be ran when the color is chosen
		flags (list)            - A list of strings for which flag to add to the sizer
		label (any)           - What this is catalogued as
		myFunctionArgs (any)    - The arguments for 'myFunction'
		myFunctionKwargs (any)  - The keyword arguments for 'myFunction'function

		Example Input: _makePickerColor(label = "changeColor")
		"""

		handle = handle_WidgetPicker()
		handle.type = Types.color
		handle._build(locals())

		return handle
	
	def _makePickerFont(self, maxFontSize = 72, addInputBox = False, fontText = False,

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, 

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None, tabSkip = False):
		"""Adds a color picker to the next cell on the grid.
		It can display the name or RGB of the color as well.

		maxFontSize (int)           - The maximum font size that can be chosen
		myFunction (str)        - What function will be ran when the color is chosen
		flags (list)            - A list of strings for which flag to add to the sizer
		label (any)           - What this is catalogued as
		myFunctionArgs (any)    - The arguments for 'myFunction'
		myFunctionKwargs (any)  - The keyword arguments for 'myFunction'function
		fontText (str)          - True if it should show the name of the font picked

		Example Input: _makePickerFont(32, "changeFont")
		"""

		handle = handle_WidgetPicker()
		handle.type = Types.font
		handle._build(locals())

		return handle
	
	def _makePickerFile(self, text = "Select a File", default = "", initialDir = "", wildcard = "*.*", 
		directoryOnly = False, changeCurrentDirectory = False, fileMustExist = False, openFile = False, 
		saveConfirmation = False, saveFile = False, smallButton = False, addInputBox = False, 

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None,

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None, tabSkip = False):
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
		

		Example Input: _makePickerFile(myFunction = self.openFile, addInputBox = True)
		Example Input: _makePickerFile(saveFile = True, myFunction = self.saveFile, saveConfirmation = True, directoryOnly = True)
		"""

		handle = handle_WidgetPicker()
		handle.type = Types.file
		handle._build(locals())

		return handle
	
	def _makePickerFileWindow(self, initialDir = "*.*", 
		directoryOnly = True, selectMultiple = False, showHidden = True,

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, 
		editLabelFunction = None, editLabelFunctionArgs = None, editLabelFunctionKwargs = None, 
		rightClickFunction = None, rightClickFunctionArgs = None, rightClickFunctionKwargs = None, 

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None, tabSkip = False):
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

		Example Input: _makePickerFileWindow("changeDirectory")
		"""

		handle = handle_WidgetPicker()
		handle.type = Types.filewindow
		handle._build(locals())

		return handle
	
	def _makePickerTime(self, time = None, *, military = False, seconds = True, 
		minimum = None, maximum = None, applyBounds = None, outOfBounds_color = "Yellow", 
		addInputSpinner = True, wrap = True, arrowKeys = True, 

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, 

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None, tabSkip = False):
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

		Example Input: _makePickerTime()
		Example Input: _makePickerTime("17:30")
		Example Input: _makePickerTime("12:30:20")
		"""

		handle = handle_WidgetPicker()
		handle.type = Types.time
		handle._build(locals())

		return handle
	
	def _makePickerDate(self, date = None, dropDown = False, 

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, 

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None, tabSkip = False):
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

		Example Input: _makePickerDate()
		Example Input: _makePickerDate("10/16/2000")
		Example Input: _makePickerDate(dropDown = True)
		"""

		handle = handle_WidgetPicker()
		handle.type = Types.date
		handle._build(locals())

		return handle
	
	def _makePickerDateWindow(self, date = None, showHolidays = False, showOther = False,
		
		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, 
		dayFunction = None, dayFunctionArgs = None, dayFunctionKwargs = None, 
		monthFunction = None, monthFunctionArgs = None, monthFunctionKwargs = None, 
		yearFunction = None, yearFunctionArgs = None, yearFunctionArgsKwargs = None, 

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None, tabSkip = False):
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


		Example Input: _makePickerDateWindow()
		"""

		handle = handle_WidgetPicker()
		handle.type = Types.datewindow
		handle._build(locals())

		return handle

	def makeCanvas(self, *args, **kwargs):
		"""Returns a canvas handle that has no panel.

		Example Input: makeCanvas()
		"""

		handle = self._makeCanvas(*args, panel = None, **kwargs)
		return handle

	def _makeCanvas(self, size = wx.DefaultSize, position = wx.DefaultPosition, 
		panel = {}, metric = None,

		initFunction = None, initFunctionArgs = None, initFunctionKwargs = None,

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None, tabSkip = False):
		"""Creates a blank canvas window.

		panel (dict) - Instructions for the panel. Keys correspond to the args and kwargs for makePanel
			- If None: Will not create a panel for the canvas

		Example Input: _makeCanvas()
		"""

		handle = handle_WidgetCanvas()
		handle.type = Types.canvas
		handle._build(locals())

		return handle

	def _makeTable(self, rows = 1, columns = 1,
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

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None, tabSkip = False):

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
			- Possible Inputs: "inputbox", "droplist", "button"

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

		Example Input: _makeTable()
		Example Input: _makeTable(rows = 3, columns = 4)
		Example Input: _makeTable(rows = 3, columns = 4, contents = [[1, 2, 3], [a, b, c], [4, 5, 6], [d, e, f]])
		Example Input: _makeTable(rows = 3, columns = 4, contents = myArray)

		Example Input: _makeTable(rows = 3, columns = 4, readOnly = True)
		Example Input: _makeTable(rows = 3, columns = 4, readOnly = {1: True})
		Example Input: _makeTable(rows = 3, columns = 4, readOnly = {1: {1: True, 3: True}})
		Example Input: _makeTable(rows = 3, columns = 4, readOnly = {None: {1: True})

		Example Input: _makeTable(rows = 3, columns = 4, cellType = {1: "droplist"})
		Example Input: _makeTable(rows = 3, columns = 4, cellType = {1: {1: "droplist", 3: "droplist"}})
		Example Input: _makeTable(rows = 3, columns = 4, cellType = {None: {1: "droplist"}})

		Example Input: _makeTable(rows = 3, columns = 4, columnSize = 20)
		Example Input: _makeTable(rows = 3, columns = 4, columnSize = {0: 50, None: 20})
		Example Input: _makeTable(rows = 3, columns = 4, columnSize = {0: 50}, autoSizeColumn = True)
		Example Input: _makeTable(rows = 3, columns = 4, columnSize = {0: 50, None: 20}, autoSizeColumn = {1: True})
		"""

		handle = handle_WidgetTable()
		handle.type = Types.table
		handle._build(locals())

		return handle

	def makeMenu(self, *args, **kwargs):
		"""Returns a menu handle without a menuBar.

		Example Input: makeCanvas()
		"""

		handle = self._makeMenu(*args, menuBar = None, **kwargs)
		return handle

	def _makeMenu(self, text = " ", detachable = False, menuBar = True,

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None, tabSkip = False):
		"""Adds a menu to a pre-existing menuBar.
		This is a collapsable array of menu items.

		text (str)        - What the menu is called
			If you add a '&', a keyboard shortcut will be made for the letter after it
		label (str)     - What this is called in the idCatalogue
		detachable (bool) - If True: The menu can be undocked

		Example Input: _makeMenu("&File")
		"""

		handle = handle_Menu()
		handle.type = Types.menu
		handle._build(locals())

		return handle

	#Panels
	def _makePanel(self, border = wx.NO_BORDER, size = wx.DefaultSize, position = wx.DefaultPosition, 
		tabTraversal = True, scroll_x = False, scroll_y = False, scrollToTop = True, scrollToChild = True,

		initFunction = None, initFunctionArgs = None, initFunctionKwargs = None,

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None, tabSkip = False):
		"""Creates a blank panel.

		border (str)        - What style the border has. "simple", "raised", "sunken" or "none". Only the first two letters are necissary
		tabTraversal (bool) - If True: Pressing [tab] will move the cursor to the next widget
		
		scroll_x (bool) - Determines if the panel has a horizontal scroll bar
			- If int: How many pixels the horizontal scroll bar will increment by
			- If True: The panel has a horizontal scroll bar
			- If False: The panel has no horizontal scroll bar
		scroll_y (bool) - Determines if the panel has a vertical scroll bar
			- If int: How many pixels the vertical scroll bar will increment by
			- If True: The panel has a vertical scroll bar
			- If False: The panel has no vertical scroll bar
		scrollToTop (bool) - Determines if the scroll bar goes to the top?
		scrollToChild (bool) - Determines if the scroll bar automatically scrolls to fully show a child when it first comes into focus

		initFunction (str)       - The function that is ran when the panel first appears
		initFunctionArgs (any)   - The arguments for 'initFunction'
		initFunctionKwargs (any) - The keyword arguments for 'initFunction'function

		Example Input: _makePanel()
		Example Input: _makePanel(size = (200, 300))
		Example Input: _makePanel(border = "raised")
		Example Input: _makePanel(tabTraversal = False)
		"""

		handle = handle_Panel()
		handle.type = Types.panel
		handle._build(locals())

		return handle

	#Sizers
	def _makeSizerGrid(self, rows = 1, columns = 1, text = None,
		rowGap = 0, colGap = 0,
		size = wx.DefaultSize, scroll_x = False, scroll_y = False, scrollToTop = True, scrollToChild = True,

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None, tabSkip = False):
		"""Creates a grid sizer to the specified size.

		label (any)     - What this is catalogued as
		rows (int)        - The number of rows that the grid has
		columns (int)     - The number of columns that the grid has
		hidden (bool)     - If True: All items in the sizer are hidden from the user, but they are still created
		rowGap (int)      - Empty space between each row
		colGap (int)      - Empty space between each column
		minWidth (int)    - The minimum width of a box. -1 means automatic
		minHeight (int)   - The minimum height of a box. -1 means automatic

		Example Input: _makeSizerGrid()
		Example Input: _makeSizerGrid(0)
		Example Input: _makeSizerGrid(rows = 4, columns = 3)
		Example Input: _makeSizerGrid(0, rows = 4, columns = 3)
		"""

		handle = handle_Sizer()
		handle.type = Types.grid
		handle._build(locals())
		return handle

	def _makeSizerGridFlex(self, rows = 1, columns = 1, text = None, vertical = None,
		rowGap = 0, colGap = 0, flexGrid = True,
		size = wx.DefaultSize, scroll_x = False, scroll_y = False, scrollToTop = True, scrollToChild = True,

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None, tabSkip = False):
		"""Creates a flex grid sizer.
		############## NEEDS TO BE FIXED #################

		label (any)     - What this is catalogued as
		rows (int)        - The number of rows that the grid has
		columns (int)     - The number of columns that the grid has
		rowGap (int)      - Empty space between each row
		colGap (int)      - Empty space between each column
		hidden (bool)     - If True: All items in the sizer are hidden from the user, but they are still created
		flexGrid (bool)   - True if the grid will be flexable. If False, this is like a normal grid sizer.
		vertical (bool)   - Determines what direction cells are flexibally (unequally) sized
			- If True: Rows are sized
			- If False: Columns are sized
			- If None: Both are sized

		Example Input: _makeSizerGridFlex()
		Example Input: _makeSizerGridFlex(0)
		Example Input: _makeSizerGridFlex(rows = 4, columns = 3)
		Example Input: _makeSizerGridFlex(0, rows = 4, columns = 3)
		"""

		handle = handle_Sizer()
		handle.type = Types.flex
		handle._build(locals())

		return handle

	def _makeSizerGridBag(self, rows = 1, columns = 1, text = None,
		rowGap = 0, colGap = 0, vertical = None, 
		emptySpace = None, flexGrid = True,
		size = wx.DefaultSize, scroll_x = False, scroll_y = False, scrollToTop = True, scrollToChild = True,

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None, tabSkip = False):
		"""Creates a bag grid sizer.

		label (any)      - What this is catalogued as
		rows (int)         - The number of rows that the grid has
		columns (int)      - The number of columns that the grid has
		rowGap (int)       - Empty space between each row
		colGap (int)       - Empty space between each column
		hidden (bool)      - If True: All items in the sizer are hidden from the user, but they are still created
		emptySpace (tuple) - The space taken up by cells that are empty or hidden; (row width, column width)
		flexGrid (bool)    - True if the grid will be flexable. If False, this is like a normal grid sizer.
		vertical (bool)    - Determines what direction cells are flexibally (unequally) sized
			- If True: Rows are sized
			- If False: Columns are sized
			- If None: Both are sized

		Example Input: _makeSizerGridBag()
		Example Input: _makeSizerGridBag(0)
		Example Input: _makeSizerGridBag(0, rows = 4, columns = 3)
		Example Input: _makeSizerGridBag(0, rows = 4, columns = 3, emptySpace = (0, 0))
		"""

		handle = handle_Sizer()
		handle.type = Types.bag
		handle._build(locals())

		return handle

	def _makeSizerBox(self, text = None, vertical = True,
		size = wx.DefaultSize, scroll_x = False, scroll_y = False, scrollToTop = True, scrollToChild = True,

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None, tabSkip = False):
		"""Creates a box sizer.

		label (any)     - What this is catalogued as
		horizontal (bool) - True to align items horizontally. False to align items vertically
		hidden (bool)     - If True: All items in the sizer are hidden from the user, but they are still created

		Example Input: _makeSizerBox()
		Example Input: _makeSizerBox(0)
		Example Input: _makeSizerBox(vertical = False)
		Example Input: _makeSizerBox(0, vertical = False)
		"""

		handle = handle_Sizer()
		handle.type = Types.box
		handle._build(locals())

		return handle

	def _makeSizerText(self, text = "", vertical = True, 
		size = wx.DefaultSize, scroll_x = False, scroll_y = False, scrollToTop = True, scrollToChild = True,

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None, tabSkip = False):
		"""Creates a static box sizer.
		This is a sizer surrounded by a box with a title, much like a wxRadioBox.

		label (any)     - What this is catalogued as
		text (str)      - The text that appears above the static box
		horizontal (bool) - True to align items horizontally. False to align items vertically
		hidden (bool)     - If True: All items in the sizer are hidden from the user, but they are still created

		Example Input: _makeSizerText()
		Example Input: _makeSizerText(0)
		Example Input: _makeSizerText(text = "Lorem")
		Example Input: _makeSizerText(0, text = "Lorem")
		"""

		handle = handle_Sizer()
		handle.type = Types.text
		handle._build(locals())

		return handle

	def _makeSizerWrap(self, text = None, extendLast = False, vertical = True,
		size = wx.DefaultSize, scroll_x = False, scroll_y = False, scrollToTop = True, scrollToChild = True,

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None, tabSkip = False):
		"""Creates a wrap sizer.
		The widgets will arrange themselves into rows and columns on their own, starting in the top-left corner.

		label (any)     - What this is catalogued as
		text (str)      - The text that appears above the static box
		horizontal (bool) - Determines the primary direction to fill widgets in
			- If True: Align items horizontally first
			- If False: Align items vertically first
		hidden (bool)     - If True: All items in the sizer are hidden from the user, but they are still created
		extendLast (bool) - If True: The last widget will extend to fill empty space

		Example Input: _makeSizerWrap()
		Example Input: _makeSizerWrap(0)
		"""

		handle = handle_Sizer()
		handle.type = Types.wrap
		handle._build(locals())

		return handle

	#Splitters
	def _makeSplitterDouble(self, sizer_0 = {}, sizer_1 = {}, panel_0 = {}, panel_1 = {},

		dividerSize = 1, dividerPosition = None, dividerGravity = 0.5, 
		vertical = True, minimumSize = 20, 
		
		initFunction = None, initFunctionArgs = None, initFunctionKwargs = None, 

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None, tabSkip = False, selected = False, flex = 0, flags = "c1"):
		"""Creates two blank panels in next to each other. 
		The border between double panels is dragable.

		leftSize (int)        - The size of the left panel. (length, width)
		rightSize (int)       - The size of the right panel. (length, width)
			- If True: 'leftPanel' is the top panel; 'rightPanel' is the bottom panel
			- If False: 'leftPanel' is the left panel; 'rightPanel' is the right panel
		border (str)          - What style the border has. "simple", "raised", "sunken" or "none". Only the first two letters are necissary
		dividerSize (int)     - How many pixels thick the dividing line is. Not available yet
		dividerPosition (int) - How many pixels to the right the dividing line starts after the 'minimumSize' location
			- If None: The line will start at the 'minimumSize' value
		dividerGravity (int)  - From 0.0 to 1.1, how much the left (or top) panel grows with respect to the right (or bottom) panel upon resizing
		vertical (bool)       - Determines the direction that the frames are split
		minimumSize (int)     - How many pixels the smaller pane must have between its far edge and the splitter.
		
		initFunction (str)       - The function that is ran when the panel first appears
		initFunctionArgs (any)   - The arguments for 'initFunction'
		initFunctionKwargs (any) - The keyword arguments for 'initFunction'function

		label (any)   - What this is catalogued as

		Example Input: _makeSplitterDouble()
		Example Input: _makeSplitterDouble(horizontal = False)
		Example Input: _makeSplitterDouble(minimumSize = 100)
		"""

		handle = handle_Splitter()
		handle.type = Types.double
		handle._build(locals())

		return handle

	def _makeSplitterQuad(self, sizer_0 = {}, sizer_1 = {}, sizer_2 = {}, sizer_3 = {},

		initFunction = None, initFunctionArgs = None, initFunctionKwargs = None,

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None, tabSkip = False):
		"""Creates four blank panels next to each other like a grid.
		The borders between quad panels are dragable. The itersection point is also dragable.
		The panel order is top left, top right, bottom left, bottom right.
		
		border (str) - What style the border has. "simple", "raised", "sunken" or "none". Only the first two letters are necissary
		label (str)  - What this is called in the idCatalogue
		
		initFunction (str)       - The function that is ran when the panel first appears
		initFunctionArgs (any)   - The arguments for 'initFunction'
		initFunctionKwargs (any) - The keyword arguments for 'initFunction'function
		tabTraversal (bool)      - If True: Hitting the Tab key will move the selected widget to the next one

		Example Input: _makeSplitterQuad()
		"""

		handle = handle_Splitter()
		handle.type = Types.quad
		handle._build(locals())

		return handle

	def _makeSplitterPoly(self, panelNumbers, sizers = {},
		dividerSize = 1, dividerPosition = None, dividerGravity = 0.5, vertical = False, minimumSize = 20, 

		initFunction = None, initFunctionArgs = None, initFunctionKwargs = None,

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None, tabSkip = False):
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
		label (str)           - What this is called in the idCatalogue
		
		initFunction (str)       - The function that is ran when the panel first appears
		initFunctionArgs (any)   - The arguments for 'initFunction'
		initFunctionKwargs (any) - The keyword arguments for 'initFunction'function
		tabTraversal (bool)      - If True: Hitting the Tab key will move the selected widget to the next one

		Example Input: _makeSplitterPoly([0, 1, 2, 3], 0)
		Example Input: _makeSplitterPoly([0, 1, 2, 3], 0, panelSizes = [(200, 300), (300, 300), (100, 300)])
		Example Input: _makeSplitterPoly([0, 1, 2, 3], 0, horizontal = False)
		Example Input: _makeSplitterPoly([0, 1, 2, 3], 0, minimumSize = 100)
		"""

		handle = handle_Splitter()
		handle.type = Types.poly
		handle._build(locals())

		return handle

	#Notebooks
	def _makeNotebook(self, label = None, tabSide = "top",
		fixedWidth = False, multiLine = False, padding = None, reduceFlicker = True,

		initFunction = None, initFunctionArgs = None, initFunctionKwargs = None,
		postPageChangeFunction = None, postPageChangeFunctionArgs = None, postPageChangeFunctionKwargs = None,
		prePageChangeFunction = None, prePageChangeFunctionArgs = None, prePageChangeFunctionKwargs = None,

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, size = wx.DefaultSize, position = wx.DefaultPosition,
		parent = None, handle = None, myId = None, tabSkip = False):
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

		Example Input: _makeNotebook()
		Example Input: _makeNotebook("myNotebook")
		Example Input: _makeNotebook(padding = (5, 5))
		Example Input: _makeNotebook(padding = (5, None))
		"""

		handle = handle_Notebook_Simple()
		handle.type = Types.notebook
		handle._build(locals())

		return handle

	def _makeNotebookAui(self, label = None,

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

		Example Input: _makeNotebookAui()
		Example Input: _makeNotebookAui("myNotebook")
		"""

		handle = handle_Notebook_Aui()
		handle.type = Types.auinotebook
		handle._build(locals())

		return handle

	#Dialog Boxes
	def makeDialogMessage(self, text = "", title = "", stayOnTop = False, icon = None, 
		addYes = False, addOk = False, addCancel = False, addHelp = False, default = False,

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None, tabSkip = False):
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
		handle.type = Types.message
		handle._build(locals())
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

	def makeDialogScroll(self, text = "", title = "",

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None, tabSkip = False):
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
		handle.type = Types.scroll
		handle._build(locals())
		return handle

	def makeDialogBusy(self, text = "", simple = True, title = None, initial = 0, stayOnTop = True,
		maximum = 100, blockAll = True, autoHide = True, can_abort = False, can_skip = False, 
		smooth = False, elapsedTime = True, estimatedTime = True, remainingTime = True,
		cursor = False, freeze = False,

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None, tabSkip = False):
		"""Does not pause the running code, but instead ignores user inputs by 
		locking the GUI until the code tells the dialog box to go away. 
		This is done by either exiting a while loop or using the hide() function.

		title (str) - What the window's title will be
			- If None: Will use 'text', and if 'text' is empty will use "Busy"

		cursor (bool) - If True: Will have a busy cursor while the dialog is showing
		freeze (bool) - If True: Will freeze and thaw it's parent

		To protect the GUI better, implement: https://wxpython.org/Phoenix/docs/html/wx.WindowDisabler.html
		_________________________________________________________________________

		Example Use:
			with myFrame.makeDialogBusy(text = "Hold on...") as myDialog:
				for i in range(100):
					time.sleep(1)
		_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

		Example Use:
			myDialog = myFrame.makeDialogBusy(text = "Hold on...")
			myDialog.show()
			for i in range(100):
				time.sleep(1)
			myDialog.hide()
		_________________________________________________________________________

		Example Input: makeDialogBusy()
		Example Input: makeDialogBusy(text = "Calculating...")
		"""

		handle = handle_Dialog()
		handle.type = Types.busy
		handle._build(locals())
		return handle

	def makeDialogChoice(self, choices = [], text = "", title = "", single = True, 
		default = None, formatter = None,

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None, tabSkip = False):
		"""Pauses the running code and shows a dialog box that has choices in a list.

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
		Example Input: makeDialogChoice([{label: "Lorem", value: 3}, {label: "Ipsum", value: 2}], formatter = lambda catalogue: catalogue["label"])
		"""

		handle = handle_Dialog()
		handle.type = Types.choice
		handle._build(locals())
		return handle

	def makeDialogInput(self, text = "", title = "", default = "",
		addYes = False, addOk = True, addCancel = True, addHelp = False,
		password = False, readOnly = False, tab = False, wrap = None, maximum = None,

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None, tabSkip = False):
		"""Pauses the running code and shows a dialog box that has an input box.

		password (bool) - If True: The text within is shown as dots
		readOnly (bool) - If True: The user cannot change the text
		tab (bool)      - If False: The 'Tab' key will move the focus to the next widget
		wrap (int)      - How many pixels wide the line will be before it wraps. 
			- If None: no wrapping is done
			- If positive: Will not break words
			- If negative: Will break words
		maximum (int)   - Determines how long the input can be
			- If None: No maximum
		_________________________________________________________________________

		Example Use:
			with myFrame.makeDialogInput("Lorem Ipsum") as myDialog:
				value = myDialog.getValue()
		_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

		Example Use:
			myDialog = myFrame.makeDialogInput("Lorem Ipsum")
			value = myDialog.getValue()
		_________________________________________________________________________

		Example Input: makeDialogInput()
		"""

		handle = handle_Dialog()
		handle.type = Types.box
		handle._build(locals())
		return handle

	def makeDialogFile(self, title = "Select a File", text = "", initialFile = "", initialDir = "", wildcard = "*.*", 
		directoryOnly = False, changeCurrentDirectory = False, fileMustExist = False, openFile = False, 
		saveConfirmation = False, saveFile = False, preview = True, single = True, newDirButton = False,

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None, tabSkip = False):
		"""Pauses the running code and shows a dialog box to get input from the user about files.
		title (str)   - What is shown on the top of the popout window
		default (str) - What the default value will be for the input box

		initialDir (str)              - Which directory it will start at. By default this is the directory that the program is in
		directoryOnly (bool)          - If True: Only the directory will be shown; no files will be shown
		changeCurrentDirectory (bool) - If True: Changes the current working directory on each user file selection change
		fileMustExist (bool)          - If True: When a file is opened, it must exist
		openFile (bool)               - If True: The file picker is configured to open a file
		saveConfirmation (bool)       - If True: When a file is saved over an existing file, it makes sure you want to do that
		saveFile (bool)               - If True: The file picker is configured to save a file
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

		Example Input: makeDialogFile()
		"""

		handle = handle_Dialog()
		handle.type = Types.file
		handle._build(locals())
		return handle

	def makeDialogColor(self, simple = True,

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None, tabSkip = False):
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
		handle.type = Types.color
		handle._build(locals())
		return handle

	def makeDialogPrintSetup(self, printData = None, printOverride = {}, helpButton = False, 
		marginMinimum = None, marginLeft = None, marginTop = None, marginRight = None, marginBottom = None, 
		editMargins = True, editOrientation = True, editPaper = True, editPrinter = True, 
		marginLeftMinimum = None, marginTopMinimum = None, marginRightMinimum = None, marginBottomMinimum = None, 

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None, tabSkip = False):
		"""Pauses the running code and shows a dialog box to get input from the user about which printer with what settings to use.

		pageNumbers (bool) - Determines the state of the 'page numbers' control box
			- If True: Enables the control box
			- If False: Disables the control box
		helpButton (bool) - Determines the state of the 'help' button
			- If True: Enables the help button
			- If False: Disables the help button

		printToFile (str) - What file to print this to
			- If None: Disables the 'print to file' check box

		selection (bool) - ?
			- If None: Disables the 'selection' radio button?

		pageFrom (int) - Sets the 'Pages' from field
		pageTo (int)   - Sets the 'Pages' to field
		pageMin (int)  - Sets the minimum number of copies
		pageMax (int)  - Sets the maximum number of copies
		copies (int)   - Sets the 'Number of copies' input spinner

		collate (bool) - Sets the 'Collate' check box

		_________________________________________________________________________

		Example Use:
			with myFrame.makeDialogPrint() as myDialog:
				printData = myDialog.getValue()
		_________________________________________________________________________

		Example Input: makeDialogPrintSetup()
		"""

		handle = handle_Dialog()
		handle.type = Types.printsetup
		handle._build(locals())
		return handle

	def makeDialogPrint(self, pageNumbers = True, helpButton = False, printToFile = None, 
		selection = None, pageFrom = None, pageTo = None, pageMin = None, pageMax = None, 
		collate = None, copies = None, printData = None, printOverride = {}, 

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None, tabSkip = False):
		"""Pauses the running code and shows a dialog box to get input from the user about printing.

		pageNumbers (bool) - Determines the state of the 'page numbers' control box
			- If True: Enables the control box
			- If False: Disables the control box
		helpButton (bool) - Determines the state of the 'help' button
			- If True: Enables the help button
			- If False: Disables the help button

		printToFile (str) - What file to print this to
			- If None: Disables the 'print to file' check box

		selection (bool) - ?
			- If None: Disables the 'selection' radio button?

		pageFrom (int) - Sets the 'Pages' from field
		pageTo (int)   - Sets the 'Pages' to field
		pageMin (int)  - Sets the minimum number of copies
		pageMax (int)  - Sets the maximum number of copies
		copies (int)   - Sets the 'Number of copies' input spinner

		collate (bool) - Sets the 'Collate' check box

		_________________________________________________________________________

		Example Use:
			with myFrame.makeDialogPrint() as myDialog:
				myDialog.setValue(text)
				myDialog.send()
		_________________________________________________________________________

		Example Input: makeDialogPrint()
		"""

		handle = handle_Dialog()
		handle.type = Types.print
		handle._build(locals())
		return handle

	def makeDialogPrintPreview(self, printData = None, printerSetup = True, printOverride = {},
		size = None, position = None, content = None,

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None, tabSkip = False):
		"""Pauses the running code and shows a dialog box to get input from the user about printing.
		_________________________________________________________________________

		Example Use:
			with myFrame.makeDialogPrintPreview() as myDialog:
				myDialog.setValue(text)
				myDialog.send()
		_________________________________________________________________________

		Example Input: makeDialogPrintPreview()
		"""

		handle = handle_Dialog()
		handle.type = Types.printpreview
		handle._build(locals())
		return handle

	def makeDialogCustom(self, myFrame = None, valueLabel = None,

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None, tabSkip = False):
		"""Allows the user to define how the frame looks on their own.

		myFrame (handle_Window) - What frame to use as the window
			- If None: Will use self
		valueLabel (str)        - The label for the widget to use for getValue()

		_________________________________________________________________________

		Example Use:
			with myFrame.makeDialogWindow(gui["customDialog"], "value") as myDialog:
				if (myDialog.isOk()):
					print("You selected ok")
				elif (myDialog.isCancel()):
					print("You selected cancel")
		_________________________________________________________________________

		Example Input: makeDialogCustom(gui["customDialog"], "value")
		"""

		if (myFrame is None):
			myFrame = self

		handle = handle_Dialog()
		handle.type = Types.custom
		handle._build(locals())
		return handle

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

		self.controller.exiting = True
		
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

		# print("onDoNothing()")
		pass
		
		#There is no event.Skip() here to prevent the event from propigating forward

	def onIdle(self, event):
		"""Runs functions only while the GUI is idle. It will pause running the functions if the GUI becomes active.
		WARNING: This is not working yet.
		"""

		print("onIdle()")
		pass

#Handles
class handle_Dummy(MyUtilities.common.ELEMENT):
	"""A handle that will accept all functions and just let the program continue without throwing an error."""

	def __repr__(self):
		representation = f"{type(self).__name__}(id = {id(self)}"
		return representation

	def __str__(self):
		output = f"{type(self).__name__}()\n-- id: {id(self)}\n"
		return output

	def __len__(self):
		return 1

	def __iter__(self):
		return MyUtilities.common.CommonIterator({})

	def __getitem__(self, key):
		return None

	def __setitem__(self, key, value):
		pass

	def __delitem__(self, key):
		pass

	def __contains__(self, key):
		return False

	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc_value, traceback):
		if (traceback is not None):
			return False

	def __getattr__(self, name):
		try:
			return super(type(self), self).__getattr__(name, value)
		except:
			return self.dummyFunction
			# return handle_Dummy()

	def dummyFunction(*args, **kwargs):
		pass

	def keys(self, *args, **kwargs):
		return {}.keys(*args, **kwargs)

	def values(self, *args, includeUnnamed = False, **kwargs):
		return {}.values(*args, **kwargs)

	def items(self, *args, includeUnnamed = False, **kwargs):
		return {}.items(*args, **kwargs)

class handle_Base(Utilities, CommonEventFunctions, MyUtilities.common.ELEMENT):
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
		self.nestingAddress = []
		self.allowBuildErrors = None
		self.makeVariables = {}
		self.flags_modification = []

		self.unnamedList = []
		self.labelCatalogue = {}
		self.labelCatalogueOrder = []
		self.nestingOrder = []
		self.boundEvents = []

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
		if (self.parent is not None):
			output += f"-- parent id: {id(self.parent)}\n"
		if (self.nestingAddress is not None):
			output += f"-- nesting address: {self.nestingAddress}\n"
		if (not self.nested):
			output += f"-- Not Nested\n"
		if (self.label is not None):
			output += f"-- label: {self.label}\n"
		if (self.type is not None):
			output += f"-- type: {self.type}\n"
		if (self.thing is not None):
			output += f"-- wxObject: {type(self.thing).__name__}\n"
		if (hasattr(self, "myWindow") and (self.myWindow is not None)):
			output += f"-- Window id: {id(self.myWindow)}\n"
		if (hasattr(self, "parentSizer") and (self.parentSizer is not None)):
			output += f"-- Sizer id: {id(self.parentSizer)}\n"
		if (self.nested):
			output += "-- nested: True\n"
		if ((self.unnamedList is not None) and (len(self.unnamedList) != 0)):
			output += f"-- unnamed items: {len(self.unnamedList)}\n"
		if ((self.labelCatalogue is not None) and (len(self.labelCatalogue) != 0)):
			output += f"-- labeled items: {len(self.labelCatalogue)}\n"

		if (self.controller.printMakeVariables):
			for variable, value in self.makeVariables.items():
				output += f"-- build - {variable}: {value}\n"

		return output

	def __len__(self):
		"""Returns the number of immediate nested elements.
		Does not include elements that those nested elements may have nested.
		"""

		return len(self.labelCatalogue) + len(self.unnamedList)

	def __iter__(self):
		"""Returns an iterator object that provides the nested objects."""

		nestedList = self._getNested()
		return MyUtilities.common.CommonIterator(nestedList)

	def __getitem__(self, key):
		"""Allows the user to index the handle to get nested elements with labels."""

		return self.get(key)

	def __setitem__(self, key, value):
		"""Allows the user to index the handle to get nested elements with labels."""

		self.labelCatalogue[key] = value

	def __delitem__(self, key):
		"""Allows the user to index the handle to get nested elements with labels."""

		if (key in self):
			self._removeAddress(key)
			if (key in self.unnamedList):
				self.unnamedList.remove(key)
			else:
				if (isinstance(key, handle_Base)):
					key = key.label
				self.labelCatalogueOrder.remove(key)
				del self.labelCatalogue[key]
		else:
			if (isinstance(key, handle_Base)):
				errorMessage = f"{key.__repr__()} not in {self.__repr__()}"
			else:
				errorMessage = f"{key} not in {self.__repr__()}"
			raise KeyError(errorMessage)

	def __contains__(self, key):
		"""Allows the user to use get() when using 'in'."""

		return self.get(key, returnExists = True)

	def __enter__(self):
		"""Allows the user to use a with statement to build the GUI."""

		return self

	def __exit__(self, exc_type, exc_value, traceback):
		"""Allows the user to use a with statement to build the GUI."""

		#Error handling
		if (traceback is not None):
			if (self.allowBuildErrors is None):
				return False
			elif (not self.allowBuildErrors):
				return True

	def keys(self, *args, **kwargs):
		return labelCatalogue.keys(*args, **kwargs)

	def values(self, *args, includeUnnamed = False, **kwargs):
		if (not includeUnnamed):
			return labelCatalogue.values(*args, **kwargs)
		return list(labelCatalogue.values(*args, **kwargs)) + [*self.unnamedList]

	def items(self, *args, includeUnnamed = False, **kwargs):
		if (not includeUnnamed):
			return labelCatalogue.items(*args, **kwargs)
		return list(labelCatalogue.items(*args, **kwargs)) + [(None, item) for item in self.unnamedList]

	@contextlib.contextmanager
	def bookend_build(self, argument_catalogue, preBuild = True, postBuild = True):
		if (preBuild):
			self._preBuild(argument_catalogue)
		yield
		if (postBuild):
			self._postBuild(argument_catalogue)

	def _preBuild(self, argument_catalogue):
		"""Runs before this object is built."""

		buildSelf, label, parent = self._getArguments(argument_catalogue, ["self", "label", "parent"])
		
		#Determine parentSizer
		if (hasattr(self, "parentSizer") and (self.parentSizer is not None)):
			warnings.warn(f"{self.__repr__()} already has the sizer {self.parentSizer.__repr__()} as 'parentSizer' in _finalNest() for {buildSelf.__repr__()}\nOverwriting 'parentSizer'", Warning, stacklevel = 2)
		
		#Store data
		self.label = label
		self.attributeOverride = {} #Stores variables to override for children {label (str): {variable (str): value (any)}}
		self.attributeAppend = {} #Stores variables to add to the current variables for children {label (str): {variable (str): value (any)}}
		# self.makeFunction = inspect.stack()[2].function #The function used to create this handle
		self.makeFunction = MyUtilities.common.getCaller()

		if (buildSelf is None):
			self.parentSizer = None
			self.myWindow = None
			self.controller = None
			self.parent = None
			return

		#Determine native sizer
		if (isinstance(buildSelf, handle_Sizer)):
			self.parentSizer = buildSelf
		elif (isinstance(buildSelf, (handle_Window, Controller, handle_MenuPopup))):
			self.parentSizer = None
		elif (isinstance(buildSelf, handle_Menu) and (buildSelf.type is not Types.toolbar)):
			self.parentSizer = None
		else:
			self.parentSizer = buildSelf.parentSizer
		
		#Determine native window
		if (isinstance(buildSelf, handle_Window)):
			self.myWindow = buildSelf
		elif (isinstance(buildSelf, Controller)):
			self.myWindow = None
		else:
			self.myWindow = buildSelf.myWindow
		
		#Determine controller
		if (isinstance(buildSelf, Controller)):
			self.controller = buildSelf
		elif (not isinstance(buildSelf, handle_Window)):
			self.controller = buildSelf.myWindow.controller
		else:
			self.controller = buildSelf.controller

		#Add object to internal catalogue
		if (not isinstance(self, handle_Dialog)):
			if (label is not None):
				if (label in buildSelf.labelCatalogue):
					warnings.warn(f"Overwriting label association for {label} in {buildSelf.__repr__()}", Warning, stacklevel = 4)

				buildSelf.labelCatalogue[self.label] = self
				buildSelf.labelCatalogueOrder.append(self.label)
			else:
				buildSelf.unnamedList.append(self)

		#Determine parent
		if (parent is not None):
			self.parent = parent
		else:
			if (not isinstance(buildSelf, Controller)):
				if (isinstance(buildSelf, (handle_Menu, handle_Dialog))):
					self.parent = buildSelf
				else:
					if (buildSelf.parent is not None):
						self.parent = buildSelf.parent
					else:
						if (buildSelf.mainPanel is not None):
							self.parent = buildSelf.mainPanel
						else:
							self.parent = buildSelf
		if ((not isinstance(buildSelf, Controller)) and (self.parent is None)):
			warnings.warn(f"There is no parent for {self.__repr__()} in {buildSelf.__repr__()}", Warning, stacklevel = 2)

		#Determine Nesting Address
		if (not isinstance(self, handle_Dialog)):
			self.nestingAddress = buildSelf.nestingAddress + [id(buildSelf)]
			buildSelf._setAddressValue(self.nestingAddress + [id(self)], {None: self})

	def _postBuild(self, argument_catalogue):
		"""Runs after this object is built."""
		
		#Unpack arguments
		buildSelf = argument_catalogue["self"]
		hidden, enabled = self._getArguments(argument_catalogue, ["hidden", "enabled"])
		maxSize, minSize = self._getArguments(argument_catalogue, ["maxSize", "minSize"])
		toolTip, tabSkip = self._getArguments(argument_catalogue, ["toolTip", "tabSkip"])

		#Determine visibility
		if (isinstance(self, handle_Window)):
			if (not hidden):
				self.showWindow()
		elif (hidden):
			if (isinstance(self, handle_Sizer)):
				self._addFinalFunction(self.setShow, (None, False))
			else:
				self.setShow(False)

		#Determine disability
		if (isinstance(self, handle_Window)):
			if (not enabled):
				pass
		elif (not enabled):
			if (isinstance(self, handle_Sizer)):
				self._addFinalFunction(self.setEnable, (None, False))
			else:
				self.setEnable(False)

		#Determine size constraints
		if (isinstance(self, handle_Sizer)):
			if (maxSize is not None):
				self.parent.thing.SetMaxSize(maxSize)
			if (minSize is not None):
				self.parent.thing.SetMinSize(minSize)
		else:
			if (maxSize is not None):
				self.thing.SetMaxSize(maxSize)
			if (minSize is not None):
				self.thing.SetMinSize(minSize)

		#Determine tool tip
		if (toolTip is not None):
			self.addToolTip(toolTip)

		if (tabSkip):
			if (isinstance(self.parent, handle_NavigatorBase)):
				self._betterBind(wx.EVT_SET_FOCUS, self.thing, self.parent._onTabTraversal_child)
				self.parent.tab_skipSet.add(self.thing)
			else:
				raise NotImplementedError()

	def nest(self, handle = None, flex = 0, flags = "c1", selected = False, linkCopy = False):
		"""Nests an object inside of self.

		handle (handle) - What to place in this object
		linkCopy (bool) - Determines what to do if 'handle' is already nested
			- If True: Will nest a linked copy of 'handle'
			- If False: Will nest a copy of 'handle'
			- If None: Will raise an error

		Example Input: nest(text)
		"""

		if (isinstance(self, handle_Base_NotebookPage)):
			return self.mySizer.nest(handle = handle, flex = flex, flags = flags, selected = selected, linkCopy = linkCopy)

		#Account for automatic text sizer nesting and scroll sizer nesting
		if (isinstance(handle, handle_Sizer)):
			if ((handle.substitute is not None) and (handle.substitute != self)):
				handle = handle.substitute

		#Create a link for multi-nested objects
		if ((handle.nested) and (not isinstance(handle, handle_Menu))):
			if (linkCopy is None):
				errorMessage = f"Cannot nest {handle.__repr__()} twice"
				raise SyntaxError(errorMessage)
			else:
				handle = self.copy(handle, linkCopy = linkCopy)

		self._finalNest(handle)

		if (isinstance(handle, handle_AuiManager)):
			iuyudkj

		#Perform Nesting
		if (isinstance(self, handle_Sizer)):
			if (isinstance(flags, (tuple, range, types.GeneratorType))):
				flags = list(flags)
			elif (not isinstance(flags, list)):
				flags = [flags]
			flags.extend(handle.flags_modification)
			flags, position, border = self.getItemMod(flags)

			if (isinstance(handle, handle_Base_NotebookPage) or (isinstance(handle, handle_WidgetPicker) and (handle.type is Types.time))):
				handle.mySizerItem = self.thing.Add(handle.mySizer.thing, int(flex), eval(flags, {'__builtins__': None, "wx": wx}, {}), border)

			elif (isinstance(handle, (handle_Widget_Base, handle_Sizer, handle_Splitter, handle_Base_Notebook, handle_Panel))):
				handle.mySizerItem = self.thing.Add(handle.thing, int(flex), eval(flags, {'__builtins__': None, "wx": wx}, {}), border)

			elif (isinstance(handle, handle_Menu)):
				if (handle.type in (Types.toolbar, Types.flatmenu)):
					handle.mySizerItem = self.thing.Add(handle.thing, int(flex), eval(flags, {'__builtins__': None, "wx": wx}, {}), border)
				else:
					errorMessage = f"Add {handle.type} as a handle type for handle_Menu nesting in a handle_Window for nest() in {self.__repr__()}"
					raise SyntaxError(errorMessage)
			else:
				errorMessage = f"Add {handle.__class__} as a handle for handle_Sizer to nest() in {self.__repr__()}"
				raise SyntaxError(errorMessage)
			handle.nestedSizer = self
		
		elif (isinstance(self, handle_Panel)):
			if (isinstance(handle, handle_Sizer)):
				self.thing.SetSizer(handle.thing)
				# self.thing.SetAutoLayout(True)
				# handle.thing.Fit(self.thing)
			else:
				errorMessage = f"Add {handle.__class__} as a handle for handle_Panel to nest() in {self.__repr__()}"
				raise SyntaxError(errorMessage)
		
		elif (isinstance(self, handle_Window)):
			if (isinstance(handle, handle_Menu)):
				if (handle.type is Types.menu):
					#Main Menu
					if (self.menuBar is None):
						self.addMenuBar()
					self.menuBar.Append(handle.thing, handle.text)
				else:
					errorMessage = f"Add {handle.type} as a handle type for handle_Menu nesting in a handle_Window for nest() in {self.__repr__()}"
					raise SyntaxError(errorMessage)
			else:
				errorMessage = f"Add {handle.__class__} as a handle for handle_Window in nest() in {self.__repr__()}"
				raise SyntaxError(errorMessage)

		elif (isinstance(self, handle_Menu)):
			if (isinstance(handle, handle_Menu)):
				if (handle.type is Types.menu):
					#Sub Menu
					self.thing.Append(wx.ID_ANY, handle.text, handle.thing)
				else:
					errorMessage = f"Add {handle.type} as a handle type for handle_Menu nesting in a handle_Menu for nest() in {self.__repr__()}"
					raise SyntaxError(errorMessage)

			elif (isinstance(handle, handle_MenuItem)):
				if (handle.type is Types.menuitem):
					if (handle.shown):
						self.thing.Append(handle.thing)
				elif (handle.type is Types.toolbaritem):
					pass
				else:
					errorMessage = f"Add {handle.type} as a handle type for handle_Menu nesting in a handle_Menu for nest() in {self.__repr__()}"
					raise SyntaxError(errorMessage)

			else:
				errorMessage = f"Add {handle.__class__} as a handle for handle_Menu in nest() in {self.__repr__()}"
				raise SyntaxError(errorMessage)

		elif (isinstance(self, handle_MenuItem)):
			if (isinstance(handle, handle_Widget_Base)):
				if (self.type is Types.toolbaritem):
					self.thing = self.parent.thing.AddControl(handle.thing)
				else:
					errorMessage = f"Add {handle.type} as a self type for handle_Widget_Base nesting in a handle_MenuItem for nest() in {self.__repr__()}"
					raise SyntaxError(errorMessage)
			else:
				errorMessage = f"Add {handle.__class__} as a handle for handle_MenuItem in nest() in {self.__repr__()}"
				raise SyntaxError(errorMessage)

		elif (isinstance(self, handle_MenuPopup)):
			if (isinstance(handle, handle_MenuPopup)):
				if (handle.type is Types.menu):
					#Sub Menu
					self.contents.append(handle)
					handle.myMenu = self
				else:
					errorMessage = f"Add {handle.type} as a handle type for handle_Menu nesting in a handle_MenuPopup for nest() in {self.__repr__()}"
					raise SyntaxError(errorMessage)
			elif (isinstance(handle, handle_MenuPopupItem)):
				self.contents.append(handle)
				handle.myMenu = self

			elif (isinstance(handle, handle_MenuPopupSubMenu)):
				self.contents.append(handle)
				handle.myMenu = self

			else:
				errorMessage = f"Add {handle.__class__} as a handle for handle_MenuPopup in nest() in {self.__repr__()}"
				raise SyntaxError(errorMessage)
					
		elif (isinstance(self, handle_WidgetInput)):
			if (self.type is Types.search):
				if (isinstance(handle, handle_Menu)):
					if (handle.type is Types.menu):
						#Sub Menu
						if (handle.label is not None):
							self.thing.SetMenu(handle.thing)
						else:
							self.thing.SetMenu(None)
					else:
						errorMessage = f"Add {handle.type} as a handle type for handle_Menu nesting in a handle_WidgetInput for nest() in {self.__repr__()}"
						raise SyntaxError(errorMessage)
				else:
					errorMessage = f"Add {handle.__class__} as a handle type for handle_Menu nesting in a handle_WidgetInput for nest() in {self.__repr__()}"
					raise SyntaxError(errorMessage)
			else:
				errorMessage = f"Add {self.type.name} as a handle type for handle_WidgetInput in nest() in {self.__repr__()}"
				raise SyntaxError(errorMessage)
		else:
			errorMessage = f"Add {self.__class__} as self to nest() in {self.__repr__()}"
			raise SyntaxError(errorMessage)

		#Select if needed
		if (selected):
			handle.thing.SetDefault()

	def link(self, handle, functionName = None, label = None):
		"""Links this handle to another for the given function.
		Modified code from: https://www.blog.pythonlibrary.org/2013/09/04/wxpython-how-to-update-a-progress-bar-from-a-thread/
		Use: http://pypubsub.sourceforge.net/v3.1/apidocs/more_advanced_use.html
		Use: https://pypubsub.readthedocs.io/en/v4.0.0/usage/module_pub.html
		Special thanks to James Johnson for how to use types() to create a class on http://jelly.codes/articles/python-dynamically-creating-classes/
		Special thanks to user166390 and pyfunc for how to replace a bound function respectively on https://stackoverflow.com/questions/1647586/is-it-possible-to-change-an-instances-method-implementation-without-changing-al and https://stackoverflow.com/questions/4364565/replacing-the-new-module

		handle (handle) - What will be linked to this handle
			- If list: A list of handles to be linked to this handle and together
			- If not handle: Will use this as a key to look it up in 'self'

		functionName (str) - The name of the function to link
			~ Can be anything callable, not just a function
			- If list: A list of function names to link
			- If dict: {label (str): functionName (str)}
			- If None: Will link all setter functions for both handles

		label (str) - What this link is called
			~ Ignored if 'functionName' is a dictionary
			- If None: Will use a label unique to 'self' and 'handle'
		_________________________________________________________________________
					
		EXAMPLE USE:
			mainWidget = mySizer.addInputBox()
			mainWidget.setFunction_click(self.updateSomething)

			mirrorWidget = mySizer.addInputBox()
			mirrorWidget.setFunction_click(self.updateSomething)

			mainWidget.link(mirrorWidget, "setValue")
			# mainWidget.link(mirrorWidget, self.updateSomething)
			mainWidget.linkEvent(mirrorWidget, wx.EVT_TEXT)
		_________________________________________________________________________

		Example Input: link(handle)
		Example Input: link(handle, "setValue")
		Example Input: link(handle, self.setValue)
		Example Input: link(handle, ["setValue", "getValue"])
		Example Input: link([myInputBox, "changableText"], "setValue")

		Example Input: link(handle, "setValue", label = "Modify Text")
		Example Input: link(handle, ["setValue", "getValue"], label = "Text")
		Example Input: link(handle, {"Modify Text": "setValue", "Get Text": "getValue"])
		Example Input: link([myInputBox, "changableText"], {"Modify Text": "setValue", "Get Text": "getValue"])

		Example Input: link(handle, {"Modify Text": "setValue", None: "getValue"])
		Example Input: link(handle, {"Modify Text": "setValue", None: ["getValue", self.getSelection])
		"""
		global topicManager

		def getTopicFunction(function):
			"""Returns a configured function that will link with the wrapper in makeLink()."""

			#Determine args, kwargs, and their respective defaults
			argList, starArgs, starStarKwargs, argsDefaults, kwargList, kwargsDefaults, annotations = inspect.getfullargspec(function)
			
			args_noDefaults = []
			args_withDefaults = {}
			if (argsDefaults is not None):
				argsDefaults_startsAt = len(argList) - len(argsDefaults) - 1
			for i, variable in enumerate(argList):
				if ((i == 0) and (inspect.ismethod(function))):
					args_noDefaults.append(variable)
					continue #skip self

				if ((argsDefaults is None) or (i < argsDefaults_startsAt)):
					args_noDefaults.append(variable)
				else:
					args_withDefaults[variable] = argsDefaults[i - argsDefaults_startsAt - 1]

			kwargs_noDefaults = []
			kwargs_withDefaults = {}#"linkedHandle_catalogue": None}
			for variable in kwargList:
				if ((kwargsDefaults is None) or (variable not in kwargsDefaults)):
					kwargs_noDefaults.append(variable)
				else:
					kwargs_withDefaults[variable] = kwargsDefaults[variable]

			#The pypubsub module does not accept the names of the args and kwargs as valid values
			#This patches that behavior
			if (starArgs is not None):
				kwargs_withDefaults[starArgs] = []
			else:
				kwargs_withDefaults["args"] = []

			if (starStarKwargs is not None):
				kwargs_withDefaults[starStarKwargs] = {}
			else:
				kwargs_withDefaults["kwargs"] = {}

			#Create function that will be used to create the subscription topic
			recipe_part1 = ", ".join(args_noDefaults)
			recipe_part2 = ", ".join(f"{key} = {value}" for key, value in args_withDefaults.items())
			recipe_part3 = f"*{starArgs}_patchFor_pypubsub" if (starArgs is not None) else "*args_patchFor_pypubsub"
			recipe_part4 = ", ".join(kwargs_noDefaults)
			recipe_part5 = ", ".join(f"{key} = {value}" for key, value in kwargs_withDefaults.items())
			recipe_part6 = f"**{starStarKwargs}_patchFor_pypubsub" if (starStarKwargs is not None) else "**kwargs_patchFor_pypubsub"
			recipe = f"lambda {', '.join(filter(None, [recipe_part1, recipe_part2, recipe_part3, recipe_part4, recipe_part5, recipe_part6]))}: None"

			if (inspect.ismethod(myFunction)):
				topicFunction = type("Temp", (object,), {"tempFunction": eval(recipe)})().tempFunction
			else:
				topicFunction = eval(recipe)

			return topicFunction

		def makeLink(function, label):
			@functools.wraps(function)
			def wrapper(self, *args, **kwargs):
				nonlocal function, label

				arguments = inspect.getcallargs(function, *args, **kwargs)
				del arguments["self"]
				pubsub_pub.sendMessage(label, **arguments)
			
			setattr(function.__self__, function.__name__, types.MethodType(wrapper, function.__self__)) #Replace function with wrapped function
			pubsub_pub.subscribe(function, label)

		def checkFit(function, topic, topicFunction):
			"""Ensures that the function fits with the given topic."""
				
			try:
				topic.validate(function)
				return
			except Exception as error:
				print("Origonal Error:", error)

			required, optional = topic.getArgs()
			argList, starArgs, starStarKwargs, argsDefaults, kwargList, kwargsDefaults, annotations = inspect.getfullargspec(handleFunction)
			
			unknownList = [item for item in [*argList, *kwargList] if item not in [*required, *optional]]
			errorMessage = f"The variables {unknownList} in the linked function {function} are not defined in the source function {topicFunction} labeled {topic.getName()}"
			raise KeyError(errorMessage)

		#########################################################################

		if (not isinstance(handle, (list, tuple))):
			handle = [handle]

		if (functionName is None):
			# functionName = [item[0] for item in inspect.getmembers(self, predicate = inspect.ismethod) if (item[0].startswith("set"))]# + self.boundEvents
			functionName = [self.setValue]
		elif (not isinstance(functionName, (list, tuple, dict))):
			functionName = [functionName]

		if (isinstance(functionName, dict)):
			myList = list(functionName.keys())
		else:
			myList = functionName

		linkCatalogue = {}
		for _functionName in myList:
			if (isinstance(_functionName, wx.PyEventBinder)):
				print(eventCatalogue[_functionName.typeId])
				jhkkjk

			if (not isinstance(_functionName, str)):
				_functionName = _functionName.__name__
			if (isinstance(functionName, dict)):
				label = functionName[_functionName]
			if (label is None):
				_label = f"{id(self)}:{_functionName}"
			else:
				_label = label
			linkCatalogue[_functionName] = _label

		for _functionName, _label in linkCatalogue.items():
			myFunction = getattr(self, _functionName)
			topicFunction = getTopicFunction(myFunction)
			topic = topicManager.getOrCreateTopic(_label, protoListener = topicFunction)
			makeLink(myFunction, _label)

			for _handle in handle:
				if (not isinstance(_handle, handle_Base)):
					_handle = self[_handle]

				handleFunction = getattr(_handle, _functionName)
				checkFit(handleFunction, topic, myFunction)
				makeLink(handleFunction, _label)

	def copy(self, handle, includeNested = True, linkCopy = False):
		"""Creates a copy of this widget and everything that is nested in it, using 'self'.

		handle (handle) - What to copy
		includeNested (bool) - Determines if nested children are copied as well
		linkCopy (bool) - Determines if the created copy should be linked to the origonal

		Example Input: copy(handle)
		Example Input: copy(handle, includeNested = False)
		Example Input: copy(handle, linkCopy = True)
		Example Input: copy(handle, includeNested = False, linkCopy = True)
		"""

		if (not hasattr(self, handle.makeFunction)):
			errorMessage = f"The function {handle.makeFunction} is not in {self.__repr__()}"
			raise SyntaxError(errorMessage)

		makeFunction = getattr(self, handle.makeFunction)
		newHandle = makeFunction(**handle.makeVariables)

		if (linkCopy):
			handle.link(newHandle)

		if (includeNested):
			for child in handle[:]:
				newChild = newHandle.copy(child)
				newHandle.nest(newChild)

				if (linkCopy):
					child.link(newChild)

		return newHandle

	def clear(self):
		"""Removes all nested widgets.

		Example Input: clear()
		"""

		for item in self.get(slice(None, None, None), checkNested = False):
			item.remove()

	def remove(self):
		"""Removes this item from it's sizer.

		Example Input: remove()
		"""

		if (isinstance(self, handle_Sizer)):
			self.clear()

		if (isinstance(self.nestedParent, handle_Sizer)):
			index = self.getSizerIndex()
			self.nestedParent.thing.Hide(index)
			self.nestedParent.thing.Remove(index)
			self.nestedParent.thing.Layout()

		else:
			errorMessage = f"Add {self.nestedParent.__class__} to remove() for {self.__repr__()}"
			raise KeyError(errorMessage)

		del self.nestedParent[self]

	def getNestedParent(self):
		"""Returns the handle for the object that nests this handle.

		Example Input: getNestedParent()
		"""

		return self.nestedParent

	def onTriggerEvent(self, event, *args, **kwargs):
		"""A wxEvent version of triggerEvent().

		Example Use: myWidget.setFunction_click(self.onTriggerEvent, myFunctionArgs = (self.EVT_FINISHED,))
		Example Use: myWidget.setFunction_click(self.onTriggerEvent, myFunctionKwargs = {"eventType": self.EVT_FINISHED, "okFunction": self.hideWindow, "okFunctionKwargs": {"modalId": wx.ID_OK}})
		"""

		self.triggerEvent(*args, **kwargs)
		event.Skip()

	def triggerEvent(self, eventType = None, *, returnEvent = False,
		okFunction = None, okFunctionArgs = None, okFunctionKwargs = None,
		vetoFunction = None, vetoFunctionArgs = None, vetoFunctionKwargs = None, **kwargs):
		"""Allows the user to easily trigger an event remotely.

		Example Input: triggerEvent(self.EVT_PAGE_CHANGED)
		Example Input: triggerEvent(self.EVT_PAGE_CHANGING, returnEvent = True, fromNode = self.currentNode, toNode = node)
		Example Input: triggerEvent(self.EVT_FINISHED, okFunction = self.hideWindow, okFunctionKwargs = {"modalId": wx.ID_OK})
		"""

		assert eventType
		newEvent = eventType(self, **kwargs)
		self.thing.GetEventHandler().ProcessEvent(newEvent)
		if (returnEvent):
			return newEvent

		if (newEvent.IsVetoed()):
			self.runMyFunction(vetoFunction, vetoFunctionArgs, vetoFunctionKwargs)
			return False

		self.runMyFunction(okFunction, okFunctionArgs, okFunctionKwargs)
		return True

	#Getters
	def getLabel(self, event = None):
		"""Returns the label for this object."""

		return self.label

	def getSize(self, event = None):
		"""Returns the size of the wxObject."""

		if (self.thing is None):
			size = None
		else:
			size = self.thing.GetSize()

		return size

	def getType(self, event = None):
		"""Returns the type for this object."""

		data = {}
		data["type"] = self.type
		data["self"] = self.__class__.__name__
		data["thing"] = self.thing.__class__.__name__

		return data

	def getFocus(self, event = None):
		"""Returns the item that is focused.
		Does not need to be nested in self or on the same window as self.
		"""

		def nestCheck(itemList, wxObject):
			"""Makes sure everything is nested."""

			answer = None
			for item in itemList:
				if (wxObject == item.thing):
					return item
				
				answer = nestCheck(item[:], wxObject)
				if (answer is not None):
					return answer
			return answer

		##################################################

		if (isinstance(self.thing, wx.Window)):
			wxObject = self.thing.FindFocus()
		elif (self.myWindow is not None):
			wxObject = self.myWindow.thing.FindFocus()
		else:
			return
		if (wxObject is None):
			raise NotImplementedError()

		handle = nestCheck(self[:], wxObject)
		if ((handle is None) and (self.myWindow is not None)):
			handle = nestCheck(self.myWindow[:], wxObject)
		if ((handle is None) and (self.controller is not None)):
			handle = nestCheck(self.controller[:], wxObject)
		return handle

	#Setters
	def setFunction_size(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		self._betterBind(wx.EVT_SIZE, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)

	def setFunction_position(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		self._betterBind(wx.EVT_MOVE, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)

	def setSize(self, size, event = None, atleast = None):
		"""Sets the size of the wxObject.

		atleast (bool) - Determines if the size should be atleast or atmost the given size
			- If True: Only changes the size if it is less than the given size
			- If False: Only changes the size if it is greater than the given size
			- If None: Changes the size, regardless of the current size
		"""

		if (self.thing is None):
			return

		if (atleast is None):
			self.thing.SetSize(size)
			return

		oldSize = self.thing.GetSize()
		newSize = [item for item in oldSize]
		if (atleast):
			if (oldSize[0] < size[0]):
				newSize[0] = size[0]
			if (oldSize[1] < size[1]):
				newSize[1] = size[1]
		else:
			if (oldSize[0] > size[0]):
				newSize[0] = size[0]
			if (oldSize[1] > size[1]):
				newSize[1] = size[1]
		self.thing.SetSize(newSize)

	#Etc
	@contextlib.contextmanager
	def frozen(self):
		try:
			self.thing.Freeze()
			yield

		finally:
			self.thing.Thaw()

	def setFocus(self):
		"""Sets the focus to this handle's wx object."""

		self.thing.SetFocus()

	def onRefresh(self, event, *args, **kwargs):
		"""A wxEvent version of refresh()."""

		self.refresh(*args, **kwargs)
		event.Skip()

	def refresh(self, updateNested = True, useSizeEvent = True):
		def applyUpdateNested(itemList):
			"""Makes sure that all nested objects call their update functions."""

			for item in itemList:
				if (item is None):
					continue

				elif (isinstance(item, (handle_MenuPopup, handle_Menu, handle_MenuItem, handle_MenuPopupItem, handle_MenuPopupSubMenu))):
					applyUpdateNested(item[:])

				elif (isinstance(item, handle_Base_NotebookPage)):
					applyUpdateNested([item.mySizer, item.myPanel])

				elif (item.thing is None):
					hjhkjjh

				elif (isinstance(item, handle_WidgetTable)):
					#Not working
					item.thing.ForceRefresh()
					item.thing.Layout()

					if (useSizeEvent):
						self.thing.SendSizeEvent()
					else:
						self.thing.Layout()
						self.thing.Refresh()

				elif (isinstance(item, handle_Sizer)):
					item.thing.Layout()
					applyUpdateNested(item[:])

				else:
					item.thing.Refresh()
					item.thing.Layout()
					applyUpdateNested(item[:])

			##################################################

		if (updateNested):
			applyUpdateNested(self[:])

		if (useSizeEvent and (hasattr(self.thing, "SendSizeEvent"))):
			self.thing.SendSizeEvent()
		else:
			if (hasattr(self.thing, "ForceRefresh")):
				self.thing.ForceRefresh()
			if (hasattr(self.thing, "Layout")):
				self.thing.Layout()
			if (hasattr(self.thing, "Refresh")):
				self.thing.Refresh()

	def _readBuildInstructions_sizer(self, parent, i, instructions):
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

		del instructions["type"]

		#Get Default build arguments
		if (sizerType == "grid"):
			sizer = parent._makeSizerGrid(**instructions)
		elif (sizerType == "flex"):
			sizer = parent._makeSizerGridFlex(**instructions)
		elif (sizerType == "bag"):
			sizer = parent._makeSizerGridBag(**instructions)
		elif (sizerType == "box"):
			sizer = parent._makeSizerBox(**instructions)
		elif (sizerType == "text"):
			sizer = parent._makeSizerText(**instructions)
		else:
			sizer = parent._makeSizerWrap(**instructions)

		return sizer

	def _readBuildInstructions_panel(self, parent, i, instructions):
		"""Interprets instructions given by the user for what panel to make and how to make it."""

		if (not isinstance(instructions, dict)):
			errorMessage = f"panel_{i} must be a dictionary for {self.__repr__()}"
			raise ValueError(errorMessage)

		#Finish building panel
		panel = parent._makePanel(**instructions)
		panel.index = i

		return panel

	def getNestedParent(self, n = 0):
		"""Returns the requested nesting parent up the nest hiarchy.

		n (int) - How many levels up the nesting hiarchy to go

		Example Input: getNestedParent()
		Example Input: getNestedParent(n = 1)
		"""

		if (n > 0):
			return self.nestedParent.getNestedParent(n = n - 1)
		return self.nestedParent

	def getSizerCoordinates(self, n = 0):
		"""Returns the current row and column this item is in it's nested sizer.
		Returns None for row and/or column if it is not nested in a sizer or the respective variable is not defined in the sizer.

		Example Input: getSizerCoordinates()
		"""

		if (n > 0):
			return self.nestedParent.getSizerCoordinates(n = n - 1)

		index = self.getSizerIndex()
		row = self.getSizerRow(index = index)
		column = self.getSizerColumn(index = index)

		return row, column

	def getSizerRow(self, index = None, n = 0):
		"""Returns the current row this item is in it's nested sizer.
		Returns None if it is not nested in a sizer or the sizer has no defined rows.
		Special thanks to user829323 for how to get row and column with a grid index on https://stackoverflow.com/questions/15510497/how-can-i-get-grid-row-col-position-given-an-item-index

		n (int) - How many levels up the nesting hiarchy to go

		Example Input: getSizerRow()
		Example Input: getSizerRow(n = 1)
		"""

		if (not isinstance(self.nestedParent, handle_Sizer)):
			errorMessage = f"Add {self.nestedParent.__class__} to getSizerRow() for {self.__repr__()}"
			raise KeyError(errorMessage)

		if (n > 0):
			return self.nestedParent.getSizerRow(n = n - 1)

		if (self.nestedParent.type is Types.wrap):
			return #TO DO: Calculate what the position is

		if (self.nestedParent.rows is None):
			return

		if (index is None):
			index = self.getSizerIndex()

		if (self.nestedParent.rows == -1):
			return index

		row = math.floor(index / self.nestedParent.columns)

		return row

	def getSizerColumn(self, index = None, n = 0):
		"""Returns the current column this item is in it's nested sizer.
		Returns None if it is not nested in a sizer or the sizer has no defined columns.
		Special thanks to user829323 for how to get row and column with a grid index on https://stackoverflow.com/questions/15510497/how-can-i-get-grid-row-col-position-given-an-item-index

		Example Input: getSizerColumn()
		"""
		
		if (not isinstance(self.nestedParent, handle_Sizer)):
			errorMessage = f"Add {self.nestedParent.__class__} to getSizerColumn() for {self.__repr__()}"
			raise KeyError(errorMessage)

		if (n > 0):
			return self.nestedParent.getSizerColumn(n = n - 1)

		if (self.nestedParent.type is Types.wrap):
			return #TO DO: Calculate what the position is

		if (self.nestedParent.columns is None):
			return

		if (index is None):
			index = self.getSizerIndex()
		
		if (self.nestedParent.columns == -1):
			return index

		column = index % self.nestedParent.columns

		return column

	def getSizerIndex(self, n = 0):
		"""Returns the index number of the sizer item in it's nested sizer.

		Example Input: getSizerIndex()
		"""
		
		if (not isinstance(self.nestedParent, handle_Sizer)):
			errorMessage = f"Add {self.nestedParent.__class__} to getSizerIndex() for {self.__repr__()}"
			raise KeyError(errorMessage)

		if (n > 0):
			return self.nestedSizer.getSizerIndex(n = n - 1)

		for i, item in enumerate(self.nestedSizer.thing.GetChildren()):
			if (item == self.mySizerItem):
				return i

		errorMessage = f"Could not find sizer item index in remove() for {self.__repr__()}"
		raise SyntaxError(errorMessage)

	def _decodePrintSettings(self, dialogData):
		"""Turns a wxPrintDialogData object into a dictionary."""

		printData = dialogData.GetPrintData()
		data = {"bin": _MyPrinter.catalogue_printBin[printData.GetBin()],
			"color": printData.GetColour(),
			"duplex": _MyPrinter.catalogue_duplex[printData.GetDuplex()],
			"file": printData.GetFilename(),
			"vertical": _MyPrinter.catalogue_orientation[printData.GetOrientation()],
			"paperId": _MyPrinter.catalogue_paperId[printData.GetPaperId()],
			"paperSize": tuple(printData.GetPaperSize()),
			"printMode": _MyPrinter.catalogue_printMode[printData.GetPrintMode()],
			"printerName": printData.GetPrinterName(),
			"quality": _MyPrinter.catalogue_quality.get(printData.GetQuality(), printData.GetQuality())}

		if (isinstance(dialogData, wx.PageSetupDialogData)):
			data[None] = wx.PageSetupDialogData(dialogData)
			data["marginMinimum"] = dialogData.GetDefaultMinMargins()
			data["marginLeft"], data["marginTop"] = dialogData.GetMarginTopLeft()
			data["marginRight"], data["marginBottom"] = dialogData.GetMarginBottomRight()
			data["marginLeftMinimum"], data["marginTopMinimum"] = dialogData.GetMinMarginTopLeft()
			data["marginRightMinimum"], data["marginBottomMinimum"] = dialogData.GetMinMarginBottomRight()
		else:
			data[None] = wx.PrintDialogData(dialogData)
			data["collate"] = dialogData.GetCollate()
			data["copies"] = dialogData.GetNoCopies()
			data["printAll"] = dialogData.GetAllPages()
			data["from"] = dialogData.GetFromPage()
			data["to"] = dialogData.GetToPage()
			data["min"] = dialogData.GetMinPage()
			data["max"] = dialogData.GetMaxPage()
			data["printToFile"] = dialogData.GetPrintToFile()
			data["selected"] = dialogData.GetSelection()

		return data

	def _encodePrintSettings(self, data, setupData = False, override = {}):
		"""Turns a dictionary into a wxPrintDialogData object."""

		if (data is None):
			if (not override):
				return
			data = override
		elif ((not override) or (all(value is None for value in override.values()))):
			if (isinstance(data, wx.PrintData)):
				return wx.PrintDialogData(data)
			elif (isinstance(data, wx.PrintDialogData) and (not setupData)):
				return data
			elif (isinstance(data, wx.PageSetupDialogData) and (setupData)):
				return data

		isDict = isinstance(data, dict)
		def getValue(variable, getter, default = None):
			nonlocal override, isDict

			if (isinstance(variable, tuple)):
				if (all((key not in override) or (override[key] is None) for key in variable)):
					return tuple(data.get(key, default) for key in variable)
				
				value = []
				for i, key in enumerate(variable.keys()):
					if ((key in override) and (override[key] is not None)):
						value.append(override[key])
					elif (isDict):
						value.append(data.get(key, default))
					else:
						value.append(getter()[i])
				return tuple(value)

			elif ((variable in override) and (override[variable] is not None)):
				return override[variable]
			elif (isDict):
				return data.get(variable, default)
			return getter()

		def apply(variable, setter, getter, catalogue = None, default = None):
			value = getValue(variable, getter, default)

			if (value is not None):
				if (not catalogue):
					return setter(value)
				elif (value in catalogue.values()):
					return setter(next(_key for _key, _value in catalogue.items() if (_value == value)))
				return setter(value)

		##################################################
		
		if (isinstance(data, (wx.PrintDialogData, wx.PageSetupDialogData))):
			printData = data.GetPrintData()
		elif (isinstance(data, wx.PrintData)):
			printData = data
		else:
			printData = wx.PrintData()

		apply("color", printData.SetColour, printData.GetColour)
		apply("file", printData.SetFilename, printData.GetFilename)
		apply("paperSize", printData.SetPaperSize, printData.GetPaperSize)
		apply("printerName", printData.SetPrinterName, printData.GetPrinterName)
		apply("bin", printData.SetBin, printData.GetBin, _MyPrinter.catalogue_printBin)
		apply("duplex", printData.SetDuplex, printData.GetDuplex, _MyPrinter.catalogue_duplex)
		apply("quality", printData.SetQuality, printData.GetQuality, _MyPrinter.catalogue_quality)
		apply("paperId", printData.SetPaperId, printData.GetPaperId, _MyPrinter.catalogue_paperId)
		apply("printMode", printData.SetPrintMode, printData.GetPrintMode, _MyPrinter.catalogue_printMode)
		apply("vertical", printData.SetOrientation, printData.GetOrientation, _MyPrinter.catalogue_orientation)

		if (setupData):
			dialogData = wx.PageSetupDialogData(printData)
			apply("marginMinimum", dialogData.SetDefaultMinMargins, dialogData.GetDefaultMinMargins)
			apply(("marginLeft", "marginTop"), dialogData.SetMarginTopLeft, dialogData.GetMarginTopLeft, default = 0)
			apply(("marginRight", "marginBottom"), dialogData.SetMarginBottomRight, dialogData.GetMarginBottomRight, default = 0)
			apply(("marginLeftMinimum", "marginTopMinimum"), dialogData.SetMinMarginTopLeft, dialogData.GetMinMarginTopLeft, default = 0)
			apply(("marginRightMinimum", "marginBottomMinimum"), dialogData.SetMinMarginBottomRight, dialogData.GetMinMarginBottomRight, default = 0)
		else:
			dialogData = wx.PrintDialogData(printData)
			apply("collate", dialogData.SetCollate, dialogData.GetCollate)
			apply("min", dialogData.SetMinPage, dialogData.GetMinPage)
			apply("max", dialogData.SetMaxPage, dialogData.GetMaxPage)
			apply("copies", dialogData.SetNoCopies, dialogData.GetNoCopies)
			apply("printToFile", dialogData.SetPrintToFile, dialogData.GetPrintToFile)
			apply("selected", dialogData.SetSelection, dialogData.GetSelection)

			if (data.get("printAll", None)):
				dialogData.SetFromPage(dialogData.GetMinPage())
				dialogData.SetToPage(dialogData.GetMaxPage())
			else:
				apply("from", dialogData.SetFromPage, dialogData.GetFromPage)
				apply("to", dialogData.SetToPage, dialogData.GetToPage)

		return dialogData

	def print(self, document = None, printData = None, title = "Document", raw = False, override = {}, popup = False):
		"""Does all the heavy lifting for printing a document.

		raw (bool) - Determines how the data is sent to the printer
				- If True: Sends the data as RAW
				- If False: Sends the data normally

		Example Input: print("Lorem Ipsum", popup = True)
		Example Input: print(self.content, printData = self.data[None], title = self.title, raw = raw, popup = False)
		Example Input: print(self.GetPrintoutForPrinting(), popup = prompt)
		"""

		if (isinstance(document, _MyPrintout)):
			myPrintout = document
			destroyPrintout = False
		else:
			myPrintout = _MyPrintout(self, document = document, title = title, raw = raw)
			destroyPrintout = True

		if (isinstance(printData, _MyPrinter)):
			myPrinter = printData
		else:
			myPrinter = _MyPrinter(self, data = printData, override = override)

		try:
			if (not myPrinter.Print(None, myPrintout, popup)):
				return
			else:
				return True# wx.PrintDialogData(myPrinter.GetPrintDialogData())
		finally:
			if (destroyPrintout):
				myPrintout.Destroy()

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

	def _overloadHelp(self, myFunction, label, args, kwargs, window = False):
		"""Helps the overloaded functions to stay small.

		Example Input: _overloadHelp("toggleEnable")
		"""

		def runFunction(handle):
			if (handle is self):
				return []

			function = getattr(handle, myFunction)
			if (isinstance(handle, handle_Sizer)):
				answer = function(None, *args, **kwargs)
			else:
				answer = function(*args, **kwargs)

			if (not isinstance(answer, list)):
				answer = [answer]
			return answer

		#############################################################

		#Account for all nested
		if (label is None):
			if (window):
				function = getattr(handle_Widget_Base, myFunction)
				answer = function(self, *args, **kwargs)
				return answer
			else:
				answerList = []
				for handle in self:
					answerList.extend(runFunction(handle))
				return answerList
		else:
			#Account for multiple objects
			if (not isinstance(label, (list, tuple, range, set, types.GeneratorType))):
				labelList = [label]
			else:
				labelList = label

			answerList = []
			for label in labelList:
				handle = self.get(label, checkNested = True)
				answerList.extend(runFunction(handle))

			if ((not isinstance(label, (list, tuple, range))) and (len(answerList) == 1)):
				return answerList[0]
			return answerList

	#Standard Functions
	def getValue(self, label = None, *args, window = False, **kwargs):
		"""Overload for getValue for handle_Widget_Base."""

		answer = self._overloadHelp("getValue", label, args, kwargs, window = window)
		return answer

	def getIndex(self, label = None, *args, window = False, **kwargs):
		"""Overload for getIndex for handle_Widget_Base."""

		answer = self._overloadHelp("getIndex", label, args, kwargs, window = window)
		return answer

	def getAll(self, label = None, *args, window = False, **kwargs):
		"""Overload for getAll for handle_Widget_Base."""

		answer = self._overloadHelp("getAll", label, args, kwargs, window = window)
		return answer

	def getSelection(self, label = None, *args, window = False, **kwargs):
		"""Overload for getSelection for handle_Widget_Base."""

		answer = self._overloadHelp("getSelection", label, args, kwargs, window = window)
		return answer

	def getLabel(self, label = None, *args, window = False, **kwargs):
		"""Overload for getLabel for handle_Widget_Base."""

		answer = self._overloadHelp("getLabel", label, args, kwargs, window = window)
		return answer

	def setValue(self, label = None, *args, window = False, **kwargs):
		"""Overload for setValue for handle_Widget_Base."""

		answer = self._overloadHelp("setValue", label, args, kwargs, window = window)
		return answer

	def setSelection(self, label = None, *args, window = False, **kwargs):
		"""Overload for setSelection for handle_Widget_Base."""

		answer = self._overloadHelp("setSelection", label, args, kwargs, window = window)
		return answer

	#Change State
	##Enable / Disable
	@wrap_skipEvent()
	def onToggleEnable(self, event, *args, **kwargs):
		"""A wx.CommandEvent version of toggleEnable."""

		self.toggleEnable(*args, event = event, **kwargs)

	def toggleEnable(self, label = None, *args, window = False, **kwargs):
		"""Overload for toggleEnable in handle_Widget_Base."""

		self._overloadHelp("toggleEnable", label, args, kwargs, window = window)

	@wrap_skipEvent()
	def onSetEnable(self, event, *args, **kwargs):
		"""A wx.CommandEvent version of setEnable."""

		self.setEnable(*args, event = event, **kwargs)

	def setEnable(self, label = None, *args, window = False, **kwargs):
		"""Overload for setEnable in handle_Widget_Base."""

		self._overloadHelp("setEnable", label, args, kwargs, window = window)

	@wrap_skipEvent()
	def onSetDisable(self, event, *args, **kwargs):
		"""A wx.CommandEvent version of setDisable."""

		self.setDisable(*args, event = event, **kwargs)

	def setDisable(self, label = None, *args, window = False, **kwargs):
		"""Overload for setDisable in handle_Widget_Base."""

		self._overloadHelp("setDisable", label, args, kwargs, window = window)

	@wrap_skipEvent()
	def onEnable(self, event, *args, **kwargs):
		"""A wx.CommandEvent version of enable."""

		self.enable(*args, event = event, **kwargs)

	def enable(self, label = None, *args, window = False, **kwargs):
		"""Overload for enable in handle_Widget_Base."""

		self._overloadHelp("enable", label, args, kwargs, window = window)

	@wrap_skipEvent()
	def onDisable(self, event, *args, **kwargs):
		"""A wx.CommandEvent version of disable."""

		self.disable(*args, event = event, **kwargs)

	def disable(self, label = None, *args, window = False, **kwargs):
		"""Overload for disable in handle_Widget_Base."""

		self._overloadHelp("disable", label, args, kwargs, window = window)

	def checkEnabled(self, label = None, *args, window = False, **kwargs):
		"""Overload for checkEnabled in handle_Widget_Base."""

		answer = self._overloadHelp("checkEnabled", label, args, kwargs, window = window)
		return answer

	def checkDisabled(self, label = None, *args, window = False, **kwargs):
		"""Overload for checkDisabled in handle_Widget_Base."""

		answer = self._overloadHelp("checkDisabled", label, args, kwargs, window = window)
		return answer

	##Show / Hide
	@wrap_skipEvent()
	def onToggleShow(self, event, *args, **kwargs):
		"""A wx.CommandEvent version of toggleShow."""

		self.toggleShow(*args, event = event, **kwargs)

	def toggleShow(self, label = None, *args, window = False, **kwargs):
		"""Overload for toggleShow in handle_Widget_Base."""

		self._overloadHelp("toggleShow", label, args, kwargs, window = window)

	@wrap_skipEvent()
	def onSetShow(self, event, *args, **kwargs):
		"""A wx.CommandEvent version of setShow."""

		self.setShow(*args, event = event, **kwargs)

	def setShow(self, label = None, *args, window = False, **kwargs):
		"""Overload for setShow in handle_Widget_Base."""

		self._overloadHelp("setShow", label, args, kwargs, window = window)

	@wrap_skipEvent()
	def onSetHide(self, event, *args, **kwargs):
		"""A wx.CommandEvent version of setHide."""

		self.setHide(*args, event = event, **kwargs)

	def setHide(self, label = None, *args, window = False, **kwargs):
		"""Overload for setHide in handle_Widget_Base."""

		self._overloadHelp("setHide", label, args, kwargs, window = window)

	@wrap_skipEvent()
	def onShow(self, event, *args, **kwargs):
		"""A wx.CommandEvent version of show."""

		self.show(*args, event = event, **kwargs)

	def show(self, label = None, *args, window = False, **kwargs):
		"""Overload for show in handle_Widget_Base."""

		self._overloadHelp("show", label, args, kwargs, window = window)

	@wrap_skipEvent()
	def onHide(self, event, *args, **kwargs):
		"""A wx.CommandEvent version of hide."""

		self.hide(*args, event = event, **kwargs)

	def hide(self, label = None, *args, window = False, **kwargs):
		"""Overload for hide in handle_Widget_Base."""

		self._overloadHelp("hide", label, args, kwargs, window = window)

	def checkShown(self, label = None, *args, window = False, **kwargs):
		"""Overload for checkShown in handle_Widget_Base."""

		answer = self._overloadHelp("checkShown", label, args, kwargs, window = window)
		return answer

	def checkHidden(self, label = None, *args, window = False, **kwargs):
		"""Overload for checkHidden in handle_Widget_Base."""

		answer = self._overloadHelp("checkHidden", label, args, kwargs, window = window)
		return answer

	##Modified
	@wrap_skipEvent()
	def onModify(self, event, *args, **kwargs):
		"""A wx.CommandEvent version of modify."""

		self.modify(*args, event = event, **kwargs)

	def modify(self, label = None, *args, window = False, **kwargs):
		"""Overload for modify in handle_Widget_Base."""

		self._overloadHelp("modify", label, args, kwargs, window = window)

	@wrap_skipEvent()
	def onSetModified(self, event, *args, **kwargs):
		"""A wx.CommandEvent version of setModified."""

		self.setModified(*args, event = event, **kwargs)

	def setModified(self, label = None, *args, window = False, **kwargs):
		"""Overload for setModified in handle_Widget_Base."""

		self._overloadHelp("setModified", label, args, kwargs, window = window)

	def checkModified(self, label = None, *args, window = False, **kwargs):
		"""Overload for checkModified in handle_Widget_Base."""

		answer = self._overloadHelp("checkModified", label, args, kwargs, window = window)
		return answer

	##Read Only
	@wrap_skipEvent()
	def onReadOnly(self, event, *args, **kwargs):
		"""A wx.CommandEvent version of readOnly."""

		self.readOnly(*args, event = event, **kwargs)

	def readOnly(self, label = None, *args, window = False, **kwargs):
		"""Overload for readOnly in handle_Widget_Base."""

		self._overloadHelp("readOnly", label, args, kwargs, window = window)

	@wrap_skipEvent()
	def onSetReadOnly(self, event, *args, **kwargs):
		"""A wx.CommandEvent version of setReadOnly."""

		self.setReadOnly(*args, event = event, **kwargs)

	def setReadOnly(self, label = None, *args, window = False, **kwargs):
		"""Overload for setReadOnly in handle_Widget_Base."""

		self._overloadHelp("setReadOnly", label, args, kwargs, window = window)

	def checkReadOnly(self, label = None, *args, window = False, **kwargs):
		"""Overload for checkReadOnly in handle_Widget_Base."""

		answer = self._overloadHelp("checkReadOnly", label, args, kwargs, window = window)
		return answer

	#Tool Tips
	def setToolTipAppearDelay(self, label = None, *args, window = False, **kwargs):
		"""Override function for setToolTipAppearDelay for handle_Widget_Base."""

		self._overloadHelp("setToolTipAppearDelay", label, args, kwargs, window = window)

	def setToolTipDisappearDelay(self, label = None, *args, window = False, **kwargs):
		"""Override function for setToolTipDisappearDelay for handle_Widget_Base."""

		self._overloadHelp("setToolTipDisappearDelay", label, args, kwargs, window = window)

	def setToolTipReappearDelay(self, label = None, *args, window = False, **kwargs):
		"""Override function for setToolTipReappearDelay for handle_Widget_Base."""

		self._overloadHelp("setToolTipReappearDelay", label, args, kwargs, window = window)

class handle_Widget_Base(handle_Base):
	"""A handle for working with a wxWidget."""

	def __init__(self):
		"""Initializes defaults."""

		#Initialize inherited classes
		handle_Base.__init__(self)

	def __len__(self):
		"""Returns what the contextual length is for the object associated with this handle."""

		if (self.type is Types.progressbar):
			value = self.thing.GetRange()

		else:
			warnings.warn(f"Add {self.type.name} to __len__() for {self.__repr__()}", Warning, stacklevel = 2)
			value = 0

		return value

	def _build(self, argument_catalogue):
		"""Determiens which build system to use for this handle."""

		def _build_line():
			"""Builds a wx line object."""
			nonlocal self, argument_catalogue

			vertical = self._getArguments(argument_catalogue, "vertical")

			#Apply settings
			if (vertical):
				direction = wx.LI_VERTICAL
			else:
				direction = wx.LI_HORIZONTAL

			myId = self._getId(argument_catalogue)

			#Create the thing to put in the grid
			self.thing = wx.StaticLine(self.parent.thing, id = myId, style = direction)

		def _build_progressBar():
			"""Builds a wx line object."""
			nonlocal self, argument_catalogue

			vertical, myMax, myInitial = self._getArguments(argument_catalogue, ["vertical", "myMax", "myInitial"])
			if (vertical):
				style = wx.GA_VERTICAL
			else:
				style = wx.GA_HORIZONTAL

			myId = self._getId(argument_catalogue)
		
			#Create the thing to put in the grid
			self.thing = wx.Gauge(self.parent.thing, id = myId, range = myMax, style = style)

			#Set Initial Conditions
			self.thing.SetValue(myInitial)
		
		#########################################################

		self._preBuild(argument_catalogue)

		if (self.type is Types.line):
			_build_line()
		elif (self.type is Types.progressbar):
			_build_progressBar()
		else:
			warnings.warn(f"Add {self.type.name} to _build() for {self.__repr__()}", Warning, stacklevel = 2)

		self._postBuild(argument_catalogue)

	#Getters
	def getValue(self, event = None):
		"""Returns what the contextual value is for the object associated with this handle."""

		if (self.type is Types.progressbar):
			value = self.thing.GetValue() #(int) - Where the progress bar currently is

		else:
			warnings.warn(f"Add {self.type.name} to getValue() for {self.__repr__()}", Warning, stacklevel = 4)
			value = None

		return value

	def getIndex(self, event = None):
		"""Returns what the contextual index is for the object associated with this handle."""

		if (False):
			pass
		else:
			warnings.warn(f"Add {self.type.name} to getIndex() for {self.__repr__()}", Warning, stacklevel = 4)
			value = None

		return value

	def getAll(self, event = None):
		"""Returns all the contextual values for the object associated with this handle."""

		if (self.type is Types.progressbar):
			value = self.thing.GetRange()

		else:
			warnings.warn(f"Add {self.type.name} to getAll() for {self.__repr__()}", Warning, stacklevel = 4)
			value = None

		return value

	#Setters
	def setValue(self, newValue, event = None):
		"""Sets the contextual value for the object associated with this handle to what the user supplies."""

		if (self.type is Types.progressbar):
			if (not isinstance(newValue, int)):
				newValue = int(newValue)

			self.thing.SetValue(newValue)

		else:
			warnings.warn(f"Add {self.type.name} to setValue() for {self.__repr__()}", Warning, stacklevel = 4)

	def setSelection(self, newValue, event = None):
		"""Sets the contextual selection for the object associated with this handle to what the user supplies."""

		warnings.warn(f"Add {self.type.name} to setSelection() for {self.__repr__()}", Warning, stacklevel = 4)

	def setReadOnly(self, state = True, event = None):
		"""Sets the contextual readOnly for the object associated with this handle to what the user supplies."""

		if (self.type is Types.line):
			pass
			
		else:
			warnings.warn(f"Add {self.type.name} to setReadOnly() for {self.__repr__()}", Warning, stacklevel = 4)

	def setFunction_rightClick(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		self._betterBind(wx.EVT_RIGHT_DOWN, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)

	def addPopupMenu(self, label = None, rightClick = True, text = None,

		preFunction = None, preFunctionArgs = None, preFunctionKwargs = None, 
		postFunction = None, postFunctionArgs = None, postFunctionKwargs = None,

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		parent = None, handle = None, myId = None, tabSkip = False):
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
		handle.type = Types.popup_widget
		parent = self
		text = None
		handle._build(locals())
		self._finalNest(handle)
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

		if (hasattr(self, "nestedSizer") and (self.nestedSizer.type is Types.flex)):
			with self.nestedSizer as mySizer:
				index = self.getSizerIndex()
				row, column = self.getSizerCoordinates()
				updateNeeded = False

				if ((row in mySizer.growFlexRow_notEmpty) and (state == (not mySizer.thing.IsRowGrowable(row)))):
					leftBound = (row + 1) * mySizer.columns - mySizer.columns
					rightBound = (row + 1) * mySizer.columns
					updateNeeded = True

					if (any(mySizer.thing.GetItem(i).IsShown() for i in range(leftBound, rightBound))):
						mySizer.growFlexRow(row, proportion = mySizer.growFlexRow_notEmpty[row])
					else:
						mySizer.thing.RemoveGrowableRow(row)

				if ((column in mySizer.growFlexColumn_notEmpty) and (state == (not mySizer.thing.IsColGrowable(column)))):
					leftBound = column
					rightBound = mySizer.rows * mySizer.columns
					step = mySizer.columns
					updateNeeded = True
					
					if (any(mySizer.thing.GetItem(i).IsShown() for i in range(leftBound, rightBound, step))):
						mySizer.growFlexColumn(column, proportion = mySizer.growFlexColumn_notEmpty[column])
					else:
						mySizer.thing.RemoveGrowableCol(column)

				#Account for textbox sizers
				if ((mySizer.substitute is not None) and (mySizer.substitute.type is Types.text)):
					text = mySizer.substitute.thing.GetStaticBox()
					if (not any(item.IsShown() for item in mySizer.thing.GetChildren())):
						if (text.IsShown()):
							text.Hide()
							updateNeeded = True
					else:
						if (not text.IsShown()):
							text.Show()
							updateNeeded = True
						text.SendSizeEventToParent()

				if (updateNeeded):
					self.myWindow.updateWindow()#updateNested = True)

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

		label = None, identity = None, myId = None, tabSkip = False):
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

		if (text is None):
			text = ""
		else:
			if (not isinstance(text, str)):
				text = f"{text}"

		if (isinstance(self, (handle_MenuItem, handle_MenuPopupItem))):     
			#Do not add empty tool tips
			if (len(text) != 0):
				if (self.type is Types.menuitem):
					self.thing.SetHelp(text)
				elif (self.type is Types.toolbaritem):
					self.thing.SetShortHelp(text)
					self.thing.SetLongHelp(text)
		else:
			#Add the tool tip
			toolTip = wx.ToolTip(text)

			#Apply properties
			if (delayAppear is not None):
				toolTip.SetDelay(delayAppear)

			if (delayDisappear is not None):
				toolTip.SetAutoPop(delayDisappear)

			if (delayReappear is not None):
				toolTip.SetReshow(delayReappear)

			if (maxWidth is not None):
				toolTip.SetMaxWidth(maxWidth)

			#Attach the tool tip to the wxObject
			self.thing.SetToolTip(toolTip)

		#Catalogue tool tip
		if (label is not None):
			if (label in self.myWindow.toolTipCatalogue):
				warnings.warn(f"Overwriting tool tip for {label} in {self.myWindow.__repr__()}", Warning, stacklevel = 2)

			self.myWindow.toolTipCatalogue[label] = toolTip

	def setToolTip(self, text = ""):
		"""Changes what the tool tip says for this handle.

		Example Input: setToolTip("Lorem Ipsum")
		"""

		if (self.type is Types.menuitem):
			self.thing.SetHelp(text)

		elif (self.type is Types.toolbaritem):
			self.thing.SetShortHelp(text)
			self.thing.SetLongHelp(text)
		else:
			self.thing.SetToolTip(text)

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

		if (label is not None):
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

		if (label is not None):
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

		if (label is not None):
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

		if (self.type is Types.text):
			value = len(self.getValue()) #(int) - How long the text is

		elif (self.type is Types.hyperlink):
			value = len(self.getValue()) #(int) - How long the url link is

		else:
			warnings.warn(f"Add {self.type.name} to __len__() for {self.__repr__()}", Warning, stacklevel = 2)
			value = 0

		return value

	def _build(self, argument_catalogue):
		"""Determiens which build system to use for this handle."""

		def _build_text():
			"""Builds a wx text object."""
			nonlocal self, argument_catalogue

			text, alignment, ellipsize = self._getArguments(argument_catalogue, ["text", "alignment", "ellipsize"])

			#Ensure correct format
			if (not isinstance(text, str)):
				text = f"{text}"

			#Apply Settings
			if (alignment is not None):
				if (isinstance(alignment, bool)):
					if (alignment):
						style = [wx.ALIGN_LEFT]
						self.flags_modification.append("al")
					else:
						style = [wx.ALIGN_CENTRE]
						self.flags_modification.append("ac")
				elif (isinstance(alignment, str)):
					if (alignment[0].lower() == "l"):
						style = [wx.ALIGN_LEFT]
						self.flags_modification.append("al")
					elif (alignment[0].lower() == "r"):
						style = [wx.ALIGN_RIGHT]
						self.flags_modification.append("ar")
					else:
						style = [wx.ALIGN_CENTRE]
						self.flags_modification.append("ac")
				elif (alignment == 0):
					style = [wx.ALIGN_LEFT]
					self.flags_modification.append("al")
				elif (alignment == 1):
					style = [wx.ALIGN_RIGHT]
					self.flags_modification.append("ar")
				else:
					style = [wx.ALIGN_CENTRE]
					self.flags_modification.append("ac")
			else:
				style = [wx.ALIGN_CENTRE]
				self.flags_modification.append("ac")
			
			if (ellipsize is not None):
				if (isinstance(ellipsize, bool)):
					if (ellipsize):
						style.append(wx.ST_ELLIPSIZE_END)
				elif (ellipsize == 0):
					style.append(wx.ST_ELLIPSIZE_START)
				elif (ellipsize == 1):
					style.append(wx.ST_ELLIPSIZE_MIDDLE)
				else:
					style.append(wx.ST_ELLIPSIZE_END)

			myId = self._getId(argument_catalogue)

			#Create the thing to put in the grid
			self.thing = wx.StaticText(self.parent.thing, id = myId, label = text, style = functools.reduce(operator.ior, style or (0,)))

			size, bold, italic, family, wrap = self._getArguments(argument_catalogue, ("size", "bold", "italic", "family", "wrap"))
			font = self.getFont(size = size, bold = bold, italic = italic, family = family)
			self.thing.SetFont(font)

			if (wrap):
				self.wrapText(wrap)

		def _build_html():
			"""Builds a blank wx html object.
			Use: https://wxpython.org/Phoenix/docs/html/html_overview.html
			Use: https://wxpython.org/Phoenix/docs/html/wx.html.HtmlWindow.html
			Use: https://wxpython.org/Phoenix/docs/html/wx.html2.WebView.html
			"""
			nonlocal self

			myId = self._getId(argument_catalogue)

			text, can_scroll, can_select, position, size = self._getArguments(argument_catalogue, ["text", "can_scroll", "can_select", "position", "size"])

			style = []
			if (can_scroll):
				style.append(wx.html.HW_SCROLLBAR_AUTO)
			else:
				style.append(wx.html.HW_SCROLLBAR_NEVER)

			if (not can_select):
				style.append(wx.html.HW_NO_SELECTION)

			#Create the thing to put in the grid
			self.thing = wx.html.HtmlWindow(self.parent.thing, id = myId, pos = position or wx.DefaultPosition, 
				size = size or wx.DefaultSize, style = functools.reduce(operator.ior, style or (0,)))

			self.setValue(text)

		def _build_hyperlink():
			"""Builds a wx hyperlink object."""
			nonlocal self, argument_catalogue

			text, myWebsite = self._getArguments(argument_catalogue, ["text", "myWebsite"])

			#Apply settings
			# wx.adv.HL_ALIGN_LEFT: Align the text to the left.
			# wx.adv.HL_ALIGN_RIGHT: Align the text to the right. This style is not supported under Windows XP but is supported under all the other Windows versions.
			# wx.adv.HL_ALIGN_CENTRE: Center the text (horizontally). This style is not supported by the native MSW implementation used under Windows XP and later.
			# wx.adv.HL_CONTEXTMENU: Pop up a context menu when the hyperlink is right-clicked. The context menu contains a “Copy URL” menu item which is automatically handled by the hyperlink and which just copies in the clipboard the URL (not the label) of the control.
			# wx.adv.HL_DEFAULT_STYLE: The default style for wx.adv.HyperlinkCtrl: BORDER_NONE|wxHL_CONTEXTMENU|wxHL_ALIGN_CENTRE.
			style = "wx.adv.HL_DEFAULT_STYLE"

			myId = self._getId(argument_catalogue)

			#Create the thing to put in the grid
			self.thing = wx.adv.HyperlinkCtrl(self.parent.thing, id = myId, label = text, url = myWebsite, style =  eval(style, {'__builtins__': None, "wx": wx}, {}))

			#Apply colors
			# SetHoverColour
			# SetNormalColour
			# SetVisitedColour

			#Bind the function(s)
			myFunction, myFunctionArgs, myFunctionKwargs = self._getArguments(argument_catalogue, ["myFunction", "myFunctionArgs", "myFunctionKwargs"])
			self.setFunction_click(myFunction, myFunctionArgs, myFunctionKwargs)

		def _build_empty():
			"""Builds a blank wx text object."""
			nonlocal self

			myId = self._getId(argument_catalogue)

			#Create the thing to put in the grid
			self.thing = wx.StaticText(self.parent.thing, id = myId, label = wx.EmptyString)
			self.wrapText(-1)
		
		#########################################################

		self._preBuild(argument_catalogue)

		if (self.type is Types.text):
			_build_text()
		elif (self.type is Types.html):
			_build_html()
		elif (self.type is Types.hyperlink):
			_build_hyperlink()
		elif (self.type is Types.empty):
			_build_empty()
		else:
			warnings.warn(f"Add {self.type.name} to _build() for {self.__repr__()}", Warning, stacklevel = 2)

		self._postBuild(argument_catalogue)

	#Getters
	def getValue(self, event = None):
		"""Returns what the contextual value is for the object associated with this handle."""

		if (self.type is Types.text):
			value = self.thing.GetLabel() #(str) - What the text says

		elif (self.type is Types.html):
			value = self.thing.ToText() #(str) - What the internal html is

		elif (self.type is Types.hyperlink):
			value = self.thing.GetURL() #(str) - What the link is

		else:
			warnings.warn(f"Add {self.type.name} to getValue() for {self.__repr__()}", Warning, stacklevel = 2)
			value = None

		return value

	#Setters
	def setValue(self, newValue, event = None):
		"""Sets the contextual value for the object associated with this handle to what the user supplies."""

		if (self.type is Types.text):
			if (not isinstance(newValue, str)):
				newValue = f"{newValue}"

			self.thing.SetLabel(newValue) #(str) - What the static text will now say
			self.thing.SendSizeEventToParent() #Update alignment

		elif (self.type is Types.html):
			self.thing.SetPage(newValue or "")

		elif (self.type is Types.hyperlink):
			if (not isinstance(newValue, str)):
				newValue = f"{newValue}"

			self.thing.SetURL(newValue) #(str) - What the hyperlink will now connect to

		else:
			warnings.warn(f"Add {self.type.name} to setValue() for {self.__repr__()}", Warning, stacklevel = 2)

	def setReadOnly(self, state = True):
		"""Sets the contextual readOnly for the object associated with this handle to what the user supplies."""

		if (self.type is Types.text):
			pass
			
		else:
			warnings.warn(f"Add {self.type.name} to setReadOnly() for {self.__repr__()}", Warning, stacklevel = 2)

	#Change Settings
	def wrapText(self, wrap = 1):
		"""Wraps the text to a specific point.

		wrap (int)      - How many pixels wide the line will be before it wraps. If negative: no wrapping is done

		Example Text: wrapText(250)
		"""

		if (wrap is not None):
			self.thing.Wrap(wrap)

	def setFunction_click(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type is Types.hyperlink):
			self._betterBind(wx.adv.EVT_HYPERLINK, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		else:
			warnings.warn(f"Add {self.type.name} to setFunction_click() for {self.__repr__()}", Warning, stacklevel = 2)

class handle_WidgetList(handle_Widget_Base):
	"""A handle for working with list widgets."""

	def __init__(self):
		"""Initializes defaults."""

		#Initialize inherited classes
		handle_Widget_Base.__init__(self)

		#Internal Variables
		self.dragable = False
		self.myDropTarget = None
		self.ignoreAutoComplete = False
		self.expanded = {None: False} #(group (str): state (bool), None: default state (bool))

		self.columnCatalogue = {}
		self.selectionColor = None
		self.lastSelection = {"group": [], "row": [], "latest": None}
		self.groups_ensured = []

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

		if (self.type is Types.drop):
			value = self.thing.GetCount() #(int) - How many items are in the drop list

		elif (self.type is Types.view):
			if (returnRows):
				value = self.thing.GetItemCount()
			else:
				value = len(self.columnCatalogue)

		else:
			warnings.warn(f"Add {self.type.name} to __len__() for {self.__repr__()}", Warning, stacklevel = 2)
			value = 0

		return value

	def _build(self, argument_catalogue):
		"""Determiens which build system to use for this handle."""

		def _build_listDrop():
			"""Builds a wx choice object.
			Use: https://bitbucket.org/raz/wxautocompletectrl/src/default/autocomplete.py
			Use: https://wiki.wxpython.org/Combo%20Box%20that%20Suggests%20Options
			"""
			nonlocal self, argument_catalogue

			def yieldValue():
				nonlocal choices

				for item in self.ensure_container(self._Munge(choices, extraArgs = (self,), returnMunger_onFail = True), convertNone = False):
					yield f"{item}"

			#########################################

			choices, alphabetic, default, readOnly = self._getArguments(argument_catalogue, ["choices", "alphabetic", "default", "readOnly"])
			formatter, inputBox, dropDown, autoComplete = self._getArguments(argument_catalogue, ["formatter", "inputBox", "dropDown", "autoComplete"])

			#Ensure that the choices are all strings
			self.choices = self.ensure_container(self._Munge(choices, extraArgs = (self,), returnMunger_onFail = True), convertNone = False)

			#Format choices to display
			if (formatter):
				self.formattedChoices = [f"{formatter(item)}" for item in self.choices]
			else:
				self.formattedChoices = [f"{item}" for item in self.choices]

			#Apply Settings
			style = []
			if (alphabetic):
				style.append(wx.CB_SORT)

			myId = self._getId(argument_catalogue)

			#Create the thing to put in the grid
			if (inputBox):
				if (readOnly):
					style.append(wx.CB_READONLY)
				else:
					style.append(wx.TE_PROCESS_ENTER)

				if (not dropDown):
					style.append(wx.CB_SIMPLE)
				else:
					style.append(wx.CB_DROPDOWN)

				self.thing = wx.ComboBox(self.parent.thing, id = myId, choices = self.formattedChoices, style = functools.reduce(operator.ior, style or (0,)))
			else:
				self.thing = wx.Choice(self.parent.thing, id = myId, choices = self.formattedChoices, style = functools.reduce(operator.ior, style or (0,)))
			
			#Set default position
			default = self._Munge(default, extraArgs = (self,), returnMunger_onFail = True)
			if (isinstance(default, (list, tuple, range, set))):
				if (not default):
					default = None
				else:
					default = default[0]

			if ((default is not None) and (not isinstance(default, int))):
				if (default in self.choices):
					default = self.choices.index(default)
				
				elif (default in self.formattedChoices):
					default = self.formattedChoices.index(default)
				
				else:
					warnings.warn(f"the default {default} was not in the provided list of choices for a {self.type} in {self.__repr__()}", Warning, stacklevel = 4)
					default = None

			self.thing.SetSelection(default or 0)

			#Bind the function(s)
			myFunction, myFunctionArgs, myFunctionKwargs = self._getArguments(argument_catalogue, ["myFunction", "myFunctionArgs", "myFunctionKwargs"])
			self.setFunction_click(myFunction, myFunctionArgs, myFunctionKwargs)

			if (autoComplete):
				self.update_autoComplete()

		def _build_listFull():
			"""Builds a wx choice object.
			Use: https://pypi.org/project/ObjectListView/1.3.1/
			Use: http://objectlistview-python-edition.readthedocs.io/en/latest/
			Use: http://www.blog.pythonlibrary.org/index.php?s=medialocker&submit=Search
			Use: https://www.codeproject.com/KB/list/objectlistview.aspx
			Use: https://www.codeproject.com/Articles/16009/A-Much-Easier-to-Use-ListView
			Use: http://code.activestate.com/recipes/577543-objectlistview-getcolumnclickedevent-handler/
			Use: http://www.blog.pythonlibrary.org/2013/12/12/wxpython-adding-tooltips-objectlistview/
			Use: http://www.blog.pythonlibrary.org/2017/11/16/wxpython-moving-items-in-objectlistview/
			"""
			nonlocal self, argument_catalogue

			def formatCatalogue(columns, catalogue, default):
				"""Ensures the provided catalogue is in the correct format."""

				if (isinstance(catalogue, (list, tuple, range))):
					return {i: catalogue[i] if (len(catalogue) > i) else default for i in range(columns)}
				elif (isinstance(catalogue, dict)):
					return {i: catalogue[i] if (i in catalogue) else default for i in range(columns)}
				return {i: catalogue for i in range(columns)}

			####################################################################

			columnTitles, columnWidth, groupIndent, hideFirstIndent = self._getArguments(argument_catalogue, ["columnTitles", "columnWidth", "groupIndent", "hideFirstIndent"])
			report, single, editable, editOnClick, columnLabels = self._getArguments(argument_catalogue, ["report", "single", "editable", "editOnClick", "columnLabels"])
			columnImage, columnAlign, columnFormatter, showColumnContextMenu = self._getArguments(argument_catalogue, ["columnImage", "columnAlign", "columnFormatter", "showColumnContextMenu"])
			border, rowLines, columnLines, showContextMenu = self._getArguments(argument_catalogue, ["border", "rowLines", "columnLines", "showContextMenu"])
			columns, drag, drop, choices, showEmptyGroups, useWeakRefs = self._getArguments(argument_catalogue, ["columns", "drag", "drop", "choices", "showEmptyGroups", "useWeakRefs"])
			group, groupFormatter, groupSeparator, copyEntireRow = self._getArguments(argument_catalogue, ["group", "groupFormatter", "groupSeparator", "copyEntireRow"])
			sortable, sortFunction, rowFormatter, pasteEntireRow, can_undo = self._getArguments(argument_catalogue, ["sortable", "sortFunction", "rowFormatter", "pasteEntireRow", "can_undo"])
			can_scroll, can_expand, can_copy, can_paste, can_selectAll, can_edit = self._getArguments(argument_catalogue, ["can_scroll", "can_expand", "can_copy", "can_paste", "can_selectAll", "can_edit"])

			if (columns is None):
				if ((choices is None) or (not isinstance(choices, (list, tuple, range, dict))) or (len(choices) == 0)):
					columns = 0
				elif (isinstance(choices, dict)):
					columns = max((len(value) if (isinstance(value, (list, tuple, range))) else 1 for value in choices.values()))
				else:
					columns = max((len(value) if (isinstance(value, (list, tuple, range))) else 1 for value in choices))

			#Ensure correct formatting
			if (isinstance(editable, (list, tuple, range))):
				editable = {i: True for i in editable}
			elif (isinstance(editable, dict)):
				editable = {i: editable[i] if (i in editable) else False for i in range(columns)}
			else:
				editable = {i: editable for i in range(columns)}

			columnTitles = formatCatalogue(columns, columnTitles, "")
			columnWidth = formatCatalogue(columns, columnWidth, -1)
			columnLabels = formatCatalogue(columns, columnLabels, None)
			columnImage = formatCatalogue(columns, columnImage, None)
			columnAlign = formatCatalogue(columns, columnAlign, "left")
			columnFormatter = formatCatalogue(columns, columnFormatter, None)
			groupFormatter = formatCatalogue(columns, groupFormatter, None)
			group = formatCatalogue(columns, group, None)

			#Create widget id
			myId = self._getId(argument_catalogue)

			#Create the thing to put in the grid
			self.thing = self._ListFull(self, self.parent.thing, myId = myId, sortable = sortable, rowFormatter = rowFormatter,
				singleSelect = single, verticalLines = columnLines, horizontalLines = rowLines, showContextMenu = showContextMenu, useWeakRefs = useWeakRefs,
				showEmptyGroups = showEmptyGroups, groupIndent = groupIndent, hideFirstIndent = hideFirstIndent, showColumnContextMenu = showColumnContextMenu,
				key_copyEntireRow = copyEntireRow, key_pasteEntireRow = pasteEntireRow, key_scroll = can_scroll, key_expand = can_expand, 
				key_copy = can_copy, key_paste = can_paste, key_selectAll = can_selectAll, key_edit = can_edit, key_undo = can_undo)
			self.thing.putBlankLineBetweenGroups = groupSeparator
			self.setSortFunction(sortFunction)

			if (editOnClick is not None):
				if (editOnClick):
					self.thing.cellEditMode = ObjectListView.ObjectListView.CELLEDIT_SINGLECLICK
				else:
					self.thing.cellEditMode = ObjectListView.ObjectListView.CELLEDIT_DOUBLECLICK
			else:
				self.thing.cellEditMode = ObjectListView.ObjectListView.CELLEDIT_F2ONLY

			#Create columns
			for i in range(columns):
				self.setColumn(i, title = columnTitles[i], label = columnLabels[i], width = columnWidth[i], editable = editable[i], 
					align = columnAlign[i], image = columnImage[i], formatter = columnFormatter[i], group = group[i], groupFormatter = groupFormatter[i], minWidth = None, refresh = False)
			self.refreshColumns()

			#Add Items
			self.setValue(choices)

			# #Determine if it's contents are dragable
			# if (drag):
			#   dragLabel, dragDelete, dragCopyOverride, allowExternalAppDelete = self._getArguments(argument_catalogue, ["dragLabel", "dragDelete", "dragCopyOverride", "allowExternalAppDelete"])
			#   preDragFunction, preDragFunctionArgs, preDragFunctionKwargs = self._getArguments(argument_catalogue, ["preDragFunction", "preDragFunctionArgs", "preDragFunctionKwargs"])
			#   postDragFunction, postDragFunctionArgs, postDragFunctionKwargs = self._getArguments(argument_catalogue, ["postDragFunction", "postDragFunctionArgs", "postDragFunctionKwargs"])
				
			#   self.dragable = True
			#   self._betterBind(wx.EVT_LIST_BEGIN_DRAG, self.thing, self._onDragList_beginDragAway, None, 
			#       {"label": dragLabel, "deleteOnDrop": dragDelete, "overrideCopy": dragCopyOverride, "allowExternalAppDelete": allowExternalAppDelete})
				
			#   self.preDragFunction = preDragFunction
			#   self.preDragFunctionArgs = preDragFunctionArgs
			#   self.preDragFunctionKwargs = preDragFunctionKwargs

			#   self.postDragFunction = postDragFunction
			#   self.postDragFunctionArgs = postDragFunctionArgs
			#   self.postDragFunctionKwargs = postDragFunctionKwargs

			# #Determine if it accepts dropped items
			# if (drop):
			#   dropIndex = self._getArguments(argument_catalogue, ["dropIndex"])
			#   preDropFunction, preDropFunctionArgs, preDropFunctionKwargs = self._getArguments(argument_catalogue, ["preDropFunction", "preDropFunctionArgs", "preDropFunctionKwargs"])
			#   postDropFunction, postDropFunctionArgs, postDropFunctionKwargs = self._getArguments(argument_catalogue, ["postDropFunction", "postDropFunctionArgs", "postDropFunctionKwargs"])
			#   dragOverFunction, dragOverFunctionArgs, postDropFunctionKwargs = self._getArguments(argument_catalogue, ["dragOverFunction", "dragOverFunctionArgs", "postDropFunctionKwargs"])
				
			#   self.myDropTarget = self._DragTextDropTarget(self.thing, dropIndex,
			#       preDropFunction = preDropFunction, preDropFunctionArgs = preDropFunctionArgs, preDropFunctionKwargs = preDropFunctionKwargs, 
			#       postDropFunction = postDropFunction, postDropFunctionArgs = postDropFunctionArgs, postDropFunctionKwargs = postDropFunctionKwargs,
			#       dragOverFunction = dragOverFunction, dragOverFunctionArgs = dragOverFunctionArgs, dragOverFunctionKwargs = postDropFunctionKwargs)
			#   self.thing.SetDropTarget(self.myDropTarget)

			# #Bind the function(s)
			self._betterBind(ObjectListView.EVT_DATA_SELECTION_CHANGED, self.thing, self._onSelectRow, mode = 2)
			self._betterBind(ObjectListView.EVT_DATA_GROUP_SELECTED, self.thing, self._onSelectGroup, mode = 2)

			# myFunction, preEditFunction, postEditFunction = self._getArguments(argument_catalogue, ["myFunction", "preEditFunction", "postEditFunction"])
			# if (myFunction is not None):
			#   myFunctionArgs, myFunctionKwargs = self._getArguments(argument_catalogue, ["myFunctionArgs", "myFunctionKwargs"])
			#   self.setFunction_click(myFunction, myFunctionArgs, myFunctionKwargs)

			# if (preEditFunction):
			#   preEditFunctionArgs, preEditFunctionKwargs = self._getArguments(argument_catalogue, ["preEditFunctionArgs", "preEditFunctionKwargs"])
			#   self.setFunction_preEdit(preEditFunction, preEditFunctionArgs, preEditFunctionKwargs)

			# if (postEditFunction):
			#   postEditFunctionArgs, postEditFunctionKwargs = self._getArguments(argument_catalogue, ["postEditFunctionArgs", "postEditFunctionKwargs"])
			#   self.setFunction_postEdit(postEditFunction, postEditFunctionArgs, postEditFunctionKwargs)

			# if (editOnClick):
			#   pass

		def _build_listTree():
			"""Builds a wx choice object."""
			nonlocal self, argument_catalogue

			
			choices, drag, drop = self._getArguments(argument_catalogue, ["choices", "drag", "drop"])
			addButton, editable, rowHighlight, root = self._getArguments(argument_catalogue, ["addButton", "editable", "rowHighlight", "root"])
			rowLines, rootLines, variableHeight, selectMultiple = self._getArguments(argument_catalogue, ["rowLines", "rootLines", "variableHeight", "selectMultiple"])

			#Apply Settings
			if (addButton is None):
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

			if (root is None):
				style += "|wx.TR_HIDE_ROOT"

			if (rowLines or rootLines):
				if (rowLines):
					style += "|wx.TR_ROW_LINES"

				if (rootLines and (root is not None)):
					style += "|wx.TR_LINES_AT_ROOT"
			else:
				style += "|wx.TR_NO_LINES"

			if (variableHeight):
				style += "|wx.TR_HAS_VARIABLE_ROW_HEIGHT"

			if (selectMultiple):
				self.subType = "multiple"
				style += "|wx.TR_MULTIPLE"
			else:
				self.subType = "single"
				style += "|wx.TR_SINGLE"

			myId = self._getId(argument_catalogue)

			#Create the thing to put in the grid
			self.thing = wx.TreeCtrl(self.parent.thing, id = myId, style = eval(style, {'__builtins__': None, "wx": wx}, {}))
			
			self.setValue({root: choices})

			preRightDragFunction, postRightDragFunction = self._getArguments(argument_catalogue, ["preRightDragFunction", "postRightDragFunction"])
			preDropFunction, postDropFunction, dragOverFunction = self._getArguments(argument_catalogue, ["preDropFunction", "postDropFunction", "dragOverFunction"])

			# #Determine if it's contents are dragable
			# if (drag):
			#   dragLabel, dragDelete, dragCopyOverride, allowExternalAppDelete = self._getArguments(argument_catalogue, ["dragLabel", "dragDelete", "dragCopyOverride", "allowExternalAppDelete"])
			#   preDragFunction, preDragFunctionArgs, preDragFunctionKwargs = self._getArguments(argument_catalogue, ["preDragFunction", "preDragFunctionArgs", "preDragFunctionKwargs"])
			#   postDragFunction, postDragFunctionArgs, postDragFunctionKwargs = self._getArguments(argument_catalogue, ["postDragFunction", "postDragFunctionArgs", "postDragFunctionKwargs"])
				
			#   self.dragable = True
			#   self._betterBind(wx.EVT_TREE_BEGIN_DRAG, self.thing, self._onDragList_beginDragAway, None, 
			#       {"label": dragLabel, "deleteOnDrop": dragDelete, "overrideCopy": dragCopyOverride, "allowExternalAppDelete": allowExternalAppDelete})
				
			#   self.preDragFunction = preDragFunction
			#   self.preDragFunctionArgs = preDragFunctionArgs
			#   self.preDragFunctionKwargs = preDragFunctionKwargs

			#   self.postDragFunction = postDragFunction
			#   self.postDragFunctionArgs = postDragFunctionArgs
			#   self.postDragFunctionKwargs = postDragFunctionKwargs

			# #Determine if it accepts dropped items
			# if (drop):
			#   dropIndex = self._getArguments(argument_catalogue, ["dropIndex"])
			#   preDropFunction, preDropFunctionArgs, preDropFunctionKwargs = self._getArguments(argument_catalogue, ["preDropFunction", "preDropFunctionArgs", "preDropFunctionKwargs"])
			#   postDropFunction, postDropFunctionArgs, postDropFunctionKwargs = self._getArguments(argument_catalogue, ["postDropFunction", "postDropFunctionArgs", "postDropFunctionKwargs"])
			#   dragOverFunction, dragOverFunctionArgs, postDropFunctionKwargs = self._getArguments(argument_catalogue, ["dragOverFunction", "dragOverFunctionArgs", "postDropFunctionKwargs"])
				
			#   self.myDropTarget = self._DragTextDropTarget(self.thing, dropIndex,
			#       preDropFunction = preDropFunction, preDropFunctionArgs = preDropFunctionArgs, preDropFunctionKwargs = preDropFunctionKwargs, 
			#       postDropFunction = postDropFunction, postDropFunctionArgs = postDropFunctionArgs, postDropFunctionKwargs = postDropFunctionKwargs,
			#       dragOverFunction = dragOverFunction, dragOverFunctionArgs = dragOverFunctionArgs, dragOverFunctionKwargs = postDropFunctionKwargs)
			#   self.thing.SetDropTarget(self.myDropTarget)

			#Bind the function(s)
			myFunction, preEditFunction, postEditFunction = self._getArguments(argument_catalogue, ["myFunction", "preEditFunction", "postEditFunction"])
			preCollapseFunction, preExpandFunction = self._getArguments(argument_catalogue, ["preCollapseFunction", "preExpandFunction"])
			postCollapseFunction, postExpandFunction = self._getArguments(argument_catalogue, ["postCollapseFunction", "postExpandFunction"])
			rightClickFunction, middleClickFunction, doubleClickFunction = self._getArguments(argument_catalogue, ["rightClickFunction", "middleClickFunction", "doubleClickFunction"])
			keyDownFunction, toolTipFunction, itemMenuFunction = self._getArguments(argument_catalogue, ["keyDownFunction", "toolTipFunction", "itemMenuFunction"])

			if (myFunction is not None):
				myFunctionArgs, myFunctionKwargs = self._getArguments(argument_catalogue, ["myFunctionArgs", "myFunctionKwargs"])
				self.setFunction_postClick(myFunction, myFunctionArgs, myFunctionKwargs)

			if (preEditFunction is not None):
				preEditFunctionArgs, preEditFunctionKwargs = self._getArguments(argument_catalogue, ["preEditFunctionArgs", "preEditFunctionKwargs"])
				self.setFunction_preEdit(preEditFunction, preEditFunctionArgs, preEditFunctionKwargs)

			if (postEditFunction is not None):
				postEditFunctionArgs, postEditFunctionKwargs = self._getArguments(argument_catalogue, ["postEditFunctionArgs", "postEditFunctionKwargs"])
				self.setFunction_postEdit(postEditFunction, postEditFunctionArgs, postEditFunctionKwargs)

			if (preCollapseFunction is not None):
				preCollapseFunctionArgs, preCollapseFunctionKwargs = self._getArguments(argument_catalogue, ["preCollapseFunctionArgs", "preCollapseFunctionKwargs"])
				self.setFunction_collapse(preCollapseFunction, preCollapseFunctionArgs, preCollapseFunctionKwargs)

			if (postCollapseFunction is not None):
				postCollapseFunctionArgs, postCollapseFunctionKwargs = self._getArguments(argument_catalogue, ["postCollapseFunctionArgs", "postCollapseFunctionKwargs"])
				self.setFunction_collapse(postCollapseFunction, postCollapseFunctionArgs, postCollapseFunctionKwargs)

			if (preExpandFunction is not None):
				preExpandFunctionArgs, preExpandFunctionKwargs = self._getArguments(argument_catalogue, ["preExpandFunctionArgs", "preExpandFunctionKwargs"])
				self.setFunction_expand(preExpandFunction, preExpandFunctionArgs, preExpandFunctionKwargs)

			if (postExpandFunction is not None):
				postExpandFunctionArgs, postExpandFunctionKwargs = self._getArguments(argument_catalogue, ["postExpandFunctionArgs", "postExpandFunctionKwargs"])
				self.setFunction_expand(postExpandFunction, postExpandFunctionArgs, postExpandFunctionKwargs)

			if (rightClickFunction is not None):
				rightClickFunctionArgs, rightClickFunctionKwargs = self._getArguments(argument_catalogue, ["rightClickFunctionArgs", "rightClickFunctionKwargs"])
				self.setFunction_rightClick(rightClickFunction, rightClickFunctionArgs, rightClickFunctionKwargs)

			if (middleClickFunction is not None):
				middleClickFunctionArgs, middleClickFunctionKwargs = self._getArguments(argument_catalogue, ["middleClickFunctionArgs", "middleClickFunctionKwargs"])
				self.setFunction_middleClick(middleClickFunction, middleClickFunctionArgs, middleClickFunctionKwargs)
			
			if (doubleClickFunction is not None):
				doubleClickFunctionArgs, doubleClickFunctionKwargs = self._getArguments(argument_catalogue, ["doubleClickFunctionArgs", "doubleClickFunctionKwargs"])
				self.setFunction_doubleClick(doubleClickFunction, doubleClickFunctionArgs, doubleClickFunctionKwargs)

			if (keyDownFunction is not None):
				keyDownFunctionArgs, keyDownFunctionKwargs = self._getArguments(argument_catalogue, ["keyDownFunctionArgs", "keyDownFunctionKwargs"])
				self.setFunction_keyDown(keyDownFunction, keyDownFunctionArgs, keyDownFunctionKwargs)

			if (toolTipFunction is not None):
				toolTipFunctionArgs, toolTipFunctionKwargs = self._getArguments(argument_catalogue, ["toolTipFunctionArgs", "toolTipFunctionKwargs"])
				self.setFunction_toolTip(toolTipFunction, toolTipFunctionArgs, toolTipFunctionKwargs)
			
			if (itemMenuFunction is not None):
				itemMenuFunctionArgs, itemMenuFunctionKwargs = self._getArguments(argument_catalogue, ["itemMenuFunctionArgs", "itemMenuFunctionKwargs"])
				self.setFunction_itemMenu(itemMenuFunction, itemMenuFunctionArgs, itemMenuFunctionKwargs)

		#########################################################

		self._preBuild(argument_catalogue)

		if (self.type is Types.drop):
			_build_listDrop()
		elif (self.type is Types.view):
			_build_listFull()
		elif (self.type is Types.tree):
			_build_listTree()
		else:
			warnings.warn(f"Add {self.type.name} to _build() for {self.__repr__()}", Warning, stacklevel = 2)

		self._postBuild(argument_catalogue)

	#Getters
	def getValue(self, event = None, fallback_lastSelection = False, group = False):
		"""Returns what the contextual value is for the object associated with this handle.

		group (bool) - Determines what is returned
			- If True: A list of strings for each selected group is returned
			- If False: A list of objects for each selected item is returned
			- If None: A dictionary containing both groups and items selected is returned
		"""

		if (self.type is Types.drop):
			index = self.thing.GetSelection()
			value = self.choices[index] #(any) - What was selected in the drop list

		elif (self.type is Types.view):
			if (group is None):
				value = {"group": [item.key for item in self.thing.GetSelectedGroups()], "row": self.thing.GetSelectedObjects(), "latest": None}
			elif (group):
				value = [item.key for item in self.thing.GetSelectedGroups()]
			else:
				value = self.thing.GetSelectedObjects()

			if (fallback_lastSelection and ((not value) or (isinstance(value, dict) and (not value["group"]) and (not value["row"])))):
				value = self.getLastSelected(group = group)

		elif (self.type is Types.tree):
			if (self.subType.lower() == "single"):
				selection = self.thing.GetSelection()
				if (selection.IsOk()):
					value = self.thing.GetItemText(selection)
				else:
					value = None
			else:
				value = []
				for selection in self.thing.GetSelections():
					if (selection.IsOk()):
						value.append(self.thing.GetItemText(selection))

		else:
			warnings.warn(f"Add {self.type.name} to getValue() for {self.__repr__()}", Warning, stacklevel = 2)
			value = None

		return value

	def getText(self, event = None, fallback_lastSelection = False, group = False):
		# return self.thing.GetValue()
		return self.getValue(event = event, fallback_lastSelection = fallback_lastSelection, group = group)

	def getChecked(self, event = None):
		value = []
		for item in self.thing.GetObjects():
			if (self.thing.IsChecked(item)):
				value.append(item)
		return value

	def getIndex(self, event = None):
		"""Returns what the contextual index is for the object associated with this handle."""

		if (self.type is Types.drop):
			value = self.thing.GetSelection() #(int) - The index number of what is selected in the drop list    

		elif (self.type is Types.view):
			value = []
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
			warnings.warn(f"Add {self.type.name} to getIndex() for {self.__repr__()}", Warning, stacklevel = 2)
			value = None

		return value

	def getAll(self, event = None, group = False):
		"""Returns all the contextual values for the object associated with this handle."""

		if (self.type is Types.drop):
			value = []
			n = self.thing.GetCount()
			for i in range(n):
				value.append(self.thing.GetString(i)) #(list) - What is in the drop list as strings

		elif (self.type is Types.view):
			if (group is None):
				value = {"group": [item.key for item in self.thing.GetGroups()], "row": self.thing.GetObjects()}
			elif (group):
				value = [item.key for item in self.thing.GetGroups()]
			else:
				value = self.thing.GetObjects()

		elif (self.type is Types.tree):
			value = {}
			root = self.thing.GetRootItem()

			if (self.subType.lower() == "hiddenroot"):
				rootText = None
			else:
				rootText = self.thing.GetItemText(root)

			if (self.thing.ItemHasChildren(root)):
				first, cookie = self.thing.GetFirstChild(root)
				text = self.thing.GetItemText(first)
				value[rootText] = {text: None}

			if (self.subType.lower() == "hiddenroot"):
				value = value[rootText]

		else:
			warnings.warn(f"Add {self.type.name} to getAll() for {self.__repr__()}", Warning, stacklevel = 2)
			value = None

		return value

	def yieldAll(self, event = None, group = False):
		if (self.type is not Types.view):
			warnings.warn(f"Add {self.type.name} to yieldAll() for {self.__repr__()}", Warning, stacklevel = 2)
			return

		for item in self.thing.modelObjects:
			yield item

	def getColumn(self, label):
		for index, column in self.thing.GetColumns().items():
			if (column.valueGetter == label):
				return column

	# def getColumn(self, event = None):
	# 	"""Returns what the contextual column is for the object associated with this handle.
	# 	Column algorithm from: wx.lib.mixins.listctrl.TextEditMixin
	# 	"""

	# 	if (self.type is Types.view):
	# 		x, y = self.getMousePosition()
	# 		x_offset = self.thing.GetScrollPos(wx.HORIZONTAL)
	# 		row, flags = self.thing.HitTest((x,y))

	# 		widthList = [0]
	# 		for i in range(self.thing.GetColumnCount()):
	# 			widthList.append(widthList[i] + self.thing.GetColumnWidth(i))
	# 		column = bisect.bisect(widthList, x + x_offset) - 1

	# 	else:
	# 		warnings.warn(f"Add {self.type.name} to getColumn() for {self.__repr__()}", Warning, stacklevel = 2)
	# 		column = None

	# 	return column

	def getLatestSelected(self, event = None):
		#Return copy, not origonal
		if (self.lastSelection["latest"] is None):
			return []
		return [*self.lastSelection[self.lastSelection["latest"]]]

	def getLastSelected(self, event = None, group = False):
		#Return copy, not origonal
		if (group is None):
			return {**self.lastSelection}
		elif (group):
			return [*self.lastSelection["group"]]
		else:
			return [*self.lastSelection["row"]]

	#Setters
	def setLastSelected(self, newValue, group = False, event = None):
		if (group is None):
			if ((newValue is None) or (not isinstance(newValue, dict))):
				self.lastSelection = {"group": [], "row": [], "latest": None}
			else:
				latest = newValue.get("latest", None)
				self.setLastSelected(newValue.get("group", None), group = True)
				self.setLastSelected(newValue.get("row", None), group = False)
				self.lastSelection["latest"] = latest
		elif (group):
			if (newValue is None):
				self.lastSelection["group"] = []
			else:
				if (isinstance(newValue, (list, tuple))):
					self.lastSelection["group"] = newValue
				elif (isinstance(newValue, (range, set, types.GeneratorType))):
					self.lastSelection["group"] = list(newValue)
				else:
					self.lastSelection["group"] = [newValue]
				self.lastSelection["latest"] = "group"
		else:
			if (newValue is None):
				self.lastSelection["row"] = []
			else:
				if (isinstance(newValue, (list, tuple))):
					self.lastSelection["row"] = newValue
				elif (isinstance(newValue, (range, set, types.GeneratorType))):
					self.lastSelection["row"] = list(newValue)
				else:
					self.lastSelection["row"] = [newValue]
				self.lastSelection["latest"] = "row"

	def _formatList(self, newValue, filterNone = False):
		if (isinstance(newValue, (range, types.GeneratorType))):
			newValue = list(newValue)
		elif (not isinstance(newValue, (list, tuple, set))):
			newValue = [newValue]

		if (any((not hasattr(item, '__dict__') for item in newValue))):
			objectList = []
			for catalogue in newValue:
				if (hasattr(catalogue, '__dict__')):
					objectList.append(catalogue)
					continue

				#Add Items
				contents = {self.columnCatalogue[column]["valueGetter"] if (isinstance(column, int)) else column: f"{text}" for column, text in catalogue.items()}
				contents["__repr__"] = lambda self: f"""ListItem({", ".join(f"{variable} = {getattr(self, variable).__repr__() if hasattr(getattr(self, variable), '__repr__') else getattr(self, variable)}" for variable in dir(self) if not variable.startswith("__"))})"""
				objectList.append(type("ListItem", (object,), contents)())
		else:
			#The user gave a list of objects
			objectList = newValue
		return objectList

	def setValue(self, newValue = None, filterNone = False, event = None):
		"""Sets the contextual value for the object associated with this handle to what the user supplies."""

		if (self.type is Types.drop):
			newValue = self.ensure_container(newValue, convertNone = False)

			if (filterNone is not None):
				if (filterNone):
					if (None in newValue):
						newValue = tuple(str(value) for value in newValue if value is not None) #Filter out None
				else:
					newValue = tuple(str(value) if (value is not None) else "" for value in newValue) #Replace None with blank space

			self.thing.Clear()
			self.thing.AppendItems(newValue) #(list) - What the choice options will now be now
			self.setChoices(newValue)

		elif (self.type is Types.view):
			objectList = self._formatList(newValue, filterNone = filterNone)
			self.thing.SetObjects(objectList)
			self.setChoices(objectList)

		elif (self.type is Types.tree):
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
			warnings.warn(f"Add {self.type.name} to setValue() for {self.__repr__()}", Warning, stacklevel = 2)

	def setSelection(self, newValue = None, event = None, deselectOthers = True, ensureVisible = True, group = False, triggerEvent = True):
		"""Sets the contextual value for the object associated with this handle to what the user supplies.
		None will deselect all items.
		"""

		if (self.type is Types.drop):
			if (newValue is not None):
				if (isinstance(newValue, str)):
					newValue = self.thing.FindString(newValue)

				if (newValue is None):
					errorMessage = f"Invalid drop list selection in setSelection() for {self.__repr__()}"
					raise ValueError(errorMessage)
			else:
				newValue = 0
			self.thing.SetSelection(newValue) #(int) - What the choice options will now be

		elif (self.type is Types.view):
			if (newValue is None):
				self.thing.UnselectAll()
				return

			newValue = self.ensure_container(newValue)

			if (any((not hasattr(item, '__dict__') for item in newValue))):
				### TO DO ### Make this check each item indiviually instead of assuming all are the same type
				if (group and True): #Check to see if there is a group labled that
					objectList = newValue
				else:
					print(newValue)
					ikiklk
			else:
				objectList = newValue

			existingList = self.thing.GetObjects()
			for item in objectList:
				if ((item not in existingList) and (item not in self.groups_ensured)):
					errorMessage = f"{item.__repr__()} is not in {self.__repr__()}"
					print("--", existingList)
					raise KeyError(errorMessage)
					print(errorMessage)
					return

			if (group):
				self.thing.SelectGroups(objectList, deselectOthers = deselectOthers)
				if (ensureVisible and objectList):
					self.thing.SelectGroup(objectList[0], deselectOthers = False, ensureVisible = ensureVisible)
			else:
				self.thing.SelectObjects(objectList, deselectOthers = deselectOthers)
				if (ensureVisible and objectList):
					self.thing.SelectObject(objectList[0], deselectOthers = False, ensureVisible = ensureVisible)

			if (objectList):
				if (triggerEvent):
					if (group):
						self.thing.TriggerEvent(ObjectListView.GroupSelectedEvent, row = objectList[0])
					else:
						self.thing.TriggerEvent(ObjectListView.SelectionChangedEvent, row = objectList[0])
				else:
					if (group):
						self._onSelectGroup()
					else:
						self._onSelectRow()
		else:
			warnings.warn(f"Add {self.type.name} to setSelection() for {self.__repr__()}", Warning, stacklevel = 2)

	def setChoices(self, choices = None):
		self.choices = choices or ()

	def setText(self, text = None, triggerEvent = True):

		if ((self.type is Types.drop) and (self.subtype.lower != "autocomplete")):
			return self.setSelection(text, triggerEvent = triggerEvent)

		if (triggerEvent):
			self.thing.SetValue(text or "")
		else:
			self.thing.ChangeValue(text or "")

	def update_autoComplete(self, choices = None, event = None):
		"""Updates the auto completer."""

		if (choices):
			self.setChoices(choices)

		self.thing.AutoComplete(self.choices or ())

	def reveal(self, row, event = None):
		"""Ensures that the given item's group is expanded and visible."""

		if (isinstance(row, (range, types.GeneratorType))):
			row = list(row)
		elif (not isinstance(row, (list, tuple, dict))):
			row = [row]

		if (any((not hasattr(item, '__dict__') for item in row))):
			ikiklk
		else:
			objectList = row

		for item in objectList:
			self.thing.Reveal(item)
			
	def addColumn(self, *args, **kwargs):
		self.setColumn(column = len(self.columnCatalogue), *args, **kwargs)

	def setColumn(self, column = None, title = None, label = None, width = None, align = None, sortLabel = None, groupSortLabel = None,
		hidden = None, editable = None, sortable = None, resizeable = None, searchable = None, reorderable = None,
		image = None, formatter = None, group = None, groupFormatter = None, minWidth = None, refresh = True, 
		renderer = None, rendererArgs = None, rendererKwargs = None, setter = None):
		"""Sets the contextual column for this handle."""

		#Create columns
		if (self.type is Types.view):
			if (column is None):
				column = len(self.columnCatalogue)

			if (column not in self.columnCatalogue):
				self.columnCatalogue[column] = {}

			self.columnCatalogue[column].setdefault("title", "")
			self.columnCatalogue[column].setdefault("width", -1)
			self.columnCatalogue[column].setdefault("align", "left")
			self.columnCatalogue[column].setdefault("minimumWidth", 5)
			self.columnCatalogue[column].setdefault("sortGetter", None)
			self.columnCatalogue[column].setdefault("valueGetter", None)
			self.columnCatalogue[column].setdefault("valueSetter", None)
			self.columnCatalogue[column].setdefault("imageGetter", None)
			self.columnCatalogue[column].setdefault("groupSortGetter", None)
			self.columnCatalogue[column].setdefault("stringConverter", None)

			self.columnCatalogue[column].setdefault("isHidden", False)
			self.columnCatalogue[column].setdefault("isEditable", True)
			self.columnCatalogue[column].setdefault("isSortable", True)
			self.columnCatalogue[column].setdefault("isResizeable", True)
			self.columnCatalogue[column].setdefault("isSearchable", True)
			self.columnCatalogue[column].setdefault("isReorderable", True)
			self.columnCatalogue[column].setdefault("isSpaceFilling", False)

			self.columnCatalogue[column].setdefault("renderer", None)
			self.columnCatalogue[column].setdefault("rendererArgs", [])
			self.columnCatalogue[column].setdefault("rendererKwargs", {})
			
			self.columnCatalogue[column].setdefault("groupKeyGetter", None)
			self.columnCatalogue[column].setdefault("groupKeyConverter", None)
			self.columnCatalogue[column].setdefault("useInitialLetterForGroupKey", False)
			self.columnCatalogue[column].setdefault("groupTitleSingleItem", None)
			self.columnCatalogue[column].setdefault("groupTitlePluralItems", None)

			if (title is not None):
				self.columnCatalogue[column]["title"] = title
			if (align is not None):
				self.columnCatalogue[column]["align"] = align
			if (label is not None):
				self.columnCatalogue[column]["valueGetter"] = label
			if (setter is not None):
				self.columnCatalogue[column]["valueSetter"] = setter
			if (sortLabel is not None):
				self.columnCatalogue[column]["sortGetter"] = sortLabel
			if (groupSortLabel is not None):
				self.columnCatalogue[column]["groupSortGetter"] = groupSortLabel
			if (image is not None):
				self.columnCatalogue[column]["imageGetter"] = image
			if (hidden is not None):
				self.columnCatalogue[column]["isHidden"] = hidden
			if (editable is not None):
				self.columnCatalogue[column]["isEditable"] = editable
			if (sortable is not None):
				self.columnCatalogue[column]["isSortable"] = sortable
			if (resizeable is not None):
				self.columnCatalogue[column]["isResizeable"] = resizeable
			if (searchable is not None):
				self.columnCatalogue[column]["isSearchable"] = searchable
			if (reorderable is not None):
				self.columnCatalogue[column]["isReorderable"] = reorderable
			if (minWidth is not None):
				self.columnCatalogue[column]["minimumWidth"] = minWidth
			if (formatter is not None):
				self.columnCatalogue[column]["stringConverter"] = formatter
			if (renderer is not None):
				self.columnCatalogue[column]["renderer"] = renderer
			if (rendererArgs is not None):
				self.columnCatalogue[column]["rendererArgs"] = rendererArgs
			if (rendererKwargs is not None):
				self.columnCatalogue[column]["rendererKwargs"] = rendererKwargs
			if (group is not None):
				if (isinstance(group, bool)):
					if (group):
						self.columnCatalogue[column]["useInitialLetterForGroupKey"] = True
				else:
					self.columnCatalogue[column]["useInitialLetterForGroupKey"] = False
					self.columnCatalogue[column]["groupKeyGetter"] = group
			if (groupFormatter is not None):
				self.columnCatalogue[column]["groupKeyConverter"] = groupFormatter

			if (width is not None):
				self.columnCatalogue[column]["width"] = width
			else:
				self.columnCatalogue[column]["width"] = self.getStringPixels(self.columnCatalogue[column]["title"])[0] + 40

			if (self.columnCatalogue[column]["width"] == -1):
				self.columnCatalogue[column]["isSpaceFilling"] = True
			else:
				self.columnCatalogue[column]["isSpaceFilling"] = False

			#Everything must have a label
			if (not self.thing.InReportView()):
				self.columnCatalogue[column]["valueGetter"] = f"value" 
			elif (self.columnCatalogue[column]["valueGetter"] is None):
				self.columnCatalogue[column]["valueGetter"] = f"unnamed_{column}" 

			#All images must be callable
			if ((self.columnCatalogue[column]["imageGetter"] is not None) and (not callable(self.columnCatalogue[column]["imageGetter"]))):
				value = self.columnCatalogue[column]["imageGetter"]
				self.columnCatalogue[column]["imageGetter"] = lambda item: value

			if (refresh):
				self.refreshColumns()
				self.refresh()
		else:
			warnings.warn(f"Add {self.type.name} to setColumns() for {self.__repr__()}", Warning, stacklevel = 2)

	def refreshColumns(self):
		if (self.type is Types.view):
			self.thing.SetColumns([ObjectListView.DataColumnDefn(**kwargs) for column, kwargs in sorted(self.columnCatalogue.items())])
		else:
			warnings.warn(f"Add {self.type.name} to setColumns() for {self.__repr__()}", Warning, stacklevel = 2)

	def refresh(self):
		self.thing.RepopulateList()

	def clearAll(self):
		self.columnCatalogue = {}
		self.thing.ClearAll()

	def expandAll(self, state = True):
		if (state):
			self.thing.ExpandAll()
		else:
			self.thing.CollapseAll()

		#Account for hidden/old/new groups
		for key in self.expanded.keys():
			self.expanded[key] = state
		self.expanded[None] = state

	def collapseAll(self, state = True):
		self.expandAll(state = not state)

	def hideGroup(self, column = None, state = True, refresh = True):
		"""Turns off row grouping.

		state (bool) - Determines if grouping is hidden or not
		column (int) - Which column to stop grouping by
			- If None: Will hide all grouping
			- If str: Will stop grouping by whichever column has this as it's variable

		Example Input: hideGroup()
		Example Input: hideGroup(column = 1)
		Example Input: hideGroup(column = "lorem")
		"""

		if (not state):
			self.showGroup(column = column, state = True, refresh = refresh)
			return

		if (column is not None):
			if (not isinstance(column, int)):
				for _column, catalogue in self.columnCatalogue.items():
					if (catalogue["valueGetter"] == column):
						column = _column
						break
				else:
					errorMessage = f"There is no column with the label {column} in showGroup() for {self.__repr__()}"
					raise KeyError(errorMessage)
						
			if (self.thing.GetAlwaysGroupByColumn() == column):
				self.thing.SetAlwaysGroupByColumn(None)

		self.thing.SetShowGroups(False)

	def showGroup(self, column = None, state = True, refresh = True):
		"""Turns on row grouping.

		state (bool) - Determines if grouping is shown or not
		column (int) - Which column to group by
			- If None: Will group by whichever column is being sorted by
			- If str: Will group by whichever column has this as it's variable

		Example Input: showGroup()
		Example Input: showGroup(column = 1)
		Example Input: showGroup(column = "lorem")
		"""

		if (not state):
			self.hideGroup(column = column, state = True, refresh = refresh)
			return

		self.thing.SetShowGroups(True)

		if (column is None):
			self.thing.SetAlwaysGroupByColumn(None)
		else:
			if (not isinstance(column, int)):
				for _column, catalogue in self.columnCatalogue.items():
					if (catalogue["valueGetter"] == column):
						column = _column
						break
				else:
					errorMessage = f"There is no column with the label {column} in showGroup() for {self.__repr__()}"
					raise KeyError(errorMessage)

			self.thing.SetAlwaysGroupByColumn(self.thing.columns[column])

	def showGroupCount(self, state = True):
		self.thing.SetShowItemCounts(state)

	def hideGroupCount(self, state = True):
		self.showGroupCount(not state)

	def setColor(self, even = None, odd = None, selected = None, group = None):
		if (even is not None):
			self.thing.evenRowsBackColor = self.getColor(even)
		if (odd is not None):
			self.thing.oddRowsBackColor = self.getColor(odd)
		if (selected is not None):
			self.selectionColor = self.getColor(selected)
		if (group is not None):
			self.thing.groupBackgroundColour = self.getColor(group)

	def getSortColumn(self):
		column = self.thing.GetSortColumn()
		if (column is not None):
			return column.title
		
	def getGroupColumn(self):
		column = self.thing.GetGroupByColumn()
		if (column is not None):
			return column.title

	def getColumnOrder(self, column = None):
		return {key: value.valueGetter for key, value in self.thing.GetColumnPosition(column = column).items()}

	def sortBy(self, label = None, ascending = True):
		if (label is None):
			self.thing.SetSortColumn(None, resortNow = True)
			# self.refreshColumns()
			# self.refresh()
			return

		if (not hasattr(label, '__dict__')):
			#The user passed in a non-object
			for _column, catalogue in self.columnCatalogue.items():
				if ((label == _column) or (label == catalogue["title"])):
					column = _column
					break
			else:
				errorMessage = f"Unknown column {label} in sortBy() for {self.__repr__()}"
				raise KeyError(errorMessage)
		else:
			#The user passed in an object
			jhkjkkjhjk

		if (self.thing.GetShowGroups()):
			self.thing.SortBy(column + 1)#, resortNow = True)
		else:
			self.thing.SortBy(column)#, resortNow = True)

	def sortGroups(self, ascending = True):
		# self.thing.SortGroups(ascending = ascending)

		def _getLowerCaseKey(group):
			try:
				return group.key.lower()
			except:
				return group.key

		if (self.thing.defaultGroupSortFunction is None):
			sortFunction = _getLowerCaseKey
		else:
			sortFunction = self.thing.defaultGroupSortFunction

		groups = sorted(self.thing.groups, key = sortFunction, reverse = not ascending)

		#Order the groups
		self.thing._SetGroups(groups)

	def enableUserSort(self, state = True):
		if (state):
			self.thing.EnableSorting()
		else:
			self.thing.DisableSorting()

	def updateUnsorted(self):
		# self.thing.UpdateUnsorted()
		pass

	def setUnsortedFunction(self, myFunction = None, widgetArg = True):
		pass
		# if (myFunction and widgetArg):
		# 	self.thing.SetUnsortedFunction(lambda *args: myFunction(*args, self))
		# else:
		# 	self.thing.SetUnsortedFunction(myFunction)

	def setSortFunction(self, myFunction = None, widgetArg = True):
		if (myFunction and widgetArg):
			self.thing.SetCompareFunction(lambda *args: myFunction(*args, self))
		else:
			self.thing.SetCompareFunction(myFunction)

	def setGroupSortFunction(self, myFunction = None, widgetArg = True):
		if (myFunction and widgetArg):
			self.thing.SetGroupCompareFunction(lambda *args: myFunction(*args, self))
		else:
			self.thing.SetGroupCompareFunction(myFunction)

	def setShowEmptyGroups(self, myFunction = None, widgetArg = True):
		if (myFunction and widgetArg):
			self.thing.SetShowEmptyGroups(lambda *args: myFunction(*args, self))
		else:
			self.thing.SetShowEmptyGroups(myFunction)

	def setFunction_getColor(self, myFunction = None, widgetArg = True):
		if (myFunction and widgetArg):
			self.thing.SetColorFunction(lambda *args: myFunction(*args, self))
		else:
			self.thing.SetColorFunction(myFunction)

	def ensureGroups(self, groupList = None):
		"""Makes sure these groups are shown, even if they are empty."""

		self.groups_ensured = groupList or []

		self.thing.SetEmptyGroups(self.groups_ensured)

	def setFilter(self, myFilter = None, widgetArg = True):
		if (myFilter and widgetArg):
			self.thing.SetFilter(lambda *args: myFilter(*args, self))
		else:
			self.thing.SetFilter(myFilter)

	def setEmptyListMessage(self, message):
		self.thing.SetEmptyListMsg(message)

	def setEmptyListFilterMsg(self, message):
		self.thing.SetEmptyListFilterMsg(message)

	def appendValue(self, newValue, where = -1, filterNone = None):
		"""Appends the given value to the current contextual value for this handle."""

		if (self.type is Types.tree):
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
						if (key is not None):
							branch = self.thing.AppendItem(where, str(key))

						if (value is not None):
							self.appendValue(value, branch)
				else:
					if (newValue is not None):
						branch = self.thing.AppendItem(where, str(newValue))

		elif (self.type is Types.view):
			objectList = self._formatList(newValue, filterNone = filterNone)
			self.thing.AddObjects(objectList)

		else:
			warnings.warn(f"Add {self.type.name} to appendValue() for {self.__repr__()}", Warning, stacklevel = 2)

	def removeValue(self, value):
		objectList = self._formatList(value)
		self.thing.RemoveObjects(objectList)

	def addContextMenuItem(self, row = None, function = None, widgetArg = True,**kwargs):
		if (function and widgetArg):
			self.thing.contextMenu.AddItem(row = row and self._formatList(row), function = lambda *args: function(*args, self), **kwargs)
		else:
			self.thing.contextMenu.AddItem(row = row and self._formatList(row), function = function, **kwargs)

	def addColumnContextMenuItem(self, function = None, widgetArg = True, **kwargs):
		if (function and widgetArg):
			self.thing.columnContextMenu.AddItem(function = lambda *args: function(*args, self), **kwargs)
		else:
			self.thing.columnContextMenu.AddItem(function = function, **kwargs)

	def setPasteEntireRow(self, state = None):
		self.thing.key_pasteEntireRow = state

	def setCopyEntireRow(self, state = None):
		self.thing.key_copyEntireRow = state

	def undo(self):
		self.thing.Undo()

	def redo(self):
		self.thing.Redo()

	def getUndoHistory(self):
		return self.thing.undoHistory

	def getRedoHistory(self):
		return self.thing.redoHistory

	def setUndoHistory(self, undoHistory = []):
		self.thing.SetUndoHistory(undoHistory)

	def setRedoHistory(self, redoHistory = []):
		self.thing.SetRedoHistory(redoHistory)

	def copy(self, row = None, column = None, *args, **kwargs):
		"""Copies the given rows and columns.

		row (handle) - The row to copy
			- If list: will copy all the given rows
			- If None: Will copy all rows

		column (handle) - The column to copy
			- If list: will copy all the given columns
			- If None: Will copy all columns

		Example Input: copy()
		"""

		if (row is not None):
			row = self.ensure_container(row)
		if (column is not None):
			column = self.ensure_container(column)

		self.thing.CopyObjectsToClipboard(row, column, *args, **kwargs)

	#Change Settings
	def setFunction_preClick(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type is Types.tree):
			self._betterBind(wx.EVT_TREE_SEL_CHANGING, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		else:
			warnings.warn(f"Add {self.type.name} to setFunction_preClick() for {self.__repr__()}", Warning, stacklevel = 2)
			
	def setFunction_postClick(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type is Types.drop):
			self._betterBind(wx.EVT_CHOICE, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		elif (self.type is Types.view):
			self._betterBind(ObjectListView.EVT_DATA_SELECTION_CHANGED, self.thing, myFunction, myFunctionArgs, myFunctionKwargs, mode = 2)
			self._betterBind(ObjectListView.EVT_DATA_SELECTION_CHANGED, self.thing, self._onSelectRow, rebind = True, mode = 2)

		elif (self.type is Types.tree):
			self._betterBind(wx.EVT_TREE_SEL_CHANGED, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		else:
			warnings.warn(f"Add {self.type.name} to setFunction_postClick() for {self.__repr__()}", Warning, stacklevel = 2)
			
	def setFunction_click(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		self.setFunction_postClick(myFunction = myFunction, myFunctionArgs = myFunctionArgs, myFunctionKwargs = myFunctionKwargs)
			
	def setFunction_groupClick(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type is Types.view):
			self._betterBind(ObjectListView.EVT_DATA_GROUP_SELECTED, self.thing, myFunction, myFunctionArgs, myFunctionKwargs, mode = 2)
			self._betterBind(ObjectListView.EVT_DATA_GROUP_SELECTED, self.thing, self._onSelectGroup, rebind = True, mode = 2)
		else:
			warnings.warn(f"Add {self.type.name} to setFunction_groupClick() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_preEdit(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type is Types.view):
			self._betterBind(ObjectListView.EVT_DATA_CELL_EDIT_STARTING, self.thing, myFunction, myFunctionArgs, myFunctionKwargs, mode = 2)
		elif (self.type is Types.tree):
			self._betterBind(wx.EVT_TREE_BEGIN_LABEL_EDIT, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		else:
			warnings.warn(f"Add {self.type.name} to setFunction_preEdit() for {self.__repr__()}", Warning, stacklevel = 2)
			
	def setFunction_postEdit(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type is Types.view):
			self._betterBind(ObjectListView.EVT_DATA_CELL_EDIT_FINISHING, self.thing, myFunction, myFunctionArgs, myFunctionKwargs, mode = 2)
			# self._betterBind(ObjectListView.EVT_DATA_CELL_EDIT_FINISHED, self.thing, myFunction, myFunctionArgs, myFunctionKwargs, mode = 2)
		elif (self.type is Types.tree):
			self._betterBind(wx.EVT_TREE_END_LABEL_EDIT, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		else:
			warnings.warn(f"Add {self.type.name} to setFunction_postEdit() for {self.__repr__()}", Warning, stacklevel = 2)
			
	def setFunction_edit(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		self.setFunction_postEdit(myFunction = myFunction, myFunctionArgs = myFunctionArgs, myFunctionKwargs = myFunctionKwargs)

	def setFunction_preDrag(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type is Types.view):
			if (not self.dragable):
				warnings.warn(f"'drag' was not enabled for {self.__repr__()} upon creation", Warning, stacklevel = 2)
			else:
				self.preDragFunction = myFunction
				self.preDragFunctionArgs = myFunctionArgs
				self.preDragFunctionKwargs = myFunctionKwargs
		else:
			warnings.warn(f"Add {self.type.name} to setFunction_preDrag() for {self.__repr__()}", Warning, stacklevel = 2)
			
	def setFunction_postDrag(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type is Types.view):
			if (not self.dragable):
				warnings.warn(f"'drag' was not enabled for {self.__repr__()} upon creation", Warning, stacklevel = 2)
			else:
				#wx.dataview.EVT_DATAVIEW_ITEM_BEGIN_DRAG
				self.postDragFunction = myFunction
				self.postDragFunctionArgs = myFunctionArgs
				self.postDragFunctionKwargs = myFunctionKwargs
		else:
			warnings.warn(f"Add {self.type.name} to setFunction_postDrag() for {self.__repr__()}", Warning, stacklevel = 2)
			
	def setFunction_preDrop(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type is Types.view):
			if (self.myDropTarget is None):
				warnings.warn(f"'drop' was not enabled for {self.__repr__()} upon creation", Warning, stacklevel = 2)
			else:
				self.myDropTarget.preDropFunction = myFunction
				self.myDropTarget.preDropFunctionArgs = myFunctionArgs
				self.myDropTarget.preDropFunctionKwargs = myFunctionKwargs
		else:
			warnings.warn(f"Add {self.type.name} to setFunction_preDrop() for {self.__repr__()}", Warning, stacklevel = 2)
			
	def setFunction_postDrop(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type is Types.view):
			if (self.myDropTarget is None):
				warnings.warn(f"'drop' was not enabled for {self.__repr__()} upon creation", Warning, stacklevel = 2)
			else:
				#wx.dataview.EVT_DATAVIEW_ITEM_DROP
				self.myDropTarget.postDropFunction = myFunction
				self.myDropTarget.postDropFunctionArgs = myFunctionArgs
				self.myDropTarget.postDropFunctionKwargs = myFunctionKwargs
		else:
			warnings.warn(f"Add {self.type.name} to setFunction_postDrop() for {self.__repr__()}", Warning, stacklevel = 2)
			
	def setFunction_dragOver(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type is Types.view):
			if (self.myDropTarget is None):
				warnings.warn(f"'drop' was not enabled for {self.__repr__()} upon creation", Warning, stacklevel = 2)
			else:
				#wx.dataview.EVT_DATAVIEW_ITEM_DROP_POSSIBLE
				self.myDropTarget.dragOverFunction = myFunction
				self.myDropTarget.dragOverFunctionArgs = myFunctionArgs
				self.myDropTarget.dragOverFunctionKwargs = myFunctionKwargs
		else:
			warnings.warn(f"Add {self.type.name} to setFunction_dragOver() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_preCollapse(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type is Types.view):
			self._betterBind(ObjectListView.EVT_DATA_COLLAPSING, self.thing, myFunction, myFunctionArgs, myFunctionKwargs, mode = 2)
		elif (self.type is Types.tree):
			self._betterBind(wx.EVT_TREE_ITEM_COLLAPSING, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		else:
			warnings.warn(f"Add {self.type.name} to setFunction_preCollapse() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_postCollapse(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type is Types.view):
			self._betterBind(ObjectListView.EVT_DATA_COLLAPSED, self.thing, myFunction, myFunctionArgs, myFunctionKwargs, mode = 2)
		elif (self.type is Types.tree):
			self._betterBind(wx.EVT_TREE_ITEM_COLLAPSED, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		else:
			warnings.warn(f"Add {self.type.name} to setFunction_postCollapse() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_preExpand(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type is Types.view):
			self._betterBind(ObjectListView.EVT_DATA_EXPANDING, self.thing, myFunction, myFunctionArgs, myFunctionKwargs, mode = 2)
		elif (self.type is Types.tree):
			self._betterBind(wx.EVT_TREE_ITEM_EXPANDING, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		else:
			warnings.warn(f"Add {self.type.name} to setFunction_preExpand() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_postExpand(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type is Types.view):
			self._betterBind(ObjectListView.EVT_DATA_EXPANDED, self.thing, myFunction, myFunctionArgs, myFunctionKwargs, mode = 2)
		elif (self.type is Types.tree):
			self._betterBind(wx.EVT_TREE_ITEM_EXPANDED, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		else:
			warnings.warn(f"Add {self.type.name} to setFunction_postExpand() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_rightClick(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type is Types.tree):
			self._betterBind(wx.EVT_TREE_ITEM_RIGHT_CLICK, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		elif (self.type is Types.view):
			self._betterBind(ObjectListView.EVT_DATA_CELL_RIGHT_CLICK, self.thing, myFunction, myFunctionArgs, myFunctionKwargs, mode = 2)
		else:
			warnings.warn(f"Add {self.type.name} to setFunction_rightClick() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_middleClick(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type is Types.tree):
			self._betterBind(wx.EVT_TREE_ITEM_MIDDLE_CLICK, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		else:
			warnings.warn(f"Add {self.type.name} to setFunction_middleClick() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_doubleClick(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type is Types.tree):
			self._betterBind(wx.EVT_TREE_ITEM_ACTIVATED, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		elif (self.type is Types.view):
			self._betterBind(ObjectListView.EVT_DATA_CELL_ACTIVATED, self.thing, myFunction, myFunctionArgs, myFunctionKwargs, mode = 2)
		else:
			warnings.warn(f"Add {self.type.name} to setFunction_middleClick() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_clickLabel(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type is Types.view):
			self._betterBind(ObjectListView.EVT_DATA_COLUMN_HEADER_LEFT_CLICK, self.thing, myFunction, myFunctionArgs, myFunctionKwargs, mode = 2)
		else:
			warnings.warn(f"Add {self.type.name} to setFunction_labelClick() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_rightClickLabel(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type is Types.view):
			self._betterBind(ObjectListView.EVT_DATA_COLUMN_HEADER_RIGHT_CLICK, self.thing, myFunction, myFunctionArgs, myFunctionKwargs, mode = 2)
		else:
			warnings.warn(f"Add {self.type.name} to setFunction_rightClickLabel() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_keyDown(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type is Types.tree):
			self._betterBind(wx.EVT_TREE_KEY_DOWN, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		else:
			warnings.warn(f"Add {self.type.name} to setFunction_keyDown() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_copy(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type is Types.view):
			self._betterBind(ObjectListView.EVT_DATA_COPY, self.thing, myFunction, myFunctionArgs, myFunctionKwargs, mode = 2)
		else:
			warnings.warn(f"Add {self.type.name} to setFunction_postEdit() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_preCopy(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type is Types.view):
			self._betterBind(ObjectListView.EVT_DATA_COPYING, self.thing, myFunction, myFunctionArgs, myFunctionKwargs, mode = 2)
		else:
			warnings.warn(f"Add {self.type.name} to setFunction_preCopy() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_postCopy(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type is Types.view):
			self._betterBind(ObjectListView.EVT_DATA_COPIED, self.thing, myFunction, myFunctionArgs, myFunctionKwargs, mode = 2)
		else:
			warnings.warn(f"Add {self.type.name} to setFunction_postCopy() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_paste(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type is Types.view):
			self._betterBind(ObjectListView.EVT_DATA_PASTE, self.thing, myFunction, myFunctionArgs, myFunctionKwargs, mode = 2)
		else:
			warnings.warn(f"Add {self.type.name} to setFunction_paste() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_prePaste(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type is Types.view):
			self._betterBind(ObjectListView.EVT_DATA_PASTING, self.thing, myFunction, myFunctionArgs, myFunctionKwargs, mode = 2)
		else:
			warnings.warn(f"Add {self.type.name} to setFunction_prePaste() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_toolTip(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type is Types.tree):
			self._betterBind(wx.EVT_TREE_ITEM_GETTOOLTIP, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		else:
			warnings.warn(f"Add {self.type.name} to setFunction_toolTip() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_itemMenu(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type is Types.tree):
			self._betterBind(wx.EVT_TREE_ITEM_MENU, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		else:
			warnings.warn(f"Add {self.type.name} to setFunction_itemMenu() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_sort(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type is Types.view):
			self._betterBind(ObjectListView.EVT_DATA_COLUMN_SORTED, self.thing, myFunction, myFunctionArgs, myFunctionKwargs, mode = 2)
		else:
			warnings.warn(f"Add {self.type.name} to setFunction_sort() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_reorder(self, *args, **kwargs):
		return self.setFunction_postReorder(*args, **kwargs)

	def setFunction_preReorder(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type is Types.view):
			self._betterBind(ObjectListView.EVT_DATA_REORDERING, self.thing, myFunction, myFunctionArgs, myFunctionKwargs, mode = 2)
		else:
			warnings.warn(f"Add {self.type.name} to setFunction_preReorder() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_postReorder(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type is Types.view):
			self._betterBind(ObjectListView.EVT_DATA_REORDERED, self.thing, myFunction, myFunctionArgs, myFunctionKwargs, mode = 2)
		else:
			warnings.warn(f"Add {self.type.name} to setFunction_postReorder() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_reorderCancel(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type is Types.view):
			self._betterBind(ObjectListView.EVT_DATA_REORDER_CANCEL, self.thing, myFunction, myFunctionArgs, myFunctionKwargs, mode = 2)
		else:
			warnings.warn(f"Add {self.type.name} to setFunction_reorderCancel() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_groupCreate(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type is Types.view):
			self._betterBind(ObjectListView.EVT_DATA_GROUP_CREATING, self.thing, myFunction, myFunctionArgs, myFunctionKwargs, mode = 2)
		else:
			warnings.warn(f"Add {self.type.name} to setFunction_groupCreate() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_undo(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type is Types.view):
			self._betterBind(ObjectListView.EVT_DATA_UNDO, self.thing, myFunction, myFunctionArgs, myFunctionKwargs, mode = 2)
		else:
			warnings.warn(f"Add {self.type.name} to setFunction_undo() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_undoTrack(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type is Types.view):
			self._betterBind(ObjectListView.EVT_DATA_UNDO_TRACK, self.thing, myFunction, myFunctionArgs, myFunctionKwargs, mode = 2)
		else:
			warnings.warn(f"Add {self.type.name} to setFunction_undoTrack() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_canUndo(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type is Types.view):
			self._betterBind(ObjectListView.EVT_DATA_UNDO_FIRST, self.thing, myFunction, myFunctionArgs, myFunctionKwargs, mode = 2)
		else:
			warnings.warn(f"Add {self.type.name} to setFunction_canUndo() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_cantUndo(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type is Types.view):
			self._betterBind(ObjectListView.EVT_DATA_UNDO_EMPTY, self.thing, myFunction, myFunctionArgs, myFunctionKwargs, mode = 2)
		else:
			warnings.warn(f"Add {self.type.name} to setFunction_cantUndo() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_redo(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type is Types.view):
			self._betterBind(ObjectListView.EVT_DATA_REDO, self.thing, myFunction, myFunctionArgs, myFunctionKwargs, mode = 2)
		else:
			warnings.warn(f"Add {self.type.name} to setFunction_redo() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_canRedo(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type is Types.view):
			self._betterBind(ObjectListView.EVT_DATA_REDO_FIRST, self.thing, myFunction, myFunctionArgs, myFunctionKwargs, mode = 2)
		else:
			warnings.warn(f"Add {self.type.name} to setFunction_canRedo() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_cantRedo(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type is Types.view):
			self._betterBind(ObjectListView.EVT_DATA_REDO_EMPTY, self.thing, myFunction, myFunctionArgs, myFunctionKwargs, mode = 2)
		else:
			warnings.warn(f"Add {self.type.name} to setFunction_cantRedo() for {self.__repr__()}", Warning, stacklevel = 2)

	def setReadOnly(self, state = True):
		"""Sets the contextual readOnly for the object associated with this handle to what the user supplies."""

		if (self.type is Types.drop):
			self.setDisable(state)
		else:
			warnings.warn(f"Add {self.type.name} to setReadOnly() for {self.__repr__()}", Warning, stacklevel = 2)

	def setItemColor(self, row = None, column = None, color = "white"):
		"""Sets the contextual row color for the object associated with this handle to what the user supplies.
		If both row and column are given, only the cell will 

		row (object) - Which row to change the color of
		column (int) - Which column to change the color of
		color (str)  - What color to make the rows/columns
			- If tuple: Will interperet as (Red, Green, Blue). Values can be integers from 0 to 255 or floats from 0.0 to 1.0
			- If None: Will use the origonal color for the row

		Example Input: setItemColor(0, color = "grey")
		Example Input: setItemColor(0, color = (255, 0, 0))
		Example Input: setItemColor(0, color = (0.5, 0.5, 0.5))
		Example Input: setItemColor(slice(None, None, None))
		Example Input: setItemColor(slice(1, 3, None))
		Example Input: setItemColor(slice(None, None, 2))
		"""

		if (self.type is Types.view):
			if (color is None):
				colorHandle = None
			else:
				colorHandle = self.getColor(color)

			if (row is not None):
				if (column is not None):
					self.thing.SetCellColour(row, column, colorHandle)
				else:
					self.thing.SetRowColour(row, colorHandle)
			else:
				if (column is not None):
					self.thing.SetColumnColour(column, colorHandle)
				else:
					self.thing.SetBackgroundColour(colorHandle)
		else:
			warnings.warn(f"Add {self.type.name} to setItemColor() for {self.__repr__()}", Warning, stacklevel = 2)

	#Event functions
	def _onDragList_beginDragAway(self, event, label = None,
		deleteOnDrop = True, overrideCopy = False, allowExternalAppDelete = True):
		"""Used to begin dragging an item away from a list.
		Modified code from: https://www.tutorialspoint.com/wxpython/wxpython_drag_and_drop.htm
		"""
		global dragDropDestination

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
		self.runMyFunction(self.preDragFunction, self.preDragFunctionArgs, self.preDragFunctionKwargs, event = event, includeEvent = True)

		#Begin dragging item
		originList_object.SetData(textToDrag_object)
		dragResult = originList_object.DoDragDrop(True)

		#Remove the dragged item from the list
		if (deleteOnDrop):
			#Make sure the text sucessfully went somewhere
			if ((dragResult != wx.DragNone) and (dragResult != wx.DragError) and (dragResult != wx.DragCancel)):
				if ((dragResult != wx.DragCopy) or ((dragResult == wx.DragCopy) and (overrideCopy))):
					#Account for dropping it into a different application
					if (dragDropDestination is not None):
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
		self.runMyFunction(self.postDragFunction, self.postDragFunctionArgs, self.postDragFunctionKwargs, event = event, includeEvent = True)

		event.Skip()

	# def _onEditList_checkReadOnly(self, event, editable):
	#   """Used to make sure the user is allowed to edit the current item.
	#   Special thanks to ErwinP for how to edit certain columns on https://stackoverflow.com/questions/12806542/wx-listctrl-with-texteditmixin-disable-editing-of-selected-cells
	#   """

	#   #Get the current selection's column
	#   thing = self._getObjectWithEvent(event)
	#   column = self.thing.GetFocusedItem()

	#   if (column not in editable):
	#       event.Veto()
	#   else:
	#       if (not editable[column]):
	#           event.Veto()
	#       else:

	#   event.Skip()

	def _onSelectRow(self, event = None):
		"""Tracks the last row selection made."""

		self.setLastSelected(self.getValue(group = False), group = False)
		
		if (event is not None):
			event.Skip()

	def _onSelectGroup(self, event = None):
		"""Tracks the last group selection made."""

		self.setLastSelected(self.getValue(group = True), group = True)
		
		if (event is not None):
			event.Skip()

	class _ListFull(ObjectListView.DataObjectListView):
		def __init__(self, parent, widget, myId = wx.ID_ANY, position = wx.DefaultPosition, size = wx.DefaultSize, **kwargs):
			"""Creates the list control object."""
			
			#Load in modules
			ObjectListView.DataObjectListView.__init__(self, widget, id = myId, pos = position, size = size, **kwargs)

			#Fix class type
			self.__name__ = "wxListCtrl"
			
			#Internal variables
			self.parent = parent

	class _DragTextDropTarget(wx.TextDropTarget):
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

			Example Input: _DragTextDropTarget(thing)
			Example Input: _DragTextDropTarget(thing, -1)
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

		def OnDragOver(self, x, y, d):
			"""Overridden function. Needed to make this work."""
			
			self.parent.runMyFunction(self.dragOverFunction, self.dragOverFunctionArgs, self.dragOverFunctionKwargs)

			return wx.DragCopy
			
		def OnDropText(self, x, y, data):
			"""Overridden function. Needed to make this work."""

			global dragDropDestination

			#Run pre-functions
			self.parent.runMyFunction(self.preDropFunction, self.preDropFunctionArgs, self.preDropFunctionKwargs)

			#Determine how to handle recieving the text
			if (self.classType == "wxListCtrl"):
				itemCount = self.parent.GetItemCount()

				#Configure drop point
				if (self.insertMode is not None):
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
							if (columnFound is not None):
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
			self.parent.runMyFunction(self.postDropFunction, self.postDropFunctionArgs, self.postDropFunctionKwargs)

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

		if (self.type is Types.box):
			value = len(self.getValue())

		elif (self.type is Types.spinner):
			if (returnMax):
				value = self.thing.GetMax()
			else:
				value = self.thing.GetMin()

		elif (self.type is Types.slider):
			if (returnMax):
				value = self.thing.GetMax()
			else:
				value = self.thing.GetMin()

		elif (self.type is Types.search):
			value = len(self.getValue())

		else:
			warnings.warn(f"Add {self.type.name} to __len__() for {self.__repr__()}", Warning, stacklevel = 2)
			value = 0

		return value

	def _build(self, argument_catalogue):
		"""Determiens which build system to use for this handle."""

		def _build_slider():
			"""Builds a wx slider object."""
			nonlocal self, argument_catalogue

			vertical = self._getArguments(argument_catalogue, "vertical")
			myInitial, myMin, myMax = self._getArguments(argument_catalogue, ["myInitial", "myMin", "myMax"])

			#Apply settings
			if (vertical):
				style = "wx.SL_HORIZONTAL"
			else:
				style = "wx.SL_VERTICAL"

			# wx.SL_MIN_MAX_LABELS: Displays minimum, maximum labels (new since wxWidgets 2.9.1).
			# wx.SL_VALUE_LABEL: Displays value label (new since wxWidgets 2.9.1).
			# wx.SL_LABELS: Displays minimum, maximum and value labels (same as wx.SL_VALUE_LABEL and wx.SL_MIN_MAX_LABELS together).
			
			# wx.SL_LEFT: Displays ticks on the left and forces the slider to be vertical.
			# wx.SL_RIGHT: Displays ticks on the right and forces the slider to be vertical.
			# wx.SL_TOP: Displays ticks on the top.
			# wx.SL_BOTTOM: Displays ticks on the bottom (this is the default).

			# wx.SL_SELRANGE: Allows the user to select a range on the slider. Windows only.
			# wx.SL_INVERSE: Inverses the minimum and maximum endpoints on the slider. Not compatible with wx.SL_SELRANGE.

			myId = self._getId(argument_catalogue)

			#Create the thing to put in the grid
			self.thing = wx.Slider(self.parent.thing, id = myId, value = myInitial, minValue = myMin, maxValue = myMax, style = eval(style, {'__builtins__': None, "wx": wx}, {}))

			#Bind the function(s)
			myFunction = self._getArguments(argument_catalogue, "myFunction")
			if (myFunction is not None):
				myFunctionArgs, myFunctionKwargs = self._getArguments(argument_catalogue, ["myFunctionArgs", "myFunctionKwargs"])
				self.setFunction_postEdit(myFunction, myFunctionArgs, myFunctionKwargs)

			# EVT_SCROLL_TOP
			# EVT_SCROLL_BOTTOM
			# EVT_SCROLL_LINEUP
			# EVT_SCROLL_LINEDOWN
			# EVT_SCROLL_PAGEUP
			# EVT_SCROLL_PAGEDOWN
			# EVT_SCROLL_THUMBTRACK
			# EVT_SCROLL_THUMBRELEASE

		def _build_inputBox():
			"""Builds a wx text control or ip address control object."""
			nonlocal self, argument_catalogue

			text, ipAddress, maxLength, verifier = self._getArguments(argument_catalogue, ["text", "ipAddress", "maxLength", "verifier"])
			password, readOnly, tab, wrap, formatter = self._getArguments(argument_catalogue, ["password", "readOnly", "tab", "wrap", "formatter"])
			autoComplete, caseSensitive, alwaysShow = self._getArguments(argument_catalogue, ["autoComplete", "caseSensitive", "alwaysShow"])
			onSelect_hide, onSelect_update, onKey_update = self._getArguments(argument_catalogue, ["onSelect_hide", "onSelect_update", "onKey_update"])

			#Prepare style attributes
			style = [wx.TE_RICH]
			if (password):
				style.append(wx.TE_PASSWORD)

			if (readOnly):
				style.append(wx.TE_READONLY)

			if (tab):
				style.append(wx.TE_PROCESS_TAB) #Interpret 'Tab' as 4 spaces

			if (wrap is not None):
				if (wrap > 0):
					style.extend((wx.TE_MULTILINE, wx.TE_WORDWRAP))
				else:
					style.extend((wx.TE_CHARWRAP, wx.TE_MULTILINE))

			# if (enterFunction is not None):
				#Interpret 'Enter' as \n
			#   style.append(wx.TE_PROCESS_ENTER)

			#Account for empty text
			if (text is None):
				text = wx.EmptyString

			myId = self._getId(argument_catalogue)

			#Create the thing to put in the grid
			if (autoComplete):
				self.subType = "autoComplete"
				self.thing = MyUtilities.wxPython.AutocompleteTextCtrl(self.parent, id = myId, verifier = verifier,
					value = text, style = style, caseSensitive = caseSensitive, alwaysShow = alwaysShow, formatter = formatter, 
					onSelect_hide = onSelect_hide, onSelect_update = onSelect_update, onKey_update = onKey_update)

				#Set maximum length
				if (maxLength is not None):
					self.thing.SetMaxLength(maxLength)
			
			elif (ipAddress):
				self.subType = "ipAddress"
				self.thing = wx.lib.masked.ipaddrctrl.IpAddrCtrl(self.parent.thing, id = myId, style = functools.reduce(operator.ior, style or (0,)))

				if (text != wx.EmptyString):
					self.thing.SetValue(text)
			else:
				self.subType = "normal"
				self.thing = wx.TextCtrl(self.parent.thing, id = myId, value = text, style = functools.reduce(operator.ior, style or (0,)))

				#Set maximum length
				if (maxLength is not None):
					self.thing.SetMaxLength(maxLength)

			#flags += "|wx.RESERVE_SPACE_EVEN_IF_HIDDEN"

			#Bind the function(s)
			myFunction, enterFunction, postEditFunction, preEditFunction = self._getArguments(argument_catalogue, ["myFunction", "enterFunction", "postEditFunction", "preEditFunction"])
			
			#self._betterBind(wx.EVT_CHAR, self.thing, enterFunction, enterFunctionArgs, enterFunctionKwargs)
			#self._betterBind(wx.EVT_KEY_UP, self.thing, self.testFunction, myFunctionArgs, myFunctionKwargs)
			if (myFunction is not None):
				myFunctionArgs, myFunctionKwargs = self._getArguments(argument_catalogue, ["myFunctionArgs", "myFunctionKwargs"])
				self.setFunction_click(myFunction, myFunctionArgs, myFunctionKwargs)

			if (enterFunction is not None):
				enterFunctionArgs, enterFunctionKwargs = self._getArguments(argument_catalogue, ["enterFunctionArgs", "enterFunctionKwargs"])
				self.setFunction_enter(enterFunction, enterFunctionArgs, enterFunctionKwargs)
			
			if (postEditFunction is not None):
				postEditFunctionArgs, postEditFunctionKwargs = self._getArguments(argument_catalogue, ["postEditFunctionArgs", "postEditFunctionKwargs"])
				self.setFunction_postEdit(postEditFunction, postEditFunctionArgs, postEditFunctionKwargs)
			
			if (preEditFunction is not None):
				preEditFunctionArgs, preEditFunctionKwargs = self._getArguments(argument_catalogue, ["preEditFunctionArgs", "preEditFunctionKwargs"])
				self.setFunction_preEdit(preEditFunction, preEditFunctionArgs, preEditFunctionKwargs)

		def _build_inputSearch():
			"""Builds a wx search control object."""
			nonlocal self, argument_catalogue

			searchButton, cancelButton, tab, alignment = self._getArguments(argument_catalogue, ["searchButton", "cancelButton", "tab", "alignment"])
			menuLabel, menuFunction, menuReplaceText, hideSelection, = self._getArguments(argument_catalogue, ["menuLabel", "menuFunction", "menuReplaceText", "hideSelection"])
			myFunction, enterFunction, searchFunction, cancelFunction = self._getArguments(argument_catalogue, ["myFunction", "enterFunction", "searchFunction", "cancelFunction"])
			choices, autoComplete = self._getArguments(argument_catalogue, ["choices", "autoComplete"])

			#Configure Settings
			style = [wx.TE_PROCESS_ENTER]

			if (tab):
				style.append(wx.TE_PROCESS_TAB) #Interpret 'Tab' as 4 spaces

			if (not hideSelection):
				style.append(wx.TE_NOHIDESEL)

			if (alignment is not None):
				if (isinstance(alignment, bool)):
					if (alignment):
						style.append(wx.TE_LEFT)
					else:
						style.append(wx.TE_CENTRE)
				elif (alignment == 0):
					style.append(wx.TE_LEFT)
				elif (alignment == 1):
					style.append(wx.TE_RIGHT)
				else:
					style.append(wx.TE_CENTRE)
			else:
				style.append(wx.TE_CENTRE)

			myId = self._getId(argument_catalogue)

			#Create the thing to put in the grid
			self.thing = wx.SearchCtrl(self.parent.thing, id = myId, value = wx.EmptyString, style = functools.reduce(operator.ior, style or (0,)))

			self.setChoices(choices)
			self.update_autoComplete()

			#Create the menu associated with this widget
			if (isinstance(menuLabel, handle_Menu)):
				self.myMenu = menuLabel
			else:
				self.myMenu = self._makeMenu(label = menuLabel)
			self.nest(self.myMenu)

			#Determine if additional features are enabled
			if (searchButton is not None):
				self.thing.ShowSearchButton(True)
			
			if (cancelButton is not None):
				self.thing.ShowCancelButton(True)

			#Bind the function(s)
			if (myFunction is not None):
				myFunctionArgs, myFunctionKwargs = self._getArguments(argument_catalogue, ["myFunctionArgs", "myFunctionKwargs"])
				self.setFunction_click(myFunction, myFunctionArgs, myFunctionKwargs)

			if (enterFunction is not None):
				enterFunctionArgs, enterFunctionKwargs = self._getArguments(argument_catalogue, ["enterFunctionArgs", "enterFunctionKwargs"])
				self.setFunction_enter(enterFunction, enterFunctionArgs, enterFunctionKwargs)

			if (searchFunction is not None):
				searchFunctionArgs, searchFunctionKwargs = self._getArguments(argument_catalogue, ["searchFunctionArgs", "searchFunctionKwargs"])
				self.setFunction_search(searchFunction, searchFunctionArgs, searchFunctionKwargs)

			if (cancelFunction is not None):
				cancelFunctionArgs, cancelFunctionKwargs = self._getArguments(argument_catalogue, ["cancelFunctionArgs", "cancelFunctionKwargs"])
				self.setFunction_cancel(cancelFunction, cancelFunctionArgs, cancelFunctionKwargs)

			if (menuFunction is not None):
				menuFunctionArgs, menuFunctionKwargs = self._getArguments(argument_catalogue, ["menuFunctionArgs", "menuFunctionKwargs"])
				self.setFunction_menuSelect(menuFunction, menuFunctionArgs, menuFunctionKwargs)
			
			if (menuReplaceText):
				self.setFunction_menuSelect(self._onSearch_replaceText)

		def _build_inputSpinner():
			"""Builds a wx search control object."""
			nonlocal self, argument_catalogue

			useFloat, readOnly, increment, digits, size = self._getArguments(argument_catalogue, ["useFloat", "readOnly", "increment", "digits", "size"])
			myInitial, myMin, myMax, exclude, useHex = self._getArguments(argument_catalogue, ["myInitial", "myMin", "myMax", "exclude", "useHex"])

			#Remember values
			self.exclude = exclude

			#wx.SP_ARROW_KEYS: The user can use arrow keys to change the value.
			#wx.SP_WRAP: The value wraps at the minimum and maximum.
			style = "wx.SP_ARROW_KEYS|wx.SP_WRAP"

			myId = self._getId(argument_catalogue)

			#Create the thing to put in the grid
			if (useFloat):
				style = "wx.lib.agw.floatspin.FS_LEFT"
				if (readOnly):
					style += "|wx.lib.agw.floatspin.FS_READONLY"

				if (increment is None):
					increment = 0.1

				if (digits is None):
					digits = 1

				self.subType = "float"
				self.thing = wx.lib.agw.floatspin.FloatSpin(self.parent.thing, id = myId, pos = wx.DefaultPosition, size = size, style = wx.SP_ARROW_KEYS|wx.SP_WRAP, value = myInitial, min_val = myMin, max_val = myMax, increment = increment, digits = digits, agwStyle = eval(style, {'__builtins__': None, "wx": wx}, {}))
			else:
				if (increment is not None):
					style = "wx.lib.agw.floatspin.FS_LEFT"
					self.subType = "float"
					self.thing = wx.lib.agw.floatspin.FloatSpin(self.parent.thing, id = myId, pos = wx.DefaultPosition, size = size, style = wx.SP_ARROW_KEYS|wx.SP_WRAP, value = myInitial, min_val = myMin, max_val = myMax, increment = increment, digits = -1, agwStyle = eval(style, {'__builtins__': None, "wx": wx}, {}))
					self.thing.SetDigits(0)
				else:
					self.subType = "normal"
					self.thing = wx.SpinCtrl(self.parent.thing, id = myId, value = wx.EmptyString, size = size, style = eval(style, {'__builtins__': None, "wx": wx}, {}), min = myMin, max = myMax, initial = myInitial)

				if (readOnly):
					self.thing.SetReadOnly()

			if (useHex):
				self.subType += "_base16"
				self.thing.SetBase(16)
			else:
				self.subType += "_base10"
				self.thing.SetBase(10)

			#Remember values
			self.previousValue = self.thing.GetValue()

			#Bind the function(s)
			myFunction, changeTextFunction = self._getArguments(argument_catalogue, ["myFunction", "changeTextFunction"])

			if (myFunction is not None):
				myFunctionArgs, myFunctionKwargs = self._getArguments(argument_catalogue, ["myFunctionArgs", "myFunctionKwargs"])
				self.setFunction_click(myFunction, myFunctionArgs, myFunctionKwargs)
	
			# if (changeTextFunction is not None):
			#   if (isinstance(changeTextFunction, bool)):
			#       if (changeTextFunction and (myFunction is not None)):
			#           self._betterBind(wx.EVT_TEXT, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
			#   else:
			#       changeTextFunctionArgs, changeTextFunctionKwargs = self._getArguments(argument_catalogue, ["changeTextFunctionArgs", "changeTextFunctionKwargs"])
			#       self._betterBind(wx.EVT_TEXT, self.thing, changeTextFunction, changeTextFunctionArgs, changeTextFunctionKwargs)

			if (not ((self.exclude is None) or (isinstance(self.exclude, (list, tuple, range)) and (len(self.exclude) == 0)))):
				self._betterBind(wx.EVT_KILL_FOCUS, self.thing, self._onCheckValue_exclude)
		
		#########################################################

		self._preBuild(argument_catalogue)

		if (self.type is Types.box):
			_build_inputBox()
		elif (self.type is Types.spinner):
			_build_inputSpinner()
		elif (self.type is Types.slider):
			_build_slider()
		elif (self.type is Types.search):
			_build_inputSearch()
		else:
			warnings.warn(f"Add {self.type.name} to _build() for {self.__repr__()}", Warning, stacklevel = 2)

		self._postBuild(argument_catalogue)

	#Getters
	def getValue(self, event = None):
		"""Returns what the contextual value is for the object associated with this handle."""

		if (self.type is Types.box):
			value = self.thing.GetValue() #(str) - What the text currently says

		elif (self.type is Types.spinner):
			value = self.thing.GetValue() #(str) - What is in the spin box

		elif (self.type is Types.slider):
			value = self.thing.GetValue() #(str) - What is in the spin box

		elif (self.type is Types.search):
			value = self.thing.GetValue() #(str) - What is in the search box

		else:
			warnings.warn(f"Add {self.type.name} to getValue() for {self.__repr__()}", Warning, stacklevel = 2)
			value = None

		return value

	def getText(self, *args, **kwargs):
		return self.getValue(*args, **kwargs)

	#Setters
	def setValue(self, newValue = None, event = None, default = None, triggerPopup = True, **kwargs):
		"""Sets the contextual value for the object associated with this handle to what the user supplies."""

		if (self.type is Types.box):
			if (newValue is None):
				newValue = "" #Filter None as blank text

			if (self.subType == "autoComplete"):
				self.thing.SetValue(f"{newValue}", default = default, triggerPopup = triggerPopup) #(str) - What will be shown in the input box
			else:
				self.thing.SetValue(f"{newValue}") #(str) - What will be shown in the input box

		elif (self.type is Types.spinner):
			if (isinstance(newValue, str)):
				if ("_base16" in self.subType):
					newValue = hex(int(newValue, 16))
				else:
					newValue = int(newValue)

			self.thing.SetValue(newValue) #(int / float) - What will be shown in the input box

		elif (self.type is Types.slider):
			self.thing.SetValue(newValue) #(int / float) - Where the slider position will be

		elif (self.type is Types.search):
			if (newValue is None):
				newValue = "" #Filter None as blank text
			self.thing.SetValue(f"{newValue}") #(str) - What will be shown in the search box

		else:
			warnings.warn(f"Add {self.type.name} to setValue() for {self.__repr__()}", Warning, stacklevel = 2)

	#Change Settings
	def setFunction_click(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type is Types.box):
			self._betterBind(wx.EVT_TEXT, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
			self._betterBind(wx.EVT_TEXT_ENTER, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)

		elif (self.type is Types.spinner):
			self._betterBind(wx.EVT_TEXT, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
			# self._betterBind(wx.EVT_SPINCTRL, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)

		elif (self.type is Types.search):
			self._betterBind(wx.EVT_TEXT, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
			self._betterBind(wx.EVT_TEXT_ENTER, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)

		else:
			warnings.warn(f"Add {self.type.name} to setFunction_click() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_enter(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type is Types.box):
			self.keyBind("enter", myFunction, myFunctionArgs, myFunctionKwargs)

		elif (self.type is Types.search):
			self.keyBind("enter", myFunction, myFunctionArgs, myFunctionKwargs)
			# self._betterBind(wx.EVT_TEXT_ENTER, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)

		else:
			warnings.warn(f"Add {self.type.name} to setFunction_enter() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_preEdit(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type is Types.box):
			self._betterBind(wx.EVT_SET_FOCUS, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		else:
			warnings.warn(f"Add {self.type.name} to setFunction_preEdit() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_postEdit(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type is Types.box):
			self._betterBind(wx.EVT_KILL_FOCUS, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)

		elif (self.type is Types.spinner):
			self._betterBind(wx.EVT_KILL_FOCUS, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)

			if (not ((self.exclude is None) or (isinstance(self.exclude, (list, tuple, range)) and (len(self.exclude) == 0)))):
				self._betterBind(wx.EVT_KILL_FOCUS, self.thing, self._onCheckValue_exclude, rebind = True)

		elif (self.type is Types.slider):
			self._betterBind(wx.EVT_SCROLL_CHANGED, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)

		else:
			warnings.warn(f"Add {self.type.name} to setFunction_postEdit() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_search(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type is Types.search):
			self._betterBind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		else:
			warnings.warn(f"Add {self.type.name} to setFunction_search() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_cancel(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type is Types.search):
			self._betterBind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		else:
			warnings.warn(f"Add {self.type.name} to setFunction_cancel() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_menuSelect(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type is Types.search):
			self._betterBind(wx.EVT_MENU, self.myMenu.thing, myFunction, myFunctionArgs, myFunctionKwargs, mode = 2)
		else:
			warnings.warn(f"Add {self.type.name} to setFunction_menuSelect() for {self.__repr__()}", Warning, stacklevel = 2)

	def setMin(self, newValue):
		"""Sets the contextual minimum for the object associated with this handle to what the user supplies."""

		if (self.type is Types.spinner):
			self.thing.SetMin(newValue) #(int / float) - What the min value will be for the the input box

		elif (self.type is Types.slider):
			self.thing.SetMin(newValue) #(int / float) - What the min slider position will be

		else:
			warnings.warn(f"Add {self.type.name} to setMin() for {self.__repr__()}", Warning, stacklevel = 2)

	def setMax(self, newValue):
		"""Sets the contextual maximum for the object associated with this handle to what the user supplies."""

		if (self.type is Types.spinner):
			self.thing.SetMax(newValue) #(int / float) - What the max value will be for the the input box

		elif (self.type is Types.slider):
			self.thing.SetMax(newValue) #(int / float) - What the max slider position will be

		else:
			warnings.warn(f"Add {self.type.name} to setMax() for {self.__repr__()}", Warning, stacklevel = 2)

	def setReadOnly(self, state = True):
		"""Sets the contextual readOnly for the object associated with this handle to what the user supplies."""

		if (self.type is Types.box):
			self.thing.SetEditable(not state)

		elif (self.type is Types.spinner):
			self.thing.Enable(not state)

		else:
			warnings.warn(f"Add {self.type.name} to setReadOnly() for {self.__repr__()}", Warning, stacklevel = 2)

	def setChoices(self, choices = None):
		self.choices = choices or ()

	def setTextColor(self, color = None):
		"""Changes the text color.

		color (tuple) - What color to make the text
			- If None: Will use the default color

		Example Input: setTextColor()
		Example Input: setTextColor((255, 0, 0))
		"""

		style = self.thing.GetDefaultStyle()
		style.SetTextColour(self.getColor(color))

		self.thing.SetStyle(0, len(self.thing.GetValue()), style)
		self.thing.SetDefaultStyle(style)

	def getTextColor(self):
		"""Returns the current text color.

		Example Input: getTextColor()
		"""

		return self.thing.GetDefaultStyle().GetTextColour().Get(includeAlpha = False)

	def update_autoComplete(self, choices = None, event = None):
		"""Updates the auto completer."""

		if (choices):
			self.setChoices(choices)

		self.thing.AutoComplete(self.choices or ())

	def _onCheckValue_exclude(self, event):
		"""Checks the current value to make sure the text is valid."""

		if (self.type is Types.spinner):
			if (self.exclude is not None):
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
			warnings.warn(f"Add {self.type.name} to _onCheckValue_exclude() for {self.__repr__()}", Warning, stacklevel = 2)

		event.Skip()

	def _onSearch_replaceText(self, event):
		"""Replaces the text in the input box with that of the popup menu."""

		if (self.type is Types.search):
			value = self.myMenu.getText(event)
			self.setValue(value)
		else:
			warnings.warn(f"Add {self.type.name} to _onSearch_replaceText() for {self.__repr__()}", Warning, stacklevel = 2)

		event.Skip()

class handle_WidgetButton(handle_Widget_Base):
	"""A handle for working with button widgets."""

	def __init__(self):
		"""Initializes defaults."""

		#Initialize inherited classes
		handle_Widget_Base.__init__(self)

	def __len__(self):
		"""Returns what the contextual length is for the object associated with this handle."""

		if (self.type is Types.check):
			value = len(self.thing.GetLabel()) #(int) - The length of the text by the check box

		elif (self.type is Types.radio):
			value = len(self.thing.GetLabel()) #(int) - The length of the text by the radio button

		elif (self.type is Types.toggle):
			value = len(self.thing.GetLabel()) #(int) - The length of the text in the toggle button

		elif (self.type is Types.radiobox):
			value = self.thing.GetCount() #(int) - How many items are in the check list

		elif (self.type is Types.checklist):
			value = self.thing.GetCount() #(int) - How many items are in the check list

		elif (self.type is Types.button):
			value = len(self.getValue()) #(int) - The length of the text in the button

		elif (self.type is Types.image):
			value = len(self.getValue()) #(int) - The length of the text in the image button

		else:
			warnings.warn(f"Add {self.type.name} to __len__() for {self.__repr__()}", Warning, stacklevel = 2)
			value = 0

		return value

	def _build(self, argument_catalogue):
		"""Determiens which build system to use for this handle."""

		def _build_button(toggleText = False):
			"""Builds a wx button object."""
			nonlocal self, argument_catalogue

			text, myFunction = self._getArguments(argument_catalogue, ["text", "myFunction"])

			myId = self._getId(argument_catalogue)

			#Create the thing to put in the grid
			self.thing = wx.Button(self.parent.thing, id = myId, label = f"{text}", style = 0)

			#Bind the function(s)
			if (toggleText):
				self._betterBind(wx.EVT_BUTTON, self.thing, self._onToggleText)

			if (myFunction is not None):
				myFunctionArgs, myFunctionKwargs = self._getArguments(argument_catalogue, ["myFunctionArgs", "myFunctionKwargs"])
				self.setFunction_click(myFunction, myFunctionArgs, myFunctionKwargs)

		def _build_buttonList():
			"""Builds a smart wx button object."""
			nonlocal self, argument_catalogue

			textList = self._getArguments(argument_catalogue, ["text"])
			
			if (not isinstance(textList, (list, tuple, range, set, types.GeneratorType))):
				textList = [textList]
			else:
				textList = [str(item) for item in textList]
			
			if (len(textList) == 0):
				textList = [""]
			argument_catalogue["text"] = textList[0]
			self.textList = textList
			
			_build_button(toggleText = True)

		def _build_buttonToggle():
			"""Builds a wx toggle button object."""
			nonlocal self, argument_catalogue

			text, myFunction, pressed = self._getArguments(argument_catalogue, ["text", "myFunction", "pressed"])

			myId = self._getId(argument_catalogue)

			#Create the thing to put in the grid
			self.thing = wx.ToggleButton(self.parent.thing, id = myId, label = f"{text}", style = 0)
			self.thing.SetValue(pressed) 

			#Bind the function(s)
			if (myFunction is not None):
				myFunctionArgs, myFunctionKwargs = self._getArguments(argument_catalogue, ["myFunctionArgs", "myFunctionKwargs"])
				self.setFunction_click(myFunction, myFunctionArgs, myFunctionKwargs)

		def _build_buttonCheck():
			"""Builds a wx check box object."""
			nonlocal self, argument_catalogue

			text, default, myFunction = self._getArguments(argument_catalogue, ["text", "default", "myFunction"])

			myId = self._getId(argument_catalogue)

			#Create the thing to put in the grid
			self.thing = wx.CheckBox(self.parent.thing, id = myId, label = f"{text}", style = 0)

			#Determine if it is on by default
			self.thing.SetValue(default)

			#Bind the function(s)
			if (myFunction is not None):
				myFunctionArgs, myFunctionKwargs = self._getArguments(argument_catalogue, ["myFunctionArgs", "myFunctionKwargs"])
				self.setFunction_click(myFunction, myFunctionArgs, myFunctionKwargs)

		def _build_checkList():
			"""Builds a wx check list box object."""
			nonlocal self, argument_catalogue

			choices, multiple, sort, myFunction = self._getArguments(argument_catalogue, ["choices", "multiple", "sort", "myFunction"])

			#Ensure that the choices given are a list or tuple
			if (not isinstance(choices, (list, tuple, range, set, types.GeneratorType))):
				choices = [choices]

			#Ensure that the choices are all strings
			choices = [str(item) for item in choices]

			#Apply settings
			style = "wx.LB_NEEDED_SB"

			if (multiple):
				style += "|wx.LB_MULTIPLE"
			
			if (sort):
				style += "|wx.LB_SORT"

			myId = self._getId(argument_catalogue)
		
			#Create the thing to put in the grid
			self.thing = wx.CheckListBox(self.parent.thing, id = myId, choices = choices, style = eval(style, {'__builtins__': None, "wx": wx}, {}))

			#Bind the function(s)
			if (myFunction is not None):
				myFunctionArgs, myFunctionKwargs = self._getArguments(argument_catalogue, ["myFunctionArgs", "myFunctionKwargs"])
				self.setFunction_click(myFunction, myFunctionArgs, myFunctionKwargs)

		def _build_buttonRadio():
			"""Builds a wx radio button object."""
			nonlocal self, argument_catalogue

			groupStart, text, default, myFunction = self._getArguments(argument_catalogue, ["groupStart", "text", "default", "myFunction"])

			#Determine if this is the start of a new radio button group
			if (groupStart):
				group = wx.RB_GROUP
			else:
				group = 0

			myId = self._getId(argument_catalogue)
		
			#Create the thing to put in the grid
			self.thing = wx.RadioButton(self.parent.thing, id = myId, label = f"{text}", style = group)

			#Determine if it is turned on by default
			self.thing.SetValue(default)

			#Bind the function(s)
			if (myFunction is not None):
				myFunctionArgs, myFunctionKwargs = self._getArguments(argument_catalogue, ["myFunctionArgs", "myFunctionKwargs"])
				self.setFunction_click(myFunction, myFunctionArgs, myFunctionKwargs)

		def _build_buttonRadioBox():
			"""Builds a wx radio box object."""
			nonlocal self, argument_catalogue

			choices, vertical, title, default, maximum, myFunction = self._getArguments(argument_catalogue, ["choices", "vertical", "title", "default", "maximum", "myFunction"])

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

			myId = self._getId(argument_catalogue)

			#Create the thing to put in the grid
			self.thing = wx.RadioBox(self.parent.thing, id = myId, label = f"{title}", choices = choices, majorDimension = maximum, style = direction)

			#Set default position
			if (len(choices) != 0):
				if (type(default) == str):
					if (default in choices):
						default = choices.index(default)

				if (default is None):
					default = 0

				self.thing.SetSelection(default)

			#Bind the function(s)
			if (myFunction is not None):
				myFunctionArgs, myFunctionKwargs = self._getArguments(argument_catalogue, ["myFunctionArgs", "myFunctionKwargs"])
				self.setFunction_click(myFunction, myFunctionArgs, myFunctionKwargs)

		def _build_buttonImage():
			"""Builds a wx bitmap button object."""
			nonlocal self, argument_catalogue

			def _imageCheck(imagePath, internal, internalDefault):
				"""Determines what image to use."""
				nonlocal self 

				if ((imagePath != "") and (imagePath is not None)):
					if ((((internal is not None) and (not internal)) or ((internal is None) and (not internalDefault))) and (not os.path.exists(imagePath))):
						return self.getImage("error", internal = True)
					elif (internal is not None):
						return self.getImage(imagePath, internal)
					return self.getImage(imagePath, internalDefault)
				else:
					return None

			#########################################################

			idlePath, disabledPath, selectedPath, text, size = self._getArguments(argument_catalogue, ["idlePath", "disabledPath", "selectedPath", "text", "size"])
			focusPath, hoverPath, toggle, myFunction = self._getArguments(argument_catalogue, ["focusPath", "hoverPath", "toggle", "myFunction"])
			internal, idle_internal, disabled_internal = self._getArguments(argument_catalogue, ["internal", "idle_internal", "disabled_internal"])
			selected_internal, focus_internal, hover_internal = self._getArguments(argument_catalogue, ["selected_internal", "focus_internal", "hover_internal"])

			# wx.BU_LEFT: Left-justifies the bitmap label.
			# wx.BU_TOP: Aligns the bitmap label to the top of the button.
			# wx.BU_RIGHT: Right-justifies the bitmap label.
			# wx.BU_BOTTOM: Aligns the bitmap label to the bottom of the button.

			#Error Check
			image = _imageCheck(idlePath, idle_internal, internal)
			if (image is None):
				image = self.getImage("error", internal = True)

			#Remember values
			self.toggle = toggle

			if (size is None):
				size = wx.DefaultSize

			myId = self._getId(argument_catalogue)

			#Create the thing to put in the grid
			if (text is not None):
				if (toggle):
					self.thing = wx.lib.buttons.GenBitmapTextToggleButton(self.parent.thing, id = myId, bitmap = image, label = text, size = size, style = wx.BU_AUTODRAW)
				else:
					self.thing = wx.lib.buttons.GenBitmapTextButton(self.parent.thing, id = myId, bitmap = image, label = text, size = size, style = wx.BU_AUTODRAW)
			else:
				if (toggle):
					self.thing = wx.lib.buttons.GenBitmapToggleButton(self.parent.thing, id = myId, bitmap = image, size = size, style = wx.BU_AUTODRAW)
				else:
					self.thing = wx.lib.buttons.GenBitmapButton(self.parent.thing, id = myId, bitmap = image, size = size, style = wx.BU_AUTODRAW)
		
			#Apply extra images
			image = _imageCheck(disabledPath, disabled_internal, internal)
			if (image is not None):
				self.thing.SetBitmapDisabled(image)

			image = _imageCheck(selectedPath, selected_internal, internal)
			if (image is not None):
				self.thing.SetBitmapSelected(image)

			image = _imageCheck(focusPath, focus_internal, internal)
			if (image is not None):
				self.thing.SetBitmapFocus(image)

			image = _imageCheck(hoverPath, hover_internal, internal)
			if (image is not None):
				self.thing.SetBitmapHover(image)

			#Bind the function(s)
			if (myFunction is not None):
				myFunctionArgs, myFunctionKwargs = self._getArguments(argument_catalogue, ["myFunctionArgs", "myFunctionKwargs"])
				self.setFunction_click(myFunction, myFunctionArgs, myFunctionKwargs)
		
		#########################################################

		self._preBuild(argument_catalogue)

		
		if (self.type is Types.button):
			_build_button()
		elif (self.type is Types.check):
			_build_buttonCheck()
		elif (self.type is Types.radio):
			_build_buttonRadio()
		elif (self.type is Types.toggle):
			_build_buttonToggle()
		elif (self.type is Types.radiobox):
			_build_buttonRadioBox()
		elif (self.type is Types.checklist):
			_build_checkList()
		elif (self.type is Types.image):
			_build_buttonImage()
		elif (self.type is Types.list):
			_build_buttonList()
		elif (self.type is Types.help):
			_build_buttonHelp()
		else:
			warnings.warn(f"Add {self.type.name} to _build() for {self.__repr__()}", Warning, stacklevel = 2)

		self._postBuild(argument_catalogue)

	#Getters
	def getValue(self, event = None):
		"""Returns what the contextual value is for the object associated with this handle."""

		if (self.type is Types.check):
			value = self.thing.GetValue() #(bool) - True: Checked; False: Un-Checked

		elif (self.type is Types.list):
			value = self.thing.GetLabel() #(str) - What the button says

		elif (self.type is Types.radio):
			value = self.thing.GetValue() #(bool) - True: Selected; False: Un-Selected

		elif (self.type is Types.toggle):
			value = self.thing.GetValue() #(bool) - True: Selected; False: Un-Selected

		elif (self.type is Types.radiobox):
			index = self.thing.GetSelection()
			if (index != -1):
				value = self.thing.GetString(index) #(str) - What the selected item's text says
			else:
				value = None

		elif (self.type is Types.checklist):
			value = self.thing.GetCheckedStrings() #(list) - What is selected in the check list as strings

		elif (self.type is Types.button):
			value = self.thing.GetLabel() #(str) - What the button says

		elif (self.type is Types.image):
			if (self.toggle):
				value = self.thing.GetToggle() #(bool) - True: Selected; False: Un-Selected
			else:
				value = None

		else:
			warnings.warn(f"Add {self.type.name} to getValue() for {self.__repr__()}", Warning, stacklevel = 3)
			value = None

		return value

	def getIndex(self, event = None):
		"""Returns what the contextual index is for the object associated with this handle."""

		if (self.type is Types.radiobox):
			value = self.thing.GetSelection() #(int) - Which button is selected by index

		elif (self.type is Types.checklist):
			value = self.thing.GetCheckedItems() #(list) - Which checkboxes are selected as integers

		else:
			warnings.warn(f"Add {self.type.name} to getIndex() for {self.__repr__()}", Warning, stacklevel = 2)
			value = None

		return value

	def getAll(self, event = None):
		"""Returns all the contextual values for the object associated with this handle."""

		if (self.type is Types.radiobox):
			value = []
			n = self.thing.GetCount()
			for i in range(n):
				value.append(thing.GetString(i)) #(list) - What is in the radio box as strings

		elif (self.type is Types.checklist):
			value = []
			n = self.thing.GetCount()
			for i in range(n):
				value.append(thing.GetString(i)) #(list) - What is in the full list as strings

		else:
			warnings.warn(f"Add {self.type.name} to getAll() for {self.__repr__()}", Warning, stacklevel = 2)
			value = None

		return value

	#Setters
	def setValue(self, newValue, event = None):
		"""Sets the contextual value for the object associated with this handle to what the user supplies."""

		if (self.type is Types.check):
			self.thing.SetValue(bool(newValue)) #(bool) - True: checked; False: un-checked

		elif (self.type is Types.list):
			self.thing.SetLabel(newValue) #(str) - What the button will say on it

		elif (self.type is Types.radio):
			self.thing.SetValue(bool(newValue)) #(bool) - True: selected; False: un-selected

		elif (self.type is Types.toggle):
			self.thing.SetValue(bool(newValue)) #(bool) - True: selected; False: un-selected

		elif (self.type is Types.radiobox):
			if (isinstance(newValue, str)):
				# if (not newValue.isdigit()):
				newValue = self.thing.FindString(newValue)

			if (newValue is None):
				errorMessage = f"Invalid radio button selection in setValue() for {self.__repr__()}"
				raise ValueError(errorMessage)

			self.thing.SetSelection(int(newValue)) #(int / str) - Which radio button to select

		elif (self.type is Types.checklist):
			if (not isinstance(newValue, dict)):
				errorMessage = "Must give a dictionary of {which item (int): state (bool)}"# or {item label (str): state (bool)}"
				raise ValueError(errorMessage)

			for index, state in newValue.items():
				if (isinstance(index, str)):
					state = self.thing.FindString(index)
				
				self.thing.Check(index, state) #(bool) - True: selected; False: un-selected
		
		elif (self.type is Types.button):
			self.thing.SetLabel(newValue) #(str) - What the button will say on it

		elif ((self.type is Types.image) and (self.toggle)):
			self.thing.SetToggle(bool(newValue)) #(bool) - True: selected; False: un-selected

		else:
			warnings.warn(f"Add {self.type.name} to setValue() for {self.__repr__()}", Warning, stacklevel = 2)

	def setSelection(self, newValue = None, event = None):
		"""Sets the contextual value for the object associated with this handle to what the user supplies."""

		if (self.type is Types.radiobox):
			if (newValue is None):
				newValue = 0
			self.setValue(newValue, event)

		elif (self.type is Types.list):
			try:
				if (isinstance(newValue, bool)):
					newValue = int(newValue)
				elif (newValue is None):
					newValue = 0

				if (isinstance(newValue, int)):
					newValue = self.textList[newValue]
				else:
					newValue = self.textList.index(newValue)
			except KeyError as error:
				print(error)
				newValue = self.textList[0]

			self.setValue(newValue, event)
		else:
			warnings.warn(f"Add {self.type.name} to setSelection() for {self.__repr__()}", Warning, stacklevel = 2)

	#Change Settings
	def setFunction_click(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		"""Changes the function that runs when the widget is clicked."""
		
		if (self.type is Types.check):
			self._betterBind(wx.EVT_CHECKBOX, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		
		elif (self.type is Types.radio):
			self._betterBind(wx.EVT_RADIOBUTTON, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)

		elif (self.type is Types.radiobox):
			self._betterBind(wx.EVT_RADIOBOX, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		
		elif (self.type is Types.button):
			self._betterBind(wx.EVT_BUTTON, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		
		elif (self.type is Types.list):
			self._betterBind(wx.EVT_BUTTON, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
			self._betterBind(wx.EVT_BUTTON, self.thing, self._onToggleText, rebind = True)
		
		elif (self.type is Types.image):
			self._betterBind(wx.EVT_BUTTON, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		
		elif (self.type is Types.toggle):
			self._betterBind(wx.EVT_TOGGLEBUTTON, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		
		elif (self.type is Types.checklist):
			self._betterBind(wx.EVT_CHECKLISTBOX, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)

		else:
			warnings.warn(f"Add {self.type.name} to setFunction_click() for {self.__repr__()}", Warning, stacklevel = 2)

	def setReadOnly(self, state = True, event = None):
		"""Sets the contextual readOnly for the object associated with this handle to what the user supplies."""

		if (self.type is Types.check):
			self.thing.SetReadOnly(state)

		else:
			warnings.warn(f"Add {self.type.name} to setReadOnly() for {self.__repr__()}", Warning, stacklevel = 2)

	def _onToggleText(self, event):
		"""Changes the value displayed on the button when the user presses it."""

		if (self.type is Types.list):
			value = self.getValue()
			if (value in self.textList):
				index = self.textList.index(value)
				if (index == len(self.textList) - 1):
					newValue = self.textList[0]
				else:
					newValue = self.textList[index + 1]
			else:
				newValue = self.textList[0]
			
			self.setValue(newValue)				

		else:
			warnings.warn(f"Add {self.type.name} to setReadOnly() for {self.__repr__()}", Warning, stacklevel = 2)

		event.Skip()

class handle_WidgetPicker(handle_Widget_Base):
	"""A handle for working with picker widgets."""

	def __init__(self):
		"""Initializes defaults."""

		#Initialize inherited classes
		handle_Widget_Base.__init__(self)

	def __len__(self):
		"""Returns what the contextual length is for the object associated with this handle."""

		if (self.type is Types.file):
			value = len(self.getValue()) #(int) - How long the file path selected is

		elif (self.type is Types.filewindow):
			value = len(self.getValue()) #(int) - How long the file path selected is

		else:
			warnings.warn(f"Add {self.type.name} to __len__() for {self.__repr__()}", Warning, stacklevel = 2)
			value = 0

		return value

	def _build(self, argument_catalogue):
		"""Determiens which build system to use for this handle."""

		def _build_pickerFile():
			"""Builds a wx file picker control or directory picker control object.
			Use: https://www.blog.pythonlibrary.org/2011/02/10/wxpython-showing-2-filetypes-in-wx-filedialog/
			"""
			nonlocal self, argument_catalogue

			default, text, initialDir, wildcard, myFunction = self._getArguments(argument_catalogue, ["default", "text", "initialDir", "wildcard", "myFunction"])
			directoryOnly, openFile, saveFile, saveConfirmation = self._getArguments(argument_catalogue, ["directoryOnly", "openFile", "saveFile", "saveConfirmation"])
			changeCurrentDirectory, fileMustExist, smallButton, addInputBox = self._getArguments(argument_catalogue, ["changeCurrentDirectory", "fileMustExist", "smallButton", "addInputBox"])

			#Picker configurations
			style = ""

			if (directoryOnly):
				##Determine which configurations to add
				if (changeCurrentDirectory):
					style += "wx.DIRP_CHANGE_DIR|"
				if (fileMustExist):
					style += "wx.DIRP_DIR_MUST_EXIST|"
				if (smallButton):
					style += "wx.DIRP_SMALL|"
				if (addInputBox):
					style += "wx.DIRP_USE_TEXTCTRL|"
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
					style += "wx.FLP_CHANGE_DIR|"
				if (fileMustExist):
					style += "wx.FLP_FILE_MUST_EXIST|"
				if (openFile):
					style += "wx.FLP_OPEN|"
				if (saveConfirmation):
					style += "wx.FLP_OVERWRITE_PROMPT|"
				if (saveFile):
					style += "wx.FLP_SAVE|"
				if (smallButton):
					style += "wx.FLP_SMALL|"
				if (addInputBox):
					style += "wx.FLP_USE_TEXTCTRL|"

			if (style != ""):
				style = style[:-1]
			else:
				style = "0"

			myId = self._getId(argument_catalogue)

			# if (initialDir is None):
			#   initialDir = ""

			# if (initialFile is None):
			#   initialFile = ""

			wildcard = self.getWildcard(wildcard)

			#Create the thing to put in the grid
			if (directoryOnly):
				self.thing = wx.DirPickerCtrl(self.parent.thing, id = myId, path = default, message = text, style = eval(style, {'__builtins__': None, "wx": wx}, {}))
			else:
				self.thing = wx.FilePickerCtrl(self.parent.thing, id = myId, path = default, message = text, wildcard = wildcard, style = eval(style, {'__builtins__': None, "wx": wx}, {}))

			#Set Initial directory
			self.thing.SetInitialDirectory(initialDir)

			#Bind the function(s)
			if (myFunction is not None):
				myFunctionArgs, myFunctionKwargs = self._getArguments(argument_catalogue, ["myFunctionArgs", "myFunctionKwargs"])
				self.setFunction_click(myFunction, myFunctionArgs, myFunctionKwargs)

		def _build_pickerFileWindow():
			"""Builds a wx generic directory control object."""
			nonlocal self, argument_catalogue

			myFunction, editLabelFunction, rightClickFunction = self._getArguments(argument_catalogue, ["myFunction", "editLabelFunction", "rightClickFunction"])
			directoryOnly, selectMultiple, initialDir, showHidden = self._getArguments(argument_catalogue, ["directoryOnly", "selectMultiple", "initialDir", "showHidden"])

			#Apply settings
			style = "wx.DIRCTRL_3D_INTERNAL|wx.SUNKEN_BORDER"

			if (directoryOnly):
				style += "|wx.DIRCTRL_DIR_ONLY"

			if (editLabelFunction is not None):
				style += "|wx.DIRCTRL_EDIT_LABELS"

			if (selectMultiple):
				style += "|wx.DIRCTRL_MULTIPLE"

			# wx.DIRCTRL_SELECT_FIRST: When setting the default path, select the first file in the directory.
			# wx.DIRCTRL_SHOW_FILTERS: Show the drop-down filter list.

			# A filter string, using the same syntax as that for wx.FileDialog. This may be empty if filters are not being used. Example: "All files (*.*)|*.*|JPEG files (*.jpg)|*.jpg"
			filterList = wx.EmptyString

			myId = self._getId(argument_catalogue)
		
			#Create the thing to put in the grid
			self.thing = wx.GenericDirCtrl(self.parent.thing, id = myId, dir = initialDir, style = eval(style, {'__builtins__': None, "wx": wx}, {}), filter = filterList)

			#Determine if it is hidden
			if (showHidden):
				self.thing.ShowHidden(True)
			else:
				self.thing.ShowHidden(False)

			#Bind the function(s)
			if (myFunction is not None):
				myFunctionArgs, myFunctionKwargs = self._getArguments(argument_catalogue, ["myFunctionArgs", "myFunctionKwargs"])
				self.setFunction_click(myFunction, myFunctionArgs, myFunctionKwargs)

			if (editLabelFunction is not None):
				editLabelFunctionArgs, editLabelFunctionKwargs = self._getArguments(argument_catalogue, ["editLabelFunctionArgs", "editLabelFunctionKwargs"])
				self.setFunction_editLabel(myFunction, myFunctionArgs, myFunctionKwargs)

			if (rightClickFunction is not None):
				rightClickFunctionArgs, rightClickFunctionKwargs = self._getArguments(argument_catalogue, ["rightClickFunctionArgs", "rightClickFunctionKwargs"])
				self.setFunction_rightClick(myFunction, myFunctionArgs, myFunctionKwargs)

		def _build_pickerDate():
			"""Builds a wx  object."""
			nonlocal self, argument_catalogue

			date, dropDown, myFunction = self._getArguments(argument_catalogue, ["date", "dropDown", "myFunction"])

			#Set the currently selected date
			if (date is not None):
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
				style = wx.adv.DP_DROPDOWN
			else:
				style = wx.adv.DP_SPIN

			myId = self._getId(argument_catalogue)

			#Create the thing to put in the grid
			self.thing = wx.adv.DatePickerCtrl(self.parent.thing, id = myId, dt = date, style = style)

			#Bind the function(s)
			if (myFunction is not None):
				myFunctionArgs, myFunctionKwargs = self._getArguments(argument_catalogue, ["myFunctionArgs", "myFunctionKwargs"])
				self.setFunction_click(myFunction, myFunctionArgs, myFunctionKwargs)

		def _build_pickerDateWindow():
			"""Builds a wx  object."""
			nonlocal self, argument_catalogue

			date, showHolidays, showOther = self._getArguments(argument_catalogue, ["date", "showHolidays", "showOther"])
			myFunction, dayFunction, monthFunction, yearFunction = self._getArguments(argument_catalogue, ["myFunction", "dayFunction", "monthFunction", "yearFunction"])

			#Set the currently selected date
			if (date is not None):
				try:
					month, day, year = re.split("[\\\\/]", date) #Format: mm/dd/yyyy
					date = wx.DateTime(day, month, year)
				except:
					errorMessage = "Calandar dates must be formatted 'mm/dd/yy'"
					raise SyntaxError(errorMessage)
			else:
				date = wx.DateTime().SetToCurrent()

			#Apply settings
			style = ""

			# wx.adv.CAL_SUNDAY_FIRST: Show Sunday as the first day in the week (not in wxGTK)
			# wx.adv.CAL_MONDAY_FIRST: Show Monday as the first day in the week (not in wxGTK)
			# wx.adv.CAL_NO_YEAR_CHANGE: Disable the year changing (deprecated, only generic)
			# wx.adv.CAL_NO_MONTH_CHANGE: Disable the month (and, implicitly, the year) changing
			# wx.adv.CAL_SEQUENTIAL_MONTH_SELECTION: Use alternative, more compact, style for the month and year selection controls. (only generic)
			# wx.adv.CAL_SHOW_WEEK_NUMBERS: Show week numbers on the left side of the calendar. (not in generic)

			if (showHolidays):
				style += "|wx.adv.CAL_SHOW_HOLIDAYS"
			
			if (showOther):
				style += "|wx.adv.CAL_SHOW_SURROUNDING_WEEKS"

			if (len(style) != 0):
				style = style[1:] #Remove leading line
			else:
				style = "0"

			myId = self._getId(argument_catalogue)
		
			#Create the thing to put in the grid
			self.thing = wx.adv.CalendarCtrl(self.parent.thing, id = myId, date = date, style = eval(style, {'__builtins__': None, "wx.adv": wx.adv}, {}))

			#Bind the function(s)
			if (myFunction is not None):
				myFunctionArgs, myFunctionKwargs = self._getArguments(argument_catalogue, ["myFunctionArgs", "myFunctionKwargs"])
				self.setFunction_click(myFunction, myFunctionArgs, myFunctionKwargs)

			if (dayFunction is not None):
				dayFunctionArgs, dayFunctionKwargs = self._getArguments(argument_catalogue, ["dayFunctionArgs", "dayFunctionKwargs"])
				self.setFunction_editDay(myFunction, myFunctionArgs, myFunctionKwargs)

			if (monthFunction is not None):
				monthFunctionArgs, monthFunctionKwargs = self._getArguments(argument_catalogue, ["monthFunctionArgs", "monthFunctionKwargs"])
				self.setFunction_editMonth(myFunction, myFunctionArgs, myFunctionKwargs)

			if (yearFunction is not None):
				yearFunctionArgs, yearFunctionKwargs = self._getArguments(argument_catalogue, ["yearFunctionArgs", "yearFunctionKwargs"])
				self.setFunction_editYear(myFunction, myFunctionArgs, myFunctionKwargs)

		def _build_pickerTime():
			"""Builds a wx time picker control object."""
			nonlocal self, argument_catalogue

			minimum, maximum, applyBounds, outOfBounds_color = self._getArguments(argument_catalogue, ["minimum", "maximum", "applyBounds", "outOfBounds_color"])
			military, seconds, addInputSpinner = self._getArguments(argument_catalogue, ["military", "seconds", "addInputSpinner"])

			myId = self._getId(argument_catalogue)

			self.thing = wx.lib.masked.TimeCtrl(self.parent.thing, id = myId, fmt24hr = military, displaySeconds = seconds, min = minimum, max = maximum, limited = applyBounds, oob_color = outOfBounds_color)

			if (addInputSpinner):
				#Create Spinner
				wrap, arrowKeys = self._getArguments(argument_catalogue, ["wrap", "arrowKeys"])

				style = [wx.SP_VERTICAL]
				if (wrap):
					style.append(wx.SP_WRAP)
				if (arrowKeys):
					style.append(wx.SP_ARROW_KEYS)

				self.spinner = wx.SpinButton(self.parent.thing, id = wx.ID_ANY, style = functools.reduce(operator.ior, style or (0,)))
				self.thing.BindSpinButton(self.spinner)

				#Create Sizer
				self.mySizer = self._makeSizerGridFlex(rows = 1, columns = 2)
				self.mySizer.growFlexRowAll()
				self.mySizer.growFlexColumn(0)

				#Nest objects
				self.mySizer.thing.Add(self.thing, proportion = 0, flag = wx.ALIGN_RIGHT | wx.EXPAND | wx.ALL, border = 0)
				self.mySizer.thing.Add(self.spinner, proportion = 0, flag = wx.ALIGN_LEFT | wx.EXPAND | wx.LEFT, border = 5)
				self.parent._finalNest(self.mySizer)

			else:
				self.spinner = None
				self.mySizer = None

			time, myFunction = self._getArguments(argument_catalogue, ["time", "myFunction"])
			self.setValue(time)

			#Bind the function(s)
			if (myFunction is not None):
				myFunctionArgs, myFunctionKwargs = self._getArguments(argument_catalogue, ["myFunctionArgs", "myFunctionKwargs"])
				self.setFunction_click(myFunction, myFunctionArgs, myFunctionKwargs)

		def _build_pickerColor():
			"""Builds a wx color picker control object."""
			nonlocal self, argument_catalogue

			addInputBox, colorText, initial, myFunction = self._getArguments(argument_catalogue, ["addInputBox", "colorText", "initial", "myFunction"])

			style = ""

			#Add settings
			if (addInputBox):
				style += "|wx.CLRP_USE_TEXTCTRL"
			
			if (colorText):
				style += "|wx.CLRP_SHOW_LABEL"

			if (len(style) == 0):
				style = "0"
			else:
				style = style[1:] #Remove leading line

			if (initial is None):
				initial = wx.BLACK
			else:
				initial = wx.BLACK

			myId = self._getId(argument_catalogue)
		
			#Create the thing to put in the grid
			self.thing = wx.ColourPickerCtrl(self.parent.thing, id = myId, colour = initial, style = eval(style, {'__builtins__': None, "wx": wx}, {}))

			#Bind the function(s)
			if (myFunction is not None):
				myFunctionArgs, myFunctionKwargs = self._getArguments(argument_catalogue, ["myFunctionArgs", "myFunctionKwargs"])
				self.setFunction_click(myFunction, myFunctionArgs, myFunctionKwargs)

		def _build_pickerFont():
			"""Builds a wx font picker control object."""
			nonlocal self, argument_catalogue

			addInputBox, fontText, maxFontSize, myFunction = self._getArguments(argument_catalogue, ["addInputBox", "fontText", "maxFontSize", "myFunction"])

			#Add settings
			style = ""
			if (addInputBox):
				style += "|wx.FNTP_USE_TEXTCTRL"
			
			if (fontText):
				style += "|wx.FNTP_FONTDESC_AS_LABEL"
				#FNTP_USEFONT_FOR_LABEL

			if (len(style) != 0):
				style = style[1:] #Remove leading line
			else:
				style = "0"

			# font = self.getFont()
			font = wx.NullFont

			myId = self._getId(argument_catalogue)
		
			#Create the thing to put in the grid
			self.thing = wx.FontPickerCtrl(self.parent.thing, id = myId, font = font, style = eval(style, {'__builtins__': None, "wx": wx}, {}))
			
			self.thing.SetMaxPointSize(maxFontSize) 

			#Bind the function(s)
			if (myFunction is not None):
				myFunctionArgs, myFunctionKwargs = self._getArguments(argument_catalogue, ["myFunctionArgs", "myFunctionKwargs"])
				self.setFunction_click(myFunction, myFunctionArgs, myFunctionKwargs)
		
		#########################################################

		self._preBuild(argument_catalogue)

		if (self.type is Types.file):
			_build_pickerFile()
		elif (self.type is Types.filewindow):
			_build_pickerFileWindow()
		elif (self.type is Types.date):
			_build_pickerDate()
		elif (self.type is Types.datewindow):
			_build_pickerDateWindow()
		elif (self.type is Types.time):
			_build_pickerTime()
		elif (self.type is Types.color):
			_build_pickerColor()
		elif (self.type is Types.font):
			_build_pickerFont()
		else:
			warnings.warn(f"Add {self.type.name} to _build() for {self.__repr__()}", Warning, stacklevel = 2)

		self._postBuild(argument_catalogue)

	#Getters
	def getValue(self, event = None, *, asString = False):
		"""Returns what the contextual value is for the object associated with this handle."""

		if (self.type is Types.file):
			value = self.thing.GetPath() #(str) - What is in the attached file picker

		elif (self.type is Types.filewindow):
			value = self.thing.GetPath() #(str) - What is in the attached file picker
		
		elif (self.type is Types.date):
			value = self.thing.GetValue() #(str) - What date is selected in the date picker
			if (value is not None):
				if (asString):
					value = f"{value.GetMonth()}/{value.GetDay()}/{value.GetYear()}"
				else:
					value = (value.GetYear(), value.GetMonth(), value.GetDay())

		elif (self.type is Types.datewindow):
			value = self.thing.GetDate() #(str) - What date is selected in the date picker
			if (value is not None):
				if (asString):
					value = f"{value.GetMonth()}/{value.GetDay()}/{value.GetYear()}"
				else:
					value = (value.GetYear(), value.GetMonth(), value.GetDay())

		elif (self.type is Types.time):
			value = self.thing.GetValue(as_wxDateTime = not asString) #(str) - What date is selected in the date picker
			if ((not asString) and (value is not None)):
				value = (value.GetHour(), value.GetMinute(), value.GetSecond())

		elif (self.type is Types.color):
			value = self.thing.GetColour()

		elif (self.type is Types.font):
			value = self.thing.GetSelectedFont()

		else:
			warnings.warn(f"Add {self.type.name} to getValue() for {self.__repr__()}", Warning, stacklevel = 2)
			value = None

		return value

	#Setters
	def setValue(self, newValue, event = None):
		"""Sets the contextual value for the object associated with this handle to what the user supplies."""

		if ((self.type is Types.date) or (self.type is Types.datewindow)):
			def formatValue():
				nonlocal newValue

				if (newValue is None):
					return wx.DateTime().SetToCurrent()

				if (isinstance(newValue, str)):
					try:
						month, day, year = re.split("[\\\\/]", newValue) #Format: mm/dd/yyyy
						month, day, year = int(month), int(day), int(year)
						return wx.DateTime(day, month, year)
					except:
						errorMessage = f"Calandar dates must be formatted 'mm/dd/yy' for setValue() for {self.__repr__()}"
						raise SyntaxError(errorMessage)

				if (len(newValue) is not 3):
					errorMessage = f"Calandar dates must be formatted (month (int), day (int), year (int)) for setValue() for {self.__repr__()}"
					raise SyntaxError(errorMessage)

				return wx.DateTime(*newValue)

		elif (self.type is Types.time):
			def formatValue():
				nonlocal newValue

				if (newValue is None):
					return wx.DateTime().SetToCurrent()

				if (isinstance(newValue, str)):
					return newValue

				if (len(newValue) not in (2, 3)):
					errorMessage = f"Calandar dates must be formatted (hour (int), minute (int), second (int)) or (hour (int), minute (int)) for setValue() for {self.__repr__()}"
					raise SyntaxError(errorMessage)

				return ":".join(f"{item}" for item in newValue)

			####################################################

		if ((self.type is Types.file) or (self.type is Types.filewindow)):
			self.thing.SetPath(newValue) #(str) - What will be shown in the input box
		
		elif ((self.type is Types.date) or (self.type is Types.datewindow)):
			self.thing.SetValue(formatValue()) #(str) - What date will be selected as 'mm/dd/yyyy'

		elif (self.type is Types.time):
			self.thing.SetValue(formatValue()) #(str) - What time will be selected as 'hour:minute:second'

		else:
			warnings.warn(f"Add {self.type.name} to setValue() for {self.__repr__()}", Warning, stacklevel = 2)


	#Change Settings
	def setFunction_click(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		"""Changes the function that runs when the widget is changed/clicked on."""
		
		if (self.type is Types.file):
			if (self.thing.GetClassName() == "wxDirPickerCtrl"):
				self._betterBind(wx.EVT_DIRPICKER_CHANGED, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
			else:
				self._betterBind(wx.EVT_FILEPICKER_CHANGED, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		elif (self.type is Types.filewindow):
			self._betterBind(wx.EVT_TREE_SEL_CHANGED, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		elif (self.type is Types.time):
			self._betterBind(wx.lib.masked.EVT_TIMEUPDATE, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		elif (self.type is Types.date):
			self._betterBind(wx.adv.EVT_DATE_CHANGED, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		elif (self.type is Types.datewindow):
			self._betterBind(wx.adv.EVT_CALENDAR_SEL_CHANGED, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		elif (self.type is Types.color):
			self._betterBind(wx.EVT_COLOURPICKER_CHANGED, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		elif (self.type is Types.font):
			self._betterBind(wx.EVT_FONTPICKER_CHANGED, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		else:
			warnings.warn(f"Add {self.type.name} to setFunction_click() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_editLabel(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		"""Changes the function that runs when a label is modified."""
		
		if (self.type is Types.filewindow):
			self._betterBind(wx.EVT_TREE_END_LABEL_EDIT, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		else:
			warnings.warn(f"Add {self.type.name} to setFunction_editLabel() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_rightClick(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		"""Changes the function that runs when the right mouse button is clicked in the widget."""
		
		if (self.type is Types.filewindow):
			self._betterBind(wx.EVT_TREE_ITEM_RIGHT_CLICK, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		else:
			warnings.warn(f"Add {self.type.name} to setFunction_rightClick() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_editDay(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		"""Changes the function that runs when the day is modified."""
		
		if (self.type is Types.datewindow):
			self._betterBind(wx.adv.EVT_CALENDAR_DAY, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		else:
			warnings.warn(f"Add {self.type.name} to setFunction_editDay() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_editMonth(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		"""Changes the function that runs when the month is modified."""
		
		if (self.type is Types.datewindow):
			self._betterBind(wx.adv.EVT_CALENDAR_MONTH, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		else:
			warnings.warn(f"Add {self.type.name} to setFunction_editMonth() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_editYear(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		"""Changes the function that runs when the year is modified."""
		
		if (self.type is Types.datewindow):
			self._betterBind(wx.adv.EVT_CALENDAR_YEAR, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		else:
			warnings.warn(f"Add {self.type.name} to setFunction_editYear() for {self.__repr__()}", Warning, stacklevel = 2)

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

		if (self.type is Types.image):
			image = self.getValue()
			if (returnRows):
				value = image.GetWidth()
			else:
				value = image.GetHeight()

		else:
			warnings.warn(f"Add {self.type.name} to __len__() for {self.__repr__()}", Warning, stacklevel = 2)
			value = 0

		return value

	def _build(self, argument_catalogue):
		"""Determiens which build system to use for this handle."""

		def _build_image():
			"""Builds a wx static bitmap object."""
			nonlocal self, argument_catalogue

			imagePath, internal, size = self._getArguments(argument_catalogue, ["imagePath", "internal", "size"])

			#Get correct image
			image = self.getImage(imagePath, internal)

			myId = self._getId(argument_catalogue)
		
			#Create the thing to put in the grid
			self.thing = wx.StaticBitmap(self.parent.thing, id = myId, bitmap = image, size = size, style = 0) #style = wx.SUNKEN_BORDER)
		
		#########################################################

		self._preBuild(argument_catalogue)

		if (self.type is Types.image):
			_build_image()
		else:
			warnings.warn(f"Add {self.type.name} to _build() for {self.__repr__()}", Warning, stacklevel = 2)

		self._postBuild(argument_catalogue)

	#Getters
	def getValue(self, event = None):
		"""Returns what the contextual value is for the object associated with this handle."""

		if (self.type is Types.image):
			value = self.thing.GetBitmap() #(bitmap) - The image that is currently being shown

		else:
			warnings.warn(f"Add {self.type.name} to getValue() for {self.__repr__()}", Warning, stacklevel = 2)
			value = None

		return value

	#Setters
	def setValue(self, newValue, event = None):
		"""Sets the contextual value for the object associated with this handle to what the user supplies."""

		if (self.type is Types.image):
			image = self.getImage(newValue)
			self.thing.SetBitmap(image) #(wxBitmap) - What the image will be now

		else:
			warnings.warn(f"Add {self.type.name} to setValue() for {self.__repr__()}", Warning, stacklevel = 2)

class handle_Menu(handle_Container_Base):
	"""A handle for working with menus."""

	def __init__(self):
		"""Initializes defaults."""

		#Initialize inherited classes
		handle_Container_Base.__init__(self)

	def _build(self, argument_catalogue):
		"""Determiens which build system to use for this handle."""

		def _build_menu():
			"""Builds a wx menu control object."""
			nonlocal self, argument_catalogue
		
			#Unpack arguments
			detachable, text = self._getArguments(argument_catalogue, ["detachable", "text"])

			#Create menu
			if (detachable):
				self.thing = wx.Menu(wx.MENU_TEAROFF)
			else:
				self.thing = wx.Menu()

			self.text = text
			
			if (len(self.text) == 0):
				self.text = " "

		def _build_flatmenu():
			"""Builds a wx flat menu control object."""
			nonlocal self, argument_catalogue
		
			#Unpack arguments
			text, smallIcons, spaceSize, canCustomize = self._getArguments(argument_catalogue, ["text", "smallIcons", "spaceSize", "canCustomize"])

			style = [wx.lib.agw.flatmenu.FM_OPT_IS_LCD, wx.lib.agw.flatmenu.FM_OPT_SHOW_TOOLBAR]

			if (canCustomize):
				style.append(wx.lib.agw.flatmenu.FM_OPT_SHOW_CUSTOMIZE)

			myId = self._getId(argument_catalogue)
			self.thing = wx.lib.agw.flatmenu.FlatMenuBar(self.parent.thing, id = myId, 
				iconSize = (32, 16)[smallIcons], 
				spacer = spaceSize or wx.lib.agw.flatmenu.SPACER,
				options = functools.reduce(operator.ior, style or (0,)))

			self.text = text or " "

		def _build_toolbar():
			"""Builds a wx toolbar control object."""
			nonlocal self, argument_catalogue

			vertical, detachable, flat, align, top = self._getArguments(argument_catalogue, ["vertical", "detachable", "flat", "align", "top"])
			showIcon, showDivider, showToolTip, showText = self._getArguments(argument_catalogue, ["showIcon", "showDivider", "showToolTip", "showText"])
			vertical_text, myFunction = self._getArguments(argument_catalogue, ["vertical_text", "myFunction"])

			if (vertical):
				style = [wx.TB_VERTICAL]
			else:
				style = [wx.TB_HORIZONTAL]

			if (detachable):
				style.append(wx.TB_DOCKABLE)

			if (flat):
				style.append(wx.TB_FLAT)
			if (not align):
				style.append(wx.TB_NOALIGN)
			if (top is None):
				style.append(wx.TB_RIGHT)
			elif (not top):
				style.append(wx.TB_BOTTOM)

			if (not showIcon):
				style.append(wx.TB_NOICONS)
			if (not showDivider):
				style.append(wx.TB_NODIVIDER)
			if (not showToolTip):
				style.append(wx.TB_NO_TOOLTIPS)
			if (showText):
				style.append(wx.TB_TEXT)
				if (vertical_text):
					style.append(wx.TB_HORZ_LAYOUT)
			
			self.thing = wx.ToolBar(self.parent.thing, style = functools.reduce(operator.ior, style or (0,)))
			self.thing.Realize()

			#Bind the function(s)
			if (myFunction is not None):
				myFunctionArgs, myFunctionKwargs = self._getArguments(argument_catalogue, ["myFunctionArgs", "myFunctionKwargs"])
				self.setFunction_click(myFunction, myFunctionArgs, myFunctionKwargs)
		
		#########################################################

		self._preBuild(argument_catalogue)

		if (self.type is Types.menu):
			_build_menu()
		elif (self.type is Types.flatmenu):
			_build_flatmenu()
		elif (self.type is Types.toolbar):
			_build_toolbar()
		else:
			warnings.warn(f"Add {self.type.name} to _build() for {self.__repr__()}", Warning, stacklevel = 2)

		self._postBuild(argument_catalogue)

	#Getters
	def getValue(self, event = None):
		"""Returns what the contextual value is for the object associated with this handle."""

		if (self.type is Types.menu):
			#Get menu item
			if (event is None):
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
			warnings.warn(f"Add {self.type.name} to getValue() for {self.__repr__()}", Warning, stacklevel = 2)
			value = None

		return value

	def getText(self, event = None):
		"""Returns what the contextual text is for the object associated with this handle."""

		if (self.type is Types.menu):
			#Get menu item
			if (event is None):
				errorMessage = "Pass the event parameter to getValue() when working with menu items"
				raise SyntaxError(errorMessage)
			
			index = event.GetId()
			item = self.thing.FindItemById(index)

			#Act on menu item
			value = item.GetLabel() #(str) - What the selected item says

		else:
			warnings.warn(f"Add {self.type.name} to getValue() for {self.__repr__()}", Warning, stacklevel = 2)
			value = None

		return value

	#Setters
	def setValue(self, newValue, event = None):
		"""Sets the contextual value for the object associated with this handle to what the user supplies."""

		if (self.type is Types.menu):
			#Get menu item
			if (event is None):
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
			warnings.warn(f"Add {self.type.name} to setValue() for {self.__repr__()}", Warning, stacklevel = 2)

	#Change Settings
	def setFunction_click(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		"""Changes the function that runs when the widget is changed/clicked on."""
		
		if (self.type is Types.menu):
			self._betterBind(wx.EVT_MENU, self.thing, myFunction, myFunctionArgs, myFunctionKwargs, mode = 2)
		elif (self.type is Types.toolbar):
			self._betterBind(wx.EVT_TOOL_RCLICKED, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		else:
			warnings.warn(f"Add {self.type.name} to setFunction_click() for {self.__repr__()}", Warning, stacklevel = 2)

	def setEnable(self, state = True, *, label = None):
		"""Enables or disables an item based on the given input.

		state (bool) - If it is enabled or not

		Example Input: setEnable()
		Example Input: setEnable(False)
		"""

		if (self.type is Types.toolbar):
			def applyEnable(myWidget):
				nonlocal self, state

				self.thing.EnableTool(myWidget.thing.GetId(), state)

		elif (self.type is Types.menu):
			def applyEnable(myWidget):
				nonlocal self, state

				myWidget.setEnable(state = state)

		else:
			warnings.warn(f"Add {self.type.name} to setEnable() for {self.__repr__()}", Warning, stacklevel = 2)

		for myWidget in self.ensure_container(label, returnForNone = lambda: self[:], convertNone = False):
			
			if (not isinstance(myWidget, handle_Base)):
				myWidget = self[myWidget]

			#Account for no wx.App.MainLoop yet
			if ((wx.EventLoop.GetActive() is None) and (not self.controller.finishing)):
				#Queue the current state to apply later; setting the enable twice before wx.App.MainLoop starts will cause the code to freeze
				self.myWindow._addFinalFunction(self.setEnable, myFunctionKwargs = {"label": myWidget, "state": state}, label = (myWidget, self.setEnable))
				continue

			applyEnable(myWidget)

	def checkEnabled(self, label = None):
		"""Checks if an item is enabled.

		Example Input: checkEnabled()
		"""

		if (self.type is Types.toolbar):
			if (label is None):
				label = self[:]
			elif (not isinstance(label, (list, tuple, range))):
				label = [label]

			answer = []
			for item in label:
				with self[item] as myWidget:
					#Account for no wx.App.MainLoop yet
					if ((wx.EventLoop.GetActive() is None) and (not self.controller.finishing) and ((myWidget, self.setEnable) in self.finalFunctionCatalogue)):
						answer.append(self.finalFunctionCatalogue[(myWidget, self.setEnable)][2]["state"])
						continue

					myId = myWidget.thing.GetId()
					answer.append(self.thing.GetToolEnabled(myId, state))
		else:
			warnings.warn(f"Add {self.type.name} to checkEnabled() for {self.__repr__()}", Warning, stacklevel = 2)
			answer = None

		return answer
		
	def setShow(self, label = None, state = True):
		"""Shows or hides an item based on the given input.

		state (bool) - If it is shown or not

		Example Input: setShow()
		Example Input: setShow(False)
		"""

		if (self.type is Types.toolbar):
			def applyShow(myWidget):
				nonlocal self

				# self.controller._hiddenToolbar.thing.RemoveTool(myWidget.thing.GetId())

				self.thing.AddTool(myWidget.thing)
				self.thing.Realize()

			def applyHide(myWidget):
				nonlocal self

				self.thing.RemoveTool(myWidget.thing.GetId())

				#The tool does not disappear once removed from the tool bar, so it will be temporarily stored on a hidden tool bar
				# print ("@1", self.controller._hiddenToolbar.thing.AddTool(myWidget.thing))
				# self.controller._hiddenToolbar.thing.Realize()

		elif (self.type is Types.menu):
			def applyShow(myWidget):
				nonlocal self

				self.thing.Append(myWidget.thing)

			def applyHide(myWidget):
				nonlocal self

				self.thing.Remove(myWidget.thing)
		else:
			warnings.warn(f"Add {self.type.name} to setShow() for {self.__repr__()}", Warning, stacklevel = 2)
			return

		################################

		for item in self.ensure_container(label, returnForNone = lambda: self[:], convertNone = False):
			with self[item] as myWidget:
				if (state):
					if (not myWidget.checkShown()):
						applyShow(myWidget)
						myWidget.shown = True
				else:
					if (myWidget.checkShown()):
						applyHide(myWidget)
						myWidget.shown = False

	def checkShown(self, label = None):
		"""Checks if an item is shown.

		Example Input: checkShown()
		"""

		if (self.type is Types.toolbar):
			if (label is None):
				label = self[:]
			elif (not isinstance(label, (list, tuple, range))):
				label = [label]

			state = []
			for item in label:
				with self[item] as myWidget:
					state.append(myWidget.checkShown())

			if (len(state) == 1):
				state = state[0]
		else:
			warnings.warn(f"Add {self.type.name} to checkShown() for {self.__repr__()}", Warning, stacklevel = 2)
			state = None

		return state

	#Add things
	def addItem(self, text = "", icon = None, internal = False, scale = None, 
		disabled_icon = None, disabled_internal = None, disabled_scale = None,
		special = None, check = None, default = False, stretchable = None,

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, 

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None, tabSkip = False, flex = 0, flags = "c1"):
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
		if (self.type is Types.menu):
			handle.type = Types.menuitem
		elif (self.type is Types.flatmenu):
			handle.type = Types.flatmenuitem
		elif (self.type is Types.toolbar):
			handle.type = Types.toolbaritem
		else:
			warnings.warn(f"Add {self.type.name} to addItem() for {self.__repr__()}", Warning, stacklevel = 2)
			return

		handle._build(locals())
		self.nest(handle)

		return handle

	def addSeparator(self, *args, **kwargs):
		"""Adds a line to a specific pre-existing menu to separate menu items.

		Example Input: addSeparator()
		"""

		handle = self.addItem(*args, text = None, stretchable = False, **kwargs)

		return handle

	def addStretchableSpace(self, *args, **kwargs):
		"""Adds a line to a specific pre-existing menu to separate menu items.

		Example Input: addStretchableSpace()
		"""

		if (self.type is Types.toolbar):
			handle = self.addItem(*args, text = None, stretchable = True, **kwargs)
		else:
			warnings.warn(f"Add {self.type.name} to addStretchableSpace() for {self.__repr__()}", Warning, stacklevel = 2)
			handle = None

		return handle

	def addSub(self, text = "", flex = 0, flags = "c1", 

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None, tabSkip = False):
		"""Adds a sub menu to a specific pre-existing menu.
		To adding items to a sub menu is the same as for menus.

		text (str)  - The text for the menu item. This is what is shown to the user
		label (int) - The label for this menu

		Example Input: addSub()
		Example Input: addSub(text = "I&mport")
		"""

		handle = handle_Menu()
		if (self.type is Types.menu):
			handle.type = Types.menu
		elif (self.type is Types.toolbar):
			handle.type = Types.toolbar
		else:
			warnings.warn(f"Add {self.type.name} to addSub() for {self.__repr__()}", Warning, stacklevel = 2)
			return

		detachable = False
		handle._build(locals())

		return handle

	def addText(self, *args, hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, widgetLabel = None, parent = None, handle = None, myId = None, tabSkip = False, flex = 0, flags = "c1", **kwargs):
		"""Adds a text widget to the tool bar."""

		if (self.type is Types.toolbar):
			handle = handle_MenuItem()
			handle.type = Types.toolbaritem
			handle.subHandle = [handle._makeText, args, kwargs]
			handle._build(locals())
		else:
			warnings.warn(f"Add {self.type.name} to addText() for {self.__repr__()}", Warning, stacklevel = 2)
			return

		return handle

	def addHtml(self, *args, hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, widgetLabel = None, parent = None, handle = None, myId = None, tabSkip = False, flex = 0, flags = "c1", **kwargs):
		"""Adds a text widget to the tool bar."""

		if (self.type is Types.toolbar):
			handle = handle_MenuItem()
			handle.type = Types.toolbaritem
			handle.subHandle = [handle._makeHtml, args, kwargs]
			handle._build(locals())
		else:
			warnings.warn(f"Add {self.type.name} to addHtml() for {self.__repr__()}", Warning, stacklevel = 2)
			return

		return handle

	def addEmpty(self, *args, **kwargs):
		"""Alias function for addStretchableSpace()."""

		return self.addStretchableSpace(*args, **kwargs)

	def addHyperlink(self, *args, hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, widgetLabel = None, parent = None, handle = None, myId = None, tabSkip = False, flex = 0, flags = "c1", **kwargs):
		"""Adds a hyperlink widget to the tool bar."""

		if (self.type is Types.toolbar):
			handle = handle_MenuItem()
			handle.type = Types.toolbaritem
			handle.subHandle = [handle._makeHyperlink, args, kwargs]
			handle._build(locals())
		else:
			warnings.warn(f"Add {self.type.name} to addHyperlink() for {self.__repr__()}", Warning, stacklevel = 2)
			handle = None

		return handle

	def addLine(self, *args, hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, widgetLabel = None, parent = None, handle = None, myId = None, tabSkip = False, flex = 0, flags = "c1", **kwargs):
		"""Adds a line widget to the tool bar."""

		if (self.type is Types.toolbar):
			handle = handle_MenuItem()
			handle.type = Types.toolbaritem
			handle.subHandle = [handle._makeLine, args, kwargs]
			handle._build(locals())
		else:
			warnings.warn(f"Add {self.type.name} to addLine() for {self.__repr__()}", Warning, stacklevel = 2)
			handle = None

		return handle

	def addListDrop(self, *args, hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, widgetLabel = None, parent = None, handle = None, myId = None, tabSkip = False, flex = 0, flags = "c1", **kwargs):
		"""Adds a drop list widget to the tool bar."""

		if (self.type is Types.toolbar):
			handle = handle_MenuItem()
			handle.type = Types.toolbaritem
			handle.subHandle = [handle._makeListDrop, args, kwargs]
			handle._build(locals())
		else:
			warnings.warn(f"Add {self.type.name} to addListDrop() for {self.__repr__()}", Warning, stacklevel = 2)
			handle = None

		return handle

	def addListFull(self, *args, hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, widgetLabel = None, parent = None, handle = None, myId = None, tabSkip = False, flex = 0, flags = "c1", **kwargs):
		"""Adds a full list widget to the tool bar."""

		if (self.type is Types.toolbar):
			handle = handle_MenuItem()
			handle.type = Types.toolbaritem
			handle.subHandle = [handle._makeListFull, args, kwargs]
			handle._build(locals())
		else:
			warnings.warn(f"Add {self.type.name} to addListFull() for {self.__repr__()}", Warning, stacklevel = 2)
			handle = None

		return handle

	def addListTree(self, *args, hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, widgetLabel = None, parent = None, handle = None, myId = None, tabSkip = False, flex = 0, flags = "c1", **kwargs):
		"""Adds a full list widget to the tool bar."""

		if (self.type is Types.toolbar):
			handle = handle_MenuItem()
			handle.type = Types.toolbaritem
			handle.subHandle = [handle._makeListTree, args, kwargs]
			handle._build(locals())
		else:
			warnings.warn(f"Add {self.type.name} to addListTree() for {self.__repr__()}", Warning, stacklevel = 2)
			handle = None

		return handle

	def addInputSlider(self, *args, hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, widgetLabel = None, parent = None, handle = None, myId = None, tabSkip = False, flex = 0, flags = "c1", **kwargs):
		"""Adds an input slider widget to the tool bar."""

		if (self.type is Types.toolbar):
			handle = handle_MenuItem()
			handle.type = Types.toolbaritem
			handle.subHandle = [handle._makeInputSlider, args, kwargs]
			handle._build(locals())
		else:
			warnings.warn(f"Add {self.type.name} to addInputSlider() for {self.__repr__()}", Warning, stacklevel = 2)
			handle = None

		return handle

	def addInputBox(self, *args, hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, widgetLabel = None, parent = None, handle = None, myId = None, tabSkip = False, flex = 0, flags = "c1", **kwargs):
		"""Adds an input box widget to the tool bar."""

		if (self.type is Types.toolbar):
			handle = handle_MenuItem()
			handle.type = Types.toolbaritem
			handle.subHandle = [handle._makeInputBox, args, kwargs]
			handle._build(locals())
		else:
			warnings.warn(f"Add {self.type.name} to addInputBox() for {self.__repr__()}", Warning, stacklevel = 2)
			handle = None

		return handle

	def addInputSearch(self, *args, hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, widgetLabel = None, parent = None, handle = None, myId = None, tabSkip = False, flex = 0, flags = "c1", **kwargs):
		"""Adds a search box widget to the tool bar."""

		if (self.type is Types.toolbar):
			handle = handle_MenuItem()
			handle.type = Types.toolbaritem
			handle.subHandle = [handle._makeInputSearch, args, kwargs]
			handle._build(locals())
		else:
			warnings.warn(f"Add {self.type.name} to addInputSearch() for {self.__repr__()}", Warning, stacklevel = 2)
			handle = None

		return handle

	def addInputSpinner(self, *args, hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, widgetLabel = None, parent = None, handle = None, myId = None, tabSkip = False, flex = 0, flags = "c1", **kwargs):
		"""Adds an input spinner widget to the tool bar."""

		if (self.type is Types.toolbar):
			handle = handle_MenuItem()
			handle.type = Types.toolbaritem
			handle.subHandle = [handle._makeInputSpinner, args, kwargs]
			handle._build(locals())
		else:
			warnings.warn(f"Add {self.type.name} to addInputSpinner() for {self.__repr__()}", Warning, stacklevel = 2)
			handle = None

		return handle

	def addButton(self, *args, hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, widgetLabel = None, parent = None, handle = None, myId = None, tabSkip = False, flex = 0, flags = "c1", **kwargs):
		"""Adds a button widget to the tool bar."""

		if (self.type is Types.toolbar):
			handle = handle_MenuItem()
			handle.type = Types.toolbaritem
			handle.subHandle = [handle._makeButton, args, kwargs]
			handle._build(locals())
		else:
			warnings.warn(f"Add {self.type.name} to addButton() for {self.__repr__()}", Warning, stacklevel = 2)
			handle = None

		return handle

	def addButtonList(self, *args, hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, widgetLabel = None, parent = None, handle = None, myId = None, tabSkip = False, flex = 0, flags = "c1", **kwargs):
		"""Adds a button widget to the tool bar."""

		if (self.type is Types.toolbar):
			handle = handle_MenuItem()
			handle.type = Types.toolbaritem
			handle.subHandle = [handle._makeButtonList, args, kwargs]
			handle._build(locals())
		else:
			warnings.warn(f"Add {self.type.name} to addButtonList() for {self.__repr__()}", Warning, stacklevel = 2)
			handle = None

		return handle

	def addButtonToggle(self, *args, hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, widgetLabel = None, parent = None, handle = None, myId = None, tabSkip = False, flex = 0, flags = "c1", **kwargs):
		"""Adds a toggle button widget to the tool bar."""

		if (self.type is Types.toolbar):
			handle = handle_MenuItem()
			handle.type = Types.toolbaritem
			handle.subHandle = [handle._makeButtonToggle, args, kwargs]
			handle._build(locals())
		else:
			warnings.warn(f"Add {self.type.name} to addButtonToggle() for {self.__repr__()}", Warning, stacklevel = 2)
			handle = None

		return handle

	def addButtonCheck(self, *args, hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, widgetLabel = None, parent = None, handle = None, myId = None, tabSkip = False, flex = 0, flags = "c1", **kwargs):
		"""Adds a check button widget to the tool bar."""

		if (self.type is Types.toolbar):
			handle = handle_MenuItem()
			handle.type = Types.toolbaritem
			handle.subHandle = [handle._makeButtonCheck, args, kwargs]
			handle._build(locals())
		else:
			warnings.warn(f"Add {self.type.name} to addButtonCheck() for {self.__repr__()}", Warning, stacklevel = 2)
			handle = None

		return handle

	def addButtonCheckList(self, *args, hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, widgetLabel = None, parent = None, handle = None, myId = None, tabSkip = False, flex = 0, flags = "c1", **kwargs):
		"""Adds a check list widget to the tool bar."""

		if (self.type is Types.toolbar):
			handle = handle_MenuItem()
			handle.type = Types.toolbaritem
			handle.subHandle = [handle._makeButtonCheckList, args, kwargs]
			handle._build(locals())
		else:
			warnings.warn(f"Add {self.type.name} to addButtonCheckList() for {self.__repr__()}", Warning, stacklevel = 2)
			handle = None

		return handle

	def addButtonRadio(self, *args, hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, widgetLabel = None, parent = None, handle = None, myId = None, tabSkip = False, flex = 0, flags = "c1", **kwargs):
		"""Adds a radio button widget to the tool bar."""

		if (self.type is Types.toolbar):
			handle = handle_MenuItem()
			handle.type = Types.toolbaritem
			handle.subHandle = [handle._makeButtonRadio, args, kwargs]
			handle._build(locals())
		else:
			warnings.warn(f"Add {self.type.name} to addButtonRadio() for {self.__repr__()}", Warning, stacklevel = 2)
			handle = None

		return handle

	def addButtonRadioBox(self, *args, hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, widgetLabel = None, parent = None, handle = None, myId = None, tabSkip = False, flex = 0, flags = "c1", **kwargs):
		"""Adds a radio button box widget to the tool bar."""

		if (self.type is Types.toolbar):
			handle = handle_MenuItem()
			handle.type = Types.toolbaritem
			handle.subHandle = [handle._makeButtonRadioBox, args, kwargs]
			handle._build(locals())
		else:
			warnings.warn(f"Add {self.type.name} to addButtonRadioBox() for {self.__repr__()}", Warning, stacklevel = 2)
			handle = None

		return handle

	def addButtonImage(self, *args, hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, widgetLabel = None, parent = None, handle = None, myId = None, tabSkip = False, flex = 0, flags = "c1", **kwargs):
		"""Adds an image button widget to the tool bar."""

		if (self.type is Types.toolbar):
			handle = handle_MenuItem()
			handle.type = Types.toolbaritem
			handle.subHandle = [handle._makeButtonImage, args, kwargs]
			handle._build(locals())
		else:
			warnings.warn(f"Add {self.type.name} to addButtonImage() for {self.__repr__()}", Warning, stacklevel = 2)
			handle = None

		return handle

	def addImage(self, *args, hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, widgetLabel = None, parent = None, handle = None, myId = None, tabSkip = False, flex = 0, flags = "c1", **kwargs):
		"""Adds an image widget to the tool bar."""

		if (self.type is Types.toolbar):
			handle = handle_MenuItem()
			handle.type = Types.toolbaritem
			handle.subHandle = [handle._makeImage, args, kwargs]
			handle._build(locals())
		else:
			warnings.warn(f"Add {self.type.name} to addImage() for {self.__repr__()}", Warning, stacklevel = 2)
			handle = None

		return handle

	def addProgressBar(self, *args, hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, widgetLabel = None, parent = None, handle = None, myId = None, tabSkip = False, flex = 0, flags = "c1", **kwargs):
		"""Adds a progress bar widget to the tool bar."""

		if (self.type is Types.toolbar):
			handle = handle_MenuItem()
			handle.type = Types.toolbaritem
			handle.subHandle = [handle._makeProgressBar, args, kwargs]
			handle._build(locals())
		else:
			warnings.warn(f"Add {self.type.name} to addProgressBar() for {self.__repr__()}", Warning, stacklevel = 2)
			handle = None

		return handle

	def addPickerColor(self, *args, hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, widgetLabel = None, parent = None, handle = None, myId = None, tabSkip = False, flex = 0, flags = "c1", **kwargs):
		"""Adds a color picker widget to the tool bar."""

		if (self.type is Types.toolbar):
			handle = handle_MenuItem()
			handle.type = Types.toolbaritem
			handle.subHandle = [handle._makePickerColor, args, kwargs]
			handle._build(locals())
		else:
			warnings.warn(f"Add {self.type.name} to addPickerColor() for {self.__repr__()}", Warning, stacklevel = 2)
			handle = None

		return handle

	def addPickerFont(self, *args, hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, widgetLabel = None, parent = None, handle = None, myId = None, tabSkip = False, flex = 0, flags = "c1", **kwargs):
		"""Adds a font picker widget to the tool bar."""

		if (self.type is Types.toolbar):
			handle = handle_MenuItem()
			handle.type = Types.toolbaritem
			handle.subHandle = [handle._makePickerFont, args, kwargs]
			handle._build(locals())
		else:
			warnings.warn(f"Add {self.type.name} to addPickerFont() for {self.__repr__()}", Warning, stacklevel = 2)
			handle = None

		return handle

	def addPickerFile(self, *args, hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, widgetLabel = None, parent = None, handle = None, myId = None, tabSkip = False, flex = 0, flags = "c1", **kwargs):
		"""Adds a file picker widget to the tool bar."""

		if (self.type is Types.toolbar):
			handle = handle_MenuItem()
			handle.type = Types.toolbaritem
			handle.subHandle = [handle._makePickerFile, args, kwargs]
			handle._build(locals())
		else:
			warnings.warn(f"Add {self.type.name} to addPickerFile() for {self.__repr__()}", Warning, stacklevel = 2)
			handle = None

		return handle

	def addPickerFileWindow(self, *args, hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, widgetLabel = None, parent = None, handle = None, myId = None, tabSkip = False, flex = 0, flags = "c1", **kwargs):
		"""Adds a file window picker widget to the tool bar."""

		if (self.type is Types.toolbar):
			handle = handle_MenuItem()
			handle.type = Types.toolbaritem
			handle.subHandle = [handle._makePickerFileWindow, args, kwargs]
			handle._build(locals())
		else:
			warnings.warn(f"Add {self.type.name} to addPickerFileWindow() for {self.__repr__()}", Warning, stacklevel = 2)
			handle = None

		return handle

	def addPickerTime(self, *args, hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, widgetLabel = None, parent = None, handle = None, myId = None, tabSkip = False, flex = 0, flags = "c1", **kwargs):
		"""Adds a time picker widget to the tool bar."""

		if (self.type is Types.toolbar):
			handle = handle_MenuItem()
			handle.type = Types.toolbaritem
			handle.subHandle = [handle._makePickerTime, args, kwargs]
			handle._build(locals())
		else:
			warnings.warn(f"Add {self.type.name} to addPickerTime() for {self.__repr__()}", Warning, stacklevel = 2)
			handle = None

		return handle

	def addPickerDate(self, *args, hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, widgetLabel = None, parent = None, handle = None, myId = None, tabSkip = False, flex = 0, flags = "c1", **kwargs):
		"""Adds a date picker widget to the tool bar."""

		if (self.type is Types.toolbar):
			handle = handle_MenuItem()
			handle.type = Types.toolbaritem
			handle.subHandle = [handle._makePickerDate, args, kwargs]
			handle._build(locals())
		else:
			warnings.warn(f"Add {self.type.name} to addPickerDate() for {self.__repr__()}", Warning, stacklevel = 2)
			handle = None

		return handle

	def addPickerDateWindow(self, *args, hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, widgetLabel = None, parent = None, handle = None, myId = None, tabSkip = False, flex = 0, flags = "c1", **kwargs):
		"""Adds a text date window picker to the tool bar."""

		if (self.type is Types.toolbar):
			handle = handle_MenuItem()
			handle.type = Types.toolbaritem
			handle.subHandle = [handle._makePickerDateWindow, args, kwargs]
			handle._build(locals())
		else:
			warnings.warn(f"Add {self.type.name} to addPickerDateWindow() for {self.__repr__()}", Warning, stacklevel = 2)
			handle = None

		return handle

class handle_MenuItem(handle_Widget_Base):
	"""A handle for working with menu widgets."""

	def __init__(self):
		"""Initializes defaults."""

		#Initialize inherited classes
		handle_Widget_Base.__init__(self)

		#Internal Variables
		self.shown = True
		self.subHandle = None

	def __len__(self):
		"""Returns what the contextual length is for the object associated with this handle."""

		if (self.type is Types.menuitem):
			value = len(self.thing.GetLabel()) #(int) - How long the text inside the menu item is

		else:
			warnings.warn(f"Add {self.type.name} to __len__() for {self.__repr__()}", Warning, stacklevel = 2)
			value = 0

		return value

	def _build(self, argument_catalogue):
		"""Determiens which build system to use for this handle."""

		def _build_menuItem():
			"""Builds a wx menu item control object."""
			nonlocal self, argument_catalogue
		
			#Unpack arguments
			buildSelf, text, hidden = self._getArguments(argument_catalogue, ["self", "text", "hidden"])
			myId = self._getArguments(argument_catalogue, ["myId"])

			#Account for separators
			if (text is None):
				myId = self._getId(argument_catalogue)

				self.subType = "separator"
				self.thing = wx.MenuItem(self.parent.thing, id = myId, kind = wx.ITEM_SEPARATOR)
			else:
				special, check, default = self._getArguments(argument_catalogue, ["special", "check", "default"])
				myFunction = self._getArguments(argument_catalogue, ["myFunction"])
				
				myId = self._getId(argument_catalogue, checkSpecial = True)
				if ((myId == wx.ID_ANY) and (len(text) == 0)):
					text = " " #Must define text or wx.MenuItem will think myId is a stock item id

				#Create Menu Item
				if (check is None):
					self.subType = "normal"
					self.thing = wx.MenuItem(self.parent.thing, myId, text)

					#Determine icon
					icon, internal = self._getArguments(argument_catalogue, ["icon", "internal"])
					if (icon is not None):
						image = self.getImage(icon, internal, scale = (16, 16))
						# image = self._convertBitmapToImage(image)
						# image = image.Scale(16, 16, wx.IMAGE_QUALITY_HIGH)
						# image = self._convertImageToBitmap(image)
						self.thing.SetBitmap(image)
				else:
					if (check):
						self.subType = "check"
						self.thing = wx.MenuItem(self.parent.thing, myId, text, kind = wx.ITEM_CHECK)
					else:
						self.subType = "radio"
						self.thing = wx.MenuItem(self.parent.thing, myId, text, kind = wx.ITEM_RADIO)

				#Determine initial value
				if (check is not None):
					if (default):
						self.thing.Check(True)

				#Determine how to do the bound function
				if (myFunction is None):
					if (special is not None):
						if (special[0] == "q" or special[0] == "e"):
							buildSelf._betterBind(wx.EVT_MENU, self.thing, "self.onExit")
						elif (special[0] == "c"):
							buildSelf._betterBind(wx.EVT_MENU, self.thing, "self.onQuit")
						elif (special[0] == "h"):
							buildSelf._betterBind(wx.EVT_MENU, self.thing, "self.onHide")
						elif (special[0] == "s"):
							buildSelf._betterBind(wx.EVT_MENU, self.thing, "self.onToggleStatusBar")
						elif (special[0] == "t"):
							buildSelf._betterBind(wx.EVT_MENU, self.thing, "self.onToggleToolBar")
						else:
							errorMessage = f"Unknown special function {special} for {self.__repr__()}"
							raise KeyError(errorMessage)
				else:
					myFunctionArgs, myFunctionKwargs = self._getArguments(argument_catalogue, ["myFunctionArgs", "myFunctionKwargs"])
					buildSelf._betterBind(wx.EVT_MENU, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)

		def _build_flatmenuItem():
			"""Builds a wx flat menu item control object."""
			nonlocal self, argument_catalogue

			#Unpack arguments
			buildSelf, text, hidden = self._getArguments(argument_catalogue, ["self", "text", "hidden"])
			myId = self._getArguments(argument_catalogue, ["myId"])

			self.thing = wx.lib.agw.flatmenu


		def _build_toolbarItem():
			"""Builds a wx tool control object."""
			nonlocal self, argument_catalogue

			if (self.subHandle is not None):
				widgetLabel, hidden = self._getArguments(argument_catalogue, ["widgetLabel", "hidden"])
				myFunction, myFunctionArgs, myFunctionKwargs = self.subHandle
				self.subHandle = myFunction(*myFunctionArgs, label = widgetLabel, **myFunctionKwargs)
				self.subType = self.subHandle.type
				self.nest(self.subHandle)
			else:
				text = self._getArguments(argument_catalogue, ["text"])
				if (text is None):
					stretchable = self._getArguments(argument_catalogue, ["stretchable"])
					if (stretchable):
						self.subType = "stretchable"
						self.thing = self.parent.thing.AddStretchableSpace()
					else:
						self.subType = "separator"
						self.thing = self.parent.thing.AddSeparator()
				else:
					icon, internal, scale = self._getArguments(argument_catalogue, ["icon", "internal", "scale"])
					disabled_icon, disabled_internal, disabled_scale = self._getArguments(argument_catalogue, ["disabled_icon", "disabled_internal", "disabled_scale"])
					check, default, myFunction, special = self._getArguments(argument_catalogue, ["check", "default", "myFunction", "special"])
					
					#Get Images
					if (icon is None):
						warnings.warn(f"No icon provided for {self.__repr__()}", Warning, stacklevel = 5)
						icon = "error"
						internal = True
					image = self.getImage(icon, internal, scale = scale)

					if (disabled_icon is None):
						imageDisabled = wx.NullBitmap
					else:
						if (disabled_internal is None):
							disabled_internal = internal
						imageDisabled = self.getImage(disabled_icon, disabled_internal, scale = disabled_scale)

					#Configure Settings
					# if (toolTip is None):
					#   toolTip = ""
					# elif (not isinstance(toolTip, str)):
					#   toolTip = f"{toolTip}"

					if (check is None):
						self.subType = "normal"
						kind = "wx.ITEM_NORMAL"
					else:
						if (check):
							self.subType = "check"
							kind = "wx.ITEM_CHECK"
						else:
							self.subType = "radio"
							kind = "wx.ITEM_RADIO"

					self.thing = self.parent.thing.AddTool(wx.ID_ANY, text, image, imageDisabled, kind = eval(kind, {'__builtins__': None, "wx": wx}, {}))#, shortHelp = toolTip, longHelp = toolTip)

					if (default):
						self.thing.SetToggle(True)#Determine how to do the bound function
					
					if (myFunction is None):
						if (special is not None):
							if (special[0] == "q" or special[0] == "e"):
								self.parent._betterBind(wx.EVT_TOOL, self.thing, "self.onExit")
							elif (special[0] == "c"):
								self.parent._betterBind(wx.EVT_TOOL, self.thing, "self.onQuit")
							elif (special[0] == "h"):
								self.parent._betterBind(wx.EVT_TOOL, self.thing, "self.onHide")
							elif (special[0] == "s"):
								self.parent._betterBind(wx.EVT_TOOL, self.thing, "self.onToggleStatusBar")
							elif (special[0] == "t"):
								self.parent._betterBind(wx.EVT_TOOL, self.thing, "self.onToggleToolBar")
							else:
								errorMessage = f"Unknown special function {special} for {self.__repr__()}"
								raise KeyError(errorMessage)
					else:
						myFunctionArgs, myFunctionKwargs = self._getArguments(argument_catalogue, ["myFunctionArgs", "myFunctionKwargs"])
						self.parent._betterBind(wx.EVT_TOOL, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)

			self.parent.thing.Realize()
		
		#########################################################

		self._preBuild(argument_catalogue)

		if (self.type is Types.menuitem):
			_build_menuItem()
		elif (self.type is Types.flatmenuitem):
			_build_flatmenuItem()
		elif (self.type is Types.toolbaritem):
			_build_toolbarItem()
		else:
			warnings.warn(f"Add {self.type.name} to _build() for {self.__repr__()}", Warning, stacklevel = 2)

		self._postBuild(argument_catalogue)

	def getValue(self, event = None):
		"""Returns what the contextual value is for the object associated with this handle."""

		if (self.type is Types.menuitem):
			if (self.thing.IsCheckable()):
				value = self.thing.IsChecked() #(bool) - True: Selected; False: Un-Selected
			else:
				value = self.thing.GetText() #(str) - What the selected item says
				
		elif ((self.type is Types.toolbaritem) and (self.subHandle is not None)):
			value = self.subHandle.getValue(event = event)
			
		else:
			warnings.warn(f"Add {self.type.name} to getValue() for {self.__repr__()}", Warning, stacklevel = 2)
			value = None

		return value

	def getIndex(self, event = None):
		"""Returns what the contextual index is for the object associated with this handle."""

		if (self.type is Types.menuitem):
			if (event is not None):
				value = event.GetId()
			else:
				errorMessage = "Pass the event parameter to getIndex() when working with menu items"
				raise SyntaxError(errorMessage)
				
		elif ((self.type is Types.toolbaritem) and (self.subHandle is not None)):
			value = self.subHandle.setValue(event = event)

		else:
			warnings.warn(f"Add {self.type.name} to getIndex() for {self.__repr__()}", Warning, stacklevel = 2)
			value = None

		return value

	#Setters
	def setValue(self, newValue, event = None):
		"""Sets the contextual value for the object associated with this handle to what the user supplies."""

		if (self.type is Types.menuitem):
			if ((self.thing.GetKind() == wx.ITEM_CHECK) or (self.thing.GetKind() == wx.ITEM_RADIO)):
				if (isinstance(newValue, str)):
					newValue = ast.literal_eval(re.sub("^['\"]|['\"]$", "", newValue))
				self.thing.Check(newValue) #(bool) - True: selected; False: un-selected
			else:
				errorMessage = f"Only a menu 'Check Box' or 'Radio Button' can be set to a different value for setValue() for {self.__repr__()}"
				raise SyntaxError(errorMessage)

		elif ((self.type is Types.toolbaritem) and (self.subHandle is not None)):
			self.subHandle.setValue(newValue, event = event)

		else:
			warnings.warn(f"Add {self.type.name} to setValue() for {self.__repr__()}", Warning, stacklevel = 2)

	#Change Settings
	def setFunction_click(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, **kwargs):
		"""Changes the function that runs when a menu item is selected."""

		if (self.type is Types.menuitem):
			self.parent._betterBind(wx.EVT_MENU, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		
		elif (self.type is Types.toolbaritem):
			if (self.subHandle is not None):
				self.subHandle.setFunction_click(myFunction = myFunction, myFunctionArgs = myFunctionArgs, myFunctionKwargs = myFunctionKwargs, **kwargs)
			else:
				self.parent._betterBind(wx.EVT_TOOL, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		else:
			warnings.warn(f"Add {self.type.name} to setFunction_enter() for {self.__repr__()}", Warning, stacklevel = 2)
	
	def setFunction_rightClick(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, **kwargs):
		"""Overridden to account for a subHandle."""

		if (self.type is Types.toolbaritem):
			if (self.subHandle is not None):
				self.subHandle.setFunction_rightClick(myFunction = myFunction, myFunctionArgs = myFunctionArgs, myFunctionKwargs = myFunctionKwargs, **kwargs)
			else:
				self.parent._betterBind(wx.EVT_TOOL_RCLICKED, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		else:
			super().setFunction_rightClick(myFunction = myFunction, myFunctionArgs = myFunctionArgs, myFunctionKwargs = myFunctionKwargs, **kwargs)

	def setFunction_enter(self, *args, **kwargs):
		"""Override function for subHandle."""

		if ((self.type is Types.toolbaritem) and (self.subHandle is not None)):
			self.subHandle.setFunction_enter(*args, **kwargs)
		else:
			warnings.warn(f"Add {self.type.name} to setFunction_enter() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_preEdit(self, *args, **kwargs):
		"""Override function for subHandle."""

		if ((self.type is Types.toolbaritem) and (self.subHandle is not None)):
			self.subHandle.setFunction_preEdit(*args, **kwargs)
		else:
			warnings.warn(f"Add {self.type.name} to setFunction_preEdit() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_postEdit(self, *args, **kwargs):
		"""Override function for subHandle."""

		if ((self.type is Types.toolbaritem) and (self.subHandle is not None)):
			self.subHandle.setFunction_postEdit(*args, **kwargs)
		else:
			warnings.warn(f"Add {self.type.name} to setFunction_postEdit() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_search(self, *args, **kwargs):
		"""Override function for subHandle."""

		if ((self.type is Types.toolbaritem) and (self.subHandle is not None)):
			self.subHandle.setFunction_search(*args, **kwargs)
		else:
			warnings.warn(f"Add {self.type.name} to setFunction_search() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_cancel(self, *args, **kwargs):
		"""Override function for subHandle."""

		if ((self.type is Types.toolbaritem) and (self.subHandle is not None)):
			self.subHandle.setFunction_cancel(*args, **kwargs)
		else:
			warnings.warn(f"Add {self.type.name} to setFunction_cancel() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_menuSelect(self, *args, **kwargs):
		"""Override function for subHandle."""

		if ((self.type is Types.toolbaritem) and (self.subHandle is not None)):
			self.subHandle.setFunction_menuSelect(*args, **kwargs)
		else:
			warnings.warn(f"Add {self.type.name} to setFunction_menuSelect() for {self.__repr__()}", Warning, stacklevel = 2)

	def setEnable(self, state = True):
		"""Enables or disables an item based on the given input.

		state (bool) - If it is enabled or not

		Example Input: setEnable()
		Example Input: setEnable(False)
		"""

		if (self.type is Types.menuitem):
			handle_Widget_Base.setEnable(self, state = state)

		elif (self.type in (Types.flatmenuitem, Types.toolbaritem)):
			self.parent.setEnable(state = state, label = self.label)

		else:
			warnings.warn(f"Add {self.type.name} to setEnable() for {self.__repr__()}", Warning, stacklevel = 2)

	def checkEnabled(self):
		"""Checks if an item is enabled.

		Example Input: checkEnabled()
		"""

		if (self.type is Types.menuitem):
			state = handle_Widget_Base.checkEnabled(self)

		elif (self.type in (Types.flatmenuitem, Types.toolbaritem)):
			state = self.parent.checkEnabled(self.label, state)

		else:
			warnings.warn(f"Add {self.type.name} to checkEnabled() for {self.__repr__()}", Warning, stacklevel = 2)
			state = None

		return state
	
	def setShow(self, state = True):
		"""Shows or hides an item based on the given input.

		state (bool) - If it is shown or not

		Example Input: setShow()
		Example Input: setShow(False)
		"""

		self.parent.setShow(self.label, state)

	def checkShown(self):
		"""Checks if an item is shown.

		Example Input: checkShown()
		"""

		state = self.shown

		return state

	def setImage(self, image = None, *, disabled = False, **imageKwargs):
		"""Changes the image on the toolbar icon.

		Example Input: setImage()
		Example Input: setImage("resources/update_timer.ico")
		"""

		if (disabled):
			self.thing.SetDisabledBitmap(self.getImage(image, **imageKwargs))
		else:
			self.thing.SetNormalBitmap(self.getImage(image, **imageKwargs))

		self.parent.thing.Realize()
		self.parent.thing.Refresh()

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

	def _build(self, argument_catalogue):
		"""Determiens which build system to use for this handle."""

		def _build_menuPopup():
			"""Builds a wx menu control object."""
			nonlocal self, argument_catalogue
		
			#Unpack arguments
			buildSelf, text, label, hidden, enabled, rightClick = self._getArguments(argument_catalogue, ["self", "text", "label", "hidden", "enabled", "rightClick"])

			#Remember sub menu details
			self.text = text
			self.label = label
			self.hidden = hidden
			self.enabled = enabled

			#Bind functions
			if (rightClick is not None):
				preFunction, preFunctionArgs, preFunctionKwargs = argument_catalogue["preFunction", "preFunctionArgs", "preFunctionKwargs"]
				postFunction, postFunctionArgs, postFunctionKwargs = argument_catalogue["postFunction", "postFunctionArgs", "postFunctionKwargs"]

				if (rightClick):
					self._betterBind(wx.EVT_RIGHT_DOWN, self.parent.thing, self.onTriggerPopupMenu, [[preFunction, preFunctionArgs, preFunctionKwargs], [postFunction, postFunctionArgs, postFunctionKwargs]])
				else:
					self._betterBind(wx.EVT_LEFT_DOWN, self.parent.thing, self.onTriggerPopupMenu, [[preFunction, preFunctionArgs, preFunctionKwargs], [postFunction, postFunctionArgs, postFunctionKwargs]])

		
		#########################################################

		self._preBuild(argument_catalogue)

		if (self.type is Types.popup):
			_build_menuPopup()
		elif (self.type is Types.popup_widget):
			_build_menuPopup()
		else:
			warnings.warn(f"Add {self.type.name} to _build() for {self.__repr__()}", Warning, stacklevel = 2)

		self._postBuild(argument_catalogue)

	def getValue(self, event = None):
		"""Returns what the contextual value is for the object associated with this handle."""

		if (self.popupMenu is not None):
			value = self.popupMenu.myMenu.getValue(event = event)
		else:
			warnings.warn(f"Popup Menu not shown for getValue() in {self.__repr__()}", Warning, stacklevel = 2)
			value = None

		return value

	def getIndex(self, event = None):
		"""Returns what the contextual index is for the object associated with this handle."""

		if (self.popupMenu is not None):
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
		check = None, default = False,

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, 

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None, tabSkip = False):
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
		handle.type = Types.popupitem
		handle._build(locals())

		self.nest(handle)

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

	def addSub(self, text = None, 

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None, tabSkip = False):
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
		handle.type = Types.popup
		handle._build(locals())

		# handle.icon = None
		# handle.internal = False
		# handle.special = None
		# handle.check = None
		# handle.default = False

		#Nest handle
		self.nest(handle)

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
			while ((parent != grandParent) and (grandParent is not None)):
				parent = grandParent
				grandParent = parent.GetParent()

				#Ignore root window position
				if (grandParent is not None):
					position += parent.GetPosition()
		else:
			#Get position on screen
			position = event.GetPosition()

		#Skip empty popup lists
		if (len(self.contents) < 1):
			warnings.warn(f"Popup Menu {self.__repr__()} for {self.myWindow.__repr__()} has no contents", Warning, stacklevel = 2)
		else:
			#Create temporary popup menu
			self.popupMenu = self._MyPopupMenu(self, preFunction, postFunction)
			self.myWindow.thing.PopupMenu(self.popupMenu.thing, position)

			#Destroy the popup menu in memory
			for item in self[:]:
				if (isinstance(item, (handle_MenuPopupItem, handle_MenuPopupSubMenu, handle_Menu, handle_MenuItem))):
					del self[item]
			self.popupMenu.thing.Destroy()
			self.popupMenu = None
			self.thing = None

		event.Skip()

	class _MyPopupMenu():
		"""Creates a pop up menu.
		Because of the way that the popup menu is created, the items within must be
		determineed before the initial creation.

		Note: The runFunction is NOT an event function. It is a normal function.

		In order to allow for customization, the user creates a dictionary of
		{labels: functions}. This dictionary is then used to populate the menu.
		"""

		def __init__(self, parent, popupMenuLabel, preFunction = [None, None, None], postFunction = [None, None, None], idCatalogueLabel = None):
			"""Defines the internal variables needed to run.

			Example Input: _MyPopupMenu(self)
			"""

			#Internal Variables
			self.parent = parent

			#Configure menu
			self.myMenu = self.addMenu()
			self.thing = self.myMenu.thing
			self.parent.thing = self.myMenu.thing

			#Run pre function(s)
			self.parent.runMyFunction(preFunction[0], preFunction[1], preFunction[2])

			#Create Menu
			self.populateMenu(self.myMenu, self.parent.contents)

			#Run post function(s)
			self.parent.runMyFunction(postFunction[0], postFunction[1], postFunction[2])

		def addMenu(self, *args, **kwargs):
			"""Adds a menu to a pre-existing menuBar.
			This is a collapsable array of menu items.

			text (str)        - What the menu is called
				If you add a '&', a keyboard shortcut will be made for the letter after it
			label (str)     - What this is called in the idCatalogue
			detachable (bool) - If True: The menu can be undocked

			Example Input: addMenu(0, "&File")
			Example Input: addMenu("first", "&File")
			"""

			handle = self.parent._makeMenu(*args, **kwargs)
			self.parent._finalNest(handle)
			return handle

		def populateMenu(self, menu, contents):
			"""Uses a dictionary to populate the menu with items and bound events."""

			#Create the menu
			if (len(contents) != 0):
				for i, handle in enumerate(contents):
					if (isinstance(handle, handle_MenuPopup)):
						subMenu = menu.addSub(text = handle.text, label = handle.label, hidden = handle.hidden)
						self.populateMenu(subMenu, handle.contents)

					elif (handle.text is not None):
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

	def _build(self, argument_catalogue):
		self._preBuild(argument_catalogue)

		text = self._getArguments(argument_catalogue, "text")

		#Check for separator
		if (text is not None):
			enabled, hidden = self._getArguments(argument_catalogue, ["enabled", "hidden"])

			myFunction, myFunctionArgs, myFunctionKwargs, = self._getArguments(argument_catalogue, ["myFunction", "myFunctionArgs", "myFunctionKwargs"])
			icon, internal = self._getArguments(argument_catalogue, ["icon", "internal"])
			check, default, = self._getArguments(argument_catalogue, ["check", "default"])

			#Prepare menu item
			if (myFunction is None):
				special = self._getArguments(argument_catalogue, "special")
				if (special is not None):
					#Ensure correct format
					if ((special is not None) and (not isinstance(special, str))):
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
	"""A handle for working with canvas widgets.
	Special thanks to FogleBird for how to implement a double buffered canvas on https://stackoverflow.com/questions/16597110/best-canvas-for-wxpython
	See: https://wiki.wxpython.org/DoubleBufferedDrawing
	See: http://zetcode.com/wxpython/gdi/

	See: https://wxpython.org/Phoenix/docs/html/wx.lib.plot.plotcanvas.PlotCanvas.html
	See: https://wxpython.org/Phoenix/docs/html/wx.lib.floatcanvas.FloatCanvas.FloatCanvas.html
	"""

	def __init__(self):
		"""Initializes defaults."""

		#Initialize inherited classes
		handle_Widget_Base.__init__(self)

		#Defaults
		self.paint_count = 0
		self.drawQueue = [] #What will be drawn on the window. Items are drawn from left to right in their list order. [function, args, kwargs, includeDC]
		self.drawQueue_saved = {}
		self.boundingBox = (0, 0, 0, 0)

	def _build(self, argument_catalogue):
		"""Determiens which build system to use for this handle."""

		def _build_canvas():
			"""Builds a wx panel object and makes it a canvas for painting."""
			nonlocal self, argument_catalogue

			panel, metric, initFunction, buildSelf = self._getArguments(argument_catalogue, ["panel", "metric", "initFunction", "self"])

			self.metric = metric
			#Create the thing
			if (panel is not None):
				self.myPanel = self._makePanel(parent = buildSelf.parent, **panel)
				self._finalNest(self.myPanel)
				self.thing = self.myPanel.thing

				#Bind Functions
				if (initFunction is not None):
					initFunctionArgs, initFunctionKwargs = self._getArguments(argument_catalogue, ["initFunctionArgs", "initFunctionKwargs"])
					self.setFunction_init(initFunction, initFunctionArgs, initFunctionKwargs)

				#Enable painting
				self._betterBind(wx.EVT_PAINT, self.thing, self._onPaint)
				self._betterBind(wx.EVT_SIZE, self.thing, self._onSize)
				# self._betterBind(wx.EVT_ERASE_BACKGROUND, self.thing, self.onDoNothing) #Disable background erasing to reduce flicker

			#Tell the window that EVT_PAINT will be running (reduces flickering)
			if (self.myWindow is not None):
				self.myWindow.thing.SetBackgroundStyle(wx.BG_STYLE_PAINT)
			if (panel is not None):
				self.thing.SetBackgroundStyle(wx.BG_STYLE_PAINT)

			self.new()
		
		#########################################################

		self._preBuild(argument_catalogue)

		if (self.type is Types.canvas):
			_build_canvas()
		else:
			warnings.warn(f"Add {self.type.name} to _build() for {self.__repr__()}", Warning, stacklevel = 2)

		self._postBuild(argument_catalogue)

	def setFunction_init(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		"""Changes the function that runs when the object is first created."""

		if (self.type is Types.canvas):
			self.parent._betterBind(wx.EVT_INIT_DIALOG, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		else:
			warnings.warn(f"Add {self.type.name} to setFunction_init() for {self.__repr__()}", Warning, stacklevel = 2)

	def _onPaint(self, event):
		"""Needed so that the GUI can draw on the panel."""

		dc = wx.AutoBufferedPaintDC(self.thing)
		dc.Clear()
		self._draw(dc)
		self.boundingBox = dc.GetBoundingBox()

		event.Skip()

	def _onSize(self, event):
		"""Needed so that the GUI can draw on the panel."""

		self.thing.Refresh()
		event.Skip()

	def setFunction_click(self, *args, **kwargs):
		"""Overload function for setFunction_click() in handle_Panel."""
		if (self.thing is None):
			errorMessage = f"A panel was not created because 'panel' was None upon creation for {self.__repr__()}"
			raise ValueError(errorMessage)

		self.myPanel.setFunction_click(*args, **kwargs)

	def update(self):
		"""Redraws the canvas."""

		if (self.thing is None):
			errorMessage = f"A panel was not created because 'panel' was None upon creation for {self.__repr__()}"
			raise ValueError(errorMessage)

		self.thing.Refresh()
		self.thing.Update()

		self.myWindow.updateWindow()

	def save(self, fileName, fileType = wx.BITMAP_TYPE_PNG):
		"""Save the contents of the buffer to the specified file.
		See: https://wxpython.org/Phoenix/docs/html/wx.BitmapType.enumeration.html

		Example Input: save("example.png")
		"""

		image = self.getCanvasImage()
		image.SaveFile(fileName, fileType)

	def _getDC(self):
		"""Returns a dc with the canvas on it."""

		dc = wx.MemoryDC()
		dc.Clear()
		self._draw(dc)

		return dc

	def getCanvasImage(self):
		"""Returns an image with the canvas on it."""

		width, height = self.getSize()
		bitmap = wx.Bitmap(width, height)

		dc = wx.MemoryDC()
		dc.SelectObject(bitmap)
		self._draw(dc)
		dc.SelectObject(wx.NullBitmap)

		image = self._convertBitmapToImage(bitmap)

		return image

	def getSize(self):
		"""Returns the size of the canvas."""

		width = self.boundingBox[2] - self.boundingBox[0] if (self.boundingBox[2] - self.boundingBox[0] > 0) else 1
		height = self.boundingBox[3] - self.boundingBox[1] if (self.boundingBox[3] - self.boundingBox[1] > 0) else 1
		return width, height

	def getDrawnSize(self):
		"""Returns the size of what would be drawn on the canvas."""

		dc = self._getDC()
		rectangle = dc.GetBoundingBox()
		width = rectangle[2] - rectangle[0] if (rectangle[2] - rectangle[0] > 0) else 1
		height = rectangle[3] - rectangle[1] if (rectangle[3] - rectangle[1] > 0) else 1
		return width, height

	def _queue(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, includeDC = False):
		"""Queues a drawing function for the canvas.

		Example Input: _queue(drawRectangle, [5, 5, 25, 25])
		"""

		#Do not queue empty functions
		if (myFunction is not None):
			self.drawQueue.append([myFunction, myFunctionArgs, myFunctionKwargs, includeDC])

	def saveQueue(self, label = None):
		"""Remembers what the queue looks like so far.

		Example Input: saveQueue()
		Example Input: saveQueue("step 1")
		"""

		if (label in self.drawQueue_saved):
			warnings.warn(f"Overwriting save queue {label} saved in saveQueue() for {self.__repr__()}", Warning, stacklevel = 2)
		
		self.drawQueue_saved[label] = self.drawQueue[:]

	def removeQueue(self, label = None):
		"""Removes a saved queue

		Example Input: removeQueue()
		Example Input: removeQueue("step 1")
		"""

		if (label in self.drawQueue_saved):
			del self.drawQueue_saved[label]
		else:
			warnings.warn(f"There is no queue {label} saved in removeQueue() for {self.__repr__()}", Warning, stacklevel = 2)

	def loadQueue(self, label = None):
		"""Replaces the draw queue with a saved queue

		Example Input: loadQueue()
		Example Input: loadQueue("step 1")
		"""

		if (label in self.drawQueue_saved):
			self.drawQueue = self.drawQueue_saved[label][:]
		else:
			warnings.warn(f"There is no queue {label} saved in loadQueue() for {self.__repr__()}", Warning, stacklevel = 2)

	def new(self):
		"""Empties the draw queue and clears the canvas.

		Example Input: new()
		"""

		#Clear queue
		self.drawQueue = []

		brush = wx.Brush("White")
		self._queue("dc.SetBackground", brush)
		self._queue("dc.Clear")

	def fit(self):
		"""Fits the sizer item size to what has been drawn on the camnvas so far.

		Example Input: fit()
		"""

		if (self.thing is None):
			errorMessage = f"A panel was not created because 'panel' was None upon creation for {self.__repr__()}"
			raise ValueError(errorMessage)

		if (not self.myWindow.checkShown(window = True)):
			self.myWindow.showWindow()
			self.myWindow.hideWindow()

		drawnSize = self.getDrawnSize()
		mySize = self.thing.GetSize()
		windowSize = self.myWindow.getWindowSize()

		size_x = windowSize[0] + drawnSize[0] - mySize[0]
		size_y = windowSize[1] + drawnSize[1] - mySize[1]
		self.myWindow.setWindowSize(size_x, size_y)

	def _draw(self, dc, modifyUnits = True):
		"""Draws the queued shapes.

		Example Input: _draw(dc)
		"""

		if (modifyUnits):
			if (self.metric is not None):
				if (self.metric):
					dc.SetMapMode(wx.MM_METRIC)
				else:
					dc.SetMapMode(wx.MM_LOMETRIC)
			else:
				dc.SetMapMode(wx.MM_TEXT)

		#Draw items in queue
		for myFunction, myFunctionArgs, myFunctionKwargs, includeDC in self.drawQueue:
			if (isinstance(myFunction, str)):
				myFunctionEvaluated = eval(myFunction, {'__builtins__': None}, {"self": self, "dc": dc})
			else:
				myFunctionEvaluated = myFunction

			if (includeDC):
				self.runMyFunction(myFunctionEvaluated, [dc] + (myFunctionArgs or []), myFunctionKwargs)
			else:
				self.runMyFunction(myFunctionEvaluated, myFunctionArgs, myFunctionKwargs)

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
		if (isinstance(color[0], (tuple, list))):
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
		if (color is None):
			color = wx.Colour(0, 0, 0)
			style, image = self.getBrushStyle("transparent", None)
			brush = wx.Brush(color, style)

		else:
			#Account for brush lists
			multiple = [False, False]
			if (isinstance(color, (tuple, list)) and isinstance(color[0], (tuple, list))):
				multiple[0] = True

			if (isinstance(style, (tuple, list))):
				multiple[1] = True

			#Create a brush list
			if (multiple[0] or multiple[1]):
				brushList = []
				for i, item in enumerate(color):
					#Determine color
					if (multiple[0]):
						#Account for void color
						if (color[i] is not None):
							color = wx.Colour(color[i][0], color[i][1], color[i][2])
						else:
							color = wx.Colour(0, 0, 0)
					else:
						#Account for void color
						if (color is not None):
							color = wx.Colour(color[0], color[1], color[2])
						else:
							color = wx.Colour(0, 0, 0)

					#Determine style
					if (multiple[1]):
						#Account for void color
						if (color[i] is not None):
							style, image = self.getBrushStyle(style[i], image)
						else:
							style, image = self.getBrushStyle("transparent", None)
					else:
						#Account for void color
						if (color is not None):
							style, image = self.getBrushStyle(style, image)
						else:
							style, image = self.getBrushStyle("transparent", None)

					#Create bruh
					brush = wx.Brush(color, style)

					#Bind image if an image style was used
					if (image is not None):
						brush.SetStipple(image)

					#Remember the brush
					brushList.append(brush)
				brush = brushList

			#Create a single brush
			else:
				#Account for void color
				if (color is not None):
					#Create brush
					color = wx.Colour(color[0], color[1], color[2])
					style, image = self.getBrushStyle(style, image)
				else:
					color = wx.Colour(0, 0, 0)
					style, image = self.getBrushStyle("transparent", None)
				brush = wx.Brush(color, style)

				#Bind image if an image style was used
				if (image is not None):
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
		if (style is not None):
			style = style.lower()

		#Normal
		if (style is None):
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
			if (image is not None):
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

		if (self.thing is None):
			errorMessage = f"A panel was not created because 'panel' was None upon creation for {self.__repr__()}"
			raise ValueError(errorMessage)

		#Scale the canvas
		if (x is not None):
			if (y is not None):
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

		if (self.thing is None):
			errorMessage = f"A panel was not created because 'panel' was None upon creation for {self.__repr__()}"
			raise ValueError(errorMessage)

		#Skip empty origins
		if (x is not None):
			#Move the origin
			if (y is not None):
				self._queue("self.thing.SetDeviceOrigin", [x, y])
			else:
				self._queue("self.thing.SetDeviceOrigin", [x, x])

	def drawRotate(self, angle = 0, center = (0, 0)):
		"""Rotates what is drawn by the given angle about the given point.

		angle (int) - How far to rotate in degrees

		Example: drawRotate(90)
		"""

		def rotateFunction(dc):
			nonlocal self, angle, center

			image = self.getCanvasImage()
			image.Rotate(angle, center)
			tempDC = wx.MemoryDC(image.ConvertToBitmap())
			boundingBox = tempDC.GetBoundingBox()

			dc.Clear()
			dc.Blit(0, 0, boundingBox[2], boundingBox[3], tempDC, boundingBox[0], boundingBox[1])

		self._queue(rotateFunction, includeDC = True)
			
	def drawImage(self, imagePath, x = None, y = None, scale = None, internal = False, alpha = False, rotate = None):
		"""Draws an image on the canvas.

		imagePath (str) - The pathway to the image
		x (int)         - The x-coordinate of the image on the canvas
		y (int)         - The y-coordinate of the image on the canvas
		scale (float)   - What percentage to scale the image at
			- If None: Will not scale the image
			- If tuple: (x scale (float), y scale (float))
			- If int: Will overwrite the current width and height

		Example Input: drawImage("python.jpg")
		Example Input: drawImage("python.jpg", 10, 10)
		Example Input: drawImage("python.jpg", (10, 10))
		Example Input: drawImage("python.jpg", scale = 2.0)
		Example Input: drawImage("python.jpg", scale = (0.5, 1.0))
		Example Input: drawImage("python.jpg", scale = (36, 36))
		"""

		#Skip blank images
		if (imagePath is not None):
			#Get correct image
			image = self.getImage(imagePath, internal, alpha = alpha, scale = scale, rotate = rotate)

			if (x is None):
				x = 0
			elif (isinstance(x, str)):
				x = ast.literal_eval(re.sub("^['\"]|['\"]$", "", x))

			if (y is None):
				if (isinstance(x, (list, tuple))):
					y = x[1]
					x = x[0]
				else:
					y = 0
			elif (isinstance(y, str)):
				y = ast.literal_eval(re.sub("^['\"]|['\"]$", "", y))

			#Draw the image
			self._queue("dc.DrawBitmap", [image, x, y, alpha])

	def drawText(self, text, x = 0, y = 0, size = 12, angle = None, x_offset = 0, y_offset = 0,
		color = (0, 0, 0), bold = False, italic = False, family = None,
		wrap = None, align = None, x_align = None, y_align = None):
		"""Draws text on the canvas.
		Special thanks to Milan Skala for how to center text on http://wxpython-users.1045709.n5.nabble.com/Draw-text-over-an-existing-bitmap-td5725527.html

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

		wrap (int)    - How far to draw the text until; it wraps back at 'x'
			- If rect or tuple: Will use the width of the given rectangle
			- If None or 0: Will not wrap the text

		align (tuple) - How far from (0, 0) to consider the bottom right corner

		x_align (str) - Where the text should be aligned in the cell
			~ "left", "right", "center"
			- If None: No alignment will be done
			- Note: Must define 'align' to use

		y_align (str) - Where the button should be aligned with respect to the x-axis in the cell
			~ "top", "bottom", "center"
			- If None: Will use "center"
			- Note: Must define 'align' to use

		Example Input: drawText("Lorem Ipsum")
		Example Input: drawText("Lorem Ipsum", 5, 5)
		Example Input: drawText("Lorem Ipsum", 5, 5, 10)
		Example Input: drawText("Lorem Ipsum", 5, 5, 10, 45)
		Example Input: drawText("Lorem Ipsum", 5, 5, color = (255, 0, 0))

		Example Input: drawText("Lorem Ipsum", wrap = 10)
		Example Input: drawText("Lorem Ipsum", wrap = (0, 10, 275, 455))
		Example Input: drawText("Lorem Ipsum", align = (0, 10, 275, 455), x_align = "center")
		Example Input: drawText("Lorem Ipsum", align = (0, 10, 275, 455), x_align = "center", angle = 90)
		"""

		if ((wrap is not None) and (not isinstance(wrap, int))):
			wrap = wx.Rect(wrap)
		if (wrap):
			dc = self._getDC()
			dc.SetFont(font)
			if (isinstance(wrap, int)):
				_text = wx.lib.wordwrap.wordwrap(text, dc.DeviceToLogicalX(wrap), dc)
			else:
				_text = wx.lib.wordwrap.wordwrap(text, dc.DeviceToLogicalX(wrap[2] - wrap[0]), dc)
		else:
			_text = text

		font = self.getFont(size = size, bold = bold, italic = italic, family = family)
		self._queue("dc.SetFont", font)

		pen = self.getPen(color)
		self._queue("dc.SetPen", pen)

		if (align is not None):
			align = wx.Rect(align)
		if (angle in [None, 0]):
			if (x_align is None):
				x_align = 0
			else:
				x_align = {"l": wx.ALIGN_LEFT, "r": wx.ALIGN_RIGHT, "c": wx.ALIGN_CENTER_HORIZONTAL}[x_align[0].lower()]

			if (y_align is None):
				y_align = wx.ALIGN_TOP
			else:
				y_align = {"t": wx.ALIGN_TOP, "b": wx.ALIGN_BOTTOM, "c": wx.ALIGN_CENTER_VERTICAL}[y_align[0].lower()]
		else:
			dc = self._getDC()
			dc.SetFont(font)
			width, height = dc.GetTextExtent(_text)

			if (x_align in [None, "l"]):
				x_align = 0
				if (angle >= 270):
					x_offset += height
				elif (angle >= 180):
					x_offset += width
				elif (angle >= 90):
					x_offset += 0
				else:
					x_offset += 0

			elif (x_align == "r"):
				x_align = align.width - width
				if (angle >= 270):
					x_offset += width
				elif (angle >= 180):
					x_offset += width
				elif (angle >= 90):
					x_offset += width - height
				else:
					x_offset += 0
			else:
				x_align = (align.width - width) / 2
				if (angle >= 270):
					x_offset += width / 2 + height / 2
				elif (angle >= 180):
					x_offset += width
				elif (angle >= 90):
					x_offset += width / 2 - height / 2
				else:
					x_offset += 0

			if (y_align in [None, "t"]):
				y_align = 0
				if (angle >= 270):
					y_offset += 0
				elif (angle >= 180):
					y_offset += height
				elif (angle >= 90):
					y_offset += width
				else:
					y_offset += 0

			elif (y_align == "b"):
				y_align = align.height - height
				if (angle >= 270):
					y_offset += -width + height
				elif (angle >= 180):
					y_offset += height
				elif (angle >= 90):
					y_offset += height
				else:
					y_offset += 0
			else:
				y_align = (align.height - height) / 2
				if (angle >= 270):
					y_offset += -width / 2 + height / 2
				elif (angle >= 180):
					y_offset += height
				elif (angle >= 90):
					y_offset += width / 2 + height / 2
				else:
					y_offset += 0

		if ((angle is not None) and (angle != 0)):
			self._queue("dc.DrawRotatedText", [_text, x + x_align + x_offset, y + y_align + y_offset, angle])
		elif (align is not None):
			self._queue("dc.DrawLabel", [_text, (x, y, align[2], align[3]), x_align|y_align])
		else:
			self._queue("dc.DrawText", [_text, x + x_offset + y_offset, y])

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
		if (isinstance(x, (tuple, list))):
			self._queue("dc.DrawPointList", [x, pen])
		else:
			self._queue("dc.SetPen", pen)
			self._queue("dc.DrawPoint", [x, y])

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
		if (isinstance(x1, (tuple, list))):
			#Determine input type
			if (isinstance(x1[0], (tuple, list))):
				#Type [(x1, y1), (x2, y2)]
				lines = [(item[0][0], item[0][1], item[1][0], item[1][1]) for item in x] #Leaf coordinates correctly
			else:
				#Type (x1, y1, x2, y2)
				lines = x1

			#Draw lines
			self._queue("dc.DrawLineList", [lines, pen])
		else:
			self._queue("dc.SetPen", pen)
			self._queue("dc.DrawLine", [x1, y1, x2, y2])

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
				self._queue("dc.DrawSpline", spline)
		else:
			self._queue("dc.SetPen", pen)
			self._queue("dc.DrawSpline", points)

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
					self._queue("dc.SetPen", pen)
				else:
					self._queue("dc.SetPen", pen[i])

				if (type(brush) != list):
					self._queue("dc.SetBrush", brush)
				else:
					self._queue("dc.SetBrush", brush[i])

				#Determine height and width
				if (height is not None):
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
				self._queue("dc.DrawEllipticArc", [item[0], item[1], arcWidth, arcHeight, arcStart, arcEnd])
		else:
			if (height is None):
				height = width

			self._queue("dc.SetPen", pen)
			self._queue("dc.SetBrush", brush)
			self._queue("dc.DrawEllipticArc", [x, y, width, height, start, end])

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
					self._queue("dc.SetPen", pen)
				else:
					self._queue("dc.SetPen", pen[i])

				#Determine height and width
				if (height is not None):
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
				self._queue("dc.DrawCheckMark", [item[0], item[1], checkMarkWidth, checkMarkHeight])
		else:
			#Draw the line
			if (height is None):
				height = width

			self._queue("dc.SetPen", pen)
			self._queue("dc.DrawCheckMark", [x, y, width, height])

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
			if (radius is not None):
				#Create rounded rectangles
				for i, item in enumerate(x):
					#Setup colors
					if ((type(pen) != list) and (type(pen) != tuple)):
						self._queue("dc.SetPen", pen)
					else:
						self._queue("dc.SetPen", pen[i])

					if (type(brush) != list):
						self._queue("dc.SetBrush", brush)
					else:
						self._queue("dc.SetBrush", brush[i])

					#Determine height and width
					if (height is not None):
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
					self._queue("dc.DrawRoundedRectangle", [item[0], item[1], width, height, radius])

			else:
				#Create non-rounded rectangle
				#Determine height and width
				if ((type(width) != list) and (type(width) != tuple)):
					width = [width for item in x]

				if (height is not None):
					if ((type(height) != list) and (type(height) != tuple)):
						height = [height for item in x]
				else:
					height = [width[i] for i in range(len(x))]

				#Configure correct arg format
				rectangles = [(item[0][0], item[0][1], width[i], height[i]) for i, item in enumerate(x)] #Leaf coordinates correctly

				#Draw Rectangle
				self._queue("dc.DrawRectangleList", [rectangles, pen, brush])
		else:

			#Draw the rectangle
			if (height is None):
				height = width

			self._queue("dc.SetPen", pen)
			self._queue("dc.SetBrush", brush)

			if (radius is not None):
				self._queue("dc.DrawRoundedRectangle", [x, y, width, height, radius])
			else:
				self._queue("dc.DrawRectangle", [x, y, width, height])

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
			self._queue("dc.DrawPolygonList", [points, pen, brush])
		else:
			self._queue("dc.SetPen", pen)
			self._queue("dc.SetBrush", brush)
			self._queue("dc.DrawPolygon", [points, 0, 0, style])

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
					self._queue("dc.SetPen", pen)
				else:
					self._queue("dc.SetPen", pen[i])

				if (type(brush) != list):
					self._queue("dc.SetBrush", brush)
				else:
					self._queue("dc.SetBrush", brush[i])

				#Determine radius
				if ((type(radius) != list) and (type(radius) != tuple)):
					circleRadius = radius
				else:
					circleRadius = radius[i]

				#Draw the circle
				self._queue("dc.DrawCircle", [item[0], item[1], circleRadius])

		else:
			#Draw the circle
			self._queue("dc.SetPen", pen)
			self._queue("dc.SetBrush", brush)
			self._queue("dc.DrawCircle", [x, y, radius])

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

			if (height is not None):
				if ((type(height) != list) and (type(height) != tuple)):
					height = [height for item in x]
			else:
				height = [width[i] for i in range(len(x))]

			#Configure correct arg format
			ellipses = [(item[0][0], item[0][1], width[i], height[i]) for i, item in enumerate(x)] #Leaf coordinates correctly

			#Draw ellipse
			self._queue("dc.DrawEllipseList", [ellipses, pen, brush])
		else:

			#Draw the ellipse
			if (height is None):
				height = width

			self._queue("dc.SetPen", pen)
			self._queue("dc.SetBrush", brush)

			self._queue("dc.DrawEllipse", [x, y, width, height])

class handle_WidgetTable(handle_Widget_Base):
	"""A handle for working with table widgets.
	Use: https://stackoverflow.com/questions/46199205/using-pythons-wx-grid-how-can-you-merge-columns
	"""

	def __init__(self):
		"""Initializes defaults."""

		#Initialize inherited classes
		handle_Widget_Base.__init__(self)

		self.previousCell = (-1, -1)
		self.lastModifiedCell = (-1, -1)
		self.readOnlyCatalogue = {}
		self.cellTypeCatalogue = {}
		self.buttonPressCatalogue = {} #{row (int): column (int): {"press": if the button is currently pressed (bool), "ranFunction": If the button has been unpressed}}

	def __len__(self):
		"""Returns what the contextual length is for the object associated with this handle.

		returnRows(bool) - Determines what is returned for 2D objects
			- If True: Returns how many rows the object has
			- If False: Returns how many columns the object has
		"""

		if (self.type is Types.table):
			if (returnRows):
				value = self.thing.GetNumberRows()
			else:
				value = self.thing.GetNumberCols()

		else:
			warnings.warn(f"Add {self.type.name} to __len__() for {self.__repr__()}", Warning, stacklevel = 2)
			value = 0

		return value

	def _build(self, argument_catalogue):
		"""Determiens which build system to use for this handle."""

		def _build_table():
			"""Builds a wx grid object."""
			nonlocal self, argument_catalogue

			rows, columns, readOnly = self._getArguments(argument_catalogue, ["rows", "columns", "readOnly" ])
			showGrid, dragableColumns, dragableRows = self._getArguments(argument_catalogue, ["showGrid", "dragableColumns", "dragableRows"])
			rowSize, columnSize, autoSizeRow, autoSizeColumn = self._getArguments(argument_catalogue, ["rowSize", "columnSize", "autoSizeRow", "autoSizeColumn"])

			rowLabelSize, columnLabelSize = self._getArguments(argument_catalogue, ["rowLabelSize", "columnLabelSize"])
			rowSizeMinimum, columnSizeMinimum, rowSizeMaximum, columnSizeMaximum = self._getArguments(argument_catalogue, ["rowSizeMinimum", "columnSizeMinimum", "rowSizeMaximum", "columnSizeMaximum"])
			gridLabels, contents, default, enterKeyExitEdit = self._getArguments(argument_catalogue, ["gridLabels", "contents", "default", "enterKeyExitEdit"])
			toolTips, arrowKeyExitEdit, editOnEnter = self._getArguments(argument_catalogue, ["toolTips", "arrowKeyExitEdit", "editOnEnter"])

			preEditFunction, postEditFunction = self._getArguments(argument_catalogue, ["preEditFunction", "postEditFunction"])
			dragFunction, selectManyFunction, selectSingleFunction = self._getArguments(argument_catalogue, ["dragFunction", "selectManyFunction", "selectSingleFunction"])
			rightClickCellFunction, rightClickLabelFunction = self._getArguments(argument_catalogue, ["rightClickCellFunction", "rightClickLabelFunction"])

			readOnlyDefault, cellType, cellTypeDefault = self._getArguments(argument_catalogue, ["readOnlyDefault", "cellType", "cellTypeDefault"])
			
			#Remember Values
			self.rowSizeMaximum = rowSizeMaximum
			self.columnSizeMaximum = columnSizeMaximum

			#Create the thing to put in the grid
			self.thing = self._Table(self, self.parent.thing, style = wx.WANTS_CHARS)
			self.thing.SetDefaultCellAlignment(wx.ALIGN_LEFT, wx.ALIGN_TOP)
			self.thing.CreateGrid(rows, columns)

			#Grid Enabling
			if (readOnly is not None):
				if (readOnly):
					self.thing.EnableCellEditControl(False)
			if ((preEditFunction is not None) or (postEditFunction is not None)):
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

			if (columnSize is not None):
				if (isinstance(columnSize, dict)):
					for column, value in columnSize.items():
						self.thing.SetColSize(column, value)
				else:
					for i in range(nColumns):
						self.thing.SetColSize(i, columnSize)         

			if (rowLabelSize is not None):
				self.thing.SetRowLabelSize(rowLabelSize)

			if (columnLabelSize is not None):
				self.thing.SetColLabelSize(columnLabelSize)

			##Minimum Sizes
			if (rowSizeMinimum is not None):
				self.thing.SetRowMinimalAcceptableHeight(rowSizeMinimum)
			
			if (columnSizeMinimum is not None):
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
			if (contents is not None):
				for row in range(len(contents)):
					for column in range(len(contents[0])):
						self.thing.SetCellValue(row, column, contents[row][column])

			##Set Cell Type for Cells
			self.cellTypeCatalogue = {}
			self.enterKeyExitEdit = enterKeyExitEdit
			self.cellTypeDefault = cellTypeDefault
			self.setTableCellType()

			for column in range(self.thing.GetNumberCols()):
				for row in range(self.thing.GetNumberRows()):
					if (not isinstance(cellType, dict)):
						self.setTableCellType(cellType, row, column)
					else:
						if (row in cellType):
							if (isinstance(cellType[row], str)):
								#Define for whole row
								self.setTableCellType(cellType[row], row, column)
							else:
								if (column in cellType[row]):
									#Define for individual cell
									self.setTableCellType(cellType[row][column], row, column)
				
				if (isinstance(cellType, dict)):
					if (None in cellType):
						if (column in cellType[None]):
							#Define for whole column
							self.setTableCellType(cellType[None][column], None, column)

			##Set Editability for Cells
			self.readOnlyCatalogue = {}
			self.readOnlyDefault = readOnlyDefault
			self.disableTableEditing(state = readOnly)
			for row in range(self.thing.GetNumberRows()):
				for column in range(self.thing.GetNumberCols()):
					if (row not in self.readOnlyCatalogue):
						self.readOnlyCatalogue[row] = {}
					if (column not in self.readOnlyCatalogue[row]):
						self.readOnlyCatalogue[row][column] = {}
					
					if (readOnly is not None):
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

			##Default Cell Selection
			if ((default is not None) and (default != (0, 0))):
				self.thing.GoToCell(default[0], default[1])

			#Bind the function(s)
			if (preEditFunction is not None):
				preEditFunctionArgs, preEditFunctionKwargs = self._getArguments(argument_catalogue, ["preEditFunctionArgs", "preEditFunctionKwargs"])
				self.setFunction_preEdit(preEditFunction, preEditFunctionArgs, preEditFunctionKwargs)

			self.setFunction_postEdit(self.setTableLastModifiedCell)
			if (postEditFunction is not None):
				postEditFunctionArgs, postEditFunctionKwargs = self._getArguments(argument_catalogue, ["postEditFunctionArgs", "postEditFunctionKwargs"])
				self.setFunction_postEdit(postEditFunction, postEditFunctionArgs, postEditFunctionKwargs)
			
			if (dragFunction is not None):      
				dragFunctionArgs, dragFunctionKwargs = self._getArguments(argument_catalogue, ["dragFunctionArgs", "dragFunctionKwargs"])
				self.setFunction_drag(dragFunction, dragFunctionArgs, dragFunctionKwargs)

			self.setFunction_selectMany(self.setTablePreviousCell)
			if (selectManyFunction is not None):
				selectManyFunctionArgs, selectManyFunctionKwargs = self._getArguments(argument_catalogue, ["selectManyFunctionArgs", "selectManyFunctionKwargs"])
				self.setFunction_selectMany(selectManyFunction, selectManyFunctionArgs, selectManyFunctionKwargs)

			self.setFunction_selectSingle(self.setTablePreviousCell)
			if (selectSingleFunction is not None):
				selectSingleFunctionArgs, selectSingleFunctionKwargs = self._getArguments(argument_catalogue, ["selectSingleFunctionArgs", "selectSingleFunctionKwargs"])
				self.setFunction_selectSingle(selectSingleFunction, selectSingleFunctionArgs, selectSingleFunctionKwargs)
			
			if (rightClickCellFunction is not None):
				rightClickCellFunctionArgs, rightClickCellFunctionKwargs = self._getArguments(argument_catalogue, ["rightClickCellFunctionArgs", "rightClickCellFunctionKwargs"])
				self.setFunction_rightClickCell(rightClickCellFunction, rightClickCellFunctionArgs, rightClickCellFunctionKwargs)

			if (rightClickLabelFunction is not None):
				rightClickLabelFunctionArgs, rightClickLabelFunctionKwargs = self._getArguments(argument_catalogue, ["rightClickLabelFunctionArgs", "rightClickLabelFunctionKwargs"])
				self.setFunction_rightClickLabel(rightClickLabelFunction, rightClickLabelFunctionArgs, rightClickLabelFunctionKwargs)

			if (toolTips is not None):
				self._betterBind(wx.EVT_MOTION, self.thing, self._onTableDisplayToolTip, toolTips)

			if (arrowKeyExitEdit):
				self._betterBind(wx.EVT_KEY_DOWN, self.thing, self._onTableArrowKeyMove, mode = 2)

			if (editOnEnter):
				self._betterBind(wx.EVT_KEY_DOWN, self.thing.GetGridWindow(), self._onTableEditOnEnter, mode = 2)

			self._betterBind(wx.EVT_SIZE, self.myWindow.thing, self._onTableAutoSize, mode = 2)

			self._betterBind(wx.EVT_LEFT_DOWN, self.thing.GetGridWindow(), self._onTableButton, True, mode = 2)
			self._betterBind(wx.EVT_LEFT_UP, self.thing.GetGridWindow(), self._onTableButton, False, mode = 2)
			self._betterBind(wx.EVT_KILL_FOCUS, self.thing.GetGridWindow(), self._onTableButton, False, mode = 2)

		#########################################################

		self._preBuild(argument_catalogue)

		if (self.type is Types.table):
			_build_table()
		else:
			warnings.warn(f"Add {self.type.name} to _build() for {self.__repr__()}", Warning, stacklevel = 2)

		self._postBuild(argument_catalogue)

	#Getters
	def getValue(self, row = None, column = None, event = None):
		"""Returns what the contextual value is for the object associated with this handle."""

		if (self.type is Types.table):
			if ((row is None) or (column is None)):
				value = []
				selection = self.getTableCurrentCell(event = event)
				for _row, _column in selection:
					value.append(self.getTableCellValue(_row, _column)) #(list) - What is in the selected cells
			else:
				value = self.getTableCellValue(row, column) #(str) - What is in the requested cell
		else:
			warnings.warn(f"Add {self.type.name} to getValue() for {self.__repr__()}", Warning, stacklevel = 2)
			value = None

		return value

	def getAll(self):
		"""Returns all the contextual values for the object associated with this handle."""

		if (self.type is Types.table):
			value = []
			for _row in range(self.thing.GetNumberRows()):
				row = []
				for _column in range(self.thing.GetNumberCols()):
					row.append(self.getTableCellValue(_row, _column)) #(list) - What is in each cell
				value.append(row)

		else:
			warnings.warn(f"Add {self.type.name} to getAll() for {self.__repr__()}", Warning, stacklevel = 2)
			value = None

		return value

	#Change Settings
	def setFunction_click(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		self.setFunction_selectSingle(myFunction = myFunction, myFunctionArgs = myFunctionArgs, myFunctionKwargs = myFunctionKwargs)

	def setFunction_rightClick(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		self.setFunction_rightClickCell(myFunction = myFunction, myFunctionArgs = myFunctionArgs, myFunctionKwargs = myFunctionKwargs)

	def setFunction_preEdit(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		self._betterBind(wx.grid.EVT_GRID_CELL_CHANGING, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)

	def setFunction_postEdit(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		self.thing.EnableEditing(True)
		self._betterBind(wx.grid.EVT_GRID_CELL_CHANGED, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)

	def setFunction_drag(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		self._betterBind(wx.grid.EVT_GRID_COL_SIZE, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		self._betterBind(wx.grid.EVT_GRID_ROW_SIZE, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)

	def setFunction_selectMany(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		self._betterBind(wx.grid.EVT_GRID_RANGE_SELECT, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)

	def setFunction_selectSingle(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		self._betterBind(wx.grid.EVT_GRID_SELECT_CELL, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)

	def setFunction_rightClickCell(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		self._betterBind(wx.grid.EVT_GRID_CELL_RIGHT_CLICK, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)

	def setFunction_rightClickLabel(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		self._betterBind(wx.grid.EVT_GRID_LABEL_RIGHT_CLICK, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)

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
				self.thing.DeleteCols(number - 1, current - number)

			self.thing.ForceRefresh()
			self._onTableAutoSize()

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
			self._onTableAutoSize()

	def setMaximumRowSize(self, row, size = -1):
		self.rowSizeMaximum[row] = size

	def setMinimumRowSize(self, row, size = -1):
		self.rowSizeMinimum[row] = size

	def setMaximumColumnSize(self, column, size = -1):
		self.columnSizeMaximum[column] = size

	def setMinimumColumnSize(self, column, size = -1):
		self.columnSizeMinimum[column] = size

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
		if (size is None):
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
			if ((row in self.rowSizeMaximum) and (self.rowSizeMaximum[row]) is not None):
				if (value > self.rowSizeMaximum[row]):
					size[row] = self.rowSizeMaximum[row]

		#Modify Size
		for row in range(self.thing.GetNumberRows()):
			self.thing.SetRowSize(row, size[None])

		for row, value in size.items():
			if (row is not None):
				if (value is None):
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
		if (size is None):
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
			if ((column in self.columnSizeMaximum) and (self.columnSizeMaximum[column]) is not None):
				if (value > self.columnSizeMaximum[column]):
					size[column] = self.columnSizeMaximum[column]

		#Modify Size
		for column in range(self.thing.GetNumberCols()):
			self.thing.SetColSize(column, size[None])

		for column, value in size.items():
			if (column is not None):
				if (value is None):
					value = default
				self.thing.SetColSize(column, value)

		#Remember Values
		self.columnSize = size
		self.autoSizeColumn = autoSize

	def setTableLastModifiedCell(self, row = None, column = None, event = None):
		"""Sets the internal last modified cell to the specified value.
		If 'row' and 'column' are None, it will take the current cell.

		Example Input: setTableLastModifiedCell()
		Example Input: setTableLastModifiedCell(1, 2)
		"""

		if ((row is not None) and (column is not None)):
			self.lastModifiedCell = (row, column)
		else:
			self.lastModifiedCell = self.getTableCurrentCell(event = event)[0]

	def getTableLastModifiedCell(self):
		"""Returns the last modified cell coordinates.

		Example Input: getTableLastModifiedCell()
		"""

		return self.lastModifiedCell

	def setTablePreviousCell(self, row = None, column = None, event = None):
		"""Sets the internal previous cell to the specified value.
		If 'row' and 'column' are None, it will take the current cell.

		Example Input: setTableLastModifiedCell()
		Example Input: setTableLastModifiedCell(1, 2)
		"""

		if ((row is not None) and (column is not None)):
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

	def enableTableEditing(self, row = None, column = None, state = True):
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

		Example Input: enableTableEditing()
		Example Input: enableTableEditing(row = 0)
		Example Input: enableTableEditing(column = 0)
		Example Input: enableTableEditing(row = 0, column = 0)
		"""

		if (state is None):
			newState = state
		elif (isinstance(state, bool)):
			newState = not state
		elif (isinstance(state, dict)):
			newState = {}
			for key, value in state.items():
				if (not isinstance(value, dict)):
					if (state is None):
						newState[key] = value
					else:
						newState[key] = not value
				else:
					if (key not in newState):
						newState[key] = {}
					for subKey, subValue in value.items():
						if (not isinstance(subValue, dict)):
							if (subValue is None):
								newState[key][subKey] = subValue
							else:
								newState[key][subKey] = not subValue
		else:
			errorMessage = f"'state' must be a bool or a dict, not {type(state)} for enableTableEditing() in {self.__repr__()}"
			raise KeyError(errorMessage)

		self.disableTableEditing(row = row, column = column,  state = newState)

	def disableTableEditing(self, row = None, column = None, state = True):
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

		Example Input: disableTableEditing()
		Example Input: disableTableEditing(row = 0)
		Example Input: disableTableEditing(column = 0)
		Example Input: disableTableEditing(row = 0, column = 0)
		"""

		def _modifyReadonly(state, row = None, column = None):
			"""Modifies the readOnly catalogue

			state (str)  - Determines the editability of the table
			row (int)    - Which row to add this to
				- If None: Will apply to all rows
			column (int) - Which column to add this to
				- If None: Will apply to all columns

			Example Input: _modifyReadonly(state[_row][_column], _row, _column)
			"""
			nonlocal self

			#Determine affected cells
			rowList = range(self.thing.GetNumberRows()) if (row is None) else [row]
			columnList = range(self.thing.GetNumberCols()) if (column is None) else [column]

			#Apply readOnly
			for _row in rowList:
				if (_row not in self.readOnlyCatalogue):
					self.readOnlyCatalogue[_row] = {}
				for _column in columnList:
					self.readOnlyCatalogue[_row][_column] = state
			
		#########################################################

		if (state is None):
			state = self.readOnlyDefault

		if (row is None):
			row = range(self.thing.GetNumberRows())
		elif (not isinstance(row, (list, tuple, range))):
			row = [row]
		
		if (column is None):
			column = range(self.thing.GetNumberCols())
		elif (not isinstance(column, (list, tuple, range))):
			column = [column]
		
		for _row in row:
			for _column in column:
				if (not isinstance(state, dict)):
					_modifyReadonly(state, _row, _column)
				else:
					if (_row in state):
						if (isinstance(state[_row], str)):
							#Define for whole row
							_modifyReadonly(state[_row], _row, _column)
						else:
							if (_column in state[_row]):
								#Define for individual cell or whole column if _row is None
								_modifyReadonly(state[_row][_column], _row, _column)

	def getTableReadOnly(self, row, column):
		"""Returns if the given cell is readOnly or not.
		The top-left corner is cell (0, 0) not (1, 1).

		row (int)         - The index of the row
		column (int)      - The index of the column

		Example Input: getTableReadOnly(1, 1)
		"""

		if ((row not in self.readOnlyCatalogue) or (column not in self.readOnlyCatalogue[row])):
			return False

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

		cellType (dict) - {None: keyword (str), **kwargs}
			- Can be a string that applies to the given row and column
			- If None: will apply the default cell type
			- Possible Inputs: 
				~ "inputBox"
				~ "dropList", {"choices": list contents (list), "endOnSelect": if focus should be lost after a selection is made (bool)}
					~ Defaults: {"choices": [], "endOnSelect": True}

				~ "dialog", {"myFrame": dialog window name (str) or dialog window handle (handle_Window), "label": The label fo the custom dialog (str)}
					~ Must supply valid "myFrame"

				~ "button", {"text": None, "myFunction": (function), "myFunctionArgs": (list), "myFunctionKwargs": (dict)}
					~ Defaults: {"text": None, "myFunction": None, "myFunctionArgs": None, "myFunctionKwargs": None}
				
				~ str

				~ int, {"minimum": (int), "maximum": (int)}
					~ Defaults: {"minimum": -1, "maximum": -1}
					~ Use a -1 to ignore min or max

				~ float, {"minimum": (float), "maximum": (float), "scientific": if e+ notation should be used (bool)}
					~ Defaults: {"minimum": -1, "maximum": -1, "scientific": False}
					~ Use a -1 to ignore min or max

				~ bool, {"showCheck": (bool)}
					~ Defaults: {"showCheck": True}
					~ If showCheck is True: Will show a check box instead of a number after and during editing
					~ If showCheck is False: Will show a check box instead of a number after editing
					~ If showCheck is None: Will show not show a check box, but numbers only

		row (int)    - Which row to apply this cell type to. Can be a list. Must be in the dict for 'cellType' or 'cellType' must be a string
		column (int) - Which column to apply this cell type to. Can be a list. Must be in the dict for 'cellType' or 'cellType' must be a string

		Example Input: setTableCellType()
		Example Input: setTableCellType({None: "dropList", ["a", "b", "c"]})
		Example Input: setTableCellType({None: "dropList", ["a", "b", "c"]}, column = 1)
		Example Input: setTableCellType({None: "dropList", ["a", "b", "c"]}, row = [1, 2, 5])
		Example Input: setTableCellType({None: {1: {None: "dropList", "choices": ["a", "b", "c"]}}})
		Example Input: setTableCellType({2: 1: {None: "dropList", "choices": ["a", "b", "c"]}}})
		Example Input: setTableCellType({None: "dialog", "myFrame": modifyBarcode"}])
		"""

		def _configureCellType(cellType, row = None, column = None):
			"""Makes the cell type into a standard form."""
			nonlocal self

			#Ensure cellType is structured correctly
			if (isinstance(cellType, dict)):
				if (None not in cellType):
					errorMessage = f"The key word for the cell type must have the dictionary key None for {self.__repr__()}"
					raise KeyError(errorMessage)
			else:
				cellType = {None: cellType}

			#Error Checking
			if (isinstance(cellType[None], str)):
				if (cellType[None].lower() not in ["inputbox", "droplist", "dialog", "button"]):
					errorMessage = f"Unknown cell type {cellType[None]} in {self.__repr__()}\ncellType: {cellType}"
					raise KeyError(errorMessage)
			elif (cellType[None] not in [str, int, float, bool]):
				errorMessage = f"Unknown cell type {cellType[None]} in {self.__repr__()}\ncellType: {cellType}"
				raise KeyError(errorMessage)

			#Apply Defaults
			if (isinstance(cellType[None], str)):
				if (cellType[None].lower() == "droplist"):
					cellType.setdefault("choices", [])
					cellType.setdefault("endOnSelect", True)
				
				elif (cellType[None].lower() == "button"):
					cellType.setdefault("text", None)
					cellType.setdefault("myFunction", None)
					cellType.setdefault("myFunctionArgs", None)
					cellType.setdefault("myFunctionKwargs", None)

				elif (cellType[None].lower() == "dialog"):
					cellType.setdefault("label", None)
			else:
				if (cellType[None] == int):
					cellType.setdefault("minimum", -1)
					cellType.setdefault("maximum", -1)

				elif (cellType[None] == float):
					cellType.setdefault("minimum", -1)
					cellType.setdefault("maximum", -1)
					cellType.setdefault("scientific", False)

				elif (cellType[None] == bool):
					cellType.setdefault("showCheck", True)

			#Create editor and/or renderer if needed
			if (str(cellType) not in self.cellTypeCatalogue):
				if (cellType[None] is None):
					self.cellTypeCatalogue[str(cellType)] = [self.thing.GetDefaultRenderer(), self.thing.GetDefaultEditor()]
				elif (isinstance(cellType[None], str) and (cellType[None].lower() in ["button"])):
					self.cellTypeCatalogue[str(cellType)] = [self._TableCellRenderer(self, cellType = cellType)]

				elif (isinstance(cellType[None], type) and (cellType[None] in [str, int, float, bool])):
					if (cellType[None] == str):
						self.cellTypeCatalogue[str(cellType)] = [wx.grid.GridCellStringRenderer(), wx.grid.GridCellTextEditor()]

					elif (cellType[None] == int):
						self.cellTypeCatalogue[str(cellType)] = [wx.grid.GridCellNumberRenderer(), wx.grid.GridCellNumberEditor(min = cellType["minimum"], max = cellType["maximum"])]
					
					elif (cellType[None] == float):
						if (cellType["scientific"]):
							self.cellTypeCatalogue[str(cellType)] = [self.thing.GetDefaultRenderer(), wx.grid.GridCellFloatEditor(min = cellType["minimum"], max = cellType["maximum"])]
						else:
							self.cellTypeCatalogue[str(cellType)] = [wx.grid.GridCellFloatRenderer(), wx.grid.GridCellFloatEditor(min = cellType["minimum"], max = cellType["maximum"])]

					else:
						if (cellType["showCheck"] is not None):
							if (cellType["showCheck"]):
								self.cellTypeCatalogue[str(cellType)] = [wx.grid.GridCellBoolRenderer(), wx.grid.GridCellBoolEditor()]
							else:
								self.cellTypeCatalogue[str(cellType)] = [wx.grid.GridCellBoolRenderer(), self.thing.GetDefaultEditor()]
						else:
							self.cellTypeCatalogue[str(cellType)] = [self.thing.GetDefaultRenderer(), wx.grid.GridCellBoolEditor()]
				else:
					self.cellTypeCatalogue[str(cellType)] = [self.thing.GetDefaultRenderer(), self._TableCellEditor(self, downOnEnter = self.enterKeyExitEdit, cellType = cellType)]

			# #Change settings if needed
			# rowList = range(self.thing.GetNumberRows()) if (row is None) else [row]
			# columnList = range(self.thing.GetNumberCols()) if (column is None) else [column]
			# for _row in rowList:
			#   for _column in columnList:
			#       if (isinstance(cellType[None], str) and (cellType[None].lower() in ["button"])):
			#           if (not self.thing.IsReadOnly(_row, _column)):
			#               self.thing.SetReadOnly(_row, _column, True)
			#       else:
			#           readOnly = self.getTableReadOnly(_row, _column)
			#           if (self.thing.IsReadOnly(_row, _column) != readOnly):
			#               self.thing.SetReadOnly(_row, _column, readOnly)

			return cellType

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

			#Housekeeping for cell types
			cellType = _configureCellType(cellType, row, column)

			#Determine affected cells
			if ((row is None) and (column is None)):
				for item in self.cellTypeCatalogue[str(cellType)]:
					if (isinstance(item, wx.grid.GridCellRenderer)):
						self.thing.SetDefaultRenderer(item)
					else:
						self.thing.SetDefaultEditor(item)

			rowList = range(self.thing.GetNumberRows()) if (row is None) else [row]
			columnList = range(self.thing.GetNumberCols()) if (column is None) else [column]

			#Assign editor to grid
			for _row in rowList:
				for _column in columnList:
					for item in self.cellTypeCatalogue[str(cellType)]:
						if (isinstance(item, wx.grid.GridCellRenderer)):
							self.thing.SetCellRenderer(_row, _column, item)
						else:
							self.thing.SetCellEditor(_row, _column, item)

			#Increment the reference variable for managing clones
			for item in self.cellTypeCatalogue[str(cellType)]:
				# if (isinstance(item, wx.grid.GridCellRenderer)):
				item.IncRef()
			
		#########################################################   

		if (cellType is None):
			cellType = self.cellTypeDefault
		if (not isinstance(row, (list, tuple, range))):
			row = [row]
		if (not isinstance(column, (list, tuple, range))):
			column = [column]

		for _row in row:
			for _column in column:
				addEditor(cellType, _row, _column)

	def clearTable(self):
		"""Clears all cells in the table

		Example Input: clearTable()
		"""
		
		self.thing.ClearGrid()

	def setTableCursor(self, row, column, ensureVisible = True):
		"""Moves the table highlight cursor to the given cell coordinates
		The top-left corner is cell (0, 0) not (1, 1).

		row (int)         - The index of the row
		column (int)      - The index of the column

		Example Input: setTableCursor(1, 2)
		"""

		#Set the cell value
		self.thing.GoToCell(row, column)
		self.thing.SetGridCursor(row, column)

		if (ensureVisible):
			self.thing.MakeCellVisible(row, column)

	def getTableCursor(self, event = None):
		"""Returns the loaction of the table highlight cursor.
		The top-left corner is cell (0, 0) not (1, 1).

		Example Input: getTableCursor()
		"""

		if (isinstance(event, wx.grid.GridEvent)):
			row = event.GetRow()
			column = event.GetCol()
		else:
			row = self.thing.GetGridCursorRow()
			column = self.thing.GetGridCursorCol()

		return (row, column)

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
		if (value is None):
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
		if (listContents is None):
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

		if ((row == -1) or (column == -1)):
			return None #Nothing Selected

		if ((row is None) and (column is None)):
			value = []
			for i in range(self.thing.GetNumberRows()):
				for j in range(self.thing.GetNumberCols()):
					#Get the cell value
					value.append(self.thing.GetCellValue(i, j))
			return None

		#Account for entire row or column request
		if ((row is not None) and (column is not None)):
			#Get the cell value
			value = self.thing.GetCellValue(row, column)

		elif (row is None):
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

	def getTableCurrentCellRow(self, event = None):
		"""Returns the row of the currently selected cells.

		Example Inputs: getTableCurrentCellRow()
		"""

		selection = self.getTableCurrentCell(event = event)
		rowList = self._removeDuplicates([row for row, column in selection])
		return rowList

	def getTableCurrentCellColumn(self, event = None):
		"""Returns the column of the currently selected cells.

		Example Inputs: getTableCurrentCellColumn()
		"""

		selection = self.getTableCurrentCell(event = event)
		columnList = self._removeDuplicates([column for row, column in selection])
		return columnList

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

		if (row is None):
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

		if (column is None):
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

		if (row is None):
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

		if (column is None):
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

	def setTableCellColor(self, row = None, column = None, color = None, textColor = None):
		"""Changes the color of the background of a cell.
		The top-left corner is cell (0, 0) not (1, 1).
		If both 'row' and 'column' are None, the entire table will be colored
		Special thanks to  for how to apply changes to the table on https://stackoverflow.com/questions/14148132/wxpython-updating-grid-cell-background-colour

		row (int)     - The index of the row
			- If None: Will color all cells of the column if 'column' is not None
		column (int)  - The index of the column
			- If None: Will color all cells of the column if 'column' is not None
		color (tuple) - What color to use. (R, G, B). Can be a string for standard colors
			- If None: Use the default wxPython background color

		Example Input: setTableCellColor()
		Example Input: setTableCellColor(1, 2, (255, 0, 0))
		Example Input: setTableCellColor(1, 2, "red")
		"""

		if (color is None):
			color = self.thing.GetDefaultCellBackgroundColour()
		else:
			color = self.getColor(color)

		if (textColor is None):
			textColor = self.thing.GetDefaultCellTextColour()
		else:
			textColor = self.getColor(textColor)

		if ((row is None) and (column is None)):
			for i in range(self.thing.GetNumberRows()):
				for j in range(self.thing.GetNumberCols()):
					#Color the cell
					self.thing.SetCellBackgroundColour(i, j, color)
					self.thing.SetCellTextColour (i, j, textColor)

		elif ((row is not None) and (column is not None)):
			#Color the cell
			self.thing.SetCellBackgroundColour(row, column, color)
			self.thing.SetCellTextColour(row, column, textColor)

		elif (row is None):
			for i in range(self.thing.GetNumberRows()):
				#Color the cell
				self.thing.SetCellBackgroundColour(i, column, color)
				self.thing.SetCellTextColour(i, column, textColor)

		else:
			for i in range(self.thing.GetNumberCols()):
				#Color the cell
				self.thing.SetCellBackgroundColour(row, i, color)
				self.thing.SetCellTextColour(row, i, textColor)

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

		Example Input: setTableCellFont(1, 2, "TimesNewRoman")
		Example Input: setTableCellFont(1, 2, wx.ROMAN)
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

		Example Input: setTableMods(1, 2, "TimesNewRoman")
		Example Input: setTableMods(1, 2, wx.ROMAN)
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

		row (int) - The index of the row

		Example Input: hideTableRow(1)
		"""

		self.thing.SetRowSize(row, 0)

	def hideTableColumn(self, column):
		"""Hides a column in a grid.
		The top-left corner is column (0, 0) not (1, 1).

		column (int) - The index of the column

		Example Input: hideTableColumn(1)
		"""

		self.thing.SetColSize(column, 0)

	def setTableRowLabelSize(self, value = 0):
		"""Sets the size for all rows

		value (int) - The new size

		Example Input: setTableRowLabelSize(20)
		"""

		self.thing.SetRowLabelSize(value)

	def setTableColumnLabelSize(self, value = 0):
		"""Sets the size for all columns

		value (int) - The new size

		Example Input: setTableColumnLabelSize(20)
		"""

		self.thing.SetColLabelSize(value)

	def getTableTextColor(self, row, column):
		"""Returns the color of the text in a cell.
		The top-left corner is cell (0, 0) not (1, 1).

		row (int)     - The index of the row
			- If None: Will color all cells of the column if 'column' is not None
		column (int)  - The index of the column
			- If None: Will color all cells of the column if 'column' is not None

		Example Input: getTableTextColor(1, 2)
		"""

		#Set the text color
		return self.thing.GetCellTextColour(row, column)

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

	def _onTableDisplayToolTip(self, event, *args, **kwargs):
		"""Displays a tool tip when the mouse moves over the cell."""

		#Get the wxObject
		thing = self._getObjectWithEvent(event)

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
			if ((row is not None) and (column is not None)):
				if ((currentRow == row) and (currentColumn == column)):
					thing.SetToolTipString(message)
				else:
					thing.SetToolTipString("")
			elif (row is not None):
				if (currentRow == row):
					thing.SetToolTipString(message)
				else:
					thing.SetToolTipString("")
			elif (column is not None):
				if (currentColumn == column):
					thing.SetToolTipString(message)
				else:
					thing.SetToolTipString("")
			else:
				thing.SetToolTipString("")

		event.Skip()

	def _onTableArrowKeyMove(self, event):
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

	def _onTableEditOnEnter(self, event):
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

	def _onTableEditOnClick(self, event, edit):
		"""Allows the user to enter 'edit cell mode' on a single click instead of a double click
		This is currently not working

		tableNumber (int) - What the table is called in the table catalogue
		edit (bool)       - If True: The user will enter 'edit cell mode' on a single click instead of a double click
							If False: The user will enter 'edit cell mode' on a double click instead of a single click

		Example Input: _onTableEditOnClick(0, True)
		"""

		### NOT WORKING YET ###
		if (edit):
			#Move editor
			selection = self.getTableCurrentCell(event)

			#Default to the top left cell if a range is selected
			row, column = selection[0]

			# wx.grid.GridCellEditor(row, column, table)

		event.Skip()

	def _onTableAutoSize(self, event = None, distributeRemainer = True, distributeAttempts = 5):
		"""Allows the table to automatically change the size of the columns to fit in the sizer element"""

		def find(autoSize, size, row = True):
			"""Finds the rows or columns.

			Example Input: find(self.autoSizeRow, self.rowSize, row = True)
			Example Input: find(self.autoSizeColumn, self.columnSize, row = False)
			"""
			nonlocal self, nRows, nColumns

			if (autoSize[None] is not None):
				itemList = [item for item, state in autoSize.items() if ((item is not None) and (state != False) and (item not in size))]
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
				if (autoSize is not None):
					for i, item in enumerate(itemList):
						if (item in itemSize):
							value = itemSize[item]
						else:
							value = itemSize[None]

						if ((item in autoSize) and (autoSize[item] < value)):
							tooLong[item] = value - autoSize[item]
						elif ((autoSize[None] is not None) and (autoSize[None] < value)):
							tooLong[item] = value - autoSize[None]

					notIncluded = [item for item in range(n) if ((item is not None) and (item not in tooLong))]
					if ((not distributeRemainer) or (len(notIncluded) == 0)):
						for item, value in tooLong.items():
							itemSize[item] = itemSize[None] - value
						tooLong = {}
					else:
						for item, value in tooLong.items():
							newValue = math.floor(value / (len(notIncluded)))

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

			if (len(itemList) == 0):
				itemSize = None
				return itemSize
			else:
				itemSize = {None: math.floor(totalSize[int(row)] / (len(itemList)))}

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

			if (itemSize is None):
				return

			if (row):
				myFunction = self.thing.SetRowSize
			else:
				myFunction = self.thing.SetColSize

			for item in itemList:
				if (item in itemSize):
					myFunction(item, itemSize[item])
				else:
					myFunction(item, itemSize[None])

		##############################################################

		try:
			if ((self.autoSizeRow[None] is not None) or (self.autoSizeColumn[None] is not None)):
				nRows = self.thing.GetNumberRows()
				nColumns = self.thing.GetNumberCols()

				rowList = find(self.autoSizeRow, self.rowSize, row = True)
				columnList = find(self.autoSizeColumn, self.columnSize, row = False)

				totalSize = self.thing.GetGridWindow().GetSize()
				rowSize = calculate(self.rowSizeMaximum, rowList, row = True)
				columnSize = calculate(self.columnSizeMaximum, columnList, row = False)

				apply(rowList, rowSize, row = True)
				apply(columnList, columnSize, row = False)

		finally:
			if (event is not None):
				event.Skip()
	
	def _onTableButton(self, event, pressed):
		"""Allows "button" cell types to function properly."""

		if (isinstance(event, wx.FocusEvent)):
			row, column = self.getTableCurrentCell()[0]
		else:
			x, y = self.thing.CalcUnscrolledPosition(event.GetPosition())
			row = self.thing.YToRow(y)
			column = self.thing.XToCol(x)

		handle = self.thing.GetCellRenderer(row, column)
		if (isinstance(handle, self._TableCellRenderer)):
			if (row not in self.buttonPressCatalogue):
				self.buttonPressCatalogue[row] = {}
			if (column not in self.buttonPressCatalogue[row]):
				self.buttonPressCatalogue[row][column] = {"press": False, "ranFunction": False}

			self.buttonPressCatalogue[row][column]["press"] = pressed
			if (not pressed):
				self.buttonPressCatalogue[row][column]["ranFunction"] = False

		self.thing.Refresh()
		event.Skip()

	####################################################################################################
	class _Table(wx.grid.Grid):
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
					return
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

		def setValue(self, row, column, value, triggerEvent = True):
			"""Triggers an event when the data is changed."""

			if (triggerEvent):
				event = wx.grid.GridEvent(self.GetId(), wx.grid.EVT_GRID_CELL_CHANGING.typeId, self, row = row, col = column, sel = True, kbd = wx.KeyboardState(controlDown = True))
				event.SetEventObject(self)
				# wx.PostEvent(self.GetEventHandler(), event)
				self.GetEventHandler().ProcessEvent(event)

			self.SetCellValue(row, column, value)

			if (triggerEvent):
				event = wx.grid.GridEvent(self.GetId(), wx.grid.EVT_GRID_CELL_CHANGED.typeId, self, row = row, col = column, sel = True, kbd = wx.KeyboardState(controlDown = True))
				event.SetEventObject(self)
				# wx.PostEvent(self.GetEventHandler(), event)
				self.GetEventHandler().ProcessEvent(event)

		# def AppendCols(self, number = 1, updateLabels = True):
		#   """Notifies the table when changes are made.
		#   Modified Code from Frank Millman on https://groups.google.com/forum/#!msg/wxpython-users/z4iobAKq0os/zzUL70WzL_AJ
		#   """

		#   wx.grid.Grid.AppendCols(self, numCols = number, updateLabels = updateLabels)
		#   # msg = wx.grid.GridTableMessage(self.GetTable(), wx.grid.GRIDTABLE_NOTIFY_COLS_APPENDED, number)
		#   # self.ProcessTableMessage(msg)

		# def AppendRows(self, number = 1, updateLabels = True):
		#   """Notifies the table when changes are made.
		#   Modified Code from Frank Millman on https://groups.google.com/forum/#!msg/wxpython-users/z4iobAKq0os/zzUL70WzL_AJ
		#   """

		#   wx.grid.Grid.AppendRows(self, numRows = number, updateLabels = updateLabels)
		#   # msg = wx.grid.GridTableMessage(self.GetTable(), wx.grid.GRIDTABLE_NOTIFY_ROWS_APPENDED, number)
		#   # self.ProcessTableMessage(msg)

		# def InsertCols(self, position = 0, number = 1):
		#   """Notifies the table when changes are made.
		#   Modified Code from Frank Millman on https://groups.google.com/forum/#!msg/wxpython-users/z4iobAKq0os/zzUL70WzL_AJ
		#   """

		#   wx.grid.Grid.InsertCols(self, pos = position, numCols = number)
		#   # msg = wx.grid.GridTableMessage(self.GetTable(), wx.grid.GRIDTABLE_NOTIFY_COLS_INSERTED, position, number)
		#   # self.ProcessTableMessage(msg)

		# def InsertRows(self, position = 0, number = 1):
		#   """Notifies the table when changes are made.
		#   Modified Code from Frank Millman on https://groups.google.com/forum/#!msg/wxpython-users/z4iobAKq0os/zzUL70WzL_AJ
		#   """

		#   wx.grid.Grid.InsertRows(self, pos = position, numRows = number)
		#   # msg = wx.grid.GridTableMessage(self.GetTable(), wx.grid.GRIDTABLE_NOTIFY_ROWS_INSERTED, position, number)
		#   # self.ProcessTableMessage(msg)

		# def DeleteCols(self, position = 0, number = 1, updateLabels = True):
		#   """Notifies the table when changes are made.
		#   Modified Code from Frank Millman on https://groups.google.com/forum/#!msg/wxpython-users/z4iobAKq0os/zzUL70WzL_AJ
		#   """

		#   wx.grid.Grid.DeleteCols(self, pos = position, numCols = number, updateLabels = updateLabels)
		#   # msg = wx.grid.GridTableMessage(self.GetTable(), wx.grid.GRIDTABLE_NOTIFY_COLS_DELETED, position, number)
		#   # self.ProcessTableMessage(msg)

		# def DeleteRows(self, position = 0, number = 1, updateLabels = True):
		#   """Notifies the table when changes are made.
		#   Modified Code from Frank Millman on https://groups.google.com/forum/#!msg/wxpython-users/z4iobAKq0os/zzUL70WzL_AJ
		#   """

		#   wx.grid.Grid.DeleteRows(self, pos = position, numRows = number, updateLabels = updateLabels)
		#   # msg = wx.grid.GridTableMessage(self.GetTable(), wx.grid.GRIDTABLE_NOTIFY_ROWS_DELETED, position, number)
		#   # self.ProcessTableMessage(msg)

	####################################################################################################        
	class _TableCellEditor(wx.grid.GridCellEditor):
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

			Example Input: _TableCellEditor()
			Example Input: _TableCellEditor(debugging = True)
			Example Input: _TableCellEditor(downOnEnter = False)
			"""

			#Load in default behavior
			super(handle_WidgetTable._TableCellEditor, self).__init__()
			# wx.grid.GridCellEditor.__init__(self)

			#Internal variables
			self.parent = parent
			self.debugging = debugging
			self.downOnEnter = downOnEnter
			self.patching_event = False #Used to make the events work correctly
			self.cellType = cellType
			# self.debugging = True

			if (isinstance(self.cellType[None], str)):
				if ((self.cellType[None].lower() == "dialog") and (isinstance(self.cellType["myFrame"], str))):
					if (self.cellType["myFrame"] not in self.parent.getDialog()):
						errorMessage = f"There is no custom dialog window {self.cellType['myFrame']} for {self.parent.__repr__()}\nCreate one using GUI_Maker.addDialog(label = {self.cellType['myFrame']}) during setup"
						raise KeyError(errorMessage)
					else:
						self.cellType["myFrame"] = self.parent.controller[self.cellTypeValue]

			#Write debug information
			if (self.debugging):
				print(f"TableCellEditor.__init__(downOnEnter = {downOnEnter}, debugging = {debugging}, cellType = {cellType})")

			# # event = wx.CommandEvent(wx.grid.EVT_GRID_CELL_CHANGING.typeId, self.parent.thing.GetId())
			# event = wx.grid.GridEvent(self.parent.thing.GetId(), wx.grid.EVT_GRID_CELL_CHANGING.typeId, self.parent.thing, row = 2, col = 3)
			# # event = wx.grid.GridEvent()#wx.ID_ANY, wx.grid.EVT_GRID_CELL_CHANGING.typeId, self.parent.thing.GetId())
			# # event.SetEventType(wx.grid.EVT_GRID_CELL_CHANGING.typeId)
			# # event.SetEventObject(self.parent.thing)

			# print(event.GetRow())

			# event.SetEventObject(self.parent.thing)
			# wx.PostEvent(self.parent.thing.GetEventHandler(), event)

		def Create(self, parent, myId, event):
			"""Called to create the control, which must derive from wx.Control.
			*Must Override*.
			"""

			#Write debug information
			if (self.debugging):
				print(f"TableCellEditor.Create(parent = {parent}, myId = {myId}, event = {event})")

			#Prepare widget control
			style = ""

			#Account for special style
			if (isinstance(self.cellType[None], str) and (self.cellType[None].lower() == "droplist")):
				#Ensure that the choices given are a list or tuple
				if (not isinstance(self.cellType["choices"], (list, tuple, range))):
					self.cellType["choices"] = [self.cellType["choices"]]

				#Ensure that the choices are all strings
				self.cellType["choices"] = [str(item) for item in self.cellType["choices"]]
				self.myCellControl = wx.Choice(parent, myId, (100, 50), choices = self.cellType["choices"])
				
				if (self.cellType["endOnSelect"]):
					self.myCellControl.Bind(wx.EVT_CHOICE, self.onSelectionMade)

				#Check readOnly
				if (self.parent.getTableCurrentCellReadOnly(event = event)):
					self.myCellControl.Enable(False)

			#Use a text box
			else:               
				#Check how the enter key is processed
				if (self.downOnEnter):
					style += "|wx.TE_PROCESS_ENTER"

				# #Check readOnly
				# if (self.parent.getTableCurrentCellReadOnly(event = event)):
				#   style += "|wx.TE_READONLY"

				#Strip of extra divider
				if (style != ""):
					if (style[0] == "|"):
						style = style[1:]
				else:
					style = "wx.DEFAULT"

				#Create text control
				self.myCellControl = wx.TextCtrl(parent, myId, "", style = eval(style, {'__builtins__': None, "wx": wx}, {}))
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
			if (self.patching_event):
				return

			#Write debug information
			if (self.debugging):
				print(f"TableCellEditor.Show(show = {show}, attr = {attr})")

			super(handle_WidgetTable._TableCellEditor, self).Show(show, attr)

		def PaintBackground(self, rect, attr):
			"""Draws the part of the cell not occupied by the edit control. The
			base  class version just fills it with background colour from the
			attribute. In this class the edit control fills the whole cell so
			don't do anything at all in order to reduce flicker.
			"""

			#Write debug information
			if (self.debugging):
				print(f"TableCellEditor.PaintBackground(rect = {rect}, attr = {attr})")

		def onSelectionMade(self, event):
			"""Modifies the droplist behavior to EndEdit on selection, not unfocus."""

			self.parent.myWindow.thing.SetFocus()
			self.parent.thing.SetFocus()
			event.Skip()

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
			if (isinstance(self.cellType[None], str)):
				if (self.cellType[None].lower() == "droplist"):
					self.myCellControl.SetStringSelection(self.startValue)
					self.myCellControl.SetFocus()

				elif (self.cellType[None].lower() == "dialog"):
					self.myCellControl.SetValue(self.startValue)
					self.myCellControl.SetFocus()

					with self.parent.makeDialogCustom(self.cellType["myFrame"], self.cellType["myFrame"].getValueLabel(), label = self.cellType["label"]) as myDialog:
						if (not myDialog.isCancel()):
							value = myDialog.getValue()
							self.myCellControl.SetValue(value)

					self.EndEdit(row, column, grid, self.startValue)

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

			if (self.patching_event):
				return

			#Write debug information
			if (self.debugging):
				print(f"TableCellEditor.EndEdit(row = {row}, column = {column}, grid = {grid}, oldValue = {oldValue})")

			#Check for read only condition
			if (self.parent.getTableReadOnly(row, column)):
				return

			if (isinstance(self.cellType[None], str) and (self.cellType[None].lower() == "droplist")):
				newValue = self.myCellControl.GetStringSelection()
			else:
				newValue = self.myCellControl.GetValue()

			#Compare Value
			if (newValue != oldValue):
				#Fix loop problem
				self.patching_event = True

				event = wx.grid.GridEvent(grid.GetId(), wx.grid.EVT_GRID_CELL_CHANGING.typeId, grid, row = row, col = column)
				event.SetEventObject(grid)
				self.parent.thing.GetEventHandler().ProcessEvent(event)

				self.ApplyEdit(row, column, grid)

				event = wx.grid.GridEvent(grid.GetId(), wx.grid.EVT_GRID_CELL_CHANGED.typeId, grid, row = row, col = column)
				event.SetEventObject(grid)
				self.parent.thing.GetEventHandler().ProcessEvent(event)

				self.patching_event = False
			
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

			if (isinstance(self.cellType[None], str) and (self.cellType[None].lower() == "droplist")):
				value = self.myCellControl.GetStringSelection()
				self.startValue = self.cellType["choices"][0]
				self.myCellControl.SetStringSelection(self.cellType["choices"][0])
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

			if (isinstance(self.cellType[None], str) and (self.cellType[None].lower() == "droplist")):
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
			#return super(handle_WidgetTable._TableCellEditor, self).IsAcceptedKey(event)

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
					if (isinstance(self.cellType[None], str) and (self.cellType[None].lower() == "droplist")):
						if (char in self.cellType["choices"]):
							self.myCellControl.SetStringSelection(char)
						else:
							self.myCellControl.SetStringSelection(self.cellType["choices"][0])
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

			return super(handle_WidgetTable._TableCellEditor, self).Destroy()

		def GetControl(self):
			"""Returns the wx control used"""

			#Write debug information
			if (self.debugging):
				print("TableCellEditor.GetControl()")

			return super(handle_WidgetTable._TableCellEditor, self).GetControl()

		def GetValue(self):
			"""Returns the current value in the wx control used"""

			#Write debug information
			if (self.debugging):
				print("TableCellEditor.GetValue()")

			return super(handle_WidgetTable._TableCellEditor, self).GetValue()

		def HandleReturn(self, event):
			"""Helps the enter key use."""

			#Write debug information
			if (self.debugging):
				print(f"TableCellEditor.HandleReturn({event})")

			return super(handle_WidgetTable._TableCellEditor, self).HandleReturn(event)

		def IsCreated(self):
			"""Returns True if the edit control has been created."""

			#Write debug information
			if (self.debugging):
				print("TableCellEditor.IsCreated()")

			return super(handle_WidgetTable._TableCellEditor, self).IsCreated()

		def SetControl(self, control):
			"""Set the wx control that will be used by this cell editor for editing the value."""

			#Write debug information
			if (self.debugging):
				print(f"TableCellEditor.SetControl({control})")

			return super(handle_WidgetTable._TableCellEditor, self).SetControl(control)

		def Clone(self):
			"""Create a new object which is the copy of this one
			*Must Override*
			"""

			#Write debug information
			if (self.debugging):
				print("TableCellEditor.Clone()")

			handle = self.parent._TableCellEditor(downOnEnter = self.downOnEnter, debugging = self.debugging, cellType = self.cellType)
			handle.IncRef()
			return handle

	class _TableCellRenderer(wx.grid.GridCellRenderer):
		"""Used to modify the grid cell renderer's behavior.
		Modified code from: Nathan McCorkle on https://groups.google.com/forum/#!topic/wxpython-users/HhtKCxPVX_s
		See: https://wiki.wxpython.org/wxPyGridCellRenderer
		See: https://github.com/wxWidgets/Phoenix/blob/master/demo/GridStdEdRend.py
		"""

		def __init__(self, parent, debugging = False, cellType = None):
			"""Defines internal variables and arranges how the renderer will behave.

			debugging (bool)   - Determines if debug information should be displayed or not
				- If True: Debug information will be printed to the command window
			cellType - Which widget type to use for the controller
				- If None: Will use 'inputBox'

			Example Input: _TableCellRenderer()
			Example Input: _TableCellRenderer(debugging = True)
			"""

			#Load in default behavior
			super(handle_WidgetTable._TableCellRenderer, self).__init__()
			# wx.grid.GridCellEditor.__init__(self)

			#Internal variables
			self.parent = parent
			self.debugging = debugging
			self.cellType = cellType
			# self.debugging = True

			#Use: https://wxpython.org/Phoenix/docs/html/wx.SystemColour.enumeration.html
			self.COLOR_BACKGROUND_SELECTED = wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHT)
			self.COLOR_BUTTON_SELECTED = wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNHIGHLIGHT)
			self.COLOR_TEXT_SELECTED = wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHTTEXT)

			self.COLOR_BUTTON_BORDER = wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNSHADOW)

			self.COLOR_BACKGROUND = wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW)
			self.COLOR_BUTTON = wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNFACE)
			self.COLOR_TEXT = wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOWTEXT)

			#Write debug information
			if (self.debugging):
				print(f"TableCellRenderer.__init__(debugging = {debugging}, cellType = {cellType})")

		def Draw(self, grid, attributes, dc, rectangle, row, column, isSelected):
			"""Customisation Point: Draw the data from grid in the rectangle with attributes using the dc.
			Use: https://github.com/wxWidgets/wxPython/blob/master/demo/RendererNative.py
			"""
			
			if (self.debugging):
				print(f"TableCellRenderer.Draw(grid = {grid}, attributes = {attributes}, dc = {dc}, rectangle = {rectangle}, row = {row}, column = {column}, isSelected = {isSelected})")

			cellColor = self.parent.getTableCellColor(row, column)
			textColor = self.parent.getTableTextColor(row, column)
			self.drawBackground(dc, rectangle, isSelected, color = cellColor)
			
			if (isinstance(self.cellType[None], str)):
				if (self.cellType[None].lower() == "button"):
					#Error Checking
					if (row not in self.parent.buttonPressCatalogue):
						self.parent.buttonPressCatalogue[row] = {}
					if (column not in self.parent.buttonPressCatalogue[row]):
						self.parent.buttonPressCatalogue[row][column] = {"press": False, "ranFunction": False}

					#Do not let the user enter the grid cell editor
					if (not grid.IsReadOnly(row, column)):
						grid.SetReadOnly(row, column, True)

					#Draw Button
					if (self.parent.buttonPressCatalogue[row][column]["press"]):
						colorOffset = 50
					else:
						colorOffset = 25

					buttonColor = tuple([item - colorOffset for item in cellColor[:-1]] + [cellColor[3]])
					buttonBorderColor = tuple([item - colorOffset - 25 for item in cellColor[:-1]] + [cellColor[3]])
					self.drawButton(dc, rectangle, isSelected, fitTo = self.cellType["text"], width_offset = 10, height_offset = 10, 
						radius = 5, x_align = "center", y_align = "center", color = buttonColor, borderColor = buttonBorderColor)

					if (self.cellType["text"] is not None):
						self.drawText(self.cellType["text"], dc, rectangle, isSelected, align = "center", color = textColor)

					#Run Function
					if ((self.parent.buttonPressCatalogue[row][column]["press"]) and (not self.parent.buttonPressCatalogue[row][column]["ranFunction"])):
						self.parent.buttonPressCatalogue[row][column]["ranFunction"] = True
						self.parent.runMyFunction(self.cellType["myFunction"], self.cellType["myFunctionArgs"], self.cellType["myFunctionKwargs"])
				else:
					text = grid.GetCellValue(row, column)
					self.drawText(text, dc, rectangle, isSelected, align = "left", color = textColor)

		def GetBestSize(self, grid, attributes, dc, row, column):
			"""Customisation Point: Determine the appropriate (best) size for the control, return as wxSize.

				Note: You _must_ return a wxSize object.  Returning a two-value-tuple
				won't raise an error, but the value won't be respected by wxPython.
				"""
			
			if (self.debugging):
				print(f"TableCellRenderer.GetBestSize(grid = {grid}, attributes = {attributes}, dc = {dc}, row = {row}, column = {column})")

			text = grid.GetCellValue(row, column)
			dc.SetFont(attributes.GetFont())
			width, height = dc.GetTextExtent(text)
			return wx.Size(width, height)

		def Clone(self):
			"""Create a new object which is the copy of this one."""
			
			if (self.debugging):
				print(f"TableCellRenderer.Clone()")

			handle = self.parent._TableCellRenderer(self.parent, debugging = self.debugging, cellType = self.cellType)
			handle.IncRef()
			return handle

		#Utility Functions
		def drawText(self, text, dc, rectangle, isSelected, x_offset = 0, y_offset = 0, align = None, color = None):
			"""Draw a simple text label in appropriate colors.
			Special thanks to Milan Skala for how to center text on http://wxpython-users.1045709.n5.nabble.com/Draw-text-over-an-existing-bitmap-td5725527.html

			align (str) - Where the text should be aligned in the cell
				~ "left", "right", "center"
				- If None: No alignment will be done

			Example Input: drawText(text, dc, rectangle, isSelected)
			Example Input: drawText(text, dc, rectangle, isSelected, align = "left", color = textColor)
			"""

			oldColor = dc.GetTextForeground()
			try:
				if (color is not None):
					color = tuple(min(255, max(0, item)) for item in color) #Ensure numbers are between 0 and 255
				else:
					if (isSelected):
						color = self.COLOR_TEXT_SELECTED
					else:
						color = self.COLOR_TEXT
				dc.SetTextForeground(color)

				if (align is None):
					x_align = 0
					y_align = 0
				else:
					width, height = dc.GetTextExtent(text)
					y_align = (rectangle.height - height) / 2
				
					if (align.lower()[0] == "l"):
						x_align = 0
					elif (align.lower()[0] == "r"):
						x_align = rectangle.width - width
					else:
						x_align = (rectangle.width - width) / 2

				dc.DrawText(text, rectangle.x + x_offset + x_align, rectangle.y + y_offset + y_align)
			finally:
				dc.SetTextForeground(oldColor)

		def drawBackground(self, dc, rectangle, isSelected, color = None):
			"""Draw an appropriate background based on selection state.

			Example Input: drawText(dc, rectangle, isSelected)
			Example Input: drawText(dc, rectangle, isSelected, color = cellColor)"""

			oldPen = dc.GetPen()
			oldBrush = dc.GetBrush()

			try:
				if (color is not None):
					color = tuple(min(255, max(0, item)) for item in color) #Ensure numbers are between 0 and 255
				else:
					if (isSelected):
						color = self.COLOR_BACKGROUND_SELECTED
					else:
						color = self.COLOR_BACKGROUND
				dc.SetBrush(wx.Brush(color, style = wx.SOLID))
			
				dc.SetPen(wx.TRANSPARENT_PEN)
				dc.DrawRectangle(rectangle.x, rectangle.y, rectangle.width, rectangle.height)
			finally:
				dc.SetPen(oldPen)
				dc.SetBrush(oldBrush)

		def drawButton(self, dc, rectangle, isSelected, fitTo = None, radius = 1, borderWidth = 1,
			x_offset = 0, y_offset = 0, width_offset = 0, height_offset = 0,
			x_align = None, y_align = None, color = None, borderColor = None):
			"""Draw a button in appropriate colors.
			If both 'x_align' and 'y_align' are None, no alignment will be done

			fitTo (str)   - Determines the initial width and height of the button
				- If str: Will use the size of the text if it were drawn
				- If None: Will use 'rectangle'

			x_align (str) - Where the button should be aligned with respect to the x-axis in the cell
				~ "left", "right", "center"
				- If None: Will use "center"

			y_align (str) - Where the button should be aligned with respect to the x-axis in the cell
				~ "top", "bottom", "center"
				- If None: Will use "center"

			Example Input: drawButton(dc, rectangle, isSelected)
			Example Input: drawButton(dc, rectangle, isSelected, x_align = "right", y_align = "top")
			Example Input: drawButton(dc, rectangle, isSelected, x_align = "center", y_align = "center", width_offset = -10, height_offset = -10)
			Example Input: drawButton(dc, rectangle, isSelected, fitTo = "Lorem Ipsum", width_offset = 6)
			"""

			oldPen = dc.GetPen()
			oldBrush = dc.GetBrush()

			try:
				if (color is not None):
					color = tuple(min(255, max(0, item)) for item in color) #Ensure numbers are between 0 and 255
				else:
					if (isSelected):
						color = self.COLOR_BUTTON_SELECTED
					else:
						color = self.COLOR_BUTTON
				dc.SetBrush(wx.Brush(color, style = wx.SOLID))

				if (borderColor is not None):
					borderColor = tuple(min(255, max(0, item)) for item in borderColor) #Ensure numbers are between 0 and 255
				else:
					borderColor = self.COLOR_BUTTON_BORDER
				dc.SetPen(wx.Pen(borderColor, width = borderWidth, style = wx.SOLID))
				# dc.SetPen(wx.TRANSPARENT_PEN)

				if (fitTo is None):
					width = rectangle.width
					height = rectangle.height
				else:
					width, height = dc.GetTextExtent(fitTo)

				if ((x_align is None) and (y_align is None)):
					x_align = 0
					y_align = 0
				else:
					if (x_align is None):
						x_align = "center"
					elif (y_align is None):
						y_align = "center"

					if (x_align.lower()[0] == "l"):
						x_align = 0
					elif (x_align.lower()[0] == "r"):
						x_align = rectangle.width - (width + width_offset)
					else:
						x_align = (rectangle.width - (width + width_offset)) / 2

					if (y_align.lower()[0] == "t"):
						y_align = 0
					elif (y_align.lower()[0] == "b"):
						y_align = rectangle.height - (height + height_offset)
					else:
						y_align = (rectangle.height - (height + height_offset)) / 2

				dc.DrawRoundedRectangle(rectangle.x + x_align + x_offset, rectangle.y + y_align + y_offset, width + width_offset, height + height_offset, radius)
			finally:
				dc.SetPen(oldPen)
				dc.SetBrush(oldBrush)
				
		def clip(self, dc, rectangle):
			"""Setup the clipping rectangle"""
			
			dc.SetClippingRegion(rectangle.x, rectangle.y, rectangle.width, rectangle.height)
		
		def unclip(self, dc):
			"""Destroy the clipping rectangle"""
			
			dc.DestroyClippingRegion()

	####################################################################################################

class handle_Sizer(handle_Container_Base):
	"""A handle for working with a wxSizer."""

	def __init__(self):
		"""Initializes defaults."""

		#Initialize inherited classes
		handle_Container_Base.__init__(self)

		#Defaults
		self.substitute = None
		self.myWindow = None
		self.rows = None
		self.columns = None
		self.growFlexColumn_notEmpty = {} #{column (int): state (bool)}
		self.growFlexRow_notEmpty = {} #{row (int): state (bool)}

	def __str__(self):
		"""Gives diagnostic information on the Sizer when it is printed out."""

		output = handle_Container_Base.__str__(self)
		
		if (self.rows is not None):
			output += f"-- Rows: {self.rows}\n"
		if (self.columns is not None):
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
		if (state is not None):
			return state

	def _build(self, argument_catalogue):
		if (self.type is None):
			errorMessage = "Must define sizer type before building"
			raise SyntaxError(errorMessage)

		sizerType = self.type
		if (sizerType not in (Types.grid, Types.flex, Types.bag, Types.box, Types.text, Types.wrap)):
			errorMessage = f"There is no 'type' {self.type}. The value should be be 'Grid', 'Flex', 'Bag', 'Box', 'Text', or 'Wrap'"
			raise KeyError(errorMessage)

		#Pre Build
		self._preBuild(argument_catalogue)

		#Unpack arguments
		buildSelf, text = self._getArguments(argument_catalogue, ["self", "text"])
		scroll_x, scroll_y, scrollToTop, scrollToChild, size = self._getArguments(argument_catalogue, ["scroll_x", "scroll_y", "scrollToTop", "scrollToChild", "size"])

		if ((scroll_x not in [False, None]) or (scroll_y not in [False, None])):
			self.substitute = self._makeSizerBox()

			panel = self._makePanel({"size": size, "scroll_x": scroll_x, "scroll_y": scroll_y, "scrollToTop": scrollToTop, "scrollToChild": scrollToChild})
			self.substitute.nest(panel)
			self.parent = panel

		#Set values
		if (isinstance(buildSelf, handle_Window)):
			self.myWindow = buildSelf
		else:
			self.myWindow = buildSelf.myWindow

		myId = self._getId(argument_catalogue)
		
		#Create Sizer
		if (sizerType is Types.grid):
			rows, columns, rowGap, colGap = self._getArguments(argument_catalogue, ["rows", "columns", "rowGap", "colGap"])
			self.thing = wx.GridSizer(rows, columns, rowGap, colGap)

		else:
			#Determine direction
			vertical = self._getArguments(argument_catalogue, "vertical")
			if (vertical is None):
				direction = wx.BOTH
			elif (vertical):
				direction = wx.VERTICAL
			else:
				direction = wx.HORIZONTAL

			if (sizerType is Types.box):
				self.thing = wx.BoxSizer(direction)

			elif (sizerType is Types.text):
				self.thing = wx.StaticBoxSizer(wx.StaticBox(self.parent.thing, myId, text), direction)

			elif (sizerType is Types.wrap):
				extendLast = self._getArguments(argument_catalogue, "extendLast")
				if (extendLast):
					flags = "wx.EXTEND_LAST_ON_EACH_LINE"
				else:
					flags = "wx.WRAPSIZER_DEFAULT_FLAGS"

				self.thing = wx.WrapSizer(direction, eval(flags, {'__builtins__': None, "wx": wx}, {}))

			else:
				rows, columns, rowGap, colGap = self._getArguments(argument_catalogue, ["rows", "columns", "rowGap", "colGap"])
				if (sizerType is Types.flex):
					self.thing = wx.FlexGridSizer(rows, columns, rowGap, colGap)

				elif (sizerType is Types.bag):
					self.thing = wx.GridBagSizer(rowGap, colGap)

					emptySpace = self._getArguments(argument_catalogue, "emptySpace")
					if (emptySpace is not None):
						self.thing.SetEmptyCellSize(emptySpace)

				else:
					errorMessage = f"Unknown sizer type {self.type} for {self.__repr__()}"
					raise KeyError(errorMessage)

				flexGrid = self._getArguments(argument_catalogue, "flexGrid")
				if (not flexGrid):
					self.thing.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_NONE)
				else:
					self.thing.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)
				
				self.thing.SetFlexibleDirection(direction)

		#Remember variables
		if (sizerType not in (Types.box, Types.text, Types.wrap)):
			self.rows = rows
			self.columns = columns

		elif (sizerType is not Types.wrap):
			if (vertical):
				self.columns = 1
				self.rows = -1
			else:
				self.rows = 1
				self.columns = -1

		#Update catalogue
		for key, value in locals().items():
			if (key != "self"):
				argument_catalogue[key] = value

		#Account for nesting in a text sizer
		if (sizerType is not Types.text):
			if (text is not None):
				self.substitute = self._makeSizerText(text = text)
		#Post Build
		self._postBuild(argument_catalogue)

		if (self.substitute is not None):
			self.substitute.nest(self)

		#Set sizer hints to main window while preserving size bounds
		minSize = self.myWindow.thing.GetMinSize()
		maxSize = self.myWindow.thing.GetMaxSize()
		size = self.myWindow.thing.GetSize()
		self.thing.SetSizeHints(self.myWindow.thing)
		self.myWindow.thing.SetMinSize(minSize)
		self.myWindow.thing.SetMaxSize(maxSize)
		self.myWindow.thing.SetSize(size)
		self.myWindow.updateWindow()

	#Change Settings
	def growFlexColumn(self, column, proportion = 0, growOnEmpty = None):
		"""Allows the column to grow as much as it can.

		column (int)      - The column that will expand
		proportion (int)  - How this column will grow compared to other growable columns
							If all are zero, they will grow equally

		Example Input: growFlexColumn(0)
		"""

		if (growOnEmpty is not None):
			if (growOnEmpty):
				self.growFlexColumn_notEmpty[column] = proportion
			elif (column in self.growFlexColumn_notEmpty):
				del self.growFlexColumn_notEmpty[column]

		#Check growability
		if (self.thing.IsColGrowable(column)):
			#The column must be growable. To change the proportion, it's growability must first be removed
			self.thing.RemoveGrowableCol(column)

		#Add attribute
		self.thing.AddGrowableCol(column, proportion)

	def growFlexRow(self, row, proportion = 0, growOnEmpty = None):
		"""Allows the row to grow as much as it can.

		row (int)      - The row that will expand
		proportion (int)  - How this row will grow compared to other growable rows
							If all are zero, they will grow equally

		Example Input: growFlexRow(1)
		"""

		if (growOnEmpty is not None):
			if (not growOnEmpty):
				self.growFlexRow_notEmpty[row] = proportion
			elif (row in self.growFlexRow_notEmpty):
				del self.growFlexRow_notEmpty[row]

		#Check growability
		if (self.thing.IsRowGrowable(row)):
			#The row must be growable. To change the proportion, it's growability must first be removed
			self.thing.RemoveGrowableRow(row)

		#Add attribute
		self.thing.AddGrowableRow(row, proportion)

	def growFlexColumnAll(self, *args, **kwargs):
		"""Allows all the columns to grow as much as they can.

		Example Input: growFlexColumnAll()
		"""

		for column in range(self.thing.GetCols()):
			self.growFlexColumn(column, *args, **kwargs)

	def growFlexRowAll(self, *args, **kwargs):
		"""Allows all the rows to grow as much as they can.

		Example Input: growFlexRowAll()
		"""

		for row in range(self.thing.GetRows()):
			self.growFlexRow(row, *args, **kwargs)

	def _addFinalFunction(self, *args, **kwargs):
		"""Overload for addFinalFunction in handle_Window()."""

		self.myWindow._addFinalFunction(*args, **kwargs)

	def addKeyPress(self, *args, **kwargs):
		"""Overload for addKeyPress in handle_Window()."""

		self.myWindow.addKeyPress(*args, **kwargs)

	#Add Widgets
	def addText(self, *args, flex = 0, flags = "c1", selected = False, **kwargs):
		"""Adds text to the grid.

		flags (list)    - A list of strings for which flag to add to the sizer. Can be just a string if only 1 flag is given
		selected (bool) - If True: This is the default thing selected
		flex (int)      - Only for Box Sizers:
			~ If 0: The cell will not grow or shrink; acts like a Flex Grid cell
			~ If not 0: The cell will grow and shrink to match the cells that have the same number

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

		handle = self._makeText(*args, **kwargs)
		self.nest(handle, flex = flex, flags = flags, selected = selected)
		
		return handle

	def addHtml(self, *args, flex = 0, flags = "c1", selected = False, **kwargs):
		"""Adds an html viewer to the grid.

		flags (list)    - A list of strings for which flag to add to the sizer. Can be just a string if only 1 flag is given
		selected (bool) - If True: This is the default thing selected
		flex (int)      - Only for Box Sizers:
			~ If 0: The cell will not grow or shrink; acts like a Flex Grid cell
			~ If not 0: The cell will grow and shrink to match the cells that have the same number

		Example Input: addHtml()
		Example Input: addHtml(text = "<html><body>Lorem Ipsum</body></html>")
		Example Input: addHtml(text = "Lorem <b>ipsum</b> <i><u>dolor</u></i> sit <font color='red'>amet</font>.")
		"""

		handle = self._makeHtml(*args, **kwargs)
		self.nest(handle, flex = flex, flags = flags, selected = selected)
		
		return handle

	def addHyperlink(self, *args, flex = 0, flags = "c1", selected = False, **kwargs):
		"""Adds a hyperlink text to the next cell on the grid.

		flags (list)    - A list of strings for which flag to add to the sizer. Can be just a string if only 1 flag is given
		selected (bool) - If True: This is the default thing selected
		flex (int)      - Only for Box Sizers:
			~ If 0: The cell will not grow or shrink; acts like a Flex Grid cell
			~ If not 0: The cell will grow and shrink to match the cells that have the same number

		Example Input: addHyperlink("wxFB Website", "http://www.wxformbuilder.org", "siteVisited")
		"""

		handle = self._makeHyperlink(*args, **kwargs)
		self.nest(handle, flex = flex, flags = flags, selected = selected)

		return handle

	def addEmpty(self, *args, flex = 0, flags = "c1", selected = False, **kwargs):
		"""Adds an empty space to the next cell on the grid.

		flags (list)    - A list of strings for which flag to add to the sizer. Can be just a string if only 1 flag is given
		selected (bool) - If True: This is the default thing selected
		flex (int)      - Only for Box Sizers:
			~ If 0: The cell will not grow or shrink; acts like a Flex Grid cell
			~ If not 0: The cell will grow and shrink to match the cells that have the same number

		Example Input: addEmpty()
		Example Input: addEmpty(label = "spacer")
		"""

		handle = self._makeEmpty(*args, **kwargs)
		self.nest(handle, flex = flex, flags = flags, selected = selected)
		return handle

	def addLine(self, *args, flex = 0, flags = "c1", selected = False, **kwargs):
		"""Adds a simple line to the window.
		It can be horizontal or vertical.

		flags (list)    - A list of strings for which flag to add to the sizer. Can be just a string if only 1 flag is given
		selected (bool) - If True: This is the default thing selected
		flex (int)      - Only for Box Sizers:
			~ If 0: The cell will not grow or shrink; acts like a Flex Grid cell
			~ If not 0: The cell will grow and shrink to match the cells that have the same number

		Example Input: addLine()
		Example Input: addLine(vertical = True)
		"""

		handle = self._makeLine(*args, **kwargs)
		self.nest(handle, flex = flex, flags = flags, selected = selected)

		return handle

	def addListDrop(self, *args, flex = 0, flags = "c1", selected = False, **kwargs):
		"""Adds a dropdown list with choices to the next cell on the grid.

		flags (list)    - A list of strings for which flag to add to the sizer. Can be just a string if only 1 flag is given
		selected (bool) - If True: This is the default thing selected
		flex (int)      - Only for Box Sizers:
			~ If 0: The cell will not grow or shrink; acts like a Flex Grid cell
			~ If not 0: The cell will grow and shrink to match the cells that have the same number

		Example Input: addListDrop(choices = ["Lorem", "Ipsum", "Dolor"])
		Example Input: addListDrop(choices = ["Lorem", "Ipsum", "Dolor"], label = "chosen")
		Example Input: addListDrop(choices = ["Lorem", "Ipsum", "Dolor"], alphabetic = True)
		"""

		handle = self._makeListDrop(*args, **kwargs)
		self.nest(handle, flex = flex, flags = flags, selected = selected)

		return handle

	def addListFull(self, *args, flex = 0, flags = "c1", selected = False, **kwargs):
		"""Adds a full list with choices to the next cell on the grid.

		flags (list)    - A list of strings for which flag to add to the sizer. Can be just a string if only 1 flag is given
		selected (bool) - If True: This is the default thing selected
		flex (int)      - Only for Box Sizers:
			~ If 0: The cell will not grow or shrink; acts like a Flex Grid cell
			~ If not 0: The cell will grow and shrink to match the cells that have the same number
		
		Example Input: addListFull(["Lorem", "Ipsum", "Dolor"])
		Example Input: addListFull(["Lorem", "Ipsum", "Dolor"], myFunction = self.onChosen)

		Example Input: addListFull(["Lorem", "Ipsum", "Dolor"], report = True)
		Example Input: addListFull([["Lorem", "Ipsum"], ["Dolor"]], report = True, columns = 2)
		Example Input: addListFull([["Lorem", "Ipsum"], ["Dolor"]], report = True, columns = 2, columnTitles = {0: "Sit", 1: "Amet"})
		Example Input: addListFull({"Sit": ["Lorem", "Ipsum"], "Amet": ["Dolor"]], report = True, columns = 2, columnTitles = {0: "Sit", 1: "Amet"})
		Example Input: addListFull({"Sit": ["Lorem", "Ipsum"], 1: ["Dolor"]], report = True, columns = 2, columnTitles = {0: "Sit"})

		Example Input: addListFull([["Lorem", "Ipsum"], ["Dolor"]], report = True, columns = 2, columnTitles = {0: "Sit", 1: "Amet"}, editable = True)

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

		handle = self._makeListFull(*args, **kwargs)
		self.nest(handle, flex = flex, flags = flags, selected = selected)

		return handle

	def addListTree(self, *args, flex = 0, flags = "c1", selected = False, **kwargs):
		"""Adds a tree list to the next cell on the grid.

		flags (list)    - A list of strings for which flag to add to the sizer. Can be just a string if only 1 flag is given
		selected (bool) - If True: This is the default thing selected
		flex (int)      - Only for Box Sizers:
			~ If 0: The cell will not grow or shrink; acts like a Flex Grid cell
			~ If not 0: The cell will grow and shrink to match the cells that have the same number

		Example Input: addListTree(choices = {"Lorem": [{"Ipsum": "Dolor"}, "Sit"], "Amet": None})
		Example Input: addListTree(choices = {"Lorem": [{"Ipsum": "Dolor"}, "Sit"], "Amet": None}, label = "chosen")
		"""

		handle = self._makeListTree(*args, **kwargs)
		self.nest(handle, flex = flex, flags = flags, selected = selected)

		return handle

	def addInputSlider(self, *args, flex = 0, flags = "c1", selected = False, **kwargs):
		"""Adds a slider bar to the next cell on the grid.

		flags (list)    - A list of strings for which flag to add to the sizer. Can be just a string if only 1 flag is given
		selected (bool) - If True: This is the default thing selected
		flex (int)      - Only for Box Sizers:
			~ If 0: The cell will not grow or shrink; acts like a Flex Grid cell
			~ If not 0: The cell will grow and shrink to match the cells that have the same number

		Example Input: addInputSlider(0, 100, 50, "initialTemperature")
		"""

		handle = self._makeInputSlider(*args, **kwargs)
		self.nest(handle, flex = flex, flags = flags, selected = selected)

		return handle
	
	def addInputBox(self, *args, flex = 0, flags = "c1", selected = False, **kwargs):
		"""Adds an input box to the next cell on the grid.

		flags (list)    - A list of strings for which flag to add to the sizer. Can be just a string if only 1 flag is given
		selected (bool) - If True: This is the default thing selected
		flex (int)      - Only for Box Sizers:
			~ If 0: The cell will not grow or shrink; acts like a Flex Grid cell
			~ If not 0: The cell will grow and shrink to match the cells that have the same number

		Example Input: addInputBox("initialTemperature", 0)
		Example Input: addInputBox("connect", 0, text = "127.0.0.0", ipAddress = True)
		"""

		handle = self._makeInputBox(*args, **kwargs)
		self.nest(handle, flex = flex, flags = flags, selected = selected)
		return handle
	
	def addInputSearch(self, *args, flex = 0, flags = "c1", selected = False, **kwargs):
		"""Adds an input box to the next cell on the grid.

		flags (list)    - A list of strings for which flag to add to the sizer. Can be just a string if only 1 flag is given
		selected (bool) - If True: This is the default thing selected
		flex (int)      - Only for Box Sizers:
			~ If 0: The cell will not grow or shrink; acts like a Flex Grid cell
			~ If not 0: The cell will grow and shrink to match the cells that have the same number

		Example Input: addInputSearch("initialTemperature")
		"""

		handle = self._makeInputSearch(*args, **kwargs)
		self.nest(handle, flex = flex, flags = flags, selected = selected)

		return handle
	
	def addInputSpinner(self, *args, flex = 0, flags = "c1", selected = False, **kwargs):
		"""Adds a spin control to the next cell on the grid. This is an input box for numbers.

		flags (list)    - A list of strings for which flag to add to the sizer. Can be just a string if only 1 flag is given
		selected (bool) - If True: This is the default thing selected
		flex (int)      - Only for Box Sizers:
			~ If 0: The cell will not grow or shrink; acts like a Flex Grid cell
			~ If not 0: The cell will grow and shrink to match the cells that have the same number
		
		Example Input: addInputSpinner(0, 100, 50, "initialTemperature")
		Example Input: addInputSpinner(0, 100, 50, "initialTemperature", maxSize = (100, 100))
		Example Input: addInputSpinner(0, 100, 50, "initialTemperature", exclude = [1,2,3])
		"""

		handle = self._makeInputSpinner(*args, **kwargs)
		self.nest(handle, flex = flex, flags = flags, selected = selected)

		return handle
	
	def addButton(self, *args, flex = 0, flags = "c1", selected = False, **kwargs):
		"""Adds a button to the next cell on the grid.

		flags (list)    - A list of strings for which flag to add to the sizer. Can be just a string if only 1 flag is given
		selected (bool) - If True: This is the default thing selected
		flex (int)      - Only for Box Sizers:
			~ If 0: The cell will not grow or shrink; acts like a Flex Grid cell
			~ If not 0: The cell will grow and shrink to match the cells that have the same number

		Example Input: addButton("Go!", "computeFinArray")
		"""

		handle = self._makeButton(*args, **kwargs)
		self.nest(handle, flex = flex, flags = flags, selected = selected)

		return handle
	
	def addButtonList(self, *args, flex = 0, flags = "c1", selected = False, **kwargs):
		"""Adds a button to the next cell on the grid.
		Each time this button is pressed, it will change the text to display the next item in the list.
		When it reaches the end of the list, it will start back at the beginning

		flags (list)    - A list of strings for which flag to add to the sizer. Can be just a string if only 1 flag is given
		selected (bool) - If True: This is the default thing selected
		flex (int)      - Only for Box Sizers:
			~ If 0: The cell will not grow or shrink; acts like a Flex Grid cell
			~ If not 0: The cell will grow and shrink to match the cells that have the same number

		Example Input: addButton("Go!", "computeFinArray")
		"""

		handle = self._makeButtonList(*args, **kwargs)
		self.nest(handle, flex = flex, flags = flags, selected = selected)

		return handle
	
	def addButtonToggle(self, *args, flex = 0, flags = "c1", selected = False, **kwargs):
		"""Adds a toggle button to the next cell on the grid.

		flags (list)    - A list of strings for which flag to add to the sizer. Can be just a string if only 1 flag is given
		selected (bool) - If True: This is the default thing selected
		flex (int)      - Only for Box Sizers:
			~ If 0: The cell will not grow or shrink; acts like a Flex Grid cell
			~ If not 0: The cell will grow and shrink to match the cells that have the same number

		Example Input: addButtonToggle("Go!", "computeFinArray")
		"""

		handle = self._makeButtonToggle(*args, **kwargs)
		self.nest(handle, flex = flex, flags = flags, selected = selected)

		return handle
	
	def addButtonCheck(self, *args, flex = 0, flags = "c1", selected = False, **kwargs):
		"""Adds a check box to the next cell on the grid.
		Event fires every time the check box is clicked

		flags (list)    - A list of strings for which flag to add to the sizer. Can be just a string if only 1 flag is given
		selected (bool) - If True: This is the default thing selected
		flex (int)      - Only for Box Sizers:
			~ If 0: The cell will not grow or shrink; acts like a Flex Grid cell
			~ If not 0: The cell will grow and shrink to match the cells that have the same number

		Example Input: addButtonCheck("compute?", "computeFinArray", 0)
		"""

		handle = self._makeButtonCheck(*args, **kwargs)
		self.nest(handle, flex = flex, flags = flags, selected = selected)
		return handle
	
	def addButtonCheckList(self, *args, flex = 0, flags = "c1", selected = False, **kwargs):
		"""Adds a checklist to the next cell on the grid.

		flags (list)    - A list of strings for which flag to add to the sizer. Can be just a string if only 1 flag is given
		selected (bool) - If True: This is the default thing selected
		flex (int)      - Only for Box Sizers:
			~ If 0: The cell will not grow or shrink; acts like a Flex Grid cell
			~ If not 0: The cell will grow and shrink to match the cells that have the same number

		Example Input: addButtonCheckList(["Milk", "Eggs", "Bread"], 0, sort = True)
		"""

		handle = self._makeButtonCheckList(*args, **kwargs)
		self.nest(handle, flex = flex, flags = flags, selected = selected)

		return handle
	
	def addButtonRadio(self, *args, flex = 0, flags = "c1", selected = False, **kwargs):
		"""Adds a radio button to the next cell on the grid. If default, it will disable the other
		radio buttons of the same group.

		flags (list)    - A list of strings for which flag to add to the sizer. Can be just a string if only 1 flag is given
		selected (bool) - If True: This is the default thing selected
		flex (int)      - Only for Box Sizers:
			~ If 0: The cell will not grow or shrink; acts like a Flex Grid cell
			~ If not 0: The cell will grow and shrink to match the cells that have the same number

		Example Input: addButtonRadio("compute?", "computeFinArray", 0, groupStart = True)
		"""

		handle = self._makeButtonRadio(*args, **kwargs)
		self.nest(handle, flex = flex, flags = flags, selected = selected)

		return handle
	
	def addButtonRadioBox(self, *args, flex = 0, flags = "c1", selected = False, **kwargs):
		"""Adds a box filled with grouped radio buttons to the next cell on the grid.
		Because these buttons are grouped, only one can be selected

		flags (list)    - A list of strings for which flag to add to the sizer. Can be just a string if only 1 flag is given
		selected (bool) - If True: This is the default thing selected
		flex (int)      - Only for Box Sizers:
			~ If 0: The cell will not grow or shrink; acts like a Flex Grid cell
			~ If not 0: The cell will grow and shrink to match the cells that have the same number

		Example Input: addButtonRadioBox(["Button 1", "Button 2", "Button 3"], "self.onQueueValue", 0)
		"""

		handle = self._makeButtonRadioBox(*args, **kwargs)
		self.nest(handle, flex = flex, flags = flags, selected = selected)

		return handle
	
	def addButtonHelp(self, *args, flex = 0, flags = "c1", selected = False, **kwargs):
		"""Adds a context help button to the next cell on the grid.

		flags (list)    - A list of strings for which flag to add to the sizer. Can be just a string if only 1 flag is given
		selected (bool) - If True: This is the default thing selected
		flex (int)      - Only for Box Sizers:
			~ If 0: The cell will not grow or shrink; acts like a Flex Grid cell
			~ If not 0: The cell will grow and shrink to match the cells that have the same number

		Example Input: addButtonHelp(label = "myHelpButton")
		"""

		handle = self._makeButtonHelp(*args, **kwargs)
		self.nest(handle, flex = flex, flags = flags, selected = selected)

		return handle
	
	def addButtonImage(self, *args, flex = 0, flags = "c1", selected = False, **kwargs):
		"""Adds a button to the next cell on the grid. You design what the button looks like yourself.

		flags (list)    - A list of strings for which flag to add to the sizer. Can be just a string if only 1 flag is given
		selected (bool) - If True: This is the default thing selected
		flex (int)      - Only for Box Sizers:
			~ If 0: The cell will not grow or shrink; acts like a Flex Grid cell
			~ If not 0: The cell will grow and shrink to match the cells that have the same number

		Example Input: addButtonImage("1.bmp", "2.bmp", "3.bmp", "4.bmp", "5.bmp", "computeFinArray")
		"""

		handle = self._makeButtonImage(*args, **kwargs)
		self.nest(handle, flex = flex, flags = flags, selected = selected)

		return handle
	
	def addImage(self, *args, flex = 0, flags = "c1", selected = False, **kwargs):
		"""Adds an embeded image to the next cell on the grid.

		flags (list)    - A list of strings for which flag to add to the sizer. Can be just a string if only 1 flag is given
		selected (bool) - If True: This is the default thing selected
		flex (int)      - Only for Box Sizers:
			~ If 0: The cell will not grow or shrink; acts like a Flex Grid cell
			~ If not 0: The cell will grow and shrink to match the cells that have the same number

		Example Input: addImage("1.bmp", 0)
		Example Input: addImage(image, 0)
		Example Input: addImage("error", 0, internal = True)
		Example Input: addImage(image, 0, size = (32, 32))
		"""

		handle = self._makeImage(*args, **kwargs)
		self.nest(handle, flex = flex, flags = flags, selected = selected)

		return handle
	
	def addProgressBar(self, *args, flex = 0, flags = "c1", selected = False, **kwargs):
		"""Adds progress bar to the next cell on the grid.

		flags (list)    - A list of strings for which flag to add to the sizer. Can be just a string if only 1 flag is given
		selected (bool) - If True: This is the default thing selected
		flex (int)      - Only for Box Sizers:
			~ If 0: The cell will not grow or shrink; acts like a Flex Grid cell
			~ If not 0: The cell will grow and shrink to match the cells that have the same number

		Example Input: addProgressBar(0, 100)
		"""

		handle = self._makeProgressBar(*args, **kwargs)
		self.nest(handle, flex = flex, flags = flags, selected = selected)

		return handle

	def addToolBar(self, *args, flex = 0, flags = "c1", selected = False, **kwargs):
		"""Adds a tool bar to the next cell on the grid.
		Menu items can be added to this.

		flags (list)    - A list of strings for which flag to add to the sizer. Can be just a string if only 1 flag is given
		selected (bool) - If True: This is the default thing selected
		flex (int)      - Only for Box Sizers:
			~ If 0: The cell will not grow or shrink; acts like a Flex Grid cell
			~ If not 0: The cell will grow and shrink to match the cells that have the same number

		Example Input: addToolBar()
		Example Input: addToolBar(label = "first")
		"""

		handle = self._makeToolBar(*args, **kwargs)
		self.nest(handle, flex = flex, flags = flags, selected = selected)

		return handle
	
	def addPickerColor(self, *args, flex = 0, flags = "c1", selected = False, **kwargs):
		"""Adds a color picker to the next cell on the grid.
		It can display the name or RGB of the color as well.

		flags (list)    - A list of strings for which flag to add to the sizer. Can be just a string if only 1 flag is given
		selected (bool) - If True: This is the default thing selected
		flex (int)      - Only for Box Sizers:
			~ If 0: The cell will not grow or shrink; acts like a Flex Grid cell
			~ If not 0: The cell will grow and shrink to match the cells that have the same number

		Example Input: addPickerColor(label = "changeColor")
		"""

		handle = self._makePickerColor(*args, **kwargs)
		self.nest(handle, flex = flex, flags = flags, selected = selected)

		return handle
	
	def addPickerFont(self, *args, flex = 0, flags = "c1", selected = False, **kwargs):
		"""Adds a color picker to the next cell on the grid.
		It can display the name or RGB of the color as well.

		flags (list)    - A list of strings for which flag to add to the sizer. Can be just a string if only 1 flag is given
		selected (bool) - If True: This is the default thing selected
		flex (int)      - Only for Box Sizers:
			~ If 0: The cell will not grow or shrink; acts like a Flex Grid cell
			~ If not 0: The cell will grow and shrink to match the cells that have the same number

		Example Input: addPickerFont(32, "changeFont")
		"""

		handle = self._makePickerFont(*args, **kwargs)
		self.nest(handle, flex = flex, flags = flags, selected = selected)

		return handle
	
	def addPickerFile(self, *args, flex = 0, flags = "c1", selected = False, **kwargs):
		"""Adds a file picker to the next cell on the grid.

		flags (list)    - A list of strings for which flag to add to the sizer. Can be just a string if only 1 flag is given
		selected (bool) - If True: This is the default thing selected
		flex (int)      - Only for Box Sizers:
			~ If 0: The cell will not grow or shrink; acts like a Flex Grid cell
			~ If not 0: The cell will grow and shrink to match the cells that have the same number
		
		Example Input: addPickerFile(myFunction = self.openFile, addInputBox = True)
		Example Input: addPickerFile(saveFile = True, myFunction = self.saveFile, saveConfirmation = True, directoryOnly = True)
		"""

		handle = self._makePickerFile(*args, **kwargs)
		self.nest(handle, flex = flex, flags = flags, selected = selected)

		return handle
	
	def addPickerFileWindow(self, *args, flex = 0, flags = "c1", selected = False, **kwargs):
		"""Adds a file picker window to the next cell on the grid.

		flags (list)    - A list of strings for which flag to add to the sizer. Can be just a string if only 1 flag is given
		selected (bool) - If True: This is the default thing selected
		flex (int)      - Only for Box Sizers:
			~ If 0: The cell will not grow or shrink; acts like a Flex Grid cell
			~ If not 0: The cell will grow and shrink to match the cells that have the same number

		Example Input: addPickerFileWindow("changeDirectory")
		"""

		handle = self._makePickerFileWindow(*args, **kwargs)
		self.nest(handle, flex = flex, flags = flags, selected = selected)

		return handle
	
	def addPickerTime(self, *args, flex = 0, flags = "c1", selected = False, **kwargs):
		"""Adds a time picker to the next cell on the grid.
		The input time is in military time.

		flags (list)    - A list of strings for which flag to add to the sizer. Can be just a string if only 1 flag is given
		selected (bool) - If True: This is the default thing selected
		flex (int)      - Only for Box Sizers:
			~ If 0: The cell will not grow or shrink; acts like a Flex Grid cell
			~ If not 0: The cell will grow and shrink to match the cells that have the same number

		Example Input: addPickerTime()
		Example Input: addPickerTime("17:30")
		Example Input: addPickerTime("12:30:20")
		"""

		handle = self._makePickerTime(*args, **kwargs)
		self.nest(handle, flex = flex, flags = flags, selected = selected)

		return handle
	
	def addPickerDate(self, *args, flex = 0, flags = "c1", selected = False, **kwargs):
		"""Adds a date picker to the next cell on the grid.

		flags (list)    - A list of strings for which flag to add to the sizer. Can be just a string if only 1 flag is given
		selected (bool) - If True: This is the default thing selected
		flex (int)      - Only for Box Sizers:
			~ If 0: The cell will not grow or shrink; acts like a Flex Grid cell
			~ If not 0: The cell will grow and shrink to match the cells that have the same number

		Example Input: addPickerDate()
		Example Input: addPickerDate("10/16/2000")
		Example Input: addPickerDate(dropDown = True)
		"""

		handle = self._makePickerDate(*args, **kwargs)
		self.nest(handle, flex = flex, flags = flags, selected = selected)

		return handle
	
	def addPickerDateWindow(self, *args, flex = 0, flags = "c1", selected = False, **kwargs):
		"""Adds a date picker to the next cell on the grid.

		flags (list)    - A list of strings for which flag to add to the sizer. Can be just a string if only 1 flag is given
		selected (bool) - If True: This is the default thing selected
		flex (int)      - Only for Box Sizers:
			~ If 0: The cell will not grow or shrink; acts like a Flex Grid cell
			~ If not 0: The cell will grow and shrink to match the cells that have the same number

		Example Input: addPickerDateWindow()
		"""

		handle = self._makePickerDateWindow(*args, **kwargs)
		self.nest(handle, flex = flex, flags = flags, selected = selected)

		return handle

	def addCanvas(self, *args, flex = 0, flags = "c1", selected = False, **kwargs):
		"""Creates a blank canvas window.

		flags (list)    - A list of strings for which flag to add to the sizer. Can be just a string if only 1 flag is given
		selected (bool) - If True: This is the default thing selected
		flex (int)      - Only for Box Sizers:
			~ If 0: The cell will not grow or shrink; acts like a Flex Grid cell
			~ If not 0: The cell will grow and shrink to match the cells that have the same number

		Example Input: addCanvas()
		"""

		handle = self._makeCanvas(*args, **kwargs)
		self.nest(handle, flex = flex, flags = flags, selected = selected)

		return handle

	def addTable(self, *args, flex = 0, flags = "c1", selected = False, **kwargs):
		"""Adds a table to the next cell on the grid. 
		If enabled, it can be edited; the column &  sizerNumber, size can be changed.
		To get a cell value, use: myGridId.GetCellValue(row, column).

		flags (list)    - A list of strings for which flag to add to the sizer. Can be just a string if only 1 flag is given
		selected (bool) - If True: This is the default thing selected
		flex (int)      - Only for Box Sizers:
			~ If 0: The cell will not grow or shrink; acts like a Flex Grid cell
			~ If not 0: The cell will grow and shrink to match the cells that have the same number

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

		handle = self._makeTable(*args, **kwargs)
		self.nest(handle, flex = flex, flags = flags, selected = selected)

		return handle

	#Splitters
	def addSplitterDouble(self, sizer_0 = {}, sizer_1 = {}, panel_0 = {}, panel_1 = {},

		dividerSize = 1, dividerPosition = None, dividerGravity = 0.5, 
		vertical = True, minimumSize = 20, 
		
		initFunction = None, initFunctionArgs = None, initFunctionKwargs = None, 

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None, tabSkip = False, selected = False, flex = 0, flags = "c1"):
		"""Creates two blank panels in next to each other. 
		The border between double panels is dragable.

		leftSize (int)        - The size of the left panel. (length, width)
		rightSize (int)       - The size of the right panel. (length, width)
			- If True: 'leftPanel' is the top panel; 'rightPanel' is the bottom panel
			- If False: 'leftPanel' is the left panel; 'rightPanel' is the right panel
		border (str)          - What style the border has. "simple", "raised", "sunken" or "none". Only the first two letters are necissary
		dividerSize (int)     - How many pixels thick the dividing line is. Not available yet
		dividerPosition (int) - How many pixels to the right the dividing line starts after the 'minimumSize' location
			- If None: The line will start at the 'minimumSize' value
		dividerGravity (int)  - From 0.0 to 1.1, how much the left (or top) panel grows with respect to the right (or bottom) panel upon resizing
		vertical (bool)       - Determines the direction that the frames are split
		minimumSize (int)     - How many pixels the smaller pane must have between its far edge and the splitter.
		
		initFunction (str)       - The function that is ran when the panel first appears
		initFunctionArgs (any)   - The arguments for 'initFunction'
		initFunctionKwargs (any) - The keyword arguments for 'initFunction'function

		label (any)   - What this is catalogued as

		Example Input: addSplitterDouble()
		Example Input: addSplitterDouble(horizontal = False)
		Example Input: addSplitterDouble(minimumSize = 100)
		"""

		handle = handle_Splitter()
		handle.type = Types.double
		handle._build(locals())

		return handle.getSizers()

	def addSplitterQuad(self, sizer_0 = {}, sizer_1 = {}, sizer_2 = {}, sizer_3 = {},

		initFunction = None, initFunctionArgs = None, initFunctionKwargs = None,

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None, tabSkip = False):
		"""Creates four blank panels next to each other like a grid.
		The borders between quad panels are dragable. The itersection point is also dragable.
		The panel order is top left, top right, bottom left, bottom right.
		
		border (str) - What style the border has. "simple", "raised", "sunken" or "none". Only the first two letters are necissary
		label (str)  - What this is called in the idCatalogue
		
		initFunction (str)       - The function that is ran when the panel first appears
		initFunctionArgs (any)   - The arguments for 'initFunction'
		initFunctionKwargs (any) - The keyword arguments for 'initFunction'function
		tabTraversal (bool)      - If True: Hitting the Tab key will move the selected widget to the next one

		Example Input: addSplitterQuad()
		"""

		handle = handle_Splitter()
		handle.type = Types.quad
		handle._build(locals())

		return handle.getSizers()

	def addSplitterPoly(self, panelNumbers, sizers = {},
		dividerSize = 1, dividerPosition = None, dividerGravity = 0.5, vertical = False, minimumSize = 20, 

		initFunction = None, initFunctionArgs = None, initFunctionKwargs = None,

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None, tabSkip = False):
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
		label (str)           - What this is called in the idCatalogue
		
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
		handle.type = Types.poly
		handle._build(locals())

		return handle.getSizers()

	#Notebooks
	def addNotebook(self, label = None, flags = None, tabSide = "top", flex = 0,
		fixedWidth = False, multiLine = False, padding = None, reduceFlicker = True,

		initFunction = None, initFunctionArgs = None, initFunctionKwargs = None,
		postPageChangeFunction = None, postPageChangeFunctionArgs = None, postPageChangeFunctionKwargs = None,
		prePageChangeFunction = None, prePageChangeFunctionArgs = None, prePageChangeFunctionKwargs = None,

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, size = wx.DefaultSize, position = wx.DefaultPosition,
		parent = None, handle = None, myId = None, tabSkip = False):
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

		handle = handle_Notebook_Simple()
		handle.type = Types.notebook
		handle._build(locals())

		self.nest(handle, flex = flex)#, flags = flags)

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

		handle = handle_Notebook_Aui()
		handle.type = Types.auinotebook
		handle._build(locals())

		self.nest(handle, flex = flex)#, flags = flags)

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
	#   handle._build(locals())

	#   self.nest(handle)

	#   return handle

	#Sizers
	def addSizerBox(self, *args, flex = 0, flags = "c1", **kwargs):
		"""Creates a box sizer.

		Example Input: addSizerBox()
		Example Input: addSizerBox(0)
		Example Input: addSizerBox(vertical = False)
		Example Input: addSizerBox(0, vertical = False)
		"""

		handle = self._makeSizerBox(*args, **kwargs)
		self.nest(handle, flex = flex, flags = flags)

		return handle

	def addSizerText(self, *args, flex = 0, flags = "c1", **kwargs):
		"""Creates a static box sizer.
		This is a sizer surrounded by a box with a title, much like a wxRadioBox.

		Example Input: addSizerText()
		Example Input: addSizerText(0)
		Example Input: addSizerText(text = "Lorem")
		Example Input: addSizerText(0, text = "Lorem")
		"""

		handle = self._makeSizerText(*args, **kwargs)
		self.nest(handle, flex = flex, flags = flags)

		return handle

	def addSizerGrid(self, *args, flex = 0, flags = "c1", **kwargs):
		"""Creates a grid sizer to the specified size.

		Example Input: addSizerGrid()
		Example Input: addSizerGrid(0)
		Example Input: addSizerGrid(rows = 4, columns = 3)
		Example Input: addSizerGrid(0, rows = 4, columns = 3)
		"""

		handle = self._makeSizerGrid(*args, **kwargs)
		self.nest(handle, flex = flex, flags = flags)

		return handle

	def addSizerGridFlex(self, *args, flex = 0, flags = "c1", **kwargs):
		"""Creates a flex grid sizer.

		Example Input: addSizerGridFlex()
		Example Input: addSizerGridFlex(0)
		Example Input: addSizerGridFlex(rows = 4, columns = 3)
		Example Input: addSizerGridFlex(0, rows = 4, columns = 3)
		"""

		handle = self._makeSizerGridFlex(*args, **kwargs)
		self.nest(handle, flex = flex, flags = flags)

		return handle

	def addSizerGridBag(self, *args, flex = 0, flags = "c1", **kwargs):
		"""Creates a bag grid sizer.

		Example Input: addSizerGridBag()
		Example Input: addSizerGridBag(0)
		Example Input: addSizerGridBag(0, rows = 4, columns = 3)
		Example Input: addSizerGridBag(0, rows = 4, columns = 3, emptySpace = (0, 0))
		"""

		handle = self._makeSizerGridBag(*args, **kwargs)
		self.nest(handle, flex = flex, flags = flags)

		return handle

	def addSizerWrap(self, *args, flex = 0, flags = "c1", **kwargs):
		"""Creates a wrap sizer.
		The widgets will arrange themselves into rows and columns on their own, starting in the top-left corner.

		Example Input: addSizerWrap()
		Example Input: addSizerWrap(0)
		"""

		handle = self._makeSizerWrap(*args, **kwargs)
		self.nest(handle, flex = flex, flags = flags)

		return handle

class handle_SizerProxy(handle_Container_Base):
	"""A handle for working with a wxSizer."""

	def __init__(self):
		"""Initializes defaults."""

		#Initialize inherited classes
		handle_Sizer.__init__(self)
		handle_Container_Base.__init__(self)

		#Defaults
		self.mySizer = None

	def __str__(self):
		"""Gives diagnostic information on the Sizer when it is printed out."""

		output = handle_Sizer.__str__(self)
		
		if (self.mySizer is not None):
			output += f"-- Sizer Proxy: {id(self.mySizer)}\n"
		return output

	#Hook functions
	@MyUtilities.common.setDocstring(handle_Sizer.growFlexColumn)
	def growFlexColumn(self, *args, **kwargs):
		return self.mySizer.growFlexColumn(*args, **kwargs)

	@MyUtilities.common.setDocstring(handle_Sizer.growFlexRow)
	def growFlexRow(self, *args, **kwargs):
		return self.mySizer.growFlexRow(*args, **kwargs)

	@MyUtilities.common.setDocstring(handle_Sizer.growFlexColumnAll)
	def growFlexColumnAll(self, *args, **kwargs):
		return self.mySizer.growFlexColumnAll(*args, **kwargs)

	@MyUtilities.common.setDocstring(handle_Sizer.growFlexRowAll)
	def growFlexRowAll(self, *args, **kwargs):
		return self.mySizer.growFlexRowAll(*args, **kwargs)

	@MyUtilities.common.setDocstring(handle_Sizer._addFinalFunction)
	def _addFinalFunction(self, *args, **kwargs):
		return self.mySizer._addFinalFunction(*args, **kwargs)

	@MyUtilities.common.setDocstring(handle_Sizer.addKeyPress)
	def addKeyPress(self, *args, **kwargs):
		return self.mySizer.addKeyPress(*args, **kwargs)

	@MyUtilities.common.setDocstring(handle_Sizer.addText)
	def addText(self, *args, **kwargs):
		return self.mySizer.addText(*args, **kwargs)

	@MyUtilities.common.setDocstring(handle_Sizer.addHtml)
	def addHtml(self, *args, **kwargs):
		return self.mySizer.addHtml(*args, **kwargs)

	@MyUtilities.common.setDocstring(handle_Sizer.addHyperlink)
	def addHyperlink(self, *args, **kwargs):
		return self.mySizer.addHyperlink(*args, **kwargs)

	@MyUtilities.common.setDocstring(handle_Sizer.addEmpty)
	def addEmpty(self, *args, **kwargs):
		return self.mySizer.addEmpty(*args, **kwargs)

	def addLine(self, *args, **kwargs):
		return self.mySizer.addLine(*args, **kwargs)

	@MyUtilities.common.setDocstring(handle_Sizer.addListDrop)
	def addListDrop(self, *args, **kwargs):
		return self.mySizer.addListDrop(*args, **kwargs)

	@MyUtilities.common.setDocstring(handle_Sizer.addListFull)
	def addListFull(self, *args, **kwargs):
		return self.mySizer.addListFull(*args, **kwargs)

	@MyUtilities.common.setDocstring(handle_Sizer.addListTree)
	def addListTree(self, *args, **kwargs):
		return self.mySizer.addListTree(*args, **kwargs)

	@MyUtilities.common.setDocstring(handle_Sizer.addInputSlider)
	def addInputSlider(self, *args, **kwargs):
		return self.mySizer.addInputSlider(*args, **kwargs)

	@MyUtilities.common.setDocstring(handle_Sizer.addInputBox)
	def addInputBox(self, *args, **kwargs):
		return self.mySizer.addInputBox(*args, **kwargs)

	def addInputSearch(self, *args, **kwargs):
		return self.mySizer.addInputSearch(*args, **kwargs)

	@MyUtilities.common.setDocstring(handle_Sizer.addInputSpinner)
	def addInputSpinner(self, *args, **kwargs):
		return self.mySizer.addInputSpinner(*args, **kwargs)

	@MyUtilities.common.setDocstring(handle_Sizer.addButton)
	def addButton(self, *args, **kwargs):
		return self.mySizer.addButton(*args, **kwargs)

	@MyUtilities.common.setDocstring(handle_Sizer.addButtonList)
	def addButtonList(self, *args, **kwargs):
		return self.mySizer.addButtonList(*args, **kwargs)

	@MyUtilities.common.setDocstring(handle_Sizer.addButtonToggle)
	def addButtonToggle(self, *args, **kwargs):
		return self.mySizer.addButtonToggle(*args, **kwargs)

	@MyUtilities.common.setDocstring(handle_Sizer.addButtonCheck)
	def addButtonCheck(self, *args, **kwargs):
		return self.mySizer.addButtonCheck(*args, **kwargs)

	def addButtonCheckList(self, *args, **kwargs):
		return self.mySizer.addButtonCheckList(*args, **kwargs)

	@MyUtilities.common.setDocstring(handle_Sizer.addButtonRadio)
	def addButtonRadio(self, *args, **kwargs):
		return self.mySizer.addButtonRadio(*args, **kwargs)

	@MyUtilities.common.setDocstring(handle_Sizer.addButtonRadioBox)
	def addButtonRadioBox(self, *args, **kwargs):
		return self.mySizer.addButtonRadioBox(*args, **kwargs)

	@MyUtilities.common.setDocstring(handle_Sizer.addButtonHelp)
	def addButtonHelp(self, *args, **kwargs):
		return self.mySizer.addButtonHelp(*args, **kwargs)

	@MyUtilities.common.setDocstring(handle_Sizer.addButtonImage)
	def addButtonImage(self, *args, **kwargs):
		return self.mySizer.addButtonImage(*args, **kwargs)

	@MyUtilities.common.setDocstring(handle_Sizer.addImage)
	def addImage(self, *args, **kwargs):
		return self.mySizer.addImage(*args, **kwargs)

	@MyUtilities.common.setDocstring(handle_Sizer.addProgressBar)
	def addProgressBar(self, *args, **kwargs):
		return self.mySizer.addProgressBar(*args, **kwargs)

	@MyUtilities.common.setDocstring(handle_Sizer.addToolBar)
	def addToolBar(self, *args, **kwargs):
		return self.mySizer.addToolBar(*args, **kwargs)

	@MyUtilities.common.setDocstring(handle_Sizer.addPickerColor)
	def addPickerColor(self, *args, **kwargs):
		return self.mySizer.addPickerColor(*args, **kwargs)

	@MyUtilities.common.setDocstring(handle_Sizer.addPickerFont)
	def addPickerFont(self, *args, **kwargs):
		return self.mySizer.addPickerFont(*args, **kwargs)

	@MyUtilities.common.setDocstring(handle_Sizer.addPickerFile)
	def addPickerFile(self, *args, **kwargs):
		return self.mySizer.addPickerFile(*args, **kwargs)

	@MyUtilities.common.setDocstring(handle_Sizer.addPickerFileWindow)
	def addPickerFileWindow(self, *args, **kwargs):
		return self.mySizer.addPickerFileWindow(*args, **kwargs)

	@MyUtilities.common.setDocstring(handle_Sizer.addPickerTime)
	def addPickerTime(self, *args, **kwargs):
		return self.mySizer.addPickerTime(*args, **kwargs)

	@MyUtilities.common.setDocstring(handle_Sizer.addPickerDate)
	def addPickerDate(self, *args, **kwargs):
		return self.mySizer.addPickerDate(*args, **kwargs)

	@MyUtilities.common.setDocstring(handle_Sizer.addPickerDateWindow)
	def addPickerDateWindow(self, *args, **kwargs):
		return self.mySizer.addPickerDateWindow(*args, **kwargs)

	@MyUtilities.common.setDocstring(handle_Sizer.addCanvas)
	def addCanvas(self, *args, **kwargs):
		return self.mySizer.addCanvas(*args, **kwargs)

	@MyUtilities.common.setDocstring(handle_Sizer.addTable)
	def addTable(self, *args, **kwargs):
		return self.mySizer.addTable(*args, **kwargs)

	@MyUtilities.common.setDocstring(handle_Sizer.addSplitterDouble)
	def addSplitterDouble(self, *args, **kwargs):
		return self.mySizer.addSplitterDouble(*args, **kwargs)

	@MyUtilities.common.setDocstring(handle_Sizer.addSplitterQuad)
	def addSplitterQuad(self, *args, **kwargs):
		return self.mySizer.addSplitterQuad(*args, **kwargs)

	@MyUtilities.common.setDocstring(handle_Sizer.addSplitterPoly)
	def addSplitterPoly(self, *args, **kwargs):
		return self.mySizer.addSplitterPoly(*args, **kwargs)

	@MyUtilities.common.setDocstring(handle_Sizer.addNotebook)
	def addNotebook(self, *args, **kwargs):
		return self.mySizer.addNotebook(*args, **kwargs)

	@MyUtilities.common.setDocstring(handle_Sizer.addNotebookAui)
	def addNotebookAui(self, *args, **kwargs):
		return self.mySizer.addNotebookAui(*args, **kwargs)

	@MyUtilities.common.setDocstring(handle_Sizer.addSizerBox)
	def addSizerBox(self, *args, **kwargs):
		return self.mySizer.addSizerBox(*args, **kwargs)

	@MyUtilities.common.setDocstring(handle_Sizer.addSizerText)
	def addSizerText(self, *args, **kwargs):
		return self.mySizer.addSizerText(*args, **kwargs)

	@MyUtilities.common.setDocstring(handle_Sizer.addSizerGrid)
	def addSizerGrid(self, *args, **kwargs):
		return self.mySizer.addSizerGrid(*args, **kwargs)

	@MyUtilities.common.setDocstring(handle_Sizer.addSizerGridFlex)
	def addSizerGridFlex(self, *args, **kwargs):
		return self.mySizer.addSizerGridFlex(*args, **kwargs)

	@MyUtilities.common.setDocstring(handle_Sizer.addSizerGridBag)
	def addSizerGridBag(self, *args, **kwargs):
		return self.mySizer.addSizerGridBag(*args, **kwargs)

	@MyUtilities.common.setDocstring(handle_Sizer.addSizerWrap)
	def addSizerWrap(self, *args, **kwargs):
		return self.mySizer.addSizerWrap(*args, **kwargs)

class handle_Dialog(handle_Base):
	"""A handle for working with a wxDialog widget.

	Modified code from: https://www.blog.pythonlibrary.org/2010/06/26/the-dialogs-of-wxpython-part-1-of-2/
	Modified code from: https://www.blog.pythonlibrary.org/2010/07/10/the-dialogs-of-wxpython-part-2-of-2/
	Modified code from: http://zetcode.com/wxpython/dialogs/
	"""

	def __init__(self):
		"""Initializes defaults."""

		#Initialize inherited classes
		handle_Base.__init__(self)

		#Defaults
		self.data = None
		self.answer = None
		self.subType = None
		self.timeEntered = None
		self.inMainThread = True
		self.childrenDialogs = set()

	def __enter__(self):
		"""Allows the user to use a with statement to build the GUI."""

		handle = handle_Base.__enter__(self)

		handle_Dialog.show(self)

		#Hiding a sub-busy window too quickly can cause the parent busy window to go behind everything
		if (self.type is Types.busy):
			self.timeEntered = time.perf_counter()

			if (self.freeze):
				if (self.parent.thing.IsFrozen()):
					#Do not thaw the parent if it is already frozen
					self.freeze = None
				else:
					self.parent.thing.Freeze()

			if (self.cursor):
				if (wx.IsBusy()):
					#Do not stop the busy cursor if it was already going
					self.cursor = None
				else:
					wx.BeginBusyCursor()

		return handle

	def __exit__(self, exc_type, exc_value, traceback):
		"""Allows the user to use a with statement to build the GUI."""

		state = handle_Base.__exit__(self, exc_type, exc_value, traceback)

		if (self.type is Types.busy):
			difference = time.perf_counter() - self.timeEntered
			if (difference < 0.05):
				#Wait for a maximum of 0.05 seconds
				time.sleep(0.05 - difference)
			
			self.hide()

			if (self.cursor):
				wx.EndBusyCursor()

			if (self.freeze):
				self.parent.thing.Thaw()

		return state

	def _build(self, argument_catalogue):
		"""Determiens which build system to use for this handle."""

		def _build_message():
			"""Builds a wx message dialog object."""
			nonlocal self, argument_catalogue

			#Gather variables
			text, title = self._getArguments(argument_catalogue, ["text", "title"])
			stayOnTop, default, icon = self._getArguments(argument_catalogue, ["stayOnTop", "default", "icon"])
			addYes, addOk, addCancel, addHelp = self._getArguments(argument_catalogue, ["addYes", "addOk", "addCancel", "addHelp"])

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
			if (icon is not None):
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
			self.thing = wx.MessageDialog(parent = None, message = text, caption = title, style = eval(style, {'__builtins__': None, "wx": wx}, {}))

		def _build_scroll():
			"""Builds a wx scroll dialog object."""
			nonlocal self, argument_catalogue

			text, title = self._getArguments(argument_catalogue, ["text", "title"])
			self.thing = wx.lib.dialogs.ScrolledMessageDialog(None, text, title)

		def _build_busy():
			"""Builds a wx busy info dialog object."""
			nonlocal self, argument_catalogue

			text, simple, blockAll, cursor, freeze = self._getArguments(argument_catalogue, ["text", "simple", "blockAll", "cursor", "freeze"])

			self.thing = -1
			self.cursor = cursor
			self.freeze = freeze
			self.blockAll = blockAll

			if (self.parent is None):
				parent = None
			else:
				parent = self.parent.thing

			if (simple):
				self.subType = "simple"
				self.buildArgs = [text]
				self.buildKwargs = {"parent": parent}

				self.progress = None
			else:
				maximum, title, autoHide, can_abort, can_skip, stayOnTop = self._getArguments(argument_catalogue, ["maximum", "title", "autoHide", "can_abort", "can_skip", "stayOnTop"])
				smooth, elapsedTime, estimatedTime, remainingTime, initial = self._getArguments(argument_catalogue, ["smooth", "elapsedTime", "estimatedTime", "remainingTime", "initial"])
				
				title = title or text or "Busy"

				self.text = text
				self.oneShot = None
				self.progress = initial

				if (maximum is None):
					self.startPulse = True
					maximum = 100
				else:
					self.startPulse = False

				self.subType = "progress"
				self.buildArgs = [title, text]
				self.buildKwargs = {"maximum": maximum, "parent": parent}

				self.buildStyle = []
				if (blockAll):
					self.buildStyle.append("wx.PD_APP_MODAL")
				if (autoHide):
					self.buildStyle.append("wx.PD_AUTO_HIDE")
				if (smooth):
					self.buildStyle.append("wx.PD_SMOOTH")
				if (can_abort):
					self.buildStyle.append("wx.PD_CAN_ABORT")
				if (can_skip):
					self.buildStyle.append("wx.PD_CAN_SKIP")
				if (elapsedTime):
					self.buildStyle.append("wx.PD_ELAPSED_TIME")
				if (estimatedTime):
					self.buildStyle.append("wx.PD_ESTIMATED_TIME")
				if (remainingTime):
					self.buildStyle.append("wx.PD_REMAINING_TIME")
				# if (stayOnTop):
				# 	self.buildStyle.append("wx.STAY_ON_TOP")

				if (not self.buildStyle):
					self.buildStyle.append("0")

		def _build_inputBox():
			"""Builds a wx text entry dialog object."""
			nonlocal self, argument_catalogue

			text, title, default = self._getArguments(argument_catalogue, ["text", "title", "default"])
			addYes, addOk, addCancel, addHelp = self._getArguments(argument_catalogue, ["addYes", "addOk", "addCancel", "addHelp"])
			password, readOnly, tab, wrap, maximum = self._getArguments(argument_catalogue, ["password", "readOnly", "tab", "wrap", "maximum"])

			#Prepare styles
			style = "wx.CENTRE"

			##Buttons
			if (addYes):
				style += "|wx.YES_NO"
			if (addOk):
				style += "|wx.OK"
			if (addCancel):
				style += "|wx.CANCEL"
			if (addHelp):
				style += "|wx.HELP"

			if (password):
				style += "|wx.TE_PASSWORD"
			if (readOnly):
				style += "|wx.TE_READONLY"
			if (tab):
				style += "|wx.TE_PROCESS_TAB"
			
			if (wrap is not None):
				if (wrap > 0):
					style += "|wx.TE_MULTILINE|wx.TE_WORDWRAP"
				else:
					style += "|wx.TE_CHARWRAP|wx.TE_MULTILINE"

			self.thing = wx.TextEntryDialog(None, text, caption = title, value = default, style = eval(style, {'__builtins__': None, "wx": wx}, {}))

			if (maximum is not None):
				self.thing.SetMaxLength(maximum)

		def _build_choice():
			"""Builds a wx choice dialog object."""
			nonlocal self, argument_catalogue

			choices, title, text, default = self._getArguments(argument_catalogue, ["choices", "title", "text", "default"])
			single, formatter = self._getArguments(argument_catalogue, ["single", "formatter"])
			
			#Ensure that the choices given are a list or tuple
			if (not isinstance(choices, (list, tuple, range))):
				choices = [choices]

			self.choices = choices

			#Format choices to display
			if (formatter):
				formattedChoices = [str(formatter(item)) for item in choices]
			else:
				formattedChoices = [str(item) for item in choices]

			
			if (single):
				self.subType = "single"
				self.thing = wx.SingleChoiceDialog(None, title, text, formattedChoices, wx.CHOICEDLG_STYLE)
			else:
				self.thing = wx.MultiChoiceDialog(None, text, title, formattedChoices, wx.CHOICEDLG_STYLE)

			if (default is not None):
				if (single):
					if (isinstance(default, (list, tuple, range, set))):
						if (len(default) == 0):
							default = 0
						else:
							default = default[0]

					if (isinstance(default, str)):
						if (default in choices):
							default = choices.index(default)
						
						elif (default in formattedChoices):
							default = formattedChoices.index(default)
						
						else:
							warnings.warn(f"{default} not in 'choices' {choices} for {self.__repr__()}", Warning, stacklevel = 2)
							default = 0

					self.thing.SetSelection(default)
				else:
					if (not isinstance(default, (list, tuple, range, set))):
						default = [default]

					defaultList = []
					for i in range(len(default)):
						if (not isinstance(default[i], int)):
							if (default[i] in choices):
								default[i] = choices.index(default[i])

							elif (default[i] in formattedChoices):
								default[i] = formattedChoices.index(default[i])

							else:
								warnings.warn(f"{default[i]} not in 'choices' {choices} for {self.__repr__()}", Warning, stacklevel = 2)
								default[i] = 0

					self.thing.SetSelections(default)

		def _build_file():
			"""Builds a wx color dialog object."""
			nonlocal self, argument_catalogue

			title, text, preview, initialFile, wildcard = self._getArguments(argument_catalogue, ["title", "text", "preview", "initialFile", "wildcard"])
			initialDir, directoryOnly, changeCurrentDirectory = self._getArguments(argument_catalogue, ["initialDir", "directoryOnly", "changeCurrentDirectory"])
			fileMustExist, openFile, saveConfirmation, saveFile = self._getArguments(argument_catalogue, ["fileMustExist", "openFile", "saveConfirmation", "saveFile"])
			single, newDirButton = self._getArguments(argument_catalogue, ["single", "newDirButton"])

			#Picker configurations
			if (directoryOnly):
				##Determine which configurations to add
				style = "wx.RESIZE_BORDER|" #Always select the newer directory dialog if there are more than one choices
				if (changeCurrentDirectory):
					style += "wx.DD_CHANGE_DIR|"
				if (fileMustExist):
					style += "wx.DD_DIR_MUST_EXIST|"
				
				if (not single):
					agwStyle = "wx.lib.agw.multidirdialog.DD_MULTIPLE|"
					if (newDirButton):
						agwStyle += "wx.lib.agw.multidirdialog.DD_NEW_DIR_BUTTON|"
					if (fileMustExist):
						agwStyle += "wx.lib.agw.multidirdialog.DD_DIR_MUST_EXIST|"

					if (agwStyle != ""):
						agwStyle = agwStyle[:-1]
			else:
				style = ""
				##Make sure conflicting configurations are not given
				if ((openFile or fileMustExist) and (saveFile or saveConfirmation)):
					errorMessage = "Open config and save config cannot be added to the same file picker"
					raise SyntaxError(errorMessage)

				if (changeCurrentDirectory and ((openFile or fileMustExist or saveFile or saveConfirmation))):
					errorMessage = "Open config and save config cannot be used in combination with a directory change"
					raise SyntaxError(errorMessage)

				##Determine which configurations to add
				if (changeCurrentDirectory):
					style += "wx.FD_CHANGE_DIR|"
				if (fileMustExist):
					style += "wx.FD_FILE_MUST_EXIST|"
				if (openFile):
					style += "wx.FD_OPEN|"
				if (saveConfirmation):
					style += "wx.FD_OVERWRITE_PROMPT|"
				if (saveFile):
					style += "wx.FD_SAVE|"
				if (preview):
					style += "wx.FD_PREVIEW|"
				if (not single):
					style += "wx.FD_MULTIPLE|"

			if (style != ""):
				style = style[:-1]
			else:
				if (directoryOnly):
					style = "wx.DD_DEFAULT_STYLE"
				else:
					style = "wx.FD_DEFAULT_STYLE"

			if (initialDir is None):
				initialDir = ""

			if (initialFile is None):
				initialFile = ""

			wildcard = self.getWildcard(wildcard)

			#Create the thing to put in the grid
			if (directoryOnly):
				if (single):
					self.subType = "directory_single"
					self.thing = wx.DirDialog(None, message = text, defaultPath = initialDir, style = eval(style, {'__builtins__': None, "wx": wx}, {}))
				else:
					self.subType = "directory"
					self.thing = wx.lib.agw.multidirdialog.MultiDirDialog(None, message = text, title = title, defaultPath = initialDir, style = eval(style, {'__builtins__': None, "wx": wx}, {}), agwStyle  = eval(agwStyle, {'__builtins__': None, "wx": wx}, {}))
			else:
				if (single):
					self.subType = "file_single"
				else:
					self.subType = "file"
				self.thing = wx.FileDialog(None, message = text, defaultDir = initialDir, defaultFile = initialFile, wildcard = wildcard, style = eval(style, {'__builtins__': None, "wx": wx}, {}))

		def _build_color():
			"""Builds a wx color dialog object."""
			nonlocal self, argument_catalogue

			simple = self._getArguments(argument_catalogue, ["simple"])

			if (simple is not None):
				self.subType = "simple"
				self.thing = wx.ColourDialog(None)
				self.thing.GetColourData().SetChooseFull(not simple)
			else:
				self.thing = wx.lib.agw.cubecolourdialog.CubeColourDialog(None)

		def _build_pageSetup():
			"""Builds a wx page setup dialog object."""
			nonlocal self, argument_catalogue

			marginMinimum = self._getArguments(argument_catalogue, ["marginMinimum"])
			printData, helpButton, printOverride = self._getArguments(argument_catalogue, ["printData", "helpButton", "printOverride"])
			marginLeft, marginTop, marginRight, marginBottom = self._getArguments(argument_catalogue, ["marginLeft", "marginTop", "marginRight", "marginBottom"])
			editMargins, editOrientation, editPaper, editPrinter = self._getArguments(argument_catalogue, ["editMargins", "editOrientation", "editPaper", "editPrinter"])
			marginLeftMinimum, marginTopMinimum, marginRightMinimum, marginBottomMinimum = self._getArguments(argument_catalogue, ["marginLeftMinimum", "marginTopMinimum", "marginRightMinimum", "marginBottomMinimum"])

			overrideData = {"marginMinimum": marginMinimum, "marginLeft": marginLeft, 
				"marginTop": marginTop, "marginRight": marginRight, "marginBottom": marginBottom, "marginLeftMinimum": marginLeftMinimum, 
				"marginTopMinimum": marginTopMinimum, "marginRightMinimum": marginRightMinimum, "marginBottomMinimum": marginBottomMinimum} 
			combinedOverride = {key: value for catalogue in (printOverride, overrideData) for key, value in catalogue.items() if (value is not None)}

			if (printData is None):
				printData = combinedOverride
			dialogData = self._encodePrintSettings(printData, setupData = True, override = combinedOverride)

			dialogData.EnableHelp(helpButton)
			dialogData.EnableMargins(editMargins)
			dialogData.EnableOrientation(editOrientation)
			dialogData.EnablePaper(editPaper)
			dialogData.EnablePrinter(editPrinter)

			self.thing = wx.PageSetupDialog(None, dialogData)

		def _build_print():
			"""Builds a wx print dialog object."""
			nonlocal self, argument_catalogue

			pageFrom, pageTo, pageMin, pageMax = self._getArguments(argument_catalogue, ["pageFrom", "pageTo", "pageMin", "pageMax"])
			printToFile, selection, collate, copies = self._getArguments(argument_catalogue, ["printToFile", "selection", "collate", "copies"])
			printData, pageNumbers, helpButton, printOverride = self._getArguments(argument_catalogue, ["printData", "pageNumbers", "helpButton", "printOverride"])
			
			overrideData = {"collate": collate, "copies": copies, "from": pageFrom, "to": pageTo, 
				"min": pageMin, "max": pageMax, "printToFile": printToFile, "selected": selection}
			combinedOverride = {key: value for catalogue in (printOverride, overrideData) for key, value in catalogue.items() if (value is not None)}
			
			if (printData is None):
				printData = combinedOverride
			dialogData = self._encodePrintSettings(printData, override = combinedOverride)
			
			dialogData.EnableHelp(helpButton)
			dialogData.EnablePageNumbers(pageNumbers)
			dialogData.EnableSelection(dialogData.GetSelection())
			dialogData.EnablePrintToFile(dialogData.GetPrintToFile())
				
			self.thing = wx.PrintDialog(None, dialogData)

			self.title = "GUI_Maker Page"
			self.content = None

		def _build_printPreview():
			"""Builds a wx print preview dialog object."""
			nonlocal self, argument_catalogue

			self.thing = -1
			printData, printerSetup, printOverride, size, position, content = self._getArguments(argument_catalogue, ["printData", "printerSetup", "printOverride", "size", "position", "content"])

			#Set Defaults
			self.size = size
			self.content = content
			self.position = position
			self.printData = printData
			self.title = "GUI_Maker Page"
			self.printerSetup = printerSetup
			self.printOverride = printOverride

		def _build_custom():
			"""Uses a frame to mimic a wx dialog object."""
			nonlocal self, argument_catalogue

			myFrame, valueLabel = self._getArguments(argument_catalogue, ["myFrame", "valueLabel"])
			self.thing = -1
			self.myFrame = myFrame

			if (valueLabel is None):
				valueLabel = myFrame.getValueLabel()
			self.valueLabel = valueLabel
		
		#########################################################

		argument_catalogue["hidden"] = False
		argument_catalogue["enabled"] = True
		self._preBuild(argument_catalogue)

		if (self.type is Types.message):
			_build_message()
		elif (self.type is Types.process):
			_build_process()
		elif (self.type is Types.scroll):
			_build_scroll()
		elif (self.type is Types.box):
			_build_inputBox()
		elif (self.type is Types.custom):
			_build_custom()
		elif (self.type is Types.busy):
			_build_busy()
		elif (self.type is Types.color):
			_build_color()
		elif (self.type is Types.file):
			_build_file()
		elif (self.type is Types.font):
			_build_font()
		elif (self.type is Types.image):
			_build_image()
		elif (self.type is Types.list):
			_build_list()
		elif (self.type is Types.choice):
			_build_choice()
		elif (self.type is Types.print):
			_build_print()
		elif (self.type is Types.printsetup):
			_build_pageSetup()
		elif (self.type is Types.printpreview):
			_build_printPreview()
		else:
			warnings.warn(f"Add {self.type.name} to _build() for {self.__repr__()}", Warning, stacklevel = 2)

		self._postBuild(argument_catalogue)

	def threadSafe(self, function, *args, **kwargs):
		if (self.inMainThread):
			return function(*args, **kwargs)
		wx.CallAfter(function, *args, **kwargs)

	def show(self):
		"""Shows the dialog box for this handle."""

		#Error Check
		if (self.thing is None):
			warnings.warn(f"The {self.type} dialogue box {self.__repr__()} has already been shown", Warning, stacklevel = 2)
			return

		if (not wx.IsMainThread()):
			if (self.type is Types.busy):
				self.inMainThread = False
			else:
				errorMessage = f"The {self.type} dialogue box {self.__repr__()} must be shown in the main thread, not a background thread"
				raise SyntaxError(errorMessage)
				# warnings.warn(errorMessage, Warning, stacklevel = 2)
				# return

		#Pause background functions
		raise NotImplementedError()
		for listener in self.controller.threadManager.pauseOnDialog:
			if ((self.label is None) or (self.label not in listener.pauseOnDialog_exclude)):
				listener.pause = True

		#Show dialogue
		if (self.type is Types.message):
			self.answer = self.thing.ShowModal()
			self.hide()

		elif (self.type is Types.box):
			self.answer = self.thing.ShowModal()
			self.hide()

		elif (self.type is Types.choice):
			self.answer = self.thing.ShowModal()
			self.hide()

		elif (self.type is Types.scroll):
			self.answer = self.thing.ShowModal()
			self.hide()

		elif (self.type is Types.custom):
			self.myFrame.myDialog = self

			self.myFrame.runMyFunction(self.myFrame.preShowFunction, self.myFrame.preShowFunctionArgs, self.myFrame.preShowFunctionKwargs, includeEvent = True)
			self.myFrame.runMyFunction(self.myFrame.postShowFunction, self.myFrame.postShowFunctionArgs, self.myFrame.postShowFunctionKwargs, includeEvent = True)

			self.myFrame.visible = True
			self.answer = self.myFrame.thing.ShowModal()
			self.hide()

		elif (self.type is Types.busy):
			#Hiding a sub-busy window in a thread can cause the parent busy window to go behind everything 
			#if the top window is not the parent during creation
			oldTopLevel = None
			if (isinstance(self.parent, handle_Dialog)):
				self.parent.childrenDialogs.add(self)

				if (not self.inMainThread):
					oldTopLevel = wx.GetApp().GetTopWindow()
					wx.GetApp().SetTopWindow(self.parent.thing)

			#Create the dialog now
			if (self.subType.lower() == "simple"):
				self.thing = wx.BusyInfo(*self.buildArgs, **self.buildKwargs)
			else:
				self.thing = wx.ProgressDialog(*self.buildArgs, **self.buildKwargs, style = eval("|".join(self.buildStyle), {'__builtins__': None, "wx": wx}, {}))

				#Account for nested children
				# self.thing.Bind(wx.EVT_CLOSE, self._onCloseChildren)

				# for myId in [self.thing.GetAffirmativeId()]:
				# 	child = self.thing.FindWindowById(myId)
				# 	print("@1", child)
				# 	if (child is None):
				# 		continue
				# 	child.Bind(wx.EVT_BUTTON, self._onCloseChildren)

				if (self.startPulse):
					self.setValue()

			#Put the top window back after creation
			if (oldTopLevel is not None):
				wx.GetApp().SetTopWindow(oldTopLevel)

		elif (self.type is Types.file):
			self.answer = self.thing.ShowModal()
			self.hide()

		elif (self.type is Types.color):
			self.answer = self.thing.ShowModal()
			self.hide()

		elif (self.type is Types.print):
			self.answer = self.thing.ShowModal()
			self.hide()

		elif (self.type is Types.printsetup):
			self.answer = self.thing.ShowModal()
			self.hide()

		elif (self.type is Types.printpreview):
			pass

		else:
			warnings.warn(f"Add {self.type.name} to show() for {self.__repr__()}", Warning, stacklevel = 2)

	def hide(self):
		"""Hides the dialog box for this handle."""

		if (self.type is Types.busy):
			if (self.subType.lower() == "simple"):
				del self.thing
			else:
				if (isinstance(self.parent, handle_Dialog)):
					self.parent.childrenDialogs.discard(self)

				#The dialog will not close until this condition is met
				maximum = self.thing.GetRange()
				if (self.thing.GetValue() < maximum):
					self.setValue(maximum)

				self.threadSafe(self.thing.Destroy)

			self.thing = None
			# if (self.blockAll):
			# 	self.windowDisabler = None

		elif (self.type is Types.printpreview):
			self.thing = None

		elif (self.type is Types.message):
			self.thing.Destroy()
			self.thing = None

		elif (self.type is Types.box):
			self.data = self.thing.GetValue()

			self.thing.Destroy()
			self.thing = None

		elif (self.type is Types.choice):
			if ((self.subType is not None) and (self.subType.lower() == "single")):
				self.data = self.thing.GetSelection()
			else:
				self.data = self.thing.GetSelections()

			self.thing.Destroy()
			self.thing = None

		elif (self.type is Types.scroll):
			self.thing.Destroy()
			self.thing = None

		elif (self.type is Types.custom):
			if ((self.answer == wx.ID_CANCEL) and (len(self.myFrame.cancelFunction) != 0)):
				self.myFrame.runMyFunction(self.myFrame.cancelFunction, self.myFrame.cancelFunctionArgs, self.myFrame.cancelFunctionKwargs, includeEvent = True)

			self.myFrame.runMyFunction(self.myFrame.preHideFunction, self.myFrame.preHideFunctionArgs, self.myFrame.preHideFunctionKwargs, includeEvent = True)
			self.myFrame.runMyFunction(self.myFrame.postHideFunction, self.myFrame.postHideFunctionArgs, self.myFrame.postHideFunctionKwargs, includeEvent = True)

			# self.myFrame.thing.Destroy() #Don't destroy it so it can appear again without the user calling addDialog() again. Time will tell if this is a bad idea or not
			self.thing = None
			self.myFrame.myDialog = None

		elif (self.type is Types.file):
			if ((self.subType is not None) and ("single" in self.subType.lower())):
				self.data = self.thing.GetPath()
			else:
				self.data = self.thing.GetPaths()

			self.thing.Destroy()
			self.thing = None

		elif (self.type is Types.color):
			self.data = self.thing.GetColourData()

			self.thing.Destroy()
			self.thing = None

		elif (self.type is Types.print):
			self.data = self._decodePrintSettings(self.thing.GetPrintDialogData())
			self.thing.Destroy()
			self.thing = None

		elif (self.type is Types.printsetup):
			self.data = self._decodePrintSettings(self.thing.GetPageSetupData())
			self.thing.Destroy()
			self.thing = None

		else:
			warnings.warn(f"Add {self.type.name} to hide() for {self.__repr__()}", Warning, stacklevel = 2)

		#Unpause background functions
		raise NotImplementedError()
		for listener in self.controller.threadManager.pauseOnDialog:
			if ((self.label is None) or (self.label not in listener.pauseOnDialog_exclude)):
				listener.pause = False

	def end(self, ok = None, cancel = None, close = None, yes = None, no = None, apply = None):
		"""Stops showing the custom window.
		This is meant to be used by a function other than the one that created the dialog.

		Example Input: end()
		Example Input: end(ok = True)
		"""

		if (ok):
			returnCode = wx.ID_OK
		elif (cancel):
			returnCode = wx.ID_CANCEL
		elif (close):
			returnCode = wx.ID_CLOSE
		elif (yes):
			returnCode = wx.ID_YES
		elif (no):
			returnCode = wx.ID_NO
		elif (apply):
			returnCode = wx.ID_APPLY
		else:
			returnCode = wx.ID_CANCEL

		self.myFrame.thing.EndModal(returnCode)

	#Getters
	def getValue(self, event = None):
		"""Returns what the contextual value is for the object associated with this handle."""

		if (self.type is Types.choice):
			if (self.data is None):
				value = None
			elif ((self.subType is not None) and (self.subType.lower() == "single")):
				value = self.choices[self.data]
			else:
				value = [self.choices[i] for i in self.data]

		elif (self.type is Types.box):
			value = self.data

		elif (self.type is Types.custom):
			if (self.valueLabel is None):
				if (self.valueLabel is None):
					errorMessage = f"In order to use getValue() for {self.__repr__()} 'valueLabel' cannot be None\nEither provide it in makeDialogCustom() for {self.__repr__()} or use setValueLabel() for {self.myFrame.__repr__()}"
					raise KeyError(errorMessage)
			else:
				if (self.valueLabel not in self.myFrame):
					errorMessage = f"There is no widget with the label {self.valueLabel} in {self.myFrame.__repr__()} for {self.__repr__()}"
					raise ValueError(errorMessage)

			value = self.myFrame.getValue(self.valueLabel)

		elif (self.type is Types.file):
			value = self.data

		elif (self.type is Types.busy):
			if (self.subType.lower() == "progress"):
				value = self.thing.GetValue()
				if (value == wx.NOT_FOUND):
					value = None
			else:
				value = None

		elif (self.type is Types.color):
			color = self.data.GetColour().Get()
			value = (color.Red(), color.Green(), color.Blue(), color.Alpha())

		elif (self.type is Types.print):
			value = {"content": self.content, **self.data} 

		elif (self.type is Types.printsetup):
			value = {**self.data} 

		elif (self.type is Types.printPreview):
			value = self.content

		else:
			warnings.warn(f"Add {self.type.name} to getValue() for {self.__repr__()}", Warning, stacklevel = 2)
			value = None

		return value

	def getIndex(self, event = None):
		"""Returns what the contextual value is for the object associated with this handle."""

		if (self.type is Types.choice):
			value = self.data

		else:
			warnings.warn(f"Add {self.type.name} to getIndex() for {self.__repr__()}", Warning, stacklevel = 2)
			value = None

		return value

	def getText(self, event = None):
		"""Returns what the contextual text is for the object associated with this handle."""

		if (self.type is Types.busy):
			if (self.subType.lower() == "progress"):
				value = self.thing.GetMessage()
			else:
				value = None
		else:
			warnings.warn(f"Add {self.type.name} to getText() for {self.__repr__()}", Warning, stacklevel = 2)
			value = None

		return value

	def getDefaultText(self, event = None):
		"""Returns what the contextual default text is for the object associated with this handle."""

		if (self.type is Types.busy):
			if (self.subType.lower() == "progress"):
				value = self.text
			else:
				value = None
		else:
			warnings.warn(f"Add {self.type.name} to getText() for {self.__repr__()}", Warning, stacklevel = 2)
			value = None

		return value

	def getMax(self, event = None):
		"""Returns what the contextual maximum is for the object associated with this handle."""

		if (self.type is Types.busy):
			if (self.subType.lower() == "progress"):
				value = self.thing.GetRange()
				if (value == wx.NOT_FOUND):
					value = None
			else:
				value = None

		else:
			warnings.warn(f"Add {self.type.name} to getMax() for {self.__repr__()}", Warning, stacklevel = 2)
			value = None

		return value

	def isOk(self):
		"""Returns if the closed dialog box answer was 'ok'."""

		if (self.answer == wx.ID_OK):
			return True
		return False

	def isCancel(self):
		"""Returns if the closed dialog box answer was 'cancel'."""

		if ((self.type is Types.busy) and (self.subType.lower() == "progress")):
			return self.thing.WasCancelled()

		if (self.answer == wx.ID_CANCEL):
			return True
		return False

	def isYes(self):
		"""Returns if the closed dialog box answer was 'yes'."""

		if (self.answer == wx.ID_YES):
			return True
		return False

	def isNo(self, event):
		"""Returns if the closed dialog box answer was 'no'."""

		if (self.answer == wx.ID_NO):
			return True
		return False

	def isApply(self, event):
		"""Returns if the closed dialog box answer was 'apply'."""

		if (self.answer == wx.ID_APPLY):
			return True
		return False

	def isClose(self, event):
		"""Returns if the closed dialog box answer was 'close'."""

		if (self.answer == wx.ID_CLOSE):
			return True
		return False

	def isSkip(self):
		"""Returns if the closed dialog box answer was 'skip'."""

		if ((self.type is Types.busy) and (self.subType.lower() == "progress")):
			return self.thing.WasSkipped()
		return False

	def isAbort(self):
		"""Returns if the closed dialog box answer was 'abort'."""

		if ((self.type is Types.busy) and (self.subType.lower() == "progress")):
			return self.thing.WasCancelled()
		return False

	def _onCloseChildren(self):
		"""Closes all children."""

		print("@2", self.childrenDialogs)

		for child in self.childrenDialogs:
			child.end(cancel = True)

	#Setters
	def _formatText(self, text):
		if (text is None):
			return self.text

		current = self.thing.GetMessage()
		if (self.oneShot is not None):
			if (current == self.oneShot):
				self.oneShot = None
				return self.text
			else:
				return self.oneShot

		if (str(text) == current):
			return ""
		return str(text)

	def setValue(self, value = None, text = "", oneShot = False, event = None):
		"""Sets the contextual value for the object associated with this handle to what the user supplies."""

		if (self.type is Types.print):
			self.content = value
		
		elif (self.type is Types.printpreview):
			self.content = value
		
		elif (self.type is Types.busy):
			if (self.subType.lower() == "progress"):
				text = self._formatText(text)
				self.progress = value

				if (value is None):
					self.answer = self.threadSafe(self.thing.Pulse, text)
				else:
					self.answer = self.threadSafe(self.thing.Update, value, text)

				if (oneShot):
					self.oneShot = text
		else:
			warnings.warn(f"Add {self.type.name} to setValue() for {self.__repr__()}", Warning, stacklevel = 2)
	
	def setText(self, text = "", oneShot = False, event = None):
		"""Sets the contextual text for the object associated with this handle to what the user supplies."""

		if (self.type is Types.busy):
			if (self.subType.lower() == "progress"):
				text = self._formatText(text)

				#Setting the value to zero causes the window to disappear
				if (self.progress is None):
					self.answer = self.threadSafe(self.thing.Pulse, text)
				else:
					self.answer = self.threadSafe(self.thing.Update, self.thing.GetValue() or 1, text)

				if (oneShot):
					self.oneShot = text
		else:
			warnings.warn(f"Add {self.type.name} to setText() for {self.__repr__()}", Warning, stacklevel = 2)

	def setDefaultText(self, text = "", apply = True, event = None):
		"""Sets the contextual default text for the object associated with this handle to what the user supplies."""

		self.text = text

		if (apply):
			self.setText(event = event)
	
	def setMax(self, value, event = None):
		"""Sets the contextual max for the object associated with this handle to what the user supplies."""

		if (self.type is Types.busy):
			if (self.subType.lower() == "progress"):
				self.threadSafe(self.thing.SetRange, value)
		else:
			warnings.warn(f"Add {self.type.name} to setMax() for {self.__repr__()}", Warning, stacklevel = 2)

	def setTitle(self, text = None, event = None):
		"""Sets the title."""

		if (self.type is Types.print):
			if (text is None):
				text = "GUI_Maker Page"
			self.title = text
		else:
			warnings.warn(f"Add {self.type.name} to setTitle() for {self.__repr__()}", Warning, stacklevel = 2)

	def setSize(self, size = None, event = None):
		"""Sets the size."""

		if (self.type is Types.print):
			self.size = size
		else:
			warnings.warn(f"Add {self.type.name} to setSize() for {self.__repr__()}", Warning, stacklevel = 2)

	#Etc
	def resume(self, size = None, event = None):
		"""Undoes the abort."""

		if (self.type is Types.busy):
			self.threadSafe(self.thing.Resume)
		else:
			warnings.warn(f"Add {self.type.name} to resume() for {self.__repr__()}", Warning, stacklevel = 2)

	def send(self, raw = False, printOverride = {}, event = None):
		"""Returns what the contextual valueDoes the contextual send command for the object associated with this handle.
		Modified code from: https://wiki.wxpython.org/Printing

		raw (bool) - Determines how the data is sent to the printer
			- If True: Sends the data as RAW
			- If False: Sends the data normally

		Example Input: send()
		Example Input: send(raw = True)
		"""

		if (self.type is Types.print):
			self.print(self.content, printData = self.data[None], title = self.title, raw = raw, printOverride = printOverride, popup = False)

		elif (self.type is Types.printpreview):
			printout = _MyPrintout(self, document = self.content, title = self.title, raw = raw)

			enablePrint = True
			if (enablePrint):
				preview = _MyPrintPreview(self, printout, printout.clone(), printData = self.printData, printerSetup = self.printerSetup, printOverride = {**printOverride, **self.printOverride})
			else:
				preview = _MyPrintPreview(self, printout, printData = self.printData, printerSetup = self.printerSetup, printOverride = {**printOverride, **self.printOverride})

			if ("__WXMAC__" in wx.PlatformInfo):
				preview.SetZoom(50)
			else:
				preview.SetZoom(35)

			if (not preview.IsOk()):
				warnings.warn(f"'printout' {printout.__repr__()} was not created correctly for {self.__repr__()}", Warning, stacklevel = 2)
				self.thing = None
				return

			previewFrame = _MyPreviewFrame(self, preview, None, title = "Print Preview", 
				pos = self.position or wx.DefaultPosition, size = self.size or wx.DefaultSize)

			image = self.getImage("print", internal = True, returnIcon = True)
			previewFrame.SetIcon(image)
			previewFrame.Initialize()


			# self.runMyFunction(self.preShowFunction, self.preShowFunctionArgs, self.preShowFunctionKwargs, includeEvent = True)
			previewFrame.Show()

			# self.runMyFunction(self.postShowFunction, self.postShowFunctionArgs, self.postShowFunctionKwargs, includeEvent = True)

		else:
			warnings.warn(f"Add {self.type.name} to send() for {self.__repr__()}", Warning, stacklevel = 2)

class _MyPrinter(wx.Printer):
	catalogue_printBin = {wx.PRINTBIN_DEFAULT: "default", wx.PRINTBIN_ONLYONE: "one", wx.PRINTBIN_LOWER: "lower",
		wx.PRINTBIN_MIDDLE: "middle", wx.PRINTBIN_MANUAL: "manual", wx.PRINTBIN_ENVELOPE: "envelope",
		wx.PRINTBIN_ENVMANUAL: "env_manual", wx.PRINTBIN_AUTO: "auto", wx.PRINTBIN_TRACTOR: "tractor",
		wx.PRINTBIN_SMALLFMT: "small", wx.PRINTBIN_LARGEFMT: "large", wx.PRINTBIN_LARGECAPACITY: "capacity",
		wx.PRINTBIN_CASSETTE: "cassette", wx.PRINTBIN_FORMSOURCE: "source", wx.PRINTBIN_USER: "user"}

	catalogue_duplex = {wx.DUPLEX_SIMPLEX: None, wx.DUPLEX_HORIZONTAL: True, wx.DUPLEX_VERTICAL: False}

	catalogue_printMode = {wx.PRINT_MODE_NONE: None, wx.PRINT_MODE_PREVIEW: "Preview in external application", 
		wx.PRINT_MODE_FILE: "Print to file", wx.PRINT_MODE_PRINTER: "Send to printer", 
		wx.PRINT_MODE_STREAM: "Send postscript data into a stream"}

	catalogue_quality = {wx.PRINT_QUALITY_HIGH: "High", wx.PRINT_QUALITY_MEDIUM: "Medium",
		wx.PRINT_QUALITY_LOW: "Low", wx.PRINT_QUALITY_DRAFT: "Draft"}

	catalogue_orientation = {wx.LANDSCAPE: False, wx.PORTRAIT: True}

	catalogue_paperId = {
		wx.PAPER_10X11: "10 x 11 in", 
		wx.PAPER_10X14: "10 x 14 in", 
		wx.PAPER_11X17: "11 x 17 in", 
		wx.PAPER_12X11: "12 x 11 in", 
		wx.PAPER_15X11: "15 x 11 in", 
		wx.PAPER_9X11: "9 x 11 in", 
		wx.PAPER_A2: "A2; 420 x 594 mm", 
		wx.PAPER_A3: "A3; 297 x 420 mm", 
		wx.PAPER_A3_EXTRA: "A3 Extra; 322 x 445 mm", 
		wx.PAPER_A3_EXTRA_TRANSVERSE: "A3 Extra Transverse; 322 x 445 mm", 
		wx.PAPER_A3_ROTATED: "A3 Rotated; 420 x 297 mm", 
		wx.PAPER_A3_TRANSVERSE: "A3 Transverse; 297 x 420 mm", 
		wx.PAPER_A4: "A4; 210 x 297 mm", 
		wx.PAPER_A4SMALL: "A4 Small; 210 x 297 mm", 
		wx.PAPER_A4_EXTRA: "A4 Extra; 9.27 x 12.69 in", 
		wx.PAPER_A4_PLUS: "A4 Plus; 210 x 330 mm", 
		wx.PAPER_A4_ROTATED: "A4 Rotated; 297 x 210 mm", 
		wx.PAPER_A4_TRANSVERSE: "A4 Transverse; 210 x 297 mm", 
		wx.PAPER_A5: "A5; 148 x 210 mm", 
		wx.PAPER_A5_EXTRA: "A5 Extra; 174 x 235 mm", 
		wx.PAPER_A5_ROTATED: "A5 Rotated; 210 x 148 mm", 
		wx.PAPER_A5_TRANSVERSE: "A5 Transverse; 148 x 210 mm", 
		wx.PAPER_A6: "A6; 105 x 148 mm", 
		wx.PAPER_A6_ROTATED: "A6 Rotated; 148 x 105 mm", 
		wx.PAPER_A_PLUS: "SuperA; 227 x 356 mm", 
		wx.PAPER_B4: "B4; 250 by 354 mm", 
		wx.PAPER_B4_JIS_ROTATED: "B4 (JIS) Rotated; 364 x 257 mm", 
		wx.PAPER_B5: "B5; 182 by 257 mm", 
		wx.PAPER_B5_EXTRA: "B5 (ISO) Extra; 201 x 276 mm", 
		wx.PAPER_B5_JIS_ROTATED: "B5 (JIS) Rotated; 257 x 182 mm", 
		wx.PAPER_B5_TRANSVERSE: "B5 (JIS) Transverse; 182 x 257 mm", 
		wx.PAPER_B6_JIS: "B6 (JIS); 128 x 182 mm", 
		wx.PAPER_B6_JIS_ROTATED: "B6 (JIS) Rotated; 182 x 128 mm", 
		wx.PAPER_B_PLUS: "SuperB; 305 x 487 mm", 
		wx.PAPER_CSHEET: "C; 17 by 22 in", 
		wx.PAPER_DBL_JAPANESE_POSTCARD: "Japanese Double Postcard; 200 x 148 mm", 
		wx.PAPER_DBL_JAPANESE_POSTCARD_ROTATED: "Double Japanese Postcard Rotated; 148 x 200 mm", 
		wx.PAPER_DSHEET: "D; 22 by 34 in", 
		wx.PAPER_ENV_10: "#10 Envelope; 4 1/8 by 9 1/2 in", 
		wx.PAPER_ENV_11: "#11 Envelope; 4 1/2 by 10 3/8 in", 
		wx.PAPER_ENV_12: "#12 Envelope; 4 3/4 by 11 in", 
		wx.PAPER_ENV_14: "#14 Envelope; 5 by 11 1/2 in", 
		wx.PAPER_ENV_9: "#9 Envelope; 3 7/8 by 8 7/8 in", 
		wx.PAPER_ENV_B4: "B4 Envelope; 250 by 353 mm", 
		wx.PAPER_ENV_B5: "B5 Envelope; 176 by 250 mm", 
		wx.PAPER_ENV_B6: "B6 Envelope; 176 by 125 mm", 
		wx.PAPER_ENV_C3: "C3 Envelope; 324 by 458 mm", 
		wx.PAPER_ENV_C4: "C4 Envelope; 229 by 324 mm", 
		wx.PAPER_ENV_C5: "C5 Envelope; 162 by 229 mm", 
		wx.PAPER_ENV_C6: "C6 Envelope; 114 by 162 mm", 
		wx.PAPER_ENV_C65: "C65 Envelope; 114 by 229 mm", 
		wx.PAPER_ENV_DL: "DL Envelope; 110 by 220 mm", 
		wx.PAPER_ENV_INVITE: "Envelope Invite; 220 x 220 mm", 
		wx.PAPER_ENV_ITALY: "Italy Envelope; 110 by 230 mm", 
		wx.PAPER_ENV_MONARCH: "Monarch Envelope; 3 7/8 by 7 1/2 mm", 
		wx.PAPER_ENV_PERSONAL: "6 3/4 Envelope; 3 5/8 by 6 1/2 in", 
		wx.PAPER_ESHEET: "E; 34 by 44 in", 
		wx.PAPER_EXECUTIVE: "Executive; 7 1/4 by 10 1/2 in", 
		wx.PAPER_FANFOLD_LGL_GERMAN: "German Legal Fanfold; 8 1/2 by 13 in", 
		wx.PAPER_FANFOLD_STD_GERMAN: "German Std Fanfold; 8 1/2 by 12 in", 
		wx.PAPER_FANFOLD_US: "US Std Fanfold; 14 7/8 by 11 in", 
		wx.PAPER_FOLIO: "Folio; 8 1/2 by 13 in.", 
		wx.PAPER_ISO_B4: "B4 (ISO); 250 x 353 mm", 
		wx.PAPER_JAPANESE_POSTCARD: "Japanese Postcard; 100 x 148 mm", 
		wx.PAPER_JAPANESE_POSTCARD_ROTATED: "Japanese Postcard Rotated; 148 x 100 mm", 
		wx.PAPER_JENV_CHOU3: "Japanese Envelope Chou #3", 
		wx.PAPER_JENV_CHOU3_ROTATED: "Japanese Envelope Chou #3 Rotated", 
		wx.PAPER_JENV_CHOU4: "Japanese Envelope Chou #4", 
		wx.PAPER_JENV_CHOU4_ROTATED: "Japanese Envelope Chou #4 Rotated", 
		wx.PAPER_JENV_KAKU2: "Japanese Envelope Kaku #2", 
		wx.PAPER_JENV_KAKU2_ROTATED: "Japanese Envelope Kaku #2 Rotated", 
		wx.PAPER_JENV_KAKU3: "Japanese Envelope Kaku #3", 
		wx.PAPER_JENV_KAKU3_ROTATED: "Japanese Envelope Kaku #3 Rotated", 
		wx.PAPER_JENV_YOU4: "Japanese Envelope You #4", 
		wx.PAPER_JENV_YOU4_ROTATED: "Japanese Envelope You #4 Rotated", 
		wx.PAPER_LEDGER: "Ledger; 17 by 11 in", 
		wx.PAPER_LEGAL: "Legal; 8 1/2 by 14 in", 
		wx.PAPER_LEGAL_EXTRA: "Legal Extra; 9.5 x 15 in", 
		wx.PAPER_LETTER: "Letter; 8 1/2 by 11 in", 
		wx.PAPER_LETTERSMALL: "Letter Small; 8 1/2 by 11 in", 
		wx.PAPER_LETTER_EXTRA: "Letter Extra; 9.5 x 12 in", 
		wx.PAPER_LETTER_EXTRA_TRANSVERSE: "Letter Extra Transverse; 9.5 x 12 in", 
		wx.PAPER_LETTER_PLUS: "Letter Plus; 8.5 x 12.69 in", 
		wx.PAPER_LETTER_ROTATED: "Letter Rotated; 11 x 8 1/2 in", 
		wx.PAPER_LETTER_TRANSVERSE: "Letter Transverse; 8.5 x 11 in", 
		wx.PAPER_NONE: "Use specific dimensions", 
		wx.PAPER_NOTE: "Note; 8 1/2 by 11 in", 
		wx.PAPER_P16K: "PRC 16K; 146 x 215 mm", 
		wx.PAPER_P16K_ROTATED: "PRC 16K Rotated; 215 x 146 mm", 
		wx.PAPER_P32K: "PRC 32K; 97 x 151 mm", 
		wx.PAPER_P32KBIG: "PRC 32K(Big); 97 x 151 mm", 
		wx.PAPER_P32KBIG_ROTATED: "PRC 32K(Big) Rotated; 151 x 97 mm", 
		wx.PAPER_P32K_ROTATED: "PRC 32K Rotated; 157 x 97 mm", 
		wx.PAPER_PENV_1: "PRC Envelope #1; 102 x 165 mm", 
		wx.PAPER_PENV_10: "PRC Envelope #10; 324 x 458 mm", 
		wx.PAPER_PENV_10_ROTATED: "PRC Envelope #10 Rotated; 458 x 324 mm", 
		wx.PAPER_PENV_1_ROTATED: "PRC Envelope #1 Rotated; 165 x 102 mm", 
		wx.PAPER_PENV_2: "PRC Envelope #2; 102 x 176 mm", 
		wx.PAPER_PENV_2_ROTATED: "PRC Envelope #2 Rotated; 176 x 102 mm", 
		wx.PAPER_PENV_3: "PRC Envelope #3; 125 x 176 mm", 
		wx.PAPER_PENV_3_ROTATED: "PRC Envelope #3 Rotated; 176 x 125 mm", 
		wx.PAPER_PENV_4: "PRC Envelope #4; 110 x 208 mm", 
		wx.PAPER_PENV_4_ROTATED: "PRC Envelope #4 Rotated; 208 x 110 mm", 
		wx.PAPER_PENV_5: "PRC Envelope #5; 110 x 220 mm", 
		wx.PAPER_PENV_5_ROTATED: "PRC Envelope #5 Rotated; 220 x 110 mm", 
		wx.PAPER_PENV_6: "PRC Envelope #6; 120 x 230 mm", 
		wx.PAPER_PENV_6_ROTATED: "PRC Envelope #6 Rotated; 230 x 120 mm", 
		wx.PAPER_PENV_7: "PRC Envelope #7; 160 x 230 mm", 
		wx.PAPER_PENV_7_ROTATED: "PRC Envelope #7 Rotated; 230 x 160 mm", 
		wx.PAPER_PENV_8: "PRC Envelope #8; 120 x 309 mm", 
		wx.PAPER_PENV_8_ROTATED: "PRC Envelope #8 Rotated; 309 x 120 mm", 
		wx.PAPER_PENV_9: "PRC Envelope #9; 229 x 324 mm", 
		wx.PAPER_PENV_9_ROTATED: "PRC Envelope #9 Rotated; 324 x 229 mm", 
		wx.PAPER_QUARTO: "Quarto; 215 by 275 mm", 
		wx.PAPER_STATEMENT: "Statement; 5 1/2 by 8 1/2 in", 
		wx.PAPER_TABLOID: "Tabloid; 11 by 17 in", 
		wx.PAPER_TABLOID_EXTRA: "Tabloid Extra; 11.69 x 18 in", 
		} 

	def __init__(self, parent, data = None, override = {}):
		self.parent = parent
		
		dialogData = self.parent._encodePrintSettings(data, override = override)
		wx.Printout.__init__(self, dialogData)

	def Print(self, window, printout, prompt = True):
		"""Prints the printout given to it.
		Special thanks to Ben Croston for how to print RAW on https://pypi.org/project/zebra/
		"""

		if ((not hasattr(printout, "raw")) or (not printout.raw)):
			answer = super().Print(window, printout, prompt = prompt)
			if (not answer):
				wx.MessageBox(("There was a problem printing.\nPerhaps your current printer is \nnot set correctly ?"), ("Printing"), wx.OK)
			return answer
		if (prompt):
			if (not self.PrintDialog(window)):
				return False

		printerName = self.GetPrintDialogData().GetPrintData().GetPrinterName()
		printout.hPrinter = win32print.OpenPrinter(printerName)
		super().Print(window, printout, prompt = False)
		win32print.ClosePrinter(printout.hPrinter)

		return True

class _MyPrintPreview(wx.PrintPreview):
	def __init__(self, parent, *args, printData = None, printerSetup = True, printOverride = {}, **kwargs):

		self.parent = parent
		self.printerSetup = printerSetup
		self.printData = printData
		self.printOverride = printOverride

		printData = self.parent._encodePrintSettings(printData, override = printOverride)
		super().__init__(*args, data = printData, **kwargs)

	def Print(self, printerSetup):
		self.parent.print(self.GetPrintoutForPrinting(), printData = self.printData, popup = self.printerSetup)
		return True

class _MyPreviewFrame(wx.PreviewFrame):
	def __init__(self, parent, preview, stepParent, *args, **kwargs):
		super().__init__(preview, stepParent, *args, **kwargs)

		self.parent = parent
		self.preview = preview
		self.stepParent = stepParent

		self.Bind(wx.EVT_CLOSE, self.OnClose)

	def OnClose(self, event):
		if (self.parent is not None):
			self.parent.hide()
		event.Skip()

class _MyPrintout(wx.Printout):
	def __init__(self, parent, document = None, title = "GUI_Maker Page", pageTo = None, pageFrom = None, raw = None, wrapText = True):
		wx.Printout.__init__(self, title)

		self.raw = raw
		self.title = title
		self.parent = parent
		self.pageTo = pageTo
		self.pageFrom = pageFrom
		self.document = document
		self.hPrinter = None
		self.wrapText = wrapText

		#Ensure this runs first
		self.OnPreparePrinting()

	def SetRaw(self, state):
		self.raw = state

	def GetPageInfo(self):
		"""Handles how many pages are in the printout."""

		minPage = 1
		maxPage = len(self.document)
		pageFrom = self.pageFrom or minPage
		pageTo = self.pageTo or maxPage

		return (minPage, maxPage, pageFrom, pageTo)

	def HasPage(self, pageNumber):
		"""Determines if the given page is in the print out."""

		try:
			self.document[pageNumber]
			return True
		except Exception as error:
			return False

	def OnPreparePrinting(self):
		"""Ensures correct format of content."""

		if (not isinstance(self.document, (list, tuple, dict, set, types.GeneratorType))):
			self.document = {1: self.document}
		elif (not isinstance(self.document, dict)):
			self.document = {pageNumber + 1: page for pageNumber, page in enumerate(self.document)}

	def OnPrintPage(self, pageNumber):
		"""Arranges the stuff on the page.
		Special thanks to Ben Croston for how to print RAW on https://pypi.org/project/zebra/
		"""

		if (not self.HasPage(pageNumber)):
			return

		page = self.document[pageNumber]

		# if ((not self.GetPreview()) and (self.raw)):
		if (self.hPrinter):
			try:
				win32print.StartPagePrinter(self.hPrinter)
				try:
					win32print.WritePrinter(self.hPrinter, page)
				except TypeError:
					win32print.WritePrinter(self.hPrinter, str(page).encode())
			finally:
				win32print.EndPagePrinter(self.hPrinter)
			return True

		dc = self.GetDC()
		dc.SetMapMode(wx.MM_POINTS) #Each logical unit is a “printer point” i.e. 1/72 of an inch
		# dc.SetMapMode(wx.MM_TWIPS) #Each logical unit is 1/20 of a “printer point”, or 1/1440 of an inch

		## TO DO ## Add isinstance(page, something with a defined font and text)
		if (isinstance(page, str)):
			dc.SetTextForeground("black")
			dc.SetFont(wx.Font(11, wx.SWISS, wx.NORMAL, wx.BOLD))
			if (self.wrapText):
				text = wx.lib.wordwrap.wordwrap(page, dc.DeviceToLogicalX(dc.GetSize().width), dc)
			else:
				text = page
			dc.DrawText(text, 0, 0)

		elif (isinstance(page, handle_WidgetCanvas)):
			with page as myCanvas:
				myCanvas._draw(dc, modifyUnits = False)

		else:
			image = self.parent.getImage(page)
			dc.DrawBitmap(image, 0, 0)

		return True

	def OnBeginPrinting(self):
		if (self.hPrinter):
			win32print.StartDocPrinter(self.hPrinter, 1, (self.title, None, 'RAW'))

	def OnEndPrinting(self):
		if (self.hPrinter):
			win32print.EndDocPrinter(self.hPrinter)

	def clone(self):
		"""Returns a copy of itself as a separate instance."""

		return _MyPrintout(self.parent, document = self.document, title = self.title, pageTo = self.pageTo, pageFrom = self.pageFrom, raw = self.raw)

class handle_Window(handle_Container_Base):
	"""A handle for working with a wxWindow."""

	def __init__(self, controller):
		"""Initializes defaults."""

		#Initialize inherited classes
		handle_Container_Base.__init__(self)

		#Defaults
		self.myDialog = None
		self.mainPanel = None
		self.mainSizer = None
		self.thing = None
		self.visible = False
		self.complexity_total = 0
		self.complexity_max = 20
		self.controller = controller

		self.toolBarOn = True
		self.autoSize = True
		self.menuBar = None
		self.auiManager = None

		self.statusBar = None
		self.statusBarOn = True
		self.statusTextDefault = {}
		self.statusBar_autoWidth = None
		self.statusTextTimer = {"listening": 0, "stop": False}

		self.refreshFunction = []
		self.refreshFunctionArgs = []
		self.refreshFunctionKwargs = []

		self.cancelFunction = []
		self.cancelFunctionArgs = []
		self.cancelFunctionKwargs = []

		self.preShowFunction = []
		self.preShowFunctionArgs = []
		self.preShowFunctionKwargs = []
		self.postShowFunction = []
		self.postShowFunctionArgs = []
		self.postShowFunctionKwargs = []

		self.preHideFunction = []
		self.preHideFunctionArgs = []
		self.preHideFunctionKwargs = []
		self.postHideFunction = []
		self.postHideFunctionArgs = []
		self.postHideFunctionKwargs = []

		self.finalFunctionList = []
		self.finalFunctionCatalogue = {}
		self.sizersIterating = {} #Keeps track of which sizers have been used in a while loop, as well as if they are still in the while loop {sizer (handle): [currently in a while loop (bool), order entered (int)]}
		self.keyPressQueue = {} #A dictionary that contains all of the key events that need to be bound to this window
		self.toolTipCatalogue = {} #A dictionary that contains all of the tool tips for this window

	def __str__(self):
		"""Gives diagnostic information on the Window when it is printed out."""

		output = handle_Container_Base.__str__(self)
		
		if (self.mainPanel is not None):
			output += f"-- main panel id: {id(self.mainPanel)}\n"
		if (self.mainSizer is not None):
			output += f"-- main sizer id: {id(self.mainSizer)}\n"
		return output

	def _build(self, argument_catalogue):
		"""Determiens which build system to use for this handle."""

		def _build_frame():
			"""Builds a wx frame object."""
			nonlocal self, argument_catalogue

			#Determine window style
			tabTraversal, stayOnTop, floatOnParent, resize, topBar, minimize, maximize, close, title = self._getArguments(argument_catalogue, ["tabTraversal", "stayOnTop", "floatOnParent", "resize", "topBar", "minimize", "maximize", "close", "title"])
			style = [wx.CLIP_CHILDREN, wx.SYSTEM_MENU]
			if (tabTraversal):
				style.append(wx.TAB_TRAVERSAL)

			if (stayOnTop):
				style.append(wx.STAY_ON_TOP)

			if (floatOnParent):
				style.append(wx.FRAME_FLOAT_ON_PARENT)

			if (resize):
				style.append(wx.RESIZE_BORDER)

			if (topBar is not None):
				if (topBar):
					style.extend((wx.MINIMIZE_BOX, wx.MAXIMIZE_BOX, wx.CLOSE_BOX))
			else:
				if (minimize):
					style.append(wx.MINIMIZE_BOX)

				if (maximize):
					style.append(wx.MAXIMIZE_BOX)

				if (close):
					style.append(wx.CLOSE_BOX)

			if (title is not None):
				style.append(wx.CAPTION)
			else:
				title = ""

			#wx.FRAME_EX_CONTEXTHELP

			#Make the frame
			size, position, smallerThanScreen = self._getArguments(argument_catalogue, ["size", "position", "smallerThanScreen"])
			self.thing = wx.Frame(None, title = title, size = size, pos = position, style = functools.reduce(operator.ior, style or (0,)))

			# if (smallerThanScreen not in (None, False)):
			#   screenSize = self.getScreenSize()
			#   if (isinstance(smallerThanScreen, int)):
			#       self.thing.SetMaxSize(screenSize[smallerThanScreen])
			#   else:
			#       self.thing.SetMaxSize(map(sum, zip(*screenSize)))
			
			#Add Properties
			icon, internal = self._getArguments(argument_catalogue, ["icon", "internal"])
			if (icon is not None):
				self.setIcon(icon, internal)

			#Bind functions
			delFunction, delFunctionArgs, delFunctionKwargs = self._getArguments(argument_catalogue, ["delFunction", "delFunctionArgs", "delFunctionKwargs"])
			initFunction, initFunctionArgs, initFunctionKwargs = self._getArguments(argument_catalogue, ["initFunction", "initFunctionArgs", "initFunctionKwargs"])
			idleFunction, idleFunctionArgs, idleFunctionKwargs = self._getArguments(argument_catalogue, ["idleFunction", "idleFunctionArgs", "idleFunctionKwargs"])
			
			if (initFunction is not None):
				self.setFunction_init(initFunction, initFunctionArgs, initFunctionKwargs)

			if (delFunction is not None):
				self.setFunction_close(delFunction, delFunctionArgs, delFunctionKwargs)
			else:
				endProgram = self._getArguments(argument_catalogue, ["endProgram"])
				if (endProgram is not None):
					if (endProgram):
						delFunction = self.controller.onExit
					else:
						delFunction = self.controller.onQuit
				else:
					delFunction = self.onHideWindow

				self.setFunction_close(delFunction)

			if (idleFunction is not None):
				self.idleQueue = None
				self._betterBind(wx.EVT_IDLE, self.thing, idleFunction, idleFunctionArgs, idleFunctionKwargs)
			else:
				self._betterBind(wx.EVT_IDLE, self.thing, self.controller.onIdle)

			#Unpack arguments
			panel = argument_catalogue["panel"]
			
			#Setup sizers and panels
			if (panel):
				self.mainPanel = self._makePanel()#"-1", parent = handle, size = (10, 10), tabTraversal = tabTraversal, useDefaultSize = False)
				self._finalNest(self.mainPanel)

			self.mainSizer = self._makeSizerBox()
			self._finalNest(self.mainSizer)

			if (panel):
				self.mainPanel.thing.SetSizer(self.mainSizer.thing)
				# self.mainPanel.thing.SetAutoLayout(True)
				# self.mainSizer.thing.Fit(self.mainPanel.thing)
			else:
				self.thing.SetSizer(self.mainSizer.thing)
				# self.thing.SetAutoLayout(True)
				# self.mainSizer.thing.Fit(self.thing)

		def _build_dialog():
			"""Builds a wx dialog object."""
			nonlocal self, argument_catalogue

			tabTraversal, stayOnTop, resize, title = self._getArguments(argument_catalogue, ["tabTraversal", "stayOnTop", "resize", "title"])
			topBar, minimize, maximize, close = self._getArguments(argument_catalogue, ["topBar", "minimize", "maximize", "close"])
			size, position, panel, valueLabel = self._getArguments(argument_catalogue, ["size", "position", "panel", "valueLabel"])
			addYes, addNo, addOk, addCancel, addClose, addApply, addLine = self._getArguments(argument_catalogue, ["addYes", "addNo", "addOk", "addCancel", "addClose", "addApply", "addLine"])
			icon, internal, smallerThanScreen = self._getArguments(argument_catalogue, ["icon", "internal", "smallerThanScreen"])
			
			#Configure Style
			style = [wx.SYSTEM_MENU]

			if (stayOnTop):
				style.append(wx.STAY_ON_TOP)

			# if (helpButton):
			#   style.append(wx.DIALOG_EX_CONTEXTHELP)

			if (resize):
				style.append(wx.RESIZE_BORDER)

			if (topBar is not None):
				if (topBar):
					style.extend((wx.MINIMIZE_BOX, wx.MAXIMIZE_BOX, wx.CLOSE_BOX))
			else:
				if (minimize):
					style.append(wx.MINIMIZE_BOX)

				if (maximize):
					style.append(wx.MAXIMIZE_BOX)

				if (close):
					style.append(wx.CLOSE_BOX)

			if (title is not None):
				style.append(wx.CAPTION)
			else:
				title = ""

			#Create Object
			self.thing = wx.Dialog(None, title = title, size = size, pos = position, style = functools.reduce(operator.ior, style or (0,)))

			if (smallerThanScreen not in (None, False)):
				if (isinstance(smallerThanScreen, bool)):
					screenSize = self.getScreenSize()
				else:
					screenSize = self.getScreenSize(number = smallerThanScreen)
				self.thing.SetMaxSize(screenSize)

			#Set Properties
			if (icon is not None):
				self.setIcon(icon, internal)

			#Remember Values
			self.valueLabel = valueLabel

			#Bind functions
			delFunction, delFunctionArgs, delFunctionKwargs = self._getArguments(argument_catalogue, ["delFunction", "delFunctionArgs", "delFunctionKwargs"])
			initFunction, initFunctionArgs, initFunctionKwargs = self._getArguments(argument_catalogue, ["initFunction", "initFunctionArgs", "initFunctionKwargs"])
			
			if (initFunction is not None):
				self.setFunction_init(initFunction, initFunctionArgs, initFunctionKwargs)

			if (delFunction is not None):
				self.setFunction_close(delFunction, delFunctionArgs, delFunctionKwargs)
			
			#Setup sizers and panels
			if (panel):
				self.mainPanel = self._makePanel()#"-1", parent = handle, size = (10, 10), tabTraversal = tabTraversal, useDefaultSize = False)
				self._finalNest(self.mainPanel)

			with self._makeSizerBox() as rootSizer:
				self._finalNest(rootSizer)
				self.mainSizer = rootSizer.addSizerBox(flex = 1)

				if (addLine):
					rootSizer.addLine(flex = 0)

				with rootSizer.addSizerBox(vertical = False, flex = 0) as buttonSizer:
					if (not isinstance(addYes, (bool, type(None)))):
						self._addAttributeOverride(addYes, "myId", wx.ID_YES)
					elif (addYes):
						buttonSizer.addButton("Yes", myId = wx.ID_YES)

					if (not isinstance(addNo, (bool, type(None)))):
						self._addAttributeOverride(addNo, "myId", wx.ID_NO)
					elif (addNo or ((addYes not in [False, None]) and (addNo is None))):
						buttonSizer.addButton("No", myId = {"myId": wx.ID_NO})

					if (not isinstance(addOk, (bool, type(None)))):
						self._addAttributeOverride(addOk, "myId", wx.ID_OK)
					elif (addOk):
						buttonSizer.addButton("Ok", myId = wx.ID_OK)

					if (not isinstance(addApply, (bool, type(None)))):
						self._addAttributeOverride(addApply, "myId", wx.ID_APPLY)
						self._addAttributeAppend(addApply, "myFunction", self.onHideWindow)
					elif (addApply):
						buttonSizer.addButton("Apply", myId = wx.ID_APPLY, myFunction = self.onHideWindow)

					if (not isinstance(addCancel, (bool, type(None)))):
						self._addAttributeOverride(addCancel, "myId", wx.ID_CANCEL)
					elif (addCancel):
						buttonSizer.addButton("Cancel", myId = wx.ID_CANCEL)

					if (not isinstance(addClose, (bool, type(None)))):
						self._addAttributeOverride(addClose, "myId", wx.ID_CLOSE)
						self._addAttributeAppend(addClose, "myFunction", self.onHideWindow)
					elif (addClose):
						buttonSizer.addButton("Close", myId = wx.ID_CLOSE, myFunction = self.onHideWindow)

				if (panel):
					self.mainPanel.thing.SetSizer(rootSizer.thing)
					# self.mainPanel.thing.SetAutoLayout(True)
					# rootSizer.thing.Fit(self.mainPanel.thing)
				else:
					self.thing.SetSizer(rootSizer.thing)
					# self.thing.SetAutoLayout(True)
					# rootSizer.thing.Fit(self.thing)

		#########################################################

		self._preBuild(argument_catalogue)

		if (self.type is Types.frame):
			_build_frame()
		elif (self.type is Types.dialog):
			_build_dialog()
		else:
			warnings.warn(f"Add {self.type.name} to _build() for {self.__repr__()}", Warning, stacklevel = 2)

		self._postBuild(argument_catalogue)

	def getDialog(self):
		"""Returns the custom dialog wiundow that this window is currently showing."""

		return self.myDialog

	def getTitle(self):
		"""Returns the title for this window."""

		return self.thing.GetTitle()
	
	def checkActive(self, event = None):
		"""Returns if the window is active or not."""

		if (event is not None):
			if (isinstance(event, wx._core.ActivateEvent)):
				return event.GetActive()
		return self.thing.IsActive()

	def getValueLabel(self, event = None):
		"""Returns what the contextual value label is for the object associated with this handle."""

		if (self.type in (Types.dialog, Types.wizard)):
			value = self.valueLabel
		else:
			warnings.warn(f"Add {self.type.name} to getValueLabel() for {self.__repr__()}", Warning, stacklevel = 2)
			value = None

		return value

	def setValueLabel(self, newValue, event = None):
		"""Sets the contextual value for the object associated with this handle to what the user supplies."""

		if (self.type in (Types.dialog, Types.wizard)):
			self.valueLabel = newValue
		else:
			warnings.warn(f"Add {self.type.name} to setValueLabel() for {self.__repr__()}", Warning, stacklevel = 2)

	#Event Functions
	def setFunction_init(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		self._betterBind(wx.EVT_ACTIVATE, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)

	def setFunction_show(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		self.setFunction_preShow(self, myFunction = myFunction, myFunctionArgs = myFunctionArgs, myFunctionKwargs = myFunctionKwargs)

	def setFunction_preShow(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		self.preShowFunction.append(myFunction)
		self.preShowFunctionArgs.append(myFunctionArgs)
		self.preShowFunctionKwargs.append(myFunctionKwargs)

	def setFunction_postShow(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		self.postShowFunction.append(myFunction)
		self.postShowFunctionArgs.append(myFunctionArgs)
		self.postShowFunctionKwargs.append(myFunctionKwargs)

	def setFunction_hide(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		self.setFunction_preHide(self, myFunction = myFunction, myFunctionArgs = myFunctionArgs, myFunctionKwargs = myFunctionKwargs)

	def setFunction_preHide(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		self.preHideFunction.append(myFunction)
		self.preHideFunctionArgs.append(myFunctionArgs)
		self.preHideFunctionKwargs.append(myFunctionKwargs)

	def setFunction_postHide(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		self.postHideFunction.append(myFunction)
		self.postHideFunctionArgs.append(myFunctionArgs)
		self.postHideFunctionKwargs.append(myFunctionKwargs)

	def setFunction_cancel(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		self.cancelFunction.append(myFunction)
		self.cancelFunctionArgs.append(myFunctionArgs)
		self.cancelFunctionKwargs.append(myFunctionKwargs)

	def setFunction_close(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		self._betterBind(wx.EVT_CLOSE, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)

	def setFunction_enter(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		self._betterBind(wx.EVT_ENTER_WINDOW, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)

	def setFunction_exit(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		self._betterBind(wx.EVT_LEAVE_WINDOW, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)

	def setFunction_focus(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		self._betterBind(wx.EVT_SET_FOCUS, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)

	def setFunction_unfocus(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		self._betterBind(wx.EVT_KILL_FOCUS, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)

	#Change Settings
	def setWindowSize(self, x = None, y = None, atleast = None):
		"""Re-defines the size of the window.

		x (int)     - The width of the window
		y (int)     - The height of the window

		Example Input: setWindowSize()
		Example Input: setWindowSize(350, 250)
		Example Input: setWindowSize((350, 250))
		"""

		if (x is None):
			self.setSize(wx.DefaultSize, atleast = atleast)
			return

		if (isinstance(x, str)):
			if (x.lower() == "default"):
				self.setSize(wx.DefaultSize, atleast = atleast)
				return
			else:
				x = ast.literal_eval(re.sub("^['\"]|['\"]$", "", x))

		if (y is None):
			y = x[1]
			x = x[0]

		#Change the frame size
		self.autoSize = False
		self.setSize((x, y), atleast = atleast)

	def getWindowSize(self):
		"""Returns the size of the window

		Example Input: getWindowSize()
		"""

		size = tuple(self.thing.GetSize())
		return size

	def setWindowPosition(self, x = None, y = None):
		"""Re-defines the position of the window.

		x (int)     - The width of the window
		y (int)     - The height of the window

		Example Input: setWindowPosition()
		Example Input: setWindowPosition(350, 250)
		Example Input: setWindowPosition((350, 250))
		"""

		if (x is None):
			self.thing.SetPosition(wx.DefaultPosition)
			return

		if (isinstance(x, str)):
			if (x.lower() == "center"):
				self.centerWindow()
				return
			elif (x.lower() == "default"):
				self.thing.SetPosition(wx.DefaultPosition)
				return
			else:
				x = ast.literal_eval(re.sub("^['\"]|['\"]$", "", x))

		if (y is None):
			y = x[1]
			x = x[0]

		#Change the frame size
		self.thing.SetPosition((x, y))

	def getWindowPosition(self):
		"""Returns the position of the window

		Example Input: getWindowPosition()
		"""

		position = tuple(self.thing.GetPosition())
		return position

	def setMinimumFrameSize(self, x = (100, 100), y = None):
		"""Sets the minimum window size for the user
		Note: the program can still explicity change the size to be smaller by using setWindowSize().

		size (int tuple) - The size of the window. (length, width)

		Example Input: setMinimumFrameSize()
		Example Input: setMinimumFrameSize(200, 100)
		Example Input: setMinimumFrameSize((200, 100))
		"""

		if (y is None):
			y = x[1]
			x = x[0]

		#Set the size property
		self.thing.SetMinSize((x, y))

	def setMaximumFrameSize(self, x = (900, 700), y = None, x_offset = False, y_offset = False):
		"""Sets the maximum window size for the user
		Note: the program can still explicity change the size to be smaller by using setWindowSize().

		size (int tuple) - The size of the window. (length, width)
		x_offset (bool) - Determines how 'size' is used in the x-axis
		y_offset (bool) - Determines how 'size' is used in the y-axis
			- If True: 'size' is an offset number from the combined screen size of all monitors
			- If int: 'size' is an offset number from the size of this monitor (0 being the left most)
			- If list: 'size' is an offset number from the combined screen size of the monitors listed
			- If False: 'size' is the size of the window
			- If None: 'size' is the size of the window

		Example Input: setMaximumFrameSize()
		Example Input: setMaximumFrameSize(700, 300)
		Example Input: setMaximumFrameSize((700, 300))
		Example Input: setMaximumFrameSize((700, 100), y_offset = 0)
		"""

		if (y is None):
			y = x[1]
			x = x[0]

		# if ()
		# screenSize = self.getScreenSize()



		#Set the size property
		self.thing.SetMaxSize((x, y))

	def setWindowTitle(self, title):
		"""Re-defines the title of the window.

		title (str) - What the new title is

		Example Input: setWindowTitle(0, "test")
		"""

		#Set the title
		self.thing.SetTitle(title)

	def centerWindow(self, offset = None, number = 0):
		"""Centers the window on the screen.

		Example Input: centerWindow()
		Example Input: centerWindow(offset = (0, -100))
		"""

		if (offset is None):
			offset = (0, 0)

		screenSize = self.getScreenSize(number = number)
		windowSize = self.thing.GetSize()

		size_x = math.floor(screenSize[0] / 2 - windowSize[0] / 2 + offset[0])
		size_y = math.floor(screenSize[1] / 2 - windowSize[1] / 2 + offset[1])

		self.thing.SetPosition((size_x, size_y))

	#Visibility
	def showWindow(self, asDialog = False, ensureVisible = True):
		"""Shows a specific window to the user.
		If the window is already shown, it will bring it to the front
		Use: https://wxpython.org/Phoenix/docs/html/wx.Window.html#wx.Window.ShowWithEffect

		Example Input: showWindow()
		Example Input: showWindow(asDialog = True)
		"""

		self.runMyFunction(self.preShowFunction, self.preShowFunctionArgs, self.preShowFunctionKwargs, includeEvent = True)

		self.thing.Show()
		# self.updateWindow()

		if (asDialog):
			self.controller.windowDisabler = [self.thing, wx.WindowDisabler(self.thing)]

		if (not self.visible):
			self.visible = True
		else:
			if (self.thing.IsIconized()):
				self.thing.Iconize(False)
			else:
				self.thing.Raise()

		if (ensureVisible and self.showWindowCheck(state = False, onScreen = True)):
			self.setWindowPosition()

		self.runMyFunction(self.postShowFunction, self.postShowFunctionArgs, self.postShowFunctionKwargs, includeEvent = True)

	def showWindowCheck(self, state = True, onScreen = False):
		"""Checks if a window is currently being shown to the user.

		state (bool) - If True: Checks if the window is NOT shown instead
		onScreen (bool) - If True: Checks if the window is visible on the computer monitor (not dragged off to the side)

		Example Input: showWindowCheck()
		Example Input: showWindowCheck(state = False)
		Example Input: showWindowCheck(onScreen = True)
		"""

		if (onScreen):
			screenSize = self.getScreenSize()
			position = self.thing.GetPosition()

			flag = (position[0] < screenSize[0]) and (position[1] < screenSize[1])
		else:
			flag = self.visible

		if (not state):
			flag = not flag

		return flag

	def onShowWindow(self, event, *args, **kwargs):
		"""Event function for showWindow()"""

		self.showWindow(*args, **kwargs)
		event.Skip()

	def hideWindow(self, event = None, modalId = None):
		"""Hides the window from view, but does not close it.
		Note: This window continues to run and take up memmory. Local variables are still active.

		Example Input: hideWindow()
		"""

		self.runMyFunction(self.preHideFunction, self.preHideFunctionArgs, self.preHideFunctionKwargs, includeEvent = True)

		if (self.controller.windowDisabler is not None):
			if (self.controller.windowDisabler[0] == self.thing):
				self.controller.windowDisabler[1] = None
				self.controller.windowDisabler = None

		if (self.visible):
			if (isinstance(self.thing, wx.Dialog)):
				if (modalId is None):
					if (event is None):
						errorMessage = f"Must either use onHideWindow() or pass either 'event' or 'modalId' to hideWindow() to hide a custom dialog for {self.__repr__()}"
						raise ValueError(errorMessage)
					modalId = event.GetEventObject().GetId()
				self.thing.EndModal(modalId)
			else:
				self.thing.Hide()
			self.visible = False
		else:
			warnings.warn(f"Window {self.label} is already hidden", Warning, stacklevel = 2)

		self.runMyFunction(self.postHideFunction, self.postHideFunctionArgs, self.postHideFunctionKwargs, includeEvent = True)

	def onHideWindow(self, event, *args, **kwargs):
		"""Event function for hideWindow()"""
		
		self.hideWindow(*args, event = event, **kwargs)

		if (event.GetClassName() != "wxCloseEvent"):
			event.Skip()

	def onSwitchWindow(self, event, *args, **kwargs):
		"""Event function for switchWindow()"""
		
		self.switchWindow(*args, **kwargs)
		event.Skip()

	def switchWindow(self, whichTo, hideFrom = True):
		"""Overload for Controller.switchWindow()."""

		self.controller.switchWindow(self, whichTo, hideFrom = hideFrom)

	#Sizers
	def getSizer(self, sizerLabel = None, returnAny = False, useNestingOrder = True):
		"""Returns a sizer when given the sizer's label.

		sizerLabel (int)  - The label of the sizer. 
			-If None: The whole sizer list is returned
		returnAny (bool)   - If True: Any sizer will be returned.

		Example Input: getSizer()
		Example Input: getSizer(0)
		Example Input: getSizer(returnAny = False)
		"""

		sizerList = self._getNested(include = handle_Sizer, useNestingOrder = useNestingOrder)

		#Account for no sizers available
		if (len(sizerList) == 0):
			warnings.warn(f"{self.__repr__()} has no sizers", Warning, stacklevel = 2)
			return

		#Account for random sizer request
		if (returnAny):
			return sizerList[0]

		#Account for whole list request
		elif (sizerLabel is None):
			return sizerList

		#Search for requested sizer
		for sizer in sizerList:
			if (sizerLabel == sizer.label):
				return sizer

		#No sizer found
		warnings.warn(f"{self.__repr__()} has no sizer '{sizerLabel}'", Warning, stacklevel = 2)
		return

	def addSizerBox(self, *args, flex = 1, flags = "c1", selected = False, **kwargs):
		"""Creates a box sizer.

		Example Input: addSizerBox()
		Example Input: addSizerBox(0)
		Example Input: addSizerBox(vertical = False)
		Example Input: addSizerBox(0, vertical = False)
		"""

		handle = self._makeSizerBox(*args, **kwargs)
		self.mainSizer.nest(handle, flex = flex, flags = flags, selected = selected)

		return handle

	def addSizerText(self, *args, flex = 1, flags = "c1", selected = False, **kwargs):
		"""Creates a static box sizer.
		This is a sizer surrounded by a box with a title, much like a wxRadioBox.

		Example Input: addSizerText()
		Example Input: addSizerText(0)
		Example Input: addSizerText(text = "Lorem")
		Example Input: addSizerText(0, text = "Lorem")
		"""

		handle = self._makeSizerText(*args, **kwargs)
		self.mainSizer.nest(handle, flex = flex, flags = flags, selected = selected)

		return handle

	def addSizerGrid(self, *args, flex = 1, flags = "c1", selected = False, **kwargs):
		"""Creates a grid sizer to the specified size.

		Example Input: addSizerGrid()
		Example Input: addSizerGrid(0)
		Example Input: addSizerGrid(rows = 4, columns = 3)
		Example Input: addSizerGrid(0, rows = 4, columns = 3)
		"""

		handle = self._makeSizerGrid(*args, **kwargs)
		self.mainSizer.nest(handle, flex = flex, flags = flags, selected = selected)

		return handle

	def addSizerGridFlex(self, *args, flex = 1, flags = "c1", selected = False, **kwargs):
		"""Creates a flex grid sizer.

		Example Input: addSizerGridFlex()
		Example Input: addSizerGridFlex(0)
		Example Input: addSizerGridFlex(rows = 4, columns = 3)
		Example Input: addSizerGridFlex(0, rows = 4, columns = 3)
		"""

		handle = self._makeSizerGridFlex(*args, **kwargs)
		self.mainSizer.nest(handle, flex = flex, flags = flags, selected = selected)

		return handle

	def addSizerGridBag(self, *args, flex = 1, flags = "c1", selected = False, **kwargs):
		"""Creates a bag grid sizer.

		Example Input: addSizerGridBag()
		Example Input: addSizerGridBag(0)
		Example Input: addSizerGridBag(0, rows = 4, columns = 3)
		Example Input: addSizerGridBag(0, rows = 4, columns = 3, emptySpace = (0, 0))
		"""

		handle = self._makeSizerGridBag(*args, **kwargs)
		self.mainSizer.nest(handle, flex = flex, flags = flags, selected = selected)

		return handle

	def addSizerWrap(self, *args, flex = 1, flags = "c1", selected = False, **kwargs):
		"""Creates a wrap sizer.
		The widgets will arrange themselves into rows and columns on their own, starting in the top-left corner.

		Example Input: addSizerWrap()
		Example Input: addSizerWrap(0)
		"""

		handle = self._makeSizerWrap(*args, **kwargs)
		self.mainSizer.nest(handle, flex = flex, flags = flags, selected = selected)

		return handle

	#Menus
	def getMenu(self, menuLabel = None, useNestingOrder = True):
		"""Returns a menu when given the menu's label.

		menuLabel (int)  - The label of the menu. 
			-If None: The whole menu list is returned

		Example Input: getMenu()
		Example Input: getMenu(0)
		"""

		menuList = self._getNested(include = handle_Menu, useNestingOrder = useNestingOrder)

		#Account for no menus available
		if (len(menuList) == 0):
			errorMessage = f"{self.__repr__()} has no menus"
			raise ValueError(errorMessage)

		#Account for whole list request
		if (menuLabel is None):
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

	def addMenu(self, *args, **kwargs):
		"""Adds a menu to a pre-existing menuBar.
		This is a collapsable array of menu items.

		text (str)        - What the menu is called
			If you add a '&', a keyboard shortcut will be made for the letter after it
		label (str)     - What this is called in the idCatalogue
		detachable (bool) - If True: The menu can be undocked

		Example Input: addMenu("&File", 0)
		Example Input: addMenu("&File", "first")
		"""

		handle = self._makeMenu(*args, **kwargs)
		self.nest(handle)

		return handle

	def addPopupMenu(self, label = None, rightClick = True, text = None,

		preFunction = None, preFunctionArgs = None, preFunctionKwargs = None, 
		postFunction = None, postFunctionArgs = None, postFunctionKwargs = None,

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		parent = None, handle = None, myId = None, tabSkip = False):
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
		handle.type = Types.popup
		handle._build(locals())
		self._finalNest(handle)
		return handle

	#Status Bars
	def checkStatusBar(self, timer = False):
		"""Returns the state of the status bar.
		True: The status bar is not currently on a timer
		False: The status bar is currently on a timer
		None: There is not a status bar

		Example Input: checkStatusBar()
		"""

		if (not self.statusBar):
			return

		if (timer):
			if (self.statusTextTimer["listening"] > 0):
				return True
			return False
		else:
			return self.statusBar.GetFieldsCount()

	def addStatusBar(self, width = None, autoWidth = False):
		"""Adds a status bar to the bottom of the window.
		If one already exists, adds another field to it.

		See: https://www.blog.pythonlibrary.org/2017/06/06/wxpython-working-with-status-bars/
		See: https://stackoverflow.com/questions/48215956/change-default-field-in-a-multi-field-statusbar-in-wxpython-to-display-menuitem
		See: https://wxpython.org/Phoenix/docs/html/wx.StatusBar.html
		
		Example Input: addStatusBar()
		"""

		if (self.statusBar is None):
			if (self.type is not Types.frame):
				if (self.mainPanel is not None):
					self.statusBar = wx.StatusBar(self.mainPanel.thing)
					rootSizer = self.mainPanel.thing.GetSizer()
				else:
					self.statusBar = wx.StatusBar(self.thing)
					rootSizer = self.thing.GetSizer()

				self.statusBar.SetFieldsCount(1)
				rootSizer.Add(self.statusBar, 0, wx.ALIGN_CENTER|wx.ALL|wx.EXPAND, 0)
			else:
				self.statusBar = self.thing.CreateStatusBar()
		else:
			current = self.statusBar.GetFieldsCount()
			self.statusBar.SetFieldsCount(current + 1)

		number = self.statusBar.GetFieldsCount() - 1
		self.setStatusTextDefault(number = number)
		self.setStatusWidth(width = width, number = number, autoWidth = autoWidth)
		self.setStatusText(number = number)

	def removeStatusBar(self):
		"""Removes a status bar if there is more than one.

		Example Input: removeStatusBar()
		"""

		if (self.statusBar is None):
			warnings.warn(f"There is no status bar for {self.__repr__()}", Warning, stacklevel = 2)
			return

		current = self.statusBar.GetFieldsCount()
		if (current == 1):
			warnings.warn(f"There must be at least one status bar after creation for {self.__repr__()}", Warning, stacklevel = 2)
			return

		self.statusBar.SetFieldsCount(current - 1)

	def setStatusWidth(self, width = None, number = None, autoWidth = False):
		"""Changes the width of the status bar to match what was given.

		width (int) - How wide the satus bar is in pixels
			- If Negative: How wide the satus bar is relative to other negative widths
			- If None: All status fields will expand evenly across the window
			- If list: [width for field 0, width for field 1, etc.]

		number (int) - Determines which status bar 'width' applies to
			- If None: Applies to all
			- If list: Applies to only those in the list

		autoWidth (bool) - Determines if 'width' should be overridden with the width of the text in the status bar
			- If True: The status bar width will change to fit the text in it
			- If False: 'width' will be used to set the status bar width

		Example Input: setStatusWidth()
		Example Input: setStatusWidth(100)
		Example Input: setStatusWidth([100, -1])
		Example Input: setStatusWidth([-2, -1])
		Example Input: setStatusWidth([-2, 100, -1])
		
		Example Input: setStatusWidth(100, number = 1)
		Example Input: setStatusWidth(number = 1, autoWidth = True)
		"""

		if (self.statusBar is None):
			warnings.warn(f"There is no status bar in setStatusWidth() for {self.__repr__()}", Warning, stacklevel = 2)
			return

		if (number is None):
			number = []
		elif (not isinstance(number, (list, tuple, range))):
			number = [number]

		if (autoWidth):
			self.statusBar_autoWidth = number
			return
		elif (len(number) == 0):
			self.statusBar_autoWidth = None

		if (width is None):
			width = -1

		if (isinstance(width, (list, tuple, range))):
			if (len(width) != self.statusBar.GetFieldsCount()):
				warnings.warn(f"There are {self.statusBar.GetFieldsCount()} fields in the status bar, but 'width' had {len(width)} elements in setStatusWidth() for {self.__repr__()}", Warning, stacklevel = 2)
				return
			elif (isinstance(width, list)):
				widthList = width
			else:
				widthList = list(width)

		elif (len(number) == 0):
			widthList = [width] * self.statusBar.GetFieldsCount()
		else:
			widthList = []
			for i in range(self.statusBar.GetFieldsCount()):
				if (i in number):
					widthList.append(width)
				else:
					widthList.append(self.statusBar.GetStatusWidth(i))

		self.statusBar.SetStatusWidths(widthList)

	def setStatusText(self, message = None, number = 0, startDelay = 0, delayChunk = 100, autoAdd = False, 
		clearBuffer = False, stop = False, forceQueue = False):
		"""Sets the text shown in the status bar.
		If a message is on a timer and a new message gets sent, the timer message will stop and not overwrite the new message.
		In a multi-field status bar, the fields are numbered starting with 0.

		message (str)  - What the status bar will say
			- If dict: {What to say (str): How long to wait in ms before moving on to the next message (int). Use None for ending}
			- If None: Will use the defaultr status message
			- If function: Will run the function and use the returned value as the message
		number (int)   - Which field to place this status in on the status bar
		startDelay (int)    - How long to wait in ms before showing the first message
		delayChunk (int) - How many seconds to wait while waiting before checking the stop condition
		autoAdd (bool) - If there is no status bar, add one

		Example Input: setStatusText()
		Example Input: setStatusText("Ready")
		Example Input: setStatusText("Saving", number = 1)
		Example Input: setStatusText({"Ready": 1000, "Set": 1000, "Go!": None, "This will not appear": 1000)
		Example Input: setStatusText({"Changes Saved": 3000, None: None)
		Example Input: setStatusText(self.checkStuff)
		Example Input: setStatusText(startDelay = 3000)
		"""

		def timerMessage():
			"""The thread function that runs for the timer status message."""
			nonlocal self, message, number, startDelay, delayChunk

			#Account for other messages with timers before this one
			while (self.statusTextTimer["listening"] > 0):
				self.statusTextTimer["stop"] = True
				time.sleep(100 / 1000)
			self.statusTextTimer["stop"] = False

			self.statusTextTimer["listening"] += 1

			if (startDelay not in [None, 0]):
				for i in range(1, (startDelay // delayChunk) + 1):
					if (self.statusTextTimer["stop"]):
						self.statusTextTimer["stop"] = False
						break
					time.sleep((i * delayChunk) / 1000)
				time.sleep((startDelay % delayChunk) / 1000)

			if (not isinstance(message, dict)):
				applyMessage(message)
			else:
				for text, delay in message.items():
					if (self.statusTextTimer["stop"]):
						self.statusTextTimer["stop"] = False
						break

					applyMessage(text)

					if (text is None):
						text = self.statusTextDefault.get(number, " ")
					if (callable(text)):
						text = text()
					if (text is None):
						text = " "
					self.statusBar.SetStatusText(text, number)

					if (delay is None):
						break

					for i in range(1, (delay // delayChunk) + 1):
						if (self.statusTextTimer["stop"]):
							self.statusTextTimer["stop"] = False
							break
						time.sleep(delayChunk / 1000)
					time.sleep((delay % delayChunk) / 1000)

			self.statusTextTimer["listening"] -= 1
			return True

		def applyMessage(text):
			"""Places the given text into the status bar."""
			nonlocal self, number

			if (not wx.IsMainThread()):
				wx.CallAfter(applyMessage, text)
				return

			if (text is None):
				text = self.statusTextDefault.get(number, " ")
			if (callable(text)):
				text = text()
			if (text is None):
				text = " "
			self.statusBar.SetStatusText(text, number)

			if (isinstance(self.statusBar_autoWidth, (list, tuple, range)) and ((len(self.statusBar_autoWidth) == 0) or (number in self.statusBar_autoWidth))):
				self.setStatusWidth(width = self.getStringPixels(text)[0], number = number)

		##################################################

		#Error Checking
		if (self.statusBar is None):
			if (autoAdd):
				self.addStatusBar()
			else:
				warnings.warn(f"There is no status bar in setStatusText() for {self.__repr__()}", Warning, stacklevel = 2)
				return

		if (self.statusBar.GetFieldsCount() <= number):
			warnings.warn(f"There are only {self.statusBar.GetFieldsCount()} fields in the status bar, so it cannot set the text for field {number} in setStatusText() for {self.__repr__()}", Warning, stacklevel = 2)
			return

		if (clearBuffer):
			while True:
				try:
					self.controller.queue_statusText.get(False)
				except queue.Empty:
					break
		if (stop):
			self.statusTextTimer["stop"] = True

		if ((not forceQueue) and (not isinstance(message, dict)) and (startDelay in [None, 0])):
			applyMessage(message)
		else:
			self.controller.queue_statusText.put((timerMessage, [], {}))

	def setStatusText_stop(self):
		"""Stops the setStatusText wherever it is in execusion."""

		self.statusTextTimer["stop"] = True

	def setStatusTextDefault(self, message = " ", number = 0):
		"""Sets the default status message for the status bar.

		message (str) - What the status bar will say on default

		Example Input: setStatusTextDefault("Ready")
		"""

		if (message is None):
			message = " "
		self.statusTextDefault[number] = message

	def getStatusText(self, number = 0):
		"""Returns the status message that is currently displaying.

		Example Input: getStatusText()
		"""

		if (self.statusBar is None):
			warnings.warn(f"There is no status bar in getStatusText() for {self.__repr__()}", Warning, stacklevel = 2)
			return
		if (self.statusBar.GetFieldsCount() <= number):
			warnings.warn(f"There are only {self.statusBar.GetFieldsCount()} fields in the status bar, so it cannot set the text for field {number} in getStatusText() for {self.__repr__()}", Warning, stacklevel = 2)
			return

		message = self.statusBar.GetStatusText(number)
		return message

	#Etc
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
		handle._build(locals())

		#Nest handle
		self._finalNest(handle)

		return handle

	def setIcon(self, icon, internal = False):
		"""Sets the icon for the .exe file.

		icon (str) - The file path to the icon for the menu item
			If None: No icon will be shown
		internal (bool) - If True: The icon provided is an internal icon, not an external file

		Example Input: setIcon("resources/cte_icon.ico")
		Example Input: setIcon("lightBulb", True)
		"""

		#Get the image
		myIcon = self.getImage(icon, internal, returnIcon = True)
		# image = self._convertBitmapToImage(image)
		# image = image.Scale(16, 16, wx.IMAGE_QUALITY_HIGH)
		# image = self._convertImageToBitmap(image)

		# #Create the icon
		# myIcon = wx.Icon(image)
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

	def updateWindow(self, autoSize = None, updateNested = False, invalidateNested = False, useSizeEvent = True):
		"""Refreshes what the window looks like when things on the top-level sizer are changed.
		Use: https://wiki.wxpython.org/WhenAndHowToCallLayout

		autoSize (bool) - Determines how the autosizing behavior is applied
			- If True: The window size will be changed to fit the sizers within
			- If False: The window size will be what was defined when it was initially created
			- If None: The internal autosize state will be used

		Example Input: updateWindow()
		Example Input: updateWindow(autoSize = False)
		"""

		def applyInvalidateNested(itemList):
			"""Invalidates the 'best size' calculation for everything nested."""

			for item in itemList:
				if (item is None):
					continue
				elif (isinstance(item, handle_Base_NotebookPage)):
					applyInvalidateNested([item.mySizer, item.myPanel])
					continue
				elif (isinstance(item, handle_MenuPopup)):
					continue
				elif (item.thing is None):
					khikukuhk

				if (hasattr(item.thing, "InvalidateBestSize")):
					item.thing.InvalidateBestSize()
				applyInvalidateNested(item[:])

		def applyUpdateNested(itemList):
			"""Makes sure that all nested objects call their update functions."""

			for item in itemList:
				if (item is None):
					continue

				elif (isinstance(item, (handle_MenuPopup, handle_Menu, handle_MenuItem, handle_MenuPopupItem, handle_MenuPopupSubMenu))):
					applyUpdateNested(item[:])

				elif (isinstance(item, handle_Base_NotebookPage)):
					applyUpdateNested([item.mySizer, item.myPanel])

				elif (item.thing is None):
					hjhkjjh

				elif (isinstance(item, handle_WidgetTable)):
					#Not working
					item.thing.ForceRefresh()
					item.thing.Layout()

					if (useSizeEvent):
						self.thing.SendSizeEvent()
					else:
						self.thing.Layout()
						self.thing.Refresh()

				elif (isinstance(item, handle_Sizer)):
					item.thing.Layout()
					applyUpdateNested(item[:])

				else:
					item.thing.Refresh()
					item.thing.Layout()
					applyUpdateNested(item[:])

		catalogue = self._getAddressValue(self.nestingAddress + [id(self)])

		#Skip empty windows
		if (len(catalogue) > 1):
			if (autoSize is None):
				autoSize = self.autoSize

			#Auto-size the window
			if (autoSize):
				if (invalidateNested):
					applyInvalidateNested(self[:])

				if (self.mainPanel is not None):
					if (invalidateNested):
						applyInvalidateNested(self.mainPanel[:])
					self.mainPanel.thing.InvalidateBestSize()
					self.mainPanel.thing.SetSize(self.mainPanel.thing.GetBestSize())

				self.thing.InvalidateBestSize()
				self.thing.SetSize(self.thing.GetBestSize())

			#Redraw the window
			if (updateNested):
				applyUpdateNested(self[:])

			if (useSizeEvent):
				if (self.mainPanel is not None):
					self.mainPanel.thing.SendSizeEvent()
				self.thing.SendSizeEvent()
			else:
				if (self.mainPanel is not None):
					self.mainPanel.thing.Layout()
					self.mainPanel.thing.Refresh()
					# self.mainPanel.thing.Update()

				# if (self.mainSizer is not None):
				#   self.mainSizer.thing.Layout() 

				self.thing.Layout()
				self.thing.Refresh()
				# self.thing.Update()

	def setRefresh(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		"""Sets the functions to call for refresh()."""

		self.refreshFunction.append(myFunction)
		self.refreshFunctionArgs.append(myFunctionArgs)
		self.refreshFunctionKwargs.append(myFunctionKwargs)

	def onRefresh(self, event, includeEvent = True):
		"""A wx event version of refresh()."""

		self.refresh(event = event, includeEvent = includeEvent)

		if (event is not None):
			event.Skip()

	def refresh(self, event = None, includeEvent = False):
		"""Runs the user defined refresh function.
		This function is intended to make sure all widget values are up to date.

		Example Input: refresh()
		"""

		if (not self.refreshFunction):
			warnings.warn(f"The refresh function for {self.__repr__()} has not been set yet\nUse setRefresh() during window creation first to set the refresh function", Warning, stacklevel = 2)
			return

		self.runMyFunction(self.refreshFunction, self.refreshFunctionArgs, self.refreshFunctionKwargs, event = event, includeEvent = includeEvent)

	def _addFinalFunction(self, myFunction, myFunctionArgs = None, myFunctionKwargs = None, label = None):
		"""Adds a function to the queue that will run after building, but before launching, the app."""

		if (label is None):
			self.finalFunctionList.append([myFunction, myFunctionArgs, myFunctionKwargs])
		else:
			self.finalFunctionCatalogue[label] = [myFunction, myFunctionArgs, myFunctionKwargs]

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
		if (self.mainPanel is not None):
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

	def addHtml(self, sizerLabel, *args, **kwargs):
		"""Overload for addHtml in handle_Sizer()."""

		mySizer = self.getSizer(sizerLabel)
		handle = mySizer.addHtml(*args, **kwargs)

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

	def addButtonList(self, sizerLabel, *args, **kwargs):
		"""Overload for addButtonList in handle_Sizer()."""

		mySizer = self.getSizer(sizerLabel)
		handle = mySizer.addButtonList(*args, **kwargs)

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

class handle_Wizard(handle_Window):
	"""A handle that mimics a wxWizard.
	Modified code from: https://www.blog.pythonlibrary.org/2012/07/12/wxpython-how-to-create-a-generic-wizard/

	Use: https://www.blog.pythonlibrary.org/2011/01/27/wxpython-a-wizard-tutorial/
	Use: http://xoomer.virgilio.it/infinity77/wxPython/wizard/wx.wizard.html
	"""

	def __init__(self, controller):
		"""Initializes defaults."""

		#Initialize inherited classes
		handle_Window.__init__(self, controller)

		#Internal Variables
		self.currentNode = None
		self.nodeResolver = anytree.Resolver("name")
		self.pageNode = anytree.Node("root", handle = self)
		self.pageElements = set()

	def _build(self, argument_catalogue):
		"""Builds a mimic for a wx wizard object."""

		with self.bookend_build(argument_catalogue):

			tabTraversal, stayOnTop, resizable, title = self._getArguments(argument_catalogue, ["tabTraversal", "stayOnTop", "resizable", "title"])
			size, position, panel, valueLabel = self._getArguments(argument_catalogue, ["size", "position", "panel", "valueLabel"])
			icon, icon_internal, smallerThanScreen = self._getArguments(argument_catalogue, ["icon", "icon_internal", "smallerThanScreen"])
			image, internal, resizable = self._getArguments(argument_catalogue, ["image", "internal", "resizable"])

			#Configure Style
			style = []

			if (stayOnTop):
				style.append(wx.STAY_ON_TOP)

			# if (helpButton):
			#   style.append(wx.DIALOG_EX_CONTEXTHELP)

			if (resizable):
				style.append(wx.RESIZE_BORDER)

			if (title is not None):
				style.append(wx.CAPTION)
			else:
				title = ""

			#Create Object
			self.thing = wx.Dialog(None, title = title, size = size, pos = position, style = functools.reduce(operator.ior, style or (0,)))

			if (smallerThanScreen not in (None, False)):
				if (isinstance(smallerThanScreen, bool)):
					screenSize = self.getScreenSize()
				else:
					screenSize = self.getScreenSize(number = smallerThanScreen)
				self.thing.SetMaxSize(screenSize)

			#Set Properties
			if (icon is not None):
				self.setIcon(icon, internal)

			#Remember Values
			self.valueLabel = valueLabel

			#Unpack arguments
			panel = argument_catalogue["panel"]
			
			#Setup sizers and panels
			if (panel):
				self.mainPanel = self._makePanel(tabTraversal = tabTraversal)
				self._finalNest(self.mainPanel)

			with self._makeSizerGridFlex(rows = 1000, columns = 1) as rootSizer:
				self._finalNest(rootSizer)
				self.mainSizer = rootSizer.addSizerBox(flex = 1)

				rootSizer.addLine(flex = 0)
				
				with rootSizer.addSizerWrap(vertical = False, flex = 0) as mySizer:
					self.choiceSizer = mySizer

				with rootSizer.addSizerGridFlex(rows = 1, columns = 3, flex = 0) as buttonSizer:
					with buttonSizer.addButton("Previous", myId = wx.ID_BACKWARD) as myWidget:
						self.button_previous = myWidget
						myWidget.setFunction_click(self.onPreviousPage)

					with buttonSizer.addButton("Finish", myId = wx.ID_ANY) as myWidget:
						self.button_finish = myWidget
						myWidget.setFunction_click(self.onTriggerEvent, myFunctionKwargs = {"eventType": self.EVT_FINISHED, "okFunction": self.hideWindow, "okFunctionKwargs": {"modalId": wx.ID_OK}})

					with buttonSizer.addButton("Cancel", myId = wx.ID_ANY) as myWidget:
						myWidget.setFunction_click(self.onTriggerEvent, myFunctionKwargs = {"eventType": self.EVT_CANCEL, "okFunction": self.hideWindow, "okFunctionKwargs": {"modalId": wx.ID_CANCEL}})

				if (panel):
					self.mainPanel.thing.SetSizer(rootSizer.thing)
				else:
					self.thing.SetSizer(rootSizer.thing)

	def reset(self, branch = None):
		self.currentNode = None
		self.showPage(branch = branch)

	def start(self, branch = None):
		self.reset(branch = branch)

		with self.makeDialogCustom(myFrame = self) as myDialog:
			pass

	def addPage(self, text = None, sizer = {}, panel = {}, image = None, internal = False,
		icon_path = None, icon_internal = False, parentNode = None, default = False,

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, tabSkip = False,
		flex = 0, flags = "c1", selected = False):
		"""Adds a page to the wizard.
		Lists can be given to add multiple pages. They are added in order from left to right.
		If only a 'pageLabel' is a list, they will all have the same 'text'.
		If 'pageLabel' and 'text' are a list of different lengths, it will not add any of them.

		text (str)  - What the page's tab will say
			- If None: The tab will be blank
		label (str) - What this is called in the idCatalogue

		Example Input: addPage()
		Example Input: addPage("Lorem")
		Example Input: addPage(["Lorem", "Ipsum"])
		Example Input: addPage({"choice_1": "Lorem", "choice_2": "Ipsum"})
		"""

		handle = handle_WizardPage(self)
		handle.type = Types.wizardpage
		with handle._build({**locals(), "parent": self, "parentNode": parentNode or self.pageNode}): pass
		handle.pageElements.add(handle.myPanel)
		self.mainSizer.nest(handle.myPanel, flex = flex, flags = flags, selected = selected)

		previousNode = handle.pageNode.parent
		with self.choiceSizer.addButton(handle.text or f"{len(previousNode.children)}", myId = wx.ID_FORWARD) as myWidget:
			previousNode.handle.pageElements.add(myWidget)
			myWidget.setFunction_click(self.onNextPage, myFunctionKwargs = {"branch": handle.nodeLabel})

		return handle

	def onShowPage(self, event, *args, **kwargs):
		"""A wxEvent version of showPage()."""

		self.showPage(*args, **kwargs)
		event.Skip()

	def showPage(self, branch = None, node = None, default = None, triggerEvent = True, direction = None):
		"""Shows the page with the given node.

		Example Input: showPage()
		"""

		def getNode(sourceNode):
			nonlocal branch, default

			label = branch or default or getattr(sourceNode, "default", None)
			if (label is not None):
				try:
					return self.nodeResolver.get(sourceNode, label)
				except anytree.resolver.ChildResolverError:
					errorMessage = f"There is no wizard page with the label {label} in {sourceNode}"
					print("@handle_Wizard.showPage", errorMessage)
			
			return sourceNode.children[0]

		#####################

		node = node or getNode(self.currentNode or self.pageNode)

		if (triggerEvent):
			event = self.triggerEvent(self.EVT_PAGE_CHANGING, returnEvent = True, fromNode = self.currentNode, toNode = node, direction = direction)
			if (event.IsVetoed()):
				return

		self.mainSizer.hide()
		self.choiceSizer.hide()

		self.currentNode = node
		for myWidget in self.currentNode.handle.pageElements:
			myWidget.show()

		self.button_previous.setEnable(self.currentNode.parent.parent is not None)
		self.button_finish.setEnable(not self.currentNode.children)

		self.updateWindow()
		self.triggerEvent(self.EVT_PAGE_CHANGED, node = node, direction = direction)

	def onNextPage(self, event, *args, **kwargs):
		"""A wxEvent version of nextPage()."""

		self.nextPage(*args, **kwargs)
		event.Skip()

	def nextPage(self, branch = None):
		"""Moves to the next page.

		branch (int) Which branch to go down
			- If None: Will use the default branch
			- If str: Will use the branch with the matching label

		Example Input: nextPage()
		Example Input: nextPage(2)
		Example Input: nextPage("lorem")
		"""

		event = self.triggerEvent(self.EVT_PAGE_NEXT, returnEvent = True, node = self.currentNode, branch = branch)
		if (event.IsVetoed()):
			return

		return self.showPage(branch = branch, direction = True)

	def onPreviousPage(self, event, *args, **kwargs):
		"""A wxEvent version of previousPage()."""

		self.previousPage(*args, **kwargs)
		event.Skip()

	def previousPage(self):
		"""Moves to the previous page.

		Example Input: previousPage()
		"""

		event = self.triggerEvent(self.EVT_PAGE_PREVIOUS, returnEvent = True, node = self.currentNode)
		if (event.IsVetoed()):
			return

		return self.showPage(node = self.currentNode.parent, direction = False)

	@MyUtilities.common.makeProperty()
	class currentPage():
		def getter(self):
			node = self.currentNode or self.pageNode.children[0]
			return node.handle

	def setFunction_pageChange(self, *args, **kwargs):
		return self.setFunction_postPageChange(*args, **kwargs)

	def setFunction_prePageChange(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		self._betterBind(self.EVT_PAGE_CHANGING, self.thing, myFunction, myFunctionArgs, myFunctionKwargs, mode = 2)

	def setFunction_postPageChange(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		self._betterBind(self.EVT_PAGE_CHANGED, self.thing, myFunction, myFunctionArgs, myFunctionKwargs, mode = 2)

	def setFunction_nextPage(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		self._betterBind(self.EVT_PAGE_NEXT, self.thing, myFunction, myFunctionArgs, myFunctionKwargs, mode = 2)

	def setFunction_previousPage(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		self._betterBind(self.EVT_PAGE_PREVIOUS, self.thing, myFunction, myFunctionArgs, myFunctionKwargs, mode = 2)

	def setFunction_cancel(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		self._betterBind(self.EVT_CANCEL, self.thing, myFunction, myFunctionArgs, myFunctionKwargs, mode = 2)

	def setFunction_finish(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		self._betterBind(self.EVT_FINISHED, self.thing, myFunction, myFunctionArgs, myFunctionKwargs, mode = 2)

	#Events
	class EVT_FINISHED(MyEvent):
		def __init__(self, parent, **kwargs):
			super().__init__(self, parent, canVeto = True)

	class EVT_CANCEL(MyEvent):
		def __init__(self, parent, **kwargs):
			super().__init__(self, parent, canVeto = True)

	class EVT_PAGE_CHANGING(MyEvent):
		def __init__(self, parent, **kwargs):
			super().__init__(self, parent, canVeto = True)

			self.toNode = kwargs.pop("toNode", None)
			self.fromNode = kwargs.pop("fromNode", None)
			self.direction = kwargs.pop("direction", None)

	class EVT_PAGE_CHANGED(MyEvent):
		def __init__(self, parent, **kwargs):
			super().__init__(self, parent, canVeto = False)

			self.node = kwargs.pop("node", None)
			self.direction = kwargs.pop("direction", None)

	class EVT_PAGE_NEXT(MyEvent):
		def __init__(self, parent, **kwargs):
			super().__init__(self, parent, canVeto = True)

			self.node = kwargs.pop("node", None)
			self.branch = kwargs.pop("branch", None)

	class EVT_PAGE_PREVIOUS(MyEvent):
		def __init__(self, parent, **kwargs):
			super().__init__(self, parent, canVeto = True)

			self.node = kwargs.pop("node", None)

class handle_NavigatorBase():
	"""COntains functions for tab traversal"""

	def __init__(self):
		"""Initializes defaults."""

		self.tab_pressed = False
		self.tab_skipSet = set()
		self.tab_direction = True

	def _postBuild(self, *args, **kwargs):
		self._betterBind(wx.EVT_NAVIGATION_KEY, self.thing, self._onTabTraversal_panel, mode = 2)
		return super()._postBuild(*args, **kwargs)

	def _onTabTraversal_panel(self, event):
		"""Helps to skip widgets that are marked to be skipped during tab traversal."""

		def reset():
			nonlocal self
			self.tab_pressed = False

		############################################

		self.tab_pressed = True
		self.tab_direction = event.GetDirection()
		wx.CallLater(100, reset)
		event.Skip()

	def _onTabTraversal_child(self, event):
		"""Handles skipping widgets that are marked to be skipped during tab traversal.
		Modified code from Frank Millman on: http://wxpython-users.1045709.n5.nabble.com/Skipping-widgets-in-tab-traversal-my-solution-but-td2324585.html
		"""

		thing = event.GetEventObject()
		if (self.tab_pressed):
			self.tab_pressed = False
			if (thing in self.tab_skipSet):
				thing.Navigate(self.tab_direction)
		event.Skip()
 
class handle_Panel(handle_NavigatorBase, handle_Container_Base):
	"""A handle for working with a wxPanel."""

	def __init__(self):
		"""Initializes defaults."""

		#Initialize inherited classes
		handle_Container_Base.__init__(self)
		handle_NavigatorBase.__init__(self)

	def __str__(self):
		"""Gives diagnostic information on the Panel when it is printed out."""

		output = handle_Container_Base.__str__(self)
		return output

	def _build(self, argument_catalogue):
		"""Determiens which build system to use for this handle."""

		def _build_normal():
			"""Builds a wx double splitter object."""
			nonlocal self, argument_catalogue

			#Error Check
			if (self.parent.thing is None):
				errorMessage = f"The object {self.parent.__repr__()} must be fully created for {self.__repr__()}"
				raise RuntimeError(errorMessage)

			#Unpack arguments
			scroll_x, scroll_y, scrollToTop, scrollToChild = self._getArguments(argument_catalogue, ["scroll_x", "scroll_y", "scrollToTop", "scrollToChild"])
			position, size, border, tabTraversal = self._getArguments(argument_catalogue, ["position", "size", "border", "tabTraversal"])
			initFunction = self._getArguments(argument_catalogue, ["initFunction"])

			#Setup
			style = [wx.EXPAND, wx.ALL]
			if (type(border) == str):
				#Ensure correct caseing
				border = border.lower()

				if (border[0:2] == "si"):
					style.append(wx.SIMPLE_BORDER)

				elif (border[0] == "r"):
					style.append(wx.RAISED_BORDER)

				elif (border[0:2] == "su"):
					style.append(wx.SUNKEN_BORDER)

				elif (border[0] == "n"):
					style.append(wx.NO_BORDER)

				else:
					errorMessage = f"Unknown border {border} in {self.__repr__()}"
					raise KeyError(errorMessage)
			else:
				style.append(wx.NO_BORDER)

			if (tabTraversal):
				style.append(wx.TAB_TRAVERSAL)

			myId = self._getId(argument_catalogue)

			#Create the panel
			if ((scroll_x not in [False, None]) or (scroll_y not in [False, None])):
				self.thing = wx.lib.scrolledpanel.ScrolledPanel(self.parent.thing, id = myId, pos = position, size = size, style = functools.reduce(operator.ior, style or (0,)))

				instructions = {}
				instructions["scrollToTop"] = scrollToTop
				instructions["scrollIntoView"] = scrollToChild
				instructions["scroll_x"] = (scroll_x not in [False, None])
				instructions["scroll_y"] = (scroll_y not in [False, None])
				instructions["rate_x"] = scroll_x if (isinstance(scroll_x, int)) else 20
				instructions["rate_y"] = scroll_y if (isinstance(scroll_x, int)) else 20

				self.thing.SetupScrolling(**instructions)

			else:
				self.thing = wx.Panel(self.parent.thing, id = myId, pos = position, size = size, style = functools.reduce(operator.ior, style or (0,)))

			#Bind Functions
			if (initFunction is not None):
				initFunctionArgs, initFunctionKwargs = self._getArguments(argument_catalogue, ["initFunctionArgs", "initFunctionKwargs"])
				self._betterBind(wx.EVT_INIT_DIALOG, self.thing, initFunction, initFunctionArgs, initFunctionKwargs)
			
			#Update catalogue
			for key, value in locals().items():
				if (key != "self"):
					argument_catalogue[key] = value
			
		#########################################################

		self._preBuild(argument_catalogue)

		if (self.type is Types.panel):
			_build_normal()
		else:
			warnings.warn(f"Add {self.type.name} to _build() for {self.__repr__()}", Warning, stacklevel = 2)

		self._postBuild(argument_catalogue)

	def setFunction_click(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		"""Changes the function that runs when a menu item is selected."""

		self._betterBind(wx.EVT_LEFT_DOWN, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)

	def toggleShow(self, *args, **kwargs):
		"""Overridden to use the panel instead of the objects nested in it."""
		
		return handle_Widget_Base.toggleShow(self, *args, **kwargs)

	def setShow(self, *args, **kwargs):
		"""Overridden to use the panel instead of the objects nested in it."""
		
		return handle_Widget_Base.setShow(self, *args, **kwargs)

	def setHide(self, *args, **kwargs):
		"""Overridden to use the panel instead of the objects nested in it."""
		
		return handle_Widget_Base.setHide(self, *args, **kwargs)

	def show(self, *args, **kwargs):
		"""Overridden to use the panel instead of the objects nested in it."""
		
		return handle_Widget_Base.show(self, *args, **kwargs)

	def hide(self, *args, **kwargs):
		"""Overridden to use the panel instead of the objects nested in it."""
		
		return handle_Widget_Base.hide(self, *args, **kwargs)

	def checkShown(self, *args, **kwargs):
		"""Overridden to use the panel instead of the objects nested in it."""
		
		return handle_Widget_Base.checkShown(self, *args, **kwargs)

	def checkHidden(self, *args, **kwargs):
		"""Overridden to use the panel instead of the objects nested in it."""

		return handle_Widget_Base.checkHidden(self, *args, **kwargs)

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

	def _postBuild(self, argument_catalogue):
		"""Runs before this object is built."""

		handle_Container_Base._postBuild(self, argument_catalogue)

		#Unpack arguments
		buildSelf = argument_catalogue["self"]

		#Nest splitter
		buildSelf.nest(self)

	def _build(self, argument_catalogue):
		"""Determiens which build system to use for this handle."""

		def _build_double():
			"""Builds a wx double splitter object."""
			nonlocal self, argument_catalogue

			vertical, minimumSize, dividerPosition, buildSelf = self._getArguments(argument_catalogue, ["vertical", "minimumSize", "dividerPosition", "self"])
			dividerGravity, dividerSize, initFunction = self._getArguments(argument_catalogue, ["dividerGravity", "dividerSize", "initFunction"])

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
				panel = self._readBuildInstructions_panel(buildSelf, i, panelInstructions)
				self.panelList.append(panel)
				self._finalNest(self.panelList[i])

				sizerInstructions["parent"] = self.panelList[i]
				sizer = self._readBuildInstructions_sizer(buildSelf, i, sizerInstructions)
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
			if (dividerPosition is not None):
				self.thing.SetSashPosition(dividerPosition)

			##Left panel growth ratio
			self.thing.SetSashGravity(dividerGravity)

			##Dividing line size
			self.thing.SetSashSize(dividerSize)

			#Bind Functions
			if (initFunction is not None):
				initFunctionArgs, initFunctionKwargs = self._getArguments(argument_catalogue, ["initFunctionArgs", "initFunctionKwargs"])
				self.setFunction_init(initFunction, initFunctionArgs, initFunctionKwargs)

		def _build_quad():
			"""Builds a wx quad splitter object."""
			nonlocal self, argument_catalogue

			buildSelf = self._getArguments(argument_catalogue, "self")
			self.myWindow = buildSelf.myWindow

			#Add panels and sizers to splitter
			for i in range(4):
				#Add panels to the splitter
				self.panelList.append(self.myWindow._makePanel(parent = self, border = "raised"))
				self.thing.AppendWindow(self.panelList[i].thing)
				self._finalNest(self.panelList[i])

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
			if (initFunction is not None):
				initFunctionArgs, initFunctionKwargs = self._getArguments(argument_catalogue, ["initFunctionArgs", "initFunctionKwargs"])
				self.setFunction_init(initFunction, initFunctionArgs, initFunctionKwargs)

		def _build_poly():
			"""Builds a wx poly splitter object."""
			nonlocal self, argument_catalogue

			minimumSize, vertical, buildSelf = self._getArguments(argument_catalogue, ["minimumSize", "vertical", "self"])
			self.myWindow = buildSelf.myWindow

			#Add panels and sizers to splitter
			for i in range(panelNumbers):
				#Add panels to the splitter
				self.panelList.append(self.myWindow._makePanel(parent = self, border = "raised"))
				self.thing.AppendWindow(self.panelList[i].thing)
				self._finalNest(self.panelList[i])

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
			if (initFunction is not None):
				initFunctionArgs, initFunctionKwargs = self._getArguments(argument_catalogue, ["initFunctionArgs", "initFunctionKwargs"])
				self.setFunction_init(initFunction, initFunctionArgs, initFunctionKwargs)

			
		#########################################################

		self._preBuild(argument_catalogue)

		if (self.type is Types.double):
			_build_double()
		elif (self.type is Types.quad):
			_build_quad()
		elif (self.type is Types.poly):
			_build_poly()
		else:
			warnings.warn(f"Add {self.type.name} to _build() for {self.__repr__()}", Warning, stacklevel = 2)

		self._postBuild(argument_catalogue)

	def setFunction_init(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		"""Changes the function that runs when the object is first created."""

		if (self.type is Types.double):
			self.parent._betterBind(wx.EVT_INIT_DIALOG, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		elif (self.type is Types.quad):
			self.parent._betterBind(wx.EVT_INIT_DIALOG, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		elif (self.type is Types.poly):
			self.parent._betterBind(wx.EVT_INIT_DIALOG, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		else:
			warnings.warn(f"Add {self.type.name} to setFunction_init() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_preMoveSash(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		"""Changes the function that runs when the object is first created."""

		if (self.type is Types.double):
			self.parent._betterBind(wx.EVT_SPLITTER_SASH_POS_CHANGING, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		else:
			warnings.warn(f"Add {self.type.name} to setFunction_preMoveSash() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_postMoveSash(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		"""Changes the function that runs when the object is first created."""

		if (self.type is Types.double):
			self.parent._betterBind(wx.EVT_SPLITTER_SASH_POS_CHANGED, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		else:
			warnings.warn(f"Add {self.type.name} to setFunction_preMoveSash() for {self.__repr__()}", Warning, stacklevel = 2)

	def getSizers(self):
		"""Returns the internal sizer list."""

		return self.sizerList

	def getSashPosition(self):
		"""Returns the current sash position."""
		
		if (self.type is Types.double):
			value = self.thing.GetSashPosition()
		else:
			warnings.warn(f"Add {self.type.name} to getSashPosition() for {self.__repr__()}", Warning, stacklevel = 2)
			value = None

		return value

	def setSashPosition(self, newValue):
		"""Changes the position of the sash marker."""
		
		if (self.type is Types.double):
			if (isinstance(newValue, str)):
				newValue = ast.literal_eval(re.sub("^['\"]|['\"]$", "", newValue))

			if (newValue is not None):
				self.thing.SetSashPosition(newValue)
		else:
			warnings.warn(f"Add {self.type.name} to setSashPosition() for {self.__repr__()}", Warning, stacklevel = 2)

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

	def _build(self, argument_catalogue):
		"""Builds a wx AuiManager object"""

		reduceFlicker = self._getArguments(argument_catalogue, ["reduceFlicker"])

		#Expand using: https://wxpython.org/Phoenix/docs/html/wx.aui.AuiManager.html

		style = "wx.lib.agw.aui.AUI_MGR_DEFAULT" #See: https://wxpython.org/Phoenix/docs/html/wx.aui.AuiManagerOption.enumeration.html#wx-aui-auimanageroption

		if (reduceFlicker):
			style += "|wx.lib.agw.aui.AUI_MGR_LIVE_RESIZE"

		self.thing = wx.lib.agw.aui.AuiManager(self.myWindow.thing, eval(style, {'__builtins__': None, "wx.lib.agw.aui": wx.lib.agw.aui}, {}))
		self.thing.SetManagedWindow(self.myWindow.thing)

		# self.mySizer = self._readBuildInstructions_sizer(self.myWindow, 0, {})
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
		if (default is not None):
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

		if (minimumSize is not None):
			paneInfo.MinSize(minimumSize)
		if (maximumSize is not None):
			paneInfo.MaxSize(maximumSize)
		if (bestSize is not None):
			paneInfo.BestSize(bestSize)

		if (fixedSize):
			paneInfo.Fixed()

		if (floatable):
			paneInfo.Float()
			paneInfo.PinButton(True)

		if (label is not None):
			paneInfo.Name(str(label))

		#Account for overriding the handle with your own widget or panel
		if (handle is None):
			#Get the object
			handle = handle_NotebookPage_Aui()
			handle.type = Types.auipage

			with handle._build({**locals(), "parent": self.myWindow, "myManager": self}): pass

		#Add Pane
		self.thing.AddPane(handle.myPanel.thing, paneInfo) 
		self.thing.Update()

		#Record nesting
		self._finalNest(handle)

		return handle

	def setFunction_click(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		"""Changes the function that runs when the object is activated."""

		self.parent._betterBind(wx.EVT_AUI_PANE_ACTIVATED, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)

	def setFunction_tabClick(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		"""Changes the function that runs when the object is activated."""

		self.parent._betterBind(wx.EVT_AUI_PANE_BUTTON, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)

	def setFunction_maximize(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		"""Changes the function that runs when the object is activated."""

		self.parent._betterBind(wx.EVT_AUI_PANE_MAXIMIZE, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)

	def setFunction_minimize(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		"""Changes the function that runs when the object is activated."""

		self.parent._betterBind(wx.EVT_AUI_PANE_MINIMIZE, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)

	def setFunction_restore(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		"""Changes the function that runs when the object is activated."""

		self.parent._betterBind(wx.EVT_AUI_PANE_RESTORE, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)

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

class handle_Base_Notebook(handle_Container_Base):
	"""A handle for working with notebook-like objects"""

	def __init__(self):
		"""Initializes defaults."""

		#Initialize inherited classes
		handle_Container_Base.__init__(self)

class handle_Notebook_Simple(handle_Base_Notebook):
	"""A handle for working with a wxNotebook."""

	def __init__(self):
		"""Initializes defaults."""

		#Initialize inherited classes
		handle_Container_Base.__init__(self)

		#Internal Variables
		self.notebookImageList = wx.ImageList(16, 16) #A wxImageList containing all tab images associated with this notebook

	def _build(self, argument_catalogue):
		"""Builds a wx notebook object."""

		with self.bookend_build(argument_catalogue):
			flags, tabSide, reduceFlicker, fixedWidth, padding, buildSelf = self._getArguments(argument_catalogue, ["flags", "tabSide", "reduceFlicker", "fixedWidth", "padding", "self"])
			initFunction, postPageChangeFunction, prePageChangeFunction, multiLine = self._getArguments(argument_catalogue, ["initFunction", "postPageChangeFunction", "prePageChangeFunction", "multiLine"])

			size, position = self._getArguments(argument_catalogue, ["size", "position"])

			#Configure Flags            
			flags, x, border = self.getItemMod(flags)

			if (tabSide is None):
				tabSide = "top"
			else:
				if (not isinstance(tabSide, str)):
					errorMessage = "'tabSide' must be a string. Please choose 'top', 'bottom', 'left', or 'right'"
					raise ValueError(errorMessage)
				if (tabSide not in ["top", "bottom", "left", "right"]):
					errorMessage = "'tabSide' must be 'top', 'bottom', 'left', or 'right'"
					raise KeyError(errorMessage)

			style = [eval(flags, {'__builtins__': None, "wx": wx}, {})]
			if (tabSide[0] == "t"):
				style.append(wx.NB_TOP)
			elif (tabSide[0] == "b"):
				style.append(wx.NB_BOTTOM)
			elif (tabSide[0] == "l"):
				style.append(wx.NB_LEFT)
			else:
				style.append(wx.NB_RIGHT)

			if (reduceFlicker):
				style.extend((wx.CLIP_CHILDREN, wx.NB_NOPAGETHEME))
			if (fixedWidth):
				style.append(wx.NB_FIXEDWIDTH)
			if (multiLine):
				style.append(wx.NB_MULTILINE)

			myId = self._getId(argument_catalogue)

			#Create notebook object
			self.thing = wx.Notebook(self.parent.thing, id = myId, size = size, pos = position, style = functools.reduce(operator.ior, style or (0,)))

			#Bind Functions
			self.parent._betterBind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.thing, self.onRefresh)
			if (initFunction is not None):
				initFunctionArgs, initFunctionKwargs = self._getArguments(argument_catalogue, ["initFunctionArgs", "initFunctionKwargs"])
				self.setFunction_init(initFunction, initFunctionArgs, initFunctionKwargs)
			
			if (prePageChangeFunction is not None):
				prePageChangeFunctionArgs, prePageChangeFunctionKwargs = self._getArguments(argument_catalogue, ["prePageChangeFunctionArgs", "prePageChangeFunctionKwargs"])
				self.setFunction_prePageChange(initFunction, initFunctionArgs, initFunctionKwargs)

			if (postPageChangeFunction is not None):
				postPageChangeFunctionArgs, postPageChangeFunctionKwargs = self._getArguments(argument_catalogue, ["postPageChangeFunctionArgs", "postPageChangeFunctionKwargs"])
				self.setFunction_postPageChange(initFunction, initFunctionArgs, initFunctionKwargs)

			#Determine if there is padding on the tabs
			if ((padding is not None) and (padding != -1)):
				#Ensure correct format
				if ((padding[0] is not None) and (padding[0] != -1)):
					width = padding[0]
				else:
					width = 0

				if ((padding[1] is not None) and (padding[1] != -1)):
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


	def setSelection(self, newValue, event = None):
		"""Sets the contextual value for the object associated with this handle to what the user supplies."""

		self.changePage(newValue)

	def getValue(self, event = None):
		"""Gets the contextual value for the object associated with this handle to what the user supplies."""

		index = self.getCurrentPage(index = True)
		return self.getPageText(index)

	#Change Settings
	def setFunction_init(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		"""Changes the function that runs when the object is first created."""

		self.parent._betterBind(wx.EVT_INIT_DIALOG, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)

	def setFunction_prePageChange(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		"""Changes the function that runs when the page begins to change."""

		self.parent._betterBind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)

	def setFunction_postPageChange(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		"""Changes the function that runs when the page has finished changing."""

		self.parent._betterBind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.thing, self.onRefresh, rebind = True) #Bugfix for cloned pages
		self.parent._betterBind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)

	def setFunction_rightClick(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		self._betterBind(wx.EVT_RIGHT_DOWN, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		for handle in self[:]:
			handle.setFunction_rightClick(myFunction = myFunction, myFunctionArgs = myFunctionArgs, myFunctionKwargs = myFunctionKwargs)

	def addPage(self, text = None, panel = {}, sizer = {},
		insert = None, default = False, icon_path = None, icon_internal = False,

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, tabSkip = False, nestPanel = True, nestSizer = True):
		"""Adds a page to the notebook.
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

		kwargs = locals()
		def yieldPage(labelList, textList):
			nonlocal self, insert, default

			if (not labelList):
				return

			#Add pages
			for i, label in enumerate(labelList):
				#Format text
				if (len(textList) is 1):
					text = textList[0]
				else:
					text = textList[i]

				#Get the object
				handle = handle_NotebookPage_Simple()
				handle.type = Types.notebookpage
				handle._build({**kwargs, **locals(), "parent": self}, nestPanel = nestPanel, nestSizer = nestSizer)

				#Determine if there is an icon on the tab
				if (handle.icon is not None):
					#Add this icon to the notebook's image catalogue
					handle.iconIndex = self.thing.notebookImageList.Add(handle.icon)
					self.thing.AssignImageList(self.thing.notebookImageList)

				#Create the tab
				if ((insert is not None) and (insert != -1)):
					if (handle.iconIndex is not None):
						self.thing.InsertPage(insert, handle.myPanel.thing, handle.text, default, handle.iconIndex)
					else:
						self.thing.InsertPage(insert, handle.myPanel.thing, handle.text, default)

				else:
					if (handle.iconIndex is not None):
						self.thing.AddPage(handle.myPanel.thing, handle.text, default, handle.iconIndex)
					else:
						self.thing.AddPage(handle.myPanel.thing, handle.text, default)

				#Record nesting
				self._finalNest(handle)

				yield handle

		###########################################

		#Error Check
		if (isinstance(label, (list, tuple, range)) and isinstance(text, (list, tuple, range))):
			if (len(label) != len(text)):
				errorMessage = f"'label' and 'text' must be the same length for {self.__repr__()}"
				raise ValueError(errorMessage)

		handleList = tuple(yieldPage(self.ensure_container(label, convertNone = False), self.ensure_container(text, convertNone = False)))
		if (not handleList):
			return None
		elif (len(handleList) is 1):
			return handleList[0]
		return handleList

	##Getters
	def getCurrentPage(self, index = None):
		"""Returns the currently selected page from the given notebook

		index (bool) - Determines in what form the page is returned.
			- If True: Returns the page's index number
			- If False: Returns the page's catalogue label
			- If None: Returns the handle object for the page

		Example Input: getCurrentPage()
		Example Input: getCurrentPage(True)
		"""

		currentPage = self.thing.GetSelection()
		if (currentPage == wx.NOT_FOUND):
			return

		if (index):
			return currentPage
		for item in self:
			if (self.getPageIndex(item) == currentPage):
				if (index is None):
					return item
				else:
					return item.label

		errorMessage = f"Unknown Error in getCurrentPage() for {self.__repr__()}"
		raise ValueError(errorMessage)

	def getPage(self, pageLabel = None):
		"""Returns the requested page handle."""

		if (pageLabel is None):
			return self.getCurrentPage()

		if (isinstance(pageLabel, handle_Base_NotebookPage)):
			return pageLabel
		
		if (pageLabel in self):
			return self[pageLabel]

		if (isinstance(pageLabel, int)):
			for page in self:
				if (self.thing.FindPage(page.myPanel.thing) == pageLabel):
					return page
		
		print("--", pageLabel)
		print("--", [item.label for item in self])
		raise NotImplementedError(f"The page {pageLabel} does not exist")

	def getPageIndex(self, pageLabel = None):
		"""Returns the page index for a page with the given label in the given notebook.

		pageLabel (str) - The catalogue label for the panel to add to the notebook

		Example Input: getPageIndex(0)
		"""

		if (pageLabel is None):
			return self.getCurrentPage(index = True)
		
		if (isinstance(pageLabel, int)):
			if ((pageLabel >= 0) and (self.thing.GetPageCount() >= pageLabel)):
				return pageLabel
			return None

		page = self.getPage(pageLabel)
		if (not page.hasClone):
			index = self.thing.FindPage(page.myPanel.thing)
			if (index == wx.NOT_FOUND):
				return None
			return index

		for index in range(self.thing.GetPageCount()):
			if (self.thing.GetPage(index) is not page.myPanel.thing):
				continue
			if (page.text == self.thing.GetPageText(index)):
				return index

	def getPageText(self, pageIndex = None):
		"""Returns the first page index for a page with the given label in the given notebook.

		pageLabel (str) - The catalogue label for the panel to add to the notebook
			- If None: Uses the current page

		Example Input: getPageText()
		Example Input: getPageText(1)
		"""

		if (pageIndex is None):
			pageIndex = self.getCurrentPage(index = True)
		elif (not isinstance(pageIndex, int)):
			pageIndex = self.getPageIndex(pageIndex)

		text = self.thing.GetPageText(pageIndex)

		return text

	def getAllPageText(self):
		"""Returns the text for all pages.

		Example Input: getAllPageText()
		"""

		content = []
		for page in self:
			content.append(page.text)
		content.reverse()

		return content

	def getTabCount(self):
		"""Returns how many tabs the notebook currently has.

		Example Input: notebookGetTabCount()
		"""

		tabCount = self.thing.GetPageCount()

		return tabCount

	def getTabRowCount(self):
		"""Returns how many rows of tabs the notebook currently has.

		Example Input: notebookGetTabRowCount()
		"""

		count = self.thing.GetRowCount()

		return count

	##Setters
	def setPageText(self, pageLabel = None, text = ""):
		"""Changes the given notebook page's tab text.

		pageLabel (str) - The catalogue label for the panel to add to the notebook
		text (str)      - What the page's tab will now say

		Example Input: notebookSetPageText(0, "Ipsum")
		"""

		page = self.getPage(pageLabel)
		page.text = text

		pageNumber = self.getPageIndex(page)
		self.thing.SetPageText(pageNumber, text)

	##Etc
	def clonePage(self, pageLabel = None, *args, switchTo = False, triggerEvent = False, **kwargs):
		"""Adds another page that uses the panel of a previously made page.

		pageLabel (str) - The catalogue label for the panel to clone from
			- If None: Will use the current page

		Example Input: clonePage()
		Example Input: clonePage(1)
		"""

		sourcePage = self.getPage(pageLabel)
		newPage = self.addPage(*args, panel = sourcePage.myPanel, sizer = sourcePage.mySizer, nestPanel = False, nestSizer = False, **kwargs)
		# newPage = self.addPage(*args, panel = sourcePage.myPanel, sizer = sourcePage.mySizer, **kwargs)

		sourcePage.hasClone = True
		newPage.hasClone = True

		if (switchTo):
			newPage.changePage(triggerEvent = triggerEvent)
		elif (self.thing.GetSelection() == sourcePage.getPageIndex()):
			#Toggle the panel back to the source page
			newPage.changePage(triggerEvent = False)
			sourcePage.changePage(triggerEvent = triggerEvent)
		return newPage

	def changePage(self, pageLabel = None, triggerEvent = True):
		"""Changes the page selection on the notebook from the current page to the given page.

		pageLabel (str)     - The catalogue label for the panel to change to
		triggerEvent (bool) - Determiens if a page change and page changing event is triggered
			- If True: The page change events are triggered
			- If False: the page change events are not triggered

		Example Input: notebookChangePage(1)
		Example Input: notebookChangePage(1, triggerEvent = False)
		"""

		pageNumber = self.getPageIndex(pageLabel)
		if (pageNumber == self.thing.GetSelection()):
			return

		if (triggerEvent):
			self.thing.SetSelection(pageNumber)
		else:
			self.thing.ChangeSelection(pageNumber)

	def removePage(self, pageLabel = None):
		"""Removes the given page from the notebook.

		pageLabel (str) - The catalogue label for the panel to add to the notebook

		Example Input: notebookRemovePage(1)
		"""

		self.hidePage(pageLabel)
		del self[pageLabel]

	def hidePage(self, pageLabel = None, state = True):
		"""Hides the given page."""

		if (not state):
			return self.showPage(pageLabel = pageLabel)

		page = self.getPage(pageLabel)
		if (not self.checkPageShown(page)):
			return

		changed = False
		if (page.hasClone):
			currentPage = self.getCurrentPage()
			if ((currentPage is not page) and (currentPage.myPanel.thing is page.myPanel.thing)):
				#Toggle the panel back to the source page
				page.changePage(triggerEvent = False)
				changed = True

		pageNumber = self.getPageIndex(page)
		self.thing.RemovePage(pageNumber)

		if (changed):
			currentPage.changePage(triggerEvent = False)

	def showPage(self, pageLabel = None, state = True, switchTo = False, triggerEvent = False):
		"""Shows the given page."""

		if (not state):
			return self.hidePage(pageLabel = pageLabel)

		page = self.getPage(pageLabel)
		if (not self.checkPageShown(page)):
			self.thing.AddPage(page.myPanel.thing, page.text)

			if ((not switchTo) and (page.hasClone)):
				currentPage = self.getCurrentPage()
				if ((currentPage is not page) and (currentPage.myPanel.thing is page.myPanel.thing)):
					#Toggle the panel back to the source page
					page.changePage(triggerEvent = False)
					currentPage.changePage(triggerEvent = triggerEvent)
		
		if (switchTo):
			page.changePage(triggerEvent = triggerEvent)

	def checkPageShown(self, pageLabel = None):
		"""Returns if the given page is shown or not."""

		page = self.getPage(pageLabel)
		if (not page.hasClone):
			return self.thing.FindPage(page.myPanel.thing) != wx.NOT_FOUND

		for index in range(self.thing.GetPageCount()):
			if (self.thing.GetPage(index) is not page.myPanel.thing):
				continue
			if (page.text == self.thing.GetPageText(index)):
				return True

		return False

	def removeAll(self):
		"""Removes all pages from the notebook.

		Example Input: notebookRemovePage()
		"""

		self.thing.DeleteAllPages()
		for item in self:
			del item

	def nextPage(self):
		"""Selects the next page in the notebook.

		Example Input: notebookNextPage()
		"""

		self.thing.AdvanceSelection()

	def backPage(self):
		"""Selects the previous page in the notebook.

		Example Input: notebookBackPage()
		"""

		self.thing.AdvanceSelection(False)

class handle_Notebook_Aui(handle_Notebook_Simple):
	"""A handle for working with a wxNotebook."""

	def _build(self, argument_catalogue):
		"""Builds a wx auiNotebook object."""

		with self.bookend_build(argument_catalogue):
			flags, buildSelf = self._getArguments(argument_catalogue, ["flags", "self"])
			initFunction, postPageChangeFunction, prePageChangeFunction = self._getArguments(argument_catalogue, ["initFunction", "postPageChangeFunction", "prePageChangeFunction"])

			tabSide, tabSplit, tabMove, tabBump = self._getArguments(argument_catalogue, ["tabSide", "tabSplit", "tabMove", "tabBump"])
			tabSmart, tabOrderAccess, tabFloat = self._getArguments(argument_catalogue, ["tabSmart", "tabOrderAccess", "tabFloat"])
			addScrollButton, addListDrop, addCloseButton = self._getArguments(argument_catalogue, ["addScrollButton", "addListDrop", "addCloseButton"])
			closeOnLeft, middleClickClose = self._getArguments(argument_catalogue, ["closeOnLeft", "middleClickClose"])
			fixedWidth, drawFocus = self._getArguments(argument_catalogue, ["fixedWidth", "drawFocus"])

			#Create Styles
			if (tabSide is not None):
				if (tabSide[0] == "t"):
					style = "wx.lib.agw.aui.AUI_NB_TOP"
				elif (tabSide[0] == "b"):
					style = "wx.lib.agw.aui.AUI_NB_BOTTOM"
				elif (tabSide[0] == "l"):
					style = "wx.lib.agw.aui.AUI_NB_LEFT"
				else:
					style = "wx.lib.agw.aui.AUI_NB_RIGHT"
			else:
				style = "wx.lib.agw.aui.AUI_NB_TOP"

			if (tabSplit):
				style += "|wx.lib.agw.aui.AUI_NB_TAB_SPLIT"

			if (tabMove):
				style += "|wx.lib.agw.aui.AUI_NB_TAB_MOVE"

			if (tabBump):
				style += "|wx.lib.agw.aui.AUI_NB_TAB_EXTERNAL_MOVE"

			if (tabSmart):
				# style += "|wx.lib.agw.aui.AUI_NB_HIDE_ON_SINGLE_TAB"
				style += "|wx.lib.agw.aui.AUI_NB_SMART_TABS"
				style += "|wx.lib.agw.aui.AUI_NB_DRAW_DND_TAB"

			if (tabOrderAccess):
				style += "|wx.lib.agw.aui.AUI_NB_ORDER_BY_ACCESS"

			if (tabFloat):
				style += "|wx.lib.agw.aui.AUI_NB_TAB_FLOAT"

			if (fixedWidth):
				style += "|wx.lib.agw.aui.AUI_NB_TAB_FIXED_WIDTH"

			if (addScrollButton):
				style += "|wx.lib.agw.aui.AUI_NB_SCROLL_BUTTONS"

			if (addListDrop is not None):
				if (addListDrop):
					style += "|wx.lib.agw.aui.AUI_NB_WINDOWLIST_BUTTON"
				else:
					style += "|wx.lib.agw.aui.AUI_NB_USE_IMAGES_DROPDOWN"

			if (addCloseButton is not None):
				if (addCloseButton):
					style += "|wx.lib.agw.aui.AUI_NB_CLOSE_ON_ALL_TABS"
				else:
					style += "|wx.lib.agw.aui.AUI_NB_CLOSE_ON_ACTIVE_TAB"

				if (closeOnLeft):
					style += "|wx.lib.agw.aui.AUI_NB_CLOSE_ON_TAB_LEFT"

			if (middleClickClose):
				style += "|wx.lib.agw.aui.AUI_NB_MIDDLE_CLICK_CLOSE"

			if (not drawFocus):
				style += "|wx.lib.agw.aui.AUI_NB_NO_TAB_FOCUS"

			self.thing = wx.lib.agw.aui.auibook.AuiNotebook(self.parent.thing, agwStyle = eval(style, {'__builtins__': None, "wx.lib.agw.aui": wx.lib.agw.aui}, {}))

			#Set values
			if (isinstance(self, handle_Window)):
				self.myWindow = buildSelf
			else:
				self.myWindow = buildSelf.myWindow

			#Link to window's aui manager
			if (self.myWindow.auiManager is None):
				self.myWindow.auiManager = handle_AuiManager(self, self.myWindow)#, reduceFlicker = reduceFlicker)
				self._build(locals())

			self.myWindow.auiManager.addPane(self)

	def setSelection(self, newValue, event = None):
		"""Sets the contextual value for the object associated with this handle to what the user supplies."""

		warnings.warn(f"Add {self.type.name} to setSelection() for {self.__repr__()}", Warning, stacklevel = 2)

	def getValue(self, event = None):
		"""Gets the contextual value for the object associated with this handle to what the user supplies."""

		warnings.warn(f"Add {self.type.name} to setSelection() for {self.__repr__()}", Warning, stacklevel = 2)

	#Change Settings
	def setFunction_init(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		"""Changes the function that runs when the object is first created."""

		warnings.warn(f"Add {self.type.name} to setFunction_init() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_prePageChange(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		"""Changes the function that runs when the page begins to change."""

		warnings.warn(f"Add {self.type.name} to setFunction_prePageChange() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_postPageChange(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		"""Changes the function that runs when the page has finished changing."""

		warnings.warn(f"Add {self.type.name} to setFunction_postPageChange() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_rightClick(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):

		warnings.warn(f"Add {self.type.name} to setFunction_rightClick() for {self.__repr__()}", Warning, stacklevel = 2)

class handle_Base_NotebookPage(handle_SizerProxy, handle_Container_Base):
	"""A handle for working with a wxNotebook."""

	def __init__(self):
		"""Initializes defaults."""

		#Initialize inherited classes
		handle_SizerProxy.__init__(self)
		handle_Container_Base.__init__(self)

		self.thing = None
		self.myPanel = None
		self.myManager = None
		self.text = None
		self.icon = None
		self.iconIndex = None
		self.type = None
		self.hasClone = False

	def __str__(self):
		"""Gives diagnostic information on the Notebook when it is printed out."""

		output = handle_Container_Base.__str__(self)

		if (self.text is not None):
			output += f"-- text: {self.text}\n"
		if (self.icon is not None):
			output += f"-- icon: {self.icon}\n"

		return output

	@contextlib.contextmanager
	def _build(self, argument_catalogue, nestPanel = True, nestSizer = True, preBuild = True, useRootParent = False):
		"""Adds a page to the notebook.
		Lists can be given to add multiple pages. They are added in order from left to right.
		If only a 'pageLabel' is a list, they will all have the same 'text'.
		If 'pageLabel' and 'text' are a list of different lengths, it will not add any of them.

		pageLabel (str)     - The catalogue label for the panel to add to the notebook
		text (str)          - What the page's tab will say
			- If None: The tab will be blank
		label (str)       - What this is called in the idCatalogue

		icon_path (str)      - Determiens if there should be an icon to the left of the text
		icon_internal (bool) - Determiens if 'image_path' refers to an internal image

		Example Input: _build(0)
		Example Input: _build("page_1")
		Example Input: _build(0, "Lorem")
		Example Input: _build([0, 1], "Lorem")
		Example Input: _build([0, 1], ["Lorem", "Ipsum"])
		Example Input: _build(0, "Lorem", insert = 2)
		Example Input: _build(0, "Lorem", select = True)
		"""

		with self.bookend_build(argument_catalogue, preBuild = preBuild):
			text, panel, sizer = self._getArguments(argument_catalogue, ("text", "panel", "sizer"))

			#Setup Panel
			if (isinstance(panel, dict)):
				if (useRootParent):
					panel["parent"] = self.myWindow.mainPanel
				else:
					panel["parent"] = self.parent
				self.myPanel = self._readBuildInstructions_panel(self, 0, panel)
			else:
				self.myPanel = panel

			#Setup Sizer
			if (isinstance(sizer, dict)):
				sizer["parent"] = self.myPanel
				self.mySizer = self._readBuildInstructions_sizer(self, 0, sizer)
			else:
				self.mySizer = sizer

			if (nestSizer):
				self.myPanel.nest(self.mySizer)

			if (nestPanel):
				self._finalNest(self.myPanel)

			#Format text
			if (text is None):
				self.text = ""
			else:
				if (not isinstance(text, str)):
					self.text = f"{text}"
				else:
					self.text = text

			yield

	def getSizer(self):
		return self.mySizer

	def remove(self, *args, **kwargs):
		"""Removes the given page from the notebook.

		Example Input: notebookRemovePage()
		"""

		return self.parent.remove(self, *args, **kwargs)

	def hidePage(self, *args, **kwargs):
		
		return self.parent.hidePage(self, *args, **kwargs)

	def showPage(self, *args, **kwargs):
		
		return self.parent.showPage(self, *args, **kwargs)

	def checkPageShown(self, *args, **kwargs):
		
		return self.parent.checkPageShown(self, *args, **kwargs)

	def changePage(self, *args, **kwargs):
		
		return self.parent.changePage(self, *args, **kwargs)

	def getIndex(self, *args, **kwargs):
		"""Returns the page index for a page with the given label in the given notebook.

		Example Input: getIndex()
		"""

		return self.parent.getIndex(self, *args, **kwargs)

	def getValue(self, event = None):
		"""Returns the first page index for a page with the given label in the given notebook.

		Example Input: getValue()
		"""

		return self.getPageText()


	def getPageText(self):
		"""Returns the page text.

		Example Input: getPageText()
		"""

		return self.text

	def getPageIndex(self):
		"""Returns the page text.

		Example Input: getPageIndex()
		"""

		return self.parent.getPageIndex(self)

class handle_NotebookPage_Simple(handle_Base_NotebookPage):
	"""A handle for working with a page in a wxNotebook."""

	def __str__(self):
		"""Gives diagnostic information on the Notebook when it is printed out."""

		output = handle_Container_Base.__str__(self)

		if (self.text is not None):
			output += f"-- text: {self.text}\n"
		if (self.icon is not None):
			output += f"-- icon: {self.icon}\n"

		return output

	def _build(self, argument_catalogue, **kwargs):
		"""Adds a page to the notebook.
		Lists can be given to add multiple pages. They are added in order from left to right.
		If only a 'pageLabel' is a list, they will all have the same 'text'.
		If 'pageLabel' and 'text' are a list of different lengths, it will not add any of them.

		pageLabel (str)     - The catalogue label for the panel to add to the notebook
		text (str)          - What the page's tab will say
			- If None: The tab will be blank
		label (str)       - What this is called in the idCatalogue

		icon_path (str)      - Determiens if there should be an icon to the left of the text
		icon_internal (bool) - Determiens if 'image_path' refers to an internal image

		Example Input: _build(0)
		Example Input: _build("page_1")
		Example Input: _build(0, "Lorem")
		Example Input: _build([0, 1], "Lorem")
		Example Input: _build([0, 1], ["Lorem", "Ipsum"])
		Example Input: _build(0, "Lorem", insert = 2)
		Example Input: _build(0, "Lorem", select = True)
		"""

		with super()._build(argument_catalogue, **kwargs):
			#Format Icon
			icon_path, icon_internal = self._getArguments(argument_catalogue, ["icon_path", "icon_internal"])
			if (icon_path is not None):
				self.icon = self.getImage(icon_path, icon_internal)#, returnIcon = True)
			else:
				self.icon = None
				self.iconIndex = None

	##Setters
	def setValue(self, newValue = "", event = None):
		"""Changes the given notebook page's tab text.

		newValue (str) - What the page's tab will now say

		Example Input: notebookSetPageText("Ipsum")
		"""

		self.parent.setPageText(self, text = newValue)

	def setFunction_rightClick(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):

		self._betterBind(wx.EVT_RIGHT_DOWN, self.myPanel.thing, myFunction, myFunctionArgs, myFunctionKwargs)


class handle_NotebookPage_Aui(handle_Base_NotebookPage):
	"""A handle for working with a wxNotebook."""

	##Setters
	def setValue(self, newValue = "", event = None):
		"""Changes the given notebook page's tab text.

		newValue (str) - What the page's tab will now say

		Example Input: notebookSetPageText("Ipsum")
		"""

		if (self.label is None):
			warnings.warn(f"A label is needed for {self.__repr__()} to change the caption", Warning, stacklevel = 2)

		self.myManager.setTitle(self.label, newValue)

	#Etc
	def dockCenter(self, *args, **kwargs):
		"""Overload for dockCenter() in handle_AuiManager."""

		if (self.label is None):
			warnings.warn(f"A label is needed for {self.__repr__()} to programatically dock it", Warning, stacklevel = 2)

		self.myManager.dockCenter(self.label, *args, **kwargs)

	def dockTop(self, *args, **kwargs):
		"""Overload for dockTop() in handle_AuiManager."""

		if (self.label is None):
			warnings.warn(f"A label is needed for {self.__repr__()} to programatically dock it", Warning, stacklevel = 2)

		self.myManager.dockTop(self.label, *args, **kwargs)

	def dockBottom(self, *args, **kwargs):
		"""Overload for dockBottom() in handle_AuiManager."""

		if (self.label is None):
			warnings.warn(f"A label is needed for {self.__repr__()} to programatically dock it", Warning, stacklevel = 2)

		self.myManager.dockBottom(self.label, *args, **kwargs)

	def dockLeft(self, *args, **kwargs):
		"""Overload for dockLeft() in handle_AuiManager."""

		if (self.label is None):
			warnings.warn(f"A label is needed for {self.__repr__()} to programatically dock it", Warning, stacklevel = 2)

		self.myManager.dockLeft(self.label, *args, **kwargs)

	def dockRight(self, *args, **kwargs):
		"""Overload for dockRight() in handle_AuiManager."""

		if (self.label is None):
			warnings.warn(f"A label is needed for {self.__repr__()} to programatically dock it", Warning, stacklevel = 2)

		self.myManager.dockRight(self.label, *args, **kwargs)

class handle_WizardPage(handle_NavigatorBase, handle_Base_NotebookPage):
	"""A handle for working with a wxNotebook."""

	def __init__(self, wizard):
		"""Initializes defaults."""

		#Initialize inherited classes
		handle_Base_NotebookPage.__init__(self)
		handle_NavigatorBase.__init__(self)

		self.wizard = wizard
		self.pageNode = None
		self.currentNode = None
		self.pageElements = set()

	@contextlib.contextmanager
	def _build(self, argument_catalogue):
		"""Adds a page to the notebook.
		Lists can be given to add multiple pages. They are added in order from left to right.
		If only a 'pageLabel' is a list, they will all have the same 'text'.
		If 'pageLabel' and 'text' are a list of different lengths, it will not add any of them.

		pageLabel (str)     - The catalogue label for the panel to add to the notebook
		text (str)          - What the page's tab will say
			- If None: The tab will be blank
		label (str)       - What this is called in the idCatalogue

		icon_path (str)      - Determiens if there should be an icon to the left of the text
		icon_internal (bool) - Determiens if 'image_path' refers to an internal image

		Example Input: _build(0)
		Example Input: _build("page_1")
		Example Input: _build(0, "Lorem")
		Example Input: _build([0, 1], "Lorem")
		Example Input: _build([0, 1], ["Lorem", "Ipsum"])
		Example Input: _build(0, "Lorem", insert = 2)
		Example Input: _build(0, "Lorem", select = True)
		"""

		with super()._build(argument_catalogue, nestPanel = False, nestSizer = False, useRootParent = True):
			self.thing = self.myPanel.thing
			
			with self._makeSizerBox() as rootSizer:
				rootSizer.nest(self.mySizer, flex = 1)
				self.myPanel.nest(rootSizer)

			parentNode, default = self._getArguments(argument_catalogue, ("parentNode", "default",))
			self.nodeLabel = self.label or f"{len(self.parent.pageNode.children)}"
			self.pageNode = anytree.Node(self.nodeLabel, parent = parentNode, handle = self)

			if (default):
				parentNode.default = self.pageNode.name

			yield

	def addPage(self, *args, parentNode = None, **kwargs):
		"""Adds a page to the wizard.
		Lists can be given to add multiple pages. They are added in order from left to right.
		If only a 'pageLabel' is a list, they will all have the same 'text'.
		If 'pageLabel' and 'text' are a list of different lengths, it will not add any of them.

		text (str)  - What the page's tab will say
			- If None: The tab will be blank
		label (str) - What this is called in the idCatalogue

		Example Input: addPage()
		Example Input: addPage("Lorem")
		Example Input: addPage(["Lorem", "Ipsum"])
		Example Input: addPage({"choice_1": "Lorem", "choice_2": "Ipsum"})
		"""

		return self.wizard.addPage(*args, parentNode = parentNode or self.pageNode, **kwargs)


# 	def getValue(self, event = None):
# 		"""Returns the first page index for a page with the given label in the given notebook.

# 		Example Input: getValue()
# 		"""

# 		warnings.warn(f"Add {self.type.name} to getValue() for {self.__repr__()}", Warning, stacklevel = 2)

# 	##Setters
# 	def setValue(self, newValue = "", event = None):
# 		"""Changes the given notebook page's tab text.

# 		newValue (str) - What the page's tab will now say

# 		Example Input: notebookSetPageText("Ipsum")
# 		"""

# 		warnings.warn(f"Add {self.type.name} to setValue() for {self.__repr__()}", Warning, stacklevel = 2)

# class _MyWizardPage(wx.adv.WizardPage):
# 	def __init__(self, parent, nextPage = None, previousPage = None, autoNext = True, autoPrevious = True, bitmap = wx.NullBitmap):

# 		wx.adv.WizardPage.__init__(self, parent.parent.thing, bitmap = bitmap or wx.NullBitmap)

# 		self.parent = parent
# 		pages = self.parent.parent.pages
		
# 		if ((not autoPrevious) or (not pages)):
# 			self.SetPrev(previousPage = previousPage)
# 		else:
# 			self.SetPrev(previousPage = previousPage or pages[-1])

# 		self.SetNext(nextPage = nextPage)
# 		if (autoNext and pages):
# 			pages[-1].thing.SetNext(nextPage = self.parent)

# 	def SetNext(self, nextPage = None):
# 		self.nextPage = nextPage
 
# 	def SetPrev(self, previousPage = None):
# 		self.previousPage = previousPage
 
# 	def GetNext(self):
# 		if (self.nextPage is not None):
# 			return self.nextPage.thing
 
# 	def GetPrev(self):
# 		if (self.previousPage is not None):
# 			return self.previousPage.thing

class MyApp():
	"""Needed to make the GUI work.
	For more functions to override: https://wxpython.org/Phoenix/docs/html/wx.AppConsole.html
	"""

	def __init__(self, parent = None, startInThread = False, **kwargs):
		self.startInThread = startInThread

		if (startInThread):
			self.app = self._MyAppThread(self, root = parent, kwargs = kwargs)
		else:
			self.app = self._App(self, root = parent, **kwargs)

	def MainLoop(self):
		self.app.MainLoop()

	class _App(wx.App):
		def __init__(self, parent, root = None, redirect = False, filename = None, 
			useBestVisual = False, clearSigInt = True, newMainLoop = None, **kwargs):
			"""Needed to make the GUI work."""

			self.root = root
			self.parent = parent
			self.newMainLoop = newMainLoop

			wx.App.__init__(self, redirect = redirect, filename = filename, useBestVisual = useBestVisual, clearSigInt = clearSigInt)

			self.exceptionHandler = ExceptionHandling.ExceptionHandler(self, **kwargs)

		def OnInit(self):
			"""Needed to make the GUI work.
			Single instance code modified from: https://wxpython.org/Phoenix/docs/html/wx.SingleInstanceChecker.html
			"""

			#Account for multiple instances of the same app
			if (self.root is not None):
				if (self.root.oneInstance):
					#Ensure only one instance per user runs
					self.root.oneInstance_name = f"SingleApp-{wx.GetUserId()}"
					self.root.oneInstance_instance = wx.SingleInstanceChecker(self.root.oneInstance_name)

					if self.root.oneInstance_instance.IsAnotherRunning():
						wx.MessageBox("Cannot run multiple instances of this program", "Runtime Error")
						return False

			if (self.newMainLoop is not None):
				self.newMainLoop()
				wx.CallAfter(self.ExitMainLoop)

			#Allow the app to progress
			return True

		def OnExit(self):
			"""Notifies the controller that the exit process has begun."""

			self.root.exiting = True

			return wx.App.OnExit(self)

	class _MyAppThread(threading.Thread):
		"""Allows the Main Loop for wx.App to run in a separate thread.
		Modified code from: https://wiki.wxpython.org/MainLoopAsThread
		"""

		def __init__(self, parent, root = None, kwargs = {}):
			#Create Thread
			threading.Thread.__init__(self)
			self.setDaemon(1)

			#Internal Variables
			self.root = root
			self.parent = parent
			self.kwargs = kwargs
			self.building = True

			self.start()
		
		def run(self):
			self.app = self.parent._App(self.parent, root = self.root, **self.kwargs)
			while (self.building):
				time.sleep(100 / 1000)
			self.app.MainLoop()

		def MainLoop(self):
			self.building = False

class Controller(Utilities, CommonEventFunctions, MyUtilities.threadManager.CommonFunctions, MyUtilities.common.CATALOGUE):
	"""This module will help to create a simple GUI using wxPython without having to learn how to use the complicated program."""

	def __init__(self, debugging = False, best = False, oneInstance = False, 
		allowBuildErrors = None, checkComplexity = True, startInThread = False, 
		newMainLoop = None, printMakeVariables = False, logCMD = False, splash = None, **kwargs):
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

		startInThread (bool) - Determines if wx.App.MainLoop runs in the main thread or not
		printMakeVariables (bool) - Determines if the variables used to make a widget should be printed or not

		newMainLoop (function) - A function to run instead of wx.App.MainLoop
			- If None: Will run wx.App.MainLoop

		splash (SplashProcess) - The splash screen handle
			- If None: Will assume there is no splash screen

		Example Input: Controller()
		Example Input: Controller(debugging = True)
		Example Input: Controller(debugging = "log.txt")  
		Example Input: Controller(oneInstance = True)
		Example Input: Controller(startInThread = True)
		"""

		#Initialize Inherited classes
		Utilities.__init__(self)
		CommonEventFunctions.__init__(self)
		MyUtilities.threadManager.CommonFunctions.__init__(self)

		#Setup Internal Variables
		self.labelCatalogue = {} #A dictionary that contains all the windows made for the gui. {windowLabel: myFrame}
		self.labelCatalogueOrder = [] #A list of what order things were added to the label catalogue. [windowLabel 1, windowLabel 2]
		self.backgroundFunction_pauseOnDialog = {} #A list of background functions to pause if a dialog box is being shown {catalogue variable (str): self: myFunction: {"state": if it should pause (bool), "exclude": what to not pause on (list)}
		self.unnamedList = [] #A list of the windows created without labels
		self.nestingOrder = []
		self.oneInstance = oneInstance #Allows the user to run only one instance of this gui at a time
		self.allowBuildErrors = allowBuildErrors
		self.nestingAddress = []
		self.nested = True #Removes any warnings that may come up
		self.checkComplexity = checkComplexity
		self.printMakeVariables = printMakeVariables
		self.windowDisabler = None
		self.controller = self
		self.splash = splash
		self.queue_statusText = MyUtilities.common.PriorityQueue(defaultPriority = 100)

		self.exiting = False
		self.finishing = False
		self.loggingPrint = False
		# self.old_stdout = sys.stdout.write
		# self.old_stderr = sys.stderr.write

		if (logCMD):
			self.logCMD()

		#Record Address
		self._setAddressValue([id(self)], {None: self})
		self.listener_statusText = self.threadManager.listen(self.listenStatusText, label = "GUI_Maker.statusText", delay = 100, errorFunction = self.listenStatusText_handleError, autoStart = False)

		#Create the wx app object
		self.app = MyApp(parent = self, startInThread = startInThread, newMainLoop = newMainLoop, **kwargs)

	def __str__(self):
		"""Gives diagnostic information on the GUI when it is printed out."""
		global nestingCatalogue

		output = f"Controller()\n-- id: {id(self)}\n"
		# windowsList = [item for item in self.labelCatalogue.values() if isinstance(item, handle_Window)]
		windowsList = self._getNested(handle_Window)
		if (len(windowsList) + len(self.unnamedList) != 0):
			output += f"-- windows: {len(windowsList) + len(self.unnamedList)}\n"
		if (len(nestingCatalogue) != 0):
			output += f"-- nesting catalogue: {nestingCatalogue}\n"

		return output

	def __repr__(self):
		representation = f"GUIController(id = {id(self)}"

		if (hasattr(self, "label")):
			representation += f", label = {self.label})"
		else:
			representation += ")"

		return representation

	def __contains__(self, key):
		"""Allows the user to use get() when using 'in'."""

		return self.get(key, returnExists = True)

	def __enter__(self):
		"""Allows the user to use a with statement to build the GUI."""

		return self

	def __exit__(self, exc_type, exc_value, traceback):
		"""Allows the user to use a with statement to build the GUI."""

		#Error handling
		if (traceback is not None):
			if (self.allowBuildErrors is None):
				return False
			elif (not self.allowBuildErrors):
				return True

		self.finish()

	def __len__(self):
		"""Returns the number of immediate nested elements.
		Does not include elements that those nested elements may have nested.
		"""

		return len(self.labelCatalogue) + len(self.unnamedList)

	def __iter__(self):
		"""Returns an iterator object that provides the nested objects."""
		
		nestedList = self._getNested()
		return MyUtilities.common.CommonIterator(nestedList)

	def __getitem__(self, key):
		"""Allows the user to index the handle to get nested elements with labels."""

		return self.get(key)

	def __setitem__(self, key, value):
		"""Allows the user to index the handle to get nested elements with labels."""

		self.labelCatalogue[key] = value

	def __delitem__(self, key):
		"""Allows the user to index the handle to get nested elements with labels."""

		self.labelCatalogueOrder.remove(key)
		del self.labelCatalogue[key]

	def exit(self):
		"""Closes the GUI."""

		self.app.OnExit()

	def get(self, *args, returnExists = False, **kwargs):
		"""Overload for get() in Utilities."""

		#Check nested windows first
		windowList = Utilities.get(self, None, typeList = [handle_Window])
		for window in windowList:
			if (returnExists):
				return window.get(*args, returnExists = returnExists, **kwargs)
			elif (window.get(*args, returnExists = True, **kwargs)):
				return window.get(*args, returnExists = returnExists, **kwargs)

		#It is not a window item, so check inside of self
		return Utilities.get(self, *args, returnExists = returnExists, **kwargs)

	def getValue(self, label, *args, **kwargs):
		"""Overload for getValue for handle_Widget_Base."""

		handle = self.get(label, *args, **kwargs)
		event = self._getArgument_event(label, args, kwargs)
		value = handle.getValue(event = event)
		return value

	def getIndex(self, label, *args, **kwargs):
		"""Overload for getIndex for handle_Widget_Base."""

		handle = self.get(label, *args, **kwargs)
		event = self._getArgument_event(label, args, kwargs)
		value = handle.getIndex(event = event)
		return value

	def getAll(self, label, *args, **kwargs):
		"""Overload for getAll for handle_Widget_Base."""

		handle = self.get(label, *args, **kwargs)
		event = self._getArgument_event(label, args, kwargs)
		value = handle.getAll(event = event)
		return value

	def getLabel(self, *args, label = None, **kwargs):
		"""Overload for getLabel for handle_Widget_Base."""

		handle = self.get(label, *args, **kwargs)
		event = self._getArgument_event(label, args, kwargs)
		value = handle.getLabel(event = event)
		return value

	def setValue(self, label, newValue, *args, **kwargs):
		"""Overload for setValue for handle_Widget_Base."""

		handle = self.get(label, *args, **kwargs)
		event = self._getArgument_event(label, args, kwargs)
		handle.setValue(newValue, event = event)

	def setSelection(self, label, newValue, *args, **kwargs):
		"""Overload for setSelection for handle_Widget_Base."""

		handle = self.get(label, *args, **kwargs)
		event = self._getArgument_event(label, args, kwargs)
		handle.setSelection(newValue, event = event)

	#Main Objects
	def addWindow(self, label = None, title = "", size = wx.DefaultSize, position = wx.DefaultPosition, panel = True, autoSize = True,
		tabTraversal = True, stayOnTop = False, floatOnParent = False, endProgram = True, smallerThanScreen = True,
		resize = True, minimize = True, maximize = True, close = True, icon = None, internal = False, topBar = True,

		initFunction = None, initFunctionArgs = None, initFunctionKwargs = None, 
		delFunction = None, delFunctionArgs = None, delFunctionKwargs = None, 
		idleFunction = None, idleFunctionArgs = None, idleFunctionKwargs = None, 

		hidden = True, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		parent = None, handle = None, tabSkip = False):
		"""Creates a new window.

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
		
		panel (bool)    - If True: All content within the window will be nested inside a main panel
		autoSize (bool) - If True: The window will determine the best size for itself
		icon (str)      - The file path to the icon for the window
			If None: No icon will be shown
		internal (bool) - If True: The icon provided is an internal icon, not an external file
		
		endProgram (bool) - Determines what happens when the close button is pressed
			- If True: Runs onExit()
			- If False: Runs onQuit()
			- If None: Runs onHideWindow()
		
		smallerThanScreen (bool) - Determines if the window can be larger than the screen size
			~ Calling the function setMaximumFrameSize() will overwrite this
			- If True: The window cannot be larger than the combined size of all monitors
			- If int: The window cannot be larger than the size of this monitor (0 being the left most)
			- If list: The window cannot be larger than the sum of the size of the monitors listed
			- If False: Does Nothing
			- If None: Does Nothing

		Example Input: addWindow()
		Example Input: addWindow(0)
		Example Input: addWindow(0, title = "Example")

		Example Input: addWindow(smallerThanScreen = None)
		Example Input: addWindow(smallerThanScreen = 0)
		Example Input: addWindow(smallerThanScreen = [0, 2])
		"""

		handle = handle_Window(self)
		handle.type = Types.frame
		handle._build(locals())
		self._finalNest(handle)

		return handle

	def addDialog(self, label = None, title = "", size = wx.DefaultSize, position = wx.DefaultPosition, panel = True, 
		tabTraversal = True, stayOnTop = False, floatOnParent = False, valueLabel = None, smallerThanScreen = True,
		resize = True, minimize = False, maximize = False, close = False, icon = None, internal = False, topBar = None,
		addYes = False, addNo = None, addOk = False, addCancel = False, addClose = False, addApply = False, addLine = False,

		initFunction = None, initFunctionArgs = None, initFunctionKwargs = None, 
		delFunction = None, delFunctionArgs = None, delFunctionKwargs = None, 

		hidden = True, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		parent = None, handle = None, tabSkip = False):
		"""Creates a new dialog window.

		label (any) - What this is catalogued as
		valueLabel (any) - The label for the widget to get the value for on getValue()
			- If None: The user must set it using setValueLabel() before calling the dialog up, or they will get an error
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
		endProgram (bool)   - Determines what happens when the close button is pressed
			- If True: runs onExit()
			- If False: runs onQuit()
			- If None: runs onHideWindow()
		
		smallerThanScreen (bool) - Determines if the window can be larger than the screen size
			~ Calling the function setMaximumFrameSize() will overwrite this
			- If True: The window cannot be larger than the combined size of all monitors
			- If int: The window cannot be larger than the size of this monitor (0 being the left most)
			- If list: The window cannot be larger than the sum of the size of the monitors listed
			- If False: Does Nothing
			- If None: Does Nothing
		
		Example Input: addDialog()
		Example Input: addDialog(0)
		Example Input: addDialog(0, title = "Example")
		"""

		handle = handle_Window(self)
		handle.type = Types.dialog
		handle._build(locals())
		self._finalNest(handle)

		return handle

	def addWizard(self, label = None, title = "", position = wx.DefaultPosition, size = wx.DefaultSize, panel = True, 
		image = None, internal = False, icon = None, icon_internal = False, resizable = True,
		tabTraversal = True, stayOnTop = False, floatOnParent = False, valueLabel = None, smallerThanScreen = True,

		hidden = True, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		parent = None, handle = None, tabSkip = False
		):
		"""Creates a new wizard dialog window.

		Example Input: addWizard()
		Example Input: addWizard(0)
		Example Input: addWizard(0, title = "Example")
		"""

		handle = handle_Wizard(self)
		handle.type = Types.wizard
		handle._build(locals())
		self._finalNest(handle)

		return handle

	#Background Threads
	def start_listenStatusText(self):
		"""Starts listening to listenStatusText()."""

		self.listener_statusText.start()

	def stop_listenStatusText(self):
		"""Stops listening to listenStatusText()."""

		self.listener_statusText.stop()

	def listenStatusText_handleError(self, error = None):
		traceback.print_exception(type(error), error, error.__traceback__)

	def listenStatusText(self):
		"""Checks if a status bar needs to be changed."""

		try:
			myFunction, args, kwargs = self.queue_statusText.get(False) #doesn't block
			success = myFunction(*args, **kwargs)
			if (not success):
				self.queue_statusText.put((myFunction, args, kwargs), priority = 50)
		
		except queue.Empty: #raised when queue is empty
			pass

	#Logistic Functions
	def finish(self):
		"""Run this when the GUI is finished."""
		global nestingCatalogue

		def nestCheck(catalogue):
			"""Makes sure everything is nested."""

			# valueList = [item for item in catalogue.values() if isinstance(item, dict)]
			
			for item in catalogue.values():
				#Skip Widgets
				if (not isinstance(item, handle_Widget_Base)): # or True):
					if (isinstance(item, dict)):
						nestCheck(item)
					else:
						if (not item.nested):
							warnings.warn(f"{item.__repr__()} not nested", Warning, stacklevel = 2)

		self.finishing = True

		#Make sure all things are nested
		# nestCheck(nestingCatalogue)
		
		#Take care of last minute things
		# windowsList = [item for item in self.labelCatalogue.values() if isinstance(item, handle_Window)]
		windowsList = self._getNested(include = handle_Window)
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
						myFrame._betterBind(wx.EVT_MENU, myFrame.thing, contents[0], contents[1], contents[2], mode = 2)
						# asciiValue = myFrame.keyBind(key, thing, contents[0], myFunctionArgsList = contents[1], myFunctionKwargsList = contents[2], event = wx.EVT_MENU, myId = myId)

						#Add to accelerator Table
						acceleratorTableQueue.append((wx.ACCEL_CTRL, 83, myId))

				acceleratorTable = wx.AcceleratorTable(acceleratorTableQueue)
				myFrame.thing.SetAcceleratorTable(acceleratorTable)

			#Run any final functions
			functionList = myFrame.finalFunctionList[:]
			functionList.extend(list(myFrame.finalFunctionCatalogue.values()))
			for myFunction, myFunctionArgs, myFunctionKwargs in functionList:
				self.runMyFunction(myFunction, myFunctionArgs, myFunctionKwargs)

			#Make sure that the window is up to date
			myFrame.updateWindow()

		self.start_listenStatusText()
		
		if (self.splash is not None):
			self.splash.hide()

		self.finishing = False

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

		if (enabled is not None):
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

		# def new_stdout(*args, fileName = "cmd_log.log", timestamp = True, **kwargs):
		# 	"""Overrides the print function to also log the information printed.

		# 	fileName (str)   - The filename for the log
		# 	timestamp (bool) - Determines if the timestamp is added to the log
		# 	"""
		# 	nonlocal self

		# 	self._logPrint(*args, fileName = fileName, timestamp = timestamp, **kwargs)

		# 	#Run the normal print function
		# 	return self.old_stdout(*args)

		# def new_stderr(*args, fileName = "error_log.log", timestamp = True, **kwargs):
		# 	"""Overrides the stderr function to also log the error information.

		# 	fileName (str)   - The filename for the log
		# 	timestamp (bool) - Determines if the timestamp is added to the log
		# 	"""
		# 	nonlocal self

		# 	self._logError(*args, fileName = fileName, timestamp = timestamp, **kwargs)

		# 	#Run the normal stderr function
		# 	return self.old_stderr(*args)

		# if (not self.loggingPrint):
		# 	self.loggingPrint = True

		# 	sys.stdout.write = new_stdout
		# 	sys.stderr.write = new_stderr
		# else:
		# 	warnings.warn(f"Already logging cmd outputs for {item.__repr__()}", Warning, stacklevel = 2)

	def isClosing(self):
		"""Returns if the GUI is trying to close or not.

		Example Input: isClosing()
		"""

		return self.exiting

	#Overloads - handle_Window
	def setWindowSize(self, windowLabel, *args, **kwargs):
		"""Overload for setWindowSize in handle_Window()."""

		myFrame = self.getWindow(windowLabel, frameOnly = False)
		myFrame.setWindowSize(*args, **kwargs)

	def setMinimumFrameSize(self, windowLabel, *args, **kwargs):
		"""Overload for setMinimumFrameSize in handle_Window()."""

		myFrame = self.getWindow(windowLabel, frameOnly = False)
		myFrame.setMinimumFrameSize(*args, **kwargs)

	def setMaximumFrameSize(self, windowLabel, *args, **kwargs):
		"""Overload for setMaximumFrameSize in handle_Window()."""

		myFrame = self.getWindow(windowLabel, frameOnly = False)
		myFrame.setMaximumFrameSize(*args, **kwargs)

	def setAutoWindowSize(self, windowLabel, *args, **kwargs):
		"""Overload for setAutoWindowSize in handle_Window()."""

		myFrame = self.getWindow(windowLabel, frameOnly = False)
		myFrame.setAutoWindowSize(*args, **kwargs)

	def setWindowTitle(self, windowLabel, title, *args, **kwargs):
		"""Overload for setWindowTitle in handle_Window()."""

		myFrame = self.getWindow(windowLabel, frameOnly = False)
		myFrame.setWindowTitle(*args, **kwargs)

	def centerWindow(self, windowLabel, *args, **kwargs):
		"""Overload for centerWindow in handle_Window()."""

		myFrame = self.getWindow(windowLabel, frameOnly = False)
		myFrame.centerWindow(*args, **kwargs)

	def showWindow(self, windowLabel, *args, **kwargs):
		"""Overload for showWindow in handle_Window()."""

		myFrame = self.getWindow(windowLabel, frameOnly = False)
		myFrame.showWindow(*args, **kwargs)

	def onShowWindow(self, event, windowLabel, *args, **kwargs):
		"""Overload for onShowWindow in handle_Window()."""

		myFrame = self.getWindow(windowLabel, frameOnly = False)
		myFrame.onShowWindow(event, *args, **kwargs)

	def showWindowCheck(self, windowLabel, *args, **kwargs):
		"""Overload for showWindowCheck in handle_Window()."""

		myFrame = self.getWindow(windowLabel, frameOnly = False)
		shown = myFrame.showWindowCheck(*args, **kwargs)
		return shown

	def hideWindow(self, windowLabel, *args, **kwargs):
		"""Overload for hideWindow in handle_Window()."""

		myFrame = self.getWindow(windowLabel, frameOnly = False)
		myFrame.hideWindow(*args, **kwargs)

	def onHideWindow(self, event, windowLabel, *args, **kwargs):
		"""Overload for onHideWindow in handle_Window()."""

		myFrame = self.getWindow(windowLabel, frameOnly = False)
		myFrame.onHideWindow(event, *args, **kwargs)

	def typicalWindowSetup(self, windowLabel, *args, **kwargs):
		"""Overload for typicalWindowSetup in handle_Window()."""

		myFrame = self.getWindow(windowLabel)
		myFrame.typicalWindowSetup(*args, **kwargs)
		
	def closeWindow(self, windowLabel, *args, **kwargs):
		"""Overload for closeWindow in handle_Window()."""

		myFrame = self.getWindow(windowLabel, frameOnly = False)
		myFrame.closeWindow(*args, **kwargs)

	def onCloseWindow(self, event, windowLabel, *args, **kwargs):
		"""Overload for onCloseWindow in handle_Window()."""

		myFrame = self.getWindow(windowLabel, frameOnly = False)
		myFrame.onCloseWindow(event, *args, **kwargs)

	def addSizerBox(self, windowLabel, *args, **kwargs):
		"""Overload for addSizerBox in handle_Window()."""

		myFrame = self.getWindow(windowLabel, frameOnly = False)
		handle = myFrame.addSizerBox(*args, **kwargs)

		return handle

	def addSizerText(self, windowLabel, *args, **kwargs):
		"""Overload for addSizerText in handle_Window()."""

		myFrame = self.getWindow(windowLabel, frameOnly = False)
		handle = myFrame.addSizerText(*args, **kwargs)

		return handle

	def addSizerGrid(self, windowLabel, *args, **kwargs):
		"""Overload for addSizerGrid in handle_Window()."""

		myFrame = self.getWindow(windowLabel, frameOnly = False)
		handle = myFrame.addSizerGrid(*args, **kwargs)

		return handle

	def addSizerGridFlex(self, windowLabel, *args, **kwargs):
		"""Overload for addSizerGridFlex in handle_Window()."""

		myFrame = self.getWindow(windowLabel, frameOnly = False)
		handle = myFrame.addSizerGridFlex(*args, **kwargs)

		return handle

	def addSizerGridBag(self, windowLabel, *args, **kwargs):
		"""Overload for addSizerGridBag in handle_Window()."""

		myFrame = self.getWindow(windowLabel, frameOnly = False)
		handle = myFrame.addSizerGridBag(*args, **kwargs)

		return handle

	def addSizerWrap(self, windowLabel, *args, **kwargs):
		"""Overload for addSizerWrap in handle_Window()."""

		myFrame = self.getWindow(windowLabel, frameOnly = False)
		handle = myFrame.addSizerWrap(*args, **kwargs)

		return handle

	def growFlexColumn(self, windowLabel, *args, **kwargs):
		"""Overload for growFlexColumn in handle_Window()."""

		myFrame = self.getWindow(windowLabel, frameOnly = False)
		myFrame.growFlexColumn(*args, **kwargs)

	def growFlexRow(self, windowLabel, *args, **kwargs):
		"""Overload for growFlexRow in handle_Window()."""

		myFrame = self.getWindow(windowLabel, frameOnly = False)
		myFrame.growFlexRow(*args, **kwargs)

	def growFlexColumnAll(self, windowLabel, *args, **kwargs):
		"""Overload for growFlexColumnAll in handle_Window()."""

		myFrame = self.getWindow(windowLabel, frameOnly = False)
		myFrame.growFlexColumnAll(*args, **kwargs)

	def growFlexRowAll(self, windowLabel, *args, **kwargs):
		"""Overload for growFlexRowAll in handle_Window()."""

		myFrame = self.getWindow(windowLabel, frameOnly = False)
		myFrame.growFlexRowAll(*args, **kwargs)

	def addText(self, windowLabel, *args, **kwargs):
		"""Overload for addText in handle_Window()."""

		myFrame = self.getWindow(windowLabel, frameOnly = False)
		handle = myFrame.addText(*args, **kwargs)

		return handle

	def addHtml(self, windowLabel, *args, **kwargs):
		"""Overload for addHtml in handle_Window()."""

		myFrame = self.getWindow(windowLabel, frameOnly = False)
		handle = myFrame.addHtml(*args, **kwargs)

		return handle

	def addHyperlink(self, windowLabel, *args, **kwargs):
		"""Overload for addHyperlink in handle_Window()."""

		myFrame = self.getWindow(windowLabel, frameOnly = False)
		handle = myFrame.addHyperlink(*args, **kwargs)

		return handle

	def addEmpty(self, windowLabel, *args, **kwargs):
		"""Overload for addEmpty in handle_Window()."""

		myFrame = self.getWindow(windowLabel, frameOnly = False)
		handle = myFrame.addEmpty(*args, **kwargs)

		return handle

	def addLine(self, windowLabel, *args, **kwargs):
		"""Overload for addLine in handle_Window()."""

		myFrame = self.getWindow(windowLabel, frameOnly = False)
		handle = myFrame.addLine(*args, **kwargs)

		return handle

	def addListDrop(self, windowLabel, *args, **kwargs):
		"""Overload for addListDrop in handle_Window()."""

		myFrame = self.getWindow(windowLabel, frameOnly = False)
		handle = myFrame.addListDrop(*args, **kwargs)

		return handle

	def addListFull(self, windowLabel, *args, **kwargs):
		"""Overload for addListFull in handle_Window()."""

		myFrame = self.getWindow(windowLabel, frameOnly = False)
		handle = myFrame.addListFull(*args, **kwargs)

		return handle

	def addInputSlider(self, windowLabel, *args, **kwargs):
		"""Overload for addInputSlider in handle_Window()."""

		myFrame = self.getWindow(windowLabel, frameOnly = False)
		handle = myFrame.addInputSlider(*args, **kwargs)

		return handle

	def addInputBox(self, windowLabel, *args, **kwargs):
		"""Overload for addInputBox in handle_Window()."""

		myFrame = self.getWindow(windowLabel, frameOnly = False)
		handle = myFrame.addInputBox(*args, **kwargs)

		return handle

	def addInputSearch(self, windowLabel, *args, **kwargs):
		"""Overload for addInputSearch in handle_Window()."""

		myFrame = self.getWindow(windowLabel, frameOnly = False)
		handle = myFrame.addInputSearch(*args, **kwargs)

		return handle

	def addInputSpinner(self, windowLabel, *args, **kwargs):
		"""Overload for addInputSpinner in handle_Window()."""

		myFrame = self.getWindow(windowLabel, frameOnly = False)
		handle = myFrame.addInputSpinner(*args, **kwargs)

		return handle

	def addButton(self, windowLabel, *args, **kwargs):
		"""Overload for addButton in handle_Window()."""

		myFrame = self.getWindow(windowLabel, frameOnly = False)
		handle = myFrame.addButton(*args, **kwargs)

		return handle

	def addButtonList(self, windowLabel, *args, **kwargs):
		"""Overload for addButtonList in handle_Window()."""

		myFrame = self.getWindow(windowLabel, frameOnly = False)
		handle = myFrame.addButtonList(*args, **kwargs)

		return handle

	def addButtonToggle(self, windowLabel, *args, **kwargs):
		"""Overload for addButtonToggle in handle_Window()."""

		myFrame = self.getWindow(windowLabel, frameOnly = False)
		handle = myFrame.addButtonToggle(*args, **kwargs)

		return handle

	def addButtonCheck(self, windowLabel, *args, **kwargs):
		"""Overload for addButtonCheck in handle_Window()."""

		myFrame = self.getWindow(windowLabel, frameOnly = False)
		handle = myFrame.addButtonCheck(*args, **kwargs)

		return handle

	def addButtonCheckList(self, windowLabel, *args, **kwargs):
		"""Overload for addButtonCheckList in handle_Window()."""

		myFrame = self.getWindow(windowLabel, frameOnly = False)
		handle = myFrame.addButtonCheckList(*args, **kwargs)

		return handle

	def addButtonRadio(self, windowLabel, *args, **kwargs):
		"""Overload for addButtonRadio in handle_Window()."""

		myFrame = self.getWindow(windowLabel, frameOnly = False)
		handle = myFrame.addButtonRadio(*args, **kwargs)

		return handle

	def addButtonRadioBox(self, windowLabel, *args, **kwargs):
		"""Overload for addButtonRadioBox in handle_Window()."""

		myFrame = self.getWindow(windowLabel, frameOnly = False)
		handle = myFrame.addButtonRadioBox(*args, **kwargs)

		return handle

	def addButtonImage(self, windowLabel, *args, **kwargs):
		"""Overload for addButtonImage in handle_Window()."""

		myFrame = self.getWindow(windowLabel, frameOnly = False)
		handle = myFrame.addButtonImage(*args, **kwargs)

		return handle

	def addImage(self, windowLabel, *args, **kwargs):
		"""Overload for addImage in handle_Window()."""

		myFrame = self.getWindow(windowLabel, frameOnly = False)
		handle = myFrame.addImage(*args, **kwargs)

		return handle

	def addProgressBar(self, windowLabel, *args, **kwargs):
		"""Overload for addProgressBar in handle_Window()."""

		myFrame = self.getWindow(windowLabel, frameOnly = False)
		handle = myFrame.addProgressBar(*args, **kwargs)

		return handle

	def addPickerColor(self, windowLabel, *args, **kwargs):
		"""Overload for addPickerColor in handle_Window()."""

		myFrame = self.getWindow(windowLabel, frameOnly = False)
		handle = myFrame.addPickerColor(*args, **kwargs)

		return handle

	def addPickerFont(self, windowLabel, *args, **kwargs):
		"""Overload for addPickerFont in handle_Window()."""

		myFrame = self.getWindow(windowLabel, frameOnly = False)
		handle = myFrame.addPickerFont(*args, **kwargs)

		return handle

	def addPickerFile(self, windowLabel, *args, **kwargs):
		"""Overload for addPickerFile in handle_Window()."""

		myFrame = self.getWindow(windowLabel, frameOnly = False)
		handle = myFrame.addPickerFile(*args, **kwargs)

		return handle

	def addPickerFileWindow(self, windowLabel, *args, **kwargs):
		"""Overload for addPickerFileWindow in handle_Window()."""

		myFrame = self.getWindow(windowLabel, frameOnly = False)
		handle = myFrame.addPickerFileWindow(*args, **kwargs)

		return handle

	def addPickerTime(self, windowLabel, *args, **kwargs):
		"""Overload for addPickerTime in handle_Window()."""

		myFrame = self.getWindow(windowLabel, frameOnly = False)
		handle = myFrame.addPickerTime(*args, **kwargs)

		return handle

	def addPickerDate(self, windowLabel, *args, **kwargs):
		"""Overload for addPickerDate in handle_Window()."""

		myFrame = self.getWindow(windowLabel, frameOnly = False)
		handle = myFrame.addPickerDate(*args, **kwargs)

		return handle

	def addPickerDateWindow(self, windowLabel, *args, **kwargs):
		"""Overload for addPickerDateWindow in handle_Window()."""

		myFrame = self.getWindow(windowLabel, frameOnly = False)
		handle = myFrame.addPickerDateWindow(*args, **kwargs)

		return handle

#Monkey Patches
# import pubsub.core.callables
# class _mp_CallArgsInfo:
# 	"""Overridden to allow any valid combination of args and kwargs."""

# 	class NO_DEFAULT:
# 		def __repr__(self):
# 			return "NO_DEFAULT"

# 	def __init__(self, func, firstArgIdx, ignoreArgs = None):
# 		args, varParamName, varOptParamName, argsDefaults, kwargs, kwargsDefaults, annotations = inspect.getfullargspec(func)
# 		self.allArgs = {}

# 		if (argsDefaults is not None):
# 			argsDefaults_startsAt = len(args) - len(argsDefaults) - 1
# 		for i, variable in enumerate(args):
# 			if ((i == 0) and (firstArgIdx > 0)):
# 				continue #skip self

# 			if ((argsDefaults is None) or (i < argsDefaults_startsAt)):
# 				self.allArgs[variable] = self.NO_DEFAULT()
# 			else:
# 				self.allArgs[variable] = argsDefaults[i - argsDefaults_startsAt - 1]

# 		self.allKwargs = {}
# 		for variable in kwargs:
# 			if ((kwargsDefaults is None) or (variable not in kwargsDefaults)):
# 				self.allKwargs[variable] = self.NO_DEFAULT()
# 			else:
# 				self.allKwargs[variable] = kwargsDefaults[variable]

# 		self.acceptsAllKwargs = (varOptParamName is not None)
# 		self.acceptsAllUnnamedArgs = (varParamName is not None)
# 		self.allParams = [*self.allArgs.keys(), *self.allKwargs.keys()]

# 		if ignoreArgs:
# 			for var_name in ignoreArgs:
# 				if (var_name in self.allArgs):
# 					del self.allArgs[var_name]
# 				elif (var_name in self.allKwargs):
# 					del self.allKwargs[var_name]

# 			if (varOptParamName in ignoreArgs):
# 				self.acceptsAllKwargs = False
# 			if (varParamName in ignoreArgs):
# 				self.acceptsAllUnnamedArgs = False

# 		self.numRequired = sum([1 for value in [*self.allArgs.values(), *self.allKwargs.values()] if (isinstance(value, self.NO_DEFAULT))])
# 		assert self.numRequired >= 0

# 		# if listener wants topic, remove that arg from args/defaultVals
# 		self.autoTopicArgName = None
# 		self.__setupAutoTopic()

# 	def getAllArgs(self):
# 		return tuple(self.allParams)

# 	def getOptionalArgs(self):
# 		return tuple([key for key, value in [*self.allArgs.items(), *self.allKwargs.items()] if (not isinstance(value, self.NO_DEFAULT))])

# 	def getRequiredArgs(self):
# 		return tuple([key for key, value in [*self.allArgs.items(), *self.allKwargs.items()] if (isinstance(value, self.NO_DEFAULT))])

# 	def __setupAutoTopic(self):
# 		for variable, value in {**self.allArgs, **self.allKwargs}.items():
# 			if (value == pubsub.core.callables.AUTO_TOPIC):
# 				del self.allArgs[variable]
# 				return

# pubsub.core.callables.CallArgsInfo = _mp_CallArgsInfo

#User Things
class User_Utilities(MyUtilities.common.Container, MyUtilities.common.CommonFunctions, MyUtilities.common.EnsureFunctions, MyUtilities.wxPython.Converters, MyUtilities.wxPython.CommonFunctions):
	def __init__(self, *args, **kwargs):
		MyUtilities.common.Container.__init__(self, *args, **kwargs)

	def makeCanvas(self, *args, **kwargs):
		"""Grants user access to Utilities._makeCanvas().

		Example Input: makeCanvas()
		"""

		return Utilities._makeCanvas(None, *args, panel = None, **kwargs)

	def makeDialogMessage(self, *args, **kwargs):
		"""Grants user access to Utilities.makeDialogMessage().

		Example Input: makeDialogMessage()
		"""

		return Utilities.makeDialogMessage(None, *args, **kwargs)

	def makeDialogError(self, *args, **kwargs):
		"""Grants user access to Utilities.makeDialogError().

		Example Input: makeDialogError()
		"""

		return Utilities.makeDialogError(None, *args, **kwargs)
		
	def makeDialogScroll(self, *args, **kwargs):
		"""Grants user access to Utilities.makeDialogScroll().

		Example Input: makeDialogScroll()
		"""

		return Utilities.makeDialogScroll(None, *args, **kwargs)

	def makeDialogBusy(self, *args, **kwargs):
		"""Grants user access to Utilities.makeDialogBusy().

		Example Input: makeDialogBusy()
		"""

		return Utilities.makeDialogBusy(None, *args, **kwargs)
		
	def makeDialogChoice(self, *args, **kwargs):
		"""Grants user access to Utilities.makeDialogChoice().

		Example Input: makeDialogChoice()
		"""

		return Utilities.makeDialogChoice(None, *args, **kwargs)
		
	def makeDialogInput(self, *args, **kwargs):
		"""Grants user access to Utilities.makeDialogInput().

		Example Input: makeDialogInput()
		"""

		return Utilities.makeDialogInput(None, *args, **kwargs)

	def makeDialogFile(self, *args, **kwargs):
		"""Grants user access to Utilities.makeDialogFile().

		Example Input: makeDialogFile()
		"""

		return Utilities.makeDialogFile(None, *args, **kwargs)

	def makeDialogColor(self, *args, **kwargs):
		"""Grants user access to Utilities.makeDialogColor().

		Example Input: makeDialogColor()
		"""

		return Utilities.makeDialogColor(None, *args, **kwargs)

	def makeDialogPrintSetup(self, *args, **kwargs):
		"""Grants user access to Utilities.makeDialogPrintSetup().

		Example Input: makeDialogPrintSetup()
		"""

		return Utilities.makeDialogPrintSetup(None, *args, **kwargs)
		
	def makeDialogPrint(self, *args, **kwargs):
		"""Grants user access to Utilities.makeDialogPrint().

		Example Input: makeDialogPrint()
		"""

		return Utilities.makeDialogPrint(None, *args, **kwargs)

	def makeDialogPrintPreview(self, *args, **kwargs):
		"""Grants user access to Utilities.makeDialogPrintPreview().

		Example Input: makeDialogPrintPreview()
		"""

		return Utilities.makeDialogPrintPreview(None, *args, **kwargs)
		
	def makeDialogCustom(self, *args, **kwargs):
		"""Grants user access to Utilities.makeDialogCustom().

		Example Input: makeDialogCustom()
		"""

		return Utilities.makeDialogCustom(None, *args, **kwargs)

if (__name__ == "__main__"):

	def buildWindow():
		"""Creates a simple window."""

		#Initialize Frame
		with gui.addWindow(label = 0, title = "Controlled Layout") as myFrame:
			# myFrame.setMinimumFrameSize((250, 200))

			#Add Content
			with myFrame.addSizerGridFlex(rows = 2, columns = 1) as mySizer:
				mySizer.growFlexRowAll()
				mySizer.growFlexColumnAll()	
					
				with mySizer.addSizerGridFlex(rows = 3, columns = 2) as mySubSizer:
					mySubSizer.growFlexRow(2)
					mySubSizer.growFlexColumnAll()	
					mySubSizer.addText("Lorem")
					mySubSizer.addText("Ipsum")
					mySubSizer.addText(text = "Dolor")
				
				with mySizer.addSizerGridFlex(rows = 3, columns = 2) as mySubSizer:
					mySubSizer.growFlexRow(2)
					mySubSizer.growFlexColumnAll()	
					mySubSizer.addInputBox(text = "Sit")
					mySubSizer.addText(text = "Amet")
					mySubSizer.addInputBox(text = "Consectetur")

			with myFrame.addSizerGridFlex(rows = 3, columns = 2) as mySizer:
				mySizer.growFlexRowAll()
				mySizer.growFlexColumnAll()	
				mySizer.addButton("Adipiscing", myFunction = lambda event: print("Adipiscing"))
				mySizer.addButton("Elit", tabSkip = True, myFunction = lambda event: print("Elit"))
				mySizer.addButton("Sed", tabSkip = True, myFunction = lambda event: print("Sed"))
				mySizer.addButton("Do", myFunction = lambda event: print("Do"))

	gui = build()
	buildWindow()
	gui.centerWindowAll()

	myFrame = gui.getWindow(0)
	myFrame.showWindow()

	gui.finish()

