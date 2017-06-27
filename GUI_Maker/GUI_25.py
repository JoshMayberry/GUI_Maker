#Version 3.4.0

#TO DO
# - Add 'hideWindow', etc. to myFrame class; Example Input: myFrame.hideWindow()

#IMPORT CONTROLS
##Here the user can turn on and off specific parts of the module, 
##which will reduce the overall size of a generated .exe.
##To do so, comment out the block of import statements
##WARNING: If you turn off a feature, make sure you dont try to use it.

#Import standard elements to interact with the computer
import os
import sys
import time
import ctypes


#Import wxPython elements to create GUI
import wx
import wx.adv
import wx.grid
import wx.lib.masked
import wx.lib.splitter
import wx.lib.agw.floatspin
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
import Cryptodome.Random
import Cryptodome.Cipher.AES
import Cryptodome.PublicKey.RSA
import Cryptodome.Cipher.PKCS1_OAEP


#Import communication elements for talking to other devices such as printers, the internet, a raspberry pi, etc.
import serial
import socket


#Import barcode software for drawing and decoding barcodes
import elaphe


#Import multi-threading to run functions as background processes
import queue
import threading
import subprocess


#Import needed support modules
import re
import atexit
import netaddr
import PIL.Image


#Import user-defined modules
# from .ExcelManipulator_6 import Excel #Used to make wxGrid objects interactable with excel


#Database Interaction
from .DatabaseAPI_9 import Database


#Required Modules
##py -m pip install
	#wxPython_Phoenix
	#openpyxl
	#numpy
	#matplotlib
	#py2exe
	#pillow
	#pycryptodomex
	#atexit
	#netaddr
	#elaphe
	#python3-ghostscript "https://pypi.python.org/pypi/python3-ghostscript/0.5.0#downloads"
	#sqlite3

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
idGen = 2000 #Used to generate individual identifyers
idCatalogue = {} #Used to keep track of important IDs
valueQueue = {} #Used to keep track of values the user wants to have
shownWindowsList = [] #Used to keep track of which windows are being shown


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
				myFunctionList, myFunctionArgsList, myFunctionKwargsList = GUI.Utilities.formatFunctionInputList(self, myFunctionList, myFunctionArgsList, myFunctionKwargsList)
				
				#Run each function
				for i, myFunction in enumerate(myFunctionList):
					#Skip empty functions
					if (myFunction != None):
						myFunctionEvaluated, myFunctionArgs, myFunctionKwargs = GUI.Utilities.formatFunctionInput(self, i, myFunctionList, myFunctionArgsList, myFunctionKwargsList)
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
		name (str)     - The thread name. By default, a unique name is constructed of the form “Thread-N” where N is a small decimal number.
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
		global shownWindowsList

		if (self.shown):
			#Wait until the window is shown to start
			while True:
				#Check if the thread should still run
				if (self.stopEvent.is_set()):
					return

				#Check if the window is shown yet
				if (self.window in shownWindowsList):
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
		Code from dynamatt on http://stackoverflow.com/questions/1205383/listing-serial-com-ports-on-windows.

		Example Input: getAllComPorts()
		"""

		ports = list(serial.tools.list_ports.comports())
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
			print("ERROR: There is no COM port object", which)
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
			print("ERROR: There is no Ethernet object", which)
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

		def open(self, address, port = 10000, error = False):
			"""Opens the socket connection.

			address (str) - The ip address/website you are connecting to
			port (int)    - The socket port that is being used
			error (bool)  - Determines what happens if an error occurs
				If True: If there is an error, returns an error indicator. Otherwise, returns a 0
				If False: Raises an error exception

			Example Input: open("www.example.com")
			"""

			#Remove any white space
			address = re.sub(" ", "", address)

			#Open the port
			if (error):
				error = self.mySocket.connect_ex((address, port))
				return error
			else:
				self.mySocket.connect((address, port))

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
				print("ERROR: Buffer size must be a power of 2, not", bufferSize)
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
				print("ERROR: Buffer size must be a power of 2, not", bufferSize)
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
				print("ERROR: There is no client", clientIp, "for this server")

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

class GUI(Communication, Security):
	"""This module will help to create a simple GUI using wxPython without 
	having to learn how to use the complicated program.

	The code contained in this module was generated using wxFormBuilder. 
	This can be found at http://www.wxformbuilder.org/. 
	The tutorials from http://zetcode.com/wxpython/ were also used.
	_________________________________________________________________________

	LOADING THIS MODULE
	It is recommended that at the top of your program you import this module
	in the following way:
		from GUI_15 import GUI

	CREATE A SEPARATE FUNCTION FOR EACH FRAME
	It is recommended that in your program, you create a function for building
	just one frame. Inside that function do the following in this order:
		(1) gui.createWindow(title) - Create the window first.
		(2) gui.setWindowSize(windowIndex, x, y) - Set the size of the window.
		(3) gui.typicalWindowSetup(windowIndex) - Adds common features to the window.
		(4) myFrame = gui.getWindow(windowIndex) - Allows you to add things to the window.
		(5) myFrame.addSizerGrid(rows, columns, windowIndex) - Add a sizer before adding widgets. 
			Can be any type of sizer.
		(6) myFrame.addText(title, windowIndex, flags = "ac") - Add all of your widgets.
			Can be any types of widgets
	When you are finished adding widgets and sizers to the frame, you're done!


	ADDING WIDGETS TO SIZERS
	Each sizer has a number of rows and columns, usually specified by you.
	Each widget that you add is placed in the highest empty row.
	Widgets fill rows from left to right.

	This means that if you have a sizer with 2 rows and 3 columns, the first
	three widgets added will be on the top row with the first on the far left,
	the second in the middle, and the third on the far right.
	If a fourth widget is added, it will be on the second row on the far left.

	If you try to add a seventh widget to the sizer, you will generate an error.
	This is because your sizer only has 6 slots for widgets.
	The number of slots a sizer has is the product of the number of rows and columns.


	ADDING A SIZER TO A SIZER
	If you add a sizer to a sizer, then it will take up the next available slot
	in the same way that widgets do. To add a sizer, do things in this order:
		(1) myFrame.addSizerGrid(9, 2, 1) - Add the sizer to the sizer
		(2) Add widgets like normal. These widgets will begin filling in
			the new sizer.
		When you are finished adding widgets to the new sizer:
		(3) myFrame.sizerInSizer(1, 0) - Tell the GUI module that you are finished
			editing the new sizer. 

	More things can be added to this new sizer after step 3 and the sizerInSizer 
	function can be called at any time (just as long as they are called).
	Despite this, it is recommended that you do things in the order given above.
	This will make it easier to (1) follow your logic, (2) debug, and (3) prevent
	errors or bugs.


	TRIGGERING FUNCTIONS IN WITH THE GUI USING WIDGETS
	Likely the main reason you want to create a GUI in the first place is to easily
	run functions you have created. This can be done with buttons, drop boxes, etc.
	Here are some examples of buttons that will trigger functions when interacted with.
		myFrame.addButton("Next", gui.onSwitchWindow, 1, myFunctionArgs = [0, 1])
		myFrame.addButton("Do Stuff", self.myFunction, 0, myFunctionArgs = [1, 2, 3])
		myFrame.addButton("Exit", "self.onExit", 0)
		myFrame.addListDrop(["Good", "Bad", "Unknown"], "self.onQueueValue", 1, myLabel = "quality", myFunctionArgs = ["quality"])
		myFrame.addInputBox("self.onQueueValue", 1, myLabel = "partName", myFunctionArgs = ["partName"])
	For more information, look up the documentation for the widget you wish to use.


	TELLING THE GUI MODULE TO ACTUALLY BUILD THE FRAMES
	If you do not run the functions to create the creames as mentioned above,
	then they will not be built in the first place. For this reason,
	it is recommended to run all window building functions (1) at the start of
	the program, and (2) as soon as the program starts.
	

	FINISHING THE GUI
	When you are all done seting up the GUI, do the following in this order:
		(1) gui.showWindow(0) - Show the user the first window.
		(2) gui.finish() - Tell the GUI module you are finished creating the GUI.
			If you try to add anything else to the GUI, it will not be added.
			This is why all of the functions for each frame need to be run before this.


	CLOSING THE GUI CORRECTLY
	If you want to close down your program inside a function, simply use the following code:
		self.gui.exit()
	_________________________________________________________________________

	USING GUI PACKAGES YOURSELF
	In order to use a package other than GUI (such as Utilities), be sure to pass in a variable for "self". 
	If the function using the package is inside a class, then this will be done automatically. 
	If the function using the package is not in a class, then you will need to pass it yourself.
	Example of an in-class function using the package 'Utilities':
		thing = GUI.Utilities.getObjectWithEvent(event)
	Example of a non-class function using the package 'Utilities':
		thing = GUI.Utilities.getObjectWithEvent(None, event)
	If this rule is not followed, the functions will not work for you.
	"""

	def __init__(self, debugging = False, best = False):
		"""Defines the internal variables needed to run.

		debugging (bool) - If True: The cmd window will appear and show debugging information. Also closes with [ctrl]+[c]
						   If string type: The pathway to a log file that will record debugging information
						   If False: No cmd or logfile will be used.
		best (bool)      - If True: The app will try to use the best visual system if more than one is available

		Example Input: GUI()
		Example Input: GUI(True)
		Example Input: GUI("log.txt")  
		"""
		super(GUI, self).__init__()
		Communication.__init__(self)
		Security.__init__(self)


		#Determine if we are in debug mode
		if (type(debugging) != str):
			self.debugging = debugging
		else:
			self.debugging = True

		#Setup Internal Variables
		self.frameDict = {} #A dictionary that contains all the windows made for the gui. {windowNumber: [myFrame, title]}

		#Used to pass functions from threads
		self.threadQueue = ThreadQueue()
		
		#Create the wx app object
		self.app = wx.App()
		
	def createWindow(self, windowNumber, title, myLabel = None, xSize = 500, ySize = 300, 
		initFunction = None, initFunctionArgs = None, initFunctionKwargs = None,
		delFunction = None, delFunctionArgs = None, delFunctionKwargs = None, 
		idleFunction = None, idleFunctionArgs = None, idleFunctionKwargs = None, 
		tabTraversal = True, stayOnTop = False, floatOnParent = False, endProgram = True,
		resize = True, minimize = True, maximize = True, close = True, 
		panel = True , autoSize = True, icon = None, internal = False, topBar = True):
		"""Creates a new window.
		Returns the index number of the created window.

		windowNumber (int) - What this window is catalogued as. Can be a string
		title (str)        - The text that appears on top of the window
		myLabel (str)      - What the window's frame is called in the idCatalogue
		xSize (int)        - The width of the window
		ySize (int)        - The height of the window
		
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
		
		Example Input: createWindow(0, "Example")
		"""

		#Create window
		myFrame = self.Window(None, title, myLabel = myLabel, xSize = xSize, ySize =ySize, 
			initFunction = initFunction, initFunctionArgs = initFunctionArgs, initFunctionKwargs = initFunctionKwargs,
			delFunction = delFunction, delFunctionArgs = delFunctionArgs, delFunctionKwargs = delFunctionKwargs, 
			idleFunction = idleFunction, idleFunctionArgs = idleFunctionArgs, idleFunctionKwargs = idleFunctionKwargs, 
			tabTraversal = tabTraversal, stayOnTop = stayOnTop, floatOnParent = floatOnParent, endProgram = endProgram,
			resize = resize, minimize = minimize, maximize = maximize, close = close, panel = panel , autoSize = autoSize,
			icon = icon, internal = internal, topBar = topBar)   

		#Catalogue Window
		self.frameDict[windowNumber] = [myFrame, title] #Save Window Address

		#Return the window
		return myFrame

		# #Return window number
		# return len(self.frameDict) - 1

	def setWindowSize(self, which, x, y):
		"""Re-defines the size of the window.

		which (int) - The index number of the window. Can be the title of the window
		x (int)     - The width of the window
		y (int)     - The height of the window

		Example Input: setWindowSize(0, 350, 250)
		"""

		#Change the frame size
		myFrame = self.getWindow(which)
		myFrame.SetSize((x, y))

	def setMinimumFrameSize(self, which, size = (100, 100)):
		"""Sets the minimum window size for the user
		Note: the program can still explicity change the size to be smaller by using setWindowSize().

		which (int)      - The index number for the window in the window catalogue
		size (int tuple) - The size of the window. (length, width)

		Example Input: setMinimumFrameSize(0)
		Example Input: setMinimumFrameSize(0, (200, 100))
		"""

		#Get the frame
		myFrame = self.getWindow(which)

		#Set the size property
		myFrame.SetMinSize(size)

	def setMaximumFrameSize(self, size = (900, 700)):
		"""Sets the maximum window size for the user
		Note: the program can still explicity change the size to be smaller by using setWindowSize().

		which (int)      - The index number for the window in the window catalogue
		size (int tuple) - The size of the window. (length, width)

		Example Input: setMaximumFrameSize(0)
		Example Input: setMaximumFrameSize(0, (700, 300))
		"""

		#Get the frame
		myFrame = self.getWindow(which)

		#Set the size property
		myFrame.SetMaxSize(size)

	def setAutoWindowSize(self, which, minimum = None):
		"""Re-defines the size of the window.

		which (int)    - The index number of the window. Can be the title of the window
		minimum (bool) - Whether the window will be sized to the minimum best size or the maximum 
						 If None: The auto size will not be set as a minimum or maximum.

		Example Input: setAutoWindowSize(0)
		Example Input: setAutoWindowSize(0, True)
		Example Input: setAutoWindowSize(0, False)
		"""

		#Get the frame
		myFrame = self.getWindow(which)

		#Determine best size
		size = myFrame.GetBestSize()

		#Set the size
		if (minimum != None):
			if (minimum):
				myFrame.SetMinSize(size)
			else:
				myFrame.SetMaxSize(size)

	def setWindowTitle(self, which, title):
		"""Re-defines the title of the window.

		which (int) - The index number of the window. Can be the previous title of the window
		title (str) - What the new title is

		Example Input: setWindowTitle(0, "test")
		"""
		myFrame = self.getWindow(which)

		myFrame.SetTitle(title)

	def getWindow(self, which):
		"""Returns a window object when given the corresponding frame number.

		which (int) - The index number of the window. Can be the title as a string

		Example Input: getWindow(0)
		Example Input: getWindow("test")
		"""

		if (type(which) == str):
			myFrame = wx.FindWindowByName(which)

		elif (type(which) == int):
			myFrame = self.frameDict[which][0]

		else:
			which = self.getWindowIndex(which)
			myFrame = self.frameDict[which][0]

		return myFrame

	def getWindowIndex(self, which):
		"""Returns the index of a window when given a string.
		If there is no window by that name, it will return None.
		Can be used to verify

		which (str) - The title as a string. Can be a wxWindow object

		Example Input: getWindowIndex("test")
		"""

		#Given the title as a string
		if (type(which) == str):
			window = wx.FindWindowByName
			for i, item in enumerate(list(self.frameDict.values())):
				if (item[0] == window):
					return i


		#Given a wxWindow object
		else:
			if (which in self.frameDict):
				for i, item in enumerate(list(self.frameDict.values())):
					if (item[0] == which):
						return i

		print("ERROR: Window not found")
		return None

	def typicalWindowSetup(self, which, skipMenu = False, skipStatus = False, skipPopup = False, skipMenuExit = False):
		"""Adds the things a window typically needs.
			- Menu Bar with exit button
			- Status Bar
			- Popup Menu
			- Border
		Sizer number 0 is the border. Sizer 1 is the hole for your GUI.
		So, start on sizer 2 instead of sizer 0 if this is used. 

		which (int)       - The index number of the window. Can be the title of the window
		skipMenu (bool)   - If True: No top bar menu will be added
		skipStatus (bool) - If True: No status bar will be added
		skipPopup (bool)  - If True: No popup menu will be added

		Example Input: typicalWindowSetup(0)
		"""

		#Get Frame
		myFrame = self.getWindow(which)

		#Add Menu Bar
		if (not skipMenu):
			myFrame.addMenuBar()
			if (not skipMenuExit):
				myFrame.addMenu(0, "&File")
				myFrame.addMenuItem(0, "&Exit", myFunction = "self.onExit", icon = "quit", internal = True)

		#Add Status Bar
		if (not skipStatus):
			myFrame.addStatusBar()
			myFrame.setStatusText("Ready")

		#Add Popup Menu
		if (not skipPopup):
			myFrame.createPopupMenu()
			myFrame.addPopupMenuItem("&Minimize", "self.onMinimize")
			myFrame.addPopupMenuItem("Maximize", "self.onMaximize")
			myFrame.addPopupMenuItem("Close", "self.onExit")
		
	def hideWindow(self, which):
		"""Hides the window from view, but does not close it.
		Note: This window continues to run and take up memmory. Local variables are still active.

		which (int) - The index number of the window. Can be the title of the window

		Example Input: hideWindow(0)
		"""
		global shownWindowsList

		myFrame = self.getWindow(which)
		myFrame.Hide()

		if (myFrame in shownWindowsList):
			shownWindowsList.remove(myFrame)
		else:
			print("ERROR: Window", which, "is already hidden.")
		
	def onHideWindow(self, event, which, *args, **kwargs):
		"""Hides the window from view, but does not close it.
		Note: This window continues to run and take up memmory. Local variables are still active.

		which (int) - The index number of the window. Can be the title of the window

		Example Input: onHideWindow(0)
		"""
		
		self.hideWindow(which)
			
		event.Skip()

	def closeWindow(self, which):
		"""Closes the window. This frees up the memmory. Local variables will be lost.

		which (int) - The index number of the window. Can be the title of the window

		Example Input: closeWindow(0)
		"""
		global shownWindowsList

		myFrame = self.getWindow(which)
		myFrame.Destroy()

		if (myFrame in shownWindowsList):
			shownWindowsList.remove(myFrame)
		else:
			print("ERROR: Window", which, "is already closed.")

	def onCloseWindow(self, event, which, *args, **kwargs):
		"""Closes the window. This frees up the memmory. Local variables will be lost.

		which (int) - The index number of the window. Can be the title of the window

		Example Input: onCloseWindow(0)
		"""
		
		self.closeWindow(which)
			
		event.Skip()

	def showWindow(self, which, autoSize = None, mainThread = False):
		"""Shows a specific window to the user.
		If the window is already shown, it will bring it to the front

		which (int)       - The index number of the window. Can be the title of the window
		autoSize (bool)   - Determines how the window will be sized
			- If True: The window size will be changed to fit the sizers within
			- If False: The window size will be what was defined when it was initially created
			- If None: The internal autosize state will be used
		mainThread (bool) - Used for multi-threading. Changes which thread calls this function
			- If True: The function will run in the main thread
			- If False: The function will run in the current thread

		Example Input: showWindow(0)
		"""
		global shownWindowsList

		if (mainThread):
			mainThread = threading.main_thread()

		myFrame = self.getWindow(which)
		myFrame.Show(True)

		if (autoSize == None):
			autoSize = myFrame.autoSize
		# myFrame.updateWindow(autoSize)

		if (myFrame not in shownWindowsList):
			shownWindowsList.append(myFrame)
		else:
			if (myFrame.IsIconized()):
				myFrame.Iconize(False)
			else:
				myFrame.Raise()

	def onShowWindow(self, event, which, autoSize = None, **kwargs):
		"""Shows a specific window to the user.

		which (int)     - The index number of the window. Can be the title of the window
		autoSize (bool) - If True: the window size will be changed to fit the sizers within
						  If False: the window size will be what was defined when it was initially created
						  If None: the internal autosize state will be used

		Example Input: onShowWindow(0)
		"""

		myFrame = self.getWindow(which)
		self.showWindow(which, autoSize)
			
		event.Skip()

	def showWindowCheck(self, which, notShown = False):
		"""Checks if a window is currently being shown to the user.

		which (int)     - The index number of the window. Can be the title of the window
		notShown (bool) - If True: checks if the window is NOT shown instead

		Example Input: showWindowCheck(0)
		"""
		global shownWindowsList

		myFrame = self.getWindow(which)

		if ((myFrame in shownWindowsList) * notShown):
			return False
		return True

	def switchWindow(self, whichFrom, whichTo, autoSize = None, hideFrom = True):
		"""Switches to another window.

		whichFrom (int) - The index number of the current window
		whichTo (int)   - The index number of the next window
		autoSize (bool) - If True: the window size will be changed to fit the sizers within
						  If False: the window size will be what was defined when it was initially created
						  If None: the internal autosize state will be used
		hideFrom (bool) - Whether to hide the current window or close it

		Example Input: switchWindow(0, 1)
		Example Input: switchWindow(0, 1, False)
		"""

		#Show next window
		self.showWindow(whichTo, autoSize)

		#Hide or close current window
		if (hideFrom):
			self.hideWindow(whichFrom)
		else:
			self.closeWindow(whichFrom)

	def onSwitchWindow(self, event, *args, **kwargs):
		"""A button event for switching from one frame to another."""

		#Unpack Input Variables
		whichFrom = args[0] #(int) - Index number for the current window
		whichTo = args[1] #(int) - Index number for the next window

		#Switch the windows
		if (len(args) > 2):
			autoSize = args[2] #bool - Whether to auto size the window or not
			self.switchWindow(whichFrom, whichTo, autoSize)
		else:
			self.switchWindow(whichFrom, whichTo)
			
		event.Skip()

	def finish(self):
		"""Run this when the GUI is finished."""

		#Take care of last minute things
		for myFrame in list(self.frameDict.values()):
			myFrame = myFrame[0]
			#Check for any window key bindings that need to happen
			if (len(myFrame.keyPressQueue) > 0):
				#Bind each key event to the window
				acceleratorTableQueue = []
				### To Do: This does not currently work with more than 1 key. Find out what is wrong. ###
				for thing, queue in myFrame.keyPressQueue.items():
					for key, contents in queue.items():

						#Bind the keys to the window
						### This is likely the issue. The event seems to be 'overwritten' by the next key ###
						myId = myFrame.newId()
						# myId = thing.GetId()
						# myFrame.Bind(wx.EVT_MENU, contents[0], id=myId)
						# myFrame.Bind(type, lambda event: handler(event, *args, **kwargs), instance)
						# print(contents[0])
						# myFrame.Bind(wx.EVT_MENU, lambda event: contents[0](event), id=eventId)
						# myFrame.Bind(wx.EVT_MENU, lambda event: contents[0](event), id = myId)
						myFrame.betterBind(wx.EVT_MENU, myFrame, contents[0], contents[1], contents[2], myId = myId, mode = 2)
						# asciiValue = myFrame.keyBind(key, thing, contents[0], myFunctionArgsList = contents[1], myFunctionKwargsList = contents[2], event = wx.EVT_MENU, myId = myId)

						#Add to accelerator Table
						acceleratorTableQueue.append((wx.ACCEL_CTRL, 83, myId))

				acceleratorTable = wx.AcceleratorTable(acceleratorTableQueue)
				myFrame.SetAcceleratorTable(acceleratorTable)

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

	#Background process handling
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

		print("@9")
		self.threadQueue.from_main_thread()

	#Etc
	def centerWindow(self, which):
		"""Centers the window on the screen.

		which (int) - The index number of the window
					  If True: All windows will be centered

		Example Input: centerWindow(0)
		Example Input: centerWindow(True)
		"""

		if (type(which) == bool):
			if (which):
				self.centerWindowAll()
				return

		myFrame = self.getWindow(which)
		myFrame.Center()

	def centerWindowAll(self):
		"""Centers all the windows on the screen.

		Example Input: centerWindowAll()
		"""

		for window in list(self.frameDict.values()):
			window[0].Center()

	def changeCursorWindow(self, which, cursorType):
		"""Changes the cursor when it is over a specific window.

		which (int)      - The index number of the window
		cursorType (str) - What the cursor will become. Only the first two letters are needed except for with the sizing cursors and "wait2".
							~ "default"  - The standard arrow cursor pointing to the left
							~ "flip"     - The standard arrow cursor pointing to the right
							~ "line"     - The text editor i-beam vertical line
							~ "question" - The standard arrow with a small question mark
							~ "wait"     - The standard hourglass or loading cursor
							~ "wait2"    - The standard arrow with a small standard hourglass or loading cursor
							~ "blank"    - No cursor image

							~ "size"     - Four arrows pointing up, down, left, and right
							~ "sizeNE"   - A diagonal arrow pointing NE and SW. Can also be "sizeSW"
							~ "sizeNW"   - A diagonal arrow pointing NW and SE. Can also be "sizeSE"
							~ "sizeN"    - A vertical arrow pointing up and down. Can also be "sizeS"
							~ "sizeE"    - A horizontal arrow pointing left and right. Can also be "sizeW"

							~ "hand"     - A hand
							~ "left"     - A hand pointing to the left
							~ "right"    - A hand pointing to the right

							~ "no"       - A no-entry sign
							~ "cross"    - A cross

							~ "target"   - A bullseye target
							~ "magnify"  - A magnifying glass
							~ "paint"    - A paint brush
							~ "pencil"   - A pencil
							~ "spray"    - A spraycan

		Example Input: changeCursorWindow(0, "magnifier")
		"""

		#Get the window
		myFrame = self.getWindow(which)

		#Determine which cursor
		cursor = GUI.Utilities.getCursorObject(cursorType)

		#Apply cursor change attribute
		myFrame.SetCursor(wx.Cursor(cursor))

	#User Friendly Functions
	def onSetObjectValue(self, event, label, newValue):
		"""Changes the value of a wxObject that is already on a shown screen.

		label (str) - A unique string associated with the object
		newValue (str) - What the new value of the object will be

		Example Input: onSetObjectValue(event, "changableText", "Lorem Ipsum")
		"""

		#Correct 'self'
		self = GUI.Utilities.getObjectWithEvent(None, event)
		parent = GUI.Utilities.getObjectParent(None, self)

		#Run the function as it should be run
		GUI.CommonEventFunctions.onSetObjectValue(parent, event, label, newValue)

		event.Skip()

	def getObjectWithEvent(self, event):
		"""Gets the object that triggered an event.

		event (CommandEvent) - The wxPython event that was triggered

		Example Input: getObjectWithEvent(event)
		"""

		#Run the function as it should be run
		thing = GUI.Utilities.getObjectWithEvent(None, event)

		return thing

	def getObjectWithLabel(self, label):
		"""Gets an object with an id label.

		label (str) - A string previously associated with an object's id; given upon the objects creation.

		Example Input: getObjectWithLabel("saveFile")
		"""

		#Run the function as it should be run
		thing = GUI.Utilities.getObjectWithLabel(GUI, label)
		
		return thing

	def getQueueValue(self, label, event = None, isType = str):
		"""Returns the value associated with the label.
		If the label does not exist, it returns None.

		label (str) - A unique string that can be used to retrieve the value
		isType (type) - What data-type to return the value as

		Example Input: getQueueValue("pi")
		Example Input: getQueueValue("pi", event)
			Example Input: getQueueValue("pi", isType = float)
		"""
		
		value = GUI.Utilities.getQueueValue(None, label, event, isType)

		return value

	def getObjectValue(self, thing, index = False, full = False):
		"""Returns the value stored in an object. Can be given a wxObject or a wxCommandEvent
		Right now, this only works when an event is passed in.

		thing (wxCommandEvent) - The event that was triggered

		Example Input: getObjectValue(thing)
		"""

		#Correct 'self'
		self = GUI.Window

		#Run the function as it should be run
		value = GUI.Utilities.getObjectValue(self, thing, index, full)

		return value

	def getObjectValueWithLabel(self, myLabel, index = False, full = False):
		"""Returns the value stored in an object when given the object's label.

		myLabel (str) - What this is called in the idCatalogue

		Example Input: getObjectValueWithLabel("myCheckBox")
		"""

		#Correct 'self'
		self = GUI.Window

		#Run the function as it should be run
		value = GUI.Utilities.getObjectValueWithLabel(self, myLabel, index, full)

		return value

	def getObjectValueWithEvent(self, event, index = False, full = False):
		"""Returns the value stored in an object when given the object's label.

		event (CommandEvent) - The wxPython event that was triggered

		Example Input: getObjectValueWithLabel(event)
		"""

		#Correct 'self'
		self = GUI.Window

		#Get the wxObject
		thing = self.getObjectWithEvent(self, event)

		#Pass this onto the correct function
		value = self.getObjectValue(self, thing, index, full)

		return value

	def getObjectParent(self, thing):
		"""Gets the parent of an object.

		thing (wxObject) - The object to find the parent of

		Example Input: getObjectParent(self)
		Example Input: getObjectParent(thing)
		"""

		#Correct 'self'
		self = GUI.Window

		#Run the function as it should be run
		parent = GUI.Utilities.getObjectParent(self, thing)

		return parent

	def getObjectFrame(self, thing, panel = False, label = False, error = True):
		"""Gets the frame of an object.

		thing (wxObject) - The object to find the parent of. Can be an event or the title of a window
		panel (bool)     - If True: Will return the panel if one exists
		label (bool)     - If True: Will return the frame's label instead of the frame
		error (bool)     - If True: Any errors will be reported to the user on the print screen

		Example Input: getObjectParent(thing)
		Example Input: getObjectParent(event)
		Example Input: getObjectParent(thing, panel = True)
		Example Input: getObjectParent(thing, label = True)
		Example Input: getObjectFrame(thing, error = False)
		"""

		#Run the function as it should be run
		myFrame = self.Utilities.getObjectFrame(self, thing, panel = panel, label = label, error = error)

		return myFrame

	def getSelectionIndex(self, thing):
		"""Returns index of a selection. Can be given a wxObject or a wxCommandEvent

		thing (str)            - A unique string that indicates what the object is labeled in the idCatalogue
		thing (wxObject)       - The object with the value
		thing (wxCommandEvent) - If provided instead, the value will be retrieved from an event object

		Example Input: getSelectionIndex(thing)
		Example Input: getSelectionIndex(event)
		"""

		#Run the function as it should be run
		index = GUI.Utilities.getSelectionIndex(None, thing)

		return index

	def onBackgroundRun(self, event, myFunctionList, myFunctionArgsList = None, myFunctionKwargsList = None, shown = False):
		"""Here so the function backgroundRun can be triggered from a bound event."""

		#Run the function correctly
		GUI.Utilities.backgroundRun(self, myFunctionList, myFunctionArgsList, myFunctionKwargsList, shown)

		event.Skip()

	def backgroundRun(self, myFunctionList, myFunctionArgsList = None, myFunctionKwargsList = None, shown = False, makeThread = True):
		"""Runs a function in the background in a way that it does not lock up the GUI.
		Meant for functions that take a long time to run.

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

		#Run the function correctly
		GUI.Utilities.backgroundRun(self, myFunctionList, myFunctionArgsList, myFunctionKwargsList, shown, makeThread)

	def formatFunctionInput(self, i, myFunctionList, myFunctionArgsList, myFunctionKwargsList):
		"""Formats the args and kwargs for various internal functions."""

		myFunctionEvaluated, myFunctionArgs, myFunctionKwargs = GUI.Utilities.formatFunctionInput(self, i, myFunctionList, myFunctionArgsList, myFunctionKwargsList)

		return myFunctionEvaluated, myFunctionArgs, myFunctionKwargs

	def formatFunctionInputList(self, myFunctionList, myFunctionArgsList, myFunctionKwargsList):
		"""Formats the args and kwargs for various internal functions."""

		#Run the function correctly
		myFunctionList, myFunctionArgsList, myFunctionKwargsList = GUI.Utilities.formatFunctionInputList(self, myFunctionList, myFunctionArgsList, myFunctionKwargsList)

		return myFunctionList, myFunctionArgsList, myFunctionKwargsList

	def autoRun(self, delay, myFunctionList, myFunctionArgsList = None, myFunctionKwargsList = None, after = False):
		"""Automatically runs the provided function.

		delay (int)           - How many milliseconds to wait before the function is executed
		myFunctionList (list) - What function will be ran. Can be a string or function object
		after (bool)          - If True: The function will run after the function that called this function instead of after a timer ends

		Example Input: autoRun(0, self.startupFunction)
		Example Input: autoRun(5000, myFrame.switchWindow, [0, 1])
		"""

		#Run the function correctly
		GUI.Utilities.autoRun(self, event, delay, myFunctionList, myFunctionArgsList, myFunctionKwargsList, after)

	def onAutoRun(self, event, delay, myFunctionList, myFunctionArgsList = None, myFunctionKwargsList = None, after = False):
		"""Automatically runs the provided function.

		delay (int)           - How many milliseconds to wait before the function is executed
		myFunctionList (list) - What function will be ran. Can be a string or function object
		after (bool)          - If True: The function will run after the function that called this function instead of after a timer ends
		"""

		#Run the function correctly
		GUI.Utilities.autoRun(self, delay, myFunctionList, myFunctionArgsList, myFunctionKwargsList, after)

	#Tables
	# def setTableCell(self, row, column, value, label, readOnly = False):
	#   """Writes something to a cell.
	#   The top-left corner is row (0, 0) not (1, 1).

	#   row (int)       - The index of the row
	#   column (int)    - The index of the column
	#   value (any)     - What will be written to the cell
	#   readOnly (bool) - If True: The user cannot edit this cell
	#       If a cell was already readOnly, and it is set to not be, it will no longer be readOnly.

	#   Example Input: setTableCell(1, 2, 42)
	#   Example Input: setTableCell(1, 2, 3.14)
	#   Example Input: setTableCell(1, 2, "Lorem Ipsum")
	#   """

	#   #Get the object that triggered the event
	#   thing = GUI.Utilities.getObjectWithEvent(None, thing)
	#   parent = GUI.Utilities.getObjectParent(None, thing)

	#   #Run the function as it should be run
	#   parent.setTableCell(self, row, column, value, label readOnly)

	class MyApp(wx.App):
		"""Needed to make the GUI work."""

		def OnInit(self):
			"""Returns this class to the user so it can be used.

			Example Input: MyApp()
			"""

			return True

	class Utilities():
		"""Contains common functions needed for various other functions.
		This is here for convenience in programming.
		"""

		def __init__(self):
			"""Defines the internal variables needed to run.

			Example Input: Meant to be inherited by GUI().
			"""

			self.dpiAware = False
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
				"special+16": 208, "special+17": 209, "special+18": 210, "special+19": 211, "special+20": 212
							   }

		def getMenuItem(self, whichMenu, whichItem):
			"""Returns the menu item of a specific menu.
			Uses the menu item's label text to find it.

			whichMenu (int) - The index of the menu to search through
			whichItem (str) - The label of the menu item

			Example Input: getMenuItem(0, '&Quit')
			"""

			myMenu = self.menuDict[whichMenu]
			itemId = myMenu.getMenuItem(whichItem)
			myItem = myMenu.getMenuItem(itemId)[0]
			return myItem

		def getMenuWindow(self, whichMenu):
			"""Returns the wxFrame a specific menu is on.
			Uses the menu item's label text to find it.

			whichMenu (int) - The index of the menu

			Example Input: getMenuItem(0)
			"""

			myFrame = self.menuDict[whichMenu]
			return myFrame

		def newId(self, label = None):
			"""Returns a unique id

			label (str) - A unique string that can be used to retrieve an id
				If None: The id is virtually irretrieveable

			Example Input: newId()
			Example Input: newId("saveFile")
			"""
			global idGen, idCatalogue

			#Generate id
			myId = idGen
			idGen += 1

			#Catalogue ID
			if (label != None):
				if (label in idCatalogue):
					print("WARNING: Overwriting id for", label)

				idCatalogue[label] = [myId, None] 

			return myId

		def getId(self, label):
			"""Returns the id of a labeled item

			label (str)      - A unique string that has already been assigned an id
			label (wxObject) - The object that has already been assigned an id

			Example Input: getId("saveFile")
			"""
			global idCatalogue

			#Retrieve the object id
			myId = None
			if (label != None):
				#Search for the label in the catalogue
				if (type(label) == str):
					for key, value in idCatalogue:
						if (key == label):
							myId = value[0]
				else:
					myId = label.GetId()
					# for key, value in idCatalogue:
					# 	if (value[1] == label):
					# 		myId = value[0]

			return myId

		def addToId(self, thing, label):
			"""Adds a thing to an id in the id catalogue.

			label (str) - A unique string that can be used to retrieve an id
				If None: The id is virtually irretrieveable

			Example Input: addToId(thing, myLabel)
			"""
			global idCatalogue

			#Only add for unique labels
			if (label != None):
				if (label in idCatalogue):
					idCatalogue[label][1] = thing

		def toggleObjectWithLabel(self, label, state = None, showHide = False, autoSize = True):
			"""Enables or disables an item.

			label (str)      - A string previously associated with an object's id; given upon the objects creation
							   If a list is given, each object will be toggled
			state (bool)     - If provided, can force the object to either be enabled (True) or disabled (False)
			showHide (bool)  - If True: Shows and hides an object instead of enabling or disabling it

			Example Input: toggleObjectWithLabel("myCheckBox")
			Example Input: toggleObjectWithLabel("myCheckBox", True)
			Example Input: toggleObjectWithLabel("myCheckBox", showHide = True)
			Example Input: toggleObjectWithLabel(["myText", "myCheckBox"])
			"""

			#Account for multiple objects
			if (type(label) != list):
				if (type(label) != tuple):
					labelList = [label]
				else:
					labelList = list(label)
			else:
				labelList = label

			for label in labelList:
				#Get the object
				thing = self.getObjectWithLabel(label)

				#Toggle the object
				if (showHide):
					#Account for special cases
					classType = thing.GetClassName()
					if ((classType == "wxGridSizer") or (classType == "wxFlexGridSizer") or (classType == "wxBagGridSizer") or (classType == "wxBoxSizer") or (classType == "wxStaticBoxSizer")):
						classType = "wxSizer"

					#Show/Hide the object
					if (state != None):
						if (classType == "wxMenuItem"):
							#Check for if it is a popup item
							for i, item in enumerate(self.popupItemsList):
								if (item[1] == label):
									self.popupItemsList[i][-1] = state
						else:
							if (classType == "wxSizer"):
								thing.ShowItems(state)
							else:
								thing.Show(state)
					else:
						if (classType == "wxMenuItem"):
							#Check for if it is a popup item
							for i, item in enumerate(self.popupItemsList):
								if (item[1] == label):
									if (self.popupItemsList[i][-1] == True):
										self.popupItemsList[i][-1] = False
									else:
										self.popupItemsList[i][-1] = True
									break
							else:
								if (thing.IsShown()):
									thing.Show(False)
								else:
									thing.Show(True)
						else:
							# print("@2", thing)

							if (classType == "wxSizer"):
								if (thing.IsShown(0)):
									thing.ShowItems(False)
									thing.Hide(0)
								else:
									thing.ShowItems(True)
							else:
								if (thing.IsShown()):
									thing.Show(False)
								else:
									thing.Show(True)

					#Update the frame
					if (classType == "wxSizer"):
						self.updateWindow(autoSize)
					else:
						myFrame = self.getObjectParent(thing)
						myFrame.updateWindow(autoSize)

				else:
					#Account for special cases
					classType = thing.GetClassName()
					if (classType == "wxMenuItem"):
						#Check for if it is a popup item
						for i, item in enumerate(self.popupItemsList):
							if (item[1] == label):
								if (state != None):
									self.popupItemsList[i][-2] = state
								else:
									if (self.popupItemsList[i][-2]):
										self.popupItemsList[i][-2] = False
									else:
										self.popupItemsList[i][-2] = True
								break
						else:
							if (thing.IsEnabled()):
								thing.Enable(False)
							else:
								thing.Enable(True)
					else:	
					#Enable/Disable the object
						if (state != None):
							thing.Enable(state)
						else:
							if (thing.IsEnabled()):
								thing.Enable(False)
							else:
								thing.Enable(True)

		def enableObjectWithLabel(self, label):
			"""Enables an item if it is disabled.
			Otherwise, it leaves it enabled.

			label (str) - A string previously associated with an object's id; given upon the objects creation

			Example Input: enableObjectWithLabel("myCheckBox")
			"""

			#Account for multiple objects
			if (type(label) != list):
				if (type(label) != tuple):
					labelList = [label]
				else:
					labelList = list(label)
			else:
				labelList = label

			for label in labelList:
				#Get the object
				thing = self.getObjectWithLabel(label)

				#Account for special cases
				classType = thing.GetClassName()
				if (classType == "wxMenuItem"):
					#Check for if it is a popup item
					for i, item in enumerate(self.popupItemsList):
						if (item[1] == label):
							self.popupItemsList[i][-2] = True
							break
					else:
						if (not thing.IsEnabled()):
							thing.Enable(True)

				elif (classType == "wxMenu"):
					#Determine menu position
					menuList = self.menubar.GetMenus()
					for i, item in enumerate(menuList):
						menu, menuText = item
						if (thing == menu):
							#Disable menu
							self.menubar.EnableTop(i, False)
							break
					else:
						print("ERROR: Menu", menuNumber, "cannot be found")

				else:
					if (not thing.IsEnabled()):
						thing.Enable(True)

		def disableObjectWithLabel(self, label):
			"""Disables an item if it is enabled.
			Otherwise, it leaves it disabled.

			label (str) - A string previously associated with an object's id; given upon the objects creation

			Example Input: disableObjectWithLabel("myCheckBox")
			"""

			#Account for multiple objects
			if (type(label) != list):
				if (type(label) != tuple):
					labelList = [label]
				else:
					labelList = list(label)
			else:
				labelList = label

			for label in labelList:
				#Get the object
				thing = self.getObjectWithLabel(label)

				#Account for special cases
				classType = thing.GetClassName()
				if (classType == "wxMenuItem"):
					#Check for if it is a popup item
					for i, item in enumerate(self.popupItemsList):
						if (item[1] == label):
							self.popupItemsList[i][-2] = False
							break
					else:
						if (not thing.IsEnabled()):
							thing.Enable(False)
				else:
					#Make sure the object is disabled
					if (thing.IsEnabled()):
						thing.Enable(False)

		def checkEnabledObjectWithLabel(self, label):
			"""Checks if an item is enabled.

			label (str) - A string previously associated with an object's id; given upon the objects creation

			Example Input: checkEnabledObjectWithLabel("myCheckBox")
			"""

			#Get the object
			thing = self.getObjectWithLabel(label)

			#Make sure the object is enabled
			state = thing.IsEnabled()
			return state

		def showObjectWithLabel(self, label, autoSize = True):
			"""Shows an item if it is hidden.
			Otherwise, it leaves it shown.

			label (str) - A string previously associated with an object's id; given upon the objects creation

			Example Input: showObjectWithLabel("myCheckBox")
			"""

			#Account for multiple objects
			if (type(label) != list):
				if (type(label) != tuple):
					labelList = [label]
				else:
					labelList = list(label)
			else:
				labelList = label
				
			for label in labelList:
				#Get the object
				thing = self.getObjectWithLabel(label)

				#Account for special cases
				classType = thing.GetClassName()
				if ((classType == "wxGridSizer") or (classType == "wxFlexGridSizer") or (classType == "wxBagGridSizer") or (classType == "wxBoxSizer") or (classType == "wxStaticBoxSizer")):
					classType = "wxSizer"

				if (classType == "wxMenuItem"):
					#Check for if it is a popup item
					for i, item in enumerate(self.popupItemsList):
						if (item[1] == label):
							self.popupItemsList[i][-1] = False
							break
					else:
						if (not thing.IsShown()):
							thing.Show(True)
				else:
					#Make sure the object is shown
					if (classType == "wxSizer"):
						if (not thing.IsShown(0)):
							thing.ShowItems(True)
					else:
						if (not thing.IsShown()):
							thing.Show(True)

				#Update the frame
				if (classType == "wxSizer"):
					self.updateWindow(autoSize)
				else:
					myFrame = self.getObjectParent(thing)
					myFrame.updateWindow(autoSize)

		def hideObjectWithLabel(self, label, autoSize = True):
			"""Disables an item if it is shown.
			Otherwise, it leaves it hidden.

			label (str) - A string previously associated with an object's id; given upon the objects creation

			Example Input: hideObjectWithLabel("myCheckBox")
			"""

			#Account for multiple objects
			if (type(label) != list):
				if (type(label) != tuple):
					labelList = [label]
				else:
					labelList = list(label)
			else:
				labelList = label

			for label in labelList:
				#Get the object
				thing = self.getObjectWithLabel(label)

				#Account for special cases
				classType = thing.GetClassName()
				if ((classType == "wxGridSizer") or (classType == "wxFlexGridSizer") or (classType == "wxBagGridSizer") or (classType == "wxBoxSizer") or (classType == "wxStaticBoxSizer")):
					classType = "wxSizer"

				if (classType == "wxMenuItem"):
					#Check for if it is a popup item
					for i, item in enumerate(self.popupItemsList):
						if (item[1] == label):
							self.popupItemsList[i][-1] = True
							break
					else:
						if (thing.IsShown()):
							thing.Hide

				else:
					#Make sure the object is hidden
					if (classType == "wxSizer"):
						if (not thing.IsShown(0)):
							continue
						else:
							thing.ShowItems(False)
							thing.Hide(0)

					else:
						if (not thing.IsShown()):
							continue
						else:
							thing.Hide()

				#Update the frame
				self.updateWindow(autoSize)

		#Getters
		def getObjectWithLabel(self, label):
			"""Gets an object with an id label.
			Currently does not work with the following wxObjects: wxMenu, wxMenuItem

			label (str) - A string previously associated with an object's id; given upon the objects creation

			Example Input: getObjectWithLabel("saveFile")
			"""
			global idCatalogue

			#Retrieve object from catalogue
			if (label in idCatalogue):
				thing = idCatalogue[label][1]
			else:
				print(idCatalogue)
				print("ERROR: No object labeled", label)
				thing = None

			return thing

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
			
			return parent
		
		def getObjectFrame(self, thing, panel = False, label = False, error = True):
			"""Gets the frame of an object.

			thing (wxObject) - The object to find the parent of. Can be an event or the title of a window
			panel (bool)     - If True: Will return the panel if one exists
			label (bool)     - If True: Will return the frame's label instead of the frame
			error (bool)     - If True: Any errors will be reported to the user on the print screen

			Example Input: getObjectFrame(thing)
			Example Input: getObjectFrame(event)
			Example Input: getObjectFrame(thing, panel = True)
			Example Input: getObjectFrame(thing, label = True)
			Example Input: getObjectFrame(thing, error = False)
			"""

			#Check for title
			if (type(thing) == str):
				#Search through all frames
				myFrame = None
				for key, value in self.frameDict.items():
					itemFrame, title = value

					if (title == thing):
						if (label):
							myFrame = key
						else:
							myFrame = itemFrame
						break
				else:
					if (error):
						print("No frame with the title: '" + thing + "'")
					return None

				#Check for panel
				if (panel):
					if ("-1" in myFrame.panelDict):
						myFrame = myFrame.panelDict["-1"]

			else:
				#Check for event
				thingClass = thing.GetClassName()
				if (thingClass == "wxCommandEvent"):
					thing = thing.GetEventObject()

				#Retrieve Frame
				myFrame = thing.GetParent()

				#Check for panel
				if (not panel):
					thingClass = myFrame.GetClassName()
					if (thingClass == "wxPanel"):
						myFrame = myFrame.GetParent()

				#Check for label return
				if (label):
					for key, value in self.frameDict.items():
						itemFrame, title = value
						
						if (itemFrame == myFrame):
							myFrame = key
							break
			
			return myFrame

		def queueValue(self, value, label):
			"""Adds the value to the queue for the user to access.

			value (any) - Something that will be stored for the user to access
			label (str) - A unique string that can be used to retrieve the value

			Example Input: queueValue(3.14, "pi")
			"""
			global valueQueue

			valueQueue[label] = value

		def getQueueValue(self, label, event = None, isType = str):
			"""Returns the value associated with the label.
			If the label does not exist, it returns None.

			label (str)   - A unique string that can be used to retrieve the value
			isType (type) - What data-type to return the value as

			Example Input: getQueueValue("pi")
			Example Input: getQueueValue("pi", event)
			Example Input: getQueueValue("pi", isType = float)
			"""
			global valueQueue

			#Check if the label exists in the value queue
			if (label in valueQueue):
				#Check if the value is coming from an event object
				value = valueQueue[label]
			else:
				value = None

			#Convert it to the correct type if necissary
			if (isType != str):
				value = isType(value)

			return value

		def checkValueQueue(self):
			"""Returns a list of the labels in 'valueQueue' as strings."""
			global valueQueue

			labelList = list(valueQueue.keys())
			return labelList

		def getObjectValueWithEvent(self, event, index = False, full = False):
			"""Returns the value stored in an object when given the object's label.

			event (CommandEvent) - The wxPython event that was triggered

			Example Input: getObjectValueWithEvent(event)
			"""

			#Get the wxObject
			thing = self.getObjectWithEvent(event)

			#Pass this onto the correct function
			value = self.getObjectValue(thing, index, full)

			return value

		def getObjectValueWithLabel(self, myLabel, index = False, full = False):
			"""Returns the value stored in an object when given the object's label.

			myLabel (str) - What this is called in the idCatalogue
			index (bool)  - If True: The index value will be returned. Use for lists, radio groups, menu items, etc.

			Example Input: getObjectValueWithLabel("myCheckBox")
			Example Input: getObjectValueWithLabel("myListDrop", True)
			"""

			#Get the wxObject
			thing = self.getObjectWithLabel(myLabel)

			#Pass this onto the correct function
			value = self.getObjectValue(thing, index, full)

			return value

		def getObjectValue(self, thing, index = False, full = False):
			"""Returns the value stored in an object. Can be given a wxObject or a wxCommandEvent

			thing (wxObject)       - The object with the value
			thing (wxCommandEvent) - If provided instead, the value will be retrieved from an event object
			index (bool)           - If True: The index value will be returned. Use for drop lists, full lists, radio groups, and menu items.
			full (bool)            - If True: All contents will be returned. Use for drop lists and full lists.

			Example Input: getObjectValue(thing)
			Example Input: getObjectValue(event)
			"""

			#Determine how the value neeeds to be extracted from the wxObject
			classType = thing.GetClassName()

			#Check if the value is coming from an event object
			if (classType == "wxCommandEvent"):
				thing = GUI.Utilities.getObjectWithEvent(self, thing)
				classType = thing.GetClassName()

			#Get the object's value
			if (classType == "wxTextCtrl"):
				value = thing.GetValue() #(str) - What is in the input box

			elif (classType == "wxSpinCtrl"):
				value = thing.GetValue() #(str) - What is in the spin box

			elif (classType == "wxChoice"):
				i = thing.GetSelection()
				if (full):
					value = []
					n = thing.GetCount()
					for i in range(n):
						value.append(thing.GetString(i)) #(list) - What is in the drop list
				else:
					if (index):
						value = i #(int) - The index number of what is selected in the drop list
					else:
						value = thing.GetString(i) #(str) - What is selected in the drop list

			elif (classType == "wxListBox"):
				i = thing.GetSelection()
				if (full):
					value = []
					n = thing.GetCount()
					for i in range(n):
						value.append(thing.GetString(i)) #(list) - What is in the full list
				else:
					if (index):
						value = i #(int) - The index number of what is selected in the full list
					else:
						value = thing.GetString(i) #(str) - What is selected in the full list

			elif (classType == "wxCheckBox"):
				value = thing.GetValue() #(bool) - True: Checked; False: Un-Checked

			elif (classType == "wxRadioBox"):
				value = thing.GetSelection() #(bool) - True: Selected; False: Un-Selected

			elif (classType == "wxRadioButton"):
				value = thing.GetValue() #(bool) - True: Selected; False: Un-Selected

			elif (classType == "wxMenuItem"):
				value = thing.IsChecked() #(bool) - True: Selected; False: Un-Selected

			elif (classType == "wxDirPickerCtrl"):
				value = thing.GetPath() #(str) - What is in the attached directory picker
			
			elif (classType == "wxFilePickerCtrl"):
				value = thing.GetPath() #(str) - What is in the attached file picker
			
			elif (classType == "wxDatePickerCtrl"):
				value = thing.GetValue() #(str) - What date is selected in the date picker
				if (value != None):
					value = str(value.GetMonth()) + "/"+ str(value.GetDay()) + "/" + str(value.GetYear())

			elif (classType == "wxCalendarCtrl"):
				value = thing.GetDate() #(str) - What date is selected in the date picker
				if (value != None):
					value = str(value.GetMonth()) + "/"+ str(value.GetDay()) + "/" + str(value.GetYear())

			elif (classType == "wxTimePickerCtrl"):
				value = thing.GetTime() #(str) - What date is selected in the date picker
				if (value != None):
					value = str(value[0]) + ":"+ str(value[1]) + ":" + str(value[2])

			elif (classType == "wxControl"):
				value = thing.GetValue() #(str) - What is in the wigit

			elif (classType == "wxStaticText"):
				value = thing.GetLabel() #(str) - What the text says

			else:
				print("Add", classType, "to getObjectValue()")
				value = None

			return value

		def getSelectionIndex(self, thing):
			"""Returns index of a selection. Can be given a wxObject or a wxCommandEvent

			thing (str)            - A unique string that indicates what the object is labeled in the idCatalogue
			thing (wxObject)       - The object with the value
			thing (wxCommandEvent) - If provided instead, the value will be retrieved from an event object

			Example Input: getSelectionIndex("pi")
			Example Input: getSelectionIndex(thing)
			Example Input: getSelectionIndex(event)
			"""

			#Determine if a label was given instead of an object or an event
			if (type(thing) == str):
				try:
					thing = self.getObjectWithLabel(self, thing)
				except:
					thing = GUI.Utilities.getObjectWithLabel(self, thing)

			#Determine how the value neeeds to be extracted from the wxObject
			classType = thing.GetClassName()

			#Check if the value is coming from an event object
			if (classType == "wxCommandEvent"):
				thing = GUI.Utilities.getObjectWithEvent(self, thing)
				classType = thing.GetClassName()

			#Get the object's value
			if (classType == "wxChoice"):
				index = thing.GetSelection() #(int) - The index of the selected list element

			#Get the object's value
			if (classType == "wxListBox"):
				index = thing.GetSelection() #(int) - The index of the selected list element

			#Get the object's value
			if (classType == "wxGrid"):
				index = thing.GetSelectedCells() #(array) - The selected cells in the table

			else:
				print("Add", classType, "to getObjectValue()")
				index = None

			return index

		def getEventValue(self, event):
			"""Here for in case the user forgets how to use getObjectValue with events correctly.

			event (wxCommandEvent) - If provided instead, the value will be retrieved from an event object

			Example Input: getEventValue(event)
			"""

			#Get the object that triggered the event
			self.getObjectValue(event)

		def getLabel(self, thing, window = False):
			"""Gets the label for any wxObject.

			thing (wxObject) - The wxPython object that is being checked
			window (bool)    - If True: The window object's label will be returned instead of the widget
			
			WHAT IS RETURNED
			Frame (str)       - The title of the frame
			Dialog (str)      - The title of the dialog box
			Button (str)      - The text displayed on the button
			Static Text (str) - The text that is displayed

			Example Input: getLabel(thing)
			"""

			#Determine how the value neeeds to be extracted from the wxObject
			classType = thing.GetClassName()

			#Check if the value is coming from an event object
			if (classType == "wxCommandEvent"):
				thing = thing.GetEventObject()

			#Check for what to return
			if (window):
				classType = thing.GetClassName()
				
				if (classType != "wxFrame"):
					if ((classType == "wxMenu") or (classType == "wxMenuItem")):
						if (classType == "wxMenuItem"):
							thing = thing.GetMenu()

						thing = thing.GetWindow()
					else:
						thing = thing.GetParent()

			#Return the label
			label = thing.GetLabel()
			return label

		def getCursor(self, cursorType):
			"""Returns a wxCursor object when given a label.

			cursorType (str) - What the cursor will become. Only the first two letters are needed except for with the sizing cursors and "wait2".
							~ "default"  - The standard arrow cursor pointing to the left
							~ "flip"     - The standard arrow cursor pointing to the right
							~ "line"     - The text editor i-beam vertical line
							~ "question" - The standard arrow with a small question mark
							~ "wait"     - The standard hourglass or loading cursor
							~ "wait2"    - The standard arrow with a small standard hourglass or loading cursor
							~ "blank"    - No cursor image

							~ "size"     - Four arrows pointing up, down, left, and right
							~ "sizeNE"   - A diagonal arrow pointing NE and SW. Can also be "sizeSW"
							~ "sizeNW"   - A diagonal arrow pointing NW and SE. Can also be "sizeSE"
							~ "sizeN"    - A vertical arrow pointing up and down. Can also be "sizeS"
							~ "sizeE"    - A horizontal arrow pointing left and right. Can also be "sizeW"

							~ "hand"     - A hand
							~ "left"     - A hand pointing to the left
							~ "right"    - A hand pointing to the right

							~ "no"       - A no-entry sign
							~ "cross"    - A cross

							~ "target"   - A bullseye target
							~ "magnify"  - A magnifying glass
							~ "paint"    - A paint brush
							~ "pencil"   - A pencil
							~ "spray"    - A spraycan

			Example Input: getCursor("wait")
			"""

			#Ensure correct case for cursorType
			cursorType = cursorType.lower()

			#Determine cursor type
			if (cursorType[0] == "default"):
				cursor = wx.CURSOR_ARROW

			elif (cursorType[0] == "flip"):
				cursor = wx.CURSOR_RIGHT_ARROW

			elif (cursorType[0] == "line"):
				cursor = wx.CURSOR_IBEAM

			elif (cursorType[0] == "question"):
				cursor = wx.CURSOR_QUESTION_ARROW

			elif (cursorType[0] == "wait"):
				cursor = wx.CURSOR_WAIT

			elif (cursorType[0] == "wait2"):
				cursor = wx.CURSOR_ARROWWAIT

			elif (cursorType[0] == "blank"):
				cursor = wx.CURSOR_BLANK

			elif (cursorType[0] ==  "size"):
				cursor = wx.CURSOR_SIZING

			elif (cursorType[0] == "sizeNE"):
				cursor = wx.CURSOR_SIZENESW

			elif (cursorType[0] == "sizeNW"):
				cursor = wx.CURSOR_SIZENWSE

			elif (cursorType[0] == "sizeN"):
				cursor = wx.CURSOR_SIZENS

			elif (cursorType[0] == "sizeE"):
				cursor = wx.CURSOR_SIZEWE

			elif (cursorType[0] == "hand" ):
				cursor = wx.CURSOR_HAND

			elif (cursorType[0] == "left"):
				cursor = wx.CURSOR_POINT_LEFT

			elif (cursorType[0] == "right"):
				cursor = wx.CURSOR_POINT_RIGHT

			elif (cursorType[0] == "no"):
				cursor = wx.CURSOR_NO_ENTRY

			elif (cursorType[0] == "cross"  ):
				cursor = wx.CURSOR_CROSS

			elif (cursorType[0] == "target"):
				cursor = wx.CURSOR_BULLSEYE

			elif (cursorType[0] == "magnify"):
				cursor = wx.CURSOR_MAGNIFIER

			elif (cursorType[0] == "paint"):
				cursor = wx.CURSOR_PAINT_BRUSH

			elif (cursorType[0] == "pencil"):
				cursor = wx.CURSOR_PENCIL

			elif (cursorType[0] == "spray"):
				cursor = wx.CURSOR_SPRAYCAN

			else:
				print("ERROR: There is no cursor", cursorType, "in changeCursorWindow()")
				cursor = wx.CURSOR_ARROW

			#Return cursor type
			return cursor

		def changeCursor(self, triggerObjectLabel, cursorType):
			"""Changes the cursor when it is over a specific wxObject.

			triggerObjectLabel (str)      - The idCatalogue label for the object that will change this cursor.
			cursorType (str) - What the cursor will become. Only the first two letters are needed except for with the sizing cursors and "wait2".
								~ "default"  - The standard arrow cursor pointing to the left
								~ "flip"     - The standard arrow cursor pointing to the right
								~ "line"     - The text editor i-beam vertical line
								~ "question" - The standard arrow with a small question mark
								~ "wait"     - The standard hourglass or loading cursor
								~ "wait2"    - The standard arrow with a small standard hourglass or loading cursor
								~ "blank"    - No cursor image

								~ "size"     - Four arrows pointing up, down, left, and right
								~ "sizeNE"   - A diagonal arrow pointing NE and SW. Can also be "sizeSW"
								~ "sizeNW"   - A diagonal arrow pointing NW and SE. Can also be "sizeSE"
								~ "sizeN"    - A vertical arrow pointing up and down. Can also be "sizeS"
								~ "sizeE"    - A horizontal arrow pointing left and right. Can also be "sizeW"

								~ "hand"     - A hand
								~ "left"     - A hand pointing to the left
								~ "right"    - A hand pointing to the right

								~ "no"       - A no-entry sign
								~ "cross"    - A cross

								~ "target"   - A bullseye target
								~ "magnify"  - A magnifying glass
								~ "paint"    - A paint brush
								~ "pencil"   - A pencil
								~ "spray"    - A spraycan

			Example Input: changeCursorWindow(0, "magnifier")
			"""

			#Get the object
			thing = self.getObjectWithLabel(triggerObjectLabel)

			#Determine which cursor
			cursor = self.getCursorObject(cursorType)

			#Apply cursor change attribute
			thing.SetCursor(wx.Cursor(cursor))

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

		#Setters
		def setObjectValue(self, thing, newValue, fixType = True, maxValue = False, minValue = False, selection = False):
			"""Changes the value of a wxObject that is already on a shown screen.
			Special thanks to Martijn Pieters for filtering None in a list on http://stackoverflow.com/questions/19363881/replace-none-value-in-list

			thing (wxObject)       - The object with the value
			thing (wxCommandEvent) - If provided instead, the value will be retrieved from an event object
			thing (str)            - If provided instead, the value will be retrieved from a labeled object
			newValue (str)         - What the new value will be

			fixType (bool)   - If True: The correct data type will be applied automatically (ex: given an int instead of a string)
			maxValue (bool)  - If True: The maximum value for the object will be changed instead of the current value
			minValue (bool)  - If True: The minimum value for the object will be changed instead of the current value
			selection (bool) - If True: The selection for the object will be changed instead of the entire list

			Example Input: setObjectValue(thing, 5)
			"""

			#Check if the value is coming from an event object or a labeled object
			if (type(thing) == str):
				try:
					thing = self.getObjectWithLabel(self, thing)
				except:
					thing = GUI.Utilities.getObjectWithLabel(self, thing)

			#Check for different function
			if (selection):
				try:
					self.setObjectSelection(thing, newValue)
				except:
					GUI.Utilities.setObjectSelection(self, thing, newValue)
			
			#Determine how the value neeeds to be changed
			classType = thing.GetClassName()

			#Check if the value is coming from an event object
			if (classType == "wxCommandEvent"):
				thing = GUI.Utilities.getObjectWithEvent(self, thing)
				classType = thing.GetClassName()

			#Change the value
			if(self.debugging):
				print("setObjectValue()", classType)

			if (classType == "wxStaticText"):
				if (fixType):
					if (type(newValue) != str):
						newValue = str(newValue)

				thing.SetLabel(newValue) #(str) - What the static text will now say

			elif (classType == "wxChoice"):
				if (None in newValue):
					newValue = [value for value in newValue if value is not None] #Filter out None
				thing.SetItems(newValue) #(list) - What the choice options will now be now

			elif (classType == "wxListBox"):
				if (None in newValue):
					newValue = [value for value in newValue if value is not None] #Filter out None
				thing.SetItems(newValue) #(list) - What the choice options will now be now

			elif (classType == "wxCheckBox"):
				thing.SetValue(newValue) #(bool) - True: checked; False: un-checked

			elif (classType == "wxRadioButton"):
				thing.SetValue(newValue) #(bool) - True: selected; False: un-selected

			elif (classType == "wxRadioBox"):
				thing.SetValue(newValue) #(bool) - True: selected; False: un-selected

			elif (classType == "wxMenuItem"):
				if ((thing.GetKind() == wx.ITEM_CHECK) or (thing.GetKind() == wx.ITEM_RADIO)):
					myMenu = thing.GetMenu()
					myId = thing.GetId()
					myMenu.Check(myId, newValue) #(bool) - True: selected; False: un-selected
				else:
					print("ERROR: Only a menu 'Check Box' or 'Radio Button' can be set to a different value")

			elif (classType == "wxTextCtrl"):
				thing.SetValue(newValue) #(str) - What will be shown in the text box

			elif (classType == "wxSpinCtrl"):
				if (maxValue or minValue):
					if (maxValue):
						thing.SetMax(newValue) #(int / float) - What the max value will be for the the input box
					else:
						thing.SetMin(newValue) #(int / float) - What the min value will be for the the input box
				else:
					thing.SetValue(newValue) #(int / float) - What will be shown in the input box

			elif (classType == "wxControl"):
				if (maxValue or minValue):
					if (maxValue):
						thing.SetMax(newValue) #(int / float) - What the max value will be for the the widget
					else:
						thing.SetMin(newValue) #(int / float) - What the min value will be for the the widget
				else:
					thing.SetValue(newValue) #(int / float) - What will be shown in the widget

			elif (classType == "wxFilePickerCtrl"):
				thing.SetPath(newValue) #(str) - What will be shown in the input box

			elif (classType == "wxDatePickerCtrl"):
				if (fixType):
					try:
						if (newValue != None):
							month, day, year = re.split("[\\\\/]", newValue) #Format: mm/dd/yyyy
							month, day, year = int(month), int(day), int(year)
							newValue = wx.DateTime(day, month, year)
						else:
							newValue = wx.DateTime().SetToCurrent()
					except:
						print("ERROR: Calandar dates must be formatted 'mm/dd/yy' for setObjectValue()")
						return

				thing.SetValue(newValue) #(str) - What date will be selected

			elif (classType == "wxCalendarCtrl"):
				if (fixType):
					try:
						if (newValue != None):
							month, day, year = re.split("[\\\\/]", newValue) #Format: mm/dd/yyyy
							month, day, year = int(month), int(day), int(year)
							newValue = wx.DateTime(day, month, year)
						else:
							newValue = wx.DateTime().SetToCurrent()
					except:
						print("ERROR: Calandar dates must be formatted 'mm/dd/yy' for setObjectValue()")
						return

				thing.SetDate(newValue) #(str) - What date will be selected

			elif (classType == "wxTimePickerCtrl"):
				if (fixType):
					try:
						if (newValue != None):
							time = re.split(":", newValue) #Format: hour:minute:second
					
							if (len(time) == 2):
								hour, minute = time
								second = "0"

							elif (len(time) == 3):
								hour, minute, second = time

							else:
								print("ERROR: Time must be formatted 'hh:mm:ss' or 'hh:mm' for setObjectValue()")
								return

						else:
							newValue = wx.DateTime().SetToCurrent()
							hour, minute, second = newValue.GetHour(), newValue.GetMinute(), newValue.GetSecond()

						hour, minute, second = int(hour), int(minute), int(second)
					except:
						print("ERROR: Time must be formatted 'hh:mm:ss' or 'hh:mm' for setObjectValue()")
						return

				thing.SetTime(hour, minute, second) #(int, int, int) - What time will be selected

			elif (classType == "wxButton"):
				thing.SetLabel(newValue) #(str) - What the button will say on it

			elif (classType == "wxStaticBitmap"):
				#Make sure the new image is a bitmap image
				if (newValue != None):
					if (type(newValue) != str):
						image = self.convertPilToBitmap(newValue)
					else:
						image = wx.Bitmap(newValue, wx.BITMAP_TYPE_ANY)
				else:
					image = wx.NullBitmap
				thing.SetBitmap(image) #(wxBitmap) - What the image will be now

			else:
				print("Add", classType, "to setObjectValue()")

		def setObjectSelection(self, thing, newValue):
			"""Changes the selection of a wxObject that is already on a shown screen.
			Special thanks to Martijn Pieters for filtering None in a list on http://stackoverflow.com/questions/19363881/replace-none-value-in-list

			thing (wxObject)       - The object with the value
			thing (wxCommandEvent) - If provided instead, the value will be retrieved from an event object
			thing (str)            - If provided instead, the value will be retrieved from a labeled object
			newValue (str)         - Which string to select

			Example Input: setObjectSelection(thing, 5)
			"""

			#Check if the value is coming from an event object or a labeled object
			if (type(thing) == str):
				try:
					thing = self.getObjectWithLabel(self, thing)
				except:
					thing = GUI.Utilities.getObjectWithLabel(self, thing)
			
			#Determine how the value neeeds to be changed
			classType = thing.GetClassName()

			#Check if the value is coming from an event object
			if (classType == "wxCommandEvent"):
				thing = GUI.Utilities.getObjectWithEvent(self, thing)
				classType = thing.GetClassName()

			#Change the value
			if(self.debugging):
				print("setObjectSelection()", classType)

			#Change the object's selection
			if (classType == "wxChoice"):
				if (type(newValue) == str):
					newValue = thing.FindString(newValue)

				if (newValue != None):
					thing.SetSelection(newValue) #(int) - What the choice options will now be
				else:
					print("ERROR: Invalid drop list selection in setObjectSelection()")

			elif (classType == "wxRadioBox"):
				if (type(newValue) == str):
					if (not newValue.isdigit()):
						newValue = thing.FindString(newValue)

				if (newValue != None):
					thing.SetSelection(int(newValue)) #(bool) - True: checked; False: unchecked
				else:
					print("ERROR: Invalid radio button selection in setObjectSelection()")

			else:
				print("Add", classType, "to setObjectSelection()")

		def setObjectReadOnly(self, thing, readOnly):
			"""Changes a wxObject that is already on a shown screen to be read only or not.

			thing (wxObject)       - The object with the value
			thing (wxCommandEvent) - If provided instead, the value will be retrieved from an event object
			thing (str)            - If provided instead, the value will be retrieved from a labeled object
			readOnly (bool)        - If True: The object is read only. Otherwise, it is not.

			Example Input: setObjectReadOnly(thing, True)
			"""

			#Check if the value is coming from an event object or a labeled object
			if (type(thing) == str):
				try:
					thing = self.getObjectWithLabel(self, thing)
				except:
					thing = GUI.Utilities.getObjectWithLabel(self, thing)
			
			#Determine how the value neeeds to be changed
			classType = thing.GetClassName()

			#Check if the value is coming from an event object
			if (classType == "wxCommandEvent"):
				thing = GUI.Utilities.getObjectWithEvent(self, thing)
				classType = thing.GetClassName()

			#Change the value
			if(self.debugging):
				print("setObjectReadOnly()", classType)

			elif (classType == "wxChoice"):
				thing.SetReadOnly(readOnly)

			elif (classType == "wxCheckBox"):
				thing.SetReadOnly(readOnly)

			elif (classType == "wxTextCtrl"):
				thing.SetEditable(not readOnly)

			else:
				print("Add", classType, "to setObjectReadOnly()")

		def setObjectValueWithLabel(self, label, newValue, fixType = True, maxValue = False, minValue = False, selection = False):
			"""Changes the value of a wxObject that is already on a shown screen.

			label (str)    - A unique string that indicates whose value to change
			newValue (str) - What the new value will be

			Example Input: setObjectValueWithLabel("myCheckBox", True)
			"""

			#Get the object
			thing = self.getObjectWithLabel(label)

			#Change the object's value
			self.setObjectValue(thing, newValue, fixType, maxValue, minValue, selection)

		def setObjectFunctionWithLabel(self, label, myFunction, myFunctionArgs = None, myFunctionKwargs = None):
			"""Binds a function to an already created button"""

			#Get the object
			thing = self.getObjectWithLabel(label)

			#Get object type
			classType = thing.GetClassName()

			#Determine the object's event
			if (classType == "wxButton"):
				event = wx.EVT_BUTTON
			else:
				print("Add", classType, "to setObjectSelection()")

			#Change the object's function
			self.betterBind(event, thing, myFunction, myFunctionArgs, myFunctionKwargs)

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
					# #Compensate for the user not making lists in lists for single functions or multiple functions
					# if (len(myFunctionArgsList) != 1):
					# 	for item in myFunctionArgsList:
					# 		if (type(item) != list):	
					# 			break
					# 	else:
					# 		myFunctionArgsList = [myFunctionArgsList]
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
					print("ERROR: myFunctionKwargs must be a dictionary for function", myFunctionEvaluated)

			return myFunctionEvaluated, myFunctionArgs, myFunctionKwargs

		def beforeFinalClosingRun(self, myFunctionList, myFunctionArgsList = None, myFunctionKwargsList = None):
			"""Runs a function before the program terminates."""

			#Create the sub-function that runs the function
			def runFunction(myFunctionEvaluated, myFunctionArgs, myFunctionKwargs):
				"""This sub-function is needed to make the multiple functions work properly."""

				#Has both args and kwargs
				if ((myFunctionKwargs != None) and (myFunctionArgs != None)):
					atexit.register(myFunctionEvaluated, *myFunctionArgs, **myFunctionKwargs)

				#Has args, but not kwargs
				elif (myFunctionArgs != None):
					atexit.register(myFunctionEvaluated, *myFunctionArgs)

				#Has kwargs, but not args
				elif (myFunctionKwargs != None):
					atexit.register(myFunctionEvaluated, **myFunctionKwargs)

				#Has neither args nor kwargs
				else:
					atexit.register(myFunctionEvaluated)

			#Skip empty functions
			if (myFunctionList != None):
				myFunctionList, myFunctionArgsList, myFunctionKwargsList = self.formatFunctionInputList(myFunctionList, myFunctionArgsList, myFunctionKwargsList)
				
				#Run each function
				for i, myFunction in enumerate(myFunctionList):
					#Skip empty functions
					if (myFunction != None):
						myFunctionEvaluated, myFunctionArgs, myFunctionKwargs = self.formatFunctionInput(i, myFunctionList, myFunctionArgsList, myFunctionKwargsList)
						runFunction(myFunctionEvaluated, myFunctionArgs, myFunctionKwargs)
			else:
				print("ERROR: myFunctionList == None for beforeFinalClosingRun()")

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

		def keyBind(self, key, thing, myFunctionList, myFunctionArgsList = None, myFunctionKwargsList = None, 
			keyUp = True, numpad = False, ctrl = False, alt = False, shift = False, event = None, myId = None):
			"""Binds wxObjects to key events.
			Speed efficency help from Aya on http://stackoverflow.com/questions/17166074/most-efficient-way-of-making-an-if-elif-elif-else-statement-when-the-else-is-don

			key (str)              - The keyboard key to bind the function(s) to
			thing (wxObject)       - What is being bound to
			myFunctionList (str)   - The function that will be ran when the event occurs
			myFunctionArgs (any)   - Any input arguments for myFunction. A list of multiple functions can be given
			myFunctionKwargs (any) - Any input keyword arguments for myFunction. A list of variables for each function can be given. The index of the variables must be the same as the index for the functions
			
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
			self.betterBind(event, thing, self.onKeyPress, [value, myFunctionList, myFunctionArgsList, myFunctionKwargsList, ctrl, alt, shift], myId = myId)

			return value #Used for finished()

		def betterBind(self, eventType, thing, myFunctionList, myFunctionArgsList = None, myFunctionKwargsList = None, myId = None, mode = 1):
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
			def bind(self, eventType, thing, myFunctionEvaluated, myFunctionArgs, myFunctionKwargs, myId, mode):
				"""This sub-function is needed to make the multiple functions work properly."""

				#Get the class type in order to bind the object to the correct thing
				thingClass = thing.GetClassName()

				##Determine how to bind the object
				if ((thingClass == "wxWindow") or (thingClass == "wxMenuItem")):
					bindObject = self
				else:
					bindObject = thing

				#Check for no provided id
				if (myId == None):
					myId = wx.ID_ANY

				#Typical binding mode
				if (mode == 1):
					#Has both args and kwargs
					if ((myFunctionKwargs != None) and (myFunctionArgs != None)):
						bindObject.Bind(eventType, lambda event: myFunctionEvaluated(event, *myFunctionArgs, **myFunctionKwargs), thing, id = myId)

					#Has args, but not kwargs
					elif (myFunctionArgs != None):
						bindObject.Bind(eventType, lambda event: myFunctionEvaluated(event, *myFunctionArgs), thing, id = myId)

					#Has kwargs, but not args
					elif (myFunctionKwargs != None):
						bindObject.Bind(eventType, lambda event: myFunctionEvaluated(event, **myFunctionKwargs), thing, id = myId)

					#Has neither args nor kwargs
					else:
						bindObject.Bind(eventType, lambda event: myFunctionEvaluated(event), thing, id = myId)

				#Binding mode for window key bindings
				elif (mode == 2):
					#Has both args and kwargs
					if ((myFunctionKwargs != None) and (myFunctionArgs != None)):
						bindObject.Bind(eventType, lambda event: myFunctionEvaluated(event, *myFunctionArgs, **myFunctionKwargs), id = myId)

					#Has args, but not kwargs
					elif (myFunctionArgs != None):
						bindObject.Bind(eventType, lambda event: myFunctionEvaluated(event, *myFunctionArgs), id = myId)

					#Has kwargs, but not args
					elif (myFunctionKwargs != None):
						bindObject.Bind(eventType, lambda event: myFunctionEvaluated(event, **myFunctionKwargs), id = myId)

					#Has neither args nor kwargs
					else:
						bindObject.Bind(eventType, lambda event: myFunctionEvaluated(event), id = myId)

				else:
					print("ERROR: Unknown mode", mode, "for betterBind()")

			#Skip empty functions
			if (myFunctionList != None):
				myFunctionList, myFunctionArgsList, myFunctionKwargsList = self.formatFunctionInputList(myFunctionList, myFunctionArgsList, myFunctionKwargsList)
				#Run each function
				for i, myFunction in enumerate(myFunctionList):
					#Skip empty functions
					if (myFunction != None):
						myFunctionEvaluated, myFunctionArgs, myFunctionKwargs = self.formatFunctionInput(i, myFunctionList, myFunctionArgsList, myFunctionKwargsList)
						bind(self, eventType, thing, myFunctionEvaluated, myFunctionArgs, myFunctionKwargs, myId, mode)

		#Containers
		def catalogueSizer(self, sizerLabel, sizer, panelLabel = None):
			"""Catalogues a sizer for future use.
			Sizers that are not explicitly given a panel will be assigned to the main panel (if there is one).

			sizerLabel (str) - The label for the sizer. Can be a integer
			sizer (wxSizer)   - The sizer object
			panelLabel (str) - The label for the associated panel. Can be an integer

			Example Input: catalogueSizer(0, sizer)
			Example Input: catalogueSizer(0, sizer, 0)
			"""

			#If this is the first sizer the user has added, the add it to the main sizer
			if (panelLabel == None):
				if ("-1" in self.panelDict):
					#Add this sizer with special settings that attach it to the main panel
					self.sizerDict[sizerLabel] = [sizer, "-1"]
					return

			#Add this sizer with the current settings
			self.sizerDict[sizerLabel] = [sizer, panelLabel]

		def cataloguePanel(self, panelLabel, panel):
			"""Catalogues a panel for future use.

			panelLabel (str) - The label for the panel. Can be a integer
			panel (wxPanel)   - The panel object

			Example Input:  cataloguePanel(0, panel)
			"""

			self.panelDict[panelLabel] = panel

		def catalogueSplitter(self, splitterLabel, splitter):
			"""Catalogues a splitter for future use.

			splitterLabel (str)  - The label for the splitter. Can be a integer
			splitter (wxSplitter) - The splitter object

			Example Input:  catalogueSplitter(0, splitter)
			"""

			self.splitterDict[splitterLabel] = splitter

		def catalogueTable(self, tableLabel, table):
			"""Catalogues a table for future use.

			tableLabel (str) - The label for the table. Can be a integer
			table (wxTable)   - The table object

			Example Input:  catalogueTable(0, table)
			"""

			self.tableDict[tableLabel] = [table, (0,0), (0,0)]

		def catalogueTableCurrentCellCoordinates(self, tableLabel, row, column):
			"""Catalogues a table for future use.

			tableLabel (str) - The label for the table. Can be a integer
			row (int)        - The currently selected row
			column (int)     - The currently selected column

			Example Input:  catalogueTable(0, 1, 1)
			"""

			table = self.tableDict[tableLabel][0]
			previousCell = self.tableDict[tableLabel][1]
			self.tableDict[tableLabel] = [table, (row, column), previousCell]

		def catalogueToolTip(self, triggerObjectLabel, toolTip):
			"""Catalogues a tool tip for future use.

			triggerObjectLabel (str) - The label for the object that triggers the tool tip
			toolTip (wxToolTip)      - The tool tip object

			Example Input:  catalogueToolTip(0, toolTip)
			"""

			self.toolTipDict[triggerObjectLabel] = toolTip

		def cataloguePopupWindow(self, popupWindowLabel, popupWindow, panel, textBox, internalVariables):
			"""Catalogues a tool tip for future use.

			popupWindowNumber (str)  - The label for the popup window. Can be an integer
			popupWindow (wxWindow)   - The tool tip object
			panel (wxPanel)          - The popup window's panel
			textBox (wxStaticText)   - The text inside the popup window
			internalVariables (dict) - {objectPosition: coordinates}

			Example Input:  cataloguePopupWindow(0, popupWindow)
			"""

			self.popupWindowDict[popupWindowLabel] = [popupWindow, panel, textBox, internalVariables]

		def catalogueCanvas(self, canvasLabel, canvas):
			"""Catalogues a canvas for future use.

			canvasLabel (str) - The label for the canvas. Can be a integer
			canvas (wxPanel)  - The panel object

			Example Input:  catalogueCanvas(0, canvas)
			"""

			self.canvasDict[canvasLabel] = canvas

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

	class ErrorHandler():
		"""Contains functions and variables to be used in error handling.
		This is here for convenience in programming.
		"""

		def __init__(self):
			"""Defines the internal variables needed to run.

			Example Input: Meant to be inherited by GUI().
			"""

			#General Errors
			self.ERROR_NONE    = 100 #No error happened
			self.ERROR_UNKNOWN = 101 #The type of error cannot be determined

			#File Errors
			self.ERROR_FILE_NONE = 200 #There is no file at the address given

		def requireType(variable, varType):
			"""Requires a specific variable to be a specific type.
			Otherwise, a TypeError is raised.

			variable (any) - The variable to check
			varType (any) - What type the variable should be. Can be a variable that is of the desired type

			Example Input: requireType(x, int)
			"""

			#Determine if variable type should be extracted
			if (type (varType) != type):
				varType = type(varType)

			#Determine if the given variable is of the desired type
			if (type(variable) != varType):
				#Determine what the message should be
				if (varType == int):
					message = "The tested variable must be an integer."
				elif (varType == str):
					message = "The tested variable must be a string."
				elif (varType == float):
					message = "The tested variable must be a float."
				elif (varType == list):
					message = "The tested variable must be a list."
				elif (varType == dict):
					message = "The tested variable must be a distionary."
				elif (varType == bool):
					message = "The tested variable must be a boolean"
				elif (varType == None):
					message = "The tested variable must be a None type."
				elif (varType == tuple):
					message = "The tested variable must be a tuple."
				elif (varType == complex):
					message = "The tested variable must be a complex number."
				elif (varType == set):
					message = "The tested variable must be a set."
				elif (varType == slice):
					message = "The tested variable must be a slice."
				else:
					message = "Cannot compare the tested variable to the given type, which is: " + str(varType) + "\nPlease add this type to requireType()"

				#Raise the error
				raise TypeError(message)

		def showError(self, errorNumber):
			"""Displays to the user what error happened.
			This function shouws non-lethal errors
			It is recommended that you use the variable name for the error type
			instead of the number that variable contains.

			errorNumber (int) - The number associated with the error type

			Example Input: showError(self.ERROR_UNKNOWN)
			"""

			############################################################
			#Expand this to show a unique message for every error type.#
			############################################################

			print("ERROR:", errorNumber)

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

			#Internal Variables
			self.statusBarOn = True
			self.toolBarOn = True

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
			if(threading.active_count() > 1):
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

		def onToggleItemEnable(self, event, *args, **kwargs):
			"""Enables or disables an item."""

			myItem = event.GetEventObject()

			if (myItem.IsEnabled()):
				myItem.Enable(False)
			else:
				myItem.Enable(True)

			event.Skip()

		def onToggleStatusBar(self, event, *args, **kwargs):
			"""Toggles the status bar on or off."""

			if(self.statusBarOn):
				self.statusbar.Hide()
				self.statusBarOn = False
			else:
				self.statusbar.Show()
				self.statusBarOn = True

			event.Skip()

		def onToggleToolBar(self, event, *args, **kwargs):
			"""Toggles the tool bar on or off."""
				
			if(self.toolBarOn):
				self.toolbar.Hide()
				self.toolBarOn = False
			else:
				self.toolbar.Show()
				self.toolBarOn = True

			event.Skip()

		#File Functions
		def onOpenFile(self, event, textCrtlLabel, *args, readOnly = None, **kwargs):
			"""Opens a file when given the label of a TextCtrl object that contains the directory.
			Returns a handler for that file.

			textCrtlLabel (str) - What the object containing the directory is called in the idCatalogue 
			readOnly (bool)     - If True: The file will be read only. If False: The file will be write only. If None: The file will be both read and write.
			
			Example Input: onOpenFile(event, "selectedDirectory")
			"""

			#Get the object that triggered the event
			parent = self.getObjectWithEvent(event)
			thing = parent.Utilities.getObjectWithLabel(textCrtlLabel)

			#Get the contents of the TextCtrl object
			filePath = thing.GetTextCtrlValue()

			#Determine if the file exists
			if (os.path.exists(filePath)):
				#Open the file
				if (readOnly == None):
					handle = open(filePath, 'r+')
				elif (readOnly):
					handle = open(filePath, 'r')
				else:
					handle = open(filePath, 'w')
			else:
				error = self.ERROR_FILE_NONE
				self.showError(error)
				handle = None

			self.queueValue(handle, textCrtlLabel)

			event.Skip()

		def onCloseFile(self, event, textCrtlLabel, handle, *args, **kwargs):
			"""Closes a file when given the label of a TextCtrl object that contains the directory and a handle for the file.
			If the file was written to, it will save the changes made to the file.
			Returns a handler for that file.

			textCrtlLabel (str)    - What the object containing the directory is called in the idCatalogue 
			handle (TextIOWrapper) - What the object containing the directory is called in the idCatalogue 
			
			Example Input: onCloseFile(event, handle)
			"""

			#Get the object that triggered the event
			parent = self.getObjectWithEvent(event)
			thing = parent.Utilities.getObjectWithLabel(textCrtlLabel)

			#Get the contents of the TextCtrl object
			filePath = thing.GetTextCtrlValue()

			#Determine if the file exists
			if (os.path.exists(filePath)):
					#CLose the file
					handle.close()
			else:
				error = self.ERROR_FILE_NONE
				self.showError(error)

			event.Skip()

		#Popup Window Functions
		def onTriggerPopupMenu(self, event, preFunction = [None, None, None], postFunction = [None, None, None]):
			"""The event that right-clicking triggers to pull up the popup menu."""

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
				position = event.GetPosition()
			
			self.PopupMenu(self.MyPopupMenu(self, preFunction, postFunction), position)

		def onPopupWindowMouseLeftDown(self, event, popupWindowNumber, *args, **kwargs):
			"""Allows the user to drag the popup window if the left mouse button is pressed.

			popupWindowNumber (int) - The index of the popup window in the popup window index.

			Example Input: onPopupWindowMouseLeftDown(event, 0)
			"""

			#Retrieve popup window object and variables
			popupWindow = self.getPopupWindow(popupWindowNumber)
			panel = self.getPopupWindowVariable(popupWindowNumber, "panel")

			#Calculate position for popup on screen
			popupWindow.Refresh()
			leftDownPosition = event.GetEventObject().ClientToScreen(event.GetPosition())
			windowPosition = popupWindow.ClientToScreen((0,0))
			panel.CaptureMouse()

			#Catalogue variables
			self.setPopupWindowVariable(popupWindowNumber, "leftDownPosition", leftDownPosition)
			self.setPopupWindowVariable(popupWindowNumber, "windowPosition", windowPosition)

			event.Skip()

		def onPopupWindowMouseMotion(self, event, popupWindowNumber, *args, **kwargs):
			"""Drags the popup window if the user presses the left mouse button.

			popupWindowNumber (int) - The index of the popup window in the popup window index.

			Example Input: onPopupWindowMouseMotion(event, 0)
			"""

			#Retrieve popup window object and variables
			popupWindow = self.getPopupWindow(popupWindowNumber)
			leftDownPosition = self.getPopupWindowVariable(popupWindowNumber, "leftDownPosition")
			windowPosition = self.getPopupWindowVariable(popupWindowNumber, "windowPosition")

			#Move the popup window
			if event.Dragging() and event.LeftIsDown():
				dragPosition = event.GetEventObject().ClientToScreen(event.GetPosition())
				newPosition = (windowPosition.x + (dragPosition.x - leftDownPosition.x),
						windowPosition.y + (dragPosition.y - leftDownPosition.y))
				popupWindow.Move(newPosition)

			event.Skip()

		def onPopupWindowMouseLeftUp(self, event, popupWindowNumber, *args, **kwargs):
			"""Disallows the user to drag the popup window if the left mouse button is pressed.

			popupWindowNumber (int) - The index of the popup window in the popup window index.

			Example Input: onPopupWindowMouseLeftUp(event, 0)
			"""

			#Retrieve popup window variables
			panel = self.getPopupWindowVariable(popupWindowNumber, "panel")

			#Stop dragging popup window
			if panel.HasCapture():
				panel.ReleaseMouse()

			event.Skip()

		def onPopupWindowRightUp(self, event, popupWindowNumber, *args, **kwargs):
			"""Closes the popup window when the right mouse button is clicked inside of the popup.

			popupWindowNumber (int) - The index of the popup window in the popup window index.

			Example Input: onPopupWindowRightUp(event, 0)
			"""

			#Retrieve popup window object
			popupWindow = self.getPopupWindow(popupWindowNumber)

			#Destroy the object
			popupWindow.Show(False)
			popupWindow.Hide()

			event.Skip()

		def onShowPopupWindow(self, event, popupWindowNumber, *args, **kwargs):
			"""Shows the popup window to the user.

			popupWindowNumber (int) - The index of the popup window in the popup window index.

			Example Input: onShowPopupWindow(event, 0)
			"""

			#Get the objects that this event controls
			widget = self.getObjectWithEvent(event)
			myFrame = self.getObjectParent(widget)
			popupWindow = myFrame.getPopupWindow(popupWindowNumber)

			#Position the popup window
			position = wx.GetMousePosition()
			popupWindow.Position(position, (0, 0))

			#Show the window
			popupWindow.Show(True)

			event.Skip()

		#Msic Functions
		def onDoNothing(self, event, *args, **kwargs):
			"""Does nothing."""

			event.skip()

		def onIdle(self, event):
			"""Runs functions only while the GUI is idle. It will pause running the functions if the GUI becomes active.
			WARNING: This is not working yet.
			"""
			global shownWindowsList

			print("@1", self.idleQueue)

			#Skip empty function list
			if (self.idleQueue != None):
				if (len(self.idleQueue) > 0):
					#Run each function
					for myFunction, myFunctionArgs, myFunctionKwargs, shown in idleQueue:
						#Check for pre-function conditions
						if (shown):
							#Check if the window is shown yet
							if (self in shownWindowsList):
								continue

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

		def onQueueValue(self, event, *args, **kwargs):
			"""Gets the value of an input object when provided with a label.
			The value is queued under the same label as the object it came from
			unless otherwise specified by the user.
			"""

			#Unpack Input Variables
			label = args[0] #(str) - A unique string associated with an object

			#Check if the object's value will be queued under a specific label
			if (len(args) > 1):
				valueLabel = args[1] #(str) - A unique string that the object's value will be queued under
			else:
				valueLabel = label

			#Get the wxObject
			thing = self.getObjectWithEvent(event)

			#Get the value
			value = self.getObjectValue(thing)
			
			#Queue the value so the user can access it
			if (value != None):
				self.queueValue(value, valueLabel)

			event.Skip()

		def onSwitchWindow(self, event, *args, **kwargs):
			"""A Message on how this function is SUPPOSED to be called."""

			print("AttributeError: 'Window' object has no attribute 'onSwitchWindow'")
			print("Instead of \"self.onSwitchWindow\" use gui.onSwitchWindow")

			event.Skip()

		def onShowWindow(self, event, *args, **kwargs):
			"""A Message on how this function is SUPPOSED to be called."""

			print("AttributeError: 'Window' object has no attribute 'onShowWindow'")
			print("Instead of \"self.onShowWindow\" use gui.onShowWindow")

			event.Skip()

		def onHideWindow(self, event, *args, **kwargs):
			"""A Message on how this function is SUPPOSED to be called."""

			print("AttributeError: 'Window' object has no attribute 'onHideWindow'")
			print("Instead of \"self.onHideWindow\" use gui.onHideWindow")

			event.Skip()

		def onCloseWindow(self, event, *args, **kwargs):
			"""A Message on how this function is SUPPOSED to be called."""

			print("AttributeError: 'Window' object has no attribute 'onCloseWindow'")
			print("Instead of \"self.onCloseWindow\" use gui.onCloseWindow")

			event.Skip()

		def onSetObjectValue(self, event, *args, **kwargs):
			"""Changes the value of a wxObject that is already on a shown screen."""

			#Unpack Input Variables
			label = args[0] #(str)    - A unique string associated with the object
			newValue = args[1] #(str) - What the new value of the object will be

			#Change the wxObject's value
			try:
				self.setObjectValue(label, newValue)
			except:
				GUI.Utilities.setObjectValue(self, label, newValue)

			event.Skip()

		def onSetObjectValueWithLabel(self, event, *args, **kwargs):
			"""Changes the value of a wxObject that is already on a shown screen."""

			#Unpack Input Variables
			label = args[0] #(str)    - A unique string associated with the object
			newValue = args[1] #(str) - What the new value of the object will be

			#Change the wxObject's value
			try:
				self.setObjectValueWithLabel(label, newValue)
			except:
				GUI.Utilities.setObjectValueWithLabel(self, label, newValue)

			event.Skip()

		def onGetObjectValueWithLabel(self, event, label, index = False, full = False, *args, **kwargs):
			"""Gets the value of a wxObject that is already on a shown screen."""

			#Get the wxObject's value
			try:
				self.getObjectValueWithLabel(label, index, full)
			except:
				GUI.Utilities.getObjectValueWithLabel(self, label, index, full)

			event.Skip()

		def onToggleObjectWithLabel(self, event, label, state = None, showHide = False, autoSize = True):
			"""Enables or disables an item."""

			self.toggleObjectWithLabel(label, state, showHide, autoSize)

			event.Skip()

		def onEnableObjectWithLabel(self, event, label, *args, **kwargs):
			"""Enables an item if it is disabled."""

			self.enableObjectWithLabel(label)

			event.Skip()

		def onDisableObjectWithLabel(self, event, label, *args, **kwargs):
			"""Disables an item if it is enabled."""

			self.disableObjectWithLabel(label)

			event.Skip()

		def onShowObjectWithLabel(self, event, label, *args, **kwargs):
			"""Shows an item if it is hidden."""

			self.showObjectWithLabel(label)

			event.Skip()

		def onHideObjectWithLabel(self, event, label, *args, **kwargs):
			"""Disables an item if it is shown."""

			self.hideObjectWithLabel(label)

			event.Skip()

		def onKeyPress(self, event, *args, **kwargs):
			"""Runs a function on a specific key press.
			Inorder to bind multiple keys to the same object, the keys must be passed in as a list.

			Keep in mind that this function runs every time any key is pressed.
			The function associated with that key will only run if the current.
			key is the same as the associated key.
			"""

			#Create the sub-function that does the binding
			def runFunction(event, myFunctionEvaluated, myFunctionArgs, myFunctionKwargs):
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
					myFunctionEvaluated(event, *myFunctionArgs, **myFunctionKwargs)

				#Has args, but not kwargs
				elif (myFunctionArgs != None):
					myFunctionEvaluated(event, *myFunctionArgs)

				#Has kwargs, but not args
				elif (myFunctionKwargs != None):
					myFunctionEvaluated(event, **myFunctionKwargs)

				#Has neither args nor kwargs
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

							runFunction(event, myFunctionEvaluated, myFunctionArgs, myFunctionKwargs)

			event.Skip()

		#Table Functions
		def onSelectCell(self, event):
			"""Queues the row and column for the user."""
			
			#Get the cell coordinates
			row = event.GetRow()
			column = event.GetCol()

			#Determine which table it is
			thing = self.getObjectWithEvent(event)
			which = -1
			for i, table in enumerate(self.tableDict.keys()):
				if (thing == self.tableDict[table][0]):
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

		def onTableArrowKeyMove(self, event, *args, **kwargs):
			"""Traverses the cells in the table using the arrow keys."""
			
			#Get the key that was pressed
			keyCode = event.GetKeyCode()

			#Determine which key was pressed
			if (keyCode == wx.WXK_UP):
				self.gird.MoveCoursorUp(True)
			elif (keyCode == wx.WXK_DOWN):
				self.grid.MoveCoursorDown(True)
			elif (keyCode == wx.WXK_LEFT):
				self.grid.MoveCoursorLeft(True)
			elif (keyCode == wx.WXK_RIGHT):
				self.grid.MoveCoursorRight(True)

			event.Skip()

		def onTableEditOnClick(self, event, tableNumber, edit):
			"""Allows the user to enter 'edit cell mode' on a single click instead of a double click
			This is currently not working

			tableNumber (int) - What the table is called in the table catalogue
			edit (bool)       - If True: The user will enter 'edit cell mode' on a single click instead of a double click
								If False: The user will enter 'edit cell mode' on a double click instead of a single click

			Example Input: onTableEditOnClick(0, True)
			"""

			### NOT WORKING YET ###
			if (edit):
				#Get the wxObject's frame
				myFrame = self.getObjectWithEvent(event)
				
				classType = myFrame.GetClassName()
				if (classType != "wxFrame"):
					myFrame = GUI.Utilities.getObjectParent(None, myFrame)

				#Move editor
				table = myFrame.getTable(tableNumber)
				row, column = self.getTableCurrentCell(tableNumber)
				# wx.grid.GridCellEditor(row, column, table)

	class Menus():
		"""Contains functions used for menus and such.
		Includes dropdown menu bars, popup menus, and tool bars.
		Menus are groups of convenient selections that are out of the way.
		This is here for convenience in programming.
		"""

		def __init__(self):
			"""Does nothing. This is here to comply with PEP 8 standards.

			Example Input: Meant to be inherited by GUI().
			"""

			pass

		#Dropdown Menu Bars
		def addMenuBar(self):
			"""Adds a menu bar to the top of the window.
			Menus with menu items can be added to this.

			Example Input: addMenuBar()
			"""

			self.menubar = wx.MenuBar()
			self.SetMenuBar(self.menubar)

		def addMenu(self, menuNumber, text, myLabel = None, detachable = False, enabled = True):
			"""Adds a menu to a pre-existing menubar.
			This is a collapsable array of menu items.

			menuNumber (int)  - The label for this menu. Can be a string
			text (str)        - What the menu is called
				If you add a '&', a keyboard shortcut will be made for the letter after it
			myLabel (str)     - What this is called in the idCatalogue
			detachable (bool) - If True: The menu can be undocked
			enabled (bool)    - If True: The user can interact with this

			Example Input: addMenu(0, "&File")
			Example Input: addMenu("first", "&File")
			"""

			#Create menu
			if (detachable):
				myMenu = wx.Menu(wx.MENU_TEAROFF)
			else:
				myMenu = wx.Menu()

			#Add menu
			self.menubar.Append(myMenu, text)

			#Determine enabling
			if (not enabled):
				#Determine menu position
				menuList = self.menubar.GetMenus()
				myText =  re.sub("&", "", text)
				for i, item in enumerate(menuList):
					menu, menuText = item
					if (menuText == myText):
						#Disable menu
						self.menubar.EnableTop(i, False)
						break
				else:
					print("ERROR: Menu", menuNumber, "cannot be found")

			#Catalogue menu
			self.menuDict[menuNumber] = myMenu #Save Menu Address

			if (myLabel != None):
				myId = self.newId(myLabel)
				self.addToId(myMenu, myLabel)

		def addMenuItem(self, which, text = "", myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, myLabel = None, 
			icon = None, internal = False, special = None, check = None, default = False, enabled = True):
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
					myId = self.newId()

			elif (myLabel != None):
				myId = self.newId(myLabel)

			else:
				myId = self.newId()

			#Create the Menu Item
			myMenu = self.menuDict[which]
			menuItem = wx.MenuItem(myMenu, myId, text)

			#Create Menu Item
			if (check == None):
				menuItem = wx.MenuItem(myMenu, myId, text)

				#Determine icon
				if (icon != None):
					image = self.getImage(icon, internal)
					image = self.convertBitmapToImage(image)
					image = image.Scale(16, 16, wx.IMAGE_QUALITY_HIGH)
					image = self.convertImageToBitmap(image)
					menuItem.SetBitmap(image)
			else:
				if (check):
					menuItem = wx.MenuItem(myMenu, myId, text, kind = wx.ITEM_CHECK)
				else:
					menuItem = wx.MenuItem(myMenu, myId, text, kind = wx.ITEM_RADIO)

			#Add Menu Item
			myMenu.Append(menuItem)

			#Determine initial value
			if (check != None):
				if (default):
					myMenu.Check(myId, True)

			#Determine enabling
			if (not enabled):
				menuItem.Enable(False)

			#Determine how to do the bound function
			if (myFunction == None):
				if (special != None):
					if (special[0] == "q" or special[0] == "e"):
						self.betterBind(wx.EVT_MENU, menuItem, "self.onExit")
					elif (special[0] == "c"):
						self.betterBind(wx.EVT_MENU, menuItem, "self.onQuit")
					elif (special[0] == "h"):
						self.betterBind(wx.EVT_MENU, menuItem, "self.onHide")
					elif (special[0] == "s"):
						self.betterBind(wx.EVT_MENU, menuItem, "self.onToggleStatusBar")
					elif (special[0] == "t"):
						self.betterBind(wx.EVT_MENU, menuItem, "self.onToggleToolBar")
			else:
				self.betterBind(wx.EVT_MENU, menuItem, myFunction, myFunctionArgs, myFunctionKwargs)
		
			self.addToId(menuItem, myLabel)

		def addMenuSeparator(self, which, myLabel = None):
			"""Adds a line to a specific pre-existing menu to separate menu items.

			which (int) - The label for the menu to add this to. Can be a string

			Example Input: addMenuSeparator(0)
			"""

			if (myLabel != None):
				myId = self.newId(myLabel)

			else:
				myId = self.newId()

			myMenu = self.menuDict[which]
			separator = wx.MenuItem(myMenu, myId, "", kind = wx.ITEM_SEPARATOR)
			myMenu.Append(separator)

		def addMenuSub(self, which, menuNumber, text):
			"""Adds a sub menu to a specific pre-existing menu.
			To adding items to a sub menu is the same as for menus.

			which (int) - The label for the menu to add this to. Can be a string
			menuNumber (int) - The label for this menu. Can be a string
			text (str)  - The label for the menu item. This is what is shown to the user

			Example Input: addMenuSub(0, "I&mport")
			"""

			subMenu = wx.Menu()
			self.menuDict[menuNumber] = subMenu #Save Menu Address

			myId = self.newId()
			myMenu = self.menuDict[which]
			myMenu.Append(myId, text, subMenu)

		#Popup Menus
		def createPopupMenu(self, preFunction = None, preFunctionArgs = None, preFunctionKwargs = None, postFunction = None, postFunctionArgs = None, postFunctionKwargs = None, rightClick = True):
			"""Enables a popup menu.

			preFunction (str)       - The function that is ran after the popup menu appears
			preFunctionArgs (any)   - The arguments for 'preFunction'
			preFunctionKwargs (any) - The keyword arguments for 'preFunction'function

			postFunction (str)       - The function that is ran after the popup menu appears
			postFunctionArgs (any)   - The arguments for 'postFunction'
			postFunctionKwargs (any) - The keyword arguments for 'postFunction'function

			rightClick - Whether right clicking (True) or left clicking (False) will bring it up.
				- If None: Will not respond to a right click. Assumes you will trigger the popup menu some other way.

			Example Input: createPopupMenu()
			Example Input: createPopupMenu(rightClick = False)
			Example Input: createPopupMenu(rightClick = None)
			Example Input: createPopupMenu(myFrame.onHideWindow, 0)
			"""

			#Check for main panel
			if ("-1" in self.panelDict):
				identity = self.panelDict["-1"]
			else:
				identity = self

			#Bind functions
			if (rightClick != None):
				if (rightClick):
					self.betterBind(wx.EVT_RIGHT_DOWN, identity, self.onTriggerPopupMenu, [[preFunction, preFunctionArgs, preFunctionKwargs], [postFunction, postFunctionArgs, postFunctionKwargs]])
				else:
					self.betterBind(wx.EVT_LEFT_DOWN, identity, self.onTriggerPopupMenu, [[preFunction, preFunctionArgs, preFunctionKwargs], [postFunction, postFunctionArgs, postFunctionKwargs]])

		def addPopupMenuItem(self, text, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, 
			special = None, icon = None, internal = False, myLabel = None, hidden = False, enabled = True, check = None, default = False):
			"""Adds an item to the popup menu.
			This must be done before it gets triggered.

			text (str)      - The label of the item. This is what is shown to the user
			special (str)   - Declares if the item has a special pre-defined functionality
				"new", "open", "save", "quit" or "exit", "status", "tool". Only the first letter matters
			icon (str)      - The file path to the icon for the menu item
				If None: No icon will be shown
			internal (bool) - If True: The icon provided is an internal icon, not an external file
				
			myFunction (str)       - The function that is ran when the item is clicked
			myFunctionArgs (any)   - The arguments for 'myFunction'
			myFunctionKwargs (any) - The keyword arguments for 'myFunction'function

			check (bool) - Determines the type of menu item it is
				~If None:  Normal menu item
				~If True:  Check box menu item
				~If False: Radio Button menu item

			default (bool) - Determines if the checkbox/radio button is intially checked/pressed
			hidden (bool)  - If True: The widget is hidden from the user, but it is still created
			enabled (bool) - If True: The user can interact with this

			addPopupMenuItem("Minimize", "self.onMinimize")
			addPopupMenuItem("Hide", myFrame.onHideWindow, 0)
			addPopupMenuItem("Show Sdvanced Settings", self.onShowAdvancedSettings, check = True)
			"""

			#Ensure correct format
			if ((special != None) and (type(special) != str)):
				print("ERROR: 'special' should be a string for addPopupMenuItem().")
				return None
			
			#Catalogue the item
			if (myFunction != None):
				if (special != None):
					special = special.lower()
					if (special[0:2] == "mi"):
						self.popupItemsList.append([text, myLabel, "self.onMinimize", None, None, icon, internal, check, default, enabled, hidden])
					elif (special[0:2] == "ma"):
						self.popupItemsList.append([text, myLabel, "self.onMaximize", None, None, icon, internal, check, default, enabled, hidden])
				else:
					self.popupItemsList.append([text, myLabel, myFunction, myFunctionArgs, myFunctionKwargs, icon, internal, check, default, enabled, hidden])

		def addPopupMenuSeparator(self, myLabel = None, hidden = False):
			"""Adds an separator line to the popup menu
			This must be done before it gets triggered.

			addPopupMenuSeparator()
			"""

			self.popupItemsList.append([None, myLabel, hidden])

		def clearPopupMenu(self):
			"""Clears the popup menu of all items."""

			self.popupItemsList = []

		#Tool Bars
		def addToolBar(self):
			"""Adds a tool bar to the top of the window."""

			self.toolbar = self.CreateToolBar()

		def addTool(self, icon, internal = None, special = None, myFunction = None,  myFunctionArgs = None, myFunctionKwargs = None):
			"""Adds a tool to the tool bar.

			icon (str) - The file path to the icon for the menu item
				If None: No icon will be shown
			internal (bool) - If True: The icon provided is an internal icon, not an external file

			special (str) - Declares if the item has a special pre-defined functionality
				"new", "open", "save", "quit" or "exit", "status", "tool". Only the first letter matters
			
			myFunction (str) - The function that is ran when the item is clicked
			myFunctionArgs (any)   - The arguments for 'myFunction'
			myFunctionKwargs (any) - The keyword arguments for 'myFunction'function

			Example Input: addTool('exit.bmp')
			Example Input: addTool('exit.bmp', "exit")
			"""

			image = self.getImage(icon, internal)
			image = self.convertBitmapToImage(image)
			image = image.Scale(16, 16, wx.IMAGE_QUALITY_HIGH)
			image = self.convertImageToBitmap(image)
			myTool = self.toolbar.AddTool(self.newId(), '', image)
			self.toolbar.Realize()

			if (myFunction == None):
				if (special != None):
					if (special[0] == "q" or special[0] == "e"):
						self.betterBind(wx.EVT_TOOL, myTool, "self.onExit")
						return
			
			self.betterBind(wx.EVT_Tool, myTool, myFunction, myFunctionArgs, myFunctionKwargs)          

			self.addToId(myTool, myLabel)

		def addToolSpacer(self):
			"""Adds a spacer to the tool bar."""

			self.toolbar.AddSeparator()         

		#Status Bars
		def addStatusBar(self):
			"""Adds a status bar to the bottom of the window."""

			self.statusbar = self.CreateStatusBar()

		def setStatusText(self, message):
			"""Sets the text shown in the status bar.

			message (str) - What the status bar will say.

			Example Input: setStatusText("Ready")`
			"""

			self.statusbar.SetStatusText(message)

		class MyPopupMenu(wx.Menu):
			"""Creates a pop up menu.
			Because of the way that the popup menu is created, the items within must be
			determineed before the initial creation.

			Note: The runFunction is NOT an event function. It is a normal function.

			In order to allow for customization, the user creates a dictionary of
			{labels:functions}. This dictionary is then used to populate the menu.
			"""

			def __init__(self, parent, preFunction = [None, None, None], postFunction = [None, None, None]):
				"""Defines the internal variables needed to run.

				Example Input: MyPopupMenu(self)
				"""

				#Internal Variables
				self.parent = parent
				self.labelList = [] 
				self.menuItemList = [] #[[myId, temporary item, hidden]]

				#Configure menu
				wx.Menu.__init__(self)
				self.discoverLabels()

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
				self.populateMenu()

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

			def __del__(self):
				"""Removes the items form the id catalogue."""
				global idCatalogue
				
				for myLabel in self.labelList:
					del idCatalogue[myLabel]

			def discoverLabels(self):
				"""Searches for items with labels and catlogues them."""

				for i, item in enumerate(self.parent.popupItemsList):
					#Create id
					if (item[1] != None):
						myId = self.parent.newId(item[1])
						self.labelList.append(item[1])

						#Record a temporary item
						if (item[0] != None):
							if (item[7] != None):
								if (item[7]):
									preItem = wx.MenuItem(self, myId, item[0], kind = wx.ITEM_CHECK)
								else:
									preItem = wx.MenuItem(self, myId, item[0], kind = wx.ITEM_RADIO)
							else:
								preItem = wx.MenuItem(self, myId, item[0])
						else:
							preItem = wx.MenuItem(self, myId, "", kind = wx.ITEM_SEPARATOR)

						#Catlogue temporary item
						self.parent.addToId(preItem, item[1])
					else:
						#Irrelevant item
						myId = self.parent.newId()
						preItem = None

					#Remember id
					self.menuItemList.append([myId, preItem, item[-1]])

			def populateMenu(self):
				"""Uses a dictionary to populate the menu with items and bound events."""

				#Create the menu
				if (len(self.parent.popupItemsList) != 0):
					for i, item in enumerate(self.parent.popupItemsList):
						myId, preItem, hidden = self.menuItemList[i]

						#Check for preFunction changes to the menu item
						if (preItem != None):
							##Kind
							if ((preItem.GetKind() == wx.ITEM_SEPARATOR) and (item[0] != None)):
								item[0] = None
							
							elif ((preItem.GetKind() == wx.ITEM_NORMAL) and (item[7] != None)):
								item[7] = None

							elif ((preItem.GetKind() == wx.ITEM_CHECK) and (item[7] != True)):
								item[7] = True

							elif ((preItem.GetKind() == wx.ITEM_RADIO) and (item[7] != False)):
								item[7] = False

							##Text
							if (item[0] != None):
								myText = re.sub("&", "", item[0])
								if (preItem.GetItemLabelText() != myText):
									item[0] = preItem.GetItemLabelText()

							##Visibility
							# if ((hidden) and (item[-1] != True)):
							# 	item[-1] = True

							elif ((not hidden) and (item[-1] == True)):
								item[-1] = True

						#Create the menu item
						if (item[0] != None):
							#Add normal menu item
							self.addItem(*item, myId = myId)
						else:
							#Add separator
							separator = wx.MenuItem(self, myId, "", kind = wx.ITEM_SEPARATOR)
							
							#Do not show the separator if it is hidden, but still create it
							if (not item[-1]):
								self.Append(separator)

							if (item[1] != None):
								self.parent.addToId(separator, item[1])

			def addItem(self, text, myLabel = None, myFunction = None, myFunctionArgs = None, myFunctionKwargs = None, 
				icon = None, internal = False, check = None, default = False, enabled = True, hidden = False, myId = None):
				"""Adds an item to the popup menu.

				text (str)             - The label of the item. This is what is shown to the user
				myFunction (str)       - The function that is ran when the item is clicked
				myFunctionArgs (any)   - The arguments for 'myFunction'
				myFunctionKwargs (any) - The keyword arguments for 'myFunction'function

				icon (str) - The file path to the icon for the menu item
					If None: No icon will be shown
				internal (bool) - If True: The icon provided is an internal icon, not an external file

				Example Input: addItem("Minimize", "min")
				Example Input: addItem("Close", "self.onQuit", icon = "close", internal = True)
				"""

				#Configure menu item
				if (check == None):
					myItem = wx.MenuItem(self, myId, text)
					if (icon != None):
						image = self.parent.getImage(icon, internal)
						image = self.parent.convertBitmapToImage(image)
						image = image.Scale(16, 16, wx.IMAGE_QUALITY_HIGH)
						image = self.parent.convertImageToBitmap(image)
						myItem.SetBitmap(image)
				else:
					if (check):
						myItem = wx.MenuItem(self, myId, text, kind = wx.ITEM_CHECK)
					else:
						myItem = wx.MenuItem(self, myId, text, kind = wx.ITEM_RADIO)

					if (default):
						self.Check(myId, True)

				#Determine enabling
				if (not enabled):
					myItem.Enable(False)

				#Do not show the item if it is hidden, but still create it
				if (not hidden):
					self.Append(myItem)

				if (myFunction != None):
					self.parent.betterBind(wx.EVT_MENU, myItem, myFunction, myFunctionArgs, myFunctionKwargs)

				if (myLabel != None):
					self.parent.addToId(myItem, myLabel)

	class Sizers():
		"""Contains functions used for sizers and such. Supports Wizards.
		Sizers are what structures the GUI layout. They allow for auto-adjustment.
		This is here for convenience in programming.
		"""

		def __init__(self):
			"""Defines the internal variables needed to run.

			Example Input: Meant to be inherited by GUI().
			"""

			pass

		def getSizer(self, sizerNumber = None, returnPanel = False, returnAny = False):
			"""Returns a sizer when given the sizer's index number.

			sizerNumber (int)  - The index number of the sizer. If None, the whole sizer list is returned
			returnPanel (bool) - If True: The panel number that the sizer corresponds to will also be returned 
			returnAny (bool)   - If True: Any sizer will be returned.

			Example Input: getSizer(0)
			Example Input: getSizer(0, returnPanel = True)
			"""

			if (returnAny):
				keyList, valueList = list(self.sizerDict.items())[0]
				sizer, panelNumber = valueList

				if (returnPanel):
					return sizer, panelNumber
				else:
					return sizer

				return sizer[0]

			if (sizerNumber != None):
				#Check for sizer object instead of sizer number
				if ((type(sizerNumber) != int) and (type(sizerNumber) != str)):
					sizer = sizerNumber
				else:
					sizer = self.sizerDict[sizerNumber][0]

				if (returnPanel):
					panelNumber = self.sizerDict[sizerNumber][1]
					return sizer, panelNumber
				else:
					return sizer
			else:
				return self.sizerDict

		def addToSizer(self, sizer, thing, flex, flags, border):
			"""Adds an object to the sizer or window.

			sizer (wxSizer)  - The sizer object that will be added to. Can also be a wxWindow object
			thing (wxObject) - What will be added to the sizer
			flex (int)       - Only applies to Box Sizers. Allows the box sizer to act like a flex grid sizer
							   If 0: The grid is unchangable
							   Otherwise: Allows this section of the box sizer to flex. Can be a boolean
			flags (str)      - Things that affect the sizer's behavior
			border (int)     - If a border flag is used, this is how many pixels the border will be

			Example Input: addToSizer(sizer, thing, 0, flags, 5)
			"""

			sizer.Add(thing, int(flex), eval(flags), border)

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
							print("ERROR: Unknown combination flag", flag)

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
							print("ERROR: Unknown alignment flag", flag)

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
							print("ERROR: Unknown border flag", flag)

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
							print("ERROR: Unknown expand flag", flag)

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
							print("ERROR: Unknown fixture flag", flag)

					##Unknown Action
					else:
						print("ERROR: Unknown flag", flag)
			else:
				fixedFlags = "0"

			#Determine stretchability
			if (stretchable):
				position = 1
			else:
				position = 0

			return fixedFlags, position, border

		def updateWindow(self, autoSize = None, wizardPageNumber = None):
			"""Refreshes what the window looks like when things on the top-level sizer are changed.

			autoSize (bool)         - If True: the window size will be changed to fit the sizers within
									  If False: the window size will be what was defined when it was initially created
									  If None: the internal autosize state will be used
			wizardFrameNumber (int) - The number of the wizard page. If None, it assumes either a frame or a panel

			Example Input: updateWindow()
			Example Input: updateWindow(autoSize = False)
			"""

			#Determine if it is a wizard or not
			if (wizardPageNumber != None):
				exec("identity = self.m_wizPage" + str(wizardPageNumber))
			else:
				#Determine if a main panel has been created
				classType = self.GetClassName()

				if (classType != "wxFrame"):
					identity = GUI.Utilities.getObjectParent(None, self)
				else:
					identity = self

			#Check for main panel
			# sizer, panelNumber = identity.getSizer(0, True)
			sizer, panelNumber = identity.getSizer(None, True, returnAny = True)

			#Refresh the window
			if (autoSize == None):
				autoSize = identity.autoSize

			if (panelNumber == "-1"):
				# identity.SetSizerAndFit(sizer)
				panel = identity.getPanel(panelNumber)
				panel.SetSizerAndFit(sizer)

			else:
				identity.SetSizerAndFit(sizer)

			# if (wizardPageNumber != None):
			# 	sizer.Fit(identity)

			#Auto-size the window
			if (autoSize):
				##Toggle the window size before setting to best size
					bestSize = identity.GetBestSize()
					modifiedSize = (bestSize[0] + 5, bestSize[1] + 5)
					identity.SetSize(modifiedSize)
					identity.SetSize(bestSize)

		def nestSizerInSizer(self, insideNumber, outsideNumber, flags = "c1", stretchable = True, border = 5, 
			autoSize = False, flex = 1, wizardPageNumber = None):
			"""Convenience function. Nests a sizer in another sizer.

			Example Input: nestSizerInSizer(1, 0)
			"""

			self.nestObjectWithIndex(insideNumber, "sizer", outsideNumber, "sizer", flags, stretchable, border, autoSize, flex, wizardPageNumber)

		def nestSizerInPanel(self, insideNumber, outsideNumber, flags = "c1", stretchable = True, border = 5, 
			autoSize = False, flex = 1, wizardPageNumber = None):
			"""Convenience function. Nests a sizer in a panel.

			Example Input: nestSizerInPanel(1, 0)
			"""

			self.nestObjectWithIndex(insideNumber, "sizer", outsideNumber, "panel", flags, stretchable, border, autoSize, flex, wizardPageNumber)

		def nestSizerInSplitter(self, insideNumber, outsideNumber, flags = "c1", stretchable = True, border = 5, 
			autoSize = False, flex = 1, wizardPageNumber = None):
			"""Convenience function. Nests a sizer in a splitter.

			Example Input: nestSizerInSplitter(0, 0)
			"""

			self.nestObjectWithIndex(insideNumber, "sizer", outsideNumber, "splitter", flags, stretchable, border, autoSize, flex, wizardPageNumber)

		def nestPanelInPanel(self, insideNumber, outsideNumber, flags = "c1", stretchable = True, border = 5, 
			autoSize = False, flex = 1, wizardPageNumber = None):
			"""Convenience function. Nests a panel in another panel.

			Example Input: nestPanelInPanel(1, 0)
			"""

			self.nestObjectWithIndex(insideNumber, "panel", outsideNumber, "panel", flags, stretchable, border, autoSize, flex, wizardPageNumber)

		def nestPanelInSizer(self, insideNumber, outsideNumber, flags = "c1", stretchable = True, border = 5, 
			autoSize = False, flex = 1, wizardPageNumber = None):
			"""Convenience function. Nests a panel in a sizer.

			Example Input: nestPanelInSizer(0, 0)
			"""

			self.nestObjectWithIndex(insideNumber, "panel", outsideNumber, "sizer", flags, stretchable, border, autoSize, flex, wizardPageNumber)

		def nestPanelInSplitter(self, insideNumber, outsideNumber, flags = "c1", stretchable = True, border = 5, 
			autoSize = False, flex = 1, wizardPageNumber = None):
			"""Convenience function. Nests a panel in a splitter.

			Example Input: nestPanelInSplitter(0, 0)
			"""

			self.nestObjectWithIndex(insideNumber, "panel", outsideNumber, "splitter", flags, stretchable, border, autoSize, flex, wizardPageNumber)

		def nestSplitterInSplitter(self, insideNumber, outsideNumber, flags = "c1", stretchable = True, border = 5, 
			autoSize = False, flex = 1, wizardPageNumber = None):
			"""Convenience function. Nests a splitter in another splitter.

			Example Input: nestSplitterInSplitter(1, 0)
			"""

			self.nestObjectWithIndex(insideNumber, "splitter", outsideNumber, "splitter", flags, stretchable, border, autoSize, flex, wizardPageNumber)

		def nestSplitterInSizer(self, insideNumber, outsideNumber, flags = "c1", stretchable = True, border = 5, 
			autoSize = False, flex = 1, wizardPageNumber = None):
			"""Convenience function. Nests a splitter in a sizer.

			Example Input: nestSplitterInSizer(1, 0)
			"""

			self.nestObjectWithIndex(insideNumber, "splitter", outsideNumber, "sizer", flags, stretchable, border, autoSize, flex, wizardPageNumber)

		def nestSplitterInPanel(self, insideNumber, outsideNumber, flags = "c1", stretchable = True, border = 5, 
			autoSize = False, flex = 1, wizardPageNumber = None):
			"""Convenience function. Nests a splitter in a panel.

			Example Input: nestSplitterInPanel(1, 0)
			"""

			self.nestObjectWithIndex(insideNumber, "splitter", outsideNumber, "panel", flags, stretchable, border, autoSize, flex, wizardPageNumber)

		def nestObjectWithIndex(self, insideNumber, insideType, outsideNumber, outsideType, flags = "c1", stretchable = True, border = 5, 
			autoSize = False, flex = 1, wizardPageNumber = None):
			"""Nests an object in another using their index numbers.

			insideNumber (int)  - The index number of the inner wxObject
			insideType (str)    - Declares what the inside object is. "panel", "sizer", "splitter". Only the first two letters are necissary
			outsideNumber (int) - The index number of the outer wxObject
			outsideType (str)   - Declares what the outside object is. "panel", "sizer", "splitter". Only the first two letters are necissary

			flags (list)        - A list of strings for which flag to add to the sizer
			stretchable (bool)  - Whether or not the item will grow and shrink with respect to a parent sizer
			border (int)        - How many pixels of blank space there is between the two spacers
			autoSize (bool)     - If True: the window size will be changed to fit the sizers within
								  If False: the window size will be what was defined when it was initially created
								  If None: the internal autosize state will be used

			wizardFrameNumber (int) - The number of the wizard page. If None, it assumes either a frame or a panel

			Example Input: nestObjectWithIndex(0, "sizer", 1, "sizer")
			Example Input: nestObjectWithIndex(0, "panel", 0, "sizer")
			Example Input: nestObjectWithIndex(0, "splitter", 0, "sizer")
			Example Input: nestObjectWithIndex(1, "panel", 0, "panel")
			"""

			#Ensure correct format
			if ((type(insideType) != str) or (type(outsideType) != str)):
				print("ERROR: Types should be strings for nestObjectWithIndex().")
				return None

			#Ensure correct caseing
			insideType = insideType.lower()
			outsideType = outsideType.lower()

			#Get what the inside object is
			if (insideType[0:2] == "si"):
				insideObject = self.getSizer(insideNumber)

			elif (insideType[0] == "p"):
				insideObject = self.getPanel(insideNumber)

			elif (insideType[0:2] == "sp"):
				insideObject = self.getSplitter(insideNumber)

			else:
				print("ERROR: The inside object " + str(insideType) + "does not exist.")
				return None

			#Get what the outside object is
			if (outsideType[0:2] == "si"):
				outsideObject = self.getSizer(outsideNumber)

			elif (outsideType[0] == "p"):
				outsideObject = self.getPanel(outsideNumber)

			elif (outsideType[0:2] == "sp"):
				outsideObject = self.getSplitter(outsideNumber)

			else:
				print("ERROR: The inside object " + str(outsideType) + "does not exist.")
				return None

			#Pass them onto the main function
			self.nestObject(insideObject, outsideObject, flags, stretchable, border, autoSize, flex, wizardPageNumber)

		def nestObject(self, insideObject, outsideObject, flags = "c1", stretchable = True, border = 5, 
			autoSize = False, flex = 1, wizardPageNumber = None):
			"""Nests an object in another when given the objects themselves.

			insideObject (wxObject) - The object on the inside
			outsideObject (wxObject) - The object on the outside

			Example Input: nestObject(insideSizer, outsideSizer)
			"""

			#Check for user error
			if (type(outsideObject) == str):
				print("ERROR: Use nestObjectWithIndex() instead of nestObject()")
				return None

			#Get Attributes
			flags, position, border = self.getItemMod(flags, stretchable, border)

			#Get what the objects are
			insideClass = insideObject.GetClassName()
			outsideClass = outsideObject.GetClassName()

			#Configure classes for sizers
			##This is to make the next section more readable
			if ((insideClass == "wxGridSizer") or (insideClass == "wxFlexGridSizer") or (insideClass == "wxBagGridSizer") or (insideClass == "wxBoxSizer") or (insideClass == "wxStaticBoxSizer")):
				insideClass = "wxSizer"

			if ((outsideClass == "wxGridSizer") or (outsideClass == "wxFlexGridSizer") or (outsideClass == "wxBagGridSizer") or (outsideClass == "wxBoxSizer") or (outsideClass == "wxStaticBoxSizer")):
				outsideClass = "wxSizer"

			#Determine what to do with them
			if (insideClass == "wxSizer"):
				#Sizer in sizer
				if (outsideClass == "wxSizer"):
					if (flags != None):
						outsideObject.Add(insideObject, flex, eval(flags), border = border)
					else:
						outsideObject.Add(insideObject, flex, flag = 0, border = border)

				#Sizer in panel
				elif (outsideClass == "wxPanel"):
					if (autoSize == None):
						autoSize = insideObject.autoSize
					
					if (autoSize):
						outsideObject.SetSizerAndFit(insideObject)
					else:
						outsideObject.SetSizer(insideObject)

				#Sizer in splitter
				elif (outsideClass == "wxSplitterWindow"):
					##Untested
					outsideObject.Add(insideObject, flex, wx.ALL|wx.GROW)

				else:
					print("Add", outsideClass, "to nestObject()")

			elif (insideClass == "wxPanel"):
				#Panel in sizer
				if (outsideClass == "wxSizer"):
					outsideObject.Add(insideObject, flex, wx.ALL|wx.GROW)

				#Panel in panel
				elif (outsideClass == "wxPanel"):
					##Untested
					outsideObject.Add(insideObject, flex, wx.ALL|wx.GROW)

				#Panel in splitter
				elif (outsideClass == "wxSplitterWindow"):
					##Untested
					outsideObject.Add(insideObject, flex, wx.ALL|wx.GROW)

				else:
					print("Add", outsideClass, "to nestObject()")

			elif (insideClass == "wxSplitterWindow"):
				#Panel in sizer
				if (outsideClass == "wxSizer"):
					outsideObject.Add(insideObject, flex, wx.ALL|wx.GROW)

				#Panel in panel
				elif (outsideClass == "wxPanel"):
					##Untested
					outsideObject.Add(insideObject, flex, wx.ALL|wx.GROW)

				#Panel in splitter
				elif (outsideClass == "wxSplitterWindow"):
					##Untested
					outsideObject.Add(insideObject, flex, wx.ALL|wx.GROW)

				else:
					print("Add", outsideClass, "to nestObject()")

			else:
				print("Add", insideClass, "to nestObject()")

		def addSizerGrid(self, rows, columns, sizerNumber, myLabel = None, hidden = False,
			rowGap = 0, colGap = 0, minWidth = -1, minHeight = -1, panelNumber = None):
			"""Creates a grid sizer to the specified size.

			rows (int)        - The number of rows that the gird has
			columns (int)     - The number of columns that the grid has
			sizerNumber (int) - The index number of the sizer
			myLabel (str)     - What this is called in the idCatalogue
			hidden (bool)     - If True: All items in the sizer are hidden from the user, but they are still created
			rowGap (int)      - Empty space between each row
			colGap (int)      - Empty space between each column
			minWidth (int)    - The minimum width of a box. -1 means automatic
			minHeight (int)   - The minimum height of a box. -1 means automatic
			panelNumber (int) - If provided, will tell the sizer which panel it belongs to

			Example Input: addSizerGrid(4, 3, 0)
			"""

			#Determine if a specific id should be set
			if (myLabel != None):
				myId = self.newId(myLabel)

			else:
				myId = self.newId()

			#Create Sizer
			sizer = wx.GridSizer(rows, columns, rowGap, colGap)

			if(self.debugging):
				print("Adding:", sizer)

			#Determine visibility
			if (hidden):
				self.addFinalFunction(sizer.ShowItems, False)

			#Catalogue Sizer
			self.catalogueSizer(sizerNumber, sizer, panelNumber)

			#Add object to idCatalogue
			self.addToId(sizer, myLabel)

		def addSizerGridFlex(self, rows, columns, sizerNumber, myLabel = None, rowGap = 0, colGap = 0, hidden = False, 
			minWidth = -1, minHeight = -1, flexGrid = True, vertical = None, panelNumber = None):
			"""Creates a flex grid sizer.
			############## NEEDS TO BE FIXED #################

			rows (int)        - The number of rows that the gird has
			columns (int)     - The number of columns that the grid has
			sizerNumber (int) - The number of the sizer that this will be added to
			myLabel (str)     - What this is called in the idCatalogue
			rowGap (int)      - Empyt space between each row
			colGap (int)      - Empty space between each column
			hidden (bool)     - If True: All items in the sizer are hidden from the user, but they are still created
			minWidth (int)    - The minimum width of a box. -1 means automatic
			minHeight (int)   - The minimum height of a box. -1 means automatic
			flexGrid (bool)   - True if the grid will be flexable. If False, this is like a normal grid sizer.
			vertical (bool)   - Determines what direction cells are flexibally (unequally) sized
									~ True: Rows are sized
									~ False: Columns are sized
									~ None: Both are sized
			panelNumber (int) - If provided, will tell the sizer which panel it belongs to

			Example Input: addSizerGridFlex(4, 3, 0)
			"""

			#Determine if a specific id should be set
			if (myLabel != None):
				myId = self.newId(myLabel)

			else:
				myId = self.newId()

			#Create Sizer
			sizer = wx.FlexGridSizer(rows, columns, rowGap, colGap)

			if(self.debugging):
				print("Adding:", sizer)
			
			#Determine flexable direction
			if (vertical == None):
				direction = wx.BOTH
			elif (vertical):
				direction = wx.VERTICAL
			else:
				direction = wx.HORIZONTAL
			sizer.SetFlexibleDirection(direction)

			#Determine if flexability specifications
			# if (flexGrid):
			# 	sizer.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)
			# else:
			# 	sizer.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_NONE)

			#Determine visibility
			if (hidden):
				self.addFinalFunction(sizer.ShowItems, False)

			#Catalogue Sizer
			self.catalogueSizer(sizerNumber, sizer, panelNumber)

			#Add object to idCatalogue
			self.addToId(sizer, myLabel)

		def growFlexColumn(self, sizerNumber, column, proportion = 0):
			"""Allows the column to grow as much as it can.

			sizerNumber (int) - The number of the sizer that this will be added to
			column (int)      - The column that will expand
			proportion (int)  - How this column will grow compared to other growable columns
								If all are zero, they will grow equally

			Example Input: growFlexColumn(0, 1)
			"""

			sizer = self.getSizer(sizerNumber)

			#Check growability
			if (sizer.IsColGrowable(column)):
				#The column must be growable. To change the proportion, it's growability must first be removed
				sizer.RemoveGrowableCol(column)

			#Add attribute
			sizer.AddGrowableCol(column, proportion)

		def growFlexRow(self, sizerNumber, row, proportion = 0):
			"""Allows the row to grow as much as it can.

			sizerNumber (int) - The number of the sizer that this will be added to
			row (int)      - The row that will expand
			proportion (int)  - How this row will grow compared to other growable rows
								If all are zero, they will grow equally

			Example Input: growFlexRow(0, 1)
			"""

			sizer = self.getSizer(sizerNumber)

			#Check growability
			if (sizer.IsRowGrowable(row)):
				#The row must be growable. To change the proportion, it's growability must first be removed
				sizer.RemoveGrowableRow(row)

			#Add attribute
			sizer.AddGrowableRow(row, proportion)

		def growFlexColumnAll(self, sizerNumber, proportion = 0):
			"""Allows all the columns to grow as much as they can.

			sizerNumber (int) - The number of the sizer that this will be added to
			column (int)      - The column that will expand
			proportion (int)  - How this column will grow compared to other growable columns
								If all are zero, they will grow equally

			Example Input: growFlexColumnAll(0)
			"""

			sizer = self.getSizer(sizerNumber)

			for column in range(sizer.GetCols()):
				self.growFlexColumn(sizerNumber, column)

		def growFlexRowAll(self, sizerNumber, proportion = 0):
			"""Allows all the rows to grow as much as they can.

			sizerNumber (int) - The number of the sizer that this will be added to
			row (int)      - The row that will expand
			proportion (int)  - How this row will grow compared to other growable rows
								If all are zero, they will grow equally

			Example Input: growFlexRowAll(0)
			"""

			sizer = self.getSizer(sizerNumber)

			for row in range(sizer.GetCols()):
				self.growFlexRow(sizerNumber, row)

		def addSizerGridBag(self, rows, columns, sizerNumber, myLabel = None, rowGap = 0, colGap = 0, minWidth = -1, minHeight = -1, 
			hidden = False, emptySpace = None, flexGrid = True, vertical = None, panelNumber = None):
			"""Creates a bag grid sizer.

			rows (int)         - The number of rows that the gird has
			columns (int)      - The number of columns that the grid has
			sizerNumber (int)  - The number of the sizer that this will be added to
			rowGap (int)       - Empyt space between each row
			colGap (int)       - Empty space between each column
			minWidth (int)     - The minimum width of a box. -1 means automatic
			minHeight (int)    - The minimum height of a box. -1 means automatic
			myLabel (str)      - What this is called in the idCatalogue
			hidden (bool)      - If True: All items in the sizer are hidden from the user, but they are still created
			emptySpace (tuple) - The space taken up by cells that are empty or hidden; (row width, column width)
			flexGrid (bool)    - True if the grid will be flexable. If False, this is like a normal grid sizer.
			vertical (bool)    - Determines what direction cells are flexibally (unequally) sized
									~ True: Rows are sized
									~ False: Columns are sized
									~ None: Both are sized
			panelNumber (int) - If provided, will tell the sizer which panel it belongs to

			Example Input: addSizerGridBag(4, 3)
			Example Input: addSizerGridBag(4, 3, emptySpace = (0, 0))
			"""

			#Determine if a specific id should be set
			if (myLabel != None):
				myId = self.newId(myLabel)

			else:
				myId = self.newId()

			#Create Sizer
			sizer = wx.GridBagSizer(rows, columns, rowGap, colGap)

			if(self.debugging):
				print("Adding:", sizer)
			
			if (vertical == None):
				direction = wx.BOTH
			elif (vertical):
				direction = wx.VERTICAL
			else:
				direction = wx.HORIZONTAL
			sizer.SetFlexibleDirection(direction)

			if (flexGrid):
				sizer.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)
			else:
				sizer.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_NONE)

			if (emptySpace != None):
				sizer.SetEmptyCellSize(emptySpace)

			#Determine visibility
			if (hidden):
				self.addFinalFunction(sizer.ShowItems, False)

			#Catalogue Sizer
			self.catalogueSizer(sizerNumber, sizer, panelNumber)

			#Add object to idCatalogue
			self.addToId(sizer, myLabel)

		def addSizerBox(self, sizerNumber, minWidth = -1, minHeight = -1, 
			horizontal = False, hidden = False, myLabel = None, panelNumber = None):
			"""Creates a box sizer.

			sizerNumber (int) - The number of the sizer that this will be added to
			minWidth (int)    - The minimum width of a box. -1 means automatic
			minHeight (int)   - The minimum height of a box. -1 means automatic
			horizontal (bool) - True to align items horizontally. False to align items vertically
			hidden (bool)     - If True: All items in the sizer are hidden from the user, but they are still created
			myLabel (str)     - What this is called in the idCatalogue
			panelNumber (int) - If provided, will tell the sizer which panel it belongs to

			Example Input: addSizerBox(0)
			"""

			#Determine if a specific id should be set
			if (myLabel != None):
				myId = self.newId(myLabel)

			else:
				myId = self.newId()

			#Create Sizer
			if (not horizontal):
				orientation = wx.VERTICAL
			else:
				orientation = wx.HORIZONTAL
			#sizer.SetMinSize(wx.Size(minWidth, minHeight)) 
			sizer = wx.BoxSizer(orientation)

			if(self.debugging):
				print("Adding:", sizer)

			#Determine visibility
			if (hidden):
				self.addFinalFunction(sizer.ShowItems, False)
			
			#Catalogue Sizer
			self.catalogueSizer(sizerNumber, sizer, panelNumber)

			#Add object to idCatalogue
			self.addToId(sizer, myLabel)

		def addSizerBoxStatic(self, myText, sizerNumber, minWidth = -1, minHeight = -1, 
			horizontal = False, hidden = False, myLabel = None, panelNumber = None):
			"""Creates a static box sizer.

			myText (str)      - The text that appears above the static box
			sizerNumber (int) - The number of the sizer that this will be added to
			minWidth (int)    - The minimum width of a box. -1 means automatic
			minHeight (int)   - The minimum height of a box. -1 means automatic
			horizontal (bool) - True to align items horizontally. False to align items vertically
			hidden (bool)     - If True: All items in the sizer are hidden from the user, but they are still created
			myLabel (str)     - What this is called in the idCatalogue
			panelNumber (int) - If provided, will tell the sizer which panel it belongs to

			Example Input: addSizerBoxStatic()
			"""

			#Determine if a specific id should be set
			if (myLabel != None):
				myId = self.newId(myLabel)

			else:
				myId = self.newId()
			
			#Create Sizer
			if (not horizontal):
				orientation = wx.VERTICAL
			else:
				orientation = wx.HORIZONTAL     
			sizer = wx.StaticBoxSizer(wx.StaticBox(self, myId, myText), orientation)
			#sizer.SetMinSize(wx.Size(minWidth, minHeight)) 

			if(self.debugging):
				print("Adding:", sizer)

			#Determine visibility
			if (hidden):
				self.addFinalFunction(sizer.ShowItems, False)
			
			#Catalogue Sizer
			self.catalogueSizer(sizerNumber, sizer, panelNumber)

			#Add object to idCatalogue
			self.addToId(sizer, myLabel)

	class Widgets():
		"""Contains functions used for widgets and such.
		Widgets are things that are placed inside sizers to add interactivity.
		This is here for convenience in programming.
		"""

		def __init__(self):
			"""Does nothing. This is here to comply with PEP 8 standards.

			Example Input: Meant to be inherited by GUI().
			"""

			pass

		def addEmpty(self, sizerNumber, flags = ["ex", "ba"], myLabel = None, default = False, hidden = False, flex = 0, wizardPageNumber = None):
			"""Adds an empty space to the next cell on the grid.

			sizerNumber (int)       - The number of the sizer that this will be added to
			myLabel (str)           - What this is called in the idCatalogue
			default (bool)          - If True: This is the default thing selected
			hidden (bool)           - If True: The widget is hidden from the user, but it is still created
			wizardFrameNumber (int) - The number of the wizard page. If None, it assumes either a frame or a panel

			Example Input: addEmpty(0, "empty1")
			Example Input: addEmpty(0)
			"""

			#Determine if a specific id should be set
			if (myLabel != None):
				myId = self.newId(myLabel)

			else:
				myId = self.newId()

			#Which sizer is being used?
			sizer, panelNumber = self.getSizer(sizerNumber, returnPanel = True)

			#Determine if it is a wizard or not
			if (wizardPageNumber != None):
				exec("identity = self.m_wizPage" + str(wizardPageNumber))

			#Determine if it is a panel or not
			elif (panelNumber != None):
				identity = self.getPanel(panelNumber)

			#It must be the frame then
			else:
				identity = self

			#Create the thing to put in the grid
			thing = wx.StaticText(identity, myId, u" ", wx.DefaultPosition, wx.DefaultSize, 0)
			self.wrapText(thing, -1)

			#Determine if it is a default
			if (default):
				thing.SetDefault() 

			#Determine visibility
			if (hidden):
				thing.Hide()

			#Configure Flags            
			flags, position, border = self.getItemMod(flags)

			#Add it to the grid
			self.addToSizer(sizer, thing, flex, flags, 5)

			#Add object to idCatalogue
			self.addToId(thing, myLabel)

		def addLine(self, sizerNumber, flags = ["ex", "ba"], myLabel = None, horizontal = True, flex = 0, hidden = False, wizardPageNumber = None):
			"""Adds a simple line to the window.
			It can be horizontal or vertical.

			sizerNumber (int)       - The number of the sizer this will be added to
			flags (list)            - A list of strings for which flag to add to the sizer
			myLabel (str)           - What this is called in the idCatalogue
			horizontal (bool)       - Whether the line is horizontal or vertical
			hidden (bool)           - If True: The widget is hidden from the user, but it is still created
			wizardFrameNumber (int) - The number of the wizard page. If None, it assumes either a frame or a panel

			Example Input: addLine(1)
			"""

			#Determine if a specific id should be set
			if (myLabel != None):
				myId = self.newId(myLabel)

			else:
				myId = self.newId()

			#Which sizer is being used?
			sizer, panelNumber = self.getSizer(sizerNumber, returnPanel = True)

			#Determine if it is a wizard or not
			if (wizardPageNumber != None):
				exec("identity = self.m_wizPage" + str(wizardPageNumber))

			#Determine if it is a panel or not
			elif (panelNumber != None):
				identity = self.getPanel(panelNumber)

			#It must be the frame then
			else:
				identity = self
			#Create the thing to put in the grid
			if (horizontal):
				thing = wx.StaticLine(identity, myId, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL)
			else:
				thing = wx.StaticLine(identity, myId, wx.DefaultPosition, wx.DefaultSize, wx.LI_VERTICAL)

			#Determine visibility
			if (hidden):
				thing.Hide()

			#Configure Flags            
			flags, position, border = self.getItemMod(flags)

			#Add it to the grid
			self.addToSizer(sizer, thing, flex, flags, 5)

			#Add object to idCatalogue
			self.addToId(thing, myLabel)

		def addText(self, myText, sizerNumber, flags = "c1", myLabel = None, default = False, hidden = False, wrap = None, flex = 0, 
			size = None, bold = False, italic = False, family = None, wizardPageNumber = None):
			"""Adds text to the grid.
			If you want to update this text, you will need to run the function setObjectValue() or setObjectValueWithLabel().
			If you provide a variable to this function and that variable changes- the text on the GUI will not update.
			It must be told to do so explicitly by using one of the functions mentioned above.
			Note: If you change the text, any word wrap will be removed. To wrap it again, call the function textWrap().

			myText (str)      - The text that will be added to the next cell on the grid.
			sizerNumber (int) - The number of the sizer that this will be added to
			flags (list)      - A list of strings for which flag to add to the sizer. Can be just a string if only 1 flag is given
			myLabel (str)     - What this is called in the idCatalogue
			default (bool)    - If True: This is the default thing selected
			hidden (bool)     - If True: The widget is hidden from the user, but it is still created
			wrap (int)        - How many pixels wide the line will be before it wraps. If negative: no wrapping is done
			flex (int)        - Only for Box Sizers:
				~ If 0: The cell will not grow or shrink; acts like a Flex Grid cell
				~ If not 0: The cell will grow and shrink to match the cells that have the same number
			
			size (int)    - The font size of the text  
			bold (bool)   - If True: the font will be bold
			italic (bool) - If True: the font will be italicized
			color (str)   - The color of the text. Can be an RGB tuple (r, g, b) or hex value
			family (str)  - What font family it is.
				~ "times new roman"         

			wizardFrameNumber (int) - The number of the wizard page. If None, it assumes either a frame or a panel

			Example Input: addText("Lorem Ipsum", 0)
			Example Input: addText("Change Me", 0, "changableText")
			Example Input: addText("Part Type", 1, flags = "c2")
			Example Input: addText("Part Type", 1, flags = ["at", "c2"])
			Example Input: addText("This line will wrap", 0, wrap = 10)
			Example Input: addText("BIG TEXT", 0, bold = True, size = 72, color = "red")
			"""

			#Determine if a specific id should be set
			if (myLabel != None):
				myId = self.newId(myLabel)
				
			else:
				myId = self.newId()

			#Which sizer is being used?
			sizer, panelNumber = self.getSizer(sizerNumber, returnPanel = True)

			#Determine if it is a wizard or not
			if (wizardPageNumber != None):
				exec("identity = self.m_wizPage" + str(wizardPageNumber))

			#Determine if it is a panel or not
			elif (panelNumber != None):
				identity = self.getPanel(panelNumber)

			#It must be the frame then
			else:
				identity = self

			#Create the thing to put in the grid
			thing = wx.StaticText(identity, myId, myText, wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_CENTRE)

			#Determine if it is a default
			if (default):
				thing.SetDefault()

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
			thing.SetFont(font)

			#Determine Attributes
			flags, position, border = self.getItemMod(flags)

			if (wrap != None):
				if (wrap > 0):
					self.wrapText(thing, wrap)

			#Determine visibility
			if (hidden):
				thing.Hide()

			#Add it to the grid
			self.addToSizer(sizer, thing, flex, flags, 5)

			#Add object to idCatalogue
			self.addToId(thing, myLabel)

		def wrapText(self, textLabel, wrap):
			"""Wraps the text to a specific point.

			textLabel (str) - What this is called in the idCatalogue
			wrap (int)      - How many pixels wide the line will be before it wraps. If negative: no wrapping is done

			Example Text: wrapText("changableText", 250)
			"""

			if (wrap != None):
				#Account for both user and GUI module
				if (type(textLabel) == str):
					thing = self.getObjectWithLabel(textLabel)
				else:
					thing = textLabel

				#Get the object's class
				thingClass = thing.GetClassName()

				#Take the appropriate action
				if (thingClass == "wxStaticText"):
					thing.Wrap(wrap)

				elif (thingClass == "wxTextCtrl"):
					print("ERROR: Wrapping can only be defined upon the creation of the input box")

				else:
					print("Add", thingClass, "to wrapText()")


		def addListDrop(self, choices, myFunction, sizerNumber, flags = "c1", myLabel = None, myFunctionArgs = None, myFunctionKwargs = None, 
			default = None, enabled = True, hidden = False, flex = 0, wizardPageNumber = None):
			"""Adds a dropdown list with choices to the next cell on the grid.

			choices (list)          - A list of the choices as strings
			myFunction (str)        - The function that is ran when the user chooses somthing from the list. If a list is given, each function will be bound.
			sizerNumber (int)       - The number of the sizer that this will be added to
			flags (list)            - A list of strings for which flag to add to the sizer
			myLabel (str)           - What this is called in the idCatalogue
			myFunctionArgs (any)    - The arguments for 'myFunction'
			myFunctionKwargs (any)  - The keyword arguments for 'myFunction'function
			default (int)           - Which item in the droplist is selected
				- If a string is given, it will select the first item in the list that matches that string. If noting matches, it will default to the first element
			enabled (bool)          - If True: The user can interact with this
			wizardFrameNumber (int) - The number of the wizard page. If None, it assumes either a frame or a panel

			Example Input: addListDrop(["choice1", "choice2", "choice3"], "chosen", 0)
			"""

			#Determine if a specific id should be set
			if (myLabel != None):
				myId = self.newId(myLabel)
			else:
				myId = self.newId()

			#Which sizer is being used?
			sizer, panelNumber = self.getSizer(sizerNumber, returnPanel = True)

			#Determine if it is a wizard or not
			if (wizardPageNumber != None):
				exec("identity = self.m_wizPage" + str(wizardPageNumber))

			#Determine if it is a panel or not
			elif (panelNumber != None):
				identity = self.getPanel(panelNumber)

			#It must be the frame then
			else:
				identity = self

			#Ensure that the choices are all strings
			for i, item in enumerate(choices):
				if (type(item) != str):
					choices[i] = str(item)

			#Create the thing to put in the grid
			thing = wx.Choice(identity, myId, wx.DefaultPosition, wx.DefaultSize, choices, style = 0)
			
			#Set default position
			if (type(default) == str):
				if (default in choices):
					default = choices.index(default)

			if (default == None):
				default = 0

			thing.SetSelection(default)

			#Determine if it is enabled
			if (not enabled):
				thing.Disable()

			#Determine visibility
			if (hidden):
				thing.Hide()

			#Configure Flags            
			flags, position, border = self.getItemMod(flags)

			#Add it to the grid
			self.addToSizer(sizer, thing, flex, flags, 5)

			#Bind the function(s)
			self.betterBind(wx.EVT_CHOICE, thing, myFunction, myFunctionArgs, myFunctionKwargs)

			#Add object to idCatalogue
			self.addToId(thing, myLabel)

		def addListFull(self, choices, myFunction, sizerNumber, flags = "c1", myLabel = None, myFunctionArgs = None, myFunctionKwargs = None, 
			default = False, enabled = True, flex = 0, wizardPageNumber = None):
			"""Adds a full list with choices to the next cell on the grid.

			choices (list)          - A list of the choices as strings
			myFunction (str)        - The function that is ran when the user chooses somthing from the list
			sizerNumber (int)       - The number of the sizer that this will be added to
			flags (list)            - A list of strings for which flag to add to the sizer
			myLabel (str)           - What this is called in the idCatalogue
			myFunctionArgs (any)    - The arguments for 'myFunction'
			myFunctionKwargs (any)  - The keyword arguments for 'myFunction'function
			default (bool)          - If True: This is the default thing selected
			enabled (bool)          - If True: The user can interact with this
			wizardFrameNumber (int) - The number of the wizard page. If None, it assumes either a frame or a panel

			Example Input: addListFull(["choice1", "choice2", "choice3"], "chosen", 0)
			"""

			#Determine if a specific id should be set
			if (myLabel != None):
				myId = self.newId(myLabel)
				
			else:
				myId = self.newId()
				
			#Which sizer is being used?
			sizer, panelNumber = self.getSizer(sizerNumber, returnPanel = True)

			#Determine if it is a wizard or not
			if (wizardPageNumber != None):
				exec("identity = self.m_wizPage" + str(wizardPageNumber))

			#Determine if it is a panel or not
			elif (panelNumber != None):
				identity = self.getPanel(panelNumber)

			#It must be the frame then
			else:
				identity = self

			#Create the thing to put in the grid
			thing = wx.ListBox(identity, myId, wx.DefaultPosition, wx.DefaultSize, choices, 0)

			#Determine if it is a default
			if (default):
				thing.SetDefault() 

			#Determine if it is enabled
			if (not enabled):
				thing.Disable()

			#Configure Flags            
			flags, position, border = self.getItemMod(flags)

			#Add it to the grid
			self.addToSizer(sizer, thing, flex, flags, 5)

			#Bind the function(s)
			self.betterBind(wx.EVT_LISTBOX, thing, myFunction, myFunctionArgs, myFunctionKwargs)

			#Add object to idCatalogue
			self.addToId(thing, myLabel)

		def addSlider(self, myMin, myMax, myInitial, myFunction, sizerNumber, flags = "c1", myLabel = None, flex = 0, 
			myFunctionArgs = None, myFunctionKwargs = None, wizardPageNumber = None):
			"""Adds a slider bar to the next cell on the grid.

			myMin (int)             - The minimum value of the slider bar
			myMax (int)             - The maximum value of the slider bar
			myInitial (int)         - The initial value of the slider bar's position
			myFunction (str)        - The function that is ran when the user enters text and presses enter
			sizerNumber (int)       - The number of the sizer that this will be added to
			flags (list)            - A list of strings for which flag to add to the sizer
			myLabel (str)           - What this is called in the idCatalogue
			myFunctionArgs (any)    - The arguments for 'myFunction'
			myFunctionKwargs (any)  - The keyword arguments for 'myFunction'function
			wizardFrameNumber (int) - The number of the wizard page. If None, it assumes either a frame or a panel

			Example Input: addSlider(0, 100, 50, "initialTemperature")
			"""

			#Determine if a specific id should be set
			if (myLabel != None):
				myId = self.newId(myLabel)
				
			else:
				myId = self.newId()
				
			#Which sizer is being used?
			sizer, panelNumber = self.getSizer(sizerNumber, returnPanel = True)

			#Determine if it is a wizard or not
			if (wizardPageNumber != None):
				exec("identity = self.m_wizPage" + str(wizardPageNumber))

			#Determine if it is a panel or not
			elif (panelNumber != None):
				identity = self.getPanel(panelNumber)

			#It must be the frame then
			else:
				identity = self

			#Create the thing to put in the grid
			thing = wx.Slider(identity, myId, myInitial, myMin, myMax, wx.DefaultPosition, wx.DefaultSize, wx.SL_HORIZONTAL)

			#Configure Flags            
			flags, position, border = self.getItemMod(flags)

			#Add it to the grid
			self.addToSizer(sizer, thing, flex, flags, 5)

			#Bind the function(s)
			self.betterBind(wx.EVT_SCROLL_CHANGED, thing, myFunction, myFunctionArgs, myFunctionKwargs)

			#Add object to idCatalogue
			self.addToId(thing, myLabel)
		
		def addInputBox(self, myFunction, sizerNumber, flags = "c1", myLabel = None, myFunctionArgs = None, myFunctionKwargs = None, text = None, maxLength = None,
			default = False, enabled = True, hidden = False, password = False, alpha = False, readOnly = False, tab = True, wrap = None, ipAddress = False,
			enterFunction = None, enterFunctionArgs = None, enterFunctionKwargs = None, flex = 0, wizardPageNumber = None):
			"""Adds an input box to the next cell on the grid.

			myFunction (str)       - The function that is ran when the user enters text
			sizerNumber (int)      - The number of the sizer that this will be added to
			flags (list)           - A list of strings for which flag to add to the sizer
			myLabel (str)          - What this is called in the idCatalogue
			myFunctionArgs (any)   - The arguments for 'myFunction'
			myFunctionKwargs (any) - The keyword arguments for 'myFunction'
			text (str)             - What is initially in the box
			maxLength (int)        - If not None: The maximum length of text that can be added
			
			default (bool)   - If True: This is the default thing selected
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

			wizardFrameNumber (int) - The number of the wizard page. If None, it assumes either a frame or a panel

			Example Input: addInputBox("initialTemperature", 0)
			Example Input: addInputBox("connect", 0, text = "127.0.0.0", ipAddress = True)
			"""
		
			#Determine if a specific id should be set
			if (myLabel != None):
				myId = self.newId(myLabel)

			else:
				myId = self.newId()
				
			#Which sizer is being used?
			sizer, panelNumber = self.getSizer(sizerNumber, returnPanel = True)

			#Determine if it is a wizard or not
			if (wizardPageNumber != None):
				exec("identity = self.m_wizPage" + str(wizardPageNumber))

			#Determine if it is a panel or not
			elif (panelNumber != None):
				identity = self.getPanel(panelNumber)

			#It must be the frame then
			else:
				identity = self

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
				thing = wx.lib.masked.ipaddrctrl.IpAddrCtrl(identity, myId, style = eval(styles))

				if (text != wx.EmptyString):
					thing.SetValue(text)
			else:
				thing = wx.TextCtrl(identity, myId, text, style = eval(styles))

				#Set maximum length
				if (maxLength != None):
					thing.SetMaxLength(maxLength)

			#Determine if it is a default
			if (default):
				thing.SetDefault() 

			#Determine if it is enabled
			if (not enabled):
				thing.Disable()

			#Configure Flags            
			flags, position, border = self.getItemMod(flags)

			#Determine visibility
			if (hidden):
				thing.Hide()

			#flags += "|wx.RESERVE_SPACE_EVEN_IF_HIDDEN"

			#Add it to the grid
			self.addToSizer(sizer, thing, flex, flags, 5)

			#Bind the function(s)
			#self.betterBind(wx.EVT_CHAR, thing, enterFunction, enterFunctionArgs, enterFunctionKwargs)
			#self.betterBind(wx.EVT_KEY_UP, thing, self.testFunction, myFunctionArgs, myFunctionKwargs)
			if (enterFunction != None):
				self.keyBind("enter", thing, enterFunction, enterFunctionArgs, enterFunctionKwargs)
			self.betterBind(wx.EVT_TEXT, thing, myFunction, myFunctionArgs, myFunctionKwargs)

			#Add object to idCatalogue
			self.addToId(thing, myLabel)

		def addInputSearch(self, myFunction, sizerNumber, flags = "c1", myLabel = None, myFunctionArgs = None, myFunctionKwargs = None, text = None, 
			searchFunction = None, searchFunctionArgs = None, searchFunctionKwargs = None, 
			cancelFunction = None, cancelFunctionArgs = None, cancelFunctionKwargs = None, 
			default = False, enabled = True, flex = 0, wizardPageNumber = None):
			"""Adds an input box to the next cell on the grid.

			myFunction (str)            - The function that is ran when the user enters text and presses enter
			sizerNumber (int)           - The number of the sizer that this will be added to
			flags (list)                - A list of strings for which flag to add to the sizer
			myLabel (str)               - What this is called in the idCatalogue
			myFunctionArgs (any)        - The arguments for 'myFunction'
			myFunctionKwargs (any)      - The keyword arguments for 'myFunction'function
			text (str)          - What is initially in the box
			
			searchFunction (str)        - If provided, this is what will be ran when the search button to the left is pressed
			searchFunctionArgs (any)    - The arguments for 'searchFunction'
			searchFunctionKwargs (any)  - The keyword arguments for 'searchFunction'function
			cancelFunction (str)        - If provided, this is what will be ran when the cancel button to the right is pressed
			cancelFunctionArgs (any)    - The arguments for 'cancelFunction'
			cancelFunctionKwargs (any)  - The keyword arguments for 'cancelFunction'function
			
			default (bool)              - If True: This is the default thing selected
			enabled (bool)              - If True: The user can interact with this
			wizardFrameNumber (int)     - The number of the wizard page. If None, it assumes either a frame or a panel

			Example Input: addInputSearch("initialTemperature")
			"""

			#Determine if a specific id should be set
			if (myLabel != None):
				myId = self.newId(myLabel)
				
			else:
				myId = self.newId()
				
			#Which sizer is being used?
			sizer, panelNumber = self.getSizer(sizerNumber, returnPanel = True)

			#Determine if it is a wizard or not
			if (wizardPageNumber != None):
				exec("identity = self.m_wizPage" + str(wizardPageNumber))

			#Determine if it is a panel or not
			elif (panelNumber != None):
				identity = self.getPanel(panelNumber)

			#It must be the frame then
			else:
				identity = self

			#Create the thing to put in the grid
			thing = wx.SearchCtrl(identity, myId, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0)

			#Determine if additional features are enabled
			if (searchFunction != None):
				thing.ShowSearchButton(True)
			if (cancelFunction != None):
				thing.ShowCancelButton(True)

			#Determine if it is a default
			if (default):
				thing.SetDefault() 

			#Determine if it is enabled
			if (not enabled):
				thing.Disable()

			#Configure Flags            
			flags, position, border = self.getItemMod(flags)

			#Add it to the grid
			self.addToSizer(sizer, thing, flex, flags, 5)

			#Bind the function(s)
			if (searchFunction != None):
				self.betterBind(wx.EVT_SEARCHCTRL_SEARCH_BTN, thing, searchFunction, searchFunctionArgs, searchFunctionKwargs)
			if (cancelFunction != None):
				self.betterBind(wx.EVT_SEARCHCTRL_CANCEL_BTN, thing, cancelFunction, cancelFunctionArgs, cancelFunctionKwargs)
			self.betterBind(wx.EVT_TEXT_ENTER, thing, myFunction, myFunctionArgs, myFunctionKwargs)

			#Add object to idCatalogue
			self.addToId(thing, myLabel)

		def addInputSpinner(self, myMin, myMax, myInitial, myFunction, sizerNumber, flags = "c1", myLabel = None, flex = 0, 
			size = wx.DefaultSize, maxSize = None, minSize = None, hidden = False, 
			myFunctionArgs = None, myFunctionKwargs = None, increment = None, digits = None, useFloat = False, readOnly = False,
			changeTextFunction = None, changeTextFunctionArgs = None, changeTextFunctionKwargs = None, wizardPageNumber = None):
			"""Adds a spin control to the next cell on the grid. This is an input box for numbers.

			myMin (int)       - The minimum value of the input spinner
			myMax (int)       - The maximum value of the input spinner
			myInitial (int)   - The initial value of the input spinner's position
			myFunction (str)  - The function that is ran when the user enters text and presses enter
			sizerNumber (int) - The number of the sizer that this will be added to
			flags (list)      - A list of strings for which flag to add to the sizer
			myLabel (str)     - What this is called in the idCatalogue

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
			
			wizardFrameNumber (int)        - The number of the wizard page. If None, it assumes either a frame or a panel

			Example Input: addInputSpinner(0, 100, 50, "initialTemperature")
			Example Input: addInputSpinner(0, 100, 50, "initialTemperature", maxSize = (100, 100))
			"""

			#Determine if a specific id should be set
			if (myLabel != None):
				myId = self.newId(myLabel)

			else:
				myId = self.newId()
				
			#Which sizer is being used?
			sizer, panelNumber = self.getSizer(sizerNumber, returnPanel = True)

			#Determine if it is a wizard or not
			if (wizardPageNumber != None):
				exec("identity = self.m_wizPage" + str(wizardPageNumber))

			#Determine if it is a panel or not
			elif (panelNumber != None):
				identity = self.getPanel(panelNumber)

			#It must be the frame then
			else:
				identity = self

			#Create the thing to put in the grid
			if (useFloat):
				style = "wx.lib.agw.floatspin.FS_LEFT"
				if (readOnly):
					style += "|wx.lib.agw.floatspin.FS_READONLY"

				if (increment == None):
					increment = 0.1

				if (digits == None):
					digits = 1

				thing = wx.lib.agw.floatspin.FloatSpin(identity, myId, wx.DefaultPosition, size, wx.SP_ARROW_KEYS|wx.SP_WRAP, myInitial, myMin, myMax, increment, digits, eval(style))
			else:
				if (increment != None):
					thing = wx.lib.agw.floatspin.FloatSpin(identity, myId, wx.DefaultPosition, size, wx.SP_ARROW_KEYS|wx.SP_WRAP, myInitial, myMin, myMax, increment, -1, eval(style))
					SetDigits(0)
				else:
					thing = wx.SpinCtrl(identity, myId, wx.EmptyString, wx.DefaultPosition, size, wx.SP_ARROW_KEYS|wx.SP_WRAP, myMin, myMax, myInitial)

				if (readOnly):
					thing.SetReadOnly()

			#Determine size constraints
			if (maxSize != None):
				thing.SetMaxSize(maxSize)

			if (minSize != None):
				thing.SetMinSize(minSize)

			# print(myLabel, thing.GetBestSize())
			# thing.SetMinSize(thing.GetBestSize())
			# thing.SetMaxSize(thing.GetBestSize())

			#Determine visibility
			if (hidden):
				thing.Hide()

			#Configure Flags            
			flags, position, border = self.getItemMod(flags)

			#Add it to the grid
			self.addToSizer(sizer, thing, flex, flags, 5)

			#Bind the function(s)
			self.betterBind(wx.EVT_SPINCTRL, thing, myFunction, myFunctionArgs, myFunctionKwargs)
			if (changeTextFunction != None):
				if (type(changeTextFunction) == bool):
					if (changeTextFunction == True):
						self.betterBind(wx.EVT_TEXT, thing, myFunction, myFunctionArgs, myFunctionKwargs)
				else:
					self.betterBind(wx.EVT_TEXT, thing, changeTextFunction, changeTextFunctionArgs, changeTextFunctionKwargs)

			#Add object to idCatalogue
			self.addToId(thing, myLabel)

		def addButton(self, myText, myFunction, sizerNumber, flags = "c1", myLabel = None, valueLabel = None,
			myFunctionArgs = None, myFunctionKwargs = None,
			default = False, enabled = True, hidden = False, flex = 0, wizardPageNumber = None):
			"""Adds a button to the next cell on the grid.

			myText (str)            - What will be written on the button
			sizerNumber (int)       - The number of the sizer that this will be added to
			flags (list)            - A list of strings for which flag to add to the sizer
			myFunction (str)        - What function will be ran when the button is pressed
			myLabel (str)           - What this is called in the idCatalogue
			valueLabel (str)        - If not None: Which label to get a value from. Ie: TextCtrl, FilePickerCtrl, etc.
			myFunctionArgs (any)    - The arguments for 'myFunction'
			myFunctionKwargs (any)  - The keyword arguments for 'myFunction'function
			default (bool)          - If True: This is the default thing selected
			enabled (bool)          - If True: The user can interact with this
			hidden (bool)           - If True: The widget is hidden from the user, but it is still created
			wizardFrameNumber (int) - The number of the wizard page. If None, it assumes either a frame or a panel

			Example Input: addButton("Go!", "computeFinArray", 0)
			"""

			#Determine if a specific id should be set
			if (myLabel != None):
				myId = self.newId(myLabel)
				
			else:
				myId = self.newId() 
				
			#Which sizer is being used?
			sizer, panelNumber = self.getSizer(sizerNumber, returnPanel = True)

			#Determine if it is a wizard or not
			if (wizardPageNumber != None):
				exec("identity = self.m_wizPage" + str(wizardPageNumber))

			#Determine if it is a panel or not
			elif (panelNumber != None):
				identity = self.getPanel(panelNumber)

			#It must be the frame then
			else:
				identity = self
		
			#Create the thing to put in the grid
			thing = wx.Button(identity, myId, myText, wx.DefaultPosition, wx.DefaultSize, 0)

			#Determine if it is a default
			if (default):
				thing.SetDefault() 

			#Determine if it is enabled
			if (not enabled):
				thing.Disable()

			#Determine visibility
			if (hidden):
				thing.Hide()

			#Configure Flags            
			flags, position, border = self.getItemMod(flags)

			#Add it to the grid
			self.addToSizer(sizer, thing, flex, flags, 5)

			#Bind the function(s)
			self.betterBind(wx.EVT_BUTTON, thing, myFunction, myFunctionArgs, myFunctionKwargs)

			#Add object to idCatalogue
			self.addToId(thing, myLabel)

		def addButtonToggle(self, myText, myFunction, sizerNumber, flags = "c1", myLabel = None, 
			myFunctionArgs = None, myFunctionKwargs = None, 
			default = False, enabled = True, flex = 0, wizardPageNumber = None):
			"""Adds a toggle button to the next cell on the grid.

			myText (str)            - What will be written on the button
			myFunction (str)        - What function will be ran when the button is pressed
			sizerNumber (int)       - The number of the sizer that this will be added to
			flags (list)            - A list of strings for which flag to add to the sizer
			myLabel (str)           - What this is called in the idCatalogue
			myFunctionArgs (any)    - The arguments for 'myFunction'
			myFunctionKwargs (any)  - The keyword arguments for 'myFunction'function
			default (bool)          - If True: This is the default thing selected
			enabled (bool)          - If True: The user can interact with this
			wizardFrameNumber (int) - The number of the wizard page. If None, it assumes either a frame or a panel

			Example Input: addButtonToggle("Go!", "computeFinArray")
			"""

			#Determine if a specific id should be set
			if (myLabel != None):
				myId = self.newId(myLabel)
				
			else:
				myId = self.newId()
				
			#Which sizer is being used?
			sizer, panelNumber = self.getSizer(sizerNumber, returnPanel = True)

			#Determine if it is a wizard or not
			if (wizardPageNumber != None):
				exec("identity = self.m_wizPage" + str(wizardPageNumber))

			#Determine if it is a panel or not
			elif (panelNumber != None):
				identity = self.getPanel(panelNumber)

			#It must be the frame then
			else:
				identity = self
		
			#Create the thing to put in the grid
			thing = wx.ToggleButton(identity, myId, myText, wx.DefaultPosition, wx.DefaultSize, 0)
			thing.SetValue(True) 

			#Determine if it is a default
			if (default):
				thing.SetDefault() 

			#Determine if it is enabled
			if (not enabled):
				thing.Disable()

			#Configure Flags            
			flags, position, border = self.getItemMod(flags)

			#Add it to the grid
			self.addToSizer(sizer, thing, flex, flags, 5)

			#Bind the function(s)
			self.betterBind(wx.EVT_TOGGLEBUTTON, thing, myFunction, myFunctionArgs, myFunctionKwargs)

			#Add object to idCatalogue
			self.addToId(thing, myLabel)

		def addButtonCheck(self, myText, myFunction, sizerNumber, flags = "c1", myLabel = None, 
			myFunctionArgs = None, myFunctionKwargs = None, default = False, enabled = True, 
			hidden = False, flex = 0, wizardPageNumber = None):
			"""Adds a check box to the next cell on the grid.
			Event fires every time the check box is clicked

			myText (str)            - What will be written to the right of the button
			myFunction (str)        - What function will be ran when the button is pressed
			sizerNumber (int)       - The number of the sizer that this will be added to
			flags (list)            - A list of strings for which flag to add to the sizer
			myLabel (str)           - What this is called in the idCatalogue
			myFunctionArgs (any)    - The arguments for 'myFunction'
			myFunctionKwargs (any)  - The keyword arguments for 'myFunction'function
			default (bool)          - If True: This is the default thing selected
			enabled (bool)          - If True: The user can interact with this
			hidden (bool)           - If True: The widget is hidden from the user, but it is still created
			wizardFrameNumber (int) - The number of the wizard page. If None, it assumes either a frame or a panel

			Example Input: addButtonCheck("compute?", "computeFinArray", 0)
			"""

			#Determine if a specific id should be set
			if (myLabel != None):
				myId = self.newId(myLabel)

			else:
				myId = self.newId()
				
			#Which sizer is being used?
			sizer, panelNumber = self.getSizer(sizerNumber, returnPanel = True)

			#Determine if it is a wizard or not
			if (wizardPageNumber != None):
				exec("identity = self.m_wizPage" + str(wizardPageNumber))

			#Determine if it is a panel or not
			elif (panelNumber != None):
				identity = self.getPanel(panelNumber)

			#It must be the frame then
			else:
				identity = self
		
			#Create the thing to put in the grid
			thing = wx.CheckBox(identity, myId, myText, wx.DefaultPosition, wx.DefaultSize, 0)

			#Determine if it is default by default
			thing.SetValue(default)

			#Determine if it is enabled
			if (not enabled):
				thing.Disable()

			#Determine visibility
			if (hidden):
				thing.Hide()

			#Configure Flags            
			flags, position, border = self.getItemMod(flags)

			#Add it to the grid
			self.addToSizer(sizer, thing, flex, flags, 5)

			#Bind the function(s)
			self.betterBind(wx.EVT_CHECKBOX, thing, myFunction, myFunctionArgs, myFunctionKwargs)

			#Add object to idCatalogue
			self.addToId(thing, myLabel)

		def addButtonRadio(self, myText, myFunction, sizerNumber, flags = "c1", myLabel = None, 
			myFunctionArgs = None, myFunctionKwargs = None, 
			default = False, enabled = True, flex = 0, groupStart = False, wizardPageNumber = None):
			"""Adds a radio button to the next cell on the grid. If default, it will disable the other
			radio buttons of the same group.

			myText (str)            - What will be written to the right of the button
			myFunction (str)        - What function will be ran when the button is pressed
			sizerNumber (int)       - The number of the sizer that this will be added to
			flags (list)            - A list of strings for which flag to add to the sizer
			myLabel (int)           - What this is called in the idCatalogue
			myFunctionArgs (any)    - The arguments for 'myFunction'
			myFunctionKwargs (any)  - The keyword arguments for 'myFunction'function
			default (bool)          - If True: This is the default thing selected
			enabled (bool)          - If True: The user can interact with this
			groupStart (bool)       - True if this is the start of a new radio button group.
			wizardFrameNumber (int) - The number of the wizard page. If None, it assumes either a frame or a panel

			Example Input: addButtonRadio("compute?", "computeFinArray", 0, groupStart = True)
			"""

			#Determine if a specific id should be set
			if (myLabel != None):
				myId = self.newId(myLabel)

			else:
				myId = self.newId()
				
			#Which sizer is being used?
			sizer, panelNumber = self.getSizer(sizerNumber, returnPanel = True)

			#Determine if it is a wizard or not
			if (wizardPageNumber != None):
				exec("identity = self.m_wizPage" + str(wizardPageNumber))

			#Determine if it is a panel or not
			elif (panelNumber != None):
				identity = self.getPanel(panelNumber)

			#It must be the frame then
			else:
				identity = self

			#determine if this is the start of a new radio button group
			if (groupStart):
				group = wx.RB_GROUP
			else:
				group = 0
		
			#Create the thing to put in the grid
			thing = wx.RadioButton(identity, myId, myText, wx.DefaultPosition, wx.DefaultSize, group)

			#Determine if it is default by default
			thing.SetValue(default)

			#Determine if it is enabled
			if (not enabled):
				thing.Disable()

			#Configure Flags            
			flags, position, border = self.getItemMod(flags)

			#Add it to the grid
			self.addToSizer(sizer, thing, flex, flags, 5)

			#Bind the function(s)
			self.betterBind(wx.EVT_RADIOBUTTON, thing, myFunction, myFunctionArgs, myFunctionKwargs)

			#Add object to idCatalogue
			self.addToId(thing, myLabel)

		def addButtonRadioBox(self, myText, myFunction, sizerNumber, title = "", flags = "c1", myLabel = None, 
			myFunctionArgs = None, myFunctionKwargs = None, 
			horizontal = False, default = 1, enabled = True, flex = 0, wizardPageNumber = None):
			"""Adds a box filled with grouped radio buttons to the next cell on the grid.
			Because these buttons are grouped, only one can be selected

			myText (list)           - What will be written to the right of the button. ["Button 1", "Button 2", "Button 3"]
			myFunction (int)        - What function will be ran when the button is pressed
			sizerNumber (int)       - The number of the sizer that this will be added to
			title (str)             - What will be written above the box
			flags (list)            - A list of strings for which flag to add to the sizer
			myLabel (int)           - What this is called in the idCatalogue
			myFunctionArgs (any)    - The arguments for 'myFunction'
			myFunctionKwargs (any)  - The keyword arguments for 'myFunction'function
			horizontal (bool)       - If True: The box will be oriented horizontally
									  If False: The box will be oriented vertically
			default (int)           - Which of the radio buttons will be selected by default
			enabled (bool)          - If True: The user can interact with this
			wizardFrameNumber (int) - The number of the wizard page. If None, it assumes either a frame or a panel

			Example Input: addButtonRadioBox(["Button 1", "Button 2", "Button 3"], "self.onQueueValue", 0)
			"""

			#Determine if a specific id should be set
			if (myLabel != None):
				myId = self.newId(myLabel)

			else:
				myId = self.newId()
				
			#Which sizer is being used?
			sizer, panelNumber = self.getSizer(sizerNumber, returnPanel = True)

			#Determine if it is a wizard or not
			if (wizardPageNumber != None):
				exec("identity = self.m_wizPage" + str(wizardPageNumber))

			#Determine if it is a panel or not
			elif (panelNumber != None):
				identity = self.getPanel(panelNumber)

			#It must be the frame then
			else:
				identity = self

			#Ensure that the choices given are a list or tuple
			if ((type(myText) != list) and (type(myText) != tuple)):
				myText = list(myText)

			#Determine orientation
			if (horizontal):
				orientation = wx.RA_SPECIFY_COL
			else:
				orientation = wx.RA_SPECIFY_ROWS

			#Create the thing to put in the grid
			thing = wx.RadioBox(identity, myId, title, wx.DefaultPosition, wx.DefaultSize, myText, 1, orientation)
	
			#Determine if it is default by default
			thing.SetSelection(default)

			#Determine if it is enabled
			if (not enabled):
				thing.Disable()

			#Configure Flags            
			flags, position, border = self.getItemMod(flags)

			#Add it to the grid
			self.addToSizer(sizer, thing, flex, flags, 5)

			#Bind the function(s)
			self.betterBind(wx.EVT_RADIOBOX, thing, myFunction, myFunctionArgs, myFunctionKwargs)

			#Add object to idCatalogue
			self.addToId(thing, myLabel)

		def addButtonImage(self, idlePath, disabledPath, selectedPath, focusPath, hoverPath, myFunction, sizerNumber, flags = "c1", myLabel = None, 
			myFunctionArgs = None, myFunctionKwargs = None, default = False, enabled = True, flex = 0, wizardPageNumber = None):
			"""Adds a button to the next cell on the grid. You design what the button looks like yourself.

			idlePath (str)          - Where the image of the button idling is on the computer
			disabledPath (str)      - Where the image of the button disabled is on the computer
			selectedPath (str)      - Where the image of the button selected is on the computer
			focusPath (str)         - Where the image of the button focused is on the computer
			hoverPath (str)         - Where the image of the button hovered is on the computer
			myFunction (str)        - What function will be ran when the button is pressed
			sizerNumber (int)       - The number of the sizer that this will be added to
			flags (list)            - A list of strings for which flag to add to the sizer
			myLabel (str)           - What this is called in the idCatalogue
			myFunctionArgs (any)    - The arguments for 'myFunction'
			myFunctionKwargs (any)  - The keyword arguments for 'myFunction'function
			default (bool)          - If True: This is the default thing selected
			enabled (bool)          - If True: The user can interact with this
			wizardFrameNumber (int) - The number of the wizard page. If None, it assumes either a frame or a panel

			Example Input: addButtonImage("1.bmp", "2.bmp", "3.bmp", "4.bmp", "5.bmp", "computeFinArray")
			"""

			#Determine if a specific id should be set
			if (myLabel != None):
				myId = self.newId(myLabel)
				
			else:
				myId = self.newId()
				
			#Which sizer is being used?
			sizer, panelNumber = self.getSizer(sizerNumber, returnPanel = True)

			#Determine if it is a wizard or not
			if (wizardPageNumber != None):
				exec("identity = self.m_wizPage" + str(wizardPageNumber))

			#Determine if it is a panel or not
			elif (panelNumber != None):
				identity = self.getPanel(panelNumber)

			#It must be the frame then
			else:
				identity = self
		
			#Create the thing to put in the grid
			thing = wx.BitmapButton(identity, myId, wx.Bitmap(idlePath, wx.BITMAP_TYPE_ANY), wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW)
		
			thing.SetBitmapDisabled(wx.Bitmap(disabledPath, wx.BITMAP_TYPE_ANY))
			thing.SetBitmapSelected(wx.Bitmap(selectedPath, wx.BITMAP_TYPE_ANY))
			thing.SetBitmapFocus(wx.Bitmap(focusPath, wx.BITMAP_TYPE_ANY))
			thing.SetBitmapHover(wx.Bitmap(hoverPath, wx.BITMAP_TYPE_ANY))

			#Determine if it is a default
			if (default):
				thing.SetDefault() 

			#Determine if it is enabled
			if (not enabled):
				thing.Disable()

			#Configure Flags            
			flags, position, border = self.getItemMod(flags)

			#Add it to the grid
			self.addToSizer(sizer, thing, flex, flags, 5)

			#Bind the function(s)
			self.betterBind(wx.EVT_BUTTON, thing, myFunction, myFunctionArgs, myFunctionKwargs)

			#Add object to idCatalogue
			self.addToId(thing, myLabel)

		def addImage(self, imagePath, sizerNumber, flags = "c1", myLabel = None, size = wx.DefaultSize,
			internal = False, flex = 0, wizardPageNumber = None):
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
				
			sizerNumber (int)       - The number of the sizer that this will be added to
			flags (list)            - A list of strings for which flag to add to the sizer
			myLabel (str)           - What this is called in the idCatalogue
			internal (bool)         - If True: The 'filePath' provided will represent an internal image
			wizardFrameNumber (int) - The number of the wizard page. If None: it assumes either a frame or a panel

			Example Input: addImage("1.bmp", 0)
			Example Input: addImage(image, 0)
			Example Input: addImage("error", 0, internal = True)
			Example Input: addImage(image, 0, size = (32, 32))
			"""

			#Determine if a specific id should be set
			if (myLabel != None):
				myId = self.newId(myLabel)
				
			else:
				myId = self.newId()
				
			#Which sizer is being used?
			sizer, panelNumber = self.getSizer(sizerNumber, returnPanel = True)

			#Determine if it is a wizard or not
			if (wizardPageNumber != None):
				exec("identity = self.m_wizPage" + str(wizardPageNumber))

			#Determine if it is a panel or not
			elif (panelNumber != None):
				identity = self.getPanel(panelNumber)

			#It must be the frame then
			else:
				identity = self

			#Get correct image
			image = self.getImage(imagePath, internal)
		
			#Create the thing to put in the grid
			thing = wx.StaticBitmap(identity, myId, image, wx.DefaultPosition, size, 0)

			#Configure Flags            
			flags, position, border = self.getItemMod(flags)

			#Add it to the grid
			self.addToSizer(sizer, thing, flex, flags, 5)

			#Add object to idCatalogue
			self.addToId(thing, myLabel)

		def addProgressBar(self, myInitial, myMax, sizerNumber, flags = "c1", myLabel = None, flex = 0, wizardPageNumber = None):
			"""Adds progress bar to the next cell on the grid.

			myInitial (int)         - The value that the progress bar starts at
			myMax (int)             - The value that the progress bar is full at
			sizerNumber (int)       - The number of the sizer that this will be added to
			flags (list)            - A list of strings for which flag to add to the sizer
			myLabel (str)           - What this is called in the idCatalogue
			wizardFrameNumber (int) - The number of the wizard page. If None, it assumes either a frame or a panel

			Example Input: addProgressBar(0, 100)
			"""

			#Determine if a specific id should be set
			if (myLabel != None):
				myId = self.newId(myLabel)
				
			else:
				myId = self.newId()
				
			#Which sizer is being used?
			sizer, panelNumber = self.getSizer(sizerNumber, returnPanel = True)

			#Determine if it is a wizard or not
			if (wizardPageNumber != None):
				exec("identity = self.m_wizPage" + str(wizardPageNumber))

			#Determine if it is a panel or not
			elif (panelNumber != None):
				identity = self.getPanel(panelNumber)

			#It must be the frame then
			else:
				identity = self
		
			#Create the thing to put in the grid
			thing = wx.Gauge(identity, myId, myMax, wx.DefaultPosition, wx.DefaultSize, wx.GA_HORIZONTAL)
			thing.SetValue(myInitial)

			#Configure Flags            
			flags, position, border = self.getItemMod(flags)

			#Add it to the grid
			self.addToSizer(sizer, thing, flex, flags, 5)

			#Add object to idCatalogue
			self.addToId(thing, myLabel)

		def addPickerColor(self, myFunction, sizerNumber, flags = "c1", myLabel = None,
		 myFunctionArgs = None, myFunctionKwargs = None, 
		 colorText = False, flex = 0, wizardPageNumber = None):
			"""Adds a color picker to the next cell on the grid.
			It can display the name or RGB of the color as well.

			myFunction (str)        - What function will be ran when the color is chosen
			sizerNumber (int)       - The number of the sizer that this will be added to
			flags (list)            - A list of strings for which flag to add to the sizer
			myLabel (str)           - What this is called in the idCatalogue
			myFunctionArgs (any)    - The arguments for 'myFunction'
			myFunctionKwargs (any)  - The keyword arguments for 'myFunction'function
			colorText (bool)        - True if it should show the name or RGB of the color picked
			wizardFrameNumber (int) - The number of the wizard page. If None, it assumes either a frame or a panel

			Example Input: addPickerColor("changeColor")
			"""

			#Determine if a specific id should be set
			if (myLabel != None):
				myId = self.newId(myLabel)

			else:
				myId = self.newId()

			#Which sizer is being used?
			sizer, panelNumber = self.getSizer(sizerNumber, returnPanel = True)

			#Determine if it is a wizard or not
			if (wizardPageNumber != None):
				exec("identity = self.m_wizPage" + str(wizardPageNumber))

			#Determine if it is a panel or not
			elif (panelNumber != None):
				identity = self.getPanel(panelNumber)

			#It must be the frame then
			else:
				identity = self
		
			#Create the thing to put in the grid
			if (colorText):
				thing = wx.ColourPickerCtrl(identity, myId, wx.BLACK, wx.DefaultPosition, wx.DefaultSize, wx.CLRP_DEFAULT_STYLE|wx.CLRP_USE_TEXTCTRL)
			else:
				thing = wx.ColourPickerCtrl(identity, myId, wx.BLACK, wx.DefaultPosition, wx.DefaultSize, wx.CLRP_DEFAULT_STYLE)

			#Configure Flags            
			flags, position, border = self.getItemMod(flags)

			#Add it to the grid
			self.addToSizer(sizer, thing, flex, flags, 5)

			#Bind the function(s)
			self.betterBind(wx.EVT_COLOURPICKER_CHANGED, thing, myFunction, myFunctionArgs, myFunctionKwargs)

			#Add object to idCatalogue
			self.addToId(thing, myLabel)

		def addPickerFont(self, maxSize, myFunction, sizerNumber, flags = "c1", myLabel = None, 
			myFunctionArgs = None, myFunctionKwargs = None, 
			fontText = False, flex = 0, wizardPageNumber = None):
			"""Adds a color picker to the next cell on the grid.
			It can display the name or RGB of the color as well.

			maxSize (int)           - The maximum font size that can be chosen
			myFunction (str)        - What function will be ran when the color is chosen
			sizerNumber (int)       - The number of the sizer that this will be added to
			flags (list)            - A list of strings for which flag to add to the sizer
			myLabel (str)           - What this is called in the idCatalogue
			myFunctionArgs (any)    - The arguments for 'myFunction'
			myFunctionKwargs (any)  - The keyword arguments for 'myFunction'function
			fontText (str)          - True if it should show the name of the font picked
			wizardFrameNumber (int) - The number of the wizard page. If None, it assumes either a frame or a panel

			Example Input: addPickerFont(32, "changeFont")
			"""

			#Determine if a specific id should be set
			if (myLabel != None):
				myId = self.newId(myLabel)

				
			else:
				myId = self.newId()
				
			#Which sizer is being used?
			sizer, panelNumber = self.getSizer(sizerNumber, returnPanel = True)

			#Determine if it is a wizard or not
			if (wizardPageNumber != None):
				exec("identity = self.m_wizPage" + str(wizardPageNumber))

			#Determine if it is a panel or not
			elif (panelNumber != None):
				identity = self.getPanel(panelNumber)

			#It must be the frame then
			else:
				identity = self
		
			#Create the thing to put in the grid
			if (fontText):
				thing = wx.FontPickerCtrl(identity, myId, wx.NullFont, wx.DefaultPosition, wx.DefaultSize, wx.FNTP_DEFAULT_STYLE|wx.FNTP_USE_TEXTCTRL)
			else:
				thing = wx.FontPickerCtrl(identity, myId, wx.NullFont, wx.DefaultPosition, wx.DefaultSize, wx.FNTP_DEFAULT_STYLE)
			thing.SetMaxPointSize(maxSize) 

			#Configure Flags            
			flags, position, border = self.getItemMod(flags)

			#Add it to the grid
			self.addToSizer(sizer, thing, flex, flags, 5)

			#Bind the function(s)
			self.betterBind(wx.EVT_FONTPICKER_CHANGED, thing, myFunction, myFunctionArgs, myFunctionKwargs)

			#Add object to idCatalogue
			self.addToId(thing, myLabel)

		def addPickerFile(self, myFunction, sizerNumber, flags = "c1", myLabel = None, 
			myFunctionArgs = None, myFunctionKwargs = None, text = "Select a File", initialDir = "*.*", flex = 0, 
			directoryOnly = False, changeCurrentDirectory = False, fileMustExist = False, openFile = False, 
			saveConfirmation = False, saveFile = False, smallButton = False, addInputBox = False, 
			hidden = False, wizardPageNumber = None):
			"""Adds a file picker to the next cell on the grid.

			myFunction (str)        - What function will be ran when the file is chosen
			sizerNumber (int)       - The number of the sizer that this will be added to
			flags (list)            - A list of strings for which flag to add to the sizer
			myLabel (str)           - What this is called in the idCatalogue
			myFunctionArgs (any)    - The arguments for 'myFunction'
			myFunctionKwargs (any)  - The keyword arguments for 'myFunction'function
			text (str)              - What is shown on the top of the popout window

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
			
			wizardFrameNumber (int) - The number of the wizard page. If None, it assumes either a frame or a panel

			Example Input: addPickerFile(self.openFile, 0, addInputBox = True)
			Example Input: addPickerFile(self.saveFile, 0, saveFile = True, saveConfirmation = True, directoryOnly = True)
			"""

			##Determine if a specific id should be set
			if (myLabel != None):
				myId = self.newId(myLabel)

			else:
				myId = self.newId()
				
			#Which sizer is being used?
			sizer, panelNumber = self.getSizer(sizerNumber, returnPanel = True)

			#Determine if it is a wizard or not
			if (wizardPageNumber != None):
				exec("identity = self.m_wizPage" + str(wizardPageNumber))

			#Determine if it is a panel or not
			elif (panelNumber != None):
				identity = self.getPanel(panelNumber)

			#It must be the frame then
			else:
				identity = self

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
					print("ERROR: Open config and save config cannot be added to the same file picker")
					return None
				if (changeCurrentDirectory and ((openFile or fileMustExist or saveFile or saveConfirmation))):
					print("Error: Open config and save config cannot be used in combination with a directory change")
					return None

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
				thing = wx.DirPickerCtrl(identity, myId, wx.EmptyString, text, wx.DefaultPosition, wx.DefaultSize, eval(config))
			else:
				thing = wx.FilePickerCtrl(identity, myId, wx.EmptyString, text, initialDir, wx.DefaultPosition, wx.DefaultSize, eval(config))

			#Set Initial directory
			thing.SetInitialDirectory(initialDir)

			#Configure Flags            
			flags, position, border = self.getItemMod(flags)

			#Determine visibility
			if (hidden):
				thing.Hide()

			#Add it to the grid
			self.addToSizer(sizer, thing, flex, flags, 5)

			#Bind the function(s)
			if (directoryOnly):
				self.betterBind(wx.EVT_DIRPICKER_CHANGED, thing, myFunction, myFunctionArgs, myFunctionKwargs)
			else:
				self.betterBind(wx.EVT_FILEPICKER_CHANGED, thing, myFunction, myFunctionArgs, myFunctionKwargs)

			#Add object to idCatalogue
			self.addToId(thing, myLabel)

		def addPickerFileWindow(self, myFunction, sizerNumber, flags = "c1", myLabel = None, 
			myFunctionArgs = None, myFunctionKwargs = None, 
			action = None, initialDir = "*.*", flex = 0, 
			editLabelFunction = None, editLabelFunctionArgs = None, editLabelFunctionKwargs = None, 
			rightClickFunction = None, rightClickFunctionArgs = None, rightClickFunctionKwargs = None, 
			directoryOnly = True, selectMultiple = False, wizardPageNumber = None):
			"""Adds a file picker window to the next cell on the grid.

			myFunction (str)               - What function will be ran when the file is chosen
			sizerNumber (int)              - The number of the sizer that this will be added to
			flags (list)                   - A list of strings for which flag to add to the sizer
			myLabel (str)                  - What this is called in the idCatalogue
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
			wizardFrameNumber (int)        - The number of the wizard page. If None, it assumes either a frame or a panel

			Example Input: addPickerFile("changeDirectory")
			"""

			#Determine if a specific id should be set
			if (myLabel != None):
				myId = self.newId(myLabel)
				
			else:
				myId = self.newId()
				
			#Which sizer is being used?
			sizer, panelNumber = self.getSizer(sizerNumber, returnPanel = True)

			#Determine if it is a wizard or not
			if (wizardPageNumber != None):
				exec("identity = self.m_wizPage" + str(wizardPageNumber))

			#Determine if it is a panel or not
			elif (panelNumber != None):
				identity = self.getPanel(panelNumber)

			#It must be the frame then
			else:
				identity = self
		
			#Create the thing to put in the grid
			if (directoryOnly):
				if (editLabelFunction != None):
					if (selectMultiple):
						thing = wx.GenericDirCtrl(identity, myId, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.DIRCTRL_3D_INTERNAL|wx.DIRCTRL_DIR_ONLY|wx.DIRCTRL_EDIT_LABELS|wx.DIRCTRL_MULTIPLE|wx.SUNKEN_BORDER, wx.EmptyString, 0)
					else:
						thing = wx.GenericDirCtrl(identity, myId, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.DIRCTRL_3D_INTERNAL|wx.DIRCTRL_DIR_ONLY|wx.DIRCTRL_EDIT_LABELS|wx.SUNKEN_BORDER, wx.EmptyString, 0)
				else:
					if (selectMultiple):
						thing = wx.GenericDirCtrl(identity, myId, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.DIRCTRL_3D_INTERNAL|wx.DIRCTRL_DIR_ONLY|wx.DIRCTRL_MULTIPLE|wx.SUNKEN_BORDER, wx.EmptyString, 0)
					else:
						thing = wx.GenericDirCtrl(identity, myId, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.DIRCTRL_3D_INTERNAL|wx.DIRCTRL_DIR_ONLY|wx.SUNKEN_BORDER, wx.EmptyString, 0)
			else:
				if (editLabelFunction != None):
					if (selectMultiple):
						thing = wx.GenericDirCtrl(identity, myId, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.DIRCTRL_3D_INTERNAL|wx.DIRCTRL_EDIT_LABELS|wx.DIRCTRL_MULTIPLE|wx.SUNKEN_BORDER, wx.EmptyString, 0)
					else:
						thing = wx.GenericDirCtrl(identity, myId, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.DIRCTRL_3D_INTERNAL|wx.DIRCTRL_EDIT_LABELS|wx.SUNKEN_BORDER, wx.EmptyString, 0)
				else:
					if (selectMultiple):
						thing = wx.GenericDirCtrl(identity, myId, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.DIRCTRL_3D_INTERNAL|wx.DIRCTRL_MULTIPLE|wx.SUNKEN_BORDER, wx.EmptyString, 0)
					else:
						thing = wx.GenericDirCtrl(identity, myId, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.DIRCTRL_3D_INTERNAL|wx.SUNKEN_BORDER, wx.EmptyString, 0)

			#Determine if it is hidden
			if (showHidden):
				thing.ShowHidden(True)
			else:
				thing.ShowHidden(False)

			#Configure Flags            
			flags, position, border = self.getItemMod(flags)

			#Add it to the grid
			self.addToSizer(sizer, thing, flex, flags, 5)

			#Bind the function(s)
			if (editLabelFunction != None):
				self.betterBind(wx.EVT_TREE_END_LABEL_EDIT, thing, editLabelFunction, editLabelFunctionArgs, editLabelFunctionKwargs)
			if (rightClickFunction != None):
				self.betterBind(wx.EVT_TREE_ITEM_RIGHT_CLICK, thing, rightClickFunction, rightClickFunctionArgs, rightClickFunctionKwargs)
			self.betterBind(wx.EVT_TREE_SEL_CHANGED, thing, myFunction, myFunctionArgs, myFunctionKwargs)

			#Add object to idCatalogue
			self.addToId(thing, myLabel)

		def addPickerTime(self, myFunction, sizerNumber, time = None,
			flags = "c1", myLabel = None, myFunctionArgs = None, myFunctionKwargs = None, 
			hidden = False, flex = 0, wizardPageNumber = None):
			"""Adds a time picker to the next cell on the grid.
			The input time is in military time.

			myFunction (str)        - What function will be ran when the time is changed
			sizerNumber (int)       - The number of the sizer that this will be added to
			time (str)              - What the currently selected time is as 'hh:mm:ss'
									  If None: The current time will be used
			flags (list)            - A list of strings for which flag to add to the sizer
			myLabel (str)           - What this is called in the idCatalogue
			myFunctionArgs (any)    - The arguments for 'myFunction'
			myFunctionKwargs (any)  - The keyword arguments for 'myFunction'function
			hidden (bool)           - If True: The widget is hidden from the user, but it is still created
			wizardFrameNumber (int) - The number of the wizard page. If None, it assumes either a frame or a panel

			Example Input: addPickerTime("changeTime", 0, "12:30:20")
			Example Input: addPickerTime("changeTime", 0, "17:30")
			"""

			#Determine if a specific id should be set
			if (myLabel != None):
				myId = self.newId(myLabel)
				
			else:
				myId = self.newId()
				
			#Which sizer is being used?
			sizer, panelNumber = self.getSizer(sizerNumber, returnPanel = True)

			#Determine if it is a wizard or not
			if (wizardPageNumber != None):
				exec("identity = self.m_wizPage" + str(wizardPageNumber))

			#Determine if it is a panel or not
			elif (panelNumber != None):
				identity = self.getPanel(panelNumber)

			#It must be the frame then
			else:
				identity = self

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
						print("ERROR: Time must be formatted 'hh:mm:ss' or 'hh:mm'. Using current time instead")
						time = wx.DateTime().SetToCurrent()

					hour, minute, second = int(hour), int(minute), int(second)
					time = wx.DateTime(1, 1, 2000, hour, minute, second)
				except:
					print("ERROR: Time must be formatted 'hh:mm:ss' or 'hh:mm'. Using current time instead")
					time = wx.DateTime().SetToCurrent()
			else:
				time = wx.DateTime().SetToCurrent()

			#Create the thing to put in the grid
			thing = wx.adv.TimePickerCtrl(identity, myId, time, wx.DefaultPosition, wx.DefaultSize, wx.adv.TP_DEFAULT)

			#Configure Flags            
			flags, position, border = self.getItemMod(flags)

			#Determine visibility
			if (hidden):
				thing.Hide()

			#Add it to the grid
			self.addToSizer(sizer, thing, flex, flags, 5)

			#Bind the function(s)
			self.betterBind(wx.adv.EVT_TIME_CHANGED, thing, myFunction, myFunctionArgs, myFunctionKwargs)

			#Add object to idCatalogue
			self.addToId(thing, myLabel)

		def addPickerDate(self, myFunction, sizerNumber, date = None,
			flags = "c1", myLabel = None, myFunctionArgs = None, myFunctionKwargs = None, 
			dropDown = False, hidden = False, flex = 0, wizardPageNumber = None):
			"""Adds a date picker to the next cell on the grid.

			myFunction (str)        - What function will be ran when the date is changed
			sizerNumber (int)       - The number of the sizer that this will be added to
			date (str)              - What the currently selected date is
									  If None: The current date will be used
			flags (list)            - A list of strings for which flag to add to the sizer
			myLabel (str)           - What this is called in the idCatalogue
			myFunctionArgs (any)    - The arguments for 'myFunction'
			myFunctionKwargs (any)  - The keyword arguments for 'myFunction'function
			dropDown (bool)         - True if a calandar dropdown should be displayed instead of just the arrows
			hidden (bool)           - If True: The widget is hidden from the user, but it is still created
			wizardFrameNumber (int) - The number of the wizard page. If None, it assumes either a frame or a panel

			Example Input: addPickerDate("changeDate", 0, "10/16/2000")
			Example Input: addPickerDate("changeDate", 0, dropDown = True)
			"""

			#Determine if a specific id should be set
			if (myLabel != None):
				myId = self.newId(myLabel)
				
			else:
				myId = self.newId()
				
			#Which sizer is being used?
			sizer, panelNumber = self.getSizer(sizerNumber, returnPanel = True)

			#Determine if it is a wizard or not
			if (wizardPageNumber != None):
				exec("identity = self.m_wizPage" + str(wizardPageNumber))

			#Determine if it is a panel or not
			elif (panelNumber != None):
				identity = self.getPanel(panelNumber)

			#It must be the frame then
			else:
				identity = self

			#Set the currently selected date
			if (date != None):
				try:
					month, day, year = re.split("[\\\\/]", newValue) #Format: mm/dd/yyyy
					month, day, year = int(month), int(day), int(year)
					date = wx.DateTime(day, month, year)
				except:
					print("ERROR: Calandar dates must be formatted 'mm/dd/yy'. Using current date instead")
					date = wx.DateTime().SetToCurrent()
			else:
				date = wx.DateTime().SetToCurrent()

			#Create the thing to put in the grid
			if (dropDown):
				thing = wx.adv.DatePickerCtrl(identity, myId, date, wx.DefaultPosition, wx.DefaultSize, wx.adv.DP_DEFAULT|wx.adv.DP_DROPDOWN)
			else:
				thing = wx.adv.DatePickerCtrl(identity, myId, date, wx.DefaultPosition, wx.DefaultSize, wx.adv.DP_DEFAULT)

			#Configure Flags            
			flags, position, border = self.getItemMod(flags)

			#Determine visibility
			if (hidden):
				thing.Hide()

			#Add it to the grid
			self.addToSizer(sizer, thing, flex, flags, 5)

			#Bind the function(s)
			self.betterBind(wx.adv.EVT_DATE_CHANGED, thing, myFunction, myFunctionArgs, myFunctionKwargs)

			#Add object to idCatalogue
			self.addToId(thing, myLabel)

		def addPickerDateWindow (self, myFunction, sizerNumber, date = None,
			flags = "c1", myLabel = None, myFunctionArgs = None, myFunctionKwargs = None, 
			showHolidays = False, showOther = False, hidden = False, flex = 0, 
			dayFunction = None, dayFunctionArgs = None, dayFunctionKwargs = None, 
			monthFunction = None, monthFunctionArgs = None, monthFunctionKwargs = None, 
			yearFunction = None, yearFunctionArgs = None, yearFunctionArgsKwargs = None, 
			wizardPageNumber = None):
			"""Adds a date picker to the next cell on the grid.

			myFunction (str)          - What function will be ran when the date is changed
			sizerNumber (int)         - The number of the sizer that this will be added to
			date (str)                - What the currently selected date is
										If None: The current date will be used
			flags (list)              - A list of strings for which flag to add to the sizer
			myLabel (str)             - What this is called in the idCatalogue
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

			wizardFrameNumber (int)   - The number of the wizard page. If None, it assumes either a frame or a panel

			Example Input: addPickerDateWindow("changeDate", 0)
			"""

			#Determine if a specific id should be set
			if (myLabel != None):
				myId = self.newId(myLabel)
			
			else:
				myId = self.newId()
				
			#Which sizer is being used?
			sizer, panelNumber = self.getSizer(sizerNumber, returnPanel = True)

			#Determine if it is a wizard or not
			if (wizardPageNumber != None):
				exec("identity = self.m_wizPage" + str(wizardPageNumber))

			#Determine if it is a panel or not
			elif (panelNumber != None):
				identity = self.getPanel(panelNumber)

			#It must be the frame then
			else:
				identity = self

			#Set the currently selected date
			if (date != None):
				try:
					month, day, year = re.split("[\\\\/]", newValue) #Format: mm/dd/yyyy
					date = wx.DateTime(day, month, year)
				except:
					print("ERROR: Calandar dates must be formatted 'mm/dd/yy'. Using current date instead")
					date = wx.DateTime().SetToCurrent()
			else:
				date = wx.DateTime().SetToCurrent()
		
			#Create the thing to put in the grid
			if (showHolidays):
				if (showOther):
					thing = wx.adv.CalendarCtrl(identity, myId, date, wx.DefaultPosition, wx.DefaultSize, wx.adv.CAL_SHOW_HOLIDAYS|wx.adv.CAL_SHOW_SURROUNDING_WEEKS)
				else:
					thing = wx.adv.CalendarCtrl(identity, myId, date, wx.DefaultPosition, wx.DefaultSize, wx.adv.CAL_SHOW_HOLIDAYS)
			else:
				if (showOther):
					thing = wx.adv.CalendarCtrl(identity, myId, date, wx.DefaultPosition, wx.DefaultSize, wx.adv.CAL_SHOW_SURROUNDING_WEEKS)
				else:
					thing = wx.adv.CalendarCtrl(identity, myId, date, wx.DefaultPosition, wx.DefaultSize, 0)

			#Configure Flags            
			flags, position, border = self.getItemMod(flags)

			#Determine visibility
			if (hidden):
				thing.Hide()

			#Add it to the grid
			self.addToSizer(sizer, thing, flex, flags, 5)

			#Bind the function(s)
			self.betterBind(wx.adv.EVT_CALENDAR_SEL_CHANGED, thing, myFunction, myFunctionArgs, myFunctionKwargs)
			if (dayFunction != None):
				self.betterBind(wx.adv.EVT_CALENDAR_DAY, thing, dayFunction, dayFunctionArgs, dayFunctionKwargs)
			if (monthFunction != None):
				self.betterBind(wx.adv.EVT_CALENDAR_MONTH, thing, monthFunction, monthFunctionArgs, monthFunctionKwargs)
			if (yearFunction != None):
				self.betterBind(wx.adv.EVT_CALENDAR_YEAR, thing, yearFunction, yearFunctionArgs, yearFunctionKwargs)

			#Add object to idCatalogue
			self.addToId(thing, myLabel)
		
		def addHyperlink(self, myText, myWebsite, myFunction, sizerNumber, flags = "c1", myLabel = None, 
			myFunctionArgs = None, myFunctionKwargs = None, 
			flex = 0, wizardPageNumber = None):
			"""Adds a hyperlink text to the next cell on the grid.

			myText (str)            - What text is shown
			myWebsite (str)         - The address of the website to open
			myFunction (str)        - What function will be ran when the link is clicked
			sizerNumber (str)       - The number of the sizer that this will be added to
			flags (list)            - A list of strings for which flag to add to the sizer
			myLabel (str)           - What this is called in the idCatalogue
			myFunctionArgs (any)    - The arguments for 'myFunction'
			myFunctionKwargs (any)  - The keyword arguments for 'myFunction'function
			wizardFrameNumber (int) - The number of the wizard page. If None, it assumes either a frame or a panel

			Example Input: addHyperlink("wxFB Website", "http://www.wxformbuilder.org", "siteVisited")
			"""

			#Determine if a specific id should be set
			if (myLabel != None):
				myId = self.newId(myLabel)
	
			else:
				myId = self.newId()
				
			#Which sizer is being used?
			sizer, panelNumber = self.getSizer(sizerNumber, returnPanel = True)

			#Determine if it is a wizard or not
			if (wizardPageNumber != None):
				exec("identity = self.m_wizPage" + str(wizardPageNumber))

			#Determine if it is a panel or not
			elif (panelNumber != None):
				identity = self.getPanel(panelNumber)

			#It must be the frame then
			else:
				identity = self
		
			#Create the thing to put in the grid
			thing = wx.HyperlinkCtrl(identity, myId, myText, myWebsite, wx.DefaultPosition, wx.DefaultSize, wx.HL_DEFAULT_STYLE)

			#Configure Flags            
			flags, position, border = self.getItemMod(flags)

			#Add it to the grid
			self.addToSizer(sizer, thing, flex, flags, 5)

			#Bind the function(s)
			self.betterBind(wx.EVT_HYPERLINK, thing, myFunction, myFunctionArgs, myFunctionKwargs)

			#Add object to idCatalogue
			self.addToId(thing, myLabel)

		def addCheckList(self, choices, myFunction, sizerNumber, flags = "c1", myLabel = None, 
			myFunctionArgs = None, myFunctionKwargs = None, 
			multiple = True, sort = False, flex = 0, wizardPageNumber = None):
			"""Adds a checklist to the next cell on the grid.

			choices (list)          - A list of strings that are the choices for the check boxes
			myFunction (str)        - What function will be ran when the date is changed
			sizerNumber (int)       - The number of the sizer that this will be added to
			flags (list)            - A list of strings for which flag to add to the sizer
			myLabel (str)           - What this is called in the idCatalogue
			myFunctionArgs (any)    - The arguments for 'myFunction'
			myFunctionKwargs (any)  - The keyword arguments for 'myFunction'function
			multiple (bool)         - True if the user can check off multiple check boxes
			sort (bool)             - True if the checklist will be sorted alphabetically or numerically
			wizardFrameNumber (int) - The number of the wizard page. If None, it assumes either a frame or a panel

			Example Input: addCheckList(["Milk", "Eggs", "Bread"], 0, sort = True)
			"""

			#Determine if a specific id should be set
			if (myLabel != None):
				myId = self.newId(myLabel)
		
			else:
				myId = self.newId()
				
			#Which sizer is being used?
			sizer, panelNumber = self.getSizer(sizerNumber, returnPanel = True)

			#Determine if it is a wizard or not
			if (wizardPageNumber != None):
				exec("identity = self.m_wizPage" + str(wizardPageNumber))

			#Determine if it is a panel or not
			elif (panelNumber != None):
				identity = self.getPanel(panelNumber)

			#It must be the frame then
			else:
				identity = self
		
			#Create the thing to put in the grid
			if (multiple):
				if (sort):
					thing = wx.CheckListBox(identity, myId, wx.DefaultPosition, wx.DefaultSize, choices, wx.LB_MULTIPLE|wx.LB_NEEDED_SB|wx.LB_SORT)
				else:
					thing = wx.CheckListBox(identity, myId, wx.DefaultPosition, wx.DefaultSize, choices, wx.LB_MULTIPLE|wx.LB_NEEDED_SB)
			else:
				if (sort):
					thing = wx.CheckListBox(identity, myId, wx.DefaultPosition, wx.DefaultSize, choices, wx.LB_NEEDED_SB|wx.LB_SORT)
				else:
					thing = wx.CheckListBox(identity, myId, wx.DefaultPosition, wx.DefaultSize, choices, wx.LB_NEEDED_SB)

			#Configure Flags            
			flags, position, border = self.getItemMod(flags)

			#Add it to the grid
			self.addToSizer(sizer, thing, flex, flags, 5)

			#Bind the function(s)
			self.betterBind(wx.EVT_CHECKLISTBOX, thing, myFunction, myFunctionArgs, myFunctionKwargs)

			#Add object to idCatalogue
			self.addToId(thing, myLabel)

		def addToolTip(self, triggerObjectLabel, text, myLabel = None,  maxWidth = None, 
			delayAppear = None, delayDisappear = None, delayReappear = None):
			"""Adds a small text box that will appear when the mouse hovers over a wxObject.

			triggerObjectLabel (str) - The id catalogue number for the object that triggers the tool tip
			text (str)               - What the text box will say
			myLabel (str)            - What this is called in the idCatalogue
			maxWidth (int)           - How long the text box will be until it wraps the text to a new line.
									   If None: The wrap width will be automatically calculated
									   If -1: The text will not wrap
			
			delayAppear (int)    - Sets a delay in milliseconds for the tool tip to appear. If None, there will be no delay
			delayDisappear (int) - Sets a delay in milliseconds for the tool tip to disappear. If None, there will be no delay
			delayReappear (int)  - Sets a delay in milliseconds for the tool tip to appear again. If None, there will be no delay

			Example Input: addToolTip("printPreview", "Shows what will be sent to the printer.")
			"""

			#Determine if a specific id should be set
			if (myLabel != None):
				myId = self.newId(myLabel)
		
			else:
				myId = self.newId()

			#Get the wxObject to add the tooltip to
			thing = self.getObjectWithLabel(triggerObjectLabel)

			#Add the tool tip
			toolTip = wx.ToolTip(text)

			#Apply properties
			if (delayAppear != None):
				toolTip.SetDelay(delayAppear)

			if (delayDisappear != None):
				toolTip.SetDelay(delayDisappear)

			if (delayReappear != None):
				toolTip.SetDelay(delayReappear)

			if (maxWidth != None):
				toolTip.SetMaxWidth(maxWidth)

			#Attach the tool tip to the wxObject
			thing.SetToolTip(toolTip)

			#Catalogue tool tip
			if (myLabel != None):
				self.catalogueToolTip(myLabel, toolTip)

			self.addToId(toolTip, myLabel)

		def getToolTip(self, triggerObjectLabel):
			"""Adds a small text box that will appear when the mouse hovers over a wxObject.

			triggerObjectLabel (str) - The id catalogue number for the object that triggers the tool tip
			
			Example Input: getToolTip("printPreview")
			"""

			#Get the wxObject to add the tooltip to
			try:
				thing = self.toolTipDict[triggerObjectLabel]
			except:
				print("ERROR: The object", triggerObjectLabel, "Has no tool tip associated with it.")
				return None

			#Add the tool tip
			toolTip = thing.GetToolTip()
			return toolTip

		#Canvas Drawing
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
			Example Input: getBrushStyle("image", "error", true)
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

		def drawUpdate(self, canvasNumber):
			"""Updates the canvas."""

			canvas = self.getCanvas(canvasNumber)
			canvas.update()

		def drawNew(self, canvasNumber):
			"""Clears the canvas."""

			canvas = self.getCanvas(canvasNumber)
			canvas.new()

		def drawSave(self, canvasNumber, imagePath = "savedImage"):
			"""Saves the canvas to an external folder."""

			canvas = self.getCanvas(canvasNumber)
			canvas.save(imagePath)

		def drawZoom(self, canvasNumber, x, y = None):
			"""Zooms the image in or out.

			x (int) - The x-axis scaling factor
					  If None: The scale will be set to 1:1
			y (int) - The y-axis scaling factor
					  If None: Will be the same as x

			Example Input: drawZoom(0, 2)
			Example Input: drawZoom(0, 2.5, 3)
			Example Input: drawZoom(0, None)
			"""

			#Get the canvas
			canvas = self.getCanvas(canvasNumber)

			#Scale the canvas
			if (x != None):
				if (y != None):
					canvas.SetUserScale(x, y)
				else:
					canvas.SetUserScale(x, x)

			else:
				canvas.SetUserScale(1, 1)

		def drawSetOrigin(self, canvasNumber, x, y = None):
			"""Changes the origin of the canvas after scaling has been applied.

			x (int) - The x-axis origin point using the current origin's coordinates
			y (int) - The y-axis origin point using the current origin's coordinates
					  If None: Will be the same as x

			Example Input: drawZoom(0, 2)
			Example Input: drawZoom(0, 2.5, 3)
			"""

			#Get the canvas
			canvas = self.getCanvas(canvasNumber)

			#Skip empty origins
			if (x != None):
				#Move the origin
				if (y != None):
					canvas.SetDeviceOrigin(x, y)
				else:
					canvas.SetDeviceOrigin(x, x)
				
		def drawImage(self, canvasNumber, imagePath, x, y, internal = True, alpha = False):
			"""Draws an image on the canvas.
			
			canvasNumber (int) - The canvas to draw this on

			imagePath (str) - The pathway to the image
			x (int)         - The x-coordinate of the image on the canvas
			y (int)         - The y-coordinate of the image on the canvas

			Example Input: drawImage(0, "python.jpg", 10, 10)
			"""

			#Skip blank images
			if (imagePath != None):
				#Get the canvas
				canvas = self.getCanvas(canvasNumber)

				#Get correct image
				image = self.getImage(imagePath, internal, alpha = alpha)

				#Draw the image
				canvas.queue("dc.DrawBitmap", [image, x, y, alpha])

		def drawText(self, canvasNumber, text, x, y, size = 12, angle = None, color = (0, 0, 0), bold = False):
			"""Draws text on the canvas.
			### To Do: Add font family, italix, and bold args ###

			canvasNumber (int) - The canvas to draw this on
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

			Example Input: drawText(0, "Lorem Ipsum", 5, 5)
			Example Input: drawText(0, "Lorem Ipsum", 5, 5, 10)
			Example Input: drawText(0, "Lorem Ipsum", 5, 5, 10, 45)
			Example Input: drawText(0, "Lorem Ipsum", 5, 5, color = (255, 0, 0))
			Example Input: drawText(0, ["Lorem Ipsum", "Dolor Sit"], 5, 5, color = (255, 0, 0)) #Will draw both on top of each other
			Example Input: drawText(0, ["Lorem Ipsum", "Dolor Sit"], 5, [5, 10]) #Will draw both in a straight line
			Example Input: drawText(0, ["Lorem Ipsum", "Dolor Sit"], 5, [5, 10], color = [(255, 0, 0), (0, 255, 0)]) #Will color both differently
			Example Input: drawText(0, ["Lorem Ipsum", "Dolor Sit"], 5, [5, 10], 18) #Will size both the same
			Example Input: drawText(0, ["Lorem Ipsum", "Dolor Sit"], 5, [5, 10], [12, 18]) #Will size both differently
			Example Input: drawText(0, ["Lorem Ipsum", "Dolor Sit"], 5, [5, 10], angle = 45) #Will rotate both to the same angle
			Example Input: drawText(0, ["Lorem Ipsum", "Dolor Sit"], 5, [5, 10], angle = [45, -45]) #Will rotate both to different angles
			Example Input: drawText(0, ["Lorem Ipsum", "Dolor Sit"], 5, [5, 10], angle = [45, 0]) #Will rotate only one
			Example Input: drawText(0, ["Lorem Ipsum", "Dolor Sit"], [5, 10], [5, 10], [12, 18], [45, 0], [(255, 0, 0), (0, 255, 0)])
			"""

			#Get the canvas
			canvas = self.getCanvas(canvasNumber)

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
						canvas.queue("dc.SetFont", font)

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
							canvas.queue("dc.SetPen", pen)
						else:
							canvas.queue("dc.SetPen", pen[i])

						#Draw text
						canvas.queue("dc.DrawRotatedText", [item, textX, textY, textAngle])
				else:
					canvas.queue("dc.SetPen", pen)
					canvas.queue("dc.DrawRotatedText", [text, x, y, angle])
			
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
							canvas.queue("dc.SetFont", font)

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
								canvas.queue("dc.SetPen", pen[i])

							#Draw text
							canvas.queue("dc.DrawText", [item, textX, textY])

					else:
						#Determine font family
						fontFamily = wx.ROMAN

						#Determine font italicization
						fontItalic = wx.ITALIC

						#Determine font boldness
						fontBold = wx.NORMAL

						#Define font
						font = wx.Font(size, fontFamily, fontItalic, fontBold)
						canvas.queue("dc.SetFont", font)

						#Ensure x-coordinates and y-coordinates are lists
						if ((type(x) != list) and (type(x) != tuple)):
							x = [x for i in range(len(text))]

						if ((type(y) != list) and (type(y) != tuple)):
							y = [y for i in range(len(text))]

						#Leaf x-coordinates and y-coordinates
						coordinates = [(x[i], y[i]) for i in range(len(text))]

						#Draw text
						canvas.queue("dc.DrawTextList", [item, coordinates, pen])
				else:
					#Determine font family
					fontFamily = wx.ROMAN

					#Determine font italicization
					fontItalic = wx.NORMAL

					#Determine font boldness
					fontBold = wx.NORMAL

					#Define font
					font = wx.Font(size, fontFamily, fontItalic, fontBold)
					canvas.queue("dc.SetFont", font)

					canvas.queue("dc.SetPen", pen)
					canvas.queue("dc.DrawText", [text, x, y])

		def drawPoint(self, canvasNumber, x, y, color = (0, 0, 0)):
			"""Draws a single pixel on the canvas.

			canvasNumber (int) - The canvas to draw this on
			x (int) - The x-coordinate of the point
					- If a list is given: Is a list containing (x, y) for each point to draw. 'y' will be ignored
					  Note: This is the fastest way to draw many points

			y (int) - The y-coordinate of the point
			color (tuple) - (R, G, B) as integers
						  - If a list of tuples is given and 'x' is a list: Each color will be used for each point in the list 'x' correcponding to that index

			Example Input: drawPoint(0, 5, 5)
			Example Input: drawPoint(0, 5, 5, (255, 0, 0))
			Example Input: drawPoint(0, [(5, 5), (7, 7)], color = (255, 0, 0))
			Example Input: drawPoint(0, [(5, 5), (7, 7)], color = [(255, 0, 0), (0, 255, 0)])
			"""

			#Get the canvas
			canvas = self.getCanvas(canvasNumber)

			#Determine point color
			pen = self.getPen(color)

			#Draw the point
			if ((type(x) == list) or (type(x) == tuple)):
				canvas.queue("dc.DrawPointList", [x, pen])
			else:
				canvas.queue("dc.SetPen", pen)
				canvas.queue("dc.DrawPoint", [x, y])

		def drawLine(self, canvasNumber, x1, y1, x2, y2, width = 1, color = (0, 0, 0)):
			"""Draws a line on the canvas.

			canvasNumber (int) - The canvas to draw this on
			x1 (int)      - The x-coordinate of endpoint 1
						  - If a list is given: Is a list containing (x1, y1, x2, y2) or [(x1, y1), (x2, y2)] for each line to draw. 'y1', 'x2', and 'y2' will be ignored
							Note: This is the fastest way to draw many lines

			y1 (int)      - The y-coordinate of endpoint 1
			x2 (int)      - The x-coordinate of endpoint 2
			y2 (int)      - The y-coordinate of endpoint 2
			width (int)   - How thick the line is
			color (tuple) - (R, G, B) as integers
						  - If a list of tuples is given and 'x1' is a list: Each color will be used for each line in the list 'x1' correcponding to that index

			Example Input: drawLine(0, 5, 5, 10, 10)
			Example Input: drawLine(0, 5, 5, 10, 10, (255, 0, 0))
			Example Input: drawLine(0, [(5, 5, 10, 10), (7, 7, 12, 12)], color = (255, 0, 0))
			Example Input: drawLine(0, [(5, 5, 10, 10), (7, 7, 12, 12)], color = [(255, 0, 0), (0, 255, 0)])
			Example Input: drawLine(0, [[(5, 5), (10, 10)], [(7, 7), (12, 12)], color = (255, 0, 0))
			"""

			#Get the canvas
			canvas = self.getCanvas(canvasNumber)

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
				canvas.queue("dc.DrawLineList", [lines, pen])
			else:
				canvas.queue("dc.SetPen", pen)
				canvas.queue("dc.DrawLine", [x1, y1, x2, y2])

		def drawSpline(self, canvasNumber, points, color = (0, 0, 0)):
			"""Draws a spline on the canvas.

			canvasNumber (int) - The canvas to draw this on
			points (list) - The vertices of the spline as tuples
						  - If a list of lists is given: Is a list containing the points for each spline to draw
							Note: This provides no speed benifit

			color (tuple) - (R, G, B) as integers
						  - If a list of tuples is given and 'points' is a list: Each color will be used for each spline in the list 'points' correcponding to that index

			Example Input: drawSpline(0, [(5, 5), (10, 10), (15, 15)])
			Example Input: drawSpline(0, [[(5, 5), (10, 10), (15, 15)], [(7, 7), (12, 12), (13, 13)], color = (255, 0, 0))
			Example Input: drawSpline(0, [[(5, 5), (10, 10), (15, 15)], [(7, 7), (12, 12), (13, 13)], color = [(255, 0, 0), (0, 255, 0)])
			"""

			#Get the canvas
			canvas = self.getCanvas(canvasNumber)

			#Determine spline color
			pen = self.getPen(color)

			#Draw the spline
			if ((type(points) == list) or (type(points) == tuple)):
				for item in points:
					#Configure points
					spline = [element for sublist in item for element in sublist]

					#Draw spline
					canvas.queue("dc.DrawSpline", spline)
			else:
				canvas.queue("dc.SetPen", pen)
				canvas.queue("dc.DrawSpline", points)

		def drawArc(self, canvasNumber, x, y, width, height = None, start = 0, end = 180, outline = (0, 0, 0), fill = None, style = None):
			"""Draws an arced line on the canvas.
			The arc is drawn counter-clockwise from (x1, y1) to (x3, y3).

			canvasNumber (int) - The canvas to draw this on
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

			Example Input: drawArc(0, 5, 5, 10)
			Example Input: drawArc(0, 5, 5, 10, start = 90, end = 180)
			Example Input: drawArc(0, 5, 5, 10, 5, outline = (255, 0, 0))
			Example Input: drawArc(0, 5, 5, 10, 5, outline = (255, 0, 0), fill = (0, 255, 0))
			Example Input: drawArc(0, [(5, 5), (7, 7)], 10, start = 90, end = 180)
			Example Input: drawArc(0, [(5, 5), (7, 7)], 10, start = [45, 225], end = [90, 270])
			Example Input: drawArc(0, [(5, 5), (7, 7)], 10, outline = (255, 0, 0))
			Example Input: drawArc(0, [(5, 5), (7, 7)], 10, outline = [(255, 0, 0), (0, 255, 0)])
			Example Input: drawArc(0, [(5, 5), (7, 7)], [7, 10], outline = (255, 0, 0))
			Example Input: drawArc(0, [(5, 5), (7, 7)], [7, 10], [5, 10], outline = (255, 0, 0))
			Example Input: drawArc(0, [(5, 5), (7, 7)], 10, outline = [(255, 0, 0), (0, 255, 0)], fill = [(0, 255, 0), (255, 0, 0)], style = "solid")
			Example Input: drawArc(0, [(5, 5), (7, 7)], 10, outline = [(255, 0, 0), (0, 255, 0)], fill = [(0, 255, 0), (255, 0, 0)], style = ["solid", "hatchCross"])
			"""

			#Get the canvas
			canvas = self.getCanvas(canvasNumber)

			#Determine arc color
			pen = self.getPen(outline)
			brush = self.getBrush(fill, style)

			#Draw the arc
			if ((type(x) == list) or (type(x) == tuple)):
				for i, item in enumerate(x):
					#Setup colors
					if ((type(pen) != list) and (type(pen) != tuple)):
						canvas.queue("dc.SetPen", pen)
					else:
						canvas.queue("dc.SetPen", pen[i])

					if (type(brush) != list):
						canvas.queue("dc.SetBrush", brush)
					else:
						canvas.queue("dc.SetBrush", brush[i])

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
					canvas.queue("dc.DrawEllipticArc", [item[0], item[1], arcWidth, arcHeight, arcStart, arcEnd])
			else:
				if (height == None):
					height = width

				canvas.queue("dc.SetPen", pen)
				canvas.queue("dc.SetBrush", brush)
				canvas.queue("dc.DrawEllipticArc", [x, y, width, height, start, end])

		def drawCheckMark(self, canvasNumber, x, y, width, height = None, color = (0, 0, 0)):
			"""Draws a check mark on the canvas.

			canvasNumber (int) - The canvas to draw this on
			x (int)       - The x-coordinate of the top-left corner of a rectangle that contains the check mark
						  - If a list is given: Is a list containing (x, y) for each point to draw. 'y' will be ignored
							Note: This provides no speed benifit

			y (int)       - The y-coordinate of the top-left corner of a rectangle that contains the check mark
			width (int)   - The width of the rectangle that contains the check mark
						  - If a list is given and 'x' is a list: Is a list containing the width for each arc to draw. Each width will be used for each check mark in the list 'x' correcponding to that index

			height (int)  - The height of the rectangle that contains the check mark. If None: It will be a square
						  - If a list is given and 'x' is a list: Is a list containing the width for each arc to draw. Each width will be used for each check mark in the list 'x' correcponding to that index

			color (tuple) - (R, G, B) as integers

			Example Input: drawCheckMark(0, 5, 5, 10)
			Example Input: drawCheckMark(0, 5, 5, 10, 5, (255, 0, 0))
			Example Input: drawCheckMark(0, [(5, 5), (10, 10)], 10)
			Example Input: drawCheckMark(0, [(5, 5), (10, 10)], [10, 5])
			Example Input: drawCheckMark(0, [(5, 5), (10, 10)], 10, color = [(255, 0, 0), (0, 255, 0)])
			"""

			#Get the canvas
			canvas = self.getCanvas(canvasNumber)

			#Determine check mark color
			pen = self.getPen(color)

			#Draw the line
			if ((type(x) == list) or (type(x) == tuple)):
				for i, item in enumerate(x):
					#Setup color
					if ((type(pen) != list) and (type(pen) != tuple)):
						canvas.queue("dc.SetPen", pen)
					else:
						canvas.queue("dc.SetPen", pen[i])

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
					canvas.queue("dc.DrawCheckMark", [item[0], item[1], checkMarkWidth, checkMarkHeight])
			else:
				#Draw the line
				if (height == None):
					height = width

				canvas.queue("dc.SetPen", pen)
				canvas.queue("dc.DrawCheckMark", [x, y, width, height])

		def drawRectangle(self, canvasNumber, x, y, width, height = None, radius = None, outline = (0, 0, 0), outlineWidth = 1, fill = None, style = None):
			"""Draws a rectangle on the canvas.

			canvasNumber (int) - The canvas to draw this on
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

			Example Input: drawRectangle(0, 5, 5, 25)
			Example Input: drawRectangle(0, 5, 5, 25, 40)
			Example Input: drawRectangle(0, 5, 5, 25, outline = (255, 0, 0))
			Example Input: drawRectangle(0, 5, 5, 10, 5, outline = (255, 0, 0), fill = (0, 255, 0))
			Example Input: drawRectangle(0, [(5, 5), (7, 7)], 10, outline = (255, 0, 0))
			Example Input: drawRectangle(0, [(5, 5), (7, 7)], 10, outline = [(255, 0, 0), (0, 255, 0)])
			Example Input: drawRectangle(0, [(5, 5), (7, 7)], [7, 10], outline = (255, 0, 0), outlineWidth = 4)
			Example Input: drawRectangle(0, [(5, 5), (7, 7)], [7, 10], [5, 10], outline = (255, 0, 0))
			Example Input: drawRectangle(0, [(5, 5), (7, 7)], 10, outline = [(255, 0, 0), (0, 255, 0)], fill = [(0, 255, 0), (255, 0, 0)], style = "solid")
			Example Input: drawRectangle(0, [(5, 5), (7, 7)], 10, outline = [(255, 0, 0), (0, 255, 0)], fill = [(0, 255, 0), (255, 0, 0)], style = ["solid", "hatchCross"])
			"""

			#Get the canvas
			canvas = self.getCanvas(canvasNumber)

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
							canvas.queue("dc.SetPen", pen)
						else:
							canvas.queue("dc.SetPen", pen[i])

						if (type(brush) != list):
							canvas.queue("dc.SetBrush", brush)
						else:
							canvas.queue("dc.SetBrush", brush[i])

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
						canvas.queue("dc.DrawRoundedRectangle", [item[0], item[1], width, height, radius])

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
					canvas.queue("dc.DrawRectangleList", [rectangles, pen, brush])
			else:

				#Draw the rectangle
				if (height == None):
					height = width

				canvas.queue("dc.SetPen", pen)
				canvas.queue("dc.SetBrush", brush)

				if (radius != None):
					canvas.queue("dc.DrawRoundedRectangle", [x, y, width, height, radius])
				else:
					canvas.queue("dc.DrawRectangle", [x, y, width, height])

		def drawPolygon(self, canvasNumber, points, outline = (0, 0, 0), outlineWidth = 1, fill = None, style = None, algorithm = 0):
			"""Draws a polygon on the canvas.

			canvasNumber (int) - The canvas to draw this on
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

			Example Input: drawPolygon(0, [(5, 5), (7, 5), (5, 7)])
			Example Input: drawPolygon(0, [(5, 5), (7, 5), (5, 7)], outline = (255, 0, 0), fill = (0, 255, 0), outlineWidth = 4)
			Example Input: drawPolygon(0, [[(5, 5), (7, 5), (5, 7)], [(8, 8), (10, 8), (8, 10)]])
			Example Input: drawPolygon(0, [[(5, 5), (7, 5), (5, 7)], [(8, 8), (10, 8), (8, 10)]], outline = [(255, 0, 0), (0, 255, 0)], fill = [(0, 255, 0), (255, 0, 0)], style = "hatchCross")
			Example Input: drawPolygon(0, [[(5, 5), (7, 5), (5, 7)], [(8, 8), (10, 8), (8, 10)]], outline = [(255, 0, 0), (0, 255, 0)], fill = [(0, 255, 0), (255, 0, 0)], style = ["solid", "hatchCross"])
			"""

			#Get the canvas
			canvas = self.getCanvas(canvasNumber)

			#Determine point color
			pen = self.getPen(outline, outlineWidth)
			brush = self.getBrush(fill, style)

			#Draw the polygon
			if (type(points) == list):
				canvas.queue("dc.DrawPolygonList", [points, pen, brush])
			else:
				canvas.queue("dc.SetPen", pen)
				canvas.queue("dc.SetBrush", brush)
				canvas.queue("dc.DrawPolygon", [points, 0, 0, style])

		def drawCircle(self, canvasNumber, x, y, radius, outline = (0, 0, 0), outlineWidth = 1, fill = None, style = None):
			"""Draws a circle on the canvas.

			canvasNumber (int) - The canvas to draw this on
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

			Example Input: drawCircle(0, 5, 5, 10)
			Example Input: drawCircle(0, 5, 5, 10, (255, 0, 0))
			Example Input: drawCircle(0, 5, 5, 10, outline = (255, 0, 0), fill = (0, 255, 0))
			Example Input: drawCircle(0, [(5, 5), (7, 7)], 10, outline = (255, 0, 0), outlineWidth = 4)
			Example Input: drawCircle(0, [(5, 5), (7, 7)], 10, outline = [(255, 0, 0), (0, 255, 0)])
			Example Input: drawCircle(0, [(5, 5), (7, 7)], [7, 10], outline = (255, 0, 0))
			Example Input: drawCircle(0, [(5, 5), (7, 7)], 10, outline = [(255, 0, 0), (0, 255, 0)], fill = [(0, 255, 0), (255, 0, 0)], style = "solid")
			Example Input: drawCircle(0, [(5, 5), (7, 7)], 10, outline = [(255, 0, 0), (0, 255, 0)], fill = [(0, 255, 0), (255, 0, 0)], style = ["solid", "hatchCross"])
			"""

			#Get the canvas
			canvas = self.getCanvas(canvasNumber)

			#Determine circle color
			pen = self.getPen(outline, outlineWidth)
			brush = self.getBrush(fill, style)

			#Draw the circle
			if ((type(x) == list) or (type(x) == tuple)):
				for i, item in enumerate(x):
					#Setup colors
					if ((type(pen) != list) and (type(pen) != tuple)):
						canvas.queue("dc.SetPen", pen)
					else:
						canvas.queue("dc.SetPen", pen[i])

					if (type(brush) != list):
						canvas.queue("dc.SetBrush", brush)
					else:
						canvas.queue("dc.SetBrush", brush[i])

					#Determine radius
					if ((type(radius) != list) and (type(radius) != tuple)):
						circleRadius = radius
					else:
						circleRadius = radius[i]

					#Draw the circle
					canvas.queue("dc.DrawCircle", [item[0], item[1], circleRadius])

			else:
				#Draw the circle
				canvas.queue("dc.SetPen", pen)
				canvas.queue("dc.SetBrush", brush)
				canvas.queue("dc.DrawCircle", [x, y, radius])

		def drawEllipse(self, canvasNumber, x, y, width, height = None, outline = (0, 0, 0), outlineWidth = 1, fill = None, style = None):
			"""Draws a ellipse on the canvas.

			canvasNumber (int) - The canvas to draw this on
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

			Example Input: drawEllipse(0, 5, 5, 25)
			Example Input: drawEllipse(0, 5, 5, 25, 40)
			Example Input: drawEllipse(0, 5, 5, 25, outline = (255, 0, 0))
			Example Input: drawEllipse(0, 5, 5, 10, 5, outline = (255, 0, 0), fill = (0, 255, 0))
			Example Input: drawEllipse(0, [(5, 5), (7, 7)], 10, outline = (255, 0, 0))
			Example Input: drawEllipse(0, [(5, 5), (7, 7)], 10, outline = [(255, 0, 0), (0, 255, 0)])
			Example Input: drawEllipse(0, [(5, 5), (7, 7)], [7, 10], outline = (255, 0, 0), outlineWidth = 4)
			Example Input: drawEllipse(0, [(5, 5), (7, 7)], [7, 10], [5, 10], outline = (255, 0, 0))
			Example Input: drawEllipse(0, [(5, 5), (7, 7)], 10, outline = [(255, 0, 0), (0, 255, 0)], fill = [(0, 255, 0), (255, 0, 0)], style = "solid")
			Example Input: drawEllipse(0, [(5, 5), (7, 7)], 10, outline = [(255, 0, 0), (0, 255, 0)], fill = [(0, 255, 0), (255, 0, 0)], style = ["solid", "hatchCross"])
			"""

			#Get the canvas
			canvas = self.getCanvas(canvasNumber)

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
				canvas.queue("dc.DrawEllipseList", [ellipses, pen, brush])
			else:

				#Draw the ellipse
				if (height == None):
					height = width

				canvas.queue("dc.SetPen", pen)
				canvas.queue("dc.SetBrush", brush)

				canvas.queue("dc.DrawEllipse", [x, y, width, height])

	class Plots():
		"""Creates and embeds a matplotlib figure in the window as a widget.
		Code adapted from: https://sukhbinder.wordpress.com/2013/12/19/matplotlib-with-wxpython-example-with-panzoom-functionality/
		and http://stackoverflow.com/questions/10737459/embedding-a-matplotlib-figure-inside-a-wxpython-panel

		Example Input: None. Meant to be inherited by Windows()
		"""

		def __init__(self, title = "MatPlotLib Figure"):
			"""Does nothing. This is here to comply with PEP 8 standards.

			title (str) - The figure's title

			Example Input: Plot()
			Example Input: Plot("Lorem Ipsum")
			"""

			# #Create the canvas
			# figure = matplotlib.figure.Figure()
			# self.subplot = figure.add_subplot(111)
			# #canvas = FigureCanvas(self, -1, figure)



			# # self.axes = self.figure.add_subplot(111)
			# # self.canvas = FigureCanvas(self, -1, self.figure)
			# # self.sizer = wx.BoxSizer(wx.VERTICAL)

			# sizer.Add(canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
			#self.SetSizerAndFit(sizer)
			# self.Fit()
			
			# #Add the canvas to the sizer
			# sizer = wx.BoxSizer(wx.VERTICAL)
			# parent.addToSizer(sizer, canvas, 1, "wx.LEFT|wx.TOP|wx.GROW", 5)
			#parent.SetSizerAndFit(sizer)

		# def draw(self, xData, yData = None):
		# 	"""Draws on the canvas.
		# 	Not meant to be inherited by the Window class, but used by it instead.

		# 	yData (list) - The y-axis location of each point. [y1, y2, y3, y4, y5, ..., yn]
		# 	xData (list) - The x-axis location of each point. [x1, x2, x3, x4, x5, ..., xn].

		# 	Example Input: draw([7.0, 5.0, 4.5, 3.0], [9.0, 10.5, 11.0, 12.5])
		# 	Example Input: draw([9.0, 10.5, 11.0, 12.5])
		# 	"""

		# 	#Determine how to plot the data
		# 	if (yData != None):
		# 		self.subplot.plot(xData, yData)
		# 	else:
		# 		self.subplot.plot(xData)
		
		def addGraph(self, sizerNumber, xData, yData = None, myLabel = None, xLength = 5.0, yLength = 4.0, title = "MatPlotLib Figure", titleSize = 12, dpi = 100, wizardPageNumber = None):
			"""Adds a matplotlib figure to a sizer.

			sizerNumber (int)       - The number of the sizer that this will be added to
			yData (list)            - The y-axis location of each point. [y1, y2, y3, y4, y5, ..., yn]
			xData (list)            - The x-axis location of each point. [x1, x2, x3, x4, x5, ..., xn].
									  If not given, the yData is interpreted as the xData and the yData is a list of incrementing integers starting at 1
			myLabel (str)           - What this is called in the idCatalogue
			xLength (float)         - The width of the plot
			yLength (float)         - The height of the plot
			title (str)             - The title for the plot
			titleSize (int)         - The font size for the plot title
			dpi (int)               - The pixels per inch count for the plot
			wizardFrameNumber (int) - The number of the wizard page. If None, it assumes either a frame or a panel

			Example Input: addGraph(0, [7.0, 5.0, 4.5, 3.0], [9.0, 10.5, 11.0, 12.5])
			Example Input: addGraph(0, [9.0, 10.5, 11.0, 12.5])
			Example Input: addGraph(0, [7.0, 5.0, 4.5, 3.0], [9.0, 10.5, 11.0, 12.5], 7.0, 6.0)
			Example Input: addGraph(0, [7.0, 5.0, 4.5, 3.0], [9.0, 10.5, 11.0, 12.5], title = "Lorem Ipsum")
			"""
			
			#Determine if a specific id should be set
			if (myLabel != None):
				myId = self.newId(myLabel)
			else:
				myId = self.newId()
				
			#Which sizer is being used?
			sizer, panelNumber = self.getSizer(sizerNumber, returnPanel = True)

			#Determine if it is a wizard or not
			if (wizardPageNumber != None):
				exec("identity = self.m_wizPage" + str(wizardPageNumber))

			#Determine if it is a panel or not
			elif (panelNumber != None):
				identity = self.getPanel(panelNumber)

			#It must be the frame then
			else:
				identity = self

			#Make the canvas panel
			plotSizer = wx.BoxSizer(wx.VERTICAL)
			canvas = GUI.CanvasPanel(identity, plotSizer)
			self.nestSizerInSizer(plotSizer, sizer)

			#Draw on that canvas
			canvas.draw(xData, yData)



			# plotSizer = wx.BoxSizer(wx.VERTICAL)
			# #self.catalogueSizer("-2", plotSizer)
			# #plotPanel = self.makePanel("-2", size = (xSize, ySize), tabTraversal = tabTraversal)

			# plotSizer.Add(self.canvas, 1, wx.ALL|wx.GROW)
			# #mainSizer.Add(mainPanel, 1, wx.ALL|wx.GROW)
			# self.SetSizerAndFit(plotSizer)



			#Add the canvas to the sizer
			#self.nestPanelInSizer(self.canvas, sizer)
			#self.addToSizer(sizer, self.canvas, 1, "wx.LEFT|wx.TOP|wx.GROW", 5)

			self.addToId(canvas, myLabel)

	class Tables():
		"""Editable tables that can connect to excel."""

		def __init__(self, title = "Example"):
			"""Defines the internal variables needed to run.

			Example Input: Tables()
			Example Input: Tables("Lorem Ipsum")
			"""

			pass
			#self.tableDict = {}

		def getTable(self, tableNumber):
			"""Returns a panel splitter when given the splitter's index number.

			tableNumber (int) - The index number of the table

			Example Input: getTable(0)
			"""

			table = self.tableDict[tableNumber][0]
			return table

		def addTable(self, nRows, nColumns, sizerNumber, tableNumber, flags = "c1", contents = None, gridLabels = [[],[]], toolTips = None, myLabel = None, 
			rowSize = None, columnSize = None, rowLabelSize = None, columnLabelSize = None, rowSizeMinimum = None, columnSizeMinimum = None,

			showGrid = True, arrowKeyMove = True, dragableRows = False, dragableColumns = False, flex = 0, readOnly = False, default = (0, 0),

			preEditFunction = None, preEditFunctionArgs = None, preEditFunctionKwargs = None, 
			postEditFunction = None, postEditFunctionArgs = None, postEditFunctionKwargs = None, 
			dragFunction = None, dragFunctionArgs = None, dragFunctionKwargs = None, 
			selectManyFunction = None, selectManyFunctionArgs = None, selectManyFunctionKwargs = None, 
			selectSingleFunction = None, selectSingleFunctionArgs = None, selectSingleFunctionKwargs = None, 
			rightClickCellFunction = None, rightClickCellFunctionArgs = None, rightClickCellFunctionKwargs = None, 
			rightClickLabelFunction = None, rightClickLabelFunctionArgs = None, rightClickLabelFunctionKwargs = None, 

			wizardPageNumber = None):

			"""Adds a table to the next cell on the grid. 
			If enabled, it can be edited; the column &  sizerNumber, size can be changed.
			To get a cell value, use: myGridId.GetCellValue(row, column).
			For a deep tutorial: http://www.blog.pythonlibrary.org/2010/03/18/wxpython-an-introduction-to-grids/

			nRows (int)       - The number of rows the table has
			nColumns (int)    - The number of columns the table has
			sizerNumber (int) - The number of the sizer that this will be added to
			tableNumber (int) - The table catalogue number for this new table
			flags (list)      - A list of strings for which flag to add to the sizer
			contents (list)   - Either a 2D list [[row], [column]] or a numpy array that contains the contents of each cell. If None, they will be blank.
			gridLabels (str)  - The labels for the [[rows], [columns]]. If not enough are provided, the resst will be capital letters.
			toolTips (list)   - The coordinates and message for all the tool tips. [[row, column, message], [row, column, message], ...]
			myLabel (str)     - What this is called in the idCatalogue
			
			rowSize (str)         - The height of the rows. 'None' will make it the default size
			columnSize (str)      - The width of the columns. 'None' will make it the default size
			rowLabelSize (int)    - The width of the row labels. 'None' will make it the default size
			columnLabelSize (int) - The height of the column labels. 'None' will make it the default size
			rowSizeMinimum (str)         - The minimum height for the rows. 'None' will make it the default size
			columnSizeMinimum (str)      - The minimum width for the columns. 'None' will make it the default size
			
			showGrid (bool)        - If True: the grid lines will be visible
			arrowKeyMove (bool)    - If True: the grid can be traversed using the arrow keys
			dragableRows (bool)    - If True: The user can drag the row lines of the cells
			dragableColumns (bool) - If True: The user can drag the column lines of the cells
			readOnly (bool)        - If True: The user will not be able to edit the cells. If an edit function is provided, this cell will be ignored
			default (tuple)        - Which cell the table starts out with selected. (row, column)

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

			Example Input: addTable(3, 4, 0, 0)
			Example Input: addTable(3, 4, 0, 0, contents = [[1, 2, 3], [a, b, c], [4, 5, 6], [d, e, f]])
			Example Input: addTable(3, 4, 0, 0, contents = myArray)
			"""
			
			#Determine if a specific id should be set
			if (myLabel != None):
				myId = self.newId(myLabel)
			else:
				myId = self.newId()

			#Which sizer is being used?
			sizer, panelNumber = self.getSizer(sizerNumber, returnPanel = True)

			#Determine if it is a wizard or not
			if (wizardPageNumber != None):
				exec("identity = self.m_wizPage" + str(wizardPageNumber))

			#Determine if it is a panel or not
			if (panelNumber != None):
				identity = self.getPanel(panelNumber)

			#It must be the frame then
			else:
				identity = self
		
			#Create the thing to put in the grid
			thing = wx.grid.Grid(identity, myId, wx.DefaultPosition, wx.DefaultSize, 0)
			thing.SetDefaultCellAlignment(wx.ALIGN_LEFT, wx.ALIGN_TOP)
			thing.CreateGrid(nRows, nColumns)

			##Grid Enabling
			if (readOnly):
				thing.EnableCellEditControl(False)
			if ((preEditFunction != None) or (postEditFunction != None)):
				thing.EnableEditing(True)
			if (showGrid):
				thing.EnableGridLines(True)

			##Grid Dragables
			if (dragableColumns):
				thing.EnableDragColSize(True)
			else:
				thing.EnableDragColMove(False)  

			if (dragableColumns or dragableRows):
				thing.EnableDragGridSize(True)
			thing.SetMargins(0, 0)

			if (dragableRows):
				thing.EnableDragRowSize(True)
			else:
				thing.EnableDragRowSize(True)
			
			##Row and Column Sizes
			if (rowSize != None):
				for i in range(nRows):
					thing.SetRowSize(i, rowSize)

			if (columnSize != None):
				for i in range(nColumns):
					thing.SetColSize(i, columnSize)         

			if (rowLabelSize != None):
				thing.SetRowLabelSize(rowLabelSize)

			if (columnLabelSize != None):
				thing.SetColLabelSize(columnLabelSize)

			##Minimum Sizes
			if (rowSizeMinimum != None):
				thing.SetRowMinimalAcceptableWidth(rowSizeMinimum)
			
			if (columnSizeMinimum != None):
				thing.SetColMinimalAcceptableWidth(columnSizeMinimum)

			##Grid Alignments
			thing.SetColLabelAlignment(wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
			thing.SetRowLabelAlignment(wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)

			##Grid Values
			for i in range(len(gridLabels[1])):
				thing.SetColLabelValue(i, str(colLabels[i]))

			for i in range(len(gridLabels[0])):
				thing.SetRowLabelValue(i, str(colLabels[i]))

			##Populate Given Cells
			if (contents != None):
				for row in range(len(contents)):
					for col in range(len(contents[0])):
						thing.SetCellValue(row, col, contents[row][col])

			##Default Cell Selection
			if ((default != None) and (default != (0, 0))):
				thing.GoToCell(default[0], default[1])

			#Configure Flags            
			flags, position, border = self.getItemMod(flags)

			#Add it to the grid
			self.addToSizer(sizer, thing, flex, flags, 5)

			#Bind the function(s)
			if (preEditFunction != None):
				self.betterBind(wx.grid.EVT_GRID_CELL_CHANGING, thing, preEditFunction, preEditFunctionArgs, preEditFunctionKwargs)
			if (postEditFunction != None):
				self.betterBind(wx.grid.EVT_GRID_CELL_CHANGED, thing, postEditFunction, postEditFunctionArgs, postEditFunctionKwargs)
			
			if (dragFunction != None):      
				self.betterBind(wx.grid.EVT_GRID_COL_SIZE, thing, dragFunction, dragFunctionArgs, dragFunctionKwargs)
				self.betterBind(wx.grid.EVT_GRID_ROW_SIZE, thing, dragFunction, dragFunctionArgs, dragFunctionKwargs)
			if (selectManyFunction != None):
				self.betterBind(wx.grid.EVT_GRID_RANGE_SELECT, thing, selectManyFunction, selectManyFunctionArgs, selectManyFunctionKwargs)
			if (selectSingleFunction != None):
				self.betterBind(wx.grid.EVT_GRID_SELECT_CELL, thing, [self.onSelectCell, selectSingleFunction], [None, selectSingleFunctionArgs], [None, selectSingleFunctionKwargs])
			else:
				self.betterBind(wx.grid.EVT_GRID_SELECT_CELL, thing, self.onSelectCell, selectSingleFunctionArgs, selectSingleFunctionKwargs)
			
			if (rightClickCellFunction != None):
				self.betterBind(wx.grid.EVT_GRID_CELL_RIGHT_CLICK, thing, rightClickCellFunction, rightClickCellFunctionArgs, rightClickCellFunctionKwargs)
			if (rightClickLabelFunction != None):
				self.betterBind(wx.grid.EVT_GRID_CELL_RIGHT_CLICK, thing, rightClickLabelFunction, rightClickLabelFunctionArgs, rightClickLabelFunctionKwargs)

			if (toolTips != None):
				self.betterBind(wx.EVT_MOTION, thing, self.onTableDisplayToolTip, toolTips)
			if (arrowKeyMove):
				self.betterBind(wx.EVT_KEY_DOWN, thing, self.onTableArrowKeyMove)

			#Catalogue Table
			self.catalogueTable(tableNumber, thing)

			#Add object to idCatalogue
			self.addToId(thing, myLabel)

		def appendRow(self, tableNumber, numberOf = 1, updateLabels = True):
			"""Adds one or more new rows to the bottom of the grid.
			The top-left corner is row (0, 0) not (1, 1).

			tableNumber (int) - What the table is called in the table catalogue
			numberOf (int)      - How many rows to add
			updateLabels (bool) - If True: The row labels will update

			Example Input: appendRow(0)
			Example Input: appendRow(0, 5)
			"""

			#Get the table object
			thing = self.getTable(tableNumber)

			thing.AppendRows(numberOf, updateLabels)

		def appendColumn(self, tableNumber, numberOf = 1, updateLabels = True):
			"""Adds one or more new columns to the right of the grid.
			The top-left corner is row (0, 0) not (1, 1).

			tableNumber (int) - The table catalogue number for this table
			numberOf (int)      - How many columns to add
			updateLabels (bool) - If True: The row labels will update

			Example Input: appendColumn(0)
			Example Input: appendColumn(0, 5)
			"""

			#Get the table object
			thing = self.getTable(tableNumber)

			thing.AppendCols(numberOf, updateLabels)

		def enableTableEditing(self, tableNumber, row = -1, column = -1):
			"""Allows the user to edit the table.

			tableNumber (int) - What the table is called in the table catalogue
			row (int)         - Which row this applies to
			col (int)         - Which column this applies to
				If both 'row' and 'column' are -1, the whole table will diabled
				If both 'row' and 'column' are given, that one cell will be disabled
				If 'row' is given and 'column is -1', that one row will be disabled
				If 'row' is -1 and 'column' is given, that one column will be disabled


			Example Input: enableTableEditing(0)
			Example Input: enableTableEditing(0, row = 0)
			Example Input: enableTableEditing(0, column = 0)
			Example Input: enableTableEditing(0, row = 0, column = 0)
			"""

			#Get the table object
			thing = self.getTable(tableNumber)

			#Determine if only 1 cell will be changed
			if ((row != -1) and (column != -1)):
				thing.SetReadOnly(row, column, False)

			elif ((row == -1) and (column == -1)):
				thing.EnableEditing(True)

			elif (row != -1):
				numberOfColumns = thing.GetNumberCols()
				for i in range(numberOfColumns):
					thing.SetReadOnly(row, i, False)

			elif (column != -1):
				numberOfRows = thing.GetNumberRows()
				for i in range(numberOfRows):
					thing.SetReadOnly(i, column, False)

		def disableTableEditing(self, tableNumber, row = -1, column = -1):
			"""Allows the user to edit the table.

			tableNumber (int) - What the table is called in the table catalogue
			row (int)         - Which row this applies to
			col (int)         - Which column this applies to
				If both 'row' and 'column' are -1, the whole table will diabled
				If both 'row' and 'column' are given, that one cell will be disabled
				If 'row' is given and 'column is -1', that one row will be disabled
				If 'row' is -1 and 'column' is given, that one column will be disabled

			Example Input: disableTableEditing(0)
			Example Input: disableTableEditing(0, row = 0)
			Example Input: disableTableEditing(0, column = 0)
			Example Input: disableTableEditing(0, row = 0, column = 0)
			"""

			#Get the table object
			thing = self.getTable(tableNumber)

			#Determine if only 1 cell will be changed
			if ((row != -1) and (column != -1)):
				thing.SetReadOnly(row, column)

			elif ((row == -1) and (column == -1)):
				thing.EnableEditing(False)

			elif (row != -1):
				numberOfColumns = thing.GetNumberCols()
				for i in range(numberOfColumns):
					thing.SetReadOnly(row, i)

			elif (column != -1):
				numberOfRows = thing.GetNumberRows()
				for i in range(numberOfRows):
					thing.SetReadOnly(i, column)

		def clearTable(self, tableNumber):
			"""Clears all cells in the table

			tableNumber (int) - What the table is called in the table catalogue

			Example Input: clearTable( 0)
			"""

			#Get the table object
			thing = self.getTable(tableNumber)
			thing.ClearGrid()

		def setTableCursor(self, row, column, tableNumber, readOnly = False):
			"""Moves the table highlight cursor to the given cell coordinates
			The top-left corner is row (0, 0) not (1, 1).

			row (int)         - The index of the row
			column (int)      - The index of the column
			tableNumber (int) - What the table is called in the table catalogue
			readOnly (bool)   - If True: The user cannot edit this cell
				If a cell was already readOnly, and it is set to not be, it will no longer be readOnly.

			Example Input: setTableCursor(1, 2, 0)
			"""

			#Get the table object
			thing = self.getTable(tableNumber)

			#Set the cell value
			thing.GoToCell(row, column)

			if(readOnly):
				thing.SetReadOnly(row, column)
			else:
				thing.SetReadOnly(row, column, False)

		def setTableCell(self, row, column, value, tableNumber, readOnly = False, noneReplace = True):
			"""Writes something to a cell.
			The top-left corner is row (0, 0) not (1, 1).

			row (int)         - The index of the row
			column (int)      - The index of the column
			value (any)       - What will be written to the cell.
			value (array)     - What will be written in the group of cells with the row nad column being the top-left coordinates. Can be a 2D list
			tableNumber (int) - What the table is called in the table catalogue
			readOnly (bool)   - If True: The user cannot edit this cell
				If a cell was already readOnly, and it is set to not be, it will no longer be readOnly.
			noneReplace (bool) - Determines what happens if the user gives a value of None for 'value'.
				- If True: Will replace the cell with ""
				- If False: Will not replace the cell

			Example Input: setTableCell(1, 2, 42, 0)
			Example Input: setTableCell(1, 2, 3.14, 0)
			Example Input: setTableCell(1, 2, "Lorem Ipsum", 0)
			"""

			#Get the table object
			thing = self.getTable(tableNumber)

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
			thing.SetCellValue(row, column, value)

			if(readOnly):
				thing.SetReadOnly(row, column)
			else:
				thing.SetReadOnly(row, column, False)

		def getTableCellValue(self, row, column, tableNumber, readOnly = False):
			"""Reads something in a cell.
			The top-left corner is row (0, 0) not (1, 1).

			row (int)         - The index of the row
			column (int)      - The index of the column
			tableNumber (int) - What the table is called in the table catalogue
			readOnly (bool)   - If True: The user cannot edit this cell
				If a cell was already readOnly, and it is set to not be, it will no longer be readOnly.

			Example Input: getTableCellValue(1, 2, 0)
			"""

			#Get the table object
			thing = self.getTable(tableNumber)

			#Get the cell value
			value = thing.GetCellValue(row, column)

			if(readOnly):
				thing.SetReadOnly(row, column)
			else:
				thing.SetReadOnly(row, column, False)

			return value

		def getTableCurrentCell(self, tableNumber, readOnly = False):
			"""Returns the row and column of the currently selected cell.
			The top-left corner is row (0, 0) not (1, 1).

			tableNumber (int) - What the table is called in the table catalogue
			readOnly (bool)   - If True: The user cannot edit this cell
				If a cell was already readOnly, and it is set to not be, it will no longer be readOnly

			Example Input: getTableCurrentCellValue(0)
			"""

			#Get the table object
			thing = self.getTable(tableNumber)

			selection = thing.GetSelectedCells()

			#Get the selected cell's coordinates
			if not selection:
				row, column = self.tableDict[tableNumber][1]
			else:
				row = selection[0]
				column = selection[1]

			#Apply readOnly rules
			if(readOnly):
				thing.SetReadOnly(row, column)
			else:
				thing.SetReadOnly(row, column, False)

			return (row, column)

		def getTableCurrentCellValue(self, tableNumber, readOnly = False):
			"""Reads something from rhe currently selected cell.
			The top-left corner is row (0, 0) not (1, 1).

			tableNumber (int) - What the table is called in the table catalogue
			readOnly (bool)   - If True: The user cannot edit this cell
				If a cell was already readOnly, and it is set to not be, it will no longer be readOnly.

			Example Input: getTableCurrentCellValue(0)
			"""

			#Get the table object
			thing = self.getTable(tableNumber)

			#Get the selected cell's coordinates
			row, column = self.getTableCurrentCell(tableNumber, readOnly)

			#Get the currently selected cell's value
			value = thing.GetCellValue(row, column)

			return value

		def getTablePreviousCell(self, tableNumber, readOnly = False):
			"""Returns the row and column of the previously selected cell.
			The top-left corner is row (0, 0) not (1, 1).

			tableNumber (int) - What the table is called in the table catalogue
			readOnly (bool)   - If True: The user cannot edit this cell
				If a cell was already readOnly, and it is set to not be, it will no longer be readOnly

			Example Input: getTablePreviousCellValue(0)
			"""

			#Get the table object
			thing = self.getTable(tableNumber)

			selection = thing.GetSelectedCells()

			#Get the selected cell's coordinates
			if not selection:
				row, column = self.tableDict[tableNumber][2]
			else:
				### Not Working Yet
				print("WARNING: Previous selection of ranges is not currently working")
				row = selection[0]
				column = selection[1]

			#Apply readOnly rules
			if(readOnly):
				thing.SetReadOnly(row, column)
			else:
				thing.SetReadOnly(row, column, False)

			return (row, column)

		def getTablePreviousCellValue(self, tableNumber, readOnly = False):
			"""Reads something from the previously selected cell.
			The top-left corner is row (0, 0) not (1, 1).

			tableNumber (int) - What the table is called in the table catalogue
			readOnly (bool)   - If True: The user cannot edit this cell
				If a cell was already readOnly, and it is set to not be, it will no longer be readOnly.

			Example Input: getTablePreviousCellValue(0)
			"""

			#Get the table object
			thing = self.getTable(tableNumber)

			#Get the selected cell's coordinates
			row, column = self.getTablePreviousCell(tableNumber, readOnly)

			#Get the currently selected cell's value
			value = thing.GetCellValue(row, column)

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

			#Get the table object
			thing = self.getTable(tableNumber)

			#Set the cell value
			thing.SetRowLabelValue(row, rowLabel)

		def setTableColumnLabel(self, column, columnLabel, tableNumber):
			"""Changes a row's tableNumber.
			The top-left corner is row (0, 0) not (1, 1).

			column (int)      - The index of the row
			columnLabel (str) - The new tableNumber for the row
			tableNumber (int) - What the table is called in the table catalogue

			Example Input: setTableColumnLabel(1, "Column 1", 0)
			"""

			#Ensure correct data type
			if (type(columnLabel) != str):
				columnLabel = str(columnLabel)

			#Get the table object
			thing = self.getTable(tableNumber)

			#Set the cell value
			thing.SetColLabelValue(column, columnLabel)

		def setTableCellFormat(self, row, column, format, tableNumber):
			"""Changes the color of the text in a cell.
			The top-left corner is row (0, 0) not (1, 1).

			row (int)         - The index of the row
			column (int)      - The index of the column
			format (str)      - The format for the cell
									~ "float" - floating point
			tableNumber (int) - What the table is called in the table catalogue

			Example Input: setTableCellFormat(1, 2, "float", 0)
			"""

			#Get the table object
			thing = self.getTable(tableNumber)

			#Set the cell format
			if (format == "float"):
				thing.SetCellFormatFloat(row, column, width, percision)

		def setTableCellFont(self, row, column, font, tableNumber, italic = False, bold = False):
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

			#Get the table object
			thing = self.getTable(tableNumber)

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

			thing.SetCellFont(row, column, font)

		######################## FIX THIS #######################
		def setTableMods(self, row, column, font, tableNumber, italic = False, bold = False):
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

			#Get the table object
			thing = self.getTable(tableNumber)

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

			thing.SetCellFont(row, column, font)

			fixedFlags, position, border = self.getItemMod(flags)
		#########################################################

		def hideTableRow(self, row, tableNumber):
			"""Hides a row in a grid.
			The top-left corner is row (0, 0) not (1, 1).

			row (int)         - The index of the row
			tableNumber (int) - What the table is called in the table catalogue

			Example Input: hideTableRow(1, 0)
			"""

			#Get the table object
			thing = self.getTable(tableNumber)

			# thing.SetRowLabelSize(0) # hide the rows
   #        grid.SetColLabelSize(0) # hide the columns

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

			#Get the table object
			thing = self.getTable(tableNumber)

			#Set the text color
			thing.SetCellTextColour(row, column, color)

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

			#Get the table object
			thing = self.getTable(tableNumber)

			#Set the text color
			thing.SetCellBackgroundColour(row, column, color)

		def autoTableSize(self, tableNumber, autoRow = True, autoColumn = True, setAsMinimum = True):
			"""Sizes the rows and columns to fit all of their contents.
			What is autosizing can be toggled on and off.

			autoRow (bool)      - If True: Rows will be resized
			autoColumn (bool)   - If True: Columns will be resized
			setAsMinimum (bool) - If True: The calculated sizes will be set as the minimums
								  Note: In order to set for only rows, call this function once for all but rows with this toggled off, and then a second time for the rest.

			Example Input: autoTableSize(0)
			Example Input: autoTableSize(0, autoColumn = False)
			Example Input: autoTableSize(0, autoRow = False, setAsMinimum = False)
			"""

			#Get the table object
			thing = self.getTable(tableNumber)

			#Size Gid
			if (autoRow):
				thing.AutoSizeRows(setAsMinimum)

			if (autoColumn):
				thing.AutoSizeColumns(setAsMinimum)

		def autoTableSizeRow(self, row, tableNumber, setAsMinimum = True):
			"""Sizes the a single row to fit its contents.
			What is autosizing can be toggled on and off.

			row (int)           - The row that will be autosized
			setAsMinimum (bool) - If True: The calculated sizes will be set as the minimums
								  
			Example Input: autoTableSizeRow(3, 0)
			Example Input: autoTableSizeRow(4, 0, setAsMinimum = False)
			"""

			#Get the table object
			thing = self.getTable(tableNumber)

			#Size Row
			thing.AutoSizeRow(row, setAsMinimum)

		def autoTableSizeColumn(self, column, tableNumber, setAsMinimum = True):
			"""Sizes the a single column to fit its contents.
			What is autosizing can be toggled on and off.

			column (int)        - The column that will be autosized
			setAsMinimum (bool) - If True: The calculated sizes will be set as the minimums
								  
			Example Input: autoTableSizeColumn(3, 0)
			Example Input: autoTableSizeColumn(4, 0, setAsMinimum = False)
			"""

			#Get the table object
			thing = self.getTable(tableNumber)

			#Size Row
			thing.AutoSizeColumn(column, setAsMinimum)

		def autoTableSizeRowLabel(self, row, tableNumber, setAsMinimum = True):
			"""Sizes the a single row to fit the height of the row label.

			row (int)           - The row that will be autosized
											  
			Example Input: autoSizeRowLabel(3, 0)
			"""

			#Get the table object
			thing = self.getTable(tableNumber)

			#Size Row
			thing.AutoSizeRowLabelSize(row)

		def autoTableSizeColumnLabel(self, column, tableNumber):
			"""Sizes the a single column to fit the width of the column label.

			column (int) - The column that will be autosized
								 
			Example Input: autoTableSizeColumnLabel(3, 0)
			"""

			#Get the table object
			thing = self.getTable(tableNumber)

			#Size Row
			thing.AutoSizeColumnLabelSize(column)

		def setTableRowSize(self, row, size, tableNumber):
			"""Changes the height of a row.

			row (int) - The index of the row
			size (int) - The new height of the row in pixels
			tableNumber (int) - What the table is called in the table catalogue

			Example Input: setTableRowSize(3, 15, 0)
			"""

			#Get the table object
			thing = self.getTable(tableNumber)

			#Set the text color
			thing.SetRowSize(row, size)

		def setTableColumnSize(self, column, size, tableNumber):
			"""Changes the width of a column.

			column (int) - The index of the column
			size (int) - The new height of the column in pixels
			tableNumber (int) - What the table is called in the table catalogue

			Example Input: setTableColumnSize(3, 15, 0)
			"""

			#Get the table object
			thing = self.getTable(tableNumber)

			#Set the text color
			thing.SetColSize(column, size)

		def setTableRowSizeDefaults(self, tableNumber):
			"""Restores the default heights to all rows.

			tableNumber (int) - What the table is called in the table catalogue

			Example Input: setTableRowSizeDefaults(0)
			"""

			#Get the table object
			thing = self.getTable(tableNumber)

			#Set the text color
			thing.SetRowSizes(wx.grid.GridSizesInfo)

		def setTableColumnSizeDefaults(self, tableNumber):
			"""Restores the default widths to all columns.

			tableNumber (int) - What the table is called in the table catalogue

			Example Input: setTableColumnSizeDefaults(0)
			"""

			#Get the table object
			thing = self.getTable(tableNumber)

			#Set the text color
			thing.SetColSizes(wx.grid.GridSizesInfo)

	class Icons():
		"""Used to make the resulting .exe file have a specific icon file."""

		def __init__(self):
			"""Does nothing. This is here to comply with PEP 8 standards.

			Example Input: Meant to be inherited by GUI().
			"""

			pass

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
			self.SetIcon(myIcon)

	class Panel(wx.Panel):
		"""A panel for a window.
		Not meant to be inherited by the Window class, but used by it instead.

		xSize (int)  - The length of the panel
		ySize (int)  - The height of the panel
		border (str) - What style the border has. "simple", "raised", "sunken" or "none". Only the first two letters are necissary
		flags (list)        - A list of strings for which flag to add to the sizer
		
		tabTraversal (bool)   - If True: Pressing [tab] will move the cursor to the next widget
		useDefaultSize (bool) - If True: The xSize and ySize will be overridden to fit as much of the widgets as it can. Will lock the panel size from re-sizing
		_________________________________________________________________________

		TAB TRAVERSAL ORDER
		The widget order is in the order which the widget was created.
		If another window or panel is clicked on, tab traversal is used, etc. and then the user goes back to the previous window,
		then the tab order will resume from where it left off (unless you use a notebook).

		EXLUDING A WIDGET FROM TAB TRAVERSAL
		This is not currently supported.
		_________________________________________________________________________
		"""

		def __init__(self, parent, xSize = wx.DefaultSize[0], ySize = wx.DefaultSize[1], myLabel = None, border = wx.NO_BORDER, myId = wx.ID_ANY, 
			position = wx.DefaultPosition, tabTraversal = True, useDefaultSize = False, autoSize = True, flags = "c1"):
			"""Creates the panel

			Example Input: Panel(parent, 200, 300)
			Example Input: Panel(parent, border = "raised")
			Example Input: Panel(parent, useDefaultSize = True)
			Example Input: Panel(parent, tabTraversal = False)
			"""
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
					print("ERROR: border " + border + "does not exist.")

			#Determine size
			if (useDefaultSize):
				size = wx.DefaultSize
			else:
				size = (xSize, ySize)

			#Get Attributes
			flags, x, y = GUI.Sizers.getItemMod(self, flags, False, None)

			if (tabTraversal):
				flags += "|wx.TAB_TRAVERSAL"

			#Create the panel
			wx.Panel.__init__(self, parent, myId, position, size, eval(str(border) + "|" + flags))

			#Internal variables
			self.autoSize = autoSize

		def updateWindow(self, autoSize = True, wizardPageNumber = None):
			"""Overload function for updateWindow() in the sizer class."""

			GUI.Window.updateWindow(self, autoSize, wizardPageNumber)

	class CanvasPanel(wx.Panel):
		"""A canvas panel for a window. Used to make graphs.
		Not meant to be inherited by the Window class, but used by it instead.
		Modified code from Chris Baker on: https://wiki.wxpython.org/DoubleBufferedDrawing

		Note: The coordinate system starts at (0, 0) in the top-left corner.
		"""

		def __init__(self, parent, panel = None, xSize = wx.DefaultSize[0], ySize = wx.DefaultSize[1], myLabel = None, border = wx.NO_BORDER,
			myId = wx.ID_ANY, position = wx.DefaultPosition, tabTraversal = True, useDefaultSize = False, flags = "c1"):
			"""Creates the canvas.

			Example Input: CanvasPanel(self)
			"""

			#Create internal variables
			self.drawQueue = [] #What will be drawn on the window. Items are drawn from left to right in their list order. [function, args, kwargs]
			self.parent = parent

			#Determine Style
			style = border

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
					print("ERROR: border " + border + "does not exist.")

			#Determine size
			if (useDefaultSize):
				size = wx.DefaultSize
			else:
				size = (xSize, ySize)

			#Get Attributes
			flags, x, y = parent.getItemMod(flags, False, None)

			if (tabTraversal):
				flags += "|wx.TAB_TRAVERSAL"

			#Ensure things draw correctly
			flags += "|wx.NO_FULL_REPAINT_ON_RESIZE"

			#Create the panel
			# classType = panel.GetClassName()
			# if ((panel != None) and (classType == "wxPanel")):
			# 	identity = panel
			# else:
			# 	identity = self
			wx.Panel.__init__(self, panel, myId, position, size, eval(str(border) + "|" + flags))

			#Enable painting
			parent.betterBind(wx.EVT_PAINT, self, self.onPaint)
			parent.betterBind(wx.EVT_SIZE, self, self.onSize)

			#onSize called to make sure the buffer is initialized.
			#This might result in onSize getting called twice on some platforms at initialization, but little harm done.
			self.onSize(None)
			self.paint_count = 0

		def onPaint(self, event):
			"""Needed so that the GUI can draw on the panel."""

			#All that is needed here is to draw the buffer to screen
			dc = wx.BufferedPaintDC(self, self._Buffer)

			event.Skip()

		def onSize(self, event):
			"""Needed so that the GUI can draw on the panel."""
			
			#Make sure the buffer is always the same size as the Window
			Size  = self.ClientSize
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
			self.Refresh()
			self.Update()

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
			self.Refresh()
			self.Update()

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

	class PopupWindow(wx.PopupWindow):
		"""A simple window that stays on top of all wxWindow objects.

		xSize (int)  - The length of the panel
		ySize (int)  - The height of the panel
		border (str) - What style the border has. "simple", "raised", "sunken" or "none". Only the first two letters are necissary
		useDefaultSize (bool) - If True: The xSize and ySize will be overridden to fit as much of the widgets as it can. Will lock the panel size from re-sizing        
		"""

		def __init__(self, parent, xSize = 300, ySize = 400, myLabel = None, border = wx.NO_BORDER, myId = wx.ID_ANY, position = wx.DefaultPosition, 
			useDefaultSize = False):
			"""Creates a dragable popup window.

			Example Input: PopupWindow(self)
			"""

			#Determine border
			if (type(border) == str):

				#Ensure correct caseing
				border = border.lower()

				if (border[0:2] == "si"):
					border = wx.SIMPLE_BORDER

				elif (border[0] == "r"):
					border = wx.RAISED_BORDER

				elif (border[0:2] == "su"):
					border = wx.SUNKEN_BORDER

				elif (border[0] == "n"):
					border = wx.NO_BORDER

				else:
					print("ERROR: border " + border + "does not exist.")

			#Make the window
			wx.PopupWindow.__init__(self, parent, border)

			#Determine size
			if (useDefaultSize):
				size = wx.DefaultSize
			else:
				size = (xSize, ySize)

			#Position the window
			self.Position(position, size)
		
	class Window(wx.Frame, CommonEventFunctions, Utilities, Menus, Sizers, Widgets, ErrorHandler, Tables, Icons, Plots):
		"""A simple window frame.

		title (str)   - The text at the top of the window
		myLabel (str) - What the frame is called in the idCatalogue
		xSize (int)   - The width of the window
		ySize (int)   - The height of the window
		
		initFunction (str)       - The function that is ran when the panel first appears
		initFunctionArgs (any)   - The arguments for 'initFunction'
		initFunctionKwargs (any) - The keyword arguments for 'initFunction'function

		delFunction (str)       - The function that is ran when the user tries to close the panel. Can be used to interrup closing
		delFunctionArgs (any)   - The arguments for 'delFunction'
		delFunctionKwargs (any) - The keyword arguments for 'delFunction'function

		idleFunction (str)       - The function that is ran when the window is idle. Note: If you bind an idleFunction, backgroundRun() can only run functions in new threads
		idleFunctionArgs (any)   - The arguments for 'idleFunction'
		idleFunctionKwargs (any) - The keyword arguments for 'idleFunction'function
		
		tabTraversal (bool) - If True: Hitting the Tab key will move the selected widget to the next one
		topBar (bool)       - An override for 'minimize', 'maximize', and 'close'.
			- If None: Will not override 'minimize', 'maximize', and 'close'.
			- If True: The top of the window will have a minimize, maximize, and close button.
			- If False: The top of the window will not have a minimize, maximize, and close button.
		autoSize (bool)     - If True: The window will determine the best size for itself
		panel (bool)        - If True: All content within the window will be nested inside a main panel
		icon (str)          - The file path to the icon for the window
			If None: No icon will be shown
		internal (bool)     - If True: The icon provided is an internal icon, not an external file
		debugging (bool)    - If True: Debugging information will be printed to the cmd window
		"""

		def __init__(self, parent, title = "My Program", myLabel = None, xSize = 500, ySize = 300, 
			initFunction = None, initFunctionArgs = None, initFunctionKwargs = None,
			delFunction = None, delFunctionArgs = None, delFunctionKwargs = None, 
			idleFunction = None, idleFunctionArgs = None, idleFunctionKwargs = None, 
			tabTraversal = True, stayOnTop = False, floatOnParent = False, endProgram = True,
			resize = True, minimize = True, maximize = True, close = True, topBar = True,
			panel = True , autoSize = True, icon = None, internal = False, debugging = False):
			"""Creates a window. This is the foundation for the GUI.

			Example Input: Window(None, "Example")
			Example Input: Window(None, "Example", myLabel = "mainFrame")
			"""
			super(GUI.Window, self).__init__(parent)

			#Debugging Variables
			self.debugging = debugging #If True: Prints diagnostic info to the screen

			#Initialize Inherited classes
			GUI.CommonEventFunctions.__init__(self)
			GUI.Utilities.__init__(self)
			GUI.Menus.__init__(self)
			GUI.Sizers.__init__(self)
			GUI.Widgets.__init__(self)
			GUI.ErrorHandler.__init__(self)
			GUI.Tables.__init__(self)
			GUI.Icons.__init__(self)
			GUI.Plots.__init__(self)

			#Window Variables
			self.menuDict          = {} #A dictionary that contains all the menus for this window. {menuLabel: menu}
			self.popupItemsList    = [] #A list that contains all of the items for the popup menu. [itemLabel, item function, item function args, item function kwargs]
			self.sizerDict         = {} #A dictionary that contains all of the sizers for this window. {windowNumber: [sizer, panelNumber]}
			self.panelDict         = {} #A dictionary that contains all of the panels for this window. {panelNumber: panel}
			self.splitterDict      = {} #A dictionary that contains all of the panelSplitters for this window. {splitterNumber: splitter}
			self.tableDict         = {} #A dictionary that contains all of the tables for this window. {tableNumber: [table, (current row, current column), (previous row, previous column)]}
			self.popupWindowDict   = {} #A dictionary that contains all of the popup windows for this window. {popupWindowNumber: [popupWindow, panel, textBox, {internalVariable:value}]}
			self.toolTipDict       = {} #A dictionary that contains all of the tool tips for this window. {triggerObjectLabel: toolTip}
			self.keyPressQueue     = {} #A dictionary that contains all of all the key events that need to be bound to this window
			self.canvasDict        = {} #A dictionary that contains all of the canvases for this window. {canvasLabel: canvas}
			self.finalFunctionList = [] #A list of functions to run after building; before launching the app. [myFunction, myFunctionArgs, myFunctionKwargs]
			self.idleQueue         = [] #A list of the functions to run while the GUI is idle. [myFunctionEvaluated, myFunctionArgs, myFunctionKwargs, only run if the window is shown]. If None: functions cannot be ran while the GUI is idle

			#CommonEventFunctions
			self.statusBarOn = True
			self.toolBarOn = True

			self.autoSize = autoSize

			#Utilities
			idGen = 2000 #Used to generate individual identifiers

			#Make the frame
			self.makeFrame(title, myLabel = myLabel, xSize = xSize, ySize = ySize, panel = panel, 
			initFunction = initFunction, initFunctionArgs = initFunctionArgs, initFunctionKwargs = initFunctionKwargs, 
			delFunction = delFunction, delFunctionArgs = delFunctionArgs, delFunctionKwargs = delFunctionKwargs, 
			idleFunction = idleFunction, idleFunctionArgs = idleFunctionArgs, idleFunctionKwargs = idleFunctionKwargs, 
			tabTraversal = tabTraversal, stayOnTop = stayOnTop, floatOnParent = floatOnParent, endProgram = endProgram,
			resize = resize, minimize = minimize, maximize = maximize, close = close, icon = icon, internal = internal, topBar = topBar)   

		#Windows
		def makeFrame(self, title, myLabel = None, xSize = 500, ySize = 300, panel = True, 
			initFunction = None, initFunctionArgs = None, initFunctionKwargs = None, 
			delFunction = None, delFunctionArgs = None, delFunctionKwargs = None, 
			idleFunction = None, idleFunctionArgs = None, idleFunctionKwargs = None, 
			tabTraversal = True, stayOnTop = False, floatOnParent = False, endProgram = True,
			resize = True, minimize = True, maximize = True, close = True, icon = None, internal = False, topBar = True):
			"""Makes a frame for the window.

			Example Input: makeFrame("Example")
			"""

			#Determine if a specific id should be set
			if (myLabel != None):
				myId = self.newId(myLabel)
			else:
				myId = self.newId()
			
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

			#Make the frame
			myFrame = wx.Frame.__init__(self, None, id = myId, title = title, pos = wx.DefaultPosition, size = (xSize, ySize), style = eval(flags), name = wx.FrameNameStr)
			
			#Add Properties
			if (icon != None):
				self.setIcon(icon, internal)

			#Bind functions
			if (initFunction != None):
				self.betterBind(wx.EVT_ACTIVATE, self, initFunction, initFunctionArgs, initFunctionKwargs)

			if (delFunction != None):
				self.betterBind(wx.EVT_CLOSE, self, delFunction, delFunctionArgs, delFunctionKwargs)
			else:
				if (endProgram != None):
					if (endProgram):
						delFunction = self.onExit
					else:
						delFunction = self.onQuit
				else:
					delFunction = self.onHide

				self.betterBind(wx.EVT_CLOSE, self, delFunction)


			if (idleFunction != None):
				self.idleQueue = None
				self.betterBind(wx.EVT_IDLE, self, idleFunction, idleFunctionArgs, idleFunctionKwargs)
			else:
				self.betterBind(wx.EVT_IDLE, self, self.onIdle)

			#Make the main panel
			if (panel):
				mainPanel = self.makePanel("-1", size = (10, 10), tabTraversal = tabTraversal, useDefaultSize = False)

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
			if ("-1" in self.panelDict):
				thing = self.panelDict["-1"]
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

		#Panels
		def addPanel(self, panelNumber, size = wx.DefaultSize, border = wx.NO_BORDER, myId = wx.ID_ANY, position = wx.DefaultPosition, 
			tabTraversal = True, useDefaultSize = False, myLabel = None, initFunction = None, initFunctionArgs = None, initFunctionKwargs = None):
			"""Convenience override Function for makePanel() that makes the function look like a widget function."""

			self.makePanel(panelNumber, size, border, myId, position, tabTraversal, useDefaultSize, myLabel, initFunction, initFunctionArgs, initFunctionKwargs)
		
		def makePanel(self, panelNumber, size = wx.DefaultSize, border = wx.NO_BORDER, myId = wx.ID_ANY, position = wx.DefaultPosition, 
			tabTraversal = True, useDefaultSize = False, myLabel = None, initFunction = None, initFunctionArgs = None, initFunctionKwargs = None):
			"""Creates a blank panel window.

			panelNumber (int) - The index number of the panel. -1 indicates it is the main level panel.
			size (int tuple)  - The size of the panel. (length, width)
			myLabel (str)     - What this is called in the idCatalogue
			border (str)      - What style the border has. "simple", "raised", "sunken" or "none". Only the first two letters are necissary
			
			tabTraversal (bool)   - If True: Pressing [tab] will move the cursor to the next widget
			useDefaultSize (bool) - If True: The xSize and ySize will be overridden to fit as much of the widgets as it can. Will lock the panel size from re-sizing

			initFunction (str)       - The function that is ran when the panel first appears
			initFunctionArgs (any)   - The arguments for 'initFunction'
			initFunctionKwargs (any) - The keyword arguments for 'initFunction'function

			Example Input: makePanel(0)
			"""

			#Determine if a specific id should be set
			if (myLabel != None):
				myId = self.newId(myLabel)
			else:
				myId = self.newId()
			
			#Create the thing
			panel = GUI.Panel(self, size[0], size[1], myLabel, border, myId, position, tabTraversal, useDefaultSize)

			#Bind Functions
			if (initFunction != None):
				self.betterBind(wx.EVT_INIT_DIALOG, panel, initFunction, initFunctionArgs, initFunctionKwargs)

			self.addToId(panel, myLabel)

			#Catalogue Panel
			self.cataloguePanel(panelNumber, panel)
			return panel

		def makePanelDouble(self, leftPanelNumber, rightPanelNumber, splitterNumber, sizerNumber, leftSize = wx.DefaultSize, rightSize = wx.DefaultSize, border = wx.NO_BORDER, 
			dividerSize = 1, dividerPosition = None, dividerGravity = 0.5, myId = wx.ID_ANY, position = wx.DefaultPosition, 
			horizontal = False, tabTraversal = True, minimumSize = 20, useDefaultSize = False, myLabel = None, 
			initFunction = None, initFunctionArgs = None, initFunctionKwargs = None, wizardPageNumber = None):
			"""Creates two blank panels in next to each other. 
			The border between double panels is dragable.

			leftPanelNumber (int)  - The index number of the left side panel
			rightPanelNumber (int) - The index number of the right side panel
			splitterNumber (int)   - The index number of the splitter
			sizerNumber (int)      - The index number of the sizer that this will be added to

			leftSize (int)         - The size of the left panel. (length, width)
			rightSize (int)        - The size of the right panel. (length, width)
										~ If True: 'leftPanel' is the top panel; 'rightPanel' is the bottom panel
										~ If False: 'leftPanel' is the left panel; 'rightPanel' is the right panel
			border (str)           - What style the border has. "simple", "raised", "sunken" or "none". Only the first two letters are necissary
			dividerSize (int)      - How many pixels thick the dividing line is. Not available yet
			dividerPosition (int)  - How many pixels to the right the dividing line starts after the 'minimumSize' location
										~ If None: The line will start at the 'minimumSize' value
			dividerGravity (int)   - From 0.0 to 1.1, how much the left (or top) panel grows with respect to the right (or bottom) panel upon resizing
			horizontal (bool)      - Determines the that direction the frames are split
			tabTraversal (bool)    - If True: Pressing [tab] will move the cursor to the next widget
			minimumSize (int)      - How many pixels the smaller pane must have between its far edge and the splitter.
			useDefaultSize (bool) - If True: The xSize and ySize will be overridden to fit as much of the widgets as it can. Will lock the panel size from re-sizing
			myLabel (str)          - What this is called in the idCatalogue
			
			initFunction (str)       - The function that is ran when the panel first appears
			initFunctionArgs (any)   - The arguments for 'initFunction'
			initFunctionKwargs (any) - The keyword arguments for 'initFunction'function

			Example Input: makePanelDouble(0, 1, 0)
			Example Input: makePanelDouble(0, 1, 0, horizontal = False)
			Example Input: makePanelDouble(0, 1, 0, minimumSize = 100)
			"""

			#Determine if a specific id should be set
			if (myLabel != None):
				myId = self.newId(myLabel)
			else:
				myId = self.newId()

			#Which sizer is being used?
			sizer, panelNumber = self.getSizer(sizerNumber, returnPanel = True)

			#Determine if it is a wizard or not
			if (wizardPageNumber != None):
				exec("identity = self.m_wizPage" + str(wizardPageNumber))

			#Determine if it is a panel or not
			elif (panelNumber != None):
				identity = self.getPanel(panelNumber)

			#It must be the frame then
			else:
				identity = self

			#Create the panel splitter
			splitter = wx.SplitterWindow(identity, style = wx.SP_LIVE_UPDATE)

			leftPanel = GUI.Panel(splitter, leftSize[0], leftSize[1], myLabel, border, myId, position, tabTraversal, useDefaultSize)
			rightPanel = GUI.Panel(splitter, rightSize[0], rightSize[1], myLabel, border, myId, position, tabTraversal, useDefaultSize)
			
			#Split the window
			if (horizontal):
				splitter.SplitHorizontally(leftPanel, rightPanel)
			else:
				splitter.SplitVertically(leftPanel, rightPanel)

			#Apply Properties
			##Minimum panel size
			splitter.SetMinimumPaneSize(minimumSize)

			##Divider position from the right
			if (dividerPosition != None):
				splitter.SetSashPosition(dividerPosition)
			
			##Left panel growth ratio
			splitter.SetSashGravity(dividerGravity)

			##Dividing line size
			splitter.SetSashSize(dividerSize)

			#Bind Functions
			if (initFunction != None):
				#self.Bind(wx.EVT_INIT_DIALOG, initFunction)
				self.betterBind(wx.EVT_INIT_DIALOG, splitter, initFunction, initFunctionArgs, initFunctionKwargs)

			#Catalogue Panel
			self.cataloguePanel(leftPanelNumber, leftPanel)
			self.cataloguePanel(rightPanelNumber, rightPanel)

			#Catalogue Splitter
			self.catalogueSplitter(splitterNumber, splitter)

			#Add it to the grid
			# self.nestSplitterInSizer(splitterNumber, sizerNumber)

			self.addToId(splitter, myLabel)

		def makePanelQuad(self, NEPanelNumber, NWPanelNumber, SWPanelNumber, SEPanelNumber, splitterNumber, NWSize = (500, 300), NESize = (500, 300), SWSize = (500, 300), SESize = (500, 300), border = wx.NO_BORDER, yId = wx.ID_ANY, position = wx.DefaultPosition, tabTraversal = True, useDefaultSize = False, myLabel = None, initFunction = None, initFunctionArgs = None, initFunctionKwargs = None):
			"""Creates four blank panels next to each other like a grid.
			The borders between quad panels are dragable. The itersection point is also dragable.
			Note: There is no 'minimumSize', 'dividerPosition', or 'dividerGravity' functionality like in makePanelDouble().

			NEPanelNumber (int)  - The index number of the upper right panel
			NWPanelNumber (int)  - The index number of the upper left panel
			SEPanelNumber (int)  - The index number of the lower left panel
			SWPanelNumber (int)  - The index number of the lower right panel
			splitterNumber (int) - The index number of the splitter

			NWSize (int) - The size of the upper right panel. (length, width)
			NESize (int) - The size of the upper left panel. (length, width)
			SESize (int) - The size of the lower left panel. (length, width)
			SWSize (int) - The size of the lower right panel. (length, width)
			
			border (str)          - What style the border has. "simple", "raised", "sunken" or "none". Only the first two letters are necissary
			tabTraversal (bool)   - If True: Pressing [tab] will move the cursor to the next widget
			useDefaultSize (bool) - If True: The xSize and ySize will be overridden to fit as much of the widgets as it can. Will lock the panel size from re-sizing
			myLabel (str)          - What this is called in the idCatalogue
			
			initFunction (str)       - The function that is ran when the panel first appears
			initFunctionArgs (any)   - The arguments for 'initFunction'
			initFunctionKwargs (any) - The keyword arguments for 'initFunction'function
			tabTraversal (bool)      - If True: Hitting the Tab key will move the selected widget to the next one

			Example Input: makePanelQuad(0, 1, 2, 3, 0)
			"""

			#Determine if a specific id should be set
			if (myLabel != None):
				myId = self.newId(myLabel)
			else:
				myId = self.newId()

			#Create the panel splitter
			splitter = wx.lib.agw.fourwaysplitter.FourWaySplitter(self, agwStyle = wx.SP_LIVE_UPDATE)
			
			NEPanel = GUI.Panel(splitter, xSize, ySize, myLabel, border, myId, position, tabTraversal, useDefaultSize)
			NWPanel = GUI.Panel(splitter, xSize, ySize, myLabel, border, myId, position, tabTraversal, useDefaultSize)
			SWPanel = GUI.Panel(splitter, xSize, ySize, myLabel, border, myId, position, tabTraversal, useDefaultSize)
			SEPanel = GUI.Panel(splitter, xSize, ySize, myLabel, border, myId, position, tabTraversal, useDefaultSize)
			
			##The panels should be added to the splitter in this order
			splitter.AppendWindow(NWPanel)
			splitter.AppendWindow(NEPanel)
			splitter.AppendWindow(SWPanel)
			splitter.AppendWindow(SEPanel)

			#Bind Functions
			if (initFunction != None):
				#self.Bind(wx.EVT_INIT_DIALOG, initFunction)
				self.betterBind(wx.EVT_INIT_DIALOG, splitter, initFunction, initFunctionArgs, initFunctionKwargs)

			#Catalogue Panel
			self.cataloguePanel(NEPanelNumber, NEPanel)
			self.cataloguePanel(NWPanelNumber, NWPanel)
			self.cataloguePanel(SWPanelNumber, SWPanel)
			self.cataloguePanel(SEPanelNumber, SEPanel)

			#Catalogue Splitter
			self.catalogueSplitter(splitterNumber, splitter)

			self.addToId(splitter, myLabel)

		def makePanelPoly(self, panelNumbers, splitterNumber, panelSizes = [(300, 400)], border = wx.NO_BORDER, dividerSize = 1, dividerPosition = None, dividerGravity = 0.5, myId = wx.ID_ANY, position = wx.DefaultPosition, horizontal = True, tabTraversal = True, minimumSize = 20, useDefaultSize = False, myLabel = None, initFunction = None, initFunctionArgs = None, initFunctionKwargs = None):
			"""Creates any number of panels side by side of each other.
			The borders between poly panels are dragable.

			panelNumbers (list)   - How many panels to set side by side. [1, 2, 3, 4, ..., n]
			splitterNumber (int)  - The index number of the splitter
			panelSizes (list)     - The sizes of each panel. [(x1, y1), (x2, y2), ..., (xn, yn)]. Note: The largest height will be applied to all?
			border (str)          - What style the border has. "simple", "raised", "sunken" or "none". Only the first two letters are necissary
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

			Example Input: makePanelQuad([0, 1, 2, 3], 0)
			Example Input: makePanelQuad([0, 1, 2, 3], 0, panelSizes = [(200, 300), (300, 300), (100, 300)])
			Example Input: makePanelQuad([0, 1, 2, 3], 0, horizontal = False)
			Example Input: makePanelQuad([0, 1, 2, 3], 0, minimumSize = 100)
			"""

			#Determine if a specific id should be set
			if (myLabel != None):
				myId = self.newId(myLabel)
			else:
				myId = self.newId()

			#Create the panel splitter
			splitter = wx.lib.splitter.MultiSplitterWindow(self, style = wx.SP_LIVE_UPDATE)
			
			for i in panelNumbers:
				panel = GUI.Panel(splitter, panelSizes[i][0], panelSizes[i][1], myLabel, border, myId, position, tabTraversal, useDefaultSize)
				splitter.AppendWindow(panel)

				#Catalogue Panel
				self.cataloguePanel(i, panel)

			#Apply Properties
			##Minimum panel size
			splitter.SetMinimumPaneSize(minimumSize)

			##Stack Direction
			if (horizontal):
				splitter.SetOrientation(wx.HORIZONTAL)
			else:
				splitter.SetOrientation(wx.VERTICAL)

			#Bind Functions
			if (initFunction != None):
				#self.Bind(wx.EVT_INIT_DIALOG, initFunction)
				self.betterBind(wx.EVT_INIT_DIALOG, splitter, initFunction, initFunctionArgs, initFunctionKwargs)

			#Catalogue Splitter
			self.catalogueSplitter(splitterNumber, splitter)

			self.addToId(splitter, myLabel)

		def makePopupWindow(self, popupWindowNumber, myText, size = (300, 200), border = wx.NO_BORDER, myId = wx.ID_ANY, position = wx.DefaultPosition, myLabel = None,
			tabTraversal = True, useDefaultSize = False, dragable = True, closeOnRight = True, closeOnLeave = False,
			triggerObjectLabel = None, initFunction = None, initFunctionArgs = None, initFunctionKwargs = None):
			"""Creates a customizable popup window with text.
			The top-left corner will be placed at the mouse pointer
			This code is addapted from the wxPythond demo on popup windows. http://stackoverflow.com/questions/23415125/wxpython-popup-window-bound-to-a-wxbutton

			popupWindowNumber (int)  - The index number of the panel
			myText (str)             - What the popup window will say
			size (int tuple)         - The size of the panel. (length, width)
			border (str)             - What style the border has. "simple", "raised", "sunken" or "none". Only the first two letters are necissary
			myLabel (str)            - What this is called in the idCatalogue
			
			tabTraversal (bool)   - If True: Pressing [tab] will move the cursor to the next widget
			useDefaultSize (bool) - If True: The xSize and ySize will be overridden to fit as much of the widgets as it can. Will lock the panel size from re-sizing
			dragable (bool)       - If True: The user can drag the popup window around the screen using the left mouse button
			closeOnRight (bool)   - If True: Closes the popup window on a left mouse click
			closeOnLeave (bool)   - If True: Closes the popup window when the mouse leaves the popup window. Not available yet

			triggerObjectLabel (str) - The idCatalogue label for the object that will call this popup window. 
									   If None: the user must bind the object using the function onShowPopupWindow()
			initFunction (str)       - The function that is ran when the panel first appears
			initFunctionArgs (any)   - The arguments for 'initFunction'
			initFunctionKwargs (any) - The keyword arguments for 'initFunction'function

			Example Input: makePopupWindow(0, "Lorem ipsum.\nDolor sit amet.")
			Example Input: makePopupWindow(0, "Lorem ipsum.\nDolor sit amet.", textLabel = "popupWindowText")
			Example Input: makePopupWindow(0, "Lorem ipsum.\nDolor sit amet.", size = (300, 400), border = "simple")
			"""

			#Determine if a specific id should be set
			if (myLabel != None):
				myId = self.newId(myLabel)
			else:
				myId = self.newId()
			
			#Create the popup window and its contents
			popupWindow = GUI.PopupWindow(self, size[0], size[1], myLabel, border, myId, position, useDefaultSize)

			panel = GUI.Panel(popupWindow, size[0], size[1], None, border, wx.ID_ANY, wx.DefaultPosition, tabTraversal, False)
			text = wx.StaticText(panel, -1, myText, pos = (10, 10))
			
			#Size the popup window
			bestSize = text.GetBestSize()
			popupWindow.SetSize((bestSize.width + 20, bestSize.height + 20))
			panel.SetSize((bestSize.width + 20, bestSize.height + 20))

			#Bind Functions
			if (initFunction != None):
				#self.Bind(wx.EVT_INIT_DIALOG, initFunction)
				self.betterBind(wx.EVT_INIT_DIALOG, popupWindow, initFunction, initFunctionArgs, initFunctionKwargs)

			popupWindowVariabels = {"panel": panel}
			if (dragable):

				# panel.Bind(wx.EVT_LEFT_DOWN, self.onPopupWindowMouseLeftDown)
				# text.Bind(wx.EVT_LEFT_DOWN, self.onPopupWindowMouseLeftDown)

				self.betterBind(wx.EVT_LEFT_DOWN, panel, self.onPopupWindowMouseLeftDown, 0)
				self.betterBind(wx.EVT_MOTION, panel, self.onPopupWindowMouseMotion, 0)
				self.betterBind(wx.EVT_LEFT_UP, panel, self.onPopupWindowMouseLeftUp, 0)

				self.betterBind(wx.EVT_LEFT_DOWN, text, self.onPopupWindowMouseLeftDown, 0)
				self.betterBind(wx.EVT_MOTION, text, self.onPopupWindowMouseMotion, 0)
				self.betterBind(wx.EVT_LEFT_UP, text, self.onPopupWindowMouseLeftUp), 0

				popupWindowVariabels["leftDownPosition"] = None
				popupWindowVariabels["windowPosition"] = None

			if (closeOnRight):
				self.betterBind(wx.EVT_RIGHT_UP, panel, self.onPopupWindowRightUp, 0)
				self.betterBind(wx.EVT_RIGHT_UP, text, self.onPopupWindowRightUp, 0)

			#Make the window callable
			if (triggerObjectLabel != None):
				#Bind the correct object type
				thing = self.getObjectWithLabel(triggerObjectLabel)

				##Ensure the correct event type
				thingClass = str(thing.GetClassName()) #Convert the class to a string
				thingClass = thingClass[3:] #Remove the 'wx.' from the current class
				thingClass = "wx.EVT_" + thingClass #Add the event prefix

				self.betterBind(thingClass, thing, self.onShowPopupWindow)

			wx.CallAfter(popupWindow.Refresh)

			#Catalogue popup window
			self.cataloguePopupWindow(popupWindowNumber, popupWindow, panel, text, popupWindowVariabels)

			self.addToId(popupWindow, myLabel)

		def getPanel(self, panelNumber):
			"""Returns a panel when given the panel's index number.

			panelNumber (int) - The index number of the panel

			Example Input: getPanel(0)
			"""

			#Account for the panel being given instead of the panel number
			if ((type(panelNumber) != int) and (type(panelNumber) != str)):
				panel = panelNumber
			else:
				panel = self.panelDict[panelNumber]

			return panel

		def getSplitter(self, splitterNumber):
			"""Returns a panel splitter when given the splitter's index number.

			splitterNumber (int) - The index number of the splitter

			Example Input: getSplitter(0)
			"""

			#Account for the splitter being given instead of the splitter number
			if ((type(splitterNumber) != int) and (type(splitterNumber) != str)):
				splitter = splitterNumber
			else:
				splitter = self.splitterDict[splitterNumber]
			return splitter

		def getPopupWindow(self, popupWindowNumber):
			"""Returns a popup window when given the popup window's index number.

			popupWindowNumber (int) - The index number of the popup window

			Example Input: getPopupWindow(0)
			"""

			#Account for the popup window being given instead of the popup window number
			if ((type(popupWindowNumber) != int) and (type(popupWindowNumber) != str)):
				popupWindow = popupWindowNumber
			else:
				popupWindow = self.popupWindowDict[popupWindowNumber][0]
			return popupWindow


		def getPopupWindowVariable(self, popupWindowNumber, label):
			"""Returns a popup window internal variable when given the popup window's index number.

			popupWindowNumber (int) - The index number of the popup window
			label (str)             - The label given to the popup window's internal variable catalogue

			Example Input: getPopupWindow(0, "leftDownPosition")
			"""

			try:
				value = self.popupWindowDict[popupWindowNumber][3][label]
				return value

			except:
				print("ERROR: The label", label, "does not exist in the popup window's internal variable catalogue.")
				return None

		def setPopupWindowVariable(self, popupWindowNumber, label, value):
			"""Changes a popup window internal variable when given the popup window's index number.

			popupWindowNumber (int) - The index number of the popup window
			label (str)             - The label given to the popup window's internal variable catalogue
			value (any)             - What the inetrnal variable's value is

			Example Input: getPopupWindow(0, "leftDownPosition", 250)
			"""

			try:
				self.popupWindowDict[popupWindowNumber][3][label] = value
				return True
				
			except:
				print("ERROR: The label", label, "does not exist in the popup window's internal variable catalogue.")
				return None

		def getPopupWindowText(self, popupWindowNumber):
			"""Returns a popup window's text when given the popup window's index number.

			popupWindowNumber (int) - The index number of the popup window

			Example Input: getPopupWindowText(0)
			"""

			#Get the wxStaticText object
			text = self.popupWindowDict[popupWindowNumber][2]

			#Get its value
			value = self.getObjectValue(text)
			return value

		def setPopupWindowText(self, myText, popupWindowNumber):
			"""Changes a popup window's text when given the popup window's index number.
			Used to dynamically change the popup menu's text.

			myText (str)            - What the popup window will say
			popupWindowNumber (int) - The index number of the popup window

			Example Input: getPopupWindowText(0)
			"""

			#Get the wxStaticText object
			popupWindow = self.popupWindowDict[popupWindowNumber][0]
			panel = self.popupWindowDict[popupWindowNumber][1]
			text = self.popupWindowDict[popupWindowNumber][2]

			#Change its value
			self.setObjectValue(text, myText)

			#Update window size
			bestSize = text.GetBestSize()
			popupWindow.SetSize((bestSize.width + 20, bestSize.height + 20))
			panel.SetSize((bestSize.width + 20, bestSize.height + 20))

		def getCanvas(self, canvasNumber):
			"""Returns a canvas when given the canvas's index number.

			canvasNumber (int) - The index number of the canvas

			Example Input: getCanvas(0)
			"""

			#Account for the canvas being given instead of the canvas number
			if ((type(canvasNumber) != int) and (type(canvasNumber) != str)):
				canvas = canvasNumber
			else:
				canvas = self.canvasDict[canvasNumber]
			return canvas

		#Canvas
		def addCanvas(self, canvasNumber, sizerNumber, size = wx.DefaultSize, border = wx.NO_BORDER, myId = wx.ID_ANY, position = wx.DefaultPosition, 
			tabTraversal = True, useDefaultSize = False, myLabel = None, initFunction = None, initFunctionArgs = None, initFunctionKwargs = None, wizardPageNumber = None):
			"""Creates a blank canvas window.

			canvasNumber (int) - The index number of the canvas. -1 indicates it is the main level canvas.
			size (int tuple)  - The size of the canvas. (length, width)
			myLabel (str)     - What this is called in the idCatalogue
			border (str)      - What style the border has. "simple", "raised", "sunken" or "none". Only the first two letters are necissary
			
			tabTraversal (bool)   - If True: Pressing [tab] will move the cursor to the next widget
			useDefaultSize (bool) - If True: The xSize and ySize will be overridden to fit as much of the widgets as it can. Will lock the canvas size from re-sizing

			initFunction (str)       - The function that is ran when the canvas first appears
			initFunctionArgs (any)   - The arguments for 'initFunction'
			initFunctionKwargs (any) - The keyword arguments for 'initFunction'function

			Example Input: makeCanvas(0)
			"""

			#Determine if a specific id should be set
			if (myLabel != None):
				myId = self.newId(myLabel)
			else:
				myId = self.newId()

			#Which sizer is being used?
			sizer, panelNumber = self.getSizer(sizerNumber, returnPanel = True)

			#Determine if it is a wizard or not
			if (wizardPageNumber != None):
				exec("identity = self.m_wizPage" + str(wizardPageNumber))

			#Determine if it is a panel or not
			elif (panelNumber != None):
				identity = self.getPanel(panelNumber)

			#It must be the frame then
			else:
				identity = self
			
			#Create the thing
			canvas = GUI.CanvasPanel(self, identity, size[0], size[1], myLabel, border, myId, position, tabTraversal, useDefaultSize)
			self.addToId(canvas, myLabel)

			#Bind Functions
			if (initFunction != None):
				self.betterBind(wx.EVT_INIT_DIALOG, canvas, initFunction, initFunctionArgs, initFunctionKwargs)

			#Catalogue Canvas
			self.catalogueCanvas(canvasNumber, canvas)

			self.nestPanelInSizer(canvas, sizer)


		#Wizards
		def startWizard(self, myLabel = None, xSize = 500, ySize = 300, myTitle = None, backgroundPath = None, minimize = True, maximize = True, resize = False, stayOnTop = False, help = False):
			"""Starts a wizard window.

			myLabel (str) - What this is called in the idCatalogue
			xSize (int) - The width of the window
			ySize (int) - The height of the window
			myTitle (str) - The title that shows up at the top of the wizard
			backgroundPath (str) - The location of the background of the wizard on the computer
			help (bool) - True if there should be a 'Help' button on the bottom

			Example Input: createFrame(600, 400)
			"""

			#Determine if a specific id should be set
			if (myLabel != None):
				myId = self.newId(myLabel)
			else:
				myId = self.newId()

			#Determine optitonal settings
			if (myTitle == None):
				myTitle = wx.EmptyString
			if (backgroundPath == None):
				backgroundPath = wx.NullBitmap

			#Create the thing
			if (stayOnTop):
				if (resize):
					if (maximize):
						if (minimize):
							myWizard = wx.wizard.Wizard.__init__ (self, id = myId, title = myTitle, bitmap = wx.Bitmap(backgroundPath, wx.BITMAP_TYPE_ANY), pos = wx.DefaultPosition, style = wx.DEFAULT_DIALOG_STYLE|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.RESIZE_BORDER|wx.STAY_ON_TOP)
						else:
							myWizard = wx.wizard.Wizard.__init__ (self, id = myId, title = myTitle, bitmap = wx.Bitmap(backgroundPath, wx.BITMAP_TYPE_ANY), pos = wx.DefaultPosition, style = wx.DEFAULT_DIALOG_STYLE|wx.MAXIMIZE_BOX|wx.RESIZE_BORDER|wx.STAY_ON_TOP)
					else:
						if (minimize):
							myWizard = wx.wizard.Wizard.__init__ (self, id = myId, title = myTitle, bitmap = wx.Bitmap(backgroundPath, wx.BITMAP_TYPE_ANY), pos = wx.DefaultPosition, style = wx.DEFAULT_DIALOG_STYLE|wx.MINIMIZE_BOX|wx.RESIZE_BORDER|wx.STAY_ON_TOP)
						else:
							myWizard = wx.wizard.Wizard.__init__ (self, id = myId, title = myTitle, bitmap = wx.Bitmap(backgroundPath, wx.BITMAP_TYPE_ANY), pos = wx.DefaultPosition, style = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.STAY_ON_TOP)
				else:
					if (maximize):
						if (minimize):
							myWizard = wx.wizard.Wizard.__init__ (self, id = myId, title = myTitle, bitmap = wx.Bitmap(backgroundPath, wx.BITMAP_TYPE_ANY), pos = wx.DefaultPosition, style = wx.DEFAULT_DIALOG_STYLE|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.STAY_ON_TOP)
						else:
							myWizard = wx.wizard.Wizard.__init__ (self, id = myId, title = myTitle, bitmap = wx.Bitmap(backgroundPath, wx.BITMAP_TYPE_ANY), pos = wx.DefaultPosition, style = wx.DEFAULT_DIALOG_STYLE|wx.MAXIMIZE_BOX|wx.STAY_ON_TOP)
					else:
						if (minimize):
							myWizard = wx.wizard.Wizard.__init__ (self, id = myId, title = myTitle, bitmap = wx.Bitmap(backgroundPath, wx.BITMAP_TYPE_ANY), pos = wx.DefaultPosition, style = wx.DEFAULT_DIALOG_STYLE|wx.MINIMIZE_BOX|wx.STAY_ON_TOP)
						else:
							myWizard = wx.wizard.Wizard.__init__ (self, id = myId, title = myTitle, bitmap = wx.Bitmap(backgroundPath, wx.BITMAP_TYPE_ANY), pos = wx.DefaultPosition, style = wx.DEFAULT_DIALOG_STYLE|wx.STAY_ON_TOP)
			else:
				if (resize):
					if (maximize):
						if (minimize):
							myWizard = wx.wizard.Wizard.__init__ (self, id = myId, title = myTitle, bitmap = wx.Bitmap(backgroundPath, wx.BITMAP_TYPE_ANY), pos = wx.DefaultPosition, style = wx.DEFAULT_DIALOG_STYLE|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.RESIZE_BORDER)
						else:
							myWizard = wx.wizard.Wizard.__init__ (self, id = myId, title = myTitle, bitmap = wx.Bitmap(backgroundPath, wx.BITMAP_TYPE_ANY), pos = wx.DefaultPosition, style = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)
					else:
						if (minimize):
							myWizard = wx.wizard.Wizard.__init__ (self, id = myId, title = myTitle, bitmap = wx.Bitmap(backgroundPath, wx.BITMAP_TYPE_ANY), pos = wx.DefaultPosition, style = wx.DEFAULT_DIALOG_STYLE|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.RESIZE_BORDER)
						else:
							myWizard = wx.wizard.Wizard.__init__ (self, id = myId, title = myTitle, bitmap = wx.Bitmap(backgroundPath, wx.BITMAP_TYPE_ANY), pos = wx.DefaultPosition, style = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)
				else:
					if (maximize):
						if (minimize):
							myWizard = wx.wizard.Wizard.__init__ (self, id = myId, title = myTitle, bitmap = wx.Bitmap(backgroundPath, wx.BITMAP_TYPE_ANY), pos = wx.DefaultPosition, style = wx.DEFAULT_DIALOG_STYLE|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
						else:
							myWizard = wx.wizard.Wizard.__init__ (self, id = myId, title = myTitle, bitmap = wx.Bitmap(backgroundPath, wx.BITMAP_TYPE_ANY), pos = wx.DefaultPosition, style = wx.DEFAULT_DIALOG_STYLE|wx.MAXIMIZE_BOX)
					else:
						if (minimize):
							myWizard = wx.wizard.Wizard.__init__ (self, id = myId, title = myTitle, bitmap = wx.Bitmap(backgroundPath, wx.BITMAP_TYPE_ANY), pos = wx.DefaultPosition, style = wx.DEFAULT_DIALOG_STYLE|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
						else:
							myWizard = wx.wizard.Wizard.__init__ (self, id = myId, title = myTitle, bitmap = wx.Bitmap(backgroundPath, wx.BITMAP_TYPE_ANY), pos = wx.DefaultPosition, style = wx.DEFAULT_DIALOG_STYLE)

			if (help):
				self.SetExtraStyle(wx.wizard.WIZARD_EX_HELPBUTTON)
			self.m_pages = []

			self.addToId(myWizard, myLabel)

		def endWizard(self, initFunction = None, initFunctionArgs = None, initFunctionKwargs = None, 
			delFunction = None, delFunctionArgs = None, delFunctionKwargs = None, 
			idleFunction = None, idleFunctionArgs = None, idleFunctionKwargs = None, 
			initPageFunction = None, initPageFunctionArgs = None, initPageFunctionKwargs = None, 
			cancelFunction = None, cancelFunctionArgs = None, cancelFunctionKwargs = None, 
			finishFunction = None, finishFunctionArgs = None, finishFunctionKwargs = None, 
			helpFunction = None, helpFunctionArgs = None, helpFunctionKwargs = None, 
			changedFunction = None, changedFunctionArgs = None, changedFunctionKwargs = None,):
			"""Finishes editing a wizard.

			initFunction (str)            - The function that is ran when the window first appears
			initFunctionArgs (any)        - The arguments for 'initFunction'
			initFunctionKwargs (any)      - The keyword arguments for 'initFunction'function

			delFunction (str)             - The function that is ran when the window is closed
			delFunctionArgs (any)         - The arguments for 'delFunction'
			delFunctionKwargs (any)       - The keyword arguments for 'delFunction'function

			idleFunction (str)            - The function that is ran when the window is idle
			idleFunctionArgs (any)        - The arguments for 'idleFunction'
			idleFunctionKwargs (any)      - The keyword arguments for 'idleFunction'function

			initPageFunction (str)        - The function that is ran when the a new page appears appears
			initPageFunctionArgs (any)    - The arguments for 'initPageFunction'
			initPageFunctionKwargs (any)  - The keyword arguments for 'initpageFunction'function

			cancelFunction (str)          - The function that is ran when the cancel button is pressed
			cancelFunctionArgs (any)      - The arguments for 'calcelFunction'
			cancelFunctionKwargs (any)    - The keyword arguments for 'cancelFunction'function

			finishFunction (str)          - The function that is ran when the finish button is pressed 
			finishFunctionArgs (any)      - The arguments for 'finishFunction'
			finishFunctionKwargs (any)    - The keyword arguments for 'finishFunction'function

			helpFunction (str)            - The function that is ran when the help button is pressed 
			helpFunctionArgs (any)        - The arguments for 'helpFunction'
			helpFunctionKwargs (any)      - The keyword arguments for 'helpFunction'function

			changedFunction (str)         - The function that is ran when things in the wizard are changed 
			changedFunctionArgs (any)     - The arguments for 'changedFunction'
			changedFunctionKwargs (any)   - The keyword arguments for 'changedFunction'function

			Example Input: endWizard()
			"""

			self.Centre(wx.BOTH)

			if (initFunction != None):
				self.betterBind(wx.EVT_ACTIVATE, thing, initFunction, initFunctionArgs, initFunctionKwargs)

			if (delFunction != None):
				self.betterBind(wx.EVT_CLOSE, thing, delFunction, delFunctionArgs, delFunctionKwargs)

			if (idleFunction != None):
				self.betterBind(wx.EVT_IDLE, thing, idleFunction, idleFunctionArgs, idleFunctionKwargs)

			if (initPageFunction != None):
				self.betterBind(wx.EVT_INIT_DIALOG, thing, initPageFunction, initPageFunctionArgs, initPageFunctionKwargs)

			if (cancelFunction != None):
				self.betterBind(wx.EVT_WIZARD_CANCEL, thing, cancelFunction, cancelFunctionArgs, cancelFunctionKwargs)

			if (finishFunction != None):
				self.betterBind(wx.EVT_WIZARD_FINISHED, thing, finishFunction, finishFunctionArgs, finishFunctionKwargs)

			if (helpFunction != None):
				self.betterBind(wx.EVT_WIZARD_HELP, thing, helpFunction, helpFunctionArgs, helpFunctionKwargs)

			if (changedFunction != None):
				self.betterBind(wx.EVT_WIZARD_PAGE_CHANGED, thing, changedFunction, changedFunctionArgs, changedFunctionKwargs)

		def startWizardPage(self, wizardPageNumber):
			"""Adds a blank wizard page to the wizard window.

			wizardPageNumber (int) - The number of frame that is being added to the wizard

			Example Input: startWizardPage(1)
			"""

			#Which page are we working with?
			exec("identity = self.m_wizPage" + str(wizardPageNumber))
			
			#Create the thing
			identity = wx.wizard.WizardPageSimple(self )
			self.add_page(identity)

		def endWizardPage(self, wizardPageNumber, sizerNumber, autoSize = True):
			"""Finishes editing a wizard page

			wizardPageNumber (int) - The number of frame that is being added to the wizard
			sizerNumber (int)      - The number of the sizer that this will be added to
			autoSize (bool)        - If True: the window size will be changed to fit the sizers within
									 If False: the window size will be what was defined when it was initially created
									 If None: the internal autosize state will be used

			Example Input: startWizardPage(1, 0)
			"""

			#Which page are we working with?
			exec("identity = self.m_wizPage" + str(wizardPageNumber))

			#Which sizer is being used?
			sizer = self.getSizer(sizerNumber)
			
			#Do the thing
			if (autoSize == None):
				autoSize = identity.autoSize

			if (autoSize):
				identity.SetSizerAndFit(sizer)
			else:
				identity.SetSizer(sizer)

			identity.Layout()
			sizer.Fit(identity)

def main():
	"""The program controller. """

	gui = GUI()
	gui.createWindow("created")
	#gui.debug(0)
	#gui.debugEasy(0)
	#gui.showWindow(0)
	gui.finish()

def print_num(dummyid, n):
	print ("From %s: %d" % (dummyid, n))

def dummy_run(dummyid):
	for i in range(5):
		gui.threadQueue.from_dummy_thread(lambda: print_num(dummyid, i))
		time.sleep(0.5)

if __name__ == '__main__':
	#main()

	#Security Test
	# guiSecurity = GUI.Security()
	# #guiSecurity.generateKeys()
	# guiSecurity.loadKeys()
	# for i in range(1000):
	#   guiSecurity.encryptData("password: Admin\ncounter: 003\nrs232: True\nport: COM1\nbaudRate: 19200\nbyteSize: 0\nparity: 0\nstopBits: 0\ntimeoutRead: None\ntimeoutWrite: None\nflowControl: False\nrtsCts: False\ndsrDtr: False")
	#   data = guiSecurity.decryptData()
	# print(data)
	
	#Queue Test
	gui = GUI()
	threading.Thread(target=dummy_run, args=("a",)).start()
	threading.Thread(target=dummy_run, args=("b",)).start()

	while True:
		gui.threadQueue.from_main_thread()