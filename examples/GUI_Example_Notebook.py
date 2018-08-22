import os
import sys
if (__name__ == "__main__"):
	sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))) #Allows to import from the parent directory

import GUI_Maker

#Create GUI object
gui = GUI_Maker.build()

def onToggleTab(event):
	"""Shows and hides some tabs."""

	with gui["notebook"] as myNotebook:
		myNotebook.hidePage("dolor", state = gui[event].getValue() == "show")
		myNotebook.hidePage("ipsum", state = gui[event].getValue() == "show")
		myNotebook.hidePage("lorem", state = gui[event].getValue() == "show")

	event.Skip()

#Construction Functions
def buildWindow():
	"""Creates a simple window."""

	#Initialize Frame
	with gui.addWindow(label = 0, title = "Controlled Layout") as myFrame:
		myFrame.setWindowSize((500, 400))

		#Add Content
		with myFrame.addSizerGridFlex(rows = 2, columns = 1) as mainSizer:
			mainSizer.growFlexRow(0)
			mainSizer.growFlexColumnAll()	

			with mainSizer.addNotebook(label = "notebook") as myNotebook:
				with myNotebook.addPage(text = "Lorem", label = "lorem", sizer = {"type": "flex", "rows": 2, "columns": 1}) as myNotebookPage:
					myNotebookPage.growFlexColumnAll()
					myNotebookPage.growFlexRow(1)

					myNotebookPage.addText(text = "1")
					myNotebookPage.addInputBox(text = "2")

				myNotebook.clonePage("lorem", text = "Clone", label = "clone")

				with myNotebook.addPage(text = "Ipsum", label = "ipsum") as myNotebookPage:
					myNotebookPage.addText(text = "3")

				with myNotebook.addPage(text = "Dolor", label = "dolor") as myNotebookPage:
					myNotebookPage.addText(text = "4")

				with myNotebook.addPage(text = "Sit", label = "sit") as myNotebookPage:
					myNotebookPage.addText(text = "5")

				with myNotebook.addPage(text = "Amet", label = "amet") as myNotebookPage:
					myNotebookPage.addText(text = "6")

			with mainSizer.addSizerGridFlex(rows = 1, columns = 1) as mySizer:
				mySizer.addButtonList(["hide", "show"], myFunction = onToggleTab)

#Run Program
if __name__ == '__main__':
	buildWindow()
	gui.centerWindowAll()

	myFrame = gui.getWindow(0)
	myFrame.showWindow()

	gui.finish()