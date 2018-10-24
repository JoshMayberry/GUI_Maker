import os
import sys
import time
if (__name__ == "__main__"):
	sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))) #Allows to import from the parent directory

import GUI_Maker

#Create GUI object
gui = GUI_Maker.build()

#Bound Functions
def onWizard_finish(event):

	event.Skip()

#Construction Functions
def buildWindow():
	"""Creates a simple window."""

	with gui.addWindow(label = 0, title = "Search Example") as myFrame:
		with myFrame.addSizerBox() as mySizer:
			choices = ["lorem", "ipsum", "dolor", "sit", "amet"]
			# with mySizer.addInputSearch(choices = choices, menuLabel = "searchMenu", menuReplaceText = True, autoComplete = True, searchButton = False) as myWidget:
			# 	print(myWidget)

			# with myWidget["searchMenu"] as myMenu:
			# 	for item in choices:
			# 		myMenu.addItem(item)

			mySizer.addListDrop(choices = choices, inputBox = True, autoComplete = True)

#Run Program
if __name__ == '__main__':
	buildWindow()
	gui.centerWindowAll()

	myFrame = gui.getWindow(0)
	myFrame.showWindow()

	gui.finish()