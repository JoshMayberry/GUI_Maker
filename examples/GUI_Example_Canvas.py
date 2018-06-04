import os
import sys
if (__name__ == "__main__"):
	sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))) #Allows to import from the parent directory

import GUI_Maker
import wx

#Create GUI object
gui = GUI_Maker.build()

#Bound Functions
def onSave(event):
	"""Saves the canvas."""

	with gui.getWindow(0) as myFrame:
		with myFrame["canvas"] as myCanvas:

			# canvasDc = myCanvas.getDC()
			canvasImage = myCanvas.getImage()
			canvasImage.SaveFile('saved.png', wx.BITMAP_TYPE_PNG)

	event.Skip()

#Construction Functions
def buildWindow():
	"""Creates a simple window."""

	#Initialize Frame
	with gui.addWindow(label = 0, title = "Canvas Test") as myFrame:
		myFrame.setMinimumFrameSize((250, 200))

		#Add Content
		with myFrame.addSizerBox(flex = 1) as mySizer:
		# with myFrame.addSizerGridFlex(rows = 2, columns = 1) as mySizer:
		# 	mySizer.growFlexRowAll()
		# 	mySizer.growFlexColumnAll()	
			with mySizer.addCanvas(label = "canvas", flex = 1) as myCanvas:
				myCanvas.drawText("Lorem Ipsum Dolor Sit Amet Lorem Ipsum Dolor Sit Amet")

			mySizer.addButton("Save", myFunction = onSave, flex = 0)

#Run Program
if __name__ == '__main__':
	buildWindow()
	gui.centerWindowAll()

	myFrame = gui.getWindow(0)
	myFrame.showWindow()

	gui.finish()