import os
import sys
if (__name__ == "__main__"):
	sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))) #Allows to import from the parent directory

import GUI_Maker
import wx

#Create GUI object
gui = GUI_Maker.build()

#Bound Functions
def onShow(event):

	myFrame = gui[1]
	with myFrame.makeDialogCustom() as myDialog:
		print(myDialog.isOk())

	event.Skip()

def onShow_2(event):

	myFrame = gui[1]
	with myFrame.makeDialogChoice(["Lorem", "Ipsum"], title = "Make a Choice", text = "Choose One") as mySubDialog:
		print(mySubDialog.getValue())

	event.Skip()

#Construction Functions
def buildWindow():
	"""Creates a simple window."""

	with gui.addWindow(label = 0, title = "Custom Dialog") as myFrame:
		with myFrame.addSizerBox() as mySizer:
			mySizer.addButton("Launch Dialog", myFunction = onShow)

	with gui.addDialog(label = 1, title = "My Dialog", addOk = True, addCancel = True) as myFrame:
		with myFrame.addSizerBox() as mySizer:
			mySizer.addText("Lorem Ipsum")
			mySizer.addButton("Nested Dialog", myFunction = onShow_2)

#Run Program
if __name__ == '__main__':
	buildWindow()
	gui.centerWindowAll()

	myFrame = gui.getWindow(0)
	myFrame.showWindow()

	gui.finish()