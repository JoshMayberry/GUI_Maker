from GUI_27 import GUI

#Create GUI object
gui = GUI()

#GUI Functions
def onChangeText(event):
	"""Changes the text on the GUI."""

	#Setup
	myFrame = gui.getWindow(0)

	#Get current text value
	value = myFrame.getObjectValueWithLabel("changableText")

	#Change text value
	if (value == "Lorem"):
		myFrame.setObjectValueWithLabel("changableText", "Ipsum")
	else:
		myFrame.setObjectValueWithLabel("changableText", "Lorem")

	#Finish GUI Event
	event.Skip()

#Construction Functions
def buildWindow():
	"""Creates a simple window."""

	#Initialize Frame
	myFrame = gui.createWindow(0, "Change the text by clicking the button", autoSize = False)
	myFrame.typicalWindowSetup()
	myFrame.setWindowSize(600, 600)
	myFrame.setMinimumFrameSize((250, 200))

	#Add Content
	myFrame.addSizerBox(0)
	myFrame.addText("Lorem", 0, myLabel = "changableText")
	myFrame.addButton("Change Text", 0, myFunction = onChangeText)

#Run Program
if __name__ == '__main__':
	buildWindow()
	gui.centerWindowAll()

	myFrame = gui.getWindow(0)
	myFrame.showWindow()

	gui.finish()