import os
import sys
import time

import wx
import platform
import traceback

import API_Com as Communication
import Utilities as MyUtilities

asCM = MyUtilities.wxPython.asCM

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

						if (canReport is not None):
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

	def makeExceptionHook(self, *args, **kwargs):
		"""Creates an exception hook.

		kwargs -> sendEmail()

		logError (bool) - Determines if errors should be sent to the error log
		printError (bool) - Determines if errors should be printed to the cmd window
		canReport (bool) - Determines if the user can report the error (given that kwargs are provided)
			- If True: The report button will be enabled
			- If False: The report button will be disabled
			- If None: The report button will not be created

		include_logs - Determines if the log files associated with the logger should be included in the report
		include_traceback - Determines if the traceback of the error should be included in the report
		include_systemInfo - Determines if information about this specific computer should be included in the report
		include_screenshots - Determines if a screenshot of the wxFrame that was active when the error occured should be included in the report

		Example Input: makeExceptionHook()
		"""

		return ExceptionHook(self, *args, **kwargs)

class ExceptionHook(MyUtilities.common.EnsureFunctions):
	def __init__(self, parent, *, logError = True, printError = True, messageError = True, 
		canReport = True, subject = None, server = None, port = None, 
		zip_log = None, zip_screenshot = None, zip_extra = None, 
		fromAddress = None, fromPassword = None, toAddress = None, 
		screenshot = None, extra_information = None, extra_files = None, printTrace_onError = False, 
		include_logs = True, include_systemInfo = True, include_traceback = True, include_screenshots = True):
		"""Replaces sys.excepthook.

		logError (bool) - Determines if errors should be sent to the error log
		printError (bool) - Determines if errors should be printed to the cmd window
		canReport (bool) - Determines if the user can report the error (given that kwargs are provided)

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
			- If dict: {None: what to attach, **kwargs for attach()}

		zip_log (str) - What to call the zip file that the logs are stored in
			- If None: Will not zip the log files

		include_logs - Determines if the log files associated with the logger should be included in the report
		include_traceback - Determines if the traceback of the error should be included in the report
		include_systemInfo - Determines if information about this specific computer should be included in the report
		include_screenshots - Determines if a screenshot of the wxFrame that was active when the error occured should be included in the report

		Example Input: ExceptionHook(self)
		Example Input: ExceptionHook(self, extra_files = "example.txt")
		Example Input: ExceptionHook(self, extra_files = ["lorem.txt", "ipsum.txt"])
		Example Input: ExceptionHook(self, extra_files = [{None: "lorem.txt", "name": "Lorem.txt"}, "ipsum.txt"])
		"""

		self.parent = parent
		self.logError = logError
		self.canReport = canReport
		self.printError = printError
		self.messageError = messageError
		self.printTrace_onError = printTrace_onError

		self.include_logs = include_logs
		self.include_traceback = include_traceback
		self.include_systemInfo = include_systemInfo
		self.include_screenshots = include_screenshots

		self.port = port
		self.server = server
		self.subject = subject
		self.toAddress = toAddress
		self.fromAddress = fromAddress
		self.fromPassword = fromPassword

		self.screenshot = screenshot
		self.extra_files = extra_files
		self.extra_information = extra_information

		self.zip_log = zip_log
		self.zip_extra = zip_extra
		self.zip_screenshot = zip_screenshot

	def __call__(self, error_cls, error, error_traceback):
		"""Displays the error and can report information about it."""

		if (self.printTrace_onError):
			MyUtilities.debugging.printCurrentTrace()
			return

		screenshot = self.getScreenshots()

		errorMessage = "".join(traceback.format_exception(error_cls, error, error_traceback))
		
		if (self.logError):
			self.parent.log_error(errorMessage)

		if (self.printError):
			print(errorMessage)

		if (self.messageError):
			with ErrorDialog(self, message = errorMessage, canReport = self.canReport) as myDialog:
				if (myDialog.isOk()):
					self.sendEmail(errorMessage, screenshot = screenshot)

	def getScreenshots(self):
		if (not self.include_screenshots):
			return

		try:
			return MyUtilities.wxPython.getWindowAsBitmap()
		except MyUtilities.wxPython.NoActiveWindowError:
			pass

	def sendEmail(self, *args, show_resultMessage = True, **kwargs):
		try:
			self.emailRoutine(*args, **kwargs)
			if (show_resultMessage):
				wx.MessageBox("Report Successful", "Success", wx.OK | wx.ICON_INFORMATION)
			return True

		except Exception as error:
			traceback.print_exception(type(error), error, error.__traceback__)
			if (show_resultMessage):
				wx.MessageBox("Report Failed", "Failure", wx.OK | wx.ICON_ERROR)
			return False

	def emailRoutine(self, errorMessage = None, toAddress = None, subject = None, *, 
		extra_sections = None, screenshot = None, include_screenshots = None, 
		include_traceback = None, include_systemInfo = None, include_logs = None):
		"""Sends an email with some relevant debugging information.

		Example Input: emailRoutine()
		"""

		def yieldSystemInfo():
			yield f"Release: {platform.release()}"
			yield f"Machine: {platform.machine()}"
			yield f"Version: {platform.version()}"
			yield f"System: {platform.system()}"
			yield f"OS: {wx.GetOsDescription()}"
			yield f"Python version: {platform.python_version()}; {platform.python_compiler()}"
			yield f"wxPython version: {wx.version()}"

		def yieldSection():
			nonlocal self, errorMessage, include_traceback, include_systemInfo

			if (errorMessage and self.ensure_default(include_traceback, default = self.include_traceback)):
				yield "Traceback", errorMessage

			if (self.ensure_default(include_systemInfo, default = self.include_systemInfo)):
				yield "System Information", "\n".join(yieldSystemInfo())

			if (self.extra_information is not None):
				yield "Extra Information", "\n".join(self.ensure_container(self.extra_information))

			for section, message in self.ensure_container(extra_sections, elementCriteria = (2, (str, None))):
				yield section, "\n".join(self.ensure_container(message))

		def yieldLogs():
			if (not self.ensure_default(include_logs, default = self.include_logs)):
				return

			for item in self.parent.log_getLogs(returnExisting = True, returnHistory = True):
				yield item

		def yieldScreenshot():
			nonlocal self, screenshot

			if (not self.ensure_default(include_screenshots, default = self.include_screenshots)):
				return

			for i, item in enumerate(self.ensure_container(screenshot), start = 1):
				if (i is 1):
					yield item, "screenshot"
				else:
					yield item, f"screenshot_{i}"

		def yieldExtraFiles():
			nonlocal self

			if (self.extra_files is None):
				return

			for item in self.ensure_container(self.extra_files):
				if (isinstance(item, dict)):
					catalogue = {**item}
					yield catalogue.pop(None, None), catalogue
					continue

				yield item, {}

		#############################################

		assert self.fromAddress is not None

		emailHandle = Communication.getEmail(label = -1)
		emailHandle.open(self.fromAddress, self.fromPassword, server = self.server, port = self.port)
		
		for section, message in yieldSection():
			emailHandle.append(message, header = section)

		for item in yieldLogs():
			emailHandle.attach(item, zip_label = self.zip_log)

		for item, name in yieldScreenshot():
			emailHandle.attach(item, zip_label = self.zip_screenshot, name = name)

		for item, _kwargs in yieldExtraFiles():
			emailHandle.attach(item, **{"zip_label": self.zip_extra, **_kwargs})

		emailHandle.send(self.ensure_default(toAddress, default = (self.toAddress, self.fromAddress)), subject = self.ensure_default(subject, (self.subject, "Automated Error Report")))

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
