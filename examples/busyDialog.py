import os
import sys
import time
if (__name__ == "__main__"):
	sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))) #Allows to import from the parent directory

import GUI_Maker

#Create GUI object
gui = GUI_Maker.build()

#Bound Functions
def onSimple(event):
	with gui[0].makeDialogBusy(text = "Test...") as myDialog:
		for i in range(3):
			print(i)
			time.sleep(1)

	event.Skip()

def onAdvanced(event):
	with gui[0].makeDialogBusy(text = "Test...", simple = False, maximum = 10, can_abort = True) as myDialog:
		for i in range(1, 11):
			time.sleep(1)
			if (i == 5):
				myDialog.setValue(i, text = "Half Way There")
			else:
				myDialog.setValue(i)

			if (myDialog.isAbort()):
				print("Abort")
				# myDialog.resume()
				break

			with myDialog.makeDialogBusy(text = "Sub Test...", simple = False, maximum = 110, can_abort = True, can_skip = True) as subTest:
				# continue
				for j in range(1, 111):
					print((i, j), subTest.isSkip())
					time.sleep(0.25)
					subTest.setValue(j)

					if (subTest.isAbort()):
						print("Sub Abort")
						break
					if (subTest.isSkip()):
						print("Sub Skip")
						break

				if (subTest.isAbort()):
					break

	event.Skip()

def onRecycle(event):
	myDialog = gui[0].makeDialogBusy(text = "Test...", simple = False, maximum = 10, can_abort = True)
	for i in range(1, 3):
		with myDialog:
			for j in range(1, 11):
				print((i, j))
				time.sleep(0.25)
				myDialog.setValue(j)

				if (myDialog.isAbort()):
					print("Abort")
					break
		myDialog.rebuild()

	event.Skip()

def onEarly(event):
	with gui[0].makeDialogBusy(text = "Test...", simple = False, maximum = 3, autoHide = False) as myDialog:
		for i in range(1, 11):
			print(i)
			time.sleep(0.25)
			myDialog.setValue(i)

	event.Skip()

def onLargeMax(event):
	maximum = 1_000_000_000
	with gui[0].makeDialogBusy(text = "Test...", simple = False, maximum = maximum, autoHide = False) as myDialog:
		for i in range(1, 21):
			print(i)
			time.sleep(0.25)
			myDialog.setValue(int(i * maximum / 20))

	event.Skip()

#Construction Functions
def buildWindow():
	"""Creates a simple window."""

	#Initialize Frame
	with gui.addWindow(label = 0, title = "Busy Dialog Example") as myFrame:
		myFrame.setWindowSize((450, 300))
		
		with myFrame.addSizerBox() as mySizer:
			mySizer.addButton(text = "Simple", myFunction = onSimple)
			mySizer.addButton(text = "Advanced", myFunction = onAdvanced)
			mySizer.addButton(text = "Recycle", myFunction = onRecycle)
			mySizer.addButton(text = "Early", myFunction = onEarly)
			mySizer.addButton(text = "Large Max", myFunction = onLargeMax)

#Run Program
if __name__ == '__main__':
	buildWindow()
	gui.centerWindowAll()

	myFrame = gui.getWindow(0)
	myFrame.showWindow()

	gui.finish()