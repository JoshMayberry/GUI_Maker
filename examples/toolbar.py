import os
import sys
if (__name__ == "__main__"):
	sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))) #Allows to import from the parent directory

import GUI_Maker

#Create GUI object
gui = GUI_Maker.build()

def onTool_1(event):
	print("Lorem")
	event.skip()

def onTool_2(event):
	print("Ipsum")
	event.skip()

def onTool_3(event):
	print("Dolor")
	event.skip()

def onTool_4(event):
	print("Sit")
	event.skip()

def onTool_5(event):
	print("Amet")
	event.skip()

#Construction Functions
def buildWindow():
	"""Creates a simple window."""

	#Initialize Frame
	with gui.addWindow(label = 0, title = "Controlled Layout") as myFrame:
		# myFrame.setMinimumFrameSize((250, 200))

		#Add Content
		with myFrame.addSizerGridFlex(rows = 2, columns = 1) as mySizer:
			mySizer.growFlexRow(1)
			mySizer.growFlexColumnAll()	

			with mySizer.addToolBar(label = "toolbar") as myToolbar: 
				pass
				
				with myToolbar.addItem(icon = "save", internal = True, label = "tool_save", enabled = False, myFunction = onTool_1) as myToolbarItem:
					myToolbarItem.addToolTip("Save Changes")

				with myToolbar.addButtonImage(label = "tool_scanner", idlePath = "resources/scanner_disabled.ico", 
					selectedPath = "resources/scanner_enabled.ico", toggle = True) as myToolbarItem:

					myToolbarItem.addToolTip("Enable/Disable the barcode scanner")
					myToolbarItem.setFunction_click(myFunction = onTool_2)
				
				with myToolbar.addItem(icon = "undo", internal = True, label = "tool_undo", enabled = False, myFunction = onTool_3) as myToolbarItem:
					myToolbarItem.addToolTip("Undo last action")
				
				with myToolbar.addItem(icon = "redo", internal = True, label = "tool_redo", enabled = False, myFunction = onTool_4) as myToolbarItem:
					myToolbarItem.addToolTip("Redo last undo")
				
				with myToolbar.addInputSearch(widgetLabel = "searchBox_attributes") as myToolbarItem:
					myToolbarItem.setFunction_click(myFunction = onTool_5)
					myToolbarItem.addToolTip("Filter what is shown")

			with mySizer.addSizerGrid(rows = 1, columns = 2) as mySubSizer:
				mySubSizer.addText("Lorem")
				mySubSizer.addText("Ipsum")

#Run Program
if __name__ == '__main__':
	buildWindow()
	gui.centerWindowAll()

	myFrame = gui.getWindow(0)
	myFrame.showWindow()

	gui.finish()