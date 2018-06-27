import os
import sys
if (__name__ == "__main__"):
	sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))) #Allows to import from the parent directory

import GUI_Maker

#Create GUI object
gui = GUI_Maker.build()

#Bound Functions
def onShow(event):
	with gui[0] as myFrame:
		print("Showing")
		myFrame.show("adipiscing")

def onHide(event):
	with gui[0] as myFrame:
		print("Hiding")
		myFrame.hide("adipiscing")

#Construction Functions
def buildWindow():
	"""Creates a simple window."""

	#Initialize Frame
	with gui.addWindow(label = 0, title = "Dynamic Flex Sizers") as myFrame:
		myFrame.setWindowSize((400, 300))

		#Add Content
		with myFrame.addSizerGridFlex(rows = 3, columns = 4) as mySizer:
			mySizer.growFlexRowAll(growOnEmpty = False)
			mySizer.growFlexColumnAll(growOnEmpty = False)	
				
			mySizer.addInputBox("lorem", label = "lorem", minSize = (36, 36))
			mySizer.addInputBox("ipsum", label = "ipsum", minSize = (36, 36))
			mySizer.addInputBox("dolor", label = "dolor", minSize = (36, 36), hidden = True)
			mySizer.addInputBox("sit", label = "sit", minSize = (36, 36))

			mySizer.addInputBox("amet", label = "amet", minSize = (36, 36), hidden = True)
			mySizer.addInputBox("consectetur", label = "consectetur", minSize = (36, 36), hidden = True)
			mySizer.addInputBox("adipiscing", label = "adipiscing", minSize = (36, 36), hidden = True)
			mySizer.addInputBox("elit", label = "elit", minSize = (36, 36), hidden = True)

			mySizer.addInputBox("sed", label = "sed", minSize = (36, 36))
			mySizer.addInputBox("do", label = "do", minSize = (36, 36), hidden = True)
			mySizer.addInputBox("eiusmod", label = "eiusmod", minSize = (36, 36), hidden = True)
			mySizer.addInputBox("tempor", label = "tempor", minSize = (36, 36))

		with myFrame.addSizerBox(vertical = False, flex = 0) as mySizer:
			mySizer.addButton("Show", myFunction = onShow)
			mySizer.addButton("Hide", myFunction = onHide)

#Run Program
if __name__ == '__main__':
	buildWindow()
	gui.centerWindowAll()

	myFrame = gui.getWindow(0)
	myFrame.showWindow()

	gui.finish()