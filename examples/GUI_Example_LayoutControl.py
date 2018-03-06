from GUI_27 import GUI

#Create GUI object
gui = GUI()

#Construction Functions
def buildWindow():
	"""Creates a simple window."""

	#Initialize Frame
	myFrame = gui.createWindow(0, "Controlled Layout", autoSize = False)
	myFrame.setMinimumFrameSize((250, 200))

	#Add Content
	myFrame.addSizerBox(0)

	myFrame.addSizerGridFlex(3, 2, 1)
	myFrame.addText("Lorem", 1)
	myFrame.addText("Ipsum", 1)
	myFrame.addText("Dolor", 1)
	myFrame.addText("Sit", 1)
	myFrame.addInputBox(1, text = "Amet")
	myFrame.addInputBox(1, text = "Consectetur")
	myFrame.nestSizerInSizer(1, 0)

	myFrame.growFlexRow(1, 2)
	myFrame.growFlexColumnAll(1)

#Run Program
if __name__ == '__main__':
	buildWindow()
	gui.centerWindowAll()

	myFrame = gui.getWindow(0)
	myFrame.showWindow()

	gui.finish()