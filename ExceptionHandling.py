import os
import sys
import time

import wx
import platform
import traceback
import contextlib

import API_Com as Communication
import Utilities as MyUtilities

@contextlib.contextmanager
def asCM(function, *args, **kwargs):
	yield function(*args, **kwargs)

class ErrorDialog(wx.Dialog):
	"""The error dialog that pops up when there is an error logged."""

	def __init__(self, parent, *, message = None, canReport = False):
		super().__init__(None, id = wx.ID_ANY, title = "An Error has occured", style = wx.CAPTION|wx.RESIZE_BORDER)

		self.SetIcon(wx.Icon(wx.ArtProvider.GetBitmap(wx.ART_ERROR)))

		with asCM(wx.BoxSizer, wx.VERTICAL) as rootSizer:
			with asCM(wx.Panel, self, wx.ID_ANY) as myPanel:
				with asCM(wx.FlexGridSizer, rows = 2, cols = 1, hgap = 0, vgap = 0) as mySizer:
					mySizer.AddGrowableRow(0)
					mySizer.AddGrowableCol(0)

					with asCM(wx.StaticText, myPanel, id = wx.ID_ANY, label = message, style = wx.TE_WORDWRAP|wx.TE_MULTILINE|wx.ALIGN_LEFT) as myWidget:
						mySizer.Add(myWidget, 1, wx.ALL|wx.EXPAND, 5)
			 
					with asCM(wx.BoxSizer, wx.HORIZONTAL) as mySubSizer:
						with asCM(wx.Button, myPanel, id = wx.ID_CANCEL, label = "Close") as myWidget:
							mySubSizer.Add(myWidget, 0, wx.ALL, 5)

						with asCM(wx.Button, myPanel, id = wx.ID_OK, label = "Report") as myWidget:
							mySubSizer.Add(myWidget, 0, wx.ALL, 5)
							if (not canReport):
								myWidget.Enable(False)

						mySizer.Add(mySubSizer, 0, wx.ALL, 5)
					myPanel.SetSizer(mySizer)
				rootSizer.Add(myPanel, proportion = 1, flag = wx.ALL|wx.EXPAND, border = 5)
			self.SetSizer(rootSizer)
		self.SetSize(self.GetBestSize())

	def __enter__(self):
		self.CenterOnScreen()
		self.answer = self.ShowModal()
		return self

	def __exit__(self, exc_type, exc_value, traceback):
		self.Destroy()
		
		if (traceback is not None):
			return False

	def isOk(self):
		return self.answer == wx.ID_OK

	def isCancel(self):
		return self.answer == wx.ID_CANCEL

class ExceptionHandler(MyUtilities.logger.LoggingFunctions, MyUtilities.common.EnsureFunctions):
	"""Takes care of errors and exceptions in the app.
	Modified code from: https://wiki.wxpython.org/CustomExceptionHandling?action=AttachFile&do=view&target=errorDialog.zip

	Use: https://www.blog.pythonlibrary.org/2014/01/31/wxpython-how-to-catch-all-exceptions/
	"""

	def __init__(self, parent, *, logger_label = None, appName = None, logDir = None, **kwargs):
		"""
		kwargs -> makeExceptionHook()

		logger_label (str) - What logger to send logs to
			- If None: Will use 'appName'

		appName (str) - What this application is called
			- If None: Will use the parent module's name
		"""
		self.parent = parent
		self.appName = self.ensure_default(appName, lambda: self.parent.__module__.split(".")[0])
	
		MyUtilities.logger.LoggingFunctions.__init__(self, 
			label = self.ensure_default(logger_label, default = self.appName), 
			config = self.getLoggerConfig(logDir = logDir), 
			force_quietRoot = __name__ == "__main__")

		sys.excepthook = self.makeExceptionHook(**kwargs)

	def getLoggerConfig(self, logDir = None):
		"""Returns a dictionary to use to configure the logger.

		logDir (str) - The directory for the log files to be saved at
			- If None: Will use: "%appdata%/{self.appName}/logs"

		Example Input: getLoggerConfig()
		"""

		def default_logDir():
			standardPaths = wx.StandardPaths.Get()
			return os.path.join(standardPaths.GetUserConfigDir(), self.appName, "logs")

		#################################################

		logDir = self.ensure_default(logDir, default = default_logDir)
		
		timestamp = "%Y/%m/%d %H:%M:%S"
		formatter = "{asctime} - {name}:{levelname}; {module}:{lineno}:{threadName} - {message}"

		logger_config = {None: {
			"level": 2, 
		}}

		for key in ("info", "warning", "error", "critical"):
			logger_config[f"handler_{key}"] = {
				"type": "file", 
				"delay": True, 
				"maximum": 20_000, 
				"name": os.path.join(logDir, f"{key}.log"), 

				"level": key, 
				"historyCount": 2, 
				"formatter": formatter, 
				"timestamp": timestamp, 
				"filter_nonLevel": True, 
			}

		return logger_config

	def makeExceptionHook(self, logError = True, printError = True, canReport = True, include_screenshots = True, **kwargs):
		"""Creates an exception hook.

		kwargs -> sendEmail()

		logError (bool) - Determines if errors should be sent to the error log
		printError (bool) - Determines if errors should be printed to the cmd window
		canReport (bool) - Determines if the user can report the error (given that kwargs are provided)

		include_logs - Determines if the log files associated with the logger should be included in the report
		include_traceback - Determines if the traceback of the error should be included in the report
		include_systemInfo - Determines if information about this specific computer should be included in the report
		include_screenshots - Determines if a screenshot of the wxFrame that was active when the error occured should be included in the report

		Example Input: makeExceptionHook()
		"""

		def exceptionHook(error_cls, error, error_traceback):
			"""Used by wxPython to display errors."""
			nonlocal self, logError, printError, kwargs

			errorMessage = "".join(traceback.format_exception(error_cls, error, error_traceback))
			
			if (logError):
				self.log_error(errorMessage)
	
			if (printError):
				print(errorMessage)	

			if (include_screenshots):
				try:
					screenshot = MyUtilities.wxPython.getWindowAsBitmap()
				except MyUtilities.wxPython.NoActiveWindowError:
					screenshot = None
			else:
				screenshot = None

			with ErrorDialog(self, message = errorMessage, canReport = canReport and bool(kwargs)) as myDialog:
				if (myDialog.isOk()):
					try:
						sendEmail(errorMessage, screenshot = screenshot, **kwargs)
						wx.MessageBox("Report Successful", "Success", wx.OK | wx.ICON_INFORMATION)

					except Exception as error:
						traceback.print_exception(type(error), error, error.__traceback__)
						wx.MessageBox("Report Failed", "Failure", wx.OK | wx.ICON_ERROR)

		def sendEmail(errorMessage, fromAddress = None, fromPassword = None, 
			toAddress = None, *, subject = None, server = None, port = None, 
			screenshot = None, extra_information = None, extra_files = None, 
			include_logs = True, include_systemInfo = True, include_traceback = True):
			"""Sends an email with some relevant debugging information.

			toAddress (str) - A valid email address to send to
			fromAddresss (str) - A valid email address to send from
			fromPassword (str) - The password for 'address'

			server (str) - What email server is being used
				- If None: Will use gmail

			port (int) - What port to use
				- If None: 587

			extra_information (str) - A paragraph of extra information to add
				- If callable, will use whatever it returns

			extra_files (str) - An extra file to attach
				- If list: Will attach all files in the list

			Example Input: sendEmail()
			"""

			def yieldSystemInfo():
				yield f"System: {platform.system()}"
				yield f"OS: {wx.GetOsDescription()}"
				yield f"Release: {platform.release()}"
				yield f"Version: {platform.version()}"
				yield f"Machine: {platform.machine()}"
				yield f"Python version: {platform.python_version()}; {platform.python_compiler()}"
				yield f"wxPython version: {wx.version()}"

			#############################################

			assert toAddress is not None
			assert fromAddress is not None
			assert fromPassword is not None

			emailHandle = Communication.getEmail(label = -1)
			emailHandle.open(fromAddress, fromPassword, server = server, port = port)
			
			if (include_traceback):
				emailHandle.append(errorMessage, header = "Traceback")

			if (include_systemInfo):
				emailHandle.append('\n'.join(yieldSystemInfo()), header = "System Information")

			if (extra_information is not None):
				emailHandle.append('\n'.join(self.ensure_container(extra_information)), header = "Extra Information")

			if (include_logs):
				for filePath in self.log_getLogs(returnExisting = True, returnHistory = True):
					emailHandle.attach(filePath)

			if (screenshot is not None):
				emailHandle.attach(screenshot, name = "screenshot")

			for item in self.ensure_container(extra_files):
				emailHandle.attach(item)

			emailHandle.send(toAddress, subject = self.ensure_default(subject, "Automated Error Report"))

		####################################################################

		return exceptionHook

if (__name__ == "__main__"):
	class TestFrame(wx.Frame):
		def __init__(self):
			super().__init__(None, wx.ID_ANY, "Lorem Ipsum")

			with asCM(wx.Panel, self, wx.ID_ANY) as myPanel:
				with asCM(wx.BoxSizer, wx.VERTICAL) as mySizer:
		 
					with asCM(wx.Button, myPanel, id = wx.ID_ANY, label = "Cause Info") as myWidget:
						myWidget.Bind(wx.EVT_BUTTON, self.onCauseInfo)
						mySizer.Add(myWidget, 0, wx.ALL, 5)
			 
					with asCM(wx.Button, myPanel, id = wx.ID_ANY, label = "Cause Warning") as myWidget:
						myWidget.Bind(wx.EVT_BUTTON, self.onCauseWarning)
						mySizer.Add(myWidget, 0, wx.ALL, 5)
			 
					with asCM(wx.Button, myPanel, id = wx.ID_ANY, label = "Cause Error") as myWidget:
						myWidget.Bind(wx.EVT_BUTTON, self.onCauseError)
						mySizer.Add(myWidget, 0, wx.ALL, 5)
			 
					with asCM(wx.Button, myPanel, id = wx.ID_ANY, label = "Cause Critical") as myWidget:
						myWidget.Bind(wx.EVT_BUTTON, self.onCauseCritical)
						mySizer.Add(myWidget, 0, wx.ALL, 5)

					myPanel.SetSizer(mySizer)
	 
		def onCauseInfo(self, event):
			global exceptionHandler

			print("@onCauseInfo")
			# exceptionHandler.logger.log_info("Lorem")
			event.Skip()

		def onCauseWarning(self, event):
			global exceptionHandler

			print("@onCauseWarning")
			# exceptionHandler.logger.log_warning("Ipsum")
			event.Skip()

		def onCauseError(self, event):
			global exceptionHandler

			print("@onCauseError")

			x = 10 / 0

			# exceptionHandler.logger.log_error("Dolor")
			event.Skip()

		def onCauseCritical(self, event):
			global exceptionHandler

			print("@onCauseCritical")
			# exceptionHandler.logger.log_critical("Sit")
			event.Skip()

	def yieldExtraInfo():
		yield "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."

	def yieldExtraFiles():
		yield "H:/Python/modules/GUI_Maker/logs/jmayberry/lorem.txt"
		yield "H:/Python/modules/GUI_Maker/logs/jmayberry/test.bmp"
		yield "H:/Python/modules/GUI_Maker/logs/jmayberry/test.png"

	##################################
			
	app = wx.App(False)
	frame = TestFrame()

	exceptionHandler = ExceptionHandler(app, appName = "Test", logError = False, printError = False,
		logDir = os.path.join(os.getcwd(), "logs", os.environ.get('username')),

		fromAddress = "material.tracker@decaturmold.com", fromPassword = "f@tfr3ddy$c@t", 
		toAddress = "josh.mayberry@decaturmold.com", port = "587", server = "194.2.1.1",
		extra_information = yieldExtraInfo(), extra_files = yieldExtraFiles())
	frame.Show()
	app.MainLoop()
