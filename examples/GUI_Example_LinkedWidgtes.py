import os
import sys
if (__name__ == "__main__"):
	sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))) #Allows to import from the parent directory

import GUI_Maker

#Create GUI object
gui = GUI_Maker.build()#printMakeVariables = True)

#Construction Functions
def buildWindows():
	"""Creates two simple windows."""

	#Initialize Frame
	with gui.addWindow(label = 0, title = "Window 1", position = (100, 100)) as myFrame:
		with myFrame.addSizerBox() as mySizer:
			sharedWidget = mySizer.addInputBox(text = "Lorem")
			mySizer.addInputBox(text = "Ipsum")

			with myFrame.addSizerBox() as mySubSizer:
				sharedSizer = mySubSizer
				mySubSizer.addText("Dolor")
				mySubSizer.addText("Sit")

		myFrame.showWindow()

	with gui.addWindow(label = 1, title = "Window 2", position = (500, 100)) as myFrame:
		with myFrame.addSizerBox() as mySizer:	
			mySizer.nest(sharedWidget, linkCopy = True)
			mySizer.nest(sharedSizer)

		myFrame.showWindow()

#Run Program
if __name__ == '__main__':
	buildWindows()
	gui.finish()