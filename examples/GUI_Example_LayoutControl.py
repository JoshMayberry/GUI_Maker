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
	with gui.addWindow(label = 0, title = "Controlled Layout") as myFrame:
		# myFrame.setMinimumFrameSize((250, 200))

		#Add Content
		with myFrame.addSizerGridFlex(rows = 2, columns = 1) as mySizer:
			mySizer.growFlexRowAll()
			mySizer.growFlexColumnAll()	
				
			with mySizer.addSizerGridFlex(rows = 3, columns = 2) as mySubSizer:
				mySubSizer.growFlexRow(2)
				mySubSizer.growFlexColumnAll()	
				mySubSizer.addText("Lorem")
				mySubSizer.addText("Ipsum")
				mySubSizer.addText(text = "Dolor")
			
			with mySizer.addSizerGridFlex(rows = 3, columns = 2) as mySubSizer:
				mySubSizer.growFlexRow(2)
				mySubSizer.growFlexColumnAll()	
				mySubSizer.addText(text = "Sit")
				mySubSizer.addInputBox(text = "Amet")
				mySubSizer.addInputBox(text = "Consectetur")

		with myFrame.addSizerGridFlex(rows = 3, columns = 2) as mySizer:
			mySizer.growFlexRowAll()
			mySizer.growFlexColumnAll()	
			mySizer.addText("Lorem")
			mySizer.addText("Ipsum")
			mySizer.addText("Dolor")

#Run Program
if __name__ == '__main__':
	buildWindow()
	gui.centerWindowAll()

	myFrame = gui.getWindow(0)
	myFrame.showWindow()

	gui.finish()