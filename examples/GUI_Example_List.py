import os
import sys
if (__name__ == "__main__"):
	sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))) #Allows to import from the parent directory

import GUI_Maker

#Create GUI object
gui = GUI_Maker.build()

#Construction Functions
def buildWindow():
	"""Creates a simple window."""

	#Initialize Frame
	with gui.addWindow(label = 0, title = "Dynamic Flex Sizers") as myFrame:
		myFrame.setWindowSize((400, 300))

		#Add Content
		with myFrame.addSizerBox() as mySizer:
			mySizer.addListFull(choices = [[1, "Lorem"], [5, "Ipsum"], [0, 3]], columns = 2, 
				columnNames = {0: "id", 1: "text"}, columnWidth = {0: 50}, editable = {1: True})

#Run Program
if __name__ == '__main__':
	buildWindow()
	gui.centerWindowAll()

	myFrame = gui.getWindow(0)
	myFrame.showWindow()

	gui.finish()