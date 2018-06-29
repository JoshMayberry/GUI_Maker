__version__ = "4.3.0"

#TO DO
# - Add File Drop: https://www.blog.pythonlibrary.org/2012/06/20/wxpython-introduction-to-drag-and-drop/
# - Add Wrap Sizer: https://www.blog.pythonlibrary.org/2014/01/22/wxpython-wrap-widgets-with-wrapsizer/
# - Look through these demos for more things: https://github.com/wxWidgets/Phoenix/tree/master/demo
# - Look through the menu examples: https://www.programcreek.com/python/example/44403/wx.EVT_FIND
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
import time
import math
import copy
import types
import bisect
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
import wx.lib.scrolledpanel
import wx.lib.mixins.listctrl
import wx.lib.agw.multidirdialog
import wx.lib.agw.fourwaysplitter
import wx.lib.agw.ultimatelistctrl
import ObjectListView

#Import matplotlib elements to add plots to the GUI
# import matplotlib
# matplotlib.use('WXAgg')
# matplotlib.get_py2exe_datafiles()
# import matplotlib.pyplot as plt
# from matplotlib.backends.backend_wxagg import FigureCanvas


#Import multi-threading to run functions as background processes
import queue
import threading
import subprocess
import pubsub.pub


#Import needed support modules
import re
import PIL


#Required Modules
##py -m pip install
	# wxPython
	# cx_Freeze
	# pillow
	# pypubsub
	# objectlistview

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
topicManager = pubsub.pub.getDefaultTopicMgr()

#Get all event names
#See: https://www.blog.pythonlibrary.org/2011/07/05/wxpython-get-the-event-name-instead-of-an-integer/
eventCatalogue = {}
for module_name, module in sys.modules.items():
	if (module_name.startswith("wx")):
		if (module_name == "wx.core"):
			module_name = "wx"
		for name in dir(module):
			if (name.startswith('EVT_')):
				event = getattr(module, name)
				if (isinstance(event, wx.PyEventBinder)):
					eventCatalogue[event.typeId] = (name, f"{module_name}.{name}", eval(f"{module_name}.{name}"))

#Debugging Functions
def printCurrentTrace():
	"""Prints out the stack trace for the current place in the program.
	Modified Code from codeasone on https://stackoverflow.com/questions/1032813/dump-stacktraces-of-all-active-threads

	Example Input: printCurrentTrace()
	"""

	code = []
	for threadId, stack in sys._current_frames().items():
		code.append("\n# ThreadID: %s" % threadId)
		for filename, lineno, name, line in traceback.extract_stack(stack):
			code.append('File: "%s", line %d, in %s' % (filename,
														lineno, name))
			if line:
				code.append("  %s" % (line.strip()))

	for line in code:
		print (line)

#Controllers
def build(*args, **kwargs):
	"""Starts the GUI making process."""

	return Controller(*args, **kwargs)

#Iterators
class _Iterator(object):
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

			return self.data.pop(0)
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
				myFunctionList, myFunctionArgsList, myFunctionKwargsList = Utilities._formatFunctionInputList(None, myFunctionList, myFunctionArgsList, myFunctionKwargsList)
				
				#Run each function
				for i, myFunction in enumerate(myFunctionList):
					#Skip empty functions
					if (myFunction != None):
						myFunctionEvaluated, myFunctionArgs, myFunctionKwargs = Utilities._formatFunctionInput(None, i, myFunctionList, myFunctionArgsList, myFunctionKwargsList)

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
						myFunction(*myFunctionArgsCombined, **myFunctionKwargsCombined)

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
					Utilities._logPrint(None, text = error, fileName = fileName)
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
class _ThreadQueue():
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
				myFunctionList, myFunctionArgsList, myFunctionKwargsList = Utilities._formatFunctionInputList(self, myFunctionList, myFunctionArgsList, myFunctionKwargsList)
				
				#Run each function
				answerList = []
				for i, myFunction in enumerate(myFunctionList):
					#Skip empty functions
					if (myFunction != None):
						myFunctionEvaluated, myFunctionArgs, myFunctionKwargs = Utilities._formatFunctionInput(self, i, myFunctionList, myFunctionArgsList, myFunctionKwargsList)
						answer = myFunction(*myFunctionArgs, **myFunctionKwargs)
						answerList.append(answer)

				#Account for just one function
				if (len(answerList) == 1):
					answerList = answerList[0]
			return answerList
		
		#########################################################

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

class _MyThread(threading.Thread):
	"""Used to run functions in the background.
	More information on threads can be found at: https://docs.python.org/3.4/library/threading.html
	Use: https://wiki.wxpython.org/Non-Blocking%20Gui
	Use: http://effbot.org/zone/thread-synchronization.htm
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

	def __init__(self, parent, threadID = None, name = None, counter = None, daemon = None):
		"""Setup the thread.

		threadID (int) -
		name (str)     - The thread name. By default, a unique name is constructed of the form "Thread-N" where N is a small decimal number.
		counter (int)  - 
		daemon (bool)  - Sets whether the thread is daemonic. If None (the default), the daemonic property is inherited from the current thread.
		
		Example Input: _MyThread()
		Example Input: _MyThread(1, "Thread-1", 1)
		Example Input: _MyThread(daemon = True)
		"""

		#Initialize the thread
		threading.Thread.__init__(self, name = name, daemon = daemon)
		# self.setDaemon(daemon)

		#Setup thread properties
		if (threadID != None):
			self.threadID = threadID

		self.stopEvent = threading.Event() #Used to stop the thread

		#Initialize internal variables
		self.parent = parent
		self.shown = None
		self.window = None
		self.myFunction = None
		self.myFunctionArgs = None
		self.myFunctionKwargs = None
		self.errorFunction = None
		self.errorFunctionArgs = None
		self.errorFunctionKwargs = None

	def runFunction(self, myFunction, myFunctionArgs, myFunctionKwargs, window, shown = False, errorFunction = None, errorFunctionArgs = None, errorFunctionKwargs = None):
		"""Sets the function to run in the thread object.

		myFunction (function)   - What function will be ran
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
		self.errorFunction = errorFunction
		self.errorFunctionArgs = errorFunctionArgs
		self.errorFunctionKwargs = errorFunctionKwargs

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

		self.parent.runMyFunction(myFunction = self.myFunction, myFunctionArgs = self.myFunctionArgs, myFunctionKwargs = self.myFunctionKwargs, 
			errorFunction = self.errorFunction, errorFunctionArgs = self.errorFunctionArgs, errorFunctionKwargs = self.errorFunctionKwargs)

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

		self.listeningCatalogue = {}
		self.oneShotCatalogue = {}
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

	def get(self, itemLabel = None, includeUnnamed = True, checkNested = True, typeList = None, subTypeList = None, returnExists = False):
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
		Example Input: get(event, returnExists = True)
		Example Input: get(slice(None, None, None), checkNested = False)
		"""

		def nestCheck(itemList, itemLabel):
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
				else:
					if (key == item.label):
						return item
				
				answer = nestCheck(item[:], key)
				if (answer != None):
					return answer
			return answer

		def checkType(handleList):
			"""Makes sure only the instance types the user wants are in the return list."""
			nonlocal typeList, subTypeList

			if ((handleList != None) and (typeList != None)):
				answer = []
				if (not isinstance(handleList, (list, tuple, range))):
					handleList = [handleList]
				if (not isinstance(typeList, (list, tuple))):
					typeList = [typeList]
				if ((subTypeList != None) and (not isinstance(subTypeList, (list, tuple)))):
					subTypeList = [subTypeList]

				for item in handleList:
					for itemType in typeList:
						if (isinstance(item, itemType)):
							if ((subTypeList != None) and (item.type.lower() not in subTypeList)):
								continue
							answer.append(item)
							break

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

			if (isinstance(itemLabel.start, handle_Base)):
				itemLabel.start = itemLabel.start.label
			if (isinstance(itemLabel.stop, handle_Base)):
				itemLabel.stop = itemLabel.stop.label

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
			if (returnExists):
				return answer != None
			return answer

		elif (itemLabel in self.unnamedList):
			answer = checkType(itemLabel)

		else:
			if (isinstance(itemLabel, handle_Base)):
				key = itemLabel.label
			else:
				key = itemLabel

			if (key == None):
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
			return answer != None
		
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

	def runMyFunction(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, event = None, includeEvent = False,
		errorFunction = None, errorFunctionArgs = None, errorFunctionKwargs = None, includeError = True):
		"""Runs a function."""

		answer = None

		try:
			#Skip empty functions
			if (myFunction != None):
				if (not isinstance(myFunction, (list, tuple))):
					if (isinstance(myFunction, str)):
						myFunction = eval(myFunction, {'__builtins__': None}, {})
					
					if (myFunctionArgs == None):
						myFunctionArgs = []
					elif (not isinstance(myFunctionArgs, (list, tuple))):
						myFunctionArgs = [myFunctionArgs]

					if (myFunctionKwargs == None):
						myFunctionKwargs = {}

					answer = myFunction(*myFunctionArgs, **myFunctionKwargs)

				elif (len(myFunction) != 0):
					myFunctionList, myFunctionArgsList, myFunctionKwargsList = self._formatFunctionInputList(myFunction, myFunctionArgs, myFunctionKwargs)
					#Run each function
					answer = []
					for i, myFunction in enumerate(myFunctionList):
						#Skip empty functions
						if (myFunction != None):
							myFunctionEvaluated, myFunctionArgs, myFunctionKwargs = self._formatFunctionInput(i, myFunctionList, myFunctionArgsList, myFunctionKwargsList)
							
							if (includeEvent):
								if (myFunctionArgs == None):
									myFunctionArgs = [event]
								else:
									myFunctionArgs = [event] + myFunctionArgs

							answer.append(myFunctionEvaluated(*myFunctionArgs, **myFunctionKwargs))

		except Exception as error:
			if (errorFunction == None):
				raise error
			else:
				if (includeError):
					if (errorFunctionArgs == None):
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
		if (myFunctionList != None):
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
		if (myFunctionArgsList != None):
			#Compensate for the user not making it a list
			if (not isinstance(myFunctionArgsList, list)):
				if (isinstance(myFunctionArgsList, (tuple, types.GeneratorType))):
					myFunctionArgsList = list(myFunctionArgsList)
				else:
					myFunctionArgsList = [myFunctionArgsList]

			#Fix list order so it is more intuitive
			if (len(myFunctionList) > 1):
				myFunctionArgsList.reverse()

			if ((len(myFunctionList) == 1) and (myFunctionArgsList[0] != None)):
				myFunctionArgsList = [myFunctionArgsList]

		##kwargs
		if (myFunctionKwargsList != None):
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
				myFunctionEvaluated = eval(myFunction, {'__builtins__': None}, {})

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

		if (myFunctionArgs == None):
			myFunctionArgs = []
		if (myFunctionKwargs == None):
			myFunctionKwargs = {}

		return myFunctionEvaluated, myFunctionArgs, myFunctionKwargs

	def _betterBind(self, eventType, thing, myFunctionList, myFunctionArgsList = None, myFunctionKwargsList = None, mode = 1, rebind = False, printError = True):
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
			- If True: Will rebind
			- If False: Will not rebind
			- If None: Will remove all previously bound functions
		_________________________________________________________________________

		MULTIPLE FUNCTION ORDER
		The functions are ran in the order given; from left to right.

		MULTIPLE FUNCTION FAILURE
		Make it a habbit to end all bound functions with 'event.Skip()'. 
		If the bound function does not end with 'event.Skip()', then it will overwrite a previously bound function.
		This will result in the new function being ran in place of both functions.
		_________________________________________________________________________

		Example Input: _betterBind(wx.EVT_BUTTON, menuItem, "self.onExit", "Extra Information")
		Example Input: _betterBind(wx.EVT_BUTTON, menuItem, ["self.toggleObjectWithLabel", "self.onQueueValue", ], [["myCheckBox", True], None])
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
			if (rebind == None):
				bindObject.Unbind(eventType, source = thing)
			elif (rebind):
				unbound = bindObject.Unbind(eventType, handler = myFunctionEvaluated, source = thing)
				if ((not unbound) and printError):
					#If the lambda style function was used, this will not work
					warnings.warn(f"Unbinding function {myFunctionEvaluated} for {self.__repr__()} failed", Warning, stacklevel = 3)

			if ((not rebind) and (eventType in self.boundEvents)):
				self.boundEvents.remove(eventType)

			#Typical binding mode
			if (mode == 1):
				if ((len(myFunctionKwargs) == 0) and (len(myFunctionArgs) == 0)):
					bindObject.Bind(eventType, myFunctionEvaluated, thing)
				else:
					bindObject.Bind(eventType, lambda event: myFunctionEvaluated(event, *myFunctionArgs, **myFunctionKwargs), thing)

			#Binding mode for window key bindings
			elif (mode == 2):
				if ((len(myFunctionKwargs) == 0) and (len(myFunctionArgs) == 0)):
					bindObject.Bind(eventType, myFunctionEvaluated)
				else:
					bindObject.Bind(eventType, lambda event: myFunctionEvaluated(event, *myFunctionArgs, **myFunctionKwargs))

			else:
				errorMessage = f"Unknown mode {mode} for _betterBind()"
				raise TypeError(errorMessage)

			if (eventType not in self.boundEvents):
				self.boundEvents.append(eventType)

		##############################################################################################################################

		#Skip empty functions
		if (myFunctionList != None):
			myFunctionList, myFunctionArgsList, myFunctionKwargsList = self._formatFunctionInputList(myFunctionList, myFunctionArgsList, myFunctionKwargsList)
			#Run each function
			for i, myFunction in enumerate(myFunctionList):
				#Skip empty functions
				if (myFunction != None):
					myFunctionEvaluated, myFunctionArgs, myFunctionKwargs = self._formatFunctionInput(i, myFunctionList, myFunctionArgsList, myFunctionKwargsList)
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
			if (myFunctionList != None):
				#Ensure that multiple function capability is given
				if ((not isinstance(myFunctionList, list)) and (myFunctionList != None)):
					if (isinstance(myFunctionList, (tuple, types.GeneratorType))):
						myFunctionList = list(myFunctionList)
					else:
						myFunctionList = [myFunctionList]

				#args
				if ((not isinstance(myFunctionArgsList, list)) and (myFunctionArgsList != None)):
					if (isinstance(myFunctionArgsList, (tuple, types.GeneratorType))):
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
				if ((not isinstance(myFunctionKwargsList, list)) and (myFunctionKwargsList != None)):
					if (isinstance(myFunctionKwargsList, (tuple, types.GeneratorType))):
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

	def getMousePosition(self):
		"""Returns the current mouse position relative to the current handle.

		Example Input: getMousePosition()
		"""

		position = self.thing.ScreenToClient(wx.GetMousePosition())

		if (not isinstance(position, (list, tuple))):
			position = position.Get()

		return position

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

	def backgroundRun(self, myFunction, myFunctionArgs = None, myFunctionKwargs = None, shown = False, makeThread = True,
		errorFunction = None, errorFunctionArgs = None, errorFunctionKwargs = None):
		"""Runs a function in the background in a way that it does not lock up the GUI.
		Meant for functions that take a long time to run.
		If makeThread is true, the new thread object will be returned to the user.

		myFunction (str)       - The function that will be ran when the event occurs
		myFunctionArgs (any)   - Any input arguments for myFunction. A list of multiple functions can be given
		myFunctionKwargs (any) - Any input keyword arguments for myFunction. A list of variables for each function can be given. The index of the variables must be the same as the index for the functions
		shown (bool)           - Determines when to run the function
			- If True: The function will only run if the window is being shown. If the window is not shown, it will terminate the function. It will wait for the window to first be shown to run
			- If False: The function will run regardless of whether the window is being shown or not
		makeThread (bool)      - Determines if this function runs on a different thread
			- If True: A new thread will be created to run the function
			- If False: The function will only run while the GUI is idle. Note: This can cause lag. Use this for operations that must be in the main thread.

		errorFunction (str)       - The function that will be ran when an error occurs
			- The 'error' must be either the first arg or a kwarg
			- If None: The error is raised
		errorFunctionArgs (any)   - Any input arguments for errorFunction. A list of multiple functions can be given
		errorFunctionKwargs (any) - Any input keyword arguments for errorFunction. A list of variables for each function can be given. The index of the variables must be the same as the index for the functions
		
		Example Input: backgroundRun(self.startupFunction)
		Example Input: backgroundRun(self.startupFunction, shown = True)
		"""

		#Skip empty functions
		if (myFunction != None):
			myFunctionList, myFunctionArgsList, myFunctionKwargsList = self._formatFunctionInputList(myFunction, myFunctionArgs, myFunctionKwargs)

			#Run each function
			for i, myFunction in enumerate(myFunctionList):
				#Skip empty functions
				if (myFunction != None):
					myFunctionEvaluated, myFunctionArgs, myFunctionKwargs = self._formatFunctionInput(i, myFunctionList, myFunctionArgsList, myFunctionKwargsList)

					#Determine how to run the function
					if (makeThread):
						#Create parallel thread
						thread = _MyThread(self, daemon = True)
						thread.runFunction(myFunctionEvaluated, myFunctionArgs, myFunctionKwargs, self, shown = shown, 
							errorFunction = errorFunction, errorFunctionArgs = errorFunctionArgs, errorFunctionKwargs = errorFunctionKwargs)
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

		#Skip empty functions
		if (myFunction != None):
			myFunctionList, myFunctionArgsList, myFunctionKwargsList = self._formatFunctionInputList(myFunction, myFunctionArgs, myFunctionKwargs)
			
			#Run each function
			for i, myFunction in enumerate(myFunctionList):
				#Skip empty functions
				if (myFunction != None):
					myFunctionEvaluated, myFunctionArgs, myFunctionKwargs = self._formatFunctionInput(i, myFunctionList, myFunctionArgsList, myFunctionKwargsList)
				
					if (after):
						wx.CallAfter(myFunctionEvaluated, *myFunctionArgs, **myFunctionKwargs)
					else:
						wx.CallLater(delay, myFunctionEvaluated, *myFunctionArgs, **myFunctionKwargs)
		else:
			warnings.warn(f"myFunctionList == None for autoRun() in {self.__repr__()}", Warning, stacklevel = 2)

	#Listen Functions
	def listen(self, myFunction, myFunctionArgs = None, myFunctionKwargs = None,
		resultFunction = None, resultFunctionArgs = None, resultFunctionKwargs = None, 
		errorFunction = None, errorFunctionArgs = None, errorFunctionKwargs = None, includeError = True,
		delay = 1000, shown = False, trigger = None, makeThread = True, 
		pauseOnDialog = False, notPauseOnDialog = []):
		"""Triggers the listen routine.

		myFunction (function)     - A function that checks certain conditions
		resultFunction (function) - A funftion that runs when 'myFunction' returns True

		delay (int) - How long to wait in milliseconds before running 'myFunction'
			- If 'trigger' is not None: How long to wait before listening for 'trigger'
		
		shown (bool) - Determines when to run the function
			- If True: The function will only run if the window is being shown. If the window is not shown, it will terminate the function. It will wait for the window to first be shown to run
			- If False: The function will run regardless of whether the window is being shown or not
		
		makeThread (bool) - Determines if this function runs on a different thread
			- If True: A new thread will be created to run the function
			- If False: The function will only run while the GUI is idle. Note: This can cause lag. Use this for operations that must be in the main thread.
		
		trigger (bool) - Determines if trigger_listen() will cause 'myFunction' to run
			- If True: Will wait for a signal from trigger_listen() before running 'myFunction'
			- If False: Will run 'myFunction' after 'delay' is over
			- If None: Will run 'myFunction' after 'delay' is over
		
		pauseOnDialog (bool) - Determines if the background function should wait if a dialog box is showing
			- If True: Will pause for any dialog window
			- If not bool: Will pause only if the dialog's label matches this
		not_pauseOnDialog (str) - The label of a dialog window to not pause on (Overrides 'pauseOnDialog'). Can be a list of labels

		Example Input: listen(self.checkCapsLock, shown = True)
		Example Input: listen(self.checkAutoLogout, resultFunction = self.logout, pauseOnDialog = True)
		Example Input: listen(self.listenScanner, pauseOnDialog = True, not_pauseOnDialog = "modifyBarcode")
		Example Input: listen(self.autoSave, trigger = True)
		"""

		def listenFunction():
			"""Listens for the myFunction to be true, then runs the resultFunction."""
			nonlocal self, myFunction, myFunctionArgs, myFunctionKwargs
			nonlocal resultFunction, resultFunctionArgs, resultFunctionKwargs, delay
			nonlocal errorFunction, errorFunctionArgs, errorFunctionKwargs, includeError

			#Account for other thread running this
			while (self.listeningCatalogue[myFunction]["listening"] > 0):
				self.listeningCatalogue[myFunction]["stop"] = True
				time.sleep(100 / 1000)
			self.listeningCatalogue[myFunction]["stop"] = False

			self.listeningCatalogue[myFunction]["listening"] += 1
			while True:
				while (self.listeningCatalogue[myFunction]["pause"]):
					if (self.listeningCatalogue[myFunction]["stop"]):
						break
					if ((delay != 0) and (delay != None)):
						time.sleep(delay / 1000)

				if (self.listeningCatalogue[myFunction]["stop"]):
					self.listeningCatalogue[myFunction]["stop"] = False
					break

				if ((delay != 0) and (delay != None)):
					time.sleep(delay / 1000)

				if (self.listeningCatalogue[myFunction]["trigger"] != None):
					while (not self.listeningCatalogue[myFunction]["trigger"]):
						if (self.listeningCatalogue[myFunction]["stop"]):
							break
						if ((delay != 0) and (delay != None)):
							time.sleep(delay / 1000)
					self.listeningCatalogue[myFunction]["trigger"] = False

				answer = self.runMyFunction(myFunction, myFunctionArgs, myFunctionKwargs, includeError = includeError,
					errorFunction = errorFunction, errorFunctionArgs = errorFunctionArgs, errorFunctionKwargs = errorFunctionKwargs)
				if (answer):
					self.runMyFunction(resultFunction, resultFunctionArgs, resultFunctionKwargs, includeError = includeError,
						errorFunction = errorFunction, errorFunctionArgs = errorFunctionArgs, errorFunctionKwargs = errorFunctionKwargs)

			self.listeningCatalogue[myFunction]["listening"] -= 1

		#########################################################

		if (myFunction not in self.listeningCatalogue):
			self.listeningCatalogue[myFunction] = {"listening": 0, "stop": False, "pause": False, "trigger": None}

		if (trigger):
			self.listeningCatalogue[myFunction]["trigger"] = False

		if (pauseOnDialog not in [None, False]):
			if ("listeningCatalogue" not in self.controller.backgroundFunction_pauseOnDialog):
				self.controller.backgroundFunction_pauseOnDialog["listeningCatalogue"] = {}
			if (self not in self.controller.backgroundFunction_pauseOnDialog["listeningCatalogue"]):
				self.controller.backgroundFunction_pauseOnDialog["listeningCatalogue"][self] = {}

			if (notPauseOnDialog == None):
				notPauseOnDialog = []
			elif (not isinstance(notPauseOnDialog, (list, tuple, range))):
				notPauseOnDialog = [notPauseOnDialog]

			self.controller.backgroundFunction_pauseOnDialog["listeningCatalogue"][self][myFunction] = {"state": pauseOnDialog, "exclude": notPauseOnDialog}

		self.backgroundRun(listenFunction, shown = shown, makeThread = makeThread)

	def stop_listen(self, myFunction):
		"""Stops the listen routine.

		myFunction (function) - A function that checks certain conditions

		Example Input: stop_listen(self.checkAutoLogout)
		"""

		if (myFunction in self.listeningCatalogue):
			self.listeningCatalogue[myFunction]["stop"] = True

	def pause_listen(self, myFunction, state = True):
		"""Pauses the listen routine.

		myFunction (function) - A function that checks certain conditions
		state (bool) - Determines if the function should be paused or not

		Example Input: pause_listen(self.checkAutoLogout)
		Example Input: pause_listen(self.checkAutoLogout, state = False)
		"""

		if (myFunction in self.listeningCatalogue):
			self.listeningCatalogue[myFunction]["pause"] = state

	def trigger_listen(self, myFunction, state = True):
		"""Turns on/off the trigger for the listen routine.

		myFunction (function) - A function that checks certain conditions
		state (bool) - Determines if the function should be paused or not

		Example Input: pause_listen(self.checkAutoLogout)
		Example Input: pause_listen(self.checkAutoLogout, state = False)
		"""

		if (myFunction in self.listeningCatalogue):
			self.listeningCatalogue[myFunction]["trigger"] = state

	def unpause_listen(self, myFunction, state = True):
		"""Unpauses the listen routine.

		myFunction (function) - A function that checks certain conditions
		state (bool) - Determines if the function should be paused or not

		Example Input: unpause_listen(self.checkAutoLogout)
		Example Input: unpause_listen(self.checkAutoLogout, state = False)
		"""

		self.pause_listen(myFunction, not state)

	#One-shot Functions
	def oneShot(self, myFunction, myFunctionArgs = None, myFunctionKwargs = None,
		alternativeFunction = None, alternativeFunctionArgs = None, alternativeFunctionKwargs = None, 
		delay = 0, delayAfter = True, allowAgain = True, shown = False, makeThread = True):
		"""Runs this function in the background only once.
		Returns if 'myFunction' ran or not.

		myFunction (function)     - A function that will run once
		alternativeFunction (function) - A funftion that runs instead of 'myFunction' if the one-shot is already made

		delay (int)       - How long to wait in milliseconds before allowing 'myFunction' to run again
		delayAfter (bool) - Determines when the delay is processed
			- If True: Delays after 'myFunction' runs
			- If False: Delays before 'myFunction' runs
		allowAgain (bool) - Determines if the 'myFunction' can run again after it has finished
			- If True: 'myFunction' can run again after it has finished
			- If False: 'myFunction' cannot run again after it has finished

		shown (bool)      - Determines when to run the function
			- If True: The function will only run if the window is being shown. If the window is not shown, it will terminate the function. It will wait for the window to first be shown to run
			- If False: The function will run regardless of whether the window is being shown or not
		makeThread (bool) - Determines if this function runs on a different thread
			- If True: A new thread will be created to run the function
			- If False: The function will only run while the GUI is idle. Note: This can cause lag. Use this for operations that must be in the main thread.

		Example Input: oneShot()
		"""

		def runOneShotFunction():
			nonlocal self, myFunction, myFunctionArgs, myFunctionKwargs, delay, allowAgain

			self.oneShotCatalogue[myFunction]["running"] = True

			if ((not delayAfter) and (delay != 0) and (delay != None)):
				time.sleep(delay / 1000)

			self.runMyFunction(myFunction, myFunctionArgs, myFunctionKwargs)

			if ((delayAfter) and (delay != 0) and (delay != None)):
				time.sleep(delay / 1000)

			if (not allowAgain):
				self.oneShotCatalogue[myFunction]["canRun"] = False

			self.oneShotCatalogue[myFunction]["running"] = False

		def runAlternativeFunction():
			nonlocal self, alternativeFunction, alternativeFunctionArgs, alternativeFunctionKwargs

			self.runMyFunction(alternativeFunction, alternativeFunctionArgs, alternativeFunctionKwargs)

		#########################################################

		if (myFunction in self.oneShotCatalogue):
			if ((self.oneShotCatalogue[myFunction]["running"]) or (not self.oneShotCatalogue[myFunction]["canRun"])):
				if (runAlternativeFunction != None):
					self.backgroundRun(runAlternativeFunction, shown = shown, makeThread = makeThread)
				return False
		else:
			self.oneShotCatalogue[myFunction] = {"running": False, "canRun": True}
	
		self.backgroundRun(runOneShotFunction, shown = shown, makeThread = makeThread)
		return True

	def reset_oneShot(self, myFunction):
		"""Allows the oneShot function to run again.

		myFunction (function) - A function that will run once

		Example Input: stop_oneShot()
		"""

		if (myFunction in self.oneShotCatalogue):
			self.oneShotCatalogue[myFunction]["canRun"] = True

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
		if (include == None):
			include = ()
		elif (isinstance(include, (list, range))):
			include = tuple(include)
		elif (not isinstance(include, tuple)):
			include = tuple([include])

		if (exclude == None):
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
				(key != None) and (None in value) and 
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

	#Settings
	def _getItemMod(self, flags = None, stretchable = True, border = 5):
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

		Example Input: _getItemMod("ac")
		Example Input: _getItemMod("ac", border = 10)
		Example Input: _getItemMod("c1")
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

	def _getImage(self, imagePath, internal = False, alpha = False, scale = None):
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

		Example Input: _getImage("example.bmp", 0)
		Example Input: _getImage(image, 0)
		Example Input: _getImage("error", 0, internal = True)
		Example Input: _getImage("example.bmp", 0, alpha = True)
		"""

		if ((imagePath != None) and (imagePath != "")):
			if (type(imagePath) != str):
				if (PIL.Image.isImageType(imagePath)):
					image = self._convertPilToBitmap(imagePath, alpha)
				else:
					errorMessage = f"Unknown file type {type(imagePath)} for _getImage() in {self.__repr__()}"
					raise KeyError(errorMessage)
			else:
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

		if (scale != None):
			if (not isinstance(scale, (list, tuple))):
				scale = [scale, scale]

			if (isinstance(scale[0], float)):
				scale[0] = math.ceil(image.GetWidth() * scale[0])
			if (isinstance(scale[1], float)):
				scale[1] = math.ceil(image.GetHeight() * scale[1])

			image = image.ConvertToImage()
			image = image.Scale(*scale)
			image = wx.Bitmap(image)

		return image

	def _getColor(self, color):
		"""Returns a wxColor object.

		color (str) - What color to return
			- If tuple: Will interperet as (Red, Green, Blue). Values can be integers from 0 to 255 or floats from 0.0 to 1.0

		Example Input: _getColor("white")
		Example Input: _getColor((255, 255, 0))
		Example Input: _getColor((0.5, 0.5, 0.5))
		Example Input: _getColor((255, 0.5, 0))
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
					warnings.warn(f"Unknown color {color} given to _getColor in {self.__repr__()}", Warning, stacklevel = 2)
					return
			elif (not isinstance(color, (list, tuple, range))):
					warnings.warn(f"'color' must be a tuple or string, not a {type(color)}, for _getColor in {self.__repr__()}", Warning, stacklevel = 2)
					return
			elif (len(color) != 3):
					warnings.warn(f"'color' must have a length of three, not {len(color)}, for _getColor in {self.__repr__()}", Warning, stacklevel = 2)
					return

			color = list(color)
			for i, item in enumerate(color):
				if (isinstance(item, float)):
					color[i] = math.ceil(item * 255)

			thing = wx.Colour(color[0], color[1], color[2])
		return thing

	def _getFont(self, size = None, bold = False, italic = False, color = None, family = None):
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

		Example Input: _getFont()
		Example Input: _getFont(size = 72, bold = True, color = "red")
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
	def _convertImageToBitmap(self, imgImage):
		"""Converts a wxImage image (wxPython) to a wxBitmap image (wxPython).
		Adapted from: https://wiki.wxpython.org/WorkingWithImages

		imgImage (object) - The wxBitmap image to convert

		Example Input: _convertImageToBitmap(image)
		"""

		bmpImage = imgImage.ConvertToBitmap()
		return bmpImage

	def _convertBitmapToImage(self, bmpImage):
		"""Converts a wxBitmap image (wxPython) to a wxImage image (wxPython).
		Adapted from: https://wiki.wxpython.org/WorkingWithImages

		bmpImage (object) - The wxBitmap image to convert

		Example Input: _convertBitmapToImage(image)
		"""

		#Determine if a static bitmap was given
		classType = bmpImage.GetClassName()
		if (classType == "wxStaticBitmap"):
			bmpImage = bmpImage.GetBitmap()

		imgImage = bmpImage.ConvertToImage()
		return imgImage

	def _convertImageToPil(self, imgImage):
		"""Converts a wxImage image (wxPython) to a PIL image (pillow).
		Adapted from: https://wiki.wxpython.org/WorkingWithImages

		imgImage (object) - The wxImage image to convert

		Example Input: _convertImageToPil(image)
		"""

		pilImage = PIL.Image.new("RGB", (imgImage.GetWidth(), imgImage.GetHeight()))
		pilImage.fromstring(imgImage.GetData())
		return pilImage

	def _convertBitmapToPil(self, bmpImage):
		"""Converts a wxBitmap image (wxPython) to a PIL image (pillow).
		Adapted from: https://wiki.wxpython.org/WorkingWithImages

		bmpImage (object) - The wxBitmap image to convert

		Example Input: _convertBitmapToPil(image)
		"""

		imgImage = self._convertBitmapToImage(bmpImage)
		pilImage = self._convertImageToPil(imgImage)
		return pilImage

	def _convertPilToImage(self, pilImage, alpha = False):
		"""Converts a PIL image (pillow) to a wxImage image (wxPython).
		Adapted from: https://wiki.wxpython.org/WorkingWithImages

		pilImage (object) - The PIL image to convert
		alpha (bool)      - If True: The image will preserve any alpha chanels

		Example Input: _convertPilToImage(image)
		Example Input: _convertPilToImage(image, True)
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

	def _convertPilToBitmap(self, pilImage, alpha = False):
		"""Converts a PIL image (pillow) to a wxBitmap image (wxPython).
		Adapted from: https://wiki.wxpython.org/WorkingWithImages

		pilImage (object) - The PIL image to convert
		alpha (bool)      - If True: The image will preserve any alpha chanels

		Example Input: _convertPilToBitmap(image)
		"""

		imgImage = self._convertPilToImage(pilImage, alpha)
		bmpImage = self._convertImageToBitmap(imgImage)
		return bmpImage

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
		if (myId == None):
			if (checkSpecial and ("special" in argument_catalogue)):
				special = self._getArguments(argument_catalogue, ["special"])
				if (special != None):
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

		if (self.label != None):
			if (not checkOverride):
				_checkOverride = {}
			elif ((self.parent != None) and (self.label in self.parent.attributeOverride)):
				_checkOverride = self.parent.attributeOverride[self.label]
			elif ((self.myWindow != None) and (self.label in self.myWindow.attributeOverride)):
				_checkOverride = self.myWindow.attributeOverride[self.label]
			else:
				_checkOverride = {}

			if (not checkAppend):
				_checkAppend = {}
			elif ((self.parent != None) and (self.label in self.parent.attributeAppend)):
				_checkAppend = self.parent.attributeAppend[self.label]
			elif ((self.myWindow != None) and (self.label in self.myWindow.attributeAppend)):
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

		if (handle != None):
			argList = [handle, *argList]
		arguments = inspect.getcallargs(function, *argList, **kwargDict)

		if (copyFrom != None):
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

	def _checkHandleType(self, typeNeeded, function):
		#Ensure correct format
		if (not isinstance(typeNeeded, (list, tuple, range))):
			typeNeeded = [typeNeeded]

		#Error check
		if (self.type.lower() not in [str(item).lower() for item in typeNeeded]):
			errorMessage = f"Cannot use type {self.type} with the function {function.__name__}"
			raise TypeError(errorMessage)

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
			if (parent.GetParent() != None):
				parent = parent.GetParent()

				if (parent.GetParent() != None):
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
			
			if (number != None):
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

		if (multiLine == None):
			multiLine = "\n" in line

		if (useDC):
			#Get the current font
			font = self._getFont()
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
			if (frameOnly and (label.type.lower() == "frame")):
				return label

		if (frameOnly):
			window = self.get(label, typeList = [handle_Window], subTypeList = ["frame"])
		else:
			window = self.get(label, typeList = [handle_Window])

		return window

	def getDialog(self, label = None):
		if ((isinstance(label, handle_Window)) and (label.type.lower() == "dialog")):
			return label

		window = self.get(label, typeList = [handle_Window], subTypeList = ["dialog"])
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
		label = None, parent = None, handle = None, myId = None):
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
		handle.type = "Text"
		handle._build(locals())

		return handle

	def _makeHyperlink(self, text = "", myWebsite = "",

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, 

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None):
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
		handle.type = "Hyperlink"
		handle._build(locals())

		return handle

	def _makeEmpty(self, 

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None):
		"""Adds an empty space to the next cell on the grid.

		label (any)     - What this is catalogued as
		selected (bool)   - If True: This is the default thing selected
		hidden (bool)     - If True: The widget is hidden from the user, but it is still created

		Example Input: _makeEmpty()
		Example Input: _makeEmpty(label = "spacer")
		"""

		handle = handle_WidgetText()
		handle.type = "Empty"
		handle._build(locals())

		return handle

	def _makeLine(self, vertical = False,

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None):
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
		handle.type = "Line"
		handle._build(locals())

		return handle

	def _makeListDrop(self, choices = [], default = None, alphabetic = False,

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, 

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None):
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
		"""

		handle = handle_WidgetList()
		handle.type = "ListDrop"
		handle._build(locals())

		return handle

	def _makeListFull(self, choices = [], default = False, single = False, editable = False,
		editOnClick = True, cellType = None, cellTypeDefault = "text", engine = 1, sortable = True,

		columns = None, columnTitles = {}, columnWidth = {}, columnLabels = {},
		columnImage = {}, columnAlign = {}, columnFormatter = {}, check = None,
		border = True, rowLines = True, columnLines = True, report = True,
		
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
		label = None, parent = None, handle = None, myId = None):
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
				~ engine 0:	two clicks to edit, one click to select
				~ engine 1: two clicks to edit
				~ engine 2: two clicks to edit
			- If None: Depends on engine
				~ engine 1: two clicks to edit
				~ engine 1: Pressing F2 edits the primary cell. Tab/Shift-Tab can be used to edit other cells
				~ engine 2: two clicks to edit
		engine (int) - Determines what library base to use for creating the list
			- If 0: Will use wx.ListCtrl
			- If 1: Will use ObjectListView
			- If 2: Will use UltimateListCtrl
			- If None: Will use wx.ListCtrl

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
		handle.type = "ListFull"
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
		label = None, parent = None, handle = None, myId = None):
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
		handle.type = "ListTree"
		handle._build(locals())

		return handle

	def _makeInputSlider(self, myMin = 0, myMax = 100, myInitial = 0, vertical = False,

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None,

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None):
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
		handle.type = "Slider"
		handle._build(locals())

		return handle
	
	def _makeInputBox(self, text = None, maxLength = None, 
		password = False, readOnly = False, tab = True, wrap = None, ipAddress = False,
		
		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, 
		enterFunction = None, enterFunctionArgs = None, enterFunctionKwargs = None, 
		postEditFunction = None, postEditFunctionArgs = None, postEditFunctionKwargs = None, 
		preEditFunction = None, preEditFunctionArgs = None, preEditFunctionKwargs = None, 

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None):
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
		tab (bool)       - If True: The 'Tab' key will move the focus to the next widget
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
		handle.type = "InputBox"
		handle._build(locals())

		return handle
	
	def _makeInputSearch(self, text = None, menuLabel = None, searchButton = True, cancelButton = True,
		hideSelection = True, tab = False, alignment = 0, menuReplaceText = False,

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, 
		enterFunction = None, enterFunctionArgs = None, enterFunctionKwargs = None, 
		searchFunction = None, searchFunctionArgs = None, searchFunctionKwargs = None, 
		cancelFunction = None, cancelFunctionArgs = None, cancelFunctionKwargs = None, 
		menuFunction = None, menuFunctionArgs = None, menuFunctionKwargs = None, 

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None):
		"""Adds an input box to the next cell on the grid.

		text (str)      - What is initially in the box
		label (any)     - What this is catalogued as
		menuLabel (any) - What the menu associated with this is catalogued as
			- If None: Will not show the menu
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
		handle.type = "InputSearch"
		handle._build(locals())

		return handle
	
	def _makeInputSpinner(self, myMin = 0, myMax = 100, myInitial = 0, size = wx.DefaultSize, 
		increment = None, digits = None, useFloat = False, readOnly = False, exclude = [],

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, 
		changeTextFunction = True, changeTextFunctionArgs = None, changeTextFunctionKwargs = None,

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None):
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
		

		Example Input: _makeInputSpinner(0, 100, 50, "initialTemperature")
		Example Input: _makeInputSpinner(0, 100, 50, "initialTemperature", maxSize = (100, 100))
		Example Input: _makeInputSpinner(0, 100, 50, "initialTemperature", exclude = [1,2,3])
		"""

		handle = handle_WidgetInput()
		handle.type = "InputSpinner"
		handle._build(locals())

		return handle
	
	def _makeButton(self, text = "", 
		
		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None,
		
		valueLabel = None,
		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None):
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

		Example Input: _makeButton("Go!", "computeFinArray", 0)
		"""

		handle = handle_WidgetButton()
		handle.type = "Button"
		handle._build(locals())

		return handle
	
	def _makeButtonToggle(self, text = "", 

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, 

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None):
		"""Adds a toggle button to the next cell on the grid.

		text (str)             - What will be written on the button
		myFunction (str)        - What function will be ran when the button is pressed
		flags (list)            - A list of strings for which flag to add to the sizer
		label (any)           - What this is catalogued as
		myFunctionArgs (any)    - The arguments for 'myFunction'
		myFunctionKwargs (any)  - The keyword arguments for 'myFunction'function
		default (bool)          - If True: This is the default thing selected
		enabled (bool)          - If True: The user can interact with this

		Example Input: _makeButtonToggle("Go!", "computeFinArray")
		"""

		handle = handle_WidgetButton()
		handle.type = "ButtonToggle"
		handle._build(locals())

		return handle
	
	def _makeButtonCheck(self, text = "", default = False,

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, 

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None):
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
		handle.type = "ButtonCheck"
		handle._build(locals())

		return handle
	
	def _makeButtonCheckList(self, choices = [], multiple = True, sort = False,

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, 

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None):
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
		handle.type = "CheckList"
		handle._build(locals())

		return handle
	
	def _makeButtonRadio(self, text = "", groupStart = False, default = False,

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, 

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None):
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
		handle.type = "ButtonRadio"
		handle._build(locals())

		return handle
	
	def _makeButtonRadioBox(self, choices = [], title = "", vertical = False, default = 0, maximum = 1,

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, 

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None):
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
		handle.type = "ButtonRadioBox"
		handle._build(locals())

		return handle
	
	def _makeButtonHelp(self, 

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, 

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None):
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
		handle.type = "ButtonHelp"
		handle._build(locals())

		return handle
	
	def _makeButtonImage(self, idlePath = "", disabledPath = "", selectedPath = "", 
		focusPath = "", hoverPath = "", text = None, toggle = False, size = None,
		internal = False, idle_internal = None, disabled_internal = None, 
		selected_internal = None, focus_internal = None, hover_internal = None,

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, 

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None):
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
		handle.type = "ButtonImage"
		handle._build(locals())

		return handle
	
	def _makeImage(self, imagePath = "", internal = False, size = wx.DefaultSize,

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None):
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
		handle.type = "Image"
		handle._build(locals())

		return handle
	
	def _makeProgressBar(self, myInitial = 0, myMax = 100, vertical = False,

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None):
		"""Adds progress bar to the next cell on the grid.

		myInitial (int)         - The value that the progress bar starts at
		myMax (int)             - The value that the progress bar is full at
		flags (list)            - A list of strings for which flag to add to the sizer
		label (any)           - What this is catalogued as

		Example Input: _makeProgressBar(0, 100)
		"""

		handle = handle_Widget_Base()
		handle.type = "ProgressBar"
		handle._build(locals())

		return handle

	def _makeToolBar(self, showText = False, showIcon = True, showDivider = False,
		detachable = False, flat = False, vertical = False, align = True,
		vertical_text = False, showToolTip = True, top = True,

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None,

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None):
		"""Adds a tool bar to the next cell on the grid.
		Menu items can be added to this.

		label (str)     - What this is called in the idCatalogue
		detachable (bool) - If True: The menu can be undocked

		Example Input: _makeToolBar()
		Example Input: _makeToolBar(label = "first")
		"""

		handle = handle_Menu()
		handle.type = "ToolBar"
		handle._build(locals())

		return handle
	
	def _makePickerColor(self, initial = None, addInputBox = False, colorText = False,

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, 

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None):
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
		handle.type = "PickerColor"
		handle._build(locals())

		return handle
	
	def _makePickerFont(self, maxFontSize = 72, addInputBox = False, fontText = False,

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, 

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None):
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
		handle.type = "PickerFont"
		handle._build(locals())

		return handle
	
	def _makePickerFile(self, text = "Select a File", default = "", initialDir = "*.*", 
		directoryOnly = False, changeCurrentDirectory = False, fileMustExist = False, openFile = False, 
		saveConfirmation = False, saveFile = False, smallButton = False, addInputBox = False, 

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None,

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None):
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
		handle.type = "PickerFile"
		handle._build(locals())

		return handle
	
	def _makePickerFileWindow(self, initialDir = "*.*", 
		directoryOnly = True, selectMultiple = False, showHidden = True,

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, 
		editLabelFunction = None, editLabelFunctionArgs = None, editLabelFunctionKwargs = None, 
		rightClickFunction = None, rightClickFunctionArgs = None, rightClickFunctionKwargs = None, 

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None):
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
		handle.type = "PickerFileWindow"
		handle._build(locals())

		return handle
	
	def _makePickerTime(self, time = None,

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, 

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None):
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
		handle.type = "PickerTime"
		handle._build(locals())

		return handle
	
	def _makePickerDate(self, date = None, dropDown = False, 

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, 

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None):
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
		handle.type = "PickerDate"
		handle._build(locals())

		return handle
	
	def _makePickerDateWindow(self, date = None, showHolidays = False, showOther = False,
		
		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, 
		dayFunction = None, dayFunctionArgs = None, dayFunctionKwargs = None, 
		monthFunction = None, monthFunctionArgs = None, monthFunctionKwargs = None, 
		yearFunction = None, yearFunctionArgs = None, yearFunctionArgsKwargs = None, 

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None):
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
		handle.type = "PickerDateWindow"
		handle._build(locals())

		return handle

	def _makeCanvas(self, size = wx.DefaultSize, position = wx.DefaultPosition, 
		panel = {}, metric = None,

		initFunction = None, initFunctionArgs = None, initFunctionKwargs = None,

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None):
		"""Creates a blank canvas window.

		panel (dict) - Instructions for the panel. Keys correspond to the args and kwargs for makePanel
			- If None: Will not create a panel for the canvas

		Example Input: _makeCanvas()
		"""

		handle = handle_WidgetCanvas()
		handle.type = "Canvas"
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
		label = None, parent = None, handle = None, myId = None):

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

		wizardFrameNumber (int) - The number of the wizard page. If None, it assumes either a frame or a panel

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
		handle.type = "Table"
		handle._build(locals())

		return handle

	def _makeMenu(self, text = " ", detachable = False,

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None):
		"""Adds a menu to a pre-existing menubar.
		This is a collapsable array of menu items.

		text (str)        - What the menu is called
			If you add a '&', a keyboard shortcut will be made for the letter after it
		label (str)     - What this is called in the idCatalogue
		detachable (bool) - If True: The menu can be undocked

		Example Input: _makeMenu("&File")
		"""

		handle = handle_Menu()
		handle.type = "Menu"
		handle._build(locals())

		return handle

	#Panels
	def _makePanel(self, border = wx.NO_BORDER, size = wx.DefaultSize, position = wx.DefaultPosition, 
		tabTraversal = True, scroll_x = False, scroll_y = False, scrollToTop = True, scrollToChild = True,

		initFunction = None, initFunctionArgs = None, initFunctionKwargs = None,

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None):
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
		handle.type = "Panel"
		handle._build(locals())

		return handle

	#Sizers
	def _makeSizerGrid(self, rows = 1, columns = 1, text = None,
		rowGap = 0, colGap = 0, minWidth = -1, minHeight = -1,
		size = wx.DefaultSize, scroll_x = False, scroll_y = False, scrollToTop = True, scrollToChild = True,

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None):
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
		handle.type = "Grid"
		handle._build(locals())
		return handle

	def _makeSizerGridFlex(self, rows = 1, columns = 1, text = None, vertical = None,
		rowGap = 0, colGap = 0, minWidth = -1, minHeight = -1, flexGrid = True,
		size = wx.DefaultSize, scroll_x = False, scroll_y = False, scrollToTop = True, scrollToChild = True,

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None):
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

		Example Input: _makeSizerGridFlex()
		Example Input: _makeSizerGridFlex(0)
		Example Input: _makeSizerGridFlex(rows = 4, columns = 3)
		Example Input: _makeSizerGridFlex(0, rows = 4, columns = 3)
		"""

		handle = handle_Sizer()
		handle.type = "Flex"
		handle._build(locals())

		return handle

	def _makeSizerGridBag(self, rows = 1, columns = 1, text = None,
		rowGap = 0, colGap = 0, minWidth = -1, minHeight = -1, vertical = None, 
		emptySpace = None, flexGrid = True,
		size = wx.DefaultSize, scroll_x = False, scroll_y = False, scrollToTop = True, scrollToChild = True,

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None):
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

		Example Input: _makeSizerGridBag()
		Example Input: _makeSizerGridBag(0)
		Example Input: _makeSizerGridBag(0, rows = 4, columns = 3)
		Example Input: _makeSizerGridBag(0, rows = 4, columns = 3, emptySpace = (0, 0))
		"""

		handle = handle_Sizer()
		handle.type = "Bag"
		handle._build(locals())

		return handle

	def _makeSizerBox(self, text = None, minWidth = -1, minHeight = -1, vertical = True,
		size = wx.DefaultSize, scroll_x = False, scroll_y = False, scrollToTop = True, scrollToChild = True,

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None):
		"""Creates a box sizer.

		label (any)     - What this is catalogued as
		minWidth (int)    - The minimum width of a box. -1 means automatic
		minHeight (int)   - The minimum height of a box. -1 means automatic
		horizontal (bool) - True to align items horizontally. False to align items vertically
		hidden (bool)     - If True: All items in the sizer are hidden from the user, but they are still created

		Example Input: _makeSizerBox()
		Example Input: _makeSizerBox(0)
		Example Input: _makeSizerBox(vertical = False)
		Example Input: _makeSizerBox(0, vertical = False)
		"""

		handle = handle_Sizer()
		handle.type = "Box"
		handle._build(locals())

		return handle

	def _makeSizerText(self, text = "", minWidth = -1, minHeight = -1, vertical = True, 
		size = wx.DefaultSize, scroll_x = False, scroll_y = False, scrollToTop = True, scrollToChild = True,

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None):
		"""Creates a static box sizer.
		This is a sizer surrounded by a box with a title, much like a wxRadioBox.

		label (any)     - What this is catalogued as
		text (str)      - The text that appears above the static box
		minWidth (int)    - The minimum width of a box. -1 means automatic
		minHeight (int)   - The minimum height of a box. -1 means automatic
		horizontal (bool) - True to align items horizontally. False to align items vertically
		hidden (bool)     - If True: All items in the sizer are hidden from the user, but they are still created

		Example Input: _makeSizerText()
		Example Input: _makeSizerText(0)
		Example Input: _makeSizerText(text = "Lorem")
		Example Input: _makeSizerText(0, text = "Lorem")
		"""

		handle = handle_Sizer()
		handle.type = "Text"
		handle._build(locals())

		return handle

	def _makeSizerWrap(self, text = None, minWidth = -1, minHeight = -1, extendLast = False, vertical = True,
		size = wx.DefaultSize, scroll_x = False, scroll_y = False, scrollToTop = True, scrollToChild = True,

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None):
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

		Example Input: _makeSizerWrap()
		Example Input: _makeSizerWrap(0)
		"""

		handle = handle_Sizer()
		handle.type = "Wrap"
		handle._build(locals())

		return handle

	#Dialog Boxes
	def makeDialogMessage(self, text = "", title = "", stayOnTop = False, icon = None, 
		addYes = False, addOk = False, addCancel = False, addHelp = False, default = False,

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None):
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
		label = None, parent = None, handle = None, myId = None):
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
		handle._build(locals())
		return handle

	def makeDialogBusy(self, text = "",

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None):
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
		handle._build(locals())
		return handle

	def makeDialogChoice(self, choices = [], text = "", title = "", single = True, default = None,

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None):
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
		"""

		handle = handle_Dialog()
		handle.type = "choice"
		handle._build(locals())
		return handle

	def makeDialogInput(self, text = "", title = "", default = "",
		addYes = False, addOk = True, addCancel = True, addHelp = False,
		password = False, readOnly = False, tab = False, wrap = None, maximum = None,

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None):
		"""Pauses the running code and shows a dialog box that has an input box.

		password (bool) - If True: The text within is shown as dots
		readOnly (bool) - If True: The user cannot change the text
		tab (bool)      - If True: The 'Tab' key will move the focus to the next widget
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
		handle.type = "inputBox"
		handle._build(locals())
		return handle

	def makeDialogFile(self, title = "Select a File", text = "", initialFile = "", initialDir = "", wildcard = "*.*", 
		directoryOnly = False, changeCurrentDirectory = False, fileMustExist = False, openFile = False, 
		saveConfirmation = False, saveFile = False, preview = True, single = True, newDirButton = False,

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None):
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
		handle.type = "file"
		handle._build(locals())
		return handle

	def makeDialogColor(self, simple = True,

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None):
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
		handle._build(locals())
		return handle

	def makeDialogPrint(self, pageNumbers = True, helpButton = False, printToFile = None, selection = None, 
		pageFrom = None, pageTo = None, pageMin = None, pageMax = None, collate = None, copies = None,

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None):
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
		handle.type = "print"
		handle._build(locals())
		return handle

	def makeDialogPrintPreview(self,

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None):
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
		handle.type = "printPreview"
		handle._build(locals())
		return handle

	def makeDialogCustom(self, myFrame = None, valueLabel = None,

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None):
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

		if (myFrame == None):
			myFrame = self

		handle = handle_Dialog()
		handle.type = "custom"
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
class handle_Dummy():
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
		return _Iterator({})

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
		if (traceback != None):
			return False

	def __getattr__(self, name):
		try:
			return super(type(self), self).__getattr__(name, value)
		except:
			return self.dummyFunction

	def dummyFunction(*args, **kwargs):
		pass

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
		if (hasattr(self, "myWindow") and (self.myWindow != None)):
			output += f"-- Window id: {id(self.myWindow)}\n"
		if (hasattr(self, "parentSizer") and (self.parentSizer != None)):
			output += f"-- Sizer id: {id(self.parentSizer)}\n"
		if (self.nested):
			output += "-- nested: True\n"
		if ((self.unnamedList != None) and (len(self.unnamedList) != 0)):
			output += f"-- unnamed items: {len(self.unnamedList)}\n"
		if ((self.labelCatalogue != None) and (len(self.labelCatalogue) != 0)):
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
		return _Iterator(nestedList)

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
		if (traceback != None):
			if (self.allowBuildErrors == None):
				return False
			elif (not self.allowBuildErrors):
				return True

	def _preBuild(self, argument_catalogue):
		"""Runs before this object is built."""

		buildSelf, label, parent = self._getArguments(argument_catalogue, ["self", "label", "parent"])
		
		#Determine parentSizer
		if (hasattr(self, "parentSizer") and (self.parentSizer != None)):
			warnings.warn(f"{self.__repr__()} already has the sizer {self.parentSizer.__repr__()} as 'parentSizer' in _finalNest() for {buildSelf.__repr__()}\nOverwriting 'parentSizer'", Warning, stacklevel = 2)
		
		#Store data
		self.label = label
		self.attributeOverride = {} #Stores variables to override for children {label (str): {variable (str): value (any)}}
		self.attributeAppend = {} #Stores variables to add to the current variables for children {label (str): {variable (str): value (any)}}
		self.makeFunction = inspect.stack()[2].function #The function used to create this handle

		#Determine native sizer
		if (isinstance(buildSelf, handle_Sizer)):
			self.parentSizer = buildSelf
		elif (isinstance(buildSelf, (handle_Window, Controller, handle_MenuPopup))):
			self.parentSizer = None
		elif (isinstance(buildSelf, handle_Menu) and (buildSelf.type.lower() != "toolbar")):
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
		if ((not isinstance(buildSelf, Controller)) and (self.parent == None)):
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
		toolTip = self._getArguments(argument_catalogue, ["toolTip"])

		#Determine visibility
		if (isinstance(self, handle_Window)):
			if (not hidden):
				self.showWindow()
		elif (hidden):
			if (isinstance(self, handle_Sizer)):
				self._addFinalFunction(self.thing.ShowItems, False)
			else:
				self.setShow(False)

		#Determine disability
		if (isinstance(self, handle_Window)):
			if (not enabled):
				pass
		elif (not enabled):
			if (isinstance(self, handle_Sizer)):
				self._addFinalFunction(self.setEnable, False)
			else:
				self.setEnable(False)

		#Determine size constraints
		if (isinstance(self, handle_Sizer)):
			if (maxSize != None):
				self.parent.thing.SetMaxSize(maxSize)
			if (minSize != None):
				self.parent.thing.SetMinSize(minSize)
		else:
			if (maxSize != None):
				self.thing.SetMaxSize(maxSize)
			if (minSize != None):
				self.thing.SetMinSize(minSize)

		#Determine tool tip
		if (toolTip != None):
			self.addToolTip(toolTip)

	def nest(self, handle = None, flex = 0, flags = "c1", selected = False, linkCopy = False):
		"""Nests an object inside of self.

		handle (handle) - What to place in this object
		linkCopy (bool) - Determines what to do if 'handle' is already nested
			- If True: Will nest a linked copy of 'handle'
			- If False: Will nest a copy of 'handle'
			- If None: Will raise an error

		Example Input: nest(text)
		"""

		#Account for automatic text sizer nesting and scroll sizer nesting
		if (isinstance(handle, handle_Sizer)):
			if ((handle.substitute != None) and (handle.substitute != self)):
				handle = handle.substitute

		#Create a link for multi-nested objects
		if (handle.nested):
			if (linkCopy == None):
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
			flags, position, border = self._getItemMod(flags)
			
			if (isinstance(handle, handle_NotebookPage)):
				handle.mySizerItem = self.thing.Add(handle.mySizer.thing, int(flex), eval(flags, {'__builtins__': None, "wx": wx}, {}), border)

			elif (isinstance(handle, (handle_Widget_Base, handle_Sizer, handle_Splitter, handle_Notebook, handle_Panel))):
				handle.mySizerItem = self.thing.Add(handle.thing, int(flex), eval(flags, {'__builtins__': None, "wx": wx}, {}), border)
			
			elif (isinstance(handle, handle_Menu)):
				if (handle.type.lower() == "toolbar"):
					handle.mySizerItem = self.thing.Add(handle.thing, int(flex), eval(flags, {'__builtins__': None, "wx": wx}, {}), border)
				else:
					warnings.warn(f"Add {handle.type} as a handle type for handle_Menu nesting in a handle_Window for nest() in {self.__repr__()}", Warning, stacklevel = 2)
					return
			else:
				warnings.warn(f"Add {handle.__class__} as a handle for handle_Sizer to nest() in {self.__repr__()}", Warning, stacklevel = 2)
				return
			handle.nestedSizer = self
		
		elif (isinstance(self, handle_Panel)):
			if (isinstance(handle, handle_Sizer)):
				self.thing.SetSizer(handle.thing)
				# self.thing.SetAutoLayout(True)
				# handle.thing.Fit(self.thing)
			else:
				warnings.warn(f"Add {handle.__class__} as a handle for handle_Panel to nest() in {self.__repr__()}", Warning, stacklevel = 2)
				return
		
		elif (isinstance(self, handle_Window)):
			if (isinstance(handle, handle_Menu)):
				if (handle.type.lower() == "menu"):
					#Main Menu
					if (self.menuBar == None):
						self.addMenuBar()
					self.menuBar.Append(handle.thing, handle.text)
				else:
					warnings.warn(f"Add {handle.type} as a handle type for handle_Menu nesting in a handle_Window for nest() in {self.__repr__()}", Warning, stacklevel = 2)
					return
			else:
				warnings.warn(f"Add {handle.__class__} as a handle for handle_Window in nest() in {self.__repr__()}", Warning, stacklevel = 2)
				return

		elif (isinstance(self, handle_Menu)):
			if (isinstance(handle, handle_Menu)):
				if (handle.type.lower() == "menu"):
					#Sub Menu
					self.thing.Append(wx.ID_ANY, handle.text, handle.thing)
				else:
					warnings.warn(f"Add {handle.type} as a handle type for handle_Menu nesting in a handle_Menu for nest() in {self.__repr__()}", Warning, stacklevel = 2)
					return

			elif (isinstance(handle, handle_MenuItem)):
				if (handle.type.lower() == "menuitem"):
					self.thing.Append(handle.thing)
				elif (handle.type.lower() == "toolbaritem"):
					pass
				else:
					warnings.warn(f"Add {handle.type} as a handle type for handle_Menu nesting in a handle_Menu for nest() in {self.__repr__()}", Warning, stacklevel = 2)
					return

			else:
				warnings.warn(f"Add {handle.__class__} as a handle for handle_Menu in nest() in {self.__repr__()}", Warning, stacklevel = 2)
				return
		
		elif (isinstance(self, handle_MenuPopup)):
			if (isinstance(handle, handle_MenuPopup)):
				if (handle.type.lower() == "menu"):
					#Sub Menu
					self.contents.append(handle)
					handle.myMenu = self
				else:
					warnings.warn(f"Add {handle.type} as a handle type for handle_Menu nesting in a handle_MenuPopup for nest() in {self.__repr__()}", Warning, stacklevel = 2)
					return
			elif (isinstance(handle, handle_MenuPopupItem)):
				self.contents.append(handle)
				handle.myMenu = self

			elif (isinstance(handle, handle_MenuPopupSubMenu)):
				self.contents.append(handle)
				handle.myMenu = self

			else:
				warnings.warn(f"Add {handle.__class__} as a handle for handle_MenuPopup in nest() in {self.__repr__()}", Warning, stacklevel = 2)
				return
					
		elif (isinstance(self, handle_WidgetInput)):
			if (self.type.lower() == "inputsearch"):
				if (isinstance(handle, handle_Menu)):
					if (handle.type.lower() == "menu"):
						#Sub Menu
						if (handle.label != None):
							self.thing.SetMenu(handle.thing)
						else:
							self.thing.SetMenu(None)
					else:
						warnings.warn(f"Add {handle.type} as a handle type for handle_Menu nesting in a handle_WidgetInput for nest() in {self.__repr__()}", Warning, stacklevel = 2)
						return
				else:
					warnings.warn(f"Add {handle.__class__} as a handle type for handle_Menu nesting in a handle_WidgetInput for nest() in {self.__repr__()}", Warning, stacklevel = 2)
					return
			else:
				warnings.warn(f"Add {self.type} as a handle type for handle_WidgetInput in nest() in {self.__repr__()}", Warning, stacklevel = 2)
				return
		else:
			warnings.warn(f"Add {self.__class__} as self to nest() in {self.__repr__()}", Warning, stacklevel = 2)
			return

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
			if (argsDefaults != None):
				argsDefaults_startsAt = len(argList) - len(argsDefaults) - 1
			for i, variable in enumerate(argList):
				if ((i == 0) and (inspect.ismethod(function))):
					args_noDefaults.append(variable)
					continue #skip self

				if ((argsDefaults == None) or (i < argsDefaults_startsAt)):
					args_noDefaults.append(variable)
				else:
					args_withDefaults[variable] = argsDefaults[i - argsDefaults_startsAt - 1]

			kwargs_noDefaults = []
			kwargs_withDefaults = {}#"linkedHandle_catalogue": None}
			for variable in kwargList:
				if ((kwargsDefaults == None) or (variable not in kwargsDefaults)):
					kwargs_noDefaults.append(variable)
				else:
					kwargs_withDefaults[variable] = kwargsDefaults[variable]

			#The pypubsub module does not accept the names of the args and kwargs as valid values
			#This patches that behavior
			if (starArgs != None):
				kwargs_withDefaults[starArgs] = []
			else:
				kwargs_withDefaults["args"] = []

			if (starStarKwargs != None):
				kwargs_withDefaults[starStarKwargs] = {}
			else:
				kwargs_withDefaults["kwargs"] = {}

			#Create function that will be used to create the subscription topic
			recipe_part1 = ", ".join(args_noDefaults)
			recipe_part2 = ", ".join(f"{key} = {value}" for key, value in args_withDefaults.items())
			recipe_part3 = f"*{starArgs}_patchFor_pypubsub" if (starArgs != None) else "*args_patchFor_pypubsub"
			recipe_part4 = ", ".join(kwargs_noDefaults)
			recipe_part5 = ", ".join(f"{key} = {value}" for key, value in kwargs_withDefaults.items())
			recipe_part6 = f"**{starStarKwargs}_patchFor_pypubsub" if (starStarKwargs != None) else "**kwargs_patchFor_pypubsub"
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

				print("@1", self.__repr__(), args, kwargs, function, label)
				arguments = inspect.getcallargs(function, *args, **kwargs)
				del arguments["self"]
				pubsub.pub.sendMessage(label, **arguments)
			
			setattr(function.__self__, function.__name__, types.MethodType(wrapper, function.__self__)) #Replace function with wrapped function
			pubsub.pub.subscribe(function, label)

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

		if (functionName == None):
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
			if (label == None):
				_label = f"{id(self)}:{_functionName}"
			else:
				_label = label
			linkCatalogue[_functionName] = _label

		for _functionName, _label in linkCatalogue.items():
			myFunction = getattr(self, _functionName)
			topicFunction = getTopicFunction(myFunction)
			topic = topicManager.getOrCreateTopic(_label, protoListener = topicFunction)

			# print("@1.1", myFunction)
			makeLink(myFunction, _label)
			# print("@1.2", myFunction)

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

	#Getters
	def getLabel(self, event = None):
		"""Returns the label for this object."""

		return self.label

	def getSize(self, event = None):
		"""Returns the size of the wxObject."""

		if (self.thing == None):
			size = None
		else:
			size = self.thing.GetSize()

		return size

	def getType(self, event = None):
		"""Returns the type for this object."""

		data = {}
		data["type"] = self.type
		data["self"] = type(self).__name__
		data["thing"] = type(self.thing).__name__

		return data

	#Setters
	def setFunction_size(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		self._betterBind(wx.EVT_SIZE, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)

	def setFunction_position(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		self._betterBind(wx.EVT_MOVE, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)

	def setSize(self, size, event = None):
		"""Sets the size of the wxObject."""

		if (self.thing != None):
			self.thing.SetSize(size)

	#Etc
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

		if (self.nestedParent.type.lower() == "wrap"):
			return #TO DO: Calculate what the position is

		if (self.nestedParent.rows == None):
			return

		if (index == None):
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

		if (self.nestedParent.type.lower() == "wrap"):
			return #TO DO: Calculate what the position is

		if (self.nestedParent.columns == None):
			return

		if (index == None):
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

		#Account for all nested
		if (label == None):
			if (window):
				function = getattr(handle_Widget_Base, myFunction)
				answer = function(self, *args, **kwargs)
				return answer
			else:
				answerList = []
				for handle in self:
					function = getattr(handle, myFunction)
					answer = function(*args, **kwargs)

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
				answer = function(*args, **kwargs)

				if (not isinstance(answer, list)):
					answer = [answer]

				answerList.extend(answer)

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
	def onToggleEnable(self, event, *args, **kwargs):
		"""A wx.CommandEvent version of toggleEnable."""

		self.toggleEnable(*args, event = event, **kwargs)
		event.Skip()

	def toggleEnable(self, label = None, *args, window = False, **kwargs):
		"""Overload for toggleEnable in handle_Widget_Base."""

		self._overloadHelp("toggleEnable", label, args, kwargs, window = window)

	def onSetEnable(self, event, *args, **kwargs):
		"""A wx.CommandEvent version of setEnable."""

		self.setEnable(*args, event = event, **kwargs)
		event.Skip()

	def setEnable(self, label = None, *args, window = False, **kwargs):
		"""Overload for setEnable in handle_Widget_Base."""

		self._overloadHelp("setEnable", label, args, kwargs, window = window)

	def onSetDisable(self, event, *args, **kwargs):
		"""A wx.CommandEvent version of setDisable."""

		self.setDisable(*args, event = event, **kwargs)
		event.Skip()

	def setDisable(self, label = None, *args, window = False, **kwargs):
		"""Overload for setDisable in handle_Widget_Base."""

		self._overloadHelp("setDisable", label, args, kwargs, window = window)

	def onEnable(self, event, *args, **kwargs):
		"""A wx.CommandEvent version of enable."""

		self.enable(*args, event = event, **kwargs)
		event.Skip()

	def enable(self, label = None, *args, window = False, **kwargs):
		"""Overload for enable in handle_Widget_Base."""

		self._overloadHelp("enable", label, args, kwargs, window = window)

	def onDisable(self, event, *args, **kwargs):
		"""A wx.CommandEvent version of disable."""

		self.disable(*args, event = event, **kwargs)
		event.Skip()

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
	def onToggleShow(self, event, *args, **kwargs):
		"""A wx.CommandEvent version of toggleShow."""

		self.toggleShow(*args, event = event, **kwargs)
		event.Skip()

	def toggleShow(self, label = None, *args, window = False, **kwargs):
		"""Overload for toggleShow in handle_Widget_Base."""

		self._overloadHelp("toggleShow", label, args, kwargs, window = window)

	def onSetShow(self, event, *args, **kwargs):
		"""A wx.CommandEvent version of setShow."""

		self.setShow(*args, event = event, **kwargs)
		event.Skip()

	def setShow(self, label = None, *args, window = False, **kwargs):
		"""Overload for setShow in handle_Widget_Base."""

		self._overloadHelp("setShow", label, args, kwargs, window = window)

	def onSetHide(self, event, *args, **kwargs):
		"""A wx.CommandEvent version of setHide."""

		self.setHide(*args, event = event, **kwargs)
		event.Skip()

	def setHide(self, label = None, *args, window = False, **kwargs):
		"""Overload for setHide in handle_Widget_Base."""

		self._overloadHelp("setHide", label, args, kwargs, window = window)

	def onShow(self, event, *args, **kwargs):
		"""A wx.CommandEvent version of show."""

		self.show(*args, event = event, **kwargs)
		event.Skip()

	def show(self, label = None, *args, window = False, **kwargs):
		"""Overload for show in handle_Widget_Base."""

		self._overloadHelp("show", label, args, kwargs, window = window)

	def onHide(self, event, *args, **kwargs):
		"""A wx.CommandEvent version of hide."""

		self.hide(*args, event = event, **kwargs)
		event.Skip()

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
	def onModify(self, event, *args, **kwargs):
		"""A wx.CommandEvent version of modify."""

		self.modify(*args, event = event, **kwargs)
		event.Skip()

	def modify(self, label = None, *args, window = False, **kwargs):
		"""Overload for modify in handle_Widget_Base."""

		self._overloadHelp("modify", label, args, kwargs, window = window)

	def onSetModified(self, event, *args, **kwargs):
		"""A wx.CommandEvent version of setModified."""

		self.setModified(*args, event = event, **kwargs)
		event.Skip()

	def setModified(self, label = None, *args, window = False, **kwargs):
		"""Overload for setModified in handle_Widget_Base."""

		self._overloadHelp("setModified", label, args, kwargs, window = window)

	def checkModified(self, label = None, *args, window = False, **kwargs):
		"""Overload for checkModified in handle_Widget_Base."""

		answer = self._overloadHelp("checkModified", label, args, kwargs, window = window)
		return answer

	##Read Only
	def onReadOnly(self, event, *args, **kwargs):
		"""A wx.CommandEvent version of readOnly."""

		self.readOnly(*args, event = event, **kwargs)
		event.Skip()

	def readOnly(self, label = None, *args, window = False, **kwargs):
		"""Overload for readOnly in handle_Widget_Base."""

		self._overloadHelp("readOnly", label, args, kwargs, window = window)

	def onSetReadOnly(self, event, *args, **kwargs):
		"""A wx.CommandEvent version of setReadOnly."""

		self.setReadOnly(*args, event = event, **kwargs)
		event.Skip()

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

		if (self.type.lower() == "progressbar"):
			value = self.thing.GetRange()

		else:
			warnings.warn(f"Add {self.type} to __len__() for {self.__repr__()}", Warning, stacklevel = 2)
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

		if (self.type.lower() == "line"):
			_build_line()
		elif (self.type.lower() == "progressbar"):
			_build_progressBar()
		else:
			warnings.warn(f"Add {self.type} to _build() for {self.__repr__()}", Warning, stacklevel = 2)

		self._postBuild(argument_catalogue)

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
		"""Sets the contextual value for the object associated with this handle to what the user supplies."""

		if (self.type.lower() == "progressbar"):
			if (not isinstance(newValue, int)):
				newValue = int(newValue)

			self.thing.SetValue(newValue)

		else:
			warnings.warn(f"Add {self.type} to setValue() for {self.__repr__()}", Warning, stacklevel = 2)

	def setSelection(self, newValue, event = None):
		"""Sets the contextual selection for the object associated with this handle to what the user supplies."""

		warnings.warn(f"Add {self.type} to setSelection() for {self.__repr__()}", Warning, stacklevel = 2)

	def setReadOnly(self, state = True, event = None):
		"""Sets the contextual readOnly for the object associated with this handle to what the user supplies."""

		if (self.type.lower() == "line"):
			pass
			
		else:
			warnings.warn(f"Add {self.type} to setReadOnly() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_rightClick(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		self._betterBind(wx.EVT_RIGHT_DOWN, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)

	def addPopupMenu(self, label = None, rightClick = True, 

		preFunction = None, preFunctionArgs = None, preFunctionKwargs = None, 
		postFunction = None, postFunctionArgs = None, postFunctionKwargs = None,

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		parent = None, handle = None, myId = None):
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

		if (hasattr(self, "nestedSizer") and (self.nestedSizer.type.lower() == "flex")):
			with self.nestedSizer as mySizer:
				index = self.getSizerIndex()
				row, column = self.getSizerCoordinates()
				updateNeeded = False

				if ((row in mySizer.growFlexRow_notEmpty) and (state == (not mySizer.thing.IsRowGrowable(row)))):
					leftBound = (row + 1) * mySizer.columns - mySizer.columns
					rightBound = (row + 1) * mySizer.columns
					updateNeeded = True

					if (any([mySizer.thing.GetItem(i).IsShown() for i in range(leftBound, rightBound)])):
						mySizer.growFlexRow(row, proportion = mySizer.growFlexRow_notEmpty[row])
					else:
						mySizer.thing.RemoveGrowableRow(row)

				if ((column in mySizer.growFlexColumn_notEmpty) and (state == (not mySizer.thing.IsColGrowable(column)))):
					leftBound = column
					rightBound = mySizer.rows * mySizer.columns
					step = mySizer.columns
					updateNeeded = True
					
					if (any([mySizer.thing.GetItem(i).IsShown() for i in range(leftBound, rightBound, step)])):
						mySizer.growFlexColumn(column, proportion = mySizer.growFlexColumn_notEmpty[column])
					else:
						mySizer.thing.RemoveGrowableCol(column)

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

		label = None, identity = None, myId = None):
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

		if (isinstance(self, (handle_MenuItem, handle_MenuPopupItem))):		
			#Do not add empty tool tips
			if (len(text) != 0):
				if (self.type.lower() == "menuitem"):
					self.thing.SetHelp(text)
				elif (self.type.lower() == "toolbaritem"):
					self.thing.SetShortHelp(text)
					self.thing.SetLongHelp(text)
		else:
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
			if (alignment != None):
				if (isinstance(alignment, bool)):
					if (alignment):
						style = "wx.ALIGN_LEFT"
						self.flags_modification.append("al")
					else:
						style = "wx.ALIGN_CENTRE"
						self.flags_modification.append("ac")
				elif (isinstance(alignment, str)):
					if (alignment[0].lower() == "l"):
						style = "wx.ALIGN_LEFT"
						self.flags_modification.append("al")
					elif (alignment[0].lower() == "r"):
						style = "wx.ALIGN_RIGHT"
						self.flags_modification.append("ar")
					else:
						style = "wx.ALIGN_CENTRE"
						self.flags_modification.append("ac")
				elif (alignment == 0):
					style = "wx.ALIGN_LEFT"
					self.flags_modification.append("al")
				elif (alignment == 1):
					style = "wx.ALIGN_RIGHT"
					self.flags_modification.append("ar")
				else:
					style = "wx.ALIGN_CENTRE"
					self.flags_modification.append("ac")
			else:
				style = "wx.ALIGN_CENTRE"
				self.flags_modification.append("ac")
			
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

			myId = self._getId(argument_catalogue)

			#Create the thing to put in the grid
			self.thing = wx.StaticText(self.parent.thing, id = myId, label = text, style = eval(style, {'__builtins__': None, "wx": wx}, {}))

			# font = self._getFont(size = size, bold = bold, italic = italic, color = color, family = family)
			# self.thing.SetFont(font)

			# if (wrap != None):
			#   if (wrap > 0):
			#       self.wrapText(wrap)

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

		if (self.type.lower() == "text"):
			_build_text()
		elif (self.type.lower() == "hyperlink"):
			_build_hyperlink()
		elif (self.type.lower() == "empty"):
			_build_empty()
		else:
			warnings.warn(f"Add {self.type} to _build() for {self.__repr__()}", Warning, stacklevel = 2)

		self._postBuild(argument_catalogue)

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
			self._betterBind(wx.adv.EVT_HYPERLINK, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		else:
			warnings.warn(f"Add {self.type} to setFunction_click() for {self.__repr__()}", Warning, stacklevel = 2)

class handle_WidgetList(handle_Widget_Base):
	"""A handle for working with list widgets."""

	def __init__(self):
		"""Initializes defaults."""

		#Initialize inherited classes
		handle_Widget_Base.__init__(self)

		#Internal Variables
		self.dragable = False
		self.myDropTarget = None

		self.checkColumn = None
		self.columnCatalogue = {}
		self.selectionColor = None

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
				value = len(self.columnCatalogue)

		else:
			warnings.warn(f"Add {self.type} to __len__() for {self.__repr__()}", Warning, stacklevel = 2)
			value = 0

		return value

	def _build(self, argument_catalogue):
		"""Determiens which build system to use for this handle."""

		def _build_listDrop():
			"""Builds a wx choice object."""
			nonlocal self, argument_catalogue

			choices, alphabetic, default = self._getArguments(argument_catalogue, ["choices", "alphabetic", "default"])

			#Ensure that the choices given are a list or tuple
			if (not isinstance(choices, (list, tuple))):
				choices = list(choices)

			#Ensure that the choices are all strings
			choices = [str(item) for item in choices]

			#Apply Settings
			if (alphabetic):
				style = wx.CB_SORT
			else:
				style = 0

			myId = self._getId(argument_catalogue)

			#Create the thing to put in the grid
			inputBox = False
			if (inputBox):
				self.thing = wx.ComboBox(self.parent.thing, id = myId, choices = choices, style = style) #wx.CB_DROPDOWN wx.CB_SIMPLE wx.CB_READONLY wx.CB_SORT
			else:
				self.thing = wx.Choice(self.parent.thing, id = myId, choices = choices, style = style)
			
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
			myFunction, myFunctionArgs, myFunctionKwargs = self._getArguments(argument_catalogue, ["myFunction", "myFunctionArgs", "myFunctionKwargs"])
			self.setFunction_click(myFunction, myFunctionArgs, myFunctionKwargs)

		def _build_listFull():
			"""Builds a wx choice object.
			Use: https://pypi.org/project/ObjectListView/1.3.1/
			Use: http://objectlistview-python-edition.readthedocs.io/en/latest/
			Use: http://www.blog.pythonlibrary.org/index.php?s=medialocker&submit=Search
			Use: https://www.codeproject.com/KB/list/objectlistview.aspx
			Use: https://www.codeproject.com/Articles/16009/A-Much-Easier-to-Use-ListView
			Use: http://code.activestate.com/recipes/577543-objectlistview-getcolumnclickedevent-handler/
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

			columnTitles, columnWidth, check = self._getArguments(argument_catalogue, ["columnTitles", "columnWidth", "check"])
			report, single, editable, editOnClick, columnLabels = self._getArguments(argument_catalogue, ["report", "single", "editable", "editOnClick", "columnLabels"])
			columnImage, columnAlign, columnFormatter = self._getArguments(argument_catalogue, ["columnImage", "columnAlign", "columnFormatter"])
			border, rowLines, columnLines, sortable = self._getArguments(argument_catalogue, ["border", "rowLines", "columnLines", "sortable"])
			columns, drag, drop, choices, engine = self._getArguments(argument_catalogue, ["columns", "drag", "drop", "choices", "engine"])

			#Determine style
			if (report):
				style = "wx.LC_REPORT"
			else:
				style = "wx.LC_LIST" #Auto calculate columns and rows
				columns = 1

			if (border):
				style += "|wx.BORDER_SUNKEN"
			if (rowLines):
				style += "|wx.LC_HRULES"
			if (columnLines):
				style += "|wx.LC_VRULES"

			if (single):
				style += "|wx.LC_SINGLE_SEL" #Default: Can select multiple with shift

			if (columns == None):
				if ((choices == None) or (not isinstance(choices, (list, tuple, range, dict))) or (len(choices) == 0)):
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

			#Create widget id
			myId = self._getId(argument_catalogue)

			#Create the thing to put in the grid
			self.thing = self._ListFull(self, self.parent.thing, myId = myId, style = style, sortable = sortable)

			if (editOnClick != None):
				if (editOnClick):
					self.thing.cellEditMode = ObjectListView.ObjectListView.CELLEDIT_SINGLECLICK
				else:
					self.thing.cellEditMode = ObjectListView.ObjectListView.CELLEDIT_DOUBLECLICK
			else:
				self.thing.cellEditMode = ObjectListView.ObjectListView.CELLEDIT_F2ONLY

			#Create columns
			self.checkColumn = check
			for i in range(columns):
				self.setColumn(i, title = columnTitles[i], label = columnLabels[i], width = columnWidth[i], editable = editable[i], 
					align = columnAlign[i], image = columnImage[i], formatter = columnFormatter[i], minWidth = None, refresh = False)
			self.refreshColumns()

			#Add Items
			self.setValue(choices)

			# #Determine if it's contents are dragable
			# if (drag):
			# 	dragLabel, dragDelete, dragCopyOverride, allowExternalAppDelete = self._getArguments(argument_catalogue, ["dragLabel", "dragDelete", "dragCopyOverride", "allowExternalAppDelete"])
			# 	preDragFunction, preDragFunctionArgs, preDragFunctionKwargs = self._getArguments(argument_catalogue, ["preDragFunction", "preDragFunctionArgs", "preDragFunctionKwargs"])
			# 	postDragFunction, postDragFunctionArgs, postDragFunctionKwargs = self._getArguments(argument_catalogue, ["postDragFunction", "postDragFunctionArgs", "postDragFunctionKwargs"])
				
			# 	self.dragable = True
			# 	self._betterBind(wx.EVT_LIST_BEGIN_DRAG, self.thing, self._onDragList_beginDragAway, None, 
			# 		{"label": dragLabel, "deleteOnDrop": dragDelete, "overrideCopy": dragCopyOverride, "allowExternalAppDelete": allowExternalAppDelete})
				
			# 	self.preDragFunction = preDragFunction
			# 	self.preDragFunctionArgs = preDragFunctionArgs
			# 	self.preDragFunctionKwargs = preDragFunctionKwargs

			# 	self.postDragFunction = postDragFunction
			# 	self.postDragFunctionArgs = postDragFunctionArgs
			# 	self.postDragFunctionKwargs = postDragFunctionKwargs

			# #Determine if it accepts dropped items
			# if (drop):
			# 	dropIndex = self._getArguments(argument_catalogue, ["dropIndex"])
			# 	preDropFunction, preDropFunctionArgs, preDropFunctionKwargs = self._getArguments(argument_catalogue, ["preDropFunction", "preDropFunctionArgs", "preDropFunctionKwargs"])
			# 	postDropFunction, postDropFunctionArgs, postDropFunctionKwargs = self._getArguments(argument_catalogue, ["postDropFunction", "postDropFunctionArgs", "postDropFunctionKwargs"])
			# 	dragOverFunction, dragOverFunctionArgs, postDropFunctionKwargs = self._getArguments(argument_catalogue, ["dragOverFunction", "dragOverFunctionArgs", "postDropFunctionKwargs"])
				
			# 	self.myDropTarget = self._DragTextDropTarget(self.thing, dropIndex,
			# 		preDropFunction = preDropFunction, preDropFunctionArgs = preDropFunctionArgs, preDropFunctionKwargs = preDropFunctionKwargs, 
			# 		postDropFunction = postDropFunction, postDropFunctionArgs = postDropFunctionArgs, postDropFunctionKwargs = postDropFunctionKwargs,
			# 		dragOverFunction = dragOverFunction, dragOverFunctionArgs = dragOverFunctionArgs, dragOverFunctionKwargs = postDropFunctionKwargs)
			# 	self.thing.SetDropTarget(self.myDropTarget)

			# #Bind the function(s)
			# myFunction, preEditFunction, postEditFunction = self._getArguments(argument_catalogue, ["myFunction", "preEditFunction", "postEditFunction"])
			# if (myFunction != None):
			# 	myFunctionArgs, myFunctionKwargs = self._getArguments(argument_catalogue, ["myFunctionArgs", "myFunctionKwargs"])
			# 	self.setFunction_click(myFunction, myFunctionArgs, myFunctionKwargs)

			# if (preEditFunction):
			# 	preEditFunctionArgs, preEditFunctionKwargs = self._getArguments(argument_catalogue, ["preEditFunctionArgs", "preEditFunctionKwargs"])
			# 	self.setFunction_preEdit(preEditFunction, preEditFunctionArgs, preEditFunctionKwargs)

			# if (postEditFunction):
			# 	postEditFunctionArgs, postEditFunctionKwargs = self._getArguments(argument_catalogue, ["postEditFunctionArgs", "postEditFunctionKwargs"])
			# 	self.setFunction_postEdit(postEditFunction, postEditFunctionArgs, postEditFunctionKwargs)

			# if (editOnClick):
			# 	pass

		def _build_listTree():
			"""Builds a wx choice object."""
			nonlocal self, argument_catalogue

			
			choices, drag, drop = self._getArguments(argument_catalogue, ["choices", "drag", "drop"])
			addButton, editable, rowHighlight, root = self._getArguments(argument_catalogue, ["addButton", "editable", "rowHighlight", "root"])
			rowLines, rootLines, variableHeight, selectMultiple = self._getArguments(argument_catalogue, ["rowLines", "rootLines", "variableHeight", "selectMultiple"])

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

			if (myFunction != None):
				myFunctionArgs, myFunctionKwargs = self._getArguments(argument_catalogue, ["myFunctionArgs", "myFunctionKwargs"])
				self.setFunction_postClick(myFunction, myFunctionArgs, myFunctionKwargs)

			if (preEditFunction != None):
				preEditFunctionArgs, preEditFunctionKwargs = self._getArguments(argument_catalogue, ["preEditFunctionArgs", "preEditFunctionKwargs"])
				self.setFunction_preEdit(preEditFunction, preEditFunctionArgs, preEditFunctionKwargs)

			if (postEditFunction != None):
				postEditFunctionArgs, postEditFunctionKwargs = self._getArguments(argument_catalogue, ["postEditFunctionArgs", "postEditFunctionKwargs"])
				self.setFunction_postEdit(postEditFunction, postEditFunctionArgs, postEditFunctionKwargs)

			if (preCollapseFunction != None):
				preCollapseFunctionArgs, preCollapseFunctionKwargs = self._getArguments(argument_catalogue, ["preCollapseFunctionArgs", "preCollapseFunctionKwargs"])
				self.setFunction_collapse(preCollapseFunction, preCollapseFunctionArgs, preCollapseFunctionKwargs)

			if (postCollapseFunction != None):
				postCollapseFunctionArgs, postCollapseFunctionKwargs = self._getArguments(argument_catalogue, ["postCollapseFunctionArgs", "postCollapseFunctionKwargs"])
				self.setFunction_collapse(postCollapseFunction, postCollapseFunctionArgs, postCollapseFunctionKwargs)

			if (preExpandFunction != None):
				preExpandFunctionArgs, preExpandFunctionKwargs = self._getArguments(argument_catalogue, ["preExpandFunctionArgs", "preExpandFunctionKwargs"])
				self.setFunction_expand(preExpandFunction, preExpandFunctionArgs, preExpandFunctionKwargs)

			if (postExpandFunction != None):
				postExpandFunctionArgs, postExpandFunctionKwargs = self._getArguments(argument_catalogue, ["postExpandFunctionArgs", "postExpandFunctionKwargs"])
				self.setFunction_expand(postExpandFunction, postExpandFunctionArgs, postExpandFunctionKwargs)

			if (rightClickFunction != None):
				rightClickFunctionArgs, rightClickFunctionKwargs = self._getArguments(argument_catalogue, ["rightClickFunctionArgs", "rightClickFunctionKwargs"])
				self.setFunction_rightClick(rightClickFunction, rightClickFunctionArgs, rightClickFunctionKwargs)

			if (middleClickFunction != None):
				middleClickFunctionArgs, middleClickFunctionKwargs = self._getArguments(argument_catalogue, ["middleClickFunctionArgs", "middleClickFunctionKwargs"])
				self.setFunction_middleClick(middleClickFunction, middleClickFunctionArgs, middleClickFunctionKwargs)
			
			if (doubleClickFunction != None):
				doubleClickFunctionArgs, doubleClickFunctionKwargs = self._getArguments(argument_catalogue, ["doubleClickFunctionArgs", "doubleClickFunctionKwargs"])
				self.setFunction_doubleClick(doubleClickFunction, doubleClickFunctionArgs, doubleClickFunctionKwargs)

			if (keyDownFunction != None):
				keyDownFunctionArgs, keyDownFunctionKwargs = self._getArguments(argument_catalogue, ["keyDownFunctionArgs", "keyDownFunctionKwargs"])
				self.setFunction_keyDown(keyDownFunction, keyDownFunctionArgs, keyDownFunctionKwargs)

			if (toolTipFunction != None):
				toolTipFunctionArgs, toolTipFunctionKwargs = self._getArguments(argument_catalogue, ["toolTipFunctionArgs", "toolTipFunctionKwargs"])
				self.setFunction_toolTip(toolTipFunction, toolTipFunctionArgs, toolTipFunctionKwargs)
			
			if (itemMenuFunction != None):
				itemMenuFunctionArgs, itemMenuFunctionKwargs = self._getArguments(argument_catalogue, ["itemMenuFunctionArgs", "itemMenuFunctionKwargs"])
				self.setFunction_itemMenu(itemMenuFunction, itemMenuFunctionArgs, itemMenuFunctionKwargs)

		#########################################################

		self._preBuild(argument_catalogue)

		if (self.type.lower() == "listdrop"):
			_build_listDrop()
		elif (self.type.lower() == "listfull"):
			_build_listFull()
		elif (self.type.lower() == "listtree"):
			_build_listTree()
		else:
			warnings.warn(f"Add {self.type} to _build() for {self.__repr__()}", Warning, stacklevel = 2)

		self._postBuild(argument_catalogue)

	#Getters
	def getValue(self, event = None):
		"""Returns what the contextual value is for the object associated with this handle."""

		if (self.type.lower() == "listdrop"):
			index = self.thing.GetSelection()
			value = self.thing.GetString(index) #(str) - What is selected in the drop list

		elif (self.type.lower() == "listfull"):
			value = self.thing.GetSelectedObjects()

			if (not self.thing.InReportView()):
				value = [item.value for item in value]

		elif (self.type.lower() == "listtree"):
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
			warnings.warn(f"Add {self.type} to getValue() for {self.__repr__()}", Warning, stacklevel = 2)
			value = None

		return value

	def getChecked(self, event = None):
		value = []
		for item in self.thing.GetObjects():
			if (self.thing.IsChecked(item)):
				value.append(item)
		return value

	def getIndex(self, event = None):
		"""Returns what the contextual index is for the object associated with this handle."""

		if (self.type.lower() == "listdrop"):
			value = self.thing.GetSelection() #(int) - The index number of what is selected in the drop list    

		elif (self.type.lower() == "listfull"):
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
			columnCount = self.columns

			n = self.thing.GetItemCount()
			for row in range(rowCount):
				subValue = []
				for column in range(columnCount):
					subValue.append(self.thing.GetItem(row, column).GetText()) #(list) - What is in the full list as strings
				value.append(subValue)
	
		elif (self.type.lower() == "listtree"):
			value = {}
			root = self.thing.GetRootItem()

			print("@1.1", self.subType.lower())
			if (self.subType.lower() == "hiddenroot"):
				rootText = None
			else:
				rootText = self.thing.GetItemText(root)

			if (self.thing.ItemHasChildren(root)):
				first, cookie = self.thing.GetFirstChild(root)
				text = self.thing.GetItemText(first)
				print("@1.2", text)
				value[rootText] = {text: None}

			if (self.subType.lower() == "hiddenroot"):
				value = value[rootText]

		else:
			warnings.warn(f"Add {self.type} to getAll() for {self.__repr__()}", Warning, stacklevel = 2)
			value = None

		return value

	def getColumn(self, event = None):
		"""Returns what the contextual column is for the object associated with this handle.
		Column algorithm from: wx.lib.mixins.listctrl.TextEditMixin
		"""

		if (self.type.lower() == "listfull"):
			x, y = self.getMousePosition()
			x_offset = self.thing.GetScrollPos(wx.HORIZONTAL)
			row, flags = self.thing.HitTest((x,y))

			widthList = [0]
			for i in range(self.thing.GetColumnCount()):
				widthList.append(widthList[i] + self.thing.GetColumnWidth(i))
			column = bisect.bisect(widthList, x + x_offset) - 1

		else:
			warnings.warn(f"Add {self.type} to getColumn() for {self.__repr__()}", Warning, stacklevel = 2)
			column = None

		return column

	#Setters
	def _formatList(self, newValue, filterNone = False):

		if (isinstance(newValue, (range, types.GeneratorType))):
			newValue = list(newValue)
		elif (not isinstance(newValue, (list, tuple, dict))):
			newValue = [newValue]

		if (any((not hasattr(item, '__dict__') for item in newValue))):
			#The user gave a list of non objects
			if ((isinstance(newValue, (list, tuple))) and (len(newValue) != 0)):
				newValue = [item if isinstance(item, (list, tuple)) else list(item) if isinstance(item, range) else [item] for item in newValue]		

			#Ensure correct length
			for item in newValue:
				while (len(item) < len(self.columnCatalogue)):
					item.append("")

			#Handle None
			if (filterNone != None):
				for item in newValue:
					if (filterNone):
						item[:] = [str(value) for value in item if value is not None] #Filter out None
					else:
						item[:] = [str(value) if (value != None) else "" for value in item] #Replace None with blank space

			#Finish formatting insurance
			if (not isinstance(newValue, dict)):
				itemDict = {}
				for row, columnList in enumerate(newValue):
					if (row not in itemDict):
						itemDict[row] = {}
					
					for column, text in enumerate(columnList):
						itemDict[row][column] = text
			else:
				itemDict = newValue

			#Add Items
			objectList = []
			for row, columnDict in itemDict.items():
				contents = {}
				for column, text in columnDict.items():
					while (column not in self.columnCatalogue):
						self.addColumn()

					if (isinstance(column, int)):
						variable = self.columnCatalogue[column]["valueGetter"]
					else:
						variable = column

					contents[variable] = f"{text}"
				contents["__repr__"] = lambda self: f"""ListItem({", ".join(f"{variable} = {getattr(self, variable).__repr__() if hasattr(getattr(self, variable), '__repr__') else getattr(self, variable)}" for variable in dir(self) if not variable.startswith("__"))})"""

				objectList.append(type("ListItem", (object,), contents)())
		else:
			#The user gave a list of objects
			objectList = newValue
		return objectList

	def setValue(self, newValue, filterNone = False, event = None):
		"""Sets the contextual value for the object associated with this handle to what the user supplies."""

		if (self.type.lower() == "listdrop"):
			if (isinstance(newValue, (range, types.GeneratorType))):
				newValue = list(newValue)
			elif (not isinstance(newValue, (list, tuple))):
				newValue = [newValue]

			if (filterNone != None):
				if (filterNone):
					if (None in newValue):
						newValue[:] = [str(value) for value in newValue if value is not None] #Filter out None
				else:
					newValue[:] = [str(value) if (value != None) else "" for value in newValue] #Replace None with blank space

			self.thing.Clear()
			self.thing.AppendItems(newValue) #(list) - What the choice options will now be now

		elif (self.type.lower() == "listfull"):
			objectList = self._formatList(newValue, filterNone = filterNone)
			self.thing.SetObjects(objectList)

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

	def addColumn(self, *args, **kwargs):
		self.setColumn(column = len(self.columnCatalogue), *args, **kwargs)

	def setColumn(self, column = None, title = None, label = None, width = None, editable = None, align = None, image = None, formatter = None, minWidth = None, refresh = True):
		"""Sets the contextual column for this handle."""

		#Create columns
		if (self.type.lower() == "listfull"):
			if (column == None):
				column = len(self.columnCatalogue)

			if (column not in self.columnCatalogue):
				self.columnCatalogue[column] = {}

			self.columnCatalogue[column].setdefault("title", "")
			self.columnCatalogue[column].setdefault("align", "left")
			self.columnCatalogue[column].setdefault("width", -1)
			self.columnCatalogue[column].setdefault("valueGetter", None)
			self.columnCatalogue[column].setdefault("isEditable", True)
			self.columnCatalogue[column].setdefault("minimumWidth", 5)
			self.columnCatalogue[column].setdefault("isSpaceFilling", False)
			self.columnCatalogue[column].setdefault("imageGetter", None)
			self.columnCatalogue[column].setdefault("stringConverter", None)

			if (title != None):
				self.columnCatalogue[column]["title"] = title
			if (align != None):
				self.columnCatalogue[column]["align"] = align
			if (label != None):
				self.columnCatalogue[column]["valueGetter"] = label
			if (image != None):
				self.columnCatalogue[column]["imageGetter"] = image
			if (editable != None):
				self.columnCatalogue[column]["isEditable"] = editable
			if (minWidth != None):
				self.columnCatalogue[column]["minimumWidth"] = minWidth
			if (formatter != None):
				self.columnCatalogue[column]["stringConverter"] = formatter

			if (width != None):
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
			elif (self.columnCatalogue[column]["valueGetter"] == None):
				self.columnCatalogue[column]["valueGetter"] = f"unnamed_{column}" 

			#All images must be callable
			if ((self.columnCatalogue[column]["imageGetter"] != None) and (not callable(self.columnCatalogue[column]["imageGetter"]))):
				value = self.columnCatalogue[column]["imageGetter"]
				self.columnCatalogue[column]["imageGetter"] = lambda item: value

			if (refresh):
				self.refreshColumns()
		else:
			warnings.warn(f"Add {self.type} to setColumns() for {self.__repr__()}", Warning, stacklevel = 2)

	def refreshColumns(self):
		if (self.type.lower() == "listfull"):
			self.thing.SetColumns((ObjectListView.ColumnDefn(**kwargs) for column, kwargs in sorted(self.columnCatalogue.items())))

			if (self.checkColumn != None):
				self.thing.CreateCheckStateColumn(self.checkColumn)
		else:
			warnings.warn(f"Add {self.type} to setColumns() for {self.__repr__()}", Warning, stacklevel = 2)

	def refresh(self):
		self.thing.RepopulateList()

	def clearAll(self):
		self.columnCatalogue = {}
		self.thing.ClearAll()

	def addColumnCheck(self, *args, **kwargs):
		self.setColumnCheck(column = len(self.columnCatalogue), *args, **kwargs)
	
	def setColumnCheck(self, column, refresh = True):
		self.checkColumn = column
		if (refresh):
			self.refreshColumns()

	def uncheck(self, row = None, state = True):
		self.check(row = row, state = not state)

	def check(self, row = None, state = True):
		if (row == None):
			row = self.thing.GetObjects()
		elif (isinstance(row, (range, types.GeneratorType))):
			row = list(row)
		elif (not isinstance(row, (list, tuple))):
			row = [row]

		for _row in row:
			if (not hasattr(_row, '__dict__')):
				#The user passed in a non-object
				item = self.thing.GetObjectAt(_row)
			else:
				#The user passed in an object
				item = _row

			if (state != None):
				if (state):
					self.thing.Check(item)
				else:
					self.thing.Uncheck(item)
			else:
				self.thing.ToggleCheck(item)
		self.thing.RefreshObjects(row)

	def checkChecked(self, row = None):
		if (isinstance(row, (range, types.GeneratorType))):
			row = list(row)
		elif (not isinstance(row, (list, tuple))):
			row = [row]

		valueList = []
		for _row in row:
			if (hasattr(_row, '__dict__')):
				#The user passed in a non-object
				item = self.thing.GetObjectAt(_row)
			else:
				#The user passed in an object
				item = _row

			valueList.append(item.IsChecked(item))

		return valueList

	def setColor(self, even = None, odd = None, selected = None):
		if (even != None):
			self.thing.evenRowsBackColor = self._getColor(even)
		if (odd != None):
			self.thing.oddRowsBackColor = self._getColor(odd)
		if (selected != None):
			self.selectionColor = self._getColor(selected)

	def addImage(self, label, imagePath, internal = False):
		"""Adds an image to the image catalogue.

		Example Input: addImage("correct", "markCheck", internal = True)
		"""

		image_16 = self._getImage(imagePath, internal = internal, scale = (16, 16))
		image_32 = self._getImage(imagePath, internal = internal, scale = (32, 32))

		self.thing.AddNamedImages(label, image_16, image_32)

	def appendValue(self, newValue, where = -1, filterNone = None):
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

		elif (self.type.lower() == "listfull"):
			objectList = self._formatList(newValue, filterNone = filterNone)
			self.thing.AddObjects(objectList)

		else:
			warnings.warn(f"Add {self.type} to setSelection() for {self.__repr__()}", Warning, stacklevel = 2)

	#Change Settings
	def setFunction_preClick(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type.lower() == "listtree"):
			self._betterBind(wx.EVT_TREE_SEL_CHANGING, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		else:
			warnings.warn(f"Add {self.type} to setFunction_click() for {self.__repr__()}", Warning, stacklevel = 2)
			
	def setFunction_postClick(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type.lower() == "listdrop"):
			self._betterBind(wx.EVT_CHOICE, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		elif (self.type.lower() == "listfull"):
			# self._betterBind(wx.EVT_LIST_ITEM_SELECTED, self.thing, self.thing.onSelect, rebind = False)
			self._betterBind(wx.EVT_LIST_ITEM_SELECTED, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)

		elif (self.type.lower() == "listtree"):
			self._betterBind(wx.EVT_TREE_SEL_CHANGED, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		else:
			warnings.warn(f"Add {self.type} to setFunction_click() for {self.__repr__()}", Warning, stacklevel = 2)
			
	def setFunction_click(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		self.setFunction_postClick(myFunction = myFunction, myFunctionArgs = myFunctionArgs, myFunctionKwargs = myFunctionKwargs)

	def setFunction_preEdit(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type.lower() == "listfull"):
			if (self.subType.lower() == "normal"):
				self._betterBind(ObjectListView.ObjectListView.EVT_CELL_EDIT_STARTING, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
			else:
				self._betterBind(wx.EVT_LIST_BEGIN_LABEL_EDIT, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		elif (self.type.lower() == "listtree"):
			self._betterBind(wx.EVT_TREE_BEGIN_LABEL_EDIT, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		else:
			warnings.warn(f"Add {self.type} to setFunction_preEdit() for {self.__repr__()}", Warning, stacklevel = 2)
			
	def setFunction_postEdit(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type.lower() == "listfull"):
			if (self.subType.lower() == "normal"):
				self._betterBind(ObjectListView.ObjectListView.EVT_CELL_EDIT_FINISHING, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
			else:
				self._betterBind(wx.EVT_LIST_END_LABEL_EDIT, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		elif (self.type.lower() == "listtree"):
			self._betterBind(wx.EVT_TREE_END_LABEL_EDIT, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
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
			self._betterBind(wx.EVT_TREE_ITEM_COLLAPSING, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		else:
			warnings.warn(f"Add {self.type} to setFunction_preCollapse() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_postCollapse(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type.lower() == "listtree"):
			self._betterBind(wx.EVT_TREE_ITEM_COLLAPSED, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		else:
			warnings.warn(f"Add {self.type} to setFunction_postCollapse() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_preExpand(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type.lower() == "listtree"):
			self._betterBind(wx.EVT_TREE_ITEM_EXPANDING, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		else:
			warnings.warn(f"Add {self.type} to setFunction_preExpand() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_postExpand(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type.lower() == "listtree"):
			self._betterBind(wx.EVT_TREE_ITEM_EXPANDED, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		else:
			warnings.warn(f"Add {self.type} to setFunction_postExpand() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_rightClick(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type.lower() == "listtree"):
			self._betterBind(wx.EVT_TREE_ITEM_RIGHT_CLICK, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		elif (self.type.lower() == "listfull"):
			self._betterBind(wx.EVT_RIGHT_DOWN, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		else:
			warnings.warn(f"Add {self.type} to setFunction_rightClick() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_middleClick(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type.lower() == "listtree"):
			self._betterBind(wx.EVT_TREE_ITEM_MIDDLE_CLICK, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		else:
			warnings.warn(f"Add {self.type} to setFunction_middleClick() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_doubleClick(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type.lower() == "listtree"):
			self._betterBind(wx.EVT_TREE_ITEM_ACTIVATED, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		elif (self.type.lower() == "listfull"):
			self._betterBind(wx.EVT_LEFT_DCLICK, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
			# self._betterBind(wx.EVT_LIST_ITEM_ACTIVATED, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		else:
			warnings.warn(f"Add {self.type} to setFunction_middleClick() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_keyDown(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type.lower() == "listtree"):
			self._betterBind(wx.EVT_TREE_KEY_DOWN, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		else:
			warnings.warn(f"Add {self.type} to setFunction_keyDown() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_toolTip(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type.lower() == "listtree"):
			self._betterBind(wx.EVT_TREE_ITEM_GETTOOLTIP, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		else:
			warnings.warn(f"Add {self.type} to setFunction_toolTip() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_itemMenu(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type.lower() == "listtree"):
			self._betterBind(wx.EVT_TREE_ITEM_MENU, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
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
			colorHandle = self._getColor(color)
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

	class _ListFull(ObjectListView.ObjectListView):
		def __init__(self, parent, widget, myId = wx.ID_ANY, position = wx.DefaultPosition, size = wx.DefaultSize, style = "0", **kwargs):
			"""Creates the list control object."""
			
			#Load in modules
			ObjectListView.ObjectListView.__init__(self, widget, id = myId, pos = position, size = size, style = eval(style, {'__builtins__': None, "wx": wx}, {}), **kwargs)

			#Fix class type
			self.__name__ = "wxListCtrl"
			
			#Internal variables
			self.parent = parent

	class _ListFull_Editable(wx.ListCtrl, wx.lib.mixins.listctrl.TextEditMixin):
		"""Allows a list control to have editable text."""

		def __init__(self, parent, widget, myId = wx.ID_ANY, position = wx.DefaultPosition, size = wx.DefaultSize, style = "0", editable = {}, editOnClick = True):
			"""Creates the editable list object."""

			#Load in modules
			wx.ListCtrl.__init__(self, widget, id = myId, pos = position, size = size, style = eval(style, {'__builtins__': None, "wx": wx}, {}))
			wx.lib.mixins.listctrl.TextEditMixin.__init__(self)

			#Fix class type
			self.__name__ = "wxListCtrl"

			#Internal variables
			self.editable = editable
			self.parent = parent
			self.event = None

			#Open editor on double click only
			if (editOnClick == None):
				self.parent._betterBind(wx.EVT_LEFT_DOWN, self, self.parent.onDoNothing, rebind = None)
			elif (not editOnClick):
				self.Unbind(wx.EVT_LEFT_DOWN)

		def make_editor(self, *args, **kwargs):
			"""Overridden to make the colors standard again."""
			
			super(handle_WidgetList._ListFull_Editable, self).make_editor(*args, **kwargs)

			self.editor.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_LISTBOX))
			self.editor.SetForegroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_CAPTIONTEXT))

		def OpenEditor(self, column, row):
			"""Overridden to make only some cells editable and fix the item size."""

			leave = False
			#Check for non-editable column
			if (self.parent.cellTypeCatalogue[column][None].lower() != "inputbox"):
				leave = True
			elif ((column in self.editable) and (not self.editable[column])):
				leave = True
			
			if (leave):
				if (self.event != None):
					if (self.event.GetSkipped()):
						self.event.Skip()
				return

			#Run Function Normally
			super(handle_WidgetList._ListFull_Editable, self).OpenEditor(column, row)

			#Make the editor fit the cell
			y = self.GetItemRect(row)[3]
			x = self.editor.GetSize()[0]
			self.editor.SetSize(x, y)

		def OnLeftDown(self, event):
			"""Overridden to continue the event if the item is not editable."""

			self.event = event

			#Run Function Normally
			super(handle_WidgetList._ListFull_Editable, self).OnLeftDown(event)

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
			if (myFunction != None):
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

			password, readOnly, tab, wrap = self._getArguments(argument_catalogue, ["password", "readOnly", "tab", "wrap"])
			text, ipAddress, maxLength = self._getArguments(argument_catalogue, ["text", "ipAddress", "maxLength"])

			#Prepare style attributes
			style = ""
			if (password):
				style += "|wx.TE_PASSWORD"

			if (readOnly):
				style += "|wx.TE_READONLY"

			if (tab):
				style += "|wx.TE_PROCESS_TAB" #Interpret 'Tab' as 4 spaces

			if (wrap != None):
				if (wrap > 0):
					style += "|wx.TE_MULTILINE|wx.TE_WORDWRAP"
				else:
					style += "|wx.TE_CHARWRAP|wx.TE_MULTILINE"

			# if (enterFunction != None):
				#Interpret 'Enter' as \n
			#   style += "|wx.TE_PROCESS_ENTER"

			#style = "|wx.EXPAND"

			#Strip of extra divider
			if (style != ""):
				if (style[0] == "|"):
					style = style[1:]
			else:
				style = "wx.DEFAULT"

			#Account for empty text
			if (text == None):
				text = wx.EmptyString

			myId = self._getId(argument_catalogue)

			#Create the thing to put in the grid
			if (ipAddress):
				self.subType = "ipAddress"
				self.thing = wx.lib.masked.ipaddrctrl.IpAddrCtrl(self.parent.thing, id = myId, style = eval(style, {'__builtins__': None, "wx": wx}, {}))

				if (text != wx.EmptyString):
					self.thing.SetValue(text)
			else:
				self.subType = "normal"
				self.thing = wx.TextCtrl(self.parent.thing, id = myId, value = text, style = eval(style, {'__builtins__': None, "wx": wx}, {}))

				#Set maximum length
				if (maxLength != None):
					self.thing.SetMaxLength(maxLength)

			#flags += "|wx.RESERVE_SPACE_EVEN_IF_HIDDEN"

			#Bind the function(s)
			myFunction, enterFunction, postEditFunction, preEditFunction = self._getArguments(argument_catalogue, ["myFunction", "enterFunction", "postEditFunction", "preEditFunction"])
			
			#self._betterBind(wx.EVT_CHAR, self.thing, enterFunction, enterFunctionArgs, enterFunctionKwargs)
			#self._betterBind(wx.EVT_KEY_UP, self.thing, self.testFunction, myFunctionArgs, myFunctionKwargs)
			if (myFunction != None):
				myFunctionArgs, myFunctionKwargs = self._getArguments(argument_catalogue, ["myFunctionArgs", "myFunctionKwargs"])
				self.setFunction_click(myFunction, myFunctionArgs, myFunctionKwargs)

			if (enterFunction != None):
				enterFunctionArgs, enterFunctionKwargs = self._getArguments(argument_catalogue, ["enterFunctionArgs", "enterFunctionKwargs"])
				self.setFunction_enter(enterFunction, enterFunctionArgs, enterFunctionKwargs)
			
			if (postEditFunction != None):
				postEditFunctionArgs, postEditFunctionKwargs = self._getArguments(argument_catalogue, ["postEditFunctionArgs", "postEditFunctionKwargs"])
				self.setFunction_postEdit(postEditFunction, postEditFunctionArgs, postEditFunctionKwargs)
			
			if (preEditFunction != None):
				preEditFunctionArgs, preEditFunctionKwargs = self._getArguments(argument_catalogue, ["preEditFunctionArgs", "preEditFunctionKwargs"])
				self.setFunction_preEdit(preEditFunction, preEditFunctionArgs, preEditFunctionKwargs)

		def _build_inputSearch():
			"""Builds a wx search control object."""
			nonlocal self, argument_catalogue

			searchButton, cancelButton, tab, alignment = self._getArguments(argument_catalogue, ["searchButton", "cancelButton", "tab", "alignment"])
			menuLabel, menuFunction, menuReplaceText, hideSelection, = self._getArguments(argument_catalogue, ["menuLabel", "menuFunction", "menuReplaceText", "hideSelection"])
			myFunction, enterFunction, searchFunction, cancelFunction = self._getArguments(argument_catalogue, ["myFunction", "enterFunction", "searchFunction", "cancelFunction"])

			#Configure Settings
			style = "wx.TE_PROCESS_ENTER"

			if (tab):
				style += "|wx.TE_PROCESS_TAB" #Interpret 'Tab' as 4 spaces

			if (not hideSelection):
				style += "|wx.TE_NOHIDESEL"

			if (alignment != None):
				if (isinstance(alignment, bool)):
					if (alignment):
						style += "|wx.TE_LEFT"
					else:
						style += "|wx.TE_CENTRE"
				elif (alignment == 0):
					style += "|wx.TE_LEFT"
				elif (alignment == 1):
					style += "|wx.TE_RIGHT"
				else:
					style += "|wx.TE_CENTRE"
			else:
				style += "|wx.TE_CENTRE"


			myId = self._getId(argument_catalogue)

			#Create the thing to put in the grid
			self.thing = wx.SearchCtrl(self.parent.thing, id = myId, value = wx.EmptyString, style = eval(style, {'__builtins__': None, "wx": wx}, {}))

			#Create the menu associated with this widget
			self.myMenu = self._makeMenu(label = menuLabel)
			self.nest(self.myMenu)

			#Determine if additional features are enabled
			if (searchButton != None):
				self.thing.ShowSearchButton(True)
			
			if (cancelButton != None):
				self.thing.ShowCancelButton(True)

			#Bind the function(s)
			if (myFunction != None):
				myFunctionArgs, myFunctionKwargs = self._getArguments(argument_catalogue, ["myFunctionArgs", "myFunctionKwargs"])
				self.setFunction_click(myFunction, myFunctionArgs, myFunctionKwargs)

			if (enterFunction != None):
				enterFunctionArgs, enterFunctionKwargs = self._getArguments(argument_catalogue, ["enterFunctionArgs", "enterFunctionKwargs"])
				self.setFunction_enter(enterFunction, enterFunctionArgs, enterFunctionKwargs)

			if (searchFunction != None):
				searchFunctionArgs, searchFunctionKwargs = self._getArguments(argument_catalogue, ["searchFunctionArgs", "searchFunctionKwargs"])
				self.setFunction_search(searchFunction, searchFunctionArgs, searchFunctionKwargs)

			if (cancelFunction != None):
				cancelFunctionArgs, cancelFunctionKwargs = self._getArguments(argument_catalogue, ["cancelFunctionArgs", "cancelFunctionKwargs"])
				self.setFunction_cancel(cancelFunction, cancelFunctionArgs, cancelFunctionKwargs)

			if (menuFunction != None):
				menuFunctionArgs, menuFunctionKwargs = self._getArguments(argument_catalogue, ["menuFunctionArgs", "menuFunctionKwargs"])
				self.setFunction_menuSelect(menuFunction, menuFunctionArgs, menuFunctionKwargs)
			
			if (menuReplaceText):
				self.setFunction_menuSelect(self._onSearch_replaceText)

		def _build_inputSpinner():
			"""Builds a wx search control object."""
			nonlocal self, argument_catalogue

			useFloat, readOnly, increment, digits, size = self._getArguments(argument_catalogue, ["useFloat", "readOnly", "increment", "digits", "size"])
			myInitial, myMin, myMax, exclude = self._getArguments(argument_catalogue, ["myInitial", "myMin", "myMax", "exclude"])

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

				if (increment == None):
					increment = 0.1

				if (digits == None):
					digits = 1

				self.subType = "float"
				self.thing = wx.lib.agw.floatspin.FloatSpin(self.parent.thing, id = myId, pos = wx.DefaultPosition, size = size, style = wx.SP_ARROW_KEYS|wx.SP_WRAP, value = myInitial, min_val = myMin, max_val = myMax, increment = increment, digits = digits, agwStyle = eval(style, {'__builtins__': None, "wx": wx}, {}))
			else:
				if (increment != None):
					style = "wx.lib.agw.floatspin.FS_LEFT"
					self.subType = "float"
					self.thing = wx.lib.agw.floatspin.FloatSpin(self.parent.thing, id = myId, pos = wx.DefaultPosition, size = size, style = wx.SP_ARROW_KEYS|wx.SP_WRAP, value = myInitial, min_val = myMin, max_val = myMax, increment = increment, digits = -1, agwStyle = eval(style, {'__builtins__': None, "wx": wx}, {}))
					self.thing.SetDigits(0)
				else:
					self.subType = "normal"
					self.thing = wx.SpinCtrl(self.parent.thing, id = myId, value = wx.EmptyString, size = size, style = eval(style, {'__builtins__': None, "wx": wx}, {}), min = myMin, max = myMax, initial = myInitial)

				if (readOnly):
					self.thing.SetReadOnly()

			#Remember values
			self.previousValue = self.thing.GetValue()

			#Bind the function(s)
			myFunction, changeTextFunction = self._getArguments(argument_catalogue, ["myFunction", "changeTextFunction"])

			if (myFunction != None):
				myFunctionArgs, myFunctionKwargs = self._getArguments(argument_catalogue, ["myFunctionArgs", "myFunctionKwargs"])
				self.setFunction_click(myFunction, myFunctionArgs, myFunctionKwargs)
	
			# if (changeTextFunction != None):
			# 	if (isinstance(changeTextFunction, bool)):
			# 		if (changeTextFunction and (myFunction != None)):
			# 			self._betterBind(wx.EVT_TEXT, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
			# 	else:
			# 		changeTextFunctionArgs, changeTextFunctionKwargs = self._getArguments(argument_catalogue, ["changeTextFunctionArgs", "changeTextFunctionKwargs"])
			# 		self._betterBind(wx.EVT_TEXT, self.thing, changeTextFunction, changeTextFunctionArgs, changeTextFunctionKwargs)

			if (not ((self.exclude == None) or (isinstance(self.exclude, (list, tuple, range)) and (len(self.exclude) == 0)))):
				self._betterBind(wx.EVT_KILL_FOCUS, self.thing, self._onCheckValue_exclude)
		
		#########################################################

		self._preBuild(argument_catalogue)

		if (self.type.lower() == "inputbox"):
			_build_inputBox()
		elif (self.type.lower() == "inputspinner"):
			_build_inputSpinner()
		elif (self.type.lower() == "slider"):
			_build_slider()
		elif (self.type.lower() == "inputsearch"):
			_build_inputSearch()
		else:
			warnings.warn(f"Add {self.type} to _build() for {self.__repr__()}", Warning, stacklevel = 2)

		self._postBuild(argument_catalogue)

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
	def setValue(self, newValue = None, event = None, **kwargs):
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
			self._betterBind(wx.EVT_TEXT, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
			self._betterBind(wx.EVT_TEXT_ENTER, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)

		elif (self.type.lower() == "inputspinner"):
			self._betterBind(wx.EVT_TEXT, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
			# self._betterBind(wx.EVT_SPINCTRL, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)

		elif (self.type.lower() == "inputsearch"):
			self._betterBind(wx.EVT_TEXT, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
			self._betterBind(wx.EVT_TEXT_ENTER, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)

		else:
			warnings.warn(f"Add {self.type} to setFunction_click() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_enter(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type.lower() == "inputbox"):
			self.keyBind("enter", myFunction, myFunctionArgs, myFunctionKwargs)

		elif (self.type.lower() == "inputsearch"):
			self.keyBind("enter", myFunction, myFunctionArgs, myFunctionKwargs)
			# self._betterBind(wx.EVT_TEXT_ENTER, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)

		else:
			warnings.warn(f"Add {self.type} to setFunction_enter() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_preEdit(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type.lower() == "inputbox"):
			self._betterBind(wx.EVT_SET_FOCUS, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		else:
			warnings.warn(f"Add {self.type} to setFunction_preEdit() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_postEdit(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type.lower() == "inputbox"):
			self._betterBind(wx.EVT_KILL_FOCUS, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)

		elif (self.type.lower() == "inputspinner"):
			self._betterBind(wx.EVT_KILL_FOCUS, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)

			if (not ((self.exclude == None) or (isinstance(self.exclude, (list, tuple, range)) and (len(self.exclude) == 0)))):
				self._betterBind(wx.EVT_KILL_FOCUS, self.thing, self._onCheckValue_exclude, rebind = True)

		elif (self.type.lower() == "slider"):
			self._betterBind(wx.EVT_SCROLL_CHANGED, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)

		else:
			warnings.warn(f"Add {self.type} to setFunction_postEdit() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_search(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type.lower() == "inputsearch"):
			self._betterBind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		else:
			warnings.warn(f"Add {self.type} to setFunction_search() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_cancel(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type.lower() == "inputsearch"):
			self._betterBind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		else:
			warnings.warn(f"Add {self.type} to setFunction_cancel() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_menuSelect(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type.lower() == "inputsearch"):
			self._betterBind(wx.EVT_MENU, self.myMenu.thing, myFunction, myFunctionArgs, myFunctionKwargs, mode = 2)
		else:
			warnings.warn(f"Add {self.type} to setFunction_menuSelect() for {self.__repr__()}", Warning, stacklevel = 2)

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

	def _onCheckValue_exclude(self, event):
		"""Checks the current value to make sure the text is valid."""

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
			warnings.warn(f"Add {self.type} to _onCheckValue_exclude() for {self.__repr__()}", Warning, stacklevel = 2)

		event.Skip()

	def _onSearch_replaceText(self, event):
		"""Replaces the text in the input box with that of the popup menu."""

		if (self.type.lower() == "inputsearch"):
			value = self.myMenu.getText(event)
			self.setValue(value)
		else:
			warnings.warn(f"Add {self.type} to _onSearch_replaceText() for {self.__repr__()}", Warning, stacklevel = 2)

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

	def _build(self, argument_catalogue):
		"""Determiens which build system to use for this handle."""

		def _build_button():
			"""Builds a wx button object."""
			nonlocal self, argument_catalogue

			text, myFunction = self._getArguments(argument_catalogue, ["text", "myFunction"])

			myId = self._getId(argument_catalogue)

			#Create the thing to put in the grid
			self.thing = wx.Button(self.parent.thing, id = myId, label = text, style = 0)

			#Bind the function(s)
			if (myFunction != None):
				myFunctionArgs, myFunctionKwargs = self._getArguments(argument_catalogue, ["myFunctionArgs", "myFunctionKwargs"])
				self.setFunction_click(myFunction, myFunctionArgs, myFunctionKwargs)

		def _build_buttonToggle():
			"""Builds a wx toggle button object."""
			nonlocal self, argument_catalogue

			text, myFunction = self._getArguments(argument_catalogue, ["text", "myFunction"])

			myId = self._getId(argument_catalogue)

			#Create the thing to put in the grid
			self.thing = wx.ToggleButton(self.parent.thing, id = myId, label = text, style = 0)
			self.thing.SetValue(True) 

			#Bind the function(s)
			if (myFunction != None):
				myFunctionArgs, myFunctionKwargs = self._getArguments(argument_catalogue, ["myFunctionArgs", "myFunctionKwargs"])
				self.setFunction_click(myFunction, myFunctionArgs, myFunctionKwargs)

		def _build_buttonCheck():
			"""Builds a wx check box object."""
			nonlocal self, argument_catalogue

			text, default, myFunction = self._getArguments(argument_catalogue, ["text", "default", "myFunction"])

			myId = self._getId(argument_catalogue)

			#Create the thing to put in the grid
			self.thing = wx.CheckBox(self.parent.thing, id = myId, label = text, style = 0)

			#Determine if it is on by default
			self.thing.SetValue(default)

			#Bind the function(s)
			if (myFunction != None):
				myFunctionArgs, myFunctionKwargs = self._getArguments(argument_catalogue, ["myFunctionArgs", "myFunctionKwargs"])
				self.setFunction_click(myFunction, myFunctionArgs, myFunctionKwargs)

		def _build_checkList():
			"""Builds a wx check list box object."""
			nonlocal self, argument_catalogue

			choices, multiple, sort, myFunction = self._getArguments(argument_catalogue, ["choices", "multiple", "sort", "myFunction"])

			#Ensure that the choices given are a list or tuple
			if (not isinstance(choices, (list, tuple, range))):
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
			if (myFunction != None):
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
			self.thing = wx.RadioButton(self.parent.thing, id = myId, label = text, style = group)

			#Determine if it is turned on by default
			self.thing.SetValue(default)

			#Bind the function(s)
			if (myFunction != None):
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
			self.thing = wx.RadioBox(self.parent.thing, id = myId, label = title, choices = choices, majorDimension = maximum, style = direction)

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
				myFunctionArgs, myFunctionKwargs = self._getArguments(argument_catalogue, ["myFunctionArgs", "myFunctionKwargs"])
				self.setFunction_click(myFunction, myFunctionArgs, myFunctionKwargs)

		def _build_buttonImage():
			"""Builds a wx bitmap button object."""
			nonlocal self, argument_catalogue

			def _imageCheck(imagePath, internal, internalDefault):
				"""Determines what image to use."""
				nonlocal self 

				if ((imagePath != "") and (imagePath != None)):
					if ((((internal != None) and (not internal)) or ((internal == None) and (not internalDefault))) and (not os.path.exists(imagePath))):
						return self._getImage("error", internal = True)
					elif (internal != None):
						return self._getImage(imagePath, internal)
					return self._getImage(imagePath, internalDefault)
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
			if (image == None):
				image = self._getImage("error", internal = True)

			#Remember values
			self.toggle = toggle

			if (size == None):
				size = wx.DefaultSize

			myId = self._getId(argument_catalogue)

			#Create the thing to put in the grid
			if (text != None):
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
			if (image != None):
				self.thing.SetBitmapDisabled(image)

			image = _imageCheck(selectedPath, selected_internal, internal)
			if (image != None):
				self.thing.SetBitmapSelected(image)

			image = _imageCheck(focusPath, focus_internal, internal)
			if (image != None):
				self.thing.SetBitmapFocus(image)

			image = _imageCheck(hoverPath, hover_internal, internal)
			if (image != None):
				self.thing.SetBitmapHover(image)

			#Bind the function(s)
			if (myFunction != None):
				myFunctionArgs, myFunctionKwargs = self._getArguments(argument_catalogue, ["myFunctionArgs", "myFunctionKwargs"])
				self.setFunction_click(myFunction, myFunctionArgs, myFunctionKwargs)
		
		#########################################################

		self._preBuild(argument_catalogue)

		
		if (self.type.lower() == "button"):
			_build_button()
		elif (self.type.lower() == "buttoncheck"):
			_build_buttonCheck()
		elif (self.type.lower() == "buttonradio"):
			_build_buttonRadio()
		elif (self.type.lower() == "buttontoggle"):
			_build_buttonToggle()
		elif (self.type.lower() == "buttonradiobox"):
			_build_buttonRadioBox()
		elif (self.type.lower() == "checklist"):
			_build_checkList()
		elif (self.type.lower() == "buttonimage"):
			_build_buttonImage()
		elif (self.type.lower() == "buttonhelp"):
			_build_buttonHelp()
		else:
			warnings.warn(f"Add {self.type} to _build() for {self.__repr__()}", Warning, stacklevel = 2)

		self._postBuild(argument_catalogue)

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

		elif (self.type.lower() == "buttonimage"):
			if (self.toggle):
				value = self.thing.GetToggle() #(bool) - True: Selected; False: Un-Selected
			else:
				value = None

		else:
			warnings.warn(f"Add {self.type} to getValue() for {self.__repr__()}", Warning, stacklevel = 3)
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
			self._betterBind(wx.EVT_CHECKBOX, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		
		elif (self.type.lower() == "buttonradio"):
			self._betterBind(wx.EVT_RADIOBUTTON, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)

		elif (self.type.lower() == "buttonradiobox"):
			self._betterBind(wx.EVT_RADIOBOX, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		
		elif (self.type.lower() == "button"):
			self._betterBind(wx.EVT_BUTTON, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		
		elif (self.type.lower() == "buttonimage"):
			self._betterBind(wx.EVT_BUTTON, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		
		elif (self.type.lower() == "buttontoggle"):
			self._betterBind(wx.EVT_TOGGLEBUTTON, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		
		elif (self.type.lower() == "checklist"):
			self._betterBind(wx.EVT_CHECKLISTBOX, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)

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

	def _build(self, argument_catalogue):
		"""Determiens which build system to use for this handle."""

		def _build_pickerFile():
			"""Builds a wx file picker control or directory picker control object."""
			nonlocal self, argument_catalogue

			default, text, initialDir, myFunction = self._getArguments(argument_catalogue, ["default", "text", "initialDir", "myFunction"])
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
		
			#Create the thing to put in the grid
			if (directoryOnly):
				self.thing = wx.DirPickerCtrl(self.parent.thing, id = myId, path = default, message = text, style = eval(style, {'__builtins__': None, "wx": wx}, {}))
			else:
				self.thing = wx.FilePickerCtrl(self.parent.thing, id = myId, path = default, message = text, wildcard = initialDir, style = eval(style, {'__builtins__': None, "wx": wx}, {}))

			#Set Initial directory
			self.thing.SetInitialDirectory(initialDir)

			#Bind the function(s)
			if (myFunction != None):
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

			if (editLabelFunction != None):
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
			if (myFunction != None):
				myFunctionArgs, myFunctionKwargs = self._getArguments(argument_catalogue, ["myFunctionArgs", "myFunctionKwargs"])
				self.setFunction_click(myFunction, myFunctionArgs, myFunctionKwargs)

			if (editLabelFunction != None):
				editLabelFunctionArgs, editLabelFunctionKwargs = self._getArguments(argument_catalogue, ["editLabelFunctionArgs", "editLabelFunctionKwargs"])
				self.setFunction_editLabel(myFunction, myFunctionArgs, myFunctionKwargs)

			if (rightClickFunction != None):
				rightClickFunctionArgs, rightClickFunctionKwargs = self._getArguments(argument_catalogue, ["rightClickFunctionArgs", "rightClickFunctionKwargs"])
				self.setFunction_rightClick(myFunction, myFunctionArgs, myFunctionKwargs)

		def _build_pickerDate():
			"""Builds a wx  object."""
			nonlocal self, argument_catalogue

			date, dropDown, myFunction = self._getArguments(argument_catalogue, ["date", "dropDown", "myFunction"])

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
				style = wx.adv.DP_DROPDOWN
			else:
				style = wx.adv.DP_SPIN

			myId = self._getId(argument_catalogue)

			#Create the thing to put in the grid
			self.thing = wx.adv.DatePickerCtrl(self.parent.thing, id = myId, dt = date, style = style)

			#Bind the function(s)
			if (myFunction != None):
				myFunctionArgs, myFunctionKwargs = self._getArguments(argument_catalogue, ["myFunctionArgs", "myFunctionKwargs"])
				self.setFunction_click(myFunction, myFunctionArgs, myFunctionKwargs)

		def _build_pickerDateWindow():
			"""Builds a wx  object."""
			nonlocal self, argument_catalogue

			date, showHolidays, showOther = self._getArguments(argument_catalogue, ["date", "showHolidays", "showOther"])
			myFunction, dayFunction, monthFunction, yearFunction = self._getArguments(argument_catalogue, ["myFunction", "dayFunction", "monthFunction", "yearFunction"])

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
			if (myFunction != None):
				myFunctionArgs, myFunctionKwargs = self._getArguments(argument_catalogue, ["myFunctionArgs", "myFunctionKwargs"])
				self.setFunction_click(myFunction, myFunctionArgs, myFunctionKwargs)

			if (dayFunction != None):
				dayFunctionArgs, dayFunctionKwargs = self._getArguments(argument_catalogue, ["dayFunctionArgs", "dayFunctionKwargs"])
				self.setFunction_editDay(myFunction, myFunctionArgs, myFunctionKwargs)

			if (monthFunction != None):
				monthFunctionArgs, monthFunctionKwargs = self._getArguments(argument_catalogue, ["monthFunctionArgs", "monthFunctionKwargs"])
				self.setFunction_editMonth(myFunction, myFunctionArgs, myFunctionKwargs)

			if (yearFunction != None):
				yearFunctionArgs, yearFunctionKwargs = self._getArguments(argument_catalogue, ["yearFunctionArgs", "yearFunctionKwargs"])
				self.setFunction_editYear(myFunction, myFunctionArgs, myFunctionKwargs)

		def _build_pickerTime():
			"""Builds a wx time picker control object."""
			nonlocal self, argument_catalogue

			time, myFunction = self._getArguments(argument_catalogue, ["time", "myFunction"])

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

			myId = self._getId(argument_catalogue)

			#Create the thing to put in the grid
			self.thing = wx.adv.TimePickerCtrl(self.parent.thing, id = myId, dt = time)

			#Bind the function(s)
			if (myFunction != None):
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

			if (initial == None):
				initial = wx.BLACK
			else:
				initial = wx.BLACK

			myId = self._getId(argument_catalogue)
		
			#Create the thing to put in the grid
			self.thing = wx.ColourPickerCtrl(self.parent.thing, id = myId, colour = initial, style = eval(style, {'__builtins__': None, "wx": wx}, {}))

			#Bind the function(s)
			if (myFunction != None):
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

			# font = self._getFont()
			font = wx.NullFont

			myId = self._getId(argument_catalogue)
		
			#Create the thing to put in the grid
			self.thing = wx.FontPickerCtrl(self.parent.thing, id = myId, font = font, style = eval(style, {'__builtins__': None, "wx": wx}, {}))
			
			self.thing.SetMaxPointSize(maxFontSize) 

			#Bind the function(s)
			if (myFunction != None):
				myFunctionArgs, myFunctionKwargs = self._getArguments(argument_catalogue, ["myFunctionArgs", "myFunctionKwargs"])
				self.setFunction_click(myFunction, myFunctionArgs, myFunctionKwargs)
		
		#########################################################

		self._preBuild(argument_catalogue)

		if (self.type.lower() == "pickerfile"):
			_build_pickerFile()
		elif (self.type.lower() == "pickerfilewindow"):
			_build_pickerFileWindow()
		elif (self.type.lower() == "pickerdate"):
			_build_pickerDate()
		elif (self.type.lower() == "pickerdatewindow"):
			_build_pickerDateWindow()
		elif (self.type.lower() == "pickertime"):
			_build_pickerTime()
		elif (self.type.lower() == "pickercolor"):
			_build_pickerColor()
		elif (self.type.lower() == "pickerfont"):
			_build_pickerFont()
		else:
			warnings.warn(f"Add {self.type} to _build() for {self.__repr__()}", Warning, stacklevel = 2)

		self._postBuild(argument_catalogue)

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
				self._betterBind(wx.EVT_DIRPICKER_CHANGED, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
			else:
				self._betterBind(wx.EVT_FILEPICKER_CHANGED, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		elif (self.type.lower() == "pickerfilewindow"):
			self._betterBind(wx.EVT_TREE_SEL_CHANGED, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		elif (self.type.lower() == "pickertime"):
			self._betterBind(wx.adv.EVT_TIME_CHANGED, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		elif (self.type.lower() == "pickerdate"):
			self._betterBind(wx.adv.EVT_DATE_CHANGED, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		elif (self.type.lower() == "pickerdatewindow"):
			self._betterBind(wx.adv.EVT_CALENDAR_SEL_CHANGED, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		elif (self.type.lower() == "pickercolor"):
			self._betterBind(wx.EVT_COLOURPICKER_CHANGED, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		elif (self.type.lower() == "pickerfont"):
			self._betterBind(wx.EVT_FONTPICKER_CHANGED, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		else:
			warnings.warn(f"Add {self.type} to setFunction_click() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_editLabel(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		"""Changes the function that runs when a label is modified."""
		
		if (self.type.lower() == "pickerfilewindow"):
			self._betterBind(wx.EVT_TREE_END_LABEL_EDIT, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		else:
			warnings.warn(f"Add {self.type} to setFunction_editLabel() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_rightClick(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		"""Changes the function that runs when the right mouse button is clicked in the widget."""
		
		if (self.type.lower() == "pickerfilewindow"):
			self._betterBind(wx.EVT_TREE_ITEM_RIGHT_CLICK, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		else:
			warnings.warn(f"Add {self.type} to setFunction_rightClick() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_editDay(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		"""Changes the function that runs when the day is modified."""
		
		if (self.type.lower() == "pickerdatewindow"):
			self._betterBind(wx.adv.EVT_CALENDAR_DAY, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		else:
			warnings.warn(f"Add {self.type} to setFunction_editDay() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_editMonth(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		"""Changes the function that runs when the month is modified."""
		
		if (self.type.lower() == "pickerdatewindow"):
			self._betterBind(wx.adv.EVT_CALENDAR_MONTH, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		else:
			warnings.warn(f"Add {self.type} to setFunction_editMonth() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_editYear(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		"""Changes the function that runs when the year is modified."""
		
		if (self.type.lower() == "pickerdatewindow"):
			self._betterBind(wx.adv.EVT_CALENDAR_YEAR, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
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

	def _build(self, argument_catalogue):
		"""Determiens which build system to use for this handle."""

		def _build_image():
			"""Builds a wx static bitmap object."""
			nonlocal self, argument_catalogue

			imagePath, internal, size = self._getArguments(argument_catalogue, ["imagePath", "internal", "size"])

			#Get correct image
			image = self._getImage(imagePath, internal)

			myId = self._getId(argument_catalogue)
		
			#Create the thing to put in the grid
			self.thing = wx.StaticBitmap(self.parent.thing, id = myId, bitmap = image, size = size, style = 0) #style = wx.SUNKEN_BORDER)
		
		#########################################################

		self._preBuild(argument_catalogue)

		if (self.type.lower() == "image"):
			_build_image()
		else:
			warnings.warn(f"Add {self.type} to _build() for {self.__repr__()}", Warning, stacklevel = 2)

		self._postBuild(argument_catalogue)

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
			image = self._getImage(newValue)
			self.thing.SetBitmap(image) #(wxBitmap) - What the image will be now

		else:
			warnings.warn(f"Add {self.type} to setValue() for {self.__repr__()}", Warning, stacklevel = 2)

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

		def _build_toolbar():
			"""Builds a wx toolbar control object."""
			nonlocal self, argument_catalogue

			vertical, detachable, flat, align, top = self._getArguments(argument_catalogue, ["vertical", "detachable", "flat", "align", "top"])
			showIcon, showDivider, showToolTip, showText = self._getArguments(argument_catalogue, ["showIcon", "showDivider", "showToolTip", "showText"])
			vertical_text, myFunction = self._getArguments(argument_catalogue, ["vertical_text", "myFunction"])

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
				style += "|wx.TB_NOICONS"
			if (not showDivider):
				style += "|wx.TB_NODIVIDER"
			if (not showToolTip):
				style += "|wx.TB_NO_TOOLTIPS"
			if (showText):
				style += "|wx.TB_TEXT"
				if (vertical_text):
					style += "|wx.TB_HORZ_LAYOUT"
			
			self.thing = wx.ToolBar(self.parent.thing, style = eval(style, {'__builtins__': None, "wx": wx}, {}))
			self.thing.Realize()

			#Bind the function(s)
			if (myFunction != None):
				myFunctionArgs, myFunctionKwargs = self._getArguments(argument_catalogue, ["myFunctionArgs", "myFunctionKwargs"])
				self.setFunction_click(myFunction, myFunctionArgs, myFunctionKwargs)
		
		#########################################################

		self._preBuild(argument_catalogue)

		if (self.type.lower() == "menu"):
			_build_menu()
		elif (self.type.lower() == "toolbar"):
			_build_toolbar()
		else:
			warnings.warn(f"Add {self.type} to _build() for {self.__repr__()}", Warning, stacklevel = 2)

		self._postBuild(argument_catalogue)

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

	def getText(self, event = None):
		"""Returns what the contextual text is for the object associated with this handle."""

		if (self.type.lower() == "menu"):
			#Get menu item
			if (event == None):
				errorMessage = "Pass the event parameter to getValue() when working with menu items"
				raise SyntaxError(errorMessage)
			
			index = event.GetId()
			item = self.thing.FindItemById(index)

			#Act on menu item
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
			self._betterBind(wx.EVT_TOOL_RCLICKED, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		else:
			warnings.warn(f"Add {self.type} to setFunction_click() for {self.__repr__()}", Warning, stacklevel = 2)

	def setEnable(self, label = None, state = True):
		"""Enables or disables an item based on the given input.

		state (bool) - If it is enabled or not

		Example Input: setEnable()
		Example Input: setEnable(False)
		"""

		if (self.type.lower() == "toolbar"):
			if (label == None):
				label = self[:]
			elif (not isinstance(label, (list, tuple, range))):
				label = [label]

			for item in label:
				with self[item] as myWidget:
					#Account for no wx.App.MainLoop yet
					if ((wx.EventLoop.GetActive() == None) and (not self.controller.finishing)):
						#Queue the current state to apply later; setting the enable twice before wx.App.MainLoop starts will cause the code to freeze
						self.myWindow._addFinalFunction(self.setEnable, myFunctionKwargs = {"label": myWidget, "state": state}, label = (myWidget, self.setEnable))
						continue

					myId = myWidget.thing.GetId()
					self.thing.EnableTool(myId, state) 
		else:
			warnings.warn(f"Add {self.type} to setEnable() for {self.__repr__()}", Warning, stacklevel = 2)

	def checkEnabled(self, label = None):
		"""Checks if an item is enabled.

		Example Input: checkEnabled()
		"""

		if (self.type.lower() == "toolbar"):
			if (label == None):
				label = self[:]
			elif (not isinstance(label, (list, tuple, range))):
				label = [label]

			answer = []
			for item in label:
				with self[item] as myWidget:
					#Account for no wx.App.MainLoop yet
					if ((wx.EventLoop.GetActive() == None) and (not self.controller.finishing) and ((myWidget, self.setEnable) in self.finalFunctionCatalogue)):
						answer.append(self.finalFunctionCatalogue[(myWidget, self.setEnable)][2]["state"])
						continue

					myId = myWidget.thing.GetId()
					answer.append(self.thing.GetToolEnabled(myId, state))
		else:
			warnings.warn(f"Add {self.type} to checkEnabled() for {self.__repr__()}", Warning, stacklevel = 2)
			answer = None

		return answer
		
	def setShow(self, label = None, state = True):
		"""Shows or hides an item based on the given input.

		state (bool) - If it is shown or not

		Example Input: setShow()
		Example Input: setShow(False)
		"""

		if (self.type.lower() == "toolbar"):
			if (label == None):
				label = self[:]
			elif (not isinstance(label, (list, tuple, range))):
				label = [label]

			for item in label:
				with self[item] as myWidget:
					myId = myWidget.thing.GetId()

					if (state):
						if (not myWidget.checkShown()):
							self.thing.AddTool(myWidget.thing)
							self.thing.Realize()
							myWidget.shown = True
					else:
						if (myWidget.checkShown()):
							self.thing.RemoveTool(myId)
							myWidget.shown = False
		else:
			warnings.warn(f"Add {self.type} to setShow() for {self.__repr__()}", Warning, stacklevel = 2)

	def checkShown(self, label = None):
		"""Checks if an item is shown.

		Example Input: checkShown()
		"""

		if (self.type.lower() == "toolbar"):
			if (label == None):
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
			warnings.warn(f"Add {self.type} to checkShown() for {self.__repr__()}", Warning, stacklevel = 2)
			state = None

		return state

	#Add things
	def addItem(self, text = "", icon = None, internal = False, disabled_icon = None, disabled_internal = None,
		special = None, check = None, default = False, stretchable = None,

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, 

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None, flex = 0, flags = "c1"):
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
		if (self.type.lower() == "menu"):
			handle.type = "MenuItem"
		elif (self.type.lower() == "toolbar"):
			handle.type = "ToolBarItem"
		else:
			warnings.warn(f"Add {self.type} to addItem() for {self.__repr__()}", Warning, stacklevel = 2)
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

		if (self.type.lower() == "toolbar"):
			handle = self.addItem(*args, text = None, stretchable = True, **kwargs)
		else:
			warnings.warn(f"Add {self.type} to addStretchableSpace() for {self.__repr__()}", Warning, stacklevel = 2)
			handle = None

		return handle

	def addSub(self, text = "", flex = 0, flags = "c1", 

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None):
		"""Adds a sub menu to a specific pre-existing menu.
		To adding items to a sub menu is the same as for menus.

		text (str)  - The text for the menu item. This is what is shown to the user
		label (int) - The label for this menu

		Example Input: addSub()
		Example Input: addSub(text = "I&mport")
		"""

		handle = handle_Menu()
		if (self.type.lower() == "menu"):
			handle.type = "Menu"
		elif (self.type.lower() == "toolbar"):
			handle.type = "ToolBar"
		else:
			warnings.warn(f"Add {self.type} to addSub() for {self.__repr__()}", Warning, stacklevel = 2)
			return

		detachable = False
		handle._build(locals())

		return handle

	def addText(self, *args, hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None, flex = 0, flags = "c1", **kwargs):
		"""Adds a text widget to the tool bar."""

		if (self.type.lower() == "toolbar"):
			handle = handle_MenuItem()
			handle.type = "ToolBarItem"
			handle.subHandle = [handle._makeText, args, kwargs]
			handle._build(locals())
		else:
			warnings.warn(f"Add {self.type} to addText() for {self.__repr__()}", Warning, stacklevel = 2)
			return

		return handle

	def addEmpty(self, *args, **kwargs):
		"""Alias function for addStretchableSpace()."""

		return self.addStretchableSpace(*args, **kwargs)

	def addHyperlink(self, *args, hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None, flex = 0, flags = "c1", **kwargs):
		"""Adds a hyperlink widget to the tool bar."""

		if (self.type.lower() == "toolbar"):
			handle = handle_MenuItem()
			handle.type = "ToolBarItem"
			handle.subHandle = [handle._makeHyperlink, args, kwargs]
			handle._build(locals())
		else:
			warnings.warn(f"Add {self.type} to addHyperlink() for {self.__repr__()}", Warning, stacklevel = 2)
			handle = None

		return handle

	def addLine(self, *args, hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None, flex = 0, flags = "c1", **kwargs):
		"""Adds a line widget to the tool bar."""

		if (self.type.lower() == "toolbar"):
			handle = handle_MenuItem()
			handle.type = "ToolBarItem"
			handle.subHandle = [handle._makeLine, args, kwargs]
			handle._build(locals())
		else:
			warnings.warn(f"Add {self.type} to addLine() for {self.__repr__()}", Warning, stacklevel = 2)
			handle = None

		return handle

	def addListDrop(self, *args, hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None, flex = 0, flags = "c1", **kwargs):
		"""Adds a drop list widget to the tool bar."""

		if (self.type.lower() == "toolbar"):
			handle = handle_MenuItem()
			handle.type = "ToolBarItem"
			handle.subHandle = [handle._makeListDrop, args, kwargs]
			handle._build(locals())
		else:
			warnings.warn(f"Add {self.type} to addListDrop() for {self.__repr__()}", Warning, stacklevel = 2)
			handle = None

		return handle

	def addListFull(self, *args, hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None, flex = 0, flags = "c1", **kwargs):
		"""Adds a full list widget to the tool bar."""

		if (self.type.lower() == "toolbar"):
			handle = handle_MenuItem()
			handle.type = "ToolBarItem"
			handle.subHandle = [handle._makeListFull, args, kwargs]
			handle._build(locals())
		else:
			warnings.warn(f"Add {self.type} to addListFull() for {self.__repr__()}", Warning, stacklevel = 2)
			handle = None

		return handle

	def addListTree(self, *args, hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None, flex = 0, flags = "c1", **kwargs):
		"""Adds a full list widget to the tool bar."""

		if (self.type.lower() == "toolbar"):
			handle = handle_MenuItem()
			handle.type = "ToolBarItem"
			handle.subHandle = [handle._makeListTree, args, kwargs]
			handle._build(locals())
		else:
			warnings.warn(f"Add {self.type} to addListTree() for {self.__repr__()}", Warning, stacklevel = 2)
			handle = None

		return handle

	def addInputSlider(self, *args, hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None, flex = 0, flags = "c1", **kwargs):
		"""Adds an input slider widget to the tool bar."""

		if (self.type.lower() == "toolbar"):
			handle = handle_MenuItem()
			handle.type = "ToolBarItem"
			handle.subHandle = [handle._makeInputSlider, args, kwargs]
			handle._build(locals())
		else:
			warnings.warn(f"Add {self.type} to addInputSlider() for {self.__repr__()}", Warning, stacklevel = 2)
			handle = None

		return handle

	def addInputBox(self, *args, hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None, flex = 0, flags = "c1", **kwargs):
		"""Adds an input box widget to the tool bar."""

		if (self.type.lower() == "toolbar"):
			handle = handle_MenuItem()
			handle.type = "ToolBarItem"
			handle.subHandle = [handle._makeInputBox, args, kwargs]
			handle._build(locals())
		else:
			warnings.warn(f"Add {self.type} to addInputBox() for {self.__repr__()}", Warning, stacklevel = 2)
			handle = None

		return handle

	def addInputSearch(self, *args, hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None, flex = 0, flags = "c1", **kwargs):
		"""Adds a search box widget to the tool bar."""

		if (self.type.lower() == "toolbar"):
			handle = handle_MenuItem()
			handle.type = "ToolBarItem"
			handle.subHandle = [handle._makeInputSearch, args, kwargs]
			handle._build(locals())
		else:
			warnings.warn(f"Add {self.type} to addInputSearch() for {self.__repr__()}", Warning, stacklevel = 2)
			handle = None

		return handle

	def addInputSpinner(self, *args, hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None, flex = 0, flags = "c1", **kwargs):
		"""Adds an input spinner widget to the tool bar."""

		if (self.type.lower() == "toolbar"):
			handle = handle_MenuItem()
			handle.type = "ToolBarItem"
			handle.subHandle = [handle._makeInputSpinner, args, kwargs]
			handle._build(locals())
		else:
			warnings.warn(f"Add {self.type} to addInputSpinner() for {self.__repr__()}", Warning, stacklevel = 2)
			handle = None

		return handle

	def addButton(self, *args, hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None, flex = 0, flags = "c1", **kwargs):
		"""Adds a button widget to the tool bar."""

		if (self.type.lower() == "toolbar"):
			handle = handle_MenuItem()
			handle.type = "ToolBarItem"
			handle.subHandle = [handle._makeButton, args, kwargs]
			handle._build(locals())
		else:
			warnings.warn(f"Add {self.type} to addButton() for {self.__repr__()}", Warning, stacklevel = 2)
			handle = None

		return handle

	def addButtonToggle(self, *args, hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None, flex = 0, flags = "c1", **kwargs):
		"""Adds a toggle button widget to the tool bar."""

		if (self.type.lower() == "toolbar"):
			handle = handle_MenuItem()
			handle.type = "ToolBarItem"
			handle.subHandle = [handle._makeButtonToggle, args, kwargs]
			handle._build(locals())
		else:
			warnings.warn(f"Add {self.type} to addButtonToggle() for {self.__repr__()}", Warning, stacklevel = 2)
			handle = None

		return handle

	def addButtonCheck(self, *args, hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None, flex = 0, flags = "c1", **kwargs):
		"""Adds a check button widget to the tool bar."""

		if (self.type.lower() == "toolbar"):
			handle = handle_MenuItem()
			handle.type = "ToolBarItem"
			handle.subHandle = [handle._makeButtonCheck, args, kwargs]
			handle._build(locals())
		else:
			warnings.warn(f"Add {self.type} to addButtonCheck() for {self.__repr__()}", Warning, stacklevel = 2)
			handle = None

		return handle

	def addButtonCheckList(self, *args, hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None, flex = 0, flags = "c1", **kwargs):
		"""Adds a check list widget to the tool bar."""

		if (self.type.lower() == "toolbar"):
			handle = handle_MenuItem()
			handle.type = "ToolBarItem"
			handle.subHandle = [handle._makeButtonCheckList, args, kwargs]
			handle._build(locals())
		else:
			warnings.warn(f"Add {self.type} to addButtonCheckList() for {self.__repr__()}", Warning, stacklevel = 2)
			handle = None

		return handle

	def addButtonRadio(self, *args, hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None, flex = 0, flags = "c1", **kwargs):
		"""Adds a radio button widget to the tool bar."""

		if (self.type.lower() == "toolbar"):
			handle = handle_MenuItem()
			handle.type = "ToolBarItem"
			handle.subHandle = [handle._makeButtonRadio, args, kwargs]
			handle._build(locals())
		else:
			warnings.warn(f"Add {self.type} to addButtonRadio() for {self.__repr__()}", Warning, stacklevel = 2)
			handle = None

		return handle

	def addButtonRadioBox(self, *args, hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None, flex = 0, flags = "c1", **kwargs):
		"""Adds a radio button box widget to the tool bar."""

		if (self.type.lower() == "toolbar"):
			handle = handle_MenuItem()
			handle.type = "ToolBarItem"
			handle.subHandle = [handle._makeButtonRadioBox, args, kwargs]
			handle._build(locals())
		else:
			warnings.warn(f"Add {self.type} to addButtonRadioBox() for {self.__repr__()}", Warning, stacklevel = 2)
			handle = None

		return handle

	def addButtonImage(self, *args, hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None, flex = 0, flags = "c1", **kwargs):
		"""Adds an image button widget to the tool bar."""

		if (self.type.lower() == "toolbar"):
			handle = handle_MenuItem()
			handle.type = "ToolBarItem"
			handle.subHandle = [handle._makeButtonImage, args, kwargs]
			handle._build(locals())
		else:
			warnings.warn(f"Add {self.type} to addButtonImage() for {self.__repr__()}", Warning, stacklevel = 2)
			handle = None

		return handle

	def addImage(self, *args, hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None, flex = 0, flags = "c1", **kwargs):
		"""Adds an image widget to the tool bar."""

		if (self.type.lower() == "toolbar"):
			handle = handle_MenuItem()
			handle.type = "ToolBarItem"
			handle.subHandle = [handle._makeImage, args, kwargs]
			handle._build(locals())
		else:
			warnings.warn(f"Add {self.type} to addImage() for {self.__repr__()}", Warning, stacklevel = 2)
			handle = None

		return handle

	def addProgressBar(self, *args, hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None, flex = 0, flags = "c1", **kwargs):
		"""Adds a progress bar widget to the tool bar."""

		if (self.type.lower() == "toolbar"):
			handle = handle_MenuItem()
			handle.type = "ToolBarItem"
			handle.subHandle = [handle._makeProgressBar, args, kwargs]
			handle._build(locals())
		else:
			warnings.warn(f"Add {self.type} to addProgressBar() for {self.__repr__()}", Warning, stacklevel = 2)
			handle = None

		return handle

	def addPickerColor(self, *args, hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None, flex = 0, flags = "c1", **kwargs):
		"""Adds a color picker widget to the tool bar."""

		if (self.type.lower() == "toolbar"):
			handle = handle_MenuItem()
			handle.type = "ToolBarItem"
			handle.subHandle = [handle._makePickerColor, args, kwargs]
			handle._build(locals())
		else:
			warnings.warn(f"Add {self.type} to addPickerColor() for {self.__repr__()}", Warning, stacklevel = 2)
			handle = None

		return handle

	def addPickerFont(self, *args, hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None, flex = 0, flags = "c1", **kwargs):
		"""Adds a font picker widget to the tool bar."""

		if (self.type.lower() == "toolbar"):
			handle = handle_MenuItem()
			handle.type = "ToolBarItem"
			handle.subHandle = [handle._makePickerFont, args, kwargs]
			handle._build(locals())
		else:
			warnings.warn(f"Add {self.type} to addPickerFont() for {self.__repr__()}", Warning, stacklevel = 2)
			handle = None

		return handle

	def addPickerFile(self, *args, hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None, flex = 0, flags = "c1", **kwargs):
		"""Adds a file picker widget to the tool bar."""

		if (self.type.lower() == "toolbar"):
			handle = handle_MenuItem()
			handle.type = "ToolBarItem"
			handle.subHandle = [handle._makePickerFile, args, kwargs]
			handle._build(locals())
		else:
			warnings.warn(f"Add {self.type} to addPickerFile() for {self.__repr__()}", Warning, stacklevel = 2)
			handle = None

		return handle

	def addPickerFileWindow(self, *args, hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None, flex = 0, flags = "c1", **kwargs):
		"""Adds a file window picker widget to the tool bar."""

		if (self.type.lower() == "toolbar"):
			handle = handle_MenuItem()
			handle.type = "ToolBarItem"
			handle.subHandle = [handle._makePickerFileWindow, args, kwargs]
			handle._build(locals())
		else:
			warnings.warn(f"Add {self.type} to addPickerFileWindow() for {self.__repr__()}", Warning, stacklevel = 2)
			handle = None

		return handle

	def addPickerTime(self, *args, hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None, flex = 0, flags = "c1", **kwargs):
		"""Adds a time picker widget to the tool bar."""

		if (self.type.lower() == "toolbar"):
			handle = handle_MenuItem()
			handle.type = "ToolBarItem"
			handle.subHandle = [handle._makePickerTime, args, kwargs]
			handle._build(locals())
		else:
			warnings.warn(f"Add {self.type} to addPickerTime() for {self.__repr__()}", Warning, stacklevel = 2)
			handle = None

		return handle

	def addPickerDate(self, *args, hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None, flex = 0, flags = "c1", **kwargs):
		"""Adds a date picker widget to the tool bar."""

		if (self.type.lower() == "toolbar"):
			handle = handle_MenuItem()
			handle.type = "ToolBarItem"
			handle.subHandle = [handle._makePickerDate, args, kwargs]
			handle._build(locals())
		else:
			warnings.warn(f"Add {self.type} to addPickerDate() for {self.__repr__()}", Warning, stacklevel = 2)
			handle = None

		return handle

	def addPickerDateWindow(self, *args, hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None, flex = 0, flags = "c1", **kwargs):
		"""Adds a text date window picker to the tool bar."""

		if (self.type.lower() == "toolbar"):
			handle = handle_MenuItem()
			handle.type = "ToolBarItem"
			handle.subHandle = [handle._makePickerDateWindow, args, kwargs]
			handle._build(locals())
		else:
			warnings.warn(f"Add {self.type} to addPickerDateWindow() for {self.__repr__()}", Warning, stacklevel = 2)
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

		if (self.type.lower() == "menuitem"):
			value = len(self.thing.GetLabel()) #(int) - How long the text inside the menu item is

		else:
			warnings.warn(f"Add {self.type} to __len__() for {self.__repr__()}", Warning, stacklevel = 2)
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
			if (text == None):
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
				if (check == None):
					self.subType = "normal"
					self.thing = wx.MenuItem(self.parent.thing, myId, text)

					#Determine icon
					icon, internal = self._getArguments(argument_catalogue, ["icon", "internal"])
					if (icon != None):
						image = self._getImage(icon, internal)
						image = self._convertBitmapToImage(image)
						image = image.Scale(16, 16, wx.IMAGE_QUALITY_HIGH)
						image = self._convertImageToBitmap(image)
						self.thing.SetBitmap(image)
				else:
					if (check):
						self.subType = "check"
						self.thing = wx.MenuItem(self.parent.thing, myId, text, kind = wx.ITEM_CHECK)
					else:
						self.subType = "radio"
						self.thing = wx.MenuItem(self.parent.thing, myId, text, kind = wx.ITEM_RADIO)

				#Determine initial value
				if (check != None):
					if (default):
						self.thing.Check(True)

				#Determine how to do the bound function
				if (myFunction == None):
					if (special != None):
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

			#Determine visibility
			if (hidden):
				if (isinstance(buildSelf, handle_Sizer)):
					buildSelf._addFinalFunction(buildSelf.thing.ShowItems, False)
				else:
					self.thing.Hide()

		def _build_toolbarItem():
			"""Builds a wx tool control object."""
			nonlocal self, argument_catalogue

			if (self.subHandle != None):
				myFunction, myFunctionArgs, myFunctionKwargs = self.subHandle
				self.subHandle = myFunction(*myFunctionArgs, **myFunctionKwargs)
				self.subType = self.subHandle.type
				self.thing = self.parent.thing.AddControl(self.subHandle.thing)
			else:
				text = self._getArguments(argument_catalogue, ["text"])
				if (text == None):
					stretchable = self._getArguments(argument_catalogue, ["stretchable"])
					if (stretchable):
						self.subType = "stretchable"
						self.thing = self.parent.thing.AddStretchableSpace()
					else:
						self.subType = "separator"
						self.thing = self.parent.thing.AddSeparator()
				else:
					icon, internal = self._getArguments(argument_catalogue, ["icon", "internal"])
					disabled_icon, disabled_internal = self._getArguments(argument_catalogue, ["disabled_icon", "disabled_internal"])
					check, default, myFunction, special = self._getArguments(argument_catalogue, ["check", "default", "myFunction", "special"])
					
					#Get Images
					if (icon == None):
						warnings.warn(f"No icon provided for {self.__repr__()}", Warning, stacklevel = 5)
						icon = "error"
						internal = True
					image = self._getImage(icon, internal)

					if (disabled_icon == None):
						imageDisabled = wx.NullBitmap
					else:
						if (disabled_internal == None):
							disabled_internal = internal
						imageDisabled = self._getImage(disabled_icon, disabled_internal)

					#Configure Settings
					# if (toolTip == None):
					# 	toolTip = ""
					# elif (not isinstance(toolTip, str)):
					# 	toolTip = f"{toolTip}"

					if (check == None):
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
					
					if (myFunction == None):
						if (special != None):
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

		if (self.type.lower() == "menuitem"):
			_build_menuItem()
		elif (self.type.lower() == "toolbaritem"):
			_build_toolbarItem()
		else:
			warnings.warn(f"Add {self.type} to _build() for {self.__repr__()}", Warning, stacklevel = 2)

		self._postBuild(argument_catalogue)

	def getValue(self, event = None):
		"""Returns what the contextual value is for the object associated with this handle."""

		if (self.type.lower() == "menuitem"):
			if (self.thing.IsCheckable()):
				value = self.thing.IsChecked() #(bool) - True: Selected; False: Un-Selected
			else:
				value = self.thing.GetText() #(str) - What the selected item says
				
		elif ((self.type.lower() == "toolbaritem") and (self.subHandle != None)):
			value = self.subHandle.getValue(event = event)
			
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
				
		elif ((self.type.lower() == "toolbaritem") and (self.subHandle != None)):
			value = self.subHandle.setValue(event = event)

		else:
			warnings.warn(f"Add {self.type} to getIndex() for {self.__repr__()}", Warning, stacklevel = 2)
			value = None

		return value

	#Setters
	def setValue(self, newValue, event = None):
		"""Sets the contextual value for the object associated with this handle to what the user supplies."""

		if (self.type.lower() == "menuitem"):
			if ((self.thing.GetKind() == wx.ITEM_CHECK) or (self.thing.GetKind() == wx.ITEM_RADIO)):
				if (isinstance(newValue, str)):
					newValue = ast.literal_eval(re.sub("^['\"]|['\"]$", "", newValue))
				self.thing.Check(newValue) #(bool) - True: selected; False: un-selected
			else:
				errorMessage = f"Only a menu 'Check Box' or 'Radio Button' can be set to a different value for setValue() for {self.__repr__()}"
				raise SyntaxError(errorMessage)

		elif ((self.type.lower() == "toolbaritem") and (self.subHandle != None)):
			self.subHandle.setValue(newValue, event = event)

		else:
			warnings.warn(f"Add {self.type} to setValue() for {self.__repr__()}", Warning, stacklevel = 2)

	#Change Settings
	def setFunction_click(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, **kwargs):
		"""Changes the function that runs when a menu item is selected."""

		if (self.type.lower() == "menuitem"):
			self.parent._betterBind(wx.EVT_MENU, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		
		elif (self.type.lower() == "toolbaritem"):
			if (self.subHandle != None):
				self.subHandle.setFunction_click(myFunction = myFunction, myFunctionArgs = myFunctionArgs, myFunctionKwargs = myFunctionKwargs, **kwargs)
			else:
				self.parent._betterBind(wx.EVT_MENU, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		
		else:
			warnings.warn(f"Add {self.type} to setFunction_enter() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_enter(self, *args, **kwargs):
		"""Override function for subHandle."""

		if ((self.type.lower() == "toolbaritem") and (self.subHandle != None)):
			self.subHandle.setFunction_enter(*args, **kwargs)
		else:
			warnings.warn(f"Add {self.type} to setFunction_enter() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_preEdit(self, *args, **kwargs):
		"""Override function for subHandle."""

		if ((self.type.lower() == "toolbaritem") and (self.subHandle != None)):
			self.subHandle.setFunction_preEdit(*args, **kwargs)
		else:
			warnings.warn(f"Add {self.type} to setFunction_preEdit() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_postEdit(self, *args, **kwargs):
		"""Override function for subHandle."""

		if ((self.type.lower() == "toolbaritem") and (self.subHandle != None)):
			self.subHandle.setFunction_postEdit(*args, **kwargs)
		else:
			warnings.warn(f"Add {self.type} to setFunction_postEdit() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_search(self, *args, **kwargs):
		"""Override function for subHandle."""

		if ((self.type.lower() == "toolbaritem") and (self.subHandle != None)):
			self.subHandle.setFunction_search(*args, **kwargs)
		else:
			warnings.warn(f"Add {self.type} to setFunction_search() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_cancel(self, *args, **kwargs):
		"""Override function for subHandle."""

		if ((self.type.lower() == "toolbaritem") and (self.subHandle != None)):
			self.subHandle.setFunction_cancel(*args, **kwargs)
		else:
			warnings.warn(f"Add {self.type} to setFunction_cancel() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_menuSelect(self, *args, **kwargs):
		"""Override function for subHandle."""

		if ((self.type.lower() == "toolbaritem") and (self.subHandle != None)):
			self.subHandle.setFunction_menuSelect(*args, **kwargs)
		else:
			warnings.warn(f"Add {self.type} to setFunction_menuSelect() for {self.__repr__()}", Warning, stacklevel = 2)

	def setEnable(self, state = True):
		"""Enables or disables an item based on the given input.

		state (bool) - If it is enabled or not

		Example Input: setEnable()
		Example Input: setEnable(False)
		"""

		if (self.type.lower() == "menuitem"):
			handle_Widget_Base.setEnable(self, state = state)

		elif (self.type.lower() == "toolbaritem"):
			self.parent.setEnable(self.label, state)

		else:
			warnings.warn(f"Add {self.type} to setEnable() for {self.__repr__()}", Warning, stacklevel = 2)

	def checkEnabled(self):
		"""Checks if an item is enabled.

		Example Input: checkEnabled()
		"""

		if (self.type.lower() == "menuitem"):
			state = handle_Widget_Base.checkEnabled(self)

		elif (self.type.lower() == "toolbaritem"):
			state = self.parent.checkEnabled(self.label, state)

		else:
			warnings.warn(f"Add {self.type} to checkEnabled() for {self.__repr__()}", Warning, stacklevel = 2)
			state = None

		return state
	
	def setShow(self, state = True):
		"""Shows or hides an item based on the given input.

		state (bool) - If it is shown or not

		Example Input: setShow()
		Example Input: setShow(False)
		"""

		if (self.type.lower() == "toolbaritem"):
			self.parent.setShow(self.label, state)

		else:
			warnings.warn(f"Add {self.type} to setShow() for {self.__repr__()}", Warning, stacklevel = 2)

	def checkShown(self):
		"""Checks if an item is shown.

		Example Input: checkShown()
		"""

		if (self.type.lower() == "toolbaritem"):
			state = self.shown

		else:
			warnings.warn(f"Add {self.type} to checkShown() for {self.__repr__()}", Warning, stacklevel = 2)
			state = None

		return state

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
			if (rightClick != None):
				preFunction, preFunctionArgs, preFunctionKwargs = argument_catalogue["preFunction", "preFunctionArgs", "preFunctionKwargs"]
				postFunction, postFunctionArgs, postFunctionKwargs = argument_catalogue["postFunction", "postFunctionArgs", "postFunctionKwargs"]

				if (rightClick):
					self._betterBind(wx.EVT_RIGHT_DOWN, self.parent.thing, self.onTriggerPopupMenu, [[preFunction, preFunctionArgs, preFunctionKwargs], [postFunction, postFunctionArgs, postFunctionKwargs]])
				else:
					self._betterBind(wx.EVT_LEFT_DOWN, self.parent.thing, self.onTriggerPopupMenu, [[preFunction, preFunctionArgs, preFunctionKwargs], [postFunction, postFunctionArgs, postFunctionKwargs]])

		
		#########################################################

		self._preBuild(argument_catalogue)

		if (self.type.lower() == "menupopup"):
			_build_menuPopup()
		elif (self.type.lower() == "menupopup_widget"):
			_build_menuPopup()
		else:
			warnings.warn(f"Add {self.type} to _build() for {self.__repr__()}", Warning, stacklevel = 2)

		self._postBuild(argument_catalogue)

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
		check = None, default = False,

		myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, 

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None):
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
		label = None, parent = None, handle = None, myId = None):
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
			"""Adds a menu to a pre-existing menubar.
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

	def _build(self, argument_catalogue):
		self._preBuild(argument_catalogue)

		text = self._getArguments(argument_catalogue, "text")

		#Check for separator
		if (text != None):
			enabled, hidden = self._getArguments(argument_catalogue, ["enabled", "hidden"])

			myFunction, myFunctionArgs, myFunctionKwargs, = self._getArguments(argument_catalogue, ["myFunction", "myFunctionArgs", "myFunctionKwargs"])
			icon, internal = self._getArguments(argument_catalogue, ["icon", "internal"])
			check, default, = self._getArguments(argument_catalogue, ["check", "default"])

			#Prepare menu item
			if (myFunction == None):
				special = self._getArguments(argument_catalogue, "special")
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
		self.drawQueue = [] #What will be drawn on the window. Items are drawn from left to right in their list order. [function, args, kwargs]
		self.drawQueue_saved = {}
		self.boundingBox = (0, 0, 0, 0)

	def _build(self, argument_catalogue):
		"""Determiens which build system to use for this handle."""

		def _build_canvas():
			"""Builds a wx panel object and makes it a canvas for painting."""
			nonlocal self, argument_catalogue

			panel, metric, initFunction, buildSelf = self._getArguments(argument_catalogue, ["panel", "metric", "initFunction", "self"])

			#Create the thing
			if (panel != None):
				self.myPanel = self._makePanel(parent = buildSelf.parent, **panel)
				self._finalNest(self.myPanel)
				self.thing = self.myPanel.thing
				self.metric = metric

				#Bind Functions
				if (initFunction != None):
					initFunctionArgs, initFunctionKwargs = self._getArguments(argument_catalogue, ["initFunctionArgs", "initFunctionKwargs"])
					self.setFunction_init(initFunction, initFunctionArgs, initFunctionKwargs)

				#Enable painting
				self._betterBind(wx.EVT_PAINT, self.thing, self._onPaint)
				self._betterBind(wx.EVT_SIZE, self.thing, self._onSize)
				# self._betterBind(wx.EVT_ERASE_BACKGROUND, self.thing, self.onDoNothing) #Disable background erasing to reduce flicker

			#Tell the window that EVT_PAINT will be running (reduces flickering)
			self.myWindow.thing.SetBackgroundStyle(wx.BG_STYLE_PAINT)
			if (panel != None):
				self.thing.SetBackgroundStyle(wx.BG_STYLE_PAINT)

			self.new()
		
		#########################################################

		self._preBuild(argument_catalogue)

		if (self.type.lower() == "canvas"):
			_build_canvas()
		else:
			warnings.warn(f"Add {self.type} to _build() for {self.__repr__()}", Warning, stacklevel = 2)

		self._postBuild(argument_catalogue)

	def setFunction_init(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		"""Changes the function that runs when the object is first created."""

		if (self.type.lower() == "canvas"):
			self.parent._betterBind(wx.EVT_INIT_DIALOG, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		else:
			warnings.warn(f"Add {self.type} to setFunction_init() for {self.__repr__()}", Warning, stacklevel = 2)

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
		if (self.thing == None):
			errorMessage = f"A panel was not created because 'panel' was None upon creation for {self.__repr__()}"
			raise ValueError(errorMessage)

		self.myPanel.setFunction_click(*args, **kwargs)

	def update(self):
		"""Redraws the canvas."""

		if (self.thing == None):
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

		image = self.getImage()
		image.SaveFile(fileName, fileType)

	def _getDC(self):
		"""Returns a dc with the canvas on it."""

		dc = wx.MemoryDC()
		dc.Clear()
		self._draw(dc)

		return dc

	def getImage(self):
		"""Returns an image with the canvas on it."""

		width, height = self.getSize()
		bitmap = wx.EmptyBitmap(width, height)

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

	def _queue(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		"""Queues a drawing function for the canvas.

		Example Input: _queue(drawRectangle, [5, 5, 25, 25])
		"""

		#Do not queue empty functions
		if (myFunction != None):
			self.drawQueue.append([myFunction, myFunctionArgs, myFunctionKwargs])

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

		if (self.thing == None):
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
			if (self.metric != None):
				if (self.metric):
					dc.SetMapMode(wx.MM_METRIC)
				else:
					dc.SetMapMode(wx.MM_LOMETRIC)
			else:
				dc.SetMapMode(wx.MM_TEXT)

		#Draw items in queue
		for myFunction, myFunctionArgs, myFunctionKwargs in self.drawQueue:
			if (isinstance(myFunction, str)):
				myFunctionEvaluated = eval(myFunction, {'__builtins__': None}, {"self": self, "dc": dc})
			else:
				myFunctionEvaluated = myFunction
			self.runMyFunction(myFunctionEvaluated, myFunctionArgs, myFunctionKwargs)

	#Drawing Functions
	def _getPen(self, color, width = 1):
		"""Returns a pen or list of pens to the user.
		Pens are used to draw shape outlines.

		color (tuple) - (R, G, B) as integers
					  - If a list of tuples is given: A brush for each color will be created
		width (int)   - How thick the pen will be

		Example Input: _getPen((255, 0, 0))
		Example Input: _getPen((255, 0, 0), 3)
		Example Input: _getPen([(255, 0, 0), (0, 255, 0)])
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

	def _getBrush(self, color, style = "solid", image = None, internal = False):
		"""Returns a pen or list of pens to the user.
		Brushes are used to fill shapes

		color (tuple)  - (R, G, B) as integers
						 If None: The fill will be transparent (no fill)
					   - If a list of tuples is given: A brush for each color will be created
		style (str)    - If not None: The fill style
					   - If a list is given: A brush for each style will be created
		image (str)    - If 'style' has "image" in it: This is the image that is used for the bitmap. Can be a PIL image
		internal (str) - If True and 'style' has "image" in it: 'image' is an iternal image

		Example Input: _getBrush((255, 0, 0))
		Example Input: _getBrush([(255, 0, 0), (0, 255, 0)])
		Example Input: _getBrush((255, 0, 0), style = "hatchCross)
		Example Input: _getBrush([(255, 0, 0), (0, 255, 0)], ["hatchCross", "solid"])
		Example Input: _getBrush(None)
		Example Input: _getBrush([(255, 0, 0), None])
		"""

		#Account for void color
		if (color == None):
			color = wx.Colour(0, 0, 0)
			style, image = self._getBrushStyle("transparent", None)
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
							style, image = self._getBrushStyle(style[i], image)
						else:
							style, image = self._getBrushStyle("transparent", None)
					else:
						#Account for void color
						if (color != None):
							style, image = self._getBrushStyle(style, image)
						else:
							style, image = self._getBrushStyle("transparent", None)

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
					style, image = self._getBrushStyle(style, image)
				else:
					color = wx.Colour(0, 0, 0)
					style, image = self._getBrushStyle("transparent", None)
				brush = wx.Brush(color, style)

				#Bind image if an image style was used
				if (image != None):
					brush.SetStipple(image)

		return brush

	def _getBrushStyle(self, style, image = None, internal = False):
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

		Example Input: _getBrushStyle("solid")
		Example Input: _getBrushStyle("image", image)
		Example Input: _getBrushStyle("image", "example.bmp")
		Example Input: _getBrushStyle("image", "error", True)
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
				image = self._getImage(imagePath, internal)

				#Determine style
				if ("t" in style):
					style = wx.BRUSHSTYLE_STIPPLE_MASK_OPAQUE

				elif ("m" in style):
					style = wx.BRUSHSTYLE_STIPPLE_MASK

				else:
					style = wx.BRUSHSTYLE_STIPPLE
			else:
				warnings.warn(f"Must supply an image path in _getBrushStyle() to use the style for {self.__repr__()}", Warning, stacklevel = 2)
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
			warnings.warn(f"Unknown style {style} in _getBrushStyle() for {self.__repr__()}", Warning, stacklevel = 2)
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

		if (self.thing == None):
			errorMessage = f"A panel was not created because 'panel' was None upon creation for {self.__repr__()}"
			raise ValueError(errorMessage)

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

		if (self.thing == None):
			errorMessage = f"A panel was not created because 'panel' was None upon creation for {self.__repr__()}"
			raise ValueError(errorMessage)

		#Skip empty origins
		if (x != None):
			#Move the origin
			if (y != None):
				self.thing.SetDeviceOrigin(x, y)
			else:
				self.thing.SetDeviceOrigin(x, x)
			
	def drawImage(self, imagePath, x = None, y = None, scale = None, internal = False, alpha = False):
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
		if (imagePath != None):
			#Get correct image
			image = self._getImage(imagePath, internal, alpha = alpha, scale = scale)

			if (x == None):
				x = 0
			elif (isinstance(x, str)):
				x = ast.literal_eval(re.sub("^['\"]|['\"]$", "", x))

			if (y == None):
				if (isinstance(x, (list, tuple))):
					y = x[1]
					x = x[0]
				else:
					y = 0
			elif (isinstance(y, str)):
				y = ast.literal_eval(re.sub("^['\"]|['\"]$", "", y))

			#Draw the image
			self._queue("dc.DrawBitmap", [image, x, y, alpha])

	def drawText(self, text, x = 0, y = 0, size = 12, angle = None, color = (0, 0, 0), bold = False, italic = False, family = None):
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

		Example Input: drawText("Lorem Ipsum")
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

		if (not isinstance(text, (list, tuple, range))):
			text = [text]

		for item in text:
			font = self._getFont(size = size, bold = bold, italic = italic, color = color, family = family)
			self._queue("dc.SetFont", font)

			pen = self._getPen(color)
			self._queue("dc.SetPen", pen)

			if ((angle != None) and (angle != 0)):
				self._queue("dc.DrawRotatedText", [item, x, y, angle])
			else:
				self._queue("dc.DrawText", [item, x, y])

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
		pen = self._getPen(color)

		#Draw the point
		if ((type(x) == list) or (type(x) == tuple)):
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
		pen = self._getPen(color, width)

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
		pen = self._getPen(color)

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
		pen = self._getPen(outline)
		brush = self._getBrush(fill, style)

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
				self._queue("dc.DrawEllipticArc", [item[0], item[1], arcWidth, arcHeight, arcStart, arcEnd])
		else:
			if (height == None):
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
		pen = self._getPen(color)

		#Draw the line
		if ((type(x) == list) or (type(x) == tuple)):
			for i, item in enumerate(x):
				#Setup color
				if ((type(pen) != list) and (type(pen) != tuple)):
					self._queue("dc.SetPen", pen)
				else:
					self._queue("dc.SetPen", pen[i])

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
				self._queue("dc.DrawCheckMark", [item[0], item[1], checkMarkWidth, checkMarkHeight])
		else:
			#Draw the line
			if (height == None):
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
		pen = self._getPen(outline, outlineWidth)
		brush = self._getBrush(fill, style)

		#Draw the rectangle
		if ((type(x) == list) or (type(x) == tuple)):
			if (radius != None):
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
					self._queue("dc.DrawRoundedRectangle", [item[0], item[1], width, height, radius])

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
				self._queue("dc.DrawRectangleList", [rectangles, pen, brush])
		else:

			#Draw the rectangle
			if (height == None):
				height = width

			self._queue("dc.SetPen", pen)
			self._queue("dc.SetBrush", brush)

			if (radius != None):
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
		pen = self._getPen(outline, outlineWidth)
		brush = self._getBrush(fill, style)

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
		pen = self._getPen(outline, outlineWidth)
		brush = self._getBrush(fill, style)

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
		pen = self._getPen(outline, outlineWidth)
		brush = self._getBrush(fill, style)

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
			self._queue("dc.DrawEllipseList", [ellipses, pen, brush])
		else:

			#Draw the ellipse
			if (height == None):
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

		if (self.type.lower() == "table"):
			if (returnRows):
				value = self.thing.GetNumberRows()
			else:
				value = self.thing.GetNumberCols()

		else:
			warnings.warn(f"Add {self.type} to __len__() for {self.__repr__()}", Warning, stacklevel = 2)
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

			##Default Cell Selection
			if ((default != None) and (default != (0, 0))):
				self.thing.GoToCell(default[0], default[1])

			#Bind the function(s)
			if (preEditFunction != None):
				preEditFunctionArgs, preEditFunctionKwargs = self._getArguments(argument_catalogue, ["preEditFunctionArgs", "preEditFunctionKwargs"])
				self.setFunction_preEdit(preEditFunction, preEditFunctionArgs, preEditFunctionKwargs)

			self.setFunction_postEdit(self.setTableLastModifiedCell)
			if (postEditFunction != None):
				postEditFunctionArgs, postEditFunctionKwargs = self._getArguments(argument_catalogue, ["postEditFunctionArgs", "postEditFunctionKwargs"])
				self.setFunction_postEdit(postEditFunction, postEditFunctionArgs, postEditFunctionKwargs)
			
			if (dragFunction != None):      
				dragFunctionArgs, dragFunctionKwargs = self._getArguments(argument_catalogue, ["dragFunctionArgs", "dragFunctionKwargs"])
				self.setFunction_drag(dragFunction, dragFunctionArgs, dragFunctionKwargs)

			self.setFunction_selectMany(self.setTablePreviousCell)
			if (selectManyFunction != None):
				selectManyFunctionArgs, selectManyFunctionKwargs = self._getArguments(argument_catalogue, ["selectManyFunctionArgs", "selectManyFunctionKwargs"])
				self.setFunction_selectMany(selectManyFunction, selectManyFunctionArgs, selectManyFunctionKwargs)

			self.setFunction_selectSingle(self.setTablePreviousCell)
			if (selectSingleFunction != None):
				selectSingleFunctionArgs, selectSingleFunctionKwargs = self._getArguments(argument_catalogue, ["selectSingleFunctionArgs", "selectSingleFunctionKwargs"])
				self.setFunction_selectSingle(selectSingleFunction, selectSingleFunctionArgs, selectSingleFunctionKwargs)
			
			if (rightClickCellFunction != None):
				rightClickCellFunctionArgs, rightClickCellFunctionKwargs = self._getArguments(argument_catalogue, ["rightClickCellFunctionArgs", "rightClickCellFunctionKwargs"])
				self.setFunction_rightClickCell(rightClickCellFunction, rightClickCellFunctionArgs, rightClickCellFunctionKwargs)

			if (rightClickLabelFunction != None):
				rightClickLabelFunctionArgs, rightClickLabelFunctionKwargs = self._getArguments(argument_catalogue, ["rightClickLabelFunctionArgs", "rightClickLabelFunctionKwargs"])
				self.setFunction_rightClickLabel(rightClickLabelFunction, rightClickLabelFunctionArgs, rightClickLabelFunctionKwargs)

			if (toolTips != None):
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

		if (self.type.lower() == "table"):
			_build_table()
		else:
			warnings.warn(f"Add {self.type} to _build() for {self.__repr__()}", Warning, stacklevel = 2)

		self._postBuild(argument_catalogue)

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

	def setTableLastModifiedCell(self, row = None, column = None, event = None):
		"""Sets the internal last modified cell to the specified value.
		If 'row' and 'column' are None, it will take the current cell.

		Example Input: setTableLastModifiedCell()
		Example Input: setTableLastModifiedCell(1, 2)
		"""

		if ((row != None) and (column != None)):
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
				if (cellType[None] == None):
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
						if (cellType["showCheck"] != None):
							if (cellType["showCheck"]):
								self.cellTypeCatalogue[str(cellType)] = [wx.grid.GridCellBoolRenderer(), wx.grid.GridCellBoolEditor()]
							else:
								self.cellTypeCatalogue[str(cellType)] = [wx.grid.GridCellBoolRenderer(), self.thing.GetDefaultEditor()]
						else:
							self.cellTypeCatalogue[str(cellType)] = [self.thing.GetDefaultRenderer(), wx.grid.GridCellBoolEditor()]
				else:
					self.cellTypeCatalogue[str(cellType)] = [self.thing.GetDefaultRenderer(), self._TableCellEditor(self, downOnEnter = self.enterKeyExitEdit, cellType = cellType)]

			# #Change settings if needed
			# rowList = range(self.thing.GetNumberRows()) if (row == None) else [row]
			# columnList = range(self.thing.GetNumberCols()) if (column == None) else [column]
			# for _row in rowList:
			# 	for _column in columnList:
			# 		if (isinstance(cellType[None], str) and (cellType[None].lower() in ["button"])):
			# 			if (not self.thing.IsReadOnly(_row, _column)):
			# 				self.thing.SetReadOnly(_row, _column, True)
			# 		else:
			# 			readOnly = self.getTableReadOnly(_row, _column)
			# 			if (self.thing.IsReadOnly(_row, _column) != readOnly):
			# 				self.thing.SetReadOnly(_row, _column, readOnly)

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
			if ((row == None) and (column == None)):
				for item in self.cellTypeCatalogue[str(cellType)]:
					if (isinstance(item, wx.grid.GridCellRenderer)):
						self.thing.SetDefaultRenderer(item)
					else:
						self.thing.SetDefaultEditor(item)

			rowList = range(self.thing.GetNumberRows()) if (row == None) else [row]
			columnList = range(self.thing.GetNumberCols()) if (column == None) else [column]

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

		if (cellType == None):
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

		color = self._getColor(color)

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

		fixedFlags, position, border = self._getItemMod(flags)
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

			totalSize = self.thing.GetGridWindow().GetSize()
			rowSize = calculate(self.rowSizeMaximum, rowList, row = True)
			columnSize = calculate(self.columnSizeMaximum, columnList, row = False)

			apply(rowList, rowSize, row = True)
			apply(columnList, columnSize, row = False)

		if (event != None):
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

		# def AppendCols(self, number = 1, updateLabels = True):
		# 	"""Notifies the table when changes are made.
		# 	Modified Code from Frank Millman on https://groups.google.com/forum/#!msg/wxpython-users/z4iobAKq0os/zzUL70WzL_AJ
		# 	"""

		# 	wx.grid.Grid.AppendCols(self, numCols = number, updateLabels = updateLabels)
		# 	# msg = wx.grid.GridTableMessage(self.GetTable(), wx.grid.GRIDTABLE_NOTIFY_COLS_APPENDED, number)
		# 	# self.ProcessTableMessage(msg)

		# def AppendRows(self, number = 1, updateLabels = True):
		# 	"""Notifies the table when changes are made.
		# 	Modified Code from Frank Millman on https://groups.google.com/forum/#!msg/wxpython-users/z4iobAKq0os/zzUL70WzL_AJ
		# 	"""

		# 	wx.grid.Grid.AppendRows(self, numRows = number, updateLabels = updateLabels)
		# 	# msg = wx.grid.GridTableMessage(self.GetTable(), wx.grid.GRIDTABLE_NOTIFY_ROWS_APPENDED, number)
		# 	# self.ProcessTableMessage(msg)

		# def InsertCols(self, position = 0, number = 1):
		# 	"""Notifies the table when changes are made.
		# 	Modified Code from Frank Millman on https://groups.google.com/forum/#!msg/wxpython-users/z4iobAKq0os/zzUL70WzL_AJ
		# 	"""

		# 	wx.grid.Grid.InsertCols(self, pos = position, numCols = number)
		# 	# msg = wx.grid.GridTableMessage(self.GetTable(), wx.grid.GRIDTABLE_NOTIFY_COLS_INSERTED, position, number)
		# 	# self.ProcessTableMessage(msg)

		# def InsertRows(self, position = 0, number = 1):
		# 	"""Notifies the table when changes are made.
		# 	Modified Code from Frank Millman on https://groups.google.com/forum/#!msg/wxpython-users/z4iobAKq0os/zzUL70WzL_AJ
		# 	"""

		# 	wx.grid.Grid.InsertRows(self, pos = position, numRows = number)
		# 	# msg = wx.grid.GridTableMessage(self.GetTable(), wx.grid.GRIDTABLE_NOTIFY_ROWS_INSERTED, position, number)
		# 	# self.ProcessTableMessage(msg)

		# def DeleteCols(self, position = 0, number = 1, updateLabels = True):
		# 	"""Notifies the table when changes are made.
		# 	Modified Code from Frank Millman on https://groups.google.com/forum/#!msg/wxpython-users/z4iobAKq0os/zzUL70WzL_AJ
		# 	"""

		# 	wx.grid.Grid.DeleteCols(self, pos = position, numCols = number, updateLabels = updateLabels)
		# 	# msg = wx.grid.GridTableMessage(self.GetTable(), wx.grid.GRIDTABLE_NOTIFY_COLS_DELETED, position, number)
		# 	# self.ProcessTableMessage(msg)

		# def DeleteRows(self, position = 0, number = 1, updateLabels = True):
		# 	"""Notifies the table when changes are made.
		# 	Modified Code from Frank Millman on https://groups.google.com/forum/#!msg/wxpython-users/z4iobAKq0os/zzUL70WzL_AJ
		# 	"""

		# 	wx.grid.Grid.DeleteRows(self, pos = position, numRows = number, updateLabels = updateLabels)
		# 	# msg = wx.grid.GridTableMessage(self.GetTable(), wx.grid.GRIDTABLE_NOTIFY_ROWS_DELETED, position, number)
		# 	# self.ProcessTableMessage(msg)

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
				# 	style += "|wx.TE_READONLY"

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
				self.parent.thing.GetEventHandler().ProcessEvent(event)

				self.ApplyEdit(row, column, grid)

				event = wx.grid.GridEvent(grid.GetId(), wx.grid.EVT_GRID_CELL_CHANGED.typeId, grid, row = row, col = column)
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

					if (self.cellType["text"] != None):
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
				if (color != None):
					color = tuple(min(255, max(0, item)) for item in color) #Ensure numbers are between 0 and 255
				else:
					if (isSelected):
						color = self.COLOR_TEXT_SELECTED
					else:
						color = self.COLOR_TEXT
				dc.SetTextForeground(color)

				if (align == None):
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
				if (color != None):
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
				if (color != None):
					color = tuple(min(255, max(0, item)) for item in color) #Ensure numbers are between 0 and 255
				else:
					if (isSelected):
						color = self.COLOR_BUTTON_SELECTED
					else:
						color = self.COLOR_BUTTON
				dc.SetBrush(wx.Brush(color, style = wx.SOLID))

				if (borderColor != None):
					borderColor = tuple(min(255, max(0, item)) for item in borderColor) #Ensure numbers are between 0 and 255
				else:
					borderColor = self.COLOR_BUTTON_BORDER
				dc.SetPen(wx.Pen(borderColor, width = borderWidth, style = wx.SOLID))
				# dc.SetPen(wx.TRANSPARENT_PEN)

				if (fitTo == None):
					width = rectangle.width
					height = rectangle.height
				else:
					width, height = dc.GetTextExtent(fitTo)

				if ((x_align == None) and (y_align == None)):
					x_align = 0
					y_align = 0
				else:
					if (x_align == None):
						x_align = "center"
					elif (y_align == None):
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

	def _build(self, argument_catalogue):
		if (self.type == None):
			errorMessage = "Must define sizer type before building"
			raise SyntaxError(errorMessage)

		sizerType = self.type.lower()
		if (sizerType not in ["grid", "flex", "bag", "box", "text", "wrap"]):
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
		if (sizerType == "grid"):
			rows, columns, rowGap, colGap = self._getArguments(argument_catalogue, ["rows", "columns", "rowGap", "colGap"])
			self.thing = wx.GridSizer(rows, columns, rowGap, colGap)

		else:
			#Determine direction
			vertical = self._getArguments(argument_catalogue, "vertical")
			if (vertical == None):
				direction = wx.BOTH
			elif (vertical):
				direction = wx.VERTICAL
			else:
				direction = wx.HORIZONTAL

			if (sizerType == "box"):
				self.thing = wx.BoxSizer(direction)

			elif (sizerType == "text"):
				self.thing = wx.StaticBoxSizer(wx.StaticBox(self.parent.thing, myId, text), direction)

			elif (sizerType == "wrap"):
				extendLast = self._getArguments(argument_catalogue, "extendLast")
				if (extendLast):
					flags = "wx.EXTEND_LAST_ON_EACH_LINE"
				else:
					flags = "wx.WRAPSIZER_DEFAULT_FLAGS"

				self.thing = wx.WrapSizer(direction, eval(flags, {'__builtins__': None, "wx": wx}, {}))

			else:
				rows, columns, rowGap, colGap = self._getArguments(argument_catalogue, ["rows", "columns", "rowGap", "colGap"])
				if (sizerType == "flex"):
					self.thing = wx.FlexGridSizer(rows, columns, rowGap, colGap)

				elif (sizerType == "bag"):
					self.thing = wx.GridBagSizer(rowGap, colGap)

					emptySpace = self._getArguments(argument_catalogue, "emptySpace")
					if (emptySpace != None):
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
		if (sizerType not in ["box", "text", "wrap"]):
			self.rows = rows
			self.columns = columns

		elif (sizerType != "wrap"):
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
		
		#Post Build
		self._postBuild(argument_catalogue)

		#Unpack arguments
		hidden = self._getArguments(argument_catalogue, "hidden")

		#Determine visibility
		if (hidden):
			if (isinstance(self, handle_Sizer)):
				self._addFinalFunction(self.thing.ShowItems, False)
			else:
				self.thing.Hide()

		#Account for nesting in a text sizer
		if (sizerType != "text"):
			if (text != None):
				self.substitute = self._makeSizerText(text = text)

		if (self.substitute != None):
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

		self._checkHandleType("Flex", self.growFlexColumn)

		if (growOnEmpty != None):
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

		self._checkHandleType("Flex", self.growFlexRow)

		if (growOnEmpty != None):
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

		self._checkHandleType("Flex", self.growFlexColumnAll)
	
		for column in range(self.thing.GetCols()):
			self.growFlexColumn(column, *args, **kwargs)

	def growFlexRowAll(self, *args, **kwargs):
		"""Allows all the rows to grow as much as they can.

		Example Input: growFlexRowAll()
		"""

		self._checkHandleType("Flex", self.growFlexRowAll)
		
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
		label = None, parent = None, handle = None, myId = None, selected = False, flex = 0, flags = "c1"):
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
		handle.type = "Double"
		handle._build(locals())

		return handle.getSizers()

	def addSplitterQuad(self, sizer_0 = {}, sizer_1 = {}, sizer_2 = {}, sizer_3 = {},

		initFunction = None, initFunctionArgs = None, initFunctionKwargs = None,

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None):
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
		handle.type = "Quad"
		handle._build(locals())

		return handle.getSizers()

	def addSplitterPoly(self, panelNumbers, sizers = {},
		dividerSize = 1, dividerPosition = None, dividerGravity = 0.5, vertical = False, minimumSize = 20, 

		initFunction = None, initFunctionArgs = None, initFunctionKwargs = None,

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None, myId = None):
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
		handle.type = "Poly"
		handle._build(locals())

		return handle.getSizers()

	#Notebooks
	def addNotebook(self, label = None, flags = None, tabSide = "top", flex = 0,
		fixedWidth = False, multiLine = False, padding = None, reduceFlicker = True,

		initFunction = None, initFunctionArgs = None, initFunctionKwargs = None,
		postPageChangeFunction = None, postPageChangeFunctionArgs = None, postPageChangeFunctionKwargs = None,
		prePageChangeFunction = None, prePageChangeFunctionArgs = None, prePageChangeFunctionKwargs = None,

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, size = wx.DefaultSize, position = wx.DefaultPosition,
		parent = None, handle = None, myId = None):
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

		handle = handle_Notebook()
		handle.type = "AuiNotebook"
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
		self.answer = None
		self.data = None
		self.subType = None

	def __enter__(self):
		"""Allows the user to use a with statement to build the GUI."""

		handle = handle_Base.__enter__(self)

		handle_Dialog.show(self)

		return handle

	def __exit__(self, exc_type, exc_value, traceback):
		"""Allows the user to use a with statement to build the GUI."""

		state = handle_Base.__exit__(self, exc_type, exc_value, traceback)

		if (self.type.lower() in ["busy"]): #, "printpreview"]):
			self.hide()

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
			self.thing = wx.MessageDialog(parent = None, message = text, caption = title, style = eval(style, {'__builtins__': None, "wx": wx}, {}))

		def _build_scroll():
			"""Builds a wx scroll dialog object."""
			nonlocal self, argument_catalogue

			text, title = self._getArguments(argument_catalogue, ["text", "title"])
			self.thing = wx.lib.dialogs.ScrolledMessageDialog(None, text, title)

		def _build_busyInfo():
			"""Builds a wx busy info dialog object."""
			nonlocal self, argument_catalogue

			self.thing = self._getArguments(argument_catalogue, ["text"])

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
			
			if (wrap != None):
				if (wrap > 0):
					style += "|wx.TE_MULTILINE|wx.TE_WORDWRAP"
				else:
					style += "|wx.TE_CHARWRAP|wx.TE_MULTILINE"

			self.thing = wx.TextEntryDialog(None, text, caption = title, value = default, style = eval(style, {'__builtins__': None, "wx": wx}, {}))

			if (maximum != None):
				self.thing.SetMaxLength(maximum)

		def _build_choice():
			"""Builds a wx choice dialog object."""
			nonlocal self, argument_catalogue

			choices, title, text, default, single = self._getArguments(argument_catalogue, ["choices", "title", "text", "default", "single"])
			
			#Ensure that the choices given are a list or tuple
			if (not isinstance(choices, (list, tuple, range))):
				choices = [choices]

			#Ensure that the choices are all strings
			choices = [str(item) for item in choices]

			self.choices = choices
			
			if (single):
				self.subType = "single"
				self.thing = wx.SingleChoiceDialog(None, title, text, choices, wx.CHOICEDLG_STYLE)
			else:
				self.thing = wx.MultiChoiceDialog(None, text, title, choices, wx.CHOICEDLG_STYLE)

			if (default != None):
				if (single):
					if (isinstance(default, (list, tuple, range))):
						if (len(default) == 0):
							default = 0
						else:
							default = default[0]

					if (isinstance(default, str)):
						if (default not in choices):
							warnings.warn(f"{self.default} not in 'choices' {choices} for {self.__repr__()}", Warning, stacklevel = 2)
							default = 0
						else:
							default = choices.index(default)

					self.thing.SetSelection(default)
				else:
					if (not isinstance(default, (list, tuple, range))):
						default = [default]

					defaultList = []
					for i in range(default):
						if (isinstance(default[i], str)):
							if (default[i] not in choices):
								warnings.warn(f"{self.default[i]} not in 'choices' {choices} for {self.__repr__()}", Warning, stacklevel = 2)
								default[i] = 0
							else:
								default[i] = choices.index(default[i])

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

			if (initialDir == None):
				initialDir = ""

			if (initialFile == None):
				initialFile = ""

			if (wildcard == None):
				wildcard = ""

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

			if (simple != None):
				self.subType = "simple"
				self.thing = wx.ColourDialog(None)
				self.thing.GetColourData().SetChooseFull(not simple)
			else:
				self.thing = wx.lib.agw.cubecolourdialog.CubeColourDialog(None)

		def _build_print():
			"""Builds a wx print dialog object."""
			nonlocal self, argument_catalogue

			pageNumbers, helpButton, printToFile, selection = self._getArguments(argument_catalogue, ["pageNumbers", "helpButton", "printToFile", "selection"])
			pageFrom, pageTo, pageMin, pageMax, collate, copies = self._getArguments(argument_catalogue, ["pageFrom", "pageTo", "pageMin", "pageMax", "collate", "copies"])

			#Configure settings
			# pd = wx.PrintData()
			# pd.SetPrinterName("")
			# pd.SetOrientation(wx.PORTRAIT)
			# pd.SetPaperId(wx.PAPER_A4)
			# pd.SetQuality(wx.PRINT_QUALITY_DRAFT)
			# pd.SetColour(True) # Black and white printing if False.
			# pd.SetNoCopies(1)
			# pd.SetCollate(True)
			# self.data = wx.PrintDialogData(pd)
			self.data = wx.PrintDialogData()

			self.data.EnablePageNumbers(pageNumbers)
			self.data.EnableHelp(helpButton)

			if (printToFile != None):
				self.data.EnablePrintToFile(True)
				self.data.SetPrintToFile(printToFile)
			else:
				self.data.EnablePrintToFile(False)

			if (selection != None):
				self.data.EnableSelection(True)
				self.data.SetSelection(selection)
			else:
				self.data.EnableSelection(True)

			if (pageFrom != None):
				self.data.SetFromPage(pageFrom)
	
			if (pageTo != None):
				self.data.SetToPage(pageTo)
			
			if (pageMin != None):
				self.data.SetMinPage(pageMin)
	
			if (pageMax != None):
				self.data.SetMaxPage(pageMax)
			
			if (collate != None):
				self.data.SetCollate(collate)
			
			if (copies != None):
				self.data.SetNoCopies(copies)
			
			# self.thing.SetAllPages(True)
			# self.thing.SetSetupDialog(True)

			self.thing = wx.PrintDialog(None, self.data)

			#Set Defaults
			self.title = "GUI_Maker Page"
			self.content = None

		def _build_printPreview():
			"""Builds a wx print dialog object."""
			nonlocal self, argument_catalogue

			#Configure settings
			# pd = wx.PrintData()
			# pd.SetPrinterName("")
			# pd.SetOrientation(wx.PORTRAIT)
			# pd.SetPaperId(wx.PAPER_A4)
			# pd.SetQuality(wx.PRINT_QUALITY_DRAFT)
			# pd.SetColour(True) # Black and white printing if False.
			# pd.SetNoCopies(1)
			# pd.SetCollate(True)
			# self.data = wx.PrintPreview(data = pd)
			# self.data = wx.PrintPreview(None)
			self.thing = -1

			#Set Defaults
			self.title = "GUI_Maker Page"
			self.position = None
			self.content = None
			self.size = None

		def _build_custom():
			"""Uses a frame to mimic a wx dialog object."""
			nonlocal self, argument_catalogue

			myFrame, valueLabel = self._getArguments(argument_catalogue, ["myFrame", "valueLabel"])
			self.thing = -1
			self.myFrame = myFrame

			if (valueLabel == None):
				valueLabel = myFrame.getValueLabel()
			self.valueLabel = valueLabel
		
		#########################################################

		argument_catalogue["hidden"] = False
		argument_catalogue["enabled"] = True
		self._preBuild(argument_catalogue)

		if (self.type.lower() == "message"):
			_build_message()
		elif (self.type.lower() == "process"):
			_build_process()
		elif (self.type.lower() == "scroll"):
			_build_scroll()
		elif (self.type.lower() == "inputbox"):
			_build_inputBox()
		elif (self.type.lower() == "custom"):
			_build_custom()
		elif (self.type.lower() == "busy"):
			_build_busyInfo()
		elif (self.type.lower() == "color"):
			_build_color()
		elif (self.type.lower() == "file"):
			_build_file()
		elif (self.type.lower() == "font"):
			_build_font()
		elif (self.type.lower() == "image"):
			_build_image()
		elif (self.type.lower() == "list"):
			_build_list()
		elif (self.type.lower() == "choice"):
			_build_choice()
		elif (self.type.lower() == "print"):
			_build_print()
		elif (self.type.lower() == "printsetup"):
			_build_pageSetup()
		elif (self.type.lower() == "printpreview"):
			_build_printPreview()
		else:
			warnings.warn(f"Add {self.type} to _build() for {self.__repr__()}", Warning, stacklevel = 2)

		self._postBuild(argument_catalogue)

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

		#Pause background functions
		for variable, handleDict in self.controller.backgroundFunction_pauseOnDialog.items():
			for handle, functionDict in handleDict.items():
				for function, attributes in functionDict.items():
					if ((attributes["state"]) and ((self.label == None) or ((self.label != None) and (self.label not in attributes["exclude"])))):
						catalogue = getattr(handle, variable)
						catalogue[function]["pause"] = True

		#Show dialogue
		if (self.type.lower() == "message"):
			self.answer = self.thing.ShowModal()
			self.hide()

		elif (self.type.lower() == "inputbox"):
			self.answer = self.thing.ShowModal()
			self.hide()

		elif (self.type.lower() == "choice"):
			self.answer = self.thing.ShowModal()
			self.hide()

		elif (self.type.lower() == "scroll"):
			self.answer = self.thing.ShowModal()
			self.hide()

		elif (self.type.lower() == "custom"):

			self.myFrame.runMyFunction(self.myFrame.preShowFunction, self.myFrame.preShowFunctionArgs, self.myFrame.preShowFunctionKwargs, includeEvent = True)
			self.myFrame.runMyFunction(self.myFrame.postShowFunction, self.myFrame.postShowFunctionArgs, self.myFrame.postShowFunctionKwargs, includeEvent = True)

			self.myFrame.visible = True
			self.answer = self.myFrame.thing.ShowModal()

		elif (self.type.lower() == "busyinfo"):
			self.thing = wx.BusyInfo(self.thing)

		elif (self.type.lower() == "file"):
			self.answer = self.thing.ShowModal()
			self.hide()

		elif (self.type.lower() == "color"):
			self.answer = self.thing.ShowModal()
			self.hide()

		elif (self.type.lower() == "print"):
			self.answer = self.thing.ShowModal()
			self.hide()

		elif (self.type.lower() == "printpreview"):
			pass

		else:
			warnings.warn(f"Add {self.type} to show() for {self.__repr__()}", Warning, stacklevel = 2)

	def hide(self):
		"""Hides the dialog box for this handle."""

		if (self.type.lower() == "busyinfo"):
			del self.thing
			self.thing = None
		elif (self.type.lower() == "printpreview"):
			self.thing.hide()
			self.thing = None

		if (self.type.lower() == "message"):
			self.thing.Destroy()
			self.thing = None

		elif (self.type.lower() == "inputbox"):
			self.data = self.thing.GetValue()

			self.thing.Destroy()
			self.thing = None

		elif (self.type.lower() == "choice"):
			if ((self.subType != None) and (self.subType.lower() == "single")):
				self.data = self.thing.GetSelection()
			else:
				self.data = self.thing.GetSelections()

			self.thing.Destroy()
			self.thing = None

		elif (self.type.lower() == "scroll"):
			self.thing.Destroy()
			self.thing = None

		elif (self.type.lower() == "custom"):
			if ((self.answer == wx.ID_CANCEL) and (len(self.myFrame.cancelFunction) != 0)):
				self.myFrame.runMyFunction(self.myFrame.cancelFunction, self.myFrame.cancelFunctionArgs, self.myFrame.cancelFunctionKwargs, includeEvent = True)

			self.myFrame.runMyFunction(self.myFrame.preHideFunction, self.myFrame.preHideFunctionArgs, self.myFrame.preHideFunctionKwargs, includeEvent = True)
			self.myFrame.runMyFunction(self.myFrame.postHideFunction, self.myFrame.postHideFunctionArgs, self.myFrame.postHideFunctionKwargs, includeEvent = True)

			# self.myFrame.thing.Destroy() #Don't destroy it so it can appear again without the user calling addDialog() again. Time will tell if this is a bad idea or not
			self.thing = None

		elif (self.type.lower() == "file"):
			if ((self.subType != None) and ("single" in self.subType.lower())):
				self.data = self.thing.GetPath()
			else:
				self.data = self.thing.GetPaths()

			self.thing.Destroy()
			self.thing = None

		elif (self.type.lower() == "color"):
			self.data = self.thing.GetColourData()

			self.thing.Destroy()
			self.thing = None

		elif (self.type.lower() == "print"):
			self.dialogData = self.thing.GetPrintDialogData()

			self.thing.Destroy()
			self.thing = None

		else:
			warnings.warn(f"Add {self.type} to hide() for {self.__repr__()}", Warning, stacklevel = 2)

		#Unpause background functions
		for variable, handleDict in self.controller.backgroundFunction_pauseOnDialog.items():
			for handle, functionDict in handleDict.items():
				for function, attributes in functionDict.items():
					if ((attributes["state"]) and ((self.label == None) or ((self.label != None) and (self.label not in attributes["exclude"])))):
						catalogue = getattr(handle, variable)
						catalogue[function]["pause"] = False

	#Getters
	def getValue(self, event = None):
		"""Returns what the contextual value is for the object associated with this handle."""

		if (self.type.lower() == "choice"):
			if ((self.subType != None) and (self.subType.lower() == "single")):
				value = self.choices[self.data]
			else:
				value = [self.choices[i] for i in self.data]

		elif (self.type.lower() == "inputbox"):
			value = self.data

		elif (self.type.lower() == "custom"):
			if (self.valueLabel == None):
				if (self.valueLabel == None):
					errorMessage = f"In order to use getValue() for {self.__repr__()} 'valueLabel' cannot be None\nEither provide it in makeDialogCustom() for {self.__repr__()} or use setValueLabel() for {self.myFrame.__repr__()}"
					raise KeyError(errorMessage)
			else:
				if (self.valueLabel not in self.myFrame):
					errorMessage = f"There is no widget with the label {self.valueLabel} in {self.myFrame.__repr__()} for {self.__repr__()}"
					raise ValueError(errorMessage)

			value = self.myFrame.getValue(self.valueLabel)

		elif (self.type.lower() == "file"):
			value = self.data

		elif (self.type.lower() == "color"):
			color = self.data.GetColour().Get()
			value = (color.Red(), color.Green(), color.Blue(), color.Alpha())

		elif (self.type.lower() == "print"):
			value = [self.data, self.dialogData, self.content]

		elif (self.type.lower() == "printPreview"):
			value = self.content

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

	#Setters
	def setValue(self, value, event = None):
		"""Sets the contextual value for the object associated with this handle to what the user supplies."""

		if (self.type.lower() == "print"):
			self.content = value
		
		elif (self.type.lower() == "printpreview"):
			self.content = value
		
		else:
			warnings.warn(f"Add {self.type} to setValue() for {self.__repr__()}", Warning, stacklevel = 2)

	def setTitle(self, text = None, event = None):
		"""Sets the title."""

		if (self.type.lower() == "print"):
			if (text == None):
				text = "GUI_Maker Page"
			self.title = text
		else:
			warnings.warn(f"Add {self.type} to setTitle() for {self.__repr__()}", Warning, stacklevel = 2)

	def setSize(self, size = None, event = None):
		"""Sets the size."""

		if (self.type.lower() == "print"):
			self.size = size
		else:
			warnings.warn(f"Add {self.type} to setTitle() for {self.__repr__()}", Warning, stacklevel = 2)

	#Etc
	def send(self, event = None):
		"""Returns what the contextual valueDoes the contextual send command for the object associated with this handle.
		Modified code from: https://wiki.wxpython.org/Printing
		"""

		if (self.type.lower() == "print"):
			printer = wx.Printer(self.dialogData)
			myPrintout = self._MyPrintout(self)

			if (not printer.Print(self, myPrintout, True)):
				wx.MessageBox(("There was a problem printing.\nPerhaps your current printer is \nnot set correctly ?"), ("Printing"), wx.OK)
				return
			else:
				self.printData = wx.PrintData(printer.GetPrintDialogData().GetPrintData())
			myPrintout.Destroy()

		elif (self.type.lower() == "printpreview"):
			handle = handle_Window(self.myWindow.controller)
			handle.type = "Preview"

			argument_catalogue = {"canvas": self._MyPrintout(self, self.title), "enablePrint": True}
			argument_catalogue = self._arrangeArguments(self.controller, Controller.addWindow, kwargDict = argument_catalogue)
			handle._build(argument_catalogue)

			handle.setWindowSize(self.size)
			handle.setWindowPosition(self.position)
			handle.showWindow()

		else:
			warnings.warn(f"Add {self.type} to send() for {self.__repr__()}", Warning, stacklevel = 2)

	class _MyPrintout(wx.Printout):
		def __init__(self, parent, title = "GUI_Maker Page"):
			wx.Printout.__init__(self, title)

			self.title = title
			self.parent = parent

		def OnPrintPage(self, page):
			"""Arranges the stuff on the page."""

			dc = self.GetDC()
			dc.SetMapMode(wx.MM_POINTS) #Each logical unit is a “printer point” i.e. 1/72 of an inch
			# dc.SetMapMode(wx.MM_TWIPS) #Each logical unit is 1/20 of a “printer point”, or 1/1440 of an inch

			if (isinstance(self.parent.content, str)):

				dc.SetTextForeground("black")
				dc.SetFont(wx.Font(11, wx.SWISS, wx.NORMAL, wx.BOLD))
				dc.DrawText(self.parent.content, 0, 0)
			if (isinstance(self.parent.content, handle_WidgetCanvas)):
				with self.parent.content as myCanvas:
					myCanvas._draw(dc, modifyUnits = False)
			else:
				image = self.parent._getImage(self.parent.content)
				dc.DrawBitmap(image, 0, 0)

			return True

		def clone(self):
			"""Returns a copy of itself as a separate instance."""

			return self.parent._MyPrintout(self.parent, title = self.title)

class handle_Window(handle_Container_Base):
	"""A handle for working with a wxWindow."""

	def __init__(self, controller):
		"""Initializes defaults."""

		#Initialize inherited classes
		handle_Container_Base.__init__(self)

		#Defaults
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
		
		if (self.mainPanel != None):
			output += f"-- main panel id: {id(self.mainPanel)}\n"
		if (self.mainSizer != None):
			output += f"-- main sizer id: {id(self.mainSizer)}\n"
		return output

	def _build(self, argument_catalogue):
		"""Determiens which build system to use for this handle."""

		def _build_frame():
			"""Builds a wx frame object."""
			nonlocal self, argument_catalogue

			#Determine window style
			tabTraversal, stayOnTop, floatOnParent, resize, topBar, minimize, maximize, close, title = self._getArguments(argument_catalogue, ["tabTraversal", "stayOnTop", "floatOnParent", "resize", "topBar", "minimize", "maximize", "close", "title"])
			style = "wx.CLIP_CHILDREN|wx.SYSTEM_MENU"
			if (tabTraversal):
				style += "|wx.TAB_TRAVERSAL"

			if (stayOnTop):
				style += "|wx.STAY_ON_TOP"

			if (floatOnParent):
				style += "|wx.FRAME_FLOAT_ON_PARENT"

			if (resize):
				style += "|wx.RESIZE_BORDER"

			if (topBar != None):
				if (topBar):
					style += "|wx.MINIMIZE_BOX|wx.MAXIMIZE_BOX|wx.CLOSE_BOX"
			else:
				if (minimize):
					style += "|wx.MINIMIZE_BOX"

				if (maximize):
					style += "|wx.MAXIMIZE_BOX"

				if (close):
					style += "|wx.CLOSE_BOX"

			if (title != None):
				style += "|wx.CAPTION"
			else:
				title = ""

			#Make the frame
			size, position, smallerThanScreen = self._getArguments(argument_catalogue, ["size", "position", "smallerThanScreen"])
			self.thing = wx.Frame(None, title = title, size = size, pos = position, style = eval(style, {'__builtins__': None, "wx": wx}, {}))

			# if (smallerThanScreen not in [None, False]):
			# 	screenSize = self.getScreenSize()
			# 	if (isinstance(smallerThanScreen, int)):
			# 		self.thing.SetMaxSize(screenSize[smallerThanScreen])
			# 	else:
			# 		self.thing.SetMaxSize(map(sum, zip(*screenSize)))
			
			#Add Properties
			icon, internal = self._getArguments(argument_catalogue, ["icon", "internal"])
			if (icon != None):
				self.setIcon(icon, internal)

			#Bind functions
			delFunction, delFunctionArgs, delFunctionKwargs = self._getArguments(argument_catalogue, ["delFunction", "delFunctionArgs", "delFunctionKwargs"])
			initFunction, initFunctionArgs, initFunctionKwargs = self._getArguments(argument_catalogue, ["initFunction", "initFunctionArgs", "initFunctionKwargs"])
			idleFunction, idleFunctionArgs, idleFunctionKwargs = self._getArguments(argument_catalogue, ["idleFunction", "idleFunctionArgs", "idleFunctionKwargs"])
			
			if (initFunction != None):
				self.setFunction_init(initFunction, initFunctionArgs, initFunctionKwargs)

			if (delFunction != None):
				self.setFunction_close(delFunction, delFunctionArgs, delFunctionKwargs)
			else:
				endProgram = self._getArguments(argument_catalogue, ["endProgram"])
				if (endProgram != None):
					if (endProgram):
						delFunction = self.controller.onExit
					else:
						delFunction = self.controller.onQuit
				else:
					delFunction = self.onHideWindow

				self.setFunction_close(delFunction)

			if (idleFunction != None):
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
			style = "wx.SYSTEM_MENU"

			if (stayOnTop):
				style += "|wx.STAY_ON_TOP"

			# if (helpButton):
			# 	style += "|wx.DIALOG_EX_CONTEXTHELP"

			if (resize):
				style += "|wx.RESIZE_BORDER"

			if (topBar != None):
				if (topBar):
					style += "|wx.MINIMIZE_BOX|wx.MAXIMIZE_BOX|wx.CLOSE_BOX"
			else:
				if (minimize):
					style += "|wx.MINIMIZE_BOX"

				if (maximize):
					style += "|wx.MAXIMIZE_BOX"

				if (close):
					style += "|wx.CLOSE_BOX"

			if (title != None):
				style += "|wx.CAPTION"
			else:
				title = ""

			#Create Object
			self.thing = wx.Dialog(None, title=title, size = size, pos = position, style = eval(style, {'__builtins__': None, "wx": wx}, {}))

			if (smallerThanScreen not in [None, False]):
				if (isinstance(smallerThanScreen, bool)):
					screenSize = self.getScreenSize()
				else:
					screenSize = self.getScreenSize(number = smallerThanScreen)
				self.thing.SetMaxSize(screenSize)

			#Set Properties
			if (icon != None):
				self.setIcon(icon, internal)

			#Remember Values
			self.valueLabel = valueLabel

			#Bind functions
			delFunction, delFunctionArgs, delFunctionKwargs = self._getArguments(argument_catalogue, ["delFunction", "delFunctionArgs", "delFunctionKwargs"])
			initFunction, initFunctionArgs, initFunctionKwargs = self._getArguments(argument_catalogue, ["initFunction", "initFunctionArgs", "initFunctionKwargs"])
			
			if (initFunction != None):
				self.setFunction_init(initFunction, initFunctionArgs, initFunctionKwargs)

			if (delFunction != None):
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
					elif (addNo or ((addYes not in [False, None]) and (addNo == None))):
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

		def _build_preview():
			"""Builds a wx preview frame object."""
			nonlocal self, argument_catalogue

			canvas, enablePrint = self._getArguments(argument_catalogue, ["canvas", "enablePrint"])

			if (enablePrint):
				preview = wx.PrintPreview(canvas, canvas.clone())
			else:
				preview = wx.PrintPreview(canvas)

			#Pre Settings
			if ("__WXMAC__" in wx.PlatformInfo):
				preview.SetZoom(50)
			else:
				preview.SetZoom(35)

			if (not preview.IsOk()):
				warnings.warn(f"'canvas' {canvas.__repr__()} was not created correctly for {self.__repr__()}", Warning, stacklevel = 2)
				self.thing = None
				return

			self.thing = wx.PreviewFrame(preview, None, "Print Preview")

			#Post Settings
			image = self._getImage("print", internal = True)
			self.thing.SetIcon(wx.Icon(image))
			self.thing.Initialize()

		#########################################################

		self._preBuild(argument_catalogue)

		if (self.type.lower() == "frame"):
			_build_frame()
		elif (self.type.lower() == "dialog"):
			_build_dialog()
		elif (self.type.lower() == "preview"):
			_build_preview()
		else:
			warnings.warn(f"Add {self.type} to _build() for {self.__repr__()}", Warning, stacklevel = 2)

		self._postBuild(argument_catalogue)

	def getTitle(self):
		"""Returns the title for this window."""

		return self.thing.GetTitle()
	
	def checkActive(self, event = None):
		"""Returns if the window is active or not."""

		if (event != None):
			if (isinstance(event, wx._core.ActivateEvent)):
				return event.GetActive()
		return self.thing.IsActive()

	def getValueLabel(self, event = None):
		"""Returns what the contextual value label is for the object associated with this handle."""

		if (self.type.lower() == "dialog"):
			value = self.valueLabel
		else:
			warnings.warn(f"Add {self.type} to getValueLabel() for {self.__repr__()}", Warning, stacklevel = 2)
			value = None

		return value

	def setValueLabel(self, newValue, event = None):
		"""Sets the contextual value for the object associated with this handle to what the user supplies."""

		if (self.type.lower() == "dialog"):
			self.valueLabel = newValue
		else:
			warnings.warn(f"Add {self.type} to setValueLabel() for {self.__repr__()}", Warning, stacklevel = 2)

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
	def setWindowSize(self, x = None, y = None):
		"""Re-defines the size of the window.

		x (int)     - The width of the window
		y (int)     - The height of the window

		Example Input: setWindowSize()
		Example Input: setWindowSize(350, 250)
		Example Input: setWindowSize((350, 250))
		"""

		if (x == None):
			self.thing.SetSize(wx.DefaultSize)
			return

		if (isinstance(x, str)):
			if (x.lower() == "default"):
				self.thing.SetSize(wx.DefaultSize)
				return
			else:
				x = ast.literal_eval(re.sub("^['\"]|['\"]$", "", x))

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

		if (x == None):
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

		if (y == None):
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

		if (y == None):
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

		if (y == None):
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

		if (offset == None):
			offset = (0, 0)

		screenSize = self.getScreenSize(number = number)
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

		self.runMyFunction(self.postShowFunction, self.postShowFunctionArgs, self.postShowFunctionKwargs, includeEvent = True)

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

	def hideWindow(self, event = None):
		"""Hides the window from view, but does not close it.
		Note: This window continues to run and take up memmory. Local variables are still active.

		Example Input: hideWindow()
		"""

		self.runMyFunction(self.preHideFunction, self.preHideFunctionArgs, self.preHideFunctionKwargs, includeEvent = True)

		if (self.controller.windowDisabler != None):
			if (self.controller.windowDisabler[0] == self.thing):
				self.controller.windowDisabler[1] = None
				self.controller.windowDisabler = None

		if (self.visible):
			if (isinstance(self.thing, wx.Dialog)):
				if (event == None):
					errorMessage = f"Must either use onHideWindow() or pass 'event' to hideWindow() to hide a custom dialog for {self.__repr__()}"
					raise ValueError(errorMessage)
				self.thing.EndModal(event.GetEventObject().GetId())
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
		elif (sizerLabel == None):
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

	def addMenu(self, *args, **kwargs):
		"""Adds a menu to a pre-existing menubar.
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

	def addPopupMenu(self, label = None, rightClick = True, 

		preFunction = None, preFunctionArgs = None, preFunctionKwargs = None, 
		postFunction = None, postFunctionArgs = None, postFunctionKwargs = None,

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		parent = None, handle = None, myId = None):
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

		if (self.statusBar == None):
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

		if (self.statusBar == None):
			if (self.type.lower() == "dialog"):
				if (self.mainPanel != None):
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

		if (self.statusBar == None):
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

		if (self.statusBar == None):
			warnings.warn(f"There is no status bar in setStatusWidth() for {self.__repr__()}", Warning, stacklevel = 2)
			return

		if (number == None):
			number = []
		elif (not isinstance(number, (list, tuple, range))):
			number = [number]

		if (autoWidth):
			self.statusBar_autoWidth = number
			return
		elif (len(number) == 0):
			self.statusBar_autoWidth = None

		if (width == None):
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

	def setStatusText(self, message = None, number = 0, startDelay = 0, autoAdd = False):
		"""Sets the text shown in the status bar.
		If a message is on a timer and a new message gets sent, the timer message will stop and not overwrite the new message.
		In a multi-field status bar, the fields are numbered starting with 0.

		message (str)  - What the status bar will say
			- If dict: {What to say (str): How long to wait in ms before moving on to the next message (int). Use None for ending}
			- If None: Will use the defaultr status message
			- If function: Will run the function and use the returned value as the message
		number (int)   - Which field to place this status in on the status bar
		startDelay (int)    - How long to wait in ms before showing the first message
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
			nonlocal self, message, number, startDelay

			#Account for other messages with timers before this one
			while (self.statusTextTimer["listening"] > 0):
				self.statusTextTimer["stop"] = True
				time.sleep(100 / 1000)
			self.statusTextTimer["stop"] = False

			self.statusTextTimer["listening"] += 1

			if (startDelay not in [None, 0]):
				time.sleep(startDelay / 1000)

			if (not isinstance(message, dict)):
				applyMessage(message)
			else:
				for text, delay in message.items():
					if (self.statusTextTimer["stop"]):
						self.statusTextTimer["stop"] = False
						break

					applyMessage(text)

					if (text == None):
						text = self.statusTextDefault.get(number, " ")
					if (callable(text)):
						text = text()
					if (text == None):
						text = " "
					self.statusBar.SetStatusText(text, number)

					if (delay == None):
						break
					time.sleep(delay / 1000)

			self.statusTextTimer["listening"] -= 1

		def applyMessage(text):
			"""Places the given text into the status bar."""
			nonlocal self, number

			if (text == None):
				text = self.statusTextDefault.get(number, " ")
			if (callable(text)):
				text = text()
			if (text == None):
				text = " "
			self.statusBar.SetStatusText(text, number)

			if (isinstance(self.statusBar_autoWidth, (list, tuple, range)) and ((len(self.statusBar_autoWidth) == 0) or (number in self.statusBar_autoWidth))):
				self.setStatusWidth(width = self.getStringPixels(text)[0], number = number)

		##################################################

		#Error Checking
		if (self.statusBar == None):
			if (autoAdd):
				self.addStatusBar()
			else:
				warnings.warn(f"There is no status bar in setStatusText() for {self.__repr__()}", Warning, stacklevel = 2)
				return

		if (self.statusBar.GetFieldsCount() <= number):
			warnings.warn(f"There are only {self.statusBar.GetFieldsCount()} fields in the status bar, so it cannot set the text for field {number} in setStatusText() for {self.__repr__()}", Warning, stacklevel = 2)
			return

		self.backgroundRun(timerMessage)

	def setStatusTextDefault(self, message = " ", number = 0):
		"""Sets the default status message for the status bar.

		message (str) - What the status bar will say on default

		Example Input: setStatusTextDefault("Ready")
		"""

		if (message == None):
			message = " "
		self.statusTextDefault[number] = message

	def getStatusText(self, number = 0):
		"""Returns the status message that is currently displaying.

		Example Input: getStatusText()
		"""

		if (self.statusBar == None):
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
		image = self._getImage(icon, internal)
		image = self._convertBitmapToImage(image)
		image = image.Scale(16, 16, wx.IMAGE_QUALITY_HIGH)
		image = self._convertImageToBitmap(image)

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
				if (item == None):
					continue
				elif (isinstance(item, handle_NotebookPage)):
					applyInvalidateNested([item.mySizer, item.myPanel])
					continue
				elif (isinstance(item, handle_MenuPopup)):
					continue
				elif (item.thing == None):
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

				elif (isinstance(item, handle_NotebookPage)):
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
			if (autoSize == None):
				autoSize = self.autoSize

			#Auto-size the window
			if (autoSize):
				if (invalidateNested):
					applyInvalidateNested(self[:])

				if (self.mainPanel != None):
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
				if (self.mainPanel != None):
					self.mainPanel.thing.SendSizeEvent()
				self.thing.SendSizeEvent()
			else:
				if (self.mainPanel != None):
					self.mainPanel.thing.Layout()
					self.mainPanel.thing.Refresh()
					# self.mainPanel.thing.Update()

				# if (self.mainSizer != None):
				# 	self.mainSizer.thing.Layout() 

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

		if (event != None):
			event.Skip()

	def refresh(self, event = None, includeEvent = False):
		"""Runs the user defined refresh function.
		This function is intended to make sure all widget values are up to date.

		Example Input: refresh()
		"""

		if (len(self.refreshFunction) == 0):
			warnings.warn(f"The refresh function for {self.__repr__()} has not been set yet\nUse setRefresh() during window creation first to set the refresh function", Warning, stacklevel = 2)
			return

		self.runMyFunction(self.refreshFunction, self.refreshFunctionArgs, self.refreshFunctionKwargs, event = event, includeEvent = includeEvent)

	def _addFinalFunction(self, myFunction, myFunctionArgs = None, myFunctionKwargs = None, label = None):
		"""Adds a function to the queue that will run after building, but before launching, the app."""

		if (label == None):
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

	def _build(self, argument_catalogue):
		"""Determiens which build system to use for this handle."""

		def _build_normal():
			"""Builds a wx double splitter object."""
			nonlocal self, argument_catalogue

			#Error Check
			if (self.parent.thing == None):
				errorMessage = f"The object {self.parent.__repr__()} must be fully created for {self.__repr__()}"
				raise RuntimeError(errorMessage)

			#Unpack arguments
			scroll_x, scroll_y, scrollToTop, scrollToChild = self._getArguments(argument_catalogue, ["scroll_x", "scroll_y", "scrollToTop", "scrollToChild"])
			position, size, border, tabTraversal = self._getArguments(argument_catalogue, ["position", "size", "border", "tabTraversal"])
			initFunction = self._getArguments(argument_catalogue, ["initFunction"])

			#Setup
			style = "wx.EXPAND|wx.ALL"
			if (type(border) == str):
				#Ensure correct caseing
				border = border.lower()

				if (border[0:2] == "si"):
					style += "|wx.SIMPLE_BORDER"

				elif (border[0] == "r"):
					style += "|wx.RAISED_BORDER"

				elif (border[0:2] == "su"):
					style += "|wx.SUNKEN_BORDER"

				elif (border[0] == "n"):
					style += "|wx.NO_BORDER"

				else:
					errorMessage = f"Unknown border {border} in {self.__repr__()}"
					raise KeyError(errorMessage)
			else:
				style += "|wx.NO_BORDER"

			if (tabTraversal):
				style += "|wx.TAB_TRAVERSAL"

			myId = self._getId(argument_catalogue)

			#Create the panel
			if ((scroll_x not in [False, None]) or (scroll_y not in [False, None])):
				self.thing = wx.lib.scrolledpanel.ScrolledPanel(self.parent.thing, id = myId, pos = position, size = size, style = eval(style, {'__builtins__': None, "wx": wx}, {}))

				instructions = {}
				instructions["scrollToTop"] = scrollToTop
				instructions["scrollIntoView"] = scrollToChild
				instructions["scroll_x"] = (scroll_x not in [False, None])
				instructions["scroll_y"] = (scroll_y not in [False, None])
				instructions["rate_x"] = scroll_x if (isinstance(scroll_x, int)) else 20
				instructions["rate_y"] = scroll_y if (isinstance(scroll_x, int)) else 20

				self.thing.SetupScrolling(**instructions)

			else:
				self.thing = wx.Panel(self.parent.thing, id = myId, pos = position, size = size, style = eval(style, {'__builtins__': None, "wx": wx}, {}))

			#Bind Functions
			if (initFunction != None):
				initFunctionArgs, initFunctionKwargs = self._getArguments(argument_catalogue, ["initFunctionArgs", "initFunctionKwargs"])
				self._betterBind(wx.EVT_INIT_DIALOG, self.thing, initFunction, initFunctionArgs, initFunctionKwargs)

			#Update catalogue
			for key, value in locals().items():
				if (key != "self"):
					argument_catalogue[key] = value
			
		#########################################################

		self._preBuild(argument_catalogue)

		if (self.type.lower() == "panel"):
			_build_normal()
		else:
			warnings.warn(f"Add {self.type} to _build() for {self.__repr__()}", Warning, stacklevel = 2)

		self._postBuild(argument_catalogue)

	def setFunction_click(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		"""Changes the function that runs when a menu item is selected."""

		self._betterBind(wx.EVT_LEFT_DOWN, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)

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
			if (dividerPosition != None):
				self.thing.SetSashPosition(dividerPosition)

			##Left panel growth ratio
			self.thing.SetSashGravity(dividerGravity)

			##Dividing line size
			self.thing.SetSashSize(dividerSize)

			#Bind Functions
			if (initFunction != None):
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
			if (initFunction != None):
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
			if (initFunction != None):
				initFunctionArgs, initFunctionKwargs = self._getArguments(argument_catalogue, ["initFunctionArgs", "initFunctionKwargs"])
				self.setFunction_init(initFunction, initFunctionArgs, initFunctionKwargs)

			
		#########################################################

		self._preBuild(argument_catalogue)

		if (self.type.lower() == "double"):
			_build_double()
		elif (self.type.lower() == "quad"):
			_build_quad()
		elif (self.type.lower() == "poly"):
			_build_poly()
		else:
			warnings.warn(f"Add {self.type} to _build() for {self.__repr__()}", Warning, stacklevel = 2)

		self._postBuild(argument_catalogue)

	def setFunction_init(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		"""Changes the function that runs when the object is first created."""

		if (self.type.lower() == "double"):
			self.parent._betterBind(wx.EVT_INIT_DIALOG, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		elif (self.type.lower() == "quad"):
			self.parent._betterBind(wx.EVT_INIT_DIALOG, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		elif (self.type.lower() == "poly"):
			self.parent._betterBind(wx.EVT_INIT_DIALOG, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		else:
			warnings.warn(f"Add {self.type} to setFunction_init() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_preMoveSash(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		"""Changes the function that runs when the object is first created."""

		if (self.type.lower() == "double"):
			self.parent._betterBind(wx.EVT_SPLITTER_SASH_POS_CHANGING, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		else:
			warnings.warn(f"Add {self.type} to setFunction_preMoveSash() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_postMoveSash(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		"""Changes the function that runs when the object is first created."""

		if (self.type.lower() == "double"):
			self.parent._betterBind(wx.EVT_SPLITTER_SASH_POS_CHANGED, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
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
				newValue = ast.literal_eval(re.sub("^['\"]|['\"]$", "", newValue))

			if (newValue != None):
				self.thing.SetSashPosition(newValue)
		else:
			warnings.warn(f"Add {self.type} to setSashPosition() for {self.__repr__()}", Warning, stacklevel = 2)

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

			handle._build(kwargs)

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

	def _build(self, argument_catalogue):
		"""Determiens which build system to use for this handle."""

		def _build_notebook():
			"""Builds a wx notebook object."""
			nonlocal self, argument_catalogue

			flags, tabSide, reduceFlicker, fixedWidth, padding, buildSelf = self._getArguments(argument_catalogue, ["flags", "tabSide", "reduceFlicker", "fixedWidth", "padding", "self"])
			initFunction, postPageChangeFunction, prePageChangeFunction, multiLine = self._getArguments(argument_catalogue, ["initFunction", "postPageChangeFunction", "prePageChangeFunction", "multiLine"])

			size, position = self._getArguments(argument_catalogue, ["size", "position"])


			#Configure Flags            
			flags, x, border = self._getItemMod(flags)

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

			myId = self._getId(argument_catalogue)

			#Create notebook object
			self.thing = wx.Notebook(self.parent.thing, id = myId, size = size, pos = position, style = eval(flags, {'__builtins__': None, "wx": wx}, {}))

			#Bind Functions
			if (initFunction != None):
				initFunctionArgs, initFunctionKwargs = self._getArguments(argument_catalogue, ["initFunctionArgs", "initFunctionKwargs"])
				self.setFunction_init(initFunction, initFunctionArgs, initFunctionKwargs)
			
			if (prePageChangeFunction != None):
				prePageChangeFunctionArgs, prePageChangeFunctionKwargs = self._getArguments(argument_catalogue, ["prePageChangeFunctionArgs", "prePageChangeFunctionKwargs"])
				self.setFunction_prePageChange(initFunction, initFunctionArgs, initFunctionKwargs)

			if (postPageChangeFunction != None):
				postPageChangeFunctionArgs, postPageChangeFunctionKwargs = self._getArguments(argument_catalogue, ["postPageChangeFunctionArgs", "postPageChangeFunctionKwargs"])
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

		def _build_auiNotebook():
			"""Builds a wx auiNotebook object."""
			nonlocal self, argument_catalogue

			flags, buildSelf = self._getArguments(argument_catalogue, ["flags", "self"])
			initFunction, postPageChangeFunction, prePageChangeFunction = self._getArguments(argument_catalogue, ["initFunction", "postPageChangeFunction", "prePageChangeFunction"])

			tabSide, tabSplit, tabMove, tabBump = self._getArguments(argument_catalogue, ["tabSide", "tabSplit", "tabMove", "tabBump"])
			tabSmart, tabOrderAccess, tabFloat = self._getArguments(argument_catalogue, ["tabSmart", "tabOrderAccess", "tabFloat"])
			addScrollButton, addListDrop, addCloseButton = self._getArguments(argument_catalogue, ["addScrollButton", "addListDrop", "addCloseButton"])
			closeOnLeft, middleClickClose = self._getArguments(argument_catalogue, ["closeOnLeft", "middleClickClose"])
			fixedWidth, drawFocus = self._getArguments(argument_catalogue, ["fixedWidth", "drawFocus"])

			#Create Styles
			if (tabSide != None):
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

			if (addListDrop != None):
				if (addListDrop):
					style += "|wx.lib.agw.aui.AUI_NB_WINDOWLIST_BUTTON"
				else:
					style += "|wx.lib.agw.aui.AUI_NB_USE_IMAGES_DROPDOWN"

			if (addCloseButton != None):
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
			if (self.myWindow.auiManager == None):
				self.myWindow.auiManager = handle_AuiManager(self, self.myWindow)#, reduceFlicker = reduceFlicker)
				self._build(locals())

			self.myWindow.auiManager.addPane(self)
		
		#########################################################

		self._preBuild(argument_catalogue)

		if (self.type.lower() == "notebook"):
			_build_notebook()
		elif (self.type.lower() == "auinotebook"):
			_build_auiNotebook()
		else:
			warnings.warn(f"Add {self.type} to _build() for {self.__repr__()}", Warning, stacklevel = 2)

		self._postBuild(argument_catalogue)

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
			self.parent._betterBind(wx.EVT_INIT_DIALOG, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		else:
			warnings.warn(f"Add {self.type} to setFunction_init() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_prePageChange(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		"""Changes the function that runs when the page begins to change."""

		if (self.type.lower() == "notebook"):
			self.parent._betterBind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		else:
			warnings.warn(f"Add {self.type} to setFunction_prePageChange() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_postPageChange(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		"""Changes the function that runs when the page has finished changing."""

		if (self.type.lower() == "notebook"):
			self.parent._betterBind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
		else:
			warnings.warn(f"Add {self.type} to setFunction_postPageChange() for {self.__repr__()}", Warning, stacklevel = 2)

	def setFunction_rightClick(self, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None):
		if (self.type.lower() == "notebook"):
			self._betterBind(wx.EVT_RIGHT_DOWN, self.thing, myFunction, myFunctionArgs, myFunctionKwargs)
			for handle in self[:]:
				handle.setFunction_rightClick(myFunction = myFunction, myFunctionArgs = myFunctionArgs, myFunctionKwargs = myFunctionKwargs)
		else:
			warnings.warn(f"Add {self.type} to setFunction_rightClick() for {self.__repr__()}", Warning, stacklevel = 2)

	def addPage(self, text = None, panel = {}, sizer = {},
		insert = None, default = False, icon_path = None, icon_internal = False,

		hidden = False, enabled = True, maxSize = None, minSize = None, toolTip = None, 
		label = None, parent = None, handle = None):
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
			kwargs = locals()
			kwargs["parent"] = self
			handle._build(kwargs)
			handleList.append(handle)

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
			self._finalNest(handle)

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

	def _build(self, argument_catalogue):
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

		Example Input: _build(0)
		Example Input: _build("page_1")
		Example Input: _build(0, "Lorem")
		Example Input: _build([0, 1], "Lorem")
		Example Input: _build([0, 1], ["Lorem", "Ipsum"])
		Example Input: _build(0, "Lorem", insert = 2)
		Example Input: _build(0, "Lorem", select = True)
		"""

		self._preBuild(argument_catalogue)

		text, panel, sizer = self._getArguments(argument_catalogue, ["text", "panel", "sizer"])

		if (isinstance(self.parent, handle_Window)):
			self.myWindow = self.parent
		else:
			self.myWindow = self.parent.myWindow
		self.index = len(self.parent) - 1

		#Setup Panel
		panel["parent"] = self.parent
		self.myPanel = self._readBuildInstructions_panel(self, 0, panel)

		#Setup Sizer
		sizer["parent"] = self.myPanel
		self.mySizer = self._readBuildInstructions_sizer(self, 0, sizer)

		self.myPanel.nest(self.mySizer)

		self._finalNest(self.myPanel)

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
			icon_path, icon_internal = self._getArguments(argument_catalogue, ["icon_path", "icon_internal"])
			if (icon_path != None):
				self.icon = self._getImage(icon_path, icon_internal)
			else:
				self.icon = None
				self.iconIndex = None

		self._postBuild(argument_catalogue)

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
			self._betterBind(wx.EVT_RIGHT_DOWN, self.myPanel.thing, myFunction, myFunctionArgs, myFunctionKwargs)
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
		def __init__(self, parent, root = None, redirect = False, filename = None, useBestVisual = False, clearSigInt = True, newMainLoop = None):
			"""Needed to make the GUI work."""

			self.root = root
			self.parent = parent
			self.newMainLoop = newMainLoop
			wx.App.__init__(self, redirect = redirect, filename = filename, useBestVisual = useBestVisual, clearSigInt = clearSigInt)

		def OnInit(self):
			"""Needed to make the GUI work.
			Single instance code modified from: https://wxpython.org/Phoenix/docs/html/wx.SingleInstanceChecker.html
			"""

			#Account for multiple instances of the same app
			if (self.root != None):
				if (self.root.oneInstance):
					#Ensure only one instance per user runs
					self.root.oneInstance_name = f"SingleApp-{wx.GetUserId()}"
					self.root.oneInstance_instance = wx.SingleInstanceChecker(self.root.oneInstance_name)

					if self.root.oneInstance_instance.IsAnotherRunning():
						wx.MessageBox("Cannot run multiple instances of this program", "Runtime Error")
						return False

			if (self.newMainLoop != None):
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

class Controller(Utilities, CommonEventFunctions):
	"""This module will help to create a simple GUI using wxPython without 
	having to learn how to use the complicated program.
	"""

	def __init__(self, debugging = False, best = False, oneInstance = False, allowBuildErrors = None, 
		checkComplexity = True, startInThread = False, newMainLoop = None, printMakeVariables = False):
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

		Example Input: Controller()
		Example Input: Controller(debugging = True)
		Example Input: Controller(debugging = "log.txt")  
		Example Input: Controller(oneInstance = True)
		Example Input: Controller(startInThread = True)
		"""
		super(Controller, self).__init__()

		#Initialize Inherited classes
		Utilities.__init__(self)
		CommonEventFunctions.__init__(self)

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

		self.exiting = False
		self.finishing = False
		self.loggingPrint = False
		self.old_stdout = sys.stdout.write
		self.old_stderr = sys.stderr.write

		#Record Address
		self._setAddressValue([id(self)], {None: self})

		#Used to pass functions from threads
		self.threadQueue = _ThreadQueue()

		#Create the wx app object
		self.app = MyApp(parent = self, startInThread = startInThread, newMainLoop = newMainLoop)

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
		representation = f"Controller(id = {id(self)}"

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
		if (traceback != None):
			if (self.allowBuildErrors == None):
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
		return _Iterator(nestedList)

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
		parent = None, handle = None):
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
		handle.type = "Frame"
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
		parent = None, handle = None):
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
		handle.type = "Dialog"
		handle._build(locals())
		self._finalNest(handle)

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

		self.finishing = True

		#Make sure all things are nested
		nestCheck(nestingCatalogue)
		
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

			self._logPrint(args, fileName = fileName, timestamp = timestamp, **kwargs)

			#Run the normal print function
			return self.old_stdout(*args)

		def new_stderr(*args, fileName = "error_log.log", timestamp = True, **kwargs):
			"""Overrides the stderr function to also log the error information.

			fileName (str)   - The filename for the log
			timestamp (bool) - Determines if the timestamp is added to the log
			"""
			nonlocal self

			self._logError(args, fileName = fileName, timestamp = timestamp, **kwargs)

			#Run the normal stderr function
			return self.old_stderr(*args)

		if (not self.loggingPrint):
			self.loggingPrint = True

			sys.stdout.write = new_stdout
			sys.stderr.write = new_stderr
		else:
			warnings.warn(f"Already logging cmd outputs for {item.__repr__()}", Warning, stacklevel = 2)

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
import pubsub.core.callables
class _mp_CallArgsInfo:
	"""Overridden to allow any valid combination of args and kwargs."""

	class NO_DEFAULT:
		def __repr__(self):
			return "NO_DEFAULT"

	def __init__(self, func, firstArgIdx, ignoreArgs = None):
		args, varParamName, varOptParamName, argsDefaults, kwargs, kwargsDefaults, annotations = inspect.getfullargspec(func)
		self.allArgs = {}

		if (argsDefaults != None):
			argsDefaults_startsAt = len(args) - len(argsDefaults) - 1
		for i, variable in enumerate(args):
			if ((i == 0) and (firstArgIdx > 0)):
				continue #skip self

			if ((argsDefaults == None) or (i < argsDefaults_startsAt)):
				self.allArgs[variable] = self.NO_DEFAULT()
			else:
				self.allArgs[variable] = argsDefaults[i - argsDefaults_startsAt - 1]

		self.allKwargs = {}
		for variable in kwargs:
			if ((kwargsDefaults == None) or (variable not in kwargsDefaults)):
				self.allKwargs[variable] = self.NO_DEFAULT()
			else:
				self.allKwargs[variable] = kwargsDefaults[variable]

		self.acceptsAllKwargs = (varOptParamName is not None)
		self.acceptsAllUnnamedArgs = (varParamName is not None)
		self.allParams = [*self.allArgs.keys(), *self.allKwargs.keys()]

		if ignoreArgs:
			for var_name in ignoreArgs:
				if (var_name in self.allArgs):
					del self.allArgs[var_name]
				elif (var_name in self.allKwargs):
					del self.allKwargs[var_name]

			if (varOptParamName in ignoreArgs):
				self.acceptsAllKwargs = False
			if (varParamName in ignoreArgs):
				self.acceptsAllUnnamedArgs = False

		self.numRequired = sum([1 for value in [*self.allArgs.values(), *self.allKwargs.values()] if (isinstance(value, self.NO_DEFAULT))])
		assert self.numRequired >= 0

		# if listener wants topic, remove that arg from args/defaultVals
		self.autoTopicArgName = None
		self.__setupAutoTopic()

	def getAllArgs(self):
		return tuple(self.allParams)

	def getOptionalArgs(self):
		return tuple([key for key, value in [*self.allArgs.items(), *self.allKwargs.items()] if (not isinstance(value, self.NO_DEFAULT))])

	def getRequiredArgs(self):
		return tuple([key for key, value in [*self.allArgs.items(), *self.allKwargs.items()] if (isinstance(value, self.NO_DEFAULT))])

	def __setupAutoTopic(self):
		for variable, value in {**self.allArgs, **self.allKwargs}.items():
			if (value == pubsub.core.callables.AUTO_TOPIC):
				del self.allArgs[variable]
				return

pubsub.core.callables.CallArgsInfo = _mp_CallArgsInfo

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

		dataCatalogue = self._getDataCatalogue()
		return self._get(dataCatalogue, key, returnExists = True)

		# if (key in self[:]):
		# 	return True
		# else:
		# 	if (hasattr(self, "_catalogue_variable") and (self._label_variable != None)):
		# 		for item in self[:]:
		# 			if (hasattr(item, self._label_variable)):
		# 				if (key == getattr(item, self._label_variable)):
		# 					return True
		# return False

	def __iter__(self):
		if (hasattr(self, "_catalogue_variable") and (self._catalogue_variable != None)):
			if (isinstance(self._catalogue_variable, Controller)):
				return self._catalogue_variable.__iter__()

		dataCatalogue = self._getDataCatalogue()
		return _Iterator(dataCatalogue)

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
					dataCatalogue = self._catalogue_variable.labelCatalogue #This might be causing some bugs with slices ex: self[:]
				else:
					dataCatalogue = self._catalogue_variable
		else:
			dataCatalogue = {}

		return dataCatalogue

	def _get(self, itemCatalogue, itemLabel = None, returnExists = False):
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

		if (returnExists):
			return answer != None

		if (answer != None):
			if (isinstance(answer, (list, tuple, range))):
				if (len(answer) == 1):
					answer = answer[0]
			return answer

		errorMessage = f"There is no item labled {itemLabel} in the data catalogue for {self.__repr__()}"
		raise KeyError(errorMessage)

	def getValue(self, variable, order = True, includeMissing = True, exclude = [], sortNone = False, reverse = False, getFunction = None):
		"""Returns a list of all values for the requested variable.
		Special thanks to Andrew Clark for how to sort None on https://stackoverflow.com/questions/18411560/python-sort-list-with-none-at-the-end

		variable (str) - what variable to retrieve from all rows
		order (str) - By what variable to order the items
			- If variable does not exist: Will place the item at the end of the list with sort() amongst themselves
			- If True: Will use the python list function sort()
			- If False: Will not sort returned items
			- If None: Will not sort returned items
		sortNone (bool) - Determines how None is sorted
			- If True: Will place None at the beginning of the list
			- If False: Will place None at the end of the list
			- If None: Will remove all instances of None from the list

		Example Input: getValue("naed")
		Example Input: getValue(self.easyPrint_selectBy)
		Example Input: getValue("naed", "defaultOrder")
		Example Input: getValue("barcode", sortNone = None)
		"""

		if (not isinstance(exclude, (list, tuple, range))):
			exclude = [exclude]
		if (getFunction == None):
			getFunction = getattr

		if ((order != None) and (not isinstance(order, bool))):
			data = [getFunction(item, variable) for item in self.getOrder(order, includeMissing = includeMissing, 
				getFunction = getFunction, sortNone = sortNone, exclude = exclude) if (item not in exclude)]
		else:
			data = [getFunction(item, variable) for item in self if (item not in exclude)]

			if ((order != None) and (isinstance(order, bool)) and order):
				data = sorted(filter(lambda item: True if (sortNone != None) else (item != None), data), 
					key = lambda item: (((item is None)     if (reverse) else (item is not None)) if (sortNone) else
										((item is not None) if (reverse) else (item is None)), item), 
					reverse = reverse)

		return data

	def getOrder(self, variable, includeMissing = True, exclude = [], sortNone = False, reverse = False, getFunction = None):
		"""Returns a list of children in order according to the variable given.
		Special thanks to Andrew Dalke for how to sort objects by attributes on https://wiki.python.org/moin/HowTo/Sorting#Key_Functions

		variable (str) - what variable to use for sorting
		includeMissing (bool) - Determiens what to do with children who do not have the requested variable
		getFunction (function) - What function to run to get the value of this variable where the args are [handle, variable]
			- If None: will use getattr

		Example Input: getOrder("order")
		Example Input: getOrder("order", includeMissing = False, sortNone = None)
		Example Input: getOrder("order", getFunction = lambda item, variable: getattr(item, variable.name))
		"""

		if (not isinstance(exclude, (list, tuple, range))):
			exclude = [exclude]
		if (getFunction == None):
			getFunction = getattr

		handleList = sorted(filter(lambda item: hasattr(item, variable) and (item not in exclude) and ((sortNone != None) or (getFunction(item, variable) != None)), self), 
			key = lambda item: (((getFunction(item, variable) is None)     if (reverse) else (getFunction(item, variable) is not None)) if (sortNone) else
								((getFunction(item, variable) is not None) if (reverse) else (getFunction(item, variable) is None)), getFunction(item, variable)), 
			reverse = reverse)
		
		if (includeMissing):
			handleList.extend([item for item in self if (not hasattr(item, variable) and (item not in exclude))])

		return handleList

	def getHandle(self, where = None, exclude = []):
		"""Returns a list of children whose variables are equal to what is given.

		where (dict) - {variable (str): value (any)}
			- If None, will not check the values given

		Example Input: getHandle()
		Example Input: getHandle({"order": 4})
		Example Input: getHandle(exclude = ["main"])
		"""

		if (not isinstance(exclude, (list, tuple, range))):
			exclude = [exclude]

		handleList = []
		for handle in self:
			if (handle not in exclude):
				if ((where != None) and (len(where) != 0)):
					for variable, value in where.items():
						if (hasattr(handle, variable) and (getattr(handle, variable) == value)):
							continue
						break
					else:
						handleList.append(handle)
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

	def getNumber(self, itemList = None, depthMax = None, _currentDepth = 1):
		"""Returns the number of items in 'itemList'.
		Special thanks to stonesam92 for how to check nested items on https://stackoverflow.com/questions/27761463/how-can-i-get-the-total-number-of-elements-in-my-arbitrarily-nested-list-of-list

		itemList (any)      - What to check the number of
			- If None: Will return the number of children in self
		_currentDepth (int) - How many recursions have been done on this branch
		depthMax (int)      - The max number of recursions to do
			- If None: Will not limit the number of recursions

		Example Input:: getNumber()
		Example Input:: getNumber([1, 2, 3])
		Example Input:: getNumber({1: 2, 3: {4: 5}})
		"""

		if ((depthMax != None) and (_currentDepth > depthMax)):
			return 0
		elif (isinstance(itemList, str)):
			return 1
		elif (isinstance(itemList, dict)):
			count = 0
			for key, value in itemList.items():
				count += 1 + self.getNumber(value, depthMax = depthMax, _currentDepth = _currentDepth + 1)
			return count
		elif (isinstance(itemList, (list, tuple, range)) or hasattr(itemList, '__iter__')):
			return sum(self.getNumber(item, depthMax = depthMax, _currentDepth = _currentDepth + 1) for item in itemList)
		else:
			return 1
