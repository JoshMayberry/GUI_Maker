import os
import sys
import time
if (__name__ == "__main__"):
	sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))) #Allows to import from the parent directory

import GUI_Maker

#Create GUI object
gui = GUI_Maker.build()

printData = None

def onPrint(event):
	global printData
	
	with gui[0].makeDialogPrintPreview(printData = printData) as myDialog:
		if (myDialog.isCancel()):
			return

		myDialog.setValue("Lorem Ipsum")
		myDialog.send()

	event.Skip()

def onSetup(event):
	global printData

	with myFrame.makeDialogPrint() as myDialog:
		if (myDialog.isCancel()):
			return
		printData = myDialog.getValue()

	event.Skip()

#Construction Functions
def buildWindow():
	"""Creates a simple window."""

	#Initialize Frame
	with gui.addWindow(label = 0, title = "Print Preview Example") as myFrame:
		myFrame.setWindowSize((450, 200))
		
		with myFrame.addSizerBox() as mySizer:
			mySizer.addButton(text = "Setup", myFunction = onSetup)
			mySizer.addButton(text = "Print", myFunction = onPrint)

#Run Program
if __name__ == '__main__':
	buildWindow()
	gui.centerWindowAll()

	myFrame = gui.getWindow(0)
	myFrame.showWindow()

	gui.finish()