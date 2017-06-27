#coding: utf-8
#Use a 32 bit python version, not a 64 bit
#Version 1.0.0

import ctypes
import atexit

class ErrorHandler():
	"""Takes care of errors.
	Meant to be inherited by BCS_IO.
	"""

	def __init__(self):
		"""Sets up the internal variables."""

		#[Error Message, Function to handle the error]
		self.errorCodes = {0x0000: self.handleError0,
						   0x0001: self.handleError1,
						   0x0002: self.handleError2,
						   0x0003: self.handleError3,
						   0x0004: self.handleError4,
						   0x0005: self.handleError5,
						   0x0006: self.handleError6,
						   0x0010: self.handleError10,
						   0x0020: self.handleError20,
						   0x0040: self.handleError40,
						   0x0080: self.handleError80,
						   0x0100: self.handleError100,
						   0x0200: self.handleError200,
						   0x0400: self.handleError400,
						   0x0800: self.handleError800,
						   0x1000: self.handleError1000,
						   0x2000: self.handleError2000,
						   0x4000: self.handleError4000,
						   0x8000: self.handleError8000}

	def handleError(self, errCode, ErrMsg, *args):
		"""Handles a recieved error code.
		Returns True if there is no error or it has been fixed

		errCode (int) - The error
		ErrMsg (str)  - String containing any error messages
		args (any)    - variables necissary to handle specific errors

		Example	Input: handleError(0)
		Example	Input: handleError(1)
		"""

		if (errCode == 0):
			#There is no problem
			errorState = True
		else:
			# #Tell the user error messages provided by the device
			# if (ErrMsg != ""):
			# 	print(ErrMsg.value.decode("utf-8"))

			#Fix the problem
			errorFunction = self.errorCodes[errCode]
			errorState = errorFunction(*args)

		return errorState

	#The user should modify these equations to take care of the various errors
	#as they pertain to their particular application
	def handleError0(self, *args):
		"""OK"""
		
		#Tell the user problem specifics
		print("Error 0: OK")

		return False

	def handleError1(self, *args):
		"""Invalid Handle"""
		
		#Tell the user problem specifics
		print("Error 1: Invalid Handle")

		return False

	def handleError2(self, *args):
		"""Device Not Found"""

		#Tell the user problem specifics
		print("Error 2: Device Not Found")

		return False

	def handleError3(self, *args):
		"""Device Not Opened"""

		#Tell the user problem specifics
		print("Error 3: Device Not Opened")

		return False

	def handleError4(self, *args):
		"""IO Error"""

		#Tell the user problem specifics
		print("Error 4: IO Error")

		return False

	def handleError5(self, *args):
		"""Insufficient Resources"""

		#Tell the user problem specifics
		print("Error 5: Insufficient Resources")

		return False

	def handleError6(self, *args):
		"""Invalid Parameter"""

		#Tell the user problem specifics
		print("Error 6: Invalid Parameter")

		return False

	def handleError10(self, *args):
		"""Other Error"""

		#Tell the user problem specifics
		print("Error 10: Other Error")

		return False

	def handleError20(self, *args):
		"""Not a valid Input port"""

		#Tell the user problem specifics
		print("Error 20: Not a valid Input port")

		return False

	def handleError40(self, *args):
		"""Incorrect input port value sent, possible USB transfer error"""

		#Tell the user problem specifics
		print("Error 40: Incorrect input port value sent, possible USB transfer error")

		return False

	def handleError80(self, *args):
		"""Not a valid Output port"""

		#Tell the user problem specifics
		print("Error 80: Not a valid Output port")

		return False

	def handleError100(self, *args):
		"""Unknown error"""

		#Tell the user problem specifics
		print("Error 100: Unknown error")

		return False

	def handleError200(self, *args):
		"""Unknown command byte"""

		#Tell the user problem specifics
		print("Error 200: Unknown command byte")

		return False

	def handleError400(self, *args):
		"""Unknown error"""

		#Tell the user problem specifics
		print("Error 400: Unknown error")

		return False

	def handleError800(self, *args):
		"""Unknown request byte returned, possible USB transfer error"""

		#Tell the user problem specifics
		print("Error 800: Unknown request byte returned, possible USB transfer error")

		return False

	def handleError1000(self, *args):
		"""Incorrect command returned"""

		#Tell the user problem specifics
		print("Error 1000: Incorrect command returned")

		return False

	def handleError2000(self, *args):
		"""Time out reading from the device"""

		#Tell the user problem specifics
		print("Error 2000: Time out reading from the device")

		return False

	def handleError4000(self, *args):
		"""Incorrect number of bytes written to device"""

		#Tell the user problem specifics
		print("Error 4000: Incorrect number of bytes written to device")

		return False

	def handleError8000(self, *args):
		"""Lorem"""

		#Tell the user problem specifics
		print("Error 8000: ?")

		return False

class Utilities():
	"""Convenience functions for BCS_IO.
	Meant to be inherited by BCS_IO.
	"""

	def __init__(self):
		"""Here for PEP-8 convention."""
		
		pass

	def getBit(self, bit, ucPVal, asBool = True):
		"""Returns the value of a specific bit.
		True ("0") means that bit is active. False ("1") means that bit is inactive.
		### Does not yet support ucLPort or ucHPort. Only ucPVal. ###

		bit (int)     - Which bit to check (0 - 7)
		ucPVal (str)  - The value of the requested port
							~ Example: "0": all 8 bits are active (binary: 00000000)
							~ Example: "255": all 8 bits are inactive (binary: 11111111)
		asBool (bool) - If True: The value will be returned as True or False
						If False: The value will be returned as "0" or "1" 

		Example Input: getBit(6, "11110111")
		"""

		#Extract the bit
		value = ucPVal[bit]

		#Return the bit
		if (asBool):
			value = not bool(value)
		return value

	def bin2int(self, number):
		"""Converts binary numbers to integers.
		Modified from Eli Bendersky on: http://stackoverflow.com/questions/2072351/python-conversion-from-binary-string-to-hexadecimal

		Example Input: bin2int("11110111")
		"""

		number = int(str(number), 2)

		return number

	def int2bin(self, number):
		"""Converts integers to binary numbers.

		Example Input: int2bin(5)
		"""

		number = "{0:08b}".format(number)

		return number

	def bitFlip(self, number):
		"""Flips the 1s with 0s in the given number.
		Modified from Amber on: http://stackoverflow.com/questions/3920494/python-flipping-binary-1s-and-0s-in-a-string

		Example Input: bitFlip("11110111")
		"""

		number = ''.join('1' if x == '0' else '0' for x in number)

		return number

class BCS_IO(ErrorHandler, Utilities):
	"""Connects to a BCS Ideas board to read and write information.

	dll_path (str) - The pathway to the RP2005 dll

	Code adapted from David Heffernan on: http://stackoverflow.com/questions/5253854/python-import-dll
	Special thanks to: http://starship.python.net/crew/theller/ctypes/tutorial.html
					   http://stackoverflow.com/questions/1781531/how-to-load-dll-using-ctypes-in-python
					   https://www.youtube.com/watch?v=fGuHMVAruAE
					   https://msdn.microsoft.com/en-us/library/ms235636.aspx

	Example Input: BCS_IO("C:/Program Files (x86)/BCS_Ideas/RP2005/Software/DLL_201/RP2005.dll")
	"""

	def __init__(self, dll_path):
		"""Sets up the connection to the RP2005 dll."""

		#Initialize Inherited classes
		ErrorHandler.__init__(self)
		Utilities.__init__(self)

		#Initialize the dll
		lib = ctypes.WinDLL(dll_path)

		#Connect to the dll functions
		self.dll_RP_ListDIO      = lib['RP_ListDIO']
		self.dll_RP_OpenDIO      = lib['RP_OpenDIO']
		self.dll_RP_CloseDIO     = lib['RP_CloseDIO']

		self.dll_RP_GetVer       = lib['RP_GetVer']
		self.dll_RP_GetVer_SN    = lib['RP_GetVer_SN']
		self.dll_RP_ReadPort     = lib['RP_ReadPort']
		self.dll_RP_ReadPort_SN  = lib['RP_ReadPort_SN']
		self.dll_RP_ReadAll      = lib['RP_ReadAll']
		self.dll_RP_ReadAll_SN   = lib['RP_ReadAll_SN']

		self.dll_RP_WritePort    = lib['RP_WritePort']
		self.dll_RP_WritePort_SN = lib['RP_WritePort_SN']
		self.dll_RP_WriteAll     = lib['RP_WriteAll']
		self.dll_RP_WriteAll_SN  = lib['RP_WriteAll_SN']

		#Set dll input variable types
		self.dll_RP_ListDIO.argtypes      = [ctypes.POINTER(ctypes.c_int),   ctypes.c_char_p,  ctypes.c_char_p]
		self.dll_RP_OpenDIO.argtypes      = [ctypes.c_char_p,  ctypes.POINTER(ctypes.c_ulong)]
		self.dll_RP_CloseDIO.argtypes     = [ctypes.c_ulong]

		self.dll_RP_GetVer.argtypes       = [ctypes.c_ulong, ctypes.c_char_p,  ctypes.c_char_p]
		self.dll_RP_GetVer_SN.argtypes    = [ctypes.c_char_p,  ctypes.c_char_p,  ctypes.c_char_p]
		self.dll_RP_ReadPort.argtypes     = [ctypes.c_ulong, ctypes.c_ubyte, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_char_p]
		self.dll_RP_ReadPort_SN.argtypes  = [ctypes.c_char_p,  ctypes.c_ubyte, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_char_p]
		self.dll_RP_ReadAll.argtypes      = [ctypes.c_ulong, ctypes.POINTER(ctypes.c_ulong), ctypes.POINTER(ctypes.c_ulong), ctypes.c_char_p]
		self.dll_RP_ReadAll_SN.argtypes   = [ctypes.c_char_p,  ctypes.POINTER(ctypes.c_ulong), ctypes.POINTER(ctypes.c_ulong), ctypes.c_char_p]
		
		self.dll_RP_WritePort.argtypes    = [ctypes.c_ulong, ctypes.c_ubyte, ctypes.c_ubyte, ctypes.c_char_p]
		self.dll_RP_WritePort_SN.argtypes = [ctypes.c_char_p,  ctypes.c_ubyte, ctypes.c_ubyte, ctypes.c_char_p]
		self.dll_RP_WriteAll.argtypes     = [ctypes.c_ulong, ctypes.c_ulong, ctypes.c_ulong, ctypes.c_char_p]
		self.dll_RP_WriteAll_SN.argtypes  = [ctypes.c_char_p,  ctypes.c_ulong, ctypes.c_ulong, ctypes.c_char_p]

		#Set dll output variable types
		self.dll_RP_ListDIO.restype      = ctypes.c_ulong
		self.dll_RP_OpenDIO.restype      = ctypes.c_ulong
		self.dll_RP_CloseDIO.restype     = ctypes.c_ulong

		self.dll_RP_GetVer.restype       = ctypes.c_ulong
		self.dll_RP_GetVer_SN.restype    = ctypes.c_ulong
		self.dll_RP_ReadPort.restype     = ctypes.c_ulong
		self.dll_RP_ReadPort_SN.restype  = ctypes.c_ulong
		self.dll_RP_ReadAll.restype      = ctypes.c_ulong
		self.dll_RP_ReadAll_SN.restype   = ctypes.c_ulong
		
		self.dll_RP_WritePort.restype    = ctypes.c_ulong
		self.dll_RP_WritePort_SN.restype = ctypes.c_ulong
		self.dll_RP_WriteAll.restype     = ctypes.c_ulong
		self.dll_RP_WriteAll_SN.restype  = ctypes.c_ulong

		#Initialize internal variables
		self.BCS_Opened = {} #{SN: True if it is open False if it is closed}

	def RP_ListDIO(self, iNumDev):
		"""Gets information concerning the devices currently connected. 
		This function returns the number of devices connected, 
		each device’s serial number and product description.

		This function is used to return each device’s serial number. 
		The serial number is then used by RP_Open to obtain
		a handle for subsequent reading and writing of DIO.

		iNumDev (int) - The number of RP2005 devices currently attached to the USB
		SN (str)      - Comma delimited string containing the serial number
						of each RP2005 device currently attached to the USB
		Desc (str)    - Comma delimited string containing the device description
						of each RP2005 device currently attached to the USB

		Example Input: RP_ListDIO()
		"""

		#Ensure ctype format
		if (type(iNumDev) == int):
			iNumDev_ctypes = ctypes.c_int(iNumDev)

		#Initialize c++ reference variables
		SN = ctypes.create_string_buffer(255) #Create a 255 byte buffer, initialized to NUL bytes
		Desc = ctypes.create_string_buffer(255) #Create a 255 byte buffer, initialized to NUL bytes

		#Interact with the dll
		ulErrCode = self.dll_RP_ListDIO(ctypes.byref(iNumDev_ctypes), SN, Desc)

		#Check for errors
		noError = self.handleError(ulErrCode, "")
		if (noError):
			#Take appropriate action
			return SN.value, Desc.value
		else:
			return -1, -1

	def RP_OpenDIO(self, SN):
		"""Open the device and return a handle which will be used for 
		subsequent reading and writing of DIO.

		SN (str)    - The serial number for the device
		hDIO (long) - Pointer to a variable of type long where the handle will be stored.
					  This handle must be used to access the device

		Example Input: RP_OpenDIO("RP0002D1")
		"""

		#Check if it is already opened
		if (SN in self.BCS_Opened):
			if (self.BCS_Opened[SN]):
				print(SN, "is already open")
				return -1

		#Initialize c++ reference variables
		hDIO = ctypes.c_ulong()

		#Interact with the dll
		ulErrCode = self.dll_RP_OpenDIO(SN, ctypes.byref(hDIO))

		#Check for errors
		noError = self.handleError(ulErrCode, "")
		if (noError):
			#Add close function to program ending protocol (in case the user does not close the device)
			if (SN not in self.BCS_Opened):
				atexit.register(self.RP_CloseDIO, hDIO)

			#Remember that this has been opened
			self.BCS_Opened[SN] = True

			#Take appropriate action
			return hDIO.value
		else:
			return -1

	def RP_CloseDIO(self, hDIO):
		"""Close an open device.

		hDIO (long) - Handle of the device to close.

		Example Input: RP_CloseDIO(hDIO)
		"""

		#Interact with the dll
		ulErrCode = self.dll_RP_CloseDIO(hDIO)
		#Check for errors
		noError = self.handleError(ulErrCode, "")
		if (noError):
			#Take appropriate action
			pass
		else:
			return -1

	def RP_GetVer(self, hDIO):
		"""Read software version from the device.

		The function does not return until the requested port has been 
		read or read timeout occurs. The read timeout is set to 1 second.

		hDIO (long)  - Handle of the device to write
		SWVer (str)  - String containing the software version of the device
		ErrMsg (str) - String containing any error messages

		Example Input: RP_GetVer(hDIO)
		"""

		#Initialize c++ reference variables
		SWVer = ctypes.create_string_buffer(255) #Create a 255 byte buffer, initialized to NUL bytes
		ErrMsg = ctypes.create_string_buffer(255) #Create a 255 byte buffer, initialized to NUL bytes

		#Interact with the dll
		ulErrCode = self.dll_RP_GetVer(hDIO, SWVer, ErrMsg)

		#Check for errors
		noError = self.handleError(ulErrCode, ErrMsg)
		if (noError):
			#Take appropriate action
			return SWVer.value
		else:
			return -1

	def RP_GetVer_SN(self, SN):
		"""Read software version from the device.
		The function will open the device, perform the function, 
		and then close the device.
		Note: Do not use this function on a device that is already opened.

		The function does not return until the requested port has been 
		read or read timeout occurs. The read timeout is set to 1 second.

		SN (str)     - Serial number of the board
		SWVer (str)  - String containing the software version of the device
		ErrMsg (str) - String containing any error messages

		Example Input: RP_GetVer_SN("RP0002D1")
		"""

		#Initialize c++ reference variables
		SWVer = ctypes.create_string_buffer(255) #Create a 255 byte buffer, initialized to NUL bytes
		ErrMsg = ctypes.create_string_buffer(255) #Create a 255 byte buffer, initialized to NUL bytes

		#Interact with the dll
		ulErrCode = self.dll_RP_GetVer_SN(SN, SWVer, ErrMsg)

		#Check for errors
		noError = self.handleError(ulErrCode, ErrMsg)
		if (noError):
			#Take appropriate action
			return SWVer.value
		else:
			return -1

	def RP_ReadPort(self, hDIO, ucPort, binary = True):
		"""Read data from the device.

		The function does not return until the requested port has been 
		read or read timeout occurs. The read timeout is set to 1 second.

		hDIO (long)   - Handle of the device to read
		ucPort (str)  - The number of the port to be read
			~ "0": Input port 0 (bits 24 - 31)
			~ "1": Input port 1 (bits 16 - 23)
			~ "2": Input port 2 (bits 8 - 15)
			~ "3": Input port 3 (bits 0 - 7)
			~ "16": Output port 0 (bits 24 - 31)
			~ "17": Output port 1 (bits 16 - 23)
			~ "18": Output port 2 (bits 8 - 15)
			~ "19": Output port 3 (bits 0 - 7)
			~ Any other value will return an error
		binary (bool) - If True: A string of binary output will be returned
						If False: A string of integer output will be returned
		ucPVal (str)  - The value of the requested port
			~ Example: "0": all 8 bits are active (binary: 00000000)
			~ Example: "255": all 8 bits are inactive (binary: 11111111)
		ErrMsg (str)  - String containing any error messages

		Example Input: RP_ReadPort(hDIO, 0)
		Example Input: RP_ReadPort(hDIO, 0, binary = False)
		"""

		#Initialize c++ reference variables
		ucPVal = ctypes.c_ubyte()
		ErrMsg = ctypes.create_string_buffer(255) #Create a 255 byte buffer, initialized to NUL bytes

		#Interact with the dll
		ulErrCode = self.dll_RP_ReadPort(hDIO, ucPort, ctypes.byref(ucPVal), ErrMsg)

		#Check for errors
		noError = self.handleError(ulErrCode, ErrMsg)
		if (noError):
			#Take appropriate action
			ucPVal = self.int2bin(ucPVal.value)
			if (not binary):
				ucPVal = self.bitFlip(ucPVal)
				ucPVal = self.bin2int(ucPVal)

			return ucPVal
		else:
			return -1

	def RP_ReadPort_SN(self, SN, ucPort, binary = True):
		"""Read data from the device.
		The function will open the device, perform the function,
		and then close the device. 
		Note: Do not use this function on a device that is already opened.

		The function does not return until the requested port has been 
		read or read timeout occurs. The read timeout is set to 1 second.

		SN (str)      - Serial number of the board
		ucPort (str)  - The number of the port to be read
							~ "0": Input port 0 (bits 24 - 31)
							~ "1": Input port 1 (bits 16 - 23)
							~ "2": Input port 2 (bits 8 - 15)
							~ "3": Input port 3 (bits 0 - 7)
							~ "16": Output port 0 (bits 24 - 31)
							~ "17": Output port 1 (bits 16 - 23)
							~ "18": Output port 2 (bits 8 - 15)
							~ "19": Output port 3 (bits 0 - 7)
							~ Any other value will return an error
		binary (bool) - If True: A string of binary output will be returned
						If False: A string of integer output will be returned
		ucPVal (str)  - The value of the requested port
							~ Example: "0": all 8 bits are active (binary: 00000000)
							~ Example: "255": all 8 bits are inactive (binary: 11111111)
		ErrMsg (str)  - String containing any error messages

		Example Input: RP_ReadPort_SN("RP0002D1", 0)
		Example Input: RP_ReadPort_SN("RP0002D1", 0, binary = False)
		"""

		#Initialize c++ reference variables
		ucPVal = ctypes.c_ubyte()
		ErrMsg = ctypes.create_string_buffer(255) #Create a 255 byte buffer, initialized to NUL bytes

		#Interact with the dll
		ulErrCode = self.dll_RP_ReadPort_SN(SN, ucPort, ucPVal, ErrMsg)

		#Check for errors
		noError = self.handleError(ulErrCode, ErrMsg)
		if (noError):
			#Take appropriate action
			ucPVal = self.int2bin(ucPVal.value)
			if (not binary):
				ucPVal = self.bitFlip(ucPVal)
				ucPVal = self.bin2int(ucPVal)

			return ucPVal
		else:
			return -1

	def RP_ReadAll(self, hDIO, binary = True):
		"""Read all 8 ports of data from the device.

		The function does not return until the requested port has been 
		read or read timeout occurs. The read timeout is set to 1 second.

		WARNING: This function will only work with boards that have 
		a firmware version of 2.00 or higher.

		hDIO (long)    - Handle of the device to read
		binary (bool)  - If True: A string of binary output will be returned
						 If False: A string of integer output will be returned
		ucLPort (long) - The value of the four input ports
		ucHPort (long) - The value of the four output ports
		ErrMsg (str)   - String containing any error messages

		Example Input: RP_ReadAll(hDIO)
		"""

		#Initialize c++ reference variables
		ucLPort = ucPVal = ctypes.c_ulong()
		ucHPort = ucPVal = ctypes.c_ulong()
		ErrMsg = ctypes.create_string_buffer(255) #Create a 255 byte buffer, initialized to NUL bytes

		#Interact with the dll
		ulErrCode = self.dll_RP_ReadAll(hDIO, ucLPort, ucHPort, ErrMsg)

		#Check for errors
		noError = self.handleError(ulErrCode, ErrMsg)
		if (noError):
			#Take appropriate action
			ucLPort = self.int2bin(ucLPort.value)
			ucHPort = self.int2bin(ucHPort.value)
			if (not binary):
				ucLPort = self.bitFlip(ucLPort)
				ucHPort = self.bitFlip(ucHPort)
				
				ucLPort = self.bin2int(ucLPort)
				ucHPort = self.bin2int(ucHPort)

			return ucLPort, ucHPort
		else:
			return -1, -1

	def RP_ReadAll_SN(self, SN, binary = True):
		"""Read all 8 ports of data from the device.
		The function will open the device, perform the function, 
		and then close the device. 
		Note: Do not use this function on a device that is already opened.

		The function does not return until the requested port has been 
		read or read timeout occurs. The read timeout is set to 1 second.

		WARNING: This function will only work with boards that have 
		a firmware version of 2.00 or higher.

		SN (str)       - Serial number of the board
		binary (bool)  - If True: A string of binary output will be returned
						 If False: A string of integer output will be returned
		ucLPort (long) - The value of the four input ports
		ucHPort (long) - The value of the four output ports
		ErrMsg (str)   - String containing any error messages

		Example Input: RP_ReadAll_SN("RP0002D1")
		"""

		#Initialize c++ reference variables
		ucLPort = ucPVal = ctypes.c_ulong()
		ucHPort = ucPVal = ctypes.c_ulong()
		ErrMsg = ctypes.create_string_buffer(255) #Create a 255 byte buffer, initialized to NUL bytes

		#Interact with the dll
		ulErrCode = self.dll_RP_ReadAll_SN(SN, ucLPort, ucHPort, ErrMsg)

		#Check for errors
		noError = self.handleError(ulErrCode, ErrMsg)
		if (noError):
			#Take appropriate action
			ucLPort = self.int2bin(ucLPort.value)
			ucHPort = self.int2bin(ucHPort.value)
			if (not binary):
				ucLPort = self.bitFlip(ucLPort)
				ucHPort = self.bitFlip(ucHPort)
				
				ucLPort = self.bin2int(ucLPort)
				ucHPort = self.bin2int(ucHPort)

			return ucLPort, ucHPort
		else:
			return -1, -1			

	def RP_WritePort(self, hDIO, ucPort, ucPVal):
		"""Set bits for an output port.

		The function does not return until the requested port has been 
		written or write timeout occurs. The write timeout is set to 1 second.

		hDIO (long)   - Handle of the device to write
		ucPort (long) - The number of the output port to be written
							~ "0": Input port 0 (bits 24 - 31)
							~ "1": Input port 1 (bits 16 - 23)
							~ "2": Input port 2 (bits 8 - 15)
							~ "3": Input port 3 (bits 0 - 7)
							~ "16": Output port 0 (bits 24 - 31)
							~ "17": Output port 1 (bits 16 - 23)
							~ "18": Output port 2 (bits 8 - 15)
							~ "19": Output port 3 (bits 0 - 7)
							~ Any other value will return an error
		ucPVal (str)  - The value to write to the output port
							~ Example: "0": all 8 bits are active (binary: 00000000)
							~ Example: "255": all 8 bits are inactive (binary: 11111111)
		ErrMsg (str)  - String containing any error messages

		Example Input: RP_WritePort(hDIO, 16, "11110111")
		"""

		#Initialize c++ reference variables
		ErrMsg = ctypes.create_string_buffer(255) #Create a 255 byte buffer, initialized to NUL bytes

		#Convert binary to hex
		ucPVal = self.bin2int(ucPVal)

		#Interact with the dll
		ulErrCode = self.dll_RP_WritePort(hDIO, ucPort, ucPVal, ErrMsg)

		#Check for errors
		noError = self.handleError(ulErrCode, ErrMsg)
		if (noError):
			#Take appropriate action
			pass
		else:
			return -1

	def RP_WritePort_SN(self, SN, ucPort, ucPVal):
		"""Set bits for an output port.
		The function will open the device, perform the function, 
		and then close the device. 
		Note: Do not use this function on a device that is already opened.

		The function does not return until the requested port has been 
		written or write timeout occurs. The write timeout is set to 1 second.

		SN (str)      - Serial number of the board
		ucPort (long) - The number of the output port to be written
							~ "0": Input port 0 (bits 24 - 31)
							~ "1": Input port 1 (bits 16 - 23)
							~ "2": Input port 2 (bits 8 - 15)
							~ "3": Input port 3 (bits 0 - 7)
							~ "16": Output port 0 (bits 24 - 31)
							~ "17": Output port 1 (bits 16 - 23)
							~ "18": Output port 2 (bits 8 - 15)
							~ "19": Output port 3 (bits 0 - 7)
							~ Any other value will return an error
		ucPVal (long) - The value to write to the output port
							~ Example: "0": all 8 bits are active (binary: 00000000)
							~ Example: "255": all 8 bits are inactive (binary: 11111111)
		ErrMsg (str)  - String containing any error messages

		Example Input: RP_WritePort_SN("RP0002D1", 0, "11110111")
		"""

		#Initialize c++ reference variables
		ErrMsg = ctypes.create_string_buffer(255) #Create a 255 byte buffer, initialized to NUL bytes

		#Convert binary to hex
		ucPVal = self.bin2int(ucPVal)

		#Interact with the dll
		ulErrCode = self.dll_RP_WritePort_SN(SN, ucPort, ucPVal, ErrMsg)

		#Check for errors
		noError = self.handleError(ulErrCode, ErrMsg)
		if (noError):
			#Take appropriate action
			pass
		else:
			return -1

	def RP_WriteAll(self, hDIO, ucLPort, ucHPort):
		"""Set bits for all of the output ports.

		The function does not return until the requested port has been 
		written or write timeout occurs. The write timeout is set to 1 second.

		WARNING: This function will only work with boards that have 
		a firmware version of 2.00 or higher.

		hDIO (long)   - Handle of the device to write
		ucLPort (long)   - The value to write to four of the output ports
							~ Output port 0 (bits 24 - 31)
							~ Output port 1 (bits 16 - 23)
							~ Output port 2 (bits 8 - 15)
							~ Output port 3 (bits 0 - 7)
		ucHPort (long)   - The value to write to four of the output ports
							~ Output port 4 (bits 24 - 31)
							~ Output port 5 (bits 16 - 23)
							~ Output port 6 (bits 8 - 15)
							~ Output port 7 (bits 0 - 7)
		ErrMsg (str)  - String containing any error messages

		Example Input: RP_WriteAll(hDIO, "11111111111111110000000000000000", "11111111111111111111111111111111")
		"""

		#Initialize c++ reference variables
		ErrMsg = ctypes.create_string_buffer(255) #Create a 255 byte buffer, initialized to NUL bytes

		#Convert binary to hex
		ucLPort = self.bin2int(ucLPort)
		ucHPort = self.bin2int(ucHPort)

		#Interact with the dll
		ulErrCode = self.dll_RP_WriteAll(hDIO, ucLPort, ucHPort, ErrMsg)

		#Check for errors
		noError = self.handleError(ulErrCode, ErrMsg)
		if (noError):
			#Take appropriate action
			pass
		else:
			return -1

	def RP_WriteAll_SN(self, SN, ucLPort, ucHPort):
		"""Set bits for all of the output ports.
		The function will open the device, perform the function, 
		and then close the device. 
		Note: Do not use this function on a device that is already opened.

		The function does not return until the requested port has been 
		written or write timeout occurs. The write timeout is set to 1 second.

		WARNING: This function will only work with boards that have 
		a firmware version of 2.00 or higher.

		SN (str)       - Serial number of the board
		ucLPort (long) - The value to write to four of the output ports
							~ Output port 0 (bits 24 - 31)
							~ Output port 1 (bits 16 - 23)
							~ Output port 2 (bits 8 - 15)
							~ Output port 3 (bits 0 - 7)
		ucHPort (long) - The value to write to four of the output ports
							~ Output port 4 (bits 24 - 31)
							~ Output port 5 (bits 16 - 23)
							~ Output port 6 (bits 8 - 15)
							~ Output port 7 (bits 0 - 7)
		ErrMsg (str)   - String containing any error messages

		Example Input: RP_WriteAll_SN("RP0002D1", "11111111111111110000000000000000", "11111111111111111111111111111111")
		"""

		#Initialize c++ reference variables
		ErrMsg = ctypes.create_string_buffer(255) #Create a 255 byte buffer, initialized to NUL bytes

		#Convert binary to hex
		ucLPort = self.bin2int(ucLPort)
		ucHPort = self.bin2int(ucHPort)

		#Interact with the dll
		ulErrCode = self.dll_RP_WriteAll_SN(SN, ucLPort, ucHPort, ErrMsg)

		#Check for errors
		noError = self.handleError(ulErrCode, ErrMsg)
		if (noError):
			#Take appropriate action
			pass
		else:
			return -1

def main():
	"""Some example code using the module above.

	Example Input: main()
	"""

	#Initialize BCS object
	bcs = BCS_IO("C:/Program Files (x86)/BCS_Ideas/RP2005/Software/DLL_201/RP2005.dll")

	#Setup BCS
	SN, Desc = bcs.RP_ListDIO(1)
	hDIO = bcs.RP_OpenDIO(SN)
	
	#Interact with BCS
	# SWVer = bcs.RP_GetVer(hDIO)

	# bcs.RP_WritePort(hDIO, 16, "11111111")
	# bcs.RP_WritePort(hDIO, 17, "11111111")
	# bcs.RP_WritePort(hDIO, 16, "10101010")
	# bcs.RP_WritePort(hDIO, 17, "10101010")

	print(bcs.RP_ReadPort(hDIO, 0))
	# print(bcs.RP_ReadAll(hDIO))

	#End program
	bcs.RP_CloseDIO(hDIO)

	# SWVer = bcs.RP_GetVer_SN(SN)
	# bcs.RP_WriteAll_SN(SN, "11101111011000110000000000000000", "11110111111011111111111111111111")
	# bcs.RP_WriteAll(hDIO, "11101111011000110000000000000000", "11110111111011111111111111111111")
	# print(bcs.RP_ReadPort_SN(SN, 16))
	# print(bcs.RP_ReadAll_SN(SN))

if __name__ == '__main__':
	main()