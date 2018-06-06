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
		with myFrame.addSizerGridFlex(rows = 1, columns = 1) as mySizer:
			mySizer.growFlexRowAll()
			mySizer.growFlexColumnAll()	

			with mySizer.addNotebook() as myNotebook:
				with myNotebook.addPage(text = "Lorem", sizer = {"type": "flex", "rows": 2, "columns": 1}) as myNotebookPage:
					myNotebookPage.growFlexColumnAll()
					myNotebookPage.growFlexRowAll()

					myNotebookPage.addText(text = "Ipsum")
					myNotebookPage.addText(text = "Dolor")

				with myNotebook.addPage(text = "Sit", sizer = {"type": "flex", "rows": 1, "columns": 1}) as myNotebookPage:
					myNotebookPage.growFlexColumnAll()
					myNotebookPage.growFlexRowAll()

					myNotebookPage.addText(text = "Amet")

#Run Program
if __name__ == '__main__':
	buildWindow()
	gui.centerWindowAll()

	myFrame = gui.getWindow(0)
	myFrame.showWindow()

	gui.finish()