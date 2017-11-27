from GUI_27 import GUI

#Create GUI object
gui = GUI()

#GUI Functions
def onChangeText(event, newValue):
	"""Changes the text on the GUI."""

	#Setup
	myFrame = gui.getWindow(0)

	#Change text value
	myFrame.setObjectValueWithLabel("changableText", newValue)

	#Finish GUI Event
	event.Skip()

#Construction Functions
def buildWindow():
	"""Creates a simple window."""

	#Initialize Frame
	myFrame = gui.createWindow(0, "Change the text by selecting a menu item", autoSize = False)
	myFrame.setMinimumFrameSize((250, 200))

	#Build Menu
	myFrame.addMenuBar()
	myFrame.addMenu(0, "Menu 1")
	myFrame.addMenuItem(0, "Option 1", myFunction = onChangeText, myFunctionArgs = "Lorem")
	myFrame.addMenuItem(0, "Option 2", myFunction = onChangeText, myFunctionArgs = "Ipsum")
	
	myFrame.addMenu(1, "Menu 2")
	myFrame.addMenuItem(1, "Option 1", myFunction = onChangeText, myFunctionArgs = "Dolor")
	myFrame.addMenuItem(1, "Option 2", myFunction = onChangeText, myFunctionArgs = "Sit")
	myFrame.addMenuSeparator(0)
	myFrame.addMenuSub(1, 2, "Sub Menu")
	myFrame.addMenuItem(2, "Option 3", myFunction = onChangeText, myFunctionArgs = "Amet")

	#Add Content
	myFrame.addSizerBox(0)
	myFrame.addText("Lorem", 0, myLabel = "changableText")

#Run Program
if __name__ == '__main__':
	buildWindow()
	gui.centerWindowAll()

	myFrame = gui.getWindow(0)
	myFrame.showWindow()

	gui.finish()