import os
import sys
import time
if (__name__ == "__main__"):
	sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))) #Allows to import from the parent directory

import GUI_Maker

#Create GUI object
gui = GUI_Maker.build()

#Bound Functions
def onShow(event):

	myWizard = gui[1]
	myWizard.start()

	event.Skip()

def onWizard_pageChange(event):
	print("Wizard Page Changed", event.GetPage().parent.__repr__())

	event.Skip()

def onWizard_cancel(event):
	print("Wizard Canceled")

	event.Skip()

def onWizard_finish(event):
	print("Wizard Finished")

	event.Skip()

#Construction Functions
def buildWindow():
	"""Creates a simple window."""

	with gui.addWindow(label = 0, title = "Wizard Example") as myFrame:
		with myFrame.addSizerBox() as mySizer:
			mySizer.addButton("Launch Wizard", myFunction = onShow)

	with gui.addWizard(label = 1, title = "My Wizard") as myWizard:
		myWizard.setFunction_pageChange(onWizard_pageChange)
		myWizard.setFunction_cancel(onWizard_cancel)
		myWizard.setFunction_finish(onWizard_finish)
		
		with myWizard.addPage() as myWizardPage:
			myWizardPage.addText(text = "lorem")

		with myWizard.addPage(label = 2) as myWizardPage:
			myWizardPage.addText(text = "ipsum")

		with myWizard.addPage() as myWizardPage:
			myWizardPage.addText(text = "dolor")

		with myWizard.addPage() as myWizardPage:
			myWizardPage.addText(text = "sit")

		with myWizard.addPage() as myWizardPage:
			myWizardPage.addText(text = "amet")

#Run Program
if __name__ == '__main__':
	buildWindow()
	gui.centerWindowAll()

	myFrame = gui.getWindow(0)
	myFrame.showWindow()

	gui.finish()